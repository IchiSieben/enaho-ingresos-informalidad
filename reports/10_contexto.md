# 10 · Contexto: brechas, penalidad, retornos y territorio

Generado por `src/10_contexto.py` el 2026-09-26 (commit `324e722`).
Muestra: 47.632 ocupados con ingreso > 0 (casos completos del torneo); 47.000 con horas > 0 para el ingreso por hora. Pesos FAC500A. Tasa ponderada de informalidad en esta muestra: 64,1 %.
Varianza: bootstrap de 200 réplicas por conglomerado (semilla 42); las regresiones llevan errores robustos por conglomerado. Sin estratos: errores algo mayores, en la dirección conservadora.

Todo es **descriptivo o de asociación**. Ninguna cifra de este reporte es un efecto causal.

## 1. Penalidad de la informalidad (log ingreso por hora)

| Especificación | Coef. | IC 95 % | Equivale a | n |
|---|---|---|---|---|
| Capital humano + geografía + sexo | -0,523 | [-0,549; -0,498] | -40,7 % | 47.000 |
| A + rama, categoría y tamaño | -0,238 | [-0,265; -0,210] | -21,1 % | 47.000 |
| Solo asalariados (A) | -0,271 | [-0,295; -0,246] | -23,7 % | 23.260 |
| Solo independientes (A) | -0,511 | [-0,589; -0,432] | -40,0 % | 20.988 |

Mediana ponderada del ingreso por hora: formal S/ 9,05, informal S/ 4,98.

Advertencia de selección: quien trabaja en la informalidad no es una muestra al azar. Controlar por lo observable no quita lo que no se observa (habilidad, preferencias, redes). Por eso la cifra es una diferencia condicional, no el efecto de formalizar a alguien.

## 2. Brecha de género

### Oaxaca-Blinder (dos partes, en log puntos; + = a favor de los hombres)

| Resultado | Controles | Brecha | Referencia | Explicada | No explicada |
|---|---|---|---|---|---|
| Por hora | A | 0,262 | pooled | -0,024 (±0,012) | 0,286 (±0,025) |
| Por hora | A | 0,262 | hombres | -0,021 (±0,011) | 0,282 (±0,025) |
| Por hora | A | 0,262 | mujeres | -0,030 (±0,014) | 0,292 (±0,025) |
| Por hora | B | 0,262 | pooled | -0,012 (±0,020) | 0,274 (±0,024) |
| Por hora | B | 0,262 | hombres | -0,009 (±0,024) | 0,271 (±0,029) |
| Por hora | B | 0,262 | mujeres | 0,012 (±0,028) | 0,250 (±0,031) |
| Mensual | A | 0,415 | pooled | 0,037 (±0,017) | 0,378 (±0,022) |
| Mensual | A | 0,415 | hombres | 0,033 (±0,016) | 0,382 (±0,025) |
| Mensual | A | 0,415 | mujeres | 0,037 (±0,019) | 0,378 (±0,021) |
| Mensual | B | 0,415 | pooled | 0,052 (±0,020) | 0,363 (±0,023) |
| Mensual | B | 0,415 | hombres | 0,054 (±0,022) | 0,361 (±0,027) |
| Mensual | B | 0,415 | mujeres | 0,069 (±0,035) | 0,346 (±0,032) |

Signo de la parte no explicada (por hora) estable entre las seis variantes: **sí**.

### Ñopo (2008), ingreso por hora, como fracción del promedio femenino

| Celdas | Δ total | Δ0 no explicada | ΔH | ΔM | ΔX | Soporte H | Soporte M | Celdas |
|---|---|---|---|---|---|---|---|---|
| educación × edad × área × dominio | 15,4 % | 20,6 % (±4,5) | 0,0 % | 0,0 % | -5,3 % | 99,9 % | 99,8 % | 487 |
| A × categoría | 15,4 % | 21,2 % (±4,5) | 0,4 % | 1,3 % | -7,5 % | 98,7 % | 95,4 % | 1751 |

## 3. Retornos a la educación (log ingreso por hora, por año de educación)

| Segmento | Coef. | IC 95 % | n |
|---|---|---|---|
| total | 8,4 % | [8,0; 8,8] | 47.000 |
| asalariados | 9,4 % | [9,0; 9,8] | 23.260 |
| independientes | 4,5 % | [3,9; 5,2] | 20.988 |
| formales | 10,6 % | [10,0; 11,2] | 14.930 |
| informales | 3,6 % | [3,1; 4,0] | 32.070 |

