# Propuesta de cambios a la bibliografía (Fase 2)

Este documento no modifica `app/referencias.py`. Es la propuesta, con el texto exacto,
para que el equipo la aplique. El detalle de verificación de cada cifra está en
`docs/MATRIZ_AFIRMACIONES.md`; el marco teórico completo, en `docs/MARCO_TEORICO.md`.

## 1. Cambios a entradas existentes de `app/referencias.py`

### `heckman2006`

La entrada en sí (cita/url/acceso/nota general) está bien y queda igual. El problema es
la frase que la cita en `app/streamlit_app.py:2344-2351`, no la ficha bibliográfica.
Ver sección 5 para el texto propuesto de esa frase.

### `psacharopoulos2018`

- **url actual**: `https://documents.worldbank.org/curated/en/442521523465644318`
  (landing page, no sirve el PDF directo).
- **url propuesta**: `https://documents1.worldbank.org/curated/en/442521523465644318/pdf/WPS8402.pdf`
- **nota actual**: "1.120 estimaciones en 139 países: retorno privado global ≈ 9 % anual;
  América Latina y el Caribe, 11,0 %."
- **nota propuesta (ES)**: "1.120 estimaciones en 139 países: retorno privado global
  ≈ 9 % anual; América Latina y el Caribe, tasa de retorno global 11,0 % (el DOI listado
  corresponde a la versión de revista en *Education Economics*, no al working paper del
  Banco Mundial, que no tiene DOI propio)."
- **nota_en propuesta**: "1,120 estimates across 139 countries: global private return
  ≈ 9% per year; Latin America and the Caribbean, 11.0% overall rate of return (the DOI
  listed is for the journal version in *Education Economics*, not the World Bank working
  paper itself, which has no DOI of its own)."

### `loayza2008`

- **url actual**: `https://www.bcrp.gob.pe/docs/Publicaciones/Revista-Estudios-Economicos/15/Estudios-Economicos-15-3.pdf`
  (responde bloqueo de bot en verificación automatizada; funciona en navegador humano).
- **url alternativa a considerar**: la copia de Wayback Machine del mismo PDF
  (`https://web.archive.org/web/2023/https://www.bcrp.gob.pe/docs/Publicaciones/Revista-Estudios-Economicos/15/Estudios-Economicos-15-3.pdf`)
  o la variante en minúsculas del propio sitio del BCRP (`ree-15/ree-15-03.pdf`), que
  también existe. Recomendación: mantener la URL actual (resuelve en navegador) y anotar
  el bloqueo de bot, siguiendo el mismo patrón que ya usa `duan1983`.
- **nota actual**: "Contexto económico de la informalidad peruana." (vaga, no verificable).
- **nota propuesta (ES)**: "Marco explicativo con tres causas no excluyentes: servicios
  públicos deficientes, régimen normativo opresivo y débil capacidad de fiscalización del
  Estado; usa la definición legal de De Soto (1989)."
- **nota_en propuesta**: "Explanatory framework with three non-exclusive causes: poor
  public services, an oppressive regulatory regime, and weak state enforcement capacity;
  uses De Soto's (1989) legal definition."
- Nota adicional: hoy `loayza2008` no tiene ninguna llamada `ref('loayza2008')` en
  `app/` — ver sección 3.

### `perry2007`

- **url actual**: `https://doi.org/10.1596/978-0-8213-7092-6` (resuelve al e-library del
  Banco Mundial, de pago para el texto completo).
- **url propuesta**: `https://documents1.worldbank.org/curated/en/326611468163756420/txt/400080Informal101OFFICIAL0USE0ONLY1.pdf`
  (copia íntegra abierta en el propio dominio del Banco Mundial).
- **nota actual**: "Marco de informalidad por exclusión frente a informalidad por
  elección."
- **nota propuesta (ES)**: "Marco de informalidad por exclusión y por elección
  (autoexclusión): el propio libro los presenta como complementarios, no como hipótesis
  en competencia."
