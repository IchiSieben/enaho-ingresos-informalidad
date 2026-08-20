# 02_fase0_autopsia.py — autopsia de la regresión baseline
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
# Fase 0.2 — Autopsia: reproducir la especificacion inicial del curso sobre los
# microdatos reales de la ENAHO 2025.
#   INGRESO = b0 + b1*urbano + b2*hombre + b3*edad + dummies educ + b*horas + b*miembros
# Corrida A: "tal cual" (ingreso en niveles, centinela 999999 SIN limpiar).
# Corrida B: identica pero con el centinela convertido a NaN.
# Ademas: VIF de anios_educacion vs dummies de nivel (colinealidad) y diagnostico
# de las candidatas a INDICE_BIENESTAR (ESTRSOCIAL, GASHOG2D, INGHOG2D, POBREZA).
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
INTERIM = RAIZ / "data" / "interim"
LLAVES = ["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"]
CENTINELAS = [999999, 999999.9]


def anios_educacion(p301a, p301b, p301c) -> pd.Series:
    # Recodificacion estandar ENAHO: nivel (P301A) + anio aprobado (P301B) o
    # grado del sistema antiguo (P301C). Completa: 6, 11, 14, 16, 18.
    grado = p301b.fillna(p301c)
    base = pd.Series(np.nan, index=p301a.index)
    base[p301a.isin([1, 2, 12])] = 0
    base[p301a == 3] = grado[p301a == 3].fillna(0)
    base[p301a == 4] = 6
    base[p301a == 5] = 6 + grado[p301a == 5].fillna(0)
    base[p301a == 6] = 11
    base[p301a == 7] = 11 + grado[p301a == 7].fillna(0)
    base[p301a == 8] = 11 + grado[p301a == 8].fillna(3)
    base[p301a == 9] = 11 + grado[p301a == 9].fillna(0)
    base[p301a == 10] = 16
    base[p301a == 11] = 18
    return base.clip(upper=20)


def ajustar_ols(df: pd.DataFrame, ycol: str, xcols: list[str], etiqueta: str) -> dict:
    d = df[[ycol] + xcols].dropna()
    X = sm.add_constant(d[xcols].astype(float))
    modelo = sm.OLS(d[ycol].astype(float), X).fit(cov_type="HC3")
    vif = {c: variance_inflation_factor(X.values, i)
           for i, c in enumerate(X.columns) if c != "const"}
    print(f"\n===== {etiqueta} (n={len(d):,}) =====")
    print(f"R2: {modelo.rsquared:.4f}   R2 aj.: {modelo.rsquared_adj:.4f}")
    tabla = pd.DataFrame({"coef": modelo.params, "ee_HC3": modelo.bse,
                          "p_valor": modelo.pvalues})
    tabla["VIF"] = pd.Series(vif)
    print(tabla.round(3).to_string())
    return {"etiqueta": etiqueta, "n": len(d), "r2": modelo.rsquared,
            "coefs": modelo.params.to_dict(), "vif": vif}


