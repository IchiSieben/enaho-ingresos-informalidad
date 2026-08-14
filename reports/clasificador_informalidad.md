# FASE 2b — Clasificador de empleo informal

Generado por `src/06_entrenar_clasificador.py`. Predictores estructurales compartidos con la regresión; SIN ingreso y SIN las columnas que definen el target (P510A1, P558A*, P511A).

- 47,632 filas | Train 38,105 / Test 9,527 (estratificado por el target)
- Prevalencia informal: 0.678 muestral (train) | 0.641 ponderada FAC500A. El baseline de PR-AUC es la prevalencia; el lift se calcula contra la muestral.

## Regresión logística — odds ratios (train, sin estandarizar)

OR>1 = mayor propensión a la informalidad vs la base (Mujer, Rural, Lima Metropolitana, Comercio, empresa >500, Empleado).

| index | odds_ratio | IC95_inf | IC95_sup | p |
|---|---|---|---|---|
| tamano_empresa_Hasta 20 | 16.714 | 14.441 | 19.344 | 0.0 |
| rama_Administración pública | 5.883 | 4.849 | 7.138 | 0.0 |
| categoria_Independiente | 5.213 | 4.709 | 5.772 | 0.0 |
| tamano_empresa_21 a 50 | 3.803 | 3.147 | 4.595 | 0.0 |
| categoria_Trabajador del hogar | 3.689 | 2.913 | 4.672 | 0.0 |
| rama_Transporte y almacenamiento | 2.983 | 2.57 | 3.463 | 0.0 |
| rama_Agropecuario y pesca | 2.918 | 2.578 | 3.302 | 0.0 |
| rama_Construcción | 1.833 | 1.6 | 2.099 | 0.0 |
| tamano_empresa_51 a 100 | 1.818 | 1.421 | 2.325 | 0.0 |
| rama_Alojamiento y restaurantes | 1.642 | 1.446 | 1.865 | 0.0 |
| dominio_Sierra Norte | 1.35 | 1.103 | 1.653 | 0.0036 |
| rama_Otros servicios | 1.34 | 1.15 | 1.561 | 0.0002 |
| dominio_Selva | 1.34 | 1.202 | 1.494 | 0.0 |
| rama_Manufactura | 1.247 | 1.095 | 1.419 | 0.0008 |
| dominio_Sierra Centro | 1.228 | 1.081 | 1.396 | 0.0016 |
| rama_Minería e hidrocarburos | 1.215 | 0.933 | 1.583 | 0.1476 |
| rama_Enseñanza | 1.2 | 0.986 | 1.46 | 0.0685 |
| rama_Salud y asistencia social | 1.146 | 0.915 | 1.436 | 0.2345 |
| categoria_Obrero | 1.049 | 0.952 | 1.156 | 0.3335 |
| dominio_Sierra Sur | 1.02 | 0.902 | 1.155 | 0.7493 |
| exper2 | 1.001 | 1.001 | 1.001 | 0.0 |
| horas_total | 0.989 | 0.987 | 0.991 | 0.0 |
| dominio_Costa Norte | 0.926 | 0.831 | 1.032 | 0.1667 |
| exper | 0.907 | 0.901 | 0.914 | 0.0 |
| tamano_empresa_101 a 500 | 0.846 | 0.666 | 1.073 | 0.1678 |
| anios_educ | 0.821 | 0.812 | 0.83 | 0.0 |
| dominio_Costa Sur | 0.788 | 0.69 | 0.9 | 0.0004 |
| dominio_Costa Centro | 0.737 | 0.656 | 0.829 | 0.0 |
| categoria_Empleador | 0.711 | 0.613 | 0.824 | 0.0 |
| sexo_Hombre | 0.669 | 0.623 | 0.719 | 0.0 |
| rama_Servicios profesionales y financieros | 0.574 | 0.501 | 0.658 | 0.0 |
| area_Urbana | 0.561 | 0.511 | 0.617 | 0.0 |


## Random Forest — `{'modelo__max_depth': 16, 'modelo__min_samples_leaf': 5, 'modelo__n_estimators': 400}` (PR-AUC grid 0.9621, 1.3 min, caché)

## Gradient Boosting — `{'modelo__learning_rate': 0.05, 'modelo__max_depth': 5, 'modelo__n_estimators': 200}` (PR-AUC grid 0.9627, 4.6 min, caché)

## Comparación (baseline PR-AUC = prevalencia = 0.678)

Selección por PR-AUC de validación cruzada, no por test (misma disciplina que el torneo).

