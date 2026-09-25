# Eje 5 — Capital humano y segmentación (Fase 2, literatura)

Todas las citas textuales fueron tomadas de texto crudo (pdftotext -layout -enc UTF-8) guardado en
`scratchpad/fase2/raw/<id>.txt`. Ninguna cita proviene de un resumen de WebFetch/WebSearch.

## A. Referencias

### mincer1974
- **Cita completa**: Mincer, J. (1974). *Schooling, Experience, and Earnings*. NBER / Columbia University Press (capítulo "The Human Capital Earnings Function", pp. 83-96).
- DOI: no tiene (volumen NBER anterior a la era DOI). URL: https://www.nber.org/system/files/chapters/c1767/c1767.pdf
- Acceso: abierto (PDF completo, capítulo del volumen).
- **Metadatos verificados**: sí (portada NBER: "Volume Title: Schooling, Experience, and Earnings", "Volume Author: Jacob A. Mincer", "Publication Date: 1974", "Chapter pages: p. 83-96").
- **Contenido verificado**: sí, texto completo del capítulo leído.
- Cita textual (Tabla 5.1, ≤40 palabras): «P(1) ln Y=6.20+.107s+.081t—.0012t2 .285» / «P(3) ln Y= f(D3) + .068t— .0009t2 + 1.207 ln W .525» (raw/mincer1974.txt líneas 476, 484).
- Qué dice: la especificación parabólica canónica (escolaridad + experiencia + experiencia²) da R²=0,285; al añadir semanas trabajadas (oferta laboral) sube a 0,525. Confirma exactamente ambas cifras que usa la app.
- Verificado: **sí**.

### card1999
- **Cita completa**: Card, D. (1999). «The Causal Effect of Education on Earnings». En Ashenfelter y Card (eds.), *Handbook of Labor Economics*, vol. 3A, cap. 30, pp. 1801-1863. Elsevier.
- DOI: 10.1016/S1573-4463(99)03011-4 (no verificado directamente, es el DOI estándar del capítulo del Handbook; el PDF abierto es la working paper previa, Berkeley CLE WP n.º 2, mayo 1998).
- URL: https://eml.berkeley.edu/~cle/wp/wp2.pdf · Acceso: abierto.
- Metadatos verificados: sí (portada: "Center for Labor Economics... Working Paper No. 2", "The Causal Effect of Education on Earnings", "David Card", "Prepared for the Handbook of Labor Economics, volume 3, edited by Orley Ashenfelter and David Card").
- Contenido verificado: sí.
- Cita textual (Tabla 1, ≤40 palabras): «R-squared 0.328 0.182 0.136 0.222 0.403» (hombres) y «R-squared 0.247 0.071 0.074 0.105 0.247» (mujeres), columna 1 = log salario por hora (raw/card1999.txt líneas 2603, 2610).
- Qué dice: en la CPS 1994-96, el R² del modelo minceriano estándar sobre log salario/hora va de 0,247 (mujeres) a 0,328 (hombres). Confirma el rango «0,247 y 0,328» que cita la app.
- Verificado: **sí**.

### lemieux2006
- **Cita completa**: Lemieux, T. (2006). «The "Mincer Equation" Thirty Years After *Schooling, Experience, and Earnings*». En Grossbard (ed.), *Jacob Mincer: A Pioneer of Modern Labor Economics*, cap. 11, pp. 127-145. Springer.
- DOI: 10.1007/0-387-29175-X_11 (no verificado directamente). URL: https://economics.ubc.ca/wp-content/uploads/sites/38/2013/05/pdf_paper_thomas-lemieux-mincer-equation.pdf · Acceso: abierto.
- Metadatos verificados: sí (portada: "Chapter 11 — The 'Mincer Equation' Thirty Years after Schooling, Experience, and Earnings").
- Contenido verificado: sí, texto completo leído.
- Cita textual (≤40 palabras): «Though Mincer (1974) considered several functional forms for the earnings equation, the most commonly used is equation (1)» (raw/lemieux2006.txt línea 150-165).
- Qué dice: evalúa si la ecuación de Mincer sigue siendo un buen benchmark 30 años después y qué ajustes de forma funcional (experiencia cuártica, escolaridad cuadrática) mejoran el ajuste. **No reporta ningún R²** en todo el texto: se buscó la cadena "R2"/"R-squared" en las 944 líneas y no aparece ni una vez. Confirma que el R² no puede atribuírsele (coherente con la autocorrección que ya hizo la app, streamlit_app.py:1999-2010).
- Verificado: **sí** (para lo que la app afirma: forma funcional, no cifra de R²).

