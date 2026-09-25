# streamlit_app.py — app Streamlit: predicción, torneo y ficha (ES / EN)
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
FASE 3 — App: ingreso laboral e informalidad en el Perú (ENAHO 2025).

Arquitectura heredada del proyecto hermano de salud publica:
- La UI la dirige `models/feature_schema.json`; ningún campo está escrito aquí.
- Lo caro vive precomputado en `models/ui_artifacts.json`.
- El bloque de umbral corre en un `@st.fragment`: mover el slider no reejecuta
  el script ni vuelve a predecir.
- Los modelos se cargan bajo demanda y cacheados.
- Ningún número visible está escrito a mano: sale del schema o los artefactos.

Novedades de este proyecto:
- Modo claro/oscuro: `PALETAS` con las mismas claves; el CSS se GENERA desde la
  paleta activa y los SVG la reciben como parámetro.
- Sección «Torneo de modelos»: la exposición hecha interfaz (tres actos).
- Experiencia potencial: el usuario NO la digita; se deriva de edad y educación.
- Bilingüe (v1.1): todo texto visible va en pares L("es", "en"); los valores
  que ve el modelo siguen en español (ver app/i18n.py). `?lang=en` en la URL
  abre la versión en inglés.
- Estimación en vivo: el perfil se estima al mover cualquier control, y hay
  perfiles de ejemplo de un clic.

v1.2:
- Sin sidebar: una barra superior con sección, idioma y tema, los tres
  ligados a la URL (`?sec=`, `?lang=`, `?theme=`) sin pisarse entre sí.
- Los SVG van en línea (markdown con HTML), sin un iframe por gráfico.

Uso:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import json
import re
import sys
from html import escape
from pathlib import Path
from time import perf_counter
from urllib.parse import quote

import joblib
import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estilos
import graficos
import i18n
import referencias
from estilos import PALETAS
from i18n import L, d, n, pc, pct, tr
from referencias import ref

RAIZ = Path(__file__).resolve().parents[1]
DIR_MODELS = RAIZ / "models"

VERSION = "1.2"
AUTOR = "Yoichi Palacios Tanaka"
GRUPO = ["Alan Nestor Cañazaca Mamani", "Magdalena Quico de la Cruz",
         "Edgar Delgado Ortega"]
PORTAFOLIO = "https://ichi7.dev"

# --------------------------------------------------------------------------
# Contratos con los módulos y con el artefacto
# --------------------------------------------------------------------------
# Los tres fallos del despliegue del 20/08/2026 fueron el mismo tipo de cosa:
# este archivo pedía algo que su proveedor no tenía, y el error saltaba a
# mitad del render —cuando el usuario ya estaba mirando la pantalla— en vez de
# al arrancar. Lo que sigue lo convierte en un fallo temprano y explícito.
GRAFICOS_REQUERIDOS = [
    "proporcion", "embudo", "franja_probabilidad", "matriz_confusion",
    "curva_precision_cobertura", "curva_calibracion", "curva_roc", "curva_pr",
    "barras_importancia", "situador", "dependencia_parcial", "barras_mae",
    "viaje_dato", "miniatura_pd",
]

# Claves del artefacto sin las que una sección no puede dibujarse. Se listan
# como rutas para poder decir exactamente cuál falta.
CLAVES_ARTEFACTO = [
    ("clasificador", "curva_umbral"),
    ("clasificador", "histograma_oof"),
    ("clasificador", "tasas_observadas"),
    ("clasificador", "dependencia_parcial"),
    ("regresor", "importancia_permutacion"),
    ("torneo", "tabla"),
    ("torneo", "autopsia", "ecuacion_inicial"),
    ("torneo", "autopsia", "corrida_limpia"),
]


def _verificar_graficos() -> None:
    faltan = [f for f in GRAFICOS_REQUERIDOS if not hasattr(graficos, f)]
    if faltan:
        raise ImportError(
            "app/graficos.py no expone " + ", ".join(faltan) + ". "
            "Si el despliegue acaba de actualizarse, el proceso puede estar "
            "sirviendo una versión anterior del módulo: reinicia la app "
            "(Manage app › Reboot) en lugar de esperar a que se recargue sola."
        )


_verificar_graficos()


def validar_artefactos(art: dict) -> dict:
    """
    Comprueba que el artefacto trae las claves que la interfaz da por hechas.

    Devuelve el mismo dict para poder encadenarlo. Levanta `KeyError` con la
    ruta exacta que falta: es preferible una pantalla de error que diga qué
    regenerar, a un `KeyError` suelto en medio de una sección.
    """
    if not art:
        return art          # la app ya avisa aparte de que falta el archivo
    for ruta in CLAVES_ARTEFACTO:
        nodo = art
        for i, clave in enumerate(ruta):
            if not isinstance(nodo, dict) or clave not in nodo:
                falta = " → ".join(ruta[:i + 1])
                raise KeyError(
                    f"models/ui_artifacts.json no tiene «{falta}». "
                    f"Regenéralo con «python src/09_precomputar_ui.py». Si "
                    f"acabas de desplegar, puede que el proceso siga con el "
                    f"artefacto anterior en caché: reinicia la app.")
            nodo = nodo[clave]
    return art


# (clave, icono). El título y la descripción dependen del idioma: salen de
# titulo_seccion() / descripcion_seccion(), no de esta lista.
SECCIONES = [
    ("ingreso", ":material/payments:"),
    ("informalidad", ":material/work_history:"),
    ("torneo", ":material/emoji_events:"),
    ("ficha", ":material/fact_check:"),
    ("maquinas", ":material/precision_manufacturing:"),
]


SECCION_POR_DEFECTO = "ingreso"
CLAVES_SECCION = [c for c, _ in SECCIONES]


def titulo_corto(clave: str) -> str:
    """Rótulo de la barra superior: las cinco caben en una fila a 1366 px."""
    return {
        "ingreso": L("Ingreso", "Income"),
        "informalidad": L("Informalidad", "Informality"),
        "torneo": L("Torneo", "Tournament"),
        "ficha": L("Ficha", "Model card"),
        "maquinas": L("Cómo se hizo", "Making of"),
    }[clave]


def titulo_seccion(clave: str) -> str:
    return {
        "ingreso": L("Estimación de ingreso", "Income estimate"),
        "informalidad": L("Empleo informal", "Informal employment"),
        "torneo": L("Torneo de modelos", "Model tournament"),
        "ficha": L("Ficha técnica", "Model card"),
        "maquinas": L("Cómo se hizo", "How it was built"),
    }[clave]


# Una línea llana por sección: qué hace, sin tener que entrar. Va en el pie,
# como mapa de la app.
def descripcion_seccion(clave: str) -> str:
    return {
        "ingreso": L("Arma un perfil y estima su ingreso mensual típico — "
                     "regresión.",
                     "Build a worker profile and estimate its typical "
                     "monthly income — regression."),
        "informalidad": L("El mismo perfil: probabilidad de que ese empleo "
                          "sea informal — clasificación.",
                          "Same profile: how likely that job is to be "
                          "informal — classification."),
        "torneo": L("Las 9 recetas comparadas y por qué ganó Gradient "
                    "Boosting.",
                    "Nine specifications head to head, and why Gradient "
                    "Boosting won."),
        "ficha": L("Datos, variables, métricas y límites, en una página.",
                   "Data, features, metrics and limits on one page."),
        "maquinas": L("El paso a paso del proyecto: datos → modelos → nube.",
                      "The pipeline step by step: data → models → cloud."),
    }[clave]


DERIVADAS = {"exper", "exper2"}   # las calcula la app, no el usuario

REPO = "https://github.com/IchiSieben/enaho-ingresos-informalidad"
BLOB = f"{REPO}/blob/main"
RUTA_REPO = re.compile(r"[\w./-]+\.(md|csv|py|json|log|toml|txt)")


def enlace_evidencia(evidencia: str) -> str:
    """
    «reports/00_autopsia_baseline.md §5» → enlace al archivo en GitHub.

    El «§n» queda fuera del href a propósito: GitHub ancla por el texto del
    encabezado (`#5-titulo`), no por su número, así que un fragmento `#§5` no
    llevaría a ninguna parte y GitHub no devuelve error por un ancla que no
    existe — el lector aterrizaría arriba del archivo sin saber por qué.
    """
    ruta, _, seccion = evidencia.partition(" §")
    ruta = ruta.strip()
    if " " in ruta or not RUTA_REPO.fullmatch(ruta):
        return f"<code>{escape(evidencia)}</code>"
    cola = f" §{escape(seccion)}" if seccion else ""
    return (f"<a class='chip-evidencia' target='_blank' rel='noopener' "
            f"href='{BLOB}/{quote(ruta)}'>{escape(ruta)}{cola} ↗</a>")


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cargar_schema() -> dict:
    return json.loads((DIR_MODELS / "feature_schema.json").read_text(encoding="utf-8"))


def firma_artefactos() -> tuple:
    """
    Identidad de la versión del artefacto en disco: (tamaño, mtime).

    `st.cache_data` indexa por los argumentos de la función, no por lo que hay
    en el archivo. Sin esta firma, un artefacto ya actualizado en disco seguía
    sirviéndose desde la caché del proceso tras un redespliegue en caliente
    —fue lo que mantuvo vivo el `KeyError: 'ecuacion_inicial'` a través de
    varios deploys seguidos.
    """
    ruta = DIR_MODELS / "ui_artifacts.json"
    if not ruta.exists():
        return ()
    s = ruta.stat()
    return (s.st_size, int(s.st_mtime))


# La firma va SIN guion bajo inicial a propósito: st.cache_data EXCLUYE de la
# clave de caché los parámetros que empiezan con «_» — con `_firma` la caché
# tenía una sola entrada para siempre y un redespliegue en caliente seguía
# sirviendo el artefacto viejo (solo el reboot lo curaba). Verificado
# empíricamente: f((1,)) y f((2,)) devolvían lo mismo.
@st.cache_data(show_spinner=False)
def _leer_artefactos(firma: tuple) -> dict:
    ruta = DIR_MODELS / "ui_artifacts.json"
    if not ruta.exists():
        return {}
    return validar_artefactos(json.loads(ruta.read_text(encoding="utf-8")))


def cargar_artefactos() -> dict:
    return _leer_artefactos(firma_artefactos())


# ui_maquinas.json es HERMANO de ui_artifacts.json (ambos los escribe src/09).
# Va en archivo aparte a propósito: la presentación congelada del 25/08/2026
# cita el tamaño en disco de ui_artifacts.json (44,7 KB) y verificar_ppt.py lo
# mide con stat() — ese archivo no puede crecer ni un byte. Las cifras nuevas
# de la sala de máquinas viven aquí; las viejas no se tocan.
def firma_maquinas() -> tuple:
    ruta = DIR_MODELS / "ui_maquinas.json"
    if not ruta.exists():
        return ()
    s = ruta.stat()
    return (s.st_size, int(s.st_mtime))


@st.cache_data(show_spinner=False)
def _leer_maquinas(firma: tuple) -> dict:
    # `firma` sin guion bajo: ver la nota de _leer_artefactos.
    ruta = DIR_MODELS / "ui_maquinas.json"
    if not ruta.exists():
        return {}
    return json.loads(ruta.read_text(encoding="utf-8"))


def cargar_maquinas() -> dict:
    return _leer_maquinas(firma_maquinas())


@st.cache_resource(show_spinner=False)
def cargar_modelo(nombre: str):
    return joblib.load(DIR_MODELS / nombre)


def columnas_esperadas(modelo) -> list[str]:
    interno = getattr(modelo, "regressor_", modelo)
    for obj in (interno, modelo):
        nombres = getattr(obj, "feature_names_in_", None)
        if nombres is not None:
            return list(nombres)
        prep = getattr(obj, "named_steps", {}).get("prep")
        if prep is not None and hasattr(prep, "feature_names_in_"):
            return list(prep.feature_names_in_)
    raise RuntimeError("El modelo no declara feature_names_in_")


# --------------------------------------------------------------------------
# Presentación
# --------------------------------------------------------------------------
# El selector de tema deriva sus opciones de PALETAS, no de una lista escrita
# aparte: así no pueden desincronizarse. Las etiquetas son solo presentación;
# si un tema no la tiene, se usa su clave capitalizada en vez de romper.
TEMA_POR_DEFECTO = "claro"


def etiquetas_tema() -> dict[str, str]:
    return {"claro": L("Claro", "Light"), "oscuro": L("Oscuro", "Dark"),
            "terminal": "Terminal"}


def opciones_tema() -> list[str]:
    """Los temas que existen de verdad, en orden estable."""
    return list(PALETAS)


def etiqueta_tema(clave: str) -> str:
    return etiquetas_tema().get(clave, clave.capitalize())


def tema_activo() -> str:
    """
    El tema de la sesión, siempre uno que exista.

    Sin `.get()` con valor por defecto a ciegas: si en la sesión quedó un tema
    que ya no existe (porque se renombró o se quitó), se corrige el estado y se
    sigue. Antes eso dejaba la app inaccesible —T() reventaba en cada
    ejecución, incluso antes de dibujar el selector con el que revertirlo.
    """
    tema = st.session_state.get("tema", TEMA_POR_DEFECTO)
    if tema not in PALETAS:
        tema = TEMA_POR_DEFECTO
        st.session_state["tema"] = tema
    return tema


def T() -> dict:
    return PALETAS[tema_activo()]


# Los tres controles de la barra y su parámetro de URL: (clave, defecto).
# La clave del widget ES el nombre del parámetro.
def _ligados() -> list[tuple[str, list, str]]:
    return [("sec", CLAVES_SECCION, SECCION_POR_DEFECTO),
            ("lang", list(i18n.IDIOMAS), i18n.IDIOMA_POR_DEFECTO),
            ("theme", list(PALETAS), TEMA_POR_DEFECTO)]


def _valor_ligado(clave: str, validos, defecto: str) -> str:
    """
    Valor de un control de la barra: primero la sesión (lo que el usuario
    eligió), si no la URL validada, si no el defecto.

    Por qué no `bind="query-params"` de Streamlit: verificado en Chromium con
    1.61, el frontend escribe en la URL el RÓTULO formateado de la opción
    (`?sec=Model+card`), no su valor. La URL cambiaba con el idioma y
    `?sec=torneo` no abría nada. AppTest no lo detecta porque no pasa por el
    frontend. Aquí la URL lleva siempre la clave estable.
    """
    v = st.session_state.get(clave)
    if v in validos:
        return v
    q = st.query_params.get(clave)
    return q if q in validos else defecto


def iniciar_estado() -> None:
    """
    Idioma, tema y sección salen de los tres controles de la barra (claves
    `lang`, `theme`, `sec`). Corre ANTES de dibujarlos: `set_page_config` y el
    CSS ya necesitan idioma y tema.

    El valor inicial se escribe en la sesión en vez de pasarlo como `default`:
    un `default` que cambia entre ejecuciones cambia la identidad del widget.
    Luego se copia a las claves de siempre (`idioma`, `tema`, `seccion`),
    que son las que leen i18n y el resto de la app.
    """
    for clave, validos, defecto in _ligados():
        st.session_state[clave] = _valor_ligado(clave, validos, defecto)
    st.session_state["idioma"] = st.session_state["lang"]
    st.session_state["tema"] = st.session_state["theme"]
    st.session_state["seccion"] = st.session_state["sec"]


def sincronizar_url() -> None:
    """
    Escribe en la URL solo lo que difiere del defecto, y respeta cualquier
    otro parámetro que traiga. Así cada control escribe SU parámetro sin
    pisar los otros dos, y la URL limpia es la portada.
    """
    propios = {c for c, _, _ in _ligados()}
    actual = st.query_params.to_dict()
    nuevo = {k: v for k, v in actual.items() if k not in propios}
    nuevo.update({c: st.session_state[c] for c, _, d in _ligados()
                  if st.session_state[c] != d})
    if nuevo != actual:
        st.query_params.from_dict(nuevo)


def html(s: str) -> None:
    st.markdown(s, unsafe_allow_html=True)


def tarjeta(etiqueta: str, valor: str, nota: str = "", color: str | None = None,
            llano: str = "") -> str:
    """`llano` es la capa 1: la frase que explica la cifra sin jerga."""
    estilo = f" style='color:{color}'" if color else ""
    frase = f"<div class='tarjeta-llano'>{llano}</div>" if llano else ""
    pie = f"<div class='tarjeta-nota'>{nota}</div>" if nota else ""
    return (f"<div class='tarjeta'><div class='tarjeta-etiqueta'>{etiqueta}</div>"
            f"<div class='tarjeta-valor'{estilo}>{valor}</div>{frase}{pie}</div>")


def cabecera(pregunta: str, llano: str, detalle: str, seccion: str,
             eyebrow: str = "") -> None:
    """
    Dos capas: el titulo es una pregunta, debajo va lenguaje llano, y el texto
    técnico exacto se muda a un expander. La precisión no se borra, se baja de
    capa.

    `seccion` desambiguaba el expander de v1.1 (cuatro expanders llamados
    igual eran el mismo widget). El popover de v1.2 no guarda estado, pero se
    conserva el parámetro: las cinco llamadas lo pasan.
    """
    if eyebrow:
        html(f"<div class='eyebrow eyebrow-seccion'>{eyebrow}</div>")
    html(f"<h1>{pregunta}</h1>")
    # v1.2: el detalle va en un popover al final de la entradilla, no en un
    # expander a todo el ancho: son ~50 px menos antes de los controles.
    with st.container(horizontal=True, vertical_alignment="bottom", gap="small"):
        html(f"<div class='entradilla'>{llano}</div>")
        with st.popover(L("Detalle técnico", "Technical detail"),
                        icon=":material/info:", type="tertiary"):
            html(f"<div class='sutil' style='max-width:68ch'>{detalle}</div>")


def grafico(svg: str, alto: int, vistazo: bool = False) -> None:
    """
    SVG en línea: sin iframe, hereda fuentes y paleta de la página.

    Por qué `st.markdown` y no `st.html`: verificado en Chromium con 1.61,
    `st.html` elimina el <svg> entero al sanear (el div llega vacío).
    `st.markdown(unsafe_allow_html=True)` conserva <title>, <animate>,
    <animateMotion>, clases, `style` y `aria-label`. Los SVG de `graficos`
    no usan `id`.

    La caja toma la proporción del viewBox (nunca recorta: el SVG escala con
    `meet`) y `alto` queda como tope, para que un gráfico estrecho no se
    estire a todo el ancho de la página. `vistazo` marca el gráfico clave de
    la sección (lo mide docs/qa/medir_vistazo.py).
    """
    w, h = graficos.proporcion(svg)
    extra = " vistazo-grafico" if vistazo else ""
    html(f"<div class='grafico{extra}{clase_quieta()}' style='aspect-ratio:"
         f"{w:g}/{h:g};max-height:{alto}px'>{svg}</div>")


def clase_quieta() -> str:
    """
    « quieto» cuando la animación de entrada NO debe repetirse.

    Cada rerun (o rerun de fragment) reemplaza el DOM del gráfico, así que su
    animación de entrada volvería a correr: arrastrar un slider haría crecer
    las barras desde cero en cada paso. Solo se anima al ENTRAR a la sección.
    """
    return "" if st.session_state.get("_animar", True) else " quieto"


def vistazo_resumen(cifras: list[tuple[str, str]], frase: str,
                    fila: bool = False) -> None:
    """
    Resumen de un vistazo: tres cifras grandes con su rótulo y una frase. Las
    cifras llegan ya calculadas desde los artefactos; esta función solo las
    maqueta. En columna junto al gráfico, o `fila=True` bajo un gráfico
    ancho (el viaje del dato no se deja leer a media página).
    """
    filas = "".join(f"<div class='vistazo-cifra'><b>{c}</b><span>{r}</span></div>"
                    for c, r in cifras)
    html(f"<div class='vistazo-cifras{' fila' if fila else ''}'>{filas}"
         f"<div class='vistazo-frase'>{frase}</div></div>")


def aviso(texto: str, clase: str = "senal-aviso") -> None:
    html(f"<div class='senal {clase}'><div>▲</div><div>{texto}</div></div>")


# --------------------------------------------------------------------------
# Formulario dirigido por el schema (con derivadas ocultas)
# --------------------------------------------------------------------------
def ayuda_de(feat: dict) -> str | None:
    partes = [tr(feat[k]) for k in ("nota", "nota_otros") if feat.get(k)]
    if feat.get("agrupadas_en_otros"):
        partes.append(L("Agrupadas en «OTROS»: ", "Grouped under “OTHER”: ")
                      + ", ".join(tr(x) for x in feat["agrupadas_en_otros"]))
    return "\n\n".join(partes) or None


# Perfiles de ejemplo: un clic y el formulario se llena. Son perfiles
# ILUSTRATIVOS armados a mano (no casos reales de la encuesta); todo valor
# está dentro de los rangos y opciones del schema, y si alguno deja de estarlo
# el formulario lo ignora en vez de romper.
PERFILES = [
    {"id": "profesional",
     "es": "Profesional en Lima", "en": "Lima professional",
     "valores": {"anios_educ": 17, "edad": 35, "horas_total": 45,
                 "sexo": "Mujer", "area": "Urbana",
                 "dominio": "Lima Metropolitana",
                 "rama": "Servicios profesionales y financieros",
                 "tamano_empresa": "Más de 500", "categoria": "Empleado"}},
    {"id": "agricultor",
     "es": "Agricultor de la sierra", "en": "Highland farmer",
     "valores": {"anios_educ": 6, "edad": 48, "horas_total": 40,
                 "sexo": "Hombre", "area": "Rural", "dominio": "Sierra Sur",
                 "rama": "Agropecuario y pesca",
                 "tamano_empresa": "Hasta 20", "categoria": "Independiente"}},
    {"id": "comerciante",
     "es": "Comerciante independiente", "en": "Self-employed trader",
     "valores": {"anios_educ": 11, "edad": 38, "horas_total": 50,
                 "sexo": "Mujer", "area": "Urbana", "dominio": "Costa Norte",
                 "rama": "Comercio", "tamano_empresa": "Hasta 20",
                 "categoria": "Independiente"}},
    {"id": "obrero",
     "es": "Obrero de construcción", "en": "Construction worker",
     "valores": {"anios_educ": 11, "edad": 29, "horas_total": 48,
                 "sexo": "Hombre", "area": "Urbana", "dominio": "Costa Centro",
                 "rama": "Construcción", "tamano_empresa": "21 a 50",
                 "categoria": "Obrero"}},
    {"id": "docente",
     "es": "Docente de escuela pública", "en": "Public school teacher",
     "valores": {"anios_educ": 16, "edad": 45, "horas_total": 30,
                 "sexo": "Mujer", "area": "Urbana", "dominio": "Sierra Centro",
                 "rama": "Enseñanza", "tamano_empresa": "Más de 500",
                 "categoria": "Empleado"}},
]