| algoritmo | PRAUC_cv | ROCAUC_cv | PRAUC_test | ROCAUC_test | Brier_test | min |
|---|---|---|---|---|---|---|
| Gradient Boosting | 0.9626 | 0.9289 | 0.9605 | 0.9274 | 0.0974 | 0.7 |
| Random Forest | 0.9619 | 0.9279 | 0.9589 | 0.926 | 0.0981 | 0.4 |
| Regresión logística | 0.9553 | 0.9164 | 0.9526 | 0.914 | 0.1053 | 0.1 |

- Ganador por PR-AUC_cv: **Gradient Boosting**

## Puntos operativos (probabilidades out-of-fold de train)

| punto | umbral | precision | recall | lift | señalados_por_1000 | F1 |
|---|---|---|---|---|---|---|
| umbral 0,5 | 0.5 | 0.881 | 0.929 | 1.3 | 714 | 0.904 |
| F1 óptimo | 0.4324 | 0.871 | 0.943 | 1.29 | 733 | 0.906 |
| precisión ≥ 0.90 | 0.6054 | 0.9 | 0.893 | 1.33 | 673 | 0.897 |
| precisión ≥ 0.85 | 0.3178 | 0.85 | 0.96 | 1.25 | 765 | 0.902 |
| precisión ≥ 0.80 | 0.1558 | 0.8 | 0.983 | 1.18 | 833 | 0.882 |


Lectura para decidir: la clase accionable es informal=1 (focalización de formalización) y es mayoritaria, así que el lift honesto contra prevalencia importa más que la precisión suelta.

**Mismos umbrales aplicados al test (estimación honesta):**

| punto | umbral | precision_test | recall_test |
|---|---|---|---|
| umbral 0,5 | 0.5 | 0.878 | 0.927 |
| F1 óptimo | 0.4324 | 0.869 | 0.942 |
| precisión ≥ 0.90 | 0.6054 | 0.9 | 0.893 |
| precisión ≥ 0.85 | 0.3178 | 0.851 | 0.962 |
| precisión ≥ 0.80 | 0.1558 | 0.801 | 0.987 |


## Importancia por permutación (caída de PR-AUC, validación)

`categoria` (P507) ramifica la definición del target (independiente→RUC, dependiente→pensión): su importancia alta es POR CONSTRUCCIÓN, no un hallazgo (nota de la ficha técnica).

| index | caida_prauc |
|---|---|
| tamano_empresa | 0.0472 |
| categoria | 0.0309 |
| anios_educ | 0.0237 |
| rama | 0.0157 |
| edad | 0.0093 |
| horas_total | 0.0039 |
| dominio | 0.0027 |
| sexo | 0.0024 |
| area | 0.0012 |
| exper | 0.0003 |
| exper2 | 0.0003 |


- Artefacto `clasificador_gb.joblib`: 0.3 MB (compress=3)
- Contrato del clasificador escrito en `models/feature_schema.json`

## Ablación estructural (tamano_empresa / categoria)

Las dos variables dominantes son las más próximas a la definición operativa del target: en microempresas, no aportar a pensiones es casi estructural — el tamaño no predice la informalidad, en buena medida ES el mecanismo. Mismo protocolo (GB ganador, split y KFold idénticos):

| variante | n_predictores | PRAUC_cv | ROCAUC_cv | PRAUC_test | ROCAUC_test | caida_PRAUC_cv |
|---|---|---|---|---|---|---|
| completa | 11 | 0.9626 | 0.9289 | 0.9605 | 0.9274 | 0.0 |
| V1: sin tamano_empresa | 10 | 0.9571 | 0.9156 | 0.9557 | 0.9152 | 0.0055 |
| V2: sin tamano_empresa ni categoria | 9 | 0.9415 | 0.8903 | 0.9404 | 0.8913 | 0.0211 |


Encuadre: el clasificador NO es una herramienta de predicción a futuro. La informalidad se determina por la configuración del empleo (tamaño de empresa, categoría ocupacional, rama), que se conoce al mismo tiempo que el estatus. Su utilidad es de FOCALIZACIÓN: identificar segmentos donde concentrar programas de formalización a partir de variables observables en registros administrativos, sin verificar caso por caso la afiliación a pensiones. Dicho así, el PR-AUC alto es coherente y esperable, no sospechoso.


Validación externa adicional: el gradiente por tamaño de empresa del modelo replica el patrón oficial del INEI 2025 (88,6% de informalidad en empresas de 1-10 trabajadores, 44% en 11-50, 15,6% en >50).
