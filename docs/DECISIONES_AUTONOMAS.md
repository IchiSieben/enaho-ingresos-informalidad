# Decisiones autónomas (rama `v2-autonomo`)

Decisiones tomadas sin el autor presente, a partir del 26/09/2026. Cada una
dice qué se eligió, qué se descartó y cómo revertirla. Todo vive en la rama
`v2-autonomo`; `main` y la app pública no se tocaron.

## Fase 2 · hotfix de citas (commit `ce5ee21`)

**D-01 · Criterio del test de `ref()`.** Se añadió el campo `verificacion`
(`contenido` | `metadatos`) a cada referencia de `app/referencias.py`. El test
`tests/test_referencias_verificadas.py` acepta `metadatos` solo para los ids
de una lista blanca con justificación; hoy solo `duan1983` (la app le
atribuye únicamente el nombre del método, que es el título del artículo).
- Descartado: exigir `contenido` a todas (obligaría a quitar Duan, que es la
  cita correcta del método) y verificar por afirmación en vez de por
  referencia (la matriz ya lo hace a mano; el test cubre lo automatizable).
- Revertir: borrar el test y el campo (`git revert ce5ee21` deshace todo el
  hotfix; para solo el test, borrar `tests/test_referencias_verificadas.py`).

**D-02 · Alcance de `inei_informal`.** La frase «se validó contra la tasa
oficial» pasó a decir que es un contraste de referencia, no una validación:
la tasa oficial (70,2 %) sale de la EPEN y la nuestra de la ENAHO.
- Descartado: buscar una tasa oficial calculada sobre la ENAHO para comparar
  la misma encuesta. Queda como tarea abierta: no se sabe si el INEI la
  publica.
- Revertir: la frase está en dos sitios de `app/streamlit_app.py` (buscar
  «No es una validación contra la misma fuente»).

**Nota.** `docs/fase2/verificar_citas.py` informa 31 problemas en los
borradores de `docs/fase2/` (sin texto crudo o sin coincidencia). No se
corrigieron: son los borradores de la investigación, no los entregables.
`verificar_entregables.py` (la matriz y el marco) da 0 problemas.

## Fase 1.6 · A. Identidad y créditos

**D-03 · Dominio.** `ichi7.dev` no resuelve. El autor confirmó que su dominio
es `ichisieben.dev` y se usa en la barra, el pie, el README y AUTHORS.md
(CITATION.cff ya lo tenía).

**D-04 · Marca.** Solo el monograma (caja + «iC7» en JetBrains Mono, el mismo
dibujo de `Landing/src/components/Nav.astro`) y el enlace «← ichisieben.dev».
No lleva la palabra «IchiSieben» al lado, como sí la lleva el landing, para
no competir con las pestañas. La fuente se carga con `text=iC7`, solo 3 glifos.
- Revertir o ajustar: `marca_barra()` en `app/streamlit_app.py`.

**D-05 · Roles en el pie.** AUTHORS.md solo asigna roles (CRediT) al autor
del software. Esos roles van en la línea «Desarrollo». Los integrantes del
grupo van sin rol, en el orden de AUTHORS.md, y el docente al final. Lo
vigila `tests/test_creditos.py`.
- Descartado: atribuir la «regresión inicial» a alguien en particular.
  AUTHORS.md la atribuye al grupo.

**D-06 · Enlaces al portafolio con `target="_top"`.** En Community Cloud la
app corre dentro de un iframe. Un enlace normal abriría el portafolio dentro
de ese marco.

## Fase 1.6 · C. Tipografía y ritmo · B. Navegación

**D-07 · Espacio duro por dos vías.** `pc`, `pct`, `sol` (nuevo) y `_mb`/`_kb`
lo ponen al formatear. Además, `html()` pasa todo por `i18n.no_cortar()`, una
red de seguridad para la prosa escrita a mano («el 25 % gana…»). Así no hubo
que tocar cada literal. Los rótulos de widgets no pasan por `html()` y quedan
fuera.
- Revertir: `NBSP = " "` en `app/i18n.py` lo desactiva todo de una vez.

**D-08 · «Detalle técnico» en la fila del título, a la derecha.** Primero se
probó justo debajo de la entradilla. Costaba 30 px y el gráfico de
Informalidad salía del primer pantallazo a 1366×768 (774 > 768 px, medido
con `docs/qa/medir_vistazo.py`). En la fila del título ocupa la misma posición
en las cinco secciones y el popover flota sin mover nada. Para recuperar el
pliegue, la entradilla pasó de 70ch a 75ch, el tope de la regla de 65–75
caracteres. Con eso, 10/10 entran en ES y en EN.
- Revertir a «debajo»: en `cabecera()`, sacar el popover del contenedor
  `cab_titulo` y ponerlo después de la entradilla.

**D-09 · «S/» de la cifra grande a 0,55 em y pegado.** En la monoespaciada,
el espacio normal ocupaba casi un carácter entero. Se alinea por línea base
con «× la mediana del país» (flex `baseline`).

