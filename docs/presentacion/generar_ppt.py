# -*- coding: utf-8 -*-
# generar_ppt.py — la exposición, generada desde los artefactos
# ---------------------------------------------------------------------------
# Autor: Yoichi Palacios Tanaka (IchiSieben) — proyecto ENAHO 2025
# Licencia: Apache-2.0 (ver LICENSE)
# ---------------------------------------------------------------------------
"""
Genera docs/presentacion/ENAHO_exposicion.pptx: 16:9, 12 láminas, notas del
orador en todas. La mesa evalúa un curso de DESPLIEGUE de machine learning:
el mazo defiende la arquitectura y sus garantías; el detalle estadístico
—torneo de nueve, embudo, umbral, prevalencia— vive en las notas, listo para
preguntas, no en pantalla.

Reglas de composición (verificar_ppt.py comprueba las medibles):

  - cada título es una AFIRMACIÓN completa, nunca un tema;
  - cero rótulos de estructura: ni «Bloque», ni «lámina n de m»;
  - un elemento visual dominante por lámina;
  - franja de acento constante en la cabecera de todas las láminas;
  - capturas tratadas como capturas de producto: recorte útil, borde fino,
    esquinas suaves;
  - cuerpo a 18 pt mínimo en sans (Calibri); la monoespaciada se reserva para
    cifras, nombres de archivo y código. Excepciones declaradas: etiquetas de
    tarjeta (14 pt, versalita mono) y pies de fuente (12 pt), sin prosa.

Regla de oro, la misma de toda la auditoría: NINGÚN número escrito de memoria.
Todo sale de:

  - models/ui_artifacts.json          (torneo, autopsia, clasificador, meta)
  - models/feature_schema.json        (variables, targets, punto operativo)
  - reports/ablacion_clasificador.csv (ablación estructural)
  - INFORME_AUDITORIA.md              (embudo N, rejilla ampliada, INEI)
  - app/referencias.py                (n.º de referencias verificadas)
  - docs/presentacion/salida_consola_verificacion.txt (VS Code = Streamlit)
  - el propio repositorio y el disco    (peso versionado, tamaño de data/)

`buscar()` aborta la generación si un patrón no aparece: preferimos no tener
presentación a tener una con una cifra inventada.

Correr:  .venv/Scripts/python.exe docs/presentacion/generar_ppt.py
"""
from pathlib import Path
import csv
import json
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

RAIZ = Path(__file__).resolve().parents[2]
AQUI = RAIZ / "docs" / "presentacion"
FIGS = AQUI / "figuras"
LOGOS = AQUI / "logos"
FIGS.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Artefactos — la única fuente de cifras
# ---------------------------------------------------------------------------
UA = json.loads((RAIZ / "models" / "ui_artifacts.json").read_text(encoding="utf-8"))
FS = json.loads((RAIZ / "models" / "feature_schema.json").read_text(encoding="utf-8"))
INFORME = (RAIZ / "INFORME_AUDITORIA.md").read_text(encoding="utf-8")
CONSOLA = (AQUI / "salida_consola_verificacion.txt").read_text(encoding="utf-8")
REQUISITOS = (RAIZ / "requirements.txt").read_text(encoding="utf-8")

sys.path.insert(0, str(RAIZ / "app"))
import referencias as REFS  # noqa: E402

with open(RAIZ / "reports" / "ablacion_clasificador.csv", encoding="utf-8") as f:
    ABLACION = list(csv.DictReader(f))


def buscar(patron: str, texto: str = INFORME,
           quien: str = "INFORME_AUDITORIA.md") -> str:
    """Un número del informe se extrae, no se copia. Si no está, se aborta."""
    m = re.search(patron, texto)
    if not m:
        raise SystemExit(f"No se encontró {patron!r} en {quien}: no se inventa.")
    return m.group(1)


# Embudo de datos (INFORME §4, reconstruido reejecutando la Fase 1). En este
# mazo el embudo se CUENTA, no se proyecta: vive en las notas del orador.
EMBUDO = {
    "crudo": buscar(r"Módulo 05 — Empleo e ingresos \(crudo\)\s+([\d.]+)"),
    "ocupados": buscar(r"\nOcupados\s+([\d.]+)"),
    "modelado": buscar(r"Dataset de modelado\s+([\d.]+) filas"),
    "torneo": buscar(r"Muestra del torneo E1–E9\s+([\d.]+)"),
    "train": buscar(r"Train ([\d.]+)"),
    "test": buscar(r"Train [\d.]+\s+·\s+Test ([\d.]+)"),
}
# Rejilla ampliada del regresor (INFORME §6)
REJILLA = {
    "vieja": buscar(r"3 de 3 en el borde\*?\*? \| ([\d]+,[\d]+) \|"),
    "nueva": buscar(r"ninguno en el borde \| \*\*([\d]+,[\d]+)\*\* \|"),
    "mejora_pct": buscar(r"−3,59 \(−([\d]+,[\d]+) %\)"),
}
# Validación externa del target (INFORME §5) y AC-5 (el 88,6 %)
EXTERNA = {
    "propia": buscar(r"Nacional ponderado \| ([\d]+,[\d]+) %"),
    "inei": buscar(r"Nacional ponderado \| [\d,]+ % \| ([\d]+,[\d]+) %"),
    "inei_1_10": buscar(r"\| \*\*(88,6) %\*\* \| INEI, tramo \*\*1-10\*\*"),
}
N_REFERENCIAS = len(REFS.REFERENCIAS)
# La tasa propia de la categoría «Hasta 20», que es lo que el 88,6 % del INEI
# NO era. Sale del precómputo, que es exactamente el arreglo que se hizo:
# la cifra se calcula, no se escribe a mano (INFORME §2.2.1).
TASA_HASTA20 = (UA["clasificador"]["tasas_observadas"]["tamano_empresa"]
                ["grupos"]["Hasta 20"]["pct_ponderado"])

TAB_TORNEO = {f["ID"]: f for f in UA["torneo"]["tabla"]}
CLF_COMP = UA["clasificador"]["comparacion"]      # GB / RF / logística
REG, CLF = FS["regresor"], FS["clasificador"]
PUNTO = CLF["punto_operativo"]
META = UA["meta"]
CURVA = UA["clasificador"]["curva_umbral"]
BASE_PR = UA["clasificador"]["pr"]["baseline"]
IMP_REG = UA["regresor"]["importancia_permutacion"]
IMP_CLF = UA["clasificador"]["importancia_permutacion"]
E6 = UA["torneo"]["explicativo_e6_ponderado"]
ABL_V2 = next(f for f in ABLACION if "categoria" in f["variante"])

# La consola local y la app en la nube deben decir lo mismo — se verifica AQUÍ,
# al generar: si algún día divergen, la PPT no se genera.
ING_TIPICO = buscar(r"ingreso típico\s+\(mediana\): S/ ([\d.]+)", CONSOLA, "consola")
ING_ESPERADO = buscar(r"ingreso esperado.*: +S/ ([\d.]+)", CONSOLA, "consola")
PROBA = buscar(r"probabilidad de informalidad: ([\d]+,[\d]+%)", CONSOLA, "consola")
# La consola imprime «97,5%» pegado; en la lámina va con espacio, como en
# la app y como manda la ortografía.
PROBA_ES = PROBA.replace("%", " %")
SKLEARN_REQ = buscar(r"scikit-learn==([\d.]+)", REQUISITOS, "requirements.txt")
if SKLEARN_REQ != META["version_scikit_learn"]:
    raise SystemExit(
        f"requirements.txt fija scikit-learn {SKLEARN_REQ} pero los artefactos "
        f"se generaron con {META['version_scikit_learn']}: los pickles no "
        f"cargarían en la nube. No se genera la presentación.")

# Variables: las mismas 11 en los dos modelos. Se comprueba, no se supone.
NUM = [f for f in REG["features"] if f["tipo"] == "numerico"]
CAT = [f for f in REG["features"] if f["tipo"] == "categorico"]
if [f["nombre"] for f in REG["features"]] != [f["nombre"] for f in CLF["features"]]:
    raise SystemExit("Regresor y clasificador ya no comparten features: "
                     "la tabla de variables daría por buena una tabla que no lo es.")
N_NIVELES = sum(len(f["opciones"]) for f in CAT)

# Peso de lo versionado y de lo que se queda fuera — medido, no recordado.
# El número de commits NO se imprime en ninguna lámina: el commit que publica
# la presentación lo cambiaría y la cifra nacería desactualizada.
import subprocess  # noqa: E402


def _git(*a) -> str:
    return subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8").stdout.strip()


SALIDA_REL = "docs/presentacion/ENAHO_exposicion.pptx"
VERSIONADOS = [f for f in _git("ls-files").split("\n") if f]
REPO = {
    "n_archivos": len(VERSIONADOS),
    # Sin contar la propia presentación: si se incluyera, la cifra que la
    # lámina de arquitectura imprime cambiaría al guardarla y no habría forma
    # de verificarla (el archivo se mide antes de existir en su tamaño final).
    "mb": round(sum((RAIZ / f).stat().st_size for f in VERSIONADOS
                    if (RAIZ / f).exists() and f != SALIDA_REL) / 1e6, 2),
}
_DATA = RAIZ / "data"
DATOS_MB = (round(sum(x.stat().st_size for x in _DATA.rglob("*") if x.is_file())
                  / 1e6, 1) if _DATA.exists() else None)
UI_KB = round((RAIZ / "models" / "ui_artifacts.json").stat().st_size / 1024, 1)
JOBLIB_KB = round(sum((RAIZ / "models" / n).stat().st_size for n in
                      ("regresor_e9.joblib", "clasificador_gb.joblib")) / 1024)

# ---------------------------------------------------------------------------
# 2. Paleta y tipografía — las del tema claro de la app (app/estilos.py)
# ---------------------------------------------------------------------------
C = {
    "fondo": "F7F5F0", "superficie": "FCFBF8", "superficie_alta": "F1EFE8",
    "borde": "D5D1C6", "texto": "1E232B", "texto_medio": "49525F",
    "texto_tenue": "5F6875", "acento": "4353CC", "acento_alto": "3542B8",
    "acento_fondo": "E6E8FA", "buena": "177A4C", "buena_fondo": "E2F2E9",
    "media": "8A5D0B", "media_fondo": "F6ECD6", "mala": "B92F33",
    "mala_fondo": "F9E3E4", "consola_fondo": "11151C", "consola_texto": "D6E2D0",
}
FUENTE = "Calibri"
MONO = "Consolas"

# Escala tipográfica. El mínimo de cuerpo es 18: proyectado, menos no se lee.
T_TITULO, T_ENTRADILLA, T_CUERPO = 36, 20, 18
T_CIFRA, T_CIFRA_XL = 34, 54
T_TABLA, T_TABLA_CAB = 18, 16
# Excepciones DECLARADAS al mínimo de 18 pt: ninguna lleva prosa.
T_ETIQUETA, T_PIE = 14, 12


def rgb(clave):
    return RGBColor.from_string(C[clave])


def mpl(clave):
    return "#" + C[clave]


def n(x) -> str:
    """1234.5 -> '1.234' (formato español, como la app)."""
    return f"{x:,.0f}".replace(",", ".")


