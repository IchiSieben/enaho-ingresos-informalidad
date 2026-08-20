# referencias.py — bibliografía verificada y afirmaciones canónicas
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
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
    },
    {
        "id": "inei_informal",
        "cita": "INEI (2025). <i>Producción y empleo informal en el Perú: "
                "Cuenta Satélite de la Economía Informal 2022-2024</i>. "
                "Instituto Nacional de Estadística e Informática, Lima.",
        "url": "https://www.gob.pe/institucion/inei/informes-publicaciones/"
               "7564428-produccion-y-empleo-informal-en-el-peru-cuenta-satelite-"
               "de-la-economia-informal-2022-2024",
        "acceso": "abierto",
        "nota": "Las tasas oficiales de empleo informal contra las que se "
                "valida la regla del target.",
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
                          f"title='Ver referencia {n}'>[{n}]</a>")
    return "".join(partes)


def lista_html() -> str:
    """La sección «Referencias», numerada igual que las llamadas."""
    filas = []
    for i, r in enumerate(REFERENCIAS, 1):
        abierto = r["acceso"] == "abierto"
        marca = (f"<span class='ref-acceso "
                 f"{'ref-abierto' if abierto else 'ref-pago'}'>"
                 f"{'acceso abierto' if abierto else 'de pago'}</span>")
        enlace = (f"<a href='{r['url']}' target='_blank' rel='noopener'>"
                  f"{r['url']}</a>")
        doi = (f"<br>DOI: <a href='https://doi.org/{r['doi']}' target='_blank' "
               f"rel='noopener'>{r['doi']}</a>" if r.get("doi") else "")
        nota = f"<br><i>{r['nota']}</i>" if r.get("nota") else ""
        filas.append(
            f"<div class='ref-item' id='ref-{i}'>"
            f"<span class='ref-num'>[{i}]</span>"
            f"<span>{r['cita']}{marca}<br>{enlace}{doi}{nota}</span></div>")
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
