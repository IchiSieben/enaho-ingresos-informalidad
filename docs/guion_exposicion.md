# Guion de exposición (10–15 minutos)

> **Qué es este documento y qué no.** El guion lámina a lámina son las **notas
> del orador de `docs/presentacion/ENAHO_exposicion.pptx`**: 18 láminas en las
> que el despliegue es el bloque protagonista, y cada nota prepara la lámina
> siguiente. Esto de aquí es lo otro: la **narrativa de fondo** —de dónde salió
> el proyecto y qué encontró—, la tabla de cifras para tener a mano y las
> preguntas anticipadas con su respuesta. Sirve para preparar y para el turno
> de preguntas, no para leer mientras se pasan las diapositivas.

Estructura: tres actos (~3 minutos cada uno) + las dos lecturas y el cierre.
Cada acto lleva sus números clave y UNA frase sugerida para decirlo. Después:
la tabla de números para tener a mano y las preguntas anticipadas.

---

## La narrativa en tres actos

### Acto 1 — La ecuación inicial y lo que escondía (~min 0–3)

La primera regresión del curso sobre estos datos produjo, en niveles:
INGRESO = 653,35 + **11,47·urbano** + **6,39·hombre** + 16,11·edad + …
(README §1). Once soles por vivir en zona urbana y seis por ser hombre son
incompatibles con las brechas conocidas del mercado laboral peruano. La
decisión que define el proyecto: **ese resultado no se descartó — se
diagnosticó**, reproduciendo la especificación sobre los microdatos reales
del INEI (`reports/00_autopsia_baseline.md`).

> **Frase sugerida:** «Esta ecuación no está mal digitada: está contando una
> historia imposible, y en vez de borrarla decidimos averiguar por qué.»

### Acto 2 — El diagnóstico: centinela y colinealidad (~min 3–6)

Tres causas, por orden de daño (`reports/00_autopsia_baseline.md`):

1. **El centinela 999999.** El INEI codifica «no sabe» como 999999 en
   variables monetarias; leído como ingreso real afecta al 2,28 % de la
   población (1.093 casos). Con centinela: R² **0,023**, urbano
   **−27.141**. Centinela → NaN: R² **0,248**, urbano **+235** — todos los
   signos se vuelven plausibles con un solo cambio.
2. **La colinealidad educativa.** Años de educación y nivel educativo
   detallado son la misma variable codificada dos veces: juntos, VIF de
   15–20 y las dummies cambian de signo (secundaria +588 → −761) sin
   mejorar el ajuste. No conviven en ninguna especificación.
3. **Niveles vs log.** El ingreso tiene asimetría 3,98 (mediana S/ 750 del
   ingreso crudo limpio, p99 S/ 7.000): la familia principal trabaja en
   log(ingreso) y vuelve a soles con la corrección de Duan.

Y el «índice de bienestar» de la consigna resultó circular: su contraparte
real (INGHOG2D) contiene al propio ingreso individual como sumando
(ρ = 0,58). Excluido de todo modelo.

> **Frase sugerida:** «Un solo código de faltante mal leído multiplicaba por
> diez el error de la regresión: la limpieza no fue un trámite, fue el
> hallazgo.»

### Acto 3 — El torneo y el clasificador (~min 6–10)

Nueve especificaciones, mismo split 80/20, misma validación cruzada de 5
pliegues, selección por MAE de CV — nunca por test
(`reports/comparacion_torneo.csv`). Gana **E9 (Gradient Boosting sobre log)**
con MAE_cv S/ 610,9; la mejor lineal interpretable (E6) queda en 690,1. La
brecha de S/ 79 (+11,5 %) estima lo que aportan las no linealidades e
interacciones (Athey & Imbens 2019). Ningún R² supera 0,5 en soles: es el
techo honesto de estos datos, no un defecto.

El clasificador de informalidad (target derivado con la regla del INEI y
validado contra la tasa oficial: 67,3 % reconstruido vs 70,2 % oficial):
GB con PR-AUC_cv **0,9626** sobre un baseline de prevalencia **0,678**;
punto operativo con precisión ≥ 0,90 → umbral 0,605, recall 0,893, **lift
1,33×** (`reports/clasificador_informalidad.md`).

> **Frase sugerida:** «De cada 1.000 trabajadores señalados, 900 son
> efectivamente informales, frente a 678 si señaláramos al azar — ese es el
> número honesto, no el 0,96.»

### Las dos lecturas + cierre del arco (~min 10–13)

- **Predictiva (E9, desplegada):** MAE test S/ 611 sobre mediana S/ 1.101;
  la app muestra la mediana condicional con la advertencia mediana/media
  (smearing ×1,401).
- **Explicativa (E6 ponderada con FAC500A, HC3):** educación **+4,8 %/año**,
  hombre +43 %, urbano +32 %, independiente −50 %, microempresa −33 %,
  minería +74 %, Sierra Norte −31 % (`reports/modelo_explicativo.md`).

