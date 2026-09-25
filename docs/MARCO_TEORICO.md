# Marco teórico — ENAHO 2025: ingresos e informalidad laboral en Perú

## English summary (≤150 words)

This document maps the app's two models — a WLS explanatory wage regression (E6) and a
Gradient Boosting informal-employment classifier — against seven literature axes: the
concept of informality, competing theoretical schools (dualist, structuralist, legalist,
voluntarist), Peruvian urban anthropology, wage-gap decompositions, human-capital /
Mincer-equation econometrics, ML in economics and targeting ethics, and Peruvian official
statistics. Every claim is labelled as *hallazgo propio* (our own finding), *consistente
con la literatura* (matches verified sources) or *lectura nuestra* (our interpretation,
not directly sourced). All findings are associational, never causal (cross-sectional WLS,
population-weighted). Sex, region, ethnicity and firm size are reported only as aggregated
structural gaps. The classifier flags job configurations, not people. The population is
restricted to employed people aged 14+ with positive labor income, which biases any gap
discussion toward the already-employed.

---

## Cómo leer este documento

Cada hallazgo de la app se compara con literatura verificada (fuente abierta, leída, cita
comprobada contra el texto crudo — detalle en `docs/MATRIZ_AFIRMACIONES.md`). Etiquetas,
exactamente tres: **hallazgo propio** (número o patrón del proyecto, sin fuente externa),
**consistente con la literatura** (coincide en dirección o magnitud con una fuente
verificada), **lectura nuestra** (interpretación sin respaldo textual directo).

Ningún resultado se describe como causa de nada («se asocia a», nunca «causa»). Sexo,
lengua materna, etnicidad y región se presentan como brechas estructurales agregadas, no
como rasgos de personas. El clasificador de informalidad **señala configuraciones de
empleo, no personas**. Toda brecha recuerda, donde corresponde, que la muestra está
restringida a ocupados de 14+ años con ingreso laboral positivo (quedan fuera desocupados,
inactivos y 6 500 trabajadores familiares no remunerados).

---

## Eje 1 — Qué es la informalidad y de dónde viene el concepto

### Qué dice la literatura

El término "sector informal" nace en 1971-1973 de una etnografía de Keith Hart sobre
migrantes frafra en Accra: la distinción clave no es "legal/ilegal" sino
"asalariado-regulado / autoempleo-esporádico" [hart1973]. Un año antes de que Hart
publicara, la misión de la OIT a Kenia ya usaba el término en un informe oficial, y
constató algo que suele olvidarse: buena parte del sector informal keniano era
"económicamente eficiente y rentable", no marginal [oit1972kenya]. Chen (2012) traza el
puente entre ese origen etnográfico y el uso estadístico actual: distingue **sector
informal** (características de la empresa, 15.ª CIET 1993) de **empleo informal**
(características del puesto de trabajo, 17.ª CIET 2003) [chen2012].

La OIT aplica el criterio de empleo informal en la práctica así: para asalariados, si el
empleador aporta a la seguridad social; para independientes y empleadores, si la unidad
económica está registrada [oit2018_mujeres_hombres]. Ese criterio operacional es
exactamente el que usa este proyecto (independiente sin RUC, o asalariado sin aporte a
pensión) [oit_17ciet].

La 21.ª CIET (2023) amplía el marco conceptual a "todas las formas de trabajo", pero no
cambia el criterio operacional para asalariados e independientes que ya aplicaba la 17.ª
CIET — la regla de la app sigue vigente sin cambios por esa actualización.

### Dónde encajan los hallazgos de la app

La app usa el criterio de empleo informal (puesto de trabajo), no el de sector informal
(empresa) — es la elección correcta para medir informalidad de personas ocupadas, que es
lo que hace el proyecto. La informalidad reconstruida por la app (67,3 % ponderado, todos
los ocupados) frente al 70,2 % oficial de INEI 2025 es una comparación de medición, no de
definición: este eje no tiene literatura que diga si una brecha de ~3 puntos es "normal"
al simplificar la regla oficial (ver eje 7).

### Tabla

| Hallazgo de la app | Qué dice la literatura | Coincide/discrepa | Etiqueta | Refs |
|---|---|---|---|---|
| Regla operacional: independiente sin RUC / asalariado sin aporte a pensión | Es exactamente el criterio operacional de la OIT para clasificar empleo informal en la práctica | Coincide | consistente con la literatura | oit2018_mujeres_hombres, oit_17ciet |
| Uso del criterio "puesto de trabajo" (17.ª CIET) en vez de "empresa" (15.ª CIET) | Es la distinción central que hace Chen (2012) y que reafirma la 21.ª CIET (2023) | Coincide | consistente con la literatura | chen2012, oit_17ciet |
| Informalidad reconstruida 67,3 % vs. INEI oficial 70,2 % (2025) | Sin literatura de este eje que evalúe la brecha de medición | No podemos concluir | lectura nuestra | — |
| Framing de "informal" en la app (contexto general, no cifra) | La literatura fundacional (Hart 1973, misión OIT a Kenia 1972) niega explícitamente que "informal" equivalga a "improductivo/residual" | Coincide (matiz) | consistente con la literatura | hart1973, oit1972kenya, chen2012 |

---

## Eje 2 — Teorías en competencia sobre la informalidad

Chen (2012) nombra y define las cuatro escuelas que organizan el debate desde los años 50
[chen2012]. Se presentan como cuatro bloques compactos, cada uno con lo que dicen
nuestros datos — este bloque está pensado para volverse tarjetas en la app.

### Dualista