def d(x, dec=2) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# 3. Figuras (matplotlib). Cada una es el elemento dominante de su lámina.
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": [FUENTE, "Segoe UI", "DejaVu Sans"],
    "figure.facecolor": mpl("fondo"), "axes.facecolor": mpl("fondo"),
    "savefig.facecolor": mpl("fondo"), "text.color": mpl("texto"),
    "axes.labelcolor": mpl("texto_medio"), "xtick.color": mpl("texto_medio"),
    "ytick.color": mpl("texto_medio"), "axes.edgecolor": mpl("borde"),
})


def _guardar(fig, nombre):
    p = FIGS / f"{nombre}.png"
    fig.savefig(p, dpi=200, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return p


def _limpiar(ax, ejes=("top", "right")):
    for e in ejes:
        ax.spines[e].set_visible(False)


def fig_arquitectura():
    # Aspecto ancho a propósito: la lámina la encaja por altura y así el
    # diagrama ocupa casi todo el ancho útil en vez de quedar encogido.
    fig, ax = plt.subplots(figsize=(14.2, 5.1))
    ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")

    def caja(x, y, w, h, titulo, lineas, fc, ec, tc=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.7",
                                    fc=fc, ec=ec, lw=1.8, zorder=3))
        ax.text(x + w / 2, y + h - 2.6, titulo, ha="center", va="top",
                fontsize=16.5, fontweight="bold", color=tc or mpl("texto"),
                zorder=4)
        ax.text(x + w / 2, y + h - 7.6, "\n".join(lineas), ha="center", va="top",
                fontsize=13, color=mpl("texto_medio"), linespacing=1.6, zorder=4)

    def flecha(x1, y1, x2, y2, texto=None, dx=0, dy=2.0, ha="center"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=26, lw=2.6, color=mpl("acento"),
                                     zorder=5, shrinkA=0, shrinkB=0))
        if texto:
            ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, texto, ha=ha,
                    va="center", fontsize=13.5, color=mpl("acento_alto"),
                    fontweight="bold", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.22", fc=mpl("fondo"), ec="none"))

    caja(1, 28, 24, 19, "1 · Microdatos INEI",
         ["data/  ·  local", "ENAHO 2025", "módulos 02 · 03 · 05"],
         mpl("superficie_alta"), mpl("borde"))
    caja(31.5, 28, 24, 19, "2 · VS Code",
         ["src/00 → src/09", "torneo, entrenamiento", "y precómputo"],
         mpl("superficie"), mpl("borde"))
    caja(62, 28, 24, 19, "3 · Artefactos",
         ["2 modelos .joblib", "ui_artifacts.json", "feature_schema.json"],
         mpl("acento_fondo"), mpl("acento"))
    flecha(25.4, 37.5, 31.1, 37.5, "lee")
    flecha(55.9, 37.5, 61.6, 37.5, "escribe")
    flecha(74, 27.6, 74, 20.4, "git push", dx=5.6, dy=0, ha="left")
    # Fila inferior a 17,5 de alto, no 16: con el cuerpo a 13 pt la tercera
    # línea se salía por debajo del borde de la caja («.streamlit.app»
    # cortado). El alto se calcula para el texto, no al revés.
    caja(62, 3, 24, 17.5, "4 · GitHub",
         ["IchiSieben /", "enaho-ingresos-informalidad", "rama main"],
         mpl("superficie"), mpl("borde"))
    caja(31.5, 3, 24, 17.5, "5 · Streamlit Cloud",
         ["app/streamlit_app.py", "redeploy automático", "en cada push"],
         mpl("superficie"), mpl("borde"))
    caja(1, 3, 24, 17.5, "6 · Navegador",
         ["enaho-ingresos-informalidad", ".streamlit.app"],
         mpl("buena_fondo"), mpl("buena"), tc=mpl("buena"))
    flecha(61.6, 11.75, 55.9, 11.75, "webhook")
    flecha(31.1, 11.75, 25.4, 11.75, "HTTPS")
    ax.add_patch(FancyBboxPatch((29.6, 26.4), 58, 22.2, boxstyle="round,pad=0.5",
                                fc="none", ec=mpl("acento"), lw=1.4,
                                ls=(0, (6, 4)), zorder=2))
    ax.text(58.8, 49.6,
            f"carpeta versionada · {d(REPO['mb'], 2)} MB · "
            f"{REPO['n_archivos']} archivos",
            ha="center", va="bottom", fontsize=14.5, color=mpl("acento_alto"),
            fontweight="bold")
    # El mensaje de los microdatos NO va aquí dentro: incrustado en el hueco
    # entre las dos filas de cajas flotaba suelto y descentraba la figura al
    # recortarla `bbox_inches="tight"`. Vive como banda de ancho completo
    # bajo el diagrama, en la propia lámina.
    return _guardar(fig, "fig_arquitectura")


def fig_precomputo():
    fig, ax = plt.subplots(figsize=(12.2, 5.0))
    ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")

    def bloque(x, w, titulo, subt, items, fc, ec, tc):
        """
        `items` son pares (qué es en llano, nombre técnico). El nombre
        técnico va debajo, gris y pequeño: quien lo conoce lo reconoce y
        quien no, ya entendió la línea de arriba.
        """
        ax.add_patch(FancyBboxPatch((x, 4), w, 32, boxstyle="round,pad=0.6",
                                    fc=fc, ec=ec, lw=1.6, zorder=3))
        ax.text(x + w / 2, 33.4, titulo, ha="center", va="top", fontsize=16,
                fontweight="bold", color=tc, zorder=4)
        ax.text(x + w / 2, 29.4, subt, ha="center", va="top", fontsize=12,
                color=mpl("texto_medio"), zorder=4)
        for k, (llano, tecnico) in enumerate(items):
            cy = 25.0 - k * 4.3
            ax.text(x + 2.6, cy, "·  " + llano, ha="left", va="top",
                    fontsize=12.8, color=mpl("texto"), zorder=4)
            ax.text(x + 4.4, cy - 1.95, tecnico, ha="left", va="top",
                    fontsize=10.5, color=mpl("texto_tenue"), zorder=4)

    n_umbral = len(CURVA["umbral"])
    n_bins = len(UA["clasificador"]["histograma_oof"]["clase_1"])
    n_pdp = len(UA["clasificador"]["dependencia_parcial"])
    bloque(1, 46, "UNA VEZ, en tu máquina", "src/09_precomputar_ui.py",
           [("Qué pasaría con cada corte del umbral",
             f"(curva de umbral · {n_umbral} puntos)"),
            ("Cómo se reparten las probabilidades del modelo",
             f"(histograma fuera de muestra · {n_bins} tramos)"),
            ("Cómo cambia la predicción con cada variable",
             f"(dependencia parcial · {n_pdp} variables)"),
            ("Con qué trabajadores parecidos se compara el perfil",
             "(cohortes y percentiles)"),
            ("Qué porcentaje es informal en cada grupo",
             "(tasas observadas)")],
           mpl("acento_fondo"), mpl("acento"), mpl("acento_alto"))
    bloque(53, 46, "EN CALIENTE, al pulsar el botón", "app/streamlit_app.py",
           [("Estimar el ingreso del perfil",
             "(una llamada a .predict() del regresor)"),
            ("Estimar su probabilidad de informalidad",
             "(una llamada a .predict_proba() del clasificador)"),
            ("Lo demás: leer el archivo guardado y dibujar",
             "(JSON → SVG)")],
           mpl("buena_fondo"), mpl("buena"), mpl("buena"))
    ax.annotate("", xy=(52.4, 20), xytext=(47.6, 20),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=22, lw=2.2,
                                color=mpl("texto_tenue")))
    ax.text(24, 1.5, f"ui_artifacts.json · {d(UI_KB, 1)} KB", ha="center",
            va="center", fontsize=14, fontweight="bold", color=mpl("acento_alto"))
    ax.text(76, 1.5, f"2 modelos .joblib · {n(JOBLIB_KB)} KB", ha="center",
            va="center", fontsize=14, fontweight="bold", color=mpl("buena"))
    return _guardar(fig, "fig_precomputo")


def fig_consola(bloque: str, nombre: str):
    """
    La salida REAL de verificacion_local.py, pintada como una terminal.

    Solo la línea de cabecera y el bloque del modelo pedido: el perfil de
    entrada (los once valores por defecto) se cuenta en las notas, no se
    proyecta. Así las dos consolas caben en una única lámina de verificación.
    """
    lineas = [l.rstrip() for l in CONSOLA.strip().split("\n")]
    inicio = next(k for k, l in enumerate(lineas) if l.startswith(f"[{bloque}"))
    fin = next((k for k, l in enumerate(lineas[inicio + 1:], inicio + 1)
                if l.startswith("[")), len(lineas))
    lineas = [lineas[0]] + [l for l in lineas[inicio:fin] if l.strip()]
    # El ancho se calcula del texto, no se tantea: con `bbox_inches="tight"` un
    # renglón que se sale ensancha el lienzo y deja el panel oscuro corto, y la
    # línea más larga aparece pintada sobre el fondo claro.
    PT_CAR, MARGEN = 0.0965, 0.22          # pulgadas por carácter a 11,5 pt
    ancho = 2 * MARGEN + max(len(l) for l in lineas) * PT_CAR
    alto = 0.285 * len(lineas) + 0.5
    fig = plt.figure(figsize=(ancho, alto), facecolor=mpl("consola_fondo"))
    ax = fig.add_axes((0, 0, 1, 1))
    ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    for k, l in enumerate(lineas):
        resalta = ("S/ " in l or "%" in l or "veredicto" in l)
        ax.text(MARGEN / ancho, 1 - (k + 0.9) / (len(lineas) + 1.0), l,
                family="monospace", fontsize=11.5,
                color="#FFD43B" if resalta else mpl("consola_texto"),
                fontweight="bold" if resalta else "normal", va="center", zorder=2)
    p = FIGS / f"{nombre}.png"
    fig.savefig(p, dpi=200, facecolor=mpl("consola_fondo"))
    plt.close(fig)
    return p


