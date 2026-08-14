# Manual de usuario — Ingreso laboral e informalidad (ENAHO 2025)

**App en vivo:** https://enaho-ingresos-informalidad.streamlit.app

Este manual está escrito para alguien que abre la aplicación sin saber nada
del proyecto. No necesitas conocimientos de estadística: cada salida de la
app se explica aquí en lenguaje llano.

---

## 1. Qué es esta herramienta — y qué NO es

**Qué es.** Una demostración interactiva de dos modelos estadísticos
entrenados sobre los microdatos públicos de la Encuesta Nacional de Hogares
del Perú (ENAHO 2025, INEI):

- Un **estimador del ingreso laboral mensual**: dado un perfil de trabajador
  (educación, edad, horas, sector, etc.), estima cuánto gana al mes un
  trabajador *típico* con ese perfil.
- Un **clasificador de empleo informal**: para el mismo tipo de perfil,
  estima la probabilidad de que ese empleo sea informal (sin RUC si es
  independiente; sin afiliación a pensiones si es dependiente).

**Qué NO es.**

- **No predice el futuro de una persona concreta.** Los modelos describen
  patrones de una encuesta: dicen cómo le va *en promedio* a la gente con un
  perfil, no cómo te irá a ti.
- **No es un instrumento de fiscalización laboral.** Que un perfil salga
  "señalado" por el clasificador significa que su *configuración de empleo*
  (tamaño de empresa, categoría, rama) es de las asociadas a la informalidad
  — no es un veredicto sobre ninguna persona ni empresa.
- **No liquida sueldos.** El error típico del estimador de ingreso es de
  S/ 611 (MAE de test, `reports/comparacion_torneo.csv`): sirve para ordenar
  y comparar perfiles, no para calcular cuánto debería pagarse a alguien.

## 2. Las cuatro secciones

La barra lateral izquierda tiene cuatro botones de navegación, un enlace al
código en GitHub y un interruptor de **tema claro/oscuro**.

| Sección | Qué hace |
|---|---|
| **Estimación de ingreso** | Llenas un perfil y obtienes el ingreso mensual típico estimado, con su contexto (mediana poblacional, casos comparables). |
| **Empleo informal** | El mismo perfil produce una probabilidad de empleo informal, con un umbral ajustable que muestra las consecuencias operativas de cada elección. |
| **Torneo de modelos** | La historia del proyecto: cómo una regresión inicial con resultados implausibles se diagnosticó y se convirtió en un torneo de nueve modelos. |
| **Ficha técnica** | Las métricas, la validación, las limitaciones declaradas y la procedencia de los datos. |

## 3. Cómo llenar el formulario

Ambas secciones de estimación usan el mismo formulario. Cada campo sale del
contrato del modelo (`models/feature_schema.json`); ninguno está inventado
por la interfaz.

| Campo | Cómo llenarlo |
|---|---|
| **Años de educación aprobados** (0–18) | Años de estudio completados: primaria completa = 6, secundaria completa = 11, técnica completa = 14, universitaria completa = 16, posgrado = 18. Valor inicial: 11. |
| **Edad** (14–80) | Edad en años. El formulario se detiene en 80 aunque la encuesta llega a 95: el modelo se entrenó con los datos intactos, pero el formulario no ofrece valores extremos poco plausibles. |
| **Horas trabajadas por semana** (4–84) | Suma de TODAS las ocupaciones (principal + secundarias). La mediana de la encuesta es 46 h/semana (`reports/01_preparacion_fase1.md`). |
| **Sexo** | Hombre / Mujer (categorías de la encuesta). |
| **Área de residencia** | Urbana / Rural. |
| **Dominio geográfico** | Una de las 8 regiones del diseño muestral del INEI (Lima Metropolitana, tres costas, tres sierras, Selva). |
| **Rama de actividad** | El sector de la ocupación principal, agrupado en 13 grandes ramas (Comercio, Agropecuario y pesca, Manufactura…). |
| **Tamaño de la empresa** | Cuántas personas trabajan en la unidad: Hasta 20 / 21 a 50 / 51 a 100 / 101 a 500 / Más de 500. |
| **Categoría ocupacional** | Empleado / Obrero / Independiente / Empleador / Trabajador del hogar. |

**La experiencia no se digita.** Debajo del formulario verás "Experiencia
potencial derivada: X años". La app la calcula sola como
*edad − años de educación − 6* (truncada en 0), la aproximación estándar de
la economía laboral. Digitarla a mano sería redundante y podría contradecir
a la edad y educación que ya escribiste.

Antes de pulsar el botón de estimar, el panel derecho muestra unos
**situadores de cohorte**: barras horizontales que ubican tu valor (punto de
color) frente a la distribución de los trabajadores de la encuesta — la
banda gruesa cubre del percentil 25 al 75 y la marca vertical es la mediana.
Sirven para saber si el perfil que estás armando es común o raro.

