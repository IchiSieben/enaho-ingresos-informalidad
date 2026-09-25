# Eje 6 — ML en economía y ética de la focalización (targeting)

## A. Referencias

### A1. Breiman, L. (2001). «Statistical Modeling: The Two Cultures». *Statistical Science* 16(3), pp. 199-215.
- DOI: 10.1214/ss/1009213726 · URL abierta: PDF alojado en www2.math.uu.se/~thulin/mm/breiman.pdf (copia académica del texto original de JSTOR) · acceso: abierto (copia terciaria; el sitio de la revista, projecteuclid.org, está detrás de un firewall Incapsula que bloqueó el fetch automatizado).
- metadatos verificados: sí (encabezado del PDF: "Statistical Science, Vol. 16, No. 3 (Aug., 2001), pp. 199–215", JSTOR stable URL 2676681).
- contenido verificado: sí. Cita textual (raw/breiman2001.txt): «Statistical Modeling: The Two Cultures / Author(s): Leo Breiman / Source: Statistical Science, Vol. 16, No. 3 (Aug., 2001), pp. 199-215» (encabezado de portada).
- Qué dice: contrapone la «cultura del modelado de datos» (se asume un proceso generador estocástico, se busca interpretar los parámetros) con la «cultura algorítmica» (el proceso es una caja negra, se optimiza precisión predictiva). Es exactamente el marco que separa E6 (explicativo) de E9 (predictivo).

### A2. Shmueli, G. (2010). «To Explain or to Predict?». *Statistical Science* 25(3), pp. 289-310.
- DOI: 10.1214/10-STS330 · URL abierta: PDF en www.stat.berkeley.edu/~aldous/157/Papers/shmueli.pdf · acceso: abierto.
- metadatos verificados: sí (cabecera del PDF: "Statistical Science 2010, Vol. 25, No. 3, 289–310, DOI: 10.1214/10-STS330").
- contenido verificado: sí. Cita textual (raw/shmueli2010.txt): «Conflation between explanation and prediction is common, yet the distinction must be understood for progressing scientific knowledge.»
- Qué dice: formaliza que un modelo con alto poder explicativo (ajuste in-sample, significancia de coeficientes) no garantiza poder predictivo out-of-sample, y viceversa — son objetivos de modelado distintos con implicancias en cada paso del proceso.

### A3. Mullainathan, S. y Spiess, J. (2017). «Machine Learning: An Applied Econometric Approach». *Journal of Economic Perspectives* 31(2), pp. 87-106.
- DOI: 10.1257/jep.31.2.87 · URL abierta: https://www.aeaweb.org/articles?id=10.1257/jep.31.2.87 (JEP es de acceso abierto) · acceso: abierto.
- metadatos verificados: sí (RePEc: título, volumen 31, issue 2, pp. 87-106 confirmados en raw/mullainathan2017_repec.html).
- contenido verificado: parcial. Se recuperó el resumen (raw/mullainathan2017.txt, 1201 caracteres) pero no la sección completa citable línea por línea; no se intentó bajar el PDF (JEP también sirve detrás de un desafío de Cloudflare en algunas rutas). El resumen confirma el tema: uso de ML para el "problema de predicción de variable Ŷ" en econometría aplicada, distinto de la estimación de parámetros causales β̂.
- Qué dice: separa "problemas de predicción" (donde ML brilla) de "problemas de estimación de parámetros" (donde la inferencia causal tradicional sigue siendo necesaria) — mismo argumento que Kleinberg et al. (A4) aplicado a política económica en general.

### A4. Kleinberg, J., Ludwig, J., Mullainathan, S. y Obermeyer, Z. (2015). «Prediction Policy Problems». *American Economic Review: Papers & Proceedings* 105(5), pp. 491-495.
- DOI: 10.1257/aer.p20151023 (no verificado directamente; no se abrió el DOI, se confirmó vía NBER y RePEc) · URL abierta: NBER Working Paper 20870, https://www.nber.org/papers/w20870 · acceso: abierto (versión NBER).
- metadatos verificados: sí (RePEc raw/kleinberg2015_repec.html confirma título "Prediction Policy Problems", AER P&P vol. 105 issue 5 pp. 491-95, año 2015).
- contenido verificado: parcial. Se obtuvo un resumen corto (raw/kleinberg2015.txt, 633 caracteres) de RePEc, no el PDF de NBER completo (no se intentó extraer por límite de tiempo del encargo).
- Qué dice: distingue problemas de política pública que son, en el fondo, problemas de predicción (p. ej. ¿quién no pagará una deuda? ¿quién necesita ayuda?) de los que son de inferencia causal (¿qué intervención cambia el resultado?), y argumenta que el machine learning aporta directamente a los primeros. Es la referencia que mejor sustenta «herramienta de focalización, no causal» para el clasificador de informalidad.