def fig_requisitos():
    """requirements.txt frente a la versión que realmente generó los pickles."""
    lineas = [l for l in REQUISITOS.strip().splitlines()
              if l.strip() and not l.startswith("#")]
    fig = plt.figure(figsize=(11.4, 4.9), facecolor=mpl("fondo"))
    ax = fig.add_axes((0, 0, 1, 1)); ax.axis("off")
    ax.set_xlim(0, 100); ax.set_ylim(-7, 40)
    ax.add_patch(FancyBboxPatch((1, 2), 46, 36, boxstyle="round,pad=0.6",
                                fc=mpl("consola_fondo"), ec=mpl("consola_fondo")))
    ax.text(4, 35.6, "requirements.txt", family="monospace", fontsize=13,
            color="#FFD43B", fontweight="bold", va="top")
    for k, l in enumerate(lineas):
        clave = l.startswith("scikit-learn")
        ax.text(4, 31.4 - k * 2.62, l, family="monospace", fontsize=12.5,
                color="#FFD43B" if clave else mpl("consola_texto"),
                fontweight="bold" if clave else "normal", va="top")
    ax.add_patch(FancyBboxPatch((53, 2), 46, 36, boxstyle="round,pad=0.6",
                                fc=mpl("acento_fondo"), ec=mpl("acento"), lw=1.8))
    ax.text(76, 35.6, "models/ui_artifacts.json  ·  meta", ha="center", va="top",
            family="monospace", fontsize=13, color=mpl("acento_alto"),
            fontweight="bold")
    filas = [("version_scikit_learn", META["version_scikit_learn"]),
             ("version_pandas", META["version_pandas"]),
             ("fecha_generacion", META["fecha_generacion"]),
             ("commit", META["commit"][:7])]
    for k, (kk, vv) in enumerate(filas):
        ax.text(56, 29.4 - k * 4.4, kk, family="monospace", fontsize=12.5,
                color=mpl("texto_medio"), va="top")
        ax.text(96, 29.4 - k * 4.4, str(vv), family="monospace", fontsize=12.5,
                color=mpl("texto"), fontweight="bold", va="top", ha="right")
    ax.text(50, 20, "=", ha="center", va="center", fontsize=34,
            color=mpl("buena"), fontweight="bold")
    ax.text(50, -4, "si no coinciden, el modelo no carga en la nube",
            ha="center", va="center", fontsize=13, color=mpl("mala"),
            fontweight="bold")
    p = FIGS / "fig_requisitos.png"
    fig.savefig(p, dpi=200, facecolor=mpl("fondo"))
    plt.close(fig)
    return p


def fig_importancia():
    eti = {f["nombre"]: f["etiqueta"] for f in REG["features"]}
    # Las del schema son etiquetas de formulario: en un eje no caben enteras.
    eti.update({"exper2": "Experiencia² (cuadrado)",
                "horas_total": "Horas trabajadas por semana",
                "tamano_empresa": "Tamaño de la empresa",
                "anios_educ": "Años de educación aprobados"})
    it = sorted(zip(IMP_REG["variables"], IMP_REG["media"], IMP_REG["desviacion"]),
                key=lambda t: -t[1])
    fig, ax = plt.subplots(figsize=(10.8, 6.0))
    y = list(range(len(it)))[::-1]
    for k, (nom, med, des) in enumerate(it):
        ax.barh(y[k], med, height=0.6,
                color=mpl("acento") if k < 2 else mpl("texto_tenue"),
                alpha=1 if k < 2 else 0.55, xerr=des,
                error_kw=dict(ecolor=mpl("texto_medio"), lw=1.2, capsize=3),
                zorder=3)
        ax.text(med + des + 2.5, y[k], f"S/ {n(med)}", va="center", fontsize=14,
                fontweight="bold", color=mpl("texto"))
        ax.text(-2.5, y[k], eti.get(nom, nom), va="center", ha="right",
                fontsize=13,
                color=mpl("texto") if k < 2 else mpl("texto_medio"))
    ax.set_xlim(0, max(m for _, m, _ in it) * 1.22)
    ax.set_ylim(-0.7, len(it) - 0.3); ax.set_yticks([])
    ax.set_xlabel("Soles/mes de error añadido al barajar la variable al azar\n"
                  f"(permutación, {IMP_REG['n_repeticiones']} repeticiones sobre "
                  f"{n(IMP_REG['n_filas'])} filas de test)",
                  fontsize=12.5, linespacing=1.5)
    ax.tick_params(axis="x", labelsize=11.5)
    ax.grid(axis="x", color="#E4E1D8", lw=0.9, zorder=0)
    _limpiar(ax, ("top", "right", "left"))
    return _guardar(fig, "fig_importancia")


F_REQ = fig_requisitos()
F_CONSOLA_REG = fig_consola("REGRESOR", "fig_consola_regresor")
F_CONSOLA_CLF = fig_consola("CLASIFICADOR", "fig_consola_clasificador")
F_ARQ = fig_arquitectura()
F_IMP = fig_importancia()
F_PRECOMP = fig_precomputo()


# ---------------------------------------------------------------------------
# 4. Utilidades python-pptx
# ---------------------------------------------------------------------------
ANCHO, ALTO = Inches(13.333), Inches(7.5)
MARGEN = 0.62                 # margen izquierdo/derecho común
UTIL = 13.333 - 2 * MARGEN    # ancho útil
prs = Presentation()
prs.slide_width, prs.slide_height = ANCHO, ALTO
BLANCO = prs.slide_layouts[6]

TITULOS: list[str] = []       # se imprimen al final: el mazo en una lista


def lamina(fondo="fondo"):
    s = prs.slides.add_slide(BLANCO)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(fondo)
    # La franja de acento constante: la misma identidad en todas las láminas.
    fr = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, ANCHO, Inches(0.07))
    fr.fill.solid()
    fr.fill.fore_color.rgb = rgb("acento")
    fr.line.fill.background()
    fr.shadow.inherit = False
    return s


def caja(s, x, y, w, h):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


def parrafo_mixto(tf, partes, primero=False, alin=None, esp_despues=8,
                  esp_linea=None):
    """
    Un párrafo con varios tramos de formato distinto, en la MISMA línea base.

    `partes` son tuplas (texto, tamaño, negrita, color, fuente). Sirve para
    lo que un párrafo por tramo no puede dar: «App:» en sans junto a su URL
    en mono sin que la etiqueta caiga en su propio renglón.
    """
    p = (tf.paragraphs[0] if primero and not tf.paragraphs[0].runs
         else tf.add_paragraph())
    for texto, tam, negrita, color, fuente in partes:
        r = p.add_run()
        r.text = texto
        r.font.name = fuente
        r.font.size = Pt(tam)
        r.font.bold = negrita
        r.font.color.rgb = rgb(color)
    if alin:
        p.alignment = alin
    p.space_after = Pt(esp_despues)
    if esp_linea:
        p.line_spacing = esp_linea
    return p


def parrafo(tf, texto, tam=T_CUERPO, color="texto", negrita=False, fuente=FUENTE,
            primero=False, alin=None, esp_despues=8, esp_linea=None):
    p = (tf.paragraphs[0] if primero and not tf.paragraphs[0].runs
         else tf.add_paragraph())
    r = p.add_run()
    r.text = texto
    r.font.name = fuente
    r.font.size = Pt(tam)
    r.font.bold = negrita
    r.font.color.rgb = rgb(color)
    if alin:
        p.alignment = alin
    p.space_after = Pt(esp_despues)
    if esp_linea:
        p.line_spacing = esp_linea
    return p


# Rejilla fija: todas las láminas empiezan el cuerpo a la misma altura. Un
# título de una línea deja aire; uno de dos lo ocupa. Lo que NO puede pasar es
# que el contenido baile de lámina en lámina.
Y_TITULO, Y_ENTRADILLA, Y_CUERPO, Y_PIE = 0.42, 1.54, 2.26, 7.02
ALTO_CUERPO = Y_PIE - Y_CUERPO - 0.16


def titulo(s, texto, entradilla=""):
    """Título de lámina (1-2 líneas a 36 pt) más una línea llana debajo."""
    TITULOS.append(texto)
    tf = caja(s, MARGEN, Y_TITULO, UTIL, 1.06)
    parrafo(tf, texto, tam=T_TITULO, negrita=True, primero=True, esp_despues=0,
            esp_linea=0.92)
    if entradilla:
        tfe = caja(s, MARGEN, Y_ENTRADILLA, min(UTIL, 11.9), 0.66)
        parrafo(tfe, entradilla, tam=T_ENTRADILLA, color="texto_medio",
                primero=True, esp_despues=0, esp_linea=1.02)
    return Y_CUERPO


def panel(s, x, y, w, h, relleno="superficie", borde="borde"):
    fig = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                             Inches(x), Inches(y), Inches(w), Inches(h))
    fig.adjustments[0] = 0.05
    fig.fill.solid()
    fig.fill.fore_color.rgb = rgb(relleno)
    fig.line.color.rgb = rgb(borde)
    fig.line.width = Pt(1.25)
    fig.shadow.inherit = False
    tf = fig.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.20)
    tf.margin_top = tf.margin_bottom = Inches(0.14)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    return fig, tf


def tarjeta(s, x, y, w, h, etiqueta, cifra, nota, color_cifra="acento",
            relleno="superficie", tam_cifra=T_CIFRA):
    """
    Etiqueta + cifra + nota. Las tres son obligatorias: una tarjeta sin nota
    es una caja con aire, y de esas hemos aprendido a desconfiar.
    """
    _, tf = panel(s, x, y, w, h, relleno=relleno)
    parrafo(tf, etiqueta.upper(), tam=T_ETIQUETA, color="texto_tenue",
            fuente=MONO, primero=True, esp_despues=4)
    parrafo(tf, cifra, tam=tam_cifra, color=color_cifra, negrita=True,
            fuente=MONO, esp_despues=6, esp_linea=0.95)
    parrafo(tf, nota, tam=T_CUERPO, color="texto_medio", esp_despues=0,
            esp_linea=1.05)


def tabla(s, x, y, w, h, filas, anchos=None, tam=T_TABLA, tam_cab=T_TABLA_CAB,
          resaltar=None, resaltar_col=None, cols_mono=None):
    """
    `cols_mono` son las columnas de cifra: monoespaciada y alineadas a la
    derecha. Las demás son prosa, en sans y a la izquierda. `resaltar` marca
    una fila (el ganador de una comparación por filas); `resaltar_col`, una
    columna (el ganador cuando los competidores son las columnas).
    """
    cols_mono = (set(range(1, len(filas[0]))) if cols_mono is None
                 else set(cols_mono))
    nf, nc = len(filas), len(filas[0])
    gt = s.shapes.add_table(nf, nc, Inches(x), Inches(y), Inches(w),
                            Inches(h)).table
    if anchos:
        total = sum(anchos)
        for j, a in enumerate(anchos):
            gt.columns[j].width = Emu(int(Inches(w) * a / total))
    for i, fila in enumerate(filas):
        for j, valor in enumerate(fila):
            celda = gt.cell(i, j)
            celda.fill.solid()
            destacada = ((resaltar is not None and i == resaltar) or
                         (resaltar_col is not None and j == resaltar_col and i > 0))
            if i == 0:
                celda.fill.fore_color.rgb = rgb("superficie_alta")
            elif destacada:
                celda.fill.fore_color.rgb = rgb("acento_fondo")
            else:
                celda.fill.fore_color.rgb = rgb("superficie")
            celda.margin_left = celda.margin_right = Inches(0.10)
            celda.margin_top = celda.margin_bottom = Inches(0.05)
            celda.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = celda.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = str(valor)
            r.font.size = Pt(tam_cab if i == 0 else tam)
            r.font.name = MONO if (i > 0 and j in cols_mono) else FUENTE
            r.font.bold = (i == 0) or destacada
            r.font.color.rgb = rgb("texto_tenue" if i == 0 else "texto")
            if j in cols_mono and i > 0:
                p.alignment = PP_ALIGN.RIGHT
    return gt


