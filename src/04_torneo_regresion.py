# FASE 2 — Torneo de especificaciones E1-E9 para el ingreso laboral mensual.
#
# Protocolo unico e identico para todas (comparacion SIN ponderar):
#   - split 80/20 (random_state=42) y KFold(5, shuffle, 42) compartidos;
#   - cross_val_predict en train -> MAE_cv (criterio de SELECCION) y residuos
#     out-of-fold de ENTRENAMIENTO -> factor de smearing de Duan (1983);
#   - refit en train completo, test 20% solo como estimacion honesta del
#     modelo ya elegido;
#   - especificaciones en log: inversion expm1 (mediana condicional) y version
#     con smearing (media condicional). El ranking usa el MAE de la mediana,
#     que es el predictor optimo bajo MAE.
# El R2 en la escala propia de cada modelo se reporta SOLO como referencia:
# comparar R2 de log contra R2 de niveles en sus propias escalas es invalido
# (miden varianzas de variables distintas).
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LassoCV, LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (DIR_FIGURAS, DIR_PROCESSED, DIR_RAW, DIR_REPORTS,
                   LLAVES_HOGAR, LLAVES_PERSONA, N_JOBS, SEMILLA,
                   busqueda_cacheada, construir_preprocesador, formato_md,
                   leer_enaho, separar_columnas)

CENTINELAS = [999999, 999999.9]
KF = KFold(n_splits=5, shuffle=True, random_state=SEMILLA)

doc: list[str] = []


def anotar(t: str = "") -> None:
    print(t, flush=True)
    doc.append(t)


# --------------------------------------------------------------------------
# Datos: dataset de modelado + miembros (mod02) + ingreso en especie (mod05)
# --------------------------------------------------------------------------
def cargar() -> pd.DataFrame:
    df = pd.read_parquet(DIR_PROCESSED / "dataset_modelado.parquet")

    # miembros del hogar sin rescatar la Sumaria: conteo de P204=1 en mod02
    m2 = leer_enaho(DIR_RAW / "1031-Modulo02" / "1031-Modulo02" / "Enaho01-2025-200.csv",
                    LLAVES_HOGAR + ["P204"])
    miembros = (m2[pd.to_numeric(m2["P204"], errors="coerce") == 1]
                .groupby(LLAVES_HOGAR).size().rename("miembros").reset_index())
    df = df.merge(miembros, on=LLAVES_HOGAR, how="left")

    # ingreso en especie/autoconsumo (deflactado, anualizado) para la sensibilidad
    m5 = leer_enaho(DIR_RAW / "1031-Modulo05" / "1031-Modulo05" / "Enaho01a-2025-500.csv",
                    LLAVES_PERSONA + ["D529T", "D540T", "D543"])
    for c in ["D529T", "D540T", "D543"]:
        m5[c] = pd.to_numeric(m5[c], errors="coerce").replace(CENTINELAS, np.nan)
    m5["especie_mes"] = m5[["D529T", "D540T", "D543"]].sum(axis=1, min_count=1) / 12
    df = df.merge(m5[LLAVES_PERSONA + ["especie_mes"]], on=LLAVES_PERSONA, how="left")
    df["especie_mes"] = df["especie_mes"].fillna(0)

    # Derivadas de las especificaciones
    df["log_horas"] = np.log1p(df["horas_total"])
    df["urbano"] = (df["area"] == "Urbana").astype(int)
    df["hombre"] = (df["sexo"] == "Hombre").astype(int)
    df["primaria"] = (df["nivel_educ"] == "Primaria").astype(int)
    df["secundaria"] = (df["nivel_educ"] == "Secundaria").astype(int)
    df["tecnica"] = (df["nivel_educ"] == "Superior técnica").astype(int)
    df["universitaria"] = df["nivel_educ"].isin(
        ["Superior universitaria", "Posgrado"]).astype(int)
    # missingness estructural: a los independientes no se les pregunta contrato
    df["contrato"] = df["contrato"].fillna("No aplica (independiente)")

    # Experiencia potencial negativa (se reporta antes del truncado de Fase 1)
    exper_cruda = df["edad"] - df["anios_educ"] - 6
    n_neg = int((exper_cruda < 0).sum())
    anotar(f"- Experiencia potencial cruda negativa en {n_neg:,} casos "
           f"({n_neg / len(df) * 100:.1f}%): jóvenes aún en formación. Truncada en 0 "
           "(y en la ficha técnica: en baja educación la experiencia potencial "
           "SOBREestima la real — Heckman, Lochner & Todd 2006).")

    antes = len(df)
    df = df.dropna(subset=["tamano_empresa", "miembros", "horas_total",
                           "anios_educ", "ingreso_mes"])
    anotar(f"- Casos completos del torneo: {len(df):,} (se pierden "
           f"{antes - len(df):,} filas, {100 * (antes - len(df)) / antes:.1f}%, "
           "casi todas por tamaño de empresa faltante)")
    return df.reset_index(drop=True)