### A5. Barocas, S., Hardt, M. y Narayanan, A. (2023). *Fairness and Machine Learning: Limitations and Opportunities*. MIT Press. (Versión web: fairmlbook.org)
- URL abierta: https://fairmlbook.org/ (libro completo en PDF y por capítulos) · acceso: abierto.
- metadatos verificados: sí (portada del sitio: «The book has been published», MIT Press, 2023, confirmado en raw/barocas_raw.html).
- contenido verificado: sí, capítulo 1 (Introduction), raw/barocas_intro.txt.
- Cita textual 1 (≤40 palabras): «What if we simply withhold gender from the data? Is that a sufficient response to concerns about gender discrimination?»
- Cita textual 2 (≤40 palabras): «In real datasets, most attributes tend to be proxies for demographic variables, and dropping them may not be a reasonable option.»
- Qué dice: quitar el atributo protegido (sexo, género) de un clasificador casi nunca es suficiente, porque otras variables actúan como proxies o «codificaciones redundantes» del atributo protegido, y suelen ser genuinamente relevantes para la decisión — no se pueden simplemente eliminar sin perder precisión.

### A6. Aiken, E., Bellue, S., Karlan, D., Udry, C. y Blumenstock, J. E. (2022). «Machine learning and phone data can improve targeting of humanitarian aid». *Nature* 603, pp. 864-870.
- DOI: 10.1038/s41586-022-04484-9 · URL abierta: https://pmc.ncbi.nlm.nih.gov/articles/PMC8967719/ · acceso: abierto.
- metadatos verificados: sí (meta tags citation_* de PMC: 5 autores, Nature, vol. 603, publicado 2022-03-16, primera página 864).
- contenido verificado: sí, resumen completo (raw/aiken2022.txt).
- Cita textual (≤40 palabras): «Relative to the geographic targeting options considered by the Government of Togo, the machine-learning approach reduces errors of exclusion by 4–21%.»
- Qué dice: entrena un clasificador de pobreza sobre datos de telefonía móvil (con encuestas como ground truth) para focalizar ayuda de emergencia COVID-19 en Togo; compara errores de exclusión, bienestar social y medidas de equidad («fairness») contra targeting geográfico y contra un registro social hipotético. Caso real, reciente y abierto de exactamente el tipo de sistema que pide el eje: ML como herramienta de focalización, con sus trade-offs de equidad hechos explícitos.
- **Candidato añadido** (no estaba en la semilla): más pertinente que un PMT genérico porque mide fairness empíricamente, no solo la discute en abstracto.

## B. Cruces con la app

1. **Separación E9 predictivo / E6 explicativo** (app: dos modelos distintos, mismo problema) → Breiman (2001) y Shmueli (2010) formalizan exactamente esta distinción como dos objetivos de modelado incompatibles entre sí en general → **coincide** → consistente con la literatura → A1, A2.

2. **«Herramienta de focalización, no causal, no predicción individual»** (app: el clasificador de informalidad «flags job configurations, not people») → Kleinberg et al. (2015) y Mullainathan & Spiess (2017) distinguen problemas de predicción de problemas de inferencia causal y sitúan el targeting de política pública en el primer grupo → **coincide** → consistente con la literatura → A3, A4. Nota: ninguno de los dos habla específicamente de informalidad laboral ni de Perú; el marco es general.

3. **PR-AUC ≈ 0.96, la ablación que quita tamaño de firma + categoría ocupacional deja PR-AUC ≈ 0.94 — el modelo «flags job configurations, not people»** → la referencia más cercana en la semilla (proxy-means testing / targeting con ML) es sohnesen2016 (ver sección E), que compara random forest contra regresión para predecir pobreza y encuentra que el ML suele ser más preciso pero no consistentemente a través del tiempo → **no podemos concluir** una comparación directa (el hallazgo del app es sobre *robustez a remover variables*, no sobre random forest vs. regresión) → **hallazgo propio**, con Aiken et al. (2022) como paralelo aplicado (ML de targeting con trade-offs de equidad) → A6.

