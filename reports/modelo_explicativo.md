# Modelo explicativo del ingreso laboral (lectura poblacional)

Generado por `src/05_modelo_explicativo.py`. Ponderado con el factor de expansión de empleo (FAC500A): los coeficientes describen a la población ocupada con ingreso, no a la muestra. Separado deliberadamente del torneo (sin ponderar): son objetivos distintos y sus tablas no se mezclan.


## E4 — Mincer extendido: E3 + sexo + área + log(horas) + rama

WLS ponderada por FAC500A, n=47,632, R² 0.3831. `efecto_pct` = (exp(coef)−1)·100: cambio porcentual del ingreso asociado a +1 unidad (o a la categoría vs su base).

| index | coef | ee_HC3 | p | efecto_pct |
|---|---|---|---|---|
| const | 3.5808 | 0.0589 | 0.0 | nan |
| anios_educ | 0.0627 | 0.0018 | 0.0 | 6.5 |
| exper | 0.033 | 0.0011 | 0.0 | 3.4 |
| exper2 | -0.0006 | 0.0 | 0.0 | -0.1 |
| hombre | 0.4046 | 0.0129 | 0.0 | 49.9 |
| urbano | 0.4886 | 0.0163 | 0.0 | 63.0 |
| log_horas | 0.4037 | 0.0139 | 0.0 | 49.7 |
| rama_Administración pública | 0.7308 | 0.0235 | 0.0 | 107.7 |
| rama_Agropecuario y pesca | -0.0721 | 0.0226 | 0.0014 | -7.0 |
| rama_Alojamiento y restaurantes | 0.1989 | 0.0241 | 0.0 | 22.0 |
| rama_Construcción | 0.4423 | 0.022 | 0.0 | 55.6 |
| rama_Enseñanza | 0.8094 | 0.0268 | 0.0 | 124.7 |
| rama_Manufactura | 0.2067 | 0.0229 | 0.0 | 23.0 |
| rama_Minería e hidrocarburos | 0.8147 | 0.0357 | 0.0 | 125.9 |
| rama_Otros servicios | 0.1577 | 0.0289 | 0.0 | 17.1 |
| rama_Salud y asistencia social | 0.791 | 0.0322 | 0.0 | 120.6 |
| rama_Servicio doméstico | 0.3682 | 0.0298 | 0.0 | 44.5 |
| rama_Servicios profesionales y financieros | 0.4362 | 0.0248 | 0.0 | 54.7 |
| rama_Transporte y almacenamiento | 0.0837 | 0.0222 | 0.0002 | 8.7 |


## E6 — Depurada: E4 + categoría + tamaño empresa + dominio (sin la dummy rama=Servicio doméstico, colineal perfecta con categoría=Trabajador del hogar)

WLS ponderada por FAC500A, n=47,632, R² 0.4729. `efecto_pct` = (exp(coef)−1)·100: cambio porcentual del ingreso asociado a +1 unidad (o a la categoría vs su base).

| index | coef | ee_HC3 | p | efecto_pct |
|---|---|---|---|---|
| const | 4.8641 | 0.0585 | 0.0 | nan |
| anios_educ | 0.0469 | 0.0018 | 0.0 | 4.8 |
| exper | 0.0398 | 0.001 | 0.0 | 4.1 |
| exper2 | -0.0006 | 0.0 | 0.0 | -0.1 |
| hombre | 0.3605 | 0.0117 | 0.0 | 43.4 |
| urbano | 0.2799 | 0.0164 | 0.0 | 32.3 |
| log_horas | 0.3423 | 0.0116 | 0.0 | 40.8 |
| rama_Administración pública | 0.1147 | 0.0262 | 0.0 | 12.2 |
| rama_Agropecuario y pesca | -0.1074 | 0.0212 | 0.0 | -10.2 |
| rama_Alojamiento y restaurantes | 0.1343 | 0.0231 | 0.0 | 14.4 |
| rama_Construcción | 0.3023 | 0.0211 | 0.0 | 35.3 |
| rama_Enseñanza | 0.308 | 0.0252 | 0.0 | 36.1 |
| rama_Manufactura | 0.0713 | 0.0214 | 0.0009 | 7.4 |
| rama_Minería e hidrocarburos | 0.5519 | 0.0345 | 0.0 | 73.7 |
| rama_Otros servicios | 0.085 | 0.0262 | 0.0012 | 8.9 |
| rama_Salud y asistencia social | 0.3279 | 0.0314 | 0.0 | 38.8 |
| rama_Servicios profesionales y financieros | 0.2431 | 0.0237 | 0.0 | 27.5 |
| rama_Transporte y almacenamiento | 0.2687 | 0.0211 | 0.0 | 30.8 |
| categoria_Empleador | 0.2938 | 0.033 | 0.0 | 34.1 |
| categoria_Independiente | -0.6858 | 0.0176 | 0.0 | -49.6 |
| categoria_Obrero | -0.1832 | 0.0137 | 0.0 | -16.7 |
| categoria_Trabajador del hogar | -0.0301 | 0.0275 | 0.2744 | -3.0 |
| tamano_empresa_101 a 500 | -0.1195 | 0.0232 | 0.0 | -11.3 |
| tamano_empresa_21 a 50 | -0.2206 | 0.0232 | 0.0 | -19.8 |
| tamano_empresa_51 a 100 | -0.2256 | 0.0271 | 0.0 | -20.2 |
| tamano_empresa_Hasta 20 | -0.4062 | 0.0167 | 0.0 | -33.4 |
| dominio_Costa Centro | -0.0033 | 0.0157 | 0.8343 | -0.3 |
| dominio_Costa Norte | -0.1287 | 0.0152 | 0.0 | -12.1 |
| dominio_Costa Sur | 0.0772 | 0.0205 | 0.0002 | 8.0 |
| dominio_Selva | -0.0275 | 0.0163 | 0.0924 | -2.7 |
| dominio_Sierra Centro | -0.2218 | 0.0192 | 0.0 | -19.9 |
| dominio_Sierra Norte | -0.3722 | 0.0275 | 0.0 | -31.1 |
| dominio_Sierra Sur | -0.1553 | 0.019 | 0.0 | -14.4 |


### Bases de comparación de las categorías

Mujer, área rural, Lima Metropolitana, rama Comercio, empresa de más de 500 personas y categoría Empleado son las bases omitidas; cada dummy se lee contra ellas.