# --------------------------------------------------------------------------
# Especificaciones
# --------------------------------------------------------------------------
CAT_BASE = {"sexo": "Mujer", "area": "Rural", "dominio": "Lima Metropolitana",
            "rama": "Comercio", "tamano_empresa": "Más de 500",
            "categoria": "Empleado", "contrato": "Contrato indefinido",
            "nivel_educ": "Sin nivel/inicial"}


def disenar(df: pd.DataFrame, numericas: list[str], categoricas: list[str]) -> pd.DataFrame:
    """Matriz de diseno para OLS: dummies con base fija y legible."""
    X = df[numericas].astype(float).copy()
    for c in categoricas:
        d = pd.get_dummies(df[c], prefix=c, dtype=float)
        base = f"{c}_{CAT_BASE[c]}"
        if base in d.columns:
            d = d.drop(columns=[base])
        elif c == "contrato":  # la base real es el codigo 1
            d = d.drop(columns=[col for col in d.columns if col.endswith("_1")])
        X = pd.concat([X, d], axis=1)
    return X


ESPECIFICACIONES = {
    "E1": {"escala": "niveles", "num": ["anios_educ"], "cat": [],
           "desc": "Ingreso ~ años educación (consigna, niveles)", "interp": "alta"},
    "E2": {"escala": "log", "num": ["anios_educ"], "cat": [],
           "desc": "log(ingreso) ~ años educación", "interp": "alta"},
    "E3": {"escala": "log", "num": ["anios_educ", "exper", "exper2"], "cat": [],
           "desc": "Mincer clásico: educ + exp + exp²", "interp": "alta"},
    "E4": {"escala": "log",
           "num": ["anios_educ", "exper", "exper2", "hombre", "urbano", "log_horas"],
           "cat": ["rama"],
           "desc": "Mincer extendido: E3 + sexo + área + log(horas) + rama", "interp": "alta"},
    "E5": {"escala": "niveles",
           "num": ["urbano", "hombre", "edad", "primaria", "secundaria", "tecnica",
                   "universitaria", "horas_total", "miembros"], "cat": [],
           "desc": "Réplica de la compañera (niveles, sin centinela)", "interp": "alta"},
    "E6": {"escala": "log",
           "num": ["anios_educ", "exper", "exper2", "hombre", "urbano", "log_horas"],
           "cat": ["rama", "categoria", "tamano_empresa", "dominio"],
           # P507=6 (trab. del hogar) y CIIU 97 (servicio domestico) son la misma
           # particion: VIF=inf. Se suelta la dummy de rama redundante.
           "drop": ["rama_Servicio doméstico"],
           "desc": "Depurada: E4 + categoría + tamaño empresa + dominio "
                   "(sin la dummy rama=Servicio doméstico, colineal perfecta "
                   "con categoría=Trabajador del hogar)", "interp": "alta"},
}

# Candidatas de E7 (Lasso) a nivel de modulo: 09_precomputar_ui.py las lee
# para la matriz especificacion x variable de la app.
E7_NUM = ["anios_educ", "exper", "exper2", "log_horas", "miembros"]
E7_CAT = ["sexo", "area", "dominio", "rama", "tamano_empresa", "categoria",
          "contrato"]

REJILLAS = {
    "E8": (RandomForestRegressor(random_state=SEMILLA, n_jobs=N_JOBS),
           {"regressor__modelo__n_estimators": [200, 400],
            "regressor__modelo__max_depth": [8, 12, None],
            "regressor__modelo__min_samples_leaf": [1, 5, 20]}),
    "E9": (GradientBoostingRegressor(random_state=SEMILLA),
           {"regressor__modelo__n_estimators": [200, 400],
            "regressor__modelo__learning_rate": [0.05, 0.1],
            "regressor__modelo__max_depth": [3, 5]}),
}
COLS_ARBOLES = ["anios_educ", "edad", "exper", "exper2", "horas_total",
                "sexo", "area", "dominio", "rama", "tamano_empresa", "categoria"]