4. **Ablación sin `sexo`: PR-AUC cae de 0.9626 a 0.9618 (diferencia real, t=6.26, p=0.003, pero magnitud irrelevante), tasas de precisión/recall por sexo casi no cambian** (reports/ablacion_sexo.md) → Barocas, Hardt y Narayanan explican por qué retirar el atributo protegido de un clasificador casi nunca «arregla» nada: otras variables (tamaño de firma, categoría ocupacional, horas) son proxies correlacionados con sexo, así que el modelo recupera casi toda la información que perdió → **coincide** con el mecanismo descrito en la literatura → consistente con la literatura → A5. El hallazgo propio es la magnitud exacta (−0.0008 de PR-AUC) y que las tasas de error por sexo apenas se mueven; la interpretación de *por qué* ocurre eso viene de A5.

5. **Sensibilidad al agregar ingreso en especie: la prima urbana baja de 54.6% a 52.0%** — no hay referencia de este eje que trate directamente esta robustez; queda fuera del alcance de A1-A6 → **no podemos concluir** (no hay literatura de este eje que lo cubra) → hallazgo propio, sin referencia asignable en este eje.

## C. Descartadas

- Ninguna referencia de la lista semilla del eje fue descartada por completo. Las cinco se verificaron con metadatos correctos; Mullainathan-Spiess y Kleinberg et al. quedaron con contenido solo **parcialmente** verificado (resumen corto, no el artículo completo) por límite de tiempo — no se descartan, pero su cita textual es más débil que las demás.
- Se evaluó y se descartó usar el DOI directo de Kleinberg et al. (10.1257/aer.p20151023): no se abrió (no se intentó dado que RePEc y NBER ya confirmaban metadatos); reportado como no verificado directamente, no como referencia inválida.
- No se buscó ni verificó `sohnesen2016`, `duan1983`, `belloni2014`, `athey2019`, `saito2015` en tanto «candidatos nuevos» porque ya eran propiedad del eje (ver sección E) — se verificaron ahí, no se duplican en A.

## D. Errores de la semilla

- Ninguno de los cinco ítems de la semilla del eje (Breiman, Shmueli, Mullainathan-Spiess, Kleinberg et al., Barocas-Hardt-Narayanan) tenía error de autor/año/título/journal. La única actualización real: la semilla decía «fairmlbook.org» como si fuera solo un sitio web; hoy es un **libro publicado** (Barocas, Hardt y Narayanan, *Fairness and Machine Learning: Limitations and Opportunities*, MIT Press, 2023), con el sitio como versión de acceso abierto del mismo texto. La cita debe llevar editorial y año de publicación del libro, no solo la URL.

## E. Refs existentes que este eje posee (`app/referencias.py`)

### duan1983
- **OK / corregir**: **corregir metadato menor**. El DOI resuelve pero Cloudflare bloquea el acceso automatizado (confirmado: raw/duan1983_raw.html devuelve un desafío "Just a moment..."). Unpaywall confirma que no existe copia de acceso abierto (`is_oa: false`, `oa_locations: []`) y que el journal es correcto: *Journal of the American Statistical Association*, ISSN 0162-1459/1537-274X, autor «Naihua Duan» (Rand Corporation), fecha de publicación 1983-09-01. La nota actual del app («no existe versión abierta legal... resuelve en navegador aunque el editor bloquee las peticiones automáticas») es correcta y queda confirmada por Unpaywall. Sin cambios de fondo.
- metadatos verificados: sí (Semantic Scholar + Unpaywall, raw/duan1983_ss.json y raw/duan1983_unpaywall.json).
- contenido verificado: no (paywall confirmado por dos fuentes independientes; ni Semantic Scholar ni Unpaywall exponen el abstract).
- Citas en app: `app/streamlit_app.py:1234` y `:1257` — describen la corrección de retransformación («smearing correction») para pasar de log-ingreso a ingreso en niveles. Esto es correcto y es exactamente lo que describe el título del paper («Smearing Estimate: A Nonparametric Retransformation Method»); no se pudo confirmar la fórmula exacta por el paywall, pero la atribución es consistente con el título/abstract conocidos de la literatura de econometría aplicada.

