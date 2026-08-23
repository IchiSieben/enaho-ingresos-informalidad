# -*- coding: utf-8 -*-
# generar_ppt.py — la exposición, generada desde los artefactos
# ---------------------------------------------------------------------------
# Autor: Yoichi Palacios Tanaka (IchiSieben) — proyecto ENAHO 2025
# Licencia: Apache-2.0 (ver LICENSE)
# ---------------------------------------------------------------------------
"""
Genera docs/presentacion/ENAHO_exposicion.pptx: 16:9, 18 láminas, notas del
orador en todas. El curso es de DESPLIEGUE de machine learning, así que el
bloque C (láminas 9-14) es el protagonista y el estadístico se comprime.

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

Reglas tipográficas (las verifica verificar_ppt.py):
  - cuerpo a 18 pt mínimo, títulos a 36 pt, sans (Calibri) para prosa
  - la monoespaciada se reserva para cifras, nombres de archivo y código
  - excepciones declaradas y deliberadas: la etiqueta de las tarjetas (14 pt,
    versalita mono) y el pie de fuente (12 pt). Ninguna lleva prosa.

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


# Embudo de datos (INFORME §4, reconstruido reejecutando la Fase 1)
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

TAB_TORNEO = {f["ID"]: f for f in UA["torneo"]["tabla"]}
CLF_COMP = UA["clasificador"]["comparacion"]      # GB / RF / logística
REG, CLF = FS["regresor"], FS["clasificador"]
PUNTO = CLF["punto_operativo"]
META = UA["meta"]
CURVA = UA["clasificador"]["curva_umbral"]
BASE_PR = UA["clasificador"]["pr"]["baseline"]
IMP_REG = UA["regresor"]["importancia_permutacion"]

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
                     "la lámina 4 daría por buena una tabla que no lo es.")
N_NIVELES = sum(len(f["opciones"]) for f in CAT)

# Peso de lo versionado y de lo que se queda fuera — medido, no recordado.
import subprocess  # noqa: E402


def _git(*a) -> str:
    return subprocess.run(["git", *a], cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8").stdout.strip()


SALIDA_REL = "docs/presentacion/ENAHO_exposicion.pptx"
VERSIONADOS = [f for f in _git("ls-files").split("\n") if f]
REPO = {
    "n_archivos": len(VERSIONADOS),
    "n_commits": _git("rev-list", "--count", "HEAD"),
    "commit": _git("rev-parse", "--short", "HEAD"),
    # Sin contar la propia presentación: si se incluyera, la cifra que la
    # lámina 9 imprime cambiaría al guardarla y no habría forma de verificarla
    # (el archivo se mide antes de existir en su tamaño final).
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


def i_umbral(u: float) -> int:
    return min(range(len(CURVA["umbral"])),
               key=lambda k: abs(CURVA["umbral"][k] - u))


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


def fig_embudo():
    pasos = [
        ("Módulo 05 crudo\nempleo e ingresos", EMBUDO["crudo"], mpl("texto_tenue")),
        ("Ocupados\n(OCU500 = 1, 14 años o más)", EMBUDO["ocupados"], mpl("texto_medio")),
        ("Dataset de modelado\ncon ingreso > 0", EMBUDO["modelado"], mpl("acento")),
        ("Muestra del torneo\nE1–E9", EMBUDO["torneo"], mpl("acento_alto")),
    ]
    val = [int(v.replace(".", "")) for _, v, _ in pasos]
    fig, ax = plt.subplots(figsize=(11.2, 4.6))
    y = list(range(len(pasos)))[::-1]
    for k, ((et, _, col), v) in enumerate(zip(pasos, val)):
        ax.barh(y[k], v, height=0.62, color=col, alpha=0.85 if k > 1 else 0.45,
                edgecolor="none", zorder=3)
        ax.text(v + max(val) * 0.012, y[k], n(v), va="center", ha="left",
                fontsize=19, fontweight="bold", color=mpl("texto"), zorder=4)
        ax.text(-max(val) * 0.015, y[k], et, va="center", ha="right",
                fontsize=13.5, color=mpl("texto_medio"), linespacing=1.35)
        if k:
            ax.annotate(f"−{n(val[k - 1] - v)}", xy=(v * 0.5, y[k] + 0.5),
                        ha="center", va="center", fontsize=12,
                        color=mpl("mala"), fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.28",
                                  fc=mpl("mala_fondo"), ec="none"))
    ax.text(val[-1] * 0.5, -0.92,
            f"Train {EMBUDO['train']}   ·   Test {EMBUDO['test']}"
            f"   (partición estratificada, semilla fija)",
            ha="center", va="center", fontsize=13.5, color=mpl("texto"),
            bbox=dict(boxstyle="round,pad=0.45", fc=mpl("acento_fondo"), ec="none"))
    ax.set_xlim(0, max(val) * 1.13)
    ax.set_ylim(-1.5, len(pasos) - 0.35)
    ax.set_yticks([]); ax.set_xticks([])
    _limpiar(ax, ("top", "right", "bottom", "left"))
    return _guardar(fig, "fig_embudo")


def fig_arquitectura():
    fig, ax = plt.subplots(figsize=(12.8, 6.0))
    ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")

    def caja(x, y, w, h, titulo, lineas, fc, ec, tc=None):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.7",
                                    fc=fc, ec=ec, lw=1.8, zorder=3))
        ax.text(x + w / 2, y + h - 2.6, titulo, ha="center", va="top",
                fontsize=15, fontweight="bold", color=tc or mpl("texto"), zorder=4)
        ax.text(x + w / 2, y + h - 7.4, "\n".join(lineas), ha="center", va="top",
                fontsize=12, color=mpl("texto_medio"), linespacing=1.6, zorder=4)

    def flecha(x1, y1, x2, y2, texto=None, dx=0, dy=2.0, ha="center"):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                     mutation_scale=24, lw=2.4, color=mpl("acento"),
                                     zorder=5, shrinkA=0, shrinkB=0))
        if texto:
            ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, texto, ha=ha,
                    va="center", fontsize=12.5, color=mpl("acento_alto"),
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
    caja(62, 3, 24, 16, "4 · GitHub",
         ["IchiSieben /", "enaho-ingresos-informalidad", "rama main"],
         mpl("superficie"), mpl("borde"))
    caja(31.5, 3, 24, 16, "5 · Streamlit Cloud",
         ["app/streamlit_app.py", "redeploy automático", "en cada push"],
         mpl("superficie"), mpl("borde"))
    caja(1, 3, 24, 16, "6 · Navegador",
         ["enaho-ingresos-", "informalidad", ".streamlit.app"],
         mpl("buena_fondo"), mpl("buena"), tc=mpl("buena"))
    flecha(61.6, 11, 55.9, 11, "webhook")
    flecha(31.1, 11, 25.4, 11, "HTTPS")
    ax.add_patch(FancyBboxPatch((29.6, 26.4), 58, 22.2, boxstyle="round,pad=0.5",
                                fc="none", ec=mpl("acento"), lw=1.4,
                                ls=(0, (6, 4)), zorder=2))
    ax.text(58.8, 49.6,
            f"carpeta versionada · {d(REPO['mb'], 2)} MB · "
            f"{REPO['n_archivos']} archivos",
            ha="center", va="bottom", fontsize=13, color=mpl("acento_alto"),
            fontweight="bold")
    if DATOS_MB:
        ax.text(13, 24.3,
                f"NO viaja al repositorio:\n{d(DATOS_MB, 1)} MB de microdatos\n"
                f"se enlaza a la fuente del INEI",
                ha="center", va="center", fontsize=12, color=mpl("mala"),
                fontweight="bold", linespacing=1.45)
    return _guardar(fig, "fig_arquitectura")


def fig_reg_rf_gb():
    e8, e9, e7 = TAB_TORNEO["E8"], TAB_TORNEO["E9"], TAB_TORNEO["E7"]
    fig, ax = plt.subplots(figsize=(10.6, 5.2))
    vals = [e8["MAE_cv"], e9["MAE_cv"]]
    barras = ax.bar(["Random Forest\n(E8)", "Gradient Boosting\n(E9)"], vals,
                    width=0.46, color=[mpl("texto_tenue"), mpl("acento")], zorder=3)
    for b, v in zip(barras, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 14, f"S/ {d(v, 1)}",
                ha="center", fontsize=22, fontweight="bold", color=mpl("texto"))
    ax.axhline(e7["MAE_cv"], color=mpl("texto_tenue"), lw=1.3, ls=(0, (5, 4)),
               zorder=2)
    ax.text(1.52, e7["MAE_cv"], f"  mejor lineal (E7): S/ {d(e7['MAE_cv'], 1)}",
            va="center", ha="left", fontsize=12.5, color=mpl("texto_tenue"))
    dif = e8["MAE_cv"] - e9["MAE_cv"]
    ax.annotate(f"{d(dif, 1)} soles de diferencia\n"
                f"({d(dif / e8['MAE_cv'] * 100, 2)} % del error)",
                xy=(0.5, max(vals) * 0.55), ha="center", va="center",
                fontsize=14, color=mpl("texto"), linespacing=1.5,
                bbox=dict(boxstyle="round,pad=0.5", fc=mpl("superficie"),
                          ec=mpl("borde"), lw=1.2))
    ax.set_ylabel("Error absoluto medio en validación cruzada (soles/mes)",
                  fontsize=12.5)
    ax.set_ylim(0, max(vals) * 1.28); ax.set_xlim(-0.62, 1.5)
    ax.tick_params(axis="x", labelsize=15, length=0)
    ax.tick_params(axis="y", labelsize=11.5)
    ax.grid(axis="y", color="#E4E1D8", lw=0.9, zorder=0)
    _limpiar(ax)
    return _guardar(fig, "fig_reg_rf_gb")


def fig_clf_tres():
    fig, ax = plt.subplots(figsize=(10.8, 5.0))
    y = list(range(len(CLF_COMP)))[::-1]
    for k, f in enumerate(CLF_COMP):
        es_gb = "Gradient" in f["algoritmo"]
        ax.barh(y[k], f["PRAUC_cv"], height=0.5,
                color=mpl("acento") if es_gb else mpl("texto_tenue"),
                alpha=1 if es_gb else 0.5, zorder=3)
        ax.text(f["PRAUC_cv"] + 0.012, y[k], d(f["PRAUC_cv"], 4), va="center",
                fontsize=19, fontweight="bold", color=mpl("texto"))
        ax.text(-0.012, y[k], f["algoritmo"] + ("  ·  desplegado" if es_gb else ""),
                va="center", ha="right", fontsize=14,
                color=mpl("texto") if es_gb else mpl("texto_medio"),
                fontweight="bold" if es_gb else "normal")
    ax.axvline(BASE_PR, color=mpl("mala"), lw=1.6, ls=(0, (5, 4)), zorder=4)
    ax.text(BASE_PR, -0.85, f"  azar = prevalencia {d(BASE_PR, 4)}", ha="left",
            va="center", fontsize=12.5, color=mpl("mala"), fontweight="bold")
    ax.set_xlim(0, 1.14); ax.set_ylim(-1.3, len(CLF_COMP) - 0.4)
    ax.set_yticks([])
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", "0,25", "0,50", "0,75", "1"], fontsize=11.5)
    ax.set_xlabel("PR-AUC en validación cruzada (5 pliegues)", fontsize=12.5)
    ax.grid(axis="x", color="#E4E1D8", lw=0.9, zorder=0)
    _limpiar(ax, ("top", "right", "left"))
    return _guardar(fig, "fig_clf_tres")


def fig_umbral():
    N = CURVA["n"]
    señal = [(tp + fp) / N * 100 for tp, fp in zip(CURVA["tp"], CURVA["fp"])]
    prec = [x * 100 for x in CURVA["precision_1"]]
    fig, ax = plt.subplots(figsize=(11.0, 5.2))
    ax.plot(señal, prec, color=mpl("acento"), lw=2.6, zorder=3)
    i_op, i_05 = i_umbral(PUNTO["umbral"]), i_umbral(0.5)
    # Las etiquetas van a zonas vacías del plano —arriba a la derecha, abajo a
    # la izquierda— para que ni el texto ni la guía crucen la curva.
    for k, etq, col, dest, ha in (
            (i_op, f"punto operativo elegido\numbral {d(PUNTO['umbral'], 4)} · "
             f"precisión {d(prec[i_op], 0)} %", mpl("acento_alto"), (79, 97), "left"),
            (i_05, f"umbral 0,500\nprecisión {d(prec[i_05], 0)} %",
             mpl("texto_tenue"), (40, 77), "right")):
        ax.plot(señal[k], prec[k], "o", ms=13, mfc=mpl("fondo"), mec=col, mew=3,
                zorder=5)
        ax.annotate(etq, xy=(señal[k], prec[k]), xytext=dest, fontsize=13,
                    color=col, fontweight="bold", linespacing=1.4, ha=ha,
                    va="center", zorder=6,
                    arrowprops=dict(arrowstyle="-", color=col, lw=1.4, shrinkB=6))
    ax.axhline(BASE_PR * 100, color=mpl("mala"), lw=1.6, ls=(0, (5, 4)), zorder=2)
    ax.text(99, BASE_PR * 100 - 1.4,
            f"señalar a TODOS: precisión {d(BASE_PR * 100, 0)} % — la prevalencia",
            ha="right", va="top", fontsize=12.5, color=mpl("mala"), fontweight="bold")
    ax.set_xlabel("% de trabajadores señalados  (cobertura)", fontsize=13)
    ax.set_ylabel("Precisión de la clase informal (%)", fontsize=13)
    ax.set_xlim(0, 100); ax.set_ylim(60, 102)
    ax.tick_params(labelsize=11.5)
    ax.grid(color="#E4E1D8", lw=0.9, zorder=0)
    _limpiar(ax)
    return _guardar(fig, "fig_umbral")


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


def fig_precomputo():
    fig, ax = plt.subplots(figsize=(12.2, 5.0))
    ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")

    def bloque(x, w, titulo, subt, items, fc, ec, tc):
        ax.add_patch(FancyBboxPatch((x, 4), w, 32, boxstyle="round,pad=0.6",
                                    fc=fc, ec=ec, lw=1.6, zorder=3))
        ax.text(x + w / 2, 33.6, titulo, ha="center", va="top", fontsize=14.5,
                fontweight="bold", color=tc, zorder=4)
        ax.text(x + w / 2, 29.8, subt, ha="center", va="top", fontsize=11.5,
                color=mpl("texto_medio"), zorder=4)
        for k, it in enumerate(items):
            ax.text(x + 2.6, 25.4 - k * 3.5, "·  " + it, ha="left", va="top",
                    fontsize=11.8, color=mpl("texto"), zorder=4)

    n_umbral = len(CURVA["umbral"])
    n_bins = len(UA["clasificador"]["histograma_oof"]["clase_1"])
    n_pdp = len(UA["clasificador"]["dependencia_parcial"])
    bloque(1, 46, "UNA VEZ, en tu máquina", "src/09_precomputar_ui.py",
           [f"curva umbral → consecuencias ({n_umbral} puntos)",
            f"histograma OOF de probabilidades ({n_bins} bins)",
            f"dependencia parcial de las {n_pdp} variables",
            "cohortes y percentiles comparables",
            "tasas observadas por grupo"],
           mpl("acento_fondo"), mpl("acento"), mpl("acento_alto"))
    bloque(53, 46, "EN CALIENTE, al pulsar el botón", "app/streamlit_app.py",
           ["una llamada a .predict() del regresor",
            "una llamada a .predict_proba()",
            "del clasificador",
            "el resto: leer el JSON y dibujar SVG"],
           mpl("buena_fondo"), mpl("buena"), mpl("buena"))
    ax.annotate("", xy=(52.4, 20), xytext=(47.6, 20),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=22, lw=2.2,
                                color=mpl("texto_tenue")))
    ax.text(24, 1.6, f"ui_artifacts.json · {d(UI_KB, 1)} KB", ha="center",
            va="center", fontsize=12.5, fontweight="bold", color=mpl("acento_alto"))
    ax.text(76, 1.6, f"2 modelos .joblib · {n(JOBLIB_KB)} KB", ha="center",
            va="center", fontsize=12.5, fontweight="bold", color=mpl("buena"))
    return _guardar(fig, "fig_precomputo")


def fig_consola(bloque: str, nombre: str):
    """
    La salida REAL de verificacion_local.py, pintada como una terminal.

    Se parte en dos figuras —una por modelo— porque cada una es la mitad
    izquierda de su lámina de verificación y ahí solo cabe una idea.
    """
    lineas = [l.rstrip() for l in CONSOLA.strip().split("\n")]
    corte = next(k for k, l in enumerate(lineas) if l.startswith("[REGRESOR"))
    cabecera, resto = lineas[:corte], lineas[corte:]
    inicio = next(k for k, l in enumerate(resto) if l.startswith(f"[{bloque}"))
    fin = next((k for k, l in enumerate(resto[inicio + 1:], inicio + 1)
                if l.startswith("[")), len(resto))
    lineas = cabecera + resto[inicio:fin]
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


F_REQ = fig_requisitos()
F_CONSOLA_REG = fig_consola("REGRESOR", "fig_consola_regresor")
F_CONSOLA_CLF = fig_consola("CLASIFICADOR", "fig_consola_clasificador")
F_EMBUDO = fig_embudo()
F_ARQ = fig_arquitectura()
F_RF_GB = fig_reg_rf_gb()
F_CLF = fig_clf_tres()
F_UMBRAL = fig_umbral()
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


def lamina(fondo="fondo"):
    s = prs.slides.add_slide(BLANCO)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = rgb(fondo)
    return s


def caja(s, x, y, w, h):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf


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
Y_CINTA, Y_TITULO, Y_ENTRADILLA, Y_CUERPO, Y_PIE = 0.16, 0.42, 1.54, 2.26, 7.02
ALTO_CUERPO = Y_PIE - Y_CUERPO - 0.16


def titulo(s, texto, entradilla=""):
    """Título de lámina (1-2 líneas a 36 pt) más una línea llana debajo."""
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
    es una caja con aire, y de esas la presentación anterior estaba llena.
    """
    _, tf = panel(s, x, y, w, h, relleno=relleno)
    parrafo(tf, etiqueta.upper(), tam=T_ETIQUETA, color="texto_tenue",
            fuente=MONO, primero=True, esp_despues=4)
    parrafo(tf, cifra, tam=tam_cifra, color=color_cifra, negrita=True,
            fuente=MONO, esp_despues=6, esp_linea=0.95)
    parrafo(tf, nota, tam=T_CUERPO, color="texto_medio", esp_despues=0,
            esp_linea=1.05)