**Qué dice.** Dos sectores segregados: uno moderno/capitalista con oferta ilimitada de
trabajo desde el sector tradicional [lewis1954, vía cita secundaria en
laportashleifer2014], y uno de subsistencia que absorbe el excedente. La migración
rural-urbana responde a diferenciales de salario esperado [harristodaro1970, cita
secundaria]. Tokman (1978) formaliza la relación informal-formal en esta tradición
[tokman1978]. La Porta y Shleifer (2014) concluyen que el modelo dual explica mejor la
evidencia de firmas informales que la lectura legalista o voluntarista pura
[laportashleifer2014].

**Qué dicen nuestros datos.** Escolaridad (OR 0,82 por año) y zona urbana (OR 0,56)
reducen la probabilidad de informalidad — compatible con fronteras de capital humano y
ubicación entre sectores [laportashleifer2014]. Los 6 500 trabajadores familiares no
remunerados excluidos (ingreso = 0) son el segmento más cercano al "excedente sin
remuneración de mercado" de Lewis; su exclusión implica que el proyecto no dice nada sobre
ese extremo.

### Estructuralista

**Qué dice.** La informalidad no es un sector aparte sino unidades subordinadas
(microempresas) que reducen costos a las firmas capitalistas grandes por subcontratación
[chen2012, portescastellsbenton1989].

**Qué dicen nuestros datos.** La penalidad de firmas pequeñas (≤20 personas: −33,4 % de
ingreso; OR 16,7 de ser informal) es compatible con subordinación económica, pero el
proyecto no observa relaciones de subcontratación entre firmas — no distingue
"subordinación estructural" de otras explicaciones (ver Ulyssea 2020 abajo).

### Legalista

**Qué dice.** De Soto (1989): la informalidad es respuesta racional al costo legal de
formalizarse; los micro-empresarios informales formalizarían si el trámite fuera barato y
los derechos de propiedad, accesibles [desoto1989, vía loayza2008 y perry2007].

**Qué dicen nuestros datos.** El proyecto no mide costo ni trámites de formalización — no
puede poner a prueba la hipótesis legalista central. La brecha positiva de empleadores
(+34,1 %) es compatible con una lectura de "capa superior" emprendedora análoga a De Soto
y Maloney, pero no confirma ni refuta el mecanismo.

### Voluntarista

**Qué dice.** Maloney (2004) lee buena parte del sector informal latinoamericano como
microempresa no regulada elegida voluntariamente, análoga a la pequeña empresa formal de
países ricos [maloney2004]. Günther y Launov, con un modelo de mezcla finita, muestran que
dentro de los independientes coexisten un régimen de "último recurso" (segmentación) y uno
de "ventaja comparativa" (elección voluntaria) [guntherlaunov2012].

**Qué dicen nuestros datos.** La penalidad de −49,6 % para independientes es compatible
con ambas lecturas a la vez: la app no tiene variables de preferencias, activos ni
historia laboral para separar los dos regímenes. No podemos concluir cuál domina.

### Sobre el debate en general

Ulyssea (2020), la revisión más reciente del debate, advierte que las brechas salariales
por sí solas **no bastan para probar segmentación**: la segmentación hipotética tiene poco
contenido empírico verificable solo con brechas de ingreso [ulyssea2020]. También
documenta que la informalidad (extensiva e intensiva) decrece con el tamaño de la firma en
todos los países estudiados — exactamente el patrón que muestra la app (firma ≤20 vs. >500:
−33,4 % de ingreso, OR 16,7 de informalidad).

### Tabla

| Hallazgo de la app | Qué dice la literatura | Coincide/discrepa | Etiqueta | Refs |
|---|---|---|---|---|
| Independiente vs. asalariado: −49,6 % (E6); OR 5,2 (clasificador) | Compatible con lectura dualista/estructuralista y voluntarista a la vez; Günther-Launov muestran que ambos regímenes coexisten | No podemos concluir cuál domina | lectura nuestra | chen2012, perry2007, guntherlaunov2012, maloney2004 |
| Empleador: +34,1 % | Compatible con la lectura legalista/voluntarista de "capa superior" emprendedora | No podemos concluir el mecanismo | lectura nuestra | maloney2004, desoto1989 (vía loayza2008) |
| Firma ≤20 vs. >500: −33,4 % (E6); OR 16,7 (clasificador) | La informalidad decrece con el tamaño de firma en todos los países que estudia Ulyssea (2020) | Coincide en dirección | consistente con la literatura | ulyssea2020, perry2007 |
| Escolaridad OR 0,82; urbano OR 0,56 (clasificador) | Coincide con la frontera dualista de capital humano y ubicación; La Porta-Shleifer encuentran gerentes menos educados en firmas informales | Coincide | consistente con la literatura | laportashleifer2014 |
| 6 500 trabajadores familiares no remunerados excluidos | Es el segmento más próximo al "excedente sin remuneración de mercado" del modelo dualista original | Limitación de muestra, no hallazgo sobre mecanismo | lectura nuestra | lewis1954 (cita secundaria) |
| Sierra Norte −31,1 %; sexo +43,4 % (E6); mujer/rural en el clasificador | Ninguna escuela del eje predice directamente sexo o región — son controles de composición | No podemos concluir | lectura nuestra | — |
| Costo de formalizar (hipótesis legalista) | El proyecto no mide costo/trámite de formalización | No podemos concluir | lectura nuestra | desoto1989 |

---

## Eje 3 — Antropología y sociología del Perú urbano

### Qué dice la literatura

Matos Mar (1984) documenta el "desborde popular": la migración andina masiva a Lima ante
un Estado que no absorbe la nueva población económicamente activa genera lo que llama el
"circuito popular contestatario" — la economía informal —, y describe cómo la vida social
de la ciudad organiza estrategias de supervivencia en torno a vínculos familiares
extendidos [matosmar1984]. Golte y Adams (1987) muestran, con estudio de campo en doce
comunidades de origen de migrantes, que el reclutamiento laboral y la formación de
talleres urbanos se organiza por redes de parentesco y paisanaje, no por mercado abierto
puro [golteadams1987].

