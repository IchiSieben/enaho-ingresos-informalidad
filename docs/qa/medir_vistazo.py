"""Criterio «de un vistazo»: ¿pregunta + controles + respuesta + gráfico
clave caben sin scroll? Mide el borde inferior de cada elemento contra el alto
del viewport, por sección, en 1440×900 y 1366×768.

Uso: python docs/qa/medir_vistazo.py <url_base> <salida.json> [lang] [tema]
Autoría: Yoichi Palacios Tanaka · grupo ENEI.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Orden de las opciones en la barra superior (v1.2).
ORDEN_BARRA = ["ingreso", "informalidad", "torneo", "ficha", "maquinas"]

BASE = sys.argv[1].rstrip("/")
SALIDA = Path(sys.argv[2])
LANG = sys.argv[3] if len(sys.argv) > 3 else "es"
TEMA = sys.argv[4] if len(sys.argv) > 4 else "claro"
TAMANOS = [(1440, 900), (1366, 768)]

# Elementos clave por sección (selectores; el primero que exista gana).
# `vistazo-*` marcan el resumen y el gráfico clave (v1.2); en la línea base
# (v1.1) se medía el primer iframe como gráfico clave.
CLAVES = {
    "ingreso": {"pregunta": ["h1"],
                "controles": [".st-key-caja_form_reg"],
                "respuesta": [".hero-cifra"],
                "grafico": [".vistazo-grafico", ".hero-barra"]},
    "informalidad": {"pregunta": ["h1"],
                     "controles": [".st-key-caja_form_clf"],
                     "respuesta": [".fila-veredicto"],
                     "grafico": [".vistazo-grafico"]},
    "torneo": {"pregunta": ["h1"],
               "respuesta": [".vistazo-cifras"],
               "grafico": [".vistazo-grafico"]},
    "ficha": {"pregunta": ["h1"],
              "respuesta": [".vistazo-cifras"],
              "grafico": [".vistazo-grafico"]},
    "maquinas": {"pregunta": ["h1"],
                 "respuesta": [".vistazo-cifras"],
                 "grafico": [".vistazo-grafico"]},
}

JS_BORDE = """(sels) => {
  for (const s of sels) {
    const el = document.querySelector('[data-testid="stMain"] ' + s);
    if (el) { const r = el.getBoundingClientRect();
              if (r.height > 0) return Math.round(r.bottom + window.scrollY); }
  }
  return null;
}"""

res = {}
with sync_playwright() as p:
    b = p.chromium.launch()
    for ancho, alto in TAMANOS:
        pg = b.new_page(viewport={"width": ancho, "height": alto})
        pg.goto(f"{BASE}/?lang={LANG}&theme={TEMA}", timeout=120000)
        pg.wait_for_selector(".st-key-sec button", timeout=120000)
        pg.wait_for_timeout(2500)
        for sec, claves in CLAVES.items():
            pg.locator(".st-key-sec button").nth(ORDEN_BARRA.index(sec)).click()
            pg.wait_for_timeout(3000)
            bordes = {k: pg.evaluate(JS_BORDE, sels) for k, sels in claves.items()}
            medidos = [v for v in bordes.values() if v is not None]
            fila = {**bordes, "alto_viewport": alto,
                    "cabe": bool(medidos) and max(medidos) <= alto
                            and None not in bordes.values()}
            res[f"{sec}@{ancho}x{alto}"] = fila
            print(sec, f"{ancho}x{alto}", fila, flush=True)
        pg.close()
    b.close()
SALIDA.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
