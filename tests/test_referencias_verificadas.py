# test_referencias_verificadas.py — toda cita ref() apunta a algo verificado
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Hotfix de citas (Fase 2). Regla: toda llamada `ref("<id>")` en `app/*.py`
debe apuntar a una entrada existente de `REFERENCIAS`, y esa entrada debe
tener `verificacion == "contenido"`, o `verificacion == "metadatos"` con su
id en la lista blanca `IDS_SOLO_METADATOS_PERMITIDOS` (con la justificación
de por qué el uso en la app no exige haber leído el contenido).
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
APP_DIR = RAIZ / "app"

sys.path.insert(0, str(APP_DIR))
from referencias import INDICE, REFERENCIAS  # noqa: E402

# id -> por qué basta con metadatos verificados (una línea cada uno).
IDS_SOLO_METADATOS_PERMITIDOS = {
    # La app solo le atribuye el nombre del método de retransformación
    # ("smearing estimate"), que es el título del artículo; no cita ningún
    # resultado ni cifra de su contenido (paywall confirmado, sin versión
    # abierta legal — ver docs/MATRIZ_AFIRMACIONES.md, fila 9).
    "duan1983",
}


def _ids_citados_en_archivo(ruta: Path) -> set[str]:
    """Extrae los ids de todas las llamadas ref("id1", "id2", ...) del AST."""
    arbol = ast.parse(ruta.read_text(encoding="utf-8"), filename=str(ruta))
    ids: set[str] = set()
    for nodo in ast.walk(arbol):
        if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                and nodo.func.id == "ref"):
            for arg in nodo.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    ids.add(arg.value)
    return ids


def _todos_los_ids_citados() -> set[str]:
    ids: set[str] = set()
    for ruta in APP_DIR.glob("*.py"):
        ids |= _ids_citados_en_archivo(ruta)
    return ids


def test_hay_llamadas_ref_en_la_app():
    # Guarda contra un refactor que rompa el AST-walk sin que nadie lo note.
    assert _todos_los_ids_citados()


def test_toda_llamada_ref_apunta_a_una_referencia_existente():
    ids_citados = _todos_los_ids_citados()
    ids_existentes = set(INDICE)
    faltantes = ids_citados - ids_existentes
    assert not faltantes, f"ref() cita ids inexistentes: {faltantes}"


def test_toda_referencia_declara_verificacion_valida():
    for r in REFERENCIAS:
        assert r.get("verificacion") in ("contenido", "metadatos"), r["id"]


def test_toda_llamada_ref_esta_verificada_por_contenido_o_en_lista_blanca():
    por_id = {r["id"]: r for r in REFERENCIAS}
    ids_citados = _todos_los_ids_citados()
    for rid in ids_citados:
        entrada = por_id[rid]
        verificacion = entrada.get("verificacion")
        if verificacion == "contenido":
            continue
        assert verificacion == "metadatos", rid
        assert rid in IDS_SOLO_METADATOS_PERMITIDOS, (
            f"'{rid}' solo tiene metadatos verificados y no está en "
            "IDS_SOLO_METADATOS_PERMITIDOS")


def test_lista_blanca_no_tiene_ids_de_mas():
    # Si un id sale de la lista blanca pero ya no se cita, o deja de existir,
    # que el test lo diga en vez de quedar como comentario muerto.
    ids_existentes = set(INDICE)
    for rid in IDS_SOLO_METADATOS_PERMITIDOS:
        assert rid in ids_existentes, rid
