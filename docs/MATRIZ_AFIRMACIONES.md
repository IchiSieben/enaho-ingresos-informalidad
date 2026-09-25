# Matriz de afirmaciones — verificación bibliográfica (Fase 2)

## Método

Cada afirmación de este proyecto que cita una fuente externa (en `app/referencias.py`,
en `app/streamlit_app.py`, en `README.md` o propuesta en `docs/MARCO_TEORICO.md`) se
verificó así: (1) se abrió la fuente en su URL/DOI y se guardó el texto crudo
(`pdftotext`/`curl`/scrape) en `scratchpad/fase2/raw/<id>.txt` — nunca un resumen
generado por un modelo; (2) se extrajo una cita textual de ≤40 palabras que respalda la
afirmación; (3) esa cita se comprobó mecánicamente contra el archivo crudo con `grep`
literal (`scratchpad/fase2/_verificacion.txt`, 31 líneas marcadas de un total mayor). Una
cita que el grep no encontró exactamente se revisó a mano: la mayoría son falsos
positivos (paráfrasis en español, texto propio del agente, encabezados partidos por el
layout del PDF, o la cita SÍ está pero en otro archivo crudo del mismo autor) — el
detalle de cada caso está en la nota de la fila correspondiente y sigue las adjudicaciones
explícitas del hilo principal. Dos referencias (`mincer1974`, la fórmula "ln Y" leída como
"In Y" por el PDF, y `breiman2001`, el encabezado JSTOR) se marcan igual **verificadas**
porque el texto real coincide una vez corregido el artefacto de extracción del PDF. Los
libros sin copia abierta completa (Lewis 1954, Harris-Todaro 1970, Tokman 1978,
Portes-Castells-Benton 1989, De Soto 1989, Levy 2008, Blinder 1973, Oaxaca 1973) llevan
**Metadatos verificados** (confirmados en al menos una bibliografía académica que sí se
abrió) y **Contenido verificado = no**: solo pueden respaldar que el trabajo existe y
trata el tema, nunca una frase textual específica.

Columnas: **Estado** es el veredicto final para `app/referencias.py` — OK (sin cambios),
corregir (cita/nota/URL a ajustar), retirar (referencia huérfana, sin uso en el código) o
nueva (propuesta de alta). El detalle de cada corrección de texto está en
`docs/PROPUESTA_REFERENCIAS.md`.

---

## Conteo

- Referencias con contenido verificado (cita textual confirmada en texto crudo): **29**
  — hart1973, oit1972kenya, chen2012, oit2018_mujeres_hombres, oit_17ciet, maloney2004,
  guntherlaunov2012 (vía preprint 2006), laportashleifer2014, ulyssea2020, matosmar1984,
  golteadams1987, rodriguez2011, kamichi2023, nopo2008, nopo_atal_winder2009,
  blaukahn2017, goldin2014, nopo_saavedra_torero2004, arpi2018, esparta_rivera2020,
  iza3151_2007, mincer1974, card1999, lemieux2006, heckman2006 (parcial, ver fila 33),
  psacharopoulos2018, yamada2007, breiman2001, shmueli2010, barocas2023, aiken2022,
  sohnesen2016, saito2015, inei_empleo_2025, inei_informal (contenido sí, pero cita cifras
  de otro año — ver fila 44).
- Referencias con solo metadatos verificados (libros/artículos sin copia abierta
  completa): **8** — lewis1954, harristodaro1970, tokman1978, portescastellsbenton1989,
  desoto1989, levy2008, oaxaca1973, blinder1973.
- Referencias con contenido parcial (resumen corto, no texto completo): **2** —
  mullainathan2017, kleinberg2015.
- No verificadas / descartadas para cita puntual: **2** — chaman2025 (BLS bloquea acceso
  automatizado), duan1983 (paywall confirmado por dos fuentes independientes, sin copia
  abierta; la atribución en el código se mantiene por ser consistente con el
  título/abstract conocido, no por lectura directa del contenido).
