# 06_entrenar_clasificador.py — clasificador de empleo informal
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
# FASE 2b — Clasificador de empleo informal (informal=1, clase MAYORITARIA).
#
# Baseline obligado: regresion logistica con odds ratios. Luego RF y GB con
# grilla acotada. Seleccion por PR-AUC de validacion cruzada (misma disciplina
# que el torneo: nunca por test). Umbrales sobre probabilidades OUT-OF-FOLD de
# train (cross_val_predict); el test solo estima honestamente el punto elegido.
#
# Regimen de recursos acordado (la maquina ya se colgo dos veces en este
# portafolio): N_JOBS=8, pre_dispatch='n_jobs', max_depth acotado en RF,
# estimadores internos con n_jobs=1 durante la busqueda. La cache de
# hiperparametros se escribe en disco tras CADA algoritmo (busqueda_cacheada).
#
# ADVERTENCIA DOCUMENTADA (ficha tecnica): P507/categoria RAMIFICA la regla del
# target (independiente->RUC, dependiente->pension). No es circular —no
# determina el target por si sola (AUC univ. 0,805)— pero saldra con
# importancia alta POR CONSTRUCCION: no es un hallazgo.
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
from sklearn.calibration import calibration_curve
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             f1_score, precision_recall_curve, roc_auc_score)
from sklearn.model_selection import GridSearchCV, KFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (DIR_FIGURAS, DIR_MODELS, DIR_PROCESSED, DIR_REPORTS,
                   SEMILLA, busqueda_cacheada, construir_preprocesador,
                   extraer_features, formato_md, guardar_con_limite,
                   guardar_schema, separar_columnas)
from importlib import import_module
torneo = import_module("04_torneo_regresion")

N_JOBS = 8                       # regimen conservador para esta corrida
KF = KFold(n_splits=5, shuffle=True, random_state=SEMILLA)
COLS = ["anios_educ", "edad", "exper", "exper2", "horas_total",
        "sexo", "area", "dominio", "rama", "tamano_empresa", "categoria"]

REJILLAS = {
    "rf": (RandomForestClassifier(random_state=SEMILLA, n_jobs=1),
           {"modelo__n_estimators": [200, 400],
            "modelo__max_depth": [8, 12, 16],          # acotada: nada de None
            "modelo__min_samples_leaf": [5, 20]}),
    "gb": (GradientBoostingClassifier(random_state=SEMILLA),
           {"modelo__n_estimators": [200, 400],
            "modelo__learning_rate": [0.05, 0.1],
            "modelo__max_depth": [3, 5]}),
}
NOMBRES = {"logit": "Regresión logística", "rf": "Random Forest",
           "gb": "Gradient Boosting"}

doc: list[str] = []


def anotar(t: str = "") -> None:
    print(t, flush=True)
    doc.append(t)


def pipeline_arbol(estimador) -> Pipeline:
    numericas, categoricas = separar_columnas(pd.DataFrame(columns=COLS).astype(
        {c: float for c in COLS[:5]} | {c: object for c in COLS[5:]}))
    return Pipeline([("prep", construir_preprocesador(numericas, categoricas)),
                     ("modelo", clone(estimador))])


def evaluar(nombre, pipe, X_tr, y_tr, X_te, y_te) -> dict:
    t0 = time.perf_counter()
    p_oof = cross_val_predict(pipe, X_tr, y_tr, cv=KF, n_jobs=N_JOBS,
                              pre_dispatch="n_jobs",
                              method="predict_proba")[:, 1]
    est = clone(pipe)
    est.fit(X_tr, y_tr)
    p_te = est.predict_proba(X_te)[:, 1]
    return {
        "nombre": nombre, "modelo": est, "p_oof": p_oof, "p_te": p_te,
        "prauc_cv": average_precision_score(y_tr, p_oof),
        "roc_cv": roc_auc_score(y_tr, p_oof),
        "prauc_test": average_precision_score(y_te, p_te),
        "roc_test": roc_auc_score(y_te, p_te),
        "brier_test": brier_score_loss(y_te, p_te),
        "min": (time.perf_counter() - t0) / 60,
    }