> **Frase sugerida:** «No elegimos entre predecir y explicar: entrenamos
> para cada pregunta su modelo, y declaramos cuál responde qué.»

---

## Números para tener a mano

| Cifra | Qué significa en una línea | Si la cuestionan |
|---|---|---|
| **S/ 610,9 / 610,8** (MAE cv/test E9) | Error medio en soles del modelo desplegado | Coinciden casi al sol: no hay sobreajuste del proceso de selección (`reports/comparacion_torneo.csv`). |
| **0,42 / 0,575** (R² soles / log, E9) | Fracción de varianza explicada, en cada escala | No son comparables entre sí. Referencia en LOG: Mincer (1974) 0,285 y Card (1999) 0,247–0,328 (ver pregunta 1). |
| **2,28 % / 1.093** | Población afectada por el centinela 999999 | Documentado en el diccionario del INEI; R² 0,023→0,248 al limpiarlo (`reports/00_autopsia_baseline.md`). |
| **3,98** | Asimetría del ingreso: cola derecha larga | Justifica el target en log y el criterio MAE. |
| **×1,401** | Factor de smearing de Duan: mediana → media | Duan (1983), calculado con residuos out-of-fold de train, nunca test. |
| **13 % bruto (E2) vs 4,8 % neto (E6)** | El retorno a la educación, leído en pareja: bruto = exp(0,1223)−1 de la regresión cruda; neto = con los canales ocupacionales descontados | La brecha ES la respuesta: la educación paga en gran parte vía acceso a mejores empleos; el punto intermedio E4 (sin controles de empleo) da 6,5 % (ver pregunta 5). |
| **S/ 79 (+11,5 %)** | Brecha E6→E9: lo que aportan las no linealidades | Athey & Imbens 2019: es una estimación del límite de la forma funcional lineal, no magia del boosting. |
| **0,9626 / 0,678** | PR-AUC cv del GB / baseline de prevalencia | El mérito es la distancia sobre 0,678, no el 0,96 suelto; sin las 2 variables casi definicionales aún da 0,9415 (`reports/ablacion_clasificador.csv`). |
| **0,605 → 0,900 / 0,893** | Umbral operativo → precisión / recall | Elegido sobre OOF de train; el test lo confirma exactamente (0,900/0,893). |
| **1,33×** | Lift: cuántas veces mejor que señalar al azar | 900 vs 678 de cada 1.000 señalados. |
| **67,3 % vs 70,2 %** | Prevalencia derivada vs oficial INEI 2025 | Sesgo uniforme de ~3 pts explicable por afiliaciones autofinanciadas a pensiones; el gradiente por tamaño va en el mismo sentido que el oficial (el INEI reporta 88,6 % en empresas de 1-10 trabajadores y 15,6 % en las de más de 50; los tramos no son los nuestros, así que coincide la dirección, no cada cifra). |
| **OR 16,7 / OR 0,82** | Chances de informalidad: microempresa / año de educación | Odds, no probabilidades; bases: empresa >500 y comparación por año (`reports/clasificador_informalidad.md`). |
| **47.899 / 38.105 / 9.527** | Población final / train / test | Cascada documentada: 84.853 → 57.716 ocupados → 47.899 con ingreso; el torneo usa 47.632 casos completos. |
| **24,6 %** | Ocupados con pago en especie/autoconsumo, excluido del target | Sensibilidad medida: el premio urbano cae solo de 54,6 % a 52,0 % al incluirlo (`reports/torneo_regresion.md`). |
| **0,0974** | Brier score del clasificador | Menos de la mitad del 0,218 de predecir siempre la prevalencia; probabilidades calibradas → legítimo priorizar con ellas. |

## Preguntas anticipadas

**1. ¿Por qué el R² es "bajo" (0,42)?**
Porque el ingreso individual depende de mucho que ninguna encuesta observa
(habilidad, redes, calidad del empleo). La ecuación de Mincer explica
típicamente entre un 25 % y un 35 % de la varianza del log del salario
(Mincer 1974, cuadro 5.1: 0,285; Card 1999, cuadro 1: 0,247–0,328). Ojo:
ni Lemieux (2006) ni Heckman et al. (2006) reportan un R², así que no se
les cita para esto. Nuestro 0,575 en log está por encima de ese rango
porque añade controles de empleo que una Mincer clásica no lleva. Un R² de 0,8 aquí sería señal de fuga, no de
calidad — lo sabemos porque la variable que "explicaba demasiado"
(INGHOG2D) resultó contener al target (`reports/00_autopsia_baseline.md`).

**2. ¿PR-AUC 0,96 no será leakage?**
Se auditó en tres frentes. Lista negra de todo lo que define el target
(P510A1, P558A*, P511A con AUC univariado 0,846 fuera). Ablación: sin
tamaño de empresa ni categoría — las dos variables más pegadas a la regla —
el PR-AUC sigue en 0,9415 (`reports/ablacion_clasificador.csv`). Y
encuadre: es una herramienta de focalización sobre configuración laboral
observable, no una predicción de evento futuro; en ese régimen, AUC alto es
coherente. Además el gradiente por tamaño replica el patrón oficial del
INEI (que reporta 88,6 % en empresas de 1-10 trabajadores y 15,6 % en las de más de 50; sus tramos no son los nuestros).

