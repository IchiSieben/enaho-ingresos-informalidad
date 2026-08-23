> **▶ Demo en vivo:** https://enaho-ingresos-informalidad.streamlit.app

# Ingreso laboral e informalidad en el Perú — ENAHO 2025

Dos modelos desplegados en Streamlit sobre los microdatos de la Encuesta
Nacional de Hogares (ENAHO 2025, INEI): un **regresor del ingreso laboral
mensual** y un **clasificador de empleo informal**. Proyecto hermano del de
**SIS-diabetes** (predicción de adherencia al seguimiento y costo de
atención con datos abiertos del SIS), con los mismos estándares: reproducibilidad total
(`random_state=42`), formulario dirigido por `feature_schema.json`,
precómputo de UI, umbrales elegidos sobre probabilidades out-of-fold y
limitaciones declaradas.

La diferencia de este proyecto es que **no muestra solo el modelo ganador:
muestra el camino**. Una regresión inicial con coeficientes implausibles
destapó un error en los datos de origen —el código de faltante del INEI leído
como un ingreso real— y se convirtió en la primera pieza de un torneo de
nueve especificaciones.

## 1. La autopsia: de dónde parte todo

Una primera regresión del grupo sobre estos datos produjo esta ecuación (en
niveles):

```
INGRESO = 653,35 + 11,47·urbano + 6,39·hombre + 16,11·edad
        + 691,92·primaria + 1.386,35·secundaria + 2.132,97·tecnica
        + 2.834,57·universitaria + 18,76·horas + 6,98·miembros
```

+11 soles por residir en zona urbana y +6 por ser hombre son incompatibles
con las brechas conocidas del mercado laboral peruano. **El problema no
estaba en cómo se modeló, sino en los datos**: el INEI codifica «no sabe»
como 999999 y ese código se leía como un ingreso real de 999.999 soles, algo
que deforma cualquier regresión sobre esa base. En vez de descartar el
resultado se **diagnosticó**, reproduciendo la especificación sobre los
microdatos reales (`reports/00_autopsia_baseline.md`). Tres causas, por orden
de daño:

| Causa | Evidencia medida |
|---|---|
| **El centinela 999999.** El INEI codifica «no sabe» como 999999 en variables monetarias (documentado en el diccionario). Afecta al 2,28 % de la población vía P530A (4,6 % de las ganancias de independientes). | Con centinela: R² 0,023, urbano **−27.141**, técnica **−12.959**. Centinela → NaN: R² 0,248, urbano **+235**, universitaria **+2.201**. Todos los signos se vuelven plausibles con un solo cambio. |
| **Colinealidad educativa.** Años de educación y nivel educativo detallado son la misma variable codificada dos veces. | Juntos: VIF 15–20 y las dummies **cambian de signo** (secundaria +588 → −761) sin mejorar el ajuste. No conviven en ninguna especificación. |
| **Niveles vs log.** El ingreso tiene asimetría 3,98 (mediana S/ 750, p99 S/ 7.000). | La familia principal trabaja en `log(ingreso)` (Mincer) y vuelve a soles con la corrección de smearing de Duan (1983). |

El «índice de bienestar» de la consigna resultó ser **leakage conceptual**:
su contraparte real (ingreso/gasto del hogar) contiene al propio ingreso
individual como sumando (ρ = 0,58, circularidad mecánica). Excluido de todo
modelo.

## 2. El torneo (mismo split 80/20, misma CV de 5 pliegues, sin ponderar)

Selección por **MAE de validación cruzada** — elegir por test tras comparar
nueve especificaciones sería seleccionar sobre el conjunto de evaluación.
MAE en soles con inversión por mediana; las especificaciones en log reportan
además la media con smearing de Duan (residuos out-of-fold de train).

| ID | Especificación | MAE cv | MAE test | R² test (soles) | Interpretab. |
|---|---|---|---|---|---|
| **E9** | **Gradient Boosting (log) · desplegada** | **610,9** | 610,8 | 0,420 | baja |
| E8 | Random Forest (log) | 613,0 | 613,0 | 0,422 | baja |
| E7 | Post-Lasso OLS (Belloni et al. 2014) | 686,9 | 686,9 | 0,262 | media |
| E6 | Depurada · **explicativa** | 690,1 | 691,2 | 0,273 | alta |
| E4 | Mincer extendido | 729,3 | 733,6 | 0,250 | alta |
| E3 | Mincer clásico (educ + exp + exp²) | 823,2 | 834,2 | 0,270 | alta |
| E5 | Réplica del baseline (niveles, ya sin centinela) | 830,3 | 837,1 | 0,243 | alta |
| E2 | log(ingreso) ~ años educación | 847,3 | 862,4 | 0,234 | alta |
| E1 | Ingreso ~ años educación (consigna) | 900,6 | 906,4 | 0,172 | alta |

