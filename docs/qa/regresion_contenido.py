"""Harness de no-regresión de contenido: extrae texto visible de las 5 secciones
de la app (tabs, expanders y popovers abiertos) en ES/EN, para v1.1 y la versión
actual, y compara.

Uso:
    python docs/qa/regresion_contenido.py extraer <url_base> <salida.json> <v11|actual>
    python docs/qa/regresion_contenido.py comparar <v11.json> <actual.json> <informe.md>
"""

from __future__ import annotations

import difflib
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

from playwright.sync_api import sync_playwright

SECCIONES = ["ingreso", "informalidad", "torneo", "ficha", "maquinas"]
IDIOMAS = ["es", "en"]

CHROME_RUIDO = [
    "Deploy", "Manage app", "Running", "Press Enter to apply",
    "Made with Streamlit",
]


def normalizar(texto: str) -> list[str]:
    """NBSP -> espacio, colapsa espacios, corta en líneas no vacías."""
    texto = texto.replace(" ", " ").replace("​", "")
    texto = unicodedata.normalize("NFC", texto)
    lineas = []
    for linea in re.split(r"[\r\n]+", texto):
        linea = re.sub(r"[ \t]+", " ", linea).strip()
        if not linea:
            continue
        if any(r in linea for r in CHROME_RUIDO):
            continue
        lineas.append(linea)
    return lineas


def texto_main(page) -> str:
    bloque = page.query_selector("section.main") or page.query_selector('[data-testid="stAppViewContainer"]')
    if bloque is None:
        return page.inner_text("body")
    return bloque.inner_text()


def texto_oculto(page) -> str:
    """Contenido que inner_text no captura por estar oculto con CSS
    (.viaje-det-0..5, escondidos con display:none/visibility) o por vivir en
    un <svg><text> (etiquetas del embudo): se lee textContent directo."""
    partes = []
    for i in range(6):
        el = page.query_selector(f".viaje-det-{i}")
        if el is not None:
            try:
                partes.append(el.text_content() or "")
            except Exception:
                pass
    for el in page.query_selector_all("svg text"):
        try:
            partes.append(el.text_content() or "")
        except Exception:
            pass
    return "\n".join(partes)


def abrir_expanders_y_popovers(page) -> None:
    # Expanders (details/summary) que no estén abiertos.
    for _ in range(3):
        cerrados = page.query_selector_all('details:not([open]) summary')
        if not cerrados:
            break
        for s in cerrados:
            try:
                s.click(timeout=2000)
                page.wait_for_timeout(150)
            except Exception:
                pass
    # Popovers: botones que abren un popover de Streamlit.
    botones_popover = page.query_selector_all('[data-testid="stPopoverButton"] button, [data-testid="stPopover"] button')
    for b in botones_popover:
        try:
            b.click(timeout=2000)
            page.wait_for_timeout(200)
        except Exception:
            pass
    # Toggles (st.toggle, p. ej. "Ver el motor" / "See the engine",
    # key="maq_motor"): sin esto, todo el contenido detrás del toggle
    # (curvas de dependencia parcial, citas, selector de variable) nunca
    # se captura. Se activan solo si están apagados (aria-checked="false").
    toggles = page.query_selector_all(
        '[data-testid="stToggle"] input[type="checkbox"], '
        '[data-baseweb="toggle"] input[type="checkbox"], '
        'label[data-testid="stWidgetLabel"] ~ [role="switch"], '
        '[role="switch"][aria-checked="false"]'
    )
    for t in toggles:
        try:
            estado = t.get_attribute("aria-checked")
            if estado == "true":
                continue
            t.click(timeout=2000)
            page.wait_for_timeout(200)
        except Exception:
            pass


def cerrar_popovers(page) -> None:
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(100)
    except Exception:
        pass


def esperar_render(page, limite_ms: int = 20000) -> None:
    """Espera a que desaparezca el botón "Stop" (spinner de ejecución)."""
    inicio = time.time()
    while (time.time() - inicio) * 1000 < limite_ms:
        stop = page.query_selector('button:has-text("Stop")')
        if stop is None:
            return
        page.wait_for_timeout(300)


