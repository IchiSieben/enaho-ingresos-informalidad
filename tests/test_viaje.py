# test_viaje.py — el viaje del dato interactivo (1.6) sin JavaScript
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Contrato del bloque: radios sin `checked` (con él React los vuelve de solo
lectura), una lectura en vivo por valor y sus keyframes, controles ◀ ▶ para
cada estación y ningún color del tema escrito en el HTML (si lo hubiera, el
bloque cambiaría con el tema y perdería el estado en cada rerun).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))
import graficos  # noqa: E402

TEXTOS = {k: k for k in ("rotulo", "pausar", "reproducir", "anterior", "siguiente",
                         "auto", "pausa", "elegir", "pista", "en_vivo")}
TEXTOS["estacion"] = "Estación {i} de {n}"
ESTACIONES = [{"titulo": f"E{i}", "sub": f"s{i}", "vivo": [f"v{i}"]} for i in range(6)]
ESTACIONES[1]["vivo"] = ["84.853 filas", "84.853 → 57.716 filas",
                         "84.853 → 57.716 → 47.899 filas"]


def _bloque() -> str:
    return graficos.viaje_interactivo(ESTACIONES, TEXTOS)


def test_radios_sin_checked_y_un_solo_nombre():
    h = _bloque()
    radios = re.findall(r"<input[^>]*>", h)
    assert radios and all("type='radio'" in r and "name='viaje'" in r for r in radios)
    assert not any("checked" in r for r in radios)


def test_cada_estacion_se_elige_con_clic_y_con_flechas():
    h = _bloque()
    for i in range(6):
        assert f"class='est est-{i} anim'" in h
        assert f"value='{i}' class='r-est'" in h
    # ◀ desde la 2.ª en adelante y ▶ hasta la penúltima, más los de «auto».
    assert h.count("vc-prev vp-") == 6 and h.count("vc-next vn-") == 6


def test_lecturas_en_vivo_con_su_ventana():
    h = _bloque()
    for j, texto in enumerate(ESTACIONES[1]["vivo"]):
        assert f"vivo-1-{j}" in h and texto.replace("→", "→") in h
        assert f"@keyframes viaje-v1-{j} " in h
    assert "18s linear infinite" in h            # 6 estaciones × 3 s


def test_sin_colores_del_tema_en_el_html():
    assert not re.search(r"#[0-9A-Fa-f]{6}\b", _bloque())


def test_detalle_seleccionado_desde_stmain():
    h = _bloque()
    assert "section[data-testid='stMain']:has(.viaje input.r-est[value='3']:checked) .viaje-det-3" in h
    assert ":not(:has(.viaje input.r-est:checked)) .viaje-det-0" in h
