# estilos.py — sistema de diseño: tokens y CSS generado
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
"""
FASE 3 — Sistema de diseño (adaptado del proyecto hermano de salud publica).

Los tokens viven en un DICCIONARIO DE PYTHON y de ahí se GENERA el CSS: los
SVG de `graficos.py` viajan a un iframe (`st.components.v1.html`) que no ve
las variables CSS del padre, así que la única fuente de verdad de color tiene
que estar en Python y pasarse como parámetro a ambos mundos.

Novedad de este proyecto: TRES paletas con las mismas claves en `PALETAS`
("claro"/"oscuro"/"terminal") y un selector en la barra lateral persistido en
`st.session_state["tema"]`. Nada de duplicar bloques CSS a mano: `css(T)`
genera el bloque completo desde la paleta activa.

El tema claro no es «invertir colores»: fondo blanco hueso (no #FFF puro),
superficies apenas grises, mismos acentos oscurecidos para mantener AA.

Semántica de señal en este dominio: ámbar = señalado como informal (caso
accionable para focalización), «bueno» = sin señal (violeta en claro/oscuro,
verde oliva en Terminal), «malo» = alerta. El acento (teal de ichi7.dev en
claro/oscuro, azul Python en Terminal) es solo interacción y «tu perfil»:
nunca significa condición laboral. Contraste AA y distinguibilidad bajo
protanopia/deuteranopia/tritanopia verificados en tests/test_color.py.
"""

from __future__ import annotations

PALETAS: dict[str, dict[str, str]] = {
    "claro": {
        # v1.2: identidad de ichi7.dev. Fondo con un matiz teal apenas
        # perceptible, tarjetas blancas, tinta casi negra y el teal de marca
        # oscurecido a teal-700 (#2DD4BF da 1,9:1 sobre blanco; #0F766E da
        # 5,5:1). Todos los pares de texto ≥ 4,5:1 (tests/test_color.py).
        "fondo":             "#EEF4F3",
        "superficie":        "#FFFFFF",
        "superficie_alta":   "#E6EFEE",
        "superficie_hover":  "#DAE7E5",
        "borde":             "#C9D8D6",
        "borde_sutil":       "#DDE7E6",
        "texto":             "#0E1A19",
        "texto_medio":       "#364746",
        "texto_tenue":       "#4F605E",
        "acento":            "#0F766E",   # teal-700: texto y trazos finos
        "acento_alto":       "#0B5E57",
        "acento_fondo":      "#DCF1ED",
        "boton_texto":       "#FFFFFF",
        # «Bueno» violeta y «malo» carmesí: con el verde y el rojo de antes,
        # ámbar y rojo quedaban a ΔE 0,02 en deuteranopia (indistinguibles).
        "senal_buena":       "#5634AC",
        "senal_media":       "#8A5A06",
        "senal_mala":        "#82182E",
        "senal_buena_fondo": "#EEE9FB",
        "senal_media_fondo": "#FBF0DA",
        "senal_mala_fondo":  "#FAE6EA",
        "senal_buena_texto": "#3F2482",
        "senal_media_texto": "#6A4608",
        "senal_mala_texto":  "#6B1325",
        "dato":              "#4E6260",
        "dato_tenue":        "#BCCFCC",
        "rejilla":           "#DDE8E6",
        "titulo":            "#061413",
        "sombra_tarjeta":    "0 1px 2px rgba(6,40,36,0.05), "
                             "0 8px 24px rgba(6,40,36,0.07)",
    },
    "oscuro": {
        "fondo":             "#0B0F10",
        "superficie":        "#121819",
        "superficie_alta":   "#182021",
        "superficie_hover":  "#1F292A",
        "borde":             "#263234",
        "borde_sutil":       "#1A2324",
        "texto":             "#E6EEED",
        "texto_medio":       "#9AABA9",
        # Aclarado para texto pequeño: .eyebrow, .et y .tarjeta-etiqueta.
        "texto_tenue":       "#7D8F8D",
        "acento":            "#2DD4BF",   # teal de ichi7.dev, 9,6:1
        "acento_alto":       "#5EEAD4",
        "acento_fondo":      "#0E2A27",
        "boton_texto":       "#04211E",
        "senal_buena":       "#9980FE",
        "senal_media":       "#E0A33E",
        "senal_mala":        "#E65A79",
        "senal_buena_fondo": "#1C1834",
        "senal_media_fondo": "#241D10",
        "senal_mala_fondo":  "#2A1219",
        "senal_buena_texto": "#D5CCFF",
        "senal_media_texto": "#F0D9AC",
        "senal_mala_texto":  "#F9C6D2",
        "dato":              "#8A9C9A",
        "dato_tenue":        "#34403F",
        "rejilla":           "#1F2929",
        # Tinta de titulares y sombra de tarjeta. En los temas oscuros el
        # titular ya destaca por contraste puro y una sombra no se ve sobre
        # fondo casi negro: ambos quedan neutros aquí y trabajan en el claro.
        "titulo":            "#F2F5FA",
        "sombra_tarjeta":    "none",
    },
    # Tercer tema: consola. Azul (#306998) y amarillo (#FFD43B) de Python sobre
    # fondo casi negro. El azul original es demasiado oscuro para texto sobre
    # negro (2,3:1), así que para tinta se usa una versión aclarada y el azul
    # de marca queda para fondos y trazos gruesos. Todos los pares de texto
    # verificados a 4,5:1 o mejor.
    "terminal": {
        "fondo":             "#0A0C10",
        "superficie":        "#11151C",
        "superficie_alta":   "#171C25",
        "superficie_hover":  "#1E2530",
        "borde":             "#2B3440",
        "borde_sutil":       "#1B2029",
        "texto":             "#D6E2D0",   # verde-claro de consola, 13,4:1
        "texto_medio":       "#9DB39A",   # 7,5:1
        "texto_tenue":       "#7C917C",   # 5,0:1
        "acento":            "#5FA8E8",   # azul Python aclarado, 7,4:1
        "acento_alto":       "#FFD43B",   # amarillo Python, 12,9:1
        "acento_fondo":      "#132433",
        "boton_texto":       "#0A0C10",
        # Terminal conserva azul y amarillo de Python (el teal aquí empeoraba:
        # acento y «bueno» a ΔE 0,02 en tritanopia). Sí cambian «bueno» (verde
        # oliva) y «malo» (rosa): el par anterior quedaba a ΔE 0,05 en
        # deuteranopia.
        "senal_buena":       "#6F9C37",
        "senal_media":       "#FFD43B",
        "senal_mala":        "#FD8994",
        "senal_buena_fondo": "#16220C",
        "senal_media_fondo": "#241E08",
        "senal_mala_fondo":  "#2A1518",
        "senal_buena_texto": "#C3E39A",
        "senal_media_texto": "#FFE58F",
        "senal_mala_texto":  "#FFC4CA",
        "dato":              "#8FA68C",
        "dato_tenue":        "#39434E",
        "rejilla":           "#222A34",
        "titulo":            "#E8F2E2",
        "sombra_tarjeta":    "none",
    },
}

