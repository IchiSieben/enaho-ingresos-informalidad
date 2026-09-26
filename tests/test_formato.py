# test_formato.py — cifra y unidad no se separan al cortar la línea
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Antes de la 1.6, «25 %», «S/ 1.299» o «0,9 MB» podían partirse en dos líneas
(el caso visto: «S/» al final de una línea de la tarjeta de comparables y
«996» al comienzo de la siguiente). Ahora llevan espacio duro.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "app"))
import i18n  # noqa: E402

NBSP = " "


@pytest.fixture
def idioma(monkeypatch):
    def fijar(lang: str) -> None:
        monkeypatch.setattr(i18n, "idioma", lambda: lang)
    return fijar


def test_porcentaje_en_espanol_lleva_espacio_duro(idioma):
    idioma("es")
    assert i18n.pc(25) == f"25{NBSP}%"
    assert i18n.pct(0.975) == f"97,5{NBSP}%"


def test_porcentaje_en_ingles_va_pegado(idioma):
    idioma("en")
    assert i18n.pc(25) == "25%"


def test_soles_sin_corte(idioma):
    idioma("es")
    assert i18n.sol(1299) == f"S/{NBSP}1.299"
    idioma("en")
    assert i18n.sol(1299) == f"S/{NBSP}1,299"


def test_red_de_seguridad_en_prosa():
    # El caso que se partía: prosa con «S/ 996» y «25 %» escritos a mano.
    antes = "la mitad del medio gana entre S/ 996 y S/ 1.923: un 25 % gana menos; 0,9 MB; 2,5 × la mediana"
    despues = i18n.no_cortar(antes)
    assert "S/ 9" not in despues and "25 %" not in despues
    assert f"S/{NBSP}996" in despues and f"0,9{NBSP}MB" in despues
    assert f"2,5{NBSP}×" in despues
    # No toca lo que no es cifra + unidad.
    assert i18n.no_cortar("3 MBs y 12 meses") == "3 MBs y 12 meses"


def test_no_quedan_soles_armados_a_mano():
    """Todo «S/ » seguido de una cifra calculada pasa por i18n.sol()."""
    patron = re.compile(r"S/ \{")
    for ruta in (RAIZ / "app").glob("*.py"):
        texto = ruta.read_text(encoding="utf-8")
        assert not patron.search(texto), f"{ruta.name}: usa sol() en vez de «S/ {{…}}»"
