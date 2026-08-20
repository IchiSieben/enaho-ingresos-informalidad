# Metodología del torneo E1–E9

Auditoría del torneo de especificaciones de `src/04_torneo_regresion.py`.
Cada afirmación de este documento viene de leer el código, releer
`reports/torneo_regresion.md` / `reports/comparacion_torneo.csv` /
`models/_hiperparametros.json`, o de reejecutar código nuevo durante la
auditoría del 18/08/2026 (scripts efímeros, no versionados; los resultados
sí quedan citados aquí con sus números exactos).

## 1. Qué varía entre E1 y E9

| ID | Algoritmo | Escala del target | Variables (num) | Variables (cat) | Ponderado | n_vars | Interpretab. |
|---|---|---|---|---|---|---|---|
| E1 | OLS | niveles | anios_educ | — | No | 1 | alta |
| E2 | OLS | log | anios_educ | — | No | 1 | alta |
| E3 | OLS | log | anios_educ, exper, exper² | — | No | 3 | alta |
| E4 | OLS | log | anios_educ, exper, exper², hombre, urbano, log_horas | rama | No | 18 | alta |
| E5 | OLS | niveles | urbano, hombre, edad, primaria, secundaria, tecnica, universitaria, horas_total, miembros | — | No | 9 | alta |
| E6 | OLS | log | anios_educ, exper, exper², hombre, urbano, log_horas | rama, categoria, tamano_empresa, dominio | No | 32 | alta |
| E7 | Post-Lasso OLS | log | anios_educ, exper, exper², log_horas, miembros | sexo, area, dominio, rama, tamano_empresa, categoria, contrato | No | 38 (de 41 candidatas) | media |
| E8 | Random Forest | log (TransformedTargetRegressor) | anios_educ, edad, exper, exper², horas_total | sexo, area, dominio, rama, tamano_empresa, categoria | No | 11 | baja |
| E9 | Gradient Boosting | log (TransformedTargetRegressor) | anios_educ, edad, exper, exper², horas_total | sexo, area, dominio, rama, tamano_empresa, categoria | No | 11 | baja |

Lectura de la progresión: E1→E3 es la ecuación de Mincer creciendo (educación
→ +experiencia); E4 añade demografía/sector; E5 es la réplica de la
especificación previa del grupo, en niveles y sin las variables
estructurales de E6; E6 añade categoría ocupacional, tamaño de empresa y
dominio geográfico (la más rica en interpretabilidad); E7 deja que Lasso
seleccione sobre un pool de candidatas más amplio pero solapado con E6; E8/E9
cambian de familia (árboles) sobre un conjunto de variables reducido a las
más "crudas" (sin dummies pre-diseñadas, el árbol las modela internamente).

**Ninguna especificación está ponderada** (FAC500A no entra en ninguna X del
torneo, verificado en la Fase 1 de esta auditoría) — la comparación es
puramente predictiva.

## 2. ¿Se compararon sobre el mismo terreno? — VERIFICADO

Este era uno de los dos puntos prioritarios de esta ronda. Tres afirmaciones,
las tres verificadas contra el código y, la del fold, además contra una
prueba mecánica independiente:

- **Misma muestra.** `04_torneo_regresion.py:main()` carga `df = cargar()`
  **una sola vez** (47.632 filas, tras perder 267 por tamaño de empresa
  faltante — 0,6 %) y calcula `idx_tr, idx_te =
  train_test_split(df.index, test_size=0.2, random_state=SEMILLA)`
  **una sola vez**, antes del bucle de especificaciones. Las nueve
  specs — incluidas E8/E9 — indexan con `.loc[idx_tr]` / `.loc[idx_te]`
  sobre matrices `X` derivadas del mismo `df`. Train 38.105 / Test 9.527.
  No hay ninguna spec que recorte filas por su cuenta.