def imagen(s, ruta, x, y, w=None, h=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    return s.shapes.add_picture(str(ruta), Inches(x), Inches(y), **kw)


def recorte_lateral(nombre: str, destino: str, fraccion: float = 0.205):
    """
    Quita la barra lateral de una captura de la app y guarda el recorte.

    Se hace AQUÍ y no a mano: si el recorte viviera en un script suelto, el
    repositorio tendría una figura que nadie sabe reproducir. Lo que se
    versiona es la captura entera; el recorte se regenera en cada corrida.
    """
    from PIL import Image as _Img
    with _Img.open(FIGS / nombre) as im:
        an, al = im.size
        salida = FIGS / destino
        im.crop((int(an * fraccion), 0, an, al)).save(salida)
    return salida


def recorte_caja(nombre: str, destino: str, caja: tuple):
    """
    Recorta una zona (fracciones izq, arriba, der, abajo) de una captura.

    Para la lámina de verificación: de la página completa de la app solo se
    proyecta la zona donde vive el número que se compara — proyectar la página
    entera encogida es proyectar nada. Las fracciones están calibradas sobre
    las capturas versionadas; si se recapturan, se recalibran.
    """
    from PIL import Image as _Img
    with _Img.open(FIGS / nombre) as im:
        an, al = im.size
        iz, ar, de, ab = caja
        salida = FIGS / destino
        im.crop((int(an * iz), int(al * ar),
                 int(an * de), int(al * ab))).save(salida)
    return salida


def pulir_captura(ruta: Path):
    """
    Trata una captura como captura de producto: esquinas suaves y borde fino.

    Devuelve un PNG con canal alfa junto al original, con sufijo `_pulida`.
    Como el recorte lateral, se regenera en cada corrida y no se versiona
    (.gitignore): lo versionado es siempre la captura original.
    """
    from PIL import Image as _Img
    from PIL import ImageDraw as _Draw
    ruta = Path(ruta)
    with _Img.open(ruta) as im:
        im = im.convert("RGBA")
        an, al = im.size
        radio = max(10, an // 90)
        mascara = _Img.new("L", (an, al), 0)
        _Draw.Draw(mascara).rounded_rectangle((0, 0, an - 1, al - 1),
                                              radius=radio, fill=255)
        im.putalpha(mascara)
        _Draw.Draw(im).rounded_rectangle((0, 0, an - 1, al - 1), radius=radio,
                                         outline="#" + C["borde"], width=3)
        salida = FIGS / f"{ruta.stem}_pulida.png"
        im.save(salida)
    return salida


def imagen_encajada(s, ruta, x, y, w, h, centrar=True):
    """Mete la imagen en la caja (x,y,w,h) sin deformarla y la centra."""
    from PIL import Image as _Img
    iw, ih = _Img.open(ruta).size
    escala = min(w / iw, h / ih)
    aw, ah = iw * escala, ih * escala
    px = x + (w - aw) / 2 if centrar else x
    py = y + (h - ah) / 2 if centrar else y
    return s.shapes.add_picture(str(ruta), Inches(px), Inches(py),
                                width=Inches(aw), height=Inches(ah))


def rotulo(s, x, y, texto, color="acento_alto", tam=T_ETIQUETA):
    """Marca de anotación sobre una captura (lámina del formulario)."""
    fig = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y),
                             Inches(0.06 + 0.098 * len(texto)), Inches(0.30))
    fig.adjustments[0] = 0.35
    fig.fill.solid()
    fig.fill.fore_color.rgb = rgb("acento_fondo")
    fig.line.color.rgb = rgb(color)
    fig.line.width = Pt(1)
    fig.shadow.inherit = False
    tf = fig.text_frame
    tf.margin_left = tf.margin_right = Inches(0.06)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    parrafo(tf, texto, tam=tam, color=color, negrita=True, fuente=MONO,
            primero=True, esp_despues=0, alin=PP_ALIGN.CENTER)
    return fig


def notas(s, texto):
    s.notes_slide.notes_text_frame.text = texto


def pie_fuente(s, texto, y=None):
    y = Y_PIE if y is None else y
    tf = caja(s, MARGEN, y, UTIL, 0.34)
    parrafo(tf, "Fuente: " + texto, tam=T_PIE, color="texto_tenue",
            primero=True, esp_despues=0)


# ---------------------------------------------------------------------------
# Lámina 1 — carátula
# ---------------------------------------------------------------------------
APP_URL = "enaho-ingresos-informalidad.streamlit.app"
REPO_URL = "github.com/IchiSieben/enaho-ingresos-informalidad"

s = lamina()
TITULOS.append("Ingreso laboral e informalidad en el Perú (carátula)")
if (LOGOS / "inei_microdatos_cabecera.jpg").exists():
    imagen(s, LOGOS / "inei_microdatos_cabecera.jpg", MARGEN, 0.42, w=4.4)
if (LOGOS / "enei_logo.png").exists():
    imagen(s, LOGOS / "enei_logo.png", 11.05, 0.34, w=1.68)

tf = caja(s, MARGEN, 1.92, 12.09, 1.66)
parrafo(tf, "Ingreso laboral e informalidad en el Perú", tam=44, negrita=True,
        primero=True, esp_despues=6, esp_linea=0.94)
parrafo(tf, "Dos modelos sobre los microdatos de la ENAHO 2025 (INEI), "
            "desplegados en una app pública", tam=T_ENTRADILLA,
        color="texto_medio", esp_despues=0, esp_linea=1.05)

tf = caja(s, MARGEN, 3.62, 12.09, 0.62)
parrafo(tf, "Curso de Machine Learning · ENEI — Escuela Nacional de "
            "Estadística e Informática", tam=T_CUERPO, primero=True,
        esp_despues=3)
parrafo(tf, "Docente: Orlando Advíncula Zeballos · 25 de agosto de 2026",
        tam=T_CUERPO, color="texto_medio", esp_despues=0)

_, tf = panel(s, MARGEN, 4.48, 12.09, 1.16, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "INTEGRANTES", tam=T_ETIQUETA, color="acento_alto", fuente=MONO,
        primero=True, esp_despues=5)
parrafo(tf, "Alan Nestor Cañazaca Mamani  ·  Magdalena Quico de la Cruz  ·  "
            "Yoichi Palacios Tanaka  ·  Edgar Delgado Ortega",
        tam=T_CUERPO, negrita=True, esp_despues=0, esp_linea=1.05)

# Dos líneas, alineadas a la izquierda: etiqueta en sans y URL en mono
# compartiendo línea base (por eso `parrafo_mixto` y no un párrafo por tramo).
# Son los dos únicos enlaces del mazo; ninguna otra lámina repite direcciones.
_, tf = panel(s, MARGEN, 5.86, 12.09, 1.24)
for _k, (_etq, _url) in enumerate((("App:  ", APP_URL),
                                   ("Repositorio:  ", REPO_URL))):
    # LEFT explícito: el primer párrafo de una autoshape hereda el centrado
    # del shape, y sin esto la línea de «App» salía corrida a la derecha
    # mientras la de «Repositorio» quedaba al margen.
    parrafo_mixto(tf, [(_etq, T_CUERPO, False, "texto_medio", FUENTE),
                       (_url, T_CUERPO, True, "acento_alto", MONO)],
                  primero=(_k == 0), alin=PP_ALIGN.LEFT,
                  esp_despues=10 if _k == 0 else 0)
notas(s, "Buenas. Somos el grupo de Alan, Magdalena, Yoichi y Edgar, del curso "
         "de Machine Learning de la ENEI, con el profesor Orlando Advíncula. "
         "Presentamos dos modelos entrenados sobre los microdatos públicos de "
         "la ENAHO 2025 del INEI: uno estima el ingreso laboral mensual y otro "
         "clasifica si un empleo es informal. Los dos están desplegados en una "
         "app pública de Streamlit que vamos a abrir en vivo. El curso es de "
         "despliegue, así que el peso de la exposición está en cómo llega el "
         "modelo del editor al navegador y en qué garantías tenemos de que lo "
         "que corre en la nube es lo que entrenamos. Esos dos enlaces son los "
         "únicos que hace falta apuntar; no vuelven a aparecer.")

# ---------------------------------------------------------------------------
# Lámina 2 — qué construimos
# ---------------------------------------------------------------------------
s = lamina()
y = titulo(s, "Una app pública, dos modelos: cuánto gana un perfil y si su "
              "empleo es informal",
           "El mismo formulario alimenta dos modelos independientes; cada "
           "pestaña corre el suyo.")
# La franja de la base, arriba: la pauta pide describir los datos antes que
# los modelos. Cada cifra sale de su artefacto (embudo del informe, conteos
# del schema); el detalle variable a variable vive en la tabla mínima de la
# lámina de los modelos.
_, tf = panel(s, MARGEN, y, 12.09, 0.80, relleno="acento_fondo",
              borde="acento")
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
parrafo_mixto(tf, [
    ("La base: ENAHO 2025 (INEI), módulos ", T_CUERPO, False, "texto", FUENTE),
    ("02 · 03 · 05", T_CUERPO, True, "acento_alto", MONO),
    (" — ", T_CUERPO, False, "texto_tenue", FUENTE),
    (EMBUDO["torneo"], T_CUERPO, True, "acento_alto", MONO),
    (" trabajadores con ingreso laboral · ", T_CUERPO, False, "texto", FUENTE),
    (str(len(REG["features"])), T_CUERPO, True, "acento_alto", MONO),
    (" variables de entrada: ", T_CUERPO, False, "texto", FUENTE),
    (str(len(NUM)), T_CUERPO, True, "acento_alto", MONO),
    (" numéricas y ", T_CUERPO, False, "texto", FUENTE),
    (str(len(CAT)), T_CUERPO, True, "acento_alto", MONO),
    (" categóricas", T_CUERPO, False, "texto", FUENTE),
], primero=True, alin=PP_ALIGN.CENTER, esp_despues=0, esp_linea=1.04)
ANCHO_CAP = 5.86
# Recortadas (la barra lateral no se lee proyectada) y pulidas como producto.
imagen_encajada(s, pulir_captura(recorte_lateral("cloud_reg_form.png",
                                                 "cloud_reg_panel.png")),
                MARGEN, y + 0.92, ANCHO_CAP, 2.42)
imagen_encajada(s, pulir_captura(recorte_lateral("cloud_clf_resultado.png",
                                                 "cloud_clf_panel.png")),
                6.85, y + 0.92, ANCHO_CAP, 2.42)
for x, etq, txt in (
        (MARGEN, "Estimación de ingreso  ·  regresión",
         "Estima el ingreso laboral mensual en soles con Gradient Boosting "
         "(especificación E9)."),
        (6.85, "Empleo informal  ·  clasificación",
         "Estima la probabilidad de que el empleo sea informal, con las "
         "mismas 11 variables.")):
    _, tf = panel(s, x, y + 3.46, ANCHO_CAP, 1.28)
    parrafo(tf, etq.upper(), tam=T_ETIQUETA, color="texto_tenue", fuente=MONO,
            primero=True, esp_despues=5)
    parrafo(tf, txt, tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.04)
pie_fuente(s, f"INFORME_AUDITORIA.md §4 (embudo) · models/feature_schema.json "
              f"(variables) · capturas de la app desplegada ({APP_URL}).")
