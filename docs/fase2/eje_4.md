# Eje 4 — Brechas salariales y descomposiciones

## A. Referencias

**1. `oaxaca1973`** — Oaxaca, R. L. (1973). "Male-Female Wage Differentials in Urban Labor
Markets". *International Economic Review*, 14(3), 693-709.
DOI: no disponible (pre-DOI). URL: https://inequality.stanford.edu/sites/default/files/media/_media/pdf/Classic_Media/Oaxaca_1973_Discrimination%20and%20Prejudice.pdf
Acceso: abierto (metadatos y PDF descargable). Verificado: **no** (contenido).
Metadatos verificados: sí (RePEc, IER 14(3):693-709, coincide en múltiples catálogos).
Contenido verificado: no — el PDF de Stanford es un escaneo sin capa de texto (pypdf y
pdftotext devuelven 0 caracteres útiles); no hay OCR disponible en este entorno. No puedo dar
cita textual. Qué dice (por descripción de terceros, no verificado directamente): propone
descomponer la brecha salarial en un componente explicado por características y un residual.
Guardado en `raw/oaxaca1973.pdf` (imagen, sin texto extraíble).

**2. `blinder1973`** — Blinder, A. S. (1973). "Wage Discrimination: Reduced Form and
Structural Estimates". *The Journal of Human Resources*, 8(4), 436-455.
DOI: 10.2307/144855. URL abierta: no encontrada (JSTOR/paywall; ninguna versión de autor
disponible). Acceso: pago. Verificado: **no**.
Metadatos verificados: sí — confirmados de forma cruzada en la lista de referencias de Ñopo
(2008/2004), que cita textualmente: "Blinder, Allan (1973). 'Wage Discrimination: Reduced
Form and Structural Estimates.' The Journal of Human Resources, VII, 4, pp. 436-55" (ver
`raw/nopo2008.txt`, líneas ~2101-2102; nota: Ñopo usa "VII" en vez de "8", mismo volumen).
Contenido verificado: no, no pude abrir el texto de Blinder mismo.

**3. `nopo2008`** — Ñopo, H. (2008). "Matching as a Tool to Decompose Wage Gaps". *The
Review of Economics and Statistics*, 90(2), 290-299. DOI: 10.1162/rest.90.2.290 (versión de
revista). URL abierta (versión de autor, IZA DP No. 981, enero 2004):
https://docs.iza.org/dp981.pdf. Acceso: abierto. Verificado: **sí**.
Cita textual (abstract, `raw/nopo2008.txt`): "Using data for Peru in the period 1986-2000, I
found that this problem of non-comparability accounts for 23% and 30% of the male and
female working populations respectively. […] the 45% gender wage gap in Peru is decomposed
as: 11% explained by differences in the supports, 6% explained by differences in the
distributions of individual characteristics and the remaining 28% cannot be explained by
differences in observable individuals' characteristics."
Qué dice: propone una alternativa no paramétrica (matching) a Oaxaca-Blinder que separa el
problema de "soporte no común" del resto; aplicada a Perú 1986-2000 encuentra una brecha de
género del 45%, de la cual 28 puntos porcentuales quedan sin explicar por características
observables.

**4. `nopo_atal_winder2009`** — Ñopo, H., Atal, J. P. y Winder, N. (2009). *New Century, Old
Disparities: Gender and Ethnic Wage Gaps in Latin America*. IDB Publications (Working
Papers) 1131 / Research Department Publications 4640, Banco Interamericano de Desarrollo.
(Versión revisada: IZA Discussion Paper No. 5085, julio 2010). URL abierta:
https://docs.iza.org/dp5085.pdf. Acceso: abierto. Verificado: **sí**.
Cita textual (abstract, `raw/nopo_atal_winder.txt`): "This paper surveys gender and ethnic
wage gaps in 18 Latin American countries, decomposing differences using matching
comparisons as a non-parametric alternative to the Blinder-Oaxaca (BO) decomposition. It is
found that men earn 9-27 percent more than women, with high cross-country heterogeneity.
The unexplained pay gap is higher among older, informal and self-employed workers and
those in small firms. Ethnic wage differences are greater than gender differences […] Higher
ethnic wage gaps are found among males, single-income generators of households and
full-time workers, and in rural areas."
Qué dice: 18 países de ALC; brecha de género 9-27% sin explicar según país; la brecha sin
explicar es MAYOR entre informales, independientes y empresas pequeñas — cruza
directamente con el hallazgo propio de −49.6% en independientes.
Nota: el IDB publicó el estudio también como libro/documento con el mismo título; no
encontré una edición separada de "2012" con esa numeración exacta (ver Descartadas / Errores
de la semilla).

