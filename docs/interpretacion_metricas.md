# Guía de interpretación de métricas

Para el autor al exponer y para cualquier lector técnico. Cada métrica o
concepto sigue la misma estructura de cinco puntos: **(a)** qué es, primero
sin jerga y luego con precisión; **(b)** cómo se calcula en este proyecto;
**(c)** el valor obtenido, con su archivo de origen; **(d)** cómo leerlo —
qué sería mejor, qué sería peor, qué NO significa; **(e)** qué valores es
razonable esperar en este tipo de datos, con la literatura que lo respalda.

Las referencias bibliográficas completas están en el README (§6).

---

## Parte I — Regresión del ingreso

### 1. MAE (error absoluto medio)

**(a)** Cuántos soles se equivoca el modelo, en promedio, sin importar el
signo. Formalmente: la media de |ingreso real − ingreso predicho| sobre los
casos evaluados.

**(b)** `mean_absolute_error(y, pred)` con la predicción invertida a soles
por la mediana (`expm1`), en `src/04_torneo_regresion.py`. Se reporta en dos
sabores: **MAE_cv** (validación cruzada de 5 pliegues en train — el criterio
de selección) y **MAE_test** (el 20 % apartado — la estimación honesta del
modelo ya elegido).

**(c)** E9, el modelo desplegado: MAE_cv **S/ 610,9** y MAE_test
**S/ 610,8** (`reports/comparacion_torneo.csv`), sobre un ingreso con
mediana S/ 1.125 en test (`models/ui_artifacts.json`, bloque
`regresor.ingreso`).

**(d)** Menor es mejor. La referencia sin modelo: la peor especificación del
torneo (E1, solo años de educación) tiene MAE_cv S/ 900,6 — el modelo
completo recorta un tercio de ese error. Que MAE_cv y MAE_test coincidan
casi al sol (610,9 vs 610,8) indica que no hay sobreajuste a los pliegues.
Lo que NO significa: que una predicción individual esté "a S/ 611 del valor
real" — es un promedio; hay perfiles con error mucho mayor (la cola alta) y
mucho menor.

**(e)** El MAE fue el criterio del torneo *porque* el ingreso tiene cola
larga (asimetría 3,98, `reports/00_autopsia_baseline.md`): el MAE pondera
cada sol de error igual, mientras que un criterio cuadrático (RMSE) dejaría
que un puñado de sueldos altísimos dominara la comparación entre modelos.
Con encuestas de hogares, un error medio del orden de la mitad de la mediana
del ingreso es lo habitual, no un defecto (véase el techo de R² en §3;
Sohnesen & Stender 2017).

### 2. RMSE (raíz del error cuadrático medio) y su diferencia con el MAE

**(a)** También mide el error promedio en soles, pero eleva al cuadrado
antes de promediar: los errores grandes pesan desproporcionadamente más.

**(b)** `sqrt(mean_squared_error(...))` en `src/04_torneo_regresion.py`,
calculado sobre la predicción de la **media** (con smearing), que es el
predictor óptimo bajo pérdida cuadrática — igual que el MAE se calcula sobre
la mediana, el predictor óptimo bajo pérdida absoluta.

**(c)** E9: RMSE_test **S/ 1.226,7** (`reports/comparacion_torneo.csv`).

**(d)** El RMSE (1.227) duplica al MAE (611): esa brecha ES la cola larga.
Si los errores fueran simétricos y moderados, ambas cifras se parecerían.
Que el RMSE sea alto no contradice al MAE: dice que los pocos casos que el
modelo falla mucho, los falla por miles de soles (los sueldos extremos son
intrínsecamente impredecibles con 9 variables). NO se debe comparar el RMSE
de un modelo con el MAE de otro: miden pérdidas distintas.

**(e)** En ingresos individuales, RMSE ≈ 2×MAE es típico de una
distribución log-normal-ish; una razón cercana a 1 sería sospechosa (¿se
truncó la cola?) y una razón mucho mayor indicaría outliers sin tratar —
aquí ya tratados vía el centinela → NaN y el target log.

### 3. R² — el tratamiento cuidadoso que merece

**(a)** La fracción de la variación del ingreso que el modelo explica. 0 =
no explica nada más que la media; 1 = explica todo. Formalmente:
1 − (varianza de los residuos / varianza del target).

**(b)** `r2_score` en test (`src/04_torneo_regresion.py`), en **dos escalas
que no deben mezclarse**: `R2_test_soles` (predicción de la media con
smearing contra el ingreso en soles) y `R2_escala_propia` (en la escala en
que cada modelo ajusta: log para E2–E9, niveles para E1/E5).

