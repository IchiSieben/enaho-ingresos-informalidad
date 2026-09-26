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
  cercana a cero o negativa. La parte no explicada va de 0,25 a 0,29, con
  signo estable en las seis variantes. Ñopo: Δ = 15,4 %, Δ0 = 20,6 % y soporte
  común > 95 %. **[Corregido en D-23: el mecanismo y la cita de este punto
  estaban mal.]**
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

**D-23 · Corrección de D-22 (alarma de contraste con la literatura).** D-22
decía dos cosas sin respaldo; el commit con el error queda en el historial,
sin reescribirlo:
1. *«Es lo mismo que describe Ñopo (2008) para el Perú.»* Falso. En Ñopo
   (2008), Perú 1986–2000 (fila 37 de la matriz), la brecha de 45 % se reparte
   en 11 + 6 puntos explicados y 28 sin explicar: la parte no explicada es
   **menor** que la brecha. En nuestros datos es **mayor**, porque la parte
   explicada es negativa. Tampoco lo respalda Ñopo, Atal y Winder (2009),
   fila 38. Queda como **hallazgo propio, distinto de Ñopo (2008)**. No
   lleva la etiqueta «consistente con la literatura». Lo que sí coincide con
   las dos fuentes es el signo: hay una brecha no explicada a favor de los
   hombres.
2. *«Las mujeres ocupadas tienen igual o más educación.»* Era una inferencia
   desde el signo de la parte explicada, sin verificar. La descomposición
   detallada, ya en el artefacto (`detalle_pooled`), dice otra cosa. Con
   controles A y por hora, educación y experiencia aportan +0,011, a favor de
   los hombres. Área aporta −0,026 y dominio −0,009. Lo que vuelve negativa
   la parte explicada es la geografía: las mujeres ocupadas son más urbanas
   (87,7 % frente a 81,4 %) y están más en Lima Metropolitana (37,2 % frente
   a 31,9 %), donde se gana más por hora. En años de educación la diferencia
   es mínima (10,67 frente a 10,71), aunque más mujeres tienen educación
   superior (41,2 % frente a 34,5 %).
- Unidades: Oaxaca trabaja sobre medias de logaritmos (0,262 ≈ 30 % entre
  medias geométricas). Ñopo trabaja sobre medias aritméticas relativas a la
  media femenina (15,4 %). No se contradicen. La nota está en el reporte y
  debe ir a la capa 2 de la app.
- Regla para la Fase 4: la app no escribe ningún «porqué» de la brecha que no
  salga de `detalle_pooled` o de `medias_por_sexo`.

## Fase 4 · Arquitectura (reemplaza la parada «antes de la arquitectura»)

**D-24 · Navegación de siete pestañas.** Orden: Empieza aquí · Ingreso ·
Informalidad · Investigación · Torneo · Ficha · Cómo se hizo. «Empieza aquí»
(`inicio`) es la sección por defecto, como pide el encargo, y los enlaces
`?sec=` siguen funcionando. Si la barra se parte en dos filas a 1366 px, se
acortan los rótulos antes de tocar el layout, y se vuelve a medir el
pliegue de las siete secciones en ES y EN.
- Revertir la portada por defecto: `SECCION_POR_DEFECTO = "ingreso"`.

**D-25 · Dónde vive el código.** Las secciones siguen en
`streamlit_app.py`, igual que las otras cinco: moverlas a módulos obligaría a
importar sus ayudantes (`html`, `L`, `cabecera`, `ref`…) desde el script
principal, y Streamlit lo ejecuta como `__main__`. Van a módulos nuevos solo
la lectura del artefacto (`app/contexto.py`: carga tolerante a que falte el
archivo, y `MOSTRAR_LENGUA = False`), el glosario (`app/glosario.py`) y el
mapa (`graficos.mapa_departamentos`, declarado en `GRAFICOS_REQUERIDOS`).
- Descartado: un módulo por sección, por el riesgo de import circular
  descrito arriba.

