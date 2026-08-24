# streamlit_app.py — app Streamlit: predicción, torneo y ficha
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
"""
FASE 3 — App: ingreso laboral e informalidad en el Perú (ENAHO 2025).

Arquitectura heredada del proyecto SIS-diabetes:
- La UI la dirige `models/feature_schema.json`; ningún campo está escrito aquí.
- Lo caro vive precomputado en `models/ui_artifacts.json`.
- El bloque de umbral corre en un `@st.fragment`: mover el slider no reejecuta
  el script ni vuelve a predecir.
- Los modelos se cargan bajo demanda y cacheados.
- Ningún número visible está escrito a mano: sale del schema o los artefactos.

Novedades de este proyecto:
- Modo claro/oscuro: `PALETAS` con las mismas claves; el CSS se GENERA desde la
  paleta activa y los SVG la reciben como parámetro (los iframes no heredan CSS).
- Sección «Torneo de modelos»: la exposición hecha interfaz (tres actos).
- Experiencia potencial: el usuario NO la digita; se deriva de edad y educación.

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
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).resolve().parent))
import estilos
import graficos
import referencias
from estilos import PALETAS
from referencias import ref

RAIZ = Path(__file__).resolve().parents[1]
DIR_MODELS = RAIZ / "models"

# --------------------------------------------------------------------------
# Contratos con los módulos y con el artefacto
# --------------------------------------------------------------------------
# Los tres fallos del despliegue del 20/08/2026 fueron el mismo tipo de cosa:
# este archivo pedía algo que su proveedor no tenía, y el error saltaba a
# mitad del render —cuando el usuario ya estaba mirando la pantalla— en vez de
# al arrancar. Lo que sigue lo convierte en un fallo temprano y explícito.
GRAFICOS_REQUERIDOS = [
    "envolver", "franja_probabilidad", "matriz_confusion",
    "curva_precision_cobertura", "curva_calibracion", "curva_roc", "curva_pr",
    "barras_importancia", "situador", "dependencia_parcial", "barras_mae",
    "viaje_dato",
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

SECCIONES = [
    ("ingreso", "Estimación de ingreso"),
    ("informalidad", "Empleo informal"),
    ("torneo", "Torneo de modelos"),
    ("ficha", "Ficha técnica"),
    ("maquinas", "⚙ Sala de máquinas"),
]
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
ETIQUETAS_TEMA = {"claro": "Claro", "oscuro": "Oscuro", "terminal": "Terminal"}


def opciones_tema() -> list[str]:
    """Los temas que existen de verdad, en orden estable."""
    return list(PALETAS)


def etiqueta_tema(clave: str) -> str:
    return ETIQUETAS_TEMA.get(clave, clave.capitalize())


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


def cabecera(pregunta: str, llano: str, detalle: str, seccion: str) -> None:
    """
    Dos capas: el titulo es una pregunta, debajo va español llano, y el texto
    técnico exacto se muda a un expander. La precisión no se borra, se baja de
    capa.

    `seccion` desambigua el expander. Streamlit identifica los widgets por
    etiqueta y posicion en el arbol: cuatro expanders llamados igual y situados
    igual son EL MISMO widget, asi que abrir el de una seccion abria el de
    todas. El sufijo rompe la colision.
    """
    html(f"<h1>{pregunta}</h1>")
    html(f"<div class='entradilla'>{llano}</div>")
    with st.expander(f"Detalle técnico · {seccion}"):
        html(f"<div class='sutil'>{detalle}</div>")


def grafico(svg: str, alto: int) -> None:
    components.html(graficos.envolver(svg, estilos.css_iframe(T())), height=alto,
                    scrolling=False)


def n(x: float, dec: int = 0) -> str:
    """Formato español: punto para miles, coma para decimales."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def d(x: float, dec: int = 2) -> str:
    """Decimal español, sin separador de miles (métricas: 0,9626)."""
    return f"{x:.{dec}f}".replace(".", ",")


def pct(x: float, dec: int = 1) -> str:
    """Fracción a porcentaje español: 0.975 -> «97,5 %»."""
    return f"{x * 100:.{dec}f}".replace(".", ",") + " %"


# --------------------------------------------------------------------------
# Formulario dirigido por el schema (con derivadas ocultas)
# --------------------------------------------------------------------------
def ayuda_de(feat: dict) -> str | None:
    partes = [feat[k] for k in ("nota", "nota_otros") if feat.get(k)]
    if feat.get("agrupadas_en_otros"):
        partes.append("Agrupadas en «OTROS»: " + ", ".join(feat["agrupadas_en_otros"]))
    return "\n\n".join(partes) or None


def formulario(features: list[dict], prefijo: str) -> pd.DataFrame:
    """
    Un control por variable del schema, EXCEPTO la experiencia potencial y su
    cuadrado: son derivadas de Mincer (edad − años educ − 6, truncada en 0) y
    digitarlas seria redundante e inconsistente. Se calculan aqui.
    """
    memoria = st.session_state.setdefault(f"valores_{prefijo}", {})
    valores = {}
    for feat in features:
        nombre, clave = feat["nombre"], f"{prefijo}_{feat['nombre']}"
        if nombre in DERIVADAS:
            continue
        previo = memoria.get(nombre, feat["default"])
        if feat["tipo"] == "numerico":
            lo, hi = float(feat["min"]), float(feat["max"])
            entero = all(float(feat[k]).is_integer() for k in ("min", "max", "default"))
            valores[nombre] = st.number_input(
                feat.get("etiqueta", nombre), min_value=lo, max_value=hi,
                value=float(min(max(float(previo), lo), hi)),
                step=1.0 if entero else 0.01,
                format="%.0f" if entero else "%.2f",
                key=clave, help=ayuda_de(feat))
        else:
            opciones = feat["opciones"]
            idx = opciones.index(previo) if previo in opciones else 0
            valores[nombre] = st.selectbox(
                feat.get("etiqueta", nombre), opciones, index=idx,
                key=clave, help=ayuda_de(feat))

    if {"edad", "anios_educ"} <= set(valores):
        exper = max(float(valores["edad"]) - float(valores["anios_educ"]) - 6, 0.0)
        valores["exper"] = exper
        valores["exper2"] = exper ** 2
        html(f"<div class='sutil'>Experiencia potencial derivada: "
             f"<b>{exper:.0f} años</b> (edad − años de educación − 6, "
             f"truncada en 0).</div>")

    st.session_state[f"valores_{prefijo}"] = valores
    orden = [f["nombre"] for f in features]
    return pd.DataFrame([valores])[[c for c in orden if c in valores]]


# Por qué cada variable se comporta como se comporta. Tres niveles, siempre
# etiquetados: DATO es lo que mide la barra; MECÁNICA es cuando la explicación
# es la propia regla que define el target (y entonces el resultado es en parte
# por construcción, no un hallazgo); HIPÓTESIS es lectura económica plausible,
# marcada como tal. Solo se escriben las que se pueden sostener.
PORQUES: dict[str, dict[str, str]] = {
    "tamano_empresa": {
        "mecanica":
            "En empresas de hasta 20 personas casi nadie aporta a pensión, y "
            "esa es justamente una de las dos reglas que definen «informal». "
            "La barra casi toca el techo por construcción: el modelo no está "
            "descubriendo algo, está reflejando la definición.",
    },
    "categoria": {
        "mecanica":
            "La categoría ocupacional decide qué regla se aplica: a "
            "independientes y empleadores se les mira el RUC; a los "
            "dependientes, el aporte a pensión. Que pese mucho es parte del "
            "diseño del target, no un descubrimiento del modelo.",
    },
    "dominio": {
        "hipotesis":
            "Selva y sierra concentran empleo independiente y agropecuario, y "
            "la literatura asocia esa estructura productiva a mayor "
            "informalidad. Es una interpretación del patrón, no una prueba: "
            "haría falta comparar empleos equivalentes entre regiones.",
    },
    "rama": {
        "hipotesis":
            "El agro y el comercio minorista concentran unidades pequeñas y "
            "trabajo por cuenta propia; la administración pública y la "
            "enseñanza, empleo asalariado con planilla. Es lectura del "
            "contexto productivo, no algo que estos datos prueben por sí solos.",
    },
    "anios_educ": {
        "hipotesis":
            "Más educación se asocia a empleos con contrato y planilla. Pero "
            "aquí no se puede separar el efecto de la educación del de los "
            "empleos a los que da acceso: es asociación, no causa.",
    },
    "area": {
        "hipotesis":
            "El empleo rural es mayoritariamente agropecuario e independiente, "
            "donde el registro tributario y la planilla son excepción. Es una "
            "interpretación de la composición del empleo, no una prueba.",
    },
}


