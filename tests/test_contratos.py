# test_contratos.py — los tres contratos que se rompieron en producción
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
"""
Reproduce sin navegador los tres fallos del despliegue del 20/08/2026.

Los tres tienen la misma forma: `streamlit_app.py` pide algo (un tema, una
función de dibujo, una clave del artefacto) que su proveedor no tiene. En la
app eso salta a mitad del render, cuando ya es tarde; aquí salta en un test.

    python -m pytest tests/ -q
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))

import estilos          # noqa: E402
import graficos         # noqa: E402
from estilos import PALETAS  # noqa: E402


# --------------------------------------------------------------------------
# Bug 1 — KeyError: 'terminal'
# --------------------------------------------------------------------------
def test_toda_opcion_de_tema_existe_en_paletas():
    """
    El widget ofrecía tres temas escritos a mano mientras PALETAS tenía otros.
    Elegir el que faltaba dejaba la app inaccesible: T() reventaba en cada
    ejecución, incluso antes de poder volver a tocar el selector.
    """
    from streamlit_app import opciones_tema
    faltan = [t for t in opciones_tema() if t not in PALETAS]
    assert not faltan, f"el selector ofrece temas que no existen: {faltan}"


def test_tema_por_defecto_es_valido():
    from streamlit_app import TEMA_POR_DEFECTO
    assert TEMA_POR_DEFECTO in PALETAS


def test_los_temas_comparten_estructura():
    """Un token que falte en un tema revienta solo al cambiar a ese tema."""
    estructuras = {t: frozenset(p) for t, p in PALETAS.items()}
    referencia = estructuras[next(iter(estructuras))]
    for tema, claves in estructuras.items():
        assert claves == referencia, (
            f"al tema «{tema}» le faltan {sorted(referencia - claves)} "
            f"y le sobran {sorted(claves - referencia)}")


@pytest.mark.parametrize("tema", sorted(PALETAS))
def test_cada_tema_genera_su_css(tema):
    css = estilos.css(PALETAS[tema])
    assert "<style>" in css and PALETAS[tema]["fondo"] in css


# --------------------------------------------------------------------------
# Bug 2 — AttributeError: module 'graficos' has no attribute ...
# --------------------------------------------------------------------------
def test_graficos_expone_lo_que_la_app_usa():
    """
    La app llamaba a `graficos.franja_probabilidad` y el módulo servido no la
    tenía. Este test compara la lista declarada contra el módulo real.
    """
    from streamlit_app import GRAFICOS_REQUERIDOS
    faltan = [f for f in GRAFICOS_REQUERIDOS if not hasattr(graficos, f)]
    assert not faltan, f"graficos.py no expone: {faltan}"


def test_la_app_no_llama_a_graficos_fuera_del_contrato():
    """Si alguien añade una llamada nueva, que el contrato se entere."""
    import re
    from streamlit_app import GRAFICOS_REQUERIDOS
    fuente = (RAIZ / "app" / "streamlit_app.py").read_text(encoding="utf-8")
    llamadas = set(re.findall(r"graficos\.(\w+)\(", fuente))
    fuera = llamadas - set(GRAFICOS_REQUERIDOS)
    assert not fuera, (
        f"la app llama a {sorted(fuera)} sin declararlo en GRAFICOS_REQUERIDOS")


# --------------------------------------------------------------------------
# Bug 3 — KeyError: 'ecuacion_inicial'
# --------------------------------------------------------------------------
def _artefactos() -> dict:
    ruta = RAIZ / "models" / "ui_artifacts.json"
    if not ruta.exists():
        pytest.skip("no hay models/ui_artifacts.json en este entorno")
    return json.loads(ruta.read_text(encoding="utf-8"))


def test_el_artefacto_trae_las_claves_que_la_app_exige():
    """
    Se renombró `ecuacion_companera` a `ecuacion_inicial` en el código y en el
    artefacto, pero la app siguió sirviendo un artefacto viejo desde la caché.
    """
    from streamlit_app import validar_artefactos
    validar_artefactos(_artefactos())   # levanta con mensaje claro si falta algo


def test_validar_artefactos_detecta_la_clave_vieja():
    """El caso real: artefacto con el nombre anterior."""
    from streamlit_app import validar_artefactos
    art = _artefactos()
    aut = art["torneo"]["autopsia"]
    aut["ecuacion_companera"] = aut.pop("ecuacion_inicial")
    with pytest.raises(KeyError, match="ecuacion_inicial"):
        validar_artefactos(art)


def test_validar_artefactos_detecta_bloque_ausente():
    from streamlit_app import validar_artefactos
    art = _artefactos()
    del art["clasificador"]["tasas_observadas"]
    with pytest.raises(KeyError, match="tasas_observadas"):
        validar_artefactos(art)


# --------------------------------------------------------------------------
# El fallo de fondo: artefacto en caché mientras el de disco ya cambió
# --------------------------------------------------------------------------
def test_la_carga_se_invalida_cuando_el_archivo_cambia(tmp_path, monkeypatch):
    """
    Los tres bugs sobrevivieron a varios redespliegues porque el proceso servía
    estado viejo. Para el artefacto, la carga tiene que depender de la versión
    del archivo, no solo de que la función no cambie.
    """
    import streamlit_app as app
    ruta = tmp_path / "ui_artifacts.json"
    monkeypatch.setattr(app, "DIR_MODELS", tmp_path)

    ruta.write_text(json.dumps({"v": 1}), encoding="utf-8")
    v1 = app.firma_artefactos()
    ruta.write_text(json.dumps({"v": 2, "relleno": "x" * 50}), encoding="utf-8")
    v2 = app.firma_artefactos()
    assert v1 != v2, "la firma no cambia al cambiar el archivo: la caché se queda pegada"


# --------------------------------------------------------------------------
# Sala de máquinas — el artefacto hermano (ui_maquinas.json)
# --------------------------------------------------------------------------
# Va en archivo aparte porque la presentación congelada cita el tamaño en
# disco de ui_artifacts.json: ese archivo no puede crecer. Mismos contratos:
# que exista lo que la sección dibuja, y que el embudo publicado cuadre.
def _maquinas() -> dict:
    ruta = RAIZ / "models" / "ui_maquinas.json"
    if not ruta.exists():
        pytest.skip("no hay models/ui_maquinas.json en este entorno")
    return json.loads(ruta.read_text(encoding="utf-8"))


def test_maquinas_trae_lo_que_la_sala_exige():
    maq = _maquinas()
    claves = [e["clave"] for e in maq["embudo"]["etapas"]]
    assert claves == ["crudo", "ocupados", "modelado", "torneo"]
    assert {"train", "test"} <= set(maq["embudo"]["split"])
    assert "modelos_bytes" in maq["tamanos"]


def test_la_carga_sirve_el_archivo_nuevo_no_la_cache(tmp_path, monkeypatch):
    """
    El agujero que quedaba del bug 3: st.cache_data EXCLUYE de la clave de
    caché los parámetros que empiezan con guion bajo, así que `_firma` nunca
    invalidó nada — la firma cambiaba y la caché devolvía el dict viejo igual
    (en Cloud, tras un redespliegue en caliente, la app mostraba los datos del
    artefacto anterior con el código nuevo). Este test lee, cambia el archivo
    y exige ver el contenido nuevo.
    """
    import streamlit_app as app
    monkeypatch.setattr(app, "DIR_MODELS", tmp_path)
    ruta = tmp_path / "ui_maquinas.json"

    ruta.write_text(json.dumps({"version": 1}), encoding="utf-8")
    assert app.cargar_maquinas()["version"] == 1
    ruta.write_text(json.dumps({"version": 2, "relleno": "x" * 60}),
                    encoding="utf-8")
    assert app.cargar_maquinas()["version"] == 2, (
        "la caché sirvió el artefacto viejo pese a que el archivo cambió: "
        "¿el parámetro de la firma vuelve a llamarse `_firma`?")


def test_el_embudo_publicado_cuadra():
    """Cada recorte debe explicar exactamente la diferencia entre etapas."""
    emb = _maquinas()["embudo"]
    etapas = emb["etapas"]
    for previa, actual in zip(etapas, etapas[1:]):
        assert previa["filas"] - actual["recorte"] == actual["filas"], (
            f"de «{previa['clave']}» a «{actual['clave']}» las cuentas no "
            f"cuadran")
    assert emb["split"]["train"] + emb["split"]["test"] == etapas[-1]["filas"]