def puntos_operativos(y, p, prevalencia) -> pd.DataFrame:
    """Umbral 0,5, F1 optimo y precision >= 0,90/0,85/0,80, con lift."""
    prec, rec, thr = precision_recall_curve(y, p)
    filas = []

    def fila(nombre, umbral):
        yhat = (p >= umbral).astype(int)
        tp = ((yhat == 1) & (y == 1)).sum()
        fp = ((yhat == 1) & (y == 0)).sum()
        fn = ((yhat == 0) & (y == 1)).sum()
        precision = tp / (tp + fp) if tp + fp else np.nan
        recall = tp / (tp + fn)
        return {"punto": nombre, "umbral": round(float(umbral), 4),
                "precision": round(precision, 3), "recall": round(recall, 3),
                "lift": round(precision / prevalencia, 2),
                "señalados_por_1000": int(round(1000 * yhat.mean())),
                "F1": round(f1_score(y, yhat), 3)}

    filas.append(fila("umbral 0,5", 0.5))
    f1s = 2 * prec[:-1] * rec[:-1] / np.clip(prec[:-1] + rec[:-1], 1e-9, None)
    filas.append(fila("F1 óptimo", thr[np.argmax(f1s)]))
    for objetivo in (0.90, 0.85, 0.80):
        validos = np.where(prec[:-1] >= objetivo)[0]
        if len(validos):
            i = validos[np.argmax(rec[validos])]     # mayor recall que cumple
            filas.append(fila(f"precisión ≥ {objetivo:.2f}", thr[i]))
        else:
            filas.append({"punto": f"precisión ≥ {objetivo:.2f} (inalcanzable)",
                          "umbral": np.nan})
    return pd.DataFrame(filas)


