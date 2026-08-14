# Fase 0 — Inventario de datos ENAHO 2025 (encuesta 1031)

Detalle por columna en `reports/inventario_columnas.csv`. Diccionario completo
extraído a `data/interim/diccionario_2025.txt` (381 páginas).

## Módulos disponibles

| Módulo | Archivo | Filas | Cols | Contenido | Rol |
|---|---|---|---|---|---|
| 02 | Enaho01-2025-200.csv | 115.145 | 40 | Características de los miembros | Demografía (P207 sexo, P208A edad, P209 estado civil) — el Módulo 05 ya trae copias |
| 03 | Enaho01A-2025-300.csv | 104.446 | 495 | Educación | P301A nivel (1–12), P301B/C año/grado → años de educación |
| 05 | Enaho01a-2025-500.csv | 84.853 | 1.413 | Empleo e ingresos | Núcleo del proyecto |
| 34 | Sumaria-2025.csv | 33.702 | 161 | Agregados del hogar | MIEPERHO (miembros); ESTRSOCIAL; INGHOG2D/GASHOG2D (diagnóstico de leakage, excluidas) |
| 09 | Modulo_09.csv | 505.530 | 47 | Gastos mantenimiento vivienda | No aporta al problema — no se usa |
| 10 | Enaho01-2025-604.csv | 404.424 | 48 | Gastos transporte/comunicaciones | No aporta al problema — no se usa |

Formato INEI confirmado: `sep=";"`, `encoding="latin-1"`, centinela `999999`
documentado en el diccionario para variables monetarias (`9999`/`99`/`9` en
variables de menor ancho). Llaves de persona: CONGLOME+VIVIENDA+HOGAR+CODPERSO
(hogar: sin CODPERSO). Merges verificados al 100% de cobertura.

## Cascada de población (Módulo 05 completo)

| Filtro | Filas |
|---|---|
| Módulo 05 (personas de 14+ elegibles) | 84.853 |
| Ocupados (OCU500 = 1; códigos verificados contra P501) | 57.716 |
| Edad ≥ 14 (P208A) — sin efecto: el módulo ya es 14+ | 57.716 |
| Ingreso laboral mensual > 0 | **47.899** |

Los ~9.800 ocupados sin ingreso son en su mayoría Trabajadores Familiares No
Remunerados (P507=5), que desaparecen de la población final — coherente.

## Columnas candidatas identificadas (verificadas en diccionario + datos)

**Ingreso laboral mensual (target de regresión):** suma de las versiones
imputadas/deflactadas/anualizadas del INEI dividida entre 12:
I524A1 (ocup. principal dependiente), I530A (ganancia neta independiente),
I538A1 e I541A (ocupaciones secundarias). Cobertura: 83% de ocupados;
mediana S/ 1.101. Las crudas (P524A1/P530A/P541A) quedan solo para la autopsia.

**Predictores estructurales (compartidos por ambos modelos):**
- `anios_educ` (derivada de P301A+P301B/C, recode estándar) y experiencia
  potencial = edad − años educ − 6 (+ cuadrado)
- P207 sexo, P208A edad
- Área urbano/rural (ESTRATO 1–5 vs 6–8) y DOMINIO geográfico (8 regiones)
- P506R4 rama de actividad CIIU rev.4 → agrupada a grandes sectores
- P513T horas semana ocup. principal (P520 descartada: solo semanas atípicas, cobertura ~10%)
- P512A tamaño de empresa (1–5)
- P507 categoría ocupacional (dependiente/independiente/empleador)

**Informalidad (target del clasificador):** `OCUPINF` NO existe en la entrega
2025 — se deriva con la regla operativa del INEI:
- Independientes y empleadores (P507 ∈ {1,2}): informal si la unidad no está
  registrada en SUNAT (P510A1 = 3). En población final: 28.037 sin RUC.
- Dependientes (P507 ∈ {3,4,6}): informal si no está afiliado a ningún
  sistema de pensiones (P558A5 = 5). En población final: 30.644 no afiliados.

**Prohibidas como predictoras del clasificador (circularidad con el target):**
P510A1, P510B, P517B1 (registro/contabilidad), P558A1–A5 (pensiones),
P511A (tipo de contrato: "sin contrato" ≈ definición para asalariados —
se verificará con AUC univariado < 0,90 antes de decidir).

**Excluidas por leakage:** INGHOG2D, GASHOG2D, POBREZA, PERCEPHO e ingreso
como predictor de informalidad (ver `00_autopsia_baseline.md` §5).
