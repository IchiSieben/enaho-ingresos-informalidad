# glosario.py — términos técnicos con su definición al pasar el cursor
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Un solo lugar para las definiciones. `termino()` devuelve un <span
tabindex=0> con la definición en un tooltip CSS: se abre con el cursor y con
el teclado (:focus). Verificado: el markdown de Streamlit conserva tabindex,
role y title. Las definiciones no llevan cifras: las cifras salen de los
artefactos, no de aquí.
"""
from __future__ import annotations

from html import escape

from i18n import L

# clave: (término ES, término EN, definición ES, definición EN)
TERMINOS: dict[str, tuple[str, str, str, str]] = {
    "enaho": ("ENAHO", "ENAHO",
              "Encuesta Nacional de Hogares del INEI: entrevista a miles de hogares "
              "cada año sobre empleo, ingresos, educación y más.",
              "Peru's National Household Survey, run by INEI: thousands of "
              "households interviewed every year about jobs, income, schooling "
              "and more."),
    "inei": ("INEI", "INEI",
             "Instituto Nacional de Estadística e Informática, la oficina "
             "estadística oficial del Perú.",
             "Peru's National Institute of Statistics and Informatics, the "
             "official statistics office."),
    "ruc": ("RUC", "RUC",
            "Registro Único de Contribuyentes: el registro tributario de la "
            "SUNAT. Un negocio sin RUC no existe para el fisco.",
            "Peru's taxpayer registry (SUNAT). A business without a RUC does "
            "not exist for the tax authority."),
    "informal": ("empleo informal", "informal employment",
                 "Trabajo sin protección legal ni social: aquí, independiente sin "
                 "RUC o dependiente al que nadie le aporta a una pensión.",
                 "Work without legal or social protection: here, self-employed "
                 "without a RUC, or an employee with no pension contributions."),
    "epen": ("EPEN", "EPEN",
             "Encuesta Permanente de Empleo Nacional del INEI, de la que sale la "
             "tasa oficial de informalidad.",
             "INEI's Permanent National Employment Survey, source of the "
             "official informality rate."),
    "factor": ("factor de expansión", "expansion factor",
               "Cuántas personas del país representa cada persona encuestada. "
               "Las cifras de población se ponderan con él.",
               "How many people in the country each respondent stands for. "
               "Population figures are weighted with it."),
    "mediana": ("mediana", "median",
                "El valor del medio: la mitad gana menos y la mitad gana más. No "
                "la mueven unos pocos ingresos muy altos.",
                "The middle value: half earn less, half earn more. A few very "
                "high incomes don't move it."),
    "ic": ("intervalo de confianza", "confidence interval",
           "Rango de valores compatibles con los datos. Al 95 %: si se repitiera "
           "la encuesta muchas veces, el rango contendría el valor verdadero en "
           "ese porcentaje de las repeticiones.",
           "Range of values compatible with the data. At 95%: if the survey were "
           "repeated many times, the range would contain the true value in that "
           "share of the repetitions."),
    "oaxaca": ("Oaxaca-Blinder", "Oaxaca-Blinder",
               "Método que parte una brecha de ingresos en lo que explican las "
               "características observadas (educación, lugar…) y lo que no.",
               "Method that splits an earnings gap into the part explained by "
               "observed traits (schooling, place…) and the part that isn't."),
    "nopo": ("Ñopo", "Ñopo",
             "Descomposición que compara solo a personas con características "
             "idénticas (emparejamiento), y reporta aparte a quienes no tienen "
             "par en el otro grupo.",
             "Decomposition that compares only people with identical traits "
             "(matching), and reports separately those with no match in the "
             "other group."),
    "retorno": ("retorno a la educación", "return to education",
                "Cuánto más se gana, en promedio, por cada año adicional de "
                "estudios, a igualdad de lo demás que se controla.",
                "How much more people earn, on average, per extra year of "
                "schooling, holding the controlled traits equal."),
    "prauc": ("PR-AUC", "PR-AUC",
              "Área bajo la curva de precisión y cobertura: resume qué tan bien "
              "el clasificador encuentra los casos positivos sin falsas alarmas.",
              "Area under the precision-recall curve: how well the classifier "
              "finds positive cases without false alarms."),
    "pd": ("dependencia parcial", "partial dependence",
           "Cómo cambia la predicción del modelo al mover una variable, "
           "promediando sobre las demás. Describe al modelo, no una causa.",
           "How the model's prediction changes as one variable moves, "
           "averaging over the rest. It describes the model, not a cause."),
    "gb": ("Gradient Boosting", "Gradient Boosting",
           "Modelo que suma cientos de árboles de decisión pequeños; cada uno "
           "corrige los errores de los anteriores.",
           "A model that adds up hundreds of small decision trees, each one "
           "correcting the errors of the ones before."),
}


def termino(clave: str, texto: str | None = None) -> str:
    """El término con su definición; `texto` reemplaza la forma visible."""
    es, en, def_es, def_en = TERMINOS[clave]
    visible = texto if texto is not None else L(es, en)
    return (f"<span class='termino' tabindex='0'>{escape(visible)}"
            f"<span class='termino-def' role='tooltip'>{escape(L(def_es, def_en))}"
            f"</span></span>")


def lista() -> str:
    """El glosario completo como lista de definiciones (para la portada)."""
    filas = "".join(
        f"<dt>{escape(L(es, en))}</dt><dd>{escape(L(d_es, d_en))}</dd>"
        for es, en, d_es, d_en in sorted(TERMINOS.values(), key=lambda t: L(t[0], t[1]).lower()))
    return f"<dl class='glosario'>{filas}</dl>"