- **nota_en propuesta**: "Framework of informality by exclusion and by choice
  (self-exclusion): the book itself presents them as complementary, not competing
  hypotheses."
- Nota adicional: hoy `perry2007` no tiene ninguna llamada `ref('perry2007')` en `app/`
  — ver sección 3.

### `oit_17ciet`

- **cita actual**: "...Actualizada por la Resolución I de la 21.ª CIET (2023)."
- **cita propuesta (ES)**: "...Revisada y ampliada por la resolución sobre estadísticas de
  la economía informal adoptada en la 21.ª CIET (2023), que extiende el alcance a todas
  las formas de trabajo."
- **cita_en propuesta**: "...Revised and expanded by the resolution on statistics on the
  informal economy adopted at the 21st ICLS (2023), which extends the scope to all forms
  of work."
- Motivo: no se pudo verificar textualmente que el documento de 2023 se llame formalmente
  "Resolución I" — el texto abierto (Report II / proyecto de resolución) no numera la
  resolución de forma explícita en el pasaje leído. Si el equipo confirma el número exacto
  contra el documento final adoptado (no el borrador Report II), puede mantenerse
  "Resolución I" citando esa fuente final.

### `sohnesen2016`

- **nota actual**: "Comparación entre aprendizaje automático y regresión en encuestas de
  hogares."
- **nota propuesta (ES)**: "Comparación entre aprendizaje automático (random forest) y
  regresión para predecir pobreza en encuestas de hogares; ningún método, incluido random
  forest, predice con consistencia a través del tiempo."
- **nota_en propuesta**: "Comparison of machine learning (random forest) and regression
  for predicting poverty in household surveys; no method, including random forest,
  predicts consistently over time."

### `inei_informal`

- **Problema**: la app y el README le atribuyen las cifras 2025 (70,2 % nacional, 64,5 %
  urbano, 94,8 % rural, 88,6 %/44,0 %/15,6 % por tamaño de empresa), pero esta publicación
  mide con EPEN "al 2024" y reporta 70,9 % nacional, 65,4 % urbano, 94,5 % rural, con
  tramos de empresa distintos (1-5/6-10/11-30/31+, no 1-10/11-50/51+).
- **Acción propuesta**: mantener `inei_informal` en la lista (referencia real y correcta
  para el dato 2024), pero **reasignar la cita de las cifras 2025 a la nueva referencia
  `inei_empleo_2025`** (sección 2). Si se desea, `inei_informal` puede quedar con nota
  corregida para dejar claro que su año de referencia es 2024:
- **nota propuesta (ES)**: "Cuenta Satélite de la Economía Informal, con datos EPEN al
  2024 (70,9 % de informalidad nacional). Para las cifras 2025 que usa este proyecto, ver
  `inei_empleo_2025`."
- **nota_en propuesta**: "Satellite Account of the Informal Economy, using EPEN data as of
  2024 (70.9% national informality). For the 2025 figures this project uses, see
  `inei_empleo_2025`."

## 2. Referencias nuevas propuestas para `app/referencias.py`

Solo se proponen las que la app citaría realmente si se aplican los cambios de la
sección 5.

### `inei_empleo_2025`