**3. ¿Por qué excluiste el ingreso en especie?**
Definición estándar de ingreso monetario, pero no se escondió: el 24,6 % de
los ocupados recibe especie/autoconsumo, y como su exclusión podía inflar
justo el premio urbano de la narrativa, se midió: 54,6 % (solo monetario)
vs 52,0 % (con especie) — 2,6 puntos, conclusiones intactas
(`reports/torneo_regresion.md`, sensibilidad publicada también en la app).

**4. ¿Por qué el torneo no está ponderado?**
Porque compara precisión predictiva intramuestral entre nueve
especificaciones: ponderar cambiaría la pérdida optimizada sin mejorar la
comparación. La lectura poblacional existe y está separada: el modelo
explicativo es WLS con FAC500A (`reports/modelo_explicativo.md`), y los
descriptivos de la app van ponderados. Cada tabla declara cuál es.

**5. ¿Por qué 4,8 % de retorno a la educación si la literatura dice 9–10 %?**
La respuesta completa es la **lectura en pareja**: en nuestros propios
datos, el retorno *bruto* es **13 %** (E2, la regresión cruda de solo
educación: exp(0,1223)−1, `reports/torneo_regresion.md`) y el *neto* es
**4,8 %** (E6, condicionando en categoría ocupacional, tamaño de empresa y
rama, `reports/modelo_explicativo.md`). La brecha entre ambos ES el
hallazgo: esos controles son canales por los que la educación opera —
estudiar más te lleva a mejores empleos, y el 4,8 % es lo que la educación
paga *dentro* del mismo tipo de empleo. El 9–10 % de Psacharopoulos &
Patrinos (2018) es un bruto sin esos controles, perfectamente compatible
con nuestro 13 % bruto; el punto intermedio E4 (6,5 %) completa la
secuencia. No hay discrepancia con la literatura: hay dos preguntas
distintas, cada una con su número.

**6. ¿Por qué la app muestra la mediana y no la media?**
El modelo entrena en log y la inversión directa estima la mediana
condicional — que además es el predictor óptimo bajo MAE, el criterio del
torneo. La media exige la corrección de smearing (×1,401) y la app la
muestra en su propia tarjeta, con la advertencia de que sumar medianas
subestima agregados (`models/feature_schema.json`, nota del smearing).

**7. ¿Por qué quedaron fuera los TFNR?**
Los 6.500 trabajadores familiares no remunerados tienen ingreso cero: no
pueden estar en un modelo de ingreso positivo. Es una restricción de
población declarada, no un error — y por eso la prevalencia del clasificador
(63,7 % ponderada) es menor que la oficial: al reconstruir la tasa sobre
TODOS los ocupados con TFNR:=informal, da 67,3 % vs 70,2 % del INEI
(`reports/01_preparacion_fase1.md`).

**8. ¿Qué pasaría con datos de otro año?**
Todo el flujo es reproducible con una corrida (`docs/arquitectura.md`, §4):
mismos scripts sobre los módulos 02/03/05 del año nuevo. Lo que se espera:
los coeficientes estructurales y el gradiente de informalidad son estables
año a año, así que las conclusiones cualitativas deberían sostenerse; las
métricas puntuales (MAE, umbral operativo) se recalcularían y el precómputo
de UI se negaría a publicar si el nuevo umbral no reprodujera el schema —
el sistema obliga a re-aprobar el punto operativo. La advertencia honesta:
el modelo no está pensado para extrapolar a otro año sin reentrenar; es
transversal, no un pronóstico. Frase de cierre: **«los coeficientes
cambiarían, el método no; la validación temporal está declarada como
trabajo futuro»**.

## Cierre — qué demuestran los dos proyectos juntos (~min 13–15)

Este proyecto es hermano del de **SIS-diabetes** (adherencia al seguimiento
y costo de atención con datos abiertos del SIS). Juntos demuestran **el
mismo método en dominios distintos** (salud pública y mercado laboral):
reproducibilidad total con semilla fija, formulario dirigido por
`feature_schema.json`, precómputo de UI, umbrales elegidos sobre
probabilidades out-of-fold y limitaciones declaradas (README, intro). La
diferencia de ENAHO es que **no muestra solo el modelo ganador: muestra el
camino** — de una ecuación implausible a un torneo de nueve
especificaciones con el diagnóstico como protagonista.

> **Frase de cierre sugerida:** «El método es el mismo en salud y en empleo:
> desconfiar de los números demasiado buenos, declarar cada decisión, y
> dejar que cualquiera pueda reproducir el camino completo — no solo el
> resultado.»