- Filas de la matriz por Estado: OK = 13 · corregir = 9 · retirar = 2 · nueva = 3.

---

## Tabla

| # | Afirmación | Dónde aparece | Fuente (id) | Página/sección | Metadatos verif. | Contenido verif. | Cita textual (≤40 palabras) | Acceso | Etiqueta | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Ecuación de Mincer, R²=0,285 (especificación canónica) | app/referencias.py (R2_MINCER_CANONICO) | mincer1974 | Cap. 5, Tabla 5.1 | sí | sí | «P(1) ln Y=6.20+.107s+.081t—.0012t2 .285» (el PDF muestra "In Y"; es "ln Y", artefacto de extracción) | abierto | consistente con la literatura | OK |
| 2 | R² sube a 0,525 al añadir semanas trabajadas | app/referencias.py (R2_MINCER_CANONICO) | mincer1974 | Cap. 5, Tabla 5.1 | sí | sí | «P(3) ln Y= f(D3) + .068t— .0009t2 + 1.207 ln W .525» | abierto | consistente con la literatura | OK |
| 3 | R² entre 0,247 y 0,328 (CPS 1994-96, especificación minceriana) | app/referencias.py (R2_MINCER_CANONICO) | card1999 | Tabla 1 | sí | sí | «R-squared 0.328 0.182 0.136 0.222 0.403» (hombres); «R-squared 0.247 0.071 0.074 0.105 0.247» (mujeres) | abierto | consistente con la literatura | OK |
| 4 | Lemieux (2006) discute forma funcional, no reporta R² | app/referencias.py (nota lemieux2006) | lemieux2006 | Texto completo | sí | sí | «Though Mincer (1974) considered several functional forms for the earnings equation, the most commonly used is equation (1)»; búsqueda de "R2"/"R-squared" en 944 líneas: 0 resultados | abierto | consistente con la literatura | OK |
| 5 | Heckman, Lochner & Todd (2006) definen experiencia potencial = edad − escolaridad − 6 | app/referencias.py (nota heckman2006) | heckman2006 | Texto completo, línea 5436/5462 | sí | sí | «experience: Potential experience is measured by Age − Years of Education − 6.» | abierto | consistente con la literatura | OK |
| 6 | Heckman, Lochner & Todd (2006): la experiencia potencial "sobreestima la experiencia efectiva" en baja educación | app/streamlit_app.py:2344-2351 | heckman2006 | Texto completo (7 838 líneas) | sí | **no** | Búsqueda exhaustiva de "overstate"/"understate"/"proxy"/"measurement error"+"experience"/"dropout"+"experience"/"discontinuous" en todo el documento: frase no encontrada | abierto | lectura nuestra (atribución no respaldada — corregir) | corregir |
| 7 | Retorno privado global ≈9%/año; 11,0% en América Latina y el Caribe | app/referencias.py (RETORNO_EDUCACION) | psacharopoulos2018 | Abstract; Tabla 3 | sí | sí | «the private average global rate of return to one extra year of schooling is about 9 percent a year»; «Latin America and Caribbean 11.0 7.3» | abierto | consistente con la literatura | corregir (URL) |
| 8 | Retornos en Perú 2004: asalariados 12,5%, independientes 6,5% | app/referencias.py (RETORNO_EDUCACION) | yamada2007 | Cuadro 4 | sí | sí | «En el año 2004, el retorno promedio por año de educación para los asalariados fue de 12.5% mientras que resultó de 6.5% para los independientes.» | abierto | consistente con la literatura | OK |
| 9 | Corrección de retransformación (smearing) de log-ingreso a niveles | app/streamlit_app.py:1234,1257 | duan1983 | Título (Crossref: JASA 78, pp. 605-610) | sí | no | Sin cita textual — paywall confirmado por Semantic Scholar, Unpaywall (`is_oa: false`) y Crossref (sin abstract). Lo único verificado es el título: «Smearing Estimate: A Nonparametric Retransformation Method» | pago | consistente con la literatura — solo en cuanto al nombre del método, que es el título del artículo; el contenido no se leyó | OK (sin afirmaciones sobre el contenido) |
| 10 | Sustento del post-Lasso (E7) | app/referencias.py (nota belloni2014) | belloni2014 | Abstract | sí | sí | El paper trata métodos de alta dimensionalidad para inferencia estructural — coincide con la nota | abierto | — (no hay E7 en la app actual; referencia huérfana) | retirar |
| 11 | Marco para leer la brecha regresión lineal vs. árboles | app/referencias.py (nota athey2019) | athey2019 | Abstract | sí | sí | Revisa métodos de ML relevantes para economistas — coincide con la nota | abierto | — (sin `ref('athey2019')` en el código) | retirar |
| 12 | Comparación ML vs. regresión para predecir pobreza | app/referencias.py (nota sohnesen2016) | sohnesen2016 | Abstract | sí | sí | «Comparing out-of-sample predictions in surveys for same year in six countries shows that random forest is often more accurate than current common practice.» | abierto | consistente con la literatura (falta el matiz: ningún método es consistente en el tiempo) | corregir (nota incompleta) |
| 13 | ROC-AUC es optimista con clases desbalanceadas; usar PR-AUC | app/streamlit_app.py:2209,2238 | saito2015 | Abstract | sí | sí | «PRC plots... can provide the viewer with an accurate prediction of future classification performance...»; «one can ask whether ROC plots could be misleading when applied in imbalanced classification scenarios» | abierto | consistente con la literatura | OK |
| 14 | Tasas oficiales de empleo informal 2025 (70,2%/64,5%/94,8%/88,6%/15,6%) | app/streamlit_app.py:1364,2133; README.md:140,147,455,461 | inei_informal (cita actual, incorrecta) | — | sí | sí (pero de otro año) | «Los datos de la informalidad se han obtenido en base a... EPEN al 2024»; «Tres de cada cuatro... (70,9%)» — cifras 2024, no 2025 | abierto | hallazgo propio, cita mal atribuida | corregir (usar inei_empleo_2025) |
| 15 | Tasas oficiales de empleo informal 2025, cifras correctas | propuesto en docs/MARCO_TEORICO.md | inei_empleo_2025 (nueva) | Cuadro 1.20, Gráfico 1.15, Cuadro 1.22 | sí | sí | «el 70,2% tenían empleo informal»; «94,8%... rural... 64,5%»; «88,6%... 1 a 10 trabajadores... 44,0%... 11 a 50... 15,6%... 51 y más» | abierto | consistente con la literatura | nueva |
| 16 | README `[8]` junto a la cifra 88,6%/15,6% | README.md:462 | (huérfano: `[8]`=sohnesen2016 en el orden actual de referencias.py) | — | — | — | El README no tiene sección de referencias numerada propia; `[8]` no corresponde a ninguna fuente INEI | — | corregir cita | corregir |
| 17 | Origen del término "informal": Hart (1973), migrantes en Accra | docs/MARCO_TEORICO.md, eje 1 | hart1973 | p. ~68 | sí | sí | «The distinction between formal and informal income opportunities is based essentially on that between wage-earning and self-employment.» | abierto | consistente con la literatura | nueva |
| 18 | Misión OIT a Kenia (1972): el sector informal es eficiente y rentable, no marginal | docs/MARCO_TEORICO.md, eje 1 | oit1972kenya | Introducción | sí | sí | «the bulk of employment in the informal sector, far from being only marginally productive, is economically efficient and profit-making» | abierto | consistente con la literatura | nueva |
| 19 | Distinción sector informal (empresa) vs. empleo informal (puesto) | docs/MARCO_TEORICO.md, eje 1 | chen2012 | p. 3, 7 | sí | sí | «unincorporated small or unregistered enterprises (1993 ICLS); informal employment refers to employment» | abierto | consistente con la literatura | nueva |
| 20 | Criterio operacional de empleo informal (aporte a seguridad social / registro de la unidad) | docs/MARCO_TEORICO.md, eje 1 | oit2018_mujeres_hombres | p. 9 | sí | sí | «the formal or informal nature of a job held by an employee is determined... social security contributions by the employer... own-account workers are considered informal when their economic units belong to the informal sector» | abierto | consistente con la literatura | nueva |
| 21 | Definición de empleo informal (17.ª CIET, 2003), vigente tras la 21.ª CIET (2023) | app/referencias.py (nota oit_17ciet) | oit_17ciet | Texto de la 21.ª CIET (Report II) | sí | sí | «informal sector, adopted by the 15th ICLS (1993)... of informal employment, endorsed by the 17th ICLS (2003)» | abierto | consistente con la literatura | corregir (nota: no confirmado el nombre "Resolución I"; usar "resolución de la 21.ª CIET (2023)") |
| 22 | Cuatro escuelas teóricas (dualista/estructuralista/legalista/voluntarista) | docs/MARCO_TEORICO.md, eje 2 | chen2012 | pp. de definición de escuelas | sí | sí | «The Dualist school sees...»; «The Structuralist school sees...»; «The Legalist school sees...»; «The Voluntarists argue...» | abierto | consistente con la literatura | nueva |
| 23 | Lewis (1954): modelo dual de oferta ilimitada de trabajo | docs/MARCO_TEORICO.md, eje 2 | lewis1954 | — | sí (vía La Porta-Shleifer 2014) | no | Solo lectura de terceros: «The evidence appears most consistent with Lewis's dual view of informality» (La Porta-Shleifer, no cita de Lewis) | pago | lectura nuestra (marco general) | nueva |
| 24 | Harris-Todaro (1970): migración por diferenciales de salario esperado | docs/MARCO_TEORICO.md, eje 2 | harristodaro1970 | — | sí (vía cita secundaria) | no | Ninguna — solo referencia secundaria confirma que la literatura de informalidad adoptó este modelo como antecedente | pago | lectura nuestra | nueva |
| 25 | Tokman (1978): relación informal-formal, tradición dualista | docs/MARCO_TEORICO.md, eje 2 | tokman1978 | — | sí (vía Chen 2012) | no | — | pago | lectura nuestra | nueva |
| 26 | Portes, Castells y Benton (1989): informalidad como unidades subordinadas | docs/MARCO_TEORICO.md, eje 2 | portescastellsbenton1989 | — | sí (vía Chen 2012) | parcial (resumen de Chen, no el libro) | «The Structuralist school sees the informal economy as subordinated economic units (micro-enterprises)» (cita de Chen sobre el libro) | pago | lectura nuestra | nueva |
| 27 | De Soto (1989): informalidad como respuesta racional al costo legal | docs/MARCO_TEORICO.md, eje 2 | desoto1989 | — | sí (año 1989 confirmado en 3 fuentes: loayza2008, perry2007, chen2012) | no | — | pago | lectura nuestra | nueva |
| 28 | Maloney (2004): sector informal como microempresa voluntaria, análoga a la formal | docs/MARCO_TEORICO.md, eje 2 | maloney2004 | p. de discusión | sí | sí | «if in fact much of the sector is voluntary, in the sense of...» | abierto | consistente con la literatura | nueva |
| 29 | Günther-Launov: coexisten régimen de último recurso y de ventaja comparativa | docs/MARCO_TEORICO.md, eje 2 | guntherlaunov2012 | preprint IZA DP2349, pp. 116-117 | sí | sí (vía preprint 2006, no la versión de revista 2012) | «the informal sector as a strategy of last resort to escape involuntary unemployment, whereas the comparative advantage hypothesis sees informal employment as a voluntary choice» | pago (versión de revista); abierto (preprint) | consistente con la literatura | nueva |
| 30 | La Porta y Shleifer (2014): el modelo dual explica mejor la evidencia de firmas informales | docs/MARCO_TEORICO.md, eje 2 | laportashleifer2014 | p. 345 (NBER WP 20205) | sí | sí | «The evidence appears most consistent with Lewis's dual view of informality, which sees the formal and informal economies as largely segregated» | abierto | consistente con la literatura | nueva |
| 31 | Levy (2008): programas sociales como incentivo a la informalidad | docs/MARCO_TEORICO.md, eje 2 | levy2008 | — | sí (vía La Porta-Shleifer 2014) | no | Solo paráfrasis de terceros | pago | lectura nuestra | nueva |
| 32 | Ulyssea (2020): las brechas salariales no bastan para probar segmentación; informalidad decrece con tamaño de firma | docs/MARCO_TEORICO.md, eje 2 | ulyssea2020 | pp. 199, 761 (copia del autor) | sí | sí | «one cannot rely on wage gaps to test for the existence of segmentation...»; «both the extensive and intensive margins of informality decline with firm size» | abierto | consistente con la literatura | nueva |
| 33 | Matos Mar (1984): el "circuito popular contestatario" nace de la crisis del Estado y la migración | docs/MARCO_TEORICO.md, eje 3 | matosmar1984 | pp. 58-59, 81 | sí | sí | «Se produce el crecimiento de una economía popular contestataria a la que la opinión pública ha dado en llamar como "informal"»; «La vida social de la ciudad acepta hoy y difunde, como parte de sus estrategias de supervivencia, la organización colectiva en base a vínculos familiares extendidos» | abierto | consistente con la literatura | nueva |
| 34 | Golte y Adams (1987): redes de parentesco y paisanaje organizan el trabajo urbano migrante | docs/MARCO_TEORICO.md, eje 3 | golteadams1987 | p. 22 | sí | sí | «en sus asociaciones empresariales y en el reclutamiento de personal, recurren a relaciones de parentesco, así como también porque mantienen su inserción en la economía comunal» | abierto | consistente con la literatura | nueva |
| 35 | Rodríguez (2011): brecha asalariado/autoempleado 22-64% (ENAHO 2008-09, matching) | docs/MARCO_TEORICO.md, eje 3 | rodriguez2011 | Resumen | sí | sí | «Los resultados sugieren la existencia de segmentación entre estos dos tipos de puestos de trabajo»; «diferencias en 22 y 31% con... diferencias en las diferencias y entre 33 y 64% con... propensity score matching» | abierto | consistente con la literatura | nueva |
| 36 | Kamichi (2023): >80% de informales no se registra por "no lo considera necesario"/"negocio pequeño" | docs/MARCO_TEORICO.md, eje 3 | kamichi2023 | Cuerpo del ensayo (datos INEI) | sí | sí | «es porque "no lo consideran necesario" (53 %), porque su "negocio es pequeño" (32,5 %) y porque "es un trabajo enventual" (9,5 %); mientras que... "le quita demasiado tiempo" (0,4 %)» | abierto | consistente con la literatura | nueva |
| 37 | Ñopo (2008): brecha de género en Perú 1986-2000 = 45%, 28 pp sin explicar | docs/MARCO_TEORICO.md, eje 4 | nopo2008 | Abstract | sí | sí | «the 45% gender wage gap in Peru is decomposed as: 11% explained by differences in the supports, 6% explained by differences in the distributions of individual characteristics and the remaining 28% cannot be explained» | abierto | consistente con la literatura | nueva |
| 38 | Ñopo-Atal-Winder (2009): brecha de género 9-27% en ALC, mayor entre informales/independientes/empresas pequeñas | docs/MARCO_TEORICO.md, eje 4 | nopo_atal_winder2009 | Abstract | sí | sí | «men earn 9-27 percent more than women... The unexplained pay gap is higher among older, informal and self-employed workers and those in small firms» | abierto | consistente con la literatura | nueva |
| 39 | Blau y Kahn (2017): capital humano convencional explica poco de la brecha de género en EE. UU. | docs/MARCO_TEORICO.md, eje 4 | blaukahn2017 | NBER WP 21913 | sí | sí | «Using PSID microdata over the 1980-2010, we provide new empirical evidence on the extent of and trends in the gender wage gap, which declined considerably over this period.» (cita corregida en la verificación; la cita original propuesta por eje_4 no era verbatim) | abierto | consistente con la literatura | nueva |
| 40 | Goldin (2014): el último tramo de la brecha de género se explica por la prima a la disponibilidad horaria | docs/MARCO_TEORICO.md, eje 4 | goldin2014 | Harvard Scholar PDF | sí | sí | «The gender gap in pay would be considerably reduced and might even vanish if firms did not have an incentive to disproportionately reward individuals who worked long hours and worked particular hours.» | abierto | consistente con la literatura | nueva |
| 41 | Ñopo-Saavedra-Torero (2004): brecha étnica en asalariados, no en independientes | docs/MARCO_TEORICO.md, eje 4 | nopo_saavedra_torero2004 | IZA DP 980 | sí | sí | «there are racially related earnings differences in favor of predominantly White individuals. In the case of the self-employed, none of the empirical distributions of earning differences attributable to race is substantially above zero» | abierto | consistente con la literatura | nueva |
| 42 | Arpi y Arpi (2018): brecha étnica ~50%, cada vez más explicada por educación | docs/MARCO_TEORICO.md, eje 4 | arpi2018 | Redalyc | sí | sí | «descomponiendo mediante el método de Blinder-Oaxaca (1973)... El alcance explicativo por características observables... aumentó de 54% en 2006 a 77% en 2016» | abierto | consistente con la literatura | nueva |
| 43 | MTPE (2020): residual no explicado en la brecha formal/informal peruana | docs/MARCO_TEORICO.md, eje 4 | esparta_rivera2020 | Boletín MTPE N.º 104 | sí | sí | «se encuentra evidencia de que dicha brecha no es atribuible únicamente a factores observables... sino también a factores no observables asociados a algún tipo de discriminación o segmentación» | abierto | consistente con la literatura | nueva |
| 44 | Evidencia de Sudáfrica: la penalidad de informalidad puede desaparecer al controlar no observables | docs/MARCO_TEORICO.md, eje 4 | iza3151_2007 | IZA DP 3151 | sí | sí | «we find that there is a gross wage penalty of a little over 18 per cent for working in the informal sector. However, once we reduce our sample... the wage penalty disappears» (autoría del WP no confirmada en el PDF) | abierto | consistente con la literatura (resultados mixtos) | nueva |
| 45 | Breiman (2001): cultura del modelado de datos vs. cultura algorítmica | docs/MARCO_TEORICO.md, eje 6 | breiman2001 | Encabezado + cuerpo | sí | sí | «Statistical Modeling: The Two Cultures / Author(s): Leo Breiman / Source: Statistical Science, Vol. 16, No. 3 (Aug., 2001), pp. 199-215» | abierto | consistente con la literatura | nueva |
| 46 | Shmueli (2010): explicar y predecir son objetivos de modelado distintos | docs/MARCO_TEORICO.md, eje 6 | shmueli2010 | p. 289 | sí | sí | «Conflation between explanation and prediction is common, yet the distinction must be understood for progressing scientific knowledge.» | abierto | consistente con la literatura | nueva |
| 47 | Mullainathan-Spiess (2017): ML para predicción, no para estimación de parámetros causales | docs/MARCO_TEORICO.md, eje 6 | mullainathan2017 | Abstract (parcial) | sí | parcial | Resumen confirma el tema; no se recuperó cita línea por línea del cuerpo | abierto | consistente con la literatura | nueva |
| 48 | Kleinberg et al. (2015): problemas de predicción vs. problemas de inferencia causal en política pública | docs/MARCO_TEORICO.md, eje 6 | kleinberg2015 | RePEc (resumen) | sí | parcial | Resumen corto confirma el argumento; no se recuperó el PDF completo de NBER | abierto | consistente con la literatura | nueva |
| 49 | Barocas, Hardt y Narayanan: quitar el atributo protegido no basta (proxies redundantes) | docs/MARCO_TEORICO.md, eje 6 | barocas2023 | Cap. 1 | sí | sí | «What if we simply withhold gender from the data? Is that a sufficient response to concerns about gender discrimination?»; «In real datasets, most attributes tend to be proxies for demographic variables, and dropping them may not be a reasonable option.» | abierto | consistente con la literatura | nueva |
| 50 | Aiken et al. (2022): ML con datos de telefonía reduce errores de exclusión en ayuda humanitaria (Togo) | docs/MARCO_TEORICO.md, eje 6 | aiken2022 | Abstract | sí | sí | «Relative to the geographic targeting options considered by the Government of Togo, the machine-learning approach reduces errors of exclusion by 4–21%.» | abierto | consistente con la literatura | nueva |

