"""Capturas de viewport por sección, idioma, tema y tamaño.

Uso: python docs/qa/capturar_secciones.py <url_base> <carpeta> [temas] [idiomas]
     temas e idiomas separados por coma (por defecto: claro / es,en).
Autoría: Yoichi Palacios Tanaka · grupo ENEI.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Orden de las opciones en la barra superior (v1.2).
ORDEN_BARRA = ["ingreso", "informalidad", "torneo", "ficha", "maquinas"]

BASE = sys.argv[1].rstrip("/")
DEST = Path(sys.argv[2])
TEMAS = (sys.argv[3] if len(sys.argv) > 3 else "claro").split(",")
IDIOMAS = (sys.argv[4] if len(sys.argv) > 4 else "es,en").split(",")
SECCIONES = ["ingreso", "informalidad", "torneo", "ficha", "maquinas"]
TAMANOS = [(1440, 900), (1366, 768)]
DEST.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    for ancho, alto in TAMANOS:
        for lang in IDIOMAS:
            for tema in TEMAS:
                pg = b.new_page(viewport={"width": ancho, "height": alto})
                pg.goto(f"{BASE}/?lang={lang}&theme={tema}", timeout=120000)
                pg.wait_for_selector(".st-key-sec button", timeout=120000)
                pg.wait_for_timeout(2500)
                for s in SECCIONES:
                    pg.locator(".st-key-sec button").nth(ORDEN_BARRA.index(s)).click()
                    pg.wait_for_timeout(3000)
                    pg.screenshot(path=str(DEST / f"{s}_{lang}_{tema}_{ancho}x{alto}.png"),
                                  timeout=120000)
                pg.close()
    b.close()
print("ok", DEST)