**(c)** E9: **0,42 en soles** y **0,575 en escala log**
(`reports/comparacion_torneo.csv`).

**(d)** Los dos números son verdaderos a la vez y NO son comparables entre
sí: la varianza del log(ingreso) y la del ingreso en soles son varianzas de
variables distintas. En soles, la cola larga es casi imposible de "explicar"
(unos pocos sueldos de S/ 20.000–31.200 concentran muchísima varianza); en
log, la escala comprime esa cola y el mismo modelo explica más proporción.
Al comparar con otro estudio hay que preguntar SIEMPRE en qué escala
reporta. Lo que NO significa un R² de 0,42: que el modelo "se equivoque el
58 % de las veces" — el R² no es una tasa de acierto.

**(e)** La pregunta inevitable es "¿0,42 no es bajo?". No: **las ecuaciones
de ingreso sobre microdatos de encuestas de hogares rondan R² de 0,25–0,35
en escala log** (las Mincer clásicas: Card 1999; Lemieux 2006; Heckman,
Lochner & Todd 2006 [verificar rango exacto por estudio]), porque el ingreso
individual depende de mucho que ninguna encuesta observa (habilidad, redes,
calidad del empleo, suerte). Nuestro 0,575 en log — con controles de
categoría, tamaño de empresa y rama que una Mincer clásica no lleva — está
en el **rango alto de lo esperable**; el propio torneo lo confirma: la
Mincer clásica E3 da 0,27 en su escala y la depurada E6 0,509
(`reports/comparacion_torneo.csv`). Conclusión explícita para la exposición:
**un R² de 0,8 en estos datos no sería señal de calidad sino de fuga de
información** — la autopsia de este proyecto muestra exactamente eso al
revés: la variable circular INGHOG2D fue excluida precisamente porque
"explicaba" demasiado (`reports/00_autopsia_baseline.md`, §5).

### 4. Transformación log, sesgo de retransformación y smearing de Duan

**(a)** El modelo no predice soles: predice el *logaritmo* del ingreso y
luego se deshace la transformación. El problema: deshacer el log de una
predicción promedio NO devuelve el promedio en soles — devuelve algo más
parecido a la mediana. A eso se le llama sesgo de retransformación.

**(b)** El target se transforma con `log1p` dentro de un
`TransformedTargetRegressor` y se invierte con `expm1`
(`src/04_torneo_regresion.py`): eso da la **mediana condicional**. La
**media condicional** se obtiene multiplicando por el factor de smearing de
Duan (1983): el promedio de `exp(residuo)` calculado con los residuos
**out-of-fold de train** (`src/07_guardar_regresor.py`) — nunca con test,
que no debe tocar ningún número publicado antes de la evaluación final.

**(c)** Factor de smearing de E9: **1,4009**
(`models/feature_schema.json`); MAE de test con la mediana S/ 610,8, con la
media S/ 741,1 (`reports/comparacion_torneo.csv`).

**(d)** Cuándo usar cada una: la **mediana** responde "¿cuánto gana un
trabajador típico con este perfil?" y es el predictor óptimo bajo MAE — por
eso la app la muestra como cifra principal. La **media** responde "¿cuánto
suman/promedian muchos trabajadores con este perfil?" y es la única válida
para agregados: sumar medianas subestima sistemáticamente los totales. Que
el MAE de la media (741) sea peor que el de la mediana (611) no significa
que la media esté "mal": es la consecuencia esperada de evaluar un predictor
de media con una métrica de mediana.

**(e)** Un factor de smearing de 1,3–1,6 es lo normal con residuos log de
ingresos (los del torneo van de 1,401 a 1,607 según la especificación,
`reports/comparacion_torneo.csv`); un factor cercano a 1,0 indicaría
residuos casi sin varianza (sospechoso) y uno mayor a 2 una cola residual
enorme. Referencia: Duan (1983), que propone el estimador precisamente
porque no exige normalidad de los residuos.

### 5. El retorno a la educación: 4,8 %/año frente al 9–10 % de la literatura

**(a)** Cuánto más ingreso se asocia a un año adicional de educación,
manteniendo lo demás constante. En un modelo log-lineal, el coeficiente de
años de educación se convierte a porcentaje con (exp(coef)−1)·100.

**(b)** WLS del modelo E6 ponderada con FAC500A y errores HC3
(`src/05_modelo_explicativo.py`): lectura poblacional, no muestral.

**(c)** **+4,8 % por año** (coef 0,0469, ee 0,0018,
`reports/modelo_explicativo.md`). En el mismo reporte, el E4 — sin
categoría, tamaño de empresa ni dominio — da **+6,5 %**; y en el torneo sin
ponderar, la regresión cruda de solo educación (E2) da un coeficiente de
0,1223 (~13 % aparente, `reports/torneo_regresion.md`).