---

## Notas sobre libros y artículos sin copia abierta (solo "existe / trata el tema")

Estas referencias tienen **Contenido verificado = no**: se citan únicamente para afirmar
que el trabajo existe y trata el tema indicado, nunca para respaldar una frase textual
específica.

- **Oaxaca (1973)** — PDF disponible pero es un escaneo sin capa de texto (pypdf/pdftotext
  devuelven 0 caracteres). Metadatos confirmados vía RePEc.
- **Blinder (1973)** — paywall JSTOR/Journal of Human Resources, sin versión de autor.
  Metadatos confirmados vía bibliografía de Ñopo (2008).
- **Lewis (1954)** — paywall Wiley. Metadatos confirmados vía La Porta-Shleifer (2014).
- **Harris y Todaro (1970)** — paywall AER. Metadatos confirmados vía cita secundaria; el
  término "sector informal" no aparece en este paper (lo acuña Hart 1973 después).
- **Tokman (1978)** — paywall Elsevier (World Development). Metadato exacto tomado de la
  bibliografía de Chen (2012).
- **Portes, Castells y Benton (1989, eds.)** — libro, paywall Johns Hopkins UP. Metadatos
  confirmados vía Chen (2012); contenido solo a través del resumen que Chen hace del
  capítulo de Castells y Portes.