**5. `blaukahn2017`** — Blau, F. D. y Kahn, L. M. (2017). "The Gender Wage Gap: Extent,
Trends, and Explanations". *Journal of Economic Literature*, 55(3), 789-865.
DOI: 10.1257/jel.20160995. URL abierta (NBER WP 21913, enero 2016):
https://www.nber.org/system/files/working_papers/w21913/w21913.pdf. Acceso: abierto (versión
NBER). Verificado: **sí**.
Cita textual (`raw/blaukahn2017_nber.txt`, línea ~30 y ~397): "provide empirical evidence on
the levels and trends in the gender wage gap, which declined considerably over this period.
By 2010, conventional human capital variables… taken together explained little of the gender
wage gap"; "unexplained gap—from 0.341 log points in 1980 to 0.197 log points in 2010."
Qué dice: en EE. UU. la brecha se redujo 1980-2010, pero el capital humano convencional ya
casi no la explica; lo que domina es ocupación/industria y un residual no explicado que bajó
pero no desapareció.

**6. `goldin2014`** — Goldin, C. (2014). "A Grand Gender Convergence: Its Last Chapter".
*American Economic Review*, 104(4), 1091-1119. DOI: 10.1257/aer.104.4.1091. URL abierta
(Harvard Scholar): https://scholar.harvard.edu/files/goldin/files/goldin_aeapress_2014_1.pdf.
Acceso: abierto. Verificado: **sí**.
Cita textual (`raw/goldin2014.txt`): "The gender gap in pay would be considerably reduced and
might even vanish if firms did not have an incentive to disproportionately reward individuals
who worked long hours and worked particular hours."
Qué dice: el último tramo de la brecha de género en EE. UU. se explica por cómo el mercado
laboral premia la disponibilidad horaria y la no-linealidad de la paga por hora, no por
diferencias de capital humano.

**7. `nopo_saavedra_torero2004`** — Ñopo, H., Saavedra, J. y Torero, M. (2004). *Ethnicity
and Earnings in Urban Peru*. IZA Discussion Paper No. 980 (enero 2004). Versión de revista:
"Ethnicity and Earnings in a Mixed-Race Labor Market", *Economic Development and Cultural
Change*, 55(4), 709-734 (julio 2007). URL abierta (IZA):
https://docs.iza.org/dp980.pdf. Acceso: abierto (WP); revista de pago. Verificado: **sí**
(versión WP).
Cita textual (`raw/nopo_saavedra_torero_ethnicity.txt`): "Our approach to the concept of
ethnicity involves the usage of instruments in many of its several dimensions: mother tongue,
parental background, religion, migration events and race. […] The results suggest that among
wage earners after controlling for a large set of characteristics, there are racially related
earnings differences in favor of predominantly White individuals. In the case of the
self-employed, none of the empirical distributions of earning differences attributable to race
is substantially above zero."
Qué dice: en Lima urbana, la brecha étnica/racial "pura" (tras controlar características)
aparece en los asalariados pero NO en los independientes — patrón distinto al que ve nuestra
app en la brecha de género (que sí persiste en la especificación WLS). Es la referencia
peruana correcta para encuadrar lengua materna/etnicidad (Fase 3), con el matiz de que usa
un índice racial multidimensional, no solo lengua materna.

**8. `arpi2018`** — Arpi Mayta, R. y Arpi Quilca, L. (2018). "Desigualdad del ingreso laboral
y nivel educativo entre grupos étnicos en el Perú". *COMUNI@CCIÓN: Revista de Investigación
en Comunicación y Desarrollo*, 9(1), 56-67. URL abierta:
https://www.redalyc.org/journal/4498/449856234006/449856234006.pdf (también en
scielo.org.pe). Acceso: abierto. Verificado: **sí**.
Cita textual (`raw/etnia_peru_redalyc.txt`): "descomponiendo mediante el método de
Blinder-Oaxaca (1973), se obtiene que la diferencia en niveles educativos logrados,
experiencia laboral y la probabilidad de formar parte del mercado laboral entre los grupos
étnicos, guarda estrecha relación con la continuidad de la diferencia en el ingreso laboral
(aproximadamente 50%)… El alcance explicativo por características observables… aumentó de
54% en 2006 a 77% en 2016; mientras, la influencia de las características no observables
(discriminación)… disminuyó de 46% a 23%."
Qué dice: con ENAHO 2006-2016 y Oaxaca-Blinder estándar (no matching), la brecha étnica de
ingresos (~50%) se mantiene estable en el tiempo, pero cada vez más explicada por educación y
menos por el residual "discriminación".

