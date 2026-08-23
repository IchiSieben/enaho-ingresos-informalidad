# 03_fase1_preparacion.py — construcción del dataset de modelado
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
# Fase 1 — Construccion del dataset de modelado.
# Poblacion: ocupados (OCU500=1), 14+, ingreso laboral mensual > 0.
# Targets: ingreso_mes (suma de anualizados INEI / 12, "suavizado") e informal
# (regla derivada: independientes/empleadores sin RUC; dependientes sin pension).
# Verificaciones pedidas: horas ocup. secundaria, prevalencia ponderada vs INEI,
# AUC univariado anti-circularidad, % de ingreso en especie.
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from comun import (CENTINELAS_MONETARIOS, DIR_INTERIM, DIR_PROCESSED, DIR_RAW,
                   DIR_REPORTS, LLAVES_PERSONA, MAPA_CATEGORIA, MAPA_DOMINIO,
                   MAPA_TAMANO, MIN_FRECUENCIA, anios_educacion, formato_md,
                   leer_enaho, nivel_educativo_agrupado, rama_agrupada)

COLS_MOD05 = LLAVES_PERSONA + [
    "DOMINIO", "ESTRATO", "OCU500", "P507", "P510A1", "P511A", "P512A",
    "P513T", "P518", "P514", "I513T", "I518", "I520",
    "I524A1", "I530A", "I538A1", "I541A",
    "D529T", "D540T", "D543",
    "P558A5", "P506R4", "P207", "P208A", "FAC500A",
]
COLS_MOD03 = LLAVES_PERSONA + ["P301A", "P301B", "P301C"]

secciones = []  # pares (titulo, texto) para el reporte


def reportar(titulo: str, texto: str) -> None:
    print(f"\n=== {titulo} ===\n{texto}")
    secciones.append((titulo, texto))