Detalle completo (RMSE, R² en escala propia, factores de smearing, VIF,
Breusch-Pagan, gráficos de residuos): `reports/torneo_regresion.md` y
`reports/comparacion_torneo.csv`.

**La brecha se interpreta, no solo se reporta**: E9 mejora a E6 en S/ 79 de
MAE (+11,5 %). Esa diferencia estima el aporte de las no linealidades e
interacciones que la forma funcional lineal no captura (Athey & Imbens 2019).
Nótese que ningún R² supera 0,5 en soles. Para situarlo: la ecuación de
Mincer explica típicamente entre un 25 % y un 35 % de la varianza del
**logaritmo del salario** — Mincer (1974), cuadro 5.1: R² = 0,285; Card
(1999), cuadro 1: 0,247–0,328 [1][3]. Ni Lemieux (2006) ni Heckman et al.
(2006) reportan un R², así que no se les puede citar para esto. Y ojo con la
escala: el 0,42 de E9 está **en soles**, mientras que esas cifras están **en
logaritmo** (la Mincer de este torneo, E3, da 0,27). Que en un mercado con
alta informalidad quepa esperar valores iguales o menores es lectura nuestra,
no un resultado publicado.

### Las dos lecturas

- **Predictiva (E9, en la app):** MAE test S/ 611 sobre una mediana de
  S/ 1.101. La app muestra la mediana condicional con la advertencia
  mediana/media (smearing ×1,401) en el panel de resultado.
- **Explicativa (E6 ponderada con FAC500A, errores HC3,
  `reports/modelo_explicativo.md`):** retorno a la educación **4,8 %/año**;
  hombre **+43 %**; urbano **+32 %**; independiente **−50 %**; empresa ≤20
  personas **−33 %** (vs >500); minería **+74 %** (vs comercio); Sierra Norte
  **−31 %** (vs Lima Metropolitana). Coherente con la literatura peruana de
  retornos a la educación (Yamada).

### Robustez medida: el ingreso en especie

El target es solo monetario, pero el 24,6 % de los ocupados recibe pago en
especie o autoconsumo (concentrado en el agro rural) — y su exclusión podría
inflar justo el coeficiente urbano que protagoniza la narrativa. Se midió:
premio urbano 54,6 % (solo monetario) vs 52,0 % (con especie). La exclusión
queda **validada como robusta y declarada**, no escondida.

## 3. El clasificador de empleo informal

`OCUPINF` no viene en la entrega 2025, así que el target se **derivó** con la
regla operativa del INEI: independientes y empleadores → informal si la
unidad no está registrada en SUNAT (P510A1=3); dependientes → informal si no
están afiliados a ningún sistema de pensiones (P558A5=5).

**Validación externa de la derivación** (con factor de expansión FAC500A):

| Contraste | Derivada | Oficial INEI 2025 |
|---|---|---|
| Nacional (todos los ocupados, TFNR incluidos) | 67,3 % | 70,2 % |
| Urbano | 61,3 % | 64,5 % |
| Rural | 91,6 % | 94,8 % |

Sesgo uniforme de ~3 pts, explicable: la afiliación a pensiones incluye
afiliaciones autofinanciadas. Además, el gradiente por tamaño de empresa del
modelo va en el mismo sentido que el patrón oficial: el INEI reporta 88,6 %
de informalidad en empresas de **1 a 10 trabajadores** y 15,6 % en las de más
de 50 [8]. Los tramos de esa publicación no son los de este proyecto (aquí,
«Hasta 20» da 81,1 % ponderado), así que lo que coincide es la dirección y la
magnitud del gradiente, no cada cifra.

**Benchmark** (selección por PR-AUC de validación cruzada; baseline =
prevalencia 0,678):

| Algoritmo | PR-AUC cv | ROC-AUC cv | PR-AUC test | Brier |
|---|---|---|---|---|
| **Gradient Boosting · desplegado** | **0,9626** | 0,9289 | 0,9605 | 0,097 |
| Random Forest | 0,9619 | 0,9279 | 0,9589 | 0,098 |
| Regresión logística (baseline) | 0,9553 | 0,9164 | 0,9526 | 0,105 |

La logística es el punto de referencia obligado y sus odds ratios cuentan la
historia conocida del mercado peruano: empresa ≤20 personas **OR 16,7**,
independiente OR 5,2, urbano OR 0,56, cada año de educación OR 0,82
(`reports/clasificador_informalidad.md`).

**Punto operativo** (elegido sobre probabilidades out-of-fold de train,
nunca sobre test): **precisión ≥ 0,90 para la clase informal**, umbral 0,605
→ recall 0,893, lift 1,33×. El número honesto para la exposición: *de cada
1.000 trabajadores señalados, 900 son efectivamente informales, frente a 678
si se señalara al azar.* El test confirma el punto (0,900 / 0,893).