def _aplicar_perfil(prefijo: str, features: list[dict]) -> None:
    """Callback de los perfiles: escribe en las claves de los widgets."""
    elegido = st.session_state.get(f"perfil_{prefijo}")
    perfil = next((p for p in PERFILES if p["id"] == elegido), None)
    if not perfil:
        return
    memoria = st.session_state.setdefault(f"valores_{prefijo}", {})
    for feat in features:
        nombre = feat["nombre"]
        v = perfil["valores"].get(nombre)
        if v is None or nombre in DERIVADAS:
            continue
        if feat["tipo"] == "numerico":
            if not float(feat["min"]) <= float(v) <= float(feat["max"]):
                continue
        elif v not in feat["opciones"]:
            continue
        st.session_state[f"{prefijo}_{nombre}"] = v
        memoria[nombre] = v


def selector_perfiles(prefijo: str, features: list[dict]) -> None:
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        html("<div class='eyebrow' style='white-space:nowrap'>"
             + L("Perfil · ejemplos de un clic", "Profile · one-click examples")
             + "</div>")
        st.pills(L("Perfiles de ejemplo", "Example profiles"),
                 [p["id"] for p in PERFILES],
                 format_func=lambda k: next(p[i18n.idioma()] for p in PERFILES
                                            if p["id"] == k),
                 key=f"perfil_{prefijo}", label_visibility="collapsed",
                 on_change=_aplicar_perfil, args=(prefijo, features))


def _control(feat: dict, prefijo: str, memoria: dict, rejilla: bool = False):
    """
    Un control para una variable del schema, según la forma del dato:
    numérica → slider (se ve el rango), categórica de hasta 3 opciones →
    control segmentado, el resto → lista.

    El valor inicial solo se pasa si la clave del widget aún no existe: pasar
    `value=` a un widget cuyo estado ya fijó un perfil hace que Streamlit
    pinte una advertencia amarilla en plena pantalla.
    """
    nombre, clave = feat["nombre"], f"{prefijo}_{feat['nombre']}"
    etiqueta = tr(feat.get("etiqueta", nombre))
    ayuda = ayuda_de(feat)
    if rejilla and len(etiqueta) > 24:
        # En la rejilla la etiqueta va en una línea y puede cortarse con
        # elipsis (CSS): la ayuda repite la etiqueta completa. Solo en las
        # largas: a un segmentado sin ayuda no se le agrega un icono vacío.
        ayuda = f"**{etiqueta}**" + (f"\n\n{ayuda}" if ayuda else "")
    previo = memoria.get(nombre, feat["default"])
    ya = clave in st.session_state
    if feat["tipo"] == "numerico":
        lo, hi = float(feat["min"]), float(feat["max"])
        entero = all(float(feat[k]).is_integer() for k in ("min", "max", "default"))
        inicial = min(max(float(previo), lo), hi)
        if entero:
            kw = {} if ya else {"value": int(inicial)}
            v = st.slider(etiqueta, int(lo), int(hi), step=1, key=clave,
                          help=ayuda, **kw)
        else:
            kw = {} if ya else {"value": inicial}
            v = st.slider(etiqueta, lo, hi, step=0.01, key=clave,
                          help=ayuda, **kw)
        return float(v)
    opciones = feat["opciones"]
    if ya and st.session_state[clave] not in opciones:
        del st.session_state[clave]
        ya = False
    inicial = previo if previo in opciones else opciones[0]
    if _es_compacto(feat):
        kw = {} if ya else {"default": inicial}
        v = st.segmented_control(etiqueta, opciones, format_func=tr,
                                 key=clave, help=ayuda, **kw)
        # El segmentado deselecciona al volver a pulsar: se recuerda el
        # último valor válido en vez de dejar el perfil a medias.
        return memoria.get(nombre, inicial) if v is None else v
    kw = {} if ya else {"index": opciones.index(inicial)}
    return st.selectbox(etiqueta, opciones, format_func=tr,
                        key=clave, help=ayuda, **kw)


def _es_compacto(feat: dict) -> bool:
    """Sliders y segmentados comparten fila; las listas van en otra."""
    return feat["tipo"] == "numerico" or len(feat["opciones"]) <= 3


def formulario(features: list[dict], prefijo: str,
               rejilla: bool = False) -> pd.DataFrame:
    """
    Un control por variable del schema, EXCEPTO la experiencia potencial y su
    cuadrado: son derivadas de Mincer (edad − años educ − 6, truncada en 0) y
    digitarlas seria redundante e inconsistente. Se calculan aqui.

    `rejilla=True` (ingreso e informalidad, v1.2): el formulario a todo el
    ancho en dos filas, sliders y segmentados en una, listas en otra, para
    que pregunta, controles y respuesta quepan sin scroll a 1366×768. La
    sala de máquinas lo usa en una columna angosta: ahí sigue vertical.
    Los valores siguen en español: `tr()` solo cambia lo que se muestra.
    """
    memoria = st.session_state.setdefault(f"valores_{prefijo}", {})
    visibles = [f for f in features if f["nombre"] not in DERIVADAS]
    valores = {}
    if rejilla:
        compactos = [f for f in visibles if _es_compacto(f)]
        listas = [f for f in visibles if not _es_compacto(f)]
        for grupo, por_fila in ((compactos, 5), (listas, 4)):
            for k in range(0, len(grupo), por_fila):
                cols = st.columns(por_fila, gap="medium")
                for col, feat in zip(cols, grupo[k:k + por_fila]):
                    with col:
                        valores[feat["nombre"]] = _control(feat, prefijo, memoria,
                                                           rejilla=True)
    else:
        for feat in visibles:
            valores[feat["nombre"]] = _control(feat, prefijo, memoria)

    if {"edad", "anios_educ"} <= set(valores):
        exper = max(float(valores["edad"]) - float(valores["anios_educ"]) - 6, 0.0)
        valores["exper"] = exper
        valores["exper2"] = exper ** 2
        html("<div class='sutil derivada'>"
             + L(f"Experiencia potencial derivada: <b>{exper:.0f} años</b> "
                 f"(edad − años de educación − 6, truncada en 0).",
                 f"Derived potential experience: <b>{exper:.0f} years</b> "
                 f"(age − years of schooling − 6, floored at 0).")
             + "</div>")

    st.session_state[f"valores_{prefijo}"] = valores
    orden = [f["nombre"] for f in features]
    return pd.DataFrame([valores])[[c for c in orden if c in valores]]


# Por qué cada variable se comporta como se comporta. Tres niveles, siempre
# etiquetados: DATO es lo que mide la barra; MECÁNICA es cuando la explicación
# es la propia regla que define el target (y entonces el resultado es en parte
# por construcción, no un hallazgo); HIPÓTESIS es lectura económica plausible,
# marcada como tal. Solo se escriben las que se pueden sostener.
def porques() -> dict[str, dict[str, str]]:
    return {
        "tamano_empresa": {
            "mecanica": L(
                "En empresas de hasta 20 personas casi nadie aporta a pensión, "
                "y esa es justamente una de las dos reglas que definen "
                "«informal». La barra casi toca el techo por construcción: el "
                "modelo no está descubriendo algo, está reflejando la "
                "definición.",
                "In firms of up to 20 people almost nobody contributes to a "
                "pension — and that is precisely one of the two rules that "
                "define “informal”. The bar nearly hits the ceiling by "
                "construction: the model isn't discovering anything, it's "
                "mirroring the definition."),
        },
        "categoria": {
            "mecanica": L(
                "La categoría ocupacional decide qué regla se aplica: a "
                "independientes y empleadores se les mira el RUC; a los "
                "dependientes, el aporte a pensión. Que pese mucho es parte "
                "del diseño del target, no un descubrimiento del modelo.",
                "Employment category decides which rule applies: the "
                "self-employed and employers are checked for a tax ID (RUC); "
                "employees, for pension contributions. Its heavy weight is "
                "part of how the target is built, not something the model "
                "discovered."),
        },
        "dominio": {
            "hipotesis": L(
                "Selva y sierra concentran empleo independiente y "
                "agropecuario, y la literatura asocia esa estructura "
                "productiva a mayor informalidad. Es una interpretación del "
                "patrón, no una prueba: haría falta comparar empleos "
                "equivalentes entre regiones.",
                "The Amazon and the highlands concentrate self-employment and "
                "farming, and the literature links that production structure "
                "to higher informality. This is a reading of the pattern, not "
                "proof: you would need to compare equivalent jobs across "
                "regions."),
        },
        "rama": {
            "hipotesis": L(
                "El agro y el comercio minorista concentran unidades pequeñas "
                "y trabajo por cuenta propia; la administración pública y la "
                "enseñanza, empleo asalariado con planilla. Es lectura del "
                "contexto productivo, no algo que estos datos prueben por sí "
                "solos.",
                "Farming and retail concentrate small units and own-account "
                "work; public administration and education, salaried jobs on "
                "a formal payroll. It's a reading of the economic context, "
                "not something these data prove on their own."),
        },
        "anios_educ": {
            "hipotesis": L(
                "Más educación se asocia a empleos con contrato y planilla. "
                "Pero aquí no se puede separar el efecto de la educación del "
                "de los empleos a los que da acceso: es asociación, no causa.",
                "More schooling goes with jobs that have contracts and a "
                "payroll. But here the effect of education can't be separated "
                "from that of the jobs it opens up: association, not "
                "causation."),
        },
        "area": {
            "hipotesis": L(
                "El empleo rural es mayoritariamente agropecuario e "
                "independiente, donde el registro tributario y la planilla son "
                "excepción. Es una interpretación de la composición del "
                "empleo, no una prueba.",
                "Rural employment is mostly farming and self-employment, "
                "where tax registration and payrolls are the exception. An "
                "interpretation of the job mix, not proof."),
        },
    }


def porque(variable: str, dato: str) -> str:
    """Bloque «por qué» con la etiqueta de honestidad que corresponda."""
    fichas = [f"<div class='porque-fila'><span class='etiqueta-dato'>"
              f"{L('dato', 'data')}</span><span>{dato}</span></div>"]
    p = porques().get(variable, {})
    if p.get("mecanica"):
        fichas.append(f"<div class='porque-fila'>"
                      f"<span class='etiqueta-mecanica'>"
                      f"{L('mecánica', 'mechanics')}</span>"
                      f"<span>{p['mecanica']}</span></div>")
    if p.get("hipotesis"):
        fichas.append(f"<div class='porque-fila'>"
                      f"<span class='etiqueta-hipotesis'>"
                      f"{L('hipótesis', 'hypothesis')}</span>"
                      f"<span>{p['hipotesis']}</span></div>")
    return f"<div class='porque'>{''.join(fichas)}</div>"


def titulo_oracion(variable: str, etiqueta: str, tasas: dict) -> str:
    """
    Título que dice el hallazgo, no la variable: «La informalidad es más alta
    en el campo: 88 % rural frente a 60 % urbana». Sale de las tasas
    observadas del artefacto — nunca escrito a mano, así no se desincroniza.
    """
    t = tasas.get(variable)
    if not t:
        return etiqueta
    alto, bajo = t["max"], t["min"]
    return L(f"{etiqueta}: {pc(alto['pct_ponderado'])} en "
             f"«{tr(alto['categoria'])}» frente a {pc(bajo['pct_ponderado'])} "
             f"en «{tr(bajo['categoria'])}»",
             f"{etiqueta}: {pc(alto['pct_ponderado'])} for "
             f"“{tr(alto['categoria'])}” vs. {pc(bajo['pct_ponderado'])} for "
             f"“{tr(bajo['categoria'])}”")


def situadores(valores: dict, features: list[dict], cohorte: dict) -> None:
    numericas = [f for f in features if f["tipo"] == "numerico"
                 and f["nombre"] not in DERIVADAS
                 and cohorte.get(f["nombre"], {}).get("tipo") == "numerico"]
    for feat in numericas:
        c = cohorte[feat["nombre"]]
        grafico(graficos.situador(float(valores.get(feat["nombre"], 0)),
                                  c["percentiles"],
                                  tr(feat.get("etiqueta", feat["nombre"]))
                                  + L(" · cohorte ponderada",
                                      " · weighted cohort"),
                                  T()), 74)
    # La marca vertical no se explicaba sola: quien no conoce la palabra
    # «mediana» veía un número flotando junto a una barra.
    if numericas:
        html("<div class='sutil'>"
             + L("La marca es la mediana de la cohorte: la mitad de los "
                 "encuestados está por debajo de ese valor. Tu perfil es el "
                 "punto de color.",
                 "The tick is the cohort median: half of the respondents sit "
                 "below that value. Your profile is the colored dot.")
             + "</div>")


# --------------------------------------------------------------------------
# Franja de cifras clave (la portada)
# --------------------------------------------------------------------------
def franja_kpi(schema: dict, art: dict) -> None:
    """
    Cuatro cifras que resumen el proyecto antes de leer nada: lo que miraría
    un gerente en diez segundos. Todas salen de los artefactos.
    """
    maq = cargar_maquinas()
    etapas = {e["clave"]: e for e in maq.get("embudo", {}).get("etapas", [])}
    muestra = etapas.get("torneo", {}).get("filas")
    tabla = art.get("torneo", {}).get("tabla", [])
    mae = schema["regresor"]["metricas_test"]["mae_mediana"]
    prauc = art.get("clasificador", {}).get("pr", {}).get("auc")
    kpis = [
        (n(muestra) if muestra else "—",
         L("trabajadores en la muestra", "workers in the sample"),
         L("ENAHO 2025 · INEI", "ENAHO 2025 · INEI (Peru)")),
        (str(len(tabla)) if tabla else "—",
         L("modelos en el torneo", "models in the tournament"),
         L("mismas filas, mismos pliegues", "same rows, same folds")),
        (f"S/ {n(mae)}", L("error medio del ingreso", "income mean abs. error"),
         L("MAE en test, por persona", "test MAE, per person")),
        (d(prauc, 2) if prauc else "—",
         L("PR-AUC informalidad", "informality PR-AUC"),
         L("clasificador en test", "classifier on test")),
    ]
    html("<div class='franja-kpi'>" + "".join(
        f"<div class='kpi' style='animation-delay:{i * 70}ms'>"
        f"<div class='kpi-valor'>{v}</div><div class='kpi-rotulo'>{r}</div>"
        f"<div class='kpi-nota'>{nota}</div></div>"
        for i, (v, r, nota) in enumerate(kpis)) + "</div>")


# --------------------------------------------------------------------------
# Umbral e impacto — fragment
# --------------------------------------------------------------------------
def indice_umbral(curva: dict, t: float) -> int:
    umbrales = curva["umbral"]
    return min(range(len(umbrales)), key=lambda i: abs(umbrales[i] - t))


def a_hist_oof() -> dict | None:
    """Histograma OOF para la franja; el fragment no recibe los artefactos."""
    return cargar_artefactos().get("clasificador", {}).get("histograma_oof")


def _ir_a_demasiado_bueno() -> None:
    st.session_state["sec"] = "ficha"
    st.session_state["resaltar_demasiado_bueno"] = True


@st.fragment
def bloque_umbral(clas: dict, curva: dict) -> None:
    """Mover el slider solo reejecuta esta función: nada se vuelve a predecir."""
    p_op = clas["punto_operativo"]
    refs = p_op["referencias"]
    presets = {
        "operativo": (float(p_op["umbral"]),
                      L("Punto operativo ★", "Operating point ★")),
        "por_defecto": (float(refs["umbral_05"]["umbral"]),
                        L("Neutro 0,5", "Neutral 0.5")),
        "f1": (float(refs["f1_optimo"]["umbral"]), L("Máx. F1", "Max F1")),
    }

    # v1.2: veredicto y franja a la izquierda, la vara a la derecha — lo que
    # cabe en la primera pantalla. Consecuencias, curva y matriz, en pestañas.
    col_v, col_p = st.columns([60, 40], gap="large")
    with col_p:
        html("<div class='eyebrow'>" + L("Dónde poner la vara",
                                         "Where to set the bar") + "</div>")
        preset = st.radio(
            L("Preajuste", "Preset"), list(presets) + ["libre"], index=0,
            format_func=lambda k: (L("Umbral libre", "Custom threshold")
                                   if k == "libre" else
                                   f"{presets[k][1]} · {d(presets[k][0], 3)}"),
            label_visibility="collapsed", key="preset_umbral",
            help=L("Los tres primeros son puntos de corte ya elegidos con "
                   "criterios distintos. «Umbral libre» te deja moverlo a mano "
                   "para ver qué se gana y qué se pierde.",
                   "The first three are cut-offs chosen by different "
                   "criteria. “Custom threshold” lets you move it by hand to "
                   "see what you gain and what you lose."))
        if preset == "libre":
            umbral = st.slider(L("Umbral", "Threshold"), 0.05, 0.95,
                               float(st.session_state.get("umbral_libre", 0.50)),
                               0.005, key="umbral_libre", format="%.3f",
                               help=L("Súbelo para señalar solo los casos más "
                                      "claros; bájalo para no dejar escapar "
                                      "informales, a costa de señalar "
                                      "formales.",
                                      "Raise it to flag only the clearest "
                                      "cases; lower it to miss fewer informal "
                                      "workers, at the cost of flagging "
                                      "formal ones."))
        else:
            umbral = presets[preset][0]
            st.slider(L("Umbral", "Threshold"), 0.05, 0.95, umbral, 0.005,
                      disabled=True, format="%.3f",
                      key=f"slider_fijo_{preset}")
        html("<div class='sutil'>"
             + L("Mover el umbral no recalcula la probabilidad del perfil: "
                 "mueve la vara con la que decidimos señalar. <b>La "
                 "probabilidad la pone el modelo; el umbral lo pones tú.</b>",
                 "Moving the threshold doesn't recompute the profile's "
                 "probability: it moves the bar we use to decide whom to "
                 "flag. <b>The model sets the probability; you set the "
                 "threshold.</b>") + "</div>")

    proba = st.session_state.get("proba_informal")
    i = indice_umbral(curva, umbral)

    # ---- Consecuencias en vivo ----
    # Los tres son números vivos: ninguno está escrito a mano.
    total = curva["n"]
    tp, fp = curva["tp"][i], curva["fp"][i]
    tn, fn = curva["tn"][i], curva["fn"][i]
    k = 1000 / total
    m_tp, m_fp, m_tn, m_fn = (round(tp * k), round(fp * k),
                              round(tn * k), round(fn * k))
    prec = curva["precision_1"][i]
    rec = curva["recall_1"][i]
    pct_senalado = (tp + fp) / total * 100

    with col_v:
        if proba is not None:
            senalado = proba >= umbral
            col = T()["senal_media"] if senalado else T()["senal_buena"]
            veredicto = (L("Señalado para focalización", "Flagged for targeting")
                         if senalado else
                         L("Sin señal por este criterio",
                           "Not flagged under this criterion"))
            html(f"<div class='fila-veredicto'>"
                 f"<span class='cifra-veredicto' style='color:{col}'>"
                 f"{pct(proba, 1)}</span>"
                 f"<span class='texto-veredicto' style='color:{col}'>"
                 f"{veredicto}</span></div>")
            html("<div class='sutil' style='margin:-2px 0 6px 0'>"
                 + (L("Su probabilidad estimada supera el umbral. La señal "
                      "apunta a una configuración de empleo, no es un "
                      "veredicto sobre la persona.",
                      "Its estimated probability is above the threshold. The "
                      "flag points to a job configuration — it is not a "
                      "verdict on the person.") if senalado else
                    L("Su probabilidad estimada queda por debajo del umbral.",
                      "Its estimated probability is below the threshold."))
                 + "</div>")
            grafico(graficos.franja_probabilidad(
                proba, umbral, a_hist_oof(), T()), 165, vistazo=True)
            # El botón vive dentro de un fragment: el callback fija la
            # sección (la clave del control de la barra, que aún no se ha
            # dibujado en el próximo run) y el rerun de toda la app se pide
            # en la rama verdadera, porque `st.rerun` dentro de un callback
            # no hace nada.
            if st.button(L("¿Por qué tan alto? →", "Why so high? →"),
                         key="ir_demasiado_bueno", type="tertiary",
                         on_click=_ir_a_demasiado_bueno,
                         help=L("Abre «¿Es demasiado bueno el clasificador?» "
                                "en la Ficha técnica: por qué un PR-AUC de "
                                "0,96 aquí es coherente y no señal de fuga de "
                                "información.",
                                "Opens “Is the classifier too good to be "
                                "true?” in the Model card: why a 0.96 PR-AUC "
                                "is consistent here and not a sign of data "
                                "leakage.")):
                st.rerun(scope="app")

    t_cons, t_curva, t_matriz = st.tabs([
        L("Qué pasa con este umbral", "What this threshold does"),
        L("Precisión frente a cobertura", "Precision vs. coverage"),
        L("Matriz de confusión", "Confusion matrix")])

    with t_cons:
        if proba is not None:
            col = T()["senal_media"] if proba >= umbral else T()["senal_buena"]
            # Los tres porcentajes de esta pantalla miden cosas distintas y se
            # confunden con facilidad. Se nombran juntos, una sola vez.
            html(f"<div class='tres-numeros'>"
                 f"<div><b style='color:{col}'>{pct(proba, 1)}</b>"
                 f"<span>{L('de ESTE PERFIL: así de informal es esta configuración', 'for THIS PROFILE: how informal this configuration looks')}</span></div>"
                 f"<div><b style='color:{T()['acento_alto']}'>{pc(pct_senalado)}</b>"
                 f"<span>{L('de LA POBLACIÓN queda sobre el umbral', 'of THE POPULATION sits above the threshold')}</span></div>"
                 f"<div><b style='color:{T()['senal_buena']}'>{pc(prec * 100)}</b>"
                 f"<span>{L('de PRECISIÓN: de cada 100 señalados, cuántos aciertas', 'PRECISION: out of 100 flagged, how many are right')}</span></div>"
                 f"</div>")
        html(f"<div class='panel' style='margin-top:8px'>"
             f"<div style='font-size:15px;line-height:1.9;color:{T()['texto']}'>"
             + L(f"Con umbral <b>{d(umbral, 3)}</b>:<br>"
                 f"se señala al <b style='color:{T()['acento_alto']}'>"
                 f"{pc(pct_senalado)}</b> de los trabajadores · "
                 f"de cada 100 señalados, <b style='color:{T()['senal_buena']}'>"
                 f"{round(prec * 100)}</b> son informales · "
                 f"se escapan <b style='color:{T()['senal_mala']}'>"
                 f"{round((1 - rec) * 100)}</b> de cada 100 informales "
                 f"(<i>falsos negativos</i>: el modelo no los señaló y sí lo eran).",
                 f"At threshold <b>{d(umbral, 3)}</b>:<br>"
                 f"<b style='color:{T()['acento_alto']}'>{pc(pct_senalado)}</b> "
                 f"of workers get flagged · "
                 f"out of every 100 flagged, <b style='color:{T()['senal_buena']}'>"
                 f"{round(prec * 100)}</b> are informal · "
                 f"<b style='color:{T()['senal_mala']}'>"
                 f"{round((1 - rec) * 100)}</b> out of every 100 informal workers "
                 f"slip through (<i>false negatives</i>: the model didn't flag "
                 f"them, but they were informal).")
             + "</div></div>")
        html("<div class='sutil' style='margin-top:8px'>"
             + L(f"★ El punto operativo aprobado exige <b>precisión ≥ 0,90 para "
                 f"la clase informal</b>: ",
                 f"★ The approved operating point requires <b>precision ≥ 0.90 "
                 f"for the informal class</b>: ")
             + tr(p_op['frase_exposicion']) + "</div>")
        with st.popover(L("¿Puede ser cero?", "Could it be zero?")):
            html("<div class='sutil' style='max-width:60ch'>"
                 + L(f"Sí: con umbral 0 señalas a todos y no se escapa nadie — "
                     f"pero la precisión cae a "
                     f"<b>{pct(clas['prevalencia_train'], 0)}</b> (la "
                     f"prevalencia), igual que señalar al azar. Por eso el umbral "
                     f"es una elección de costos, no un defecto.",
                     f"Yes: with a threshold of 0 you flag everyone and nobody "
                     f"slips through — but precision drops to "
                     f"<b>{pct(clas['prevalencia_train'], 0)}</b> (the "
                     f"prevalence), no better than flagging at random. That's why "
                     f"the threshold is a cost trade-off, not a flaw.")
                 + "</div>")

    with t_curva:
        if a_curva := curva.get("precision_1"):
            grafico(graficos.curva_precision_cobertura(
                curva["recall_1"], a_curva, (rec, prec),
                [(presets[k_][1], indice_umbral(curva, presets[k_][0]))
                 for k_ in presets], curva, T()), 350)
            html("<div class='sutil'>"
                 + L("El punto blanco es el umbral que tienes puesto. Las marcas "
                     "son los tres preajustes. Cada punto de la curva es un umbral "
                     "posible: subirlo te mueve arriba y a la izquierda (más "
                     "acierto, más informales que se escapan); bajarlo, abajo y a "
                     "la derecha.",
                     "The hollow dot is your current threshold; the small marks "
                     "are the three presets. Every point on the curve is a "
                     "possible threshold: raising it moves you up and to the left "
                     "(more precision, more informal workers missed); lowering "
                     "it, down and to the right.")
                 + "</div>")

    with t_matriz:
        html("<div class='sutil' style='max-width:78ch;margin-bottom:8px'>"
             + L("Cada trabajador cae en una de estas cuatro casillas según lo que "
                 "el modelo dijo y lo que realmente era. <b>Subir el umbral</b> "
                 "reduce los falsos positivos y aumenta los falsos negativos: "
                 "señalas menos gente, aciertas más en los que señalas, pero se te "
                 "escapan más informales. <b>Bajarlo</b> hace exactamente lo "
                 "contrario. No hay un punto que mejore las dos cosas a la vez; "
                 "por eso hay que elegir.",
                 "Every worker lands in one of these four boxes, depending on what "
                 "the model said and what was actually true. <b>Raising the "
                 "threshold</b> cuts false positives and adds false negatives: "
                 "you flag fewer people and are right more often, but more "
                 "informal workers slip through. <b>Lowering it</b> does exactly "
                 "the opposite. No point improves both at once — that's why you "
                 "have to choose.")
             + "</div>")
        grafico(graficos.matriz_confusion(m_tp, m_fp, m_tn, m_fn, T()), 330)
        html("<div class='sutil'>"
             + L(f"Calculado sobre {n(total)} trabajadores del entrenamiento con "
                 f"probabilidades <i>out-of-fold</i> —es decir, estimadas para "
                 f"cada persona por un modelo que no la usó al entrenar— y "
                 f"escalado a 1.000. Precisión de la clase informal: "
                 f"{d(prec, 4)} · recall: {d(rec, 4)}.",
                 f"Computed on {n(total)} training workers using "
                 f"<i>out-of-fold</i> probabilities — each person scored by a "
                 f"model that never saw them during training — and scaled to "
                 f"1,000. Informal-class precision: {d(prec, 4)} · recall: "
                 f"{d(rec, 4)}.")
             + "</div>")