notas(s, f"Primero la base, que es la franja de arriba: microdatos públicos "
         f"de la ENAHO 2025 del INEI, tres módulos —el 02 de miembros del "
         f"hogar, el 03 de educación y el 05 de empleo e ingresos— cruzados "
         f"por persona. Tras los filtros documentados quedan "
         f"{EMBUDO['torneo']} trabajadores con ingreso laboral, descritos por "
         f"once variables: cinco numéricas y seis categóricas, las mismas "
         f"para los dos modelos; el detalle variable a variable viene unas "
         f"láminas más adelante. Sobre esa base, la app tiene cuatro "
         f"secciones y estas son las dos que hacen predicción. A la "
         f"izquierda, el formulario del regresor: se describe un perfil "
         f"laboral y devuelve un ingreso mensual típico en soles. A la "
         f"derecha, la pestaña de informalidad: con las mismas once variables "
         f"devuelve una probabilidad y, según dónde se ponga el umbral, un "
         f"veredicto. Son dos modelos independientes que comparten las "
         f"entradas, no un modelo con dos salidas. Y toda la app se explica "
         f"sola: lectura llana con expander técnico, gráficos etiquetados "
         f"como DATO, MECÁNICA o HIPÓTESIS, la matriz de confusión en "
         f"castellano, y {N_REFERENCIAS} referencias con el enlace comprobado "
         f"una a una. Nadie necesita abrir el código para entender qué está "
         f"viendo.")

# ---------------------------------------------------------------------------
# Lámina 3 — la arquitectura, el ancla del mazo
# ---------------------------------------------------------------------------
s = lamina()
y = titulo(s, "Cada push a main redespliega la app en la nube, sin pasos "
              "manuales",
           "Del editor al navegador solo hay commits: Streamlit Cloud "
           "reconstruye y publica en cada push.")
# El diagrama manda: se lleva el grueso del alto y se centra en el ancho
# útil. Debajo, una banda de ancho completo con el mensaje de los
# microdatos — antes iba incrustado en un hueco del propio diagrama, donde
# flotaba suelto entre las cajas.
ALTO_DIAG = ALTO_CUERPO - 1.10
imagen_encajada(s, F_ARQ, MARGEN, y, 12.09, ALTO_DIAG)
_, tf = panel(s, MARGEN, y + ALTO_DIAG + 0.16, 12.09, 0.88,
              relleno="buena_fondo", borde="buena")
parrafo(tf, f"Los microdatos se quedan en la máquina: los {d(DATOS_MB, 1)} MB "
            f"de la ENAHO no viajan al repositorio, que enlaza a la fuente "
            f"oficial del INEI.",
        tam=T_CUERPO, color="buena", negrita=True, primero=True,
        esp_despues=0, esp_linea=1.06, alin=PP_ALIGN.CENTER)
pie_fuente(s, "docs/arquitectura.md · .gitignore · git ls-files · tamaños "
              "medidos del disco al generar esta lámina")
notas(s, f"Esta es la lámina que sostiene todo lo demás. El pipeline completo "
         f"corre en local, en VS Code: los scripts numerados del 00 al 09 "
         f"leen los microdatos del INEI, entrenan los modelos y escriben los "
         f"artefactos: dos .joblib y los JSON de contrato con la app. Los "
         f"microdatos son {d(DATOS_MB, 1)} megabytes que el .gitignore "
         f"excluye por diseño: no se redistribuyen, se enlaza a la fuente. Lo "
         f"que sale de la máquina son {d(REPO['mb'], 2)} megabytes en "
         f"{REPO['n_archivos']} archivos, en carpetas con un rol fijo: src/ "
         f"para el entrenamiento, models/ para los artefactos, app/ para lo "
         f"desplegado, docs/ y reports/ para la evidencia. GitHub recibe el "
         f"push, avisa por webhook a Streamlit Community Cloud, y la nube "
         f"reconstruye el entorno y publica. Entre guardar en el editor y ver "
         f"el cambio en el navegador no hay ningún paso manual: esa es la "
         f"definición de despliegue continuo que defendemos aquí.")

# ---------------------------------------------------------------------------
# Lámina 4 — artefactos precomputados
# ---------------------------------------------------------------------------
s = lamina()
y = titulo(s, "La app no calcula al abrirse: lee resultados ya guardados",
           "Curvas, histogramas y tablas se calcularon una sola vez, al "
           "entrenar. La app solo las lee y las dibuja.")
DIAGRAMA_H = 3.10
imagen_encajada(s, F_PRECOMP, MARGEN, y, 12.09, DIAGRAMA_H)
# El recorrido real, medido, como elemento central de la lámina. UNA sola
# línea: el texto se acorta hasta que entra, nunca se parte en dos dejando
# la cifra final huérfana en el renglón de abajo. Las cifras van a 26 pt,
# no a 34, justamente para que quepa entera.
_, tf_flujo = panel(s, MARGEN, y + DIAGRAMA_H + 0.13, 12.09,
                    ALTO_CUERPO - DIAGRAMA_H - 0.25, relleno="acento_fondo",
                    borde="acento")
tf_flujo.vertical_anchor = MSO_ANCHOR.MIDDLE
T_FLUJO = 26
parrafo_mixto(tf_flujo, [
    ("Abrir la app", T_CUERPO, False, "texto_medio", FUENTE),
    ("  →  ", T_CUERPO, True, "texto_tenue", MONO),
    ("0", T_FLUJO, True, "buena", MONO),
    (" ejecuciones", T_CUERPO, False, "texto_medio", FUENTE),
    ("      Pulsar «Estimar»", T_CUERPO, False, "texto_medio", FUENTE),
    ("  →  ", T_CUERPO, True, "texto_tenue", MONO),
    ("1", T_FLUJO, True, "acento", MONO),
    (" predicción", T_CUERPO, False, "texto_medio", FUENTE),
    ("  →  ", T_CUERPO, True, "texto_tenue", MONO),
    (f"S/ {ING_TIPICO}", T_FLUJO, True, "acento_alto", MONO),
], primero=True, alin=PP_ALIGN.CENTER, esp_despues=0)
pie_fuente(s, "src/09_precomputar_ui.py · models/ui_artifacts.json · "
              "models/*.joblib · docs/presentacion/verificacion_local.py")
notas(s, f"Este es el recorrido real de abrir la app: cero ejecuciones del "
         f"modelo. Las curvas de umbral, los histogramas, las tablas de "
         f"consecuencias y las dependencias parciales se calcularon una sola "
         f"vez, en 09_precomputar_ui.py, y viajan como un JSON de "
         f"{d(UI_KB, 1)} kilobytes. La app en producción abre ese archivo y "
         f"dibuja: no hay nada que calcular ahí. Los .joblib solo entran "
         f"cuando el usuario arma un perfil y pulsa «Estimar»: una llamada a "
         f"predict, que da S/ {ING_TIPICO} para el perfil por defecto, y una "
         f"a predict_proba. Además, cache_data y cache_resource evitan releer "
         f"el JSON y los "
         f"modelos en cada interacción de la sesión. Community Cloud da poca "
         f"memoria por aplicación: mantener el trabajo pesado fuera del "
         f"tiempo de ejecución es lo que permite que cargue rápido y no se "
         f"quede sin memoria. Qué gana el usuario: una app que responde al "
         f"instante; qué ganamos nosotros: una app que no se cae.")

# ---------------------------------------------------------------------------
# Lámina 5 — versiones fijadas
# ---------------------------------------------------------------------------
s = lamina()
y = titulo(s, "El pickle exige la misma scikit-learn que lo entrenó: cada "
              "versión queda fijada",
           "requirements.txt fija las versiones que generaron los artefactos, "
           "y Streamlit Cloud reconstruye ese mismo entorno.")
imagen_encajada(s, F_REQ, MARGEN, y, 8.30, 4.35)
tarjeta(s, 9.15, y + 0.08, 3.56, 2.08, "scikit-learn fijado", SKLEARN_REQ,
        "La misma que entrenó los .joblib. Si dejan de coincidir, este "
        "generador aborta.", color_cifra="acento")
tarjeta(s, 9.15, y + 2.26, 3.56, 2.08, "la nube apunta a", "main",
        "Streamlit Cloud sigue esa rama y reconstruye el entorno en "
        "cada push.", color_cifra="buena", tam_cifra=30)
pie_fuente(s, "requirements.txt · models/ui_artifacts.json (meta) · panel de "
              "Streamlit Community Cloud")
notas(s, f"requirements.txt no deja ninguna versión suelta. scikit-learn "
         f"queda fijado en {SKLEARN_REQ}, la misma con la que se generaron "
         f"los .joblib, porque un modelo serializado con otra versión puede "
         f"no cargar, o cargar y comportarse distinto, sin ningún aviso. La "
         f"comprobación no es una promesa del archivo: el propio generador de "
         f"esta presentación compara requirements.txt con la versión anotada "
         f"en los artefactos y se niega a producir el .pptx si no coinciden. "
         f"Del lado de la nube, Streamlit Cloud apunta a un archivo y una "
         f"rama fijos —app/streamlit_app.py en main— y reconstruye ese "
         f"entorno en cada push. La versión de pandas, {META['version_pandas']}, "
         f"queda fijada por la misma razón.")

# ---------------------------------------------------------------------------
# Lámina 6 — el formulario por dentro
# ---------------------------------------------------------------------------
s = lamina()
y = titulo(s, "El formulario no declara ni un campo a mano: se genera desde "
              "feature_schema.json",
           "Cada componente de Streamlit resuelve un problema concreto; si el "
           "schema cambia, el formulario cambia solo.")
ANCHO_IMG = 6.90
imagen(s, pulir_captura(FIGS / "cloud_form.png"), MARGEN, y, w=ANCHO_IMG)
# Las chinchetas se colocan en fracciones de la captura, no en pulgadas
# sueltas: si mañana cambia el tamaño de la imagen, siguen en su sitio.
ALTO_IMG = ANCHO_IMG / 1.5
for k, (fx, fy) in enumerate(((0.10, 0.50), (0.30, 0.42), (0.30, 0.72),
                              (0.28, 0.22)), start=1):
    rotulo(s, MARGEN + fx * ANCHO_IMG, y + fy * ALTO_IMG, str(k))
# La leyenda va numerada y en una sola columna: cuatro entradas cortas caben,
# cuatro entradas explicadas no. El desarrollo largo está en las notas.
COMPONENTES = [
    ("1 · st.radio", "cambia de tema desde PALETAS"),
    ("2 · st.number_input", "una por variable numérica"),
    ("3 · st.selectbox", "una por variable categórica"),
    ("4 · st.expander · st.popover", "lectura llana y lectura técnica"),
]
tfc = caja(s, 7.75, y + 0.02, 4.96, 2.48)
for k, (nom, txt) in enumerate(COMPONENTES):
    parrafo(tfc, nom, tam=T_CUERPO, color="acento_alto", negrita=True,
            fuente=MONO, primero=(k == 0), esp_despues=1)
    parrafo(tfc, txt, tam=T_CUERPO, color="texto_medio", esp_despues=4,
            esp_linea=1.0)