**D-10 · Tope de 1360 px con `!important`.** El `max-width: 1400px` ya estaba,
pero el ancho «wide» de Streamlit lo pisaba y en 2560 px el contenido llegaba
a los bordes.

**D-11 · Pestañas.** Hay 6 px entre pestañas, fondo de acento al 12 % al pasar
el cursor, cursor de mano, anillo de foco y la activa en acento pleno. Idioma
y tema van en un contenedor propio (`ajustes`), a la derecha y tras una línea
vertical. En móvil bajan a su propia fila.

## Fase 1.6 · D. La animación de «Cómo se hizo»

**D-12 · Opción elegida: (a) ampliada. HTML + CSS con radios y `:has()`, sin
JavaScript y sin componente.** Una prueba en Chromium con Streamlit 1.61
(`st.markdown` con `unsafe_allow_html`) dio lo siguiente. Conserva `<input
type=radio name=…>` y `<label>`, y las reglas con `:has()` se aplican. El
atributo `checked` no se puede usar: React vuelve controlado el radio y deja
de responder al clic. Por eso «ningún radio marcado» equivale a «auto». El
estado sobrevive a un rerun si el HTML es idéntico byte a byte. Con eso sale
todo lo que pedía la opción (b) sin sus costos: ▶/❚❚, ◀ ▶ estación por
estación y clic en una estación del diagrama que selecciona su detalle abajo,
sin rerun.
- Descartado (b), componente bidireccional: exigía `st.components` (lo
  prohíbe un test aprobado, `3a5317b`) o un componente v2 con JS propio, que
  es más frágil de mantener y reinstala el viaje a Python en cada clic.
- Descartado SMIL: no se pausa desde CSS (la queja original).
- Diseño: 3 s por estación, 18 s por vuelta. El punto se detiene el 72 % del
  tramo y viaja en el resto. Las lecturas «en vivo» (84.853 → 57.716 → 47.899
  → 47.632 filas; 38.105 / 9.527; 9 recetas; MB y KB) salen de
  `ui_maquinas.json` y del artefacto (`_lecturas_vivas`), y cada una tiene su
  ventana de tiempo. Con movimiento reducido queda quieto en la estación 1.
  En móvil las estaciones se apilan y el punto baja.
- Los seis detalles van en el HTML de la pestaña. El CSS muestra el elegido
  desde el ancestro común (`stMain:has(...)`); sin elegir, se ve el 1.
- `graficos.viaje_dato` y `viaje_dato_vertical` (SMIL) ya no los usa la app.
  Se conservan porque los cubren los tests de contrato. **Propuesta:**
  retirarlos junto con `css_iframe` y `envolver`.
- Revertir: `git revert` del commit de D. El selector y el toggle vuelven.

## Fase 1.6 · E. Interactividad evidente

**D-13 · «Perfil al azar»** es un botón terciario con el icono
`:material/shuffle:`, junto al rótulo de los perfiles. Debajo de las pastillas
ocupaba una fila entera, y a 1366×768 el gráfico de Informalidad salía del
pliegue. Sortea cada variable dentro del schema. La única regla cruzada que
aplica es edad ≥ educación + 6, para que la experiencia potencial no sea
negativa. Al usarlo, se apaga la pastilla de ejemplo elegida.
- Descartado: sortear con los pesos de la ENAHO (perfiles «típicos»). Sería
  más realista, pero exige precomputar una tabla, y un sorteo uniforme dentro
  del schema cumple lo pedido.

**D-14 · Chips «ver el código →» nuevos.** Van al pie de 8 bloques: Ingreso
(src/07), Informalidad (src/06), Acto 1 (src/02), Acto 3 (src/04), ficha del
clasificador (src/06, 08, 08b), ficha del regresor (src/07), embudo (src/03)
y «Mueve una variable» (src/09). Ahora se ven como botones: caja, hover y
cursor.

**D-15 · Pista de uso.** Es un solo micro-texto, «Haz clic en una estación
para ver su detalle abajo», en el viaje. No se añadió ningún tutorial: el
recorrido guiado queda para «Empieza aquí» (Fase 4).

## Fase 3 · Propuesta (reemplaza la parada «DETENTE tras proponer»)

**D-16 · Qué se construye y en qué orden (valor × viabilidad).** Todo sale de
`src/10_contexto.py` y se escribe en `models/ui_contexto.json` (escritura
atómica) y en `reports/10_contexto.md`:
1. Penalidad de la informalidad: WLS de log(ingreso por hora) con
   `informal`, con dos juegos de controles y por categoría ocupacional.
2. Brecha de género: Oaxaca-Blinder de dos partes y Ñopo (emparejamiento
   exacto por celdas), con el soporte común reportado.
3. Retornos a la educación por segmento: asalariados vs. independientes y
   formales vs. informales. Se contrasta con Yamada (2007) y con
   Psacharopoulos y Patrinos (2018), ya verificados en la matriz (filas 7 y 8).