def main() -> None:
    df = pd.read_parquet(INTERIM / "fase0_poblacion.parquet")

    # Recuperar P524A1/P530A CRUDOS (el parquet ya los tiene limpios)
    crudo = pd.read_csv(RAW / "1031-Modulo05" / "1031-Modulo05" / "Enaho01a-2025-500.csv",
                        sep=";", encoding="latin-1", usecols=LLAVES + ["P524A1", "P530A"],
                        dtype={k: str for k in LLAVES})
    crudo = crudo.rename(columns={"P524A1": "P524A1_crudo", "P530A": "P530A_crudo"})
    df = df.merge(crudo, on=LLAVES, how="left")

    # --- Variables de la especificacion inicial ---
    # INGRESO ingenuo: el monto del ultimo pago (P524A1) leido como "ingreso mensual",
    # y para independientes la ganancia neta del mes (P530A). Sin tocar el centinela.
    df["INGRESO_A"] = pd.to_numeric(df["P524A1_crudo"], errors="coerce").fillna(
        pd.to_numeric(df["P530A_crudo"], errors="coerce"))
    df["INGRESO_B"] = df["INGRESO_A"].replace(CENTINELAS, np.nan)

    df["urbano"] = df["ESTRATO"].astype(float).le(5).astype(int)   # estratos 6-8 = rural
    df["hombre"] = df["P207"].astype(float).eq(1).astype(int)
    df["edad"] = pd.to_numeric(df["P208A"], errors="coerce")
    p301a = pd.to_numeric(df["P301A_m3"], errors="coerce")
    p301b = pd.to_numeric(df["P301B"], errors="coerce")
    p301c = pd.to_numeric(df["P301C"], errors="coerce")
    df["primaria"] = p301a.isin([3, 4]).astype(int)
    df["secundaria"] = p301a.isin([5, 6]).astype(int)
    df["tecnica"] = p301a.isin([7, 8]).astype(int)
    df["universitaria"] = p301a.isin([9, 10, 11]).astype(int)
    # P520 solo se pregunta si la semana fue atipica (cobertura ~10%); la de
    # cobertura completa es P513T (horas trabajadas la semana pasada, ocup. principal)
    df["horas"] = pd.to_numeric(df["P513T"], errors="coerce")
    df["miembros"] = pd.to_numeric(df["MIEPERHO"], errors="coerce")
    df["anios_educ"] = anios_educacion(p301a, p301b, p301c)

    xcols = ["urbano", "hombre", "edad", "primaria", "secundaria", "tecnica",
             "universitaria", "horas", "miembros"]

    print("=== Distribucion del INGRESO ingenuo (con centinela) ===")
    print(df["INGRESO_A"].describe(percentiles=[.5, .9, .99]).round(1).to_string())
    print(f"n con centinela: {df['INGRESO_A'].isin(CENTINELAS).sum():,} "
          f"({df['INGRESO_A'].isin(CENTINELAS).mean()*100:.2f}% de la poblacion)")

    resA = ajustar_ols(df, "INGRESO_A", xcols, "Corrida A: niveles, centinela SIN limpiar")
    resB = ajustar_ols(df, "INGRESO_B", xcols, "Corrida B: niveles, centinela -> NaN")

    # Colinealidad anios de educacion vs dummies de nivel (consigna multiple completa)
    ajustar_ols(df, "INGRESO_B", ["anios_educ"] + xcols,
                "Corrida C: B + anios_educ junto a las dummies (diagnostico VIF)")

    # Outliers en niveles (justificacion del log)
    y = df["INGRESO_B"].dropna()
    print("\n=== Cola del ingreso limpio (justificacion del log) ===")
    print(f"asimetria: {y.skew():.2f}  p50: {y.median():.0f}  p99: {y.quantile(.99):.0f}  "
          f"max: {y.max():.0f}  media: {y.mean():.0f}")

    # INDICE_BIENESTAR: candidatas reales y su relacion con el ingreso
    print("\n=== Diagnostico INDICE_BIENESTAR (post-tratamiento / leakage) ===")
    df["log_ing"] = np.log1p(df["INGRESO_B"])
    for c in ["ESTRSOCIAL", "GASHOG2D", "INGHOG2D", "POBREZA"]:
        v = pd.to_numeric(df[c], errors="coerce")
        rho = df["log_ing"].corr(v, method="spearman")
        print(f"{c:11s} corr Spearman con log(ingreso): {rho:6.3f}")
    per_capita = pd.to_numeric(df["INGHOG2D"], errors="coerce") / df["miembros"]
    print(f"{'INGHOG2D/mieperho':11s} corr Spearman: {df['log_ing'].corr(per_capita, method='spearman'):6.3f}")
    # El ingreso individual es sumando directo de INGHOG2D: circularidad mecanica.

    df.to_parquet(INTERIM / "fase0_autopsia.parquet", index=False)
    print("\nEscrito: data/interim/fase0_autopsia.parquet")


if __name__ == "__main__":
    main()
