# contexto.py — lectura de models/ui_contexto.json y del GeoJSON de departamentos
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
La app solo LEE lo que precomputó src/10_contexto.py. Si el archivo falta
(clon sin correr la Fase 3), `cargar()` devuelve {} y las secciones muestran
un aviso en vez de caerse.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

DIR_MODELS = Path(__file__).resolve().parents[1] / "models"
RUTA = DIR_MODELS / "ui_contexto.json"
RUTA_GEO = DIR_MODELS / "peru_departamentos.geojson"

# Brechas por lengua materna: calculadas, pero no se publican hasta que el
# autor las revise (encargo de la v2, D-16). En True aparece su bloque en
# «Investigación».
MOSTRAR_LENGUA = False


def _firma(ruta: Path) -> tuple:
    if not ruta.exists():
        return ()
    s = ruta.stat()
    return (s.st_size, int(s.st_mtime))


@st.cache_data(show_spinner=False)
def _leer(ruta: str, firma: tuple) -> dict:
    # `firma` invalida la caché cuando cambia el archivo.
    p = Path(ruta)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def cargar() -> dict:
    return _leer(str(RUTA), _firma(RUTA))


def cargar_geo() -> dict:
    return _leer(str(RUTA_GEO), _firma(RUTA_GEO))
