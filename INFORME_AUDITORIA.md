# Informe de auditoría — ENAHO 2025: ingreso laboral e informalidad

Auditoría interna del repositorio `enaho-ingresos-informalidad` realizada
entre el 18 y el 20 de agosto de 2026 sobre el commit `cf86e8e` y
posteriores.

**Regla que gobierna este informe:** ningún número sale de memoria ni de
razonamiento. Todo dato aquí viene de leer un artefacto del repositorio
(`.joblib`, `.json`, `.csv`) o de reejecutar código sobre los microdatos
locales. Lo que no se pudo trazar hasta un archivo o una corrida está
listado explícitamente en la sección 6, **NO VERIFICADO**.

---

## 1. Resumen para quien tiene un minuto

- **No se encontró ningún hallazgo bloqueante.** Los resultados publicados
  (torneo E1–E9, clasificador de informalidad, app desplegada) se
  sostienen. El ranking del torneo es válido: las nueve especificaciones
  se compararon sobre la misma muestra, los mismos pliegues y la misma
  semilla, y eso se verificó, no se asumió.
- **El hallazgo más relevante es de método, no de resultado:** la rejilla
  de hiperparámetros del modelo desplegado (E9) estaba acotada — sus tres
  hiperparámetros cayeron en el borde. Se amplió y se re-corrió: el MAE
  mejora S/ 3,59 (0,59 %) y el ganador no cambia. La mejora es real pero
  sustantivamente irrelevante, así que **el modelo desplegado se deja como
  está**, con el hallazgo documentado.
- **Dos correcciones aplicadas** durante la auditoría: se amplió la
  constante de centinelas por prevención, y se marcaron como anotación
  manual tres secciones de un reporte que el pipeline no reproduce.
- **Lo que falta** son las fases 3 a 6 del plan de trabajo (laboratorio,
  explicación de métricas, tooltips, visualizaciones) y cuatro
  verificaciones pendientes listadas en la sección 6.

---

## 2. Hallazgos clasificados

### 2.1 Bloqueante

**Ninguno.** No se encontró ningún defecto que invalide un resultado
publicado, comprometa la integridad de los datos o impida presentar el
proyecto. Esta categoría queda vacía y eso es en sí un resultado de la
auditoría, no una omisión.

### 2.2 A corregir

| # | Hallazgo | Evidencia | Estado |
|---|---|---|---|
| **AC-1** | **Rejillas del clasificador de informalidad sin auditar.** El mismo patrón de bordes detectado en el regresor aparece en el clasificador: GB tiene 3 de 3 hiperparámetros en el borde (`n_estimators=200`, `learning_rate=0.05`, `max_depth=5`), RF tiene 2 de 3. El PR-AUC de 0,9626 que se cita como cifra del proyecto **no está confirmado como óptimo**. | `models/_hiperparametros.json` vs `REJILLAS` en `src/06_entrenar_clasificador.py:54-63` | **Pendiente.** Fuera del alcance de esta ronda. |
| **AC-2** | **Trazabilidad rota en el reporte de Fase 1.** Tres secciones de `reports/01_preparacion_fase1.md` (validación de constructo, decisión sobre P511A, ponderación) no las genera `src/03_fase1_preparacion.py`. Verificado reejecutando el script: produce un archivo 36 líneas más corto. Los números son correctos (se re-verificaron con código independiente), pero la afirmación de que todo se reproduce corriendo el pipeline no se sostiene para esa parte. | Reejecución del script + `git log --follow` (el script no cambió desde `b61e7fb`) | **Mitigado**: las tres secciones quedan marcadas como anotación manual post-hoc (commit `ce5ea10`). **Falta** trasladarlas al script. |
| **AC-3** | **Optimismo por doble inmersión en la selección de hiperparámetros.** `GridSearchCV` usa el mismo `KFold` y los mismos datos con los que después se rankean las especificaciones: para E9, `best_score_` y el `MAE_cv` de la tabla son la misma cantidad (610,9 en ambos). La magnitud del sesgo no está cuantificada. | `src/04_torneo_regresion.py:306-310` vs `models/_hiperparametros.json` | **Pendiente.** Requiere validación anidada. |
| **AC-4** | **`n_jobs=20` en una máquina de 6 núcleos reales.** No es solo ineficiencia: durante la re-optimización, `RandomForestRegressor(n_jobs=20)` anidado dentro de `GridSearchCV(n_jobs=20)` mató los procesos worker de `loky` y tumbó una corrida de 70 minutos. | `reports/torneo_rejilla_ampliada.log`; núcleos confirmados con `Get-CimInstance Win32_Processor` | **Mitigado** en el script de re-optimización (`n_jobs=1` en el estimador). **Falta** revisar el mismo patrón en `src/06_entrenar_clasificador.py` y `src/08_ablacion_clasificador.py`. |

