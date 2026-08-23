# 09_precomputar_ui.py — precómputo de los artefactos de la UI
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
# FASE 3 (parte 1) — Precomputo de los artefactos que consume la interfaz.
# Produce models/ui_artifacts.json. Mover el slider de umbral en la app no
# recalcula nada: lee una curva ya resuelta sobre probabilidades OUT-OF-FOLD
# de train. El script VERIFICA que esas probabilidades reproducen los umbrales
# publicados en el schema antes de escribir nada.
#
# Ponderacion (decision de Fase 1): los descriptivos de cohorte que muestra la
# app van PONDERADOS con FAC500A; las curvas del modelo (umbral, ROC, PR,
# calibracion) son muestrales porque describen al modelo, no a la poblacion.
import ast
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import statsmodels.api as sm
from sklearn.base import clone
from sklearn.inspection import partial_dependence, permutation_importance
from sklearn.metrics import (average_precision_score, precision_recall_curve,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import KFold, cross_val_predict, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (DIR_MODELS, DIR_PROCESSED, DIR_REPORTS, ETIQUETAS,
                   RUTA_SCHEMA, SEMILLA, escribir_json_atomico,
                   separar_columnas)
from importlib import import_module
torneo = import_module("04_torneo_regresion")

RAIZ = Path(__file__).resolve().parents[1]
RUTA_SALIDA = DIR_MODELS / "ui_artifacts.json"
RUTA_OOF = DIR_MODELS / "_oof_clasificador.npy"

N_JOBS = 8
N_PD = 5_000
N_PERM = 9_000
GRID_PD = 20
N_PUNTOS_CURVA = 200
# Paso de la curva de umbral. A 0,005 el slider se siente continuo: entre dos
# posiciones consecutivas las cifras de impacto ya cambian.
PASO_UMBRAL = 0.005
PERCENTILES = [5, 25, 50, 75, 95]
ETIQUETA_OTROS = "OTROS"
COLS_CLF = ["anios_educ", "edad", "exper", "exper2", "horas_total",
            "sexo", "area", "dominio", "rama", "tamano_empresa", "categoria"]


def log(msg: str = "") -> None:
    print(msg, flush=True)


def r(x, n=6):
    if isinstance(x, (list, tuple, np.ndarray)):
        return [r(v, n) for v in x]
    return round(float(x), n)


def pctl_pond(valores: np.ndarray, pesos: np.ndarray, qs: list[float]) -> list[float]:
    """Percentiles ponderados (interpolacion sobre la masa acumulada)."""
    orden = np.argsort(valores)
    v, w = np.asarray(valores)[orden], np.asarray(pesos)[orden]
    acum = np.cumsum(w) - 0.5 * w
    acum /= np.sum(w)
    return [float(np.interp(q / 100, acum, v)) for q in qs]


# --------------------------------------------------------------------------
# Curva de umbral (identica a la del SIS: sumas acumuladas, no 99 reevaluaciones)
# --------------------------------------------------------------------------
def curva_umbral(y, proba, extra=(), paso=PASO_UMBRAL) -> dict:
    y = np.asarray(y).astype(np.int64)
    umbrales = np.union1d(np.round(np.arange(0.01, 0.9901 + paso / 2, paso), 4),
                          np.round(np.asarray(list(extra), dtype=float), 6))
    umbrales = umbrales[(umbrales >= 0.01) & (umbrales <= 0.99)]
    positivos, negativos = int(y.sum()), int((1 - y).sum())

    orden = np.sort(proba)
    idx = np.searchsorted(orden, umbrales, side="left")
    predichos_pos = len(proba) - idx
    orden_pos = np.sort(proba[y == 1])
    tp = positivos - np.searchsorted(orden_pos, umbrales, side="left")
    fp = predichos_pos - tp
    fn = positivos - tp
    tn = negativos - fp

    with np.errstate(divide="ignore", invalid="ignore"):
        prec1 = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
        rec1 = np.where(positivos > 0, tp / positivos, 0.0)
        prec0 = np.where(tn + fn > 0, tn / (tn + fn), 0.0)
        rec0 = np.where(negativos > 0, tn / negativos, 0.0)

    return {
        "umbral": r(umbrales, 4),
        "tp": [int(v) for v in tp], "fp": [int(v) for v in fp],
        "tn": [int(v) for v in tn], "fn": [int(v) for v in fn],
        "precision_1": r(prec1, 5), "recall_1": r(rec1, 5),
        "precision_0": r(prec0, 5), "recall_0": r(rec0, 5),
        "n": int(len(proba)),
    }


def reproducir_umbrales(y, proba) -> dict:
    """Replica la eleccion de umbrales de 06 para verificar la curva."""
    prec, rec, thr = precision_recall_curve(y, proba)
    f1 = 2 * prec[:-1] * rec[:-1] / np.clip(prec[:-1] + rec[:-1], 1e-9, None)
    validos = np.where(prec[:-1] >= 0.90)[0]
    i = validos[np.argmax(rec[validos])]
    return {"f1_optimo": float(thr[np.argmax(f1)]),
            "precision_090": float(thr[i])}


def submuestrear(*arrays, n=N_PUNTOS_CURVA):
    largo = len(arrays[0])
    idx = (np.arange(largo) if largo <= n
           else np.unique(np.linspace(0, largo - 1, n).astype(int)))
    return [np.asarray(a)[idx] for a in arrays]


def curva_calibracion(y, proba, bins=10) -> dict:
    bordes = np.linspace(0.0, 1.0, bins + 1)
    cual = np.clip(np.digitize(proba, bordes[1:-1], right=False), 0, bins - 1)
    filas = []
    for b in range(bins):
        m = cual == b
        if not m.any():
            continue
        filas.append({"bin": b, "proba_media": r(proba[m].mean(), 5),
                      "frecuencia_observada": r(np.asarray(y)[m].mean(), 5),
                      "n": int(m.sum())})
    return {"bins": filas}


def histograma_por_clase(y, proba, bins=50) -> dict:
    bordes = np.linspace(0.0, 1.0, bins + 1)
    y = np.asarray(y)
    h1, _ = np.histogram(proba[y == 1], bins=bordes)
    h0, _ = np.histogram(proba[y == 0], bins=bordes)
    return {"bordes": r(bordes, 4),
            "clase_1": [int(v) for v in h1],
            "clase_0": [int(v) for v in h0]}


def distribucion_cohorte(X: pd.DataFrame, pesos: pd.Series,
                         features_schema: list[dict]) -> dict:
    """Percentiles PONDERADOS para numericas; masa ponderada para categoricas."""
    salida = {}
    w_total = float(pesos.sum())
    for feat in features_schema:
        col = feat["nombre"]
        if col not in X.columns:
            continue
        if feat["tipo"] == "numerico":
            s = pd.to_numeric(X[col], errors="coerce")
            m = s.notna()
            pct = pctl_pond(s[m].to_numpy(), pesos[m].to_numpy(), PERCENTILES)
            salida[col] = {
                "tipo": "numerico", "ponderado": True,
                "percentiles": {str(p): r(v, 3) for p, v in zip(PERCENTILES, pct)},
                "media": r(np.average(s[m], weights=pesos[m]), 3),
                "n": int(m.sum()),
            }
        else:
            opciones = set(feat.get("opciones", []))
            s = X[col].astype(str)
            if ETIQUETA_OTROS in opciones:
                s = s.where(s.isin(opciones), ETIQUETA_OTROS)
            masa = pesos.groupby(s).sum().sort_values(ascending=False)
            salida[col] = {
                "tipo": "categorico", "ponderado": True,
                "participacion_pct": {str(k): r(100 * v / w_total, 2)
                                      for k, v in masa.items()},
                "n": int(len(s)),
            }
    return salida


def tasas_observadas(df: pd.DataFrame, features_schema: list[dict]) -> dict:
    """
    Tasa de informalidad OBSERVADA por categoria, ponderada y cruda.

    No confundir con la dependencia parcial: aquella estima el efecto de mover
    una variable con el resto promediado (ceteris paribus), esta cuenta lo que
    hay en la muestra. Para un titulo del tipo "la informalidad es mas alta en
    el campo" la cifra honesta es la observada; el efecto parcial responde otra
    pregunta y da otro numero. La app las usa en sitios distintos y lo dice.
    """
    salida = {}
    for feat in features_schema:
        col = feat["nombre"]
        if feat["tipo"] != "categorico" or col not in df.columns:
            continue
        opciones = set(feat.get("opciones", []))
        s = df[col].astype(str)
        if ETIQUETA_OTROS in opciones:
            s = s.where(s.isin(opciones), ETIQUETA_OTROS)
        grupos = {}
        for val, g in df.groupby(s, observed=True):
            w = g["FAC500A"]
            grupos[str(val)] = {
                "pct_ponderado": r(100 * (g["informal"] * w).sum() / w.sum(), 2),
                "pct_crudo": r(100 * g["informal"].mean(), 2),
                "n": int(len(g)),
            }
        if len(grupos) >= 2:
            orden = sorted(grupos.items(), key=lambda kv: kv[1]["pct_ponderado"])
            salida[col] = {
                "grupos": grupos,
                "min": {"categoria": orden[0][0], **orden[0][1]},
                "max": {"categoria": orden[-1][0], **orden[-1][1]},
            }
    return salida


def colapsar_a_opciones(X: pd.DataFrame, features_schema: list[dict]) -> pd.DataFrame:
    X = X.copy()
    for feat in features_schema:
        col, opciones = feat["nombre"], set(feat.get("opciones", []))
        if feat["tipo"] != "categorico" or col not in X.columns:
            continue
        if ETIQUETA_OTROS in opciones:
            s = X[col].astype(str)
            X[col] = s.where(s.isin(opciones), ETIQUETA_OTROS)
    return X


def dependencia_parcial(modelo, X: pd.DataFrame, es_clasificador: bool,
                        features_schema: list[dict]) -> dict:
    muestra = X.sample(min(N_PD, len(X)), random_state=SEMILLA)
    muestra = colapsar_a_opciones(muestra, features_schema)
    _, categoricas = separar_columnas(muestra)
    # partial_dependence rechaza enteros (redondeo implicito): todo a float
    for c in muestra.columns:
        if c not in categoricas:
            muestra[c] = muestra[c].astype(float)
    cat = [c for c in muestra.columns if c in set(categoricas)]

    salida = {}
    for col in muestra.columns:
        t0 = time.perf_counter()
        res = partial_dependence(
            modelo, muestra, features=[col],
            categorical_features=cat or None,
            grid_resolution=GRID_PD,
            response_method="predict_proba" if es_clasificador else "auto",
            kind="average")
        valores = list(res["grid_values"][0])
        salida[col] = {
            "tipo": "categorico" if col in set(cat) else "numerico",
            "valores": [str(v) for v in valores] if col in set(cat) else r(valores, 4),
            "efecto": r(np.asarray(res["average"])[0], 6),
        }
        log(f"    {col:<18} {len(valores):>3} puntos ({time.perf_counter() - t0:.1f}s)")
    return salida


def importancia_permutada(modelo, X, y, scoring: str) -> dict:
    n = min(N_PERM, len(X))
    Xs = X.sample(n, random_state=SEMILLA)
    ys = y.loc[Xs.index]
    perm = permutation_importance(modelo, Xs, ys, scoring=scoring, n_repeats=5,
                                  random_state=SEMILLA, n_jobs=N_JOBS)
    orden = np.argsort(perm.importances_mean)[::-1]
    return {"scoring": scoring, "n_filas": int(n), "n_repeticiones": 5,
            "variables": [str(X.columns[i]) for i in orden],
            "media": r(perm.importances_mean[orden], 6),
            "desviacion": r(perm.importances_std[orden], 6)}


def hash_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAIZ,
                             capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except Exception:
        return None


# --------------------------------------------------------------------------
# Bloque "variables": matriz especificacion x variable, Lasso E7 y descartadas
# --------------------------------------------------------------------------
# Derivadas de spec -> variable conceptual (una fila por variable, no por dummy)
NORMALIZA_VAR = {"hombre": "sexo", "urbano": "area", "log_horas": "horas",
                 "horas_total": "horas", "primaria": "nivel_educ",
                 "secundaria": "nivel_educ", "tecnica": "nivel_educ",
                 "universitaria": "nivel_educ"}
ORDEN_VARIABLES = ["anios_educ", "nivel_educ", "edad", "exper", "exper2",
                   "sexo", "area", "horas", "miembros", "dominio", "rama",
                   "tamano_empresa", "categoria", "contrato"]
ETIQUETAS_MATRIZ = ETIQUETAS | {
    "nivel_educ": "Nivel educativo (dummies)",
    "exper2": "Experiencia² (años²)",
    "horas": "Horas semanales (log u horas según spec)",
    "miembros": "Miembros del hogar",
    "contrato": "Tipo de contrato",
}


def artefactos_variables() -> dict:
    """Matriz leida de las specs REALES de 04, Lasso E7 leido del reporte."""
    specs = {k: set(v["num"]) | set(v["cat"])
             for k, v in torneo.ESPECIFICACIONES.items()}
    specs["E7"] = set(torneo.E7_NUM) | set(torneo.E7_CAT)
    specs["E8"] = set(torneo.COLS_ARBOLES)
    specs["E9"] = set(torneo.COLS_ARBOLES)
    orden_espec = [f"E{i}" for i in range(1, 10)]
    normalizadas = {e: {NORMALIZA_VAR.get(c, c) for c in cols}
                    for e, cols in specs.items()}
    sobran = set().union(*normalizadas.values()) - set(ORDEN_VARIABLES)
    if sobran:
        raise SystemExit(f"Variables de las specs sin fila en la matriz: {sobran}")
    filas = [{"variable": v,
              "etiqueta": ETIQUETAS_MATRIZ.get(v, v),
              "entra": {e: v in normalizadas[e] for e in orden_espec}}
             for v in ORDEN_VARIABLES]

    # Lasso E7: numeros del reporte generado por 04 (no se recalcula aqui)
    texto = (DIR_REPORTS / "torneo_regresion.md").read_text(encoding="utf-8")
    m = re.search(r"Candidatas: (\d+) columnas; Lasso \(alpha=([0-9.]+)\) "
                  r"conserva (\d+)\.", texto)
    m2 = re.search(r"- Eliminadas: (\[[^\]]*\])", texto)
    if not (m and m2):
        raise SystemExit("No se pudo leer el bloque E7 de reports/torneo_regresion.md")
    eliminadas = ast.literal_eval(m2.group(1))

    descartadas = [
        {"nombre": "«Índice de bienestar» (INGHOG2D; y derivados GASHOG2D, POBREZA)",
         "motivo": "Circularidad mecánica: el ingreso individual es un sumando "
                   "del ingreso del hogar (ρ Spearman 0,575; 0,619 per cápita). "
                   "Excluido de todo modelo.",
         "evidencia": "reports/00_autopsia_baseline.md §5"},
        {"nombre": "P511A — tipo de contrato",
         "motivo": "Cuasi-definicional de la informalidad para asalariados "
                   "(AUC univariado 0,846): prohibida en el clasificador. En la "
                   "regresión solo participa como candidata de E7.",
         "evidencia": "reports/01_preparacion_fase1.md"},
        {"nombre": "Centinela 999999 (nota: no es una variable)",
         "motivo": "Código de faltante del INEI en variables monetarias, leído "
                   "como valor real en el baseline; convertido a NaN antes de "
                   "todo cálculo (R² 0,023 → 0,248 al limpiarlo).",
         "evidencia": "reports/00_autopsia_baseline.md §1–2"},
        {"nombre": "TFNR — trabajadores familiares no remunerados",
         "motivo": "Restricción de población, no variable: 6.500 ocupados con "
                   "ingreso = 0 quedan fuera de la población de modelado "
                   "(informales por definición; la prevalencia lo declara).",
         "evidencia": "reports/01_preparacion_fase1.md"},
    ]

    return {
        "matriz": {"especificaciones": orden_espec, "filas": filas},
        "nota_matriz": ("Leída de las especificaciones de "
                        "src/04_torneo_regresion.py. E7: columnas candidatas al "
                        "Lasso (la selección decide cuáles quedan). E6 suelta la "
                        "dummy rama=Servicio doméstico, colineal perfecta con "
                        "categoría=Trabajador del hogar."),
        "lasso_e7": {
            "candidatas": int(m.group(1)),
            "alpha": float(m.group(2)),
            "conservadas": int(m.group(3)),
            "eliminadas": eliminadas,
            "drop_manual_e6": list(torneo.ESPECIFICACIONES["E6"].get("drop", [])),
            "fuente": "reports/torneo_regresion.md",
        },
        "descartadas": descartadas,
    }


# --------------------------------------------------------------------------
# Seccion torneo: la narrativa en tres actos con numeros CALCULADOS
# --------------------------------------------------------------------------
def artefactos_torneo(df: pd.DataFrame) -> dict:
    # Acto 1-2: la autopsia se recalcula desde el parquet de Fase 0 (rapido)
    aut = pd.read_parquet(RAIZ / "data" / "interim" / "fase0_autopsia.parquet")
    xcols = ["urbano", "hombre", "edad", "primaria", "secundaria", "tecnica",
             "universitaria", "horas", "miembros"]

    def ols(ycol):
        d = aut[[ycol] + xcols].dropna().astype(float)
        m = sm.OLS(d[ycol], sm.add_constant(d[xcols])).fit(cov_type="HC3")
        return {"r2": r(m.rsquared, 4), "n": int(len(d)),
                "coefs": {k: r(v, 2) for k, v in m.params.items()}}

    corrida_a, corrida_b = ols("INGRESO_A"), ols("INGRESO_B")
    n_cent = int(aut["INGRESO_A"].isin([999999, 999999.9]).sum())
    asimetria = r(aut["INGRESO_B"].dropna().skew(), 2)

    # Ecuacion inicial del curso: el punto de partida del proyecto. El fallo
    # que destapo estaba en los datos del INEI, no en su modelado.
    baseline_curso = {"const": 653.35, "urbano": 11.47, "hombre": 6.39, "edad": 16.11,
                 "primaria": 691.92, "secundaria": 1386.35, "tecnica": 2132.97,
                 "universitaria": 2834.57, "horas": 18.76, "miembros": 6.98}

    # Acto 3: sensibilidad al ingreso en especie (E4, dos targets) y E6 ponderada
    idx_tr, _ = train_test_split(df.index, test_size=0.2, random_state=SEMILLA)
    spec4 = torneo.ESPECIFICACIONES["E4"]
    X4 = torneo.disenar(df, spec4["num"], spec4["cat"])
    sensibilidad = []
    for nombre, y in [("solo monetario", df["ingreso_mes"]),
                      ("monetario + especie", df["ingreso_mes"] + df["especie_mes"])]:
        m = sm.OLS(np.log1p(y.loc[idx_tr]),
                   sm.add_constant(X4.loc[idx_tr].astype(float))).fit(cov_type="HC3")
        sensibilidad.append({"target": nombre,
                             "premio_urbano_pct": r(100 * (np.exp(m.params["urbano"]) - 1), 1),
                             "coef_educ_pct": r(100 * (np.exp(m.params["anios_educ"]) - 1), 1),
                             "r2": r(m.rsquared, 4)})

    spec6 = torneo.ESPECIFICACIONES["E6"]
    X6 = torneo.disenar(df, spec6["num"], spec6["cat"])
    X6 = X6.drop(columns=[c for c in spec6.get("drop", []) if c in X6.columns])
    m6 = sm.WLS(np.log1p(df["ingreso_mes"]), sm.add_constant(X6.astype(float)),
                weights=df["FAC500A"]).fit(cov_type="HC3")
    efectos6 = {k: r(100 * (np.exp(v) - 1), 1) for k, v in m6.params.items()
                if k != "const"}

    tabla = pd.read_csv(DIR_REPORTS / "comparacion_torneo.csv")
    return {
        "tabla": json.loads(tabla.to_json(orient="records")),
        "desplegada": "E9",
        "explicativa": "E6",
        "autopsia": {
            "corrida_sucia": corrida_a, "corrida_limpia": corrida_b,
            "n_centinelas": n_cent,
            "pct_centinelas": r(100 * n_cent / len(aut), 2),
            "asimetria_limpia": asimetria,
            "ecuacion_inicial": baseline_curso,
            "nota": ("La réplica se corrió sobre los microdatos reales de la "
                     "ENAHO 2025, no sobre el archivo de práctica del curso."),
        },
        "sensibilidad_especie": sensibilidad,
        "explicativo_e6_ponderado": {"r2": r(m6.rsquared, 4), "efectos_pct": efectos6},
        "variables": artefactos_variables(),
    }


# --------------------------------------------------------------------------
def main() -> None:
    schema = json.loads(RUTA_SCHEMA.read_text(encoding="utf-8"))
    artefactos: dict = {}

    df = pd.read_parquet(DIR_PROCESSED / "torneo_frame.parquet")

    # ================= CLASIFICADOR =================
    clas = schema["clasificador"]
    log("CLASIFICADOR — empleo informal (clasificador_gb.joblib)")
    modelo_a = joblib.load(DIR_MODELS / "clasificador_gb.joblib")

    dfc = df.dropna(subset=["informal"])
    y_a = dfc["informal"].astype(int)
    X_a = dfc[COLS_CLF]
    idx_tr, idx_te = train_test_split(dfc.index, test_size=0.2,
                                      random_state=SEMILLA, stratify=y_a)
    X_tr, X_te = X_a.loc[idx_tr], X_a.loc[idx_te]
    y_tr, y_te = y_a.loc[idx_tr], y_a.loc[idx_te]
    log(f"  train {len(X_tr):,} | test {len(X_te):,}")

    proba_oof = None
    if RUTA_OOF.exists():
        guardado = np.load(RUTA_OOF)
        if len(guardado) == len(X_tr):
            proba_oof = guardado.astype(np.float64)
            log("  OOF recuperadas de cache")
    if proba_oof is None:
        log("  probabilidades out-of-fold (5 pliegues)...")
        kf = KFold(n_splits=5, shuffle=True, random_state=SEMILLA)
        proba_oof = cross_val_predict(clone(modelo_a), X_tr, y_tr, cv=kf,
                                      n_jobs=N_JOBS, pre_dispatch="n_jobs",
                                      method="predict_proba")[:, 1]
        np.save(RUTA_OOF, proba_oof.astype(np.float32))

    # Verificacion contra el schema antes de publicar la curva
    recalc = reproducir_umbrales(y_tr.to_numpy(), proba_oof)
    publicados = {
        "precision_090": clas["punto_operativo"]["umbral"],
        "f1_optimo": clas["punto_operativo"]["referencias"]["f1_optimo"]["umbral"],
    }
    log(f"  umbrales recalculados: {recalc}")
    log(f"  umbrales publicados  : {publicados}")
    desvio = {k: (recalc[k], publicados[k]) for k in publicados
              if abs(recalc[k] - publicados[k]) > 1e-3}
    if desvio:
        raise SystemExit(f"Las OOF no reproducen los umbrales publicados: {desvio}. "
                         "Se aborta sin escribir nada.")
    log("  -> reproducen los umbrales publicados")

    proba_te = modelo_a.predict_proba(X_te)[:, 1]
    fpr, tpr, _ = roc_curve(y_te, proba_te)
    fpr, tpr = submuestrear(fpr, tpr)
    prec, rec, _ = precision_recall_curve(y_te, proba_te)
    prec, rec = submuestrear(prec, rec)

    log("  dependencia parcial:")
    pd_a = dependencia_parcial(modelo_a, X_tr, True, clas["features"])
    log("  importancia por permutacion...")
    imp_a = importancia_permutada(modelo_a, X_te, y_te, "average_precision")

    extra = [0.5, publicados["f1_optimo"], publicados["precision_090"]]
    artefactos["clasificador"] = {
        "algoritmo": "gb",
        "curva_umbral": curva_umbral(y_tr.to_numpy(), proba_oof, extra=extra),
        # Franja de probabilidad de la app: el fondo es la distribucion OOF de
        # los 38.105 del entrenamiento. 60 bins es el detalle que se distingue
        # a simple vista sin engordar el JSON.
        "histograma_oof": histograma_por_clase(y_tr.to_numpy(), proba_oof,
                                               bins=60),
        "curva_umbral_origen": "OOF sobre train (5 pliegues); el test no decide nada.",
        "roc": {"fpr": r(fpr, 5), "tpr": r(tpr, 5),
                "auc": r(roc_auc_score(y_te, proba_te), 4)},
        "pr": {"recall": r(rec, 5), "precision": r(prec, 5),
               "auc": r(average_precision_score(y_te, proba_te), 4),
               "baseline": r(float(y_te.mean()), 4)},
        "calibracion": curva_calibracion(y_te.to_numpy(), proba_te),
        "histograma_probabilidades": histograma_por_clase(y_te.to_numpy(), proba_te),
        "dependencia_parcial": pd_a,
        "importancia_permutacion": imp_a,
        "cohorte": distribucion_cohorte(X_a, dfc["FAC500A"], clas["features"]),
        "tasas_observadas": tasas_observadas(dfc, clas["features"]),
        "comparacion": json.loads(pd.read_csv(
            DIR_REPORTS / "comparacion_clasificador.csv").to_json(orient="records")),
    }

    # ================= REGRESOR =================
    reg = schema["regresor"]
    log("\nREGRESOR — ingreso laboral (regresor_e9.joblib)")
    modelo_b = joblib.load(DIR_MODELS / "regresor_e9.joblib")
    y_b = df["ingreso_mes"]
    X_b = df[torneo.COLS_ARBOLES]
    idx_trb, idx_teb = train_test_split(df.index, test_size=0.2, random_state=SEMILLA)

    log("  dependencia parcial:")
    pd_b = dependencia_parcial(modelo_b, X_b.loc[idx_trb], False, reg["features"])
    log("  importancia por permutacion...")
    imp_b = importancia_permutada(modelo_b, X_b.loc[idx_teb], y_b.loc[idx_teb],
                                  "neg_mean_absolute_error")

    # IQR de casos comparables: sexo x area x banda educativa, PONDERADO
    bandas = pd.cut(df["anios_educ"], bins=[-0.1, 6, 11, 14, 25],
                    labels=["0-6", "7-11", "12-14", "15+"])
    comparables = {}
    for (sexo, area, banda), g in df.groupby(["sexo", "area", bandas],
                                             observed=True):
        if len(g) < 100:
            continue
        p25, p50, p75 = pctl_pond(g["ingreso_mes"].to_numpy(),
                                  g["FAC500A"].to_numpy(), [25, 50, 75])
        comparables[f"{sexo}|{area}|{banda}"] = {
            "p25": r(p25, 0), "p50": r(p50, 0), "p75": r(p75, 0), "n": int(len(g))}

    mediana_pond = pctl_pond(y_b.to_numpy(), df["FAC500A"].to_numpy(), [50])[0]
    artefactos["regresor"] = {
        "algoritmo": "e9",
        "dependencia_parcial": pd_b,
        "importancia_permutacion": imp_b,
        "cohorte": distribucion_cohorte(X_b, df["FAC500A"], reg["features"]),
        "ingreso": {
            "mediana_ponderada": r(mediana_pond, 0),
            "mediana_test": r(float(np.median(y_b.loc[idx_teb])), 0),
            "media_test": r(float(np.mean(y_b.loc[idx_teb])), 0),
            "bandas_educ": ["0-6", "7-11", "12-14", "15+"],
            "comparables": comparables,
            "nota_comparables": ("Percentiles 25-75 ponderados (FAC500A) por "
                                 "sexo × área × banda de años de educación."),
        },
    }

    # ================= TORNEO =================
    log("\nTORNEO — narrativa y tablas...")
    artefactos["torneo"] = artefactos_torneo(df)

    # ================= META =================
    artefactos["meta"] = {
        "generado_por": "src/09_precomputar_ui.py",
        "fecha_generacion": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "version_scikit_learn": sklearn.__version__,
        "version_pandas": pd.__version__,
        "commit": hash_commit(),
        "ponderacion": ("Cohortes y comparables ponderados con FAC500A; curvas "
                        "del modelo muestrales; entrenamiento sin ponderar."),
    }

    escribir_json_atomico(
        RUTA_SALIDA,
        json.dumps(artefactos, ensure_ascii=False, separators=(",", ":")))
    kb = RUTA_SALIDA.stat().st_size / 1024
    log(f"\n{RUTA_SALIDA.name}: {kb:.1f} KB")
    if kb > 500:
        log("*** AVISO: supera el objetivo de 500 KB ***")


if __name__ == "__main__":
    main()