# El control del umbral vive en la OTRA pestaña, así que no está en la
# captura de la izquierda: se capturó aparte de la app en producción
# (capturar_umbral.py) y va DENTRO de este recuadro, con su marcador sobre
# el slider real. El recuadro se dimensiona a partir del alto real de la
# imagen, no al tanteo: así nunca se sale por debajo del pie de fuente.
CAP_UMBRAL = FIGS / "cloud_umbral_control.png"
# Debajo de las cuatro entradas de la leyenda: cada una son dos renglones a
# 18 pt, así que la lista llega hasta ~y+2,6 y el recuadro tiene que
# empezar por debajo o le come la última línea al punto 4.
_Y_PANEL_5 = y + 2.80
if CAP_UMBRAL.exists():
    from PIL import Image as _ImgU
    _iw, _ih = _ImgU.open(CAP_UMBRAL).size
    _ancho_u = 4.62
    _alto_u = _ancho_u * _ih / _iw
    _x_u, _y_u = 7.92, _Y_PANEL_5 + 0.52
    panel(s, 7.75, _Y_PANEL_5, 4.96, _alto_u + 0.76,
          relleno="acento_fondo", borde="acento")
    tf = caja(s, 7.95, _Y_PANEL_5 + 0.14, 4.60, 0.32)
    parrafo(tf, "5 · st.slider + st.fragment", tam=T_CUERPO,
            color="acento_alto", negrita=True, fuente=MONO, primero=True,
            esp_despues=0)
    imagen(s, pulir_captura(CAP_UMBRAL), _x_u, _y_u, w=_ancho_u)
    # El marcador cae sobre el slider real, en fracciones de la captura:
    # el control ocupa la mitad derecha, a media altura.
    rotulo(s, _x_u + 0.66 * _ancho_u, _y_u + 0.44 * _alto_u, "5")
else:
    _, tf = panel(s, 7.75, _Y_PANEL_5, 4.96, 1.20, relleno="acento_fondo",
                  borde="acento")
    parrafo(tf, "5 · st.slider + st.fragment", tam=T_CUERPO,
            color="acento_alto", negrita=True, fuente=MONO, primero=True,
            esp_despues=2)
    parrafo(tf, "En «Empleo informal»: moverlo reejecuta solo ese fragmento.",
            tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.02)
pie_fuente(s, "captura de la app desplegada · app/streamlit_app.py "
              "(componentes realmente usados) · models/feature_schema.json")
notas(s, "El formulario no declara ningún campo a mano: recorre "
         "feature_schema.json y arma un control por variable, número o "
         "selector según el tipo. Los numéricos usan number_input con su paso "
         "y su rango; los categóricos, selectbox con las opciones que "
         "realmente vio el codificador entrenado. Si mañana cambia una "
         "variable en el schema, el formulario cambia solo: el schema es el "
         "contrato entre el entrenamiento y la interfaz. El slider del umbral "
         "vive en un st.fragment: moverlo reejecuta solo ese fragmento y no "
         "la página entera, así que la predicción y los artefactos no se "
         "vuelven a cargar en cada arrastre. El expander separa la lectura "
         "llana de la técnica, el popover resuelve una pregunta puntual sin "
         "ocupar espacio permanente, y el selector de tema es un radio que "
         "lee sus opciones de PALETAS, la misma paleta que estás viendo en "
         "estas láminas.")

# ---------------------------------------------------------------------------
# Lámina 7 — disciplina de entrega
# ---------------------------------------------------------------------------
s = lamina()
y = titulo(s, "Lo que se publica va firmado, con tests y medido sobre la app "
              "viva",
           "Tres controles rodean cada entrega: que la app y los archivos del "
           "modelo digan lo mismo, quién publicó cada versión, y qué se ve "
           "de verdad en la app.")
filas = [["Control", "Qué garantiza", "Dónde se comprueba"],
         ["Tests de contrato",
          "Que la app no pida nada que sus archivos no tengan. Los tres "
          "fallos reales están reproducidos sin navegador: si vuelven, "
          "saltan en local y no en la nube.",
          "tests/test_contratos.py"],
         ["Commits firmados",
          "Cada versión publicada lleva la firma SSH del autor: se sabe quién "
          "publicó qué.",
          "git log --show-signature"],
         ["QA sobre la app viva",
          "Lo que se afirma de la app desplegada se mide en su DOM con "
          "Playwright, no se mira a ojo.",
          "docs/POST_ENTREGA.md"]]
tabla(s, MARGEN, y, 12.09, 2.70, filas, anchos=[22, 52, 26], tam=16,
      tam_cab=16, cols_mono=[])
# Los tres fallos, nombrados. Un recuadro que dice «rompió tres contratos»
# sin decir cuáles no se puede narrar: cada línea dice qué se rompió y qué
# vio el usuario. Salen de tests/test_contratos.py, un test por fallo.
# Cada uno cabe en UNA línea a 18 pt: tres fallos de dos líneas desbordaban
# el panel y se metían debajo del pie de fuente.
_, tf = panel(s, MARGEN, y + 3.12, 12.09, 1.52, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "LOS TRES FALLOS DEL 20 DE AGOSTO, HOY CADA UNO UN TEST",
        tam=T_ETIQUETA, color="acento_alto", fuente=MONO, primero=True,
        esp_despues=5)
for _fallo in (
        "Un tema del selector no estaba en la paleta: elegirlo dejaba la app "
        "en blanco, sin vuelta atrás.",
        "La app pedía un gráfico que el módulo desplegado no tenía: la "
        "página se cortaba a medio dibujo.",
        "Se renombró una clave del artefacto y la app siguió sirviendo la "
        "vieja desde su caché."):
    parrafo(tf, "—  " + _fallo, tam=T_CUERPO, color="texto", esp_despues=2,
            esp_linea=1.0)
pie_fuente(s, "tests/test_contratos.py · git log --show-signature · "
              "docs/POST_ENTREGA.md (estándares de la corrida de entrega)")
notas(s, "Tres controles distintos, cada uno contra un tipo de fallo "
         "distinto. Primero, los tests de contrato: un despliegue del 20 de "
         "agosto rompió la app tres veces con la misma forma de error, la "
         "app pedía algo que su proveedor no tenía: un tema que no estaba en "
         "la paleta, una función de dibujo que no existía, una clave del "
         "artefacto renombrada. Cada uno de esos fallos está hoy reproducido "
         "como un test de pytest que corre sin navegador: si el error vuelve, "
         "salta en local antes del push, no en producción delante del "
         "usuario. Segundo, la autoría: cada commit va firmado con una clave "
         "SSH y git log muestra la firma buena; en un repositorio público, "
         "saber quién publicó qué no es un adorno. Tercero, el QA: cuando "
         "afirmamos algo de la app desplegada, por ejemplo que un gráfico ya "
         "no se corta, no lo miramos a ojo: se mide sobre el DOM real con "
         "Playwright. Ese estándar quedó escrito en la guía de post-entrega "
         "del proyecto.")

# ---------------------------------------------------------------------------
# Lámina 8 — los modelos: RF y GB en los dos problemas (guía)
# ---------------------------------------------------------------------------
s = lamina()
e7, e8, e9 = TAB_TORNEO["E7"], TAB_TORNEO["E8"], TAB_TORNEO["E9"]
gb = next(f for f in CLF_COMP if "Gradient" in f["algoritmo"])
rf = next(f for f in CLF_COMP if "Random" in f["algoritmo"])
lo = next(f for f in CLF_COMP if f not in (gb, rf))
y = titulo(s, "Elegimos Gradient Boosting: le gana a Random Forest por poco, "
              "con las mismas 11 variables",
           "Mismos datos, mismos cinco pliegues, misma semilla; el modelo se "
           "eligió por validación cruzada, nunca por el test.")
filas = [["", "Random Forest", "Gradient Boosting", "Referencia lineal"],
         ["Ingreso mensual — MAE cv, soles",
          d(e8["MAE_cv"], 1), d(e9["MAE_cv"], 1),
          f"{d(e7['MAE_cv'], 1)}  (E7)"],
         ["Empleo informal — PR-AUC cv",
          d(rf["PRAUC_cv"], 4), d(gb["PRAUC_cv"], 4),
          f"{d(lo['PRAUC_cv'], 4)}  (logística)"]]
tabla(s, MARGEN, y, 12.09, 1.60, filas, anchos=[34, 21, 24, 21],
      resaltar_col=2, cols_mono=[1, 2, 3])
filas_v = [["Variables de entrada",
            f"las mismas {len(NUM) + len(CAT)} variables en los dos modelos"],
           [f"Numéricas ({len(NUM)})",
            "años de educación · edad · experiencia · experiencia² · "
            "horas semanales"],
           [f"Categóricas ({len(CAT)})",
            f"sexo · área · dominio geográfico · rama de actividad · tamaño "
            f"de empresa · categoría ocupacional — {N_NIVELES} niveles "
            f"one-hot dentro del pipeline"]]
tabla(s, MARGEN, y + 2.02, 12.09, 1.50, filas_v, anchos=[24, 76], tam=16,
      tam_cab=16, cols_mono=[])
_, tf = panel(s, MARGEN, y + 3.86, 12.09, 0.90, relleno="acento_fondo",
              borde="acento")
parrafo(tf, f"El clasificador no se corta en 0,5: el umbral operativo "
            f"{d(PUNTO['umbral'], 4)} se fijó para que la precisión llegue a "
            f"{d(PUNTO['precision_oof'], 2)} — esa es una decisión de costos, "
            f"no del modelo.",
        tam=T_CUERPO, color="texto", primero=True, esp_despues=0,
        esp_linea=1.06)
pie_fuente(s, "models/ui_artifacts.json (torneo.tabla, "
              "clasificador.comparacion) · models/feature_schema.json · "
              "src/04, src/06")
notas(s, f"La guía pide comparar Random Forest y Gradient Boosting, y esta "
         f"es la comparación en los dos problemas a la vez. En regresión, "
         f"Gradient Boosting se equivoca de media en S/ {d(e9['MAE_cv'], 1)} "
         f"al mes y Random Forest en S/ {d(e8['MAE_cv'], 1)}: empate "
         f"práctico; la mejor especificación lineal, E7, queda en "
         f"S/ {d(e7['MAE_cv'], 1)}, y ahí sí hay distancia. En clasificación "
         f"gana también Gradient Boosting: PR-AUC de {d(gb['PRAUC_cv'], 4)} "
         f"contra {d(rf['PRAUC_cv'], 4)} del Random Forest y "
         f"{d(lo['PRAUC_cv'], 4)} de la logística. Contexto que conviene "
         f"tener a mano: detrás de la fila de regresión hay un torneo de "
         f"nueve especificaciones, de la consigna E1 con "
         f"S/ {d(TAB_TORNEO['E1']['MAE_cv'], 1)} de error hasta E9; los "
         f"datos vienen de un embudo documentado: {EMBUDO['crudo']} registros "
         f"del módulo de empleo, {EMBUDO['ocupados']} ocupados de 14 años o "
         f"más, {EMBUDO['modelado']} con ingreso positivo y "
         f"{EMBUDO['torneo']} casos completos, partidos en {EMBUDO['train']} "
         f"de entrenamiento y {EMBUDO['test']} de prueba con semilla fija. "
         f"Medimos PR-AUC y no accuracy porque la prevalencia es "
         f"{d(BASE_PR, 4)}: decir «informal» a todos ya acierta el "
         f"{d(BASE_PR * 100, 1)} % de las veces. Y la selección es siempre "
         f"por validación cruzada: el test se miró una sola vez, al final.")