def porque(variable: str, dato: str) -> str:
    """Bloque «por qué» con la etiqueta de honestidad que corresponda."""
    fichas = [f"<div class='porque-fila'><span class='etiqueta-dato'>dato</span>"
              f"<span>{dato}</span></div>"]
    p = PORQUES.get(variable, {})
    if p.get("mecanica"):
        fichas.append(f"<div class='porque-fila'>"
                      f"<span class='etiqueta-mecanica'>mecánica</span>"
                      f"<span>{p['mecanica']}</span></div>")
    if p.get("hipotesis"):
        fichas.append(f"<div class='porque-fila'>"
                      f"<span class='etiqueta-hipotesis'>hipótesis</span>"
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
    return (f"{etiqueta}: {alto['pct_ponderado']:.0f} % en "
            f"«{alto['categoria']}» frente a {bajo['pct_ponderado']:.0f} % en "
            f"«{bajo['categoria']}»")


def situadores(valores: dict, features: list[dict], cohorte: dict) -> None:
    numericas = [f for f in features if f["tipo"] == "numerico"
                 and f["nombre"] not in DERIVADAS
                 and cohorte.get(f["nombre"], {}).get("tipo") == "numerico"]
    for feat in numericas:
        c = cohorte[feat["nombre"]]
        grafico(graficos.situador(float(valores.get(feat["nombre"], 0)),
                                  c["percentiles"],
                                  feat.get("etiqueta", feat["nombre"]) + " · cohorte ponderada",
                                  T()), 74)


# --------------------------------------------------------------------------
# Umbral e impacto — fragment
# --------------------------------------------------------------------------
def indice_umbral(curva: dict, t: float) -> int:
    umbrales = curva["umbral"]
    return min(range(len(umbrales)), key=lambda i: abs(umbrales[i] - t))


def a_hist_oof() -> dict | None:
    """Histograma OOF para la franja; el fragment no recibe los artefactos."""
    return cargar_artefactos().get("clasificador", {}).get("histograma_oof")


@st.fragment
def bloque_umbral(clas: dict, curva: dict) -> None:
    """Mover el slider solo reejecuta esta función: nada se vuelve a predecir."""
    p_op = clas["punto_operativo"]
    refs = p_op["referencias"]
    presets = {
        "operativo": (float(p_op["umbral"]), "Punto operativo ★"),
        "por_defecto": (float(refs["umbral_05"]["umbral"]), "Neutro 0,5"),
        "f1": (float(refs["f1_optimo"]["umbral"]), "Máx. F1"),
    }

    html("<div class='eyebrow'>Dónde poner la vara</div>")
    html("<div class='sutil' style='margin:6px 0 10px 0;max-width:78ch'>"
         "Mover el umbral no recalcula la probabilidad del perfil: mueve la "
         "vara con la que decidimos señalar. <b>La probabilidad la pone el "
         "modelo; el umbral lo pones tú.</b></div>")

    col_p, col_s = st.columns([1, 1])
    with col_p:
        preset = st.radio(
            "Preajuste", list(presets) + ["libre"], index=0,
            format_func=lambda k: ("Umbral libre" if k == "libre" else
                                   f"{presets[k][1]} · {d(presets[k][0], 3)}"),
            label_visibility="collapsed", key="preset_umbral",
            help="Los tres primeros son puntos de corte ya elegidos con "
                 "criterios distintos. «Umbral libre» te deja moverlo a mano "
                 "para ver qué se gana y qué se pierde.")
    with col_s:
        if preset == "libre":
            umbral = st.slider("Umbral", 0.05, 0.95,
                               float(st.session_state.get("umbral_libre", 0.50)),
                               0.005, key="umbral_libre", format="%.3f",
                               help="Súbelo para señalar solo los casos más "
                                    "claros; bájalo para no dejar escapar "
                                    "informales, a costa de señalar formales.")
        else:
            umbral = presets[preset][0]
            st.slider("Umbral", 0.05, 0.95, umbral, 0.005, disabled=True,
                      format="%.3f",
                      key=f"slider_fijo_{preset}")

    html(f"<div class='sutil' style='margin-top:8px'>★ El punto operativo "
         f"aprobado exige <b>precisión ≥ 0,90 para la clase informal</b>: "
         f"{p_op['frase_exposicion']}</div>")

    proba = st.session_state.get("proba_informal")
    i = indice_umbral(curva, umbral)

    # ---- Consecuencias en vivo ----
    # Se calculan ANTES del veredicto porque la línea de «tres números» que va
    # pegada a la cifra grande necesita la cobertura y la precisión de este
    # mismo umbral. Los tres son números vivos: ninguno está escrito a mano.
    total = curva["n"]
    tp, fp = curva["tp"][i], curva["fp"][i]
    tn, fn = curva["tn"][i], curva["fn"][i]
    k = 1000 / total
    m_tp, m_fp, m_tn, m_fn = (round(tp * k), round(fp * k),
                              round(tn * k), round(fn * k))
    senalados = m_tp + m_fp
    prec = curva["precision_1"][i]
    rec = curva["recall_1"][i]
    pct_senalado = (tp + fp) / total * 100

    # Cabina: cifra + veredicto en una fila compacta, franja debajo, y las
    # consecuencias del umbral pegadas. Antes el medidor ocupaba 310 px para
    # decir un solo número y empujaba lo interactivo fuera de la pantalla.
    if proba is not None:
        senalado = proba >= umbral
        col = T()["senal_media"] if senalado else T()["senal_buena"]
        veredicto = ("Señalado para focalización" if senalado
                     else "Sin señal por este criterio")
        html(f"<div class='fila-veredicto'>"
             f"<span class='cifra-veredicto' style='color:{col}'>"
             f"{pct(proba, 1)}</span>"
             f"<span class='texto-veredicto' style='color:{col}'>"
             f"{veredicto}</span></div>")
        html(f"<div class='sutil' style='margin:-2px 0 10px 0'>"
             + ("Su probabilidad estimada supera el umbral. La señal apunta a "
                "una configuración de empleo, no es un veredicto sobre la "
                "persona." if senalado else
                "Su probabilidad estimada queda por debajo del umbral.")
             + "</div>")
        # Los tres porcentajes de esta pantalla miden cosas distintas y se
        # confunden con facilidad. Se nombran juntos, una sola vez, con los
        # valores del umbral que el usuario tiene puesto ahora mismo.
        html(f"<div class='sutil' style='margin:-4px 0 10px 0;max-width:88ch'>"
             f"<b>Tres números distintos:</b> "
             f"<b style='color:{col}'>{pct(proba, 1)}</b> es <b>DE ESTE "
             f"PERFIL</b> (así de informal es esta configuración) · "
             f"<b style='color:{T()['acento_alto']}'>{pct_senalado:.0f} %</b> "
             f"es <b>CUÁNTA POBLACIÓN</b> queda sobre el umbral · "
             f"<b style='color:{T()['senal_buena']}'>{round(prec * 100)} %</b> "
             f"es <b>LA PRECISIÓN</b> (de cada 100 señalados, cuántos "
             f"aciertas).</div>")
        # No hay anclas de URL: la navegación es por session_state. El botón
        # cambia de sección y marca el destino para que se vea al llegar.
        if st.button("¿Por qué tan alto? →", key="ir_demasiado_bueno",
                     type="tertiary",
                     help="Abre «¿Es demasiado bueno el clasificador?» en la "
                          "Ficha técnica: por qué un PR-AUC de 0,96 aquí es "
                          "coherente y no señal de fuga de información."):
            st.session_state["seccion"] = "ficha"
            st.session_state["resaltar_demasiado_bueno"] = True
            st.rerun(scope="app")
        grafico(graficos.franja_probabilidad(
            proba, umbral, a_hist_oof(), T()), 165)

    html("<div class='eyebrow' style='margin-top:4px'>Qué pasa con este umbral</div>")
    
    html(f"<div class='panel' style='margin-top:8px'>"
         f"<div style='font-size:15px;line-height:1.9;color:{T()['texto']}'>"
         f"Con umbral <b>{d(umbral, 3)}</b>:<br>"
         f"se señala al <b style='color:{T()['acento_alto']}'>"
         f"{pct_senalado:.0f} %</b> de los trabajadores · "
         f"de cada 100 señalados, <b style='color:{T()['senal_buena']}'>"
         f"{round(prec * 100)}</b> son informales · "
         f"se escapan <b style='color:{T()['senal_mala']}'>"
         f"{round((1 - rec) * 100)}</b> de cada 100 informales "
         f"(<i>falsos negativos</i>: el modelo no los señaló y sí lo eran)."
         f"</div></div>")

    # La pregunta que sigue a «se escapan N» siempre es la misma: ¿por qué no
    # cero? Se responde aquí, con la prevalencia leída del schema.
    with st.popover("¿Puede ser cero?", use_container_width=False):
        html(f"<div class='sutil' style='max-width:60ch'>Sí: con umbral 0 "
             f"señalas a todos y no se escapa nadie — pero la precisión cae a "
             f"<b>{pct(clas['prevalencia_train'], 0)}</b> (la prevalencia), "
             f"igual que señalar al azar. Por eso el umbral es una elección de "
             f"costos, no un defecto.</div>")

    if a_curva := curva.get("precision_1"):
        grafico(graficos.curva_precision_cobertura(
            curva["recall_1"], a_curva, (rec, prec),
            [(presets[k_][1], indice_umbral(curva, presets[k_][0]))
             for k_ in presets], curva, T()), 350)
        html("<div class='sutil'>El punto blanco es el umbral que tienes "
             "puesto. Las marcas son los tres preajustes. Cada punto de la "
             "curva es un umbral posible: subirlo te mueve arriba y a la "
             "izquierda (más acierto, más informales que se escapan); bajarlo, "
             "abajo y a la derecha.</div>")

    st.write("")
    html("<h3>Matriz de confusión: los cuatro resultados posibles</h3>")
    html("<div class='sutil' style='max-width:78ch;margin-bottom:8px'>"
         "Cada trabajador cae en una de estas cuatro casillas según lo que el "
         "modelo dijo y lo que realmente era. <b>Subir el umbral</b> reduce "
         "los falsos positivos y aumenta los falsos negativos: señalas menos "
         "gente, aciertas más en los que señalas, pero se te escapan más "
         "informales. <b>Bajarlo</b> hace exactamente lo contrario. No hay "
         "un punto que mejore las dos cosas a la vez; por eso hay que "
         "elegir.</div>")
    # 330, no 290: con 290 el SVG (520x286) escalado al ancho de la columna
    # salía por debajo del iframe y cortaba la fila inferior por la mitad.
    grafico(graficos.matriz_confusion(m_tp, m_fp, m_tn, m_fn, T()), 330)
    html(f"<div class='sutil'>Calculado sobre {n(total)} trabajadores del "
         f"entrenamiento con probabilidades <i>out-of-fold</i> —es decir, "
         f"estimadas para cada persona por un modelo que no la usó al "
         f"entrenar— y escalado a 1.000. Precisión de la clase informal: "
         f"{d(prec, 4)} · recall: {d(rec, 4)}.</div>")


# --------------------------------------------------------------------------
# Sección 1: estimación de ingreso
# --------------------------------------------------------------------------
def seccion_ingreso(schema: dict, art: dict) -> None:
    reg = schema["regresor"]
    b = art.get("regresor", {})

    n_train = int(reg["n_entrenamiento"]) + int(reg["n_test"])
    cabecera(
        "¿Cuánto gana al mes una persona con este perfil?",
        f"El modelo aprendió de {n(n_train)} trabajadores encuestados por el "
        "INEI (ENAHO 2025). Arma un perfil a la izquierda y estima su ingreso "
        "mensual típico. Dos avisos: es un promedio del año, no el sueldo del "
        "mes pasado, y solo cuenta pagos en dinero.",
        f"{reg['descripcion_target']}<br><br>"
        "«Imputada» significa que el INEI completó los valores que la persona "
        "no supo responder. «Deflactada» significa que los soles de todos los "
        "meses se llevaron a un mismo poder adquisitivo, para que sean "
        "comparables. «Anualizada ÷ 12» significa que se suma el ingreso de "
        "todo el año y se reparte en doce meses iguales: por eso es un ingreso "
        "estabilizado y no el del mes de la entrevista. La población son "
        "ocupados de 14 años o más con ingreso laboral positivo.",
        seccion="ingreso")
    st.write("")

    izq, der = st.columns([35, 65], gap="large")
    with izq:
        html("<div class='eyebrow'>Perfil del trabajador</div>")
        fila = formulario(reg["features"], "reg")
        st.write("")
        if st.button("Estimar ingreso", type="primary", key="btn_reg"):
            modelo = cargar_modelo("regresor_e9.joblib")
            st.session_state["ingreso"] = float(
                modelo.predict(fila[columnas_esperadas(modelo)])[0])

    with der:
        ingreso = st.session_state.get("ingreso")
        if ingreso is None:
            html("<div class='panel'><div class='panel-titulo'>Sin estimación "
                 "todavía</div><div class='sutil'>Describe el perfil y pulsa "
                 "«Estimar ingreso». Mientras tanto, así se distribuye la "
                 "cohorte ponderada.</div></div>")
            st.write("")
            if b.get("cohorte"):
                situadores(st.session_state.get("valores_reg", {}),
                           reg["features"], b["cohorte"])
            return

        smear = float(reg["smearing_duan"])
        media = (ingreso + 1) * smear - 1
        ing_art = b.get("ingreso", {})
        mediana_pob = ing_art.get("mediana_ponderada", reg["ingreso_mediano_train"])

        tarjetas = [
            tarjeta("ingreso típico", f"S/ {n(ingreso)}",
                    color=T()["acento_alto"],
                    llano=f"La mitad de los perfiles como este gana menos de "
                          f"S/ {n(ingreso)}; la otra mitad, más."),
            tarjeta("ingreso esperado", f"S/ {n(media)}",
                    llano="El promedio. Es más alto porque unos pocos sueldos "
                          "muy grandes lo jalan hacia arriba.",
                    nota=f"Incluye la corrección × {d(smear, 3)} que compensa "
                         f"haber entrenado en logaritmo — ver «Cómo leer estas "
                         f"tres cifras»."),
            tarjeta("mediana del país", f"S/ {n(float(mediana_pob))}",
                    llano=f"Para comparar: la mitad de todos los trabajadores "
                          f"del país gana menos de S/ {n(float(mediana_pob))}."),
        ]

        # IQR de casos comparables
        v = st.session_state.get("valores_reg", {})
        clave_comp = None
        if ing_art.get("comparables") and {"sexo", "area", "anios_educ"} <= set(v):
            educ = float(v["anios_educ"])
            banda = ("0-6" if educ <= 6 else "7-11" if educ <= 11
                     else "12-14" if educ <= 14 else "15+")
            clave_comp = f"{v['sexo']}|{v['area']}|{banda}"
            comp = ing_art["comparables"].get(clave_comp)
            if comp:
                tarjetas.append(tarjeta(
                    "casos comparables (<span class='pista' title='Un "
                    "percentil marca el punto por debajo del cual queda ese "
                    "porcentaje de los casos: el P25 deja debajo al 25 % y el "
                    "P75, al 75 %. Entre los dos vive la mitad central.'>"
                    "P25–P75</span>)",
                    f"S/ {n(comp['p25'])} – {n(comp['p75'])}",
                    f"{v['sexo'].lower()}, área {v['area'].lower()}, "
                    f"{banda} años de educación · mediana S/ {n(comp['p50'])} · "
                    f"n={n(comp['n'])}",
                    llano=f"De los {n(comp['n'])} encuestados parecidos a este "
                          f"perfil, la mitad del medio gana entre "
                          f"S/ {n(comp['p25'])} y S/ {n(comp['p75'])}: un 25 % "
                          f"gana menos que S/ {n(comp['p25'])} y un 25 % más "
                          f"que S/ {n(comp['p75'])}."))

        html("<div class='rejilla-tarjetas'>" + "".join(tarjetas) + "</div>")
        st.write("")
        mae = reg["metricas_test"]["mae_mediana"]
        html(f"<div class='senal senal-aviso'><div>▲</div><div>"
             f"<b>Esta cifra es un ingreso típico, no una promesa de sueldo.</b> "
             f"En promedio se equivoca en unos S/ {n(mae)} por persona. Sirve "
             f"para comparar perfiles entre sí, no para decirle a nadie cuánto "
             f"va a cobrar.</div></div>")

        with st.expander("Cómo leer estas tres cifras"):
            html(f"<div class='sutil'>"
                 f"<b>Por qué la primera cifra es una mediana y no un "
                 f"promedio.</b> El modelo aprende sobre el logaritmo del "
                 f"ingreso, porque unos pocos sueldos altísimos deforman "
                 f"cualquier promedio. Al deshacer ese logaritmo se obtiene la "
                 f"<i>mediana condicional</i>: el valor que parte al grupo en "
                 f"dos mitades iguales. Es la cifra honesta para «cuánto gana "
                 f"alguien así».<br><br>"
                 f"<b>De dónde sale la corrección × {d(smear, 3)}.</b> Para pasar "
                 f"de la mediana al promedio no basta con deshacer el "
                 f"logaritmo: hay que multiplicar por un factor que recupera la "
                 f"masa de la cola alta. Es la corrección de <i>smearing</i>"
                 f"{ref('duan1983')} de "
                 f"Duan (1983), estimada con los residuos de validación cruzada "
                 f"del entrenamiento. Sin ella, el promedio saldría "
                 f"subestimado en torno a un "
                 f"{(1 - 1 / smear) * 100:.0f} %.<br><br>"
                 f"<b>Qué queda fuera.</b> El target es solo dinero: el pago en "
                 f"especie y el autoconsumo (que recibe el 24,6 % de los "
                 f"ocupados, sobre todo en el agro) no se cuentan. Y es un "
                 f"ingreso anualizado y repartido en doce meses, no el del mes "
                 f"de la entrevista.<br><br>"
                 f"<b>Error de la estimación.</b> MAE en el conjunto de prueba: "
                 f"S/ {n(mae)}. La incertidumbre individual es grande y está "
                 f"declarada: el modelo ordena perfiles, no liquida sueldos."
                 f"</div>")

    imp = b.get("importancia_permutacion")
    if st.session_state.get("ingreso") is not None and imp:
        st.divider()
        html("<h2>Si barajamos al azar esta variable, ¿cuántos soles más se "
             "equivoca el modelo?</h2>")
        html("<div class='entradilla'>Eso mide la <b>importancia por "
             "permutación</b>: se desordena una sola variable, se vuelve a "
             "estimar, y se mira cuánto empeora. Cuanto más empeora, más "
             "dependía el modelo de esa variable. <b>MAE</b> es el error "
             "promedio en soles.</div>")
        st.write("")
        etiquetas = {f["nombre"]: f.get("etiqueta", f["nombre"])
                     for f in reg["features"]}
        grafico(graficos.barras_importancia(
            imp["variables"], imp["media"], imp["desviacion"], T(),
            unidad="aumento del MAE al permutar (S/)", etiquetas=etiquetas),
            30 + len(imp["variables"]) * 30 + 18)


# --------------------------------------------------------------------------
# Sección 2: informalidad
# --------------------------------------------------------------------------
def seccion_informalidad(schema: dict, art: dict) -> None:
    clas = schema["clasificador"]
    a = art.get("clasificador", {})

    cabecera(
        "¿Qué tan probable es que un empleo como este sea informal?",
        "Informal según la regla del INEI: independiente sin RUC, o dependiente "
        "sin aporte a pensión. El modelo estima esa probabilidad para el perfil "
        "que armes. Señala configuraciones de empleo, no juzga personas.",
        f"{clas['descripcion_target']} {clas.get('encuadre', '')}<br><br>"
        "La regla se derivó de dos preguntas de la encuesta: a los "
        "independientes y empleadores se les pregunta si tienen RUC (registro "
        "tributario); a los dependientes, si les aportan a un sistema de "
        "pensiones. La derivación se validó contra la tasa oficial: "
        "reconstruida sobre todos los ocupados da 67,3 % frente al 70,2 % que "
        "publica el INEI para 2025." + ref("inei_informal"),
        seccion="informalidad")
    st.write("")

    izq, der = st.columns([35, 65], gap="large")
    with izq:
        html("<div class='eyebrow'>Perfil del trabajador</div>")
        fila = formulario(clas["features"], "clf")
        st.write("")
        if st.button("Estimar probabilidad", type="primary", key="btn_clf"):
            modelo = cargar_modelo("clasificador_gb.joblib")
            st.session_state["proba_informal"] = float(
                modelo.predict_proba(fila[columnas_esperadas(modelo)])[:, 1][0])

    with der:
        if st.session_state.get("proba_informal") is None:
            html("<div class='panel'><div class='panel-titulo'>Sin estimación "
                 "todavía</div><div class='sutil'>Describe el perfil y pulsa "
                 "«Estimar probabilidad». Mientras tanto, así se distribuye la "
                 "cohorte ponderada.</div></div>")
            st.write("")
            if a.get("cohorte"):
                situadores(st.session_state.get("valores_clf", {}),
                           clas["features"], a["cohorte"])
        elif a.get("curva_umbral"):
            bloque_umbral(clas, a["curva_umbral"])
        else:
            html("<div class='senal senal-aviso'><div>▲</div><div>Falta "
                 "<code>models/ui_artifacts.json</code>. Corre "
                 "<code>python src/09_precomputar_ui.py</code>.</div></div>")

    if st.session_state.get("proba_informal") is not None and a.get("dependencia_parcial"):
        st.divider()
        html("<h2>Qué empuja la probabilidad hacia arriba o hacia abajo</h2>")
        html("<div class='entradilla'>Cada gráfico responde: si solo cambiara "
             "esta característica y todo lo demás se quedara igual, ¿cómo se "
             "movería la probabilidad? En cada uno, el color marca el valor del "
             "perfil que armaste. Su nombre técnico es <b>dependencia "
             "parcial</b>.</div>")
        with st.expander("Detalle técnico"):
            html("<div class='sutil'>Son curvas de <b>dependencia parcial</b>: "
                 "el modelo predice sobre toda la muestra fijando esta variable "
                 "en cada valor posible y promediando el resto, lo que aísla su "
                 "efecto marginal. <b>No son tasas observadas:</b> la tasa real "
                 "de informalidad en un grupo mezcla el efecto de esta variable "
                 "con el de todas las que la acompañan. Por eso el efecto "
                 "parcial de «Rural» y el porcentaje real de informalidad rural "
                 "no son el mismo número, y no deberían serlo.</div>")
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
            etiqueta = feat.get("etiqueta", nombre)
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
                        html(f"<div class='sutil'>La línea punteada marca "
                             f"<b>{n(float(v))}</b>, el valor de tu perfil.</div>")
                    else:
                        html(f"<div class='sutil'>La barra en color es "
                             f"«{v}», el valor de tu perfil. Pasa el cursor por "
                             f"cualquier barra para ver su cifra.</div>")
                t = tasas.get(nombre)
                if t:
                    dato = (f"en la muestra, {t['max']['pct_ponderado']:.0f} % "
                            f"de «{t['max']['categoria']}» tiene empleo "
                            f"informal, frente a "
                            f"{t['min']['pct_ponderado']:.0f} % de "
                            f"«{t['min']['categoria']}».")
                elif perfil["tipo"] == "numerico" and len(perfil["efecto"]) > 1:
                    # Sin categorías que contrastar, el dato es la tendencia:
                    # de dónde a dónde se mueve la probabilidad de punta a punta.
                    ini, fin = perfil["efecto"][0], perfil["efecto"][-1]
                    v0, v1 = perfil["valores"][0], perfil["valores"][-1]
                    verbo = "baja" if fin < ini else "sube"
                    dato = (f"al pasar de {n(float(v0))} a {n(float(v1))}, la "
                            f"probabilidad estimada {verbo} de "
                            f"{ini * 100:.0f} % a {fin * 100:.0f} %.")
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
    lineas = [f"INGRESO = {coefs.get('const', 0):,.2f}"]
    for k in orden[1:]:
        if k in coefs:
            v = coefs[k]
            lineas.append(f"  {'+' if v >= 0 else '−'} {abs(v):,.2f} · {k}")
    return f"<div class='eyebrow'>{titulo}</div><div class='ecuacion'>" + \
           "\n".join(lineas) + "</div>"


def seccion_torneo(schema: dict, art: dict) -> None:
    t = art.get("torneo")
    if not t:
        html("<div class='senal senal-aviso'><div>▲</div><div>Falta el bloque "
             "torneo en <code>ui_artifacts.json</code>.</div></div>")
        return
    aut = t["autopsia"]

    cabecera(
        "¿Por qué este modelo y no otro?",
        "Nueve maneras de armar el mismo modelo de ingreso compitieron con reglas "
        "idénticas: misma muestra, misma partición, misma vara de medir. Gana "
        "la que se equivoca menos en soles con datos que no vio. Aquí está la "
        "comparación completa, incluida la versión inicial del curso: su "
        "diagnóstico destapó un error en los datos de origen que afectaba a "
        "cualquiera que usara esa base sin conocerlo. <b>Todo lo de esta "
        "sección es el modelo de INGRESO</b> (una regresión: estima soles). El clasificador de informalidad no compite aquí; su comparación está en la "
        "Ficha técnica.",
        "Las nueve especificaciones comparten muestra, partición "
        "entrenamiento/prueba y los mismos cinco pliegues de validación "
        "cruzada, con semilla fija. Sin eso el ranking no sería comparable. La "
        "selección se hace por el error de validación cruzada y no por el de "
        "prueba: elegir por prueba tras comparar nueve candidatos sería "
        "seleccionar sobre el conjunto con el que luego se dice ser honesto.",
        seccion="torneo")

    # ---- Acto 1 y 2 ----
    html("<h2>Acto 1 · La ecuación inicial</h2>")
    html("<div class='entradilla'>Cada línea suma o resta soles al ingreso "
         "estimado. Por ejemplo, «+ 11,47 · urbano» significa: si la persona "
         "vive en zona urbana, súmale S/ 11,47 al total.</div>")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        html(_ecuacion(aut["ecuacion_inicial"],
                       "Versión inicial (con el centinela sin limpiar)"))
        html("<div class='sutil' style='margin-top:8px'>+11 soles por residir "
             "en zona urbana y +6 por ser hombre: incompatible con las brechas "
             "conocidas del mercado laboral peruano. <b>El problema no estaba "
             "en cómo se modeló, sino en los datos.</b> El INEI codifica «no "
             "sabe» como 999999, y ese código se estaba leyendo como un "
             "ingreso real de 999.999 soles. Unos pocos registros así "
             "deforman cualquier regresión, la haga quien la haga. Encontrarlo "
             "no fue suerte: salió de revisar si los coeficientes tenían "
             "sentido económico, que es exactamente lo que hay que hacer "
             "antes de dar un modelo por bueno.</div>")
    with c2:
        html(_ecuacion(aut["corrida_limpia"]["coefs"],
                       "Misma especificación, centinela 999999 → NaN"))
        html(f"<div class='sutil' style='margin-top:8px'>Con solo convertir el "
             f"código de faltante del INEI a NaN, el R² pasa de "
             f"<b>{d(aut['corrida_sucia']['r2'], 3)}</b> a "
             f"<b>{d(aut['corrida_limpia']['r2'], 3)}</b> y todos los signos se "
             f"vuelven económicamente plausibles.</div>")

    html("<h2>Acto 2 · El diagnóstico</h2>")
    html(f"<div class='panel'><div style='line-height:1.8;font-size:13px;color:"
         f"{T()['texto']}'>"
         f"<b>1 · El centinela.</b> El {d(aut['pct_centinelas'], 2)} % de la "
         f"población tenía el código 999999 («no sabe») leído como ingreso "
         f"real de un millón de soles. R² sucio: "
         f"{d(aut['corrida_sucia']['r2'], 3)}; limpio: "
         f"{d(aut['corrida_limpia']['r2'], 3)}.<br>"
         f"<b>2 · La colinealidad (dos variables que dicen lo mismo).</b> "
         f"Años de educación y nivel educativo "
         f"detallado son la misma variable codificada dos veces: juntos "
         f"disparan el VIF a ~20 y voltean signos. No conviven en ninguna "
         f"especificación del torneo.<br>"
         f"<b>3 · La escala.</b> El ingreso limpio tiene asimetría "
         f"{d(aut['asimetria_limpia'], 2)}: en niveles, unos pocos sueldos altos "
         f"dominan la regresión. La familia principal trabaja en log "
         f"(ecuación de Mincer) y vuelve a soles con la corrección de Duan."
         f"</div></div>")

    # ---- Acto 3: tabla + barras ----
    html("<h2>Acto 3 · El torneo</h2>")
    filas = ""
    for f in t["tabla"]:
        clase = " class='destacada'" if f["ID"] == t["desplegada"] else ""
        marca = " · desplegada" if f["ID"] == t["desplegada"] else (
            " · explicativa" if f["ID"] == t["explicativa"] else "")
        filas += (f"<tr{clase}><td>{f['ID']}{marca}</td>"
                  f"<td style='text-align:left'>{f['especificacion'][:58]}</td>"
                  f"<td>{n(f['MAE_cv'])}</td><td>{n(f['MAE_test'])}</td>"
                  f"<td>{d(f['R2_test_soles'], 3)}</td>"
                  f"<td>{f['interpretabilidad']}</td></tr>")
    html(f"<table class='tabla'><thead><tr><th>ID</th><th>Especificación</th>"
         f"<th>MAE cv (S/)</th><th>MAE test (S/)</th><th>R² soles</th>"
         f"<th>Interpretab.</th></tr></thead><tbody>{filas}</tbody></table>")
    html("<div class='sutil' style='margin-top:10px;max-width:78ch'>La "
         "selección usa el MAE de validación cruzada en train — elegir por "
         "test tras comparar nueve especificaciones sería seleccionar sobre "
         "el conjunto de evaluación. El MAE de test se reporta como estimación "
         "honesta del modelo ya elegido.</div>")
    st.write("")
    orden = sorted(t["tabla"], key=lambda f: f["MAE_cv"])
    grafico(graficos.barras_mae([f["ID"] for f in orden],
                                [f["MAE_cv"] for f in orden],
                                t["desplegada"], T()),
            28 + len(orden) * 32 + 30)

    # ---- Qué variable entra dónde y cuánto pesa ----
    vb = t.get("variables")
    if vb:
        html("<h2>Qué variable entra dónde y cuánto pesa</h2>")
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
                filas += (f"<tr><td style='text-align:left'>{f['etiqueta']}"
                          f"</td>{celdas}</tr>")
            html(f"<table class='tabla'><thead><tr><th>Variable</th>{cab}"
                 f"</tr></thead><tbody>{filas}</tbody></table>")
            html(f"<div class='sutil' style='margin-top:8px'>"
                 f"{vb['nota_matriz']}</div>")
        with col_i:
            imp = art.get("regresor", {}).get("importancia_permutacion")
            if imp:
                html(f"<div class='eyebrow'>Peso en {t['desplegada']} · "
                     "importancia por permutación</div>")
                st.write("")
                etiquetas = {f["nombre"]: f.get("etiqueta", f["nombre"])
                             for f in schema["regresor"]["features"]}
                # versiones cortas: esta columna es más angosta que la de ingreso
                etiquetas |= {"horas_total": "Horas semanales",
                              "exper2": "Experiencia²"}
                grafico(graficos.barras_importancia(
                    imp["variables"], imp["media"], imp["desviacion"], T(),
                    unidad="aumento del MAE al permutar (S/)",
                    etiquetas=etiquetas),
                    30 + len(imp["variables"]) * 30 + 18)
                html("<div class='sutil'>La matriz dice quién entra; estas "
                     "barras dicen cuánto pesa en el modelo desplegado "
                     "(precomputado en models/ui_artifacts.json).</div>")

        l7 = vb.get("lasso_e7")
        if l7:
            html("<h3>Qué variables sobran: lo que descartó el Lasso en E7</h3>")
            html("<div class='sutil' style='max-width:78ch'>El <b>Lasso</b> es un método que penaliza tener muchas variables: deja en cero las que no "
                 "aportan lo suficiente y así elige solas cuáles se quedan. Una <b>dummy</b> es una columna de sí/no que representa una categoría "
                 "(por ejemplo, «trabaja en el sector X»).</div>")
            drop_manual = set(l7.get("drop_manual_e6", []))
            eliminadas = l7["eliminadas"]
            coincide = sorted(drop_manual & set(eliminadas))
            extras = [e for e in eliminadas if e not in drop_manual]
            partes = [
                f"De <b>{l7['candidatas']}</b> columnas candidatas, el Lasso "
                f"(α = {d(l7['alpha'], 5)}) conservó <b>{l7['conservadas']}</b> "
                f"y eliminó {len(eliminadas)}: "
                + ", ".join(f"<code>{e}</code>" for e in eliminadas)
                + f" ({l7.get('fuente', '')})."]
            if coincide:
                partes.append(
                    "La selección automática <b>confirmó la depuración manual "
                    "de E6</b>: eliminó "
                    + ", ".join(f"<code>{c}</code>" for c in coincide)
                    + ", la misma dummy que E6 suelta a mano por colinealidad "
                      "perfecta con categoría=Trabajador del hogar.")
            if extras:
                partes.append(
                    "Donde discrepa: además descartó "
                    + ", ".join(f"<code>{e}</code>" for e in extras)
                    + ", dummies de categorías con poca masa muestral que E6 "
                      "conserva — la penalización del Lasso castiga a los "
                      "grupos chicos, no necesariamente a los irrelevantes "
                      "(la cautela de Belloni et al. 2014 que el reporte "
                      "declara).")
            html(f"<div class='panel'><div style='font-size:13px;"
                 f"line-height:1.75;color:{T()['texto']}'>"
                 + " ".join(partes) + "</div></div>")

        desc = vb.get("descartadas")
        if desc:
            html("<h3>Variables descartadas y por qué</h3>")
            filas = "".join(
                f"<tr><td style='text-align:left'>{d['nombre']}</td>"
                f"<td style='text-align:left'>{d['motivo']}</td>"
                f"<td style='text-align:left'>"
                f"{enlace_evidencia(d['evidencia'])}</td></tr>" for d in desc)
            html(f"<table class='tabla'><thead><tr><th>Variable</th>"
                 f"<th>Motivo</th><th>Evidencia</th></tr></thead>"
                 f"<tbody>{filas}</tbody></table>")

    e6 = t["explicativo_e6_ponderado"]["efectos_pct"]
    html("<h2>Las dos lecturas finales</h2>")
    html(f"<div class='panel'><div style='line-height:1.8;font-size:13px;color:"
         f"{T()['texto']}'>"
         f"<b>La predictiva (E9, desplegada):</b> Gradient Boosting sobre log "
         f"del ingreso. La brecha frente a la mejor OLS estima lo que aportan "
         f"las no linealidades e interacciones que la forma lineal no captura."
         f"<br><b>La explicativa (E6, ponderada a población):</b> cada año de "
         f"educación se asocia a <b>{e6.get('anios_educ', 0):+.1f} %</b> de "
         f"ingreso; ser hombre, <b>{e6.get('hombre', 0):+.1f} %</b>; residir "
         f"en zona urbana, <b>{e6.get('urbano', 0):+.1f} %</b>; trabajar como "
         f"independiente, <b>{e6.get('categoria_Independiente', 0):+.1f} %</b>; "
         f"una empresa de hasta 20 personas frente a una de más de 500, "
         f"<b>{e6.get('tamano_empresa_Hasta 20', 0):+.1f} %</b>; Sierra Norte "
         f"frente a Lima Metropolitana, "
         f"<b>{e6.get('dominio_Sierra Norte', 0):+.1f} %</b>.</div></div>")

    sens = t.get("sensibilidad_especie", [])
    if len(sens) == 2:
        html("<h2>Robustez: ¿y el ingreso en especie?</h2>")
        html(f"<div class='sutil' style='max-width:78ch'>El 24,6 % de los "
             f"ocupados recibe pago en especie o autoconsumo (concentrado en "
             f"el agro rural). Si excluirlo sesgara el premio urbano, la "
             f"narrativa entera quedaría en duda — así que se midió: con "
             f"target solo monetario el premio urbano es "
             f"<b>{d(sens[0]['premio_urbano_pct'], 1)} %</b>; añadiendo especie, "
             f"<b>{d(sens[1]['premio_urbano_pct'], 1)} %</b>. La exclusión queda "
             f"validada como robusta y declarada.</div>")


# --------------------------------------------------------------------------
# Sección 4: ficha técnica
# --------------------------------------------------------------------------
# Hallazgos de la auditoría interna. Resumen de INFORME_AUDITORIA.md: se
# escriben aquí a mano y a propósito, porque son juicios sobre el proyecto, no
# métricas que se puedan recalcular. La cifra de cada uno sí sale del informe.
#
# `origen` dice DÓNDE NACIÓ el problema, que es distinto de en qué estado
# está. Un fallo de la fuente y uno propio se corrigen igual pero no enseñan
# lo mismo. Un hallazgo puede tener dos orígenes: el del R² es a la vez
# decisión propia (tres versiones circulando) y documentación (dos citas que
# no sostenían lo que se les atribuía).
ORIGENES = {
    "datos": ("origen-datos", "datos de origen",
              "el problema venía en la fuente (INEI) y afectaría a cualquiera "
              "que use estos datos. Ej.: el centinela 999999."),
    "propia": ("origen-propia", "decisión propia",
               "lo introdujimos nosotros al elegir o resumir. Ej.: la rejilla "
               "acotada, el 88,6 % mal etiquetado, las tres afirmaciones "
               "contradictorias del R²."),
    "doc": ("origen-doc", "documentación",
            "citas que no decían lo que se les atribuía. Ej.: Lemieux y "
            "Heckman sin R² reportado."),
}

AUDITORIA = [
    {"sev": "corregido", "origen": ["datos"],
     "titulo": "El código de faltante leído como un ingreso",
     "texto": "El INEI codifica «no sabe» como 999999. Ese valor se estaba "
              "leyendo como un ingreso real de 999.999 soles, y con él la "
              "regresión daba +11 soles por vivir en zona urbana. Convertirlo "
              "a dato faltante subió el R² de 0,023 a 0,248 y devolvió el "
              "sentido económico a todos los coeficientes."},
    {"sev": "a corregir", "origen": ["propia"],
     "titulo": "La rejilla de hiperparámetros estaba acotada",
     "texto": "Los tres hiperparámetros del modelo desplegado quedaron en el "
              "borde de los valores que se probaron: señal de que el óptimo "
              "estaba fuera. Se amplió y se volvió a buscar: el error baja de "
              "S/ 610,90 a S/ 607,31 y los tres quedan ya en el interior. La "
              "mejora es sistemática (gana en los 5 pliegues) pero de 0,59 %, "
              "así que NO se promovió: no justifica regenerar el modelo en "
              "producción. Las rejillas del clasificador siguen sin revisar."},
    {"sev": "corregido", "origen": ["propia"],
     "titulo": "Una cifra del INEI con la etiqueta equivocada",
     "texto": "Se publicaba que el gradiente por tamaño de empresa «replica el "
              "patrón oficial (88,6 % en microempresas)». Ese 88,6 % es del "
              "INEI y corresponde al tramo de 1 a 10 trabajadores, que no es "
              "la categoría «Hasta 20» de este proyecto — cuyo valor propio es "
              "81,1 %. No era un dato inventado, era una comparación mal "
              "etiquetada."},
    {"sev": "corregido", "origen": ["propia", "doc"],
     "titulo": "Tres afirmaciones distintas sobre el mismo dato",
     "texto": "Sobre el R² esperable circulaban «0,4–0,5», «rara vez supera "
              "0,4» y «ningún R² supera 0,5», en cuatro sitios a la vez. Al ir "
              "a las fuentes resultó que ni Lemieux (2006) ni Heckman et al. "
              "(2006) reportan un R², así que no se les podía citar para eso. "
              "Ahora la afirmación se define una sola vez, sobre los cuadros "
              "de Mincer y Card, y se dice cuál es lectura propia."},
    {"sev": "estructural", "origen": [],
     "titulo": "La solución, para que no vuelva a pasar",
     "texto": "Los dos primeros problemas tenían la misma raíz: cifras "
              "escritas a mano que nadie vuelve a comprobar. Ahora las tasas "
              "por grupo se calculan en el precómputo (`tasas_observadas`) y "
              "los títulos de los gráficos se generan desde ahí, y la "
              "bibliografía vive en un solo módulo. Una cifra escrita a mano "
              "puede quedar obsoleta en silencio; una calculada, no."},
]


def seccion_auditoria() -> None:
    """Los hallazgos de auditoría del propio proyecto, publicados."""
    html("<h2>Qué encontró la auditoría de este proyecto</h2>")
    html("<div class='entradilla'>Antes de publicar, este proyecto pasó por "
         "una revisión de consistencia: cada cifra se cruzó contra el archivo "
         "que la genera, cada cita contra su fuente original, y cada decisión "
         "de modelado contra su evidencia. Verificar el propio trabajo es "
         "parte del método — lo que no siempre se hace es publicar el "
         "resultado. Esto fue lo que apareció, clasificado según dónde nació "
         "cada problema.</div>")
    html("<div class='leyenda-origen'>" + "".join(
        f"<div><span class='origen {clase}'>{etiqueta}</span>"
        f"<span>{glosa}</span></div>"
        for clase, etiqueta, glosa in ORIGENES.values()) + "</div>")
    colores = {"corregido": ("ref-abierto", "corregido"),
               "a corregir": ("ref-pago", "pendiente"),
               "estructural": ("etiqueta-dato", "solución de fondo")}
    filas = []
    for h in AUDITORIA:
        clase, etiqueta = colores[h["sev"]]
        origenes = "".join(
            f"<span class='origen {ORIGENES[o][0]}'>{ORIGENES[o][1]}</span>"
            for o in h["origen"])
        filas.append(
            f"<div class='hallazgo'>"
            f"<div class='hallazgo-cab'>"
            f"<span class='ref-acceso {clase}'>{etiqueta}</span>{origenes}"
            f"<b>{h['titulo']}</b></div>"
            f"<div class='sutil'>{h['texto']}</div></div>")
    html(f"<div class='ref-lista'>{''.join(filas)}</div>")
    html("<div class='sutil' style='margin-top:16px'>El informe completo, con "
         "los hallazgos clasificados por severidad y la lista de lo que quedó "
         "sin verificar, está en "
         f"{enlace_evidencia('INFORME_AUDITORIA.md')} del repositorio.</div>")
    # La sección cierra con el método, no con el enlace: es la frase que dice
    # por qué los hallazgos siguen publicados en vez de haberse borrado.
    html("<div class='sutil' style='margin-top:12px;max-width:78ch'>Los "
         "problemas de origen se corrigen y se documentan; los propios se "
         "corrigen y se aprende de ellos; los de cita se verifican yendo al "
         "texto completo. Ninguno se borra: un hallazgo corregido en silencio "
         "es un hallazgo desperdiciado.</div>")


def seccion_ficha(schema: dict, art: dict) -> None:
    clas, reg = schema["clasificador"], schema["regresor"]
    a = art.get("clasificador", {})
    meta = art.get("meta", {})

    cabecera(
        "¿Qué tan fiables son estos dos modelos?",
        "Qué miden, dónde fallan y qué no se puede concluir con ellos. Son dos "
        "modelos distintos y cada uno se juzga con las métricas de su familia: "
        "no se pueden comparar entre sí.",
        "Un regresor estima una cantidad y se mide por el error en soles; un "
        "clasificador estima una probabilidad y se mide por cómo ordena los "
        "casos. Un regresor no tiene umbral, así que no puede tener curva ROC; "
        "un clasificador no tiene error en soles. Poner las métricas de uno en "
        "el otro no es más rigor, es una confusión de categorías.",
        seccion="ficha técnica")

    # Al llegar desde «¿Por qué tan alto? →» se marca el bloque de destino. No
    # se usa un id: Streamlit sanea el HTML de st.markdown y borra el atributo,
    # y de todos modos la navegación es por session_state, no por URL — no hay
    # ancla que haga scroll. Este h2 es lo primero tras la cabecera, así que al
    # cambiar de sección ya se ve; el resalte solo dice «es este».
    resaltar = st.session_state.pop("resaltar_demasiado_bueno", False)
    html(f"<h2{' class=\"resaltado\"' if resaltar else ''}>"
         f"¿Es demasiado bueno el clasificador de informalidad?</h2>")
    filas = ""
    for f in a.get("comparacion", []):
        es_gb = "Gradient" in f["algoritmo"]
        clase = " class='destacada'" if es_gb else " class='atenuada'"
        filas += (f"<tr{clase}><td>{f['algoritmo']}"
                  f"{' · desplegado' if es_gb else ''}</td>"
                  f"<td>{d(f['PRAUC_cv'], 4)}</td><td>{d(f['PRAUC_test'], 4)}</td>"
                  f"<td>{d(f['ROCAUC_test'], 4)}</td><td>{d(f['Brier_test'], 4)}</td></tr>")
    html(f"<table class='tabla'><thead><tr><th>Algoritmo</th><th>PR-AUC cv</th>"
         f"<th>PR-AUC test</th><th>ROC-AUC test</th><th>Brier</th></tr></thead>"
         f"<tbody>{filas}</tbody></table>")
    # El gradiente sale de tasas_observadas, no escrito a mano. Antes citaba el
    # 88,6 % del INEI etiquetado como «microempresas», que el lector mapea a la
    # categoría «Hasta 20» de este proyecto — y esa vale 81,1 %. La cifra del
    # INEI es del tramo 1-10, que no es el mismo (auditoría 20/08/2026, AC-5).
    tam = a.get("tasas_observadas", {}).get("tamano_empresa")
    gradiente = ""
    if tam:
        # Se muestran los DOS y se dice que los tramos no coinciden: «Hasta 20»
        # no es «1-10». Antes solo aparecía la cifra del INEI, etiquetada
        # «microempresas», y se leía como si fuera el dato propio.
        gradiente = (f". El gradiente por tamaño de empresa va en el mismo "
                     f"sentido que el oficial: aquí "
                     f"{d(tam['max']['pct_ponderado'], 1)} % de informalidad "
                     f"en «{tam['max']['categoria']}» frente a "
                     f"{d(tam['min']['pct_ponderado'], 1)} % en "
                     f"«{tam['min']['categoria']}» (ponderado a población, es decir, "
                     f"contando a cada encuestado por las personas que "
                     f"representa); el INEI "
                     f"reporta 88,6 % en empresas de <b>1 a 10 "
                     f"trabajadores</b> y 15,6 % en las de más de 50. Los "
                     f"tramos no son los mismos, así que las dos cifras no "
                     f"son directamente comparables")
    html(f"<div class='sutil' style='margin-top:10px;max-width:78ch'>Baseline "
         f"de PR-AUC = prevalencia ({d(clas['prevalencia_train'], 3)} muestral; "
         f"{d(clas['prevalencia_ponderada'], 3)} ponderada). La regla del target "
         f"se validó contra la tasa oficial: reconstruida sobre todos los "
         f"ocupados da 67,3 % frente al 70,2 % que publica el "
         f"INEI{ref('inei_informal')}{gradiente}. La definición de empleo "
         f"informal que se replica es la internacional de la OIT "
         f"(17.ª CIET){ref('oit_17ciet')}.</div>")

    abl = clas.get("ablacion", [])
    if abl:
        html("<h3>Ablación estructural</h3>")
        filas = ""
        for i, f in enumerate(abl):
            clase = " class='destacada'" if i == 0 else " class='atenuada'"
            filas += (f"<tr{clase}><td>{f['variante']}</td>"
                      f"<td>{f['n_predictores']}</td><td>{d(f['PRAUC_cv'], 4)}</td>"
                      f"<td>{d(f['ROCAUC_cv'], 4)}</td>"
                      f"<td>{d(f.get('caida_PRAUC_cv', 0), 4)}</td></tr>")
        html(f"<table class='tabla'><thead><tr><th>Variante</th><th>vars</th>"
             f"<th>PR-AUC cv</th><th>ROC-AUC cv</th><th>caída</th></tr></thead>"
             f"<tbody>{filas}</tbody></table>")
        html("<div class='sutil' style='margin-top:10px;max-width:78ch'>"
             "Tamaño de empresa y categoría ocupacional son las variables más "
             "próximas a la definición operativa del target: en microempresas, "
             "no aportar a pensiones es casi estructural. Aun quitando ambas, "
             "el PR-AUC se sostiene en 0,94: educación, área, rama y horas "
             "cargan la señal restante. El clasificador identifica la "
             "<b>configuración laboral</b> asociada a la informalidad — es una "
             "herramienta de focalización, no de predicción a futuro, y por "
             "eso su PR-AUC alto es coherente, no sospechoso.</div>")

    if a.get("calibracion"):
        html("<h3>¿Significan algo las probabilidades?</h3>")
        st.write("")
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1:
            grafico(graficos.curva_calibracion(a["calibracion"]["bins"], T()), 330)
        with c2:
            if a.get("roc"):
                grafico(graficos.curva_roc(a["roc"]["fpr"], a["roc"]["tpr"],
                                           a["roc"]["auc"], None, T()), 330)
        with c3:
            if a.get("pr"):
                grafico(graficos.curva_pr(a["pr"]["recall"], a["pr"]["precision"],
                                          a["pr"]["auc"], a["pr"]["baseline"],
                                          None, T()), 330)

    pr_auc = a.get("pr", {}).get("auc")
    base = a.get("pr", {}).get("baseline")
    if pr_auc and base:
        abl0 = abl[0]["PRAUC_cv"] if abl else None
        abl2 = abl[-1]["PRAUC_cv"] if abl and len(abl) > 1 else None
        html("<div class='panel' style='margin-top:12px'>"
             f"<div class='panel-titulo'>Un {d(pr_auc, 2)} de PR-AUC suele ser "
             f"señal de fuga. Aquí no lo es, y esta es la razón</div>"
             f"<div class='sutil' style='margin-top:8px'>"
             f"<b>Primero, el punto de partida no es cero.</b> Como el "
             f"{pct(base, 1)} de los trabajadores de la muestra es informal, "
             f"señalar a todo el mundo al azar ya acertaría {pct(base, 1)} de las "
             f"veces. Ese es el suelo contra el que hay que leer el "
             f"{d(pr_auc, 4)}, no el 0,5 de una moneda. Por eso se mira PR-AUC y "
             f"no solo ROC-AUC: con clases desbalanceadas la curva ROC da "
             f"una impresión demasiado optimista{ref('saito2015')}.<br><br>"
             f"<b>Segundo, la relación es casi definicional y está declarada.</b> "
             f"Tamaño de empresa y categoría ocupacional están muy pegadas a la "
             f"regla que define el target. Por eso se midió qué pasa sin ellas: "
             + (f"el PR-AUC baja de {d(abl0, 4)} a {d(abl2, 4)}, se sostiene, y la "
                f"señal restante la cargan educación, área, rama y horas. "
                if abl0 and abl2 else "")
             + "<br><br>"
             f"<b>Tercero, no predice el futuro.</b> Estima la probabilidad de "
             f"que un empleo <i>ya existente</i> sea informal a partir de sus "
             f"características. Es una herramienta de focalización, no un "
             f"pronóstico, y en ese planteamiento un acierto alto es lo "
             f"esperable.<br><br>"
             f"<b>Por contraste: un R² de 0,9 en el regresor de ingreso sí "
             f"sería sospechoso.</b> El ingreso individual tiene una parte "
             f"grande e irreducible que ninguna encuesta observa —habilidad, "
             f"suerte, redes, negociación—. Un ajuste casi perfecto ahí "
             f"significaría que se coló una variable que contiene al propio "
             f"ingreso. De hecho pasó una vez en este proyecto, con el "
             f"«índice de bienestar», y por eso se excluyó."
             f"</div></div>")

    html("<h2>¿Cuánto se equivoca el estimador de ingreso?</h2>")
    m = reg["metricas_test"]
    html("<div class='rejilla-tarjetas'>"
         + tarjeta("MAE test (mediana)", f"S/ {n(m['mae_mediana'])}")
         + tarjeta("MAE test (media smearing)", f"S/ {n(m['mae_media_smear'])}")
         + tarjeta("R² en soles", f"{d(m['r2_soles'], 3)}",
                   llano="El modelo explica esa fracción de la variación del "
                         "ingreso. Ver abajo por qué no es un valor bajo.")
         + "</div>")

    # Afirmación canónica del R²: definida en app/referencias.py y citada aquí.
    # Antes vivía escrita a mano en cuatro sitios con tres rangos distintos.
    html("<h3>¿Un R² de "
         + d(m["r2_soles"], 2) + " no es bajo?</h3>")
    html(f"<div class='sutil' style='max-width:78ch'>"
         f"<b>No, y conviene decir contra qué se compara.</b> "
         + referencias.R2_MINCER_CANONICO.format(
             ref_mincer=ref("mincer1974"), ref_card=ref("card1999"))
         + "<br><br>" + referencias.R2_ADVERTENCIA_CONTEXTO
         + "<br><br><b>Cuidado al comparar: no todos estos R² miden lo "
         f"mismo.</b> El {d(m['r2_soles'], 2)} de la tarjeta es del modelo "
         f"desplegado (E9) medido <b>en soles</b>. La ecuación de Mincer de "
         f"este mismo torneo (E3) da <b>0,27</b> <b>en logaritmo</b>, que es "
         f"la escala de las cifras de la literatura. Son números de escalas "
         f"distintas: ponerlos uno al lado del otro sin decirlo sería "
         f"comparar cosas diferentes.</div>")

    html("<h2>Limitaciones declaradas</h2>")
    lim = [
        "<b>Ingreso autorreportado y suavizado.</b> El target es la versión "
        "imputada, deflactada y anualizada del INEI dividida entre 12: un "
        "ingreso estabilizado, no el del mes de la entrevista. La validez de "
        "constructo hereda los límites del autorreporte en encuestas de hogares.",
        "<b>Solo ingreso monetario.</b> El 24,6 % de los ocupados recibe pago "
        "en especie o autoconsumo, excluido del target. La sensibilidad medida "
        "(sección Torneo) acota el sesgo: el premio urbano cae 2,6 puntos al "
        "incluirlo.",
        "<b>Población restringida.</b> Solo ocupados de 14+ con ingreso "
        "laboral positivo: quedan fuera desocupados, inactivos y los 6.500 "
        "trabajadores familiares no remunerados (informales por definición). "
        "La prevalencia del clasificador es por eso menor que la oficial.",
        "<b>Experiencia potencial, no real.</b> Se usa edad − años de "
        "educación − 6 (truncada en 0; 0,2 % de casos negativos). En "
        "trabajadores de baja educación sobreestima la experiencia efectiva "
        "(Heckman, Lochner & Todd, 2006)" + ref("heckman2006") + ".",
        "<b>Categoría ocupacional ramifica el target del clasificador.</b> "
        "Su importancia alta es por construcción, no un hallazgo.",
        "<b>Herramienta demostrativa.</b> Salidas poblacionales para ordenar "
        "perfiles y focalizar gestión; no liquidan sueldos ni certifican la "
        "situación laboral de ninguna persona concreta.",
    ]
    html("<div class='panel'><div style='display:flex;flex-direction:column;"
         "gap:14px;font-size:13px;line-height:1.65;color:" + T()["texto_medio"] +
         "'>" + "".join(f"<div>{x}</div>" for x in lim) + "</div></div>")

    html("<h2>Procedencia</h2>")
    proc = [
        ("Fuente", "INEI — Encuesta Nacional de Hogares (ENAHO) 2025, "
                   "microdatos públicos (encuesta 1031)"),
        ("Módulos", "02 miembros del hogar · 03 educación · 05 empleo e ingresos"),
        ("Licencia", "Microdatos de descarga libre del INEI; no se "
                     "redistribuyen en el repositorio"),
        ("Clasificador", f"{n(clas['n_entrenamiento'])} train / {n(clas['n_test'])} test"),
        ("Regresor", f"{n(reg['n_entrenamiento'])} train / {n(reg['n_test'])} test"),
        ("Ponderación", meta.get("ponderacion", "—")),
        ("scikit-learn", meta.get("version_scikit_learn", "—")),
        ("Artefactos de UI", meta.get("fecha_generacion", "—")),
        ("Commit", (meta.get("commit") or "—")[:12]),
    ]
    html("<table class='tabla'><tbody>"
         + "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in proc)
         + "</tbody></table>")

    seccion_auditoria()

    html("<h2>Referencias</h2>")
    html("<div class='sutil' style='max-width:78ch;margin-bottom:16px'>"
         "Toda afirmación de esta app que no sea un cálculo propio sobre los "
         "microdatos lleva su referencia. Donde la literatura no dice lo que "
         "haría falta para respaldar una frase, se dice que la lectura es "
         "nuestra en vez de atribuírsela a nadie. Se marca cuáles son de "
         "acceso abierto: enlazar algo que el lector no puede abrir es "
         "citar a medias.</div>")
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

    crudo = emb.get("crudo", {}).get("filas")
    muestra = emb.get("torneo", {}).get("filas")
    ganador, segundo = (tabla + [{}, {}])[:2]

    # Reconciliación con la lámina del mazo: las DOS cifras vienen leídas
    # (medición viva vs. blobs de git al commit del mazo), ninguna a mano.
    mazo = tam.get("repo_mazo") or {}
    nota_nube = None
    if mazo.get("bytes") and tam.get("repo_versionado_bytes"):
        nota_nube = (f"El mazo congelado midió {n(mazo['bytes'] / 1e6, 1)} MB "
                     "en su commit; la diferencia es la propia presentación y "
                     "esta pestaña, añadidas después — el repo crece, la "
                     "medición del mazo quedó anclada a su commit.")

    return [
        {"titulo": "Microdatos INEI", "sub": _mb(tam.get("data_bytes")),
         "entra": "Tres archivos CSV públicos del INEI (ENAHO 2025): módulo "
                  "02 (miembros del hogar), 03 (educación) y 05 (empleo e "
                  "ingresos). Separados por «;», codificación latin-1 y hasta "
                  "una columna con coma decimal — los datos reales llegan así.",
         "decide": "Qué módulos sirven para la pregunta: 02, 03 y 05 se "
                   "quedan; la Sumaria y los módulos 09/10 se descartaron "
                   "porque no aportan variables a estos dos problemas.",
         "sale": f"El módulo 05 crudo: {n(crudo)} filas de personas "
                 "encuestadas, todavía con centinelas y sin filtrar.",
         "tarjetas": [
             ("microdatos en disco", _mb(tam.get("data_bytes")),
              "Viven solo en la computadora de desarrollo: jamás suben a "
              "GitHub ni a la nube."),
             ("filas crudas · módulo 05", n(crudo) if crudo else "—",
              "Cada fila es una persona encuestada."),
         ]},
        {"titulo": "Limpieza", "sub": (f"{n(muestra)} filas" if muestra else "—"),
         "entra": f"Las {n(crudo)} filas crudas más la educación y demografía "
                  "de los módulos 02 y 03.",
         "decide": "Dos cosas: qué es un dato falso (el 999999 que el INEI "
                   "usa como «no sabe» se convierte en vacío) y quién "
                   "pertenece a la población de estudio — los filtros del "
                   "embudo que se ve más abajo.",
         "sale": f"{n(muestra)} trabajadores listos para el torneo, en un "
                 f"parquet de {_mb(tam.get('torneo_frame_bytes'))}.",
         "tarjetas": [
             ("centinelas limpiados",
              n(autopsia.get("n_centinelas", 0)) if autopsia else "—",
              f"Con ellos dentro, una regresión de prueba salía absurda: R² "
              f"{d(autopsia.get('corrida_sucia', {}).get('r2', 0), 2)} y hasta "
              f"la educación «restaba» ingreso. Limpios: R² "
              f"{d(autopsia.get('corrida_limpia', {}).get('r2', 0), 2)} y "
              f"signos con sentido."),
             ("TFNR excluidos", n(tfnr.get("filas", 0)) if tfnr else "—",
              "Trabajadores familiares no remunerados: trabajan, pero sin "
              "sueldo no hay cifra que aprender."),
         ]},
        {"titulo": "Torneo", "sub": f"{len(tabla)} recetas" if tabla else "—",
         "entra": f"El train de {n(split.get('train', 0))} filas en "
                  "validación cruzada de 5 pliegues; el test no opina.",
         "decide": "Qué receta gana. Nueve especificaciones E1–E9 —de la "
                   "regresión lineal simple al gradient boosting— compiten "
                   "por el MAE de validación cruzada: un solo número por "
                   "receta, decidido ANTES de mirar el test.",
         "sale": (f"La receta {art.get('torneo', {}).get('desplegada', '—')} "
                  f"elegida: se equivoca S/ {d(ganador.get('MAE_cv', 0), 1)} "
                  f"al mes en promedio; la segunda ({segundo.get('ID', '—')}) "
                  f"S/ {d(segundo.get('MAE_cv', 0), 1)}." if tabla else "—"),
         "tarjetas": [
             ("MAE_cv del ganador",
              f"S/ {d(ganador.get('MAE_cv', 0), 1)}" if tabla else "—",
              "Cuánto se equivoca por persona, medido sin tocar el test."),
             ("recetas comparadas", str(len(tabla)) if tabla else "—",
              "Mismas filas, mismos pliegues: solo cambia la receta."),
         ]},
        {"titulo": "Entrenamiento", "sub": "2 × .joblib",
         "entra": f"La receta ganadora y las {n(split.get('train', 0))} filas "
                  "de entrenamiento.",
         "decide": "Los últimos números propios del modelo: entrenar el "
                   "gradient boosting definitivo y calcular la corrección de "
                   f"Duan (× {d(float(reg['smearing_duan']), 4)}) con "
                   "residuos out-of-fold — nunca con el test.",
         "sale": "Dos modelos serializados (.joblib) que viajan DENTRO del "
                 "repositorio: la nube no reentrena, solo los lee.",
         "tarjetas": [
             ("regresor_e9.joblib", _kb(modelos.get("regresor_e9.joblib")),
              "El estimador de ingreso, listo para predecir."),
             ("clasificador_gb.joblib",
              _kb(modelos.get("clasificador_gb.joblib")),
              "El detector de empleo informal."),
             ("corrección de Duan", f"× {d(float(reg['smearing_duan']), 4)}",
              "Una constante calculada al entrenar; la app solo multiplica."),
         ]},
        {"titulo": "Artefactos", "sub": "3 × JSON",
         "entra": "Los modelos entrenados y los microdatos, por última vez.",
         "decide": "Todo lo que la app va a dibujar se calcula AQUÍ, una sola "
                   "vez: curvas de umbral, dependencia parcial (11 variables "
                   "× 20 puntos), importancia por permutación (9.000 filas × "
                   "5 repeticiones), cohortes ponderadas.",
         "sale": "Tres JSON pequeños: ui_artifacts.json, feature_schema.json "
                 "y ui_maquinas.json (el de esta pestaña). Mover un control "
                 "en la app no recalcula nada: lee de aquí.",
         "tarjetas": [
             ("ui_artifacts.json", _kb(modelos.get("ui_artifacts.json")),
              f"De {_mb(tam.get('data_bytes'))} de microdatos a esto: la app "
              "solo carga lo precomputado."),
             ("feature_schema.json", _kb(modelos.get("feature_schema.json")),
              "El contrato del formulario: variables, rangos y opciones."),
         ]},
        {"titulo": "Nube", "sub": _mb(tam.get("repo_versionado_bytes")),
         "entra": f"El repositorio versionado: {n(tam.get('repo_archivos', 0))} "
                  f"archivos, {_mb(tam.get('repo_versionado_bytes'))} — "
                  "código, modelos, artefactos y presentación. Los microdatos "
                  "NO.",
         "decide": f"Qué viaja y qué no: data/ "
                   f"({_mb(tam.get('data_bytes'))}) se queda; los .joblib y "
                   "los JSON sí van. Y las versiones quedan fijadas en "
                   "requirements.txt: la nube instala exactamente lo probado "
                   "en local.",
         "sale": "La app pública en Streamlit Community Cloud. Cada push a "
                 "main la redespliega sola en unos minutos — esta pestaña "
                 "llegó así.",
         "tarjetas": [
             ("sube a la nube", _mb(tam.get("repo_versionado_bytes")),
              "Todo lo versionado en GitHub, presentación incluida."),
             ("se queda en local", _mb(tam.get("data_bytes")),
              "Los microdatos: pesan demasiado y la app no los necesita."),
             ("scikit-learn fijado", meta.get("version_scikit_learn", "—"),
              "La misma versión que entrenó los modelos: un .joblib no es "
              "portable entre versiones."),
         ],
         "nota": nota_nube},
    ]


def _sankey_embudo(maq: dict) -> None:
    try:
        import plotly.graph_objects as go
    except ImportError:
        html("<div class='senal senal-aviso'><div>▲</div><div>Falta "
             "<code>plotly</code> (está en requirements.txt): el diagrama "
             "del embudo no puede dibujarse.</div></div>")
        return

    Tt = T()
    emb = maq["embudo"]
    e = {x["clave"]: x for x in emb["etapas"]}
    tfnr, split = emb["tfnr"], emb["split"]

    def rgba(hexcolor: str, a: float) -> str:
        h = hexcolor.lstrip("#")
        return (f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},"
                f"{int(h[4:6], 16)},{a})")

    etiquetas = [
        f"Módulo 05 crudo · {n(e['crudo']['filas'])}",
        f"Ocupados · {n(e['ocupados']['filas'])}",
        f"Dataset de modelado · {n(e['modelado']['filas'])}",
        f"Muestra del torneo · {n(e['torneo']['filas'])}",
        f"Train · {n(split['train'])}",
        f"Test · {n(split['test'])}",
        f"No ocupados · {n(e['ocupados']['recorte'])}",
        f"Menores de 14 o sin ingreso · {n(e['modelado']['recorte'])}",
        f"Casos incompletos · {n(e['torneo']['recorte'])}",
    ]
    color_nodo = [Tt["acento"]] * 6 + [Tt["dato"]] * 3
    sigue, fuera = rgba(Tt["acento"], 0.30), rgba(Tt["dato"], 0.35)
    enlaces = [
        # (origen, destino, valor, color, por qué)
        (0, 1, e["ocupados"]["filas"], sigue,
         "Siguen: quienes estuvieron ocupados en la semana de referencia "
         "(OCU500 = 1)."),
        (0, 6, e["ocupados"]["recorte"], fuera,
         "El modelo estima ingreso del trabajo: sin ocupación no hay ingreso "
         "laboral que estimar."),
        (1, 2, e["modelado"]["filas"], sigue,
         "Siguen: ocupados de 14 años o más con ingreso monetario positivo."),
        (1, 7, e["modelado"]["recorte"], fuera,
         f"Menores de 14 (edad mínima laboral del INEI) o sin ingreso "
         f"laboral positivo. Aquí van los {n(tfnr['filas'])} TFNR: "
         f"trabajadores familiares no remunerados — trabajan, pero sin "
         f"sueldo no hay cifra que aprender."),
        (2, 3, e["torneo"]["filas"], sigue,
         "Siguen: filas completas en todas las variables del torneo."),
        (2, 8, e["torneo"]["recorte"], fuera,
         "Las 9 recetas deben compararse sobre exactamente las mismas filas: "
         "fuera quien no tiene completos tamaño de empresa, miembros, horas, "
         "educación o ingreso (0,6 %)."),
        (3, 4, split["train"], sigue,
         f"El 80 % entrena los modelos ({split['descripcion']})."),
        (3, 5, split["test"], sigue,
         "El 20 % queda guardado y solo se mira al final, para medir sin "
         "hacer trampa."),
    ]
    tema = estilos.nombre_tema(Tt)
    fuente = (estilos.FUENTE_MONO if tema in estilos.TEMAS_MONO
              else estilos.FUENTE_UI)
    fig = go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(
            label=etiquetas, color=color_nodo, pad=22, thickness=14,
            line=dict(width=0),
            x=[0.01, 0.26, 0.51, 0.76, 0.99, 0.99, 0.26, 0.51, 0.76],
            hovertemplate="%{label}<extra></extra>"),
        link=dict(
            source=[l[0] for l in enlaces], target=[l[1] for l in enlaces],
            value=[l[2] for l in enlaces], color=[l[3] for l in enlaces],
            customdata=[l[4] for l in enlaces],
            hovertemplate="%{value:,.0f} filas<br>%{customdata}"
                          "<extra></extra>")))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=fuente, size=13, color=Tt["texto"]),
        separators=",.", height=430, margin=dict(l=8, r=8, t=12, b=8),
        hoverlabel=dict(bgcolor=Tt["superficie_alta"],
                        font=dict(family=fuente, color=Tt["texto"])))
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


