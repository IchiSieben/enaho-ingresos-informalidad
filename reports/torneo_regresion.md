# FASE 2 — Torneo de especificaciones (regresión del ingreso)

Generado por `src/04_torneo_regresion.py`. Torneo SIN ponderar (comparación predictiva); la lectura poblacional ponderada vive en `reports/modelo_explicativo.md`.

- Experiencia potencial cruda negativa en 107 casos (0.2%): jóvenes aún en formación. Truncada en 0 (y en la ficha técnica: en baja educación la experiencia potencial SOBREestima la real — Heckman, Lochner & Todd 2006).
- Casos completos del torneo: 47,632 (se pierden 267 filas, 0.6%, casi todas por tamaño de empresa faltante)
- Train 38,105 | Test 9,527 | CV: KFold(5, shuffle, 42)

**E1 — inferencia OLS en train (escala niveles), R² 0.1641, Breusch-Pagan p=2.42e-69:**

| index | coef | ee_HC3 | p | VIF |
|---|---|---|---|---|
| anios_educ | 132.6978 | 1.7538 | 0.0 | 1.0 |
| const | 120.701 | 14.8909 | 0.0 | nan |


**E2 — inferencia OLS en train (escala log), R² 0.2144, Breusch-Pagan p=7.51e-211:**

| index | coef | ee_HC3 | p | VIF |
|---|---|---|---|---|
| anios_educ | 0.1223 | 0.0014 | 0.0 | 1.0 |
| const | 5.4916 | 0.0162 | 0.0 | nan |


**E3 — inferencia OLS en train (escala log), R² 0.2661, Breusch-Pagan p=2.95e-184:**

| index | coef | ee_HC3 | p | VIF |
|---|---|---|---|---|
| anios_educ | 0.1042 | 0.0015 | 0.0 | 1.49 |
| const | 5.2759 | 0.0237 | 0.0 | nan |
| exper | 0.0457 | 0.001 | 0.0 | 10.5 |
| exper2 | -0.0008 | 0.0 | 0.0 | 10.84 |


**E4 — inferencia OLS en train (escala log), R² 0.4171, Breusch-Pagan p=0.00e+00:**

| index | coef | ee_HC3 | p | VIF |
|---|---|---|---|---|
| anios_educ | 0.0554 | 0.0017 | 0.0 | 2.07 |
| const | 3.6318 | 0.048 | 0.0 | nan |
| exper | 0.0345 | 0.001 | 0.0 | 10.86 |
| exper2 | -0.0006 | 0.0 | 0.0 | 11.2 |
| hombre | 0.4357 | 0.0116 | 0.0 | 1.31 |
| log_horas | 0.4032 | 0.0106 | 0.0 | 1.07 |
| rama_Administración pública | 0.837 | 0.02 | 0.0 | 1.25 |
| rama_Agropecuario y pesca | -0.0583 | 0.0199 | 0.0033 | 2.55 |
| rama_Alojamiento y restaurantes | 0.2778 | 0.0216 | 0.0 | 1.35 |
| rama_Construcción | 0.5062 | 0.0196 | 0.0 | 1.39 |
| rama_Enseñanza | 1.031 | 0.0227 | 0.0 | 1.38 |
| rama_Manufactura | 0.1831 | 0.022 | 0.0 | 1.35 |
| rama_Minería e hidrocarburos | 0.9425 | 0.0343 | 0.0 | 1.09 |
| rama_Otros servicios | 0.184 | 0.0257 | 0.0 | 1.24 |
| rama_Salud y asistencia social | 0.9489 | 0.0278 | 0.0 | 1.17 |
| rama_Servicio doméstico | 0.3802 | 0.0258 | 0.0 | 1.1 |
| rama_Servicios profesionales y financieros | 0.4824 | 0.0219 | 0.0 | 1.3 |
| rama_Transporte y almacenamiento | 0.1476 | 0.0185 | 0.0 | 1.42 |
| urbano | 0.4357 | 0.0145 | 0.0 | 1.52 |


**E5 — inferencia OLS en train (escala niveles), R² 0.2379, Breusch-Pagan p=5.07e-142:**