- **Mismos folds.** `KF = KFold(n_splits=5, shuffle=True, random_state=SEMILLA)`
  es un **único objeto de módulo**, reutilizado sin reinstanciar tanto en
  `cross_val_predict(..., cv=KF, ...)` (E1–E9 vía `evaluar_spec`) como en
  `GridSearchCV(..., cv=KF, ...)` (E8/E9). Como todas las specs comparten el
  mismo `idx_tr` (mismo orden, mismo largo), `KFold.split()` —determinista
  bajo `random_state` fijo y sensible solo a la posición, no al contenido—
  produce literalmente las mismas particiones fila-a-fila sin importar
  cuántas columnas tenga cada spec. Lo confirmé con una prueba aparte:
  dos arrays de igual longitud/orden pero distinto número de columnas y
  contenido aleatorio distinto, pasados al mismo objeto `KFold`, producen
  folds idénticos índice por índice (`True`).
- **Misma métrica de selección.** El ranking final (`tabla.sort_values
  ("MAE_cv")`) usa `mae_cv` para las nueve filas, calculado siempre por
  `evaluar_spec` con el mismo criterio (mediana condicional invertida desde
  la escala de ajuste). E7 (Lasso) y E8/E9 (árboles) no son casos aparte:
  pasan por la misma función.

**Conclusión: el ranking del torneo es válido bajo este criterio.** No
encontré ninguna spec evaluada con folds, muestra o métrica distintos.

## 3. ¿Los hiperparámetros se ajustaron con los mismos datos con los que se rankeó?

**Sí, y hay optimismo — de magnitud modesta pero no nula.** `GridSearchCV`
para E8/E9 usa `cv=KF` sobre `X_arb.loc[idx_tr]` (líneas 306-310); su
`best_score_` es la MISMA cantidad (mismo CV, mismos datos) que después se
reporta como `MAE_cv` en la tabla final del torneo — de hecho para E9 los
dos valores coinciden casi al centavo: `best_score_` da MAE grid S/ 610,9
(`models/_hiperparametros.json`) y la fila final de la tabla dice
`MAE_cv 610.9`. La selección de hiperparámetros y el ranking de
especificaciones comparten exactamente el mismo conjunto de validación
cruzada — es el patrón clásico de optimismo por "doble inmersión"
(hyperparameter search + model selection sobre el mismo split).

Magnitud probable: con una rejilla de solo 8 combinaciones (2×2×2) por
modelo y una validación de 5 pliegues sobre 38 mil filas, el sesgo esperado
es bajo (unos pocos soles de MAE, no docenas) — pero no lo puedo cuantificar
sin correr una validación anidada, que no ejecuté esta ronda por prioridad
explícita del usuario en los dos puntos siguientes. **Pendiente, marcado
`NO VERIFICADO`**: validación anidada para E9 (ganador) y E8 (runner-up
entre los árboles). Recomendación para una próxima ronda: envolver el
`GridSearchCV` en un `cross_val_score` externo con un `KFold` *distinto*
(otra semilla) para separar limpiamente selección de hiperparámetros y
estimación de desempeño.

## 4. Rejilla vs. óptimo — el hallazgo central de esta auditoría

Segundo punto prioritario. Comparé cada `best_params_` contra su rejilla
buscada (`REJILLAS` en `04_torneo_regresion.py` y `models/_hiperparametros.json`):

### E9 — Gradient Boosting (el modelo desplegado)

| Hiperparámetro | Rejilla buscada | `best_params_` | ¿En el borde? |
|---|---|---|---|
| `n_estimators` | [200, 400] | **400** | 🔴 SÍ — borde superior |
| `learning_rate` | [0.05, 0.1] | **0.05** | 🔴 SÍ — borde inferior |
| `max_depth` | [3, 5] | **5** | 🔴 SÍ — borde superior |

**Los tres hiperparámetros del modelo ganador cayeron en el borde de su
rejilla.** Esto es la señal más fuerte de que la rejilla estaba mal puesta:
el óptimo real de al menos uno de los tres —probablemente todos, dado el
patrón consistente hacia "más árboles, más profundidad, menor tasa de
aprendizaje"— queda fuera del espacio que se buscó. No hay forma de saber,
con los datos actuales, si S/ 610,9 de MAE_cv es el mejor MAE alcanzable por
Gradient Boosting en este problema o si una rejilla más ancha (p. ej.
`n_estimators: [400, 600, 800]`, `learning_rate: [0.01, 0.03, 0.05]`,
`max_depth: [5, 7, 9]`) lo mejora.