def _rayos_x(reg: dict, fila: pd.DataFrame) -> None:
    """
    Una predicción REAL con el capó abierto: los mismos pasos que corre la
    pestaña de ingreso, cronometrados en esta sesión. Teatro honesto: nada de
    la secuencia está inventado ni pregrabado.
    """
    def ms(t0: float) -> str:
        dt = (perf_counter() - t0) * 1000
        return "&lt;1 ms" if dt < 1 else f"{n(dt)} ms"

    with st.status("Motor en marcha…", expanded=True) as estado:
        def paso(k: int, titulo: str, llano: str, t0: float) -> None:
            st.markdown(f"**{k} · {titulo}** — {ms(t0)}",
                        unsafe_allow_html=True)
            st.markdown(f"<div class='sutil'>{llano}</div>",
                        unsafe_allow_html=True)

        total0 = perf_counter()
        t0 = perf_counter()
        modelo = cargar_modelo("regresor_e9.joblib")
        paso(1, "Leer el modelo entrenado", "regresor_e9.joblib llega listo "
             "desde el repositorio: aquí nunca se entrena nada. La primera "
             "vez se lee del disco; después queda en memoria.", t0)

        t0 = perf_counter()
        cols = columnas_esperadas(modelo)
        fila_ord = fila[cols]
        paso(2, "Ordenar tu perfil", f"Una fila con las {len(cols)} variables "
             "en el orden exacto que el modelo declara — ni una más, ni una "
             "menos: es el contrato del schema.", t0)

        interno = getattr(modelo, "regressor_", None)
        internos = getattr(interno, "named_steps", {}) if interno is not None else {}
        prep, gb = internos.get("prep"), internos.get("modelo")
        k = 3
        if prep is not None and gb is not None:
            t0 = perf_counter()
            Xt = prep.transform(fila_ord)
            paso(k, "Abrir las categorías (one-hot)", "Cada categoría se "
                 f"vuelve una columna de ceros y unos: la fila pasa de "
                 f"{len(cols)} a {Xt.shape[1]} columnas, que es lo único que "
                 "el árbol sabe leer.", t0)
            k += 1
            t0 = perf_counter()
            log_pred = float(gb.predict(Xt)[0])
            paso(k, "Predecir en la escala del entrenamiento", "El gradient "
                 f"boosting responde en logaritmo: {d(log_pred, 3)}. Se "
                 "entrenó así porque los ingresos tienen cola larga.", t0)
            k += 1

        t0 = perf_counter()
        mediana = float(modelo.predict(fila_ord)[0])
        paso(k, "Deshacer el logaritmo", f"S/ {n(mediana)} — el ingreso "
             "típico (mediana): la mitad de los perfiles como este gana "
             "menos, la otra mitad más.", t0)
        k += 1

        t0 = perf_counter()
        smear = float(reg["smearing_duan"])
        media = (mediana + 1) * smear - 1
        paso(k, "Corrección de Duan", f"× {d(smear, 4)}: deshacer un "
             "logaritmo deja corto el promedio; esta constante —calculada al "
             "entrenar, nunca aquí— lo repara. Ingreso esperado: "
             f"S/ {n(media)}.", t0)

        # expanded=True: al completar, los pasos QUEDAN a la vista — son el
        # contenido de la sección, no un spinner que esconder.
        estado.update(label=f"Motor recorrido: {k} pasos en "
                            f"{n((perf_counter() - total0) * 1000)} ms",
                      state="complete", expanded=True)

    tarjetas = [
        tarjeta("ingreso típico", f"S/ {n(mediana)}", color=T()["acento_alto"],
                llano="El mismo número que da la pestaña «Estimación de "
                      "ingreso» con este perfil: es el mismo motor, solo que "
                      "con el capó abierto."),
        tarjeta("ingreso esperado", f"S/ {n(media)}",
                llano="El promedio, tras la corrección de Duan del paso "
                      "final."),
    ]
    html("<div class='rejilla-tarjetas'>" + "".join(tarjetas) + "</div>")