Kamichi (2023), con datos secundarios de INEI, ofrece evidencia contra el relato de que la
informalidad es sobre todo evasión deliberada: más del 80 % de las unidades informales no
se registra porque "no lo considera necesario" o "el negocio es pequeño"; menos del 2 %
cita trámites complicados o carga tributaria [kamichi2023]. Rodríguez (2011), con ENAHO
2008-2009 y métodos de matching, encuentra brechas de ingreso entre asalariados y
autoempleados de 22 % a 64 % según el método, consistentes con segmentación del mercado,
no solo con diferencias de capital humano observable [rodriguez2011].

### Dónde encajan los hallazgos de la app

La brecha de −49,6 % de independientes cae dentro del rango 33-64 % que documenta
Rodríguez (2011) con matching sobre otra muestra y otro año. El framing de "informalidad
como fenómeno estructural, no evasión" que usa la app coincide con lo que documenta
Kamichi (2023). La brecha regional (Sierra Norte −31,1 %, Sierra Centro −19,9 % frente a
Lima Metropolitana) tiene una lectura histórica en Matos Mar y Golte-Adams —centralización
productiva en Lima y migración andina masiva—, pero esos libros son de los años 80, sobre
Lima, y no traen cifras comparables al corte transversal 2025 del proyecto: sirven como
lectura del porqué histórico, no como validación del número actual.

### Tabla

| Hallazgo de la app | Qué dice la literatura | Coincide/discrepa | Etiqueta | Refs |
|---|---|---|---|---|
| Self-empleado −49,6 % (E6); OR 5,2 (clasificador) | Rodríguez (2011): brechas de 22-64 % asalariado/autoempleado, atribuidas a segmentación | Coincide en dirección y orden de magnitud | consistente con la literatura | rodriguez2011 |
| Framing "informalidad no es solo evasión" | Kamichi (2023): >80 % de informales no se registra por "no lo considera necesario" o "negocio pequeño"; <2 % por trámites/impuestos | Coincide | consistente con la literatura | kamichi2023 |
| Regional: Sierra Norte −31,1 %, Sierra Centro −19,9 % vs. Lima; urbano +32,3 % | Matos Mar y Golte-Adams documentan el origen histórico de la centralización en Lima y la migración andina, sin cifras comparables al corte actual | No podemos concluir el número; sí el porqué histórico | lectura nuestra | matosmar1984, golteadams1987 |
| Categoría ocupacional / trabajadores familiares no remunerados excluidos | Golte y Adams: el reclutamiento y los talleres se organizan por parentesco y paisanaje, no mercado abierto | No podemos concluir vínculo causal con el diseño muestral | lectura nuestra | golteadams1987 |
| Firma ≤20 vs. >500: −33,4 % | Ninguna de las cuatro fuentes de este eje mide tamaño de firma | No podemos concluir desde este eje | lectura nuestra | — |

---

## Eje 4 — Brechas salariales y descomposiciones

### Qué dice la literatura

Oaxaca (1973) y Blinder (1973) proponen el método canónico de descomposición de brechas
salariales en un componente explicado por características y un residual [oaxaca1973,
blinder1973 — metadatos verificados, contenido no verificable por escaneo sin capa de
texto]. Ñopo (2008), con matching no paramétrico sobre Perú 1986-2000, encuentra una
brecha de género bruta de 45 %, con 28 puntos porcentuales sin explicar por
características observables [nopo2008]. Ñopo, Atal y Winder (2009), en 18 países de
América Latina, encuentran una prima masculina no explicada de 9-27 % y señalan que **la
brecha no explicada es mayor entre trabajadores informales, independientes y de empresas
pequeñas** [nopo_atal_winder2009]. Blau y Kahn (2017) documentan que en EE. UU. el capital
humano convencional ya casi no explica la brecha de género: domina un residual que bajó de
0,341 a 0,197 log-puntos entre 1980 y 2010 [blaukahn2017]. Goldin (2014) atribuye el
último tramo de esa brecha a la prima que el mercado paga por disponibilidad horaria, no a
capital humano [goldin2014].

Para Perú, Ñopo, Saavedra y Torero (2004) encuentran brecha étnica/racial significativa
entre asalariados pero **no** entre independientes, con un índice multidimensional (lengua
materna, origen familiar, religión, migración, raza) [nopo_saavedra_torero2004]. Arpi y
Arpi (2018), con Oaxaca-Blinder estándar y ENAHO 2006-2016, encuentran brecha étnica de
ingresos ~50 % estable en el tiempo, cada vez más explicada por educación
[arpi2018]. El MTPE (2020) confirma un residual no explicado en la brecha formal/informal
peruana, que se reduce porque el ingreso informal crece más rápido que el formal
[esparta_rivera2020]. Un estudio para Sudáfrica (no Perú) muestra que la "penalidad de
informalidad" puede desaparecer al controlar heterogeneidad no observada y neto de
impuestos — evidencia de literatura mixta sobre esta penalidad [iza3151_2007].

### Dónde encajan los hallazgos de la app

El coeficiente condicional de género (+43,4 %, ya controlando escolaridad, experiencia,
horas, industria, categoría, tamaño de firma y región) es comparable al residual "no
explicado" de estos estudios, no a una brecha bruta — en ese sentido es consistente con el
patrón de que el capital humano convencional absorbe poco de la brecha de género. La
brecha de independientes (−49,6 %) es consistente en dirección con Ñopo-Atal-Winder (mayor
brecha no explicada entre informales/independientes/empresas pequeñas), pero ningún
estudio verificado reporta una cifra comparable número a número para Perú. No se encontró
literatura académica verificada que descomponga específicamente la brecha urbano-rural ni
la brecha regional peruana con Oaxaca-Blinder o matching — esos dos hallazgos de la app
quedan sin contraste directo.

