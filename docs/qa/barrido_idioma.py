"""Barrido de idioma: abre las 7 secciones en un idioma, con pestañas,
desplegables, popovers y toggles abiertos, y busca líneas que parezcan del
otro idioma. Lee también el texto que el CSS oculta: definiciones del glosario
(.termino-def) y títulos de los gráficos (<svg><title>).

Uso:
    python docs/qa/barrido_idioma.py <url_base> <informe.md>

Heurística: una línea se marca si tiene al menos 3 palabras funcionales del
otro idioma y más que del propio, o 2 y ninguna del propio. En la vista en
inglés se listan además, para revisión a mano, las líneas con tildes, ñ, ¿ o
¡ que no son nombres propios conocidos. Los títulos de obras citadas se reportan
aparte (una cita en español es legítima en la vista en inglés).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
# Mismo orden que la barra de la app (medir_vistazo corre al importarse).
ORDEN_BARRA = ["inicio", "ingreso", "informalidad", "investigacion", "torneo", "ficha",
               "maquinas"]
from regresion_contenido import (  # noqa: E402
    esperar_render, iterar_estaciones_viaje, iterar_tabs_y_recolectar,
)

ES = set("""de la el los las que para con por una del se es más son en al lo como
pero sin sobre entre cada hasta cuando donde este esta estos estas ese esa hay
tiene según también porque qué cómo cuánto ingreso hora años brecha mujeres
hombres educación""".split())
EN = set("""the of and to in for with by an is are more than this that these those
each from when where which not how what income hour years gap women men
schooling education""".split())
# Palabras compartidas o ambiguas que no cuentan para ninguno.
AMBIGUAS = {"a", "no", "y", "o", "e", "i", "u", "en"}


def palabras(linea: str) -> list[str]:
    return re.findall(r"[a-záéíóúñü]+", linea.lower())


def puntaje(linea: str) -> tuple[int, int]:
    ws = [w for w in palabras(linea) if w not in AMBIGUAS]
    return sum(w in ES for w in ws), sum(w in EN for w in ws)


# Nombres propios con tilde o ñ que son legítimos en la vista en inglés.
# Solo nombres que el barrido encontró: créditos y departamentos. Las
# pestañas y «Perú» NO van aquí: en la vista en inglés no deben aparecer.
PROPIOS = re.compile(r"Ñopo|Cañazaca|Mamani|Palacios|Advíncula|Quico de la Cruz|"
                     r"Junín|Apurímac|Huánuco|San Martín|Áncash|"
                     # Nombres de columnas del modelo (vienen de ui_artifacts.json).
                     r"(categoria|rama|dominio|area|tamano_empresa)_[^,(]+")


def literales() -> dict[str, set[str]]:
    """
    Cruce exacto: los pares L("es", "en") de la app, de 10 caracteres o más.
    Un literal español en la vista EN (o al revés) es un residuo seguro, sin
    depender de palabras funcionales.
    """
    app = (Path(__file__).resolve().parents[2] / "app" / "streamlit_app.py"
           ).read_text(encoding="utf-8")
    pares = re.findall(r'L\(\s*"([^"{}<\\]{10,})",\s*"([^"{}<\\]{10,})"\s*\)', app)
    es = {a.strip() for a, b in pares if a != b}
    en = {b.strip() for a, b in pares if a != b}
    return {"en": es - en, "es": en - es}


def con_tilde(linea: str) -> bool:
    resto = PROPIOS.sub("", linea)
    return bool(re.search(r"[áéíóúñ¿¡]", resto, re.I))


def parece_cita(linea: str) -> bool:
    # «Autor, A. (2008). Título…» o líneas con DOI/URL.
    return bool(re.search(r"\(\d{4}[a-z]?\)|doi|https?://|\bpp?\.\s?\d", linea, re.I))


def texto_oculto_extra(page) -> list[str]:
    return page.evaluate("""() => [
        ...[...document.querySelectorAll('.termino-def')].map(e => e.textContent),
        ...[...document.querySelectorAll('svg title')].map(e => e.textContent),
    ].map(s => (s || '').trim()).filter(Boolean)""")


def barrer(url: str, idioma: str, browser) -> dict[str, list[str]]:
    salida = {}
    page = browser.new_page(viewport={"width": 1366, "height": 900})
    for sec in ORDEN_BARRA:
        page.goto(f"{url}/?sec={sec}&lang={idioma}", wait_until="load")
        page.wait_for_selector(".pie", timeout=120000)
        esperar_render(page, 20000)
        lineas = iterar_tabs_y_recolectar(page) + iterar_estaciones_viaje(page)
        lineas += texto_oculto_extra(page)
        vistas, unicas = set(), []
        for l in lineas:
            for sub in l.split("\n"):
                sub = sub.strip()
                if sub and sub not in vistas:
                    vistas.add(sub)
                    unicas.append(sub)
        salida[sec] = unicas
    page.close()
    return salida


def main() -> None:
    url, informe = sys.argv[1].rstrip("/"), Path(sys.argv[2])
    partes = ["# Barrido de idioma\n",
              "Líneas de cada vista que parecen del otro idioma. Heurística en "
              "`docs/qa/barrido_idioma.py`.\n"]
    total = 0
    ajenos = literales()
    with sync_playwright() as p:
        b = p.chromium.launch()
        for idioma in ("en", "es"):
            datos = barrer(url, idioma, b)
            partes.append(f"\n## Vista `lang={idioma}`\n")
            for sec, lineas in datos.items():
                marcadas, citas, tildes = [], [], []
                for l in lineas:
                    # Literal completo (con límites de palabra: «Voluntarist» no
                    # cuenta dentro de «Voluntarista») y fuera de las citas.
                    exacto = [x for x in ajenos[idioma]
                              if re.search(r"(?<!\w)" + re.escape(x) + r"(?![\w(])", l)]
                    # Si el literal ajeno está dentro de uno propio presente en la
                    # línea («ENAHO 2025 · INEI» en «ENAHO 2025 · INEI (Peru)»), no
                    # es residuo.
                    propios = ajenos["es" if idioma == "en" else "en"]
                    exacto = [x for x in exacto
                              if not any(x in y and y in l for y in propios)]
                    if exacto and not parece_cita(l):
                        marcadas.append(f"{l}  ← literal del otro idioma: «{exacto[0]}»")
                        continue
                    es, en = puntaje(PROPIOS.sub("", l))
                    ajeno, propio = (es, en) if idioma == "en" else (en, es)
                    if (ajeno >= 3 and ajeno > propio) or (ajeno >= 2 and propio == 0):
                        (citas if parece_cita(l) else marcadas).append(l)
                    elif idioma == "en" and con_tilde(l) and not parece_cita(l):
                        tildes.append(l)
                total += len(marcadas) + len(tildes)
                partes.append(f"\n### {sec} · {len(lineas)} líneas · "
                              f"{len(marcadas)} marcadas · {len(citas)} citas\n")
                partes += [f"- {l[:200]}" for l in marcadas]
                if tildes:
                    partes.append("\nCon tildes o ñ (revisar a mano):\n")
                    partes += [f"- {l[:160]}" for l in tildes]
                if citas:
                    partes.append("\nCitas (títulos en su idioma original):\n")
                    partes += [f"- {l[:160]}" for l in citas]
        b.close()
    partes.append(f"\nLiterales cruzados: {len(ajenos['en'])} ES y "
                  f"{len(ajenos['es'])} EN.\n")
    partes.append(f"\n**Total marcadas (sin citas, con tildes): {total}**\n")
    informe.write_text("\n".join(partes), encoding="utf-8")
    print(f"marcadas: {total} -> {informe}")


if __name__ == "__main__":
    main()