# ---------------------------------------------------------------------------
# Lámina 9 — qué variables pesan (guía)
# ---------------------------------------------------------------------------
s = lamina()
_orden = sorted(zip(IMP_REG["variables"], IMP_REG["media"]), key=lambda t: -t[1])
_orden_clf = sorted(zip(IMP_CLF["variables"], IMP_CLF["media"]),
                    key=lambda t: -t[1])
# El título afirma que el trío es el mismo en ambos modelos. Se comprueba,
# no se supone: si algún día los artefactos divergen, no se genera una
# lámina que afirma algo que dejó de ser cierto.
if ({v for v, _ in _orden[:3]} != {v for v, _ in _orden_clf[:3]}):
    raise SystemExit(
        "El top 3 de importancia ya no coincide entre regresor y "
        "clasificador: el título de la lámina de variables lo afirma. "
        "Revísalo antes de generar.")
y = titulo(s, "Las mismas tres variables cargan los dos modelos: categoría, "
              "educación y tamaño de empresa",
           "Con cada modelo ya entrenado, desordenamos una columna a la vez "
           "y medimos cuánto empeora: soles de error en el regresor, puntos "
           "de PR-AUC en el clasificador. Uso, no causa.")
imagen_encajada(s, F_IMP, MARGEN, y, 8.00, 4.55)
tarjeta(s, 8.86, y + 0.05, 3.85, 1.38, "categoría ocupacional",
        f"S/ {n(_orden[0][1])}", "Soles de error si se pierde.",
        color_cifra="acento", tam_cifra=30)
tarjeta(s, 8.86, y + 1.53, 3.85, 1.38, "años de educación",
        f"S/ {n(_orden[1][1])}", "La segunda, mismo cálculo.",
        color_cifra="acento", tam_cifra=30)
# El clasificador, con su propia métrica: cuántos puntos de PR-AUC pierde
# al barajar cada variable. Etiquetas cortas porque en 3,85" no caben las
# del formulario.
_ETI_CORTA = {"tamano_empresa": "tamaño de empresa",
              "categoria": "categoría ocupacional",
              "anios_educ": "años de educación",
              "horas_total": "horas semanales"}
_, tf = panel(s, 8.86, y + 3.01, 3.85, 1.66, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "Y EN EL CLASIFICADOR · TOP 3", tam=T_ETIQUETA,
        color="acento_alto", fuente=MONO, primero=True, esp_despues=4)
for _nom, _med in _orden_clf[:3]:
    parrafo_mixto(tf, [
        (_ETI_CORTA.get(_nom, _nom), T_CUERPO, False, "texto", FUENTE),
        (f"  −{d(_med, 3)}", T_CUERPO, True, "acento_alto", MONO),
    ], esp_despues=2, esp_linea=1.0)
parrafo(tf, "PUNTOS DE PR-AUC PERDIDOS", tam=T_ETIQUETA, color="texto_tenue",
        fuente=MONO, esp_despues=0)
pie_fuente(s, f"models/ui_artifacts.json (importancia_permutacion del "
              f"regresor y del clasificador): {IMP_REG['n_repeticiones']} "
              f"repeticiones sobre {n(IMP_REG['n_filas'])} filas de test en "
              f"ambos")
notas(s, f"Tomamos una variable, desordenamos sus valores al azar entre las "
         f"personas, y medimos cuánto empeora cada modelo ya entrenado. En "
         f"el regresor eso se mide en soles: la categoría ocupacional sube "
         f"el error en unos S/ {n(_orden[0][1])} al mes y los años de "
         f"educación en unos S/ {n(_orden[1][1])}. En el clasificador, el "
         f"mismo ejercicio se mide en puntos de PR-AUC: barajar el tamaño de "
         f"empresa le quita {d(_orden_clf[0][1], 3)}, la categoría "
         f"ocupacional {d(_orden_clf[1][1], 3)} y los años de educación "
         f"{d(_orden_clf[2][1], 3)}. Es el mismo trío en los dos modelos, en "
         f"distinto orden — y coherente con la ablación estructural: quitar "
         f"tamaño y categoría juntas baja el PR-AUC de "
         f"{d(float(ABLACION[0]['PRAUC_cv']), 4)} a "
         f"{d(float(ABL_V2['PRAUC_cv']), 4)}. Ojo con la lectura: esto mide "
         f"cuánto usa cada modelo la variable, no cuánto causa la variable "
         f"en la realidad. Para la lectura causal está el modelo explicativo "
         f"E6, una regresión ponderada aparte que está en la app: ahí cada "
         f"año de educación se asocia a un "
         f"{d(E6['efectos_pct']['anios_educ'], 1)} % más de ingreso y vivir "
         f"en zona urbana a un {d(E6['efectos_pct']['urbano'], 1)} % más.")

# ---------------------------------------------------------------------------
# Lámina 10 — verificación local = nube, los dos modelos (guía)
# ---------------------------------------------------------------------------
s = lamina()
y = titulo(s, "El modelo local y el desplegado dan el mismo número, dígito a "
              "dígito",
           "El mismo perfil se corrió en la consola de VS Code y en la app "
           "pública: tres números, cero diferencias.")
tf = caja(s, MARGEN, y + 0.02, 5.30, 0.26)
parrafo(tf, "VS CODE · CONSOLA LOCAL", tam=T_ETIQUETA, color="texto_tenue",
        fuente=MONO, primero=True, esp_despues=0, alin=PP_ALIGN.CENTER)
tf = caja(s, 6.62, y + 0.02, 6.09, 0.26)
parrafo(tf, "STREAMLIT COMMUNITY CLOUD · APP PÚBLICA", tam=T_ETIQUETA,
        color="texto_tenue", fuente=MONO, primero=True, esp_despues=0,
        alin=PP_ALIGN.CENTER)
# De cada captura de la app se proyecta SOLO la zona del número comparado:
# las tarjetas del regresor y la banda del veredicto del clasificador.
ZONA_REG = pulir_captura(recorte_caja(
    "cloud_reg_tarjetas.png", "cloud_reg_zona.png",
    (0.525, 0.440, 0.955, 0.760)))
ZONA_CLF = pulir_captura(recorte_caja(
    "cloud_clf_resultado.png", "cloud_clf_zona.png",
    (0.525, 0.010, 0.968, 0.198)))
for fila_y, fig_con, captura in ((y + 0.34, F_CONSOLA_REG, ZONA_REG),
                                 (y + 1.86, F_CONSOLA_CLF, ZONA_CLF)):
    imagen_encajada(s, fig_con, MARGEN, fila_y, 5.30, 1.42)
    tf = caja(s, 5.98, fila_y + 0.46, 0.60, 0.50)
    parrafo(tf, "=", tam=40, color="buena", negrita=True, primero=True,
            esp_despues=0, alin=PP_ALIGN.CENTER)
    imagen_encajada(s, captura, 6.62, fila_y, 6.09, 1.42)
TARJETAS = [
    ("ingreso típico (mediana)", f"S/ {ING_TIPICO}",
     "Idéntico en los dos lados.", "acento"),
    ("ingreso esperado (media)", f"S/ {ING_ESPERADO}",
     f"La mediana × Duan {d(REG['smearing_duan'], 4)}.", "acento"),
    ("prob. de informalidad", PROBA_ES,
     f"Umbral {d(PUNTO['umbral'], 4)}: señalado.", "media"),
]
_anch = (12.09 - 0.35 * (len(TARJETAS) - 1)) / len(TARJETAS)
for k, (etq, cif, txt, col) in enumerate(TARJETAS):
    tarjeta(s, MARGEN + k * (_anch + 0.35), y + 3.50, _anch, 1.22,
            etq, cif, txt, color_cifra=col, tam_cifra=22)
pie_fuente(s, "docs/presentacion/verificacion_local.py · "
              "salida_consola_verificacion.txt · capturas de la app desplegada")
notas(s, f"Antes de dar la app por buena corrimos el mismo perfil —los once "
         f"valores por defecto del formulario— en la consola local de VS "
         f"Code y lo comparamos con la app ya desplegada. El regresor da "
         f"S/ {ING_TIPICO} de ingreso típico, la mediana del Gradient "
         f"Boosting E9, y S/ {ING_ESPERADO} de ingreso esperado, que aplica "
         f"el factor de smearing de Duan {d(REG['smearing_duan'], 4)} sobre "
         f"esa mediana. El clasificador da {PROBA_ES} de probabilidad de "
         f"informalidad, y con el umbral operativo {d(PUNTO['umbral'], 4)} el "
         f"empleo queda señalado: la consola imprime INFORMAL y la app dice "
         f"«señalado para focalización», que es lo mismo dicho con cuidado, "
         f"porque la señal es sobre una configuración de empleo y no sobre la "
         f"persona. Un detalle honesto: el formulario del clasificador "
         f"arranca con un valor de horas distinto al del regresor, así que "
         f"los dos perfiles no son idénticos entre sí; dentro de cada fila, "
         f"consola y app comparan exactamente el mismo perfil. Cuidado con lo "
         f"que prueba esto: no valida que el modelo prediga bien, valida que "
         f"la nube corre exactamente el artefacto que entrenamos, no una "
         f"copia vieja ni un reentrenamiento distinto.")

# ---------------------------------------------------------------------------
# Lámina 11 — la auditoría
# ---------------------------------------------------------------------------
s = lamina()
_aut = UA["torneo"]["autopsia"]
y = titulo(s, "Revisamos nuestro propio trabajo: cuatro errores encontrados, "
              "cuatro publicados",
           "Cada cifra contra el archivo que la genera, cada cita contra su "
           "fuente; cada hallazgo, con su origen.")
# La columna «Qué pasó» se narra: cada fila dice qué se leía mal y en qué
# quedó. El texto sigue a la sección «Qué encontró la auditoría» de la app
# (app/streamlit_app.py · AUDITORIA), que es donde vive la versión canónica.
filas = [["Hallazgo", "Dónde nació", "Qué pasó"],
         ["El código de faltante, leído como un sueldo",
          "DATOS DE ORIGEN",
          f"999999 es «no sabe», pero entraba como S/ 999.999: tratarlo como "
          f"faltante subió el R² de {d(_aut['corrida_sucia']['r2'], 3)} a "
          f"{d(_aut['corrida_limpia']['r2'], 3)}"],
         ["La rejilla de hiperparámetros estaba acotada",
          "DECISIÓN PROPIA",
          f"Los tres quedaron en el borde. Ampliada, el error baja de "
          f"S/ {REJILLA['vieja']} a S/ {REJILLA['nueva']} "
          f"({REJILLA['mejora_pct']} %): no se promovió"],
         ["Una cifra del INEI con la etiqueta equivocada",
          "DECISIÓN PROPIA",
          f"El {EXTERNA['inei_1_10']} % es del tramo 1-10 del INEI; nuestra "
          f"categoría «Hasta 20» da {d(TASA_HASTA20, 1)} %"],
         ["Tres afirmaciones distintas sobre el mismo R²",
          "DECISIÓN PROPIA · DOCUMENTACIÓN",
          "Circulaban «0,4–0,5», «rara vez supera 0,4» y «ninguno supera "
          "0,5»: quedó una, sobre Mincer y Card"]]