### 2.3 Cosmético

| # | Hallazgo | Evidencia |
|---|---|---|
| **CO-1** | **`models/clasificador_gb_reducido.joblib` es huérfano en la app** (309 KB). Lo escribe `src/08_ablacion_clasificador.py:79` y viaja en cada despliegue a Streamlit Cloud, pero ningún módulo de `app/` lo carga (búsqueda de «reducido» en `app/`: 0 resultados). Sus métricas sí llegan a la interfaz, pero por `feature_schema.json`, no por el modelo. |
| **CO-2** | **`reports/figuras/` es el 63 % del peso versionado** (2,79 MB de 4,40 MB). Son capturas de evidencia, no insumos de ningún script. |
| **CO-3** | **`models/_hiperparametros.json` es huérfano desde la perspectiva de la app**: solo lo leen los scripts, como caché de búsqueda. Es correcto que exista; se anota para el inventario. |
| **CO-4** | **La constante de centinelas cubría solo dos anchos.** `CENTINELAS_MONETARIOS` era `[999999, 999999.9]`; el diccionario del INEI también usa `9999` y `99999` en columnas de menor ancho. Sin fuga activa (ninguna columna de esas está en el pipeline), pero una variable nueva podría colarse. |

**CO-4 quedó corregido** durante la auditoría (commit `ce5ea10`): la
constante ahora cubre los cuatro valores. Se verificó antes de aplicarlo
que ninguna de las siete columnas monetarias que usa el pipeline tiene un
valor legítimo de 9999 o 99999 — cero falsos positivos — y que el dataset
resultante sigue teniendo exactamente 47.899 filas.

### 2.4 Correcto (verificado, no requiere acción)

