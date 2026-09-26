# test_fase5.py — QA de cierre de la v1.2.0: bilingüe, artefactos y contratos
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))
APP = (RAIZ / "app" / "streamlit_app.py").read_text(encoding="utf-8")
RUTA_CTX = RAIZ / "models" / "ui_contexto.json"


# --------------------------------------------------------------------------
# ui_artifacts.json es intocable: ni una coma (regla del encargo).
# --------------------------------------------------------------------------
def test_ui_artifacts_intacto():
    ruta = RAIZ / "models" / "ui_artifacts.json"
    if not ruta.exists():
        pytest.skip("no hay models/ui_artifacts.json en este entorno")
    datos = ruta.read_bytes()
    assert len(datos) == 45815
    assert hashlib.sha256(datos).hexdigest().startswith("be5122b589ef")


# --------------------------------------------------------------------------
# Referencias: toda cita y toda nota existen en los dos idiomas.
# --------------------------------------------------------------------------
def test_toda_referencia_es_bilingue():
    import referencias
    for r in referencias.REFERENCIAS:
        for k in ("cita", "cita_en", "nota", "nota_en"):
            assert r.get(k, "").strip(), (r["id"], k)
        # La nota en inglés es una traducción, no una copia de la española.
        assert r["nota_en"] != r["nota"], r["id"]


# --------------------------------------------------------------------------
# ui_contexto.json: cifras finitas, intervalos bien formados y claves que la
# app lee presentes.
# --------------------------------------------------------------------------
def _ctx() -> dict:
    if not RUTA_CTX.exists():
        pytest.skip("no hay models/ui_contexto.json en este entorno")
    return json.loads(RUTA_CTX.read_text(encoding="utf-8"))


def _estimaciones(o, ruta=""):
    if isinstance(o, dict):
        if "valor" in o:
            yield ruta, o
            return
        for k, v in o.items():
            yield from _estimaciones(v, f"{ruta}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from _estimaciones(v, f"{ruta}/{i}")


def test_contexto_cifras_finitas_e_intervalos_ordenados():
    ests = list(_estimaciones(_ctx()))
    assert len(ests) > 50
    for ruta, e in ests:
        assert isinstance(e["valor"], (int, float)) and math.isfinite(e["valor"]), ruta
        if "ic95" in e:
            lo, hi = e["ic95"]
            assert math.isfinite(lo) and math.isfinite(hi) and lo <= hi, ruta
        if "ee" in e:
            assert e["ee"] >= 0, ruta


def test_la_app_solo_lee_claves_que_el_contexto_trae():
    ctx = _ctx()
    leidas = set(re.findall(r'ctx\["([a-z_]+)"\]', APP))
    leidas |= set(re.findall(r'ctx\.get\("([a-z_]+)"', APP))
    assert leidas, "no se encontraron lecturas de ctx en la app"
    assert leidas <= set(ctx), leidas - set(ctx)


# --------------------------------------------------------------------------
# Glosario: todo término que la app usa existe y está en los dos idiomas.
# --------------------------------------------------------------------------
def test_todo_termino_usado_existe():
    import glosario
    usados = set(re.findall(r"termino\(['\"]([a-z]+)['\"]", APP))
    assert usados, "la app no usa el glosario"
    assert usados <= set(glosario.TERMINOS), usados - set(glosario.TERMINOS)


# --------------------------------------------------------------------------
# Textos bilingües: ningún L(es, en) nuevo con el mismo texto en los dos
# idiomas, salvo nombres propios y siglas.
# --------------------------------------------------------------------------
def test_l_con_dos_textos_distintos_en_las_secciones_nuevas():
    i = APP.index("def etiqueta_afirmacion(")
    j = APP.index("def pie_creditos(")
    pares = re.findall(r'L\(\s*"([^"]+)",\s*"([^"]+)"\s*\)', APP[i:j])
    assert len(pares) > 30
    iguales = [a for a, b in pares if a == b and re.search(r"[a-záéíóúñ]{4,}", a)
               and not re.fullmatch(r"[A-ZÑ][\w\-ñ]+(\s\(\d{4}\))?", a)]
    assert not iguales, iguales