Nota de selección: todas las brechas de este eje se calculan sobre ocupados con ingreso
positivo; no dicen nada sobre la brecha en la probabilidad de tener empleo remunerado.

### Tabla

| Hallazgo de la app | Qué dice la literatura | Coincide/discrepa | Etiqueta | Refs |
|---|---|---|---|---|
| Male vs. female +43,4 % (E6, condicional) | Ñopo (2008): 45 % bruto, 28 pp sin explicar (Perú 1986-2000); Ñopo-Atal-Winder: 9-27 % sin explicar en ALC; Blau-Kahn: capital humano no absorbe casi nada de la brecha | Consistente en magnitud y patrón | consistente con la literatura | nopo2008, nopo_atal_winder2009, blaukahn2017 |
| Self-employed −49,6 % (E6) | Ñopo-Atal-Winder: la brecha no explicada es mayor entre informales/independientes/empresas pequeñas; MTPE confirma residual formal/informal; evidencia sudafricana muestra que la penalidad puede ser artefacto de no observables | Consistente en dirección, mixta en mecanismo | lectura nuestra sobre comparabilidad | nopo_atal_winder2009, esparta_rivera2020, iza3151_2007 |
| Urban vs. rural +32,3 % (E6) | Sin fuente académica verificada que descomponga esta brecha específica en Perú | No podemos concluir | hallazgo propio | — |
| Regional (Sierra Norte −31,1 %, Sierra Centro −19,9 %) | Sin fuente académica verificada con descomposición regional peruana | No podemos concluir | hallazgo propio | — |
| Marco para lengua materna/etnicidad (Fase 3, propuesta) | Ñopo-Saavedra-Torero: brecha étnica en asalariados, no en independientes; Arpi-Arpi: brecha étnica ~50 % estable, cada vez más explicada por educación | Marco útil, con matiz metodológico | lectura nuestra | nopo_saavedra_torero2004, arpi2018 |

---

## Eje 5 — Capital humano y la ecuación de Mincer

### Qué dice la literatura

La ecuación minceriana canónica (escolaridad + experiencia + experiencia²) da R² = 0,285
en el ejercicio original de Mincer sobre datos de EE. UU.; al añadir semanas trabajadas
sube a 0,525, pero entonces ya no mide solo capital humano sino también oferta laboral
[mincer1974]. Card (1999), sobre la CPS 1994-96, reporta R² entre 0,247 (mujeres) y 0,328
(hombres) para la especificación minceriana estándar sobre log-salario por hora [card1999].
Ni Lemieux (2006) ni Heckman, Lochner y Todd (2006) reportan ningún R² en sus textos
completos — se buscó exhaustivamente y no aparece [lemieux2006, heckman2006]: son
referencias sobre forma funcional y sobre qué identifica cada especificación, no sobre
bondad de ajuste. Heckman, Lochner y Todd (2006) sí definen la experiencia potencial como
edad − años de educación − 6, exactamente la fórmula que usa la app, pero **no** afirman
que esa medida sobreestime la experiencia efectiva en trabajadores de baja educación — esa
frase no se encontró en el texto pese a búsqueda exhaustiva.

Psacharopoulos y Patrinos (2018), con 1 120 estimaciones en 139 países, reportan un retorno
privado global promedio de ~9 % anual por año de escolaridad, y 11,0 % en América Latina y
el Caribe [psacharopoulos2018]. Yamada (2007), con ENAHO 2004, encuentra retornos por
segmento en Perú: 12,5 % anual para asalariados frente a 6,5 % para independientes
[yamada2007].

### Dónde encajan los hallazgos de la app

El coeficiente de escolaridad de la app (+4,8 % por año, coeficiente condicional del WLS) es
menor que los retornos mincerianos simples de Yamada (6,5-12,5 %) y de Psacharopoulos y
Patrinos (9-11 %). Que un coeficiente con más controles (ocupación, tamaño de firma,
región) sea menor que un retorno bruto tipo Mincer es consistente con la dirección
esperada, pero ninguna fuente verificada de este eje afirma explícitamente que agregar
esos controles reduzca el retorno a la escolaridad — es una lectura nuestra, no una cita.
El R² de la especificación logarítmica de la app (0,27) cae dentro del rango 0,247-0,328
de Card y cerca del 0,285 de Mincer — consistente con la literatura. La autocorrección que
ya hizo la app sobre Lemieux y Heckman (ninguno de los dos reporta R²) queda reverificada.
La atribución a Heckman, Lochner y Todd (2006) de que la experiencia potencial sobreestima
la experiencia efectiva en baja educación **no tiene respaldo textual** en la fuente citada
— es plausible como lectura propia (edad−escolaridad−6 asume entrada continua al mercado
laboral; en trayectorias con interrupciones, comunes en baja educación e informalidad, la
experiencia efectiva sería menor que la potencial), pero no debe presentarse como algo que
el paper dice.

### Tabla

