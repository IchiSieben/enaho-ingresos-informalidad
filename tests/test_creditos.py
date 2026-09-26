# test_creditos.py — el pie no inventa ni infla créditos
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Los créditos de la app salen de AUTHORS.md: mismos nombres, mismo orden, y
ningún rol que no esté escrito allí. Se leen las constantes por AST para no
importar la app (importarla arranca Streamlit).
"""
from __future__ import annotations

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
AUTHORS = (RAIZ / "AUTHORS.md").read_text(encoding="utf-8")


def _constante(nombre: str):
    arbol = ast.parse((RAIZ / "app" / "streamlit_app.py").read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if (isinstance(nodo, ast.Assign) and len(nodo.targets) == 1
                and getattr(nodo.targets[0], "id", None) == nombre):
            return ast.literal_eval(nodo.value)
    raise AssertionError(f"no está la constante {nombre}")


def test_grupo_en_el_orden_de_authors():
    grupo = _constante("GRUPO")
    seccion = AUTHORS.split("## Grupo del curso")[1].split("## Docente")[0]
    posiciones = [seccion.index(f"**{nombre}**") for nombre in grupo]
    assert posiciones == sorted(posiciones)
    assert seccion.count("- **") == len(grupo)


def test_roles_del_autor_salen_de_authors():
    seccion = AUTHORS.split("## Autor del software")[1].split("## Grupo")[0]
    seccion = " ".join(seccion.split())
    for es, _ in _constante("ROLES_AUTOR"):
        assert es in seccion, f"rol «{es}» no figura en AUTHORS.md"


def test_docente_es_el_de_authors():
    assert _constante("DOCENTE") in AUTHORS.split("## Docente")[1]


def test_portafolio_es_el_dominio_vigente():
    assert _constante("PORTAFOLIO") == "https://ichisieben.dev"
