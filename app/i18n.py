# i18n.py — español / inglés: selector, textos de datos y formato numérico
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Dos idiomas sin tocar los modelos ni los artefactos.

Reglas:
- Los VALORES que ve el modelo siguen en español siempre («Hombre»,
  «Hasta 20»…): el pipeline se entrenó con esas cadenas. Solo cambia lo que
  se MUESTRA, vía `tr()` en los `format_func` y en los rótulos.
- El texto de la interfaz va en pares `L("es", "en")` junto al código que lo
  usa: con prosa larga, un catálogo de claves separado se desincroniza.
- `ui_artifacts.json` no se toca (la presentación congelada mide su tamaño):
  sus cadenas se traducen aquí, al leerlas.
- El idioma vive en `st.session_state["idioma"]` y en `?lang=` de la URL, así
  el portafolio puede enlazar directo a la versión en inglés.
"""

from __future__ import annotations

import re

IDIOMAS = {"es": "Español", "en": "English"}
IDIOMA_POR_DEFECTO = "es"


def idioma() -> str:
    """Idioma de ESTA sesión. Fuera de Streamlit (tests) vale el por defecto."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx() is None:
            return IDIOMA_POR_DEFECTO
        import streamlit as st
        lang = st.session_state.get("idioma", IDIOMA_POR_DEFECTO)
        return lang if lang in IDIOMAS else IDIOMA_POR_DEFECTO
    except Exception:
        return IDIOMA_POR_DEFECTO


def en() -> bool:
    return idioma() == "en"


def L(es: str, en_: str) -> str:
    """El texto en el idioma activo."""
    return en_ if en() else es


# --------------------------------------------------------------------------
# Formato numérico: el lector hispano espera 1.234,5 y 97,5 %; el anglosajón
# 1,234.5 y 97.5%. Mezclarlos es el error más visible de una traducción.
# --------------------------------------------------------------------------
def n(x: float, dec: int = 0) -> str:
    """Miles y decimales según idioma."""
    s = f"{x:,.{dec}f}"
    if en():
        return s
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def d(x: float, dec: int = 2) -> str:
    """Decimal sin separador de miles (métricas: 0,9626 / 0.9626)."""
    s = f"{x:.{dec}f}"
    return s if en() else s.replace(".", ",")


def pct(x: float, dec: int = 1) -> str:
    """Fracción a porcentaje: 0.975 -> «97,5 %» / «97.5%»."""
    return d(x * 100, dec) + ("%" if en() else " %")


def pc(v: float, dec: int = 0) -> str:
    """Un número que YA es porcentaje: 41.5 -> «41,5 %» / «41.5%»."""
    return d(v, dec) + ("%" if en() else " %")


