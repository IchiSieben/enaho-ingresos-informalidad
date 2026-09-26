# test_perfil_azar.py — «Perfil al azar» solo arma combinaciones válidas
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))
SCHEMA = json.loads((RAIZ / "models" / "feature_schema.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("modelo", ["regresor", "clasificador"])
def test_doscientos_sorteos_validos(modelo):
    import streamlit_app as app
    features = SCHEMA[modelo]["features"]
    rng = random.Random(1234)
    for _ in range(200):
        v = app.perfil_al_azar(features, rng)
        for f in features:
            if f["nombre"] in app.DERIVADAS:
                assert f["nombre"] not in v          # las calcula la app
            elif f["tipo"] == "numerico":
                assert f["min"] <= v[f["nombre"]] <= f["max"]
            else:
                assert v[f["nombre"]] in f["opciones"]
        # Experiencia potencial nunca negativa.
        assert v["edad"] - v["anios_educ"] - 6 >= 0


def test_semilla_inyectable_es_determinista():
    import streamlit_app as app
    features = SCHEMA["regresor"]["features"]
    assert (app.perfil_al_azar(features, random.Random(7))
            == app.perfil_al_azar(features, random.Random(7)))
