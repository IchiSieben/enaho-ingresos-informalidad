# Notas de arquitectura: Predictor de ingresos e informalidad (ENAHO 2025)

Fuente de estas notas: el código del repo, verificado línea por línea. `docs/arquitectura.md` se usó como guía y no se modificó. Lo que no está en el código figura como "por confirmar" y no se dibuja.

## 1. Las 9 preguntas del manual

1. **Actores.** Una persona visitante que abre la página del proyecto en el sitio del portafolio o entra directo a la app. Sistemas externos: el INEI (fuente de los microdatos, descarga manual), GitHub (repo público), Streamlit Cloud (hospeda la app). No hay roles ni autenticación: la app es de solo lectura y sin cuentas.
2. **Contenedores.** (a) Microdatos del INEI, CSV en `data/raw/` (no versionados). (b) Carpeta `data/` local con `interim/` y `processed/` en parquet (ignorada por git, `.gitignore`). (c) Pipeline de entrenamiento, scripts `src/00` a `src/09` en Python 3.12 (pandas, scikit-learn, statsmodels), corre en el PC Windows del autor. (d) Carpeta `models/` con 3 `.joblib`, `feature_schema.json`, `ui_artifacts.json`, `ui_maquinas.json` y la caché de hiperparámetros, versionada en el repo. (e) Repo en GitHub. (f) App Streamlit (`app/streamlit_app.py`) en Streamlit Cloud. (g) Navegador del visitante. (h) Ficha y página del proyecto en el sitio del portafolio (repo aparte, en Hostinger). Escala: la app no entrena ni lee `data/`; cada sesión carga los modelos cacheados (`st.cache_resource`), así que escala con lo que dé el plan gratuito de Streamlit Cloud (límites por confirmar).
3. **Llamadas reales.** Ver la tabla de la sección 2.
4. **Flujos.** "Entrenar el torneo y publicar artefactos", "Una predicción en la app", "Publicar un modelo nuevo".
5. **Núcleo.** No aplica como hexagonal: no hay API ni lógica de negocio servida. El "núcleo" es el contrato entre entrenamiento y app (`feature_schema.json` + `ui_artifacts.json`), cubierto en la vista de datos.
6. **Datos.** No hay base de datos. Estructura de archivos: `data/raw` (CSV) a `data/interim` y `data/processed` (parquet) a `models/` (joblib y JSON) a `reports/` (Markdown, CSV, figuras). Detalle en la vista "Datos".
7. **Despliegue.** Local: `run.ps1` (corre un script de `src/` con `python -u` y deja logs en `logs/`). Nube: Streamlit Cloud sirve `app/streamlit_app.py` con `requirements.txt` y el `models/` del repo; `.streamlit/config.toml` fija el tema. No hay workflows de CI en el repo (no existe `.github/workflows`).
8. **Historias de usuario.** No aplica (proyecto de análisis y demostración, no nació de requisitos de terceros).
9. **Decisiones.** Se infieren de `docs/arquitectura.md` §3 y se verificaron en código (no existe `docs/DECISIONES.md`). Marcadas como inferidas en la página.

## 2. Tabla de llamadas con evidencia

| Id | De a | Qué viaja | Evidencia (archivo:función) |
|---|---|---|---|
| e1 | INEI a `data/` | CSV crudos de los módulos 02, 03, 05, 34 (descarga manual, no es código) | `docs/arquitectura.md` §4; `src/comun.py:27` (`DIR_RAW`), `src/comun.py:85` (`leer_enaho`) |
| e2 | `data/` a pipeline | lectura de CSV y parquet entre etapas | `src/03_fase1_preparacion.py:39-41,177`; `src/04_torneo_regresion.py:60,63,70,384`; `src/06_entrenar_clasificador.py:139` |
| e3 | pipeline a `models/` | `.joblib`, `feature_schema.json` por secciones, `ui_artifacts.json`, `ui_maquinas.json` | `src/comun.py:268` (`escribir_json_atomico`), `src/comun.py:300` (`guardar_schema`), `src/06_entrenar_clasificador.py:306`, `src/07_guardar_regresor.py:52`, `src/08_ablacion_clasificador.py:82`, `src/09_precomputar_ui.py:47,731` |
| e4 | `models/` a GitHub | git push (los artefactos viajan versionados; `data/` queda fuera) | `.gitignore` (`data/` ignorado), `git ls-files` lista `models/*.joblib` y `models/*.json` |
| e5 | GitHub a Streamlit Cloud | la nube sirve el repo público con `requirements.txt` | `README.md:3` (URL de la demo), `docs/arquitectura.md` §4, comentario en `app/streamlit_app.py:2672` ("la nube no reentrena"). Disparo automático al hacer push: por confirmar, no está en el código |
| e6 | navegador a app | HTTPS; parámetros `?sec=` `?lang=` `?theme=` | `app/streamlit_app.py:390` (`sincronizar_url`), `app/streamlit_app.py:3474` (`main`) |
| e7 | navegador a Landing | GET de la página `/predictor-ingresos/` | `Landing/src/pages/predictor-ingresos/index.astro`, `PredictorIngresosPage.astro` (otro repo) |
| e8 | Landing a app | enlace saliente a la demo | `Landing/src/components/PredictorIngresosPage.astro:67` (`href={data.demoUrl}`); `demoUrl` en la ficha `predictor-ingresos.md` |

Dentro de la app (no son llamadas entre contenedores, van en el texto del flujo): `cargar_modelo` (`streamlit_app.py:286`, `joblib.load`), `modelo.predict` (`:1112`), `predict_proba` (`:1382`), `@st.fragment` en `_ingreso_en_vivo` (`:1096`), `_informalidad_en_vivo` (`:1368`) y `bloque_umbral` (`:869`).

## 3. Por confirmar (no dibujado)

- Si Streamlit Cloud se redespliega solo en cada push a la rama principal (configuración de la plataforma, no del repo).
- Rama y archivo principal configurados en Streamlit Cloud; límites de memoria y de visitas del plan.
- La página `/predictor-ingresos/` de la Landing no incrusta la app con iframe hoy (`PredictorIngresosPage.astro` solo enlaza `demoUrl`); no se dibuja ningún iframe.
- Si el entrenamiento se ejecutó alguna vez en la Mac mini: nada en el código lo indica; solo se dibuja el PC Windows.
- Estado de la ejecución de pruebas (`tests/`) en CI: no hay CI en el repo.

## 4. Observaciones de privacidad del repo (no se copian a la página)

- `app/streamlit_app.py` (constantes `AUTOR` y `GRUPO`, líneas 63-65, lista de grupo incluida) y las cabeceras de `src/*.py` contienen el nombre del autor y de tres compañeros de grupo del curso. La página generada no los repite.
- `app/streamlit_app.py:66` y `app/estilos.py` apuntan a un dominio de portafolio anterior al actual.
- `docs/presentacion/` incluye logos institucionales y material del curso; revisar antes de publicar el repo como caso de estudio.
