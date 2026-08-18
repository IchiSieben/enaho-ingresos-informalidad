# 07_guardar_regresor.py — refit y guardado del regresor E9
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
# FASE 2 (cierre) — Refit y guardado del regresor desplegado: E9 (GB, log
# target) con los hiperparametros cacheados del torneo. Guarda el artefacto,
# el factor de smearing (residuos OOF de train) y el contrato de features.
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict, train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (DIR_MODELS, DIR_PROCESSED, RUTA_CACHE_PARAMS, SEMILLA,
                   extraer_features, guardar_con_limite, guardar_schema)
from importlib import import_module
torneo = import_module("04_torneo_regresion")

N_JOBS = 8


def main() -> None:
    df = pd.read_parquet(DIR_PROCESSED / "torneo_frame.parquet")
    y = df["ingreso_mes"]
    X = df[torneo.COLS_ARBOLES]
    idx_tr, idx_te = train_test_split(df.index, test_size=0.2, random_state=SEMILLA)

    params = json.loads(RUTA_CACHE_PARAMS.read_text(encoding="utf-8"))["torneo_E9"]["params"]
    modelo = torneo.modelo_arbol(GradientBoostingRegressor(random_state=SEMILLA))
    modelo.set_params(**params)

    # Smearing de Duan con residuos out-of-fold de TRAIN (nunca test)
    kf = KFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    interno = clone(modelo.regressor)
    z_tr = np.log1p(y.loc[idx_tr])
    z_oof = cross_val_predict(interno, X.loc[idx_tr], z_tr, cv=kf, n_jobs=N_JOBS,
                              pre_dispatch="n_jobs")
    smearing = float(np.mean(np.exp(z_tr - z_oof)))

    modelo.fit(X.loc[idx_tr], y.loc[idx_tr])           # TTR: predice en soles (mediana)
    pred_med = modelo.predict(X.loc[idx_te])
    pred_media = (pred_med + 1) * smearing - 1
    mae = mean_absolute_error(y.loc[idx_te], pred_med)
    print(f"MAE test (mediana): S/ {mae:.1f} | smearing {smearing:.3f}")

    ruta = DIR_MODELS / "regresor_e9.joblib"
    mb = guardar_con_limite(modelo, ruta)
    print(f"Artefacto {ruta.name}: {mb:.1f} MB")

    guardar_schema("regresor", {
        "target": "ingreso_mes",
        "descripcion_target": "Ingreso laboral mensual monetario (suma de las "
                              "versiones imputadas/deflactadas/anualizadas del "
                              "INEI / 12: ingreso suavizado, no el del mes de "
                              "referencia). Solo ocupados con ingreso > 0.",
        "algoritmo_recomendado": "E9 Gradient Boosting (log target)",
        "smearing_duan": round(smearing, 4),
        "nota_smearing": "predict() devuelve la MEDIANA condicional (expm1); "
                         "la media condicional = (pred+1)*smearing_duan - 1 "
                         "(Duan 1983, residuos OOF de train).",
        "metricas_test": {
            "mae_mediana": round(float(mae), 1),
            "mae_media_smear": round(float(mean_absolute_error(y.loc[idx_te], pred_media)), 1),
            "rmse_media_smear": round(float(np.sqrt(mean_squared_error(y.loc[idx_te], pred_media))), 1),
            "r2_soles": round(float(r2_score(y.loc[idx_te], pred_media)), 3),
        },
        "n_entrenamiento": int(len(idx_tr)), "n_test": int(len(idx_te)),
        "ingreso_mediano_train": round(float(y.loc[idx_tr].median()), 1),
        "features": extraer_features(modelo.regressor_, X.loc[idx_tr]),
    })
    print("Schema del regresor escrito en models/feature_schema.json")


if __name__ == "__main__":
    main()