### heckman2006
- **Cita completa**: Heckman, J., Lochner, L. y Todd, P. (2006). «Earnings Functions, Rates of Return and Treatment Effects: The Mincer Equation and Beyond». *Handbook of the Economics of Education*, vol. 1, cap. 7, pp. 307-458. Elsevier.
- DOI: 10.1016/S1574-0692(06)01007-5 (no verificado directamente). URL: https://www.nber.org/papers/w11544 (versión abierta = NBER WP 11544, agosto 2005). Acceso: abierto.
- Metadatos verificados: sí, con una precisión — el título real en portada es «EARNINGS FUNCTIONS, RATES OF RETURN, AND TREATMENT EFFECTS: THE MINCER EQUATION AND BEYOND», autores James J. Heckman, Lance J. Lochner, Petra E. Todd, NBER WP 11544, agosto 2005 (el capítulo del Handbook es 2006; la WP es la versión previa).
- Contenido verificado: sí, texto completo (7.838 líneas) revisado.
- Cita textual (≤40 palabras): «experience: Potential experience is measured by Age − Years of Education − 6.» (raw/heckman2006.txt línea 5436, repetida en 5462).
- Qué dice: el paper SÍ define y usa "potential experience = edad − años de educación − 6" (confirma la fórmula que usa la app). **Pero no encontré, tras buscar "overstate", "understate", "proxy", "measurement error… experience", "dropout"+"experience", "discontinuous"/"interrupt" en todo el documento, ninguna frase que diga que la experiencia potencial sobreestima la experiencia efectiva en trabajadores de baja educación.** Es la misma clase de error que ya corrigió la app con Lemieux/R²: una afirmación plausible pero no localizable en la fuente citada.
- Verificado: **parcial** — la fórmula sí; el enunciado sobre sobreestimación en baja educación, **no** (ver sección D).

### psacharopoulos2018
- **Cita completa**: Psacharopoulos, G. y Patrinos, H. A. (2018). *Returns to Investment in Education: A Decennial Review of the Global Literature*. Policy Research Working Paper 8402. Banco Mundial (Education Global Practice, abril 2018).
- DOI: 10.1080/09645292.2018.1484426 — **nota**: ese DOI corresponde a la versión de revista (*Education Economics* 26(5), 2018), no al working paper del Banco Mundial en sí; el WP no trae DOI propio. No es un error, pero conviene decirlo (mismo patrón que sohnesen2016, ya señalado en el archivo).
- URL: https://documents1.worldbank.org/curated/en/442521523465644318/pdf/WPS8402.pdf (PDF real encontrado; la URL `documents.worldbank.org/curated/en/...` del archivo actual es una landing page que no sirve el PDF directo — **sugerir cambiar la URL** por la de documents1, que sí resuelve). Acceso: abierto.
- Metadatos verificados: sí (portada: "Policy Research Working Paper WPS8402", "George Psacharopoulos", "Harry Antony Patrinos", "Education Global Practice, April 2018").
- Contenido verificado: sí.
- Cita textual (≤40 palabras): «the private average global rate of return to one extra year of schooling is about 9 percent a year» (abstract, raw/psacharopoulos2018.txt línea 25-26); «Latin America and Caribbean 11.0 7.3» (Tabla 3, línea 463).
- Qué dice: 1.120 estimaciones en 139 países; retorno privado global promedio ≈9 %/año; América Latina y el Caribe 11,0 % (tasa "overall rate of return", no exactamente "por año adicional de escolaridad" sino tasa de retorno global de la región — ligera diferencia de matiz frente a la nota actual, que dice "11,0 % anual"; la tabla la llama "overall rate of return (%)").
- Verificado: **sí**, con la precisión de matiz anterior.