# --------------------------------------------------------------------------
# Sección 1: estimación de ingreso
# --------------------------------------------------------------------------
@st.fragment
def _ingreso_en_vivo(schema: dict, art: dict) -> None:
    """
    Todo lo que depende del perfil, en un fragment: mover un slider reejecuta
    solo esto (formulario, estimación, cifra, tarjetas, cohorte), no la
    cabecera ni lo que va debajo del pliegue.
    """
    reg = schema["regresor"]
    b = art.get("regresor", {})
    with st.container(border=True, key="caja_form_reg"):
        selector_perfiles("reg", reg["features"])
        fila = formulario(reg["features"], "reg", rejilla=True)
    # Estimación en vivo: predecir una fila con el modelo ya cacheado cuesta
    # milisegundos, así que no hace falta un botón que el usuario olvide.
    modelo = cargar_modelo("regresor_e9.joblib")
    st.session_state["ingreso"] = float(
        modelo.predict(fila[columnas_esperadas(modelo)])[0])

    ingreso = st.session_state["ingreso"]
    smear = float(reg["smearing_duan"])
    media = (ingreso + 1) * smear - 1
    ing_art = b.get("ingreso", {})
    mediana_pob = float(ing_art.get("mediana_ponderada",
                                    reg["ingreso_mediano_train"]))

    # Cifra protagonista: el ingreso típico, grande, con su lectura al
    # lado y una barra que lo sitúa frente a la mediana del país.
    razon = ingreso / mediana_pob if mediana_pob else 1.0
    rel = (L(f"{d(razon, 1)} × la mediana del país",
             f"{d(razon, 1)}× the national median") if razon >= 1.05 else
           L(f"{pc((1 - razon) * 100)} por debajo de la mediana del país",
             f"{pc((1 - razon) * 100)} below the national median")
           if razon <= 0.95 else
           L("en la mediana del país", "right at the national median"))
    tope = max(ingreso, mediana_pob, media) * 1.15
    html(f"<div class='hero-cifra{clase_quieta()}'>"
         f"<div class='eyebrow'>{L('Ingreso mensual típico estimado', 'Estimated typical monthly income')}</div>"
         f"<div class='hero-fila'><span class='hero-valor'>S/ {n(ingreso)}</span>"
         f"<span class='hero-rel'>{rel}</span></div>"
         f"<div class='hero-barra'>"
         f"<div class='hero-relleno' style='width:{ingreso / tope * 100:.1f}%'></div>"
         f"<div class='hero-marca{' hero-marca-der' if mediana_pob / tope > 0.7 else ''}' "
         f"style='left:{mediana_pob / tope * 100:.1f}%'>"
         f"<span>{L('mediana país', 'national median')} S/ {n(mediana_pob)}</span></div>"
         f"</div></div>")

    # El ingreso típico ya es la cifra protagonista: las tarjetas dan el
    # contexto (promedio, país, casos parecidos), no lo repiten.
    tarjetas = [
        tarjeta(L("ingreso esperado", "expected income"), f"S/ {n(media)}",
                llano=L("El promedio. Es más alto porque unos pocos "
                        "sueldos muy grandes lo jalan hacia arriba.",
                        "The average. It's higher because a few very "
                        "large paychecks pull it up."),
                nota=L(f"Incluye la corrección × {d(smear, 3)} que "
                       f"compensa haber entrenado en logaritmo — ver "
                       f"«Cómo leer estas cifras».",
                       f"Includes the × {d(smear, 3)} correction that "
                       f"offsets training on the log scale — see “How to "
                       f"read these figures”.")),
        tarjeta(L("mediana del país", "national median"),
                f"S/ {n(mediana_pob)}",
                llano=L(f"Para comparar: la mitad de todos los "
                        f"trabajadores del país gana menos de "
                        f"S/ {n(mediana_pob)}.",
                        f"For reference: half of all workers in Peru "
                        f"earn less than S/ {n(mediana_pob)}.")),
    ]

    # IQR de casos comparables
    v = st.session_state.get("valores_reg", {})
    if ing_art.get("comparables") and {"sexo", "area", "anios_educ"} <= set(v):
        educ = float(v["anios_educ"])
        banda = ("0-6" if educ <= 6 else "7-11" if educ <= 11
                 else "12-14" if educ <= 14 else "15+")
        comp = ing_art["comparables"].get(f"{v['sexo']}|{v['area']}|{banda}")
        if comp:
            pista = L("Un percentil marca el punto por debajo del cual "
                      "queda ese porcentaje de los casos: el P25 deja "
                      "debajo al 25 % y el P75, al 75 %. Entre los dos "
                      "vive la mitad central.",
                      "A percentile is the point below which that share "
                      "of cases falls: P25 leaves 25% below it and P75, "
                      "75%. The middle half lives between them.")
            tarjetas.append(tarjeta(
                L("casos comparables", "comparable cases")
                + f" (<span class='pista' title='{pista}'>P25–P75</span>)",
                f"S/ {n(comp['p25'])} – {n(comp['p75'])}",
                L(f"{tr(v['sexo']).lower()}, área {tr(v['area']).lower()}, "
                  f"{banda} años de educación · mediana S/ {n(comp['p50'])}"
                  f" · n={n(comp['n'])}",
                  f"{tr(v['sexo']).lower()}, {tr(v['area']).lower()} area, "
                  f"{banda} years of schooling · median S/ "
                  f"{n(comp['p50'])} · n={n(comp['n'])}"),
                llano=L(f"De los {n(comp['n'])} encuestados parecidos a "
                        f"este perfil, la mitad del medio gana entre "
                        f"S/ {n(comp['p25'])} y S/ {n(comp['p75'])}: un "
                        f"25 % gana menos que S/ {n(comp['p25'])} y un "
                        f"25 % más que S/ {n(comp['p75'])}.",
                        f"Of the {n(comp['n'])} respondents similar to "
                        f"this profile, the middle half earns between "
                        f"S/ {n(comp['p25'])} and S/ {n(comp['p75'])}: "
                        f"25% earn less than S/ {n(comp['p25'])} and 25% "
                        f"more than S/ {n(comp['p75'])}.")))

    html("<div class='rejilla-tarjetas'>" + "".join(tarjetas) + "</div>")
    st.write("")
    mae = reg["metricas_test"]["mae_mediana"]
    aviso(L(f"<b>Esta cifra es un ingreso típico, no una promesa de "
            f"sueldo.</b> En promedio se equivoca en unos S/ {n(mae)} por "
            f"persona. Sirve para comparar perfiles entre sí, no para "
            f"decirle a nadie cuánto va a cobrar.",
            f"<b>This is a typical income, not a salary promise.</b> On "
            f"average it's off by about S/ {n(mae)} per person. Use it to "
            f"compare profiles, not to tell anyone what they will be "
            f"paid."))

    with st.expander(L("Cómo leer estas cifras", "How to read these figures")):
        html("<div class='sutil'>" + L(
            f"<b>Por qué la primera cifra es una mediana y no un "
            f"promedio.</b> El modelo aprende sobre el logaritmo del "
            f"ingreso, porque unos pocos sueldos altísimos deforman "
            f"cualquier promedio. Al deshacer ese logaritmo se obtiene la "
            f"<i>mediana condicional</i>: el valor que parte al grupo en "
            f"dos mitades iguales. Es la cifra honesta para «cuánto gana "
            f"alguien así».<br><br>"
            f"<b>De dónde sale la corrección × {d(smear, 3)}.</b> Para "
            f"pasar de la mediana al promedio no basta con deshacer el "
            f"logaritmo: hay que multiplicar por un factor que recupera la "
            f"masa de la cola alta. Es la corrección de <i>smearing</i>"
            f"{ref('duan1983')} de Duan (1983), estimada con los residuos "
            f"de validación cruzada del entrenamiento. Sin ella, el "
            f"promedio saldría subestimado en torno a un "
            f"{pc((1 - 1 / smear) * 100)}.<br><br>"
            f"<b>Qué queda fuera.</b> El target es solo dinero: el pago en "
            f"especie y el autoconsumo (que recibe el 24,6 % de los "
            f"ocupados, sobre todo en el agro) no se cuentan. Y es un "
            f"ingreso anualizado y repartido en doce meses, no el del mes "
            f"de la entrevista.<br><br>"
            f"<b>Error de la estimación.</b> MAE en el conjunto de prueba: "
            f"S/ {n(mae)}. La incertidumbre individual es grande y está "
            f"declarada: el modelo ordena perfiles, no liquida sueldos.",
            f"<b>Why the first figure is a median, not an average.</b> The "
            f"model learns on the log of income, because a handful of "
            f"very high paychecks distort any average. Undoing the log "
            f"gives the <i>conditional median</i>: the value that splits "
            f"the group into two equal halves. It's the honest answer to "
            f"“how much does someone like this earn”.<br><br>"
            f"<b>Where the × {d(smear, 3)} correction comes from.</b> To "
            f"go from the median to the mean, undoing the log isn't "
            f"enough: you have to multiply by a factor that recovers the "
            f"mass of the upper tail. That's Duan's (1983) "
            f"<i>smearing</i> correction{ref('duan1983')}, estimated from "
            f"the training cross-validation residuals. Without it the "
            f"mean would be understated by about "
            f"{pc((1 - 1 / smear) * 100)}.<br><br>"
            f"<b>What's left out.</b> The target is cash only: in-kind "
            f"pay and own consumption (received by 24.6% of workers, "
            f"mostly in farming) aren't counted. And it's an annualized "
            f"income split over twelve months, not the interview "
            f"month's.<br><br>"
            f"<b>Estimation error.</b> Test-set MAE: S/ {n(mae)}. "
            f"Individual uncertainty is large and stated up front: the "
            f"model ranks profiles, it doesn't set salaries.")
            + "</div>")

    if b.get("cohorte"):
        with st.expander(L("Tu perfil frente a la cohorte",
                           "Your profile vs. the cohort")):
            situadores(v, reg["features"], b["cohorte"])


def seccion_ingreso(schema: dict, art: dict) -> None:
    reg = schema["regresor"]
    b = art.get("regresor", {})

    n_train = int(reg["n_entrenamiento"]) + int(reg["n_test"])
    cabecera(
        L("¿Cuánto gana al mes una persona con este perfil?",
          "How much does a person with this profile earn per month?"),
        L(f"Aprendió de {n(n_train)} trabajadores de la ENAHO 2025 (INEI). "
          "Elige un ejemplo o mueve los controles: la estimación cambia al "
          "instante. Es un promedio del año y solo cuenta pagos en dinero.",
          f"Trained on {n(n_train)} workers from Peru's ENAHO 2025 household "
          "survey (INEI). Pick an example or move the controls: the estimate "
          "updates instantly. It's a year-round average of cash pay only."),
        tr(reg['descripcion_target']) + "<br><br>"
        + L("«Imputada» significa que el INEI completó los valores que la "
            "persona no supo responder. «Deflactada» significa que los soles "
            "de todos los meses se llevaron a un mismo poder adquisitivo, para "
            "que sean comparables. «Anualizada ÷ 12» significa que se suma el "
            "ingreso de todo el año y se reparte en doce meses iguales: por "
            "eso es un ingreso estabilizado y no el del mes de la entrevista. "
            "La población son ocupados de 14 años o más con ingreso laboral "
            "positivo.",
            "“Imputed” means INEI filled in values the respondent couldn't "
            "answer. “Deflated” means soles from every month were brought to "
            "the same purchasing power so they are comparable. “Annualized ÷ "
            "12” means the whole year's income is added up and split into "
            "twelve equal months — a smoothed income, not the one from the "
            "interview month. The population is employed people aged 14+ with "
            "positive labor income. Amounts are in Peruvian soles (S/)."),
        seccion=L("ingreso", "income"),
        eyebrow=L("Regresión · Gradient Boosting", "Regression · Gradient Boosting"))
    _ingreso_en_vivo(schema, art)
    # Las cifras del proyecto, debajo del pliegue hasta que exista la
    # portada «Empieza aquí» (Fase 4).
    franja_kpi(schema, art)

    imp = b.get("importancia_permutacion")
    if imp:
        st.divider()
        html("<h2>" + L("Si barajamos al azar esta variable, ¿cuántos soles "
                        "más se equivoca el modelo?",
                        "If we shuffle this feature at random, how many more "
                        "soles does the model miss by?") + "</h2>")
        html("<div class='entradilla'>" + L(
            "Eso mide la <b>importancia por permutación</b>: se desordena una "
            "sola variable, se vuelve a estimar, y se mira cuánto empeora. "
            "Cuanto más empeora, más dependía el modelo de esa variable. "
            "<b>MAE</b> es el error promedio en soles.",
            "That's what <b>permutation importance</b> measures: shuffle a "
            "single feature, predict again, and see how much worse it gets. "
            "The bigger the hit, the more the model relied on that feature. "
            "<b>MAE</b> is the mean absolute error in soles.") + "</div>")
        st.write("")
        etiquetas = {f["nombre"]: tr(f.get("etiqueta", f["nombre"]))
                     for f in reg["features"]}
        grafico(graficos.barras_importancia(
            imp["variables"], imp["media"], imp["desviacion"], T(),
            unidad=L("aumento del MAE al permutar (S/)",
                     "MAE increase when shuffled (S/)"),
            etiquetas=etiquetas),
            30 + len(imp["variables"]) * 30 + 18)


# --------------------------------------------------------------------------
# Sección 2: informalidad
# --------------------------------------------------------------------------
def seccion_informalidad(schema: dict, art: dict) -> None:
    clas = schema["clasificador"]

    cabecera(
        L("¿Qué tan probable es que un empleo como este sea informal?",
          "How likely is a job like this to be informal?"),
        L("Informal según el INEI: independiente sin RUC o dependiente sin "
          "aporte a pensión. El modelo estima esa probabilidad para el perfil "
          "que armes. Señala configuraciones de empleo, no personas.",
          "Informal under INEI's rule: self-employed without a tax ID (RUC), "
          "or an employee with no pension contributions. The model scores "
          "the profile you build. It flags job configurations, not people."),
        f"{tr(clas['descripcion_target'])} {tr(clas.get('encuadre', ''))}<br><br>"
        + L("La regla se derivó de dos preguntas de la encuesta: a los "
            "independientes y empleadores se les pregunta si tienen RUC "
            "(registro tributario); a los dependientes, si les aportan a un "
            "sistema de pensiones. La derivación se validó contra la tasa "
            "oficial: reconstruida sobre todos los ocupados da 67,3 % frente "
            "al 70,2 % que publica el INEI para 2025.",
            "The rule was derived from two survey questions: the "
            "self-employed and employers are asked whether they have a RUC "
            "(tax registration); employees, whether anyone contributes to a "
            "pension scheme for them. The derivation was validated against "
            "the official rate: rebuilt over all employed people it gives "
            "67.3% vs. the 70.2% INEI publishes for 2025.")
        + ref("inei_informal"),
        seccion=L("informalidad", "informality"),
        eyebrow=L("Clasificación · Gradient Boosting",
                  "Classification · Gradient Boosting"))

    _informalidad_en_vivo(schema, art)