**9. `esparta_rivera2020`** — Esparta Polanco, D. y Rivera Reyna, G. (2020). *Brechas
salariales entre el empleo formal e informal*. Boletín Informativo Laboral N.º 104 (agosto
2020), Ministerio de Trabajo y Promoción del Empleo (MTPE), Perú.
URL abierta: https://cdn.www.gob.pe/uploads/document/file/1297314/Art%202%20-%20Brechas%20salarial.pdf.
Acceso: abierto. Verificado: **sí**.
Cita textual (`raw/mtpe_brecha_formal_informal.txt`): "los ingresos laborales de los
trabajadores informales vienen creciendo con mayor velocidad que el de los trabajadores
formales, lo cual se traduce en una reducción en la brecha salarial… Al descomponer la
brecha salarial entre ambos grupos de trabajadores… se encuentra evidencia de que dicha
brecha no es atribuible únicamente a factores observables… sino también a factores no
observables asociados a algún tipo de discriminación o segmentación en el mercado laboral."
Qué dice: fuente oficial peruana (MTPE) que descompone la brecha formal/informal y confirma
un residual no explicado — coincide en dirección con la penalidad de −49.6% de
independientes de nuestro E6, aunque mide formal/informal, no independiente/asalariado.

**10. `iza3151_2007`** — [Autor no confirmado con certeza en el PDF disponible —
la carátula del WP sólo lista "IZA DP No. 3151"; RePEc lo atribuye a Sabine Bernabè y
Calogero Carletto — **no verificado directamente el nombre del autor en el PDF**, solo el
título y contenido]. *Is There An Informal Employment Wage Penalty? Evidence from South
Africa*. IZA Discussion Paper No. 3151 (2007).
URL abierta: https://docs.iza.org/dp3151.pdf. Acceso: abierto. Verificado: **sí** (contenido;
autoría pendiente de confirmar, ver Descartadas).
Cita textual (`raw/iza_informal_penalty.txt`): "we find that there is a gross wage penalty of
a little over 18 per cent for working in the informal sector. However, once we reduce our
sample to a group for which we can reasonably calculate earnings net of taxes and control for
time invariant unobservables the wage penalty disappears."
Qué dice: evidencia de Sudáfrica (no Perú) de que la penalidad de informalidad puede ser un
artefacto de impuestos/heterogeneidad no observada — sustento directo de "resultados mixtos"
que pide el brief. Se usa solo como contraste metodológico, no como cifra para Perú.

**11. `chaman2025`** — Chaman Alvarez, J. F. (2025). "Analyzing wage gaps between male and
female workers in Peru: a novel decomposition methodology and case study". *Monthly Labor
Review*, agosto 2025, U.S. Bureau of Labor Statistics.
URL: https://www.bls.gov/opub/mlr/2025/article/analyzing-wage-gaps-between-male-and-female-workers-in-peru-a-novel-decomposition-methodology-and-case-study.htm.
Acceso: abierto (sitio .gov), pero bloquea peticiones automatizadas (curl y el snapshot de
Wayback Machine solo devuelven el shell JS, sin el cuerpo del artículo). Verificado: **no**
(contenido). Metadatos verificados: sí (autor, título, revista y fecha confirmados por
WebFetch y por la búsqueda). No pude obtener una cita textual con cifras; no reporto ningún
número de este artículo.

## B. Cruces con la app

1. **Male vs female +43.4% (E6, condicional, WLS)** → Ñopo (2008) encuentra una brecha de
   género en Perú (1986-2000) de 45%, de la cual 28 puntos quedan sin explicar por
   características observables `[nopo2008]`; Ñopo, Atal y Winder (2009) sitúan a los países de
   ALC entre 9-27% de prima masculina no explicada `[nopo_atal_winder2009]`; Blau y Kahn (2017)
   documentan que en EE. UU. el capital humano convencional ya casi no explica la brecha
   `[blaukahn2017]`. → **Consistente con la literatura** en magnitud y en el patrón "el capital
   humano no absorbe casi nada de la brecha" — el +43.4% de nuestro E6 es un coeficiente
   condicional (ya controla escolaridad, experiencia, horas, industria, categoría, tamaño de
   firma y región), así que es comparable al residual "no explicado" de estos estudios, no a
   la brecha bruta. Etiqueta: hallazgo propio, consistente con la literatura.