**(d)** La secuencia 13 % → 6,5 % → 4,8 % no es una contradicción: es el
mismo retorno medido con más o menos canales descontados. Nuestra
especificación E6 condiciona en **categoría ocupacional, tamaño de empresa y
rama — que son CANALES por los que la educación opera**: estudiar más te
lleva a empresas más grandes, a empleos asalariados formales y a ramas mejor
pagadas. El 4,8 % es el retorno **neto de esos canales** (lo que la
educación paga *dentro* del mismo tipo de empleo); el retorno **bruto** —
incluyendo el acceso a mejores empleos — es el que la literatura comparada
reporta en 9–10 %. Es la distinción entre retorno condicional e
incondicional, y es material de primera para la exposición: no elegimos un
número, elegimos qué pregunta responde cada número.

**(e)** Psacharopoulos & Patrinos (2018) sitúan el retorno privado promedio
mundial en torno al 9–10 % por año en especificaciones Mincer básicas; para
el Perú, los trabajos de Yamada (CIES / U. del Pacífico) dan contexto
nacional. Un retorno condicional menor que el bruto es el resultado esperado
cuando se controla por ocupación (Heckman, Lochner & Todd 2006 discuten qué
interpreta cada especificación).

### 6. VIF (factor de inflación de varianza)

**(a)** Mide cuánto se "infla" la incertidumbre de un coeficiente porque su
variable está correlacionada con las demás. VIF 1 = variable independiente
de las otras; VIF alto = la variable es casi combinación de las demás y su
coeficiente se vuelve inestable.

**(b)** `variance_inflation_factor` de statsmodels sobre la matriz de diseño
de cada OLS del torneo (`src/04_torneo_regresion.py`).

**(c)** Con las **convenciones de 5 (alerta) y 10 (problema serio)**: en la
autopsia, años de educación junto a las dummies de nivel educativo disparan
VIF de 15,0–19,5 (`reports/00_autopsia_baseline.md`, §3) — por eso no
conviven en ninguna especificación. En E6, casi todo está por debajo de 4;
las excepciones son `exper` (11,65) y `exper2` (11,59)
(`reports/torneo_regresion.md`).

**(d)** El VIF alto de exper/exper² NO es un problema: un polinomio siempre
correlaciona con su cuadrado, y lo que interesa (la forma de la curva
edad-ingreso) se lee de ambos términos juntos, no de cada coeficiente por
separado. El VIF sí fue diagnóstico en la autopsia: coeficientes que
**cambian de signo** al añadir una variable redundante (secundaria +588 →
−761) sin mejorar el ajuste es la firma de la colinealidad dañina.

**(e)** En especificaciones Mincer, VIF ~10 en el par experiencia/
experiencia² es universal (se puede evitar centrando la variable, sin
cambiar nada sustantivo). El caso extremo del proyecto: la dummy
rama=Servicio doméstico contra categoría=Trabajador del hogar es
**colinealidad perfecta** (VIF infinito) — son la misma partición de la
muestra — y por eso E6 suelta esa dummy (`reports/comparacion_torneo.csv`,
descripción de E6).

### 7. Errores estándar robustos HC3

**(a)** La medida de incertidumbre de cada coeficiente, calculada sin asumir
que la dispersión de los residuos es constante. Si esa dispersión varía con
el nivel de ingreso (y en ingresos siempre varía), los errores estándar
clásicos son demasiado optimistas.

**(b)** Todas las inferencias OLS/WLS del proyecto se ajustan con
`cov_type="HC3"` (`src/04_torneo_regresion.py`,
`src/05_modelo_explicativo.py`), la variante de errores robustos de
Davidson-MacKinnon que es conservadora en muestras con puntos influyentes.

**(c)** Ejemplo: el coeficiente de educación en E6 ponderada es 0,0469 con
ee_HC3 0,0018 (`reports/modelo_explicativo.md`) — un intervalo de ±0,0036,
estrecho gracias a n=47.632.

**(d)** HC3 no cambia los coeficientes, solo su incertidumbre declarada. Con
muestras de este tamaño casi todo sale "significativo": lo informativo no es
el asterisco sino la magnitud del efecto. NO protege contra sesgos de
especificación (variables omitidas, circularidad): solo contra
heterocedasticidad.

**(e)** Con datos de encuestas de ingresos, reportar HC (White) o HC3 es el
estándar; los errores clásicos serían un descuido dado el test de
Breusch-Pagan siguiente.

### 8. Test de Breusch-Pagan