| # | Verificación | Cómo se comprobó |
|---|---|---|
| **OK-1** | **El torneo comparó sobre el mismo terreno.** Misma muestra (47.632 filas), mismo split (train 38.105 / test 9.527, `random_state=42`), mismo `KFold(5, shuffle, 42)` y misma métrica de selección para las nueve especificaciones. | Lectura del código (`df` y el split se calculan una sola vez, antes del bucle; `KF` es un único objeto de módulo) **más** una prueba mecánica: el mismo objeto `KFold` aplicado a matrices de distinta forma pero igual longitud y orden produce folds idénticos índice por índice. |
| **OK-2** | **`FAC500A` no se filtra a ningún modelo predictivo.** No aparece en ninguna matriz `X` del torneo ni del clasificador; se usa solo en el modelo explicativo (WLS), en descriptivos precomputados y como cálculo de prevalencia reportada. Cero apariciones en `app/`. | Búsqueda exhaustiva en `src/` y `app/`; inspección de `X = df[COLS]` en `src/06_entrenar_clasificador.py:142`. |
| **OK-3** | **El Módulo 34 (Sumaria) no entra en ningún pipeline predictivo.** Solo aparece en los dos scripts de diagnóstico de Fase 0, uno de los cuales existe precisamente para demostrar la circularidad del «índice de bienestar» y descartarlo. El conteo de miembros del hogar se calcula desde el Módulo 02, no rescatando la Sumaria. | Búsqueda de `Sumaria`/`MIEPERHO`/`INGHOG2D` en `src/`; comentario explícito en `src/04_torneo_regresion.py:62`. |
| **OK-4** | **Ningún centinela sobrevive al preprocesamiento.** Barrido exhaustivo sobre **todas** las columnas numéricas de los cuatro módulos crudos (no solo las conocidas): los tres artefactos que alimentan el modelado tienen **cero** valores centinela. | Ver sección 4. |
| **OK-5** | **La tasa de informalidad reconcilia con el INEI** con una brecha uniforme y explicada. | Ver sección 5. |
| **OK-6** | **La importancia de variables de E9 es estable.** Reentrenando con 5 semillas distintas del modelo, **las 8 variables más importantes conservan el rango exacto** (desviación 0,00). Solo `exper` y `exper²` —las dos de menor magnitud, casi empatadas— intercambian el 9.º y 10.º lugar. | 5 refits completos con `permutation_importance` sobre el test, `scoring=neg_mean_absolute_error`. |
| **OK-7** | **La selección se hizo por `MAE_cv`, no por test.** Elegir por MAE de test tras comparar nueve especificaciones habría sido seleccionar sobre el conjunto de evaluación; el código lo evita y lo documenta. | `src/04_torneo_regresion.py:339-345`. |
| **OK-8** | **La versión de scikit-learn coincide.** Los tres `.joblib` se generaron con 1.9.0, idéntica a `requirements.txt`. Leída del interior de los pickles (interceptando `_sklearn_version` durante la deserialización), no del entorno. | Sección 3 del inventario. |
| **OK-9** | **`data/` está fuera del repositorio** y `models/*.joblib` dentro, como corresponde. Ningún archivo bajo `data/` está rastreado. | `git ls-files` completo. |

---

## 3. Inventario (Fase 0)

Estado del repositorio: rama `main`, working tree limpio, sincronizada con
`origin/main` al inicio de la auditoría.

| Concepto | Valor |
|---|---|
| Peso total versionado | 4,40 MB (52 archivos) |
| `models/` | 1,35 MB |
| `reports/figuras/` | 2,79 MB (63 % del total) |
| `.git` | 4,35 MB |
| Artefactos que la app espera y no existen | **Ninguno** |

Las cuatro rutas literales que abre `app/streamlit_app.py` —
`models/feature_schema.json`, `models/ui_artifacts.json`,
`models/regresor_e9.joblib`, `models/clasificador_gb.joblib` — existen,
están versionadas, y dos de ellas tienen manejo explícito de ausencia.

---

## 4. Embudo de datos (Fase 1)

Reconstruido reejecutando `src/03_fase1_preparacion.py` sobre los
microdatos locales.

```
Módulo 05 — Empleo e ingresos (crudo)                     84.853
     │
     ├─ filtro: ocupados (OCU500 = 1)                    −27.137
     ▼
Ocupados                                                  57.716
     │
     ├─ filtro: 14 años o más (P208A ≥ 14)
     ├─ filtro: ingreso laboral mensual > 0                −9.817
     │     de los cuales TFNR (P507 = 5): 6.500 filas
     │     (1.425.458 personas ponderadas) — trabajadores
     │     familiares no remunerados, informales por
     │     definición, excluidos por tener ingreso = 0
     ▼
Dataset de modelado                        47.899 filas × 20 columnas
     │
     ├─ filtro (solo torneo): casos completos en
     │  tamaño de empresa, miembros, horas, educación
     │  e ingreso                                            −267  (0,6 %)
     ▼
Muestra del torneo E1–E9                                  47.632
     │
     ├─ split 80/20, random_state = 42
     ▼
Train 38.105  ·  Test 9.527
```

