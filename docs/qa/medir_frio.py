"""Separa el costo en frío de «Cómo se hizo»: servidor recién levantado vs.
navegador nuevo sobre servidor caliente.

Uso: python docs/qa/medir_frio.py <url_base>   (el servidor debe estar recién arrancado)
Autoría: Yoichi Palacios Tanaka · grupo ENEI.
"""
import sys
import time

from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip("/")
JS_QUIETO = open(__file__.replace("medir_frio.py", "medir_rendimiento.py"),
                 encoding="utf-8").read().split('JS_QUIETO = """')[1].split('"""')[0]


def medir(b, etiqueta):
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page()
    bytes_js = []
    pg.on("response", lambda r: bytes_js.append((r.url, r.headers.get("content-length"))))
    t0 = time.perf_counter()
    pg.goto(f"{BASE}/?lang=es")
    pg.wait_for_selector(".st-key-sec button", timeout=180000)
    pg.evaluate(JS_QUIETO)
    t_carga = time.perf_counter() - t0
    bytes_js.clear()
    t0 = time.perf_counter()
    pg.locator(".st-key-sec button").nth(4).click()
    pg.wait_for_timeout(150)
    pg.evaluate(JS_QUIETO)
    t_maq = time.perf_counter() - t0
    grandes = [(u.rsplit("/", 1)[-1][:40], int(c)) for u, c in bytes_js if c and int(c) > 200_000]
    print(f"{etiqueta}: carga {t_carga:.2f}s · ir a 'Cómo se hizo' {t_maq:.2f}s · "
          f"responses {len(bytes_js)} · >200KB {grandes}", flush=True)
    ctx.close()


with sync_playwright() as p:
    b = p.chromium.launch()
    medir(b, "servidor frío + navegador nuevo")
    medir(b, "servidor caliente + navegador nuevo")
    medir(b, "servidor caliente + navegador nuevo (2)")
    b.close()