**(a)** Contrasta si la dispersión de los residuos es constante
(homocedasticidad, la hipótesis nula) o depende de las variables del modelo
(heterocedasticidad). Si depende, los errores estándar clásicos no valen y
hay que usar robustos.

**(b)** `het_breuschpagan` de statsmodels sobre los residuos de cada OLS en
train (`src/04_torneo_regresion.py`). Su estadístico es de tipo
**chi-cuadrado** (un multiplicador de Lagrange: n·R² de la regresión
auxiliar de los residuos al cuadrado, con tantos grados de libertad como
regresores); se lee con su p-value: p pequeño → se rechaza la
homocedasticidad.

**(c)** En todas las especificaciones el p-value es minúsculo: E1
p=2,42·10⁻⁶⁹, E4 y E6 p≈0 al límite de la precisión numérica
(`reports/torneo_regresion.md`).

**(d)** Rechazar homocedasticidad aquí NO invalida el modelo: era el
resultado esperado (la varianza del ingreso crece con el ingreso) y la
respuesta correcta es la que se tomó — errores HC3 en toda inferencia. Un
p-value grande habría sido una sorpresa, no una meta.

**(e)** Con n≈38.000 y datos de ingresos, este test rechaza prácticamente
siempre; su papel es documentar formalmente por qué los errores robustos no
son opcionales.

---

## Parte II — Clasificación de empleo informal

### 9. ROC-AUC y PR-AUC

**(a)** Dos resúmenes de qué tan bien ordena el clasificador. **ROC-AUC**:
la probabilidad de que un informal tomado al azar reciba mayor puntaje que
un formal tomado al azar (0,5 = azar, 1 = orden perfecto). **PR-AUC**:
promedio de la precisión a lo largo de todos los niveles de cobertura —
cuánta pureza mantienes mientras vas señalando más casos.

**(b)** `roc_auc_score` y `average_precision_score`
(`src/06_entrenar_clasificador.py`), en validación cruzada sobre train
(criterio de selección) y en test (estimación honesta).

**(c)** Gradient Boosting desplegado: PR-AUC_cv **0,9626** / test
**0,9605**; ROC-AUC_cv **0,9289** / test **0,9274**; la logística baseline
queda en 0,9553 / 0,9526 (`reports/comparacion_clasificador.csv`).

**(d)** **Por qué manda la PR-AUC con clases desbalanceadas:** la ROC-AUC
usa la tasa de falsos positivos, cuyo denominador es la clase minoritaria
aquí irrelevante para la acción; la PR-AUC usa la precisión, cuyo
denominador son los *señalados* — exactamente el costo operativo. Y la
lectura honesta exige el baseline: un clasificador que señalara a **todos**
lograría precisión igual a la prevalencia, **0,678**
(`reports/clasificador_informalidad.md`). El mérito del modelo no es el
0,96 suelto sino la distancia sobre 0,678 — que en el punto operativo se
expresa como **lift 1,33×** (§13): *ese* es el número honesto. Lo que NO
significa: 0,96 no es "96 % de acierto".

**(e)** Con una clase mayoritaria al 68 %, PR-AUC alto es matemáticamente
mucho más fácil que con una clase al 5 %: cualquier comparación con PR-AUC
de otros problemas debe pasar por la prevalencia. Para qué esperar aquí, ver
la sección siguiente.

### 10. Por qué un PR-AUC de 0,96 aquí NO es sospechoso

**(a)** La pregunta de todo revisor: "¿tan alto? ¿no habrá fuga de
información?". La respuesta tiene tres patas: encuadre, ablación y
validación externa.

**(b)** El encuadre está declarado en el schema y la ficha técnica
(`models/feature_schema.json`, clave `encuadre`); la ablación re-entrena el
mismo GB sin las variables casi definicionales
(`src/08_ablacion_clasificador.py`); la validación externa contrasta el
gradiente del modelo con las cifras oficiales del INEI.

**(c)** **Encuadre:** el clasificador NO predice el futuro — identifica la
**configuración laboral asociada a la informalidad** (tamaño de empresa,
categoría, rama), que se conoce al mismo tiempo que el estatus. Es una
herramienta de **focalización**: encontrar segmentos donde concentrar
programas de formalización desde variables observables en registros
administrativos, sin verificar caso a caso la afiliación a pensiones. La
informalidad no es un evento aleatorio futuro: es casi una propiedad
estructural del puesto — y un modelo que la reconoce bien es coherente, no
sospechoso. **Ablación que lo acota:** sin `tamano_empresa`, PR-AUC_cv
0,9571; sin `tamano_empresa` ni `categoria`, **0,9415**
(`reports/ablacion_clasificador.csv`) — educación, área, rama y horas
sostienen la señal restante, así que el 0,96 no colgaba de una variable
tramposa. **Validación externa:** el gradiente por tamaño de empresa del
modelo replica el patrón oficial del INEI 2025 — 88,6 % de informalidad en
empresas de 1–10 trabajadores, 44 % en 11–50, 15,6 % en >50
(`reports/clasificador_informalidad.md`).

