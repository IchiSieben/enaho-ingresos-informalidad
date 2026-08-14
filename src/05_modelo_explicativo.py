# FASE 2 — Modelo explicativo (entregable separado del torneo).
# E4 y E6 en log, PONDERADAS con FAC500A (WLS) y errores HC3, sobre la muestra
# completa: lectura poblacional de los coeficientes. El torneo E1-E9 va sin
# ponderar (comparacion predictiva); aqui no hay ranking ni metricas de test.
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import DIR_PROCESSED, DIR_REPORTS, formato_md

sys.path.insert(0, str(Path(__file__).resolve().parent))
from importlib import import_module

torneo = import_module("04_torneo_regresion")

doc: list[str] = []


def anotar(t: str = "") -> None:
    print(t, flush=True)
    doc.append(t)


def ajustar_wls(df: pd.DataFrame, clave: str) -> None:
    spec = torneo.ESPECIFICACIONES[clave]
    X = torneo.disenar(df, spec["num"], spec["cat"])
    X = X.drop(columns=[c for c in spec.get("drop", []) if c in X.columns])
    z = np.log1p(df["ingreso_mes"])
    m = sm.WLS(z, sm.add_constant(X.astype(float)), weights=df["FAC500A"]).fit(
        cov_type="HC3")
    tabla = pd.DataFrame({
        "coef": m.params.round(4),
        "ee_HC3": m.bse.round(4),
        "p": m.pvalues.round(4),
        "efecto_pct": (100 * (np.exp(m.params) - 1)).round(1),
    })
    tabla.loc["const", "efecto_pct"] = np.nan
    anotar(f"\n## {clave} — {spec['desc']}\n")
    anotar(f"WLS ponderada por FAC500A, n={len(df):,}, R² {m.rsquared:.4f}. "
           "`efecto_pct` = (exp(coef)−1)·100: cambio porcentual del ingreso "
           "asociado a +1 unidad (o a la categoría vs su base).\n")
    anotar(formato_md(tabla, index=True))


def main() -> None:
    anotar("# Modelo explicativo del ingreso laboral (lectura poblacional)\n")
    anotar("Generado por `src/05_modelo_explicativo.py`. Ponderado con el factor "
           "de expansión de empleo (FAC500A): los coeficientes describen a la "
           "población ocupada con ingreso, no a la muestra. Separado "
           "deliberadamente del torneo (sin ponderar): son objetivos distintos "
           "y sus tablas no se mezclan.\n")
    df = pd.read_parquet(DIR_PROCESSED / "torneo_frame.parquet")
    for clave in ("E4", "E6"):
        ajustar_wls(df, clave)

    anotar("\n### Bases de comparación de las categorías\n")
    anotar("Mujer, área rural, Lima Metropolitana, rama Comercio, empresa de "
           "más de 500 personas y categoría Empleado son las bases omitidas; "
           "cada dummy se lee contra ellas.\n")
    (DIR_REPORTS / "modelo_explicativo.md").write_text("\n".join(doc) + "\n",
                                                       encoding="utf-8")
    print("\nEscrito: reports/modelo_explicativo.md")


if __name__ == "__main__":
    main()