# Una línea llana por variable del explorador. Escritas MIRANDO las curvas
# precomputadas (no al revés): si se regeneran los artefactos y una curva
# cambia de forma, la línea correspondiente hay que revisarla a mano.
LINEAS_PD: dict[str, str] = {
    "anios_educ": "Cada año suma, pero no parejo: el tramo que más paga es "
                  "el final — la educación superior.",
    "edad": "Sube hasta la madurez laboral y luego se aplana: los últimos "
            "años ya no añaden ingreso.",
    "horas_total": "Más horas, más ingreso — pero lejos de proporcional: "
                   "multiplicar las horas por ocho apenas duplica la "
                   "estimación.",
    "sexo": "Con el mismo perfil, el modelo estima menos para las mujeres: "
            "es la brecha que existe en los datos de la encuesta — descrita, "
            "no avalada.",
    "area": "El mismo perfil paga distinto según dónde vive: urbano por "
            "encima de rural.",
    "dominio": "La geografía mueve la estimación: costa y Lima por encima; "
               "la sierra, más abajo.",
    "rama": "Minería paga como ninguna otra rama; el agro, menos que todas — "
            "con la misma persona.",
    "tamano_empresa": "Cuanto más grande la empresa, mayor la estimación: el "
                      "salto grande está entre «hasta 20» y el resto.",
    "categoria": "Empleadores arriba, independientes abajo: esta variable "
                 "mueve la estimación más que casi cualquier otra.",
}


