# -*- coding: utf-8 -*-
# capturar_umbral.py — captura el control del umbral desde la app desplegada
# ---------------------------------------------------------------------------
# Autor: Yoichi Palacios Tanaka (IchiSieben) — proyecto ENAHO 2025
# Licencia: Apache-2.0 (ver LICENSE)
# ---------------------------------------------------------------------------
"""
Guarda docs/presentacion/figuras/cloud_umbral_control.png: el selector de
preajuste y el slider del umbral, capturados de la app EN PRODUCCIÓN.

Por qué existe este script: la lámina del formulario señala con marcadores
los componentes de Streamlit sobre una captura. El control del umbral vive
en la pestaña «Empleo informal», que ninguna de las capturas versionadas
mostraba — y una captura que no existe no se dibuja a mano: se toma.

Tres cosas que este script sabe y que cuestan una tarde averiguar:

  1. En Streamlit Community Cloud la app corre DENTRO de un iframe cuya URL
     contiene «/~/+/». Un `page.locator(...)` sobre el documento principal
     no ve absolutamente nada y `inner_text("body")` vuelve vacío. Hay que
     quedarse con el frame correcto y consultar desde ahí.
  2. El bloque del umbral NO existe al abrir la pestaña: hasta que se pulsa
     «Estimar probabilidad», la app dibuja «Sin estimación todavía» y no
     hay ni selector ni slider en el DOM. Esperar el control sin estimar
     antes es esperar para siempre.
  3. El slider solo aparece con el preajuste «Umbral libre»: con cualquiera
     de los tres puntos de corte predefinidos, Streamlit dibuja el valor
     fijo y no el control. Hay que elegir esa opción antes de capturar.

Correr:  .venv/Scripts/python.exe docs/presentacion/capturar_umbral.py
"""
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
FIGS = AQUI / "figuras"
FIGS.mkdir(exist_ok=True)
SALIDA = FIGS / "cloud_umbral_control.png"

APP = "https://enaho-ingresos-informalidad.streamlit.app"
ESPERA_ARRANQUE = 90_000     # Community Cloud despierta la app al primer hit


def frame_de_la_app(page):
    """El frame donde vive la app; en Cloud NO es el documento principal."""
    for _ in range(60):
        for f in page.frames:
            if "/~/+/" in (f.url or ""):
                return f
        page.wait_for_timeout(1_000)
    # En local (streamlit run) no hay iframe: la app es el documento.
    return page.main_frame


def main() -> int:
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        page = navegador.new_page(viewport={"width": 1600, "height": 1200},
                                  device_scale_factor=2)
        print(f"abriendo {APP} …")
        page.goto(APP, timeout=ESPERA_ARRANQUE, wait_until="domcontentloaded")
        app = frame_de_la_app(page)
        print(f"frame de la app: {app.url[:70]}…")

        # La app tarda en pintar: se espera a un texto propio, no a un sleep.
        app.get_by_text("Empleo informal", exact=False).first.wait_for(
            timeout=ESPERA_ARRANQUE)
        app.get_by_text("Empleo informal", exact=False).first.click()
        print("pestaña «Empleo informal» abierta")

        # Sin estimar no hay bloque de umbral en el DOM (ver docstring).
        app.get_by_role("button", name="Estimar probabilidad").first.click()
        print("«Estimar probabilidad» pulsado")

        # El bloque del umbral: se espera su encabezado propio.
        app.get_by_text("Dónde poner la vara", exact=False).first.wait_for(
            timeout=60_000)

        # Sin «Umbral libre» no hay slider que capturar (ver docstring).
        app.get_by_text("Umbral libre", exact=False).first.click()
        app.get_by_role("slider").first.wait_for(timeout=30_000)
        page.wait_for_timeout(1_200)          # que asiente la animación
        print("preajuste «Umbral libre» elegido; el slider está en pantalla")

        # Se recorta el bloque, no la página: lo que se proyecta es el
        # control, no una captura entera encogida hasta ser ilegible.
        bloque = app.get_by_text("Dónde poner la vara", exact=False).first
        caja = bloque.bounding_box()
        slider = app.get_by_role("slider").first.bounding_box()
        if not caja or not slider:
            print("no se pudo medir el bloque del umbral", file=sys.stderr)
            return 1
        arriba = caja["y"] - 8
        abajo = slider["y"] + slider["height"] + 26
        page.screenshot(path=str(SALIDA), clip={
            "x": max(caja["x"] - 12, 0), "y": max(arriba, 0),
            "width": min(caja["width"] + 24, 1600), "height": abajo - arriba})
        navegador.close()

    print(f"{SALIDA.relative_to(AQUI.parents[1])} · "
          f"{SALIDA.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
