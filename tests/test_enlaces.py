# test_enlaces.py — ?sec=, ?lang= y ?theme= conviven sin pisarse
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Lo que AppTest puede ver: cómo la app LEE la URL y qué escribe en
`st.query_params`. Que el navegador muestre esa URL lo comprueba
docs/qa/probar_enlaces.py en Chromium (AppTest no pasa por el frontend).

Los clics simulados arrancan en español. AppTest reenvía el estado de TODOS
los widgets llamando a su `format_func` fuera del script, donde `L()` vale el
idioma por defecto: en inglés busca «Oscuro» entre «Light/Dark/Terminal» y
falla aunque la app esté bien. Los clics en inglés van en la prueba de
Chromium.
"""
from __future__ import annotations

import itertools
from pathlib import Path

import pytest

pytest.importorskip("streamlit.testing.v1")
from streamlit.testing.v1 import AppTest  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
APP = str(RAIZ / "app" / "streamlit_app.py")
SECS = ["ingreso", "informalidad", "torneo", "ficha", "maquinas"]

if not (RAIZ / "models" / "regresor_e9.joblib").exists():
    pytest.skip("sin modelos entrenados", allow_module_level=True)


def abrir(**qp) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    for k, v in qp.items():
        at.query_params[k] = v
    at.run()
    assert not at.exception, at.exception[0].value
    return at


def estado(at: AppTest) -> tuple:
    return tuple(at.session_state[k] for k in ("sec", "lang", "theme"))


def url(at: AppTest) -> dict:
    return {k: v[0] if isinstance(v, list) else v
            for k, v in at.query_params.items()}


# Una muestra de la rejilla sec × lang × theme: todas las secciones, cada una
# con un idioma y un tema distintos, más la portada limpia.
COMBOS = [(s, lang, t) for (s, (lang, t)) in zip(
    SECS, itertools.cycle(itertools.product(["es", "en"],
                                            ["claro", "oscuro", "terminal"])))]


@pytest.mark.parametrize("sec,lang,theme", COMBOS)
def test_la_url_combinada_abre_justo_eso(sec, lang, theme):
    at = abrir(sec=sec, lang=lang, theme=theme)
    assert estado(at) == (sec, lang, theme)
    # Los espejos que lee el resto de la app siguen a los controles.
    assert (at.session_state["seccion"], at.session_state["idioma"],
            at.session_state["tema"]) == (sec, lang, theme)


def test_url_limpia_es_la_portada():
    at = abrir()
    assert estado(at) == ("ingreso", "es", "claro")
    assert url(at) == {}


def test_cambiar_uno_no_pisa_los_otros():
    at = abrir(sec="torneo", theme="terminal")
    at.button_group(key="theme").set_value("oscuro").run()
    assert estado(at) == ("torneo", "es", "oscuro")
    assert url(at) == {"sec": "torneo", "theme": "oscuro"}
    at.button_group(key="sec").set_value("ficha").run()
    assert url(at) == {"sec": "ficha", "theme": "oscuro"}
    at.button_group(key="lang").set_value("en").run()
    assert url(at) == {"sec": "ficha", "lang": "en", "theme": "oscuro"}
    # Volver al defecto quita SOLO ese parámetro.
    at = abrir(sec="ficha", theme="oscuro")
    at.button_group(key="theme").set_value("claro").run()
    assert url(at) == {"sec": "ficha"}


def test_parametros_ajenos_se_respetan():
    at = abrir(sec="torneo", utm_source="portafolio")
    at.button_group(key="theme").set_value("terminal").run()
    assert url(at) == {"sec": "torneo", "theme": "terminal",
                       "utm_source": "portafolio"}


def test_valores_invalidos_caen_al_defecto_y_salen_de_la_url():
    at = abrir(sec="nada", lang="xx", theme="foo")
    assert estado(at) == ("ingreso", "es", "claro")
    assert url(at) == {}


def test_guarda_contra_el_re_clic():
    # Un control segmentado sin `required` deselecciona al pulsar la opción
    # activa y deja la app sin sección: los tres deben declararlo.
    at = abrir()
    for clave in ("sec", "lang", "theme"):
        assert at.button_group(key=clave).proto.required, clave
    at.button_group(key="sec").set_value("torneo").run()
    at.button_group(key="sec").set_value("torneo").run()
    assert at.session_state["sec"] == "torneo"


def test_por_que_tan_alto_lleva_a_la_ficha_sin_perder_el_tema():
    # El botón vive en un fragment: si solo cambiara la clave, se reejecutaría
    # el fragment y la sección no cambiaría.
    at = abrir(sec="informalidad", theme="terminal")
    at.button(key="ir_demasiado_bueno").click().run()
    assert not at.exception
    assert estado(at) == ("ficha", "es", "terminal")
    assert url(at) == {"sec": "ficha", "theme": "terminal"}