**(d)** Qué SÍ sería sospechoso: usar como predictor una variable que
*define* el target (P510A1 registro SUNAT, P558A* pensiones, y P511A
contrato con AUC univariado 0,846) — todas están prohibidas
(`reports/01_preparacion_fase1.md`). El caso gris declarado: `categoria`
(P507) **ramifica la propia definición del target** (independiente→regla
del RUC, dependiente→regla de pensiones); no lo determina por sí sola (AUC
univariado 0,805) pero su importancia alta es **por construcción**, no un
hallazgo.

**(e)** En problemas de focalización con variables estructurales, AUC altos
son la norma; en problemas de *predicción de eventos futuros* (impago,
abandono), un 0,96 sí exigiría buscar fuga. Saber en cuál de los dos
regímenes está tu problema es la lección exportable.

### 11. Calibración y Brier score

**(a)** Un modelo está **calibrado** si sus probabilidades significan lo que
dicen: de los casos a los que asigna 70 %, alrededor del 70 % son
efectivamente informales. El **Brier score** es el error cuadrático medio de
las probabilidades contra el resultado 0/1: mezcla calibración y capacidad
de discriminar en un solo número (menor = mejor).

**(b)** `calibration_curve`/bins en test y `brier_score_loss`
(`src/06_entrenar_clasificador.py`, `src/09_precomputar_ui.py`).

**(c)** Brier del GB en test: **0,0974**
(`reports/comparacion_clasificador.csv`). La curva de calibración va pegada
a la diagonal: en el bin más poblado, probabilidad media 0,966 y frecuencia
observada 0,971; en el más bajo, 0,054 vs 0,035
(`models/ui_artifacts.json`, bloque `calibracion`).

**(d)** La referencia: un "modelo" que asignara a todos la prevalencia
(0,678) tendría Brier = 0,678·(1−0,678) ≈ 0,218 — el GB lo reduce a menos de
la mitad. **Por qué importa:** la calibración es lo que **legitima usar las
probabilidades para priorizar**. El umbral de la app, el panel "de cada
1.000" y los presets solo tienen sentido si un 0,70 se comporta como un 70 %
real; con probabilidades descalibradas, el ranking podría servir pero los
números absolutos serían ficción. Lo que NO garantiza la calibración:
que el modelo discrimine bien (un modelo que asigna 0,678 a todos está
perfectamente calibrado y es inútil) — por eso se mira junto con la PR-AUC.

**(e)** Los métodos de boosting tienden a salir razonablemente calibrados
sin post-procesamiento; los bosques aleatorios suelen comprimir hacia el
centro. Con n de test de 9.527 los bins de calibración son estables.

### 12. Odds ratios de la regresión logística

**(a)** El odds ratio (OR) de una variable dice por cuánto se multiplican
las *chances* (probabilidad/(1−probabilidad)) de ser informal al pasar de la
categoría base a esa categoría, con lo demás constante. OR > 1 = más
propensión; OR < 1 = menos; OR = 1 = sin asociación.

**(b)** exp(coeficiente) de una logística de statsmodels ajustada en train
con las variables sin estandarizar (`src/06_entrenar_clasificador.py`);
bases: Mujer, Rural, Lima Metropolitana, Comercio, empresa >500, Empleado.

**(c)** Los dos protagonistas: empresa **Hasta 20 personas, OR 16,7** (IC95
14,4–19,3) frente a >500; y **años de educación, OR 0,82** por año (IC95
0,81–0,83). Otros: independiente 5,2, administración pública 5,9, área
urbana 0,56, hombre 0,67 (`reports/clasificador_informalidad.md`).

**(d)** Lecturas correctas: trabajar en una microempresa multiplica por
16,7 las *chances* — no la probabilidad — de informalidad respecto de una
empresa grande; cada año de educación multiplica las chances por 0,82, es
decir las reduce un 18 % (y once años de secundaria completa las dividen
por ~0,82¹¹ ≈ 0,11). Cuando la probabilidad base es alta (aquí 0,68), un OR
grande NO se traduce en un multiplicador igual de grande de la
probabilidad: las chances crecen mucho más deprisa que la probabilidad, que
está acotada en 1. La relación con los coeficientes es directa: OR =
exp(coef); coeficiente positivo ⇔ OR > 1.