def main() -> None:
    m5 = leer_enaho(DIR_RAW / "1031-Modulo05" / "1031-Modulo05" / "Enaho01a-2025-500.csv",
                    COLS_MOD05)
    m3 = leer_enaho(DIR_RAW / "1031-Modulo03" / "1031-Modulo03" / "Enaho01A-2025-300.csv",
                    COLS_MOD03)

    # Centinelas documentados en el diccionario -> NaN antes de todo calculo
    for c in ["I524A1", "I530A", "I538A1", "I541A", "D529T", "D540T", "D543"]:
        m5[c] = pd.to_numeric(m5[c], errors="coerce").replace(CENTINELAS_MONETARIOS, np.nan)
    m5["P518"] = pd.to_numeric(m5["P518"], errors="coerce").replace(99, np.nan)
    for c in ["P513T", "I513T", "I518", "I520", "P208A"]:
        m5[c] = pd.to_numeric(m5[c], errors="coerce")
    # El factor de expansion viene con coma decimal ("150,29814...")
    m5["FAC500A"] = pd.to_numeric(m5["FAC500A"].str.replace(",", ".", regex=False),
                                  errors="coerce")

    # --- Cascada de poblacion ---
    ocupados = m5[m5["OCU500"] == 1].copy()
    n_tfnr = int((pd.to_numeric(ocupados["P507"], errors="coerce") == 5).sum())
    fac_tfnr = float(ocupados.loc[pd.to_numeric(ocupados["P507"], errors="coerce") == 5,
                                  "FAC500A"].sum())

    ocupados["ingreso_mes"] = ocupados[["I524A1", "I530A", "I538A1", "I541A"]].sum(
        axis=1, min_count=1) / 12
    df = ocupados[(ocupados["P208A"] >= 14) & (ocupados["ingreso_mes"] > 0)].copy()
    reportar("Cascada de poblacion",
             f"mod05 {len(m5):,} -> ocupados {len(ocupados):,} -> 14+ e ingreso>0 {len(df):,}\n"
             f"TFNR (P507=5) excluidos por ingreso=0: {n_tfnr:,} "
             f"({n_tfnr/len(ocupados)*100:.1f}% de ocupados; ponderado {fac_tfnr:,.0f} personas). "
             "Son informales por definicion: la poblacion final subestima algo la "
             "prevalencia oficial (restriccion de poblacion, no error).")

    # --- 1. Horas: principal + secundaria ---
    p514 = pd.to_numeric(df["P514"], errors="coerce")
    tiene_sec = (p514 == 1) | df["I538A1"].gt(0) | df["I541A"].gt(0)
    df["horas_prin"] = df["I513T"].fillna(df["P513T"])
    df["horas_sec"] = df["I518"].fillna(df["P518"])
    cobertura_sec = df.loc[tiene_sec, "horas_sec"].notna().mean() * 100
    df["horas_total"] = df["horas_prin"].fillna(0) + df["horas_sec"].fillna(0)
    df.loc[df["horas_prin"].isna() & df["horas_sec"].isna(), "horas_total"] = np.nan
    reportar("Horas totales (correccion del desajuste)",
             f"Con ocupacion secundaria: {tiene_sec.sum():,} ({tiene_sec.mean()*100:.1f}% "
             f"de la poblacion). Cobertura de horas secundarias (I518/P518) entre ellos: "
             f"{cobertura_sec:.1f}%.\n"
             f"horas_total = I513T (fallback P513T) + I518 (fallback P518, 0 si no hay "
             f"secundaria). Cobertura final: {df['horas_total'].notna().mean()*100:.1f}%. "
             f"Mediana {df['horas_total'].median():.0f} h/sem.")

    # --- Derivadas Mincer y demograficas ---
    df = df.merge(m3, on=LLAVES_PERSONA, how="left")
    p301a = pd.to_numeric(df["P301A_y"] if "P301A_y" in df else df["P301A"], errors="coerce")
    p301b = pd.to_numeric(df["P301B"], errors="coerce")
    p301c = pd.to_numeric(df["P301C"], errors="coerce")
    df["anios_educ"] = anios_educacion(p301a, p301b, p301c)
    df["nivel_educ"] = nivel_educativo_agrupado(p301a)
    df["edad"] = df["P208A"]
    df["exper"] = (df["edad"] - df["anios_educ"] - 6).clip(lower=0)
    df["exper2"] = df["exper"] ** 2
    df["sexo"] = pd.to_numeric(df["P207"], errors="coerce").map({1: "Hombre", 2: "Mujer"})
    df["area"] = np.where(pd.to_numeric(df["ESTRATO"], errors="coerce") <= 5,
                          "Urbana", "Rural")
    df["dominio"] = pd.to_numeric(df["DOMINIO"], errors="coerce").map(MAPA_DOMINIO)
    df["tamano_empresa"] = pd.to_numeric(df["P512A"], errors="coerce").map(MAPA_TAMANO)
    df["categoria"] = pd.to_numeric(df["P507"], errors="coerce").map(MAPA_CATEGORIA)
    df["rama"] = rama_agrupada(df["P506R4"])

    # Agrupacion de ramas raras por conteo absoluto
    conteos = df["rama"].value_counts()
    raras = conteos[conteos < MIN_FRECUENCIA].index.tolist()
    if raras:
        df["rama"] = df["rama"].replace({r: "Otros servicios" for r in raras})
    reportar("Rama de actividad agrupada (umbral 300 obs.)",
             f"Colapsadas a 'Otros servicios': {raras or 'ninguna'}\n"
             + df["rama"].value_counts().to_string())
    conteos_nivel = df["nivel_educ"].value_counts()
    reportar("Nivel educativo agrupado", conteos_nivel.to_string())

    # --- 2. Target de informalidad ---
    p507 = pd.to_numeric(df["P507"], errors="coerce")
    p510a1 = pd.to_numeric(df["P510A1"], errors="coerce")
    p558a5 = pd.to_numeric(df["P558A5"], errors="coerce")
    df["informal"] = np.nan
    indep = p507.isin([1, 2])
    dep = p507.isin([3, 4, 6])
    df.loc[indep & p510a1.notna(), "informal"] = (p510a1[indep] == 3).astype(float)
    df.loc[dep & p558a5.notna(), "informal"] = (p558a5[dep] == 5).astype(float)

    sin_target = df["informal"].isna().sum()
    prev_simple = df["informal"].mean() * 100
    w = df["FAC500A"]
    prev_pond = (df["informal"] * w).sum() / w[df["informal"].notna()].sum() * 100
    reportar("Prevalencia de informalidad (validacion externa)",
             f"Sin target (P510A1/P558A5 faltante): {sin_target:,} filas.\n"
             f"Prevalencia muestral: {prev_simple:.1f}% | PONDERADA (FAC500A): "
             f"{prev_pond:.1f}%.\n"
             f"Referencia INEI 2025: 70,2% nacional (empleo informal, EPEN/ENAHO). "
             f"Desviacion: {prev_pond - 70.2:+.1f} pts — se esperaba algo menor por la "
             f"exclusion de los TFNR (informales por definicion, sin ingreso).")
    filas_area = {}
    for area, g in df.groupby("area"):
        filas_area[area] = round((g["informal"] * g["FAC500A"]).sum()
                                 / g.loc[g["informal"].notna(), "FAC500A"].sum() * 100, 1)
    reportar("Prevalencia ponderada por area (contraste 64,5% urbano / 94,8% rural INEI)",
             pd.Series(filas_area).to_string())

    # --- AUC univariado anti-circularidad ---
    df["contrato"] = df["P511A"].astype("string")  # solo para el diagnostico
    candidatas = ["anios_educ", "edad", "exper", "horas_total", "sexo", "area",
                  "dominio", "rama", "tamano_empresa", "categoria", "nivel_educ",
                  "contrato"]
    y = df["informal"]
    filas_auc = []
    for c in candidatas:
        v = df[c]
        mask = y.notna() & v.notna()
        if v.dtype == object or isinstance(v.dtype, pd.StringDtype) or not pd.api.types.is_numeric_dtype(v):
            codif = v[mask].map(y[mask].groupby(v[mask]).mean())
        else:
            codif = v[mask].astype(float)
        auc = roc_auc_score(y[mask], codif)
        filas_auc.append({"variable": c, "auc_univariado": round(max(auc, 1 - auc), 3)})
    tabla_auc = pd.DataFrame(filas_auc).sort_values("auc_univariado", ascending=False)
    reportar("AUC univariado contra el target informal", tabla_auc.to_string(index=False))

    # --- 3. Ingreso en especie (exclusion declarada) ---
    especie = df[["D529T", "D540T", "D543"]].gt(0).any(axis=1)
    reportar("Ingreso en especie (excluido del target)",
             f"Ocupados de la poblacion final con pago en especie o autoconsumo "
             f"(D529T/D540T/D543 > 0): {especie.sum():,} ({especie.mean()*100:.1f}%). "
             "El target es solo ingreso monetario; esta exclusion queda declarada.")

    # --- Guardado ---
    finales = (LLAVES_PERSONA
               + ["ingreso_mes", "informal", "anios_educ", "nivel_educ", "edad",
                  "exper", "exper2", "sexo", "area", "dominio", "rama",
                  "horas_total", "tamano_empresa", "categoria", "FAC500A",
                  "contrato"])
    out = df[finales].copy()
    DIR_PROCESSED.mkdir(parents=True, exist_ok=True)
    out.to_parquet(DIR_PROCESSED / "dataset_modelado.parquet", index=False)
    nulos = out.isna().mean().mul(100).round(1)
    reportar("Dataset final", f"{out.shape[0]:,} filas x {out.shape[1]} cols -> "
             f"data/processed/dataset_modelado.parquet\n% nulos por columna:\n"
             + nulos[nulos > 0].to_string())

    # Reporte md
    md = ["# Fase 1 — Preparación del dataset de modelado\n",
          "Script: `src/03_fase1_preparacion.py`. Semilla no aplica (sin muestreo: "
          "47.9k < 300k filas).\n"]
    for titulo, texto in secciones:
        md.append(f"## {titulo}\n\n```\n{texto}\n```\n")
    (DIR_REPORTS / "01_preparacion_fase1.md").write_text("\n".join(md), encoding="utf-8")
    print("\nEscrito: reports/01_preparacion_fase1.md")


if __name__ == "__main__":
    main()