@st.fragment
def _informalidad_en_vivo(schema: dict, art: dict) -> None:
    """
    El perfil, su probabilidad, el umbral y las curvas que marcan el valor del
    perfil: todo lo que un slider cambia, en un fragment. `bloque_umbral` es
    un fragment anidado: mover la vara no vuelve a predecir.
    """
    clas = schema["clasificador"]
    a = art.get("clasificador", {})
    with st.container(border=True, key="caja_form_clf"):
        selector_perfiles("clf", clas["features"])
        fila = formulario(clas["features"], "clf", rejilla=True)
    modelo = cargar_modelo("clasificador_gb.joblib")
    st.session_state["proba_informal"] = float(
        modelo.predict_proba(fila[columnas_esperadas(modelo)])[:, 1][0])

    if a.get("curva_umbral"):
        bloque_umbral(clas, a["curva_umbral"])
    else:
        aviso(L("Falta <code>models/ui_artifacts.json</code>. Corre "
                "<code>python src/09_precomputar_ui.py</code>.",
                "<code>models/ui_artifacts.json</code> is missing. Run "
                "<code>python src/09_precomputar_ui.py</code>."))

    if a.get("dependencia_parcial"):
        st.divider()
        html("<h2>" + L("Qué empuja la probabilidad hacia arriba o hacia abajo",
                        "What pushes the probability up or down") + "</h2>")
        html("<div class='entradilla'>" + L(
            "Cada gráfico responde: si solo cambiara esta característica y "
            "todo lo demás se quedara igual, ¿cómo se movería la probabilidad? "
            "En cada uno, el color marca el valor del perfil que armaste. Su "
            "nombre técnico es <b>dependencia parcial</b>.",
            "Each chart answers: if only this characteristic changed and "
            "everything else stayed the same, how would the probability move? "
            "In each one, color marks your profile's value. The technical "
            "name is <b>partial dependence</b>.") + "</div>")
        with st.expander(L("Detalle técnico", "Technical detail")):
            html("<div class='sutil'>" + L(
                "Son curvas de <b>dependencia parcial</b>: el modelo predice "
                "sobre toda la muestra fijando esta variable en cada valor "
                "posible y promediando el resto, lo que aísla su efecto "
                "marginal. <b>No son tasas observadas:</b> la tasa real de "
                "informalidad en un grupo mezcla el efecto de esta variable "
                "con el de todas las que la acompañan. Por eso el efecto "
                "parcial de «Rural» y el porcentaje real de informalidad rural "
                "no son el mismo número, y no deberían serlo.",
                "These are <b>partial dependence</b> curves: the model "
                "predicts over the whole sample with this feature fixed at "
                "each possible value, averaging over the rest, which isolates "
                "its marginal effect. <b>They are not observed rates:</b> the "
                "actual informality rate of a group mixes this feature's "
                "effect with that of everything that travels with it. That's "
                "why the partial effect of “Rural” and the actual rural "
                "informality rate are not the same number — and shouldn't "
                "be.") + "</div>")
        st.write("")
        valores = st.session_state.get("valores_clf", {})
        tasas = a.get("tasas_observadas", {})
        cols = st.columns(2, gap="medium")
        j = 0
        for feat in clas["features"]:
            nombre = feat["nombre"]
            perfil = a["dependencia_parcial"].get(nombre)
            if not perfil or nombre in DERIVADAS:
                continue
            etiqueta = tr(feat.get("etiqueta", nombre))
            with cols[j % 2]:
                html(f"<div class='titulo-grafico'>"
                     f"{titulo_oracion(nombre, etiqueta, tasas)}</div>")
                grafico(graficos.dependencia_parcial(
                    perfil["valores"], perfil["efecto"], perfil["tipo"],
                    etiqueta, T(), marca=valores.get(nombre),
                    formato_y="prob", mostrar_etiqueta=False), 210)
                v = valores.get(nombre)
                if v is not None:
                    # En las numéricas «este caso» es una línea vertical, no una
                    # barra: la frase tiene que decir lo que se ve.
                    if perfil["tipo"] == "numerico":
                        html("<div class='sutil'>" + L(
                            f"La línea punteada marca <b>{n(float(v))}</b>, "
                            f"el valor de tu perfil.",
                            f"The dashed line marks <b>{n(float(v))}</b>, "
                            f"your profile's value.") + "</div>")
                    else:
                        html("<div class='sutil'>" + L(
                            f"La barra en color es «{tr(v)}», el valor de tu "
                            f"perfil. Pasa el cursor por cualquier barra para "
                            f"ver su cifra.",
                            f"The colored bar is “{tr(v)}”, your profile's "
                            f"value. Hover over any bar to see its "
                            f"number.") + "</div>")
                t = tasas.get(nombre)
                if t:
                    dato = L(f"en la muestra, {pc(t['max']['pct_ponderado'])} "
                             f"de «{tr(t['max']['categoria'])}» tiene empleo "
                             f"informal, frente a "
                             f"{pc(t['min']['pct_ponderado'])} de "
                             f"«{tr(t['min']['categoria'])}».",
                             f"in the sample, {pc(t['max']['pct_ponderado'])} "
                             f"of “{tr(t['max']['categoria'])}” hold informal "
                             f"jobs, vs. {pc(t['min']['pct_ponderado'])} of "
                             f"“{tr(t['min']['categoria'])}”.")
                elif perfil["tipo"] == "numerico" and len(perfil["efecto"]) > 1:
                    # Sin categorías que contrastar, el dato es la tendencia:
                    # de dónde a dónde se mueve la probabilidad de punta a punta.
                    ini, fin = perfil["efecto"][0], perfil["efecto"][-1]
                    v0, v1 = perfil["valores"][0], perfil["valores"][-1]
                    dato = L(f"al pasar de {n(float(v0))} a {n(float(v1))}, "
                             f"la probabilidad estimada "
                             f"{'baja' if fin < ini else 'sube'} de "
                             f"{pc(ini * 100)} a {pc(fin * 100)}.",
                             f"going from {n(float(v0))} to {n(float(v1))}, "
                             f"the estimated probability "
                             f"{'falls' if fin < ini else 'rises'} from "
                             f"{pc(ini * 100)} to {pc(fin * 100)}.")
                else:
                    dato = ""
                if dato:
                    html(porque(nombre, dato))
                st.write("")
            j += 1


# --------------------------------------------------------------------------
# Sección 3: torneo de modelos (la exposición hecha interfaz)
# --------------------------------------------------------------------------
def _ecuacion(coefs: dict, titulo: str) -> str:
    orden = ["const", "urbano", "hombre", "edad", "primaria", "secundaria",
             "tecnica", "universitaria", "horas", "miembros"]
    nombres = {"urbano": L("urbano", "urban"), "hombre": L("hombre", "male"),
               "edad": L("edad", "age"), "primaria": L("primaria", "primary"),
               "secundaria": L("secundaria", "secondary"),
               "tecnica": L("tecnica", "technical"),
               "universitaria": L("universitaria", "university"),
               "horas": L("horas", "hours"),
               "miembros": L("miembros", "hh_members")}
    lineas = [f"{L('INGRESO', 'INCOME')} = {n(coefs.get('const', 0), 2)}"]
    for k in orden[1:]:
        if k in coefs:
            v = coefs[k]
            lineas.append(f"  {'+' if v >= 0 else '−'} {n(abs(v), 2)} · "
                          f"{nombres[k]}")
    return f"<div class='eyebrow'>{titulo}</div><div class='ecuacion'>" + \
           "\n".join(lineas) + "</div>"


def _acto_ecuacion_inicial(aut: dict) -> None:
    """Acto 1 del torneo: la ecuación del curso, sucia y limpia."""
    html("<div class='entradilla'>" + L(
        "Cada línea suma o resta soles al ingreso estimado. Por ejemplo, "
        "«+ 11,47 · urbano» significa: si la persona vive en zona urbana, "
        "súmale S/ 11,47 al total.",
        "Each line adds or subtracts soles from the estimated income. For "
        "example, “+ 11.47 · urban” means: if the person lives in an urban "
        "area, add S/ 11.47 to the total.") + "</div>")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        html(_ecuacion(aut["ecuacion_inicial"],
                       L("Versión inicial (con el centinela sin limpiar)",
                         "Initial version (sentinel not cleaned)")))
        html("<div class='sutil' style='margin-top:8px'>" + L(
            "+11 soles por residir en zona urbana y +6 por ser hombre: "
            "incompatible con las brechas conocidas del mercado laboral "
            "peruano. <b>El problema no estaba en cómo se modeló, sino en los "
            "datos.</b> El INEI codifica «no sabe» como 999999, y ese código "
            "se estaba leyendo como un ingreso real de 999.999 soles. Unos "
            "pocos registros así deforman cualquier regresión, la haga quien "
            "la haga. Encontrarlo no fue suerte: salió de revisar si los "
            "coeficientes tenían sentido económico, que es exactamente lo que "
            "hay que hacer antes de dar un modelo por bueno.",
            "+11 soles for living in an urban area and +6 for being male: "
            "incompatible with the well-known gaps in Peru's labor market. "
            "<b>The problem wasn't the modeling — it was the data.</b> INEI "
            "codes “don't know” as 999999, and that code was being read as a "
            "real income of 999,999 soles. A handful of records like that "
            "will warp any regression, whoever runs it. Finding it wasn't "
            "luck: it came from checking whether the coefficients made "
            "economic sense, which is exactly what you should do before "
            "trusting a model.") + "</div>")
    with c2:
        html(_ecuacion(aut["corrida_limpia"]["coefs"],
                       L("Misma especificación, centinela 999999 → NaN",
                         "Same specification, sentinel 999999 → NaN")))
        html("<div class='sutil' style='margin-top:8px'>" + L(
            f"Con solo convertir el código de faltante del INEI a NaN, el R² "
            f"pasa de <b>{d(aut['corrida_sucia']['r2'], 3)}</b> a "
            f"<b>{d(aut['corrida_limpia']['r2'], 3)}</b> y todos los signos se "
            f"vuelven económicamente plausibles.",
            f"Just converting INEI's missing-value code to NaN takes R² from "
            f"<b>{d(aut['corrida_sucia']['r2'], 3)}</b> to "
            f"<b>{d(aut['corrida_limpia']['r2'], 3)}</b>, and every sign "
            f"becomes economically plausible.") + "</div>")


def _acto_diagnostico(aut: dict) -> None:
    """Acto 2 del torneo: centinela, colinealidad y escala."""
    html(f"<div class='panel'><div style='line-height:1.8;font-size:14px;color:"
         f"{T()['texto']}'>" + L(
             f"<b>1 · El centinela.</b> El {pc(aut['pct_centinelas'], 2)} de "
             f"la población tenía el código 999999 («no sabe») leído como "
             f"ingreso real de un millón de soles. R² sucio: "
             f"{d(aut['corrida_sucia']['r2'], 3)}; limpio: "
             f"{d(aut['corrida_limpia']['r2'], 3)}.<br>"
             f"<b>2 · La colinealidad (dos variables que dicen lo mismo).</b> "
             f"Años de educación y nivel educativo detallado son la misma "
             f"variable codificada dos veces: juntos disparan el VIF a ~20 y "
             f"voltean signos. No conviven en ninguna especificación del "
             f"torneo.<br>"
             f"<b>3 · La escala.</b> El ingreso limpio tiene asimetría "
             f"{d(aut['asimetria_limpia'], 2)}: en niveles, unos pocos sueldos "
             f"altos dominan la regresión. La familia principal trabaja en log "
             f"(ecuación de Mincer) y vuelve a soles con la corrección de "
             f"Duan.",
             f"<b>1 · The sentinel.</b> {pc(aut['pct_centinelas'], 2)} of the "
             f"population had the 999999 code (“don't know”) read as a real "
             f"income of a million soles. Dirty R²: "
             f"{d(aut['corrida_sucia']['r2'], 3)}; clean: "
             f"{d(aut['corrida_limpia']['r2'], 3)}.<br>"
             f"<b>2 · Collinearity (two features saying the same thing).</b> "
             f"Years of schooling and detailed education level are the same "
             f"variable encoded twice: together they push the VIF to ~20 and "
             f"flip signs. They never share a specification in the "
             f"tournament.<br>"
             f"<b>3 · Scale.</b> Clean income has a skewness of "
             f"{d(aut['asimetria_limpia'], 2)}: in levels, a few high "
             f"paychecks dominate the regression. The main family works in "
             f"logs (the Mincer equation) and returns to soles with Duan's "
             f"correction.")
         + "</div></div>")


def _acto_torneo(t: dict) -> None:
    """Acto 3 del torneo: la tabla completa de las especificaciones."""
    filas = ""
    for f in t["tabla"]:
        clase = " class='destacada'" if f["ID"] == t["desplegada"] else ""
        marca = (L(" · desplegada", " · deployed") if f["ID"] == t["desplegada"]
                 else L(" · explicativa", " · explanatory")
                 if f["ID"] == t["explicativa"] else "")
        filas += (f"<tr{clase}><td>{f['ID']}{marca}</td>"
                  f"<td style='text-align:left'>{tr(f['especificacion'])}</td>"
                  f"<td>{n(f['MAE_cv'])}</td><td>{n(f['MAE_test'])}</td>"
                  f"<td>{d(f['R2_test_soles'], 3)}</td>"
                  f"<td>{tr(f['interpretabilidad'])}</td></tr>")
    html(f"<div class='tabla-envoltura'><table class='tabla'><thead><tr><th>ID</th>"
         f"<th class='izq'>{L('Especificación', 'Specification')}</th>"
         f"<th>MAE cv (S/)</th><th>MAE test (S/)</th>"
         f"<th>{L('R² soles', 'R² (soles)')}</th>"
         f"<th>{L('Interpretab.', 'Interpretab.')}</th></tr></thead>"
         f"<tbody>{filas}</tbody></table></div>")
    html("<div class='sutil' style='margin-top:10px;max-width:78ch'>" + L(
        "La selección usa el MAE de validación cruzada en train — elegir por "
        "test tras comparar nueve especificaciones sería seleccionar sobre el "
        "conjunto de evaluación. El MAE de test se reporta como estimación "
        "honesta del modelo ya elegido.",
        "Selection uses the cross-validated MAE on the training set — "
        "choosing by test after comparing nine specifications would mean "
        "selecting on the evaluation set. Test MAE is reported as an honest "
        "estimate of the already-chosen model.") + "</div>")


def seccion_torneo(schema: dict, art: dict) -> None:
    t = art.get("torneo")
    if not t:
        aviso(L("Falta el bloque torneo en <code>ui_artifacts.json</code>.",
                "The tournament block is missing from "
                "<code>ui_artifacts.json</code>."))
        return
    aut = t["autopsia"]

    cabecera(
        L("¿Por qué este modelo y no otro?", "Why this model and not another?"),
        L("Nueve maneras de armar el mismo modelo de <b>ingreso</b> compitieron "
          "con reglas idénticas. Gana la que se equivoca menos en soles con "
          "datos que no vio. El clasificador de informalidad no compite aquí: "
          "su comparación está en la Ficha técnica.",
          "Nine ways of building the same <b>income</b> model competed under "
          "identical rules. The winner is whichever misses by the fewest soles "
          "on data it hasn't seen. The informality classifier doesn't compete "
          "here: its comparison lives in the Model card."),
        L("Las nueve especificaciones comparten muestra, partición "
          "entrenamiento/prueba y los mismos cinco pliegues de validación "
          "cruzada, con semilla fija. Sin eso el ranking no sería comparable. "
          "La selección se hace por el error de validación cruzada y no por "
          "el de prueba: elegir por prueba tras comparar nueve candidatos "
          "sería seleccionar sobre el conjunto con el que luego se dice ser "
          "honesto.",
          "All nine specifications share the sample, the train/test split and "
          "the same five cross-validation folds, with a fixed seed. Without "
          "that the ranking wouldn't be comparable. Selection uses the "
          "cross-validation error, not the test error: picking by test after "
          "comparing nine candidates would mean selecting on the very set "
          "you later claim keeps you honest."),
        seccion=L("torneo", "tournament"),
        eyebrow=L("Selección de modelo · 9 especificaciones",
                  "Model selection · 9 specifications"))

    # ---- De un vistazo: barras + tres cifras + una frase ----
    orden = sorted(t["tabla"], key=lambda f: f["MAE_cv"])
    gan = next(f for f in t["tabla"] if f["ID"] == t["desplegada"])
    # "lineal" = lo que la propia tabla no marca con interpretabilidad "baja"
    # (las ecuaciones OLS; los árboles son "baja"): el criterio lo pone el
    # artefacto, no una lista escrita aquí
    interp = min((f for f in t["tabla"] if f["interpretabilidad"] != "baja"),
                 key=lambda f: f["MAE_cv"])
    mejora = (interp["MAE_cv"] - gan["MAE_cv"]) / interp["MAE_cv"] * 100
    col_v, col_c = st.columns([60, 40], gap="large")
    with col_v:
        grafico(graficos.barras_mae([f["ID"] for f in orden],
                                    [f["MAE_cv"] for f in orden],
                                    t["desplegada"], T()),
                28 + len(orden) * 32 + 30, vistazo=True)
    with col_c:
        vistazo_resumen(
            [(f"S/ {n(gan['MAE_cv'])}",
              L(f"error medio de {gan['ID']}, la ganadora (validación cruzada)",
                f"mean error of {gan['ID']}, the winner (cross-validation)")),
             (f"−{pc(mejora, 1)}",
              L(f"frente a la mejor ecuación lineal ({interp['ID']})",
                f"vs. the best linear equation ({interp['ID']})")),
             (str(len(t["tabla"])),
              L("especificaciones con la misma muestra y los mismos pliegues",
                "specifications on the same sample and the same folds"))],
            L(f"El Gradient Boosting ({gan['ID']}) predice mejor; la ecuación "
              f"{t['explicativa']} se queda para explicar qué pesa y cuánto.",
              f"Gradient Boosting ({gan['ID']}) predicts better; equation "
              f"{t['explicativa']} stays on to explain what matters and how "
              f"much."))

    acto1, acto2, acto3 = st.tabs([
        L("Acto 1 · La ecuación inicial", "Act 1 · The initial equation"),
        L("Acto 2 · El diagnóstico", "Act 2 · The diagnosis"),
        L("Acto 3 · El torneo", "Act 3 · The tournament")])

    with acto1:
        _acto_ecuacion_inicial(aut)
    with acto2:
        _acto_diagnostico(aut)
    with acto3:
        _acto_torneo(t)

    # ---- Qué variable entra dónde y cuánto pesa ----
    vb = t.get("variables")
    if vb:
        html("<h2>" + L("Qué variable entra dónde y cuánto pesa",
                        "Which feature goes where, and how much it weighs")
             + "</h2>")
        col_m, col_i = st.columns([54, 46], gap="large")
        with col_m:
            m = vb["matriz"]
            cab = "".join(
                f"<th style='text-align:center'>{e}"
                f"{' ★' if e == t['desplegada'] else ''}</th>"
                for e in m["especificaciones"])
            filas = ""
            for f in m["filas"]:
                celdas = ""
                for e in m["especificaciones"]:
                    entra = f["entra"].get(e, False)
                    destacada = entra and e == t["desplegada"]
                    color = (T()["acento_alto"] if destacada
                             else T()["texto"] if entra else T()["texto_tenue"])
                    celdas += (f"<td style='text-align:center;color:{color}'>"
                               f"{'●' if entra else '·'}</td>")
                filas += (f"<tr><td style='text-align:left'>{tr(f['etiqueta'])}"
                          f"</td>{celdas}</tr>")
            html(f"<div class='tabla-envoltura'><table class='tabla'><thead><tr>"
                 f"<th>{L('Variable', 'Feature')}</th>{cab}"
                 f"</tr></thead><tbody>{filas}</tbody></table></div>")
            html(f"<div class='sutil' style='margin-top:8px'>"
                 f"{tr(vb['nota_matriz'])}</div>")
        with col_i:
            imp = art.get("regresor", {}).get("importancia_permutacion")
            if imp:
                html(f"<div class='eyebrow'>"
                     + L(f"Peso en {t['desplegada']} · importancia por "
                         f"permutación",
                         f"Weight in {t['desplegada']} · permutation "
                         f"importance") + "</div>")
                st.write("")
                etiquetas = {f["nombre"]: tr(f.get("etiqueta", f["nombre"]))
                             for f in schema["regresor"]["features"]}
                # versiones cortas: esta columna es más angosta que la de ingreso
                etiquetas |= {"horas_total": L("Horas semanales", "Weekly hours"),
                              "exper2": L("Experiencia²", "Experience²")}
                grafico(graficos.barras_importancia(
                    imp["variables"], imp["media"], imp["desviacion"], T(),
                    unidad=L("aumento del MAE al permutar (S/)",
                             "MAE increase when shuffled (S/)"),
                    etiquetas=etiquetas),
                    30 + len(imp["variables"]) * 30 + 18)
                html("<div class='sutil'>" + L(
                    "La matriz dice quién entra; estas barras dicen cuánto "
                    "pesa en el modelo desplegado (precomputado en "
                    "models/ui_artifacts.json).",
                    "The matrix says who gets in; these bars say how much "
                    "each one weighs in the deployed model (precomputed in "
                    "models/ui_artifacts.json).") + "</div>")

        l7 = vb.get("lasso_e7")
        if l7:
            html("<h3>" + L("Qué variables sobran: lo que descartó el Lasso en E7",
                            "Which features are redundant: what the Lasso "
                            "dropped in E7") + "</h3>")
            html("<div class='sutil' style='max-width:78ch'>" + L(
                "El <b>Lasso</b> es un método que penaliza tener muchas "
                "variables: deja en cero las que no aportan lo suficiente y "
                "así elige solas cuáles se quedan. Una <b>dummy</b> es una "
                "columna de sí/no que representa una categoría (por ejemplo, "
                "«trabaja en el sector X»).",
                "The <b>Lasso</b> is a method that penalizes having many "
                "features: it shrinks the ones that don't contribute enough "
                "to zero, so it picks on its own which ones stay. A "
                "<b>dummy</b> is a yes/no column representing one category "
                "(e.g., “works in industry X”).") + "</div>")
            drop_manual = set(l7.get("drop_manual_e6", []))
            eliminadas = l7["eliminadas"]
            coincide = sorted(drop_manual & set(eliminadas))
            extras = [e for e in eliminadas if e not in drop_manual]
            lista = ", ".join(f"<code>{e}</code>" for e in eliminadas)
            partes = [L(
                f"De <b>{l7['candidatas']}</b> columnas candidatas, el Lasso "
                f"(α = {d(l7['alpha'], 5)}) conservó <b>{l7['conservadas']}</b> "
                f"y eliminó {len(eliminadas)}: {lista} ({l7.get('fuente', '')}).",
                f"Out of <b>{l7['candidatas']}</b> candidate columns, the "
                f"Lasso (α = {d(l7['alpha'], 5)}) kept "
                f"<b>{l7['conservadas']}</b> and dropped {len(eliminadas)}: "
                f"{lista} ({l7.get('fuente', '')}).")]
            if coincide:
                cod = ", ".join(f"<code>{c}</code>" for c in coincide)
                partes.append(L(
                    f"La selección automática <b>confirmó la depuración manual "
                    f"de E6</b>: eliminó {cod}, la misma dummy que E6 suelta a "
                    f"mano por colinealidad perfecta con categoría=Trabajador "
                    f"del hogar.",
                    f"The automatic selection <b>confirmed E6's manual "
                    f"pruning</b>: it dropped {cod}, the same dummy E6 removes "
                    f"by hand for perfect collinearity with "
                    f"category=Domestic worker."))
            if extras:
                cod = ", ".join(f"<code>{e}</code>" for e in extras)
                partes.append(L(
                    f"Donde discrepa: además descartó {cod}, dummies de "
                    f"categorías con poca masa muestral que E6 conserva — la "
                    f"penalización del Lasso castiga a los grupos chicos, no "
                    f"necesariamente a los irrelevantes (la cautela de "
                    f"Belloni et al. 2014 que el reporte declara).",
                    f"Where it disagrees: it also dropped {cod}, dummies for "
                    f"thinly populated categories that E6 keeps — the Lasso "
                    f"penalty punishes small groups, not necessarily "
                    f"irrelevant ones (the caveat from Belloni et al. 2014 "
                    f"that the report states)."))
            html(f"<div class='panel'><div style='font-size:14px;"
                 f"line-height:1.75;color:{T()['texto']}'>"
                 + " ".join(partes) + "</div></div>")

        desc = vb.get("descartadas")
        if desc:
            html("<h3>" + L("Variables descartadas y por qué",
                            "Excluded variables and why") + "</h3>")
            filas = "".join(
                f"<tr><td style='text-align:left'>{tr(x['nombre'])}</td>"
                f"<td style='text-align:left'>{tr(x['motivo'])}</td>"
                f"<td style='text-align:left'>"
                f"{enlace_evidencia(x['evidencia'])}</td></tr>" for x in desc)
            html(f"<div class='tabla-envoltura'><table class='tabla'><thead><tr>"
                 f"<th>{L('Variable', 'Variable')}</th>"
                 f"<th class='izq'>{L('Motivo', 'Reason')}</th>"
                 f"<th class='izq'>{L('Evidencia', 'Evidence')}</th></tr></thead>"
                 f"<tbody>{filas}</tbody></table></div>")

    e6 = t["explicativo_e6_ponderado"]["efectos_pct"]

    def sig(k: str) -> str:
        v = e6.get(k, 0)
        return ("+" if v >= 0 else "−") + pc(abs(v), 1)

    html("<h2>" + L("Las dos lecturas finales", "The two final readings") + "</h2>")
    html(f"<div class='panel'><div style='line-height:1.8;font-size:14px;color:"
         f"{T()['texto']}'>" + L(
             f"<b>La predictiva (E9, desplegada):</b> Gradient Boosting sobre "
             f"log del ingreso. La brecha frente a la mejor OLS estima lo que "
             f"aportan las no linealidades e interacciones que la forma lineal "
             f"no captura."
             f"<br><b>La explicativa (E6, ponderada a población):</b> cada año "
             f"de educación se asocia a <b>{sig('anios_educ')}</b> de ingreso; "
             f"ser hombre, <b>{sig('hombre')}</b>; residir en zona urbana, "
             f"<b>{sig('urbano')}</b>; trabajar como independiente, "
             f"<b>{sig('categoria_Independiente')}</b>; una empresa de hasta "
             f"20 personas frente a una de más de 500, "
             f"<b>{sig('tamano_empresa_Hasta 20')}</b>; Sierra Norte frente a "
             f"Lima Metropolitana, <b>{sig('dominio_Sierra Norte')}</b>.",
             f"<b>The predictive one (E9, deployed):</b> Gradient Boosting on "
             f"log income. Its gap over the best OLS estimates what the "
             f"non-linearities and interactions a linear form can't capture "
             f"are worth."
             f"<br><b>The explanatory one (E6, population-weighted):</b> each "
             f"extra year of schooling is associated with "
             f"<b>{sig('anios_educ')}</b> income; being male, "
             f"<b>{sig('hombre')}</b>; living in an urban area, "
             f"<b>{sig('urbano')}</b>; working self-employed, "
             f"<b>{sig('categoria_Independiente')}</b>; a firm of up to 20 "
             f"people vs. one with over 500, "
             f"<b>{sig('tamano_empresa_Hasta 20')}</b>; the Northern Highlands "
             f"vs. Metropolitan Lima, <b>{sig('dominio_Sierra Norte')}</b>.")
         + "</div></div>")

    sens = t.get("sensibilidad_especie", [])
    if len(sens) == 2:
        html("<h2>" + L("Robustez: ¿y el ingreso en especie?",
                        "Robustness: what about in-kind income?") + "</h2>")
        html("<div class='sutil' style='max-width:78ch'>" + L(
            f"El 24,6 % de los ocupados recibe pago en especie o autoconsumo "
            f"(concentrado en el agro rural). Si excluirlo sesgara el premio "
            f"urbano, la narrativa entera quedaría en duda — así que se midió: "
            f"con target solo monetario el premio urbano es "
            f"<b>{pc(sens[0]['premio_urbano_pct'], 1)}</b>; añadiendo especie, "
            f"<b>{pc(sens[1]['premio_urbano_pct'], 1)}</b>. La exclusión queda "
            f"validada como robusta y declarada.",
            f"24.6% of workers receive in-kind pay or own consumption "
            f"(concentrated in rural farming). If excluding it biased the "
            f"urban premium, the whole story would be in doubt — so it was "
            f"measured: with a cash-only target the urban premium is "
            f"<b>{pc(sens[0]['premio_urbano_pct'], 1)}</b>; adding in-kind, "
            f"<b>{pc(sens[1]['premio_urbano_pct'], 1)}</b>. The exclusion is "
            f"validated as robust and stated up front.") + "</div>")


