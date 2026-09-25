# Ablación: el clasificador sin `sexo`

Generado por `src/08b_ablacion_sexo.py`. Mismo protocolo que la ablación estructural: GB con los hiperparámetros ganadores, mismo split y KFold de 5 pliegues, predicciones fuera de pliegue sobre entrenamiento (n = 38.105). Cada variante se evalúa en su propio punto operativo con la regla aprobada, precisión ≥ 0,90 (el umbral de la completa reproduce el del schema, 0.6054).

## Rendimiento global (muestra)

| variante | PRAUC_cv | PRAUC_desv_pliegues | umbral_propio | senalados | precision | recall |
|---|---|---|---|---|---|---|
| completa | 0.9626 | 0.0016 | 0.6054 | 0.6728 | 0.9 | 0.8935 |
| sin sexo | 0.9618 | 0.0014 | 0.6139 | 0.6704 | 0.9 | 0.8903 |


Diferencia de PR-AUC por pliegue (completa − sin sexo): media 0.0009, positiva en 5/5 pliegues. t remuestreado corregido (Nadeau y Bengio, 2003) = 6.26, p = 0.003. Se lee igual que la rejilla ampliada de E9: diferencia sistemática, magnitud irrelevante.

## Por sexo, cada variante en su punto operativo

«muestra» = sin ponderar; «ponderado» = con FAC500A (población).

| variante | sexo | base | n | senalados | precision | recall |
|---|---|---|---|---|---|---|
| completa | Hombre | muestra | 21613 | 0.6585 | 0.8986 | 0.884 |
| completa | Hombre | ponderado | 21613 | 0.5965 | 0.8782 | 0.8388 |
| completa | Mujer | muestra | 16492 | 0.6915 | 0.9018 | 0.9056 |
| completa | Mujer | ponderado | 16492 | 0.653 | 0.8876 | 0.8763 |
| sin sexo | Hombre | muestra | 21613 | 0.6746 | 0.892 | 0.8989 |
| sin sexo | Hombre | ponderado | 21613 | 0.6163 | 0.8709 | 0.8594 |
| sin sexo | Mujer | muestra | 16492 | 0.665 | 0.9106 | 0.8794 |
| sin sexo | Mujer | ponderado | 16492 | 0.6253 | 0.8983 | 0.8493 |


Lectura: la decisión de mantener o retirar `sexo` es del autor. Este reporte mide el costo predictivo y cómo cambian las tasas de error por grupo; no afirma que alguna variante sea «justa».
