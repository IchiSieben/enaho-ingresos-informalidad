"""Mide el costo de interacción de la app: rerun por slider, iframes y red.

Uso: python docs/qa/medir_rendimiento.py <url_base> <salida.json> [rondas]
Autoría: Yoichi Palacios Tanaka · grupo ENEI.

Por sección: tiempo hasta que la app queda quieta tras cargarla; número de
iframes; y, al mover el primer slider del área principal, el tiempo del rerun
(de la tecla hasta que `stApp` vuelve a notRunning y el DOM deja de cambiar),
las requests de red que dispara y cuántas son a Google Fonts.
"""
import json
import statistics
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# Orden de las opciones en la barra superior (v1.2).
ORDEN_BARRA = ["ingreso", "informalidad", "torneo", "ficha", "maquinas"]

BASE = sys.argv[1].rstrip("/")
SALIDA = Path(sys.argv[2])
RONDAS = int(sys.argv[3]) if len(sys.argv) > 3 else 5
SECCIONES = ["ingreso", "informalidad", "torneo", "ficha", "maquinas"]

# Quieto = el script terminó y no hubo mutaciones del DOM en 300 ms.
JS_QUIETO = """() => new Promise(res => {
  const app = document.querySelector('[data-testid="stApp"]');
  let t = null;
  const listo = () => app.getAttribute('data-test-script-state') !== 'running';
  const obs = new MutationObserver(() => { clearTimeout(t); t = setTimeout(fin, 300); });
  function fin() { if (listo()) { obs.disconnect(); res(true); } else { t = setTimeout(fin, 100); } }
  obs.observe(document.body, {subtree: true, childList: true, attributes: true, characterData: true});
  t = setTimeout(fin, 300);
})"""


def quieto(fr):
    fr.evaluate(JS_QUIETO)


def marco(pg):
    # En Streamlit Cloud la app vive en un iframe /~/+/; en local, en el documento.
    if "streamlit.app" not in BASE:
        return pg.main_frame
    boton = pg.get_by_role("button", name="Yes, get this app back up!")
    pg.wait_for_timeout(3000)
    if boton.count():
        boton.click()
    for _ in range(240):
        for f in pg.frames:
            if "/~/+/" in f.url:
                return f
        pg.wait_for_timeout(1000)
    raise RuntimeError("sin iframe /~/+/")


def main():
    res = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        reqs = []
        pg.on("request", lambda r: reqs.append(r.url))
        t0 = time.perf_counter()
        pg.goto(f"{BASE}/?lang=es", timeout=120000)
        fr = marco(pg)
        fr.wait_for_selector(".st-key-sec button", timeout=240000)
        quieto(fr)
        res["carga_inicial_s"] = round(time.perf_counter() - t0, 2)
        res["requests_carga"] = len(reqs)
        for s in SECCIONES:
            reqs.clear()
            t0 = time.perf_counter()
            fr.locator(".st-key-sec button").nth(ORDEN_BARRA.index(s)).click()
            pg.wait_for_timeout(150)
            quieto(fr)
            fila = {"cambio_seccion_s": round(time.perf_counter() - t0, 2),
                    "iframes": fr.locator("iframe").count(),
                    "requests_cambio": len(reqs),
                    "requests_fonts_cambio": sum("fonts.g" in u for u in reqs)}
            # Streamlit 1.61 usa react-aria: el foco vive en un input range oculto.
            slider = fr.locator('[data-testid="stMain"] [data-testid="stSlider"] input[type="range"]')
            if slider.count():
                tiempos, n_req, n_fonts = [], [], []
                for i in range(RONDAS):
                    reqs.clear()
                    slider.first.focus()
                    t0 = time.perf_counter()
                    slider.first.press("ArrowRight" if i % 2 == 0 else "ArrowLeft")
                    pg.wait_for_timeout(100)
                    quieto(fr)
                    tiempos.append(time.perf_counter() - t0)
                    n_req.append(len(reqs))
                    n_fonts.append(sum("fonts.g" in u for u in reqs))
                fila.update({"rerun_slider_mediana_s": round(statistics.median(tiempos), 3),
                             "rerun_slider_max_s": round(max(tiempos), 3),
                             "requests_por_slider": int(statistics.median(n_req)),
                             "fonts_por_slider": int(statistics.median(n_fonts))})
            res[s] = fila
            print(s, fila, flush=True)
        b.close()
    SALIDA.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