**Encuadre — léase antes de impresionarse por el PR-AUC:** el clasificador
NO es una herramienta de predicción a futuro. La informalidad se determina
por la configuración del empleo (tamaño de empresa, categoría ocupacional,
rama), que se conoce al mismo tiempo que el estatus. Su utilidad es de
**focalización**: identificar segmentos donde concentrar programas de
formalización a partir de variables observables en registros administrativos,
sin verificar caso por caso la afiliación a pensiones. La **ablación
estructural** lo acota: sin tamaño de empresa, PR-AUC 0,957; sin tamaño ni
categoría, 0,942 — educación, área, rama y horas sostienen la señal restante.
`categoria` (P507) además **ramifica la propia definición del target**
(independiente→RUC, dependiente→pensiones): su importancia alta es por
construcción, no un hallazgo.

## 4. Decisiones de diseño declaradas

- **Ponderación.** El torneo y el entrenamiento van **sin ponderar** (son
  comparación y precisión predictiva intramuestral); los descriptivos,
  prevalencias, medianas de cohorte de la app y el modelo explicativo van
  **ponderados con FAC500A** (lectura poblacional). Cada tabla declara cuál es.
  Detalle técnico: FAC500A viene con **coma decimal** en el CSV del INEI.
- **Target de ingreso.** Suma de las versiones imputadas/deflactadas/
  **anualizadas** del INEI (I524A1, I530A, I538A1, I541A) ÷ 12: un ingreso
  **suavizado**, no el del mes de referencia, y libre del centinela y de la
  trampa de periodicidad de P524A1 (que es «monto del último pago», no mensual).
- **Horas.** P520 solo se pregunta en semanas atípicas (cobertura ~10 %);
  se usa I513T + I518 (principal + secundarias, cobertura 100 %).
- **Población.** Ocupados 14+ con ingreso > 0 (47.899 tras cascada
  documentada). Los 6.500 TFNR quedan fuera por ingreso nulo — restricción de
  población, no error.
- **Anti-circularidad.** Prohibidas como predictoras del clasificador las
  columnas que definen el target (P510A1, P510B, P558A*, P517B1) y P511A
  (contrato, AUC univariado 0,846 — casi definicional para asalariados). El
  ingreso tampoco es predictor de la informalidad.
- **Experiencia potencial** = edad − años educación − 6, truncada en 0
  (0,2 % de negativos). En baja educación sobreestima la experiencia real
  (Heckman, Lochner & Todd 2006). La app la deriva; el usuario no la digita.

### Nota de calidad sobre el material del curso

El archivo `INEI_ENAHO_500registrosML_inicialsol1.xlsx` distribuido como
insumo inicial es un **dataset sintético de práctica**: DNIs falsos,
menores de 2 y 10 años con ingresos de miles de soles, y estados
PEA/ocupado inconsistentes. No se usó. Todo este proyecto — incluida la
réplica del baseline — corre sobre los **microdatos reales** de la ENAHO
2025 descargados del INEI (misma disciplina que la nota DM_Insumos del
proyecto SIS).

## 5. Reproducción

```
python -m venv .venv && .venv\Scripts\pip install -r requirements.txt
# colocar los módulos 02, 03 y 05 de la ENAHO 2025 (encuesta 1031) en data/raw/
.venv\Scripts\python src/00_extraer_diccionario.py
.venv\Scripts\python src/00_inventario.py
.venv\Scripts\python src/01_fase0_poblacion.py
.venv\Scripts\python src/02_fase0_autopsia.py
.venv\Scripts\python src/03_fase1_preparacion.py
.venv\Scripts\python src/04_torneo_regresion.py
.venv\Scripts\python src/05_modelo_explicativo.py
.venv\Scripts\python src/06_entrenar_clasificador.py
.venv\Scripts\python src/07_guardar_regresor.py
.venv\Scripts\python src/08_ablacion_clasificador.py
.venv\Scripts\python src/09_precomputar_ui.py
streamlit run app/streamlit_app.py
```

Los microdatos **no se redistribuyen** en este repositorio (`data/` está en
`.gitignore`); se descargan de los microdatos públicos del INEI
(https://proyectos.inei.gob.pe/microdatos/, ENAHO 2025, encuesta 1031,
módulos 02, 03 y 05).

## 6. Documentación

- [Manual de usuario](docs/manual_usuario.md) — para quien abre la app sin
  conocer el proyecto: qué es (y qué no), cómo llenar el formulario, cómo
  leer cada salida y preguntas frecuentes.
- [Arquitectura](docs/arquitectura.md) — para desarrolladores: el flujo
  completo con diagrama, mapa archivo por archivo, las decisiones de diseño
  con su porqué, cómo reproducir todo y cómo se agregaría una variable nueva.
