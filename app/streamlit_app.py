# streamlit_app.py — app Streamlit: predicción, torneo y ficha
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
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
import sys
from pathlib import Path

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

SECCIONES = [
    ("ingreso", "Estimación de ingreso"),
    ("informalidad", "Empleo informal"),
    ("torneo", "Torneo de modelos"),
    ("ficha", "Ficha técnica"),
]
DERIVADAS = {"exper", "exper2"}   # las calcula la app, no el usuario


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cargar_schema() -> dict:
    return json.loads((DIR_MODELS / "feature_schema.json").read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def cargar_artefactos() -> dict:
    ruta = DIR_MODELS / "ui_artifacts.json"
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}


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
def T() -> dict:
    return PALETAS[st.session_state.get("tema", "oscuro")]


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

    st.divider()
    if proba is not None:
        grafico(graficos.medidor(proba, umbral,
                                 st.session_state.get("hist_cohorte"), T()), 310)
        if proba >= umbral:
            html(f"<div class='senal senal-aviso'><div>▲</div><div>"
                 f"<b>Perfil señalado para focalización.</b> La probabilidad "
                 f"estimada de empleo informal ({pct(proba, 1)}) supera el umbral "
                 f"({d(umbral, 3)}). La señal identifica una configuración laboral, "
                 f"no un veredicto sobre la persona.</div></div>")
        else:
            html(f"<div class='senal senal-ok'><div>●</div><div>"
                 f"<b>Sin señal por este criterio.</b> La probabilidad estimada "
                 f"({pct(proba, 1)}) queda por debajo del umbral ({d(umbral, 3)})."
                 f"</div></div>")

    # ---- Consecuencias en vivo ----
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

    st.divider()
    html("<div class='eyebrow'>Qué pasa con este umbral</div>")
    html(f"<div class='panel' style='margin-top:8px'>"
         f"<div style='font-size:15px;line-height:1.9;color:{T()['texto']}'>"
         f"Con umbral <b>{d(umbral, 3)}</b>:<br>"
         f"se señala al <b style='color:{T()['acento_alto']}'>"
         f"{pct_senalado:.0f} %</b> de los trabajadores · "
         f"de cada 100 señalados, <b style='color:{T()['senal_buena']}'>"
         f"{round(prec * 100)}</b> son informales · "
         f"se escapan <b style='color:{T()['senal_mala']}'>"
         f"{round((1 - rec) * 100)}</b> de cada 100 informales."
         f"</div></div>")

    if a_curva := curva.get("precision_1"):
        grafico(graficos.curva_precision_cobertura(
            curva["recall_1"], a_curva, (rec, prec),
            [(presets[k_][1], indice_umbral(curva, presets[k_][0]))
             for k_ in presets], curva, T()), 330)
        html("<div class='sutil'>El punto blanco es el umbral que tienes "
             "puesto. Las marcas son los tres preajustes. Cada punto de la "
             "curva es un umbral posible: subirlo te mueve arriba y a la "
             "izquierda (más acierto, más informales que se escapan); bajarlo, "
             "abajo y a la derecha.</div>")

    st.write("")
    grafico(graficos.matriz_confusion(m_tp, m_fp, m_tn, m_fn, T()), 270)
    html(f"<div class='sutil'>Calculado sobre {n(total)} trabajadores del "
         f"entrenamiento con probabilidades out-of-fold, escalado a 1.000. "
         f"Precisión clase informal: {d(prec, 4)} · recall: {d(rec, 4)}.</div>")


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
                    "casos comparables (p25–p75)",
                    f"S/ {n(comp['p25'])} – {n(comp['p75'])}",
                    f"{v['sexo'].lower()}, área {v['area'].lower()}, "
                    f"{banda} años de educación · mediana S/ {n(comp['p50'])} · "
                    f"n={n(comp['n'])}"))

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
        html("<div class='eyebrow'>Qué determina el ingreso estimado</div>")
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
            st.session_state["hist_cohorte"] = a.get("histograma_probabilidades")

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
             "perfil que armaste.</div>")
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
        "Este proyecto no muestra solo el modelo ganador: muestra el camino. "
        "Se probaron nueve formas distintas de estimar el ingreso, todas sobre "
        "los mismos datos y con la misma prueba. Aquí está la comparación "
        "completa, incluida la primera versión que salió mal.",
        "Las nueve especificaciones comparten muestra, partición "
        "entrenamiento/prueba y los mismos cinco pliegues de validación "
        "cruzada, con semilla fija. Sin eso el ranking no sería comparable. La "
        "selección se hace por el error de validación cruzada y no por el de "
        "prueba: elegir por prueba tras comparar nueve candidatos sería "
        "seleccionar sobre el conjunto con el que luego se dice ser honesto.",
        seccion="torneo")

    # ---- Acto 1 y 2 ----
    html("<h2>Acto 1 · La ecuación inicial</h2>")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        html(_ecuacion(aut["ecuacion_companera"],
                       "Versión inicial del grupo (datos con centinela)"))
        html("<div class='sutil' style='margin-top:8px'>+11 soles por residir "
             "en zona urbana y +6 por ser hombre: incompatible con las brechas "
             "conocidas del mercado laboral peruano. Ese resultado no se "
             "descartó — se diagnosticó.</div>")
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
         f"<b>2 · La colinealidad.</b> Años de educación y nivel educativo "
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
            html("<h3>Qué eliminó el Lasso en E7</h3>")
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
                f"<td style='text-align:left'><code>{d['evidencia']}</code>"
                f"</td></tr>" for d in desc)
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

    html("<h2>¿Es demasiado bueno el clasificador de informalidad?</h2>")
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
                     f"«{tam['min']['categoria']}» (ponderado); el INEI "
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
             f"<a href='https://github.com/IchiSieben/enaho-ingresos-informalidad' "
             f"target='_blank' style='color:{T()['acento_alto']};"
             f"text-decoration:none'>Código y metodología en GitHub ↗</a></div>")
        for clave, titulo in SECCIONES:
            activo = st.session_state["seccion"] == clave
            if st.button(titulo, key=f"nav_{clave}",
                         type="primary" if activo else "secondary"):
                st.session_state["seccion"] = clave
                st.rerun()
        st.write("")
        oscuro = st.toggle("Tema oscuro", value=st.session_state["tema"] == "oscuro",
                           key="toggle_tema")
        nuevo = "oscuro" if oscuro else "claro"
        if nuevo != st.session_state["tema"]:
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
    else:
        seccion_ficha(schema, art)


if __name__ == "__main__":
    main()