def esperar_texto_estable(page, intentos: int = 8, pausa_ms: int = 1000) -> str:
    """Espera a que el texto principal + oculto sea idéntico en dos lecturas
    consecutivas separadas por ~1s, en vez de dormir un tiempo fijo. Evita el
    no-determinismo documentado en triage.md (mismo contenido "falta" en una
    corrida y no en otra por timing de re-render)."""
    anterior = None
    for _ in range(intentos):
        actual = texto_main(page) + "\n" + texto_oculto(page)
        if anterior is not None and actual == anterior:
            return actual
        anterior = actual
        page.wait_for_timeout(pausa_ms)
    return anterior or ""


def recolectar_estado(page) -> list[str]:
    esperar_render(page)
    abrir_expanders_y_popovers(page)
    esperar_render(page)
    txt = esperar_texto_estable(page)
    lineas = normalizar(txt)
    if lineas == ["Stop"] or not lineas:
        esperar_render(page, 15000)
        txt = esperar_texto_estable(page)
        lineas = normalizar(txt)
    cerrar_popovers(page)
    return lineas


def iterar_tabs_y_recolectar(page) -> list[str]:
    """Recorre cada grupo de tabs visible, clickeando cada tab y recolectando."""
    todas = []
    todas += recolectar_estado(page)
    grupos = page.query_selector_all('[data-testid="stTabs"]')
    for gi in range(len(grupos)):
        grupos = page.query_selector_all('[data-testid="stTabs"]')
        if gi >= len(grupos):
            break
        botones = grupos[gi].query_selector_all('button[role="tab"]')
        for ti in range(len(botones)):
            grupos = page.query_selector_all('[data-testid="stTabs"]')
            if gi >= len(grupos):
                break
            botones = grupos[gi].query_selector_all('button[role="tab"]')
            if ti >= len(botones):
                break
            try:
                botones[ti].click(timeout=3000)
                page.wait_for_timeout(300)
            except Exception:
                continue
            todas += recolectar_estado(page)
    return todas


def iterar_estaciones_viaje(page) -> list[str]:
    """"Cómo se hizo" / motor: intenta iterar las estaciones del viaje del
    dato. En v1.6+ es un st.segmented_control (key="maq_estacion",
    data-testid="stButtonGroup"), no un selectbox: se itera clickeando cada
    boton[role="radio"]. Se conserva el barrido de selectbox por si v1.1 (o
    alguna otra sección) todavía usa uno."""
    todas = []

    grupos_segmentados = page.query_selector_all('.st-key-maq_estacion [data-testid="stButtonGroup"]')
    for grupo in grupos_segmentados:
        botones = grupo.query_selector_all('button[role="radio"]')
        n = len(botones)
        for i in range(n):
            botones = page.query_selector_all(
                '.st-key-maq_estacion [data-testid="stButtonGroup"] button[role="radio"]'
            )
            if i >= len(botones):
                break
            try:
                botones[i].click(timeout=2000)
                page.wait_for_timeout(300)
            except Exception:
                continue
            todas += recolectar_estado(page)

    # Selectbox de "estación" por posición (compatibilidad v1.1): probamos
    # hasta 8 opciones.
    combos = page.query_selector_all('[data-testid="stSelectbox"] [data-baseweb="select"]')
    for combo in combos:
        try:
            combo.click(timeout=2000)
            page.wait_for_timeout(150)
            opciones = page.query_selector_all('[role="listbox"] [role="option"]')
            n = len(opciones)
            page.keyboard.press("Escape")
            page.wait_for_timeout(100)
        except Exception:
            continue
        if n < 2 or n > 8:
            continue
        for i in range(n):
            try:
                combo.click(timeout=2000)
                page.wait_for_timeout(150)
                opciones = page.query_selector_all('[role="listbox"] [role="option"]')
                if i >= len(opciones):
                    page.keyboard.press("Escape")
                    continue
                opciones[i].click(timeout=2000)
                page.wait_for_timeout(300)
            except Exception:
                continue
            todas += recolectar_estado(page)
    return todas


def extraer_seccion(page, clave: str) -> list[str]:
    lineas = iterar_tabs_y_recolectar(page)
    lineas += iterar_estaciones_viaje(page)
    # de-dup preservando orden
    vistas = set()
    salida = []
    for l in lineas:
        if l not in vistas:
            vistas.add(l)
            salida.append(l)
    return salida


def click_boton_sidebar(page, clave: str) -> bool:
    sel = f'[data-testid="stSidebar"] .st-key-nav_{clave} button, [data-testid="stSidebar"] button[kind]:has-text("")'
    boton = page.query_selector(f'.st-key-nav_{clave} button')
    if boton is None:
        return False
    try:
        boton.click(timeout=3000)
        page.wait_for_timeout(800)
        return True
    except Exception:
        return False


