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

## Incidente 24/08/2026: caída en Cloud tras f468c45 (ronda «simple y vivo»)

13. **TODO: re-aterrizar la ronda revertida en cd3a945** (viaje animado SMIL,
    links al código por estación, modo delta y panorama de miniaturas).
    Diagnóstico registrado esa noche:
    - La app pública cayó con `ImportError` levantado por el guard
      `_verificar_graficos()` (`streamlit_app.py:81/89`); Streamlit Cloud
      redacta el mensaje en pantalla — **el nombre exacto que faltaba está
      solo en los logs de Manage app** (leerlos antes de reintentar).
    - En local NO reproduce: en el commit f468c45 el import es limpio y
      `graficos.miniatura_pd`/`viaje_dato` existen (Python 3.12.10; smoke
      Playwright 24/24 antes del push). El traceback de Cloud muestra
      formato de Python 3.13 (`~~~^^`): el entorno de Cloud no es el local.
    - Los números de línea 81/89 son idénticos en f468c45 y 7f18278 (la
      edición de GRAFICOS_REQUERIDOS reemplazó una línea por una línea),
      así que el traceback no identifica qué versión del script corría.
    - Hipótesis principal (consistente con el bug del 20/08 y con el fix
      de caché de cd7f/7f18278): recarga en caliente que reejecuta el
      script principal NUEVO (exige `miniatura_pd`) con el módulo
      `graficos` VIEJO aún en `sys.modules`, y un Reboot que no re-trajo
      el build completo de f468c45.
    - Plan de reintento: (a) leer los logs de Manage app; (b) aterrizar en
      DOS commits — primero `app/graficos.py` solo, después
      `streamlit_app.py` + `GRAFICOS_REQUERIDOS` — para que ninguna
      recarga vea un script que exige nombres que su módulo cacheado no
      tiene; (c) tras el deploy, Reboot completo y smoke en la URL
      pública; (d) evaluar fijar la versión de Python de Cloud a 3.12
      para casar con local.

    **RESUELTO (24/08/2026, mañana).** Re-aterrizado según el plan:
    - **Python fijado en 3.12 en la configuración de la app en Streamlit
      Cloud** (antes corría 3.13; local es 3.12.10) — el pin forzó un
      rebuild completo que se esperó y verificó antes de tocar main.
    - Pre-vuelo bajo Python 3.13.14 real (`uv run --python 3.13`): el
      graficos.py de f468c45 importaba limpio — quedó descartado un fallo
      de sintaxis/import propio de 3.13; la causa de trabajo es la recarga
      en caliente con el módulo viejo (el log de Manage app se perdió con
      la rotación del reboot/rebuild, así que no hay confirmación textual).
    - Aterrizaje en dos commits: f869eb9 (solo app/graficos.py, sin
      consumidores — gate en la URL pública detectando el deploy por el
      viewBox nuevo del SVG) y 509e916 (streamlit_app.py + contrato en el
      mismo commit). Smoke Playwright completo en la URL pública tras cada
      push: título nuevo, animación SMIL, delta con cifra, 849/1.189.