```python
{
    "id": "inei_empleo_2025",
    "cita": "INEI (2026). <i>Perú: Comportamiento de los Indicadores del Mercado "
            "Laboral a Nivel Nacional y en 27 Ciudades. Enero-Diciembre 2025 | "
            "Cuarto Trimestre 2025</i>. Informe Técnico, febrero 2026. Instituto "
            "Nacional de Estadística e Informática, Lima.",
    "url": "https://www.gob.pe/institucion/inei/informes-publicaciones/"
           "7739601-peru-comportamiento-de-los-indicadores-del-mercado-laboral-"
           "a-nivel-nacional-y-27-ciudades-cuarto-trimestre-2025",
    "acceso": "abierto",
    "nota": "Cuadro 1.20 (empleo informal nacional 70,2 %), Gráfico 1.15 (urbano "
            "64,5 %, rural 94,8 %) y Cuadro 1.22 (por tamaño de empresa: 88,6 % "
            "en 1-10 trabajadores, 44,0 % en 11-50, 15,6 % en 51+), año 2025.",
    "cita_en": "INEI (2026). <i>Peru: Labor Market Indicators at the National "
               "Level and in 27 Cities. January-December 2025 | Fourth Quarter "
               "2025</i>. Technical Report, February 2026. National Institute of "
               "Statistics and Informatics (INEI), Lima.",
    "nota_en": "Table 1.20 (national informal employment 70.2%), Chart 1.15 "
               "(urban 64.5%, rural 94.8%) and Table 1.22 (by firm size: 88.6% "
               "in 1-10 workers, 44.0% in 11-50, 15.6% in 51+), year 2025.",
},
```

### `chen2012`

```python
{
    "id": "chen2012",
    "cita": "Chen, M. A. (2012). <i>The Informal Economy: Definitions, Theories "
            "and Policies</i>. WIEGO Working Paper n.º 1. WIEGO.",
    "url": "https://www.wiego.org/wp-content/uploads/2019/09/Chen_WIEGO_WP1.pdf",
    "acceso": "abierto",
    "nota": "Ancla del marco de cuatro escuelas (dualista, estructuralista, "
            "legalista, voluntarista) y del origen histórico del término "
            "(Hart 1973, misión OIT a Kenia 1972, CIET 1993/2003).",
    "cita_en": "Chen, M. A. (2012). <i>The Informal Economy: Definitions, "
               "Theories and Policies</i>. WIEGO Working Paper No. 1. WIEGO.",
    "nota_en": "Anchor for the four-school framework (dualist, structuralist, "
               "legalist, voluntarist) and for the historical origin of the "
               "term (Hart 1973, ILO Kenya mission 1972, ICLS 1993/2003).",
},
```

### `ulyssea2020`

```python
{
    "id": "ulyssea2020",
    "cita": "Ulyssea, G. (2020). «Informality: Causes and Consequences for "
            "Development». <i>Annual Review of Economics</i> 12, pp. 525-546.",
    "url": "https://www.dropbox.com/scl/fi/awm4ua8fpioqppa0agy5d/"
           "annurev-economics-082119-121914.pdf",
    "doi": "10.1146/annurev-economics-082119-121914",
    "acceso": "abierto",
    "nota": "Revisión del debate dualista/voluntarista; advierte que "
            "las brechas salariales por sí solas no bastan para probar "
            "segmentación, y documenta que la informalidad decrece con el "
            "tamaño de la firma en todos los países estudiados.",
    "cita_en": "Ulyssea, G. (2020). “Informality: Causes and Consequences for "
               "Development”. <i>Annual Review of Economics</i> 12, pp. 525-546.",
    "nota_en": "Review of the dualist/voluntarist debate; warns that "
               "wage gaps alone are not enough to test for segmentation, and "
               "documents that informality declines with firm size in every "
               "country studied.",
},
```

## 3. Referencias que quedan solo en docs (no entran a `app/referencias.py`)

Estas están verificadas y sustentan afirmaciones de `docs/MARCO_TEORICO.md`, pero la app
no las cita directamente hoy — quedan como bibliografía de respaldo del documento, no como
entradas numeradas de la interfaz, salvo que el equipo decida citarlas en texto nuevo:

hart1973, oit1972kenya, oit2018_mujeres_hombres, lewis1954, harristodaro1970, tokman1978,
portescastellsbenton1989, desoto1989, maloney2004, guntherlaunov2012, laportashleifer2014,
levy2008, matosmar1984, golteadams1987, rodriguez2011, kamichi2023, oaxaca1973,
blinder1973, nopo2008, nopo_atal_winder2009, blaukahn2017, goldin2014,
nopo_saavedra_torero2004, arpi2018, esparta_rivera2020, iza3151_2007, breiman2001,
shmueli2010, mullainathan2017, kleinberg2015, barocas2023, aiken2022.