# El tema Terminal va TODO en monoespaciada, no solo las cifras.
TEMAS_MONO = {"terminal"}

E = {"1": "4px", "2": "8px", "3": "12px", "4": "16px",
     "6": "24px", "8": "32px", "12": "48px"}
# v1.1: un escalón más grande en todo el cuerpo. 12-13 px se leía bien en
# la exposición (proyector, de cerca) pero apretado en un portafolio.
F = {"micro": "11px", "mini": "13px", "cuerpo": "14.5px", "medio": "16px",
     "sub": "21px", "titulo": "28px", "cifra": "30px", "cifra_xl": "50px",
     "hero": "56px"}
R = {"sm": "4px", "md": "6px", "lg": "10px"}

# Cuerpo en Inter (más legible en tamaños chicos) y titulares en Inter Tight
# (misma familia, más compacta): jerarquía sin mezclar estilos.
FUENTE_UI = "'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif"
FUENTE_TITULO = "'Inter Tight', 'Inter', system-ui, sans-serif"
FUENTE_MONO = "'IBM Plex Mono', ui-monospace, 'Cascadia Code', monospace"

IMPORT_FUENTES = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;600;700&"
    "family=Inter+Tight:wght@500;600;700;800&"
    "family=IBM+Plex+Mono:wght@400;500&display=swap');"
)


def nombre_tema(T: dict[str, str]) -> str:
    """Qué paleta es esta, por su color de fondo."""
    for nombre, paleta in PALETAS.items():
        if paleta["fondo"] == T["fondo"]:
            return nombre
    return "claro"


