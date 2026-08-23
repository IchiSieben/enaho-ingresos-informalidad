# 01_fase0_poblacion.py — verificación empírica de población y centinelas
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
# Fase 0.1 (continuacion) — Verificacion empirica sobre archivos completos:
# codigos de OCU500, magnitud del centinela 999999 en las variables monetarias,
# candidatas de ingreso laboral mensual y cascada de filtros de poblacion.
# Nombres de columna tomados del Diccionario_2025.pdf (data/interim/diccionario_2025.txt).
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
INTERIM = RAIZ / "data" / "interim"

CENTINELAS = [999999, 999999.9]
LLAVES_PERSONA = ["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"]
LLAVES_HOGAR = ["CONGLOME", "VIVIENDA", "HOGAR"]

# Modulo 05: empleo e ingresos. P* = reportado, I* = imputado/deflactado/ANUALIZADO.
COLS_MOD05 = LLAVES_PERSONA + [
    "UBIGEO", "DOMINIO", "ESTRATO",           # geografia (ESTRATO 1-6 urbano, 7-8 rural AER)
    "OCU500", "P501", "P507", "P510",          # condicion de actividad y categoria
    "P510A1", "P510B",                          # registro SUNAT y contabilidad (sector informal)
    "P511A", "P512A", "P512B",                  # contrato y tamano de empresa
    "P513T", "P520",                            # horas ocup. principal / total normal
    "P523", "P524A1", "P530A",                  # periodicidad de pago, ingreso dep., ganancia indep.
    "P541A",                                    # ganancia neta ocup. secundaria
    "I524A1", "I530A", "I538A1", "I541A",      # anualizados: dep, indep, sec-dep, sec-indep
    "P5581A", "P5582A", "P5583A", "P5584A", "P5585A",  # sistema de pensiones (afiliacion)
    "P558A1", "P558A2", "P558A3", "P558A4", "P558A5",
    "P506R4", "P516R4",                         # rama de actividad CIIU rev4 (principal/secundaria)
    "P207", "P208A", "P209", "P301A",          # copias demograficas incluidas en el modulo
    "FAC500A",
]
COLS_MOD03 = LLAVES_PERSONA + ["P301A", "P301B", "P301C"]
COLS_SUMARIA = LLAVES_HOGAR + ["MIEPERHO", "PERCEPHO", "INGHOG2D", "GASHOG2D",
                               "ESTRSOCIAL", "POBREZA", "FACTOR07"]


def leer(ruta: Path, usecols: list[str]) -> pd.DataFrame:
    # dtype str en llaves: CONGLOME/VIVIENDA traen ceros a la izquierda.
    return pd.read_csv(ruta, sep=";", encoding="latin-1", usecols=usecols,
                       dtype={k: str for k in LLAVES_PERSONA}, low_memory=False)