2. **Self-employed −49.6% (E6)** → Ñopo, Atal y Winder (2009): "the unexplained pay gap is
   higher among older, informal and self-employed workers" `[nopo_atal_winder2009]`; MTPE
   (2020) confirma un residual no explicado en la brecha formal/informal peruana
   `[esparta_rivera2020]`; IZA DP3151 muestra que en otro contexto (Sudáfrica) la penalidad de
   informalidad puede reducirse a cero al controlar heterogeneidad no observada y neto de
   impuestos `[iza3151_2007]`. → **Consistente en dirección, con lectura mixta en magnitud**: la
   literatura confirma que independientes/informales tienden a tener mayor brecha no
   explicada, pero también advierte que parte de esa brecha puede ser artefacto de variables no
   observadas (habilidad, selección) más que "penalidad pura". No podemos concluir que el
   −49.6% sea comparable número a número con ningún estudio específico de Perú — ninguno de
   los encontrados reporta exactamente esa cifra para independientes vs. asalariados peruanos.
   Etiqueta: hallazgo propio, lectura nuestra sobre la comparabilidad.

3. **Urban vs rural +32.3% (E6)** → No encontré una fuente académica abierta y verificada que
   descomponga específicamente la brecha urbano-rural peruana con Oaxaca-Blinder o matching
   (solo prensa: Gestion.pe/La República citando IPE/INEI, brecha de GÉNERO urbano 27.6% vs.
   rural 39.7% en 2024 — no es la misma brecha que mide nuestro modelo). → **No podemos
   concluir**: no hay referencia verificada con cita textual para esta comparación específica.
   Etiqueta: hallazgo propio, sin contraste verificado.

4. **Regional (Sierra Norte −31.1%, Sierra Centro −19.9% vs. Lima Metropolitana)** → mismo
   caso que el punto 3: los artículos de prensa mencionan el centralismo salarial de Lima, pero
   no logré verificar con texto primario abierto un estudio académico que descomponga la
   brecha regional peruana. Ñopo/Saavedra/Torero (2004) sí encuentran mayor brecha étnica en
   zonas rurales `[nopo_saavedra_torero2004]`, que es un proxy relacionado pero no idéntico
   (etnicidad, no región per se). → **No podemos concluir** con una referencia directa.

5. **Brecha por lengua materna/etnicidad (Fase 3, marco estructural)** → Ñopo, Saavedra y
   Torero (2004): usan lengua materna como una de varias dimensiones de un índice étnico
   multidimensional; encuentran brecha racial significativa entre asalariados pero no entre
   independientes `[nopo_saavedra_torero2004]`. Arpi Mayta y Arpi Quilca (2018), con
   Oaxaca-Blinder estándar y ENAHO 2006-2016, encuentran una brecha étnica de ingresos
   ~50% que se mantiene estable, cada vez más explicada por educación y menos por el residual
   `[arpi2018]`. Ñopo, Atal y Winder (2009) confirman que las brechas étnicas en ALC son
   mayores que las de género y más marcadas en zonas rurales `[nopo_atal_winder2009]`. → Marco
   útil para la propuesta de Fase 3 (4 grupos agregados castellano/quechua/aimara/amazónicas):
   la literatura peruana usa lengua materna como UN componente de un índice más amplio, no como
   variable única — al reducir a 4 grupos por lengua, el proyecto simplifica respecto a estos
   antecedentes, lo cual debe decirse explícitamente al presentar la propuesta. Etiqueta:
   lectura nuestra (framing), apoyada en literatura consistente.

6. **Penalidad de informalidad — literatura con resultados mixtos** → Confirmado: MTPE (2020)
   encuentra que la brecha formal/informal en Perú se ha ido reduciendo porque el ingreso
   informal crece más rápido, aunque sigue habiendo un residual no explicado
   `[esparta_rivera2020]`; IZA DP3151 muestra que, en otro país, la "penalidad" puede
   desaparecer al controlar impuestos y heterogeneidad no observada `[iza3151_2007]`. →
   Confirma explícitamente lo que pedía el brief: "hay literatura con resultados mixtos".
   Etiqueta: consistente con la literatura (mixta, tal como se anticipaba).

## C. Descartadas

- **Ñopo (2012), *New Century, Old Disparities*, "BM/BID"** (semilla): no encontré una edición
  de 2012 con ese título exacto. El estudio existe como IDB Working Paper 1131 / Research
  Dept. Publication 4640 (2009) y como IZA DP 5085 (2010), solo Banco Interamericano de
  Desarrollo — no Banco Mundial. Reemplazado por `nopo_atal_winder2009` con año y editorial
  corregidos.