# --------------------------------------------------------------------------
# Sección 4: ficha técnica
# --------------------------------------------------------------------------
# Hallazgos de la auditoría interna. Resumen de INFORME_AUDITORIA.md: se
# escriben aquí a mano y a propósito, porque son juicios sobre el proyecto, no
# métricas que se puedan recalcular. La cifra de cada uno sí sale del informe.
#
# `origen` dice DÓNDE NACIÓ el problema, que es distinto de en qué estado
# está. Un fallo de la fuente y uno propio se corrigen igual pero no enseñan
# lo mismo.
def origenes() -> dict[str, tuple[str, str, str]]:
    return {
        "datos": ("origen-datos", L("datos de origen", "source data"),
                  L("el problema venía en la fuente (INEI) y afectaría a "
                    "cualquiera que use estos datos. Ej.: el centinela 999999.",
                    "the problem came with the source (INEI) and would affect "
                    "anyone using these data. E.g., the 999999 sentinel.")),
        "propia": ("origen-propia", L("decisión propia", "our own decision"),
                   L("lo introdujimos nosotros al elegir o resumir. Ej.: la "
                     "rejilla acotada, el 88,6 % mal etiquetado, las tres "
                     "afirmaciones contradictorias del R².",
                     "we introduced it ourselves when choosing or "
                     "summarizing. E.g., the bounded grid, the mislabeled "
                     "88.6%, the three contradictory R² claims.")),
        "doc": ("origen-doc", L("documentación", "documentation"),
                L("citas que no decían lo que se les atribuía. Ej.: Lemieux y "
                  "Heckman sin R² reportado.",
                  "citations that didn't say what was attributed to them. "
                  "E.g., Lemieux and Heckman, who report no R².")),
    }


def auditoria() -> list[dict]:
    return [
        {"sev": "corregido", "origen": ["datos"],
         "titulo": L("El código de faltante leído como un ingreso",
                     "The missing-value code read as an income"),
         "texto": L("El INEI codifica «no sabe» como 999999. Ese valor se "
                    "estaba leyendo como un ingreso real de 999.999 soles, y "
                    "con él la regresión daba +11 soles por vivir en zona "
                    "urbana. Convertirlo a dato faltante subió el R² de 0,023 "
                    "a 0,248 y devolvió el sentido económico a todos los "
                    "coeficientes.",
                    "INEI codes “don't know” as 999999. That value was being "
                    "read as a real income of 999,999 soles, and with it the "
                    "regression gave +11 soles for living in an urban area. "
                    "Turning it into a missing value lifted R² from 0.023 to "
                    "0.248 and restored economic sense to every "
                    "coefficient.")},
        {"sev": "a corregir", "origen": ["propia"],
         "titulo": L("La rejilla de hiperparámetros estaba acotada",
                     "The hyperparameter grid was too narrow"),
         "texto": L("Los tres hiperparámetros del modelo desplegado quedaron "
                    "en el borde de los valores que se probaron: señal de que "
                    "el óptimo estaba fuera. Se amplió y se volvió a buscar: "
                    "el error baja de S/ 610,90 a S/ 607,31 y los tres quedan "
                    "ya en el interior. La mejora es sistemática (gana en los "
                    "5 pliegues) pero de 0,59 %, así que NO se promovió: no "
                    "justifica regenerar el modelo en producción. Las "
                    "rejillas del clasificador siguen sin revisar.",
                    "All three hyperparameters of the deployed model landed on "
                    "the edge of the values tried — a sign the optimum lay "
                    "outside. The grid was widened and searched again: error "
                    "drops from S/ 610.90 to S/ 607.31 and all three now sit "
                    "inside. The gain is systematic (it wins on all 5 folds) "
                    "but only 0.59%, so it was NOT promoted: it doesn't "
                    "justify regenerating the production model. The "
                    "classifier's grids are still unreviewed.")},
        {"sev": "corregido", "origen": ["propia"],
         "titulo": L("Una cifra del INEI con la etiqueta equivocada",
                     "An INEI figure with the wrong label"),
         "texto": L("Se publicaba que el gradiente por tamaño de empresa "
                    "«replica el patrón oficial (88,6 % en microempresas)». "
                    "Ese 88,6 % es del INEI y corresponde al tramo de 1 a 10 "
                    "trabajadores, que no es la categoría «Hasta 20» de este "
                    "proyecto — cuyo valor propio es 81,1 %. No era un dato "
                    "inventado, era una comparación mal etiquetada.",
                    "We stated that the firm-size gradient “replicates the "
                    "official pattern (88.6% in micro-enterprises)”. That "
                    "88.6% is INEI's and refers to the 1–10 workers band, "
                    "which is not this project's “Up to 20” category — whose "
                    "own value is 81.1%. Not a made-up number: a mislabeled "
                    "comparison.")},
        {"sev": "corregido", "origen": ["propia", "doc"],
         "titulo": L("Tres afirmaciones distintas sobre el mismo dato",
                     "Three different claims about the same fact"),
         "texto": L("Sobre el R² esperable circulaban «0,4–0,5», «rara vez "
                    "supera 0,4» y «ningún R² supera 0,5», en cuatro sitios a "
                    "la vez. Al ir a las fuentes resultó que ni Lemieux (2006) "
                    "ni Heckman et al. (2006) reportan un R², así que no se "
                    "les podía citar para eso. Ahora la afirmación se define "
                    "una sola vez, sobre los cuadros de Mincer y Card, y se "
                    "dice cuál es lectura propia.",
                    "Three versions of the expected R² were circulating — "
                    "“0.4–0.5”, “rarely above 0.4” and “no R² exceeds 0.5” — "
                    "in four places at once. Going back to the sources showed "
                    "that neither Lemieux (2006) nor Heckman et al. (2006) "
                    "report an R², so they couldn't be cited for it. The "
                    "claim is now defined once, from Mincer's and Card's "
                    "tables, and our own reading is labeled as such.")},
        {"sev": "estructural", "origen": [],
         "titulo": L("La solución, para que no vuelva a pasar",
                     "The fix, so it doesn't happen again"),
         "texto": L("Los dos primeros problemas tenían la misma raíz: cifras "
                    "escritas a mano que nadie vuelve a comprobar. Ahora las "
                    "tasas por grupo se calculan en el precómputo "
                    "(`tasas_observadas`) y los títulos de los gráficos se "
                    "generan desde ahí, y la bibliografía vive en un solo "
                    "módulo. Una cifra escrita a mano puede quedar obsoleta en "
                    "silencio; una calculada, no.",
                    "The first two problems shared a root: hand-typed figures "
                    "that nobody re-checks. Group rates are now computed in "
                    "the precompute step (`tasas_observadas`), chart titles "
                    "are generated from them, and the bibliography lives in a "
                    "single module. A hand-typed number can silently go "
                    "stale; a computed one can't.")},
    ]


def seccion_auditoria() -> None:
    """Los hallazgos de auditoría del propio proyecto, publicados."""
    html("<h2>" + L("Qué encontró la auditoría de este proyecto",
                    "What this project's audit found") + "</h2>")
    html("<div class='entradilla'>" + L(
        "Antes de publicar, este proyecto pasó por una revisión de "
        "consistencia: cada cifra se cruzó contra el archivo que la genera, "
        "cada cita contra su fuente original, y cada decisión de modelado "
        "contra su evidencia. Verificar el propio trabajo es parte del método "
        "— lo que no siempre se hace es publicar el resultado. Esto fue lo que "
        "apareció, clasificado según dónde nació cada problema.",
        "Before publishing, this project went through a consistency review: "
        "every figure was checked against the file that produces it, every "
        "citation against its original source, and every modeling decision "
        "against its evidence. Checking your own work is part of the method "
        "— what's less common is publishing the result. Here's what turned "
        "up, grouped by where each problem was born.") + "</div>")
    orig = origenes()
    html("<div class='leyenda-origen'>" + "".join(
        f"<div><span class='origen {clase}'>{etiqueta}</span>"
        f"<span>{glosa}</span></div>"
        for clase, etiqueta, glosa in orig.values()) + "</div>")
    colores = {"corregido": ("ref-abierto", L("corregido", "fixed")),
               "a corregir": ("ref-pago", L("pendiente", "pending")),
               "estructural": ("etiqueta-dato",
                               L("solución de fondo", "root-cause fix"))}
    filas = []
    for h in auditoria():
        clase, etiqueta = colores[h["sev"]]
        origen_html = "".join(
            f"<span class='origen {orig[o][0]}'>{orig[o][1]}</span>"
            for o in h["origen"])
        filas.append(
            f"<div class='hallazgo'>"
            f"<div class='hallazgo-cab'>"
            f"<span class='ref-acceso {clase}'>{etiqueta}</span>{origen_html}"
            f"<b>{h['titulo']}</b></div>"
            f"<div class='sutil'>{h['texto']}</div></div>")
    html(f"<div class='ref-lista'>{''.join(filas)}</div>")
    html("<div class='sutil' style='margin-top:16px'>" + L(
        "El informe completo, con los hallazgos clasificados por severidad y "
        "la lista de lo que quedó sin verificar, está en ",
        "The full report — findings ranked by severity, plus the list of "
        "what remains unverified (in Spanish) — is at ")
        + f"{enlace_evidencia('INFORME_AUDITORIA.md')}"
        + L(" del repositorio.", " in the repository.") + "</div>")
    # La sección cierra con el método, no con el enlace: es la frase que dice
    # por qué los hallazgos siguen publicados en vez de haberse borrado.
    html("<div class='sutil' style='margin-top:12px;max-width:78ch'>" + L(
        "Los problemas de origen se corrigen y se documentan; los propios se "
        "corrigen y se aprende de ellos; los de cita se verifican yendo al "
        "texto completo. Ninguno se borra: un hallazgo corregido en silencio "
        "es un hallazgo desperdiciado.",
        "Source problems get fixed and documented; our own get fixed and "
        "learned from; citation problems get checked against the full text. "
        "None is deleted: a finding fixed in silence is a finding "
        "wasted.") + "</div>")


def _ficha_clasificador(clas: dict, a: dict, abl: list) -> None:
    """Ficha, pestaña 1: comparación de algoritmos, ablación y calibración."""
    filas = ""
    for f in a.get("comparacion", []):
        es_gb = "Gradient" in f["algoritmo"]
        clase = " class='destacada'" if es_gb else " class='atenuada'"
        filas += (f"<tr{clase}><td>{tr(f['algoritmo'])}"
                  f"{L(' · desplegado', ' · deployed') if es_gb else ''}</td>"
                  f"<td>{d(f['PRAUC_cv'], 4)}</td><td>{d(f['PRAUC_test'], 4)}</td>"
                  f"<td>{d(f['ROCAUC_test'], 4)}</td><td>{d(f['Brier_test'], 4)}</td></tr>")
    html(f"<div class='tabla-envoltura'><table class='tabla'><thead><tr>"
         f"<th>{L('Algoritmo', 'Algorithm')}</th><th>PR-AUC cv</th>"
         f"<th>PR-AUC test</th><th>ROC-AUC test</th><th>Brier</th></tr></thead>"
         f"<tbody>{filas}</tbody></table></div>")
    # El gradiente sale de tasas_observadas, no escrito a mano (auditoría
    # 20/08/2026, AC-5): «Hasta 20» no es el tramo 1-10 del INEI.
    tam = a.get("tasas_observadas", {}).get("tamano_empresa")
    gradiente = ""
    if tam:
        gradiente = L(
            f". El gradiente por tamaño de empresa va en el mismo sentido que "
            f"el oficial: aquí {pc(tam['max']['pct_ponderado'], 1)} de "
            f"informalidad en «{tr(tam['max']['categoria'])}» frente a "
            f"{pc(tam['min']['pct_ponderado'], 1)} en "
            f"«{tr(tam['min']['categoria'])}» (ponderado a población, es "
            f"decir, contando a cada encuestado por las personas que "
            f"representa); el INEI reporta 88,6 % en empresas de <b>1 a 10 "
            f"trabajadores</b> y 15,6 % en las de más de 50. Los tramos no son "
            f"los mismos, así que las dos cifras no son directamente "
            f"comparables",
            f". The firm-size gradient points the same way as the official "
            f"one: here {pc(tam['max']['pct_ponderado'], 1)} informality in "
            f"“{tr(tam['max']['categoria'])}” vs. "
            f"{pc(tam['min']['pct_ponderado'], 1)} in "
            f"“{tr(tam['min']['categoria'])}” (population-weighted, i.e. each "
            f"respondent counted by the number of people they represent); "
            f"INEI reports 88.6% in firms of <b>1 to 10 workers</b> and 15.6% "
            f"in those with over 50. The bands differ, so the two figures "
            f"aren't directly comparable")
    html("<div class='sutil' style='margin-top:10px;max-width:78ch'>" + L(
        f"Baseline de PR-AUC = prevalencia ({d(clas['prevalencia_train'], 3)} "
        f"muestral; {d(clas['prevalencia_ponderada'], 3)} ponderada). La regla "
        f"del target se validó contra la tasa oficial: reconstruida sobre "
        f"todos los ocupados da 67,3 % frente al 70,2 % que publica el "
        f"INEI{ref('inei_informal')}{gradiente}. La definición de empleo "
        f"informal que se replica es la internacional de la OIT "
        f"(17.ª CIET){ref('oit_17ciet')}.",
        f"PR-AUC baseline = prevalence ({d(clas['prevalencia_train'], 3)} "
        f"sample; {d(clas['prevalencia_ponderada'], 3)} weighted). The target "
        f"rule was validated against the official rate: rebuilt over all "
        f"employed people it gives 67.3% vs. the 70.2% INEI "
        f"publishes{ref('inei_informal')}{gradiente}. The definition of "
        f"informal employment replicated here is the ILO's international one "
        f"(17th ICLS){ref('oit_17ciet')}.") + "</div>")

    if abl:
        html("<h3>" + L("Ablación estructural", "Structural ablation") + "</h3>")
        filas = ""
        for i, f in enumerate(abl):
            clase = " class='destacada'" if i == 0 else " class='atenuada'"
            filas += (f"<tr{clase}><td>{tr(f['variante'])}</td>"
                      f"<td>{f['n_predictores']}</td><td>{d(f['PRAUC_cv'], 4)}</td>"
                      f"<td>{d(f['ROCAUC_cv'], 4)}</td>"
                      f"<td>{d(f.get('caida_PRAUC_cv', 0), 4)}</td></tr>")
        html(f"<div class='tabla-envoltura'><table class='tabla'><thead><tr>"
             f"<th>{L('Variante', 'Variant')}</th><th>vars</th>"
             f"<th>PR-AUC cv</th><th>ROC-AUC cv</th>"
             f"<th>{L('caída', 'drop')}</th></tr></thead>"
             f"<tbody>{filas}</tbody></table></div>")
        html("<div class='sutil' style='margin-top:10px;max-width:78ch'>" + L(
            "Tamaño de empresa y categoría ocupacional son las variables más "
            "próximas a la definición operativa del target: en microempresas, "
            "no aportar a pensiones es casi estructural. Aun quitando ambas, "
            "el PR-AUC se sostiene en 0,94: educación, área, rama y horas "
            "cargan la señal restante. El clasificador identifica la "
            "<b>configuración laboral</b> asociada a la informalidad — es una "
            "herramienta de focalización, no de predicción a futuro, y por "
            "eso su PR-AUC alto es coherente, no sospechoso.",
            "Firm size and employment category are the features closest to "
            "the target's operational definition: in micro-firms, not "
            "contributing to a pension is almost structural. Even with both "
            "removed, PR-AUC holds at 0.94: schooling, area, industry and "
            "hours carry the remaining signal. The classifier identifies the "
            "<b>job configuration</b> associated with informality — it's a "
            "targeting tool, not a forecast, which is why a high PR-AUC is "
            "consistent here rather than suspicious.") + "</div>")

    if a.get("calibracion"):
        html("<h3>" + L("¿Significan algo las probabilidades?",
                        "Do the probabilities mean anything?") + "</h3>")
        st.write("")
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            grafico(graficos.curva_calibracion(a["calibracion"]["bins"], T()), 330)
        with c2:
            if a.get("roc"):
                grafico(graficos.curva_roc(a["roc"]["fpr"], a["roc"]["tpr"],
                                           a["roc"]["auc"], None, T()), 330)

    pr_auc = a.get("pr", {}).get("auc")
    base = a.get("pr", {}).get("baseline")
    if pr_auc and base:
        abl0 = abl[0]["PRAUC_cv"] if abl else None
        abl2 = abl[-1]["PRAUC_cv"] if abl and len(abl) > 1 else None
        html("<div class='panel' style='margin-top:12px'>"
             + "<div class='panel-titulo'>"
             + L(f"Un {d(pr_auc, 2)} de PR-AUC suele ser señal de fuga. Aquí no "
                 f"lo es, y esta es la razón",
                 f"A {d(pr_auc, 2)} PR-AUC is usually a leakage red flag. Here "
                 f"it isn't — and here's why")
             + "</div><div class='sutil' style='margin-top:8px'>"
             + L(f"<b>Primero, el punto de partida no es cero.</b> Como el "
                 f"{pct(base, 1)} de los trabajadores de la muestra es "
                 f"informal, señalar a todo el mundo al azar ya acertaría "
                 f"{pct(base, 1)} de las veces. Ese es el suelo contra el que "
                 f"hay que leer el {d(pr_auc, 4)}, no el 0,5 de una moneda. Por "
                 f"eso se mira PR-AUC y no solo ROC-AUC: con clases "
                 f"desbalanceadas la curva ROC da una impresión demasiado "
                 f"optimista{ref('saito2015')}.<br><br>"
                 f"<b>Segundo, la relación es casi definicional y está "
                 f"declarada.</b> Tamaño de empresa y categoría ocupacional "
                 f"están muy pegadas a la regla que define el target. Por eso "
                 f"se midió qué pasa sin ellas: "
                 + (f"el PR-AUC baja de {d(abl0, 4)} a {d(abl2, 4)}, se "
                    f"sostiene, y la señal restante la cargan educación, área, "
                    f"rama y horas. " if abl0 and abl2 else "")
                 + "<br><br>"
                 f"<b>Tercero, no predice el futuro.</b> Estima la probabilidad "
                 f"de que un empleo <i>ya existente</i> sea informal a partir "
                 f"de sus características. Es una herramienta de focalización, "
                 f"no un pronóstico, y en ese planteamiento un acierto alto es "
                 f"lo esperable.<br><br>"
                 f"<b>Por contraste: un R² de 0,9 en el regresor de ingreso sí "
                 f"sería sospechoso.</b> El ingreso individual tiene una parte "
                 f"grande e irreducible que ninguna encuesta observa "
                 f"—habilidad, suerte, redes, negociación—. Un ajuste casi "
                 f"perfecto ahí significaría que se coló una variable que "
                 f"contiene al propio ingreso. De hecho pasó una vez en este "
                 f"proyecto, con el «índice de bienestar», y por eso se "
                 f"excluyó.",
                 f"<b>First, the starting point isn't zero.</b> Since "
                 f"{pct(base, 1)} of the workers in the sample are informal, "
                 f"flagging everyone at random would already be right "
                 f"{pct(base, 1)} of the time. That's the floor to read "
                 f"{d(pr_auc, 4)} against — not a coin's 0.5. That's why we "
                 f"look at PR-AUC and not just ROC-AUC: with imbalanced "
                 f"classes the ROC curve looks overly "
                 f"optimistic{ref('saito2015')}.<br><br>"
                 f"<b>Second, the relationship is nearly definitional, and we "
                 f"say so.</b> Firm size and employment category sit very "
                 f"close to the rule that defines the target. So we measured "
                 f"what happens without them: "
                 + (f"PR-AUC goes from {d(abl0, 4)} to {d(abl2, 4)} — it "
                    f"holds, and schooling, area, industry and hours carry "
                    f"the remaining signal. " if abl0 and abl2 else "")
                 + "<br><br>"
                 f"<b>Third, it doesn't predict the future.</b> It estimates "
                 f"the probability that an <i>existing</i> job is informal "
                 f"from its characteristics. It's a targeting tool, not a "
                 f"forecast, and under that framing high accuracy is what "
                 f"you'd expect.<br><br>"
                 f"<b>By contrast: an R² of 0.9 in the income regressor "
                 f"<i>would</i> be suspicious.</b> Individual income has a "
                 f"large, irreducible component no survey observes — skill, "
                 f"luck, networks, bargaining. A near-perfect fit there would "
                 f"mean a variable containing income itself had leaked in. It "
                 f"actually happened once in this project, with the “welfare "
                 f"index”, which is why it was excluded.")
             + "</div></div>")


