# -*- coding: utf-8 -*-
# verificacion_local.py — comprobar en VS Code lo mismo que muestra la app
# ---------------------------------------------------------------------------
# Autor: Yoichi Palacios Tanaka (IchiSieben) — proyecto ENAHO 2025
# Licencia: Apache-2.0 (ver LICENSE)
# ---------------------------------------------------------------------------
"""
Requisito de la guía del curso: los resultados del modelo corridos desde
VS Code deben coincidir con los del modelo desplegado en Streamlit.

Este script carga los MISMOS artefactos que usa la app (models/*.joblib,
models/feature_schema.json) y predice con el MISMO perfil por defecto del
formulario (los `default` del schema). La app hace exactamente esto:

  - regresor:      pred = modelo.predict(fila)[0]          -> «ingreso típico»
                   media = (pred + 1) * smearing - 1        -> «ingreso esperado»
  - clasificador:  proba = modelo.predict_proba(fila)[:, 1][0]

Correr:  .venv/Scripts/python.exe docs/presentacion/verificacion_local.py
"""
from pathlib import Path
import json

import joblib
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
MODELS = RAIZ / "models"

schema = json.loads((MODELS / "feature_schema.json").read_text(encoding="utf-8"))


def perfil_por_defecto(features: list[dict]) -> pd.DataFrame:
    """El perfil que el formulario de la app muestra al abrir."""
    return pd.DataFrame([{f["nombre"]: f["default"] for f in features}])


def columnas_esperadas(modelo) -> list[str]:
    for obj in (modelo, getattr(modelo, "named_steps", {}).get("regressor")):
        if obj is None:
            continue
        nombres = getattr(obj, "feature_names_in_", None)
        if nombres is not None:
            return list(nombres)
        prep = getattr(obj, "named_steps", {}).get("prep")
        if prep is not None and hasattr(prep, "feature_names_in_"):
            return list(prep.feature_names_in_)
    raise RuntimeError("El modelo no declara feature_names_in_")


def main() -> None:
    reg = schema["regresor"]
    fila = perfil_por_defecto(reg["features"])
    print("=== Verificación VS Code = Streamlit — ENAHO 2025 ===")
    print("\nPerfil (defaults del formulario):")
    for k, v in fila.iloc[0].items():
        print(f"  {k:16s} = {v}")

    modelo = joblib.load(MODELS / "regresor_e9.joblib")
    pred = float(modelo.predict(fila[columnas_esperadas(modelo)])[0])
    smear = float(reg["smearing_duan"])
    media = (pred + 1) * smear - 1
    print("\n[REGRESOR E9 — Gradient Boosting]")
    print(f"  ingreso típico  (mediana): S/ {pred:,.0f}".replace(",", "."))
    print(f"  ingreso esperado (media aplicando smearing {smear}): "
          f"S/ {media:,.0f}".replace(",", "."))

    cla = schema["clasificador"]
    fila_clf = perfil_por_defecto(cla["features"])  # defaults propios (horas=46)
    clf = joblib.load(MODELS / "clasificador_gb.joblib")
    proba = float(clf.predict_proba(fila_clf[columnas_esperadas(clf)])[:, 1][0])
    umbral = cla["punto_operativo"]["umbral"]
    print("\n[CLASIFICADOR GB — empleo informal]")
    print(f"  probabilidad de informalidad: {proba:.1%}".replace(".", ","))
    print(f"  umbral operativo (precisión >= 0,90): {umbral}")
    print(f"  veredicto: {'INFORMAL' if proba >= umbral else 'FORMAL'}")


if __name__ == "__main__":
    main()
