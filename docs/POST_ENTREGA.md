# Post-entrega — backlog priorizado para la v2 del portafolio

> Congelado el 23/08/2026, al cierre de la entrega del curso. Regla de la
> corrida de entrega: nada de esto se toca en la versión desplegada que se
> expone. Todo cambio de esta lista va en rama aparte y con los mismos
> estándares del proyecto (artefactos versionados, verificación con
> Playwright, cifras trazables).

## Interfaz

1. **Migración de componentes a streamlit-shadcn-ui.** Requiere Streamlit
   ≥ 1.60; evaluar en rama aparte, nunca directo al main desplegado.
   Inventariar antes qué componentes propios (tarjetas, franja de
   probabilidad, medidores) tienen equivalente real.
2. **Toggle en vivo GB ↔ RF en ambas pestañas.** Requiere entrenar y
   versionar los artefactos RF que hoy no existen en `models/` (solo hay
   hiperparámetros en `_hiperparametros.json`); duplicar la verificación de
   contratos de la app.
3. **Clic-para-fijar-umbral con selection events.** Verificar la API de
   `st.plotly_chart`/selection events contra la versión de Streamlit
   desplegada antes de tocar nada.
4. **GIF/animación de carga personalizada.**

## Narrativa y visualización

5. **Scrollytelling «cómo se construyó esta app»**: datos → entrenamiento →
   artefactos → deploy, con animación.
6. **Visualización comparativa de cómo aprenden GB vs RF**: secuencial que
   corrige residuos vs paralelo que promedia árboles — la diferencia de
   núcleo, animada.
7. **Mapa 3D por departamento con pydeck** (Fase 6 del plan maestro,
   pendiente desde la auditoría).

## Deuda de auditoría (INFORME_AUDITORIA.md)

8. **AC-1: auditar las rejillas del clasificador** (GB 3/3 hiperparámetros
   en el borde; el PR-AUC 0,9626 no está confirmado como óptimo). Mismo
   tratamiento que recibió el regresor: ampliar, test pareado, decidir con
   criterio sustantivo.
9. **NV-1: validación anidada** para cuantificar el optimismo por doble
   inmersión de la selección de hiperparámetros.
10. **AC-2: trasladar al código** las tres secciones manuales del reporte de
    Fase 1 (validación de constructo, P511A, ponderación).
11. **AC-4: revisar `n_jobs`** en `src/06_entrenar_clasificador.py` y
    `src/08_ablacion_clasificador.py` (la máquina tiene 6 núcleos reales;
    `n_jobs=1` en el estimador cuando está dentro de GridSearchCV).

## Reutilización

12. **Paquete PyPI de auditoría de microdatos ENAHO** (`enahoaudit` o
    similar). Nicho: barrido de centinelas, factores de expansión con coma
    decimal, tabla umbral → consecuencias, embudo de N reproducible.