### yamada2007
- **Cita completa**: Yamada, G. (2007). *Retornos a la educación superior en el mercado laboral: ¿vale la pena el esfuerzo?* Informe final, Proyecto Mediano CIES-ACDI/IDRC 2005, Centro de Investigación de la Universidad del Pacífico / CIES, enero 2007. Asistente de investigación: María Cárdenas.
- DOI: no tiene. URL usada para verificar (la de `referencias.py` no descarga el PDF; funcionó el espejo): https://cies.org.pe/wp-content/uploads/2016/07/retornos-a-la-educacion-superior-en-el-mercado-laboral.pdf — **sugerir verificar en vivo la URL actual del repo** (`cies.org.pe/publicaciones/...`), no pude confirmar que sirva el PDF directamente vs. una página de aterrizaje; el mirror sí sirve el documento completo. Acceso: abierto.
- Metadatos verificados: sí (portada: "Universidad del Pacífico, Centro de Investigación", "Retornos a la Educación Superior en el Mercado Laboral: ¿Vale la pena el esfuerzo?", "Gustavo Yamada", enero 2007).
- Contenido verificado: sí.
- Cita textual (≤40 palabras): «En el año 2004, el retorno promedio por año de educación para los asalariados fue de 12.5% mientras que resultó de 6.5% para los independientes.» (raw/yamada2007.txt líneas 914-916, Cuadro 4).
- Qué dice: retornos lineales mincerianos por tipo de empleo (ENAHO 2004): asalariados 12,5 %, independientes 6,5 %. Coincide exactamente con la nota de la app.
- Verificado: **sí**.

## B. Cruces con la app

1. **+4,8 % por año de escolaridad (E6, WLS con controles)** → Psacharopoulos & Patrinos 2018: retorno global ≈9 %, LAC 11,0 % (retornos mincerianos simples, sin controles de ocupación/firma). Yamada 2007: 12,5 % asalariados / 6,5 % independientes en Perú 2004 (también sin esos controles). → **no podemos concluir que coincida o discrepe directamente**: son magnitudes distintas (retorno bruto tipo Mincer vs. coeficiente WLS condicional a género, experiencia, horas, industria, categoría ocupacional, tamaño de firma y región). Que el 4,8 % de E6 sea menor que el 6,5-12,5 % de Yamada y el 9-11 % de Psacharopoulos & Patrinos es **consistente con la literatura** en la dirección esperada (más controles → coeficiente menor), pero **ningún texto que verifiqué afirma explícitamente que agregar controles de ocupación/firma reduce el retorno a la escolaridad** (grep de "occupation control", "firm size", "bad control" en card1999, heckman2006 y lemieux2006: cero resultados). Etiqueta: **lectura nuestra**, no atribuible a estas fuentes. Ids: psacharopoulos2018, yamada2007.

2. **R² de E9 (soles) y E3 (log, 0,27)** → Mincer 1974: R²=0,285 (especificación canónica) / 0,525 (con semanas trabajadas). Card 1999: R² 0,247-0,328 (log salario/hora, CPS). → El 0,27 en logaritmo de E3 (mencionado en streamlit_app.py:2293) cae **dentro** del rango 0,247-0,328 de Card y cerca del 0,285 de Mincer. Etiqueta: **consistente con la literatura**. Ids: mincer1974, card1999.

3. **"Ningún R² supera 0,4-0,5" / cifras de Lemieux y Heckman sobre R²** (ya corregido en la app) → confirmado: ni Lemieux 2006 ni Heckman, Lochner & Todd 2006 reportan un R² en el texto completo que leí. La autocorrección de la app (streamlit_app.py:1994-2010) es correcta y queda re-verificada. Ids: lemieux2006, heckman2006.