### E8 — Random Forest (runner-up entre árboles)

| Hiperparámetro | Rejilla buscada | `best_params_` | ¿En el borde? |
|---|---|---|---|
| `n_estimators` | [200, 400] | **200** | 🔴 SÍ — borde inferior |
| `max_depth` | [8, 12, None] | 12 | No (interior) |
| `min_samples_leaf` | [1, 5, 20] | 5 | No (interior) |

Un borde también, pero en la dirección opuesta (menos árboles, no más) — más
plausible como óptimo genuino (RF no sobreajusta con menos estimadores de la
misma forma que GB), aunque igual habría que confirmar extendiendo hacia
abajo (100, 50).

### Hallazgo relacionado (mismo patrón, clasificador de informalidad)

No estaba en el alcance de esta ronda pero usa la misma infraestructura
(`REJILLAS` en `06_entrenar_clasificador.py`) y refuerza el patrón — lo dejo
anotado, no lo profundicé:

- **GB clasificador**: `n_estimators=200` (borde inferior de [200,400]),
  `learning_rate=0.05` (borde inferior de [0.05,0.1]), `max_depth=5` (borde
  superior de [3,5]) — 3 de 3 en el borde.
- **RF clasificador**: `n_estimators=400` (borde superior), `max_depth=16`
  (borde superior de [8,12,16] — **nota**: el propio código comenta
  `# acotada: nada de None`, así que este límite es una decisión deliberada
  contra el sobreajuste, no un descuido), `min_samples_leaf=5` (borde
  inferior de [5,20]).

**Recomendación (histórica, ver actualización abajo):** antes de citar S/
610,9 (o el PR-AUC 0,9626 del clasificador) como "el" número del proyecto,
extender las cuatro rejillas (regresor y clasificador) en la dirección de
cada borde y re-optimizar. Es probable que el número mejore un poco, no que
cambie el ranking relativo E9>E8>...>E1 (la brecha con E7/E6 es de ~80
soles, mucho mayor que lo que suele mover una rejilla más ancha en este
tipo de modelos), pero no puedo afirmar eso sin correrlo — **marcado
`NO VERIFICADO`**.

### Actualización — rejilla ampliada y reoptimización (18/08/2026)

**El hallazgo de arriba se queda tal cual quedó documentado**: la primera
rejilla del torneo estaba acotada, se detectó en esta auditoría, y a
continuación se amplió y se re-corrió E8/E9 con la MISMA muestra (47.632
filas), el MISMO split (train 38.105/test 9.527, `random_state=42`) y el
MISMO `KFold(5, shuffle, 42)` — verificado con un `assert` en el script de
re-optimización antes de correr cualquier búsqueda.

**Rejillas ampliadas** (dirección: `learning_rate` hacia abajo,
`n_estimators` hacia arriba, `max_depth` hacia arriba — instrucción
explícita del usuario, aplicada donde el hiperparámetro existe):

| Modelo | Hiperparámetro | Rejilla vieja | Rejilla nueva |
|---|---|---|---|
| E9 (GB) | `n_estimators` | [200, 400] | **[400, 800, 1200]** |
| E9 (GB) | `learning_rate` | [0.05, 0.1] | **[0.01, 0.02, 0.05]** |
| E9 (GB) | `max_depth` | [3, 5] | **[5, 7, 9]** |
| E8 (RF) | `n_estimators` | [200, 400] | **[400, 800, 1200]** |
| E8 (RF) | `max_depth` | [8, 12, None] | [8, 12, None] — sin cambio |
| E8 (RF) | `min_samples_leaf` | [1, 5, 20] | [1, 5, 20] — sin cambio |

`max_depth` de RF **no se pudo ampliar "hacia arriba"**: la rejilla ya
incluía `None` (sin límite), el máximo posible en un grid discreto. Queda
anotado, no resuelto en silencio: el borde que sí se había detectado para
E8 fue `n_estimators=200` (borde **inferior**), y la dirección pedida
("hacia arriba") no prueba esa dirección — ver el resultado abajo, que de
todos modos permite concluir algo sobre esto.

