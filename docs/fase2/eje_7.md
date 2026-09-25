# EJE 7 — Contexto institucional peruano (cifras oficiales)

## A. Referencias

### 1. INEI (2026) — Informe Técnico Q4/anual 2025 de empleo [NUEVA — reemplaza a inei_informal para la cifra 2025]
- **id sugerido**: `inei_empleo_2025`
- **Cita completa (APA)**: Instituto Nacional de Estadística e Informática. (2026). *Perú: Comportamiento de los Indicadores del Mercado Laboral a Nivel Nacional y en 27 Ciudades. Enero-Diciembre 2025 | Cuarto Trimestre 2025*. Informe Técnico, febrero 2026. INEI, Lima.
- **DOI**: no tiene.
- **URL abierta**: https://www.gob.pe/institucion/inei/informes-publicaciones/7739601-peru-comportamiento-de-los-indicadores-del-mercado-laboral-a-nivel-nacional-y-27-ciudades-cuarto-trimestre-2025 (PDF: cdn.www.gob.pe/uploads/document/file/9450232/7739601-...pdf)
- **Acceso**: abierto (PDF descargado sin paywall).
- **Verificado**: sí. Descargado y convertido a texto (`raw/inei_q4_2025.pdf` / `.txt`, 64 páginas).
- **Cita textual** (Cuadro N.° 1.20, p. 26): «Según resultados de la Encuesta Permanente de Empleo Nacional (EPEN) del año 2025, en el país, el 70,2% tenían empleo informal» — 70,9% en 2024, 70,2% en 2025.
- **Cita textual** (Gráfico N.° 1.15, p. 26): «el 94,8% de la población ocupada del área rural tenía empleo informal, en tanto en el área urbana el 64,5%».
- **Cita textual** (Cuadro N.° 1.22, p. 28): «El 88,6% de la población ocupada en empresas de 1 a 10 trabajadores tenían empleo informal, en empresas de 11 a 50 trabajadores el 44,0% y en las empresas de 51 y más trabajadores el 15,6%».
- Qué dice: informe técnico trimestral/anual de EPEN, publicado en febrero de 2026, con las tasas de empleo informal 2024 vs. 2025 por área, sexo, edad, educación, tamaño de empresa y rama.

### 2. `inei_informal` (ya en `referencias.py`) — referencia que POSEO

- **Cita tal como está en el repo**: INEI (2025). *Producción y empleo informal en el Perú: Cuenta Satélite de la Economía Informal 2022-2024*. INEI, Lima.
- **URL**: https://www.gob.pe/institucion/inei/informes-publicaciones/7564428-... (PDF: cdn.www.gob.pe/uploads/document/file/9215525/7564428-libro.pdf).
- **Acceso**: abierto. Verificado sí — descargado, 128 páginas (`raw/inei_csei_2022_2024.pdf/.txt`).
- **Metadatos verificados**: el pie de imprenta dice «Lima, diciembre 2025» (no 2025 como año del dato — 2025 es el año de PUBLICACIÓN).
- **Contenido verificado — cita textual** (p. 5 / Presentación): «Los datos de la informalidad se han obtenido en base a la reciente información de las Cuentas Nacionales al 2024, y la Encuesta Permanente de Empleo Nacional (EPEN) al 2024.»
- **Cita textual** (Resumen, p. 7): «Tres de cada cuatro trabajadores de la PEA ocupada se desempeñaban en un empleo informal (70,9%)» — año 2024.
- **Cita textual** (p. 50-51, Gráfico 4.1c/4.1d): empleo informal urbano 65,4%; rural 94,5% (2024) — tramos de empresa usados aquí son 1-5/6-10/11-30/31+, NO 1-10/11-50/51+.
- **Veredicto (regla 10): CORREGIR.**
  1. El año del dato es **2024**, no 2025 (la publicación explícitamente usa EPEN «al 2024»). La app dice «el 70,2 % que publica el INEI para 2025» y cita `inei_informal` — imposible: esta publicación no puede contener una cifra de 2025 porque no la mide. Lo que sí publica para 2024 es 70,9 %, no 70,2 %.
  2. El `nota` del repo («Las tasas oficiales de empleo informal contra las que se valida la regla del target») sigue siendo correcto en general, pero la cifra puntual de 70,2 %/2025 que la app le atribuye no está en esta fuente.
  3. **Fix concreto**: para la comparación con 2025 (70,2 % nacional, 64,5 % urbano, 94,8 % rural, 88,6 %/15,6 % por tamaño de empresa), citar `inei_empleo_2025` (arriba), no `inei_informal`. `inei_informal` puede seguirse citando, pero para el dato 2024 (70,9 % nacional / 65,4 % urbano / 94,5 % rural) y con tramos de empresa distintos (1-5/6-10/11-30/31+, no 1-10/11-50/51+).