def modelo_arbol(estimador) -> TransformedTargetRegressor:
    numericas = [c for c in COLS_ARBOLES if c not in
                 ("sexo", "area", "dominio", "rama", "tamano_empresa", "categoria")]
    categoricas = [c for c in COLS_ARBOLES if c not in numericas]
    pipe = Pipeline([("prep", construir_preprocesador(numericas, categoricas)),
                     ("modelo", clone(estimador))])
    return TransformedTargetRegressor(regressor=pipe, func=np.log1p,
                                      inverse_func=np.expm1)


# --------------------------------------------------------------------------
# Protocolo comun de evaluacion
# --------------------------------------------------------------------------
def evaluar_spec(clave: str, escala: str, estimador_z, X_tr, X_te, y_tr, y_te) -> dict:
    """
    estimador_z predice en la escala de ajuste: z=log1p(y) si escala='log',
    z=y si 'niveles'. Un solo cross_val_predict da MAE_cv y residuos OOF.
    """
    z_tr = np.log1p(y_tr) if escala == "log" else y_tr.astype(float)

    z_oof = cross_val_predict(estimador_z, X_tr, z_tr, cv=KF, n_jobs=N_JOBS)
    est = clone(estimador_z)
    est.fit(X_tr, z_tr)
    z_te = est.predict(X_te)

    if escala == "log":
        smear = float(np.mean(np.exp(z_tr - z_oof)))  # Duan con residuos OOF de train
        pred_cv_med = np.expm1(z_oof)
        pred_te_med = np.expm1(z_te)
        pred_te_media = np.exp(z_te) * smear - 1
        r2_propio = r2_score(np.log1p(y_te), z_te)
    else:
        smear = np.nan
        pred_cv_med = z_oof
        pred_te_med = z_te
        pred_te_media = z_te
        r2_propio = r2_score(y_te, z_te)

    return {
        "id": clave, "modelo_ajustado": est, "smearing": smear,
        "mae_cv": mean_absolute_error(y_tr, pred_cv_med),
        "mae_test": mean_absolute_error(y_te, pred_te_med),
        "mae_test_smear": mean_absolute_error(y_te, pred_te_media),
        "rmse_test": float(np.sqrt(mean_squared_error(y_te, pred_te_media))),
        "r2_test_soles": r2_score(y_te, pred_te_media),
        "r2_escala_propia": r2_propio,
        "pred_te_med": pred_te_med,
    }


def inferencia_ols(clave: str, X: pd.DataFrame, z: pd.Series, escala: str) -> None:
    """Coeficientes HC3, VIF y Breusch-Pagan sobre TRAIN; figuras de residuos."""
    Xc = sm.add_constant(X.astype(float))
    m = sm.OLS(z, Xc).fit(cov_type="HC3")
    vif = pd.Series({c: variance_inflation_factor(Xc.values, i)
                     for i, c in enumerate(Xc.columns) if c != "const"})
    bp = het_breuschpagan(m.resid, Xc)
    tabla = pd.DataFrame({"coef": m.params.round(4), "ee_HC3": m.bse.round(4),
                          "p": m.pvalues.round(4), "VIF": vif.round(2)})
    anotar(f"\n**{clave} — inferencia OLS en train (escala {escala}), "
           f"R² {m.rsquared:.4f}, Breusch-Pagan p={bp[1]:.2e}:**\n")
    anotar(formato_md(tabla, index=True))

    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.2))
    ejes[0].scatter(m.fittedvalues, m.resid, s=3, alpha=0.15, color="#3d6f9e",
                    edgecolors="none")
    ejes[0].axhline(0, ls="--", color="crimson", lw=1)
    ejes[0].set_xlabel("Ajustados"); ejes[0].set_ylabel("Residuos")
    ejes[0].set_title(f"{clave}: residuos vs ajustados")
    sm.qqplot(m.resid, line="45", fit=True, ax=ejes[1],
              markerfacecolor="#3d6f9e", markeredgecolor="none", markersize=2, alpha=0.3)
    ejes[1].set_title(f"{clave}: QQ de residuos")
    fig.tight_layout()
    fig.savefig(DIR_FIGURAS / f"02_ols_{clave}.png", dpi=130)
    plt.close(fig)