**D-26 · Portada «Empieza aquí», aterrizaje en dos tiempos.** El primer
pantallazo lleva el titular, tres cifras y el botón del recorrido. Las cifras
son la población y la parte que vive en Lima Metropolitana (estimadas con la
ENAHO, `ui_contexto.peru`, rotuladas así) y la tasa oficial del INEI (ya
citada, `inei_informal`). Debajo va lo demás:
- Qué es un empleo informal, con cuatro personajes **ficticios, rotulados
  como tales**: vendedora de mercado, taxista, agricultor y trabajadora del
  hogar. Cada uno lleva la tasa observada de su rama, leída de
  `ui_artifacts.clasificador.tasas_observadas.rama`. Lo que significa para
  la pensión, la salud y el crédito es cualitativo y sin cifras.
- Por qué importa.
- Qué hace la app: el recorrido guiado, cinco pasos con un botón que abre
  cada pestaña.
- **La comparación con América Latina y la OCDE se omite.** Ninguna cifra
  pasó por `verificar_citas.py`. Queda como pendiente.

**D-27 · Pestaña «Investigación».** Lleva:
- Las cuatro escuelas (Chen 2012, fila 22, verificada), como tarjetas
  comparables. Cada «qué dicen nuestros datos» es **lectura nuestra**, con
  números del artefacto. La legalista se apoya en De Soto (fila 27), que ya
  es «lectura nuestra», y se dice.
- Los análisis de la Fase 3 en capa 1 y capa 2. La brecha de género se
  rotula como hallazgo propio, distinto de Ñopo 2008 (D-23).
- El mapa y la tabla de cruces hallazgo ↔ literatura, con las tres
  etiquetas.
- Ética y límites de la focalización.
- La lengua materna, solo si `MOSTRAR_LENGUA` es verdadera.

**D-28 · Mapa sin JavaScript.** SVG coroplético generado en Python desde
`models/peru_departamentos.geojson`, con proyección equirrectangular
corregida por el coseno de la latitud media. Se cachea con
`st.cache_data`, así que se calcula una vez por proceso. Cinco tramos de
color con los tokens del tema. Hover vía `<title>` (probado: el markdown lo
conserva) y un resaltado CSS. El n de cada departamento va en el título. Al
lado va una tabla accesible con los mismos datos.

**D-29 · Glosario.** Un solo módulo con términos bilingües y una función,
`termino(clave, texto)`, que devuelve un `<span tabindex=0>` con la
definición en un tooltip CSS (`:hover` y `:focus`). Así funciona con
teclado: está probado que `tabindex`, `role` y `title` sobreviven al
saneado. Las definiciones no llevan cifras.

**D-30 · Hilo narrativo y tests.** Ingreso e Informalidad llevan una línea de
cruce con enlace a la pestaña Investigación (`?sec=investigacion`,
`target=_self`), sin reescribir lo que hay. Tests nuevos:
- contrato del mapa;
- la lengua no aparece con la bandera en falso;
- la app no se cae si falta `ui_contexto.json`;
- toda etiqueta «consistente con la literatura» apunta a una referencia con
  `verificacion == "contenido"`.

El README y `CITATION.cff` 1.2.0 se escriben al final, con las cifras ya
fijas.

## Fase 4 · Construcción

**D-31 · La pestaña de portada se llama «Inicio / Start».** Con la activa en
negrita, «Empieza aquí» partía la barra en dos filas a 1366 px, y la
sección que se abría bajaba 48 px. El título de la página sí dice «Empieza
aquí · el Perú en 60 segundos». Medido con `docs/qa/medir_vistazo.py`: las 7
secciones entran en el primer pantallazo a 1366×768, en ES y en EN, con el
h1 a 142 px en todas.
- Revertir: la clave `inicio` en `titulo_corto()`.

