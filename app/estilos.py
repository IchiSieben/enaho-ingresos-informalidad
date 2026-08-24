# estilos.py — sistema de diseño: tokens y CSS generado
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
"""
FASE 3 — Sistema de diseño (adaptado del proyecto SIS-diabetes).

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
accionable para focalización), verde = sin señal. El acento índigo queda solo
para interacción, nunca significa condición laboral.
"""

from __future__ import annotations

PALETAS: dict[str, dict[str, str]] = {
    "oscuro": {
        "fondo":             "#0D0F12",
        "superficie":        "#14181F",
        "superficie_alta":   "#1A1F28",
        "superficie_hover":  "#202632",
        "borde":             "#272E3A",
        "borde_sutil":       "#1C222B",
        "texto":             "#E7EAF0",
        "texto_medio":       "#98A1B0",
        # Aclarado de #6B7585: aquel daba 3,8:1 sobre superficie, por debajo
        # del AA que exige texto pequeño, y este color se usa justo en las
        # etiquetas pequeñas (.eyebrow, .et, .tarjeta-etiqueta).
        "texto_tenue":       "#778191",
        "acento":            "#6E7BF2",
        "acento_alto":       "#8A94F7",
        "acento_fondo":      "#1B1F38",
        "boton_texto":       "#0B0D14",
        "senal_buena":       "#3DD68C",
        "senal_media":       "#E0A33E",
        "senal_mala":        "#E5484D",
        "senal_buena_fondo": "#12241C",
        "senal_media_fondo": "#241D10",
        "senal_mala_fondo":  "#2A1416",
        "senal_buena_texto": "#B6EED2",
        "senal_media_texto": "#F0D9AC",
        "senal_mala_texto":  "#F7C9CB",
        "dato":              "#8B95A6",
        "dato_tenue":        "#3A424F",
        "rejilla":           "#222834",
    },
    "claro": {
        "fondo":             "#F7F5F0",   # blanco hueso, no #FFF puro
        "superficie":        "#FCFBF8",
        "superficie_alta":   "#F1EFE8",
        "superficie_hover":  "#ECE9E1",
        "borde":             "#D5D1C6",
        "borde_sutil":       "#E5E2D9",
        "texto":             "#1E232B",
        "texto_medio":       "#49525F",   # 7,9:1 sobre superficie — AA holgado
        "texto_tenue":       "#5F6875",   # 5,9:1 — AA en texto pequeño
        "acento":            "#4353CC",   # índigo oscurecido: 6,3:1 sobre fondo
        "acento_alto":       "#3542B8",
        "acento_fondo":      "#E6E8FA",
        "boton_texto":       "#FFFFFF",
        "senal_buena":       "#177A4C",
        "senal_media":       "#8A5D0B",
        "senal_mala":        "#B92F33",
        "senal_buena_fondo": "#E2F2E9",
        "senal_media_fondo": "#F6ECD6",
        "senal_mala_fondo":  "#F9E3E4",
        "senal_buena_texto": "#0E5636",
        "senal_media_texto": "#6B4A0C",
        "senal_mala_texto":  "#8C2226",
        "dato":              "#5B6472",
        "dato_tenue":        "#CBD0D9",
        "rejilla":           "#E4E1D8",
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
        "senal_buena":       "#5FD68C",
        "senal_media":       "#FFD43B",
        "senal_mala":        "#FF7B72",
        "senal_buena_fondo": "#0E2418",
        "senal_media_fondo": "#241E08",
        "senal_mala_fondo":  "#2A1315",
        "senal_buena_texto": "#9FE8BC",
        "senal_media_texto": "#FFE58F",
        "senal_mala_texto":  "#FFB3AE",
        "dato":              "#8FA68C",
        "dato_tenue":        "#39434E",
        "rejilla":           "#222A34",
    },
}

# El tema Terminal va TODO en monoespaciada, no solo las cifras.
TEMAS_MONO = {"terminal"}

E = {"1": "4px", "2": "8px", "3": "12px", "4": "16px",
     "6": "24px", "8": "32px", "12": "48px"}
F = {"micro": "11px", "mini": "12px", "cuerpo": "13px", "medio": "15px",
     "sub": "18px", "titulo": "24px", "cifra": "32px", "cifra_xl": "44px"}
R = {"sm": "4px", "md": "6px", "lg": "10px"}

FUENTE_UI = "'Inter Tight', system-ui, -apple-system, sans-serif"
FUENTE_MONO = "'IBM Plex Mono', ui-monospace, 'Cascadia Code', monospace"

IMPORT_FUENTES = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Inter+Tight:wght@400;500;600;700&"
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

h1, h2, h3, h4 {{ color: {T['texto']}; letter-spacing: -0.02em; font-weight: 600; }}
h1 {{ font-size: {F['titulo']}; margin: 0 0 var(--e1) 0; }}
h2 {{ font-size: {F['sub']}; margin: var(--e6) 0 var(--e3) 0; }}
h3 {{ font-size: {F['medio']}; margin: var(--e4) 0 var(--e2) 0; }}

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {{
  background: {T['superficie']};
  border-right: 1px solid {T['borde_sutil']};
}}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{ padding-top: var(--e6); }}

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
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
  background: {T['acento_fondo']};
  color: {T['acento_alto']};
  border-color: {T['acento']}55;
}}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
  color: {T['texto_medio']} !important;
}}
[data-testid="stSidebar"] label[data-baseweb="checkbox"] span,
[data-testid="stSidebar"] .stToggle span {{ color: {T['texto_medio']}; }}

/* ---------- Tarjetas ---------- */
.tarjeta {{
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
@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; transition: none !important; }}
}}
"""
