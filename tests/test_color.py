# test_color.py — la paleta se verifica con números, no a ojo
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
import itertools
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from color import CVD, contraste, delta_e  # noqa: E402
from estilos import PALETAS  # noqa: E402

TINTAS = ["texto", "texto_medio", "texto_tenue", "acento", "acento_alto",
          "senal_buena", "senal_media", "senal_mala", "titulo"]
FONDOS = ["fondo", "superficie", "superficie_alta"]
SEMANTICOS = ["acento", "senal_buena", "senal_media", "senal_mala"]
# ΔE OKLab mínimo entre colores semánticos, visto con cada tipo de CVD. Un
# JND ronda 0,02; 0,10 es «distinto a simple vista, lado a lado».
DELTA_MIN = 0.10


@pytest.mark.parametrize("tema", list(PALETAS))
def test_texto_aa_sobre_todos_los_fondos(tema):
    T = PALETAS[tema]
    malos = [(t, f, round(contraste(T[t], T[f]), 2))
             for t in TINTAS for f in FONDOS if contraste(T[t], T[f]) < 4.5]
    assert not malos, f"{tema}: pares bajo AA {malos}"


@pytest.mark.parametrize("tema", list(PALETAS))
def test_senales_sobre_su_propio_fondo(tema):
    T = PALETAS[tema]
    for s in ("buena", "media", "mala"):
        c = contraste(T[f"senal_{s}_texto"], T[f"senal_{s}_fondo"])
        assert c >= 4.5, f"{tema}: senal_{s}_texto sobre su fondo = {c:.2f}"
    assert contraste(T["boton_texto"], T["acento"]) >= 4.5


def test_config_toml_coincide_con_la_paleta_clara():
    # Streamlit pinta con config.toml antes de que entre nuestro CSS: si no
    # coinciden, la carga parpadea con otro color.
    import tomllib
    raiz = Path(__file__).resolve().parents[1]
    tema = tomllib.loads((raiz / ".streamlit" / "config.toml").read_text(encoding="utf-8"))["theme"]
    claro = PALETAS["claro"]
    assert tema["primaryColor"].upper() == claro["acento"].upper()
    assert tema["backgroundColor"].upper() == claro["fondo"].upper()
    assert tema["secondaryBackgroundColor"].upper() == claro["superficie"].upper()
    assert tema["textColor"].upper() == claro["texto"].upper()


@pytest.mark.parametrize("tema", list(PALETAS))
def test_semanticos_distinguibles_con_daltonismo(tema):
    T = PALETAS[tema]
    peor = min((delta_e(T[a], T[b], tipo), a, b, tipo or "normal")
               for a, b in itertools.combinations(SEMANTICOS, 2)
               for tipo in (None, *CVD))
    assert peor[0] >= DELTA_MIN, f"{tema}: {peor[1]}–{peor[2]} en {peor[3]} = {peor[0]:.3f}"


@pytest.mark.parametrize("tema", list(PALETAS))
def test_filtro_de_pista_lleva_al_acento(tema):
    # La pista del slider se recolorea con FILTRO_PISTA (estilos.py). Si la
    # paleta cambia y el filtro no, la pista quedaría de otro color.
    import re
    from color import aplicar_filtro
    from estilos import FILTRO_PISTA
    T = PALETAS[tema]
    f = FILTRO_PISTA[tema]
    if f == "none":
        resultado = "#0F766E"
    else:
        g, s, b = map(float, re.findall(r"-?\d+(?:\.\d+)?", f))
        resultado = aplicar_filtro("#0F766E", g, s, b)
    assert delta_e(resultado, T["acento"]) < 0.02, (tema, resultado, T["acento"])
    # WCAG 1.4.11: componentes de interfaz a 3:1 contra su fondo.
    assert contraste(resultado, T["superficie"]) >= 3


@pytest.mark.parametrize("tema", list(PALETAS))
def test_widgets_nativos_visibles(tema):
    # Pulgar, radio marcado y toggle encendido van en acento; apagados, en
    # texto_tenue. Ambos a 3:1 contra la superficie (WCAG 1.4.11).
    T = PALETAS[tema]
    for token in ("acento", "texto_tenue"):
        assert contraste(T[token], T["superficie"]) >= 3, (tema, token)
    assert contraste(T["boton_texto"], T["acento"]) >= 3