**D-32 · Alcance del glosario.** El módulo y sus 14 términos se usan en la
portada y en Investigación, y el glosario completo está en un expander de la
portada. No se sembraron términos en el texto de las cinco pestañas
anteriores: el encargo pide no reescribir lo que ya está bien.
**Propuesta:** marcar RUC, PR-AUC y dependencia parcial en Informalidad,
Ficha y «Cómo se hizo» con `glosario.termino()`, en un commit aparte.

**D-33 · Cuatro referencias nuevas en la app.** Son `chen2012`,
`maloney2004`, `nopo2008` y `nopo_atal_winder2009`. Las cuatro están
verificadas contra texto crudo (filas 22, 28, 37 y 38 de la matriz). Se
agregan al final de `REFERENCIAS`, así que la numeración de las llamadas
existentes no cambia. Un test exige que toda frase «consistente con la
literatura» cite solo referencias con `verificacion == "contenido"`.

**D-34 · Correcciones antes del push (revisión del advisor).**
- El vistazo de Investigación decía «33 % de la brecha de género que no se
  explica», y eso se lee como un tercio de la brecha. En realidad es
  exp(0,286) − 1: una diferencia de pago. Ahora dice «diferencia por hora
  entre hombres y mujeres que no explican educación, experiencia ni lugar».
  La parte no explicada es mayor que el 100 % de la brecha: 28,6 frente a
  26,2 log puntos × 100.
- La cita de Maloney (2004) estaba en la «predicción» de la tarjeta
  voluntarista, pero la fila 28 de la matriz solo verifica que buena parte
  del sector es voluntario. La cita pasa a la descripción. Las cuatro
  predicciones («Predeciría») son derivación nuestra y llevan «lectura
  nuestra». Es el mismo tipo de error que D-23.
- Cada etiqueta va ahora justo después de la frase que rotula. El contraste
  con Psacharopoulos y Patrinos y la diferencia con Ñopo 2008 quedaron
  fuera de la etiqueta «consistente».
- El test de «consistente» ahora también lee las filas de la tabla de
  cruces.
- Los cruces de Ingreso e Informalidad eran enlaces `<a href>`: recargaban
  la página, abrían otra sesión y perdían el perfil. Ahora son botones con
  callback. Probado en Chromium: no recarga, y al volver el perfil sigue ahí.

**D-35 · Alcance de «la parte no explicada supera la brecha» (2026-09-26,
Fase 4, revisión del advisor antes del push).** El README decía que la parte
no explicada era mayor que la brecha «en las seis especificaciones». Los
artefactos dicen otra cosa. Por hora, la brecha es 0,262 y la parte no
explicada es mayor en cinco de las seis variantes: B con referencia mujeres
da 0,250. En el ingreso mensual (brecha 0,415) es menor en las seis
(0,346–0,382).
- Se decidió acotar el enunciado a «por hora, en la especificación
  principal», en tres lugares: el párrafo de contraste de Investigación, la
  fila de la tabla de cruces y el README (ES y EN). En los tres se dice
  también que en el ingreso mensual la parte no explicada es menor.
- Se revisó el contraste con Ñopo (2008) contra la nota verificada en
  `referencias.py`. Perú 1986–2000: brecha de 45 %, de la que 28 puntos no se
  explican. Es menor que el total, así que la etiqueta «hallazgo propio,
  distinto de Ñopo» se mantiene para el resultado por hora. Nuestro Ñopo por
  hora da lo mismo (Δ0 20,6 % > Δ 15,4 %).
- Queda sin verificar contra el texto crudo si Ñopo (2008) usa ingreso por
  hora o mensual. Si fuera mensual, nuestro resultado mensual coincidiría con
  el suyo. Por eso el texto no dice que los resultados se contradigan: dice
  que el patrón por hora es nuestro.
- Descartado: mantener «seis de seis», que es falso, y quitar el contraste,
  que tiene respaldo para el resultado por hora.
- Revertir: `git revert` del commit «D-35».