**(e)** El patrón replica la historia conocida del mercado laboral peruano
(informalidad concentrada en microempresas, independientes y baja
educación; menor en Lima y en empleo asalariado grande) — que la logística
baseline la cuente igual que el GB es en sí una validación: la señal es
estructural, no un artefacto del algoritmo. La sorpresa aparente de
administración pública (OR 5,9) se lee contra su base (Comercio) y junto a
su peso pequeño en la población (4,4 % ponderado,
`models/ui_artifacts.json`).

### 13. Selección de umbral con probabilidades out-of-fold

**(a)** El clasificador entrega una probabilidad; para *actuar* hay que
elegir desde qué valor se señala un caso. Ese umbral se eligió sobre
probabilidades **out-of-fold** (OOF): cada caso de train evaluado por un
modelo que no lo vio al entrenarse.

**(b)** `cross_val_predict(..., method="predict_proba")` sobre train; los
candidatos (0,5, F1 óptimo, precisión ≥ 0,90/0,85/0,80) se tabulan con su
precisión, recall, lift y señalados por 1.000
(`src/06_entrenar_clasificador.py`). El test se usa una sola vez, para
confirmar el punto ya elegido.

**(c)** Punto operativo aprobado: **precisión ≥ 0,90 para la clase
informal** → umbral **0,6054**, recall 0,893, lift 1,33, 673 señalados por
1.000 (`models/feature_schema.json`). Aplicado al test: precisión 0,900,
recall 0,893 (`reports/clasificador_informalidad.md`) — el punto se
sostiene exactamente.

**(d)** **Por qué nunca sobre test:** elegir el umbral mirando el test sería
usar el conjunto de evaluación como conjunto de decisión — la cifra final
quedaría inflada por construcción y ya no habría con qué estimar
honestamente. Es la misma disciplina que seleccionar modelos por MAE_cv y no
por MAE_test. **Qué significa el punto operativo:** de cada 1.000
trabajadores señalados, 900 son efectivamente informales, frente a 678 si se
señalara al azar; el precio es dejar pasar el 10,7 % de los informales
(recall 0,893). Otro criterio (F1, más cobertura) es legítimo: por eso la
app expone los presets en vez de esconder la decisión.

**(e)** En problemas de focalización con presupuesto limitado, fijar la
precisión y maximizar el recall sujeto a ella (lo que hace el código) es la
formulación natural; el "0,5 por defecto" no corresponde a ninguna decisión
de costo y solo figura como referencia.

### 14. Importancia por permutación vs por impureza

**(a)** ¿Qué variables importan al modelo? La importancia **por
permutación** desordena una variable y mide cuánto empeora una métrica real
en datos apartados. La importancia **por impureza** (la nativa de los
árboles) suma cuánto usó el modelo cada variable al construirse — mide uso,
no utilidad.

**(b)** `permutation_importance` con scoring `average_precision` para el
clasificador (validación apartada de train,
`src/06_entrenar_clasificador.py`; test en
`src/09_precomputar_ui.py`) y `neg_mean_absolute_error` para el regresor
(test, 5 repeticiones, `src/09_precomputar_ui.py`).

**(c)** Clasificador (caída de PR-AUC): tamano_empresa 0,047, categoria
0,031, anios_educ 0,024, rama 0,016
(`reports/clasificador_informalidad.md`). Regresor (aumento del MAE):
categoria S/ 139, anios_educ S/ 128, tamano_empresa S/ 69, horas S/ 65,
edad S/ 56, área S/ 6,4 (`models/ui_artifacts.json`,
`importancia_permutacion`).

**(d)** **Por qué se usa la primera:** la impureza está sesgada hacia
variables de alta cardinalidad, se mide sobre el propio train y no dice
nada de la métrica que importa. La permutación se evalúa en datos que el
modelo no memorizó y en la métrica operativa. **Su limitación, declarada:**
con variables **correlacionadas**, permutar una mientras la otra sigue
intacta subestima a ambas — el modelo compensa con la gemela. Aquí aplica:
área aparece con S/ 6,4 no porque el territorio no importe, sino porque
dominio, rama y tamaño de empresa ya llevan casi toda esa información. Y la
importancia alta de `categoria` en el clasificador es por construcción
(§10d), no un hallazgo.

**(e)** Referencia general del contraste entre ambas: Athey & Imbens (2019)
sobre la lectura causal-descriptiva de estos diagnósticos; la documentación
de scikit-learn advierte formalmente el sesgo de la impureza y el efecto de
la correlación.

---

## Parte III — Conceptos transversales

### 15. Ponderación con el factor de expansión (FAC500A)

**(a)** La ENAHO no es un censo: cada encuestado "representa" a un número
distinto de peruanos. El factor de expansión FAC500A dice a cuántos. Sin él,
los promedios describen la muestra; con él, describen la población.