## 4. Referencias descartadas y por qué

De las secciones "C. Descartadas" de cada eje:

- **Frosch (2024)**, sobre la 21.ª CIET — paywall Sage Journals (403), sin versión de
  autor abierta. Sustituida por el documento primario de la OIT (Report II).
- **Kolev (2015)**, brecha étnica de mujeres indígenas en Perú — paywall Wiley (403), sin
  versión abierta. Muy relevante temáticamente; recomendable para una segunda ronda si
  aparece copia abierta.
- **Chaman Álvarez (2025)**, BLS Monthly Labor Review — bls.gov bloquea acceso
  automatizado (curl y Wayback Machine devuelven solo el armazón JS). Metadatos
  confirmados, ninguna cifra citada.
- **Ñopo (2012), "BM/BID"** (id de la semilla) — no existe con esa combinación exacta de
  año/editorial. El trabajo real es Ñopo, Atal y Winder (2009, BID / IZA DP 5085, 2010),
  solo del Banco Interamericano de Desarrollo, no del Banco Mundial. Reemplazada por
  `nopo_atal_winder2009`.
- **"Tokman/PREALC, verificar la obra exacta"** (nota de la semilla, no una referencia) —
  reemplazada por Tokman (1978), *World Development* 6(9-10), la obra fundacional que cita
  Chen (2012) para la escuela dualista.
- **Búsquedas de GRADE/CIES sobre "confianza en el Estado y economía popular"** — no se
  encontró un paper reciente con ese vínculo específico y datos propios; solo notas de
  prensa e informes de coyuntura, que no cumplen el estándar de verificación.
- **Notas de prensa/institucionales sobre "emprendimiento por necesidad"** (Trome, Mercado
  Negro, Centrum/PUCP) — no son papers, no cumplen el estándar de verificación.
- **SUNAT (regímenes NRUS/RER/MYPE), ONP/AFP, RMV, Ley 31047, impacto COVID-19 en la
  informalidad** — no cubiertos en esta ronda por límite de tiempo; datos encontrados por
  búsqueda web (RMV S/ 1 130 desde 1/1/2025, D.S. 006-2024-TR; Ley 31047 publicada
  1/10/2020) no se guardaron como texto crudo verificado, así que no se reportan como
  referencias válidas. Pendiente para una segunda ronda si el eje institucional los
  necesita.

## 5. Frases del código de la app que deben cambiar

### `app/streamlit_app.py:2344-2351` — atribución a Heckman, Lochner & Todd (2006)

**Texto actual (ES)**:
> "Experiencia potencial, no real. Se usa edad − años de educación − 6 (truncada en 0;
> {negativa} de casos negativos). En trabajadores de baja educación sobreestima la
> experiencia efectiva (Heckman, Lochner & Todd, 2006)" + ref("heckman2006") + "."

**Problema**: la fórmula (edad − escolaridad − 6) sí está en Heckman, Lochner y Todd
(2006); el enunciado de que esa medida sobreestima la experiencia efectiva en baja
educación no aparece en el texto completo del paper (búsqueda exhaustiva sin resultado —
ver `docs/MATRIZ_AFIRMACIONES.md`, fila 6). Es el mismo tipo de error que la auditoría del
20/08/2026 ya corrigió una vez con Lemieux (2006).

**Texto propuesto (ES)**, sin atribución indebida:
> "Experiencia potencial, no real. Se usa edad − años de educación − 6 (truncada en 0;
> {negativa} de casos negativos), como en Heckman, Lochner y Todd (2006)" + ref("heckman2006")
> + ". Lectura nuestra, no un resultado publicado: si la trayectoria laboral tuvo
> interrupciones, la experiencia efectiva es menor que la potencial."