**Incidente durante la corrida — reportado, no oculto:** el primer intento
de correr ambas rejillas en una sola tarea se cayó durante E8:
`RandomForestRegressor(n_jobs=20)` quedó **anidado** dentro de
`GridSearchCV(n_jobs=20)` en una máquina de **6 núcleos reales** (no 20 —
confirmado con `wmic`/`Get-CimInstance`), y los procesos worker de `loky`
murieron (`resource_tracker: process died unexpectedly`, luego un
`KeyError` fatal). E9 ya había terminado antes de la caída y su resultado
es válido. Se reintentó solo E8 con el estimador en `n_jobs=1` (el
paralelismo lo hace únicamente `GridSearchCV`, `n_jobs=20`, sin
anidamiento) — terminó limpio en 28,5 min. Log completo en
`reports/torneo_rejilla_ampliada.log` y `reports/torneo_rejilla_ampliada_e8.log`;
resultados en `reports/comparacion_torneo_rejilla_ampliada.csv`.

**Resultado — tabla antes/después:**

| ID | `best_params_` ANTES | MAE_cv ANTES | `best_params_` DESPUÉS | MAE_cv DESPUÉS | Δ MAE_cv | ¿Sigue en el borde? |
|---|---|---|---|---|---|---|
| **E9** | n_est=400, lr=0.05, depth=5 (**los 3 en el borde**) | 610,9 | n_est=**800**, lr=**0.01**, depth=**7** | **607,3** | **−3,6 (−0,59 %)** | **No — los 3 quedaron en el interior** |
| E8 | n_est=200 (borde), depth=12, leaf=5 | 613,0 | n_est=**800** (interior), depth=12, leaf=5 | 613,0 | +0,0 (+0,00 %) | No — pero ver nota abajo |

**Lectura:**