**Barrido de centinelas.** Se escanearon **todas** las columnas numéricas
de los cuatro módulos crudos buscando los valores 999999, 999999.9, 99999
y 9999 — no solo las columnas que se recordaban:

- **Módulo 03:** ~90 columnas con centinela residual, todas del bloque de
  gasto en educación detallado (`P311*`, `D311*`, `P312*`). **Ninguna la
  usa el proyecto**, que solo lee `P301A`, `P301B` y `P301C`.
- **Módulo 05:** ~110 columnas con centinela residual, casi todas ítems
  granulares de ingreso secundario y pensiones. **Ninguna está en el
  pipeline.** De las columnas que sí se usan:
  - `I524A1`, `I530A`, `I538A1`, `I541A` (las que arman el target):
    **cero centinelas en el archivo crudo** — el INEI las entrega ya
    limpias.
  - `D529T`, `D540T`, `D543` (ingreso en especie): sí traían centinela
    (59, 3 y 13 casos), limpiados correctamente y por partida doble en
    `src/03_fase1_preparacion.py:46` y `src/04_torneo_regresion.py:72`.
- **Sumaria:** 4 celdas residuales en columnas no usadas.
- **Artefactos de modelado** (`dataset_modelado.parquet`,
  `torneo_frame.parquet`, `fase0_poblacion.parquet`): **0 valores
  centinela sobrevivientes**. Sin bug.

---

## 5. Tasa de informalidad frente al INEI

Reconstruida con código independiente sobre los 57.716 ocupados completos
(regla derivada del proyecto, más los TFNR imputados como informales por
definición; cobertura 99,8 %).

| Corte | Muestra | INEI 2025 | Brecha |
|---|---|---|---|
| Nacional ponderado | 67,3 % | 70,2 % | −2,9 pts |
| Urbano | 61,3 % | 64,5 % | −3,2 pts |
| Rural | 91,6 % | 94,8 % | −3,2 pts |

**La brecha es uniforme (~3 pts) en los tres cortes**, con una desviación
estándar de apenas 0,14 pts entre ellos, y eso es lo que sostiene la
explicación. Un error de muestreo o de cobertura afectaría a cada estrato
con magnitud distinta, proporcional a su varianza; que la brecha se
mantenga prácticamente constante entre niveles tan dispares (61 % urbano
frente a 92 % rural) es la firma de un **sesgo sistemático de definición,
no de ruido muestral**: la afiliación a pensiones (`P558A5`) incluye
afiliaciones autofinanciadas, de modo que un subconjunto estable de
asalariados que el INEI cuenta como informales queda aquí clasificado como
formal, en la misma proporción sin importar el estrato.

La derivación queda validada como constructo, con su fuente de sesgo
acotada y documentada.

---

## 6. El torneo E1–E9 (Fase 2)

Documento completo: [`docs/METODOLOGIA_TORNEO.md`](docs/METODOLOGIA_TORNEO.md).

### 6.1 Resultados, ordenados por el criterio de selección

| ID | Especificación | MAE_cv | MAE test | R² test (soles) | Interpretab. |
|---|---|---|---|---|---|
| **E9** | **Gradient Boosting (log) — desplegada** | **610,9** | 610,8 | 0,420 | baja |
| E8 | Random Forest (log) | 613,0 | 613,0 | 0,422 | baja |
| E7 | Post-Lasso OLS | 686,9 | 686,9 | 0,262 | media |
| E6 | Depurada — explicativa | 690,1 | 691,2 | 0,273 | alta |
| E4 | Mincer extendido | 729,3 | 733,6 | 0,250 | alta |
| E3 | Mincer clásico | 823,2 | 834,2 | 0,270 | alta |
| E5 | Réplica de la especificación previa del grupo | 830,3 | 837,1 | 0,243 | alta |
| E2 | log(ingreso) ~ años de educación | 847,3 | 862,4 | 0,234 | alta |
| E1 | Ingreso ~ años de educación (niveles) | 900,6 | 906,4 | 0,172 | alta |

