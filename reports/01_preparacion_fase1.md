# Fase 1 — Preparación del dataset de modelado

Script: `src/03_fase1_preparacion.py`. Semilla no aplica (sin muestreo: 47.9k < 300k filas).

## Cascada de poblacion

```
mod05 84,853 -> ocupados 57,716 -> 14+ e ingreso>0 47,899
TFNR (P507=5) excluidos por ingreso=0: 6,500 (11.3% de ocupados; ponderado 1,425,458 personas). Son informales por definicion: la poblacion final subestima algo la prevalencia oficial (restriccion de poblacion, no error).
```

## Horas totales (correccion del desajuste)

```
Con ocupacion secundaria: 10,876 (22.7% de la poblacion). Cobertura de horas secundarias (I518/P518) entre ellos: 100.0%.
horas_total = I513T (fallback P513T) + I518 (fallback P518, 0 si no hay secundaria). Cobertura final: 100.0%. Mediana 46 h/sem.
```

## Rama de actividad agrupada (umbral 300 obs.)

```
Colapsadas a 'Otros servicios': ['Electricidad, gas y agua', 'Información y comunicaciones']
rama
Agropecuario y pesca                     12898
Comercio                                  8269
Alojamiento y restaurantes                3799
Manufactura                               3606
Transporte y almacenamiento               3340
Construcción                              2956
Servicios profesionales y financieros     2710
Administración pública                    2572
Enseñanza                                 2544
Otros servicios                           2257
Salud y asistencia social                 1343
Servicio doméstico                         909
Minería e hidrocarburos                    696
```

## Nivel educativo agrupado

```
nivel_educ
Secundaria                19638
Primaria                  10467
Superior técnica           7563
Superior universitaria     7554
Sin nivel/inicial          1469
Posgrado                   1187
```

## Prevalencia de informalidad (validacion externa)

```
Sin target (P510A1/P558A5 faltante): 0 filas.
Prevalencia muestral: 67.4% | PONDERADA (FAC500A): 63.7%.
Referencia INEI 2025: 70,2% nacional (empleo informal, EPEN/ENAHO). Desviacion: -6.5 pts — se esperaba algo menor por la exclusion de los TFNR (informales por definicion, sin ingreso).
```

## Prevalencia ponderada por area (contraste 64,5% urbano / 94,8% rural INEI)

```
Rural     88.1
Urbana    59.1
```

## AUC univariado contra el target informal

```
      variable  auc_univariado
      contrato           0.846
     categoria           0.805
    anios_educ           0.792
          rama           0.782
tamano_empresa           0.780
    nivel_educ           0.770
          area           0.642
       dominio           0.633
         exper           0.592
   horas_total           0.550
          edad           0.526
          sexo           0.513
```

## Ingreso en especie (excluido del target)

```
Ocupados de la poblacion final con pago en especie o autoconsumo (D529T/D540T/D543 > 0): 11,760 (24.6%). El target es solo ingreso monetario; esta exclusion queda declarada.
```

## Dataset final

```
47,899 filas x 20 cols -> data/processed/dataset_modelado.parquet
% nulos por columna:
tamano_empresa    0.5
```

## Validación de constructo: prevalencia reconstruida sobre TODOS los ocupados

La población de modelado excluye a los TFNR (sin ingreso), que son informales
por definición. Para validar la regla se reconstruyó la tasa sobre los 57.716
ocupados completos (regla derivada + TFNR:=informal; cobertura 99,8%):

```
Nacional ponderado: 67,3%   (INEI 2025: 70,2%  ->  -2,9 pts)
Urbano:             61,3%   (INEI: 64,5%       ->  -3,2 pts)
Rural:              91,6%   (INEI: 94,8%       ->  -3,2 pts)
```

Dentro del margen de 3-4 pts en los tres contrastes, con un sesgo uniforme y
explicable: la afiliación a pensiones (P558A5) incluye afiliaciones
autofinanciadas, de modo que algunos asalariados oficialmente informales
cuentan aquí como formales. La derivación queda VALIDADA como constructo.
En la población de modelado (con ingreso > 0) la prevalencia es 67,4%
muestral / 63,7% ponderada — menor que la nacional por la exclusión de TFNR
(6.500 filas; 1,43 M de personas ponderadas), restricción de población
documentada, no error.

## Decisión sobre P511A (tipo de contrato)

AUC univariado 0,846: por debajo del umbral de exclusión (0,85) pero
consistente con su papel de casi-definición para asalariados. NO forma parte
de los predictores del clasificador (nunca estuvo en la lista aprobada); se
conserva en el dataset (`contrato`) únicamente para la réplica E5 de la
consigna de regresión y este diagnóstico.

## Ponderación (decisión de diseño)

- Descriptivos, prevalencias, medianas de cohorte de la app y OLS con lectura
  poblacional: PONDERADOS con FAC500A (viene con coma decimal; convertida).
- Entrenamiento de modelos predictivos: SIN ponderar (el objetivo es precisión
  individual dentro de la muestra, no inferencia poblacional).