- **E9 (el modelo desplegado): el hallazgo se confirma con datos.** Los
  tres hiperparámetros se movieron del borde al interior de la rejilla
  ampliada, y el MAE_cv mejoró S/ 3,6 (0,59 %) — modesto pero real y en la
  dirección predicha ("más árboles, más profundidad, menor tasa de
  aprendizaje" era, en efecto, mejor). **El ganador del torneo NO cambia**:
  E9 sigue siendo el mejor (607,3 vs el segundo lugar E8 en 613,0 — la
  brecha incluso se amplía levemente, de 2,1 a 5,65 soles).
- **E8: la mejora no aparece, y eso también es informativo.** Al mover
  `n_estimators` del borde inferior (200) al interior de la rejilla nueva
  (800 gana sobre 400 y 1200), el MAE_cv no se movió ni un centavo (613,0
  → 613,0, literalmente igual redondeando a una cifra decimal). Esto es
  consistente con que Random Forest alcanza una meseta de desempeño rápido
  en `n_estimators` — 200, 400 u 800 árboles rinden lo mismo en este
  problema. El borde original (`n_estimators=200`) no ocultaba una mejora
  real; el algoritmo ya estaba en su techo. **La dirección "hacia abajo"
  que la instrucción no cubrió (100, 50 árboles) queda sin probar** —
  dado el patrón de meseta, es improbable que cambie nada, pero no está
  verificado y se deja anotado así, no se asume.
- El PR-AUC del clasificador (0,9626) y sus rejillas (RF/GB) **no se
  tocaron en esta ronda** — seguían fuera del alcance explícito del
  usuario. El patrón de bordes que se documentó arriba para ellas sigue
  sin resolver.

### ¿La mejora de E9 es distinguible del ruido? — dispersión entre pliegues

Recalculé el MAE de **cada uno de los 5 pliegues** por separado, para ambas
configuraciones de E9, sobre el mismo `KFold(5, shuffle, 42)`:

| Config | MAE por pliegue (S/) | MAE_cv | Desv. est. entre pliegues (ddof=1) |
|---|---|---|---|
| Rejilla **vieja** (n=400, lr=0.05, depth=5) | 618,54 · 611,16 · 606,02 · 610,35 · 608,42 | **610,90** | **4,71** |
| Rejilla **nueva** (n=800, lr=0.01, depth=7) | 615,10 · 606,02 · 604,67 · 604,64 · 606,14 | **607,31** | **4,41** |

La media de los pliegues reproduce exactamente el `MAE_cv` reportado en la
tabla del torneo (610,90 y 607,31), lo que valida el cálculo.

**Dos lecturas, y conviene tener las dos a mano:**

1. **En dispersión bruta, la diferencia se confunde con el ruido.** La
   brecha entre configuraciones (S/ 3,59) es **menor que una desviación
   estándar entre pliegues** (4,71 y 4,41). Dicho de otro modo: la
   variabilidad de un mismo modelo al cambiar de pliegue es mayor que la
   diferencia entre los dos modelos.
2. **Pero la prueba correcta es pareada, y ahí la mejora sí es
   sistemática.** Los 5 pliegues son *los mismos* en ambas
   configuraciones (mismo objeto `KFold`, misma semilla), así que
   comparar sus medias como muestras independientes descarta información.
   Pliegue a pliegue, la configuración nueva gana en **5 de 5**, con
   diferencias de +3,44 / +5,14 / +1,35 / +5,71 / +2,28 (media 3,58,
   desv. 1,85, error estándar 0,83). El **t pareado da 4,34 con p =
   0,012** (df=4): la mejora es consistente, no ruido de muestreo. Un t
   de muestras independientes daría p = 0,25, pero es el test equivocado
   aquí precisamente porque ignora el pareamiento.

**Decisión: los hiperparámetros nuevos NO se promueven al modelo
desplegado.** El motivo no es que la mejora sea estadísticamente
indistinguible —el test pareado muestra que no lo es— sino que es
**sustantivamente irrelevante**: S/ 3,59 de MAE sobre un ingreso mediano
de S/ 750 es una mejora del 0,59 %, muy por debajo del error de medición
del propio instrumento (la ENAHO imputa ingresos y el centinela 999999
afectaba al 2,28 % de la población). No justifica regenerar
`models/regresor_e9.joblib`, revalidar el factor de smearing, rehacer el
precómputo de la UI ni repetir el chequeo de estabilidad de importancia.
El modelo desplegado sigue siendo el de la rejilla original, y este
apartado queda como hallazgo de auditoría documentado.

**Estabilidad de la importancia de E9 (reconfirmación).** El chequeo de
5 semillas de refit de la sección 7 se hizo sobre los `best_params_`
*viejos* (n_est=400, lr=0.05, depth=5). Con los `best_params_` *nuevos*
(n_est=800, lr=0.01, depth=7) no se repitió el chequeo de 5 semillas en
esta ronda — el resultado de la sección 7 (**las 8 variables más
importantes conservan el rango exacto en las 5 semillas de refit**,
desviación 0,00) queda válido para la configuración con la que se
demostró, no re-verificado para la nueva. Marcado como pendiente para una
próxima ronda si se decide promover los nuevos hiperparámetros al
artefacto desplegado (`models/regresor_e9.joblib`) — **hoy el modelo
desplegado sigue siendo el de la rejilla vieja**; esta ronda fue de
auditoría/reoptimización exploratoria, no reemplazó `models/regresor_e9.joblib`
ni `models/_hiperparametros.json`.

## 5. Lasso (E7) — qué retuvo y con qué alfa

- **Alfa**: `0,00059`, elegido por `LassoCV(cv=KF, ...)` — es decir, con el
  mismo `KF` compartido del torneo (misma malla de validación que todo lo
  demás, mismo argumento de optimismo modesto que la sección 3).
- **Candidatas**: 41 columnas (tras one-hot de `sexo, area, dominio, rama,
  tamano_empresa, categoria, contrato`).
- **Retenidas**: 38 de 41 — Lasso apenas poda en este problema.
- **Eliminadas** (las 3): `categoria_Empleador`, `categoria_Trabajador del
  hogar`, `rama_Servicio doméstico`. Consistente con el motivo documentado
  en el código para E6: `rama_Servicio doméstico` es colineal casi perfecta
  con `categoria_Trabajador del hogar` (mismo subgrupo poblacional descrito
  por dos variables), y Lasso resuelve exactamente esa redundancia.
- El código deja la advertencia correcta: con alfa elegido sobre train
  completo y sin refit externo, "la inferencia post-Lasso es descriptiva,
  no formal" (Belloni et al. 2014) — la especificación E7 en la tabla del
  torneo se reporta con interpretabilidad "media", no "alta", por esta razón.

## 6. Variables descartadas — evidencia concreta

| Variable | Por qué salió | Evidencia |
|---|---|---|
| `INGHOG2D` / índice de bienestar | Circularidad: el ingreso individual es sumando directo del ingreso del hogar | ρ Spearman 0,58 con el target, documentado en `02_fase0_autopsia.py` y el README §1 |
| `rama_Servicio doméstico` (dummy) | Colinealidad perfecta con `categoria=Trabajador del hogar` (mismo subgrupo, dos codificaciones) | VIF=inf reportado en comentario de `04_torneo_regresion.py:148-150`; excluida en E6; Lasso la descarta también en E7 (sección 5) |
| `P511A` (tipo de contrato) | AUC univariado 0,846 (bajo el umbral 0,85 pero casi-definicional para asalariados) | `reports/01_preparacion_fase1.md` — nunca estuvo en la lista aprobada de predictores del clasificador; se conserva solo para la réplica E5 |
| `FAC500A` como feature | Es un peso de expansión muestral, no una característica del individuo — inflaría artificialmente la señal si se usara como predictor | Verificado en la Fase 1 de esta auditoría: no aparece en ninguna `X` de `04` ni `06` |

## 7. Estabilidad de la importancia de E9 (5 semillas de refit)

Reentrené E9 (Gradient Boosting, mismos `best_params_` cacheados) con 5
semillas distintas del **modelo** (42–46, no solo repeticiones de shuffle
sobre un único fit) y calculé `permutation_importance` sobre el test set
(`scoring=neg_mean_absolute_error`, `n_repeats=5` por semilla) para cada una.
Esto es más estricto que la importancia por permutación ya guardada en
`models/ui_artifacts.json` (esa repite el shuffle 5 veces sobre **un solo**
modelo fijo; esta prueba cambia el modelo mismo).

**Resultado — el ranking NO baila:**

| Variable | Rank medio | Desv. del rank (5 semillas) |
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

Las 8 variables más importantes tienen **rango idéntico en las 5 semillas**
(desviación 0,00). Solo `exper` y `exper²` —las dos de menor magnitud y con
valores casi empatados (10-16 vs 8-14 de caída en MAE, según semilla)—
intercambian el 9° y 10° lugar ocasionalmente. Contra la hipótesis del
prompt maestro ("si el orden baila, la narrativa es más débil"): **aquí no
baila** — la afirmación "categoría ocupacional, años de educación y tamaño
de empresa son las variables que más pesan en E9" queda respaldada con
evidencia de estabilidad, no solo con un fit único.

---

*Generado como parte de la auditoría del 18/08/2026, actualizado el mismo
día con la reoptimización de rejilla. Puntos que siguen marcados
`NO VERIFICADO`: magnitud exacta del optimismo de hyperparameter tuning
(sección 3, validación anidada pendiente); si ampliar las rejillas del
**clasificador** de informalidad (RF/GB) cambia el PR-AUC reportado
(sección 4, fuera del alcance de esta ronda); estabilidad de la
importancia de E9 con los `best_params_` NUEVOS (sección 4, actualización —
el chequeo de 5 semillas se hizo con los parámetros viejos); si probar
`n_estimators` por debajo de 400 en E8 (RF) cambia algo (sección 4,
actualización — la dirección "hacia abajo" no se cubrió esta ronda). Punto
que quedó **resuelto con datos**: si ampliar la rejilla de E9 cambia el
MAE_cv — sí, mejora S/ 3,59 (610,90 → 607,31), los tres hiperparámetros
se mueven al interior de la rejilla ampliada y la mejora es sistemática
(5/5 pliegues, t pareado p = 0,012); el ganador del torneo no cambia y la
mejora se juzga sustantivamente irrelevante, por lo que no se promueve.*