# Ojo: python-pptx NO recorta una tabla, la CRECE hasta que quepa el texto. El
# alto que se le pasa es un mínimo, así que lo que va debajo hay que colocarlo
# contando con ese crecimiento — o acortar la celda, que es lo que se hizo.
tabla(s, MARGEN, y, 12.09, 2.65, filas, anchos=[30, 23, 47], tam=16,
      tam_cab=16, cols_mono=[])
# La tabla CRECE con el texto: con «Qué pasó» narrado, la cuarta fila baja
# hasta ~y+3,3. El panel arranca por debajo de eso o le pisa la última fila.
_, tf = panel(s, MARGEN, y + 3.44, 12.09, 1.20, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "LA LÍNEA DE MÉTODO", tam=T_ETIQUETA, color="acento_alto",
        fuente=MONO, primero=True, esp_despues=4)
parrafo(tf, "Los de origen se corrigen y se documentan; los propios se "
            "corrigen y se aprende de ellos; los de cita se verifican en el "
            "texto completo. Ninguno se borra en silencio.",
        tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.04)
pie_fuente(s, "INFORME_AUDITORIA.md · models/ui_artifacts.json (torneo.autopsia) "
              "· la sección «Qué encontró la auditoría» de la propia app")
notas(s, f"Antes de publicar, el proyecto se auditó a sí mismo: cada cifra "
         f"contra el script que la genera, cada cita contra su fuente "
         f"original. Aparecieron cuatro problemas y se publicaron los cuatro, "
         f"cada uno con la etiqueta de dónde nació. El primero venía en los "
         f"datos: el INEI codifica «no sabe» como 999999 y ese valor se "
         f"estaba leyendo como un ingreso real de casi un millón de soles; "
         f"convertirlo en dato faltante subió el R² de "
         f"{d(_aut['corrida_sucia']['r2'], 3)} a "
         f"{d(_aut['corrida_limpia']['r2'], 3)} y devolvió el sentido "
         f"económico a los coeficientes. Los otros tres nacieron en nuestro "
         f"propio trabajo. El de la rejilla merece una frase más: la rejilla "
         f"original dejaba los tres hiperparámetros ganadores en el borde, la "
         f"ampliada baja el error a S/ {REJILLA['nueva']}, y aun así NO se "
         f"promovió, porque un {REJILLA['mejora_pct']} % de mejora no "
         f"justifica invalidar la evidencia ya documentada: esa disciplina "
         f"—separar «es mejor» de «vale la pena cambiarlo»— es parte del "
         f"método. Ninguno de los hallazgos cambia el modelo en producción. "
         f"El valor de auditar no fue que no hubiera errores: fue "
         f"encontrarlos y dejarlos escritos.")

# ---------------------------------------------------------------------------
# Lámina 12 — cierre
# ---------------------------------------------------------------------------
s = lamina()
y = titulo(s, "El regresor compara perfiles; el clasificador señala empleos, "
              "no personas",
           "Qué se puede afirmar con cada modelo, qué no, y qué dejó el "
           "despliegue.")
filas = [["", "Regresor de ingreso", "Clasificador de informalidad"],
         ["Sí se puede afirmar",
          f"Un ingreso típico para un perfil, con un error medio de "
          f"S/ {d(REG['metricas_test']['mae_mediana'], 0)} al mes.",
          f"Que una configuración laboral observable se asocia a informalidad "
          f"(PR-AUC de test {d(CLF['metricas_test']['prauc'], 4)})."],
         ["No se puede afirmar",
          "Cuánto va a cobrar una persona concreta. Sirve para comparar "
          "perfiles, no para fijar sueldos.",
          "Que alguien vaya a ser informal. No predice el futuro ni juzga a "
          "ninguna persona."]]
tabla(s, MARGEN, y, 12.09, 2.10, filas, anchos=[20, 40, 40], tam=16,
      tam_cab=16, cols_mono=[])
_, tf = panel(s, MARGEN, y + 2.50, 12.09, 1.26, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "QUÉ DEJÓ EL DESPLIEGUE", tam=T_ETIQUETA, color="acento_alto",
        fuente=MONO, primero=True, esp_despues=6)
parrafo(tf, f"Fijar las versiones exactas (scikit-learn {SKLEARN_REQ}, pandas "
            f"{META['version_pandas']}) y precomputar todo lo pesado en un "
            f"JSON de {d(UI_KB, 1)} KB es lo que hace que la app cargue "
            f"rápido y no se quede sin memoria.",
        tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.06)
tf = caja(s, MARGEN, y + 4.02, 12.09, 0.62)
parrafo(tf, "Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · "
            "Yoichi Palacios Tanaka · Edgar Delgado Ortega",
        tam=T_CUERPO, color="texto", negrita=True, primero=True,
        esp_despues=2, alin=PP_ALIGN.CENTER)
parrafo(tf, "Docente: Orlando Advíncula Zeballos",
        tam=T_CUERPO, color="texto_medio", esp_despues=0, alin=PP_ALIGN.CENTER)
pie_fuente(s, "models/feature_schema.json (métricas de test) · AUTHORS.md · "
              "CITATION.cff · LICENSE (Apache-2.0) y docs/LICENSE-DOCS.md")
notas(s, f"Para cerrar, los límites. El regresor da un ingreso típico con un "
         f"error medio de unos S/ {d(REG['metricas_test']['mae_mediana'], 0)} "
         f"al mes: sirve para comparar perfiles entre sí, no para decirle a "
         f"una persona cuánto va a cobrar. El clasificador identifica si una "
         f"configuración laboral observable se asocia a la informalidad, con "
         f"un PR-AUC de test de {d(CLF['metricas_test']['prauc'], 4)}; es una "
         f"herramienta de focalización, no predice el futuro de nadie. Del "
         f"despliegue nos llevamos dos cosas concretas: fijar las versiones "
         f"exactas de las librerías, porque un pickle no es portable entre "
         f"versiones, y sacar todo el cálculo pesado del tiempo de ejecución. "
         f"Los enlaces están en la portada. Gracias.")

# ---------------------------------------------------------------------------
# Guardado
# ---------------------------------------------------------------------------
GUION = AQUI / "guion_hallazgos.md"
GUION.write_text(f"""# Los cuatro hallazgos, para contarlos en voz alta

> Generado por `docs/presentacion/generar_ppt.py` junto con la lámina de la
> auditoría: las cifras salen de los mismos artefactos que la presentación,
> no se escriben aquí a mano. La versión canónica de cada hallazgo vive en
> `app/streamlit_app.py` (lista `AUDITORIA`) y en `INFORME_AUDITORIA.md`.

Un párrafo por hallazgo. Cada uno se puede contar en unos treinta segundos
y responde a lo mismo: qué se leía mal, cómo se notó, en qué quedó.

## 1. El código de faltante, leído como un sueldo

*Nació en los datos de origen.* El INEI codifica «no sabe» como el valor
999999. Ese número entraba al modelo como si fuera un ingreso real de
999.999 soles al mes, y arrastraba consigo toda la regresión: con esos casos
dentro, vivir en zona urbana aparecía asociado a **once soles** más de
ingreso, una cifra sin ningún sentido económico. Al tratar el centinela como
dato faltante, el R² pasó de **{d(_aut['corrida_sucia']['r2'], 3)}** a
**{d(_aut['corrida_limpia']['r2'], 3)}** y todos los coeficientes
recuperaron su signo y su magnitud esperables. Es el hallazgo más grave de
los cuatro y el único que no nació en una decisión nuestra: le habría pasado
a cualquiera que use estos microdatos sin leer el diccionario de variables.

## 2. La rejilla de hiperparámetros estaba acotada

*Decisión propia.* Al buscar los hiperparámetros del modelo desplegado, los
tres ganadores quedaron en el borde del rango que se había probado — la
señal clásica de que el óptimo estaba fuera de la rejilla y nunca se llegó a
mirar. Se amplió el rango y se volvió a buscar: el error baja de
**S/ {REJILLA['vieja']}** a **S/ {REJILLA['nueva']}**, y los tres
hiperparámetros quedan ya en el interior. La mejora es sistemática: gana en
los cinco pliegues de la validación cruzada. Y aun así **no se promovió**.
El motivo no es que la diferencia sea ruido, porque no lo es: es que
{REJILLA['mejora_pct']} % de mejora no justifica regenerar el artefacto
desplegado, revalidar el factor de smearing y rehacer todo el precómputo de
la interfaz. Separar «es mejor» de «vale la pena cambiarlo» es parte del
método, y el hallazgo queda documentado en vez de barrido.

## 3. Una cifra del INEI con la etiqueta equivocada

*Decisión propia.* Se publicaba que el gradiente por tamaño de empresa
«replica el patrón oficial del INEI, con {EXTERNA['inei_1_10']} % de
informalidad en microempresas». La cifra es real y es del INEI, pero
corresponde a su tramo de **1 a 10 trabajadores**, que no es la categoría
«Hasta 20» que usa este proyecto. Al resumir se perdió el tramo, y el lector
terminaba mapeando el {EXTERNA['inei_1_10']} % a una categoría nuestra cuyo
valor propio es **{d(TASA_HASTA20, 1)} %**. No era un dato inventado: era
una comparación mal etiquetada, que es más difícil de detectar precisamente
porque cada mitad, por separado, es correcta. La app ya no la escribe a
mano: la calcula en el precómputo.

## 4. Tres afirmaciones distintas sobre el mismo R²

*Decisión propia y de documentación.* Sobre cuál es el R² esperable en una
ecuación de ingresos circulaban por el proyecto tres versiones a la vez —
«0,4–0,5», «rara vez supera 0,4» y «ningún R² supera 0,5» — repartidas en
cuatro sitios distintos, cada una escrita en un momento diferente y ninguna
consciente de las otras. Al ir a verificarlas apareció el segundo problema:
las dos fuentes que se citaban para sostenerlas, Lemieux (2006) y Heckman,
Lochner y Todd (2006), **no reportan ningún R²**, así que no se las podía
citar para eso. Hoy la afirmación se define **una sola vez**, se apoya en
los cuadros de Mincer y de Card, y dice explícitamente qué parte es lectura
nuestra. La solución de fondo es esa: una cifra, un lugar donde vive.

---

**La línea de método.** Los problemas de origen se corrigen y se documentan;
los propios se corrigen y se aprende de ellos; los de cita se verifican
yendo al texto completo. Ninguno se borra: un hallazgo corregido en silencio
es un hallazgo desperdiciado. Y los dos primeros tenían la misma raíz —
cifras escritas a mano que nadie vuelve a comprobar — así que el arreglo
estructural fue sacarlas del texto y calcularlas en el precómputo.
""", encoding="utf-8")

SALIDA = AQUI / "ENAHO_exposicion.pptx"
prs.save(SALIDA)
print(f"{SALIDA.relative_to(RAIZ)} · {len(prs.slides._sldIdLst)} láminas · "
      f"{SALIDA.stat().st_size / 1e6:.2f} MB")
print(f"{GUION.relative_to(RAIZ)} · guion de los cuatro hallazgos\n")
print("Títulos-afirmación del mazo:")
for k, t in enumerate(TITULOS, 1):
    print(f"  {k:>2}. {t}")
print("\nVerifícala con:  .venv/Scripts/python.exe docs/presentacion/verificar_ppt.py")
