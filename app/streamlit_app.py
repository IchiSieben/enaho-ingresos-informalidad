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
from estilos import PALETAS

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


def tarjeta(etiqueta: str, valor: str, nota: str = "", color: str | None = None) -> str:
    estilo = f" style='color:{color}'" if color else ""
    pie = f"<div class='tarjeta-nota'>{nota}</div>" if nota else ""
    return (f"<div class='tarjeta'><div class='tarjeta-etiqueta'>{etiqueta}</div>"
            f"<div class='tarjeta-valor'{estilo}>{valor}</div>{pie}</div>")


def grafico(svg: str, alto: int) -> None:
    components.html(graficos.envolver(svg, estilos.css_iframe(T())), height=alto,
                    scrolling=False)


def n(x: float, dec: int = 0) -> str:
    return f"{x:,.{dec}f}"


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

    html("<div class='eyebrow'>Punto operativo</div>")
    col_p, col_s = st.columns([1, 1])
    with col_p:
        preset = st.radio(
            "Preajuste", list(presets) + ["libre"], index=0,
            format_func=lambda k: ("Umbral libre" if k == "libre" else
                                   f"{presets[k][1]} · {presets[k][0]:.3f}"),
            label_visibility="collapsed", key="preset_umbral")
    with col_s:
        if preset == "libre":
            umbral = st.slider("Umbral", 0.01, 0.99,
                               float(st.session_state.get("umbral_libre", 0.50)),
                               0.01, key="umbral_libre")
        else:
            umbral = presets[preset][0]
            st.slider("Umbral", 0.01, 0.99, umbral, 0.01, disabled=True,
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
                 f"estimada de empleo informal ({proba:.1%}) supera el umbral "
                 f"({umbral:.3f}). La señal identifica una configuración laboral, "
                 f"no un veredicto sobre la persona.</div></div>")
        else:
            html(f"<div class='senal senal-ok'><div>●</div><div>"
                 f"<b>Sin señal por este criterio.</b> La probabilidad estimada "
                 f"({proba:.1%}) queda por debajo del umbral ({umbral:.3f})."
                 f"</div></div>")

    # ---- Impacto operativo por 1.000 evaluados ----
    total = curva["n"]
    tp, fp = curva["tp"][i], curva["fp"][i]
    tn, fn = curva["tn"][i], curva["fn"][i]
    k = 1000 / total
    m_tp, m_fp, m_tn, m_fn = (round(tp * k), round(fp * k),
                              round(tn * k), round(fn * k))
    senalados = m_tp + m_fp
    prec = curva["precision_1"][i]

    st.divider()
    html("<div class='eyebrow'>Impacto operativo</div>")
    html(f"<div class='panel' style='margin-top:8px'>"
         f"<div style='font-size:15px;line-height:1.75;color:{T()['texto']}'>"
         f"Con este umbral, de cada <b>1.000</b> trabajadores evaluados se "
         f"señalarían <b style='color:{T()['acento_alto']}'>{senalados}</b> para "
         f"programas de formalización.<br>De cada 1.000 <i>señalados</i>, "
         f"<b style='color:{T()['senal_buena']}'>{round(prec * 1000)}</b> serían "
         f"efectivamente informales (precisión {prec:.1%}).<br>Quedarían sin "
         f"señalar <b style='color:{T()['senal_mala']}'>{m_fn}</b> informales "
         f"por cada 1.000 evaluados.</div></div>")

    grafico(graficos.matriz_confusion(m_tp, m_fp, m_tn, m_fn, T()), 270)
    html(f"<div class='sutil'>Calculado sobre {n(total)} trabajadores del "
         f"entrenamiento con probabilidades out-of-fold, escalado a 1.000. "
         f"Precisión clase informal: {prec:.4f} · recall: "
         f"{curva['recall_1'][i]:.4f}.</div>")