### 3. Sobre la referencia `[8]` del README

- El README no tiene lista numerada propia de referencias — no encontré ningún bloque `[1]…[15]` en `README.md` (grep vacío). Los números `[n]` que aparecen en el texto (p. ej. `[8]`) son huérfanos: no hay una sección "Referencias" en el README que los defina.
- Sin embargo, la numeración del repo real es la de `app/referencias.py::REFERENCIAS` (orden de la lista = número mostrado en la app, ver comentario en el propio archivo, línea 25: «El orden de esta lista ES la numeración [1], [2]… que ve el lector»). En esa lista, **la posición 8 es `sohnesen2016`** (Sohnesen & Stender 2016, *Is Random Forest a Superior Methodology for Predicting Poverty?*, World Bank Policy Research WP 7612) — un paper de metodología de machine learning para pobreza, **no una fuente del INEI**.
- **Veredicto NV-7 (3): el `[8]` que el README pone junto a «el INEI reporta 88,6 % ... 15,6 %» está mal — o el README lo copió sin adaptar la numeración de la app, o nunca existió una lista de referencias numerada en el README y `[8]` quedó huérfano. En cualquier caso, la cifra 88,6 %/15,6 % no tiene hoy una cita verificable en el propio documento; la fuente real y verificada es `inei_empleo_2025` (arriba), Cuadro N.° 1.22.**

## B. Cruces con la app

1. **Hallazgo propio — informalidad reconstruida 67,3 % (todos los ocupados, ENAHO) vs. 70,2 % INEI 2025 (EPEN).**
   Literatura: `inei_empleo_2025`, Cuadro 1.20 — 70,2 % nacional 2025, EPEN. **No podemos concluir "coincide/discrepa" limpiamente**: son encuestas distintas (ENAHO vs. EPEN) con años de referencia y definiciones operativas ligeramente distintas (la app deriva informalidad con la regla operacional SUNAT/pensiones sobre ENAHO 2025; el INEI mide directamente con EPEN 2025). El sesgo de ~3 puntos que el README atribuye a «afiliación autofinanciada a pensiones» es una lectura razonable pero no verificada contra una fuente que aísle ese efecto — no encontré una publicación INEI que descomponga el sesgo ENAHO-vs-EPEN por esa causa específica. Etiqueta: **hallazgo propio**, con la salvedad de que el benchmark correcto (`inei_empleo_2025`) reemplaza al citado (`inei_informal`, que es de 2024).
   Ids: `inei_empleo_2025` (nueva), `inei_informal` (corregir cita).

2. **Hallazgo propio — Urbano 64,5 % / Rural 94,8 % oficial INEI 2025 (tabla del README).**
   Coincide dígito por dígito con `inei_empleo_2025`, Gráfico 1.15 (p. 26): 64,5 % urbano, 94,8 % rural, año 2025. **Coincide exactamente.** Solo falta corregir la cita: el README no cita ninguna referencia en esas filas de tabla (no hay marcador `[n]`), así que no hay error de atribución ahí, pero conviene añadir `ref('inei_empleo_2025')`.
   Ids: `inei_empleo_2025`.

