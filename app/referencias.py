# referencias.py — bibliografía verificada y afirmaciones canónicas
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Fuente ÚNICA de la bibliografía y de las afirmaciones que dependen de ella.

Por qué existe este módulo: la auditoría del 20/08/2026 encontró tres
afirmaciones distintas y contradictorias sobre el mismo dato (el R² esperable
en una ecuación de ingresos) repartidas por la app, el README y dos
documentos. Una afirmación que se escribe en cuatro sitios se contradice a sí
misma en cuanto uno cambia. Aquí se define una vez y el resto la cita.

Cada entrada lleva `acceso`: "abierto" si el enlace da el texto completo sin
pagar, "pago" si solo hay metadatos. Se marca en la interfaz para no prometer
lo que el lector no va a poder abrir.

Todas las URL se verificaron el 20/08/2026. Las de Elsevier, Wiley, Annual
Reviews y Taylor & Francis responden 403 a peticiones automáticas pero
resuelven en navegador; para esas se prioriza la versión abierta del autor y
se conserva el DOI como ancla estable.
"""

from __future__ import annotations

from i18n import L, en

# El orden de esta lista ES la numeración [1], [2]… que ve el lector.
REFERENCIAS: list[dict] = [
    {
        "id": "mincer1974",
        "cita": "Mincer, J. (1974). <i>Schooling, Experience, and Earnings</i>. "
                "Human Behavior and Social Institutions n.º 2. NBER / Columbia "
                "University Press.",
        "url": "https://www.nber.org/system/files/chapters/c1767/c1767.pdf",
        "acceso": "abierto",
        "nota": "Capítulo 5, cuadro 5.1: la ecuación canónica y su R².",
        "cita_en": "Mincer, J. (1974). <i>Schooling, Experience, and Earnings</i>. "
                   "Human Behavior and Social Institutions no. 2. NBER / Columbia "
                   "University Press.",
        "nota_en": "Chapter 5, table 5.1: the canonical equation and its R².",
        "verificacion": "contenido",
    },
    {
        "id": "card1999",
        "cita": "Card, D. (1999). «The Causal Effect of Education on Earnings». "
                "En Ashenfelter y Card (eds.), <i>Handbook of Labor "
                "Economics</i>, vol. 3A, cap. 30, pp. 1801-1863. Elsevier.",
        "url": "https://eml.berkeley.edu/~cle/wp/wp2.pdf",
        "doi": "10.1016/S1573-4463(99)03011-4",
        "acceso": "abierto",
        "nota": "Versión abierta del autor (Berkeley CLE WP n.º 2). "
                "Cuadro 1: R² de la ecuación sobre CPS 1994-96.",
        "cita_en": "Card, D. (1999). “The Causal Effect of Education on Earnings”. "
                   "In Ashenfelter and Card (eds.), <i>Handbook of Labor "
                   "Economics</i>, vol. 3A, ch. 30, pp. 1801-1863. Elsevier.",
        "nota_en": "Author's open version (Berkeley CLE WP no. 2). Table 1: R² of "
                   "the equation on CPS 1994-96.",
        "verificacion": "contenido",
    },
    {
        "id": "lemieux2006",
        "cita": "Lemieux, T. (2006). «The “Mincer Equation” Thirty Years After "
                "<i>Schooling, Experience, and Earnings</i>». En Grossbard "
                "(ed.), <i>Jacob Mincer: A Pioneer of Modern Labor "
                "Economics</i>, cap. 11, pp. 127-145. Springer.",
        "url": "https://economics.ubc.ca/wp-content/uploads/sites/38/2013/05/"
               "pdf_paper_thomas-lemieux-mincer-equation.pdf",
        "doi": "10.1007/0-387-29175-X_11",
        "acceso": "abierto",
        "nota": "Versión abierta del autor (UBC). Vigencia y límites de la "
                "especificación; discute el ajuste en términos de forma "
                "funcional, no de R².",
        "cita_en": "Lemieux, T. (2006). “The ‘Mincer Equation’ Thirty Years After "
                   "<i>Schooling, Experience, and Earnings</i>”. In Grossbard (ed.),"
                   " <i>Jacob Mincer: A Pioneer of Modern Labor Economics</i>, ch. "
                   "11, pp. 127-145. Springer.",
        "nota_en": "Author's open version (UBC). Relevance and limits of the "
                   "specification; discusses fit in terms of functional form, not "
                   "R².",
        "verificacion": "contenido",
    },
    {
        "id": "heckman2006",
        "cita": "Heckman, J., Lochner, L. y Todd, P. (2006). «Earnings "
                "Functions, Rates of Return and Treatment Effects: The Mincer "
                "Equation and Beyond». <i>Handbook of the Economics of "
                "Education</i>, vol. 1, cap. 7, pp. 307-458. Elsevier.",
        "url": "https://www.nber.org/papers/w11544",
        "doi": "10.1016/S1574-0692(06)01007-5",
        "acceso": "abierto",
        "nota": "Versión abierta (NBER WP 11544). Qué interpreta cada "
                "especificación y los límites de la experiencia potencial.",
        "cita_en": "Heckman, J., Lochner, L. and Todd, P. (2006). “Earnings "
                   "Functions, Rates of Return and Treatment Effects: The Mincer "
                   "Equation and Beyond”. <i>Handbook of the Economics of "
                   "Education</i>, vol. 1, ch. 7, pp. 307-458. Elsevier.",
        "nota_en": "Open version (NBER WP 11544). What each specification identifies"
                   " and the limits of potential experience.",
        "verificacion": "contenido",
    },
    {
        "id": "duan1983",
        "cita": "Duan, N. (1983). «Smearing Estimate: A Nonparametric "
                "Retransformation Method». <i>Journal of the American "
                "Statistical Association</i> 78(383), pp. 605-610.",
        "url": "https://doi.org/10.1080/01621459.1983.10478017",
        "doi": "10.1080/01621459.1983.10478017",
        "acceso": "pago",
        "nota": "La corrección de retransformación que usa el modelo. No "
                "existe versión abierta legal, así que el enlace es el DOI: "
                "resuelve en navegador aunque el editor bloquee las "
                "peticiones automáticas.",
        "cita_en": "Duan, N. (1983). “Smearing Estimate: A Nonparametric "
                   "Retransformation Method”. <i>Journal of the American Statistical"
                   " Association</i> 78(383), pp. 605-610.",
        "nota_en": "The retransformation correction the model uses. There is no "
                   "legal open version, so the link is the DOI: it resolves in a "
                   "browser even though the publisher blocks automated requests.",
        "verificacion": "metadatos",
    },
    {
        "id": "belloni2014",
        "cita": "Belloni, A., Chernozhukov, V. y Hansen, C. (2014). "
                "«High-Dimensional Methods and Inference on Structural and "
                "Treatment Effects». <i>Journal of Economic Perspectives</i> "
                "28(2), pp. 29-50.",
        "url": "https://www.aeaweb.org/articles?id=10.1257%2Fjep.28.2.29",
        "doi": "10.1257/jep.28.2.29",
        "acceso": "abierto",
        "nota": "Sustento y cautelas del post-Lasso (especificación E7).",
        "cita_en": "Belloni, A., Chernozhukov, V. and Hansen, C. (2014). "
                   "“High-Dimensional Methods and Inference on Structural and "
                   "Treatment Effects”. <i>Journal of Economic Perspectives</i> "
                   "28(2), pp. 29-50.",
        "nota_en": "Rationale and caveats for post-Lasso (specification E7).",
        "verificacion": "contenido",
    },
    {
        "id": "athey2019",
        "cita": "Athey, S. e Imbens, G. (2019). «Machine Learning Methods That "
                "Economists Should Know About». <i>Annual Review of "
                "Economics</i> 11(1), pp. 685-725.",
        "url": "https://arxiv.org/abs/1903.10075",
        "doi": "10.1146/annurev-economics-080217-053433",
        "acceso": "abierto",
        "nota": "Versión abierta (arXiv). El marco para leer la brecha entre "
                "regresión lineal y árboles.",
        "cita_en": "Athey, S. and Imbens, G. (2019). “Machine Learning Methods That "
                   "Economists Should Know About”. <i>Annual Review of Economics</i>"
                   " 11(1), pp. 685-725.",
        "nota_en": "Open version (arXiv). The framework for reading the gap between "
                   "linear regression and trees.",
        "verificacion": "contenido",
    },
    {
        "id": "sohnesen2016",
        "cita": "Sohnesen, T. P. y Stender, N. (2016). <i>Is Random Forest a "
                "Superior Methodology for Predicting Poverty? An Empirical "
                "Assessment</i>. Policy Research Working Paper 7612. Banco "
                "Mundial.",
        "url": "https://ideas.repec.org/p/wbk/wbrwps/7612.html",
        "doi": "10.1002/pop4.169",
        "acceso": "abierto",
        "nota": "Comparación entre aprendizaje automático y regresión en "
                "encuestas de hogares. El DOI corresponde a la versión de "
                "revista (Poverty & Public Policy 9(1), 2017), de pago.",
        "cita_en": "Sohnesen, T. P. and Stender, N. (2016). <i>Is Random Forest a "
                   "Superior Methodology for Predicting Poverty? An Empirical "
                   "Assessment</i>. Policy Research Working Paper 7612. World Bank.",
        "nota_en": "Comparison of machine learning and regression on household "
                   "surveys. The DOI points to the journal version (Poverty & Public"
                   " Policy 9(1), 2017), which is paywalled.",
        "verificacion": "contenido",
    },
    {
        "id": "psacharopoulos2018",
        "cita": "Psacharopoulos, G. y Patrinos, H. A. (2018). <i>Returns to "
                "Investment in Education: A Decennial Review of the Global "
                "Literature</i>. Policy Research Working Paper 8402. Banco "
                "Mundial.",
        "url": "https://documents.worldbank.org/curated/en/442521523465644318",
        "doi": "10.1080/09645292.2018.1484426",
        "acceso": "abierto",
        "nota": "1.120 estimaciones en 139 países: retorno privado global "
                "≈ 9 % anual; América Latina y el Caribe, 11,0 %.",
        "cita_en": "Psacharopoulos, G. and Patrinos, H. A. (2018). <i>Returns to "
                   "Investment in Education: A Decennial Review of the Global "
                   "Literature</i>. Policy Research Working Paper 8402. World Bank.",
        "nota_en": "1,120 estimates across 139 countries: global private return ≈ 9%"
                   " per year; Latin America and the Caribbean, 11.0%.",
        "verificacion": "contenido",
    },
    {
        "id": "yamada2007",
        "cita": "Yamada, G. (2007). <i>Retornos a la educación superior en el "
                "mercado laboral: ¿vale la pena el esfuerzo?</i> CIES / "
                "Universidad del Pacífico.",
        "url": "https://cies.org.pe/publicaciones/retornos-a-la-educacion-"
               "superior-en-el-mercado-laboral-vale-la-pena-el-esfuerzo/",
        "acceso": "abierto",
        "nota": "Retornos por segmento en Perú: 12,5 % anual para asalariados "
                "frente a 6,5 % para independientes (2004).",
        "cita_en": "Yamada, G. (2007). <i>Retornos a la educación superior en el "
                   "mercado laboral: ¿vale la pena el esfuerzo?</i> CIES / "
                   "Universidad del Pacífico.",
        "nota_en": "Returns by segment in Peru: 12.5% per year for wage earners "
                   "versus 6.5% for the self-employed (2004).",
        "verificacion": "contenido",
    },
    {
        "id": "inei_informal",
        "cita": "INEI (2026). <i>Perú: Comportamiento de los Indicadores del "
                "Mercado Laboral a Nivel Nacional y en 27 Ciudades. "
                "Enero-Diciembre 2025 | Cuarto Trimestre 2025</i>. Informe "
                "Técnico, febrero 2026. Instituto Nacional de Estadística e "
                "Informática, Lima.",
        "url": "https://www.gob.pe/institucion/inei/informes-publicaciones/"
               "7739601-peru-comportamiento-de-los-indicadores-del-mercado-"
               "laboral-a-nivel-nacional-y-27-ciudades-cuarto-trimestre-2025",
        "acceso": "abierto",
        "nota": "Cuadro 1.20 (empleo informal nacional 70,2 %), Gráfico 1.15 "
                "(urbano 64,5 %, rural 94,8 %) y Cuadro 1.22 (por tamaño de "
                "empresa: 88,6 % en 1-10 trabajadores, 44,0 % en 11-50, "
                "15,6 % en 51 y más), año 2025, pp. 26-28. La tasa oficial se "
                "mide con la Encuesta Permanente de Empleo Nacional (EPEN); "
                "la de este proyecto se reconstruye sobre la ENAHO. Son "
                "encuestas distintas, así que el contraste es una "
                "referencia, no una validación contra la misma fuente.",
        "cita_en": "INEI (2026). <i>Peru: Labor Market Indicators at the "
                   "National Level and in 27 Cities. January-December 2025 | "
                   "Fourth Quarter 2025</i>. Technical Report, February 2026. "
                   "National Institute of Statistics and Informatics (INEI), "
                   "Lima.",
        "nota_en": "Table 1.20 (national informal employment 70.2%), Chart "
                   "1.15 (urban 64.5%, rural 94.8%) and Table 1.22 (by firm "
                   "size: 88.6% in 1-10 workers, 44.0% in 11-50, 15.6% in 51+"
                   "), year 2025, pp. 26-28. The official rate is measured "
                   "with the National Permanent Employment Survey (EPEN); "
                   "this project's rate is rebuilt from the ENAHO. They are "
                   "different surveys, so the contrast is a reference, not a "
                   "validation against the same source.",
        "verificacion": "contenido",
    },
    {
        "id": "oit_17ciet",
        "cita": "OIT (2003). <i>Guidelines concerning a statistical definition "
                "of informal employment</i>. 17.ª Conferencia Internacional de "
                "Estadísticos del Trabajo, Ginebra. Actualizada por la "
                "Resolución I de la 21.ª CIET (2023).",
        "url": "https://www.ilo.org/resource/guidelines-concerning-statistical-"
               "definition-informal-employment-0",
        "acceso": "abierto",
        "nota": "La definición internacional de EMPLEO informal (criterio de "
                "puesto de trabajo), que es la que usa este proyecto. No "
                "confundir con la 15.ª CIET (1993), que define el SECTOR "
                "informal por características de la empresa.",
        "cita_en": "ILO (2003). <i>Guidelines concerning a statistical definition of"
                   " informal employment</i>. 17th International Conference of "
                   "Labour Statisticians, Geneva. Updated by Resolution I of the "
                   "21st ICLS (2023).",
        "nota_en": "The international definition of informal EMPLOYMENT (a job-based"
                   " criterion), which is the one this project uses. Not to be "
                   "confused with the 15th ICLS (1993), which defines the informal "
                   "SECTOR by enterprise characteristics.",
        "verificacion": "contenido",
    },
    {
        "id": "saito2015",
        "cita": "Saito, T. y Rehmsmeier, M. (2015). «The Precision-Recall Plot "
                "Is More Informative than the ROC Plot When Evaluating Binary "
                "Classifiers on Imbalanced Datasets». <i>PLOS ONE</i> 10(3), "
                "e0118432.",
        "url": "https://journals.plos.org/plosone/article?id=10.1371%2F"
               "journal.pone.0118432",
        "doi": "10.1371/journal.pone.0118432",
        "acceso": "abierto",
        "nota": "Por qué se mira PR-AUC y no solo ROC-AUC con clases "
                "desbalanceadas.",
        "cita_en": "Saito, T. and Rehmsmeier, M. (2015). “The Precision-Recall Plot "
                   "Is More Informative than the ROC Plot When Evaluating Binary "
                   "Classifiers on Imbalanced Datasets”. <i>PLOS ONE</i> 10(3), "
                   "e0118432.",
        "nota_en": "Why we look at PR-AUC and not only ROC-AUC with imbalanced "
                   "classes.",
        "verificacion": "contenido",
    },
    {
        "id": "loayza2008",
        "cita": "Loayza, N. (2008). «Causas y consecuencias de la informalidad "
                "en el Perú». <i>Revista Estudios Económicos</i> n.º 15, "
                "pp. 43-64. Banco Central de Reserva del Perú.",
        "url": "https://www.bcrp.gob.pe/docs/Publicaciones/"
               "Revista-Estudios-Economicos/15/Estudios-Economicos-15-3.pdf",
        "acceso": "abierto",
        "nota": "Contexto económico de la informalidad peruana.",
        "cita_en": "Loayza, N. (2008). “Causas y consecuencias de la informalidad en"
                   " el Perú”. <i>Revista Estudios Económicos</i> no. 15, pp. 43-64."
                   " Central Reserve Bank of Peru.",
        "nota_en": "Economic context of informality in Peru.",
        "verificacion": "contenido",
    },
    {
        "id": "perry2007",
        "cita": "Perry, G. E., Maloney, W. F., Arias, O. S., Fajnzylber, P., "
                "Mason, A. D. y Saavedra-Chanduvi, J. (2007). <i>Informality: "
                "Exit and Exclusion</i>. Banco Mundial.",
        "url": "https://doi.org/10.1596/978-0-8213-7092-6",
        "doi": "10.1596/978-0-8213-7092-6",
        "acceso": "abierto",
        "nota": "Marco de informalidad por exclusión frente a informalidad "
                "por elección.",
        "cita_en": "Perry, G. E., Maloney, W. F., Arias, O. S., Fajnzylber, P., "
                   "Mason, A. D. and Saavedra-Chanduvi, J. (2007). <i>Informality: "
                   "Exit and Exclusion</i>. World Bank.",
        "nota_en": "Framework of informality as exclusion versus informality as "
                   "choice.",
        "verificacion": "contenido",
    },
]

INDICE = {r["id"]: i + 1 for i, r in enumerate(REFERENCIAS)}


def ref(*ids: str) -> str:
    """Llamada numerada: ref('card1999') -> «[2]», enlazada a la lista."""
    partes = []
    for i in ids:
        n = INDICE.get(i)
        if n:
            partes.append(f"<a class='ref-llamada' href='#ref-{n}' "
                          f"title='{L('Ver referencia', 'See reference')} "
                          f"{n}'>[{n}]</a>")
    return "".join(partes)


def lista_html() -> str:
    """La sección «Referencias», numerada igual que las llamadas."""
    filas = []
    ingles = en()
    for i, r in enumerate(REFERENCIAS, 1):
        abierto = r["acceso"] == "abierto"
        marca = (f"<span class='ref-acceso "
                 f"{'ref-abierto' if abierto else 'ref-pago'}'>"
                 + (L("acceso abierto", "open access") if abierto
                    else L("de pago", "paywalled")) + "</span>")
        enlace = (f"<a href='{r['url']}' target='_blank' rel='noopener'>"
                  f"{r['url']}</a>")
        doi = (f"<br>DOI: <a href='https://doi.org/{r['doi']}' target='_blank' "
               f"rel='noopener'>{r['doi']}</a>" if r.get("doi") else "")
        cita = r.get("cita_en", r["cita"]) if ingles else r["cita"]
        texto_nota = r.get("nota_en", r.get("nota")) if ingles else r.get("nota")
        nota = f"<br><i>{texto_nota}</i>" if texto_nota else ""
        filas.append(
            f"<div class='ref-item' id='ref-{i}'>"
            f"<span class='ref-num'>[{i}]</span>"
            f"<span>{cita}{marca}<br>{enlace}{doi}{nota}</span></div>")
    return f"<div class='ref-lista'>{''.join(filas)}</div>"


# --------------------------------------------------------------------------
# Afirmaciones canónicas: se definen UNA vez y se citan desde donde haga falta
# --------------------------------------------------------------------------
# Regla de la auditoría: si no hay una fuente que lo enuncie tal cual, se
# redacta como lectura propia sobre cifras concretas y verificables, en vez de
# colgarle a un autor algo que no dijo.
#
# Sobre el R²: ni Lemieux (2006) ni Heckman et al. (2006) reportan un R² —lo
# verificamos en los textos completos—, así que no se les puede citar para
# esto. Los únicos valores citables salen de los cuadros de Mincer y de Card.
R2_MINCER_CANONICO = (
    "La ecuación de Mincer explica típicamente entre un 25 % y un 35 % de la "
    "varianza del logaritmo del salario. No es una cifra que la literatura "
    "enuncie como regla: son los valores de los ejercicios de referencia "
    "—Mincer (1974), cuadro 5.1: R² = 0,285 para la especificación canónica"
    "{ref_mincer}; Card (1999), cuadro 1: R² entre 0,247 y 0,328 sobre la CPS "
    "1994-96{ref_card}—. Cuando Mincer añade las semanas trabajadas, el R² "
    "sube a 0,525, pero entonces la ecuación ya no mide solo capital humano: "
    "incorpora oferta laboral."
)

R2_ADVERTENCIA_CONTEXTO = (
    "Esas cifras vienen de encuestas de Estados Unidos. En un mercado con "
    "alta informalidad y mucho trabajo independiente —donde el ingreso se "
    "mide con más error— lo esperable es un R² igual o menor, no mayor. "
    "Extrapolar el rango a Perú es una lectura nuestra, no un resultado "
    "publicado."
)

RETORNO_EDUCACION = (
    "El retorno privado medio global a un año más de escolaridad ronda el "
    "9 % anual, y el 11,0 % en América Latina y el Caribe{ref_psa}. Para "
    "Perú las estimaciones van del 8,6 % al 12,5 % según el año y el "
    "segmento, con una brecha grande entre asalariados (12,5 %) e "
    "independientes (6,5 %) en 2004{ref_yamada}."
)


# Versiones en inglés: mismos marcadores {ref_…}, cifras en formato inglés.
R2_MINCER_CANONICO_EN = (
    "The Mincer equation typically explains between 25% and 35% of the "
    "variance of log wages. This is not a figure the literature states as a "
    "rule: it is what the benchmark exercises report —Mincer (1974), table "
    "5.1: R² = 0.285 for the canonical specification{ref_mincer}; Card "
    "(1999), table 1: R² between 0.247 and 0.328 on the 1994-96 "
    "CPS{ref_card}—. When Mincer adds weeks worked, the R² rises to 0.525, "
    "but the equation then no longer measures human capital alone: it also "
    "captures labor supply."
)

R2_ADVERTENCIA_CONTEXTO_EN = (
    "Those figures come from US surveys. In a market with high informality "
    "and a large share of self-employment —where income is measured with "
    "more error— one should expect an equal or lower R², not a higher one. "
    "Extrapolating the range to Peru is our own reading, not a published "
    "result."
)

RETORNO_EDUCACION_EN = (
    "The average global private return to one more year of schooling is "
    "around 9% per year, and 11.0% in Latin America and the "
    "Caribbean{ref_psa}. For Peru, estimates range from 8.6% to 12.5% "
    "depending on the year and the segment, with a wide gap between wage "
    "earners (12.5%) and the self-employed (6.5%) in 2004{ref_yamada}."
)


def r2_mincer() -> str:
    """Plantilla del R² canónico en el idioma activo (sin formatear)."""
    return L(R2_MINCER_CANONICO, R2_MINCER_CANONICO_EN)


def r2_advertencia() -> str:
    return L(R2_ADVERTENCIA_CONTEXTO, R2_ADVERTENCIA_CONTEXTO_EN)


def retorno_educacion() -> str:
    return L(RETORNO_EDUCACION, RETORNO_EDUCACION_EN)