| index | coef | ee_HC3 | p | VIF |
|---|---|---|---|---|
| const | -928.7192 | 44.6447 | 0.0 | nan |
| edad | 9.9064 | 0.5238 | 0.0 | 1.32 |
| hombre | 378.6374 | 14.2218 | 0.0 | 1.04 |
| horas_total | 13.0587 | 0.366 | 0.0 | 1.02 |
| miembros | 8.6281 | 3.7592 | 0.0217 | 1.13 |
| primaria | 220.7054 | 23.5976 | 0.0 | 6.59 |
| secundaria | 633.4462 | 26.4546 | 0.0 | 9.48 |
| tecnica | 1176.3507 | 31.144 | 0.0 | 5.79 |
| universitaria | 2149.9354 | 38.7593 | 0.0 | 6.45 |
| urbano | 329.5673 | 13.8137 | 0.0 | 1.21 |


**E6 — inferencia OLS en train (escala log), R² 0.4950, Breusch-Pagan p=0.00e+00:**

| index | coef | ee_HC3 | p | VIF |
|---|---|---|---|---|
| anios_educ | 0.0419 | 0.0016 | 0.0 | 2.26 |
| categoria_Empleador | 0.2723 | 0.0294 | 0.0 | 1.37 |
| categoria_Independiente | -0.6967 | 0.0148 | 0.0 | 3.32 |
| categoria_Obrero | -0.1607 | 0.0122 | 0.0 | 2.27 |
| categoria_Trabajador del hogar | -0.0583 | 0.0245 | 0.0172 | 1.24 |
| const | 4.9471 | 0.05 | 0.0 | nan |
| dominio_Costa Centro | 0.0045 | 0.0161 | 0.7788 | 1.67 |
| dominio_Costa Norte | -0.1376 | 0.0154 | 0.0 | 1.91 |
| dominio_Costa Sur | 0.0714 | 0.0189 | 0.0002 | 1.45 |
| dominio_Selva | -0.0322 | 0.0153 | 0.0354 | 2.41 |
| dominio_Sierra Centro | -0.3082 | 0.0184 | 0.0 | 2.14 |
| dominio_Sierra Norte | -0.387 | 0.0272 | 0.0 | 1.5 |
| dominio_Sierra Sur | -0.185 | 0.0183 | 0.0 | 1.83 |
| exper | 0.0409 | 0.0009 | 0.0 | 11.65 |
| exper2 | -0.0007 | 0.0 | 0.0 | 11.59 |
| hombre | 0.3919 | 0.0108 | 0.0 | 1.34 |
| log_horas | 0.3486 | 0.0093 | 0.0 | 1.09 |
| rama_Administración pública | 0.0946 | 0.0227 | 0.0 | 2.02 |
| rama_Agropecuario y pesca | -0.137 | 0.0191 | 0.0 | 2.67 |
| rama_Alojamiento y restaurantes | 0.1708 | 0.0208 | 0.0 | 1.38 |
| rama_Construcción | 0.2893 | 0.019 | 0.0 | 1.52 |
| rama_Enseñanza | 0.4008 | 0.0222 | 0.0 | 1.86 |
| rama_Manufactura | 0.0414 | 0.0205 | 0.0439 | 1.41 |
| rama_Minería e hidrocarburos | 0.5521 | 0.0326 | 0.0 | 1.17 |
| rama_Otros servicios | 0.0889 | 0.0237 | 0.0002 | 1.25 |
| rama_Salud y asistencia social | 0.3767 | 0.0269 | 0.0 | 1.39 |
| rama_Servicios profesionales y financieros | 0.2663 | 0.0212 | 0.0 | 1.35 |
| rama_Transporte y almacenamiento | 0.3089 | 0.0181 | 0.0 | 1.45 |
| tamano_empresa_101 a 500 | -0.1307 | 0.0207 | 0.0 | 1.43 |
| tamano_empresa_21 a 50 | -0.2633 | 0.0197 | 0.0 | 1.4 |
| tamano_empresa_51 a 100 | -0.2296 | 0.0246 | 0.0 | 1.27 |
| tamano_empresa_Hasta 20 | -0.4628 | 0.0145 | 0.0 | 3.84 |
| urbano | 0.2465 | 0.0141 | 0.0 | 1.69 |


## E7 — Lasso y post-Lasso