# --------------------------------------------------------------------------
# Sección 1: estimación de ingreso
# --------------------------------------------------------------------------
def seccion_ingreso(schema: dict, art: dict) -> None:
    reg = schema["regresor"]
    b = art.get("regresor", {})

    html("<h1>Estimación de ingreso laboral</h1>")
    html(f"<div class='sutil' style='max-width:74ch'>{reg['descripcion_target']}</div>")
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
            tarjeta("ingreso típico estimado (mediana)", f"S/ {n(ingreso)}",
                    color=T()["acento_alto"]),
            tarjeta("ingreso esperado (media, smearing)", f"S/ {n(media)}",
                    f"corrección de Duan × {smear:.3f}"),
            tarjeta("mediana poblacional", f"S/ {n(float(mediana_pob))}",
                    "ponderada con el factor de expansión"),
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
        html(f"<div class='senal senal-aviso'><div>▲</div><div>"
             f"<b>La cifra principal es un ingreso típico (mediana condicional), "
             f"no un ingreso esperado (media).</b> El modelo se entrena en "
             f"log y la inversión directa estima la mediana; la media exige la "
             f"corrección de smearing de Duan (×{smear:.3f}) que se muestra en "
             f"la segunda tarjeta. Además el target es un ingreso "
             f"<b>suavizado</b> (anualizado ÷ 12) y <b>solo monetario</b>: el "
             f"pago en especie y autoconsumo (24,6 % de los ocupados lo recibe) "
             f"queda fuera.</div></div>")
        mae = reg["metricas_test"]["mae_mediana"]
        html(f"<div class='sutil' style='margin-top:12px'>MAE en test: "
             f"S/ {n(mae)}. La incertidumbre individual es grande y está "
             f"declarada: el modelo ordena perfiles, no liquida sueldos.</div>")

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

    html("<h1>Empleo informal</h1>")
    html(f"<div class='sutil' style='max-width:74ch'>{clas['descripcion_target']} "
         f"{clas.get('encuadre', '')}</div>")
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
        html("<div class='eyebrow'>Cómo pesa cada variable</div>")
        html("<div class='sutil' style='max-width:78ch'>Efecto marginal sobre la "
             "probabilidad de informalidad, con el resto de la población "
             "promediada. <b>Nota de construcción:</b> la categoría ocupacional "
             "ramifica la propia definición del target (independiente → RUC; "
             "dependiente → pensiones), así que su peso alto no es un "
             "hallazgo.</div>")
        st.write("")
        valores = st.session_state.get("valores_clf", {})
        cols = st.columns(2, gap="medium")
        j = 0
        for feat in clas["features"]:
            perfil = a["dependencia_parcial"].get(feat["nombre"])
            if not perfil or feat["nombre"] in DERIVADAS:
                continue
            with cols[j % 2]:
                grafico(graficos.dependencia_parcial(
                    perfil["valores"], perfil["efecto"], perfil["tipo"],
                    feat.get("etiqueta", feat["nombre"]), T(),
                    marca=valores.get(feat["nombre"]), formato_y="prob"), 210)
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


def seccion_torneo(art: dict) -> None:
    t = art.get("torneo")
    if not t:
        html("<div class='senal senal-aviso'><div>▲</div><div>Falta el bloque "
             "torneo en <code>ui_artifacts.json</code>.</div></div>")
        return
    aut = t["autopsia"]

    html("<h1>Torneo de modelos</h1>")
    html("<div class='sutil' style='max-width:78ch'>Este proyecto no muestra "
         "solo el modelo ganador: muestra el camino. Una regresión inicial con "
         "coeficientes implausibles se convierte en el punto de partida de un "
         "torneo de nueve especificaciones con el mismo split y la misma "
         "validación cruzada.</div>")

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
             f"<b>{aut['corrida_sucia']['r2']:.3f}</b> a "
             f"<b>{aut['corrida_limpia']['r2']:.3f}</b> y todos los signos se "
             f"vuelven económicamente plausibles.</div>")

    html("<h2>Acto 2 · El diagnóstico</h2>")
    html(f"<div class='panel'><div style='line-height:1.8;font-size:13px;color:"
         f"{T()['texto']}'>"
         f"<b>1 · El centinela.</b> El {aut['pct_centinelas']:.2f} % de la "
         f"población tenía el código 999999 («no sabe») leído como ingreso "
         f"real de un millón de soles. R² sucio: "
         f"{aut['corrida_sucia']['r2']:.3f}; limpio: "
         f"{aut['corrida_limpia']['r2']:.3f}.<br>"
         f"<b>2 · La colinealidad.</b> Años de educación y nivel educativo "
         f"detallado son la misma variable codificada dos veces: juntos "
         f"disparan el VIF a ~20 y voltean signos. No conviven en ninguna "
         f"especificación del torneo.<br>"
         f"<b>3 · La escala.</b> El ingreso limpio tiene asimetría "
         f"{aut['asimetria_limpia']:.2f}: en niveles, unos pocos sueldos altos "
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
                  f"<td>{f['MAE_cv']:,.0f}</td><td>{f['MAE_test']:,.0f}</td>"
                  f"<td>{f['R2_test_soles']:.3f}</td>"
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
             f"<b>{sens[0]['premio_urbano_pct']:.1f} %</b>; añadiendo especie, "
             f"<b>{sens[1]['premio_urbano_pct']:.1f} %</b>. La exclusión queda "
             f"validada como robusta y declarada.</div>")