# --------------------------------------------------------------------------
def main() -> None:
    anotar("# FASE 2 — Torneo de especificaciones (regresión del ingreso)\n")
    anotar("Generado por `src/04_torneo_regresion.py`. Torneo SIN ponderar "
           "(comparación predictiva); la lectura poblacional ponderada vive en "
           "`reports/modelo_explicativo.md`.\n")

    df = cargar()
    y = df["ingreso_mes"]
    idx_tr, idx_te = train_test_split(df.index, test_size=0.2, random_state=SEMILLA)
    anotar(f"- Train {len(idx_tr):,} | Test {len(idx_te):,} | CV: KFold(5, shuffle, 42)")

    resultados = []

    # --- OLS E1-E6 ---
    for clave, spec in ESPECIFICACIONES.items():
        X = disenar(df, spec["num"], spec["cat"])
        X = X.drop(columns=[c for c in spec.get("drop", []) if c in X.columns])
        r = evaluar_spec(clave, spec["escala"], LinearRegression(),
                         X.loc[idx_tr], X.loc[idx_te], y.loc[idx_tr], y.loc[idx_te])
        r.update({"desc": spec["desc"], "interp": spec["interp"],
                  "n_vars": X.shape[1]})
        resultados.append(r)
        z_tr = np.log1p(y.loc[idx_tr]) if spec["escala"] == "log" else y.loc[idx_tr]
        inferencia_ols(clave, X.loc[idx_tr], z_tr, spec["escala"])

    # --- E7: Lasso + post-Lasso OLS ---
    anotar("\n## E7 — Lasso y post-Lasso\n")
    X7 = disenar(df, E7_NUM, E7_CAT)
    lasso = Pipeline([("esc", StandardScaler()),
                      ("modelo", LassoCV(cv=KF, random_state=SEMILLA, n_jobs=N_JOBS))])
    lasso.fit(X7.loc[idx_tr], np.log1p(y.loc[idx_tr]))
    coefs = pd.Series(lasso.named_steps["modelo"].coef_, index=X7.columns)
    sobreviven = coefs[coefs.abs() > 1e-6].index.tolist()
    anotar(f"- Candidatas: {X7.shape[1]} columnas; Lasso (alpha="
           f"{lasso.named_steps['modelo'].alpha_:.5f}) conserva {len(sobreviven)}.")
    anotar(f"- Eliminadas: {sorted(set(X7.columns) - set(sobreviven)) or 'ninguna'}")
    anotar("- Nota (Belloni et al. 2014): la selección se hizo una vez sobre el "
           "train completo; la inferencia post-Lasso es descriptiva, no formal.")
    X7p = X7[sobreviven]
    r7 = evaluar_spec("E7", "log", LinearRegression(),
                      X7p.loc[idx_tr], X7p.loc[idx_te], y.loc[idx_tr], y.loc[idx_te])
    r7.update({"desc": "Post-Lasso: OLS sobre las variables que Lasso conserva",
               "interp": "media", "n_vars": len(sobreviven)})
    resultados.append(r7)

    # --- E8/E9: arboles con grilla cacheada ---
    X_arb = df[COLS_ARBOLES]
    for clave in ("E8", "E9"):
        estimador, rejilla = REJILLAS[clave]

        def ejecutar_busqueda():
            t = time.perf_counter()
            b = GridSearchCV(modelo_arbol(estimador), rejilla, cv=KF,
                             scoring="neg_mean_absolute_error", n_jobs=N_JOBS,
                             refit=False)
            b.fit(X_arb.loc[idx_tr], y.loc[idx_tr])
            return b.best_params_, float(b.best_score_), time.perf_counter() - t

        params, score, seg, cache = busqueda_cacheada(f"torneo_{clave}",
                                                      ejecutar_busqueda)
        anotar(f"\n## {clave} — mejores hiperparámetros: `{params}` "
               f"(MAE grid S/ {-score:.1f}, {seg / 60:.1f} min"
               + (", caché)" if cache else ")"))

        base = modelo_arbol(estimador)
        base.set_params(**params)
        # el protocolo comun trabaja en escala z: se usa el pipeline interno
        interno = clone(base.regressor)
        r = evaluar_spec(clave, "log", interno, X_arb.loc[idx_tr],
                         X_arb.loc[idx_te], y.loc[idx_tr], y.loc[idx_te])
        r.update({"desc": ("Random Forest" if clave == "E8" else
                           "Gradient Boosting") + " (log target, pipeline sklearn)",
                  "interp": "baja", "n_vars": len(COLS_ARBOLES)})
        resultados.append(r)

    # --- Tabla del torneo ---
    tabla = pd.DataFrame([{
        "ID": r["id"], "especificacion": r["desc"],
        "MAE_cv": round(r["mae_cv"], 1), "MAE_test": round(r["mae_test"], 1),
        "MAE_test_media_smear": round(r["mae_test_smear"], 1),
        "RMSE_test": round(r["rmse_test"], 1),
        "R2_test_soles": round(r["r2_test_soles"], 3),
        "R2_escala_propia": round(r["r2_escala_propia"], 3),
        "smearing_Duan": round(r["smearing"], 3) if np.isfinite(r["smearing"]) else "",
        "n_vars": r["n_vars"], "interpretabilidad": r["interp"],
    } for r in resultados]).sort_values("MAE_cv")
    anotar("\n## Tabla del torneo (ordenada por MAE_cv, el criterio de selección)\n")
    anotar("La selección usa MAE_cv (5 pliegues en train): elegir por MAE de test "
           "tras comparar 9 especificaciones sería seleccionar sobre el conjunto "
           "de evaluación. MAE_test se reporta como estimación honesta del ya "
           "elegido. MAE en soles con inversión por mediana (expm1); la columna "
           "smear reporta la media condicional (Duan con residuos OOF de train).\n")
    anotar(formato_md(tabla))
    tabla.to_csv(DIR_REPORTS / "comparacion_torneo.csv", index=False)

    # Brecha OLS vs arboles
    mae = {r["id"]: r["mae_cv"] for r in resultados}
    mejor_ols = min(mae["E4"], mae["E6"])
    mejor_arbol = min(mae["E8"], mae["E9"])
    anotar(f"\n- Brecha E4/E6 vs E8/E9 en MAE_cv: S/ {mejor_ols - mejor_arbol:+.1f} "
           f"({100 * (mejor_ols - mejor_arbol) / mejor_ols:+.1f}%). Esta brecha "
           "estima el aporte de no linealidades e interacciones que la forma "
           "funcional lineal no captura (Athey & Imbens 2019).")

    # --- Sensibilidad: ingreso monetario vs monetario + especie (E4) ---
    anotar("\n## Sensibilidad al ingreso en especie (E4, dos targets)\n")
    X4 = disenar(df, ESPECIFICACIONES["E4"]["num"], ESPECIFICACIONES["E4"]["cat"])
    y_esp = df["ingreso_mes"] + df["especie_mes"]
    filas = []
    for nombre, target in [("solo monetario", y), ("monetario + especie", y_esp)]:
        m = sm.OLS(np.log1p(target.loc[idx_tr]),
                   sm.add_constant(X4.loc[idx_tr].astype(float))).fit(cov_type="HC3")
        filas.append({
            "target": nombre,
            "coef_urbano": round(m.params["urbano"], 4),
            "premio_urbano_pct": round(100 * (np.exp(m.params["urbano"]) - 1), 1),
            "coef_rama_agro": round(m.params.get("rama_Agropecuario y pesca", np.nan), 4),
            "coef_educ": round(m.params["anios_educ"], 4),
            "R2": round(m.rsquared, 4),
        })
    tabla_esp = pd.DataFrame(filas)
    anotar(formato_md(tabla_esp))
    delta = filas[0]["premio_urbano_pct"] - filas[1]["premio_urbano_pct"]
    anotar(f"- El premio urbano cae {delta:.1f} puntos porcentuales al incluir "
           "especie/autoconsumo. El modelo desplegado sigue siendo monetario "
           "(definición estándar), pero esta sensibilidad se publica.")

    (DIR_REPORTS / "torneo_regresion.md").write_text("\n".join(doc) + "\n",
                                                     encoding="utf-8")
    df.to_parquet(DIR_PROCESSED / "torneo_frame.parquet", index=False)
    pd.Series(idx_te).to_csv(DIR_PROCESSED / "indices_test.csv", index=False)
    print("\nEscrito: reports/torneo_regresion.md, reports/comparacion_torneo.csv")


if __name__ == "__main__":
    main()