def _ficha_regresor(reg: dict) -> None:
    """Ficha, pestaña 2: el error del estimador de ingreso, en soles."""
    html("<h2>" + L("¿Cuánto se equivoca el estimador de ingreso?",
                    "How far off is the income estimator?") + "</h2>")
    m = reg["metricas_test"]
    html("<div class='rejilla-tarjetas'>"
         + tarjeta(L("MAE test (mediana)", "test MAE (median)"),
                   f"S/ {n(m['mae_mediana'])}")
         + tarjeta(L("MAE test (media smearing)", "test MAE (smearing mean)"),
                   f"S/ {n(m['mae_media_smear'])}")
         + tarjeta(L("R² en soles", "R² in soles"), f"{d(m['r2_soles'], 3)}",
                   llano=L("El modelo explica esa fracción de la variación "
                           "del ingreso. Ver abajo por qué no es un valor "
                           "bajo.",
                           "The model explains that share of the variation "
                           "in income. See below why that isn't low."))
         + "</div>")

    # Afirmación canónica del R²: definida en app/referencias.py y citada aquí.
    html("<h3>" + L(f"¿Un R² de {d(m['r2_soles'], 2)} no es bajo?",
                    f"Isn't an R² of {d(m['r2_soles'], 2)} low?") + "</h3>")
    html("<div class='sutil' style='max-width:78ch'>"
         + L("<b>No, y conviene decir contra qué se compara.</b> ",
             "<b>No — and it's worth saying what it's compared against.</b> ")
         + referencias.r2_mincer().format(
             ref_mincer=ref("mincer1974"), ref_card=ref("card1999"))
         + "<br><br>" + referencias.r2_advertencia()
         + "<br><br>" + L(
             f"<b>Cuidado al comparar: no todos estos R² miden lo mismo.</b> "
             f"El {d(m['r2_soles'], 2)} de la tarjeta es del modelo desplegado "
             f"(E9) medido <b>en soles</b>. La ecuación de Mincer de este "
             f"mismo torneo (E3) da <b>0,27</b> <b>en logaritmo</b>, que es la "
             f"escala de las cifras de la literatura. Son números de escalas "
             f"distintas: ponerlos uno al lado del otro sin decirlo sería "
             f"comparar cosas diferentes.",
             f"<b>Careful when comparing: not all of these R² measure the same "
             f"thing.</b> The card's {d(m['r2_soles'], 2)} belongs to the "
             f"deployed model (E9), measured <b>in soles</b>. This same "
             f"tournament's Mincer equation (E3) gives <b>0.27</b> <b>in "
             f"logs</b>, which is the scale of the literature's figures. "
             f"They're numbers on different scales: putting them side by side "
             f"without saying so would compare different things.")
         + "</div>")


def _ficha_limites(clas: dict, reg: dict, meta: dict) -> None:
    """Ficha, pestaña 3: limitaciones, procedencia y auditoría."""
    html("<h2>" + L("Limitaciones declaradas", "Stated limitations") + "</h2>")
    lim = [
        L("<b>Ingreso autorreportado y suavizado.</b> El target es la versión "
          "imputada, deflactada y anualizada del INEI dividida entre 12: un "
          "ingreso estabilizado, no el del mes de la entrevista. La validez de "
          "constructo hereda los límites del autorreporte en encuestas de "
          "hogares.",
          "<b>Self-reported, smoothed income.</b> The target is INEI's "
          "imputed, deflated and annualized income divided by 12: a "
          "stabilized income, not the interview month's. Construct validity "
          "inherits the limits of self-reporting in household surveys."),
        L("<b>Solo ingreso monetario.</b> El 24,6 % de los ocupados recibe "
          "pago en especie o autoconsumo, excluido del target. La "
          "sensibilidad medida (sección Torneo) acota el sesgo: el premio "
          "urbano cae 2,6 puntos al incluirlo.",
          "<b>Cash income only.</b> 24.6% of workers receive in-kind pay or "
          "own consumption, excluded from the target. The measured "
          "sensitivity (Tournament section) bounds the bias: the urban "
          "premium drops 2.6 points when it's included."),
        L("<b>Población restringida.</b> Solo ocupados de 14+ con ingreso "
          "laboral positivo: quedan fuera desocupados, inactivos y los 6.500 "
          "trabajadores familiares no remunerados (informales por "
          "definición). La prevalencia del clasificador es por eso menor que "
          "la oficial.",
          "<b>Restricted population.</b> Only employed people aged 14+ with "
          "positive labor income: the unemployed, the inactive and the 6,500 "
          "unpaid family workers (informal by definition) are left out. "
          "That's why the classifier's prevalence is lower than the official "
          "rate."),
        L("<b>Experiencia potencial, no real.</b> Se usa edad − años de "
          "educación − 6 (truncada en 0; 0,2 % de casos negativos). En "
          "trabajadores de baja educación sobreestima la experiencia efectiva "
          "(Heckman, Lochner & Todd, 2006)",
          "<b>Potential, not actual, experience.</b> We use age − years of "
          "schooling − 6 (floored at 0; 0.2% of cases negative). For "
          "low-education workers it overstates actual experience (Heckman, "
          "Lochner & Todd, 2006)") + ref("heckman2006") + ".",
        L("<b>Categoría ocupacional ramifica el target del clasificador.</b> "
          "Su importancia alta es por construcción, no un hallazgo.",
          "<b>Employment category branches the classifier's target.</b> Its "
          "high importance is by construction, not a finding."),
        L("<b>Herramienta demostrativa.</b> Salidas poblacionales para "
          "ordenar perfiles y focalizar gestión; no liquidan sueldos ni "
          "certifican la situación laboral de ninguna persona concreta.",
          "<b>A demonstration tool.</b> Population-level outputs to rank "
          "profiles and target policy; they don't set salaries or certify "
          "any specific person's employment status."),
    ]
    html("<div class='panel'><div class='lista-limites'>"
         + "".join(f"<div>{x}</div>" for x in lim) + "</div></div>")

    html("<h2>" + L("Procedencia", "Provenance") + "</h2>")
    proc = [
        (L("Fuente", "Source"),
         L("INEI — Encuesta Nacional de Hogares (ENAHO) 2025, microdatos "
           "públicos (encuesta 1031)",
           "INEI — National Household Survey (ENAHO) 2025, public microdata "
           "(survey 1031)")),
        (L("Módulos", "Modules"),
         L("02 miembros del hogar · 03 educación · 05 empleo e ingresos",
           "02 household members · 03 education · 05 employment and income")),
        (L("Licencia", "License"),
         L("Microdatos de descarga libre del INEI; no se redistribuyen en el "
           "repositorio",
           "Free-to-download INEI microdata; not redistributed in the "
           "repository")),
        (L("Clasificador", "Classifier"),
         f"{n(clas['n_entrenamiento'])} train / {n(clas['n_test'])} test"),
        (L("Regresor", "Regressor"),
         f"{n(reg['n_entrenamiento'])} train / {n(reg['n_test'])} test"),
        (L("Ponderación", "Weighting"), tr(meta.get("ponderacion", "—"))),
        ("scikit-learn", meta.get("version_scikit_learn", "—")),
        (L("Artefactos de UI", "UI artifacts"), meta.get("fecha_generacion", "—")),
        ("Commit", (meta.get("commit") or "—")[:12]),
    ]
    html("<div class='tabla-envoltura'><table class='tabla'><tbody>"
         + "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in proc)
         + "</tbody></table></div>")

    seccion_auditoria()


def seccion_ficha(schema: dict, art: dict) -> None:
    clas, reg = schema["clasificador"], schema["regresor"]
    a = art.get("clasificador", {})
    meta = art.get("meta", {})

    cabecera(
        L("¿Qué tan fiables son estos dos modelos?",
          "How reliable are these two models?"),
        L("Qué miden, dónde fallan y qué no se puede concluir con ellos. Son "
          "dos modelos distintos y cada uno se juzga con las métricas de su "
          "familia: no se pueden comparar entre sí.",
          "What they measure, where they fail, and what you can't conclude "
          "from them. They are two different models, and each is judged by "
          "its own family's metrics: they can't be compared with each other."),
        L("Un regresor estima una cantidad y se mide por el error en soles; "
          "un clasificador estima una probabilidad y se mide por cómo ordena "
          "los casos. Un regresor no tiene umbral, así que no puede tener "
          "curva ROC; un clasificador no tiene error en soles. Poner las "
          "métricas de uno en el otro no es más rigor, es una confusión de "
          "categorías.",
          "A regressor estimates a quantity and is measured by its error in "
          "soles; a classifier estimates a probability and is measured by how "
          "well it ranks cases. A regressor has no threshold, so it can't "
          "have an ROC curve; a classifier has no error in soles. Putting one "
          "model's metrics on the other isn't extra rigor — it's a category "
          "mistake."),
        seccion=L("ficha técnica", "model card"),
        eyebrow=L("Ficha técnica · métricas y límites",
                  "Model card · metrics and limits"))

    # Al llegar desde «¿Por qué tan alto? →» se marca el bloque de destino. No
    # se usa un ancla: la navegación es por session_state, no por URL, así que
    # no hay nada que haga scroll. Por eso el resumen de un vistazo de la ficha
    # responde justo esa pregunta: queda lo primero tras la cabecera, visible
    # al cambiar de sección, y el resalte solo dice «es este».
    resaltar = st.session_state.pop("resaltar_demasiado_bueno", False)
    html(f"<h2{' class=\"resaltado\"' if resaltar else ''}>"
         + L("¿Es demasiado bueno el clasificador de informalidad?",
             "Is the informality classifier too good to be true?") + "</h2>")

    abl = clas.get("ablacion", [])
    pr = a.get("pr", {})
    if pr:
        col_v, col_c = st.columns([55, 45], gap="large")
        with col_v:
            grafico(graficos.curva_pr(pr["recall"], pr["precision"], pr["auc"],
                                      pr["baseline"], None, T()), 330,
                    vistazo=True)
        with col_c:
            cifras = [
                (d(pr["auc"], 2),
                 L("PR-AUC en test: qué tan bien ordena a los informales "
                   "primero", "test PR-AUC: how well it ranks informal jobs "
                   "first")),
                (d(pr["baseline"], 2),
                 L("el suelo: lo que acertaría señalar a todos al azar",
                   "the floor: what flagging everyone at random would score"))]
            if len(abl) > 1:
                cifras.append((d(abl[-1]["PRAUC_test"], 2),
                               L("PR-AUC en test sin tamaño de empresa ni "
                                 "categoría, las variables más pegadas al "
                                 "target",
                                 "test PR-AUC without firm size or "
                                 "employment category, the features closest "
                                 "to the target")))
            vistazo_resumen(cifras, L(
                "Alto, pero no es fuga: el suelo ya es alto y la señal se "
                "sostiene sin las variables casi definicionales. El estimador "
                "de ingreso se mide aparte, en soles.",
                "High, but not leakage: the floor is already high and the "
                "signal holds without the near-definitional features. The "
                "income estimator is measured separately, in soles."))

    t_clf, t_reg, t_lim = st.tabs([
        L("Clasificador de informalidad", "Informality classifier"),
        L("Estimador de ingreso", "Income estimator"),
        L("Límites y procedencia", "Limits and provenance")])
    with t_clf:
        _ficha_clasificador(clas, a, abl)
    with t_reg:
        _ficha_regresor(reg)
    with t_lim:
        _ficha_limites(clas, reg, meta)

    html("<h2>" + L("Referencias", "References") + "</h2>")
    html("<div class='sutil' style='max-width:78ch;margin-bottom:16px'>" + L(
        "Toda afirmación de esta app que no sea un cálculo propio sobre los "
        "microdatos lleva su referencia. Donde la literatura no dice lo que "
        "haría falta para respaldar una frase, se dice que la lectura es "
        "nuestra en vez de atribuírsela a nadie. Se marca cuáles son de acceso "
        "abierto: enlazar algo que el lector no puede abrir es citar a medias.",
        "Every claim in this app that isn't our own computation on the "
        "microdata carries a reference. Where the literature doesn't say what "
        "a sentence would need, we say the reading is ours instead of "
        "attributing it to anyone. Open-access sources are marked: linking "
        "something the reader can't open is only half a citation.") + "</div>")
    html(referencias.lista_html())


# --------------------------------------------------------------------------
# Sección 5: sala de máquinas — cómo se construyó
# --------------------------------------------------------------------------
# Sus cifras salen de models/ui_maquinas.json (hermano de ui_artifacts.json,
# ambos de src/09) y de los artefactos ya existentes. Nada se calcula aquí,
# salvo el «rayos X»: una predicción real cronometrada paso a paso.
#
# TODO(fase2): walkthrough del código por estación (enlaces blob/main a src/00-09).
# TODO(fase2): quiz de autoevaluación al pie de cada sección.
# TODO(fase2): comparador visual E1→E9 sobre torneo.tabla.
def _mb(b) -> str:
    return "—" if b is None else n(b / 1e6, 1) + " MB"


def _kb(b) -> str:
    return "—" if b is None else n(b / 1024, 1) + " KB"


def _enlace_pie(texto: str, ruta: str) -> str:
    """Chip-enlace al archivo exacto en GitHub, en pestaña nueva."""
    return (f"<a class='chip-evidencia' target='_blank' rel='noopener' "
            f"href='{BLOB}/{quote(ruta)}'>{escape(texto)}</a>")