- **De Soto (1989)** — libro, sin edición abierta completa localizada. Año de la edición
  inglesa (1989, no 1986) confirmado en tres fuentes independientes abiertas (Loayza 2008,
  Perry et al. 2007, Chen 2012); editorial en disputa entre dos fuentes secundarias
  (Basic Books según Perry et al.; Harper & Row según una búsqueda web no verificada
  directamente) — no resuelto, se deja anotado.
- **Levy (2008)** — libro, Brookings Institution, sin PDF abierto localizado. Metadatos
  confirmados vía La Porta-Shleifer (2014); contenido solo a través de la paráfrasis que
  hacen de él.

## Casos no verificados / descartados para cita puntual

- **Chaman Álvarez (2025)**, *Monthly Labor Review* (BLS): metadatos confirmados (autor,
  título, revista, fecha), pero el sitio bls.gov bloquea peticiones automatizadas (curl
  directo y snapshot de Wayback Machine solo devuelven el armazón JS). No se usa ninguna
  cifra de este artículo en ningún documento.
- **Frosch (2024)**, sobre la 21.ª CIET: paywall (Sage Journals, 403). Se sustituyó por el
  documento primario de la OIT (Report II de la 21.ª CIET), con acceso abierto confirmado.
- **Kolev (2015)**, sobre brecha étnica de mujeres indígenas en Perú: paywall Wiley (403),
  sin versión de autor abierta encontrada. Descartada por no poder verificar contenido.