| Hallazgo de la app | Qué dice la literatura | Coincide/discrepa | Etiqueta | Refs |
|---|---|---|---|---|
| +4,8 % por año de escolaridad (E6, condicional) | Yamada: 6,5-12,5 %; Psacharopoulos-Patrinos: 9-11 % (retornos brutos, sin controles de ocupación/firma) | Menor, en la dirección esperada al agregar controles, pero sin fuente que lo afirme explícitamente | lectura nuestra | psacharopoulos2018, yamada2007 |
| R² de la especificación logarítmica (0,27) | Mincer: 0,285; Card: 0,247-0,328 | Dentro del rango | consistente con la literatura | mincer1974, card1999 |
| "Ningún R² supera 0,4-0,5" (autocorrección ya vigente en la app) | Ni Lemieux ni Heckman et al. reportan R² en el texto completo | Confirmado | consistente con la literatura | lemieux2006, heckman2006 |
| "Experiencia potencial sobreestima la efectiva en baja educación" (atribuida a Heckman et al. 2006) | La fórmula sí está en la fuente; el enunciado de sobreestimación, no | No respaldado en la fuente citada | lectura nuestra (corregir atribución) | heckman2006 |

---

## Eje 6 — Machine learning en economía y ética del targeting

### Qué dice la literatura

Breiman (2001) contrapone la "cultura del modelado de datos" (se asume un proceso
generador y se interpretan parámetros) con la "cultura algorítmica" (el proceso es una
caja negra, se optimiza precisión predictiva) [breiman2001]. Shmueli (2010) formaliza que
un modelo con alto poder explicativo no garantiza poder predictivo, y viceversa: son
objetivos de modelado distintos [shmueli2010]. Es exactamente el marco que separa el E6
(explicativo) del E9 (predictivo) en este proyecto.

Kleinberg, Ludwig, Mullainathan y Obermeyer (2015) distinguen problemas de política
pública que son, en el fondo, problemas de predicción (¿quién necesita ayuda?) de los que
son de inferencia causal (¿qué intervención cambia el resultado?), y sitúan el machine
learning como herramienta natural para los primeros [kleinberg2015]. Mullainathan y Spiess
(2017) hacen la misma distinción desde la econometría aplicada [mullainathan2017]. Barocas,
Hardt y Narayanan explican por qué retirar un atributo protegido (p. ej. sexo) de un
clasificador casi nunca "arregla" la equidad: otras variables actúan como proxies o
codificaciones redundantes del atributo protegido y suelen ser genuinamente relevantes
para la predicción [barocas2023]. Aiken et al. (2022), con datos de telefonía móvil en
Togo, muestran un caso real de ML para focalización de ayuda de emergencia, con sus
trade-offs de equidad medidos empíricamente, no solo discutidos en abstracto [aiken2022].

### Dónde encajan los hallazgos de la app

La separación explícita entre E9 (predictivo) y E6 (explicativo) coincide con el marco de
Breiman y Shmueli. El encuadre de la app — "el clasificador flags job configurations, not
people", herramienta de focalización y no de predicción individual ni de inferencia
causal — coincide con Kleinberg et al. y Mullainathan-Spiess, aunque ninguno de los dos
habla específicamente de informalidad laboral ni de Perú: el marco es general, no
específico del dominio.

La ablación de sexo del clasificador (PR-AUC cae de 0,9626 a 0,9618; diferencia real,
t = 6,26, p = 0,003, pero de magnitud irrelevante; las tasas de precisión/recall por sexo
casi no cambian) coincide con el mecanismo que describe Barocas, Hardt y Narayanan: otras
variables (tamaño de firma, categoría ocupacional, horas) son proxies correlacionados con
sexo, así que el modelo recupera casi toda la información al quitar el atributo protegido.
La magnitud exacta de la caída y que las tasas de error por sexo apenas se muevan es
hallazgo propio; el *por qué* ocurre viene de la literatura.

El hecho de que la ablación de tamaño de firma y categoría ocupacional (dos variables muy
importantes) deje el PR-AUC casi intacto (0,96 → 0,94) es un hallazgo propio sobre
robustez del modelo, sin comparación directa disponible en este eje — Aiken et al. (2022)
sirve como paralelo aplicado (ML de focalización con trade-offs de equidad medidos), no
como validación numérica.

### Tabla

| Hallazgo de la app | Qué dice la literatura | Coincide/discrepa | Etiqueta | Refs |
|---|---|---|---|---|
| Separación E9 predictivo / E6 explicativo | Breiman (2001) y Shmueli (2010) formalizan esta distinción como objetivos de modelado incompatibles en general | Coincide | consistente con la literatura | breiman2001, shmueli2010 |
| "Herramienta de focalización, no causal, no individual" | Kleinberg et al. (2015) y Mullainathan-Spiess (2017) sitúan el targeting de política pública como problema de predicción, distinto de inferencia causal | Coincide (marco general, no específico de informalidad) | consistente con la literatura | kleinberg2015, mullainathan2017 |
| PR-AUC ≈ 0,96; ablación de firma+categoría deja PR-AUC ≈ 0,94 | Sin literatura de este eje sobre esta forma específica de robustez | No podemos concluir | hallazgo propio | — |
| Ablación de sexo: PR-AUC 0,9626→0,9618, tasas por sexo casi sin cambio | Barocas, Hardt y Narayanan: quitar el atributo protegido no arregla nada porque otras variables son proxies redundantes | Coincide el mecanismo | consistente con la literatura | barocas2023 |
| Sensibilidad de la prima urbana al ingreso en especie (54,6 %→52,0 %) | Sin literatura de este eje que lo cubra | No podemos concluir | hallazgo propio | — |

---

## Eje 7 — Contexto institucional peruano (cifras oficiales de INEI)

### Qué dice la literatura

El informe técnico de INEI de febrero de 2026 (EPEN, año de referencia 2025) reporta:
informalidad nacional 70,2 %; urbano 64,5 %, rural 94,8 %; por tamaño de empresa, 88,6 %
en empresas de 1 a 10 trabajadores, 44,0 % en las de 11 a 50, y 15,6 % en las de 51 o más
[inei_empleo_2025]. Es una fuente distinta de la que hoy cita `app/referencias.py` como
`inei_informal`: esa publicación (Cuenta Satélite de la Economía Informal, editada en
diciembre de 2025) mide con datos de EPEN "al 2024", no 2025, y reporta 70,9 % nacional,
65,4 % urbano, 94,5 % rural, con tramos de empresa distintos (1-5/6-10/11-30/31+)
[inei_informal].

