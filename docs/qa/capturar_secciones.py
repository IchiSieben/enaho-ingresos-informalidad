"""Capturas de viewport por sección, idioma, tema y tamaño.

Uso: python docs/qa/capturar_secciones.py <url_base> <carpeta> [temas] [idiomas] [tamaños]
     temas, idiomas y tamaños separados por coma (por defecto: claro / es,en /
     1440x900,1366x768).
Autoría: Yoichi Palacios Tanaka · grupo ENEI.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Orden de las opciones en la barra superior (v2: siete pestañas).
ORDEN_BARRA = ["inicio", "ingreso", "informalidad", "investigacion", "torneo", "ficha",
               "maquinas"]

BASE = sys.argv[1].rstrip("/")
DEST = Path(sys.argv[2])
TEMAS = (sys.argv[3] if len(sys.argv) > 3 else "claro").split(",")
IDIOMAS = (sys.argv[4] if len(sys.argv) > 4 else "es,en").split(",")
SECCIONES = ORDEN_BARRA
TAMANOS = [tuple(int(v) for v in t.split("x")) for t in
           (sys.argv[5] if len(sys.argv) > 5 else "1440x900,1366x768").split(",")]
DEST.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    for ancho, alto in TAMANOS:
        for lang in IDIOMAS:
            for tema in TEMAS:
                pg = b.new_page(viewport={"width": ancho, "height": alto})
                for s in SECCIONES:
                    # Carga directa por URL: con el clic en la barra, una sección
                    # lenta (Investigación) se fotografiaba con el contenido de la
                    # anterior todavía en pantalla.
                    pg.goto(f"{BASE}/?sec={s}&lang={lang}&theme={tema}", timeout=120000)
                    pg.wait_for_selector(".pie", timeout=120000)
                    pg.wait_for_function(
                        "!document.querySelector('[data-testid=\"stStatusWidget\"]')",
                        timeout=120000)
                    pg.wait_for_timeout(2500)
                    pg.screenshot(path=str(DEST / f"{s}_{lang}_{tema}_{ancho}x{alto}.png"),
                                  timeout=120000)
                pg.close()
    b.close()
print("ok", DEST)
