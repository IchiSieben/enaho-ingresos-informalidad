# Fase 0 — Autopsia de la regresión baseline (ENAHO 2025)

Fuente: microdatos ENAHO 2025 (INEI, encuesta 1031). Módulos 02, 03, 05 y 34
(sumaria). **La réplica se corrió sobre los microdatos reales del INEI, no
sobre el archivo de práctica del curso** (`INEI_ENAHO_500registrosML_
inicialsol1.xlsx`, que es sintético: DNI falsos, menores de 2 y 10 años con
ingresos de miles de soles; ver nota de calidad en el README). Scripts: `src/00_inventario.py`, `src/01_fase0_poblacion.py`,
`src/02_fase0_autopsia.py`. Población: ocupados (OCU500=1), edad ≥ 14, con
ingreso laboral reportado.

## 1. El problema del centinela 999999

El diccionario del INEI documenta `999999 Missing value` en todas las variables
monetarias declaradas. Magnitud medida sobre el archivo completo del Módulo 05:

| Variable | Descripción | No nulos | Centinelas | % |
|---|---|---|---|---|
| P524A1 | Ingreso último pago (dependientes) | 25.147 | 376 | 0,44% |
| P530A  | Ganancia neta mes anterior (independientes) | 25.908 | 3.883 | **4,58%** |
| P541A  | Ganancia ocupación secundaria | 5.755 | 1.048 | 1,24% |
| I524A1, I530A, I538A1, I541A | Versiones imputadas/anualizadas del INEI | — | **0** | 0% |

En la población de estudio, el ingreso "ingenuo" (P524A1 ∪ P530A leído como
mensual) contiene **1.093 centinelas (2,28%)**: la media salta a S/ 24.022
contra una mediana de S/ 794.

## 2. Reproducción de la especificación inicial del curso

Misma ecuación (niveles, dummies de nivel educativo, horas, miembros), mismo
dataset, dos corridas. Errores estándar HC3.

| | Corrida A: centinela SIN limpiar (n=47.889) | Corrida B: centinela → NaN (n=46.796) |
|---|---|---|
| R² | **0,023** | **0,248** |
| urbano | **−27.141** | +235 |
| hombre | +4.937 (ns) | +255 |
| edad | +204 | +13,8 |
| secundaria | −6.957 (ns) | +588 |
| técnica | **−12.959** | +1.216 |
| universitaria | −10.296 (ns) | +2.201 |
| horas | **−653** | +11,7 |
| miembros | −429 (ns) | +6,9 |

Lectura: con 2,28% de filas en 999999, el modelo "aprende" a perseguir
outliers de un millón de soles: residir en zona urbana "cuesta" 27 mil soles y
la educación técnica "reduce" el ingreso en 13 mil. Basta convertir el
centinela a NaN para que **todos** los signos se vuelvan económicamente
plausibles y el R² se multiplique por 10. La ecuación inicial
(urbano +11,47, hombre +6,39) es consistente con este mecanismo: coeficientes
diluidos por ruido masivo en la variable dependiente.

## 3. Colinealidad años de educación vs nivel educativo detallado

La consigna pide incluir ambos. Corrida C = B + `anios_educ`:

- VIF: secundaria 18,7 — técnica 15,0 — universitaria 19,5 — anios_educ 8,1
  (en B, sin años, los VIF de las dummies eran 5,9–9,5).
- Los coeficientes de las dummies **cambian de signo** (secundaria pasa de
  +588 a −761) sin que el ajuste mejore materialmente (R² 0,248 → 0,269).

Años de educación y nivel detallado son codificaciones de la misma variable:
juntos son ininterpretables. Decisión propuesta: la familia Mincer usa
`anios_educ`; el nivel detallado se usa solo como alternativa (no junto).

## 4. Outliers y la escala del ingreso

Ingreso limpio: asimetría 3,98, mediana S/ 750, p99 S/ 7.000, máximo S/ 31.200.
Cola larga clásica → el target de la familia principal será `log(ingreso)`
vía `TransformedTargetRegressor(log1p/expm1)` con corrección de smearing para
volver a soles (Duan, 1983).

## 5. INDICE_BIENESTAR: diagnóstico de circularidad

La consigna incluye un "índice de bienestar". Sus contrapartes reales y su
correlación (Spearman) con log(ingreso individual):

| Candidata | ρ | Veredicto |
|---|---|---|
| INGHOG2D (ingreso neto del hogar) | 0,575 (0,619 per cápita) | **Circularidad mecánica**: el ingreso individual es un sumando de INGHOG2D. Excluida. |
| GASHOG2D (gasto del hogar) | 0,364 | Post-tratamiento: el gasto es consecuencia del ingreso. Excluida de modelos explicativos. |
| POBREZA | 0,238 | Derivada de INGHOG2D/línea de pobreza. Excluida. |
| ESTRSOCIAL (estrato A–E/rural del marco censal) | −0,384 | Pre-determinada (se asigna al conglomerado en el marco muestral, no al hogar por su ingreso). Admisible como control geográfico, redundante con urbano/dominio. |

Confirmación de la hipótesis: el "índice de bienestar" (en cualquiera de sus
versiones hogar-monetarias) es leakage conceptual y queda fuera de todo modelo.

## 6. Consecuencias para el diseño

1. Centinelas → NaN antes de cualquier cálculo (regla ya aplicada).
2. Target de regresión: `ingreso_laboral_mes` = (I524A1 + I530A + I538A1 +
   I541A) / 12 — las versiones **imputadas, deflactadas y anualizadas** del
   INEI, libres de centinela y de la trampa de periodicidad de P524A1 (que es
   "monto del último pago", no mensual: depende de P523 diario/semanal/
   quincenal/mensual).
3. Familia principal en log; especificaciones en niveles solo como parte del
   torneo (E1, E5).
4. `anios_educ` y nivel detallado no conviven en una misma especificación.
5. Fuera INGHOG2D, GASHOG2D, POBREZA y derivados.