- [Guía de interpretación de métricas](docs/interpretacion_metricas.md) —
  cada métrica del proyecto (MAE, R², smearing, PR-AUC, calibración, odds
  ratios, VIF…) con qué es, cómo se calcula aquí, el valor obtenido, cómo
  leerlo y qué es razonable esperar según la literatura.
- [Guion de exposición](docs/guion_exposicion.md) — la narrativa en tres
  actos para presentar en 10–15 minutos, los números para tener a mano y las
  preguntas anticipadas con respuesta.
- [Metodología del torneo](docs/METODOLOGIA_TORNEO.md) — qué varía entre E1
  y E9, la verificación de que las nueve se compararon sobre la misma
  muestra y los mismos pliegues, las rejillas de hiperparámetros con su
  re-optimización, el Lasso de E7 y la estabilidad de la importancia de
  variables.
- [Informe de auditoría](INFORME_AUDITORIA.md) — revisión interna del
  repositorio: hallazgos clasificados por severidad, el embudo de datos con
  el N de cada paso, el barrido de centinelas, la reconciliación de la tasa
  de informalidad con el INEI y la lista de lo que quedó sin verificar.

## 7. Qué puedes reutilizar

| Parte | Licencia | Condición |
|---|---|---|
| Código (`src/`, `app/`, `run.ps1`) y artefactos de `models/` | [Apache-2.0](LICENSE) | Los derivados deben declarar los cambios y conservar el contenido de [`NOTICE`](NOTICE) (sección 4d). |
| Documentación, `reports/*.md` y figuras | [CC BY-NC 4.0](docs/LICENSE-DOCS.md) | Atribución obligatoria; sin uso comercial. |
| Microdatos ENAHO 2025 | Del INEI, **no se redistribuyen aquí** | Descarga de la [fuente oficial](https://proyectos.inei.gob.pe/microdatos/) bajo sus términos de uso. |

Para citar el proyecto, GitHub genera la cita desde [`CITATION.cff`](CITATION.cff)
(botón «Cite this repository»).

## 8. Créditos

Proyecto elaborado en el marco del curso de **Machine Learning** de la
**ENEI** (Escuela Nacional de Estadística e Informática, INEI), con el
docente **Orlando Advíncula Zeballos**. Grupo: **Alan Nestor Cañazaca
Mamani**, **Magdalena Quico de la Cruz**, **Yoichiro Palacios Tanaka** y
**Edgar Delgado Ortega**. Autoría detallada y roles CRediT en
[`AUTHORS.md`](AUTHORS.md).

## 9. Marco bibliográfico

- Mincer, J. (1974). *Schooling, Experience, and Earnings*. NBER. — E3 es
  literalmente esta ecuación.
- Heckman, J., Lochner, L. & Todd, P. (2006). "Earnings Functions, Rates of
  Return and Treatment Effects: The Mincer Equation and Beyond". *Handbook of
  the Economics of Education*. — Por qué exp y exp², y los límites de la
  experiencia potencial.
- Lemieux, T. (2006). "The 'Mincer Equation' Thirty Years After". — Vigencia
  y extensiones de la especificación.
- Duan, N. (1983). "Smearing Estimate: A Nonparametric Retransformation
  Method". *JASA* 78(383). — La corrección de retransformación del torneo.
- Athey, S. & Imbens, G. (2019). "Machine Learning Methods That Economists
  Should Know About". *Annual Review of Economics* 11. — El marco para leer
  la brecha OLS vs árboles.
- Belloni, A., Chernozhukov, V. & Hansen, C. (2014). "High-Dimensional
  Methods and Inference on Structural and Treatment Effects". *JEP* 28(2). —
  El sustento (y las cautelas) del post-Lasso (E7).
- Sohnesen, T. P. & Stender, N. (2016). "Is Random Forest a Superior
  Methodology for Predicting Poverty? An Empirical Assessment". World Bank
  Policy Research WP **7612** (el 7970 es otro paper). — Benchmark
  ML vs regresión en encuestas de hogares.
- Yamada, G. (2007). *Retornos a la educación superior en el mercado laboral:
  ¿vale la pena el esfuerzo?* CIES / U. del Pacífico. — Retornos por segmento
  en Perú: 12,5 % anual para asalariados frente a 6,5 % para independientes
  (2004), la brecha que este proyecto vuelve a encontrar.
- INEI — Ficha técnica y diccionario de la ENAHO 2025; informes técnicos de
  empleo e informalidad 2025 (contraste de prevalencias).

---

*Herramienta demostrativa con fines académicos sobre microdatos públicos.
No es un instrumento de fiscalización laboral ni certifica la situación de
ninguna persona.*
