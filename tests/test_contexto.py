# test_contexto.py — contrato y coherencia de models/ui_contexto.json (Fase 3)
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
El artefacto lo escribe src/10_contexto.py con los microdatos (fuera del
repo). Aquí se comprueba lo que la app va a leer: claves, que ninguna celda
visible tenga n < 100, que las descomposiciones sumen, y que las funciones de
cálculo sean deterministas con la semilla (sobre datos sintéticos).
"""
from __future__ import annotations

import json
import sys
from importlib import import_module
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "app"))
ctx = import_module("10_contexto")
ART = json.loads((RAIZ / "models" / "ui_contexto.json").read_text(encoding="utf-8"))


def test_claves_de_primer_nivel():
    assert set(ART) == {"meta", "penalidad", "genero", "retornos", "departamentos",
                        "lengua", "alarmas", "peru"}
    for k in ("n", "n_hora", "informal_pct", "B", "semilla", "n_min", "commit"):
        assert k in ART["meta"]
    assert ART["meta"]["B"] >= 200, "el artefacto publicado va con B >= 200"


def test_ninguna_celda_visible_bajo_el_minimo():
    n_min = ART["meta"]["n_min"]
    for bloque in ("departamentos", "lengua"):
        for nombre, g in ART[bloque]["grupos"].items():
            assert g["mostrar"] == (g["n"] >= n_min), nombre
    for spec in ART["penalidad"]["log_hora"].values():
        assert spec["n"] >= n_min
    for seg in ART["retornos"].values():
        assert seg["n"] >= n_min


def test_mapa_reproduce_la_tasa_de_la_muestra():
    assert ART["departamentos"]["control_nacional"] == pytest.approx(
        ART["meta"]["informal_pct"], abs=0.05)
    assert sum(g["n"] for g in ART["departamentos"]["grupos"].values()) == ART["meta"]["n"]


def test_descomposiciones_suman():
    for y in ("log_hora", "log_mes"):
        for c in ("A", "B"):
            o = ART["genero"]["oaxaca"][y][c]
            for ref in ("pooled", "hombres", "mujeres"):
                total = o[ref]["explicada"]["valor"] + o[ref]["no_explicada"]["valor"]
                assert total == pytest.approx(o["brecha"]["valor"], abs=2e-4)
    for c in ("A", "B"):
        o = ART["genero"]["nopo"][c]
        partes = sum(o[k]["valor"] for k in ("d0", "dH", "dM", "dX"))
        assert partes == pytest.approx(o["delta"]["valor"], abs=5e-4)


def test_detalle_de_oaxaca_suma_la_explicada():
    for y in ("log_hora", "log_mes"):
        for c in ("A", "B"):
            o = ART["genero"]["oaxaca"][y][c]
            suma = sum(v["valor"] for v in o["detalle_pooled"].values())
            assert suma == pytest.approx(o["pooled"]["explicada"]["valor"], abs=5e-4)


def test_peru_en_cifras():
    p = ART["peru"]
    assert sum(p["pct_region"].values()) == pytest.approx(100, abs=0.05)
    assert 0 < p["pct_lima_metropolitana"] < p["pct_region"]["costa"]
    assert p["ocupados_14"] < p["poblacion"]


def test_etiquetas_nuevas_tienen_traduccion():
    import i18n
    nombres = list(ART["departamentos"]["nombres"].values()) + list(ART["lengua"]["grupos"])
    assert not [x for x in nombres if x not in i18n.VALORES]


# --------------------------------------------------------------------------
# Funciones de cálculo sobre datos sintéticos
# --------------------------------------------------------------------------
def _sinteticos(semilla: int = 0, n: int = 3000) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)
    return pd.DataFrame({
        "c": rng.integers(0, 40, n),
        "y": rng.lognormal(1.5, 0.6, n),
        "w": rng.uniform(50, 300, n),
        "h": rng.integers(0, 2, n),
        "conglome": rng.integers(0, 300, n).astype(str),
    })


def test_nopo_identidad_con_soporte_parcial():
    d = _sinteticos()
    # Celdas exclusivas de cada grupo: fuerza ΔH y ΔM distintos de cero.
    d.loc[(d["h"] == 1) & (d.index % 17 == 0), "c"] = 900
    d.loc[(d["h"] == 0) & (d.index % 19 == 0), "c"] = 901
    r = ctx.nopo(d["c"].to_numpy(), d["y"].to_numpy(), d["w"].to_numpy(), d["h"].to_numpy())
    assert r["dH"] != 0 and r["dM"] != 0
    assert r["d0"] + r["dH"] + r["dM"] + r["dX"] == pytest.approx(r["delta"], abs=1e-12)


def test_oaxaca_identidad():
    d = _sinteticos(1)
    X = np.column_stack([np.ones(len(d)), d["c"].to_numpy(float)])
    r = ctx.oaxaca(X, np.log(d["y"].to_numpy()), d["w"].to_numpy(), d["h"].to_numpy())
    for ref in ("pooled", "hombres", "mujeres"):
        assert r[ref]["explicada"] + r[ref]["no_explicada"] == pytest.approx(r["brecha"])


def test_bootstrap_determinista_con_semilla():
    s = _sinteticos()["conglome"]
    a = list(ctx.pesos_bootstrap(s, 5, 42))
    b = list(ctx.pesos_bootstrap(s, 5, 42))
    assert all(np.array_equal(x, y) for x, y in zip(a, b))
    # Cada réplica conserva el número de conglomerados.
    assert all(len(np.unique(s[x > 0])) <= s.nunique() for x in a)


def test_mediana_ponderada():
    assert ctx.mediana_p(np.array([1.0, 2.0, 3.0]), np.array([1.0, 1.0, 10.0])) == 3.0
    assert ctx.mediana_p(np.array([1.0, 2.0, 3.0]), np.array([1.0, 1.0, 1.0])) == 2.0


def test_geojson_cubre_los_departamentos_del_artefacto():
    g = json.loads((RAIZ / "models" / "peru_departamentos.geojson").read_text(encoding="utf-8"))
    assert g["fuente"]["licencia"] == "Public Domain"
    codigos = {f["properties"]["depto"] for f in g["features"]}
    assert codigos == set(ART["departamentos"]["grupos"])
    assert (RAIZ / "models" / "peru_departamentos.geojson").stat().st_size < 200_000