def css(T: dict[str, str]) -> str:
    """Bloque CSS completo GENERADO desde la paleta activa."""
    tema = nombre_tema(T)
    esquema = "light" if tema == "claro" else "dark"
    # En Terminal el cuerpo entero va en monoespaciada, no solo las cifras.
    fuente_cuerpo = FUENTE_MONO if tema in TEMAS_MONO else FUENTE_UI
    fuente_titulo = FUENTE_MONO if tema in TEMAS_MONO else FUENTE_TITULO
    return f"""<style>
{IMPORT_FUENTES}

:root {{
  --fondo: {T['fondo']};
  --superficie: {T['superficie']};
  --superficie-alta: {T['superficie_alta']};
  --borde: {T['borde']};
  --borde-sutil: {T['borde_sutil']};
  --texto: {T['texto']};
  --texto-medio: {T['texto_medio']};
  --texto-tenue: {T['texto_tenue']};
  --acento: {T['acento']};
  --e1: {E['1']}; --e2: {E['2']}; --e3: {E['3']}; --e4: {E['4']};
  --e6: {E['6']}; --e8: {E['8']}; --e12: {E['12']};
  --r-sm: {R['sm']}; --r-md: {R['md']}; --r-lg: {R['lg']};
}}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
#MainMenu, footer {{ display: none !important; }}

[data-testid="stAppViewContainer"] {{ background: {T['fondo']}; }}
[data-testid="stAppViewBlockContainer"],
.block-container {{
  padding-top: var(--e6) !important;
  padding-bottom: var(--e12) !important;
  max-width: 1400px;
}}

html, body, [data-testid="stAppViewContainer"] * {{
  font-family: {fuente_cuerpo};
  -webkit-font-smoothing: antialiased;
}}
/* El selector `*` de arriba también alcanza a los iconos de Streamlit, que son
   ligaduras tipográficas: sin su fuente, el nombre del icono se imprime literal
   ("arrow_drop_down") al lado del texto. Hay que devolvérsela. El prefijo ^= es
   a propósito: el check del st.status llega como stExpanderIconCheck (y el de
   error como stExpanderIconError) — con el selector exacto se escapaban y la
   palabra "check" aparecía impresa junto al encabezado. */
[data-testid="stIconMaterial"], [data-testid^="stExpanderIcon"],
.material-symbols-rounded, span.material-icons {{
  font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}}
body {{ color: {T['texto']}; font-size: {F['cuerpo']}; }}
[data-testid="stAppViewContainer"] p, [data-testid="stAppViewContainer"] li,
[data-testid="stMarkdownContainer"] {{ color: {T['texto']}; }}

.cifra, .cifra-xl, .mono, table, td, th,
[data-testid="stMetricValue"], .tarjeta-valor, .num {{
  font-variant-numeric: tabular-nums;
  font-feature-settings: "tnum" 1;
}}

h1, h2, h3, h4 {{ color: {T['titulo']}; letter-spacing: -0.02em; font-weight: 600; }}
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
.marca-titulo, .kpi-valor, .hero-rel {{ font-family: {fuente_titulo}; }}
[data-testid="stAppViewContainer"] h1 {{ font-size: {F['titulo']} !important; }}
[data-testid="stAppViewContainer"] h2 {{ font-size: {F['sub']} !important; padding: 0 !important;
                                        margin: 40px 0 12px 0 !important; }}
[data-testid="stAppViewContainer"] h3 {{ font-size: {F['medio']} !important; padding: 0 !important;
                                        margin: 24px 0 8px 0 !important; }}
h1 {{ font-size: {F['titulo']}; font-weight: 700 !important; line-height: 1.12;
      letter-spacing: -0.03em; margin: 0 0 var(--e2) 0; max-width: 40ch;
      animation: aparecer 220ms cubic-bezier(.2,.7,.2,1) both; }}
h2 {{ font-size: {F['sub']}; font-weight: 650 !important; line-height: 1.25;
      margin: var(--e8) 0 var(--e3) 0; max-width: 46ch; }}
h3 {{ font-size: {F['medio']}; margin: var(--e6) 0 var(--e2) 0; }}

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {{
  background: {T['superficie']};
  border-right: 1px solid {T['borde_sutil']};
}}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{ padding-top: var(--e6); }}

/* Línea llana bajo cada botón de navegación: qué hace la pestaña sin entrar.
   El margen negativo la pega a su botón (el gap por defecto la dejaba
   huérfana a media distancia entre dos botones). */
[data-testid="stSidebar"] .nav-desc {{
  font-size: {F['mini']};
  color: {T['texto_tenue']};
  line-height: 1.35;
  margin: -8px 2px var(--e3) 2px;   /* ritmo vertical en escala de 8 */
}}
/* El pie del sidebar es letra chica de verdad: no compite con la
   navegación ni con las descripciones. */
[data-testid="stSidebar"] .sutil {{ font-size: {F['micro']}; }}

/* El selector de estaciones del viaje (control segmentado del área principal)
   va más visible que el tamaño por defecto. Scoped a stMain a propósito: el
   selector de tema también es un stButtonGroup, pero vive en el sidebar y ese
   se queda como está. El font-size va sobre el <p> interno (el texto llega
   como markdown dentro del botón y no hereda del button). */
section[data-testid="stMain"] [data-testid="stButtonGroup"] button {{
  padding: 8px 18px !important;
  cursor: pointer;
  transition: background 150ms ease, color 150ms ease, border-color 150ms ease;
}}
section[data-testid="stMain"] [data-testid="stButtonGroup"] button p {{
  font-size: {F['medio']} !important;
}}
/* El acento aparece al pasar por encima: sin esto, el tema claro casi no
   usaba su índigo y los controles se sentían apagados. */
section[data-testid="stMain"] [data-testid="stButtonGroup"] button:hover {{
  background: {T['acento_fondo']} !important;
  border-color: {T['acento']}55 !important;
}}
section[data-testid="stMain"] [data-testid="stButtonGroup"] button:hover p {{
  color: {T['acento_alto']} !important;
}}

.marca {{
  font-family: {FUENTE_MONO};
  font-size: {F['micro']};
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: {T['texto_tenue']};
  margin-bottom: var(--e1);
}}
.marca-titulo {{
  font-size: {F['medio']};
  font-weight: 600;
  letter-spacing: -0.02em;
  color: {T['texto']};
  margin-bottom: var(--e6);
  line-height: 1.3;
}}

[data-testid="stSidebar"] .stButton > button {{
  width: 100%;
  text-align: left;
  justify-content: flex-start;
  background: transparent;
  border: 1px solid transparent;
  color: {T['texto_medio']};
  font-size: {F['cuerpo']};
  font-weight: 500;
  padding: var(--e2) var(--e3);
  border-radius: var(--r-md);
  transition: background 150ms ease, color 150ms ease, border-color 150ms ease;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
  background: {T['superficie_hover']};
  color: {T['texto']};
  border-color: {T['borde_sutil']};
}}
/* La pestaña activa se reconoce sin leerla: fondo suave, tinta de acento y
   una barra de acento a la izquierda —el mismo gesto en los tres temas. */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
  background: {T['acento_fondo']};
  color: {T['acento_alto']};
  border-color: {T['acento']}55;
  border-left: 3px solid {T['acento']};
}}
/* El hover genérico del primario (más abajo) oscurecía la pestaña activa y
   dejaba su texto ilegible: en el sidebar el activo no cambia al pasar. */
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
[data-testid="stSidebar"] .stButton > button[kind="primary"]:focus {{
  background: {T['acento_fondo']};
  color: {T['acento_alto']};
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
[data-testid="stSidebar"] .stButton > button[kind="primary"] [data-testid="stIconMaterial"] {{
  color: {T['acento_alto']} !important; font-weight: 600;
}}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
  color: {T['texto_medio']} !important;
}}
[data-testid="stSidebar"] label[data-baseweb="checkbox"] span,
[data-testid="stSidebar"] .stToggle span {{ color: {T['texto_medio']}; }}

/* ---------- Tarjetas ---------- */
.tarjeta {{
  box-shadow: {T['sombra_tarjeta']};
  background: {T['superficie']};
  border: 1px solid {T['borde_sutil']};
  border-radius: var(--r-lg);
  padding: var(--e4);
}}
.tarjeta-etiqueta {{
  font-family: {FUENTE_MONO};
  font-size: {F['micro']};
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: {T['texto_tenue']};
  margin-bottom: var(--e2);
}}
/* Las cifras van en mono: el contraste con la sans del texto da el aire
   técnico y además alinea los dígitos entre tarjetas. */
.tarjeta-valor {{
  font-family: {FUENTE_MONO};
  font-size: {F['cifra']};
  font-weight: 500;
  letter-spacing: -0.02em;
  line-height: 1.15;
  color: {T['texto']};
}}
/* Capa 1: la frase en español llano que explica la cifra de la tarjeta. */
.tarjeta-llano {{
  font-size: {F['cuerpo']};
  color: {T['texto']};
  margin-top: var(--e2);
  line-height: 1.55;
}}
/* Capa 2: la precisión técnica, un escalón por debajo en jerarquía. */
.tarjeta-nota {{
  font-size: {F['mini']};
  color: {T['texto_medio']};
  margin-top: var(--e2);
  line-height: 1.5;
}}

/* Entradilla: el párrafo llano bajo el título-pregunta. Más grande que el
   cuerpo porque es lo primero que se lee y decide si alguien sigue leyendo. */
.entradilla {{
  font-size: {F['medio']};
  line-height: 1.65;
  color: {T['texto']};
  max-width: 68ch;
  margin-bottom: var(--e3);
}}
.rejilla-tarjetas {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--e3);
}}

/* ---------- Panel ---------- */
.panel {{
  background: {T['superficie']};
  border: 1px solid {T['borde_sutil']};
  border-radius: var(--r-lg);
  padding: var(--e6);
}}
.panel-titulo {{
  font-size: {F['medio']};
  font-weight: 600;
  letter-spacing: -0.01em;
  margin-bottom: var(--e1);
}}
.eyebrow {{
  font-family: {FUENTE_MONO};
  font-size: {F['micro']};
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: {T['texto_tenue']};
}}
.sutil {{ color: {T['texto_medio']}; font-size: {F['mini']}; line-height: 1.6; }}

/* ---------- Señales ---------- */
.senal {{
  display: flex; gap: var(--e3); align-items: flex-start;
  border-radius: var(--r-md);
  padding: var(--e3) var(--e4);
  border: 1px solid transparent;
  font-size: {F['cuerpo']};
  line-height: 1.55;
}}
.senal-alerta {{
  background: {T['senal_mala_fondo']};
  border-color: {T['senal_mala']}55;
  color: {T['senal_mala_texto']};
}}
.senal-ok {{
  background: {T['senal_buena_fondo']};
  border-color: {T['senal_buena']}55;
  color: {T['senal_buena_texto']};
}}
.senal-aviso {{
  background: {T['senal_media_fondo']};
  border-color: {T['senal_media']}66;
  color: {T['senal_media_texto']};
}}

/* ---------- Controles ---------- */
[data-baseweb="input"] input,
[data-baseweb="select"] > div,
[data-testid="stNumberInput"] input {{
  background: {T['superficie_alta']} !important;
  border: 1px solid {T['borde']} !important;
  border-radius: var(--r-md) !important;
  color: {T['texto']} !important;
  font-size: {F['cuerpo']} !important;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}}
/* Streamlit 1.6x cambió el selectbox a un ComboBox de react-aria: ya no hay
   data-baseweb que pintar. Sin esto quedaba blanco sobre negro en los
   temas oscuros. */
[data-testid="stSelectbox"] [role="group"] {{
  background: {T['superficie_alta']} !important;
  border: 1px solid {T['borde']} !important;
  border-radius: var(--r-md) !important;
  transition: border-color 150ms ease, box-shadow 150ms ease;
}}
[data-testid="stSelectbox"] [role="group"]:focus-within {{
  border-color: {T['acento']} !important;
  box-shadow: 0 0 0 3px {T['acento']}22 !important;
}}
[data-testid="stSelectbox"] input, [data-testid="stSelectbox"] button {{
  color: {T['texto']} !important; background: transparent !important;
  font-size: {F['cuerpo']} !important;
}}
[role="listbox"] {{ background: {T['superficie_alta']} !important;
                   border: 1px solid {T['borde']} !important; }}
[role="listbox"] [role="option"] {{ color: {T['texto']} !important; }}
[role="listbox"] [role="option"][data-focused], [role="listbox"] [role="option"]:hover {{
  background: {T['acento_fondo']} !important; color: {T['acento_alto']} !important;
}}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within {{
  border-color: {T['acento']} !important;
  box-shadow: 0 0 0 3px {T['acento']}22 !important;
}}
[data-testid="stWidgetLabel"] p {{
  font-size: {F['mini']} !important;
  font-weight: 500;
  color: {T['texto_medio']} !important;
  margin-bottom: var(--e1) !important;
}}
[data-baseweb="popover"] li {{ font-size: {F['cuerpo']}; }}
[data-baseweb="popover"] ul {{ background: {T['superficie_alta']} !important; }}
[data-baseweb="popover"] li {{ color: {T['texto']} !important; }}

[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {{
  background: {T['acento']} !important;
  border: 2px solid {T['fondo']} !important;
  box-shadow: 0 0 0 1px {T['acento']} !important;
}}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div {{
  background: {T['dato_tenue']} !important;
}}
[data-testid="stSlider"] [data-testid="stTickBar"] div,
[data-testid="stSlider"] [data-testid="stThumbValue"] {{ color: {T['texto_medio']} !important; }}

.stButton > button[kind="primary"] {{
  background: {T['acento']};
  border: 1px solid {T['acento']};
  color: {T['boton_texto']};
  font-weight: 600;
  font-size: {F['cuerpo']};
  border-radius: var(--r-md);
  padding: var(--e2) var(--e4);
  transition: background 150ms ease, transform 150ms ease;
}}
.stButton > button[kind="primary"]:hover {{ background: {T['acento_alto']}; }}
.stButton > button:focus-visible {{
  outline: 2px solid {T['acento']};
  outline-offset: 2px;
}}
.stButton > button[kind="secondary"] {{
  background: {T['superficie_alta']};
  border: 1px solid {T['borde']};
  color: {T['texto']};
}}
/* Terciario: es un enlace de navegación interna, no un botón. Sin esto hereda
   el color de texto normal y no se lee como algo pulsable. */
.stButton > button[kind="tertiary"] {{
  background: transparent;
  border: none;
  padding: 0;
  color: {T['acento_alto']};
}}
.stButton > button[kind="tertiary"] p {{
  color: {T['acento_alto']} !important;
  text-decoration: underline;
  text-underline-offset: 3px;
}}
.stButton > button[kind="tertiary"]:hover p {{ color: {T['acento']} !important; }}

/* Radio */
[data-testid="stRadio"] label p {{ color: {T['texto']} !important; }}

/* Selector segmentado (tema de la barra lateral). Sin esto hereda los
   colores por defecto de Streamlit, que no conocen la paleta activa: en
   Terminal las etiquetas quedaban ilegibles. En esta version el control
   se rinde como stButtonGroup con role="radio"; se cubre tambien el
   testid stSegmentedControl de otras versiones. */
[data-testid="stButtonGroup"] button,
[data-testid="stSegmentedControl"] button {{
  background: {T['superficie_alta']} !important;
  border: 1px solid {T['borde']} !important;
  color: {T['texto']} !important;
}}
[data-testid="stButtonGroup"] button p,
[data-testid="stSegmentedControl"] button p {{
  color: {T['texto']} !important;
}}
[data-testid="stButtonGroup"] button[aria-checked="true"],
[data-testid="stSegmentedControl"] button[aria-checked="true"] {{
  background: {T['acento']} !important;
  border-color: {T['acento']} !important;
}}
[data-testid="stButtonGroup"] button[aria-checked="true"] p,
[data-testid="stSegmentedControl"] button[aria-checked="true"] p {{
  color: {T['boton_texto']} !important;
}}

/* ---------- Tablas ---------- */
.tabla {{ width: 100%; border-collapse: collapse; font-size: {F['mini']}; }}
.tabla th {{
  font-family: {FUENTE_MONO};
  font-size: {F['micro']};
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: {T['texto_tenue']};
  text-align: right;
  font-weight: 500;
  padding: var(--e2) var(--e3);
  border-bottom: 1px solid {T['borde']};
}}
.tabla th:first-child, .tabla td:first-child {{ text-align: left; }}
.tabla th.izq {{ text-align: left; }}
.tabla td {{
  padding: var(--e2) var(--e3);
  border-bottom: 1px solid {T['borde_sutil']};
  color: {T['texto']};
  text-align: right;
}}
.tabla tr:last-child td {{ border-bottom: none; }}
.tabla .destacada td {{ color: {T['texto']}; font-weight: 600; }}
.tabla .destacada {{ background: {T['acento_fondo']}; }}
.tabla .atenuada td {{ color: {T['texto_medio']}; }}

/* Ecuaciones lado a lado (sección torneo) */
.ecuacion {{
  font-family: {FUENTE_MONO};
  font-size: {F['mini']};
  line-height: 1.8;
  background: {T['superficie_alta']};
  border: 1px solid {T['borde_sutil']};
  border-radius: var(--r-md);
  padding: var(--e4);
  overflow-x: auto;
  white-space: pre;
  color: {T['texto']};
}}

/* ---------- Bloque «por qué»: dato / mecánica / hipótesis ----------
   Las tres etiquetas tienen color distinto a propósito: separar lo medido de
   lo que es consecuencia de la definición y de lo que es interpretación es el
   método, y tiene que verse de un vistazo. */
.porque {{
  display: flex; flex-direction: column; gap: var(--e2);
  margin-top: var(--e2);
}}

/* Título-oración: dice el hallazgo, no el nombre de la variable. Va sobre el
   gráfico, donde antes solo iba la etiqueta de la variable. */
.titulo-grafico {{
  font-size: {F['cuerpo']};
  font-weight: 600;
  line-height: 1.45;
  color: {T['texto']};
  margin-bottom: var(--e1);
}}
.porque-fila {{
  display: flex; gap: var(--e2); align-items: baseline;
  font-size: {F['mini']};
  line-height: 1.55;
  color: {T['texto_medio']};
}}
.porque-fila > span:last-child {{ flex: 1; }}
.etiqueta-dato, .etiqueta-mecanica, .etiqueta-hipotesis {{
  font-family: {FUENTE_MONO};
  font-size: {F['micro']};
  letter-spacing: 0.06em;
  text-transform: uppercase;
  padding: 1px 6px;
  border-radius: var(--r-sm);
  white-space: nowrap;
  flex-shrink: 0;
}}
.etiqueta-dato {{
  background: {T['acento_fondo']}; color: {T['acento_alto']};
}}
.etiqueta-mecanica {{
  background: {T['senal_media_fondo']}; color: {T['senal_media_texto']};
}}
.etiqueta-hipotesis {{
  background: {T['superficie_alta']}; color: {T['texto_tenue']};
  border: 1px dashed {T['borde']};
}}

/* ---------- Hallazgos de auditoría ---------- */
.hallazgo {{
  border-left: 2px solid {T['borde']};
  padding-left: var(--e3);
}}
.hallazgo-cab {{
  display: flex; align-items: baseline; gap: var(--e2);
  flex-wrap: wrap;
  margin-bottom: var(--e1);
  color: {T['texto']};
  font-size: {F['cuerpo']};
}}
/* Etiqueta de ORIGEN: dónde nació el problema. Va junto a la de estado, y se
   distingue de ella por el borde: el estado es macizo, el origen perfilado. */
.origen {{
  font-family: {FUENTE_MONO};
  font-size: {F['micro']};
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 1px 5px;
  border-radius: var(--r-sm);
  white-space: nowrap;
  background: transparent;
}}
.origen-datos {{ color: {T['senal_media_texto']}; border: 1px solid {T['senal_media']}; }}
.origen-propia {{ color: {T['acento_alto']}; border: 1px solid {T['acento']}; }}
.origen-doc {{ color: {T['texto_tenue']}; border: 1px solid {T['borde']}; }}
.leyenda-origen {{
  display: flex; flex-direction: column; gap: var(--e1);
  font-size: {F['mini']};
  line-height: 1.55;
  color: {T['texto_medio']};
  margin: var(--e3) 0 var(--e4) 0;
  padding-left: var(--e3);
  border-left: 2px solid {T['borde_sutil']};
}}
.leyenda-origen > div {{ display: flex; gap: var(--e2); align-items: baseline; }}

/* Enlace a la evidencia en GitHub: el archivo se abre, el §n queda como texto
   porque GitHub no ancla por número de sección. */
a.chip-evidencia {{
  font-family: {FUENTE_MONO};
  font-size: {F['micro']};
  color: {T['acento_alto']};
  text-decoration: none;
  border-bottom: 1px solid {T['borde']};
  white-space: nowrap;
}}
a.chip-evidencia:hover {{ border-bottom-color: {T['acento_alto']}; }}

/* Pista: término con explicación al pasar el cursor. */
.pista {{ border-bottom: 1px dotted {T['texto_tenue']}; cursor: help; }}

/* Destino del enlace «¿Por qué tan alto?»: marca el bloque al que se saltó. */
h2.resaltado {{
  background: {T['acento_fondo']};
  border-left: 3px solid {T['acento']};
  padding: var(--e2) var(--e3);
  border-radius: var(--r-sm);
}}

/* ---------- Fila de veredicto (cabina) ----------
   La cifra y el veredicto en una sola línea, para que la franja y las
   consecuencias del umbral quepan sin scroll en un portátil de 768 px. */
.fila-veredicto {{
  display: flex; align-items: baseline; gap: var(--e3);
  flex-wrap: wrap;
  margin-bottom: var(--e1);
}}
.cifra-veredicto {{
  font-family: {FUENTE_MONO};
  font-size: {F['cifra_xl']};
  font-weight: 500;
  letter-spacing: -0.03em;
  line-height: 1;
}}
.texto-veredicto {{
  font-size: {F['sub']};
  font-weight: 600;
  letter-spacing: -0.01em;
}}

/* ---------- Referencias ----------
   Las llamadas [1] son superíndices clicables; la lista de abajo numera igual.
   Criterio de tesis: toda afirmación que no sea cálculo propio lleva una. */
a.ref-llamada {{
  font-size: 0.75em;
  vertical-align: super;
  line-height: 0;
  color: {T['acento']};
  text-decoration: none;
  padding: 0 1px;
  font-family: {FUENTE_MONO};
}}
a.ref-llamada:hover {{ text-decoration: underline; }}
.ref-lista {{
  display: flex; flex-direction: column; gap: var(--e3);
  font-size: {F['mini']};
  line-height: 1.55;
  color: {T['texto_medio']};
}}
.ref-item {{ display: flex; gap: var(--e2); }}
.ref-num {{
  font-family: {FUENTE_MONO};
  color: {T['acento']};
  flex-shrink: 0;
  min-width: 2.2em;
}}
.ref-item a {{ color: {T['acento_alto']}; word-break: break-word; }}
.ref-acceso {{
  font-family: {FUENTE_MONO};
  font-size: {F['micro']};
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 1px 5px;
  border-radius: var(--r-sm);
  margin-left: var(--e1);
  white-space: nowrap;
}}
.ref-abierto {{ background: {T['senal_buena_fondo']}; color: {T['senal_buena_texto']}; }}
.ref-pago    {{ background: {T['superficie_alta']}; color: {T['texto_tenue']}; }}

/* ---------- Expander: la capa 2 ---------- */
[data-testid="stExpander"] {{
  border: 1px solid {T['borde_sutil']} !important;
  border-radius: var(--r-md) !important;
  background: {T['superficie']} !important;
}}
/* Borde de acento a la izquierda: el bloque se lee como un aparte, no como
   cuerpo principal. */
[data-testid="stExpander"] {{
  border-left: 3px solid {T['acento']} !important;
}}
[data-testid="stExpander"] summary {{
  font-size: {F['mini']} !important;
  font-weight: 500;
  color: {T['texto_medio']} !important;
  padding: var(--e3) var(--e4) !important;
  display: flex !important;
  align-items: center !important;   /* icono y etiqueta a la misma base */
  gap: var(--e1);
}}
[data-testid="stExpander"] summary:hover {{ color: {T['acento_alto']} !important; }}
/* Padding uniforme: antes sobraba aire en medio y no habia nada abajo. */
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
  padding: 0 var(--e4) var(--e4) var(--e4) !important;
}}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] > div {{
  gap: var(--e3) !important;
}}
[data-testid="stExpander"] p,
[data-testid="stExpander"] .sutil {{
  font-size: {F['mini']} !important;
  line-height: 1.6 !important;
  max-width: 75ch;               /* de borde a borde en monitor ancho no se lee */
}}
[data-testid="stExpander"] .sutil br + br {{ line-height: 2.2; }}

hr, [data-testid="stDivider"] {{ border-color: {T['borde_sutil']} !important; }}

[data-testid="stIFrame"] {{ background: transparent !important; color-scheme: {esquema}; }}

/* ==========================================================================
   v1.1 — capa de presentación del portafolio
   ========================================================================== */

/* Movimiento: una sola curva de entrada para todo. Suave y corta: la página
   se «asienta» en vez de saltar. Se apaga entera con reduced-motion (abajo). */
@keyframes aparecer {{
  from {{ opacity: 0; transform: translateY(4px); }}
  to   {{ opacity: 1; transform: none; }}
}}
@keyframes crecer-x {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
@keyframes pulso {{
  0%, 100% {{ box-shadow: 0 0 0 0 {T['acento']}33; }}
  50%      {{ box-shadow: 0 0 0 6px {T['acento']}00; }}
}}
.entradilla, .tarjeta, .panel, .kpi, .hero-cifra, .tres-numeros > div,
.porque, .hallazgo, .fila-veredicto, .paso-viaje, .estacion-cab {{
  animation: aparecer 220ms cubic-bezier(.2,.7,.2,1) both;
}}
.rejilla-tarjetas > .tarjeta:nth-child(2) {{ animation-delay: 30ms; }}
.rejilla-tarjetas > .tarjeta:nth-child(3) {{ animation-delay: 60ms; }}
.rejilla-tarjetas > .tarjeta:nth-child(4) {{ animation-delay: 90ms; }}
.tarjeta {{ transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease; }}
.tarjeta:hover {{ transform: translateY(-2px); border-color: {T['acento']}55; }}

.eyebrow-seccion {{ color: {T['acento_alto']}; margin-bottom: var(--e2); }}
.entradilla {{ font-size: {F['medio']}; max-width: 70ch; color: {T['texto_medio']}; }}

/* Franja de cifras clave: la portada ejecutiva */
.franja-kpi {{
  display: grid; grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px; background: {T['borde_sutil']};
  border: 1px solid {T['borde_sutil']}; border-radius: var(--r-lg);
  overflow: hidden; margin: var(--e4) 0 var(--e6) 0;
  box-shadow: {T['sombra_tarjeta']};
}}
.kpi {{ background: {T['superficie']}; padding: var(--e4) var(--e4) var(--e3); }}
.kpi-valor {{
  font-size: 28px; font-weight: 700; letter-spacing: -0.03em;
  color: {T['titulo']}; line-height: 1.1; font-variant-numeric: tabular-nums;
}}
.kpi-rotulo {{ font-size: {F['mini']}; color: {T['texto']}; margin-top: 4px; font-weight: 500; }}
.kpi-nota {{ font-family: {FUENTE_MONO}; font-size: {F['micro']}; color: {T['texto_tenue']};
            letter-spacing: 0.04em; margin-top: 2px; }}

/* Cifra protagonista del ingreso */
.hero-cifra {{
  background: linear-gradient(135deg, {T['acento_fondo']} 0%, {T['superficie']} 70%);
  border: 1px solid {T['acento']}33; border-radius: 14px;
  padding: var(--e6) var(--e6) var(--e8); margin-bottom: var(--e4);
  box-shadow: {T['sombra_tarjeta']};
}}
.hero-fila {{ display: flex; align-items: baseline; gap: var(--e4); flex-wrap: wrap;
             margin: var(--e2) 0 var(--e6) 0; }}
.hero-valor {{
  font-family: {FUENTE_MONO}; font-size: {F['hero']}; font-weight: 500;
  letter-spacing: -0.04em; line-height: 1; color: {T['acento_alto']};
  font-variant-numeric: tabular-nums;
}}
.hero-rel {{ font-size: {F['sub']}; font-weight: 600; color: {T['texto']}; letter-spacing: -0.01em; }}
.hero-barra {{ position: relative; height: 10px; border-radius: 999px;
              background: {T['dato_tenue']}66; }}
.hero-relleno {{
  position: absolute; inset: 0 auto 0 0; border-radius: 999px;
  background: linear-gradient(90deg, {T['acento']}, {T['acento_alto']});
  transform-origin: left; animation: crecer-x 250ms cubic-bezier(.2,.7,.2,1) both;
  transition: width 250ms cubic-bezier(.2,.7,.2,1);
}}
.hero-marca {{ position: absolute; top: -6px; bottom: -6px; width: 2px;
              background: {T['texto']}; border-radius: 2px; }}
.hero-marca-der span {{ left: auto !important; right: -2px; transform: none !important; }}
.hero-marca span {{
  position: absolute; top: 20px; left: 50%; transform: translateX(-50%);
  white-space: nowrap; font-family: {FUENTE_MONO}; font-size: {F['micro']};
  letter-spacing: 0.06em; text-transform: uppercase; color: {T['texto_tenue']};
}}

/* Los tres porcentajes distintos del clasificador, uno por fila */
.tres-numeros {{ display: grid; grid-template-columns: repeat(3, minmax(0,1fr));
                gap: var(--e3); margin: 0 0 var(--e3) 0; }}
.tres-numeros > div {{
  background: {T['superficie']}; border: 1px solid {T['borde_sutil']};
  border-radius: var(--r-md); padding: var(--e3); display: flex;
  flex-direction: column; gap: 2px;
}}
.tres-numeros b {{ font-family: {FUENTE_MONO}; font-size: 22px; font-weight: 500; }}
.tres-numeros span {{ font-size: {F['mini']}; color: {T['texto_medio']}; line-height: 1.4; }}

/* Cajas con borde (formulario): superficie blanca y sombra suave */
.st-key-caja_form_reg, .st-key-caja_form_clf, .st-key-caja_form_maq {{
  background: {T['superficie']} !important;
  border: 1px solid {T['borde_sutil']} !important;
  border-radius: 14px !important;
  box-shadow: {T['sombra_tarjeta']};
}}
.derivada {{ padding: var(--e2) var(--e3); background: {T['superficie_alta']};
            border-radius: var(--r-md); margin-bottom: var(--e2); }}

/* Pills (perfiles de ejemplo) */
[data-testid="stPills"] button, [data-testid="stButtonGroup"] button[kind^="pills"] {{
  border-radius: 999px !important;
  transition: background 150ms ease, border-color 150ms ease, transform 150ms ease;
}}
[data-testid="stPills"] button:hover {{ transform: translateY(-1px); }}

/* Slider: pista de acento y pulgar con halo al tocarlo */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]:focus,
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"]:hover {{
  animation: pulso 1.2s ease-out 1;
}}

/* Tablas: envoltura con scroll horizontal en móvil y fila con hover */
.tabla-envoltura {{
  overflow-x: auto; border: 1px solid {T['borde_sutil']};
  border-radius: var(--r-lg); background: {T['superficie']};
  box-shadow: {T['sombra_tarjeta']};
}}
.tabla-envoltura .tabla th {{ background: {T['superficie_alta']}; }}
.tabla tbody tr {{ transition: background 120ms ease; }}
.tabla tbody tr:hover {{ background: {T['superficie_hover']}; }}

.lista-limites {{ display: flex; flex-direction: column; gap: 14px;
                 font-size: {F['cuerpo']}; line-height: 1.65; color: {T['texto_medio']}; }}

/* Sala de máquinas: cabecera de estación y los tres pasos */
.estacion-cab {{ display: flex; align-items: center; gap: var(--e3);
                font-size: {F['sub']}; font-weight: 650; color: {T['titulo']};
                margin: var(--e2) 0 var(--e3) 0; }}
.estacion-num {{
  display: inline-grid; place-items: center; width: 34px; height: 34px;
  border-radius: 50%; background: {T['acento']}; color: {T['boton_texto']};
  font-family: {FUENTE_MONO}; font-size: 15px;
}}
.paso-viaje {{ border-top: 2px solid {T['acento']}; padding-top: var(--e3);
              height: 100%; }}
.paso-viaje .sutil {{ font-size: {F['cuerpo']}; color: {T['texto']}; margin-top: var(--e2); }}

/* ==========================================================================
   v1.2 — barra superior, gráficos en línea y resumen «de un vistazo»
   ========================================================================== */

/* Barra superior: marca + secciones + idioma + tema. Reemplaza al sidebar y
   devuelve su ancho al contenido. Pegajosa: la navegación nunca se pierde. */
.st-key-barra {{
  position: sticky; top: 0; z-index: 50;
  background: {T['fondo']}ee;
  backdrop-filter: blur(6px);
  border-bottom: 1px solid {T['borde_sutil']};
  padding: var(--e2) 0 !important;
  margin-bottom: var(--e4);
}}
.marca-barra {{
  display: flex; align-items: baseline; gap: var(--e2);
  white-space: nowrap; font-size: {F['cuerpo']}; color: {T['texto']};
}}
.marca-barra .rombo {{ color: {T['acento']}; font-size: 18px; }}
.marca-barra b {{ font-weight: 650; }}
.marca-barra .quien {{ color: {T['texto_medio']}; border-bottom: 1px dotted {T['texto_tenue']};
                      cursor: help; }}
/* Navegación activa: fondo de acento pleno. El resto, texto medio sin borde. */
.st-key-sec [data-testid="stButtonGroup"] button {{
  background: transparent !important; border-color: transparent !important;
  padding: 6px 12px !important;
}}
.st-key-sec [data-testid="stButtonGroup"] button p {{
  color: {T['texto_medio']} !important; font-size: {F['cuerpo']} !important;
  font-weight: 500;
}}
.st-key-sec [data-testid="stButtonGroup"] button:hover p {{ color: {T['acento_alto']} !important; }}
.st-key-sec [data-testid="stButtonGroup"] button[aria-checked="true"] {{
  background: {T['acento']} !important; border-color: {T['acento']} !important;
}}
.st-key-sec [data-testid="stButtonGroup"] button[aria-checked="true"] p {{
  color: {T['boton_texto']} !important; font-weight: 600;
}}
.st-key-lang [data-testid="stButtonGroup"] button,
.st-key-theme [data-testid="stButtonGroup"] button {{ padding: 4px 10px !important; }}
.st-key-lang [data-testid="stButtonGroup"] button p,
.st-key-theme [data-testid="stButtonGroup"] button p {{ font-size: {F['mini']} !important; }}

/* Gráficos en línea (st.html): heredan fuentes y paleta de la página, sin
   iframe ni @import propio. La caja tiene alto fijo y el SVG se ajusta DENTRO
   (preserveAspectRatio meet): el mismo contrato que tenían los iframes. */
.grafico {{ width: 100%; }}
.grafico svg {{ display: block; width: 100%; height: 100%; overflow: visible; }}
.grafico svg text {{ font-family: {fuente_cuerpo}; font-variant-numeric: tabular-nums; }}
.grafico .et {{ font-family: {FUENTE_MONO}; font-size: 10px; letter-spacing: 0.08em;
               text-transform: uppercase; fill: {T['texto_tenue']}; }}
.grafico .vl {{ font-size: 12px; fill: {T['texto']}; }}
.grafico .vs {{ font-size: 11px; fill: {T['texto_medio']}; }}
.grafico .anim-barra {{ transform-box: fill-box; transform-origin: left center;
                       animation: g-crecer-x 240ms cubic-bezier(.2,.7,.2,1) both; }}
.grafico .anim-columna {{ transform-box: fill-box; transform-origin: center bottom;
                         animation: g-crecer-y 240ms cubic-bezier(.2,.7,.2,1) both; }}
.grafico .anim-trazo {{ stroke-dasharray: 1; stroke-dashoffset: 1;
                       animation: g-trazo 250ms cubic-bezier(.4,0,.2,1) forwards; }}
.grafico .anim-celda {{ animation: g-aparecer 200ms ease both; }}
.grafico .anim-punto {{ transform-box: fill-box; transform-origin: center;
                       animation: g-pop 220ms cubic-bezier(.3,1.4,.5,1) both; }}
@keyframes g-crecer-x {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
@keyframes g-crecer-y {{ from {{ transform: scaleY(0); }} to {{ transform: scaleY(1); }} }}
@keyframes g-trazo {{ to {{ stroke-dashoffset: 0; }} }}
@keyframes g-aparecer {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes g-pop {{ from {{ transform: scale(0); }} to {{ transform: scale(1); }} }}

/* Resumen de un vistazo: cifras grandes con su rótulo, y una frase. */
.vistazo-cifras {{ display: flex; flex-direction: column; gap: var(--e4); }}
.vistazo-cifra b {{
  display: block; font-family: {FUENTE_MONO}; font-size: {F['cifra']};
  font-weight: 500; letter-spacing: -0.02em; color: {T['acento_alto']}; line-height: 1.1;
}}
.vistazo-cifra span {{ font-size: {F['mini']}; color: {T['texto_medio']}; line-height: 1.45; }}
.vistazo-frase {{ font-size: {F['medio']}; line-height: 1.55; color: {T['texto']};
                 border-left: 3px solid {T['acento']}; padding-left: var(--e3); }}

/* Jerarquía del tema claro: las cabeceras de bloque llevan una marca de
   acento; los temas oscuros ya destacan por contraste. */
h2 {{ border-left: 3px solid {T['acento']}; padding-left: var(--e3) !important; }}

/* Firma: pie de página y sidebar */
.pie {{
  margin-top: var(--e12); padding-top: var(--e6);
  border-top: 1px solid {T['borde_sutil']};
  font-size: {F['mini']}; color: {T['texto_tenue']}; line-height: 1.8;
}}
.pie-autor {{ color: {T['texto']}; font-size: {F['cuerpo']}; }}
.pie a {{ color: {T['acento_alto']}; text-decoration: none; }}
.pie a:hover {{ text-decoration: underline; }}
.sidebar-firma {{
  margin-top: var(--e4); padding-top: var(--e3);
  border-top: 1px solid {T['borde_sutil']};
  font-size: {F['mini']}; color: {T['texto_medio']}; line-height: 1.5;
}}
.sidebar-firma b {{ color: {T['texto']}; }}

@media (max-width: 900px) {{
  /* En móvil el sidebar tapa todo: ahí SÍ hace falta poder cerrarlo. */
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarCollapsedControl"],
  [data-testid="stExpandSidebarButton"],
  [data-testid="stHeader"] {{ display: flex !important; }}
  [data-testid="stHeader"] {{ background: transparent !important; }}
  /* El botón para reabrir el sidebar vive DENTRO de stToolbar: se muestra la
     barra y se esconde todo lo demás que trae. */
  [data-testid="stToolbar"] {{ display: flex !important; }}
  [data-testid="stToolbarActions"], [data-testid="stMainMenu"],
  [data-testid="stAppDeployButton"], #MainMenu {{ display: none !important; }}
  [data-testid="stExpandSidebarButton"] {{
    background: {T['superficie']} !important; border: 1px solid {T['borde']};
    border-radius: var(--r-md); color: {T['texto']} !important;
  }}
  /* Barra superior en móvil: la marca y los selectores en una fila, las
     secciones debajo en una sola línea con scroll horizontal. */
  .st-key-barra {{ flex-wrap: wrap !important; row-gap: var(--e2) !important; }}
  .st-key-sec {{ order: 3; width: 100% !important; max-width: 100%; overflow-x: auto; }}
  .st-key-sec [data-testid="stButtonGroup"] > div {{ flex-wrap: nowrap !important; }}
  .st-key-sec [data-testid="stButtonGroup"] button {{ white-space: nowrap; flex-shrink: 0; }}
  .franja-kpi {{ grid-template-columns: repeat(2, minmax(0,1fr)); }}
  .tres-numeros {{ grid-template-columns: 1fr; }}
  .hero-valor {{ font-size: 40px; }}
  h1 {{ font-size: 26px; }}
}}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }}
}}

@media (max-width: 900px) {{
  .block-container {{ padding-left: var(--e4) !important; padding-right: var(--e4) !important; }}
  .tarjeta-valor {{ font-size: {F['titulo']}; }}
  .rejilla-tarjetas {{ grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }}
}}
</style>"""