def vinetas(s, x, y, w, h, items, tam=T_CUERPO, marca="—"):
    tf = caja(s, x, y, w, h)
    for k, it in enumerate(items):
        parrafo(tf, f"{marca}  {it}", tam=tam, color="texto", primero=(k == 0),
                esp_despues=12, esp_linea=1.08)
    return tf


def tabla(s, x, y, w, h, filas, anchos=None, tam=T_TABLA, tam_cab=T_TABLA_CAB,
          resaltar=None, cols_mono=None):
    """
    `cols_mono` son las columnas de cifra: monoespaciada y alineadas a la
    derecha. Las demás son prosa, en sans y a la izquierda. Un umbral único
    ponía en mono una columna entera de texto corrido.
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
            if i == 0:
                celda.fill.fore_color.rgb = rgb("superficie_alta")
            elif resaltar is not None and i == resaltar:
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
            r.font.bold = (i == 0) or (resaltar is not None and i == resaltar)
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


def conector(s, x1, y1, x2, y2, color="acento"):
    ln = s.shapes.add_connector(1, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = rgb(color)
    ln.line.width = Pt(1.5)
    return ln


def notas(s, texto):
    s.notes_slide.notes_text_frame.text = texto


def pie_fuente(s, texto, y=None):
    y = Y_PIE if y is None else y
    tf = caja(s, MARGEN, y, UTIL, 0.34)
    parrafo(tf, "Fuente: " + texto, tam=T_PIE, color="texto_tenue",
            primero=True, esp_despues=0)


def cinta(s, texto, y=None):
    """Marca de bloque en la esquina superior: dice dónde estamos."""
    y = Y_CINTA if y is None else y
    tf = caja(s, MARGEN, y, UTIL, 0.26)
    parrafo(tf, texto.upper(), tam=T_ETIQUETA, color="texto_tenue", fuente=MONO,
            primero=True, esp_despues=0)


# ---------------------------------------------------------------------------
# BLOQUE A — Qué construimos
# ---------------------------------------------------------------------------
APP_URL = "enaho-ingresos-informalidad.streamlit.app"
REPO_URL = "github.com/IchiSieben/enaho-ingresos-informalidad"

# --- Lámina 1: carátula --------------------------------------------------
s = lamina()
if (LOGOS / "inei_microdatos_cabecera.jpg").exists():
    imagen(s, LOGOS / "inei_microdatos_cabecera.jpg", MARGEN, 0.46, w=4.4)
if (LOGOS / "enei_logo.png").exists():
    imagen(s, LOGOS / "enei_logo.png", 11.05, 0.34, w=1.68)

tf = caja(s, MARGEN, 2.10, 12.09, 1.9)
parrafo(tf, "Ingreso laboral e informalidad en el Perú", tam=44, negrita=True,
        primero=True, esp_despues=6, esp_linea=0.94)
parrafo(tf, "Dos modelos sobre los microdatos de la ENAHO 2025 (INEI), "
            "desplegados en una app pública", tam=T_ENTRADILLA,
        color="texto_medio", esp_despues=0, esp_linea=1.05)

tf = caja(s, MARGEN, 4.02, 12.09, 0.9)
parrafo(tf, "Curso de Machine Learning · ENEI — Escuela Nacional de "
            "Estadística e Informática", tam=T_CUERPO, primero=True,
        esp_despues=4)
parrafo(tf, "Docente: Orlando Advíncula Zeballos · Agosto de 2026",
        tam=T_CUERPO, color="texto_medio", esp_despues=0)

_, tf = panel(s, MARGEN, 5.02, 12.09, 1.34, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "INTEGRANTES", tam=T_ETIQUETA, color="acento_alto", fuente=MONO,
        primero=True, esp_despues=6)
parrafo(tf, "Alan Nestor Cañazaca Mamani   ·   Magdalena Quico de la Cruz",
        tam=T_CUERPO, negrita=True, esp_despues=3)
parrafo(tf, "Yoichi Palacios Tanaka   ·   Edgar Delgado Ortega",
        tam=T_CUERPO, negrita=True, esp_despues=0)

_, tf = panel(s, MARGEN, 6.52, 12.09, 0.76)
parrafo(tf, f"App:  {APP_URL}        Repositorio:  {REPO_URL}",
        tam=T_CUERPO, color="acento_alto", fuente=MONO, primero=True,
        esp_despues=0)
notas(s, "Buenas. Somos el grupo de Alan, Magdalena, Yoichi y Edgar, del curso "
         "de Machine Learning de la ENEI, con el profesor Orlando Advíncula. "
         "Presentamos dos modelos entrenados sobre los microdatos públicos de "
         "la ENAHO 2025 del INEI: uno estima el ingreso laboral mensual y otro "
         "clasifica si un empleo es informal. Los dos están desplegados en una "
         "app pública de Streamlit que vamos a abrir en vivo. El curso es de "
         "despliegue, así que el peso de la exposición está en cómo llega el "
         "modelo del editor al navegador, no en la estadística. Esos dos "
         "enlaces de abajo son los únicos que hace falta apuntar.")

# --- Lámina 2: los dos proyectos ----------------------------------------
s = lamina()
cinta(s, "Bloque A · qué construimos    ·    lámina 2 de 18")
y = titulo(s, "Una app, dos modelos: cuánto gana una persona y si su empleo "
              "es informal",
           "El mismo formulario alimenta dos modelos distintos; cada pestaña "
           "corre el suyo.")
ANCHO_CAP = 5.86
# Recortadas: con la barra lateral dentro, el contenido no se lee proyectado.
imagen_encajada(s, recorte_lateral("cloud_reg_form.png", "cloud_reg_panel.png"),
                MARGEN, y, ANCHO_CAP, 3.02)
imagen_encajada(s, recorte_lateral("cloud_clf_resultado.png",
                                   "cloud_clf_panel.png"),
                6.85, y, ANCHO_CAP, 3.02)
for x, etq, txt in (
        (MARGEN, "Estimación de ingreso  ·  regresión",
         "Estima el ingreso laboral mensual en soles con Gradient Boosting "
         "sobre el logaritmo del ingreso (especificación E9)."),
        (6.85, "Empleo informal  ·  clasificación",
         "Estima la probabilidad de que el empleo sea informal, también con "
         "Gradient Boosting, sobre las mismas once variables.")):
    _, tf = panel(s, x, y + 3.14, ANCHO_CAP, 1.48)
    parrafo(tf, etq.upper(), tam=T_ETIQUETA, color="texto_tenue", fuente=MONO,
            primero=True, esp_despues=6)
    parrafo(tf, txt, tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.06)
pie_fuente(s, f"capturas de la app desplegada en Streamlit Community Cloud "
              f"({APP_URL}).")
notas(s, "La app tiene cuatro secciones; estas son las dos que hacen "
         "predicción. A la izquierda, el formulario del regresor: se describe "
         "un perfil laboral y devuelve un ingreso mensual típico en soles. A "
         "la derecha, la pestaña de informalidad: con las mismas once "
         "variables devuelve una probabilidad y, según dónde se ponga el "
         "umbral, un veredicto. Son dos modelos independientes que comparten "
         "las entradas, no un modelo con dos salidas. Las otras dos secciones "
         "son el torneo de modelos y la ficha técnica, y las vemos al final.")

# --- Lámina 3: el embudo de datos ---------------------------------------
s = lamina()
cinta(s, "Bloque A · qué construimos    ·    lámina 3 de 18")
y = titulo(s, f"De {EMBUDO['crudo']} registros del INEI quedan "
              f"{EMBUDO['torneo']} personas comparables",
           "Tres filtros documentados, no un recorte a conveniencia.")
imagen_encajada(s, F_EMBUDO, MARGEN, y, 12.09, 3.45)
_, tf = panel(s, MARGEN, y + 3.57, 12.09, 0.95)
parrafo(tf, f"ENAHO 2025 (INEI), módulos 02 (miembros del hogar) · 03 "
            f"(educación) · 05 (empleo e ingresos). Cada corte está en "
            f"src/03_fase1_preparacion.py y en el informe de auditoría.",
        tam=T_CUERPO, color="texto", primero=True, esp_despues=0, esp_linea=1.06)
pie_fuente(s, "INFORME_AUDITORIA.md §4 (embudo reconstruido reejecutando la "
              "Fase 1) · src/03_fase1_preparacion.py")
notas(s, f"Antes de entrenar nada había que decidir qué filas entraban. "
         f"Partimos del módulo de empleo e ingresos: {EMBUDO['crudo']} "
         f"registros, de los que {EMBUDO['ocupados']} son personas ocupadas de "
         f"14 años o más. Exigir un ingreso laboral mayor que cero deja "
         f"{EMBUDO['modelado']}: ahí quedan fuera, por ejemplo, los "
         f"trabajadores familiares no remunerados, que declaran ingreso cero "
         f"por definición. El último corte quita las filas sin alguna variable "
         f"del modelo y deja {EMBUDO['torneo']}. De ahí salen "
         f"{EMBUDO['train']} de entrenamiento y {EMBUDO['test']} de prueba, "
         f"con semilla fija. Ninguno de estos números está escrito a mano en "
         f"la diapositiva: se leen del informe al generarla.")

# ---------------------------------------------------------------------------
# BLOQUE B — Los modelos, con los dos algoritmos a la vista
# ---------------------------------------------------------------------------
# --- Lámina 4: las variables [GUÍA] --------------------------------------
s = lamina()
cinta(s, "Bloque B · los modelos    ·    lámina 4 de 18    ·    exigida por la guía")
y = titulo(s, f"Once variables: {len(NUM)} numéricas y {len(CAT)} categóricas, "
              f"las mismas en los dos modelos",
           "El regresor de ingreso y el clasificador de informalidad parten "
           "del mismo conjunto de entradas.")
# Las del schema son etiquetas de formulario: en una celda no caben enteras.
ETIQUETAS_CORTAS = {"exper2": "Experiencia² (cuadrado)",
                    "horas_total": "Horas trabajadas por semana",
                    "exper": "Experiencia potencial (años)"}
PERFIL = dict(re.findall(r"^\s{2}(\w+)\s+= (.+)$", CONSOLA, re.M))
filas_num = [["Numérica (5)", "Rango", "Perfil de ejemplo"]]
for f in NUM:
    filas_num.append([ETIQUETAS_CORTAS.get(f["nombre"], f["etiqueta"]),
                      f"{d(f['min'], 0)} – {d(f['max'], 0)}",
                      PERFIL.get(f["nombre"], "")])
filas_cat = [["Categórica (6)", "Niveles", "Perfil de ejemplo"]]
for f in CAT:
    filas_cat.append([f["etiqueta"], str(len(f["opciones"])),
                      PERFIL.get(f["nombre"], "")])
tabla(s, MARGEN, y, 5.86, 2.45, filas_num, anchos=[46, 24, 30], tam=16,
      tam_cab=16)
tabla(s, 6.85, y, 5.86, 2.85, filas_cat, anchos=[46, 20, 34], tam=16,
      tam_cab=16)
_, tf = panel(s, MARGEN, 5.64, 12.09, 1.20, relleno="acento_fondo",
              borde="acento")
parrafo(tf, f"Las {len(CAT)} categóricas aportan {N_NIVELES} niveles, que el "
            f"pipeline convierte en columnas indicadoras (one-hot) dentro del "
            f"propio modelo. Las {len(NUM)} numéricas entran tal cual: "
            f"experiencia² es la única derivada, y la calcula la app, no el "
            f"usuario.",
        tam=T_CUERPO, color="texto", primero=True, esp_despues=0, esp_linea=1.06)
pie_fuente(s, "models/feature_schema.json (features, tipo, rango y opciones) · "
              "docs/presentacion/salida_consola_verificacion.txt (perfil)")
notas(s, f"La guía pide distinguir explícitamente las variables numéricas de "
         f"las categóricas, así que aquí están las once. Cinco numéricas: años "
         f"de educación, edad, experiencia potencial, su cuadrado y horas "
         f"trabajadas por semana. Seis categóricas: sexo, área, dominio "
         f"geográfico, rama de actividad, tamaño de empresa y categoría "
         f"ocupacional. Entre las seis suman {N_NIVELES} niveles, que el "
         f"pipeline codifica en one-hot dentro del propio modelo: eso importa "
         f"para el despliegue, porque significa que la app manda un "
         f"diccionario con los valores en bruto y no tiene que replicar la "
         f"codificación. La columna de la derecha es el perfil por defecto del "
         f"formulario, el mismo con el que verificamos al final.")

# --- Lámina 5: regresión, RF vs GB [GUÍA] --------------------------------
s = lamina()
cinta(s, "Bloque B · los modelos    ·    lámina 5 de 18    ·    exigida por la guía")
e8, e9 = TAB_TORNEO["E8"], TAB_TORNEO["E9"]
y = titulo(s, "Random Forest y Gradient Boosting empatan en el error del "
              "regresor",
           "Los dos algoritmos de ensamble del curso, sobre los mismos datos, "
           "los mismos 5 pliegues y la misma semilla.")
imagen_encajada(s, F_RF_GB, MARGEN, y, 7.86, 4.28)
tarjeta(s, 8.72, y + 0.10, 3.99, 2.05, "Gradient Boosting · E9",
        f"S/ {d(e9['MAE_cv'], 1)}", "Error absoluto medio en validación "
        "cruzada. Es el que se desplegó.", color_cifra="acento")
tarjeta(s, 8.72, y + 2.30, 3.99, 2.05, "Random Forest · E8",
        f"S/ {d(e8['MAE_cv'], 1)}", "El mismo error, a dos soles. Elegir uno u "
        "otro no cambia lo que ve el usuario.", color_cifra="texto_medio")
pie_fuente(s, f"models/ui_artifacts.json (torneo.tabla) · "
              f"src/04_torneo_regresion.py · artefactos del commit "
              f"{META['commit'][:7]}")
notas(s, f"El curso pedía comparar Random Forest y Gradient Boosting, así que "
         f"esta es la comparación de frente. Mismos datos, mismos cinco "
         f"pliegues, misma semilla. Gradient Boosting se equivoca de media en "
         f"S/ {d(e9['MAE_cv'], 1)} al mes y Random Forest en "
         f"S/ {d(e8['MAE_cv'], 1)}: dos soles de diferencia sobre un error de "
         f"seiscientos, es decir, empate práctico. La línea punteada es la "
         f"mejor especificación lineal del torneo, E7, en "
         f"S/ {d(TAB_TORNEO['E7']['MAE_cv'], 1)}: ahí sí hay una diferencia "
         f"real, de "
         f"S/ {d(TAB_TORNEO['E7']['MAE_cv'] - TAB_TORNEO['E9']['MAE_cv'], 1)}. "
         f"Detrás de esto hay un torneo de "
         f"nueve especificaciones, de E1 a E9, que está documentado en "
         f"docs/METODOLOGIA_TORNEO.md y en la propia app. Elegimos E9 por el "
         f"error en validación cruzada, nunca por el de test.")

# --- Lámina 6: clasificación, tres algoritmos [GUÍA] ---------------------
s = lamina()
cinta(s, "Bloque B · los modelos    ·    lámina 6 de 18    ·    exigida por la guía")
y = titulo(s, "En clasificación gana Gradient Boosting, también por poco",
           "Los tres algoritmos con las mismas cuatro métricas: dos ensambles "
           "y un modelo lineal.")
filas = [["Algoritmo", "PR-AUC cv", "PR-AUC test", "ROC-AUC test", "Brier test"]]
ganador = None
for k, f in enumerate(CLF_COMP):
    es_gb = "Gradient" in f["algoritmo"]
    if es_gb:
        ganador = k + 1
    filas.append([f["algoritmo"] + ("  ·  desplegado" if es_gb else ""),
                  d(f["PRAUC_cv"], 4), d(f["PRAUC_test"], 4),
                  d(f["ROCAUC_test"], 4), d(f["Brier_test"], 4)])
tabla(s, MARGEN, y, 12.09, 2.05, filas, anchos=[34, 16, 17, 17, 16],
      resaltar=ganador)
imagen_encajada(s, F_CLF, MARGEN, y + 2.20, 12.09, 2.30)
pie_fuente(s, "models/ui_artifacts.json (clasificador.comparacion) · "
              "src/06_entrenar_clasificador.py")
notas(s, f"Mismo ejercicio del lado de la clasificación, y aquí entra también "
         f"la regresión logística, que es el modelo lineal de referencia. "
         f"Gradient Boosting gana en las cuatro métricas, pero por márgenes "
         f"muy pequeños: {d(CLF_COMP[0]['PRAUC_cv'], 4)} contra "
         f"{d(CLF_COMP[1]['PRAUC_cv'], 4)} del Random Forest. El Brier mide "
         f"error de calibración, así que ahí menos es mejor. La línea roja del "
         f"gráfico es lo importante: la prevalencia. Como el "
         f"{d(BASE_PR * 100, 1)} % de los ocupados de la muestra es informal, "
         f"un modelo que dijera «informal» a todo el mundo ya tendría un "
         f"PR-AUC de {d(BASE_PR, 4)}. Por eso la mejora hay que leerla contra "
         f"esa línea y no contra cero, y por eso no usamos accuracy.")

# --- Lámina 7: cómo se eligió el ganador [GUÍA] --------------------------
s = lamina()
cinta(s, "Bloque B · los modelos    ·    lámina 7 de 18    ·    exigida por la guía")
i_op = i_umbral(PUNTO["umbral"])
cob_op = round((CURVA["tp"][i_op] + CURVA["fp"][i_op]) / CURVA["n"] * 100)
y = titulo(s, f"El umbral {d(PUNTO['umbral'], 4)} se fijó para que 9 de cada "
              f"10 señalados sean informales",
           "Elegir modelo y elegir umbral son dos decisiones distintas: la "
           "primera es técnica, la segunda es de costos.")
imagen_encajada(s, F_UMBRAL, MARGEN, y, 7.86, 4.28)
# Dos tarjetas, no tres: la prevalencia ya está dibujada en la curva como
# línea roja, y repetirla en una caja era decir dos veces lo mismo.
tarjeta(s, 8.72, y + 0.05, 3.99, 2.03, "umbral operativo",
        d(PUNTO["umbral"], 4),
        f"Probabilidad mínima para señalar. Con este umbral se señala al "
        f"{cob_op} % de los trabajadores.", color_cifra="acento")
tarjeta(s, 8.72, y + 2.25, 3.99, 2.03, "precisión exigida",
        d(PUNTO["precision_oof"], 2),
        f"De cada 100 señalados, {round(PUNTO['precision_oof'] * 100)} son "
        f"informales de verdad. Ese fue el criterio.", color_cifra="buena")
pie_fuente(s, "models/feature_schema.json (clasificador.punto_operativo) · "
              "models/ui_artifacts.json (clasificador.curva_umbral, curva OOF "
              "sobre train)")
notas(s, f"Tres decisiones de método en una lámina. Primera: el ganador se "
         f"elige por validación cruzada, no por el conjunto de prueba; el test "
         f"se mira una sola vez, al final, y no decide nada. Segunda: en "
         f"clasificación miramos PR-AUC y no accuracy, porque con una "
         f"prevalencia de {d(BASE_PR, 4)} decir «informal» a todos ya acierta "
         f"el {d(BASE_PR * 100, 1)} % de las veces. Tercera: el umbral. La "
         f"curva muestra el intercambio: cuanto más alto lo pones, más aciertas "
         f"en los que señalas y más informales se te escapan. Fijamos "
         f"{d(PUNTO['umbral'], 4)} porque es donde la precisión llega a "
         f"{d(PUNTO['precision_oof'], 2)}. En la app ese umbral se puede mover "
         f"y ver las consecuencias en vivo: es una elección de costos, no un "
         f"resultado del modelo.")

# --- Lámina 8: importancia de variables [GUÍA] ---------------------------
s = lamina()
cinta(s, "Bloque B · los modelos    ·    lámina 8 de 18    ·    exigida por la guía")
_orden = sorted(zip(IMP_REG["variables"], IMP_REG["media"]), key=lambda t: -t[1])
y = titulo(s, "La categoría ocupacional es lo que más error añade si se baraja",
           "Cuántos soles más se equivoca el modelo cuando esa variable deja "
           "de significar nada.")
imagen_encajada(s, F_IMP, MARGEN, y, 8.00, 4.55)
tarjeta(s, 8.86, y + 0.20, 3.85, 1.80, "categoría ocupacional",
        f"S/ {n(_orden[0][1])}",
        "Lo que sube el error medio al desordenar esta columna al azar.",
        color_cifra="acento")
tarjeta(s, 8.86, y + 2.20, 3.85, 1.80, "años de educación",
        f"S/ {n(_orden[1][1])}",
        "La segunda que más pesa. Las dos juntas explican la mitad del efecto "
        "medido.", color_cifra="acento")
pie_fuente(s, f"models/ui_artifacts.json (regresor.importancia_permutacion): "
              f"{IMP_REG['n_repeticiones']} repeticiones sobre "
              f"{n(IMP_REG['n_filas'])} filas de test")
notas(s, f"La guía pide explicar por qué el modelo vale lo que vale, y esta es "
         f"la forma llana de decirlo: tomamos una variable, desordenamos sus "
         f"valores al azar entre las personas, y medimos cuántos soles más se "
         f"equivoca el modelo. Si la variable no aportaba nada, no pasa nada; "
         f"si aportaba, el error sube. La categoría ocupacional sube el error "
         f"en unos S/ {n(_orden[0][1])} al mes y los años de educación en unos "
         f"S/ {n(_orden[1][1])}. Ojo con la lectura: esto mide cuánto usa el "
         f"modelo cada variable, no cuánto causa cada variable en el ingreso "
         f"real. Para la lectura causal está el modelo explicativo E6, que es "
         f"una regresión ponderada aparte y está en la app.")

# ---------------------------------------------------------------------------
# BLOQUE C — El despliegue: el corazón de la exposición
# ---------------------------------------------------------------------------
# --- Lámina 9: arquitectura del despliegue --------------------------------
s = lamina()
cinta(s, "Bloque C · el despliegue    ·    lámina 9 de 18")
y = titulo(s, "Al repositorio viajan el código y los artefactos, nunca los datos",
           "Los microdatos del INEI se quedan en la máquina; lo que sale es "
           "código y un puñado de archivos pequeños.")
imagen_encajada(s, F_ARQ, MARGEN, y, 12.09, 3.68)
_, tf = panel(s, MARGEN, y + 3.80, 12.09, 0.80, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "Cada «git push» a la rama main dispara un redespliegue automático "
            "en Streamlit Community Cloud: no hay ningún paso manual entre el "
            "editor y el navegador.",
        tam=T_CUERPO, color="texto", primero=True, esp_despues=0)
pie_fuente(s, f"docs/arquitectura.md · .gitignore · repositorio en la rama "
              f"main, commit {REPO['commit']} · tamaños medidos del disco")
notas(s, f"El pipeline completo corre en local, en VS Code: los scripts "
         f"numerados del 00 al 09 leen los microdatos del INEI, entrenan los "
         f"modelos y escriben los artefactos. Esos microdatos no se suben a "
         f"ningún lado: son {d(DATOS_MB, 1)} megabytes que se descargan de la "
         f"fuente oficial, y el repositorio los excluye por diseño en el "
         f".gitignore. Lo único que sale de la máquina son código y unos pocos "
         f"archivos pequeños: los .joblib entrenados y tres JSON, dos de "
         f"contrato con la app y uno con los hiperparámetros. En total "
         f"{d(REPO['mb'], 2)} megabytes. Streamlit Community Cloud vigila la "
         f"rama main en GitHub y cada push dispara un redespliegue automático, "
         f"sin ningún paso manual de por medio. Ese mismo repositorio tiene "
         f"una estructura de carpetas fija que conviene mirar de cerca.")

# --- Lámina 10: el repositorio por dentro --------------------------------
s = lamina()
cinta(s, "Bloque C · el despliegue    ·    lámina 10 de 18")
_arbol = {}
for _f in VERSIONADOS:
    _arbol.setdefault(_f.split("/")[0] if "/" in _f else "(raíz)", []).append(_f)
y = titulo(s, "El repositorio separa entrenamiento, artefactos, app y evidencia",
           "Cada carpeta tiene un rol fijo. Los microdatos no tienen carpeta "
           "propia porque no están aquí.")
imagen_encajada(s, FIGS / "gh_arbol.png", MARGEN, y, 5.55, 4.48)
filas = [["Carpeta", "Archivos", "Para qué"],
         ["src/", str(len(_arbol.get("src", []))),
          "scripts 00 → 09, en ese orden"],
         ["models/", str(len(_arbol.get("models", []))),
          "artefactos: .joblib y JSON de contrato"],
         ["app/", str(len(_arbol.get("app", []))),
          "la aplicación desplegada"],
         ["docs/ · reports/",
          f"{len(_arbol.get('docs', []))} · {len(_arbol.get('reports', []))}",
          "documentación y evidencia"],
         ["data/", "fuera", "microdatos del INEI: no se redistribuyen"]]
tabla(s, 6.45, y + 0.22, 6.26, 2.85, filas, anchos=[26, 17, 57], tam=16,
      tam_cab=16, cols_mono=[1])
_, tf = panel(s, 6.45, y + 3.62, 6.26, 0.86)
parrafo(tf, f"{REPO['n_archivos']} archivos versionados · "
            f"{REPO['n_commits']} commits · {d(REPO['mb'], 2)} MB",
        tam=T_CUERPO, color="acento_alto", fuente=MONO, primero=True,
        esp_despues=0)
pie_fuente(s, "git ls-files sobre el repositorio · captura de "
              "github.com/IchiSieben/enaho-ingresos-informalidad")
notas(s, f"El repositorio tiene {REPO['n_archivos']} archivos y "
         f"{REPO['n_commits']} commits, sin contar los microdatos porque esos "
         f"nunca entraron. src/ guarda los scripts numerados del 00 al 09 más "
         f"un módulo común, y se ejecutan en ese orden fijo. models/ versiona "
         f"los artefactos: los .joblib entrenados y los JSON de contrato con "
         f"la app; la caché de probabilidades out-of-fold queda fuera porque "
         f"es derivable y pesa. docs/ y reports/ juntan la documentación de "
         f"arquitectura y la evidencia de cada paso: auditoría, torneo, "
         f"ablación. data/ cierra el árbol como recordatorio de lo ya dicho: "
         f"esa carpeta no existe en el repositorio. Uno de los archivos más "
         f"simples de ese árbol, requirements.txt, es también uno de los más "
         f"importantes.")

# --- Lámina 11: de VS Code a la nube -------------------------------------
s = lamina()
cinta(s, "Bloque C · el despliegue    ·    lámina 11 de 18")
y = titulo(s, "Las versiones quedan fijadas: con otro scikit-learn el modelo "
              "no carga",
           "requirements.txt fija cada versión a la que generó los artefactos, "
           "y Streamlit Cloud reconstruye ese mismo entorno.")
imagen_encajada(s, F_REQ, MARGEN, y, 8.30, 4.35)
tarjeta(s, 9.15, y + 0.08, 3.56, 2.08, "scikit-learn fijado", SKLEARN_REQ,
        "La misma que entrenó los .joblib. Si dejan de coincidir, este "
        "generador aborta.", color_cifra="acento")
tarjeta(s, 9.15, y + 2.26, 3.56, 2.08, "la nube apunta a", "main",
        "Streamlit Cloud sigue app/streamlit_app.py en esa rama y "
        "reconstruye el entorno en cada push.", color_cifra="buena",
        tam_cifra=30)
pie_fuente(s, "requirements.txt · models/ui_artifacts.json (meta) · panel de "
              "Streamlit Community Cloud")
notas(s, f"requirements.txt no deja ninguna versión suelta. scikit-learn queda "
         f"fijado en {SKLEARN_REQ}, la misma con la que se generaron los "
         f".joblib, porque un modelo entrenado con otra versión puede no "
         f"cargar, o cargar y comportarse distinto, sin ningún aviso. La "
         f"comprobación no es una promesa del archivo: el propio generador de "
         f"esta presentación compara requirements.txt con la versión anotada "
         f"en los artefactos y se niega a producir el .pptx si no coinciden. "
         f"Del lado de la nube, Streamlit Cloud apunta a un archivo y una rama "
         f"fijos —app/streamlit_app.py en main— y reconstruye ese entorno en "
         f"cada push. Ese entorno reconstruido es el que sostiene, widget por "
         f"widget, el formulario de la app.")

# --- Lámina 12: cómo está hecho el formulario [GUÍA] ---------------------
s = lamina()
cinta(s, "Bloque C · el despliegue    ·    lámina 12 de 18    ·    exigida por la guía")
y = titulo(s, "Cada componente de Streamlit del formulario resuelve un "
              "problema concreto",
           "El formulario no declara ni un campo a mano: los recorre desde "
           "feature_schema.json.")
ANCHO_IMG = 6.90
imagen(s, FIGS / "cloud_form.png", MARGEN, y, w=ANCHO_IMG)
# Las chinchetas se colocan en fracciones de la captura, no en pulgadas
# sueltas: si mañana cambia el tamaño de la imagen, siguen en su sitio.
ALTO_IMG = ANCHO_IMG / 1.5
for k, (fx, fy) in enumerate(((0.10, 0.50), (0.30, 0.42), (0.30, 0.72),
                              (0.62, 0.30)), start=1):
    rotulo(s, MARGEN + fx * ANCHO_IMG, y + fy * ALTO_IMG, str(k))
# La leyenda va numerada y en una sola columna: cuatro entradas cortas caben,
# cuatro entradas explicadas no. El desarrollo largo está en las notas.
COMPONENTES = [
    ("1 · st.radio", "cambia de tema desde PALETAS"),
    ("2 · st.number_input", "una por variable numérica"),
    ("3 · st.selectbox", "una por variable categórica"),
    ("4 · st.expander · st.popover", "lectura llana y lectura técnica"),
]
tfc = caja(s, 7.75, y + 0.04, 4.96, 2.98)
for k, (nom, txt) in enumerate(COMPONENTES):
    parrafo(tfc, nom, tam=T_CUERPO, color="acento_alto", negrita=True,
            fuente=MONO, primero=(k == 0), esp_despues=1)
    parrafo(tfc, txt, tam=T_CUERPO, color="texto_medio", esp_despues=13,
            esp_linea=1.02)
_, tf = panel(s, 7.75, y + 3.06, 4.96, 1.55, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "st.fragment", tam=T_CUERPO, color="acento_alto", negrita=True,
        fuente=MONO, primero=True, esp_despues=2)
parrafo(tf, "El umbral vive dentro de un fragmento: moverlo reejecuta solo "
            "ese bloque, no la página entera.",
        tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.02)
pie_fuente(s, "captura de la app desplegada · app/streamlit_app.py "
              "(componentes realmente usados) · models/feature_schema.json")
notas(s, "El formulario no declara ningún campo a mano: recorre "
         "feature_schema.json y arma un control por variable, número o "
         "selector según el tipo. Los numéricos usan number_input con su paso "
         "y su rango; los categóricos, selectbox con las opciones que "
         "realmente vio el codificador entrenado. Si mañana cambia una "
         "variable en el schema, el formulario cambia solo. El bloque del "
         "umbral vive en un st.fragment: mover el slider reejecuta solo ese "
         "fragmento y no la página entera, así que la predicción y los "
         "artefactos no se vuelven a cargar en cada arrastre. El expander "
         "separa la lectura llana de la técnica, el popover resuelve una "
         "pregunta puntual sin ocupar espacio permanente, y el selector de "
         "tema es un radio que lee sus opciones de PALETAS. Todo ese "
         "formulario, sin embargo, solo predice el perfil puntual: el resto de "
         "los gráficos ya viene calculado de antes.")

# --- Lámina 13: por qué la app carga rápido ------------------------------
s = lamina()
cinta(s, "Bloque C · el despliegue    ·    lámina 13 de 18")
y = titulo(s, "En producción solo se predice el perfil; lo demás ya está "
              "calculado",
           "Curvas, histogramas y tablas se calcularon una sola vez, al "
           "entrenar. La app solo las lee y las dibuja.")
imagen_encajada(s, F_PRECOMP, MARGEN, y, 12.09, 2.92)
tarjeta(s, MARGEN, y + 3.02, 5.86, 1.60, "ui_artifacts.json",
        f"{d(UI_KB, 1)} KB", "Todo lo que la app dibuja en cada visita. No "
        "recalcula nada.", color_cifra="acento", tam_cifra=30)
tarjeta(s, 6.85, y + 3.02, 5.86, 1.60, "los dos modelos .joblib",
        f"{n(JOBLIB_KB)} KB", "Solo entran a trabajar cuando hay que predecir "
        "el perfil del formulario.", color_cifra="buena", tam_cifra=30)
pie_fuente(s, "src/09_precomputar_ui.py · models/ui_artifacts.json · "
              "models/*.joblib · tamaños medidos del disco")
notas(s, f"La decisión de ingeniería que más se nota al usar la app es esta: "
         f"nada pesado se calcula mientras alguien la mira. Las curvas de "
         f"umbral, los histogramas, las tablas de consecuencias y las "
         f"dependencias parciales se calculan una sola vez, en "
         f"09_precomputar_ui.py, y viajan como un JSON de {d(UI_KB, 1)} "
         f"kilobytes. La app en producción abre ese archivo y dibuja. Los "
         f".joblib solo entran cuando hay que predecir el perfil puntual que "
         f"arma el usuario. Además, cache_data y cache_resource evitan releer "
         f"el JSON y los modelos en cada interacción de la sesión. Community "
         f"Cloud da poca memoria por aplicación, así que mantener el trabajo "
         f"pesado fuera del tiempo de ejecución es justamente lo que permite "
         f"que cargue rápido y no se quede sin memoria. Ese mismo material "
         f"precalculado es el que sostiene la capa educativa de cada gráfico.")

# --- Lámina 14: la capa educativa ----------------------------------------
s = lamina()
cinta(s, "Bloque C · el despliegue    ·    lámina 14 de 18")
y = titulo(s, "La app se explica sola: dos capas de lectura y gráficos "
              "etiquetados",
           "Nadie debería tener que abrir el código para entender qué está "
           "viendo.")
MOSAICO = [
    ("Dos capas: llano y «Detalle técnico»", "cloud_edu_expander.png"),
    ("La matriz nombrada en castellano", "cloud_edu_matriz.png"),
    ("Cada cifra con su frase llana", "cloud_edu_tarjetas.png"),
    (f"{N_REFERENCIAS} referencias con enlace verificado", "cloud_edu_referencias.png"),
]
for k, (cap, arch) in enumerate(MOSAICO):
    cx = MARGEN + (k % 2) * 4.55
    cy = y + (k // 2) * 2.26
    tf = caja(s, cx, cy, 4.30, 0.28)
    parrafo(tf, cap.upper(), tam=T_ETIQUETA, color="texto_tenue", fuente=MONO,
            primero=True, esp_despues=0)
    imagen_encajada(s, FIGS / arch, cx, cy + 0.30, 4.30, 1.70, centrar=False)
tarjeta(s, 9.62, y + 0.08, 3.09, 2.08, "referencias", str(N_REFERENCIAS),
        "Con DOI y URL comprobadas una a una.", color_cifra="acento")
_, tf = panel(s, 9.62, y + 2.26, 3.09, 2.32)
parrafo(tf, "TAMBIÉN", tam=T_ETIQUETA, color="texto_tenue", fuente=MONO,
        primero=True, esp_despues=6)
parrafo(tf, "Ayuda en cada campo · etiquetas DATO / MECÁNICA / HIPÓTESIS en "
            "los gráficos · tres temas, con contraste AA.",
        tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.05)
pie_fuente(s, "capturas de la app desplegada · app/referencias.py · "
              "app/graficos.py · docs/manual_usuario.md")
notas(s, f"La app se pensó para que nadie necesite abrir el código. Cada "
         f"sección tiene dos capas: primero una lectura llana y después un "
         f"expander de «Detalle técnico» para quien quiera la fórmula o el "
         f"supuesto exacto. Los gráficos etiquetan cada elemento como DATO, "
         f"MECÁNICA o HIPÓTESIS, para distinguir qué es medición, qué es cómo "
         f"funciona el cálculo y qué es una lectura nuestra. La matriz de "
         f"confusión no usa la jerga de verdaderos y falsos positivos: nombra "
         f"las cuatro casillas en castellano. Y hay {N_REFERENCIAS} "
         f"referencias bibliográficas con el enlace comprobado una a una, "
         f"ancladas a la sección que las cita. Toda esta capa solo tiene "
         f"sentido si el modelo que corre en la nube es exactamente el mismo "
         f"que se entrenó en local: eso es lo que se verificó a continuación.")

# ---------------------------------------------------------------------------
# BLOQUE D — Que funciona de verdad
# ---------------------------------------------------------------------------
def lamina_verificacion(numero, guia_txt, tit, ent, fig_consola, captura,
                        tarjetas, pie, nota):
    s = lamina()
    cinta(s, f"Bloque D · que funciona    ·    lámina {numero} de 18{guia_txt}")
    y = titulo(s, tit, ent)
    imagen_encajada(s, fig_consola, MARGEN, y, 5.30, 3.00)
    tf = caja(s, 5.98, y + 1.28, 0.60, 0.5)
    parrafo(tf, "=", tam=40, color="buena", negrita=True, primero=True,
            esp_despues=0, alin=PP_ALIGN.CENTER)
    imagen_encajada(s, captura, 6.62, y, 6.09, 3.00)
    tf = caja(s, MARGEN, y + 3.06, 5.30, 0.30)
    parrafo(tf, "VS CODE · CONSOLA LOCAL", tam=T_ETIQUETA, color="texto_tenue",
            fuente=MONO, primero=True, esp_despues=0, alin=PP_ALIGN.CENTER)
    tf = caja(s, 6.62, y + 3.06, 6.09, 0.30)
    parrafo(tf, "STREAMLIT COMMUNITY CLOUD · APP PÚBLICA", tam=T_ETIQUETA,
            color="texto_tenue", fuente=MONO, primero=True, esp_despues=0,
            alin=PP_ALIGN.CENTER)
    anchura = (12.09 - 0.35 * (len(tarjetas) - 1)) / len(tarjetas)
    for k, (etq, cif, txt, col) in enumerate(tarjetas):
        tarjeta(s, MARGEN + k * (anchura + 0.35), y + 3.44, anchura, 1.30,
                etq, cif, txt, color_cifra=col, tam_cifra=26)
    pie_fuente(s, pie)
    notas(s, nota)
    return s


lamina_verificacion(
    15, "    ·    exigida por la guía",
    "La consola local y la app pública dan el mismo número",
    "Mismo perfil, mismo artefacto: se corrió en VS Code y se comparó con la "
    "app ya desplegada.",
    F_CONSOLA_REG, FIGS / "cloud_reg_tarjetas.png",
    [("ingreso típico (mediana)", f"S/ {ING_TIPICO}",
      "El mismo valor en los dos entornos.", "acento"),
     ("ingreso esperado (media)", f"S/ {ING_ESPERADO}",
      f"Aplica el factor de Duan {d(REG['smearing_duan'], 4)} sobre la "
      f"mediana.", "acento")],
    "docs/presentacion/verificacion_local.py · captura de la app desplegada",
    f"Antes de mostrar la app en clase corrimos el mismo perfil en la consola "
    f"local de VS Code y lo comparamos con la app ya desplegada. El resultado "
    f"es idéntico: S/ {ING_TIPICO} de ingreso típico, que es la mediana que da "
    f"el Gradient Boosting E9, y S/ {ING_ESPERADO} de ingreso esperado, que "
    f"aplica el factor de smearing de Duan sobre esa mediana. Cuidado con lo "
    f"que prueba esto: no valida que el modelo prediga bien, valida que la app "
    f"en la nube corre exactamente el mismo artefacto que se entrenó y se "
    f"probó en local, no una copia vieja ni un reentrenamiento distinto. La "
    f"misma comprobación se repitió con el segundo modelo.")

_horas_clf = next(f["default"] for f in CLF["features"]
                  if f["nombre"] == "horas_total")
_horas_reg = next(f["default"] for f in REG["features"]
                  if f["nombre"] == "horas_total")
lamina_verificacion(
    16, "    ·    exigida por la guía",
    f"El clasificador también coincide: {PROBA_ES} en los dos entornos",
    "La misma comprobación con el segundo modelo, y una diferencia de perfil "
    "que conviene declarar.",
    F_CONSOLA_CLF, FIGS / "cloud_clf_resultado.png",
    [("probabilidad de informalidad", PROBA_ES,
      "Mismo número en la consola y en la app.", "acento"),
     ("veredicto", "señalado",
      f"Con el umbral operativo {d(PUNTO['umbral'], 4)} de la lámina 7.",
      "media")],
    "docs/presentacion/verificacion_local.py · models/feature_schema.json "
    "(punto_operativo) · captura de la app desplegada",
    f"La consola local y la app en la nube devuelven la misma probabilidad, "
    f"{PROBA_ES}, con el mismo umbral operativo de {d(PUNTO['umbral'], 4)} que "
    f"fijamos en la lámina 7. Un detalle honesto que conviene decir en voz "
    f"alta: el formulario del clasificador arranca con "
    f"{d(_horas_clf, 0)} horas por defecto y el del regresor con "
    f"{d(_horas_reg, 0)}; el script de verificación usa el valor por defecto "
    f"de cada modelo, así que los dos perfiles de las láminas 15 y 16 no son "
    f"idénticos entre sí. Dentro de cada lámina, en cambio, la consola y la "
    f"app comparan exactamente el mismo perfil. La consola imprime la palabra "
    f"INFORMAL y la app dice «señalado para focalización»: es lo mismo dicho "
    f"de dos maneras, y la de la app es deliberada, porque la señal es sobre "
    f"una configuración de empleo y no sobre la persona. Antes de dar la app "
    f"por buena, el proyecto pasó también por una auditoría interna.")

# --- Lámina 17: la auditoría en una lámina -------------------------------
s = lamina()
cinta(s, "Bloque D · que funciona    ·    lámina 17 de 18")
_aut = UA["torneo"]["autopsia"]
y = titulo(s, "La auditoría encontró cuatro problemas y publicó los cuatro",
           "Una revisión de consistencia antes de publicar: cada cifra contra "
           "el archivo que la genera, cada cita contra su fuente.")
filas = [["Hallazgo", "Dónde nació", "Qué pasó"],
         ["El centinela 999999 leído como un ingreso",
          "DATOS DE ORIGEN",
          f"El R² pasa de {d(_aut['corrida_sucia']['r2'], 3)} a "
          f"{d(_aut['corrida_limpia']['r2'], 3)} al tratarlo como faltante"],
         ["La rejilla de hiperparámetros estaba acotada",
          "DECISIÓN PROPIA",
          f"El error baja de S/ {REJILLA['vieja']} a S/ {REJILLA['nueva']}: "
          f"{REJILLA['mejora_pct']} %. No se promovió"],
         ["Una cifra del INEI con la etiqueta equivocada",
          "DECISIÓN PROPIA",
          f"El {EXTERNA['inei_1_10']} % es del tramo 1-10, no de «Hasta 20»"],
         ["Tres afirmaciones distintas sobre el mismo R²",
          "DECISIÓN PROPIA · DOCUMENTACIÓN",
          "Ni Lemieux ni Heckman reportan ese R²"]]
# Ojo: python-pptx NO recorta una tabla, la CRECE hasta que quepa el texto. El
# alto que se le pasa es un mínimo, así que lo que va debajo hay que colocarlo
# contando con ese crecimiento — o acortar la celda, que es lo que se hizo.
tabla(s, MARGEN, y, 12.09, 2.65, filas, anchos=[32, 24, 44], tam=16,
      tam_cab=16, cols_mono=[])
_, tf = panel(s, MARGEN, y + 3.05, 12.09, 1.48, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "LA LÍNEA DE MÉTODO", tam=T_ETIQUETA, color="acento_alto",
        fuente=MONO, primero=True, esp_despues=6)
parrafo(tf, "Los problemas de origen se corrigen y se documentan; los propios "
            "se corrigen y se aprende de ellos; los de cita se verifican yendo "
            "al texto completo. Ninguno se borra: un hallazgo corregido en "
            "silencio es un hallazgo desperdiciado.",
        tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.06)
pie_fuente(s, "INFORME_AUDITORIA.md · models/ui_artifacts.json (torneo.autopsia) "
              "· la sección «Qué encontró la auditoría» de la propia app")
notas(s, f"Antes de publicar, el proyecto se auditó a sí mismo: cada cifra "
         f"contra el script que la genera, cada cita contra su fuente "
         f"original. Aparecieron cuatro problemas y se publicaron los cuatro. "
         f"El primero venía en los datos: el INEI codifica «no sabe» como "
         f"999999 y ese valor se estaba leyendo como un ingreso real de casi "
         f"un millón de soles; convertirlo en dato faltante subió el R² de "
         f"{d(_aut['corrida_sucia']['r2'], 3)} a "
         f"{d(_aut['corrida_limpia']['r2'], 3)} y devolvió el sentido "
         f"económico a los coeficientes. Ese fallo estaba en los datos del "
         f"INEI, no en el modelado de nadie. Los otros tres nacieron en "
         f"nuestro propio trabajo de elegir y de resumir, y uno de ellos "
         f"además en las citas. Ninguno cambia el modelo que está en "
         f"producción. El valor de auditar no fue que no hubiera errores: fue "
         f"encontrarlos y dejarlos escritos.")

# --- Lámina 18: conclusiones [GUÍA] --------------------------------------
s = lamina()
cinta(s, "Bloque D · que funciona    ·    lámina 18 de 18    ·    exigida por la guía")
y = titulo(s, "El regresor compara perfiles; el clasificador señala, no "
              "predice destinos",
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
_, tf = panel(s, MARGEN, y + 2.44, 5.86, 2.14)
parrafo(tf, "QUÉ DEJÓ EL DESPLIEGUE", tam=T_ETIQUETA, color="texto_tenue",
        fuente=MONO, primero=True, esp_despues=6)
parrafo(tf, f"Fijar las versiones exactas (scikit-learn {SKLEARN_REQ}, pandas "
            f"{META['version_pandas']}) y precomputar todo lo pesado en un "
            f"JSON de {d(UI_KB, 1)} KB es lo que hace que la app cargue "
            f"rápido y no se quede sin memoria.",
        tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.06)
_, tf = panel(s, 6.85, y + 2.44, 5.86, 2.14, relleno="acento_fondo",
              borde="acento")
parrafo(tf, "CRÉDITOS", tam=T_ETIQUETA, color="acento_alto", fuente=MONO,
        primero=True, esp_despues=6)
parrafo(tf, "Software y análisis (CRediT): Yoichi Palacios Tanaka. "
            "Exposición y trabajo de curso: Alan Nestor Cañazaca Mamani, "
            "Magdalena Quico de la Cruz y Edgar Delgado Ortega. Docente: "
            "Orlando Advíncula Zeballos.",
        tam=T_CUERPO, color="texto", esp_despues=0, esp_linea=1.06)
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
SALIDA = AQUI / "ENAHO_exposicion.pptx"
prs.save(SALIDA)
print(f"{SALIDA.relative_to(RAIZ)} · {len(prs.slides.__iter__.__self__._sldIdLst)} "
      f"láminas · {SALIDA.stat().st_size / 1e6:.2f} MB")
print("Verifícala con:  .venv/Scripts/python.exe docs/presentacion/verificar_ppt.py")