**Texto propuesto (EN)**:
> "Potential, not actual, experience. We use age − years of schooling − 6 (floored at 0;
> {negativa} of cases negative), as in Heckman, Lochner & Todd (2006)" + ref("heckman2006")
> + ". Our own reading, not a published result: if a work history had interruptions,
> actual experience is lower than potential."

### `app/streamlit_app.py:1364` y `app/streamlit_app.py:2133-2137` — cita de `inei_informal` para 70,2 % (2025)

**Texto actual (ES, línea 1364)**: "...la tasa oficial: reconstruida sobre todos los
ocupados da {...} frente al 70,2 % que publica el INEI para 2025." + ref("inei_informal")

**Problema**: `inei_informal` (Cuenta Satélite) mide con datos EPEN al 2024 y reporta
70,9 %, no 70,2 %. La cifra 70,2 % (2025) está en el informe técnico EPEN 2025
(`inei_empleo_2025`).

**Corrección propuesta**: sustituir `ref("inei_informal")` por `ref("inei_empleo_2025")`
en ambas apariciones (líneas 1372 y 2135/2142 del bloque `ref(...)`), una vez agregada la
nueva entrada. El texto narrativo no necesita cambiar, solo la referencia numerada que
enlaza.

### `README.md:463` — marcador `[8]` junto a "88,6 % ... 15,6 %"

**Texto actual**: "...el INEI reporta 88,6 % de informalidad en empresas de **1 a 10
trabajadores** y 15,6 % en las de más de 50 [8]."

**Problema**: el README no tiene una sección de referencias numerada propia; si `[8]`
pretendía seguir el orden de `app/referencias.py`, la posición 8 corresponde a
`sohnesen2016` (metodología de random forest para pobreza), que no tiene relación con esta
cifra del INEI.

**Corrección propuesta**: si el README adopta una lista de referencias numerada (como la
de la app), el marcador debe apuntar a `inei_empleo_2025` (o a `inei_informal` con la nota
corregida, si se prefiere no crear la referencia nueva). Alternativa más simple: quitar el
marcador `[8]` del README y dejar la cifra sin numerar, ya que hoy el README no define
ninguna lista — o añadir una nota a pie con la cita completa de `inei_empleo_2025`.

## 6. Referencias listadas pero nunca citadas desde `app/` (auditoría de uso)

Se buscó `ref('<id>')` en todo `app/` para cada id de `REFERENCIAS`. No tienen ninguna
llamada: `lemieux2006` (usada solo indirectamente vía R2_MINCER_CANONICO, que sí se
renderiza — no huérfana), `belloni2014`, `athey2019`, `sohnesen2016`, `psacharopoulos2018`
(usada vía `RETORNO_EDUCACION`, que tampoco se llama desde ninguna vista — código muerto),
`yamada2007` (misma situación: `RETORNO_EDUCACION`/`retorno_educacion()` no se invoca en
ningún archivo fuera de `referencias.py`), `loayza2008`, `perry2007`.

En limpio, huérfanas de verdad (sin ninguna función que las use, ni directa ni vía
plantilla): `belloni2014`, `athey2019`, `loayza2008`, `perry2007`. Con función definida
pero no invocada desde ninguna vista (`RETORNO_EDUCACION`/`retorno_educacion()`):
`psacharopoulos2018`, `yamada2007`. Recomendación: si `retorno_educacion()` se conecta a la
interfaz, hacerlo con la nota de `psacharopoulos2018` ya corregida (sección 1); si
`belloni2014`/`athey2019`/`loayza2008`/`perry2007` no se van a usar pronto, retirarlas de
`REFERENCIAS` para no listar en la app fuentes que ningún texto cita — o dejarlas
explícitamente marcadas como "pendiente de uso" en un comentario del propio archivo.
