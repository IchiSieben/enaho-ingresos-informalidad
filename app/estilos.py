"""
FASE 3 — Sistema de diseño (adaptado del proyecto SIS-diabetes).

Los tokens viven en un DICCIONARIO DE PYTHON y de ahí se GENERA el CSS: los
SVG de `graficos.py` viajan a un iframe (`st.components.v1.html`) que no ve
las variables CSS del padre, así que la única fuente de verdad de color tiene
que estar en Python y pasarse como parámetro a ambos mundos.

Novedad de este proyecto: DOS paletas con las mismas claves en `PALETAS`
("oscuro"/"claro") y un toggle en la barra lateral persistido en
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
        "texto_tenue":       "#6B7585",
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
}

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


def css(T: dict[str, str]) -> str:
    """Bloque CSS completo GENERADO desde la paleta activa."""
    esquema = "dark" if T["fondo"] == PALETAS["oscuro"]["fondo"] else "light"
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
  font-family: {FUENTE_UI};
  -webkit-font-smoothing: antialiased;
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
.tarjeta-valor {{
  font-size: {F['cifra']};
  font-weight: 600;
  letter-spacing: -0.03em;
  line-height: 1.05;
  color: {T['texto']};
}}
.tarjeta-nota {{
  font-size: {F['mini']};
  color: {T['texto_medio']};
  margin-top: var(--e2);
  line-height: 1.5;
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

/* Radio */
[data-testid="stRadio"] label p {{ color: {T['texto']} !important; }}

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
    esquema = "dark" if T["fondo"] == PALETAS["oscuro"]["fondo"] else "light"
    return f"""
{IMPORT_FUENTES}
html {{ color-scheme: {esquema}; }}
html, body {{
  margin: 0; padding: 0; background: transparent;
  font-family: {FUENTE_UI};
  font-variant-numeric: tabular-nums;
}}
svg {{ display: block; width: 100%; height: auto; overflow: visible; }}
.et {{ font-family: {FUENTE_MONO}; font-size: 10px; letter-spacing: 0.08em;
       text-transform: uppercase; fill: {T['texto_tenue']}; }}
.vl {{ font-size: 12px; fill: {T['texto']}; font-variant-numeric: tabular-nums; }}
.vs {{ font-size: 11px; fill: {T['texto_medio']}; font-variant-numeric: tabular-nums; }}
@media (prefers-reduced-motion: reduce) {{
  * {{ animation: none !important; transition: none !important; }}
}}
"""
