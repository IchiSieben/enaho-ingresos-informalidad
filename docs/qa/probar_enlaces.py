# probar_enlaces.py — los tres parámetros de la URL conviven sin pisarse
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Complemento de tests/test_enlaces.py. AppTest comprueba que la app LEE bien
`?sec=`, `?lang=` y `?theme=`, pero no puede ver la URL del navegador: quien la
reescribe al pulsar un control es el frontend. Esto lo comprueba en Chromium.

Uso: python docs/qa/probar_enlaces.py http://localhost:8599
Sale con código 1 si algún caso falla.
"""
from __future__ import annotations

import sys
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip("/")


def params(url: str) -> dict:
    return {k: v[0] for k, v in parse_qs(urlparse(url).query).items()}


def esperar(pg) -> None:
    pg.wait_for_selector(".st-key-sec button", timeout=120000)
    # Justo tras goto/click el atributo puede seguir en el `notRunning` del
    # run anterior: se da un margen para que el nuevo run arranque.
    pg.wait_for_timeout(600)
    pg.wait_for_function(
        "document.querySelector('[data-testid=stApp]')"
        "?.getAttribute('data-test-script-state') === 'notRunning'",
        timeout=120000)
    pg.wait_for_timeout(400)


def activo(pg, clave: str) -> str:
    return pg.locator(f".st-key-{clave} button[aria-checked='true']").inner_text().strip()


def pulsar(pg, clave: str, texto: str) -> None:
    pg.locator(f".st-key-{clave} button", has_text=texto).first.click()
    esperar(pg)


fallos: list[str] = []


def comprobar(nombre: str, cond: bool, detalle: str) -> None:
    print(("OK   " if cond else "FALLA") + f" {nombre}: {detalle}")
    if not cond:
        fallos.append(nombre)


with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={"width": 1366, "height": 768})

    # 1. Los tres a la vez abren justo eso.
    pg.goto(f"{BASE}/?sec=torneo&lang=en&theme=terminal")
    esperar(pg)
    comprobar("carga combinada", (activo(pg, "sec"), activo(pg, "lang"),
                                  activo(pg, "theme")) == ("Tournament", "EN", "Terminal"),
              f"{activo(pg, 'sec')} / {activo(pg, 'lang')} / {activo(pg, 'theme')}")

    # 2. Cambiar uno no pisa los otros dos.
    pulsar(pg, "theme", "Light")
    q = params(pg.url)
    comprobar("tema no pisa", q.get("sec") == "torneo" and q.get("lang") == "en"
              and "theme" not in q, f"{q}  (claro es el defecto: sale de la URL)")
    pulsar(pg, "sec", "Model card")
    q = params(pg.url)
    comprobar("sección no pisa", q == {"sec": "ficha", "lang": "en"}, str(q))
    pulsar(pg, "lang", "ES")
    q = params(pg.url)
    comprobar("idioma no pisa", q == {"sec": "ficha"}, str(q))
    comprobar("idioma aplicado", activo(pg, "sec") == "Ficha", activo(pg, "sec"))

    # 3. Guarda contra el re-clic: pulsar la opción activa no la deselecciona.
    pulsar(pg, "sec", "Ficha")
    comprobar("re-clic en sección", activo(pg, "sec") == "Ficha"
              and params(pg.url).get("sec") == "ficha", pg.url)
    pulsar(pg, "theme", "Claro")
    comprobar("re-clic en tema", activo(pg, "theme") == "Claro", activo(pg, "theme"))

    # 4. «¿Por qué tan alto?» (dentro de un fragment) salta a la ficha en
    #    inglés sin perder idioma ni tema.
    pg.goto(f"{BASE}/?sec=informalidad&lang=en&theme=terminal")
    esperar(pg)
    pg.locator(".st-key-ir_demasiado_bueno button").first.click(timeout=120000)
    esperar(pg)
    comprobar("salto a la ficha", params(pg.url) == {"sec": "ficha", "lang": "en",
                                                     "theme": "terminal"}
              and activo(pg, "sec") == "Model card"
              and pg.locator("h2.resaltado").count() == 1, pg.url)
    # El destino tiene que verse sin scroll: el resumen de la ficha responde
    # justo esa pregunta, y está encima de las pestañas.
    borde = pg.evaluate("() => { const h = document.querySelector('h2.resaltado');"
                        " return h ? [Math.round(h.getBoundingClientRect().bottom),"
                        " window.innerHeight] : null }")
    comprobar("destino visible", bool(borde) and borde[0] < borde[1], str(borde))

    # 5. Valores inválidos: caen al defecto sin romper.
    pg.goto(f"{BASE}/?sec=nada&lang=xx&theme=foo")
    esperar(pg)
    comprobar("inválidos", (activo(pg, "sec"), activo(pg, "lang"),
                            activo(pg, "theme")) == ("Ingreso", "ES", "Claro")
              and pg.locator("[data-testid=stException]").count() == 0, pg.url)

    # 6. Recarga: la URL compartida reproduce el estado.
    pg.goto(f"{BASE}/?sec=maquinas&theme=oscuro")
    esperar(pg)
    pg.reload()
    esperar(pg)
    comprobar("recarga", (activo(pg, "sec"), activo(pg, "theme")) == ("Cómo se hizo", "Oscuro"),
              f"{activo(pg, 'sec')} / {activo(pg, 'theme')}")
    nav.close()

print(f"\n{len(fallos)} fallo(s)")
sys.exit(1 if fallos else 0)
