# -*- coding: utf-8 -*-
# generar_ppt.py — la exposición, generada desde los artefactos
# ---------------------------------------------------------------------------
# Autor: Yoichi Palacios (IchiSieben) — proyecto ENAHO 2025
# Licencia: Apache-2.0 (ver LICENSE)
# ---------------------------------------------------------------------------
"""
Genera docs/presentacion/ENAHO_exposicion.pptx (16:9, 16 láminas, notas del
orador) siguiendo la guía del docente. Regla de oro, la misma de toda la
auditoría: NINGÚN número escrito de memoria — todo sale de:

  - models/ui_artifacts.json          (torneo, autopsia, clasificador, meta)
  - models/feature_schema.json        (variables, targets, punto operativo)
  - reports/ablacion_clasificador.csv (ablación estructural)
  - INFORME_AUDITORIA.md              (embudo N, rejilla ampliada, INEI)
  - app/referencias.py                (n.º de referencias verificadas)
  - docs/presentacion/salida_consola_verificacion.txt (VS Code = Streamlit)

Las capturas de la app DESPLEGADA (docs/presentacion/figuras/cloud_*.png)
se tomaron con Playwright sobre https://enaho-ingresos-informalidad.streamlit.app
con el perfil por defecto del formulario — el mismo que corre
verificacion_local.py en consola.

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
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
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

sys.path.insert(0, str(RAIZ / "app"))
import referencias as REFS  # noqa: E402  (n.º de referencias verificadas)

with open(RAIZ / "reports" / "ablacion_clasificador.csv", encoding="utf-8") as f:
    ABLACION = list(csv.DictReader(f))


def buscar(patron: str, texto: str = INFORME, quien: str = "INFORME_AUDITORIA.md") -> str:
    """Un número del informe se extrae, no se copia. Si no está, se aborta."""
    m = re.search(patron, texto)
    if not m:
        raise SystemExit(f"No se encontró {patron!r} en {quien}: no se inventa.")
    return m.group(1)


# Embudo de datos (INFORME §4, reconstruido reejecutando la Fase 1)
EMBUDO = {
    "crudo": buscar(r"Módulo 05 — Empleo e ingresos \(crudo\)\s+([\d.]+)"),
    "ocupados": buscar(r"\nOcupados\s+([\d.]+)"),
    "modelado": buscar(r"Dataset de modelado\s+([\d.]+) filas"),
    "torneo": buscar(r"Muestra del torneo E1–E9\s+([\d.]+)"),
    "dropna": buscar(r"e ingreso\s+−([\d.]+)\s+\(0,6"),
    "train": buscar(r"Train ([\d.]+)"),
    "test": buscar(r"Train [\d.]+\s+·\s+Test ([\d.]+)"),
}
# Rejilla ampliada del regresor (INFORME §6)
REJILLA = {
    "vieja": buscar(r"3 de 3 en el borde\*?\*? \| ([\d]+,[\d]+) \|"),
    "nueva": buscar(r"ninguno en el borde \| \*\*([\d]+,[\d]+)\*\* \|"),
    "mejora_pct": buscar(r"−3,59 \(−([\d]+,[\d]+) %\)"),
    "t": buscar(r"t pareado de ([\d]+,[\d]+)"),
    "p": buscar(r"p = ([\d]+,[\d]+)"),
}
# Validación externa del target (INFORME §5) y AC-5 (el 88,6 %)
EXTERNA = {
    "propia": buscar(r"Nacional ponderado \| ([\d]+,[\d]+) %"),
    "inei": buscar(r"Nacional ponderado \| [\d,]+ % \| ([\d]+,[\d]+) %"),
    "gradiente_1_10": buscar(r"\| \*\*(88,6) %\*\* \| INEI, tramo \*\*1-10\*\*"),
}
N_REFERENCIAS = len(REFS.REFERENCIAS)

TAB_TORNEO = UA["torneo"]["tabla"]           # 9 especificaciones, orden MAE_cv
AUTOPSIA = UA["torneo"]["autopsia"]
CLF_COMP = UA["clasificador"]["comparacion"]  # GB / RF / logística
REG = FS["regresor"]
CLF = FS["clasificador"]
PUNTO = CLF["punto_operativo"]
META = UA["meta"]

# La consola local y la app en la nube deben decir lo mismo — se verifica AQUÍ,
# al generar: si algún día divergen, la PPT no se genera.
ING_TIPICO = buscar(r"ingreso típico\s+\(mediana\): S/ ([\d.]+)", CONSOLA, "consola")
ING_ESPERADO = buscar(r"S/ ([\d.]+)\s*\n\n\[CLASIFICADOR", CONSOLA + "\n", "consola") \
    if False else buscar(r"ingreso esperado.*: +S/ ([\d.]+)", CONSOLA, "consola")
PROBA = buscar(r"probabilidad de informalidad: ([\d]+,[\d]+%)", CONSOLA, "consola")

# ---------------------------------------------------------------------------
# 2. Paleta — la del tema claro de la app (app/estilos.py)
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
MONO = "Courier New"


def rgb(clave):
    return RGBColor.from_string(C[clave])


def mpl(clave):
    return "#" + C[clave]


# ---------------------------------------------------------------------------
# 3. Figuras generadas (matplotlib, paleta del tema claro)
# ---------------------------------------------------------------------------
def fig_importancia_regresor():
    imp = UA["regresor"]["importancia_permutacion"]
    pares = sorted(zip(imp["variables"], imp["media"]), key=lambda x: x[1])
    et = {"categoria": "Categoría ocupacional", "anios_educ": "Años de educación",
          "tamano_empresa": "Tamaño de la empresa", "horas_total": "Horas semanales",
          "edad": "Edad", "dominio": "Dominio geográfico", "rama": "Rama de actividad",
          "sexo": "Sexo", "area": "Área", "exper": "Experiencia", "exper2": "Experiencia²"}
    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=200)
    fig.patch.set_facecolor(mpl("superficie"))
    ax.set_facecolor(mpl("superficie"))
    nombres = [et.get(v, v) for v, _ in pares]
    valores = [m for _, m in pares]
    ax.barh(nombres, valores, color=mpl("acento"), height=0.62)
    for i, v in enumerate(valores):
        ax.text(v + 1.5, i, f"S/ {v:,.0f}".replace(",", "."), va="center",
                fontsize=10, color=mpl("texto"), family="monospace")
    ax.set_xlabel("S/ de error extra al permutar la variable",
                  fontsize=9, color=mpl("texto_medio"))
    ax.tick_params(colors=mpl("texto"), labelsize=10)
    for s in ax.spines.values():
        s.set_color(mpl("borde"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, max(valores) * 1.18)
    fig.tight_layout()
    ruta = FIGS / "fig_importancia_regresor.png"
    fig.savefig(ruta, facecolor=fig.get_facecolor())
    plt.close(fig)
    return ruta


def fig_torneo_mae():
    filas = sorted(TAB_TORNEO, key=lambda f: f["MAE_cv"])
    ids = [f["ID"] for f in filas][::-1]
    maes = [f["MAE_cv"] for f in filas][::-1]
    colores = [mpl("acento") if i == "E9" else
               ("#8A94C7" if i == "E8" else mpl("borde")) for i in ids]
    fig, ax = plt.subplots(figsize=(5.4, 4.0), dpi=200)
    fig.patch.set_facecolor(mpl("superficie"))
    ax.set_facecolor(mpl("superficie"))
    ax.barh(ids, maes, color=colores, height=0.62)
    for i, v in enumerate(maes):
        ax.text(v + 8, i, f"{v:,.0f}".replace(",", "."), va="center",
                fontsize=10, color=mpl("texto"), family="monospace")
    ax.set_xlabel("MAE de validación cruzada (S/ al mes) — menor es mejor",
                  fontsize=9, color=mpl("texto_medio"))
    ax.tick_params(colors=mpl("texto"), labelsize=10)
    for s in ax.spines.values():
        s.set_color(mpl("borde"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(0, max(maes) * 1.15)
    fig.tight_layout()
    ruta = FIGS / "fig_torneo_mae.png"
    fig.savefig(ruta, facecolor=fig.get_facecolor())
    plt.close(fig)
    return ruta


def fig_consola():
    """La salida REAL de verificacion_local.py, tal cual, como imagen."""
    lineas = CONSOLA.rstrip().splitlines()
    fig, ax = plt.subplots(figsize=(6.4, 0.185 * len(lineas) + 0.5), dpi=200)
    fig.patch.set_facecolor(mpl("consola_fondo"))
    ax.set_facecolor(mpl("consola_fondo"))
    ax.axis("off")
    texto = "\n".join(lineas)
    ax.text(0.012, 0.985, "PS> .venv/Scripts/python.exe docs/presentacion/"
            "verificacion_local.py\n" + texto,
            family="monospace", fontsize=7.6, color=mpl("consola_texto"),
            va="top", ha="left", transform=ax.transAxes, linespacing=1.35)
    fig.tight_layout(pad=0.4)
    ruta = FIGS / "fig_consola_local.png"
    fig.savefig(ruta, facecolor=fig.get_facecolor())
    plt.close(fig)
    return ruta


F_IMP = fig_importancia_regresor()
F_MAE = fig_torneo_mae()
F_CONSOLA = fig_consola()
F_PR_CAL = RAIZ / "reports" / "figuras" / "03_pr_calibracion.png"
F_IMP_CLF = RAIZ / "reports" / "figuras" / "03_importancia_clasificador.png"

# ---------------------------------------------------------------------------
# 4. Utilidades python-pptx
# ---------------------------------------------------------------------------
ANCHO, ALTO = Inches(13.333), Inches(7.5)
prs = Presentation()
prs.slide_width, prs.slide_height = ANCHO, ALTO
BLANCO = prs.slide_layouts[6]  # en blanco


def lamina(fondo="fondo"):
    s = prs.slides.add_slide(BLANCO)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(fondo)
    return s


def caja(s, x, y, w, h):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tb.text_frame.word_wrap = True
    tb.text_frame.margin_left = tb.text_frame.margin_right = 0
    tb.text_frame.margin_top = tb.text_frame.margin_bottom = 0
    return tb.text_frame


def parrafo(tf, texto, tam=15, color="texto", negrita=False, fuente=FUENTE,
            primero=False, alin=None, esp_despues=6):
    p = tf.paragraphs[0] if primero and not tf.paragraphs[0].runs else tf.add_paragraph()
    r = p.add_run()
    r.text = texto
    r.font.name = fuente
    r.font.size = Pt(tam)
    r.font.bold = negrita
    r.font.color.rgb = rgb(color)
    if alin:
        p.alignment = alin
    p.space_after = Pt(esp_despues)
    return p


def titulo(s, texto, y=0.42, tam=30):
    tf = caja(s, 0.55, y, 12.2, 0.95)
    parrafo(tf, texto, tam=tam, negrita=True, primero=True)


def panel(s, x, y, w, h, relleno="superficie", borde="borde"):
    from pptx.enum.shapes import MSO_SHAPE
    fig = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                             Inches(x), Inches(y), Inches(w), Inches(h))
    fig.adjustments[0] = 0.055
    fig.fill.solid()
    fig.fill.fore_color.rgb = rgb(relleno)
    fig.line.color.rgb = rgb(borde)
    fig.line.width = Pt(1)
    fig.shadow.inherit = False
    tf = fig.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.16)
    tf.margin_top = tf.margin_bottom = Inches(0.10)
    tf.vertical_anchor = MSO_ANCHOR.TOP
    return fig, tf


def tarjeta_cifra(s, x, y, w, etiqueta, cifra, nota=None, color_cifra="acento",
                  h=1.55, relleno="superficie"):
    _, tf = panel(s, x, y, w, h, relleno=relleno)
    parrafo(tf, etiqueta.upper(), tam=10.5, color="texto_tenue", fuente=MONO,
            primero=True, esp_despues=2)
    parrafo(tf, cifra, tam=25, color=color_cifra, negrita=True, fuente=MONO,
            esp_despues=2)
    if nota:
        parrafo(tf, nota, tam=10.5, color="texto_medio", esp_despues=0)


def tabla(s, x, y, w, h, filas, anchos=None, tam=11.5, tam_cab=10):
    nf, nc = len(filas), len(filas[0])
    gt = s.shapes.add_table(nf, nc, Inches(x), Inches(y), Inches(w), Inches(h)).table
    if anchos:
        total = sum(anchos)
        for j, a in enumerate(anchos):
            gt.columns[j].width = Emu(int(Inches(w) * a / total))
    for i, fila in enumerate(filas):
        for j, valor in enumerate(fila):
            celda = gt.cell(i, j)
            celda.fill.solid()
            celda.fill.fore_color.rgb = rgb("superficie_alta" if i == 0 else "superficie")
            celda.margin_left = celda.margin_right = Inches(0.07)
            celda.margin_top = celda.margin_bottom = Inches(0.03)
            tf = celda.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run()
            r.text = str(valor)
            r.font.size = Pt(tam_cab if i == 0 else tam)
            r.font.name = MONO if (i > 0 and j > 0) else FUENTE
            r.font.bold = i == 0
            r.font.color.rgb = rgb("texto_tenue" if i == 0 else "texto")
    return gt


def imagen(s, ruta, x, y, w=None, h=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    return s.shapes.add_picture(str(ruta), Inches(x), Inches(y), **kw)


def notas(s, texto):
    s.notes_slide.notes_text_frame.text = texto


def pie_fuente(s, texto, y=7.08):
    tf = caja(s, 0.55, y, 12.2, 0.35)
    parrafo(tf, "Fuente: " + texto, tam=9.5, color="texto_tenue", primero=True,
            esp_despues=0)


def n(x):
    """1234.5 -> '1.234' (formato español, como la app)."""
    return f"{x:,.0f}".replace(",", ".")


def d(x, dec=2):
    return f"{x:.{dec}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Lámina 1 — Carátula
# ---------------------------------------------------------------------------
s = lamina()
if (LOGOS / "inei_microdatos_cabecera.jpg").exists():
    pic = imagen(s, LOGOS / "inei_microdatos_cabecera.jpg", 0.55, 0.5, w=4.6)
if (LOGOS / "enei_logo.png").exists():
    imagen(s, LOGOS / "enei_logo.png", 11.05, 0.35, w=1.75)
tf = caja(s, 0.55, 2.05, 12.2, 2.2)
parrafo(tf, "Ingreso laboral e informalidad en el Perú", tam=40, negrita=True,
        primero=True, esp_despues=2)
parrafo(tf, "Dos modelos de machine learning sobre los microdatos de la "
        "ENAHO 2025 (INEI), desplegados en Streamlit", tam=19,
        color="texto_medio")
tf = caja(s, 0.55, 4.15, 12.2, 1.05)
parrafo(tf, "Curso de Machine Learning · ENEI — Escuela Nacional de "
        "Estadística e Informática", tam=15, color="texto", primero=True,
        esp_despues=2)
parrafo(tf, "Docente: Orlando Advíncula Zeballos · Agosto de 2026", tam=15,
        color="texto_medio")
_, tf = panel(s, 0.55, 5.35, 12.2, 1.45, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "INTEGRANTES", tam=11, color="acento_alto", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, "Alan Nestor Cañazaca Mamani   ·   Magdalena Quico de la Cruz   ·   "
        "Yoichiro Palacios Tanaka   ·   Edgar Delgado Ortega", tam=16,
        negrita=True, esp_despues=0)
notas(s, "Buenos días. Somos el grupo de Alan, Magdalena, Yoichiro y Edgar. "
      "Vamos a presentar dos modelos entrenados sobre los microdatos públicos "
      "de la ENAHO 2025 del INEI: uno que estima el ingreso laboral mensual y "
      "otro que clasifica el empleo informal. Los dos están desplegados en una "
      "app pública de Streamlit que vamos a mostrar en vivo. Todo lo que van a "
      "ver sale de artefactos versionados: cada número de esta presentación se "
      "puede defender con un archivo del repositorio.")

# ---------------------------------------------------------------------------
# Lámina 2 — Proyecto 1 y Proyecto 2
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Dos proyectos, una misma base y una misma app")
_, tf = panel(s, 0.55, 1.55, 6.0, 2.6)
parrafo(tf, "PROYECTO 1 · REGRESIÓN", tam=11, color="acento", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, "Ingreso laboral mensual", tam=20, negrita=True, esp_despues=4)
parrafo(tf, "¿Cuánto gana al mes una persona con este perfil? Gradient "
        "Boosting sobre el logaritmo del ingreso monetario (E9, ganador de un "
        "torneo de 9 especificaciones).", tam=13.5, color="texto_medio",
        esp_despues=0)
_, tf = panel(s, 6.8, 1.55, 6.0, 2.6)
parrafo(tf, "PROYECTO 2 · CLASIFICACIÓN", tam=11, color="acento", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, "Empleo informal", tam=20, negrita=True, esp_despues=4)
parrafo(tf, "¿Qué probabilidad tiene este perfil de ser un empleo informal? "
        "Gradient Boosting con umbral operativo elegido por precisión, según "
        "la regla del INEI (RUC / pensión).", tam=13.5, color="texto_medio",
        esp_despues=0)
_, tf = panel(s, 0.55, 4.45, 12.25, 1.9, relleno="superficie_alta")
parrafo(tf, "LOS DOS ENLACES", tam=11, color="texto_tenue", fuente=MONO,
        primero=True, esp_despues=6)
parrafo(tf, "App desplegada:   https://enaho-ingresos-informalidad.streamlit.app",
        tam=16, fuente=MONO, color="acento", esp_despues=6)
parrafo(tf, "Código y metodología:   https://github.com/IchiSieben/enaho-ingresos-informalidad",
        tam=16, fuente=MONO, color="acento", esp_despues=0)
notas(s, "Los dos proyectos comparten base de datos, muestra y app. El primero "
      "es una regresión: estima el ingreso laboral mensual de un perfil. El "
      "segundo es un clasificador: estima la probabilidad de que ese empleo "
      "sea informal. Estos son los dos enlaces: la app desplegada en Streamlit "
      "Cloud y el repositorio de GitHub con todo el código, los reportes y la "
      "auditoría. Pueden abrirlos ahora mismo desde el celular.")

# ---------------------------------------------------------------------------
# Lámina 3 — Descripción de la base de datos (embudo)
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "La base: ENAHO 2025 del INEI, microdatos públicos")
tf = caja(s, 0.55, 1.35, 12.2, 0.75)
parrafo(tf, "Encuesta Nacional de Hogares (encuesta 1031), módulos 02 "
        "(miembros del hogar), 03 (educación) y 05 (empleo e ingresos), unidos "
        "por persona.", tam=14.5, color="texto_medio", primero=True)
pasos = [
    (f"{EMBUDO['crudo']}", "filas crudas del módulo 05 (empleo)", "superficie"),
    (f"{EMBUDO['ocupados']}", "ocupados (OCU500 = 1)", "superficie"),
    (f"{EMBUDO['modelado']}", "de 14+ años con ingreso > 0", "superficie"),
    (f"{EMBUDO['torneo']}", f"casos completos para el torneo "
     f"(−{EMBUDO['dropna']} por faltantes, 0,6 %)", "acento_fondo"),
]
x = 0.55
for cifra, texto, relleno in pasos:
    _, tf = panel(s, x, 2.55, 2.75, 1.75, relleno=relleno)
    parrafo(tf, cifra, tam=26, negrita=True, fuente=MONO, color="acento",
            primero=True, esp_despues=2)
    parrafo(tf, texto, tam=11.5, color="texto_medio", esp_despues=0)
    if x < 9.5:
        tfl = caja(s, x + 2.78, 3.15, 0.5, 0.5)
        parrafo(tfl, "→", tam=24, color="texto_tenue", primero=True)
    x += 3.2
_, tf = panel(s, 0.55, 4.75, 12.25, 1.65, relleno="superficie_alta")
parrafo(tf, "DOS DECISIONES DECLARADAS", tam=10.5, color="texto_tenue",
        fuente=MONO, primero=True, esp_despues=4)
parrafo(tf, f"· Los 6.500 trabajadores familiares no remunerados quedan fuera "
        f"(ingreso = 0): informales por definición, pero sin target de ingreso.",
        tam=13, color="texto", esp_despues=3)
parrafo(tf, f"· Split 80/20 con semilla fija: train {EMBUDO['train']} · "
        f"test {EMBUDO['test']}. El test no decide nada durante el modelado.",
        tam=13, color="texto", esp_despues=0)
pie_fuente(s, "INFORME_AUDITORIA.md §4 (embudo reconstruido reejecutando "
           "src/03_fase1_preparacion.py)")
notas(s, "La base son los microdatos públicos de la ENAHO 2025, que cualquiera "
      "puede descargar del portal del INEI. Usamos tres módulos: hogar, "
      "educación y empleo. Este es el embudo completo: de casi 85 mil filas "
      "del módulo de empleo pasamos a 57.716 ocupados, 47.899 con ingreso "
      "positivo, y 47.632 casos completos para el torneo. Cada filtro está "
      "documentado y el embudo se verificó en la auditoría reejecutando el "
      "script de preparación. El split 80/20 se hace una sola vez con semilla "
      "fija y el test no se toca hasta el final.")

# ---------------------------------------------------------------------------
# Lámina 4 — Variables del regresor
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "El regresor: qué entra y qué se predice")
num = [f for f in REG["features"] if f["tipo"] == "numerico"]
cat = [f for f in REG["features"] if f["tipo"] != "numerico"]
_, tf = panel(s, 0.55, 1.5, 5.95, 3.4)
parrafo(tf, f"NUMÉRICAS ({len(num)})", tam=11, color="acento", fuente=MONO,
        primero=True, esp_despues=5)
ETIQ = {"exper2": "Experiencia² (cuadrado de la anterior)"}
for f in num:
    parrafo(tf, f"· {ETIQ.get(f['nombre'], f['etiqueta'])}", tam=13.5,
            esp_despues=3)
_, tf = panel(s, 6.85, 1.5, 5.95, 3.4)
parrafo(tf, f"CATEGÓRICAS ({len(cat)})", tam=11, color="acento", fuente=MONO,
        primero=True, esp_despues=5)
for f in cat:
    parrafo(tf, f"· {f['etiqueta']} ({len(f.get('opciones', []))} opciones)",
            tam=13.5, esp_despues=3)
_, tf = panel(s, 0.55, 5.15, 12.25, 1.45, relleno="acento_fondo", borde="acento")
parrafo(tf, "TARGET", tam=10.5, color="acento_alto", fuente=MONO, primero=True,
        esp_despues=3)
parrafo(tf, "log(ingreso laboral mensual monetario) — el ingreso «suavizado» "
        "del INEI: imputado, deflactado y anualizado ÷ 12. Se entrena en "
        "logaritmo por la cola larga de los sueldos; al volver a soles se "
        f"aplica la corrección de smearing de Duan (× {d(REG['smearing_duan'], 3)}).",
        tam=13.5, esp_despues=0)
pie_fuente(s, "models/feature_schema.json (regresor.features, smearing_duan)")
notas(s, "El regresor usa once variables: cinco numéricas, como años de "
      "educación, edad y horas trabajadas, y seis categóricas, como la rama de "
      "actividad, el tamaño de empresa y la categoría ocupacional. El target "
      "es el logaritmo del ingreso mensual monetario. ¿Por qué logaritmo? "
      "Porque los sueldos tienen cola larga: pocos sueldos enormes dominarían "
      "el error. Y al volver de logaritmo a soles aplicamos la corrección de "
      "smearing de Duan, que compensa el sesgo de esa vuelta. El preprocesa"
      "miento distingue numéricas y categóricas en un pipeline de scikit-learn "
      "con one-hot encoding, tal como pide la guía.")

# ---------------------------------------------------------------------------
# Lámina 5 — Preprocesamiento: la autopsia del centinela
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Preprocesamiento: el 999999 que valía como sueldo")
suc, lim = AUTOPSIA["corrida_sucia"], AUTOPSIA["corrida_limpia"]
_, tf = panel(s, 0.55, 1.5, 5.95, 3.7, relleno="mala_fondo", borde="mala")
parrafo(tf, "ANTES · CON CENTINELA", tam=11, color="mala", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, f"R² = {d(suc['r2'], 3)}", tam=24, negrita=True, fuente=MONO,
        color="mala", esp_despues=4)
parrafo(tf, f"const {n(suc['coefs']['const'])} · urbano "
        f"{n(suc['coefs']['urbano'])} · universitaria "
        f"{n(suc['coefs']['universitaria'])}", tam=12.5, fuente=MONO,
        esp_despues=4)
parrafo(tf, "Vivir en zona urbana «resta» S/ 27 mil; la universidad «resta» "
        "S/ 10 mil. Económicamente imposible.", tam=12.5, color="texto_medio",
        esp_despues=0)
_, tf = panel(s, 6.85, 1.5, 5.95, 3.7, relleno="buena_fondo", borde="buena")
parrafo(tf, "DESPUÉS · SOLO LIMPIANDO EL CÓDIGO DE FALTANTE", tam=11,
        color="buena", fuente=MONO, primero=True, esp_despues=4)
parrafo(tf, f"R² = {d(lim['r2'], 3)}", tam=24, negrita=True, fuente=MONO,
        color="buena", esp_despues=4)
parrafo(tf, f"const {n(lim['coefs']['const'])} · urbano "
        f"+{n(lim['coefs']['urbano'])} · universitaria "
        f"+{n(lim['coefs']['universitaria'])}", tam=12.5, fuente=MONO,
        esp_despues=4)
parrafo(tf, f"Mismos datos, misma ecuación. Solo se convirtió el 999999 "
        f"({n(AUTOPSIA['n_centinelas'])} filas, {d(AUTOPSIA['pct_centinelas'])} %) "
        "en faltante.", tam=12.5, color="texto_medio", esp_despues=0)
_, tf = panel(s, 0.55, 5.45, 12.25, 1.15, relleno="superficie_alta")
parrafo(tf, "El 999999 es el código de «no sabe / no responde» del INEI, leído "
        "como un ingreso real. Se encontró revisando plausibilidad económica: "
        "el problema estaba en los datos de origen, no en el modelado.",
        tam=14, negrita=True, primero=True, esp_despues=0)
pie_fuente(s, "models/ui_artifacts.json (torneo.autopsia: corrida_sucia / "
           "corrida_limpia, n_centinelas)")
notas(s, "Antes de modelar hubo que hacer una autopsia. Una primera regresión "
      "del grupo daba coeficientes imposibles: vivir en zona urbana restaba 27 "
      "mil soles y tener universidad restaba 10 mil. Ese resultado no era un "
      "error de código: el INEI codifica «no sabe, no responde» como 999999, y "
      "leído como sueldo real destroza la regresión. Son solo 1.093 filas, el "
      "2,3 por ciento, pero el R² pasa de 0,023 a 0,248 con solo convertirlas "
      "en faltantes. La lección: revisar la plausibilidad económica de los "
      "coeficientes encuentra errores que ninguna métrica técnica avisa.")

# ---------------------------------------------------------------------------
# Lámina 6 — Modelado del regresor: el torneo E1–E9
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "El torneo: nueve especificaciones, mismas reglas")
tf = caja(s, 0.55, 1.3, 12.2, 0.62)
parrafo(tf, "Misma muestra, mismo split 80/20, mismos 5 pliegues, misma "
        "semilla y misma métrica (MAE de validación cruzada) para las nueve.",
        tam=14, color="texto_medio", primero=True)
CORTAS = {
    "E1": "Ingreso ~ educación (consigna, niveles)",
    "E2": "log(ingreso) ~ educación",
    "E3": "Mincer clásico: educ + exp + exp²",
    "E4": "Mincer extendido (+sexo, área, horas, rama)",
    "E5": "Réplica del baseline del curso (sin centinela)",
    "E6": "Depurada (+categoría, tamaño, dominio)",
    "E7": "Post-Lasso (OLS sobre lo que Lasso conserva)",
    "E8": "Random Forest (log target)",
    "E9": "Gradient Boosting (log target)",
}
filas = [["", "Especificación", "MAE CV (S/)"]]
for f in sorted(TAB_TORNEO, key=lambda r: r["ID"]):
    filas.append([f["ID"], CORTAS[f["ID"]], d(f["MAE_cv"], 1)])
tabla(s, 0.55, 2.1, 6.7, 4.4, filas, anchos=[1, 7, 2], tam=11.5)
imagen(s, F_MAE, 7.55, 2.1, w=5.3)
pie_fuente(s, "models/ui_artifacts.json (torneo.tabla) · figura generada de "
           "ese mismo artefacto")
notas(s, "En vez de entrenar un solo modelo, montamos un torneo de nueve "
      "especificaciones: desde la consigna original del curso hasta Gradient "
      "Boosting, pasando por la ecuación de Mincer y un post-Lasso. La regla "
      "es que todas compiten en el mismo terreno: misma muestra, mismo split, "
      "los mismos cinco pliegues de validación cruzada, la misma semilla y la "
      "misma métrica. Eso lo verificó después la auditoría. En la tabla se ve "
      "la historia completa: cada variable económica que se agrega mejora el "
      "error, y los dos modelos de árboles, E8 y E9, ganan por unos 75 soles "
      "de error al mejor modelo lineal.")

# ---------------------------------------------------------------------------
# Lámina 7 — Selección del modelo (métricas)
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Selección: gana E9, y se elige por CV, no por test")
e9 = next(f for f in TAB_TORNEO if f["ID"] == "E9")
e8 = next(f for f in TAB_TORNEO if f["ID"] == "E8")
tarjeta_cifra(s, 0.55, 1.5, 3.9, "E9 · Gradient Boosting",
              f"S/ {d(e9['MAE_cv'], 1)}", "MAE CV — el ganador desplegado",
              h=1.7)
tarjeta_cifra(s, 4.75, 1.5, 3.9, "E8 · Random Forest",
              f"S/ {d(e8['MAE_cv'], 1)}", "MAE CV — segundo, a 2 soles",
              color_cifra="texto_medio", h=1.7)
tarjeta_cifra(s, 8.95, 1.5, 3.85, "R² en soles (test)",
              d(e9["R2_test_soles"], 2), f"RMSE {n(e9['RMSE_test'])} · "
              f"smearing {d(e9['smearing_Duan'], 3)}",
              color_cifra="texto_medio", h=1.7)
_, tf = panel(s, 0.55, 3.5, 12.25, 1.5)
parrafo(tf, "POR QUÉ POR CV Y NO POR TEST", tam=10.5, color="texto_tenue",
        fuente=MONO, primero=True, esp_despues=4)
parrafo(tf, "El test se reserva para estimar el error del ganador, no para "
        "elegirlo: si el test votara, dejaría de ser una medida honesta del "
        "error futuro. La validación cruzada usa solo el train, cinco veces.",
        tam=13.5, esp_despues=0)
_, tf = panel(s, 0.55, 5.25, 12.25, 1.5, relleno="media_fondo", borde="media")
parrafo(tf, "LA REJILLA, AUDITADA", tam=10.5, color="media", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, f"Los 3 hiperparámetros óptimos de E9 estaban en el borde de la "
        f"rejilla. Se amplió y mejoró: S/ {REJILLA['vieja']} → "
        f"S/ {REJILLA['nueva']} (−{REJILLA['mejora_pct']} %, sistemática: 5/5 "
        f"pliegues, t = {REJILLA['t']}, p = {REJILLA['p']}). No se redesplegó: "
        "la mejora es real pero sustantivamente irrelevante.", tam=13.5,
        esp_despues=0)
pie_fuente(s, "models/ui_artifacts.json (torneo.tabla) · INFORME_AUDITORIA.md §6")
notas(s, "La guía pide explicar la selección del modelo con métricas, y aquí "
      "está: gana E9, Gradient Boosting, con 611 soles de error medio, sobre "
      "E8, Random Forest, con 613. Importante: se selecciona por validación "
      "cruzada y no por test, porque el test solo sirve para estimar el error "
      "del ganador; si votara, quedaría contaminado. Y un detalle que nos "
      "diferencia: auditamos la rejilla de hiperparámetros, encontramos los "
      "óptimos en el borde, la ampliamos, y la mejora resultó sistemática pero "
      "de solo el 0,6 por ciento — así que decidimos no redesplegar. Esa "
      "decisión también está documentada.")

# ---------------------------------------------------------------------------
# Lámina 8 — Importancia de features (regresor)
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Qué variables explican el ingreso estimado")
tf = caja(s, 0.55, 1.32, 12.2, 0.66)
imp = UA["regresor"]["importancia_permutacion"]
parrafo(tf, "Importancia por permutación, en soles: si barajamos esta "
        "variable, ¿cuántos soles más se equivoca el modelo? "
        f"({n(imp['n_filas'])} filas, {imp['n_repeticiones']} repeticiones).",
        tam=14, color="texto_medio", primero=True)
imagen(s, F_IMP, 0.9, 2.1, w=8.3)
_, tf = panel(s, 9.55, 2.3, 3.25, 3.5, relleno="superficie_alta")
parrafo(tf, "LECTURA", tam=10.5, color="texto_tenue", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, f"La categoría ocupacional y la educación dominan: barajarlas "
        f"cuesta ~S/ {n(imp['media'][0])} y ~S/ {n(imp['media'][1])} de error "
        "extra.", tam=12.5, esp_despues=4)
parrafo(tf, "Coincide con la lectura económica del modelo explicativo E6: "
        "educación, horas y segmento del empleo.", tam=12.5,
        color="texto_medio", esp_despues=0)
pie_fuente(s, "models/ui_artifacts.json (regresor.importancia_permutacion)")
notas(s, "¿Por qué el modelo estima lo que estima? Esta es la importancia por "
      "permutación medida en soles, que es la forma más honesta de leerla: si "
      "barajamos una variable y el error sube 139 soles, esa variable "
      "aportaba eso. Las dos que dominan son la categoría ocupacional — ser "
      "independiente, obrero, empleador — y los años de educación. Después "
      "vienen el tamaño de la empresa, las horas y la edad. Esto coincide con "
      "lo que el modelo explicativo lineal encuentra con coeficientes: no es "
      "una caja negra que inventa; ordena las mismas palancas que la economía "
      "laboral conoce.")

# ---------------------------------------------------------------------------
# Lámina 9 — Streamlit en acción (regresor)
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Streamlit en acción: el regresor")
imagen(s, FIGS / "cloud_reg_tarjetas.png", 0.55, 1.5, w=9.2)
_, tf = panel(s, 10.0, 1.6, 2.8, 4.5, relleno="superficie_alta")
parrafo(tf, "LA APP", tam=10.5, color="texto_tenue", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, "· Formulario en dos columnas dirigido por feature_schema.json",
        tam=11.5, esp_despues=3)
parrafo(tf, "· Tarjetas: ingreso típico, esperado (con smearing) y mediana "
        "del país", tam=11.5, esp_despues=3)
parrafo(tf, "· Dos capas: español llano arriba, detalle técnico en "
        "expanders", tam=11.5, esp_despues=3)
parrafo(tf, "· Tooltips, situadores de cohorte y 3 temas (claro / oscuro / "
        "terminal)", tam=11.5, esp_despues=0)
pie_fuente(s, "captura Playwright de la app desplegada (perfil por defecto, "
           "tema claro)")
notas(s, "Así se ve el regresor desplegado. A la izquierda el formulario, "
      "dirigido por el esquema de features: cada control sale del JSON, no "
      "está escrito a mano. A la derecha las tres tarjetas: el ingreso típico "
      "del perfil, el esperado con la corrección de smearing, y la mediana "
      "del país para comparar. La app tiene una capa educativa: el registro "
      "de arriba es español llano y el detalle técnico vive en expanders, con "
      "tooltips y hasta tres temas de color. Esta captura es de la app real "
      "en la nube, no de un mockup.")

# ---------------------------------------------------------------------------
# Lámina 10 — Verificación VS Code = Streamlit (regresor)
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Verificación: VS Code y Streamlit dicen lo mismo")
tf = caja(s, 0.55, 1.3, 12.2, 0.6)
parrafo(tf, "Mismo perfil (los defaults del formulario), mismo artefacto "
        "regresor_e9.joblib: consola local a la izquierda, app desplegada a "
        "la derecha.", tam=14, color="texto_medio", primero=True)
imagen(s, F_CONSOLA, 0.55, 2.05, w=6.1)
imagen(s, FIGS / "cloud_reg_tarjetas.png", 6.95, 2.05, w=5.85)
_, tf = panel(s, 6.95, 5.5, 5.85, 1.1, relleno="buena_fondo", borde="buena")
parrafo(tf, f"típico:   S/ {ING_TIPICO} = S/ {ING_TIPICO}", tam=13.5,
        negrita=True, fuente=MONO, color="buena", primero=True, esp_despues=1)
parrafo(tf, f"esperado: S/ {ING_ESPERADO} = S/ {ING_ESPERADO}", tam=13.5,
        negrita=True, fuente=MONO, color="buena", esp_despues=2)
parrafo(tf, "idénticos dígito a dígito", tam=11.5, color="buena",
        esp_despues=0)
pie_fuente(s, "docs/presentacion/verificacion_local.py (salida real de "
           "consola) · captura Playwright de la app en la nube")
notas(s, "La guía pide comprobar que los resultados desde VS Code coinciden "
      "con el modelo desplegado, y aquí está la prueba lado a lado. A la "
      "izquierda, la salida real de consola de un script que carga el mismo "
      "joblib del repositorio y predice con el perfil por defecto del "
      "formulario: 849 soles de ingreso típico, 1.189 de esperado. A la "
      "derecha, la app desplegada en Streamlit Cloud con ese mismo perfil: "
      "849 y 1.189. Idénticos dígito a dígito, porque es el mismo artefacto "
      "binario corriendo en los dos lados — GitHub garantiza que lo que está "
      "en la nube es lo que está en el repo.")

# ---------------------------------------------------------------------------
# Lámina 11 — Variables del clasificador + regla del target
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "El clasificador: mismas 11 variables, target con regla INEI")
_, tf = panel(s, 0.55, 1.5, 5.95, 2.5)
parrafo(tf, "LAS VARIABLES", tam=11, color="acento", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, "Las mismas 11 del regresor: 5 numéricas + 6 categóricas. Nada "
        "del lado del target entra como predictor.", tam=13, esp_despues=4)
parrafo(tf, "P511A (tipo de contrato) se excluyó a propósito: separa casi "
        "sola (AUC 0,846) y convierte el problema en trivial.", tam=13,
        color="texto_medio", esp_despues=0)
_, tf = panel(s, 6.85, 1.5, 5.95, 2.5, relleno="acento_fondo", borde="acento")
parrafo(tf, "TARGET · REGLA DERIVADA DEL INEI", tam=11, color="acento_alto",
        fuente=MONO, primero=True, esp_despues=4)
parrafo(tf, "· Independiente o empleador SIN RUC → informal", tam=13.5,
        esp_despues=3)
parrafo(tf, "· Dependiente SIN afiliación a pensión → informal", tam=13.5,
        esp_despues=3)
parrafo(tf, f"Prevalencia: {d(FS['clasificador']['prevalencia_train'] * 100, 1)} % "
        f"muestral · {d(FS['clasificador']['prevalencia_ponderada'] * 100, 1)} % "
        "ponderada", tam=12.5, color="texto_medio", fuente=MONO, esp_despues=0)
imagen(s, F_IMP_CLF, 0.9, 4.25, h=2.35)
tfl = caja(s, 7.6, 4.7, 5.2, 1.6)
parrafo(tfl, "La importancia del clasificador repite el patrón: categoría "
        "ocupacional y tamaño de empresa dominan — y eso obliga a la pregunta "
        "de la lámina 13.", tam=13, color="texto_medio", primero=True)
pie_fuente(s, "models/feature_schema.json (clasificador) · "
           "reports/figuras/03_importancia_clasificador.png")
notas(s, "El clasificador usa exactamente las mismas once variables que el "
      "regresor. Lo importante es el target: el empleo informal no viene "
      "etiquetado en la encuesta, se deriva con la regla del INEI. Un "
      "independiente o empleador sin RUC es informal; un dependiente al que "
      "no le aportan a pensión, también. Dos de cada tres empleos de la "
      "muestra son informales. Y una decisión declarada: excluimos el tipo de "
      "contrato como predictor porque separa casi solo y habría convertido el "
      "ejercicio en trivial. La importancia muestra que categoría y tamaño de "
      "empresa dominan — enseguida veremos por qué eso exige un examen extra.")

# ---------------------------------------------------------------------------
# Lámina 12 — Modelado y selección del clasificador
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Selección del clasificador: PR-AUC, no accuracy")
filas = [["Algoritmo", "PR-AUC CV", "PR-AUC test", "Brier"]]
for a in CLF_COMP:
    filas.append([a["algoritmo"], d(a["PRAUC_cv"], 4), d(a["PRAUC_test"], 4),
                  d(a["Brier_test"], 4)])
tabla(s, 0.55, 1.5, 7.0, 1.9, filas, anchos=[3.4, 2, 2, 1.8], tam=12.5)
_, tf = panel(s, 7.95, 1.5, 4.85, 1.9, relleno="superficie_alta")
parrafo(tf, "POR QUÉ PR-AUC", tam=10.5, color="texto_tenue", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, f"Con prevalencia {d(FS['clasificador']['prevalencia_train'], 3)}, "
        "un modelo que dice «todos informales» ya acierta 68 de 100. El "
        "PR-AUC mide lo que importa: precisión y cobertura de la clase "
        "informal.", tam=12, esp_despues=0)
_, tf = panel(s, 0.55, 3.75, 12.25, 2.6, relleno="acento_fondo", borde="acento")
parrafo(tf, "PUNTO OPERATIVO APROBADO", tam=11, color="acento_alto",
        fuente=MONO, primero=True, esp_despues=5)
parrafo(tf, f"Criterio: {PUNTO['criterio'].split('(')[0].strip()} → umbral "
        f"{d(PUNTO['umbral'], 4)}", tam=15, negrita=True, esp_despues=4)
parrafo(tf, PUNTO["frase_exposicion"], tam=14.5, esp_despues=4)
parrafo(tf, f"recall {d(PUNTO['recall_oof'], 3)} · elegido sobre "
        "probabilidades out-of-fold del train: el test no decide el umbral",
        tam=12.5, color="texto_medio", fuente=MONO, esp_despues=0)
pie_fuente(s, "models/ui_artifacts.json (clasificador.comparacion) · "
           "models/feature_schema.json (punto_operativo)")
notas(s, "Compiten tres algoritmos: Gradient Boosting, Random Forest y una "
      "regresión logística como referencia lineal. Gana GB con PR-AUC de "
      "0,9626 en validación cruzada. ¿Por qué PR-AUC y no accuracy? Porque "
      "con 68 por ciento de informales, decir «todos informales» ya acierta "
      "68 de cada 100: el accuracy engaña. Después de elegir el modelo, "
      "elegimos el punto operativo: exigimos precisión de al menos 0,90, lo "
      "que da un umbral de 0,605. En llano: de cada mil trabajadores "
      "señalados, 900 son efectivamente informales, frente a 678 si "
      "señaláramos al azar. Y el umbral se eligió con probabilidades "
      "out-of-fold del train, nunca con el test.")

# ---------------------------------------------------------------------------
# Lámina 13 — ¿Demasiado bueno?
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "¿0,96 es demasiado bueno? Cuatro exámenes")
abl = ABLACION
tarjeta_cifra(s, 0.55, 1.45, 2.95, "1 · Baseline honesto",
              d(FS["clasificador"]["prevalencia_train"], 3),
              "la prevalencia: el punto de partida real del PR-AUC",
              color_cifra="texto_medio", h=1.85)
tarjeta_cifra(s, 3.65, 1.45, 2.95, "2 · Ablación estructural",
              f"{d(float(abl[0]['PRAUC_cv']), 4)} → {d(float(abl[2]['PRAUC_cv']), 4)}",
              "sin tamaño ni categoría (cuasi-definicionales) sigue alto",
              h=1.85)
tarjeta_cifra(s, 6.75, 1.45, 2.95, "3 · Calibración",
              d(next(a for a in CLF_COMP if a["algoritmo"] == "Gradient Boosting")["Brier_test"], 4),
              "Brier en test: las probabilidades se parecen a las tasas "
              "reales", color_cifra="texto_medio", h=1.85)
tarjeta_cifra(s, 9.85, 1.45, 2.95, "4 · Contraste externo",
              f"{EXTERNA['propia']} % vs {EXTERNA['inei']} %",
              "tasa reconstruida vs oficial INEI 2025",
              color_cifra="texto_medio", h=1.85)
imagen(s, F_PR_CAL, 0.9, 3.6, h=2.85)
_, tf = panel(s, 7.8, 3.75, 5.0, 2.55, relleno="media_fondo", borde="media")
parrafo(tf, "EL GRADIENTE, BIEN ETIQUETADO", tam=10.5, color="media",
        fuente=MONO, primero=True, esp_despues=4)
parrafo(tf, f"El {EXTERNA['gradiente_1_10']} % de informalidad que publica el "
        "INEI es del tramo de empresas de 1–10 trabajadores — no de la "
        "categoría propia «Hasta 20» (81,1 %). La auditoría corrigió esa "
        "etiqueta en todo el repositorio.", tam=12.5, esp_despues=4)
parrafo(tf, "El patrón por tamaño de empresa del modelo replica el oficial, "
        "comparando tramos comparables.", tam=12.5, color="texto_medio",
        esp_despues=0)
pie_fuente(s, "reports/ablacion_clasificador.csv · INFORME_AUDITORIA.md §5 y "
           "AC-5 · reports/figuras/03_pr_calibracion.png")
notas(s, "Un PR-AUC de 0,96 obliga a sospechar, así que lo sometimos a cuatro "
      "exámenes. Uno: el baseline honesto no es 0,5 sino la prevalencia, "
      "0,68. Dos: quitamos las dos variables casi definicionales — tamaño de "
      "empresa y categoría — y el PR-AUC solo cae a 0,94: el modelo no vive "
      "de un atajo. Tres: la calibración es buena, las probabilidades que da "
      "se parecen a las tasas reales. Y cuatro: la regla del target, "
      "reconstruida sobre todos los ocupados, da 67,3 por ciento de "
      "informalidad contra el 70,2 oficial del INEI — 2,9 puntos explicables "
      "por los familiares no remunerados. Además, en la auditoría corregimos "
      "una etiqueta: el famoso 88,6 por ciento del INEI es del tramo de 1 a "
      "10 trabajadores, no de nuestra categoría «hasta 20».")

# ---------------------------------------------------------------------------
# Lámina 14 — Streamlit + verificación (clasificador)
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "El clasificador en la app — y su verificación")
# La captura de la matriz incluye toda la página; se recorta al panel de la
# matriz (mismos píxeles de la captura real, solo encuadre).
from PIL import Image as _Img
_rec = FIGS / "cloud_clf_matriz_recorte.png"
_Img.open(FIGS / "cloud_clf_matriz.png").crop((1400, 100, 2620, 1240)).save(_rec)
imagen(s, FIGS / "cloud_clf_resultado.png", 0.55, 1.45, w=6.2)
imagen(s, _rec, 6.95, 1.45, h=3.49)
_, tf = panel(s, 0.55, 5.15, 6.0, 1.78, relleno="superficie_alta")
parrafo(tf, "EN LA APP", tam=10.5, color="texto_tenue", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, "· Umbral vivo: señalados, aciertos y escapes al moverlo", tam=12,
        esp_despues=2)
parrafo(tf, "· Matriz de confusión «por cada 1.000 evaluados»", tam=12,
        esp_despues=2)
parrafo(tf, "· Dependencia parcial: qué empuja la probabilidad", tam=12,
        esp_despues=0)
_, tf = panel(s, 6.75, 5.15, 6.05, 1.78, relleno="buena_fondo", borde="buena")
parrafo(tf, "VS CODE = STREAMLIT", tam=10.5, color="buena", fuente=MONO,
        primero=True, esp_despues=4)
parrafo(tf, f"consola local: {PROBA.replace('%', ' %')} · app desplegada: "
        f"{PROBA.replace('%', ' %')}", tam=13.5, negrita=True, fuente=MONO,
        color="buena", esp_despues=2)
parrafo(tf, "mismo clasificador_gb.joblib y perfil por defecto en los dos "
        "lados", tam=11, color="texto_medio", esp_despues=0)
pie_fuente(s, "capturas Playwright de la app desplegada · "
           "docs/presentacion/verificacion_local.py")
notas(s, "Así se ve el clasificador en la app. A la izquierda, la estimación "
      "para el perfil por defecto: 97,5 por ciento de probabilidad de "
      "informalidad, señalado para focalización, con el umbral vivo que el "
      "usuario puede mover. A la derecha, la matriz de confusión traducida a "
      "«por cada mil evaluados»: 606 informales bien señalados, 67 falsas "
      "alarmas, 72 que se escapan y 255 formales correctos. Y la misma "
      "verificación que en el regresor: la consola local con el mismo joblib "
      "da exactamente 97,5 por ciento, idéntico a la app desplegada.")

# ---------------------------------------------------------------------------
# Lámina 15 — Qué encontró la auditoría
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Qué encontró la auditoría (y está publicado)")
hallazgos = [
    ("El centinela leído como ingreso",
     f"999999 = «no responde» tratado como sueldo real: "
     f"{n(AUTOPSIA['n_centinelas'])} filas que hundían el R² a "
     f"{d(AUTOPSIA['corrida_sucia']['r2'], 3)}."),
    ("Rejillas con óptimos en el borde",
     f"Los 3 hiperparámetros de E9 al límite de la rejilla; ampliada: "
     f"−{REJILLA['mejora_pct']} % de MAE, mejora real pero irrelevante — no "
     "se redesplegó."),
    ("La cifra 88,6 % mal etiquetada",
     f"El {EXTERNA['gradiente_1_10']} % del INEI es del tramo 1–10 "
     "trabajadores, no de «microempresas» en general: corregida en app, "
     "README y docs."),
    (f"Las {N_REFERENCIAS} referencias, verificadas una a una",
     "Dos citas no decían lo que se les atribuía (ningún R² en Lemieux 2006 "
     "ni en Heckman et al. 2006): se reemplazaron por las citables (Mincer "
     "1974, Card 1999)."),
]
y = 1.5
for i, (tit, cuerpo) in enumerate(hallazgos, 1):
    _, tf = panel(s, 0.55, y, 12.25, 1.18)
    parrafo(tf, f"{i} · {tit}", tam=14.5, negrita=True, primero=True,
            esp_despues=2)
    parrafo(tf, cuerpo, tam=12.5, color="texto_medio", esp_despues=0)
    y += 1.32
tf = caja(s, 0.55, y + 0.05, 12.2, 0.5)
parrafo(tf, "Informe completo en INFORME_AUDITORIA.md (raíz del repo) y en la "
        "sección «Qué encontró la auditoría» de la ficha técnica de la app.",
        tam=12.5, color="texto_medio", primero=True)
pie_fuente(s, "INFORME_AUDITORIA.md · app/referencias.py "
           f"({N_REFERENCIAS} referencias con DOI/URL verificadas)")
notas(s, "Esto es lo que creemos que diferencia al proyecto: lo auditamos "
      "como si fuera de otro, y publicamos lo que salió. Cuatro hallazgos "
      "principales. El centinela del INEI leído como ingreso, que ya vieron. "
      "Las rejillas de hiperparámetros con óptimos en el borde: se ampliaron "
      "y documentamos por qué no redesplegamos. Una cifra oficial mal "
      "etiquetada al resumirla — 88,6 es del tramo de 1 a 10 trabajadores. Y "
      "las quince referencias bibliográficas verificadas una a una contra el "
      "texto original: dos citas que circulaban no decían lo que se les "
      "atribuía y se reemplazaron. Todo está en el informe de auditoría del "
      "repositorio y en la propia app.")

# ---------------------------------------------------------------------------
# Lámina 16 — Conclusiones
# ---------------------------------------------------------------------------
s = lamina()
titulo(s, "Conclusiones: qué se puede afirmar y qué no")
_, tf = panel(s, 0.55, 1.45, 5.95, 3.1, relleno="buena_fondo", borde="buena")
parrafo(tf, "SÍ SIRVE PARA", tam=11, color="buena", fuente=MONO, primero=True,
        esp_despues=5)
parrafo(tf, "· Ordenar y comparar perfiles: E9 recorta el MAE de S/ "
        f"{d(next(f for f in TAB_TORNEO if f['ID'] == 'E1')['MAE_cv'], 0)} "
        f"(consigna) a S/ {d(e9['MAE_cv'], 0)}", tam=13, esp_despues=3)
parrafo(tf, "· Focalizar formalización: 900 aciertos por cada 1.000 "
        "señalados (lift 1,33×)", tam=13, esp_despues=3)
parrafo(tf, "· Leer brechas robustas: educación, urbano/rural, segmento del "
        "empleo — consistentes entre modelos", tam=13, esp_despues=0)
_, tf = panel(s, 6.85, 1.45, 5.95, 3.1, relleno="mala_fondo", borde="mala")
parrafo(tf, "NO SIRVE PARA", tam=11, color="mala", fuente=MONO, primero=True,
        esp_despues=5)
parrafo(tf, f"· Liquidar sueldos: se equivoca ~S/ {d(e9['MAE_cv'], 0)} por "
        "persona en promedio", tam=13, esp_despues=3)
parrafo(tf, "· Dar veredictos sobre personas: la señal apunta a una "
        "configuración de empleo", tam=13, esp_despues=3)
parrafo(tf, "· Afirmar causalidad: es asociación en una encuesta de corte "
        "transversal", tam=13, esp_despues=0)
_, tf = panel(s, 0.55, 4.85, 12.25, 1.75, relleno="superficie_alta")
parrafo(tf, "app: enaho-ingresos-informalidad.streamlit.app  ·  "
        "repo: github.com/IchiSieben/enaho-ingresos-informalidad", tam=12.5,
        fuente=MONO, color="acento", primero=True, esp_despues=5)
parrafo(tf, "Créditos (CRediT en AUTHORS.md): grupo — Alan Nestor Cañazaca "
        "Mamani, Magdalena Quico de la Cruz, Yoichiro Palacios Tanaka, Edgar "
        "Delgado Ortega. Software y análisis: Yoichi Palacios (IchiSieben). "
        "Datos: INEI — ENAHO 2025. Docente: Orlando Advíncula Zeballos.",
        tam=12, color="texto_medio", esp_despues=0)
pie_fuente(s, f"generado desde artefactos el {META['fecha_generacion']} "
           f"(ui_artifacts commit {META['commit'][:7]}) por "
           "docs/presentacion/generar_ppt.py")
notas(s, "Cerramos con lo que estos modelos son y no son. Sirven para "
      "ordenar perfiles y comparar escenarios, para focalizar esfuerzos de "
      "formalización con un lift medido, y para leer brechas que aparecen "
      "consistentemente: educación, urbano-rural, segmento del empleo. No "
      "sirven para liquidar el sueldo de nadie — el error medio es de unos "
      "611 soles —, no dan veredictos sobre personas y no prueban "
      "causalidad. Los límites están declarados en la propia app. Aquí "
      "quedan los enlaces y los créditos. Gracias — y las preguntas que "
      "quieran, la app está en línea para probarlas en vivo.")

# ---------------------------------------------------------------------------
# Guardar
# ---------------------------------------------------------------------------
SALIDA = AQUI / "ENAHO_exposicion.pptx"
prs.save(SALIDA)
print(f"OK: {SALIDA} ({len(prs.slides.slides if hasattr(prs.slides, 'slides') else prs.slides._sldIdLst)} láminas)")