def seccion_maquinas(schema: dict, art: dict) -> None:
    reg = schema["regresor"]
    maq = cargar_maquinas()

    cabecera(
        "⚙ Sala de máquinas — cómo se construyó",
        "Esta pestaña abre el capó: el recorrido de los datos desde los CSV "
        "del INEI hasta la página que estás viendo, los filtros con sus "
        "recortes, el motor de la predicción paso a paso y un explorador "
        "para mover una variable. Nada de lo que ves aquí se calcula de "
        "nuevo: sale de los mismos artefactos que alimentan las otras "
        "pestañas.",
        "Las cifras del embudo y los tamaños medidos viven en "
        "<code>models/ui_maquinas.json</code>, generado por "
        "<code>src/09_precomputar_ui.py</code> leyendo el embudo auditado de "
        "<code>INFORME_AUDITORIA.md §4</code> y midiendo los archivos en "
        "disco. Va en un artefacto hermano de <code>ui_artifacts.json</code> "
        "porque la presentación congelada cita el tamaño en disco de este "
        "último: no puede crecer ni un byte.",
        seccion="máquinas")
    st.write("")

    if not maq:
        html("<div class='senal senal-aviso'><div>▲</div><div>Falta "
             "<code>models/ui_maquinas.json</code>. Genéralo con "
             "<code>python src/09_precomputar_ui.py --solo-maquinas</code>."
             "</div></div>")
        return

    # ---------- 1 · El viaje del dato ----------
    html("<h2>El viaje del dato</h2>")
    html("<div class='entradilla'>Seis estaciones desde la encuesta hasta la "
         "nube. Elige una y mira qué entra, qué se decide y qué sale — con "
         "sus tamaños medidos.</div>")
    estaciones = _estaciones(schema, art, maq)
    titulos = [e["titulo"] for e in estaciones]
    control = getattr(st, "segmented_control", None)
    if control is not None:
        elegido = control("Estación", titulos, default=titulos[0],
                          key="maq_estacion", label_visibility="collapsed")
    else:
        elegido = st.radio("Estación", titulos, horizontal=True,
                           key="maq_estacion", label_visibility="collapsed")
    idx = titulos.index(elegido) if elegido in titulos else 0
    grafico(graficos.viaje_dato(titulos, [e["sub"] for e in estaciones],
                                idx, T()), 150)
    est = estaciones[idx]
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, rotulo, texto in ((c1, "Qué entra", est["entra"]),
                               (c2, "Qué se decide", est["decide"]),
                               (c3, "Qué sale", est["sale"])):
        with col:
            html(f"<div class='eyebrow'>{rotulo}</div>"
                 f"<div class='sutil'>{texto}</div>")
    st.write("")
    html("<div class='rejilla-tarjetas'>"
         + "".join(tarjeta(et, v, llano=ll) for et, v, ll in est["tarjetas"])
         + "</div>")
    if est.get("nota"):
        html(f"<div class='sutil' style='margin-top:8px'>{est['nota']}</div>")
    with st.expander("¿Qué principio hay aquí? · viaje"):
        html("<div class='sutil'>Precómputo y fuente única: la app no "
             "calcula al abrirse — todo lo que este viaje muestra lo generó "
             "<code>src/09</code> una sola vez, y es lo mismo que alimenta "
             "las otras pestañas y la presentación.</div>")

    st.divider()

    # ---------- 2 · El embudo ----------
    html("<h2>El embudo: de la encuesta al modelo</h2>")
    html("<div class='entradilla'>Cada filtro recorta filas y tiene un "
         "porqué: pasa el cursor por los flujos para leerlo. Del módulo "
         "crudo a la muestra final del torneo.</div>")
    _sankey_embudo(maq)
    with st.expander("¿Qué principio hay aquí? · embudo"):
        html("<div class='sutil'>Estos números no están tecleados en esta "
             "página: <code>src/09</code> los lee del informe de auditoría "
             "(§4), verifica que las restas cuadren y los publica en el "
             "artefacto. Si el informe cambia, esta página cambia sola — o "
             "el generador aborta.</div>")

    st.divider()

    # ---------- 3 · Rayos X de la predicción ----------
    html("<h2>Rayos X de la predicción</h2>")
    html("<div class='entradilla'>El mismo formulario de la primera pestaña, "
         "pero con el capó abierto: al estimar se ve cada paso real del "
         "motor, con su tiempo.</div>")
    if st.toggle("Ver el motor", key="maq_motor",
                 help="Los pasos son los reales de esta sesión, "
                      "cronometrados al ejecutarse. No es una animación."):
        izq, der = st.columns([35, 65], gap="large")
        with izq:
            html("<div class='eyebrow'>Perfil del trabajador</div>")
            html("<div class='sutil'>Mismo perfil por defecto que la pestaña "
                 "de ingreso: mismo número, mismo motor.</div>")
            fila = formulario(reg["features"], "maq")
            st.write("")
            lanzar = st.button("Estimar mirando el motor", type="primary",
                               key="btn_maq")
        with der:
            if lanzar:
                _rayos_x(reg, fila)
            else:
                html("<div class='panel'><div class='panel-titulo'>Motor en "
                     "espera</div><div class='sutil'>Arma el perfil y pulsa "
                     "«Estimar mirando el motor»: verás leer el schema, "
                     "abrir las categorías en columnas, predecir en "
                     "logaritmo, deshacerlo y aplicar la corrección de Duan "
                     "— cada paso con su tiempo real.</div></div>")
    with st.expander("¿Qué principio hay aquí? · motor"):
        html("<div class='sutil'>Teatro honesto: la secuencia son los pasos "
             "reales, cronometrados en tu sesión. Lo único que la app no "
             "hace nunca en vivo es entrenar: el modelo llegó listo en el "
             "repositorio, con las versiones fijadas.</div>")

    st.divider()

    # ---------- 4 · Mueve una variable ----------
    html("<h2>Mueve una variable</h2>")
    html("<div class='entradilla'>Si solo cambiara esta característica y "
         "todo lo demás quedara igual, ¿cómo se movería el ingreso "
         "estimado? Curvas precomputadas: elegir no recalcula nada.</div>")
    pd_reg = art.get("regresor", {}).get("dependencia_parcial", {})
    feats = [f for f in reg["features"]
             if f["nombre"] not in DERIVADAS and pd_reg.get(f["nombre"])]
    if not feats:
        html("<div class='senal senal-aviso'><div>▲</div><div>El artefacto "
             "no trae la dependencia parcial del regresor.</div></div>")
    else:
        feat = st.selectbox(
            "Variable", feats,
            format_func=lambda f: f.get("etiqueta", f["nombre"]),
            key="maq_var")
        nombre = feat["nombre"]
        perfil = pd_reg[nombre]
        marca = (st.session_state.get("valores_maq", {}).get(nombre)
                 or st.session_state.get("valores_reg", {}).get(nombre))
        html(f"<div class='titulo-grafico'>"
             f"{escape(feat.get('etiqueta', nombre))}</div>")
        grafico(graficos.dependencia_parcial(
            perfil["valores"], perfil["efecto"], perfil["tipo"],
            feat.get("etiqueta", nombre), T(), marca=marca,
            formato_y="soles", mostrar_etiqueta=False), 230)
        linea = LINEAS_PD.get(nombre, "Así cambia la estimación cuando solo "
                                      "se mueve esta variable.")
        html(f"<div class='sutil'><b>{linea}</b> El eje vertical es el "
             "ingreso típico estimado (S/ al mes) con el resto del perfil "
             "en su valor promedio.</div>")
        html("<div class='sutil'>¿Por qué 9 y no 11? Experiencia y "
             "experiencia² van atadas — moverlas por separado sería un "
             "perfil imposible.</div>")
    with st.expander("¿Qué principio hay aquí? · explorador"):
        html("<div class='sutil'>Precómputo puro: cada curva son 20 puntos "
             "que <code>src/09</code> calculó una sola vez sobre 5.000 "
             "filas. Mover el selector no toca el modelo — por eso responde "
             "al instante.</div>")


