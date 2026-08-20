# 08_ablacion_clasificador.py — ablación estructural del clasificador
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
# FASE 2b (cierre) — Ablacion estructural del clasificador y fijado del punto
# operativo en el schema.
#
# Pregunta: ¿cuanto del PR-AUC 0,96 viene de variables casi definicionales?
# tamano_empresa y categoria son las mas proximas a la regla del target (en
# microempresas no aportar a pensiones es casi estructural). Variantes con el
# MISMO protocolo (GB con los hiperparametros ganadores, mismo split y KFold):
#   completa | V1: sin tamano_empresa | V2: sin tamano_empresa ni categoria
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import KFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (DIR_MODELS, DIR_PROCESSED, DIR_REPORTS, RUTA_CACHE_PARAMS,
                   RUTA_SCHEMA, SEMILLA, construir_preprocesador,
                   escribir_json_atomico, extraer_features, formato_md,
                   guardar_con_limite)

N_JOBS = 8
KF = KFold(n_splits=5, shuffle=True, random_state=SEMILLA)
NUMERICAS = ["anios_educ", "edad", "exper", "exper2", "horas_total"]
CATEGORICAS = ["sexo", "area", "dominio", "rama", "tamano_empresa", "categoria"]

VARIANTES = {
    "completa": [],
    "V1: sin tamano_empresa": ["tamano_empresa"],
    "V2: sin tamano_empresa ni categoria": ["tamano_empresa", "categoria"],
}