### Dónde encajan los hallazgos de la app

Las cifras 2025 que hoy usa la app (70,2 % nacional; 64,5 % urbano; 94,8 % rural; 88,6 % y
15,6 % por tamaño de empresa) están **correctamente citadas en valor**, pero la fuente que
las respalda debería ser el informe técnico EPEN 2025, no la Cuenta Satélite (que mide
2024 y da números distintos — ver `docs/PROPUESTA_REFERENCIAS.md` para el detalle de la
corrección). La comparación entre la informalidad reconstruida por la app (67,3 % nacional
ponderado) y el 70,2 % oficial cruza dos encuestas distintas (ENAHO vs. EPEN) con
definiciones operativas ligeramente distintas: la app atribuye la brecha de ~3 puntos a la
afiliación autofinanciada a pensiones, lectura razonable pero no verificada contra una
fuente que aísle específicamente ese efecto. El gradiente de informalidad por tamaño de
firma que produce el modelo va en el mismo sentido que el oficial (más informalidad en
firmas pequeñas), aunque los tramos de tamaño no son comparables uno a uno.

### Tabla

| Hallazgo de la app | Qué dice la literatura | Coincide/discrepa | Etiqueta | Refs |
|---|---|---|---|---|
| Informalidad reconstruida 67,3 % vs. oficial 70,2 % (2025) | inei_empleo_2025: 70,2 % nacional EPEN 2025 | Encuestas distintas (ENAHO vs. EPEN); brecha de ~3 pts sin fuente que aísle la causa | hallazgo propio | inei_empleo_2025 |
| Urbano 64,5 % / rural 94,8 % oficial (tabla del README) | Coincide dígito por dígito con inei_empleo_2025, Gráfico 1.15 | Coincide exactamente | consistente con la literatura | inei_empleo_2025 |
| "INEI reporta 88,6 % (1-10 trab.) y 15,6 % (>50)" | Coincide dígito por dígito con inei_empleo_2025, Cuadro 1.22 | Coincide exactamente el dato; la cita `[8]` del README apunta a la referencia equivocada | corregir cita, no el dato | inei_empleo_2025 |

---

## Qué no podemos afirmar

- **Causalidad.** Los coeficientes de E6 son asociaciones condicionales de una regresión
  de corte transversal ponderada por diseño muestral (WLS + FAC500A, errores HC3). Ninguna
  cifra implica que una característica "cause" mayor o menor ingreso.
- **Selección.** Toda brecha (género, urbano-rural, región, categoría ocupacional) se
  calcula sobre las 47 632 personas ocupadas de 14+ años con ingreso positivo. Quedan
  fuera desocupados, inactivos y 6 500 trabajadores familiares no remunerados — el modelo
  no dice nada sobre la brecha en la probabilidad de estar empleado.
- **Individuos.** El clasificador señala configuraciones de empleo (tamaño de firma,
  categoría ocupacional, escolaridad, ubicación), no personas; no es predicción individual.
- **Comparabilidad numérica exacta.** Ninguna cifra del proyecto es "la misma" que una
  cifra citada: otras muestras, años y métodos. Las coincidencias "consistente con la
  literatura" son de dirección y orden de magnitud, no de igualdad.
- **Mecanismo de la informalidad.** No se puede distinguir, con los datos disponibles,
  entre las lecturas dualista, estructuralista, legalista y voluntarista de la brecha de
  independientes/asalariados: no hay variables de preferencias, activos, historia laboral
  ni costo de formalización.
- **Brecha étnica/lingüística.** No está modelada en la versión actual (Fase 3,
  pendiente); la literatura peruana usa lengua materna como un componente de un índice más
  amplio, no como variable única — la simplificación a 4 grupos que propone Fase 3 debe
  declararse como tal frente a esos antecedentes.

## Referencias (APA)

- Aiken, E., Bellue, S., Karlan, D., Udry, C., & Blumenstock, J. E. (2022). Machine
  learning and phone data can improve targeting of humanitarian aid. *Nature*, 603,
  864–870. https://doi.org/10.1038/s41586-022-04484-9 — acceso: abierto (PMC).
- Arpi Mayta, R., & Arpi Quilca, L. (2018). Desigualdad del ingreso laboral y nivel
  educativo entre grupos étnicos en el Perú. *COMUNI@CCIÓN*, 9(1), 56–67.
  https://www.redalyc.org/journal/4498/449856234006/449856234006.pdf — acceso: abierto.
- Barocas, S., Hardt, M., & Narayanan, A. (2023). *Fairness and Machine Learning:
  Limitations and Opportunities*. MIT Press. https://fairmlbook.org/ — acceso: abierto.
- Blau, F. D., & Kahn, L. M. (2017). The gender wage gap: Extent, trends, and
  explanations. *Journal of Economic Literature*, 55(3), 789–865.
  https://doi.org/10.1257/jel.20160995 — acceso: abierto (NBER WP 21913).
- Blinder, A. S. (1973). Wage discrimination: Reduced form and structural estimates.
  *The Journal of Human Resources*, 8(4), 436–455. https://doi.org/10.2307/144855 —
  acceso: pago (metadatos verificados vía Ñopo 2008; contenido no verificado).
- Breiman, L. (2001). Statistical modeling: The two cultures. *Statistical Science*,
  16(3), 199–215. https://doi.org/10.1214/ss/1009213726 — acceso: abierto (copia
  académica).