def main() -> None:
    m5 = leer(RAW / "1031-Modulo05" / "1031-Modulo05" / "Enaho01a-2025-500.csv", COLS_MOD05)
    m3 = leer(RAW / "1031-Modulo03" / "1031-Modulo03" / "Enaho01A-2025-300.csv", COLS_MOD03)
    su = leer(RAW / "1031-Modulo34" / "1031-Modulo34" / "Sumaria-2025.csv",
              [c for c in COLS_SUMARIA])

    print(f"mod05: {m5.shape}, mod03: {m3.shape}, sumaria: {su.shape}")

    print("\n=== OCU500 (Indicador de la PEA) — conteo de valores ===")
    print(m5["OCU500"].value_counts(dropna=False).sort_index().to_string())
    print("\nCruce OCU500 x P501 (¿tuvo trabajo la semana pasada?):")
    print(pd.crosstab(m5["OCU500"], m5["P501"], dropna=False).to_string())

    print("\n=== Centinela 999999 en variables monetarias (archivo completo) ===")
    monetarias = ["P524A1", "P530A", "P541A", "I524A1", "I530A", "I538A1", "I541A"]
    filas = []
    for c in monetarias:
        s = pd.to_numeric(m5[c], errors="coerce")
        filas.append({
            "columna": c,
            "no_nulos": int(s.notna().sum()),
            "n_centinela": int(s.isin(CENTINELAS).sum()),
            "pct_centinela_sobre_no_nulos": round(s.isin(CENTINELAS).mean() * 100, 2),
            "max_sin_centinela": float(s[~s.isin(CENTINELAS)].max()),
            "mediana_sin_centinela": float(s[~s.isin(CENTINELAS)].median()),
        })
    print(pd.DataFrame(filas).to_string(index=False))

    # Ingreso laboral mensual a partir de los anualizados (I* ya imputados y deflactados)
    for c in monetarias:
        m5[c] = pd.to_numeric(m5[c], errors="coerce").replace(CENTINELAS, np.nan)

    m5["ing_principal_dep"] = m5["I524A1"] / 12
    m5["ing_principal_indep"] = m5["I530A"] / 12
    m5["ing_secundaria_dep"] = m5["I538A1"] / 12
    m5["ing_secundaria_indep"] = m5["I541A"] / 12
    partes = ["ing_principal_dep", "ing_principal_indep",
              "ing_secundaria_dep", "ing_secundaria_indep"]
    m5["ingreso_laboral_mes"] = m5[partes].sum(axis=1, min_count=1)

    ocupados = m5[m5["OCU500"] == 1]
    print(f"\n=== Cobertura de las candidatas de ingreso entre ocupados (OCU500==1, n={len(ocupados):,}) ===")
    for c in partes + ["ingreso_laboral_mes"]:
        s = ocupados[c]
        print(f"{c:24s} no-nulo: {s.notna().sum():7,} ({s.notna().mean()*100:5.1f}%) "
              f"mediana: {s.median():10.1f}  p95: {s.quantile(0.95):10.1f}")

    print("\n=== Cascada de filtros de poblacion ===")
    n0 = len(m5)
    paso1 = m5[m5["OCU500"] == 1]
    paso2 = paso1[pd.to_numeric(paso1["P208A"], errors="coerce") >= 14]
    paso3 = paso2[paso2["ingreso_laboral_mes"] > 0]
    print(f"filas mod05:                    {n0:8,}")
    print(f"+ ocupados (OCU500==1):         {len(paso1):8,}")
    print(f"+ edad >= 14 (P208A):           {len(paso2):8,}")
    print(f"+ ingreso laboral mensual > 0:  {len(paso3):8,}")

    print("\n=== P507 (categoria ocupacional) en la poblacion final ===")
    print(paso3["P507"].value_counts(dropna=False).sort_index().to_string())

    print("\n=== Insumos de informalidad en la poblacion final ===")
    print("P510A1 (registro SUNAT, solo independientes/empleadores):")
    print(paso3["P510A1"].value_counts(dropna=False).sort_index().to_string())
    print("\nP5585A / P558A5 (no afiliado a pension):")
    for c in ["P5585A", "P558A5"]:
        print(f"{c}: ", paso3[c].value_counts(dropna=False).sort_index().to_dict())
    print("\nP511A (tipo de contrato, dependientes):")
    print(paso3["P511A"].value_counts(dropna=False).sort_index().to_string())

    # Merge con educacion y sumaria para verificar perdidas
    df = paso3.merge(m3, on=LLAVES_PERSONA, how="left", suffixes=("", "_m3"))
    df = df.merge(su, on=LLAVES_HOGAR, how="left")
    print(f"\n=== Merges ===")
    print(f"con mod03 (educacion):  P301A_m3 no-nulo {df['P301A_m3'].notna().mean()*100:.1f}%")
    print(f"con sumaria:            MIEPERHO no-nulo {df['MIEPERHO'].notna().mean()*100:.1f}%")
    print(f"\nESTRSOCIAL en poblacion final:")
    print(df["ESTRSOCIAL"].value_counts(dropna=False).sort_index().to_string())

    df.to_parquet(INTERIM / "fase0_poblacion.parquet", index=False)
    print(f"\nEscrito: data/interim/fase0_poblacion.parquet ({len(df):,} filas)")


if __name__ == "__main__":
    main()