def main() -> None:
    df = pd.read_parquet(DIR_PROCESSED / "torneo_frame.parquet").dropna(subset=["informal"])
    y = df["informal"].astype(int)
    idx_tr, idx_te = train_test_split(df.index, test_size=0.2,
                                      random_state=SEMILLA, stratify=y)
    y_tr, y_te = y.loc[idx_tr], y.loc[idx_te]

    params = json.loads(RUTA_CACHE_PARAMS.read_text(encoding="utf-8"))["clasif_gb"]["params"]
    params = {k.replace("modelo__", ""): v for k, v in params.items()}
    print(f"GB con hiperparametros ganadores fijos: {params}\n")

    filas, modelos = [], {}
    for nombre, quitar in VARIANTES.items():
        num = [c for c in NUMERICAS if c not in quitar]
        cat = [c for c in CATEGORICAS if c not in quitar]
        X = df[num + cat]
        pipe = Pipeline([
            ("prep", construir_preprocesador(num, cat)),
            ("modelo", GradientBoostingClassifier(random_state=SEMILLA, **params)),
        ])
        p_oof = cross_val_predict(pipe, X.loc[idx_tr], y_tr, cv=KF, n_jobs=N_JOBS,
                                  pre_dispatch="n_jobs", method="predict_proba")[:, 1]
        pipe.fit(X.loc[idx_tr], y_tr)
        p_te = pipe.predict_proba(X.loc[idx_te])[:, 1]
        filas.append({
            "variante": nombre, "n_predictores": len(num) + len(cat),
            "PRAUC_cv": round(average_precision_score(y_tr, p_oof), 4),
            "ROCAUC_cv": round(roc_auc_score(y_tr, p_oof), 4),
            "PRAUC_test": round(average_precision_score(y_te, p_te), 4),
            "ROCAUC_test": round(roc_auc_score(y_te, p_te), 4),
        })
        modelos[nombre] = (pipe, X)
        print(filas[-1])

    tabla = pd.DataFrame(filas)
    base = tabla.iloc[0]
    tabla["caida_PRAUC_cv"] = (base["PRAUC_cv"] - tabla["PRAUC_cv"]).round(4)

    # Mejor variante reducida (V1 salvo empate practico)
    mejor_red = tabla.iloc[1:].sort_values("PRAUC_cv", ascending=False).iloc[0]
    pipe_red, X_red = modelos[mejor_red["variante"]]
    mb = guardar_con_limite(pipe_red, DIR_MODELS / "clasificador_gb_reducido.joblib")
    print(f"\nGuardado clasificador_gb_reducido.joblib ({mejor_red['variante']}, {mb:.1f} MB)")

    # --- Reporte ---
    md = ["\n## Ablación estructural (tamano_empresa / categoria)\n",
          "Las dos variables dominantes son las más próximas a la definición "
          "operativa del target: en microempresas, no aportar a pensiones es "
          "casi estructural — el tamaño no predice la informalidad, en buena "
          "medida ES el mecanismo. Mismo protocolo (GB ganador, split y KFold "
          "idénticos):\n",
          formato_md(tabla),
          "\nEncuadre: el clasificador NO es una herramienta de predicción a "
          "futuro. La informalidad se determina por la configuración del empleo "
          "(tamaño de empresa, categoría ocupacional, rama), que se conoce al "
          "mismo tiempo que el estatus. Su utilidad es de FOCALIZACIÓN: "
          "identificar segmentos donde concentrar programas de formalización a "
          "partir de variables observables en registros administrativos, sin "
          "verificar caso por caso la afiliación a pensiones. Dicho así, el "
          "PR-AUC alto es coherente y esperable, no sospechoso.\n",
          # Los tramos del INEI (1-10, 11-50, >50) NO son los de este proyecto
          # (Hasta 20, 21-50, 51-100, 101-500, Mas de 500). El gradiente va en
          # el mismo sentido, que es lo que valida la regla, pero las cifras no
          # son comparables una a una y hay que decirlo: al resumir esta frase
          # sin el tramo se leia el 88,6 % como si fuera el dato propio de
          # «Hasta 20», que vale 81,1 % (auditoria 20/08/2026, AC-5).
          "\nValidación externa adicional: el gradiente por tamaño de empresa "
          "va en el mismo sentido que el patrón oficial del INEI, que reporta "
          "88,6 % de informalidad en empresas de 1-10 trabajadores, 44 % en "
          "11-50 y 15,6 % en más de 50 [INEI, Producción y empleo informal en "
          "el Perú: Cuenta Satélite de la Economía Informal 2022-2024, 2025]. "
          "Los tramos de esa publicación no coinciden con los de este "
          "proyecto, así que las cifras no son directamente comparables: lo "
          "que se valida es la dirección y la magnitud del gradiente, no la "
          "coincidencia de cada valor.\n"]
    with open(DIR_REPORTS / "clasificador_informalidad.md", "a", encoding="utf-8") as f:
        f.write("\n".join(md))
    tabla.to_csv(DIR_REPORTS / "ablacion_clasificador.csv", index=False)

    # --- Punto operativo al schema (sin pisar el resto de la seccion) ---
    schema = json.loads(RUTA_SCHEMA.read_text(encoding="utf-8"))
    schema["clasificador"]["punto_operativo"] = {
        "criterio": "precisión ≥ 0,90 para la clase informal (aprobado 14/08/2026)",
        "umbral": 0.6054,
        "precision_oof": 0.900, "recall_oof": 0.893, "lift": 1.33,
        "frase_exposicion": "De cada 1.000 trabajadores señalados, 900 son "
                            "efectivamente informales, frente a 678 si se "
                            "señalara al azar (lift 1,33x).",
        "referencias": {"umbral_05": {"umbral": 0.5, "precision": 0.881,
                                      "recall": 0.929, "F1": 0.904},
                        "f1_optimo": {"umbral": 0.4324, "precision": 0.871,
                                      "recall": 0.943, "F1": 0.906}},
    }
    schema["clasificador"]["ablacion"] = tabla.to_dict(orient="records")
    schema["clasificador"]["encuadre"] = (
        "Herramienta de focalización, no de predicción a futuro: identifica la "
        "configuración laboral asociada a la informalidad desde variables "
        "observables en registros administrativos.")
    schema["clasificador_reducido"] = {
        "variante": str(mejor_red["variante"]),
        "metricas": {k: float(mejor_red[k]) for k in
                     ["PRAUC_cv", "ROCAUC_cv", "PRAUC_test", "ROCAUC_test"]},
        "features": extraer_features(pipe_red, X_red.loc[idx_tr]),
    }
    escribir_json_atomico(RUTA_SCHEMA,
                          json.dumps(schema, indent=2, ensure_ascii=False))
    print("Punto operativo y ablación escritos en feature_schema.json")


if __name__ == "__main__":
    main()