# --------------------------------------------------------------------------
# Textos que llegan de los datos (schema y artefactos)
# --------------------------------------------------------------------------
VALORES: dict[str, str] = {
    # categorías
    "Hombre": "Man", "Mujer": "Woman",
    "Rural": "Rural", "Urbana": "Urban",
    "Costa Centro": "Central Coast", "Costa Norte": "North Coast",
    "Costa Sur": "South Coast", "Lima Metropolitana": "Metropolitan Lima",
    "Selva": "Amazon", "Sierra Centro": "Central Highlands",
    "Sierra Norte": "Northern Highlands", "Sierra Sur": "Southern Highlands",
    "Administración pública": "Public administration",
    "Agropecuario y pesca": "Agriculture & fishing",
    "Alojamiento y restaurantes": "Hotels & restaurants",
    "Comercio": "Trade", "Construcción": "Construction",
    "Enseñanza": "Education", "Manufactura": "Manufacturing",
    "Minería e hidrocarburos": "Mining & oil/gas",
    "Otros servicios": "Other services",
    "Salud y asistencia social": "Health & social work",
    "Servicio doméstico": "Domestic service",
    "Servicios profesionales y financieros": "Professional & financial",
    "Transporte y almacenamiento": "Transport & storage",
    "101 a 500": "101–500", "21 a 50": "21–50", "51 a 100": "51–100",
    "Hasta 20": "Up to 20", "Más de 500": "Over 500",
    "Empleado": "Salaried employee", "Empleador": "Employer",
    "Independiente": "Self-employed", "Obrero": "Wage laborer",
    "Trabajador del hogar": "Domestic worker",
    # etiquetas de variables
    "Años de educación aprobados": "Years of schooling completed",
    "Edad (años)": "Age (years)",
    "Experiencia potencial (años)": "Potential experience (years)",
    "exper2": "Experience²",
    "Horas trabajadas por semana (todas las ocupaciones)":
        "Weekly hours worked (all jobs)",
    "Sexo": "Sex", "Área de residencia": "Area of residence",
    "Dominio geográfico": "Geographic domain",
    "Rama de actividad (agrupada)": "Industry (grouped)",
    "Tamaño de la empresa (personas)": "Firm size (workers)",
    "Categoría ocupacional": "Employment category",
    "Nivel educativo (dummies)": "Education level (dummies)",
    "Experiencia² (años²)": "Experience² (years²)",
    "Horas semanales (log u horas según spec)":
        "Weekly hours (log or level, by spec)",
    "Miembros del hogar": "Household members",
    "Tipo de contrato": "Contract type",
    "Horas semanales": "Weekly hours", "Experiencia²": "Experience²",
    # algoritmos, interpretabilidad, variantes
    "Regresión logística": "Logistic regression",
    "baja": "low", "media": "medium", "alta": "high",
    "completa": "full model",
    "V1: sin tamano_empresa": "V1: without firm size",
    "V2: sin tamano_empresa ni categoria":
        "V2: without firm size or employment category",
    "solo monetario": "cash only", "monetario + especie": "cash + in-kind",
    # especificaciones del torneo
    "Gradient Boosting (log target, pipeline sklearn)":
        "Gradient Boosting (log target, sklearn pipeline)",
    "Random Forest (log target, pipeline sklearn)":
        "Random Forest (log target, sklearn pipeline)",
    "Post-Lasso: OLS sobre las variables que Lasso conserva":
        "Post-Lasso: OLS on the variables Lasso keeps",
    "Depurada: E4 + categoría + tamaño empresa + dominio (sin la dummy "
    "rama=Servicio doméstico, colineal perfecta con categoría=Trabajador "
    "del hogar)":
        "Pruned: E4 + category + firm size + domain (drops the "
        "industry=Domestic service dummy, perfectly collinear with "
        "category=Domestic worker)",
    "Mincer extendido: E3 + sexo + área + log(horas) + rama":
        "Extended Mincer: E3 + sex + area + log(hours) + industry",
    "Mincer clásico: educ + exp + exp²": "Classic Mincer: educ + exp + exp²",
    "Réplica del baseline del curso (niveles, ya sin centinela)":
        "Replica of the course baseline (levels, sentinel removed)",
    "log(ingreso) ~ años educación": "log(income) ~ years of schooling",
    "Ingreso ~ años educación (consigna, niveles)":
        "Income ~ years of schooling (assignment, levels)",
    # textos largos del schema / artefactos
    "Empleo informal (regla INEI derivada: independiente/empleador sin RUC; "
    "dependiente sin afiliación a pensión). Validada contra la tasa oficial "
    "2025.":
        "Informal employment (derived INEI rule: self-employed/employer "
        "without a tax ID (RUC); employee without pension enrollment). "
        "Validated against the official 2025 rate.",
    "Herramienta de focalización, no de predicción a futuro: identifica la "
    "configuración laboral asociada a la informalidad desde variables "
    "observables en registros administrativos.":
        "A targeting tool, not a forecast: it identifies the job "
        "configuration associated with informality from variables that "
        "administrative records can observe.",
    "Ingreso laboral mensual monetario (suma de las versiones "
    "imputadas/deflactadas/anualizadas del INEI / 12: ingreso suavizado, no "
    "el del mes de referencia). Solo ocupados con ingreso > 0.":
        "Monthly cash labor income (sum of INEI's imputed/deflated/annualized "
        "variables ÷ 12: a smoothed income, not the reference month's). "
        "Employed people with income > 0 only.",
    "De cada 1.000 trabajadores señalados, 900 son efectivamente "
    "informales, frente a 678 si se señalara al azar (lift 1,33x).":
        "Out of every 1,000 workers flagged, 900 are actually informal, "
        "versus 678 if they were flagged at random (lift 1.33×).",
    "Cohortes y comparables ponderados con FAC500A; curvas del modelo "
    "muestrales; entrenamiento sin ponderar.":
        "Cohorts and comparables weighted with FAC500A; model curves "
        "unweighted (sample); training unweighted.",
    "Leída de las especificaciones de src/04_torneo_regresion.py. E7: "
    "columnas candidatas al Lasso (la selección decide cuáles quedan). E6 "
    "suelta la dummy rama=Servicio doméstico, colineal perfecta con "
    "categoría=Trabajador del hogar.":
        "Read from the specifications in src/04_torneo_regresion.py. E7: "
        "candidate columns for the Lasso (the selection decides which "
        "stay). E6 drops the industry=Domestic service dummy, perfectly "
        "collinear with category=Domestic worker.",
    "«Índice de bienestar» (INGHOG2D; y derivados GASHOG2D, POBREZA)":
        "“Welfare index” (INGHOG2D; and derivatives GASHOG2D, POBREZA)",
    "Circularidad mecánica: el ingreso individual es un sumando del ingreso "
    "del hogar (ρ Spearman 0,575; 0,619 per cápita). Excluido de todo "
    "modelo.":
        "Mechanical circularity: individual income is one of the terms of "
        "household income (Spearman ρ 0.575; 0.619 per capita). Excluded "
        "from every model.",
    "P511A — tipo de contrato": "P511A — contract type",
    "Cuasi-definicional de la informalidad para asalariados (AUC univariado "
    "0,846): prohibida en el clasificador. En la regresión solo participa "
    "como candidata de E7.":
        "Quasi-definitional of informality for wage earners (univariate AUC "
        "0.846): banned from the classifier. In the regression it only "
        "enters as an E7 candidate.",
    "Centinela 999999 (nota: no es una variable)":
        "Sentinel 999999 (note: not a variable)",
    "Código de faltante del INEI en variables monetarias, leído como valor "
    "real en el baseline; convertido a NaN antes de todo cálculo (R² 0,023 "
    "→ 0,248 al limpiarlo).":
        "INEI's missing-value code in money variables, read as a real value "
        "in the baseline; converted to NaN before any computation (R² 0.023 "
        "→ 0.248 once cleaned).",
    "TFNR — trabajadores familiares no remunerados":
        "TFNR — unpaid family workers",
    "Restricción de población, no variable: 6.500 ocupados con ingreso = 0 "
    "quedan fuera de la población de modelado (informales por definición; "
    "la prevalencia lo declara).":
        "A population restriction, not a variable: 6,500 employed people "
        "with income = 0 fall outside the modeling population (informal by "
        "definition; the stated prevalence reflects it).",
}

# Etiquetas crudas del schema que tampoco sirven en español.
VALORES_ES: dict[str, str] = {"exper2": "Experiencia²"}

_RANGO = re.compile(
    r"El rango del formulario \((\d+)–(\d+)\) es más estrecho que el del "
    r"entrenamiento \((\d+)–(\d+)\)\. El modelo se entrenó con los datos "
    r"intactos; el formulario no ofrece valores implausibles presentes en la "
    r"fuente\.")


def tr(s) -> str:
    """Traduce un texto que llega de los datos. En español no toca nada."""
    if s is None:
        return s
    s = str(s)
    if not en():
        return VALORES_ES.get(s, s)
    if s in VALORES:
        return VALORES[s]
    m = _RANGO.fullmatch(s)
    if m:
        a, b, c, e = m.groups()
        return (f"The form's range ({a}–{b}) is narrower than the training "
                f"range ({c}–{e}). The model was trained on the untouched "
                f"data; the form simply doesn't offer implausible values "
                f"present in the source.")
    return s