def _estaciones(schema: dict, art: dict, maq: dict) -> list[dict]:
    """Contenido de las seis estaciones; toda cifra viene de un artefacto."""
    reg = schema["regresor"]
    tam = maq.get("tamanos", {})
    modelos = tam.get("modelos_bytes", {})
    emb = {e["clave"]: e for e in maq.get("embudo", {}).get("etapas", [])}
    split = maq.get("embudo", {}).get("split", {})
    tfnr = maq.get("embudo", {}).get("tfnr", {})
    tabla = sorted(art.get("torneo", {}).get("tabla", []),
                   key=lambda f: f["MAE_cv"])
    autopsia = art.get("torneo", {}).get("autopsia", {})
    meta = art.get("meta", {})
    desplegada = art.get("torneo", {}).get("desplegada", "—")

    crudo = emb.get("crudo", {}).get("filas")
    muestra = emb.get("torneo", {}).get("filas")
    ganador, segundo = (tabla + [{}, {}])[:2]
    smear = d(float(reg["smearing_duan"]), 4)
    ver_codigo = L("ver el código →", "view the code →")

    # Reconciliación con la lámina del mazo: las DOS cifras vienen leídas
    # (medición viva vs. blobs de git al commit del mazo), ninguna a mano.
    mazo = tam.get("repo_mazo") or {}
    nota_nube = None
    if mazo.get("bytes") and tam.get("repo_versionado_bytes"):
        nota_nube = L(
            f"El mazo congelado midió {n(mazo['bytes'] / 1e6, 1)} MB en su "
            "commit; la diferencia es la propia presentación y esta pestaña, "
            "añadidas después — el repo crece, la medición del mazo quedó "
            "anclada a su commit.",
            f"The frozen slide deck measured {n(mazo['bytes'] / 1e6, 1)} MB at "
            "its commit; the difference is the presentation itself and this "
            "tab, added later — the repo grows, the deck's measurement stayed "
            "pinned to its commit.")

    return [
        {"titulo": L("Microdatos INEI", "INEI microdata"),
         "sub": _mb(tam.get("data_bytes")),
         "entra": L("Tres archivos CSV públicos del INEI (ENAHO 2025): módulo "
                    "02 (miembros del hogar), 03 (educación) y 05 (empleo e "
                    "ingresos). Separados por «;», codificación latin-1 y "
                    "hasta una columna con coma decimal — los datos reales "
                    "llegan así.",
                    "Three public INEI CSV files (ENAHO 2025): module 02 "
                    "(household members), 03 (education) and 05 (employment "
                    "and income). Semicolon-separated, latin-1 encoded, and "
                    "even a column with comma decimals — real data arrives "
                    "like that."),
         "decide": L("Qué módulos sirven para la pregunta: 02, 03 y 05 se "
                     "quedan; la Sumaria y los módulos 09/10 se descartaron "
                     "porque no aportan variables a estos dos problemas.",
                     "Which modules serve the question: 02, 03 and 05 stay; "
                     "the Sumaria and modules 09/10 were dropped because they "
                     "add no features to these two problems."),
         "sale": L(f"El módulo 05 crudo: {n(crudo)} filas de personas "
                   "encuestadas, todavía con centinelas y sin filtrar.",
                   f"Raw module 05: {n(crudo)} rows of surveyed people, "
                   "sentinels still in and unfiltered."),
         "tarjetas": [
             (L("microdatos en disco", "microdata on disk"),
              _mb(tam.get("data_bytes")),
              L("Viven solo en la computadora de desarrollo: jamás suben a "
                "GitHub ni a la nube.",
                "They live only on the development machine: never pushed to "
                "GitHub or the cloud.")),
             (L("filas crudas · módulo 05", "raw rows · module 05"),
              n(crudo) if crudo else "—",
              L("Cada fila es una persona encuestada.",
                "Each row is one surveyed person.")),
         ],
         "codigo": [(ver_codigo, "src/00_inventario.py")]},
        {"titulo": L("Limpieza", "Cleaning"),
         "sub": (L(f"{n(muestra)} filas", f"{n(muestra)} rows")
                 if muestra else "—"),
         "entra": L(f"Las {n(crudo)} filas crudas más la educación y "
                    "demografía de los módulos 02 y 03.",
                    f"The {n(crudo)} raw rows plus education and demographics "
                    "from modules 02 and 03."),
         "decide": L("Dos cosas: qué es un dato falso (el 999999 que el INEI "
                     "usa como «no sabe» se convierte en vacío) y quién "
                     "pertenece a la población de estudio — los filtros del "
                     "embudo que se ve más abajo.",
                     "Two things: what counts as a fake value (the 999999 "
                     "INEI uses for “don't know” becomes missing) and who "
                     "belongs to the study population — the funnel filters "
                     "shown below."),
         "sale": L(f"{n(muestra)} trabajadores listos para el torneo, "
                   f"guardados en un solo archivo de tabla (formato parquet) "
                   f"de {_mb(tam.get('torneo_frame_bytes'))}.",
                   f"{n(muestra)} workers ready for the tournament, stored in "
                   f"a single table file (parquet format) of "
                   f"{_mb(tam.get('torneo_frame_bytes'))}."),
         "tarjetas": [
             (L("centinelas limpiados", "sentinels cleaned"),
              n(autopsia.get("n_centinelas", 0)) if autopsia else "—",
              L(f"Con ellos dentro, una regresión de prueba salía absurda: R² "
                f"{d(autopsia.get('corrida_sucia', {}).get('r2', 0), 2)} y "
                f"hasta la educación «restaba» ingreso. Limpios: R² "
                f"{d(autopsia.get('corrida_limpia', {}).get('r2', 0), 2)} y "
                f"signos con sentido.",
                f"With them in, a test regression came out absurd: R² "
                f"{d(autopsia.get('corrida_sucia', {}).get('r2', 0), 2)} and "
                f"even schooling “subtracted” income. Cleaned: R² "
                f"{d(autopsia.get('corrida_limpia', {}).get('r2', 0), 2)} "
                f"and signs that make sense.")),
             (L("TFNR excluidos", "unpaid family workers excluded"),
              n(tfnr.get("filas", 0)) if tfnr else "—",
              L("Trabajadores familiares no remunerados: trabajan, pero sin "
                "sueldo no hay cifra que aprender.",
                "They work, but with no pay there's no figure to learn.")),
         ],
         "codigo": [(ver_codigo, "src/03_fase1_preparacion.py"),
                    (L("el embudo auditado (§4) →", "the audited funnel (§4) →"),
                     "INFORME_AUDITORIA.md")]},
        {"titulo": L("Torneo", "Tournament"),
         "sub": (L(f"{len(tabla)} recetas", f"{len(tabla)} recipes")
                 if tabla else "—"),
         "entra": L(f"Las {n(split.get('train', 0))} filas de entrenamiento, "
                    "partidas en 5 bloques: cada receta se entrena con cuatro "
                    "y se prueba con el quinto, cinco veces (validación "
                    "cruzada de 5 pliegues). El test no opina todavía.",
                    f"The {n(split.get('train', 0))} training rows, split into "
                    "5 blocks: each recipe trains on four and is tested on "
                    "the fifth, five times over (5-fold cross-validation). "
                    "The test set has no say yet."),
         "decide": L("Qué receta gana. Nueve especificaciones E1–E9 —de la "
                     "regresión lineal simple al <i>gradient boosting</i>, "
                     "que encadena árboles de decisión corrigiendo cada uno el "
                     "error del anterior— compiten por el error medio de esa "
                     "validación cruzada: un solo número por receta, decidido "
                     "ANTES de mirar el test.",
                     "Which recipe wins. Nine specifications E1–E9 — from "
                     "simple linear regression to <i>gradient boosting</i>, "
                     "which chains decision trees, each correcting the "
                     "previous one's error — compete on the mean error of "
                     "that cross-validation: one number per recipe, decided "
                     "BEFORE looking at the test set."),
         "sale": (L(f"La receta {desplegada} elegida: se equivoca "
                    f"S/ {d(ganador.get('MAE_cv', 0), 1)} al mes en promedio; "
                    f"la segunda ({segundo.get('ID', '—')}) "
                    f"S/ {d(segundo.get('MAE_cv', 0), 1)}.",
                    f"Recipe {desplegada} is chosen: it's off by "
                    f"S/ {d(ganador.get('MAE_cv', 0), 1)} a month on average; "
                    f"the runner-up ({segundo.get('ID', '—')}), "
                    f"S/ {d(segundo.get('MAE_cv', 0), 1)}.")
                  if tabla else "—"),
         "tarjetas": [
             (L("MAE_cv del ganador", "winner's MAE_cv"),
              f"S/ {d(ganador.get('MAE_cv', 0), 1)}" if tabla else "—",
              L("Cuánto se equivoca por persona, medido sin tocar el test.",
                "How far off it is per person, measured without touching "
                "the test set.")),
             (L("recetas comparadas", "recipes compared"),
              str(len(tabla)) if tabla else "—",
              L("Mismas filas, mismos pliegues: solo cambia la receta.",
                "Same rows, same folds: only the recipe changes.")),
         ],
         "codigo": [(ver_codigo, "src/04_torneo_regresion.py")]},
        {"titulo": L("Entrenamiento", "Training"), "sub": "2 × .joblib",
         "entra": L(f"La receta ganadora y las {n(split.get('train', 0))} "
                    "filas de entrenamiento.",
                    f"The winning recipe and the {n(split.get('train', 0))} "
                    "training rows."),
         "decide": L("Los últimos números propios del modelo: entrenar la "
                     "receta ganadora definitiva y calcular la corrección de "
                     f"Duan (× {smear}, la constante que repara el promedio "
                     "al deshacer el logaritmo) usando solo los errores "
                     "medidos en esa validación cruzada — nunca con el test.",
                     "The model's last numbers of its own: fit the final "
                     "winning recipe and compute Duan's correction "
                     f"(× {smear}, the constant that repairs the average when "
                     "undoing the log) using only the errors measured in that "
                     "cross-validation — never the test set."),
         "sale": L("Dos modelos ya entrenados, guardados como archivo "
                   "(.joblib) DENTRO del repositorio: la nube no reentrena, "
                   "solo los lee.",
                   "Two trained models, saved as files (.joblib) INSIDE the "
                   "repository: the cloud never retrains, it only loads "
                   "them."),
         "tarjetas": [
             ("regresor_e9.joblib", _kb(modelos.get("regresor_e9.joblib")),
              L("El estimador de ingreso, listo para predecir.",
                "The income estimator, ready to predict.")),
             ("clasificador_gb.joblib",
              _kb(modelos.get("clasificador_gb.joblib")),
              L("El detector de empleo informal.",
                "The informal-employment detector.")),
             (L("corrección de Duan", "Duan correction"), f"× {smear}",
              L("Una constante calculada al entrenar; la app solo multiplica.",
                "A constant computed at training time; the app just "
                "multiplies.")),
         ],
         "codigo": [(ver_codigo, "src/07_guardar_regresor.py"),
                    (L("el clasificador →", "the classifier →"),
                     "src/06_entrenar_clasificador.py")]},
        {"titulo": L("Artefactos", "Artifacts"), "sub": "3 × JSON",
         "entra": L("Los modelos entrenados y los microdatos, por última vez.",
                    "The trained models and the microdata, one last time."),
         "decide": L("Todo lo que la app va a dibujar se calcula AQUÍ, una "
                     "sola vez: curvas de umbral, dependencia parcial (11 "
                     "variables × 20 puntos), importancia por permutación "
                     "(9.000 filas × 5 repeticiones), cohortes ponderadas.",
                     "Everything the app will draw is computed HERE, once: "
                     "threshold curves, partial dependence (11 features × 20 "
                     "points), permutation importance (9,000 rows × 5 "
                     "repeats), weighted cohorts."),
         "sale": L("Tres JSON pequeños: ui_artifacts.json, feature_schema.json "
                   "y ui_maquinas.json (el de esta pestaña). Mover un control "
                   "en la app no recalcula nada: lee de aquí.",
                   "Three small JSON files: ui_artifacts.json, "
                   "feature_schema.json and ui_maquinas.json (this tab's). "
                   "Moving a control in the app recomputes nothing: it reads "
                   "from here."),
         "tarjetas": [
             ("ui_artifacts.json", _kb(modelos.get("ui_artifacts.json")),
              L(f"De {_mb(tam.get('data_bytes'))} de microdatos a esto: la "
                "app solo carga lo precomputado.",
                f"From {_mb(tam.get('data_bytes'))} of microdata down to "
                "this: the app only loads what's precomputed.")),
             ("feature_schema.json", _kb(modelos.get("feature_schema.json")),
              L("El contrato del formulario: variables, rangos y opciones.",
                "The form's contract: features, ranges and options.")),
         ],
         "codigo": [(ver_codigo, "src/09_precomputar_ui.py")]},
        {"titulo": L("Nube", "Cloud"), "sub": _mb(tam.get("repo_versionado_bytes")),
         "entra": L(f"El repositorio versionado: "
                    f"{n(tam.get('repo_archivos', 0))} archivos, "
                    f"{_mb(tam.get('repo_versionado_bytes'))} — código, "
                    "modelos, artefactos y presentación. Los microdatos NO.",
                    f"The versioned repository: "
                    f"{n(tam.get('repo_archivos', 0))} files, "
                    f"{_mb(tam.get('repo_versionado_bytes'))} — code, models, "
                    "artifacts and slides. The microdata, NO."),
         "decide": L(f"Qué viaja y qué no: data/ "
                     f"({_mb(tam.get('data_bytes'))}) se queda; los .joblib y "
                     "los JSON sí van. Y las versiones quedan fijadas en "
                     "requirements.txt: la nube instala exactamente lo "
                     "probado en local.",
                     f"What travels and what doesn't: data/ "
                     f"({_mb(tam.get('data_bytes'))}) stays; the .joblib and "
                     "JSON files go. Versions are pinned in requirements.txt: "
                     "the cloud installs exactly what was tested locally."),
         "sale": L("La app pública en Streamlit Community Cloud. Cada push a "
                   "main la redespliega sola en unos minutos — esta pestaña "
                   "llegó así.",
                   "The public app on Streamlit Community Cloud. Every push "
                   "to main redeploys it automatically within minutes — this "
                   "tab arrived that way."),
         "tarjetas": [
             (L("sube a la nube", "goes to the cloud"),
              _mb(tam.get("repo_versionado_bytes")),
              L("Todo lo versionado en GitHub, presentación incluida.",
                "Everything versioned on GitHub, slides included.")),
             (L("se queda en local", "stays local"), _mb(tam.get("data_bytes")),
              L("Los microdatos: pesan demasiado y la app no los necesita.",
                "The microdata: too heavy, and the app doesn't need them.")),
             (L("scikit-learn fijado", "scikit-learn pinned"),
              meta.get("version_scikit_learn", "—"),
              L("La misma versión que entrenó los modelos: un .joblib no es "
                "portable entre versiones.",
                "The same version that trained the models: a .joblib isn't "
                "portable across versions.")),
         ],
         "nota": nota_nube,
         "codigo": [(ver_codigo, "app/streamlit_app.py")]},
    ]


def _embudo(maq: dict) -> None:
    """
    Embudo SVG propio (antes un Sankey de plotly: 4,7 MB de JavaScript y
    ~2,5 s en la primera figura, con el «por qué» escondido en un hover). El
    motivo de cada recorte ahora se lee sin interactuar.
    """
    emb = maq["embudo"]
    e = {x["clave"]: x for x in emb["etapas"]}
    tfnr, split = emb["tfnr"], emb["split"]
    # El recorte del torneo se cuenta sobre el dataset de modelado: es la
    # cifra que justifica «casi nadie se pierde» y sale de los datos.
    rel = e["torneo"]["recorte"] / e["modelado"]["filas"] * 100
    svg = graficos.embudo(
        [(L("Módulo 05 crudo", "Raw module 05"), e["crudo"]["filas"]),
         (L("Ocupados", "Employed"), e["ocupados"]["filas"]),
         (L("Dataset de modelado", "Modeling dataset"), e["modelado"]["filas"]),
         (L("Muestra del torneo", "Tournament sample"), e["torneo"]["filas"])],
        [(L("No ocupados", "Not employed"), e["ocupados"]["recorte"],
          L("El modelo estima ingreso del trabajo: sin ocupación en la semana "
            "de referencia (OCU500 ≠ 1) no hay ingreso laboral que estimar.",
            "The model estimates labor income: with no job in the reference "
            "week (OCU500 ≠ 1) there's no labor income to estimate.")),
         (L("Menores de 14 o sin ingreso", "Under 14 or no income"),
          e["modelado"]["recorte"],
          L(f"Menores de 14 (edad mínima laboral del INEI) o sin ingreso "
            f"laboral positivo. Aquí van los {n(tfnr['filas'])} TFNR: "
            f"trabajadores familiares no remunerados — trabajan, pero sin "
            f"sueldo no hay cifra que aprender.",
            f"Under 14 (INEI's minimum working age) or without positive labor "
            f"income. The {n(tfnr['filas'])} unpaid family workers go here — "
            f"they work, but with no pay there's no figure to learn.")),
         (L("Casos incompletos", "Incomplete cases"), e["torneo"]["recorte"],
          L(f"Las 9 recetas deben compararse sobre exactamente las mismas "
            f"filas: fuera quien no tiene completos tamaño de empresa, "
            f"miembros, horas, educación o ingreso ({pc(rel, 1)} del dataset "
            f"de modelado).",
            f"The 9 recipes must be compared on exactly the same rows: out "
            f"goes anyone missing firm size, household members, hours, "
            f"schooling or income ({pc(rel, 1)} of the modeling dataset)."))],
        [(L("Entrenamiento", "Training"), split["train"],
          L(f"el 80 % entrena los modelos ({split['descripcion']}).",
            f"80% trains the models ({split['descripcion']}).")),
         (L("Prueba", "Test"), split["test"],
          L("el 20 % queda guardado y solo se mira al final, para medir sin "
            "hacer trampa.",
            "20% is held out and only looked at the end, to measure without "
            "cheating."))],
        T())
    grafico(svg, 520)


def _rayos_x(reg: dict, fila: pd.DataFrame) -> None:
    """
    Una predicción REAL con el capó abierto: los mismos pasos que corre la
    pestaña de ingreso, cronometrados en esta sesión. Teatro honesto: nada de
    la secuencia está inventado ni pregrabado.
    """
    def ms(t0: float) -> str:
        dt = (perf_counter() - t0) * 1000
        return "&lt;1 ms" if dt < 1 else f"{n(dt)} ms"

    with st.status(L("Motor en marcha…", "Engine running…"),
                   expanded=True) as estado:
        def paso(k: int, titulo: str, llano: str, t0: float) -> None:
            st.markdown(f"**{k} · {titulo}** — {ms(t0)}",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='sutil'>{llano}</div>",
                        unsafe_allow_html=True)

        total0 = perf_counter()
        t0 = perf_counter()
        modelo = cargar_modelo("regresor_e9.joblib")
        paso(1, L("Leer el modelo entrenado", "Load the trained model"),
             L("regresor_e9.joblib llega listo desde el repositorio: aquí "
               "nunca se entrena nada. La primera vez se lee del disco; "
               "después queda en memoria.",
               "regresor_e9.joblib arrives ready from the repository: nothing "
               "is ever trained here. The first time it's read from disk; "
               "after that it stays in memory."), t0)

        t0 = perf_counter()
        cols = columnas_esperadas(modelo)
        fila_ord = fila[cols]
        paso(2, L("Ordenar tu perfil", "Line up your profile"),
             L(f"Una fila con las {len(cols)} variables en el orden exacto "
               "que el modelo declara — ni una más, ni una menos: es el "
               "contrato del schema.",
               f"One row with the {len(cols)} features in the exact order the "
               "model declares — not one more, not one less: that's the "
               "schema contract."), t0)

        interno = getattr(modelo, "regressor_", None)
        internos = getattr(interno, "named_steps", {}) if interno is not None else {}
        prep, gb = internos.get("prep"), internos.get("modelo")
        k = 3
        if prep is not None and gb is not None:
            t0 = perf_counter()
            Xt = prep.transform(fila_ord)
            paso(k, L("Abrir las categorías (one-hot)",
                      "Expand the categories (one-hot)"),
                 L(f"Cada categoría se vuelve una columna de ceros y unos: la "
                   f"fila pasa de {len(cols)} a {Xt.shape[1]} columnas, que es "
                   "lo único que el árbol sabe leer.",
                   f"Each category becomes a column of zeros and ones: the "
                   f"row goes from {len(cols)} to {Xt.shape[1]} columns, "
                   "which is all a tree knows how to read."), t0)
            k += 1
            t0 = perf_counter()
            log_pred = float(gb.predict(Xt)[0])
            paso(k, L("Predecir en la escala del entrenamiento",
                      "Predict on the training scale"),
                 L(f"El gradient boosting responde en logaritmo: "
                   f"{d(log_pred, 3)}. Se entrenó así porque los ingresos "
                   "tienen cola larga.",
                   f"Gradient boosting answers in logs: {d(log_pred, 3)}. It "
                   "was trained that way because incomes have a long tail."),
                 t0)
            k += 1

        t0 = perf_counter()
        mediana = float(modelo.predict(fila_ord)[0])
        paso(k, L("Deshacer el logaritmo", "Undo the log"),
             L(f"S/ {n(mediana)} — el ingreso típico (mediana): la mitad de "
               "los perfiles como este gana menos, la otra mitad más.",
               f"S/ {n(mediana)} — the typical income (median): half of the "
               "profiles like this earn less, the other half more."), t0)
        k += 1

        t0 = perf_counter()
        smear = float(reg["smearing_duan"])
        media = (mediana + 1) * smear - 1
        paso(k, L("Corrección de Duan", "Duan correction"),
             L(f"× {d(smear, 4)}: deshacer un logaritmo deja corto el "
               "promedio; esta constante —calculada al entrenar, nunca aquí— "
               f"lo repara. Ingreso esperado: S/ {n(media)}.",
               f"× {d(smear, 4)}: undoing a log leaves the average short; "
               "this constant — computed at training time, never here — "
               f"fixes it. Expected income: S/ {n(media)}."), t0)

        # expanded=True: al completar, los pasos QUEDAN a la vista — son el
        # contenido de la sección, no un spinner que esconder.
        total = n((perf_counter() - total0) * 1000)
        estado.update(label=L(f"Motor recorrido: {k} pasos en {total} ms",
                              f"Engine done: {k} steps in {total} ms"),
                      state="complete", expanded=True)

    tarjetas = [
        tarjeta(L("ingreso típico", "typical income"), f"S/ {n(mediana)}",
                color=T()["acento_alto"],
                llano=L("El mismo número que da la pestaña «Estimación de "
                        "ingreso» con este perfil: es el mismo cálculo, visto "
                        "paso a paso.",
                        "The same number the “Income estimate” tab gives for "
                        "this profile: it's the same computation, seen step "
                        "by step.")),
        tarjeta(L("ingreso esperado", "expected income"), f"S/ {n(media)}",
                llano=L("El promedio, tras la corrección de Duan del paso "
                        "final.",
                        "The average, after the final step's Duan "
                        "correction.")),
    ]
    html("<div class='rejilla-tarjetas'>" + "".join(tarjetas) + "</div>")


# Una línea llana por variable del explorador. Escritas MIRANDO las curvas
# precomputadas (no al revés): si se regeneran los artefactos y una curva
# cambia de forma, la línea correspondiente hay que revisarla a mano.
def lineas_pd() -> dict[str, str]:
    return {
        "anios_educ": L("Cada año suma, pero no parejo: el tramo que más paga "
                        "es el final — la educación superior.",
                        "Every year adds, but not evenly: the stretch that "
                        "pays most is the last one — higher education."),
        "edad": L("Sube hasta la madurez laboral y luego se aplana: los "
                  "últimos años ya no añaden ingreso.",
                  "It rises until working maturity and then flattens: the "
                  "later years add no more income."),
        "horas_total": L("Más horas, más ingreso — pero lejos de proporcional: "
                         "multiplicar las horas por ocho apenas duplica la "
                         "estimación.",
                         "More hours, more income — but far from "
                         "proportional: multiplying hours by eight barely "
                         "doubles the estimate."),
        "sexo": L("Con el mismo perfil, el modelo estima menos para las "
                  "mujeres: es la brecha que existe en los datos de la "
                  "encuesta — descrita, no avalada.",
                  "With the same profile, the model estimates less for "
                  "women: that's the gap present in the survey data — "
                  "described, not endorsed."),
        "area": L("El mismo perfil paga distinto según dónde vive: urbano por "
                  "encima de rural.",
                  "The same profile pays differently depending on where it "
                  "lives: urban above rural."),
        "dominio": L("La geografía mueve la estimación: costa y Lima por "
                     "encima; la sierra, más abajo.",
                     "Geography moves the estimate: the coast and Lima on "
                     "top; the highlands, lower."),
        "rama": L("Minería paga como ninguna otra rama; el agro, menos que "
                  "todas — con la misma persona.",
                  "Mining pays like no other industry; farming, less than "
                  "all — for the same person."),
        "tamano_empresa": L("Cuanto más grande la empresa, mayor la "
                            "estimación: el salto grande está entre «hasta 20» "
                            "y el resto.",
                            "The bigger the firm, the higher the estimate: "
                            "the big jump is between “up to 20” and the "
                            "rest."),
        "categoria": L("Empleadores arriba, independientes abajo: esta "
                       "variable mueve la estimación más que casi cualquier "
                       "otra.",
                       "Employers on top, self-employed at the bottom: this "
                       "feature moves the estimate more than almost any "
                       "other."),
    }


def _maq_viaje(estaciones: list, titulos: list, idx: int) -> None:
    """Cómo se hizo, pestaña 1: selector de estación y su detalle."""
    # Se indexa por posición: los títulos cambian con el idioma y el control
    # no puede perder la estación elegida al cambiarlo.
    elegido = st.segmented_control(
        L("Estación", "Station"), list(range(len(titulos))),
        format_func=lambda i: f"{i + 1} · {titulos[i]}",
        default=st.session_state.get("maq_estacion_ok", 0),
        key="maq_estacion", label_visibility="collapsed")
    # st.segmented_control DESELECCIONA al pulsar la opción ya activa y
    # devuelve None: se recuerda la última válida.
    if elegido is not None:
        st.session_state["maq_estacion_ok"] = elegido
    st.toggle(L("▶ Ver el viaje en movimiento",
                          "▶ Watch the journey in motion"),
                        value=True, key="maq_viaje_anim",
                        help=L("Un punto recorre las seis estaciones en bucle "
                               "(12 s por vuelta). El detalle de abajo lo "
                               "sigue eligiendo el selector.",
                               "A dot travels the six stations in a loop "
                               "(12 s per lap). The selector above still "
                               "picks the detail below."))
    est = estaciones[idx]
    html(f"<div class='estacion-cab'><span class='estacion-num'>{idx + 1}</span>"
         f"<span>{est['titulo']}</span></div>")
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, rotulo, texto in ((c1, L("Qué entra", "What goes in"), est["entra"]),
                               (c2, L("Qué se decide", "What gets decided"),
                                est["decide"]),
                               (c3, L("Qué sale", "What comes out"), est["sale"])):
        with col:
            html(f"<div class='paso-viaje'><div class='eyebrow'>{rotulo}</div>"
                 f"<div class='sutil'>{texto}</div></div>")
    st.write("")
    html("<div class='rejilla-tarjetas'>"
         + "".join(tarjeta(et, v, llano=ll) for et, v, ll in est["tarjetas"])
         + "</div>")
    if est.get("nota"):
        html(f"<div class='sutil' style='margin-top:8px'>{est['nota']}</div>")
    if est.get("codigo"):
        html("<div style='margin-top:10px'>"
             + " ".join(_enlace_pie(t, r) for t, r in est["codigo"])
             + "</div>")
    with st.expander(L("¿Qué principio hay aquí? · viaje",
                       "What's the principle here? · journey")):
        html("<div class='sutil'>" + L(
            "Precómputo y fuente única: la app no calcula al abrirse — todo lo "
            "que este viaje muestra lo generó <code>src/09</code> una sola "
            "vez, y es lo mismo que alimenta las otras pestañas y la "
            "presentación.",
            "Precompute and a single source of truth: the app computes nothing "
            "on load — everything this journey shows was generated once by "
            "<code>src/09</code>, and it's the same data feeding the other "
            "tabs and the presentation.") + "</div>")


def _maq_embudo(maq: dict) -> None:
    """Cómo se hizo, pestaña 2: el embudo de filas con su porqué."""
    html("<div class='entradilla'>" + L(
        "Cada filtro recorta filas y tiene un porqué, escrito junto al trozo "
        "que se cae. Los porcentajes son sobre el total crudo.",
        "Every filter trims rows and has a reason, written next to the piece "
        "that falls off. Percentages are of the raw total.") + "</div>")
    _embudo(maq)
    with st.expander(L("¿Qué principio hay aquí? · embudo",
                       "What's the principle here? · funnel")):
        html("<div class='sutil'>" + L(
            "Estos números no están tecleados en esta página: "
            "<code>src/09</code> los lee del informe de auditoría (§4), "
            "verifica que las restas cuadren y los publica en el artefacto. Si "
            "el informe cambia, esta página cambia sola — o el generador "
            "aborta.",
            "These numbers aren't typed into this page: <code>src/09</code> "
            "reads them from the audit report (§4), checks that the "
            "subtractions add up and publishes them in the artifact. If the "
            "report changes, this page changes with it — or the generator "
            "aborts.") + "</div>")