- Card, D. (1999). The causal effect of education on earnings. En O. Ashenfelter & D.
  Card (eds.), *Handbook of Labor Economics*, vol. 3A, cap. 30 (pp. 1801–1863). Elsevier.
  https://eml.berkeley.edu/~cle/wp/wp2.pdf — acceso: abierto.
- Chen, M. A. (2012). *The Informal Economy: Definitions, Theories and Policies* (WIEGO
  Working Paper No. 1). WIEGO. https://www.wiego.org/wp-content/uploads/2019/09/
  Chen_WIEGO_WP1.pdf — acceso: abierto.
- De Soto, H. (1989). *The Other Path*. Basic Books. (Ed. española: *El otro sendero*,
  1986.) — acceso: pago; metadatos verificados vía Loayza (2008), Perry et al. (2007) y
  Chen (2012); contenido no verificado directamente.
- Golte, J., & Adams, N. (1987/1990). *Los caballos de Troya de los invasores:
  estrategias campesinas en la conquista de la gran Lima* (2.ª ed.). IEP.
  https://repositorio.iep.org.pe/items/8e0e0c4c-28c9-4c7a-b80d-fd7106d0271b — acceso:
  abierto.
- Goldin, C. (2014). A grand gender convergence: Its last chapter. *American Economic
  Review*, 104(4), 1091–1119. https://doi.org/10.1257/aer.104.4.1091 — acceso: abierto
  (Harvard Scholar).
- Günther, I., & Launov, A. (2012). Informal employment in developing countries:
  Opportunity or last resort? *Journal of Development Economics*, 97(1), 88–98.
  https://doi.org/10.1016/j.jdeveco.2011.01.001 — acceso: pago (contenido verificado
  sobre el preprint IZA DP 2349, 2006, abierto en https://docs.iza.org/dp2349.pdf).
- Harris, J. R., & Todaro, M. P. (1970). Migration, unemployment and development: A
  two-sector analysis. *American Economic Review*, 60(1), 126–142. — acceso: pago;
  contenido no verificado directamente (solo referencia secundaria).
- Hart, K. (1973). Informal income opportunities and urban employment in Ghana. *The
  Journal of Modern African Studies*, 11(1), 61–89. https://doi.org/10.1017/
  S0022278X00008089 — acceso: abierto (copia académica).
- Heckman, J., Lochner, L., & Todd, P. (2006). Earnings functions, rates of return and
  treatment effects: The Mincer equation and beyond. *Handbook of the Economics of
  Education*, vol. 1, cap. 7 (pp. 307–458). Elsevier. https://www.nber.org/papers/w11544
  — acceso: abierto (NBER WP 11544).
- Kamichi Miyashiro, M. J. (2023). La realidad de la informalidad en el Perú previo a su
  bicentenario. *Desde el Sur*, 15(1), e0013. https://doi.org/10.21142/des-1501-2023-0013
  — acceso: abierto (SciELO Perú).
- Kleinberg, J., Ludwig, J., Mullainathan, S., & Obermeyer, Z. (2015). Prediction policy
  problems. *American Economic Review: Papers & Proceedings*, 105(5), 491–495.
  https://www.nber.org/papers/w20870 — acceso: abierto (NBER WP 20870).
- La Porta, R., & Shleifer, A. (2014). Informality and development. *Journal of Economic
  Perspectives*, 28(3), 109–126. https://www.nber.org/system/files/working_papers/w20205/
  w20205.pdf — acceso: abierto (NBER WP 20205).
- Levy, S. (2008). *Good Intentions, Bad Outcomes: Social Policy, Informality, and
  Economic Growth in Mexico*. Brookings Institution. — acceso: pago; metadatos
  verificados vía cita secundaria en La Porta-Shleifer (2014); contenido no verificado.
- Lewis, W. A. (1954). Economic development with unlimited supplies of labour. *The
  Manchester School*, 22(2), 139–191. https://doi.org/10.1111/j.1467-9957.1954.tb00021.x
  — acceso: pago; metadatos verificados vía cita secundaria; contenido no verificado.
- Maloney, W. F. (2004). Informality revisited. *World Development*, 32(7), 1159–1178.
  https://doi.org/10.1016/j.worlddev.2004.01.008 — acceso: abierto (https://www.ilo.org/
  media/153361/download).
- Matos Mar, J. (1984/1985). *Desborde popular y crisis del Estado: el nuevo rostro del
  Perú en la década de 1980* (2.ª ed.). IEP. https://repositorio.iep.org.pe/items/
  a89c507d-c435-4cdb-b436-e70e73dd67f2 — acceso: abierto.
- Mincer, J. (1974). *Schooling, Experience, and Earnings*. NBER/Columbia University
  Press. https://www.nber.org/system/files/chapters/c1767/c1767.pdf — acceso: abierto.
- Mullainathan, S., & Spiess, J. (2017). Machine learning: An applied econometric
  approach. *Journal of Economic Perspectives*, 31(2), 87–106.
  https://doi.org/10.1257/jep.31.2.87 — acceso: abierto.
- Ñopo, H. (2008). Matching as a tool to decompose wage gaps. *The Review of Economics
  and Statistics*, 90(2), 290–299. https://doi.org/10.1162/rest.90.2.290 — acceso:
  abierto (IZA DP 981).
- Ñopo, H., Atal, J. P., & Winder, N. (2009/2010). *New Century, Old Disparities: Gender
  and Ethnic Wage Gaps in Latin America* (IDB Working Paper 1131; IZA DP 5085).
  https://docs.iza.org/dp5085.pdf — acceso: abierto.
- Ñopo, H., Saavedra, J., & Torero, M. (2004/2007). Ethnicity and earnings in a
  mixed-race labor market. *Economic Development and Cultural Change*, 55(4), 709–734.
  https://docs.iza.org/dp980.pdf — acceso: abierto (IZA DP 980).