## 4. Cómo leer la estimación de ingreso

Al pulsar «Estimar ingreso» aparecen hasta cuatro tarjetas:

1. **Ingreso típico estimado (mediana).** La cifra principal. Es el ingreso
   del trabajador *mediano* con ese perfil: la mitad de los trabajadores
   comparables gana menos y la otra mitad gana más.
2. **Ingreso esperado (media, smearing).** El *promedio* para ese perfil,
   siempre mayor que la mediana (×1,401, la corrección de Duan del modelo,
   `models/feature_schema.json`). ¿Por qué son distintas? Porque los ingresos
   son muy desiguales: unos pocos sueldos altos jalan el promedio hacia
   arriba, pero no mueven a la persona del medio.
3. **Mediana poblacional: S/ 1.203** (`models/ui_artifacts.json`, ponderada
   con el factor de expansión de la encuesta). El punto de referencia: si la
   estimación de tu perfil está por encima o por debajo de esto, ya sabes de
   qué lado de la población cae.
4. **Casos comparables (p25–p75).** El rango donde gana el 50 % central de
   los trabajadores *reales* de la encuesta con tu mismo sexo, área y banda
   educativa (bandas: 0–6, 7–11, 12–14 y 15+ años de educación). Ejemplo:
   para hombre, urbano, 15+ años de educación el rango es
   S/ 1.521 – S/ 3.994 con mediana S/ 2.597 (`models/ui_artifacts.json`).
   **Cómo interpretarlo:** si la estimación puntual cae dentro de ese rango,
   es un perfil corriente; el ancho del rango te recuerda cuánta variación
   real existe incluso entre personas "iguales" en el papel.

**¿Cuál mirar, mediana o media?** Para responder "¿cuánto gana alguien así?"
mira la **mediana** (por eso es la tarjeta principal). Para presupuestar o
agregar sobre muchos trabajadores, la **media**.

**La advertencia de los agregados.** La app avisa que sumar las
estimaciones principales (medianas) de muchos perfiles **subestima** el
total: en una distribución tan asimétrica la mediana está siempre por debajo
de la media, y los totales se construyen con medias. Si necesitaras un
agregado, tendrías que sumar la segunda tarjeta, no la primera.

Debajo aparece **"Qué determina el ingreso estimado"**: barras con cuánto
empeora el modelo (en soles de error) al desordenar cada variable. Las que
mandan son la categoría ocupacional (S/ 139) y los años de educación
(S/ 128); el área de residencia por sí sola aporta poco (S/ 6,4)
(`models/ui_artifacts.json`) — porque su efecto ya viaja en parte dentro de
rama, tamaño de empresa y dominio.

## 5. Cómo leer la sección de empleo informal

### El medidor de probabilidad

Tras pulsar «Estimar probabilidad» aparece un arco semicircular con un
número grande: la **probabilidad estimada de que un empleo con ese perfil
sea informal**. Un 75 % significa: *de cada 100 trabajadores de la encuesta
con este perfil, unos 75 tienen empleo informal*. No significa "75 % seguro
sobre esta persona". Las probabilidades del modelo están **calibradas** (los
porcentajes se cumplen en los datos: ver Ficha técnica), así que el número
se puede leer literalmente como una frecuencia.

Sobre el arco hay dos marcas: la línea del **umbral** vigente y, detrás,
unas barras grises con la distribución de la cohorte (dónde cae la mayoría
de los trabajadores). Si la probabilidad supera el umbral, el perfil queda
**señalado para focalización** (mensaje ámbar); si no, "sin señal" (verde).

### Los preajustes de umbral

El umbral decide desde qué probabilidad un perfil queda señalado. Hay tres
preajustes y un modo libre (todos los números vienen de
`models/feature_schema.json`):

| Preajuste | Umbral | Qué prioriza | Cuándo usarlo |
|---|---|---|---|
| **Punto operativo ★** | 0,605 | Que los señalados de verdad lo sean: precisión 90 %, deteniendo el 89,3 % de los informales | El aprobado del proyecto: cuando equivocarse al señalar tiene costo (visitas, programas con cupo). |
| **Neutro 0,5** | 0,500 | El punto "ingenuo" de referencia | Solo como comparación: nadie eligió este número, es el default matemático. |
| **Máx. F1** | 0,432 | El mejor equilibrio conjunto precisión/cobertura (F1 0,906) | Cuando ambos errores pesan igual. |
| **Umbral libre** | 0,01–0,99 | Lo que tú quieras explorar | Para ver cómo se mueven los números del panel de impacto. |

Al **bajar** el umbral señalas a más gente: atrapas más informales (sube el
recall) pero también señalas a más formales por error (baja la precisión).
Al **subirlo**, lo contrario. No hay umbral "correcto": hay costos distintos
de cada error, y por eso la app te deja verlos.