def main() -> None:
    anotar("# FASE 2b — Clasificador de empleo informal\n")
    anotar("Generado por `src/06_entrenar_clasificador.py`. Predictores "
           "estructurales compartidos con la regresión; SIN ingreso y SIN las "
           "columnas que definen el target (P510A1, P558A*, P511A).\n")

    df = pd.read_parquet(DIR_PROCESSED / "torneo_frame.parquet")
    df = df.dropna(subset=["informal"])
    y = df["informal"].astype(int)
    X = df[COLS]

    idx_tr, idx_te = train_test_split(df.index, test_size=0.2,
                                      random_state=SEMILLA, stratify=y)
    X_tr, X_te = X.loc[idx_tr], X.loc[idx_te]
    y_tr, y_te = y.loc[idx_tr], y.loc[idx_te]
    prevalencia = float(y_tr.mean())
    w = df["FAC500A"]
    prev_pond = float((y * w).sum() / w.sum())
    anotar(f"- {len(df):,} filas | Train {len(idx_tr):,} / Test {len(idx_te):,} "
           "(estratificado por el target)")
    anotar(f"- Prevalencia informal: {prevalencia:.3f} muestral (train) | "
           f"{prev_pond:.3f} ponderada FAC500A. El baseline de PR-AUC es la "
           "prevalencia; el lift se calcula contra la muestral.")

    resultados = []

    # --- Logistica: protocolo sklearn + odds ratios statsmodels ---
    Xl = torneo.disenar(df, ["anios_educ", "exper", "exper2", "horas_total"],
                        ["sexo", "area", "dominio", "rama", "tamano_empresa",
                         "categoria"])
    # misma colinealidad perfecta que en E6 (P507=6 <-> CIIU 97): sin este drop
    # los OR de ambas dummies salen con IC 0-inf
    Xl = Xl.drop(columns=["rama_Servicio doméstico"], errors="ignore")
    pipe_logit = Pipeline([("esc", StandardScaler()),
                           ("modelo", LogisticRegression(max_iter=2000,
                                                         random_state=SEMILLA))])
    r = evaluar("logit", pipe_logit, Xl.loc[idx_tr], y_tr, Xl.loc[idx_te], y_te)
    resultados.append(r)

    m = sm.Logit(y_tr, sm.add_constant(Xl.loc[idx_tr].astype(float))).fit(disp=0)
    ic = m.conf_int()
    tabla_or = pd.DataFrame({
        "odds_ratio": np.exp(m.params).round(3),
        "IC95_inf": np.exp(ic[0]).round(3),
        "IC95_sup": np.exp(ic[1]).round(3),
        "p": m.pvalues.round(4),
    }).drop(index="const")
    anotar("\n## Regresión logística — odds ratios (train, sin estandarizar)\n")
    anotar("OR>1 = mayor propensión a la informalidad vs la base (Mujer, Rural, "
           "Lima Metropolitana, Comercio, empresa >500, Empleado).\n")
    anotar(formato_md(tabla_or.sort_values("odds_ratio", ascending=False), index=True))

    # --- RF y GB ---
    for clave in ("rf", "gb"):
        estimador, rejilla = REJILLAS[clave]

        def ejecutar_busqueda():
            t = time.perf_counter()
            b = GridSearchCV(pipeline_arbol(estimador), rejilla, cv=KF,
                             scoring="average_precision", n_jobs=N_JOBS,
                             pre_dispatch="n_jobs", refit=False)
            b.fit(X_tr, y_tr)
            return b.best_params_, float(b.best_score_), time.perf_counter() - t

        params, score, seg, cache = busqueda_cacheada(f"clasif_{clave}",
                                                      ejecutar_busqueda)
        anotar(f"\n## {NOMBRES[clave]} — `{params}` (PR-AUC grid {score:.4f}, "
               f"{seg / 60:.1f} min{', caché' if cache else ''})")

        pipe = pipeline_arbol(estimador)
        pipe.set_params(**params)
        # RF queda con n_jobs=1: cross_val_predict ya paraleliza con N_JOBS=8
        # y anidar paralelismo (8x8 hilos) es lo que colgo la maquina antes.
        r = evaluar(clave, pipe, X_tr, y_tr, X_te, y_te)
        resultados.append(r)

    # --- Tabla comparativa ---
    tabla = pd.DataFrame([{
        "algoritmo": NOMBRES[r["nombre"]],
        "PRAUC_cv": round(r["prauc_cv"], 4), "ROCAUC_cv": round(r["roc_cv"], 4),
        "PRAUC_test": round(r["prauc_test"], 4),
        "ROCAUC_test": round(r["roc_test"], 4),
        "Brier_test": round(r["brier_test"], 4),
        "min": round(r["min"], 1),
    } for r in resultados]).sort_values("PRAUC_cv", ascending=False)
    anotar(f"\n## Comparación (baseline PR-AUC = prevalencia = {prevalencia:.3f})\n")
    anotar("Selección por PR-AUC de validación cruzada, no por test (misma "
           "disciplina que el torneo).\n")
    anotar(formato_md(tabla))
    tabla.to_csv(DIR_REPORTS / "comparacion_clasificador.csv", index=False)

    ganador = max(resultados, key=lambda r: r["prauc_cv"])
    anotar(f"- Ganador por PR-AUC_cv: **{NOMBRES[ganador['nombre']]}**")

    # --- Puntos operativos sobre OOF de train ---
    anotar("\n## Puntos operativos (probabilidades out-of-fold de train)\n")
    puntos = puntos_operativos(y_tr.to_numpy(), ganador["p_oof"], prevalencia)
    anotar(formato_md(puntos))
    anotar("\nLectura para decidir: la clase accionable es informal=1 "
           "(focalización de formalización) y es mayoritaria, así que el lift "
           "honesto contra prevalencia importa más que la precisión suelta.")

    # Estimacion honesta en test de los mismos umbrales
    anotar("\n**Mismos umbrales aplicados al test (estimación honesta):**\n")
    puntos_test = []
    for _, p in puntos.iterrows():
        if not np.isfinite(p["umbral"]):
            continue
        yhat = (ganador["p_te"] >= p["umbral"]).astype(int)
        tp = int(((yhat == 1) & (y_te == 1)).sum())
        fp = int(((yhat == 1) & (y_te == 0)).sum())
        fn = int(((yhat == 0) & (y_te == 1)).sum())
        puntos_test.append({"punto": p["punto"], "umbral": p["umbral"],
                            "precision_test": round(tp / (tp + fp), 3),
                            "recall_test": round(tp / (tp + fn), 3)})
    anotar(formato_md(pd.DataFrame(puntos_test)))

    # --- Figuras: PR, calibracion ---
    prec, rec, _ = precision_recall_curve(y_tr, ganador["p_oof"])
    fig, ejes = plt.subplots(1, 2, figsize=(12, 4.6))
    ejes[0].plot(rec, prec, color="#3d6f9e", lw=1.6,
                 label=f"{NOMBRES[ganador['nombre']]} (OOF train)")
    ejes[0].axhline(prevalencia, ls="--", color="gray", lw=1,
                    label=f"Prevalencia = {prevalencia:.3f}")
    for obj, color in [(0.90, "crimson"), (0.85, "#c07b4a"), (0.80, "#2e8b6f")]:
        fila = puntos[puntos["punto"].str.contains(f"{obj:.2f}")]
        if len(fila) and np.isfinite(fila.iloc[0].get("umbral", np.nan)):
            ejes[0].scatter(fila.iloc[0]["recall"], fila.iloc[0]["precision"],
                            color=color, zorder=5, s=40,
                            label=f"prec≥{obj:.2f}: recall {fila.iloc[0]['recall']:.2f}")
    ejes[0].set_xlabel("Recall (informales detectados)")
    ejes[0].set_ylabel("Precisión")
    ejes[0].set_title("Curva precisión-recall — clase informal")
    ejes[0].legend(fontsize=8)

    for r, color in [(ganador, "#3d6f9e"), (resultados[0], "#c07b4a")]:
        frac, medio = calibration_curve(y_te, r["p_te"], n_bins=10)
        ejes[1].plot(medio, frac, "o-", ms=3, lw=1.2, color=color,
                     label=NOMBRES[r["nombre"]])
    ejes[1].plot([0, 1], [0, 1], "--", color="gray", lw=1)
    ejes[1].set_xlabel("Probabilidad predicha")
    ejes[1].set_ylabel("Fracción informal observada")
    ejes[1].set_title("Calibración (test)")
    ejes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(DIR_FIGURAS / "03_pr_calibracion.png", dpi=130)
    plt.close(fig)

    # --- Importancia por permutacion (ganador, validacion apartada) ---
    if ganador["nombre"] != "logit":
        X_fit, X_val, y_fit, y_val = train_test_split(
            X_tr, y_tr, test_size=0.2, random_state=SEMILLA, stratify=y_tr)
        mv = clone(ganador["modelo"])
        mv.fit(X_fit, y_fit)
        perm = permutation_importance(mv, X_val, y_val,
                                      scoring="average_precision", n_repeats=5,
                                      random_state=SEMILLA, n_jobs=N_JOBS)
        imp = pd.Series(perm.importances_mean, index=COLS).sort_values(ascending=False)
        anotar("\n## Importancia por permutación (caída de PR-AUC, validación)\n")
        anotar("`categoria` (P507) ramifica la definición del target "
               "(independiente→RUC, dependiente→pensión): su importancia alta es "
               "POR CONSTRUCCIÓN, no un hallazgo (nota de la ficha técnica).\n")
        anotar(formato_md(pd.DataFrame({"caida_prauc": imp.round(4)}), index=True))
        fig, eje = plt.subplots(figsize=(7, 4.2))
        imp.sort_values().plot.barh(ax=eje, color="#c07b4a")
        eje.set_xlabel("Caída de PR-AUC al permutar")
        eje.set_title("Importancia por permutación — clasificador")
        fig.tight_layout()
        fig.savefig(DIR_FIGURAS / "03_importancia_clasificador.png", dpi=130)
        plt.close(fig)

    # --- Artefacto + schema (el umbral operativo se fija tras la decision) ---
    ruta = DIR_MODELS / f"clasificador_{ganador['nombre']}.joblib"
    mb = guardar_con_limite(ganador["modelo"], ruta)
    anotar(f"\n- Artefacto `{ruta.name}`: {mb:.1f} MB (compress=3)")
    if ganador["nombre"] != "logit":
        guardar_schema("clasificador", {
            "target": "informal",
            "descripcion_target": "Empleo informal (regla INEI derivada: "
                                  "independiente/empleador sin RUC; dependiente "
                                  "sin afiliación a pensión). Validada contra la "
                                  "tasa oficial 2025.",
            "algoritmo_recomendado": ganador["nombre"],
            "prevalencia_train": round(prevalencia, 4),
            "prevalencia_ponderada": round(prev_pond, 4),
            "metricas_test": {"prauc": round(ganador["prauc_test"], 4),
                              "rocauc": round(ganador["roc_test"], 4),
                              "brier": round(ganador["brier_test"], 4)},
            "puntos_operativos_oof": puntos.to_dict(orient="records"),
            "n_entrenamiento": int(len(idx_tr)), "n_test": int(len(idx_te)),
            "features": extraer_features(ganador["modelo"], X_tr),
        })
        anotar("- Contrato del clasificador escrito en `models/feature_schema.json`")

    (DIR_REPORTS / "clasificador_informalidad.md").write_text(
        "\n".join(doc) + "\n", encoding="utf-8")
    print("\nEscrito: reports/clasificador_informalidad.md")


if __name__ == "__main__":
    main()