### 6.2 La rejilla estaba acotada — hallazgo y re-optimización

Los tres hiperparámetros de E9, el modelo desplegado, cayeron **en el
borde** de su rejilla de búsqueda. Eso significa que el óptimo real quedaba
fuera del espacio explorado. Se amplió la rejilla en la dirección de cada
borde (`learning_rate` hacia abajo, `n_estimators` y `max_depth` hacia
arriba) y se volvió a buscar, conservando exactamente la misma muestra,
el mismo split y los mismos pliegues.

| ID | `best_params_` antes | MAE_cv antes | `best_params_` después | MAE_cv después | Δ |
|---|---|---|---|---|---|
| **E9** | n=400, lr=0.05, depth=5 — **3 de 3 en el borde** | 610,90 | n=**800**, lr=**0.01**, depth=**7** — ninguno en el borde | **607,31** | −3,59 (−0,59 %) |
| E8 | n=200 (borde), depth=12, leaf=5 | 613,0 | n=**800** (interior), depth=12, leaf=5 | 613,0 | 0,00 |

**El ganador no cambia:** E9 sigue primero, y su ventaja sobre E8 incluso
se amplía (de 2,1 a 5,65 soles). En E8 el movimiento del borde al interior
no mejoró nada, lo que indica que Random Forest ya estaba en su meseta de
desempeño: el borde no ocultaba una mejora.

### 6.3 ¿La mejora de E9 es distinguible del ruido?

MAE de cada pliegue por separado, ambas configuraciones, mismos 5
pliegues:

| Config | MAE por pliegue (S/) | MAE_cv | Desv. est. entre pliegues |
|---|---|---|---|
| Rejilla vieja | 618,54 · 611,16 · 606,02 · 610,35 · 608,42 | 610,90 | 4,71 |
| Rejilla nueva | 615,10 · 606,02 · 604,67 · 604,64 · 606,14 | 607,31 | 4,41 |

Hay que leer esto con cuidado, porque las dos lecturas posibles no
coinciden:

- **En dispersión bruta**, la diferencia (3,59) es menor que una
  desviación estándar entre pliegues (4,71): la variabilidad de un mismo
  modelo al cambiar de pliegue supera la diferencia entre los dos modelos.
- **Pero la prueba correcta es pareada**, porque los cinco pliegues son
  los mismos en ambas configuraciones. Pliegue a pliegue, la nueva gana en
  **5 de 5**, con un t pareado de 4,34 y **p = 0,012**. La mejora es
  sistemática, no ruido.

**Decisión: no se promueven los hiperparámetros nuevos.** El motivo no es
que la mejora sea estadísticamente indistinguible —no lo es— sino que es
**sustantivamente irrelevante**: S/ 3,59 sobre un ingreso mediano de S/ 750
es un 0,59 %, muy por debajo del error del propio instrumento de medición.
No justifica regenerar el artefacto desplegado, revalidar el factor de
smearing ni rehacer el precómputo de la interfaz. El modelo en producción
sigue siendo el de la rejilla original y el hallazgo queda documentado.

### 6.4 Estabilidad de la importancia de variables

Reentrenando E9 con 5 semillas distintas del modelo, **las 8 variables más
importantes conservan el rango exacto en las cinco corridas** (desviación
del rango: 0,00). Solo `exper` y `exper²`, las dos de menor magnitud y con
valores casi empatados, intercambian el 9.º y 10.º puesto.

| Variable | Rango medio | Desv. del rango |
|---|---|---|
| categoria | 1,0 | 0,00 |
| anios_educ | 2,0 | 0,00 |
| tamano_empresa | 3,0 | 0,00 |
| horas_total | 4,0 | 0,00 |
| edad | 5,0 | 0,00 |
| rama | 6,0 | 0,00 |
| sexo | 7,0 | 0,00 |
| dominio | 8,0 | 0,00 |
| exper2 | 9,4 | 0,55 |
| exper | 9,6 | 0,55 |
| area | 11,0 | 0,00 |