- Candidatas: 41 columnas; Lasso (alpha=0.00059) conserva 38.
- Eliminadas: ['categoria_Empleador', 'categoria_Trabajador del hogar', 'rama_Servicio doméstico']
- Nota (Belloni et al. 2014): la selección se hizo una vez sobre el train completo; la inferencia post-Lasso es descriptiva, no formal.

## E8 — mejores hiperparámetros: `{'regressor__modelo__max_depth': 12, 'regressor__modelo__min_samples_leaf': 5, 'regressor__modelo__n_estimators': 200}` (MAE grid S/ 613.0, 7.6 min, caché)

## E9 — mejores hiperparámetros: `{'regressor__modelo__learning_rate': 0.05, 'regressor__modelo__max_depth': 5, 'regressor__modelo__n_estimators': 400}` (MAE grid S/ 610.9, 5.1 min, caché)

## Tabla del torneo (ordenada por MAE_cv, el criterio de selección)

La selección usa MAE_cv (5 pliegues en train): elegir por MAE de test tras comparar 9 especificaciones sería seleccionar sobre el conjunto de evaluación. MAE_test se reporta como estimación honesta del ya elegido. MAE en soles con inversión por mediana (expm1); la columna smear reporta la media condicional (Duan con residuos OOF de train).

| ID | especificacion | MAE_cv | MAE_test | MAE_test_media_smear | RMSE_test | R2_test_soles | R2_escala_propia | smearing_Duan | n_vars | interpretabilidad |
|---|---|---|---|---|---|---|---|---|---|---|
| E9 | Gradient Boosting (log target, pipeline sklearn) | 610.9 | 610.8 | 741.1 | 1226.7 | 0.42 | 0.575 | 1.401 | 11 | baja |
| E8 | Random Forest (log target, pipeline sklearn) | 613.0 | 613.0 | 741.3 | 1225.0 | 0.422 | 0.567 | 1.405 | 11 | baja |
| E7 | Post-Lasso: OLS sobre las variables que Lasso conserva | 686.9 | 686.9 | 840.5 | 1383.6 | 0.262 | 0.511 | 1.434 | 38 | media |
| E6 | Depurada: E4 + categoría + tamaño empresa + dominio (sin la dummy rama=Servicio doméstico, colineal perfecta con categoría=Trabajador del hogar) | 690.1 | 691.2 | 841.2 | 1373.2 | 0.273 | 0.509 | 1.438 | 32 | alta |
| E4 | Mincer extendido: E3 + sexo + área + log(horas) + rama | 729.3 | 733.6 | 857.0 | 1395.1 | 0.25 | 0.429 | 1.498 | 18 | alta |
| E3 | Mincer clásico: educ + exp + exp² | 823.2 | 834.2 | 842.4 | 1376.2 | 0.27 | 0.27 | 1.564 | 3 | alta |
| E5 | Réplica de la compañera (niveles, sin centinela) | 830.3 | 837.1 | 837.1 | 1401.6 | 0.243 | 0.243 |  | 9 | alta |
| E2 | log(ingreso) ~ años educación | 847.3 | 862.4 | 879.1 | 1409.5 | 0.234 | 0.216 | 1.607 | 1 | alta |
| E1 | Ingreso ~ años educación (consigna, niveles) | 900.6 | 906.4 | 906.4 | 1465.7 | 0.172 | 0.172 |  | 1 | alta |


- Brecha E4/E6 vs E8/E9 en MAE_cv: S/ +79.2 (+11.5%). Esta brecha estima el aporte de no linealidades e interacciones que la forma funcional lineal no captura (Athey & Imbens 2019).

## Sensibilidad al ingreso en especie (E4, dos targets)

| target | coef_urbano | premio_urbano_pct | coef_rama_agro | coef_educ | R2 |
|---|---|---|---|---|---|
| solo monetario | 0.4357 | 54.6 | -0.0583 | 0.0554 | 0.4171 |
| monetario + especie | 0.4187 | 52.0 | -0.0206 | 0.0524 | 0.4115 |

- El premio urbano cae 2.6 puntos porcentuales al incluir especie/autoconsumo. El modelo desplegado sigue siendo monetario (definición estándar), pero esta sensibilidad se publica.