def _maq_rayos(reg: dict) -> None:
    """Cómo se hizo, pestaña 3: la predicción paso a paso, cronometrada."""
    html("<div class='entradilla'>" + L(
        "El mismo formulario de la primera pestaña; al estimar se ve cada "
        "paso real del cálculo, con su tiempo.",
        "The same form as the first tab; when you run it you see every real "
        "step of the computation, with its timing.") + "</div>")
    if st.toggle(L("Ver el motor", "Open the engine"), key="maq_motor",
                 help=L("Los pasos son los reales de esta sesión, "
                        "cronometrados al ejecutarse. No es una animación.",
                        "The steps are this session's real ones, timed as "
                        "they run. It's not an animation.")):
        izq, der = st.columns([36, 64], gap="large")
        with izq:
            with st.container(border=True, key="caja_form_maq"):
                html("<div class='eyebrow'>" + L("Perfil del trabajador",
                                                 "Worker profile") + "</div>")
                selector_perfiles("maq", reg["features"])
                fila = formulario(reg["features"], "maq")
                lanzar = st.button(L("Estimar mirando el motor",
                                     "Run it with the hood open"),
                                   type="primary", key="btn_maq",
                                   icon=":material/play_arrow:")
        with der:
            if lanzar:
                _rayos_x(reg, fila)
            else:
                html("<div class='panel'><div class='panel-titulo'>"
                     + L("Motor en espera", "Engine idle")
                     + "</div><div class='sutil'>" + L(
                         "Arma el perfil y pulsa «Estimar mirando el motor»: "
                         "verás cargar el modelo, abrir las categorías en "
                         "columnas de ceros y unos, predecir en logaritmo, "
                         "deshacerlo y aplicar la corrección de Duan — cada "
                         "paso con su tiempo real.",
                         "Build the profile and press “Run it with the hood "
                         "open”: you'll see the model load, the categories "
                         "expand into columns of zeros and ones, the log "
                         "prediction, undoing it, and Duan's correction — "
                         "each step with its real timing.")
                     + "</div></div>")
    with st.expander(L("¿Qué principio hay aquí? · motor",
                       "What's the principle here? · engine")):
        html("<div class='sutil'>" + L(
            "Teatro honesto: la secuencia son los pasos reales, cronometrados "
            "en tu sesión. Lo único que la app no hace nunca en vivo es "
            "entrenar: el modelo llegó listo en el repositorio, con las "
            "versiones fijadas.",
            "Honest theater: the sequence is the real steps, timed in your "
            "session. The one thing the app never does live is train: the "
            "model arrived ready in the repository, with pinned "
            "versions.") + "</div>")


def _maq_mueve(reg: dict, art: dict) -> None:
    """Cómo se hizo, pestaña 4: dependencia parcial de una variable."""
    html("<div class='entradilla'>" + L(
        "¿Cuánto cambiaría el ingreso estimado si esta característica fuera "
        "distinta y todo lo demás quedara igual? Es la pregunta clásica del "
        "<i>ceteris paribus</i>, y la curva que la responde se llama "
        "dependencia parcial: el modelo ya entrenado se recorre a lo largo de "
        "los valores de una variable, con el resto del perfil en su promedio. "
        "Las curvas se calcularon una sola vez al entrenar — elegir aquí solo "
        "muestra la que pides.",
        "How much would the estimated income change if this characteristic "
        "were different and everything else stayed the same? It's the classic "
        "<i>ceteris paribus</i> question, and the curve that answers it is "
        "called partial dependence: the trained model is swept across the "
        "values of one feature, with the rest of the profile at its average. "
        "The curves were computed once at training time — choosing here just "
        "shows the one you ask for.") + "</div>")
    pd_reg = art.get("regresor", {}).get("dependencia_parcial", {})
    feats = [f for f in reg["features"]
             if f["nombre"] not in DERIVADAS and pd_reg.get(f["nombre"])]
    if not feats:
        aviso(L("El artefacto no trae la dependencia parcial del regresor.",
                "The artifact doesn't include the regressor's partial "
                "dependence."))
    else:
        # El panorama: las 9 formas de un vistazo, todas precomputadas.
        html("<div class='eyebrow'>" + L("El panorama · las 9 curvas de un "
                                         "vistazo",
                                         "The big picture · all 9 curves at "
                                         "a glance") + "</div>")
        cols9 = st.columns(3, gap="medium")
        for j, f9 in enumerate(feats):
            p9 = pd_reg[f9["nombre"]]
            with cols9[j % 3]:
                grafico(graficos.miniatura_pd(
                    p9["valores"], p9["efecto"], p9["tipo"], T()), 70)
                html(f"<div class='sutil' style='margin-top:-8px;"
                     f"text-align:center'>"
                     f"{escape(tr(f9.get('etiqueta', f9['nombre'])))}</div>")
        st.write("")
        nombres = [f["nombre"] for f in feats]
        nombre = st.selectbox(
            L("Variable", "Feature"), nombres,
            format_func=lambda k: tr(next(f for f in feats if f["nombre"] == k)
                                     .get("etiqueta", k)),
            key="maq_var")
        feat = next(f for f in feats if f["nombre"] == nombre)
        perfil = pd_reg[nombre]
        marca = (st.session_state.get("valores_maq", {}).get(nombre)
                 or st.session_state.get("valores_reg", {}).get(nombre))
        html(f"<div class='titulo-grafico'>"
             f"{escape(tr(feat.get('etiqueta', nombre)))}</div>")
        grafico(graficos.dependencia_parcial(
            perfil["valores"], perfil["efecto"], perfil["tipo"],
            tr(feat.get("etiqueta", nombre)), T(), marca=marca,
            formato_y="soles", mostrar_etiqueta=False), 230)
        linea = lineas_pd().get(nombre, L("Así cambia la estimación cuando "
                                          "solo se mueve esta variable.",
                                          "This is how the estimate changes "
                                          "when only this feature moves."))
        html(f"<div class='sutil'><b>{linea}</b> " + L(
            "El eje vertical es el ingreso típico estimado (S/ al mes) con el "
            "resto del perfil en su valor promedio.",
            "The vertical axis is the estimated typical income (S/ per month) "
            "with the rest of the profile at its average value.") + "</div>")
        html("<div class='sutil'>" + L(
            "¿Por qué 9 y no 11? Experiencia y experiencia² van atadas — "
            "moverlas por separado sería un perfil imposible.",
            "Why 9 and not 11? Experience and experience² are tied together — "
            "moving them separately would make an impossible "
            "profile.") + "</div>")

        # Modo delta: dos puntos YA precomputados de la misma curva; el
        # selector no toca el modelo. Numéricas y categóricas NO comparten
        # semántica: en una curva continua el delta es un recorrido; entre
        # barras es una comparación, y no hay «camino».
        st.write("")
        es_num = perfil["tipo"] == "numerico"
        vals = perfil["valores"]
        efec = [float(e) for e in perfil["efecto"]]
        etiqs = ([d(float(v), 1) for v in vals] if es_num
                 else [tr(v) for v in vals])
        crudos = [str(v) for v in vals]

        if es_num:
            rotulo = L("¿Y si cambia? · el delta sobre la curva",
                       "What if it changes? · the delta along the curve")
            ini_de, ini_a = 0, len(vals) - 1
        else:
            rotulo = L("¿Y si fuera otra? · la diferencia entre categorías",
                       "What if it were another? · the gap between categories")
            # «de» = la categoría del perfil; si nadie estimó todavía, la más
            # frecuente de la cohorte ponderada. «a» = la de mayor estimación.
            actual = (st.session_state.get("valores_maq", {}).get(nombre)
                      or st.session_state.get("valores_reg", {}).get(nombre))
            ini_de = None
            if actual is not None and str(actual) in crudos:
                ini_de = crudos.index(str(actual))
            if ini_de is None:
                repartos = (art.get("regresor", {}).get("cohorte", {})
                            .get(nombre, {}).get("participacion_pct", {}))
                frecuente = max(repartos, key=repartos.get) if repartos else None
                ini_de = (crudos.index(str(frecuente))
                          if frecuente is not None and str(frecuente) in crudos
                          else 0)
            ini_a = max(range(len(efec)), key=lambda i: efec[i])
            if ini_a == ini_de:               # el perfil ya está en la más alta
                ini_de = min(range(len(efec)), key=lambda i: efec[i])

        html(f"<div class='eyebrow'>{rotulo}</div>")
        c_de, c_a = st.columns(2)
        with c_de:
            i_de = st.selectbox(L("de …", "from …"), range(len(vals)),
                                index=ini_de, format_func=lambda i: etiqs[i],
                                key=f"maq_delta_de_{nombre}")
        with c_a:
            i_a = st.selectbox(L("a …", "to …"), range(len(vals)), index=ini_a,
                               format_func=lambda i: etiqs[i],
                               key=f"maq_delta_a_{nombre}")

        if (not es_num) and i_de == i_a:
            aviso(L("Elegiste la misma categoría en los dos lados: la "
                    "diferencia es cero por definición. Elige dos distintas "
                    "para comparar.",
                    "You picked the same category on both sides: the "
                    "difference is zero by definition. Pick two different "
                    "ones to compare."))
        else:
            delta = efec[i_a] - efec[i_de]
            signo = "+" if delta >= 0 else "−"
            llano_delta = (
                L("Dos puntos de la misma curva: cuánto cambia la estimación "
                  "al recorrer la variable de un valor a otro.",
                  "Two points on the same curve: how much the estimate "
                  "changes as the feature goes from one value to another.")
                if es_num else
                L("Dos alturas de barra: cuánto separa el modelo a una "
                  "categoría de otra, con el resto del perfil igual. No hay "
                  "«camino» entre categorías — solo comparación.",
                  "Two bar heights: how far the model sets one category apart "
                  "from another, with the rest of the profile unchanged. "
                  "There's no “path” between categories — only comparison."))
            verbo = (L("pasar", "going") if es_num
                     else L("diferencia", "difference"))
            html("<div class='rejilla-tarjetas'>" + tarjeta(
                L(f"{verbo} de {escape(etiqs[i_de])} a {escape(etiqs[i_a])}",
                  f"{verbo} from {escape(etiqs[i_de])} to {escape(etiqs[i_a])}"),
                f"≈ {signo}S/ {n(abs(delta))}",
                nota=L("Diferencia que describe el modelo, no un efecto causal.",
                       "A difference the model describes, not a causal "
                       "effect."),
                llano=llano_delta) + "</div>")
    with st.expander(L("¿Qué principio hay aquí? · explorador",
                       "What's the principle here? · explorer")):
        html("<div class='sutil'>" + L(
            "Precómputo puro: cada curva son 20 puntos que <code>src/09</code> "
            "calculó una sola vez sobre 5.000 filas. Mover el selector no toca "
            "el modelo — por eso responde al instante.",
            "Pure precompute: each curve is 20 points that <code>src/09</code> "
            "computed once over 5,000 rows. Moving the selector doesn't touch "
            "the model — that's why it responds instantly.") + "</div>")
        html("<div class='sutil' style='margin-top:8px'>" + L(
            "La dependencia parcial tiene pedigrí: la introdujo el mismo "
            "artículo que propuso el <i>gradient boosting</i> desplegado "
            "aquí.<br>",
            "Partial dependence has a pedigree: it was introduced by the same "
            "paper that proposed the <i>gradient boosting</i> deployed "
            "here.<br>")
             + "· Friedman, J. H. (2001). Greedy function approximation: A "
             "gradient boosting machine. <i>Annals of Statistics, 29</i>(5), "
             "1189–1232, §8.2.<br>"
             "· Hastie, Tibshirani &amp; Friedman (2009). <i>The Elements "
             "of Statistical Learning</i> (" + L("2.ª ed.", "2nd ed.")
             + "), §10.13.2. Springer.<br>"
             "· Molnar, C. (2022). <i>Interpretable Machine Learning</i> ("
             + L("2.ª ed.), capítulo", "2nd ed.), chapter")
             + " <i>Partial Dependence Plot</i> — "
             "<a href='https://christophm.github.io/interpretable-ml-book/' "
             "target='_blank' rel='noopener'>christophm.github.io/"
             "interpretable-ml-book ↗</a> ("
             + L("acceso libre", "open access") + ").</div>")
        html("<div class='sutil' style='margin-top:8px'>" + L(
            "La advertencia honesta de esos mismos textos: estas curvas asumen "
            "que la variable movida no está fuertemente correlacionada con las "
            "demás — por eso experiencia y experiencia² no se mueven por "
            "separado.",
            "The honest caveat from those same texts: these curves assume the "
            "moved feature isn't strongly correlated with the others — which "
            "is why experience and experience² aren't moved "
            "separately.") + "</div>")


def seccion_maquinas(schema: dict, art: dict) -> None:
    reg = schema["regresor"]
    maq = cargar_maquinas()

    cabecera(
        L("Cómo se hizo: de la encuesta del INEI a la app",
          "How it was built: from INEI's survey to this app"),
        L("De la encuesta del INEI a esta app, paso a paso. Ninguna cifra se "
          "calcula aquí: todo sale de los mismos archivos que alimentan las "
          "demás secciones.",
          "From INEI's survey to this app, step by step. No figure is computed "
          "here: everything comes from the same files that feed the other "
          "sections."),
        L("Las cifras del embudo y los tamaños medidos viven en "
          "<code>models/ui_maquinas.json</code>, generado por "
          "<code>src/09_precomputar_ui.py</code> leyendo el embudo auditado de "
          "<code>INFORME_AUDITORIA.md §4</code> y midiendo los archivos en "
          "disco. Va en un artefacto hermano de <code>ui_artifacts.json</code> "
          "porque la presentación congelada cita el tamaño en disco de este "
          "último: no puede crecer ni un byte.",
          "The funnel figures and measured sizes live in "
          "<code>models/ui_maquinas.json</code>, generated by "
          "<code>src/09_precomputar_ui.py</code> by reading the audited funnel "
          "in <code>INFORME_AUDITORIA.md §4</code> and measuring the files on "
          "disk. It's a sibling artifact of <code>ui_artifacts.json</code> "
          "because the frozen presentation cites the latter's size on disk: "
          "it can't grow by a single byte."),
        seccion=L("máquinas", "engine room"),
        eyebrow=L("Sala de máquinas · MLOps de punta a punta",
                  "Engine room · end-to-end MLOps"))

    if not maq:
        aviso(L("Falta <code>models/ui_maquinas.json</code>. Genéralo con "
                "<code>python src/09_precomputar_ui.py --solo-maquinas</code>.",
                "<code>models/ui_maquinas.json</code> is missing. Generate it "
                "with <code>python src/09_precomputar_ui.py "
                "--solo-maquinas</code>."))
        return

    # ---- De un vistazo: el viaje + tres cifras + una frase ----
    estaciones = _estaciones(schema, art, maq)
    titulos = [e["titulo"] for e in estaciones]
    # El selector de estación vive en la primera pestaña, DEBAJO del SVG: se
    # lee su valor de session_state antes de dibujar, para que el viaje
    # resalte la estación ya elegida en este mismo rerun.
    # st.segmented_control DESELECCIONA al pulsar la opción ya activa y
    # devuelve None: se recuerda la última válida.
    if st.session_state.get("maq_estacion") is not None:
        st.session_state["maq_estacion_ok"] = st.session_state["maq_estacion"]
    idx = st.session_state.get("maq_estacion_ok", 0)
    # La animación vive DENTRO del SVG (SMIL): sin reruns ni sleeps. Arranca
    # encendida: es lo primero que ve quien entra a esta sección.
    animado = st.session_state.get("maq_viaje_anim", True)
    grafico(graficos.viaje_dato(titulos, [e["sub"] for e in estaciones],
                                idx, T(), animado=animado), 185, vistazo=True)
    emb, tam = maq["embudo"], maq["tamanos"]
    crudo = emb["etapas"][0]["filas"]
    modelado = emb["split"]["train"] + emb["split"]["test"]
    b_modelos = sum(v for k, v in tam["modelos_bytes"].items()
                    if k.endswith(".joblib"))
    vistazo_resumen(
        [(f"{n(crudo)} → {n(modelado)}",
          L("filas: del módulo de empleo crudo a la muestra que entrena y "
            "evalúa", "rows: from the raw employment module to the sample "
            "that trains and evaluates")),
         (_mb(tam["data_bytes"]),
          L(f"de microdatos que nunca entran al repositorio (el repo "
            f"versionado pesa {_mb(tam['repo_versionado_bytes'])})",
            f"of microdata that never enter the repository (the versioned "
            f"repo weighs {_mb(tam['repo_versionado_bytes'])})")),
         (_mb(b_modelos),
          L("pesan los dos modelos que carga la app",
            "is the weight of the two models the app loads"))],
        L("Todo lo caro se calcula una vez, fuera de la app; la app solo lee "
          "artefactos y responde.",
          "Everything expensive is computed once, outside the app; the app "
          "only reads artifacts and answers."),
        fila=True)

    t_viaje, t_embudo, t_rayos, t_mueve = st.tabs([
        L("El viaje, estación por estación", "The journey, station by station"),
        L("El embudo", "The funnel"),
        L("Rayos X de la predicción", "X-ray of a prediction"),
        L("Mueve una variable", "Move one feature")])
    with t_viaje:
        _maq_viaje(estaciones, titulos, idx)
    with t_embudo:
        _maq_embudo(maq)
    with t_rayos:
        _maq_rayos(reg)
    with t_mueve:
        _maq_mueve(reg, art)


# --------------------------------------------------------------------------
# Créditos: la firma del proyecto al pie de cada página
# --------------------------------------------------------------------------
DOCENTE = "Orlando Advíncula Zeballos"


def pie_creditos() -> None:
    """
    Autoría completa en TODAS las secciones: sin sidebar, el pie es el único
    lugar que se ve en cualquier página. Lleva también el mapa de la app (qué
    hace cada sección) y el límite de uso, que antes vivían en el sidebar.
    """
    grupo = " · ".join(GRUPO)
    mapa = "".join(f"<li><b>{titulo_seccion(c)}</b> — {descripcion_seccion(c)}</li>"
                   for c in CLAVES_SECCION)
    html(f"<div class='pie'>"
         f"<div class='pie-autor'>{L('Hecho por', 'Built by')} "
         f"<b>{AUTOR}</b> · <a href='{PORTAFOLIO}' target='_blank' "
         f"rel='noopener'>{PORTAFOLIO.removeprefix('https://')}</a> · "
         f"<a href='{REPO}' target='_blank' rel='noopener'>"
         + L("Código y metodología en GitHub ↗", "Code & methodology on GitHub ↗")
         + "</a></div>"
         f"<div>{L('Grupo del curso de Machine Learning (ENEI):', 'Machine Learning course group (ENEI, Peru):')} "
         f"{grupo} · {L('Docente', 'Instructor')}: {DOCENTE}</div>"
         f"<ul class='pie-mapa'>{mapa}</ul>"
         f"<div>"
         + L("Herramienta demostrativa sobre microdatos públicos del INEI. No "
             "es un instrumento de fiscalización laboral.",
             "A demonstration tool built on INEI public microdata. Not a "
             "labor-enforcement instrument.")
         + f"</div>"
         f"<div>{L('Datos', 'Data')}: INEI — ENAHO 2025 · "
         f"{L('Código', 'Code')}: Apache-2.0 · v{VERSION}</div>"
         f"</div>")


# --------------------------------------------------------------------------
# Barra superior: marca, secciones, idioma y tema
# --------------------------------------------------------------------------
def barra_superior() -> None:
    """
    Los tres selectores van ligados a la URL (ver `sincronizar_url`), así que
    `?sec=torneo&lang=en&theme=terminal` abre justo eso y se puede compartir.

    `required=True` es la guarda contra el re-clic: un control segmentado
    normal deselecciona al pulsar la opción activa, y la app quedaba sin
    sección. Sin `default`: el valor ya está en la sesión (`iniciar_estado`).
    """
    tooltip = escape(L("Con el grupo ENEI: ", "With the ENEI group: ")
                     + ", ".join(GRUPO) + " · "
                     + L("Docente", "Instructor") + f": {DOCENTE}", quote=True)
    with st.container(horizontal=True, vertical_alignment="center",
                      gap="small", key="barra"):
        st.markdown(f"<div class='marca-barra'><span class='rombo'>◆</span>"
                    f"<span class='quien' title='{tooltip}'>{AUTOR}</span>"
                    f"</div>", unsafe_allow_html=True, width="content")
        st.segmented_control(
            L("Sección", "Section"), CLAVES_SECCION,
            format_func=titulo_corto, key="sec", required=True,
            label_visibility="collapsed", width="content")
        st.segmented_control(
            "Idioma / Language", list(i18n.IDIOMAS),
            format_func=str.upper, key="lang", required=True,
            label_visibility="collapsed", width="content")
        # Las opciones salen de PALETAS: añadir un tema allí lo hace aparecer
        # aquí, y quitarlo lo hace desaparecer. No hay lista que mantener.
        st.segmented_control(
            L("Tema", "Theme"), opciones_tema(),
            format_func=etiqueta_tema, key="theme", required=True,
            label_visibility="collapsed", width="content")


# --------------------------------------------------------------------------
def main() -> None:
    iniciar_estado()
    st.set_page_config(
        page_title=L("ENAHO — ingreso e informalidad",
                     "ENAHO — income & informality in Peru"),
        page_icon="◈", layout="wide")
    html(estilos.css(T()))

    if not (DIR_MODELS / "feature_schema.json").exists():
        aviso(L("No se encuentra <code>models/feature_schema.json</code>. "
                "Corre antes los scripts de <code>src/</code>.",
                "<code>models/feature_schema.json</code> not found. Run the "
                "<code>src/</code> scripts first."), "senal-alerta")
        st.stop()

    schema, art = cargar_schema(), cargar_artefactos()
    barra_superior()
    sincronizar_url()

    seccion = st.session_state["seccion"]
    # Se anima al entrar a una sección, no al rerun por un cambio de tema o
    # idioma, ni al rerun de un fragment (que no pasa por aquí: lee el False
    # que se deja al final).
    st.session_state["_animar"] = seccion != st.session_state.get("_ultima_seccion")
    st.session_state["_ultima_seccion"] = seccion
    if seccion == "ingreso":
        seccion_ingreso(schema, art)
    elif seccion == "informalidad":
        seccion_informalidad(schema, art)
    elif seccion == "torneo":
        seccion_torneo(schema, art)
    elif seccion == "maquinas":
        seccion_maquinas(schema, art)
    else:
        seccion_ficha(schema, art)
    pie_creditos()
    st.session_state["_animar"] = False


if __name__ == "__main__":
    main()