La afirmación «categoría ocupacional, años de educación y tamaño de
empresa son las variables que más pesan» queda respaldada por evidencia de
estabilidad, no por un único ajuste.

### 6.5 Lasso (E7)

Alfa `0,00059`, elegido por `LassoCV` con el mismo `KFold` compartido. De
41 candidatas conserva 38. Las tres que elimina —`categoria_Empleador`,
`categoria_Trabajador del hogar` y `rama_Servicio doméstico`— son
exactamente las redundancias que el código ya había identificado a mano
para E6: servicio doméstico como rama y trabajador del hogar como
categoría describen el mismo subgrupo poblacional.

---

## 7. NO VERIFICADO

Lo que esta auditoría **no** pudo confirmar, para que nadie lo dé por
comprobado:

| # | Qué queda sin verificar | Por qué importa |
|---|---|---|
| **NV-1** | **Magnitud del optimismo por doble inmersión.** Los hiperparámetros se eligieron con el mismo esquema de validación cruzada con el que se rankearon las especificaciones. El sesgo existe (AC-3); su tamaño no se midió. | Requiere validación anidada: envolver el `GridSearchCV` en un `cross_val_score` externo con otra semilla. |
| **NV-2** | **Si ampliar las rejillas del clasificador de informalidad cambia el PR-AUC.** Las rejillas de RF y GB del clasificador tienen el mismo problema de bordes que tenía el regresor, y no se re-corrieron. El 0,9626 no está confirmado como óptimo. | Es la cifra insignia del clasificador. |
| **NV-3** | **Si `n_estimators` por debajo de 400 cambia algo en E8.** El borde detectado en E8 era inferior (200), y la ampliación pedida iba «hacia arriba», así que esa dirección no se probó. Dado el patrón de meseta observado, es improbable que cambie, pero no está comprobado. | Menor: E8 no es el modelo desplegado. |
| **NV-4** | **Estabilidad de la importancia con los hiperparámetros nuevos.** El chequeo de 5 semillas se hizo con la configuración vieja, que es la desplegada. No se repitió con la nueva. | Solo importaría si en el futuro se decidiera promover los hiperparámetros nuevos. |
| **NV-5** | **Reproducibilidad de tres secciones del reporte de Fase 1.** Sus números se re-verificaron con código independiente y son exactos, pero el pipeline documentado no los genera (AC-2). | Afecta a la afirmación de reproducibilidad total, no a la corrección de los datos. |
| **NV-6** | **Fases 3 a 6 del plan de trabajo.** Pestaña de laboratorio, explicación de métricas, tooltips y modo tutorial, y visualizaciones 3D no se ejecutaron en esta ronda. | Son mejoras planificadas, no defectos. |

---

## 8. Correcciones aplicadas durante la auditoría

| Commit | Qué cambió |
|---|---|
| `ce5ea10` | `CENTINELAS_MONETARIOS` ampliado a los cuatro anchos del diccionario (prevención, sin fuga activa; verificado que no introduce falsos positivos y que el dataset no cambia). Tres secciones de `reports/01_preparacion_fase1.md` marcadas como anotación manual post-hoc. Argumento de la brecha de informalidad reforzado con la desviación entre cortes. |
| `11e2e46` | `docs/METODOLOGIA_TORNEO.md`: auditoría completa del torneo. |
| `833d3f2` | Re-optimización de rejilla de E8/E9, con sus logs y resultados. |

Ningún cambio de esta auditoría modificó un modelo desplegado, un artefacto
de producción ni un resultado publicado.

---

*Auditoría realizada sobre el repositorio
[enaho-ingresos-informalidad](https://github.com/IchiSieben/enaho-ingresos-informalidad).
Documentación bajo CC BY-NC 4.0; ver [`docs/LICENSE-DOCS.md`](docs/LICENSE-DOCS.md).*