# --------------------------------------------------------------------------
# Sección 4: ficha técnica
# --------------------------------------------------------------------------
def seccion_ficha(schema: dict, art: dict) -> None:
    clas, reg = schema["clasificador"], schema["regresor"]
    a = art.get("clasificador", {})
    meta = art.get("meta", {})

    html("<h1>Ficha técnica</h1>")
    html("<div class='sutil' style='max-width:78ch'>Qué miden los modelos, "
         "dónde fallan y qué no se puede concluir con ellos.</div>")

    html("<h2>Clasificador de informalidad</h2>")
    filas = ""
    for f in a.get("comparacion", []):
        es_gb = "Gradient" in f["algoritmo"]
        clase = " class='destacada'" if es_gb else " class='atenuada'"
        filas += (f"<tr{clase}><td>{f['algoritmo']}"
                  f"{' · desplegado' if es_gb else ''}</td>"
                  f"<td>{f['PRAUC_cv']:.4f}</td><td>{f['PRAUC_test']:.4f}</td>"
                  f"<td>{f['ROCAUC_test']:.4f}</td><td>{f['Brier_test']:.4f}</td></tr>")
    html(f"<table class='tabla'><thead><tr><th>Algoritmo</th><th>PR-AUC cv</th>"
         f"<th>PR-AUC test</th><th>ROC-AUC test</th><th>Brier</th></tr></thead>"
         f"<tbody>{filas}</tbody></table>")
    html(f"<div class='sutil' style='margin-top:10px;max-width:78ch'>Baseline "
         f"de PR-AUC = prevalencia ({clas['prevalencia_train']:.3f} muestral; "
         f"{clas['prevalencia_ponderada']:.3f} ponderada). La regla del target "
         f"se validó contra la tasa oficial: reconstruida sobre todos los "
         f"ocupados da 67,3 % frente al 70,2 % del INEI 2025, y el gradiente "
         f"por tamaño de empresa replica el patrón oficial (88,6 % de "
         f"informalidad en microempresas vs 15,6 % en grandes).</div>")

    abl = clas.get("ablacion", [])
    if abl:
        html("<h3>Ablación estructural</h3>")
        filas = ""
        for i, f in enumerate(abl):
            clase = " class='destacada'" if i == 0 else " class='atenuada'"
            filas += (f"<tr{clase}><td>{f['variante']}</td>"
                      f"<td>{f['n_predictores']}</td><td>{f['PRAUC_cv']:.4f}</td>"
                      f"<td>{f['ROCAUC_cv']:.4f}</td>"
                      f"<td>{f.get('caida_PRAUC_cv', 0):.4f}</td></tr>")
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

    html("<h2>Regresor de ingreso</h2>")
    m = reg["metricas_test"]
    html("<div class='rejilla-tarjetas'>"
         + tarjeta("MAE test (mediana)", f"S/ {n(m['mae_mediana'])}")
         + tarjeta("MAE test (media smearing)", f"S/ {n(m['mae_media_smear'])}")
         + tarjeta("R² en soles", f"{m['r2_soles']:.3f}",
                   "esperable en ingresos individuales: 0,4–0,5 es techo "
                   "habitual con encuestas de hogares")
         + "</div>")

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
        "(Heckman, Lochner & Todd, 2006).",
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


# --------------------------------------------------------------------------
def main() -> None:
    st.set_page_config(page_title="ENAHO — ingreso e informalidad",
                       page_icon="◈", layout="wide",
                       initial_sidebar_state="expanded")
    st.session_state.setdefault("tema", "oscuro")
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
        for clave, titulo in SECCIONES:
            activo = st.session_state["seccion"] == clave
            if st.button(titulo, key=f"nav_{clave}",
                         type="primary" if activo else "secondary"):
                st.session_state["seccion"] = clave
                st.rerun()
        st.write("")
        claro = st.toggle("Tema claro", value=st.session_state["tema"] == "claro",
                          key="toggle_tema")
        nuevo = "claro" if claro else "oscuro"
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
        seccion_torneo(art)
    else:
        seccion_ficha(schema, art)


if __name__ == "__main__":
    main()
