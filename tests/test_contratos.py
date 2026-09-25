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


def test_el_embudo_svg_muestra_motivo_y_porcentaje():
    """
    Condición del reemplazo del Sankey: cada recorte conserva su motivo
    legible (texto visible Y <title>) y su porcentaje sobre el total crudo,
    con decimal bajo el 1 %.
    """
    import re
    from html import unescape
    motivos = ["Motivo del primer recorte, con varias palabras para partir "
               "en más de una línea si hace falta.", "Segundo motivo.",
               "Tercer motivo, el recorte chico."]
    svg = graficos.embudo(
        [("Crudo", 1000), ("A", 700), ("B", 500), ("C", 497)],
        [("fuera 1", 300, motivos[0]), ("fuera 2", 200, motivos[1]),
         ("fuera 3", 3, motivos[2])],
        [("Train", 400, "entrena"), ("Test", 97, "evalúa")], PALETAS["claro"])
    titulos = unescape(" ".join(re.findall(r"<title>(.*?)</title>", svg)))
    visible = unescape(" ".join(re.findall(r"<text[^>]*>(.*?)</text>", svg)))
    for m in motivos:
        assert m in titulos
        assert m in visible, f"motivo no visible: {m}"
    assert "0,3 %" in visible          # 3 de 1000: el entero diría «0 %»
    assert "30 %" in visible and "100 %" in visible
    assert graficos.proporcion(svg)[0] == 960
    # Entrada ≤ 250 ms: solo clases de animación del contrato, sin retrasos.
    assert "animation-delay" not in svg
    with pytest.raises(ValueError):
        graficos.embudo([("a", 1), ("b", 1)], [], [], PALETAS["claro"])


# --------------------------------------------------------------------------
# Bilingüe (v1.1): ningún texto de datos se queda en español en la versión EN
# --------------------------------------------------------------------------
def _schema() -> dict:
    return json.loads((RAIZ / "models" / "feature_schema.json")
                      .read_text(encoding="utf-8"))


def test_toda_categoria_y_etiqueta_tiene_traduccion():
    """Una opción nueva en el schema sin traducir saldría en español en EN."""
    import i18n
    faltan = set()
    for bloque in ("regresor", "clasificador"):
        for f in _schema()[bloque]["features"]:
            faltan |= {x for x in [f.get("etiqueta")] + f.get("opciones", [])
                       if x and x not in i18n.VALORES}
    assert not faltan, f"sin traducción en i18n.VALORES: {sorted(faltan)}"


def test_perfiles_de_ejemplo_son_validos():
    """Un perfil con un valor fuera del schema se ignoraría en silencio."""
    from streamlit_app import PERFILES
    feats = {f["nombre"]: f for f in _schema()["regresor"]["features"]}
    for p in PERFILES:
        for nombre, v in p["valores"].items():
            f = feats[nombre]
            if f["tipo"] == "numerico":
                assert float(f["min"]) <= float(v) <= float(f["max"]), (p["id"], nombre)
            else:
                assert v in f["opciones"], (p["id"], nombre, v)


@pytest.mark.parametrize("animado", [False, True])
def test_viaje_vertical_lleva_los_mismos_datos(animado):
    """
    La variante apilada del viaje (pantallas angostas) muestra las mismas
    estaciones y subtítulos que la horizontal, y cabe en 360 de ancho.
    """
    from html import unescape
    titulos = ["Microdatos", "Limpieza", "Torneo"]
    subs = ["601 MB", "47.632 filas", "9 recetas"]
    h = graficos.viaje_dato(titulos, subs, 1, PALETAS["claro"], animado=animado)
    v = graficos.viaje_dato_vertical(titulos, subs, 1, PALETAS["claro"],
                                     animado=animado)
    assert graficos.proporcion(v)[0] == 360
    for t, s in zip(titulos, subs):
        assert t in unescape(h) and t in unescape(v)
        assert s in unescape(h) and s in unescape(v)
    assert ("animateMotion" in v) == animado
