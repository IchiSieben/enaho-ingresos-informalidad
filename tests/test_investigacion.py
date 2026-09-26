# test_investigacion.py — portada, pestaña Investigación, glosario y mapa (Fase 4)
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

pytest.importorskip("streamlit.testing.v1")
from streamlit.testing.v1 import AppTest  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
APP = str(RAIZ / "app" / "streamlit_app.py")
sys.path.insert(0, str(RAIZ / "app"))

if not (RAIZ / "models" / "regresor_e9.joblib").exists():
    pytest.skip("sin modelos entrenados", allow_module_level=True)


def _abrir(**qp) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=180)
    for k, v in qp.items():
        at.query_params[k] = v
    at.run()
    assert not at.exception, at.exception[0].value
    return at


def _texto(at: AppTest) -> str:
    return " ".join(m.value for m in at.markdown)


@pytest.mark.parametrize("lang", ["es", "en"])
def test_lengua_materna_oculta_con_la_bandera_en_falso(lang):
    import contexto
    assert contexto.MOSTRAR_LENGUA is False
    at = _abrir(sec="investigacion", lang=lang)
    etiquetas = [t.label for t in at.tabs]
    assert not any("materna" in e or "Mother tongue" in e for e in etiquetas)
    texto = _texto(at)
    for lengua in ("Quechua", "Aimara", "Aymara"):
        assert lengua not in texto


def test_la_app_no_se_cae_sin_ui_contexto(monkeypatch):
    import contexto
    monkeypatch.setattr(contexto, "RUTA", RAIZ / "models" / "no_existe.json")
    for sec in ("inicio", "investigacion"):
        at = _abrir(sec=sec)
        assert "ui_contexto.json" in _texto(at)


def test_consistente_solo_con_referencias_de_contenido():
    """
    Toda frase rotulada «consistente con la literatura» cita solo referencias
    verificadas contra su contenido (no solo metadatos).
    """
    import referencias
    verif = {r["id"]: r["verificacion"] for r in referencias.REFERENCIAS}
    codigo = (RAIZ / "app" / "streamlit_app.py").read_text(encoding="utf-8")
    bloques = [b for b in re.split(r"\n\s*html\(", codigo)
               if 'etiqueta_afirmacion("consistente")' in b]
    assert bloques, "no se encontró ninguna afirmación «consistente»"
    for b in bloques:
        ids = re.findall(r'ref\("([^"]+)"\)', b)
        assert ids, "afirmación «consistente» sin referencia"
        assert all(verif[i] == "contenido" for i in ids), ids


def test_glosario_sin_cifras_y_bilingue():
    import glosario
    for clave, (es, en, d_es, d_en) in glosario.TERMINOS.items():
        assert es and en and d_es and d_en, clave
        # Las cifras salen de los artefactos, no de las definiciones (salvo
        # el 95 del intervalo de confianza, que es su definición).
        for d in (d_es, d_en):
            assert not re.search(r"\d", d.replace("95", "")), clave
    html = glosario.termino("ruc")
    assert "tabindex='0'" in html and "role='tooltip'" in html


def test_mapa_un_poligono_por_feature_con_su_titulo():
    import graficos
    import estilos
    geo = json.loads((RAIZ / "models" / "peru_departamentos.geojson").read_text(encoding="utf-8"))
    ctx = json.loads((RAIZ / "models" / "ui_contexto.json").read_text(encoding="utf-8"))
    grupos = ctx["departamentos"]["grupos"]
    valores = {c: g["informal_pct"]["valor"] for c, g in grupos.items()}
    svg = graficos.mapa_departamentos(geo, valores, {c: f"t{c}" for c in grupos},
                                      [60, 68, 75, 79], estilos.PALETAS["claro"], "x")
    assert svg.count("<path class='dep'") == len(geo["features"])
    assert svg.count("<title>") == len(geo["features"])
    assert graficos.proporcion(svg)[0] > 0