### El panel «de cada 1.000 evaluados…»

Este panel traduce el umbral a consecuencias concretas. **De dónde salen los
números:** de los 38.105 trabajadores del conjunto de entrenamiento, con
probabilidades *out-of-fold* (cada trabajador fue evaluado por una versión
del modelo que no lo vio al entrenarse — la simulación honesta de "datos
nuevos"), reescalados a 1.000 (`models/ui_artifacts.json`, bloque
`curva_umbral`). No son cifras del mismo conjunto donde se midió la nota
final del modelo, así que no están infladas.

Con el punto operativo (0,605): de cada 1.000 evaluados se señalan **673**;
de cada 1.000 *señalados*, **900** son efectivamente informales (frente a
678 si señalaras al azar); y quedan sin señalar unos 72 informales por cada
1.000 evaluados. La matriz de cuatro celdas de abajo muestra las mismas
cuentas: señalados con razón, señalados innecesarios, informales sin señalar
y formales sin señalar.

### «Cómo pesa cada variable»

Los gráficos finales muestran el efecto marginal de cada variable sobre la
probabilidad (con el resto de la población promediada). Verás que **tamaño
de empresa** domina: pasar de "Más de 500" a "Hasta 20" mueve la
probabilidad promedio de 0,27 a 0,75 (`models/ui_artifacts.json`). Ojo a la
nota de la app: la **categoría ocupacional** pesa mucho *por construcción*
(la propia definición de informalidad se bifurca según seas independiente o
dependiente), no porque sea un hallazgo.

## 6. Preguntas frecuentes

**¿Por qué al cambiar solo la edad casi no cambia el ingreso estimado?**
Porque la edad no es lo que más pesa. Al desordenar variables, la categoría
ocupacional y la educación le cuestan al modelo S/ 139 y S/ 128 de error
extra; la edad, S/ 56, y la experiencia derivada apenas S/ 10–12
(`models/ui_artifacts.json`). Además el efecto de la edad se aplana: el
ingreso estimado sube con fuerza hasta los ~45 años y de ahí en adelante el
perfil es casi plano. Cambiar la edad de 50 a 60 mueve poco porque en los
datos reales también mueve poco.

**Puse mi propio perfil y el número no se parece a mi sueldo. ¿Está roto?**
No. El error típico es S/ 611 y la cifra es la *mediana* de un grupo, no tu
caso. Dos personas idénticas en estas 9 variables pueden ganar muy distinto
(mira el ancho del rango p25–p75 de comparables). El modelo ordena perfiles;
no adivina personas.

**¿Por qué la app muestra la mediana y no la media?**
Porque el modelo se entrena con el logaritmo del ingreso (los ingresos son
muy asimétricos) y al deshacer esa transformación lo que se obtiene
directamente es la mediana. La media exige una corrección adicional
(smearing de Duan, ×1,401) que la app muestra en su propia tarjeta. Además,
para la pregunta "¿cuánto gana alguien así?", la mediana es la respuesta
menos engañosa.

**Me salió "perfil señalado". ¿Eso dice que soy un trabajador informal?**
No. Dice que tu *configuración de empleo* (tamaño de empresa, categoría,
rama…) es de las que en la encuesta están mayoritariamente asociadas a
empleo informal. Es una herramienta para focalizar programas de
formalización por segmentos, no para etiquetar personas.

**¿Por qué no puedo escribir mis años de experiencia?**
Porque la app usa la *experiencia potencial* (edad − educación − 6), que se
deriva sola de dos campos que ya llenaste. Pedírtela otra vez permitiría
combinaciones imposibles (más experiencia que años de vida adulta) y no
añadiría información al modelo.

**¿El ingreso estimado incluye propinas, pagos en especie o autoconsumo?**
No: el modelo estima solo el ingreso **monetario**. El 24,6 % de los
ocupados recibe parte de su pago en especie o autoconsumo
(`reports/01_preparacion_fase1.md`) — sobre todo en el agro rural — y eso
queda fuera del número que ves. El proyecto midió que esta exclusión no
distorsiona las conclusiones (sección Torneo de la app).

**¿Por qué el ingreso estimado "típico" parece bajo comparado con los
sueldos de Lima?**
Porque la referencia es todo el Perú ocupado con ingreso, cuya mediana
ponderada es S/ 1.203 al mes (`models/ui_artifacts.json`) — incluye
trabajadores rurales, independientes y a tiempo parcial. Un perfil urbano,
educado y asalariado estimará muy por encima de esa cifra.

**¿Puedo usar esto para decidir una contratación, un sueldo o una
inspección?**
No. Es una herramienta demostrativa con fines académicos sobre microdatos
públicos. No certifica la situación de ninguna persona ni empresa, y sus
salidas son promedios poblacionales con incertidumbre declarada.