- **Kolev (2015), "Ethnic wage gaps in Peru: What drives the particular disadvantage of
  indigenous women?", International Labour Review** (candidato nuevo, no semilla): muy
  relevante (brecha étnica de mujeres indígenas en Perú), pero solo pude acceder al
  abstract/paywall de Wiley (403 a peticiones automatizadas, sin versión de autor abierta que
  encontrara). Descartada por no poder verificar contenido con cita textual bajo la regla 4.
- **Chaman Alvarez (2025), BLS Monthly Labor Review**: candidato fuerte (brecha de género en
  Perú, metodología de descomposición nueva) pero el sitio bls.gov bloquea todo acceso
  automatizado (curl directo y vía Wayback Machine devuelven solo el armazón JS sin el cuerpo
  del artículo). Reportado en sección A como no verificado en contenido; no se usa ninguna
  cifra de él en la sección B.
- **Autoría de IZA DP3151**: no pude confirmar el nombre del autor dentro del propio PDF (la
  carátula solo dice "IZA DP No. 3151"); lo uso solo como evidencia metodológica de
  "resultados mixtos", no como cita con autor en el cuerpo de la app.
- Brecha urbano-rural y regional específica de Perú con metodología de descomposición: no
  encontré una fuente académica abierta verificable en el tiempo disponible (solo prensa
  citando IPE/INEI). Queda pendiente para una siguiente ronda si se necesita justificar esas
  cifras del modelo con literatura primaria.

## D. Errores de la semilla

1. **Ñopo (2012)** → año y editorial incorrectos. El trabajo relevante es Ñopo, Atal y Winder
   (2009/2010), publicado por el BID (no Banco Mundial/BID conjuntamente). Ver sección C.
2. El brief listaba "Ñopo (2008), REStat" correctamente, pero conviene anotar que la versión
   de acceso abierto que usé es la de IZA DP 981 (2004), previa a la publicación en revista
   (2008); el contenido y las cifras citadas son las mismas en ambas versiones según coteja el
   propio Ñopo en su bibliografía, pero no verifiqué la versión de revista misma (de pago).
3. La semilla no distinguía entre `nopo_saavedra_torero` (etnicidad/lengua materna, Lima
   urbana, 2004/2007) y `nopo2008`/`nopo_atal_winder2009` (género, matching, multi-país) — son
   tres papers distintos de Ñopo con coautores distintos; los trato como referencias separadas
   (7, 3 y 4) para no atribuir hallazgos de uno a otro.

## E. Refs existentes (propiedad de este eje)

**`yamada2007`** (única referencia axis-4 en `app/referencias.py`):
- `cita`/`url`: Yamada, G. (2007). *Retornos a la educación superior en el mercado laboral:
  ¿vale la pena el esfuerzo?* CIES / Universidad del Pacífico.
  URL: https://cies.org.pe/publicaciones/retornos-a-la-educacion-superior-en-el-mercado-laboral-vale-la-pena-el-esfuerzo/
  — la página carga correctamente y el título coincide exactamente (confirmado en
  `raw/yamada2007_page.html`). `acceso: "abierto"` es correcto: la página de CIES enlaza al
  PDF completo.
- `nota`: "Retornos por segmento en Perú: 12,5% anual para asalariados frente a 6,5% para
  independientes (2004)." → **No pude verificar esta cifra específica.** La página de
  aterrizaje de CIES no contiene los números 12,5%/6,5% ni las palabras "asalariados"/
  "independientes" en el texto que devuelve curl (solo metadatos/resumen genérico); las cifras
  deben estar en el PDF completo enlazado desde ahí, que no pude descargar dentro del tiempo de
  esta sesión (el enlace de descarga es dinámico/JS). **Verificado: no** para el contenido de
  la nota — recomiendo: (a) descargar el PDF real en una próxima ronda y confirmar 12,5%/6,5%,
  o (b) mientras tanto, marcar la nota como "cifra no reverificada en esta ronda" en vez de
  presentarla como dato cerrado.
- **Uso real en la app**: busqué `retorno_educacion()` (la función que arma esta nota con
  `{ref_yamada}`) en todo el repo y **no se llama desde ningún archivo fuera de
  `referencias.py`** — es código muerto hoy. La función `RETORNO_EDUCACION` existe pero no se
  renderiza en ninguna página. Recomendación: **corregir la cifra citada (o retirarla si no se
  puede reverificar) antes de conectarla a la UI**, ya que si se usa tal cual quedaría una cifra
  sin verificación textual directa, contra la regla 1 del brief.
- Veredicto: **corregir** (reverificar 12,5%/6,5% contra el PDF fuente antes de usar la nota
  en la interfaz; hoy no se usa, así que no hay urgencia de romper nada, pero tampoco debe
  activarse sin esa verificación).