Contraste referencial, no réplica: Yamada (2007) reporta para 2004 un 12,5 % en asalariados y un 6,5 % en independientes; Psacharopoulos y Patrinos (2018), un 11,0 % privado para América Latina y el Caribe. Los años, las muestras y las especificaciones son distintos.

## 4. Departamentos

| Departamento | n | Informalidad | IC 95 % | Ingreso mensual mediano | Se muestra |
|---|---|---|---|---|---|
| Amazonas | 1.572 | 82,8 % | [79,0; 86,7] | S/ 889 | sí |
| Áncash | 1.982 | 68,4 % | [65,1; 72,2] | S/ 1.053 | sí |
| Apurímac | 1.075 | 75,6 % | [70,9; 80,4] | S/ 819 | sí |
| Arequipa | 2.288 | 54,4 % | [50,4; 58,0] | S/ 1.429 | sí |
| Ayacucho | 1.385 | 78,6 % | [74,4; 82,6] | S/ 805 | sí |
| Cajamarca | 1.899 | 79,4 % | [75,5; 82,5] | S/ 694 | sí |
| Callao | 1.503 | 50,4 % | [47,3; 53,7] | S/ 1.349 | sí |
| Cusco | 1.677 | 72,8 % | [70,1; 76,9] | S/ 1.006 | sí |
| Huancavelica | 1.316 | 83,4 % | [78,8; 86,5] | S/ 701 | sí |
| Huánuco | 1.534 | 82,8 % | [78,8; 86,0] | S/ 739 | sí |
| Ica | 2.305 | 47,0 % | [43,8; 49,5] | S/ 1.589 | sí |
| Junín | 2.193 | 73,3 % | [70,3; 76,2] | S/ 1.121 | sí |
| La Libertad | 2.273 | 59,8 % | [56,7; 62,5] | S/ 1.132 | sí |
| Lambayeque | 2.049 | 65,0 % | [62,1; 67,9] | S/ 1.126 | sí |
| Lima | 6.830 | 54,8 % | [53,0; 56,6] | S/ 1.355 | sí |
| Loreto | 2.117 | 72,7 % | [69,8; 76,1] | S/ 1.040 | sí |
| Madre de Dios | 878 | 77,1 % | [71,9; 81,9] | S/ 1.495 | sí |
| Moquegua | 1.209 | 45,2 % | [40,9; 50,2] | S/ 1.597 | sí |
| Pasco | 1.102 | 67,0 % | [60,9; 72,6] | S/ 1.001 | sí |
| Piura | 2.439 | 67,0 % | [64,4; 70,1] | S/ 1.123 | sí |
| Puno | 1.086 | 81,5 % | [77,3; 86,1] | S/ 914 | sí |
| San Martín | 2.117 | 79,0 % | [75,8; 82,3] | S/ 1.102 | sí |
| Tacna | 1.662 | 63,4 % | [59,5; 67,9] | S/ 1.199 | sí |
| Tumbes | 1.246 | 75,1 % | [72,1; 78,7] | S/ 1.036 | sí |
| Ucayali | 1.895 | 74,5 % | [71,3; 77,5] | S/ 1.125 | sí |

Control de agregación: la media ponderada de las celdas reproduce la tasa de la muestra (64,1 %).

## 5. Lengua materna (oculto en la app: `MOSTRAR_LENGUA = False`)

Se analiza agregada y como brecha estructural, no como juicio sobre personas: la lengua materna se asocia con dónde se nació, qué escuela hubo y qué mercado laboral queda cerca.

| Lengua | n | Informalidad | Ingreso mensual mediano | Brecha ajustada por hora vs. castellano | Se muestra |
|---|---|---|---|---|---|
| Aimara | 1.052 | 80,1 % | S/ 1.036 | -22,9 % [-31,4; -13,4] | sí |
| Castellano | 37.764 | 61,0 % | S/ 1.249 | referencia | sí |
| Otra lengua originaria | 667 | 88,8 % | S/ 548 | -30,0 % [-38,8; -19,9] | sí |
| Quechua | 8.033 | 79,4 % | S/ 918 | -8,9 % [-12,8; -4,8] | sí |

## Alarmas

- Ninguna.

## Limitaciones

- Ingreso monetario declarado, sin ingreso en especie. Es el mismo del resto de la app.
- El ingreso por hora usa horas habituales de la semana de referencia × 52/12.
- Se ignoran los estratos del diseño muestral, así que los intervalos son algo conservadores.
- La muestra excluye a los trabajadores familiares no remunerados (ingreso 0), que son informales por definición. Por eso la tasa de informalidad queda por debajo de la oficial.