# --------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="ENAHO — ingreso e informalidad",
                       page_icon="◈", layout="wide",
                       initial_sidebar_state="expanded")
    st.session_state.setdefault("tema", "claro")
    st.session_state.setdefault("seccion", "ingreso")
    html(estilos.css(T()))

    if not (DIR_MODELS / "feature_schema.json").exists():
        html("<div class='senal senal-alerta'><div>▲</div><div>No se encuentra "
             "<code>models/feature_schema.json</code>. Corre antes los scripts "
             "de <code>src/</code>.</div></div>")
        st.stop()

    schema, art = cargar_schema(), cargar_artefactos()

    with st.sidebar:
        html("<div class='marca'>INEI · ENAHO 2025</div>"
             "<div class='marca-titulo'>Ingreso laboral<br>e informalidad</div>")
        html(f"<div class='sutil' style='margin:-12px 0 16px 0'>"
             f"<a href='{REPO}' "
             f"target='_blank' style='color:{T()['acento_alto']};"
             f"text-decoration:none'>Código y metodología en GitHub ↗</a></div>")
        for clave, titulo in SECCIONES:
            activo = st.session_state["seccion"] == clave
            if st.button(titulo, key=f"nav_{clave}",
                         type="primary" if activo else "secondary"):
                st.session_state["seccion"] = clave
                st.rerun()
        st.write("")
        # Las opciones salen de PALETAS: añadir un tema allí lo hace aparecer
        # aquí, y quitarlo lo hace desaparecer. No hay lista que mantener.
        opciones = opciones_tema()
        actual = tema_activo()
        control = getattr(st, "segmented_control", None)
        if control is not None:
            nuevo = control("Tema", opciones, default=actual,
                            format_func=etiqueta_tema,
                            key="sel_tema", label_visibility="collapsed")
        else:
            nuevo = st.radio("Tema", opciones, index=opciones.index(actual),
                             format_func=etiqueta_tema, horizontal=True,
                             key="sel_tema", label_visibility="collapsed")
        if nuevo and nuevo != actual:
            st.session_state["tema"] = nuevo
            st.rerun()
        html(f"<div class='sutil' style='border-top:1px solid "
             f"{T()['borde_sutil']};padding-top:12px'>Herramienta demostrativa "
             f"sobre microdatos públicos del INEI. No es un instrumento de "
             f"fiscalización laboral.</div>")

    seccion = st.session_state["seccion"]
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


if __name__ == "__main__":
    main()