**(b)** FAC500A viene en el CSV del INEI **con coma decimal** y se convierte
al leer (`src/03_fase1_preparacion.py`). Se usó en: prevalencias
poblacionales, percentiles de cohorte y comparables de la app
(`src/09_precomputar_ui.py`) y el modelo explicativo (WLS,
`src/05_modelo_explicativo.py`). NO se usó en: el torneo, el entrenamiento
de los modelos predictivos ni sus métricas.

**(c)** El efecto se ve en la prevalencia de informalidad: 0,678 muestral
vs 0,641 ponderada (`models/feature_schema.json`) — la muestra
sobre-representa segmentos más informales que su peso poblacional.

**(d)** **Por qué la separación:** el torneo compara la *precisión
predictiva intramuestral* de nueve especificaciones — ponderar cambiaría la
pérdida que se optimiza sin mejorar la comparación, y las métricas dejarían
de ser errores por individuo evaluado. Las *lecturas poblacionales*
(coeficientes del modelo explicativo, medianas de cohorte, prevalencias) sí
deben hablar del Perú, no de la muestra: van ponderadas. Cada tabla del
proyecto declara cuál es. Mezclarlas — comparar un MAE muestral con una
mediana ponderada como si fueran del mismo universo — es el error a evitar.

**(e)** Es la práctica estándar en la literatura de ML sobre encuestas de
hogares (Sohnesen & Stender 2017 entrenan sin ponderar y reportan
poblacionalmente).

### 16. Validación cruzada y la distinción MAE_cv vs MAE_test

**(a)** La validación cruzada (CV) parte el conjunto de entrenamiento en 5
pliegues: cada modelo se evalúa 5 veces sobre datos que no vio, sin gastar
el test. **MAE_cv** es esa estimación; **MAE_test** es la del 20 % apartado
que ningún proceso de decisión tocó.

**(b)** `KFold(5, shuffle, random_state=42)` compartido por todo el torneo
y el clasificador; `cross_val_predict` produce las predicciones out-of-fold
de las que salen MAE_cv, el smearing y los umbrales
(`src/04_torneo_regresion.py`, `src/06_entrenar_clasificador.py`).

**(c)** E9: MAE_cv 610,9 → MAE_test 610,8; GB clasificador: PR-AUC_cv
0,9626 → test 0,9605 (`reports/comparacion_torneo.csv`,
`reports/comparacion_clasificador.csv`).

**(d)** **La selección usa CV; el test solo estima.** Elegir entre nueve
especificaciones por su MAE de test sería *seleccionar sobre el conjunto de
evaluación*: el ganador lo sería en parte por suerte en ese 20 % y su cifra
final quedaría sesgada al optimismo. Con la disciplina correcta, el test se
mira una vez, después de decidir todo (modelo, hiperparámetros, umbral). Que
cv y test casi coincidan aquí es la señal de que la disciplina funcionó; una
brecha grande habría delatado sobreajuste del proceso de selección.

**(e)** La brecha esperable cv→test crece con cuántas decisiones se tomaron
mirando la cv; con 9 especificaciones y grillas modestas, décimas de sol o
milésimas de AUC son lo normal.

### 17. Fuga de información: los tres casos concretos de este proyecto

Un catálogo de patrones — cada uno con su detección y su regla.

1. **El centinela 999999 (fuga de código de faltante a valor).** El INEI
   codifica «no sabe» como 999999 en variables monetarias. Leído como
   ingreso real, el 2,28 % de la población (1.093 casos) pasó a "ganar" un
   millón de soles: R² 0,023 y coeficientes absurdos (urbano −27.141);
   convertido a NaN, R² 0,248 y todos los signos plausibles
   (`reports/00_autopsia_baseline.md`). **Patrón:** siempre cruzar el
   diccionario de la fuente antes de modelar; un R² que se multiplica por 10
   con una sola regla de limpieza es la firma de un centinela.
2. **INGHOG2D, la variable circular.** El "índice de bienestar" de la
   consigna corresponde al ingreso del hogar — que **contiene al propio
   ingreso individual como sumando** (ρ de Spearman 0,575; 0,619 per
   cápita). Predecir el ingreso con una suma que lo incluye es circularidad
   mecánica: excluida de todo modelo, junto con sus derivadas GASHOG2D
   (post-tratamiento) y POBREZA (`reports/00_autopsia_baseline.md`, §5).
   **Patrón:** ante una variable "demasiado buena", perseguir su fórmula de
   construcción hasta la fuente.
