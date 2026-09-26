# 10b_mapa_geo.py — GeoJSON liviano de departamentos para el mapa de contexto
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Descarga geoBoundaries PER ADM1 (versión simplificada, fijada al commit
90a1d52 del repo wmgeolab/geoBoundaries), le pone a cada polígono el código
de departamento del UBIGEO y redondea coordenadas a 3 decimales (~100 m).

Licencia de la fuente, verificada en la API de geoBoundaries
(geoboundaries.org/api/current/gbOpen/PER/ADM1/): Public Domain, origen
Wikimedia Commons. Build del 21/02/2024.

geoBoundaries separa «Municipalidad Metropolitana de Lima» de «Lima»
(provincias). La ENAHO los junta en el código 15, así que los dos polígonos
llevan el mismo código.

Uso: python src/10b_mapa_geo.py
"""
from __future__ import annotations

import json
import sys
import unicodedata
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import DIR_MODELS, escribir_json_atomico

URL = ("https://github.com/wmgeolab/geoBoundaries/raw/90a1d52/releaseData/gbOpen/"
       "PER/ADM1/geoBoundaries-PER-ADM1_simplified.geojson")
RUTA = DIR_MODELS / "peru_departamentos.geojson"
FUENTE = {"nombre": "geoBoundaries gbOpen PER ADM1 (simplificado)", "url": URL,
          "licencia": "Public Domain", "origen": "Wikimedia Commons",
          "build": "2024-02-21"}


def _clave(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return s.removeprefix("el ").strip()


def codigos() -> dict[str, str]:
    ctx = __import__("importlib").import_module("10_contexto")
    mapa = {_clave(n): c for c, n in ctx.DEPARTAMENTOS.items()}
    mapa[_clave("Municipalidad Metropolitana de Lima")] = "15"
    return mapa


def redondear(coords, dec: int = 3):
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], dec), round(coords[1], dec)]
    return [redondear(c, dec) for c in coords]


def main() -> None:
    with urllib.request.urlopen(URL, timeout=60) as r:
        g = json.load(r)
    mapa = codigos()
    feats = []
    for f in g["features"]:
        nombre = f["properties"]["shapeName"]
        cod = mapa[_clave(nombre)]          # KeyError = nombre nuevo en la fuente
        geom = f["geometry"]
        feats.append({"type": "Feature",
                      "properties": {"depto": cod, "nombre_fuente": nombre},
                      "geometry": {"type": geom["type"],
                                   "coordinates": redondear(geom["coordinates"])}})
    assert len({f["properties"]["depto"] for f in feats}) == 25, "faltan departamentos"
    salida = {"type": "FeatureCollection", "fuente": FUENTE, "features": feats}
    escribir_json_atomico(RUTA, json.dumps(salida, ensure_ascii=False, separators=(",", ":")))
    print(f"ok · {RUTA.name} · {RUTA.stat().st_size / 1024:.0f} KB · {len(feats)} polígonos")


if __name__ == "__main__":
    main()