def extraer(url_base: str, salida: Path, version: str) -> None:
    resultado: dict[str, dict[str, list[str]]] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for idioma in IDIOMAS:
            page = browser.new_page()
            if version == "actual":
                page.goto(f"{url_base}/?sec=ingreso&lang={idioma}", wait_until="load")
            else:
                page.goto(f"{url_base}/?lang={idioma}", wait_until="load")
            esperar_render(page, 25000)
            page.wait_for_timeout(1000)
            for clave in SECCIONES:
                if version == "actual":
                    page.goto(f"{url_base}/?sec={clave}&lang={idioma}", wait_until="load")
                else:
                    ok = click_boton_sidebar(page, clave)
                    if not ok:
                        print(f"AVISO: no se pudo clickear nav_{clave} en v1.1", file=sys.stderr)
                esperar_render(page, 20000)
                # Se extrae dos veces y se toma la unión: mata la
                # no-determinismo de timing documentado en triage.md (una
                # tab/popover que a veces no re-renderiza a tiempo).
                lineas_a = extraer_seccion(page, clave)
                if version == "actual":
                    page.goto(f"{url_base}/?sec={clave}&lang={idioma}", wait_until="load")
                else:
                    click_boton_sidebar(page, clave)
                esperar_render(page, 20000)
                lineas_b = extraer_seccion(page, clave)
                vistas = set()
                lineas = []
                for l in lineas_a + lineas_b:
                    if l not in vistas:
                        vistas.add(l)
                        lineas.append(l)
                resultado.setdefault(clave, {})[idioma] = lineas
                print(
                    f"[{version}] {clave}/{idioma}: {len(lineas)} lineas "
                    f"(corrida1={len(lineas_a)} corrida2={len(lineas_b)})",
                    file=sys.stderr,
                )
            page.close()
        browser.close()
    salida.parent.mkdir(parents=True, exist_ok=True)
    salida.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Escrito {salida}", file=sys.stderr)


def comparar(v11: Path, actual: Path, informe: Path) -> None:
    d1 = json.loads(v11.read_text(encoding="utf-8"))
    d2 = json.loads(actual.read_text(encoding="utf-8"))
    out = ["# Informe de regresión de contenido — v1.1 vs actual\n"]
    for clave in SECCIONES:
        out.append(f"\n## Sección: {clave}\n")
        for idioma in IDIOMAS:
            l1 = d1.get(clave, {}).get(idioma, [])
            l2 = d2.get(clave, {}).get(idioma, [])
            s1, s2 = set(l1), set(l2)
            falta = sorted(s1 - s2)
            nuevo = sorted(s2 - s1)
            cambios = []
            usados_nuevo = set()
            for f in list(falta):
                mejor, mejor_r = None, 0.0
                for n in nuevo:
                    if n in usados_nuevo:
                        continue
                    r = difflib.SequenceMatcher(None, f, n).ratio()
                    if r > mejor_r:
                        mejor, mejor_r = n, r
                if mejor is not None and mejor_r >= 0.8:
                    cambios.append((f, mejor, mejor_r))
                    usados_nuevo.add(mejor)
                    falta.remove(f)
            nuevo = [n for n in nuevo if n not in usados_nuevo]
            out.append(f"\n### {idioma} (v1.1: {len(l1)} líneas · actual: {len(l2)} líneas)\n")
            if cambios:
                out.append("**Cambió:**\n")
                for f, n, r in cambios:
                    out.append(f"- `{f}` → `{n}` (ratio {r:.2f})")
                out.append("")
            if falta:
                out.append("**Falta (estaba en v1.1, ya no está):**\n")
                for f in falta:
                    out.append(f"- {f}")
                out.append("")
            if nuevo:
                out.append("**Nuevo (no estaba en v1.1):**\n")
                for n in nuevo:
                    out.append(f"- {n}")
                out.append("")
            if not (cambios or falta or nuevo):
                out.append("Sin diferencias.\n")
    informe.parent.mkdir(parents=True, exist_ok=True)
    informe.write_text("\n".join(out), encoding="utf-8")
    print(f"Escrito {informe}", file=sys.stderr)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "extraer":
        _, _, url_base, salida, version = sys.argv
        extraer(url_base.rstrip("/"), Path(salida), version)
    elif cmd == "comparar":
        _, _, v11, actual, informe = sys.argv
        comparar(Path(v11), Path(actual), Path(informe))
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