def css_iframe(T: dict[str, str]) -> str:
    """
    CSS mínimo del contenido de `st.components.v1.html`: el iframe no hereda
    nada del padre, así que la paleta ACTIVA se pasa también aquí.

    El `color-scheme` interno DEBE coincidir con el del iframe padre: si el
    padre es dark y el documento embebido queda en 'normal', Chromium pinta
    un lienzo blanco opaco detrás del contenido aunque todo sea transparente.
    """
    tema = nombre_tema(T)
    esquema = "light" if tema == "claro" else "dark"
    fuente_cuerpo = FUENTE_MONO if tema in TEMAS_MONO else FUENTE_UI
    return f"""
{IMPORT_FUENTES}
html {{ color-scheme: {esquema}; }}
html, body {{
  margin: 0; padding: 0; background: transparent;
  height: 100%;
  font-family: {fuente_cuerpo};
  font-variant-numeric: tabular-nums;
}}
/* El iframe de components.html lleva alto FIJO y scrolling=False. Con
   `width:100%; height:auto` el SVG se escalaba solo por el ancho: en una
   ventana ancha crecía por debajo del borde del iframe y la fila inferior de
   la matriz de confusión quedaba cortada. Con `height:100%` y el
   preserveAspectRatio por defecto (meet) el dibujo se ajusta DENTRO de la
   caja: se encoge si hace falta, pero nunca se sale. */
svg {{ display: block; width: 100%; height: 100%; overflow: visible; }}
.et {{ font-family: {FUENTE_MONO}; font-size: 10px; letter-spacing: 0.08em;
       text-transform: uppercase; fill: {T['texto_tenue']}; }}
.vl {{ font-size: 12px; fill: {T['texto']}; font-variant-numeric: tabular-nums; }}
.vs {{ font-size: 11px; fill: {T['texto_medio']}; font-variant-numeric: tabular-nums; }}
/* Entradas de los gráficos: barras que crecen, trazos que se dibujan. Los
   hooks (clases) los pone graficos.py; aquí solo el movimiento. */
.anim-barra {{ transform-box: fill-box; transform-origin: left center;
              animation: g-crecer-x 620ms cubic-bezier(.2,.7,.2,1) both; }}
.anim-columna {{ transform-box: fill-box; transform-origin: center bottom;
                animation: g-crecer-y 620ms cubic-bezier(.2,.7,.2,1) both; }}
.anim-trazo {{ stroke-dasharray: 1; stroke-dashoffset: 1;
              animation: g-trazo 1100ms cubic-bezier(.4,0,.2,1) 120ms forwards; }}
.anim-celda {{ animation: g-aparecer 500ms ease both; }}
.anim-punto {{ transform-box: fill-box; transform-origin: center;
              animation: g-pop 480ms cubic-bezier(.3,1.5,.5,1) both; }}
@keyframes g-crecer-x {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}
@keyframes g-crecer-y {{ from {{ transform: scaleY(0); }} to {{ transform: scaleY(1); }} }}
@keyframes g-trazo {{ to {{ stroke-dashoffset: 0; }} }}
@keyframes g-aparecer {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes g-pop {{ from {{ transform: scale(0); }} to {{ transform: scale(1); }} }}
@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; transition: none !important; }}
  .anim-trazo {{ stroke-dasharray: none; stroke-dashoffset: 0; }}
}}
"""