3. **NV-7 — «el INEI reporta 88,6 % en empresas de 1 a 10 trabajadores y 15,6 % en las de más de 50» [8].**
   Coincide dígito por dígito con `inei_empleo_2025`, Cuadro 1.22 (p. 28): 88,6 % (1-10 trab.), 44,0 % (11-50 trab.), 15,6 % (51+ trab.), año 2025. **La cifra es correcta y verificable**, pero el marcador `[8]` que la acompaña en el README apunta (si sigue el orden de `referencias.py`) a `sohnesen2016`, que no tiene nada que ver. Etiqueta: **corregir cita**, no el dato.
   Ids: `inei_empleo_2025` (correcta), `sohnesen2016` (mal atribuida, descartar de esa oración).

## C. Descartadas

- Los seed items de SUNAT (regímenes NRUS/RER/MYPE), ONP/AFP (fracción que aporta), remuneración mínima vital, Ley 31047, e impacto COVID-19 en la informalidad: **no cubiertos en esta pasada** por límite de tiempo/presupuesto de la sesión, después de agotar el esfuerzo en cerrar `inei_informal` y NV-7 (que eran el encargo explícito y no negociable de este eje). Encontré vía búsqueda web (no verificado con texto crudo, por lo tanto sin cita válida bajo la regla 1) que: la RMV vigente sería S/ 1 130 desde el 1/1/2025 por D.S. N.° 006-2024-TR (El Peruano, 28/12/2024); la Ley 31047 se publicó el 1/10/2020 en El Peruano. Ninguna de las dos se abrió en El Peruano directamente ni se guardó texto crudo — **no se pueden reportar como verificadas**. Recomiendo una segunda pasada específica para estos cuatro puntos si el eje los necesita con la misma rigurosidad que el INEI.
- `informe-tecnico_empleonacional.pdf` (sin sufijo) e `informe_epen_nacional.pdf`: descartados como fuente porque, al abrirlos, resultaron ser informes de trimestres anteriores (Q4-2024 y Q2-2024 respectivamente, por fecha de creación del PDF) y el segundo no menciona informalidad en absoluto.
- «Informe de Empleo N.° 1, trimestre Oct-Nov-Dic 2025» (otra serie de boletines INEI, distinta de la usada arriba): descartado, no contiene ninguna mención de informalidad (0 coincidencias de "informal" en el texto extraído).

## D. Errores de la semilla

1. `inei_informal` tal como está citado en `app/referencias.py` (línea 202-217) es una publicación real y abierta, pero **no puede respaldar una cifra de 2025**: su propio texto dice que usa EPEN «al 2024». El dato que sí trae para 2024 es 70,9 % nacional (no 70,2 %), 65,4 % urbano (no 64,5 %), 94,5 % rural (no 94,8 %), y usa tramos de tamaño de empresa distintos (1-5/6-10/11-30/31+, no 1-10/11-50/51+). La fuente correcta para las cifras 2025 que usa la app y el README es la nueva `inei_empleo_2025` propuesta arriba.
2. El README cita `[8]` para la cifra de informalidad por tamaño de empresa; si esa numeración sigue el orden de `app/referencias.py`, `[8]` es `sohnesen2016` (metodología de random forest para pobreza, Banco Mundial), no una fuente del INEI. El README además no tiene una lista de referencias numerada propia, así que `[8]` es un marcador huérfano tal como está el archivo hoy.

---
**Conteo**: verificadas 2 (`inei_empleo_2025` nueva, `inei_informal` existente — con corrección) · no verificadas/no cubiertas 4 seed items secundarios (RMV, Ley 31047, SUNAT, ONP/AFP/OIT) · descartadas 3 fuentes candidatas.