3. **Las variables definicionales del clasificador.** El target `informal`
   se deriva de P510A1 (RUC) y P558A5 (pensiones): esas columnas y sus
   hermanas (P510B, P517B1, P558A1–A4) están prohibidas como predictoras, y
   P511A (tipo de contrato) se excluyó por ser casi-definición para
   asalariados (AUC univariado 0,846,
   `reports/01_preparacion_fase1.md`). El control se hizo con un **AUC
   univariado** por candidata antes de entrenar. **Patrón:** con targets
   derivados, lista negra explícita de todo lo que participa en la regla, y
   un umbral de sospecha para lo que se le parezca; lo que se queda en zona
   gris (categoría, AUC 0,805) entra con advertencia documentada.

### 18. Glosario de una línea

- **Asimetría (skewness):** cuánto se estira una distribución hacia un lado; el ingreso limpio tiene 3,98 — cola derecha larga (`reports/00_autopsia_baseline.md`).
- **Percentil:** el valor debajo del cual cae un porcentaje dado; p99 = S/ 7.000 significa que el 99 % gana menos de eso.
- **Mediana / media:** el valor del caso del medio / el promedio; en distribuciones asimétricas la media supera a la mediana.
- **Dummy:** variable 0/1 que codifica una categoría (urbano = 1 si el área es urbana).
- **Categoría base:** la categoría omitida contra la que se leen las dummies (aquí: Mujer, Rural, Lima Metropolitana, Comercio, empresa >500, Empleado).
- **Colinealidad:** cuando unas variables son casi combinación de otras; **perfecta** cuando lo son exactamente (rama Servicio doméstico ↔ categoría Trabajador del hogar), y entonces algún coeficiente no puede estimarse.
- **VIF:** medida de colinealidad por variable; alertas convencionales en 5 y 10.
- **Chi-cuadrado:** familia de distribuciones con la que se leen muchos estadísticos de contraste (Breusch-Pagan entre ellos); "estadístico tipo chi-cuadrado" = se compara contra esa distribución para obtener el p-value.
- **p-value:** probabilidad de ver un resultado tan extremo como el observado si la hipótesis nula fuera cierta; pequeño = evidencia contra la nula, no "probabilidad de que la nula sea falsa".
- **IC95:** rango que, con el procedimiento repetido, contendría el valor verdadero el 95 % de las veces.
- **OLS / WLS:** regresión lineal por mínimos cuadrados ordinarios / ponderados (aquí, ponderados por FAC500A).
- **Log / log1p / expm1:** logaritmo natural; log1p(x)=log(1+x) tolera ceros; expm1 lo invierte.
- **Out-of-fold (OOF):** predicción de un caso hecha por el modelo del pliegue que no lo contuvo: simulación honesta de datos nuevos dentro de train.
- **Prevalencia:** proporción de la clase positiva (informal): 0,678 muestral, 0,641 ponderada.
- **Lift:** precisión del modelo dividida por la prevalencia: cuántas veces mejor que señalar al azar (1,33× en el punto operativo).
- **Precisión / recall:** de los señalados, cuántos son positivos reales / de los positivos reales, cuántos fueron señalados.
- **F1:** media armónica de precisión y recall; su óptimo aquí está en umbral 0,432.
- **Umbral / punto operativo:** probabilidad a partir de la cual se señala / el umbral elegido con un criterio explícito (0,6054, precisión ≥ 0,90).
- **Factor de expansión:** a cuántas personas representa cada encuestado (FAC500A).
- **Experiencia potencial:** edad − años de educación − 6, truncada en 0; sobreestima la real en baja educación (Heckman, Lochner & Todd 2006).
- **Smearing (Duan):** corrección multiplicativa (aquí ×1,401) para recuperar la media en soles tras predecir en log.
- **TFNR:** trabajadores familiares no remunerados; 6.500 excluidos de la población por ingreso cero (restricción de población, no error).
- **Centinela:** código numérico que significa "dato faltante" (999999 del INEI); debe convertirse a NaN antes de todo cálculo.
- **Leakage (fuga):** cualquier vía por la que información del target se cuela en los predictores o en las decisiones de evaluación; ver §17.
- **Ablación:** re-entrenar quitando variables para medir cuánto de la métrica depende de ellas.
- **Dependencia parcial:** efecto promedio de una variable sobre la predicción, con el resto de la población promediada.
- **Brier score:** error cuadrático medio de las probabilidades contra el resultado 0/1; 0,097 aquí vs 0,218 de predecir siempre la prevalencia.
- **Estratificación:** partir train/test conservando la proporción de clases del target.
- **Pipeline:** cadena preprocesamiento+modelo empaquetada, para que imputación y escalado se ajusten solo con datos de entrenamiento en cada pliegue.