4. **"Experiencia potencial, no real… sobreestima la experiencia efectiva (Heckman, Lochner & Todd, 2006)"** (streamlit_app.py:2344-2351) → la fórmula (edad − escolaridad − 6) SÍ está en Heckman et al. 2006, pero el enunciado de que sobreestima la experiencia real en trabajadores de baja educación **no lo encontré en el texto** tras una búsqueda exhaustiva. Etiqueta: **no podemos concluir / posible misatribución** — ver sección D, es la misma clase de error que el proyecto ya corrigió una vez con Lemieux. Recomendación: quitar la atribución a Heckman et al. 2006 para esa frase concreta, o cambiarla a «lectura nuestra» (edad−escolaridad−6 asume entrada continua al mercado laboral desde que se deja la escuela; en trabajos con interrupciones —común en baja educación e informalidad— la experiencia efectiva es menor que la potencial, pero esto es una inferencia razonable nuestra, no una cita). Id: heckman2006.

## C. Descartadas
- Ninguna de las seis referencias que poseo (mincer1974, card1999, lemieux2006, heckman2006, psacharopoulos2018, yamada2007) se descarta: las seis abrieron y dieron texto legible. Doeringer y Piore (1971) no estaban en mi lista de "existentes que poseo"; no los busqué porque el ámbito de esta pasada era auditar las seis ya citadas en el código, no ampliar la bibliografía. Si se desea sumarlos, es trabajo pendiente, no descartado por falla de verificación.

## D. Errores/precisiones de la semilla y del archivo actual
1. **heckman2006**: la app atribuye a Heckman, Lochner & Todd (2006) que la experiencia potencial "sobreestima la experiencia efectiva" en trabajadores de baja educación. Verifiqué la fórmula pero no ese enunciado específico en 7.838 líneas de texto. Recomiendo bajar la certeza de la nota o marcarla como lectura propia — no repetir el patrón que ya causó la auditoría de Lemieux.
2. **psacharopoulos2018**: la URL en `referencias.py` (`documents.worldbank.org/curated/en/442521523465644318`) es una landing page; el PDF real y descargable es `https://documents1.worldbank.org/curated/en/442521523465644318/pdf/WPS8402.pdf`. Sugerir actualizar el enlace para que el lector llegue directo al texto. El DOI listado es de la versión de revista (Education Economics), no del working paper — aclarar en la nota, como ya se hace con sohnesen2016.
3. **yamada2007**: la app no registra `doi` (correcto, no tiene). La URL del repo no la pude descargar directamente (devolvió HTML de 7 KB, probablemente landing/redirect); el espejo de 2016 en cies.org.pe sí sirvió el PDF completo. Sugerir confirmar en vivo que la URL vigente resuelve al PDF y no a una página intermedia.
4. Título de heckman2006 en portada real: coma después de "RATES OF RETURN," ("EARNINGS FUNCTIONS, RATES OF RETURN, AND TREATMENT EFFECTS..."), diferencia tipográfica menor frente a la cita de la app ("Rates of Return and Treatment Effects") — no cambia el significado, mencionar solo por exactitud bibliográfica.

## E. Refs existentes (ids que poseo) — resumen OK/corregir/retirar
- **mincer1974**: OK. cita, url, acceso y nota correctos y verificados.
- **card1999**: OK. cita, url, acceso y nota correctos y verificados.
- **lemieux2006**: OK. cita, url, acceso y nota correctos; confirmado que no reporta R².
- **heckman2006**: **corregir**. La entrada en referencias.py (cita/url/acceso) está bien, pero la frase que la cita en streamlit_app.py:2344-2351 (sobreestimación de experiencia en baja educación) no está respaldada por el texto verificado — corregir la atribución o marcarla como lectura propia.
- **psacharopoulos2018**: **corregir** la URL (usar el PDF directo de documents1.worldbank.org) y aclarar en la nota que el DOI es de la versión de revista.
- **yamada2007**: OK en cuanto a contenido citado; verificar en vivo que la URL del repo resuelve al PDF (no pude confirmarlo con la URL exacta que trae el archivo).