### belloni2014
- **retirar (de la app, no de referencias.py)**: **no está citado en ningún lugar de `app/` ni `README.md`** — se buscó `ref('belloni2014')` en todo el repo y no aparece ninguna coincidencia fuera de la propia entrada en `referencias.py`. La nota del archivo dice «Sustento y cautelas del post-Lasso (especificación E7)», pero no hay especificación E7 citándola en el código ni evidencia de que exista un E7 en el app actual (el brief solo describe E9 y E6). Es una referencia huérfana: correcta en sus metadatos, pero desconectada del código.
- metadatos verificados: sí (RePEc y AEAweb, raw/belloni2014_repec.html y raw/belloni2014_raw.html: autores Belloni/Chernozhukov/Hansen, JEP 28(2), pp. 29-50, DOI 10.1257/jep.28.2.29 — todo coincide con `referencias.py`).
- contenido verificado: sí (abstract completo, raw/belloni2014.txt): el paper trata métodos de alta dimensionalidad para inferencia sobre parámetros estructurales y efectos de tratamiento — coincide con la nota, pero no hay ninguna sentencia del app que lo use.
- **Acción sugerida**: si el eje E7 no existe en la versión actual del app, retirar la entrada de `referencias.py` o, si se planea reintroducir el post-Lasso, dejarla pero marcarla como pendiente de uso.

### athey2019
- **retirar (de la app, no de referencias.py)**: mismo caso que belloni2014 — **no está citado con `ref('athey2019')` en ningún archivo de `app/`**. La nota dice que es «el marco para leer la brecha entre regresión lineal y árboles», pero no hay una sentencia en `streamlit_app.py` que la use.
- metadatos verificados: sí (arXiv, raw/athey2019_abs.html): Athey y Imbens, *Annual Review of Economics* 11(1), pp. 685-725, versión abierta en arXiv 1903.10075 — coincide con `referencias.py`. El DOI 10.1146/annurev-economics-080217-053433 no se verificó directamente contra Annual Reviews (solo se abrió arXiv), pero es el DOI estándar publicado para este artículo.
- contenido verificado: sí (abstract completo, raw/athey2019.txt): revisa métodos de ML relevantes para economistas (supervisado, no supervisado, matrix completion) y métodos híbridos ML+econometría para inferencia causal — coincide con la nota del app.
- **Acción sugerida**: igual que belloni2014, es una referencia huérfana en el código actual.

### sohnesen2016
- **OK, con una precisión**: sí está correctamente descrita, aunque tampoco se encontró `ref('sohnesen2016')` citado en `app/`. A diferencia de las dos anteriores, esta SÍ es directamente relevante al eje 6 (comparación random forest vs. regresión para predecir pobreza) — se recomienda usarla si se agrega una sección de referencias comparables al clasificador de informalidad.
- metadatos verificados: sí (RePEc, raw/sohnesen2016_raw.html): título «Is random forest a superior methodology for predicting poverty? An empirical assessment», Policy Research Working Paper 7612, Banco Mundial, 2016 — coincide con `referencias.py`. Autores Sohnesen/Stender no se pudieron extraer de los metadatos RePEc en este pase (el campo `citation_author` no apareció en el HTML descargado), pero el título y año exactos sí.
- contenido verificado: sí (abstract completo, raw/sohnesen2016.txt). Cita textual (≤40 palabras): «Comparing out-of-sample predictions in surveys for same year in six countries shows that random forest is often more accurate than current common practice.» Y: «None of the methods consistently provides accurate predictions of poverty over time.»
- La nota del app («Comparación entre aprendizaje automático y regresión en encuestas de hogares») es correcta pero incompleta: el hallazgo central del paper incluye el matiz de que **ningún método (incluido random forest) predice pobreza de forma consistente a través del tiempo** — vale la pena añadir ese matiz si se cita en el texto del app, para no sugerir que random forest «gana» sin condiciones.

### saito2015
- **OK, sin cambios.**
- metadatos verificados: sí (PLOS ONE, raw/saito2015_raw.html): Saito y Rehmsmeier, *PLOS ONE* 10(3), e0118432, DOI 10.1371/journal.pone.0118432 — coincide exactamente con `referencias.py`.
- contenido verificado: sí (abstract completo, raw/saito2015.txt). Cita textual (≤40 palabras): «PRC plots, on the other hand, can provide the viewer with an accurate prediction of future classification performance due to the fact that they evaluate the fraction of true positives among positive predictions.»
- Citas en app: `app/streamlit_app.py:2209` y `:2238` — el texto dice que el ROC-AUC es «optimista» con clases desbalanceadas y remite a saito2015 para justificar mirar PR-AUC. Esto **coincide exactamente** con lo que dice el paper: «one can ask whether ROC plots could be misleading when applied in imbalanced classification scenarios... the visual interpretability of ROC plots... can be deceptive.» Nota y uso en el código: correctos, sin cambios.