4. Mapa por departamento: tasa de informalidad e ingreso mediano, ponderados
   y con su n. El GeoJSON es un paso aparte: solo entra con licencia abierta
   verificada en la página de la fuente.
5. Lengua materna, agregada: castellano, quechua, aimara y «otra lengua
   originaria» (códigos 3 y 10–15 del diccionario 2025). El código 3 es
   «otra lengua nativa», que no es necesariamente amazónica; por eso el
   rótulo no dice «amazónicas». Se calcula; la app no
   la muestra (`MOSTRAR_LENGUA = False`).
- Descartado: la etnicidad (P558C). El encargo no la pide, es sensible, y la
  categoría 9 tiene n = 40.

**D-17 · Muestra.** Es la misma de 47.632 que narra la app
(`torneo_frame.parquet`, casos completos). No se usan las 47.899 del
dataset de modelado. Su tasa ponderada de informalidad es 64,1 %. El 67,3 %
del reporte de la Fase 1 es otra población: todos los ocupados de 14 años o
más, antes del filtro de casos completos. El test de agregación compara el
mapa contra la muestra propia, no contra el 67,3 %.

**D-18 · Variable de resultado.** La principal es log(ingreso por hora):
`ingreso_mes / (horas_total × 52/12)`. El ingreso mensual mezcla el salario
con las horas trabajadas, y las mujeres trabajan menos horas remuneradas. La
secundaria es log(ingreso mensual). El ingreso y las horas suman
ocupación principal y secundaria en `03_fase1_preparacion.py`, así que
cubren lo mismo. Se excluyen las filas con 0 horas.

**D-19 · Pesos y varianza.** FAC500A en todo. Los errores estándar de las
regresiones son robustos por conglomerado (CONGLOME). Para Oaxaca, Ñopo y
las medianas se usa un bootstrap de conglomerados con semilla fija. No se
usan los estratos, lo cual da errores algo más grandes: es la dirección
conservadora.

**D-20 · Señales de alarma.** Oaxaca se corre con dos juegos de controles:
(A) capital humano y geografía, y (B) A más rama, categoría y tamaño, que
son «malos controles» porque también son resultados. Se corre con tres
coeficientes de referencia: pooled con dummy de grupo, hombres y mujeres. Si
la parte no explicada cambia de signo entre variantes, o una celda que se
mostraría tiene n < 100, el resultado se marca `mostrar: false` y se anota
aquí. No se para el trabajo.

**D-21 · GeoJSON de departamentos.** Sale de geoBoundaries gbOpen PER ADM1,
versión simplificada y fijada al commit `90a1d52`. La API de geoBoundaries
declara la licencia como Public Domain (origen: Wikimedia Commons). Se
redondea a 3 decimales (unos 100 m) y queda en 123 KB, así que se versiona
en `models/peru_departamentos.geojson` (lo genera `src/10b_mapa_geo.py`).
geoBoundaries separa Lima Metropolitana de Lima provincias; la ENAHO los
junta en el código 15, así que los dos polígonos llevan el 15.
- Descartado: GADM (sus términos restringen la redistribución) y Natural
  Earth (no verificado en esta sesión; geoBoundaries ya cumple).
- Revertir: borrar el archivo y el script. El test del mapa falla a
  propósito.

## Fase 3 · Resultados (reemplaza la parada «DETENTE con los resultados»)

**D-22 · Sin señales de alarma.** Corrida con B = 200, semilla 42; el detalle
está en `reports/10_contexto.md`.
- **Penalidad por hora de la informalidad**, con controles A: −40,7 %. Con
  controles B (rama, categoría y tamaño): −21,1 %. Entre asalariados es
  −23,7 % y entre independientes −40,0 %. Es una diferencia condicional, no
  un efecto: hay selección.
- **Brecha de género por hora:** 0,262 log puntos. La parte explicada es
  cercana a cero o negativa: entre quienes trabajan, las mujeres tienen igual
  o más educación. La parte no explicada va de 0,25 a 0,29, con signo estable
  en las seis variantes. Ñopo da resultados parecidos: Δ = 15,4 %, Δ0 = 20,6 %
  y soporte común > 95 %. Es lo mismo que describe Ñopo (2008) para el Perú
  (filas 37–38 de la matriz): una parte no explicada mayor que la brecha
  total.
- **Retornos a la educación:** 9,4 % en asalariados y 4,5 % en
  independientes. El orden es el de Yamada (2007), con 12,5 % y 6,5 % en
  2004; los niveles 2025 son menores. Esto último no se interpreta: los
  años, la muestra y la especificación son distintos.
- **Departamentos:** los 25 tienen n ≥ 878. Madre de Dios es el más chico.
- **Lengua materna:** los cuatro grupos tienen n ≥ 667. Queda oculta en la
  app (`MOSTRAR_LENGUA = False`) hasta que el autor la revise, como pide el
  encargo.
- Revertir: borrar `models/ui_contexto.json`. La app de la Fase 4 no debe
  romperse si el archivo falta.