- Oaxaca, R. L. (1973). Male-female wage differentials in urban labor markets.
  *International Economic Review*, 14(3), 693–709. — acceso: abierto en PDF, pero sin
  capa de texto (contenido no verificable en esta ronda).
- OIT / International Labour Office. (1972). *Employment, Incomes and Equality: A
  Strategy for Increasing Productive Employment in Kenya*. ILO.
  https://webapps.ilo.org/public/libdoc/ilo/1972/72B09_608_engl.pdf — acceso: abierto.
- OIT. (2003). *Guidelines Concerning a Statistical Definition of Informal Employment*
  (17.ª CIET), revisada por la resolución de la 21.ª CIET (2023).
  https://www.ilo.org/resource/guidelines-concerning-statistical-definition-informal-
  employment-0 — acceso: abierto.
- Bonnet, F., Leung, V., & Chacaltana, J. (2018). *Women and Men in the Informal
  Economy: A Statistical Picture* (3.ª ed.). OIT. https://www.ilo.org/sites/default/
  files/2024-04/Women_men_informal_economy_statistical_picture.pdf — acceso: abierto.
- Perry, G. E., Maloney, W. F., Arias, O. S., Fajnzylber, P., Mason, A. D., &
  Saavedra-Chanduvi, J. (2007). *Informality: Exit and Exclusion*. Banco Mundial.
  https://documents1.worldbank.org/curated/en/326611468163756420/txt/
  400080Informal101OFFICIAL0USE0ONLY1.pdf — acceso: abierto.
- Portes, A., Castells, M., & Benton, L. A. (eds.). (1989). *The Informal Economy:
  Studies in Advanced and Less Developed Countries*. Johns Hopkins University Press. —
  acceso: pago; metadatos verificados vía Chen (2012); contenido no verificado.
  directamente.
- Psacharopoulos, G., & Patrinos, H. A. (2018). *Returns to Investment in Education: A
  Decennial Review of the Global Literature* (Policy Research Working Paper 8402).
  Banco Mundial. https://documents1.worldbank.org/curated/en/442521523465644318/pdf/
  WPS8402.pdf — acceso: abierto.
- Rodríguez, J. S. (2011). *Brechas de ingresos laborales entre asalariados y
  autoempleados en el Perú* (Documento de Trabajo 318). PUCP.
  http://files.pucp.edu.pe/departamento/economia/DDD318.pdf — acceso: abierto.
- Saito, T., & Rehmsmeier, M. (2015). The precision-recall plot is more informative than
  the ROC plot when evaluating binary classifiers on imbalanced datasets. *PLOS ONE*,
  10(3), e0118432. https://doi.org/10.1371/journal.pone.0118432 — acceso: abierto.
- Shmueli, G. (2010). To explain or to predict? *Statistical Science*, 25(3), 289–310.
  https://doi.org/10.1214/10-STS330 — acceso: abierto.
- Sohnesen, T. P., & Stender, N. (2016). *Is Random Forest a Superior Methodology for
  Predicting Poverty? An Empirical Assessment* (Policy Research Working Paper 7612).
  Banco Mundial. https://ideas.repec.org/p/wbk/wbrwps/7612.html — acceso: abierto.
- Tokman, V. (1978). An exploration into the nature of the informal-formal sector
  relationship. *World Development*, 6(9-10). — acceso: pago; metadato verificado vía
  Chen (2012); contenido no verificado.
- Ulyssea, G. (2020). Informality: Causes and consequences for development. *Annual
  Review of Economics*, 12, 525–546. https://doi.org/10.1146/annurev-
  economics-082119-121914 — acceso: abierto (copia del autor).
- Esparta Polanco, D., & Rivera Reyna, G. (2020). *Brechas salariales entre el empleo
  formal e informal* (Boletín Informativo Laboral N.º 104). MTPE.
  https://cdn.www.gob.pe/uploads/document/file/1297314/Art%202%20-%20Brechas%20
  salarial.pdf — acceso: abierto.
- INEI. (2026). *Perú: Comportamiento de los Indicadores del Mercado Laboral a Nivel
  Nacional y en 27 Ciudades. Enero-Diciembre 2025 | Cuarto Trimestre 2025*. Informe
  Técnico, febrero 2026. https://www.gob.pe/institucion/inei/informes-publicaciones/
  7739601 — acceso: abierto.
- INEI. (2025). *Producción y Empleo Informal en el Perú: Cuenta Satélite de la Economía
  Informal 2022-2024*. https://www.gob.pe/institucion/inei/informes-publicaciones/
  7564428 — acceso: abierto. (Mide EPEN al 2024, no 2025 — ver aclaración en Eje 7.)
- Yamada, G. (2007). *Retornos a la Educación Superior en el Mercado Laboral: ¿Vale la
  Pena el Esfuerzo?* CIES / Universidad del Pacífico. https://cies.org.pe/publicaciones/
  retornos-a-la-educacion-superior-en-el-mercado-laboral-vale-la-pena-el-esfuerzo/ —
  acceso: abierto.
- Lemieux, T. (2006). The "Mincer equation" thirty years after *Schooling, Experience,
  and Earnings*. En S. Grossbard (ed.), *Jacob Mincer: A Pioneer of Modern Labor
  Economics*, cap. 11 (pp. 127–145). Springer. https://economics.ubc.ca/wp-content/
  uploads/sites/38/2013/05/pdf_paper_thomas-lemieux-mincer-equation.pdf — acceso:
  abierto.
- Duan, N. (1983). Smearing estimate: A nonparametric retransformation method. *Journal
  of the American Statistical Association*, 78(383), 605–610. — acceso: pago.
