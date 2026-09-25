# Diagnóstico v2: de app de curso a trabajo de investigación

> Autoría: Yoichi Palacios Tanaka, con el grupo ENEI (Alan Nestor Cañazaca
> Mamani, Magdalena Quico de la Cruz, Edgar Delgado Ortega).
> Fecha: 24/09/2026 · Base: `main` en `004dbbe` (v1.1 bilingüe, en producción).
> Fase 1 del plan v2: solo diagnóstico, no se ha cambiado nada del código.

## Cómo se hizo este diagnóstico

- Lectura del repo completo (`README.md`, `INFORME_AUDITORIA.md`, `docs/`,
  `reports/`, `src/`, `app/`, `tests/`, `models/`).
- Recorrido de la app local en `?lang=es` y `?lang=en`: las 5 secciones con
  todos los expanders abiertos y el texto de los iframes, leído como las tres
  personas del encargo. También una captura móvil a 390 px.
- Comprobaciones puntuales sobre los microdatos (`data/`, fuera del repo):
  conteos de celdas para lengua materna, autoidentificación étnica y
  departamento dentro de la población modelada (n = 47.899 antes del
  recorte final a 47.632).
- Un agente de reconocimiento y uno de recorrido hicieron la primera pasada.
  **Se desmintieron seis de sus afirmaciones** al verificarlas (ver el
  anexo A). Aquí entra solo lo verificado.

---

## 1. Inventario honesto

### Sólido (verificado)

| Qué | Evidencia |
|---|---|
| Separación predictivo / explicativo | Torneo E1–E9 sin ponderar y elegido por `MAE_cv` (no por test); modelo explicativo E6 aparte, WLS + FAC500A + HC3. |
| Disciplina anti-fuga | Sección «¿es demasiado bueno?» en la ficha, ablación (PR-AUC 0,9626 → 0,9415 sin tamaño ni categoría), P511A fuera del clasificador, INGHOG2D excluido y contado. |
| Lenguaje causal | La dependencia parcial se rotula como «asociación, no efecto causal» en todas las pestañas y en los dos idiomas. |
| R² bien calibrado | `R2_MINCER_CANONICO` separa el R² en soles (E9, 0,42) del R² en log (Mincer/Card, 0,25–0,33) y aclara que Lemieux y Heckman et al. no reportan R². |
| Ponderación declarada | La tabla de procedencia dice qué va ponderado con FAC500A (cohortes, comparables) y qué no (curvas, entrenamiento). |
| Precómputo e integridad | Nada caro en caliente; `ui_artifacts.json` con SHA256 fijo (`BE5122B5…1D14E1`, 45.815 bytes); artefacto hermano `ui_maquinas.json`. |
| Contratos | 17 tests: temas, `GRAFICOS_REQUERIDOS`, claves de artefactos, invalidación de caché, traducciones del schema y perfiles válidos. |
| i18n | Sin español residual en EN ni inglés residual en ES en las 10 vistas leídas. Formato numérico correcto por idioma (`× 1,401` / `× 1.401`, `47.632` / `47,632`). |
| Despliegue | Protocolo de dos commits más gate en la URL pública; v1.1 verificada en la nube con conteos de texto idénticos a local. |
| Autocrítica pública | La sección de auditoría de la ficha (centinela 999999, 88,6 % mal etiquetado, tres R² contradictorios) es la mejor señal de credibilidad de la app. |

### A medias

| Qué | Estado real |
|---|---|
| Rejillas del clasificador (AC-1) | GB con 3/3 hiperparámetros en el borde de la rejilla: el PR-AUC 0,9626 **no está confirmado como óptimo**. En el regresor la re-optimización ya dio 0,59 % (no se promovió). |
| Optimismo de la selección (AC-3) | Sin validación anidada: el `best_score_` de GridSearch y el `MAE_cv` del torneo son la misma cifra en E9. |
| Trazabilidad de Fase 1 (AC-2) | Tres secciones de `reports/01_preparacion_fase1.md` están escritas a mano (sus cifras son correctas, pero no las reproduce el script). |
| Incertidumbre de métricas | La app muestra ±1 desviación entre pliegues en las barras de dependencia parcial, pero **no** en MAE ni en PR-AUC: son estimaciones puntuales. |
| Calibración | Curva de confiabilidad y Brier 0,0974, sin ECE ni lectura de los extremos. |
| Caché del schema | `cargar_schema()` sigue con caché eterna por proceso: el mismo defecto del 20/08, todavía latente. |
| Artefacto huérfano (CO-1) | `clasificador_gb_reducido.joblib` (309 KB) viaja a Cloud y ningún módulo de `app/` lo carga (0 referencias). |
| Commit en la ficha | Muestra `ffaed0bcca3d` con el rótulo «Artefactos de UI · 2026-08-20»: es correcto (commit de los artefactos, no del código desplegado), pero el rótulo no lo dice. Un ingeniero ML lo va a leer como el commit en producción. |

### Inmaduro o no verificado

- **Marco teórico: inexistente.** Perry et al. (2007) y Loayza (2008) están
  en las referencias, pero ninguna escuela de pensamiento (dualista,
  estructuralista, legalista, voluntarista) se usa para leer los resultados.
  Faltan De Soto, Ñopo, Maloney, Hart y Matos Mar.
- **Selección muestral sin marco.** Solo se modelan personas ocupadas con
  ingreso > 0. Se menciona como límite, pero no se conecta con Heckman (1979)
  ni se dice qué sesga.
- **Benchmarks del INEI sin fuente citable (NV-7).** El 70,2 %, 64,5 %,
  94,8 % y el 88,6 / 44 / 15,6 % por tamaño no tienen una referencia en el
  repo. Rompe la regla «ningún número sin referencia».
- **Citas existentes sin re-verificar en esta ronda.** Después del error con
  Lemieux y Heckman, las `nota` de Yamada (2007), Perry et al. (2007),
  Loayza (2008), Sohnesen y Stender (2016) y el resto de
  `app/referencias.py` (16 entradas) pasan a **«a re-verificar en Fase 2»**.
  No se certifican aquí.
- **`INFORME_AUDITORIA.md` está desactualizado.** Todavía presenta AC-5 y
  AC-6 como hallazgos abiertos, aunque la app y el README ya los corrigieron
  (y la ficha los narra como resueltos). Un economista que abra ese archivo
  ve errores que ya no existen, y ninguna marca de «resuelto».

---

## 2. Brechas por persona

### Lector de afuera (reclutador, sin contexto del Perú ni de ML)

- **Primer minuto:** entra directo a un formulario de ingreso. No hay ni una
  línea de «por qué importa»: no se dice qué es el empleo informal, que el
  Perú está en torno al 70 %, ni qué significa eso para la pensión o la salud.
- **Siglas sin glosa:** la primera línea visible es «INEI · ENAHO 2025 ·
  PERÚ». «RUC» aparece en la pestaña de informalidad sin explicación. PR-AUC,
  MAE y dependencia parcial solo se explican dentro de expanders.
- **Todo arranca colapsado:** «Detalle técnico», «Cómo leer estas cifras» y
  «Tu perfil frente a la cohorte» empiezan cerrados. Para alguien sin
  contexto, eso se lee como «no hay más».
- **Lo mejor está al fondo:** el viaje del dato (601,3 MB → 12,3 MB), el
  embudo en Sankey y la auditoría propia son lo más impresionante, y están
  en las pestañas 4 y 5.
- **Arranque en frío:** la app de Streamlit Cloud se duerme por inactividad.
  Un enlace frío muestra «Zzzz» y un botón, y tarda cerca de un minuto en
  levantar. Esto ya tiene solución prevista en el portafolio: la página
  estática `/predictor-ingresos/` con video y un iframe `?embed=true`. El
  diagnóstico lo ata a ese plan, no a pings artificiales.
- **Wow disponible:** una portada «Empieza aquí» con el Perú en 60 segundos,
  personajes ficticios y un recorrido guiado. También un glosario al pasar el
  cursor.

### Economista / científico social

- **A favor:** calibración del R², disciplina causal, ponderación declarada y
  modelo explicativo con HC3.
- **Le falta la conversación académica:** los hallazgos quedan descriptivos.
  El 81 % de informalidad en firmas «hasta 20» frente al 10 % en grandes, o
  la brecha rural, no se leen contra ninguna teoría. ¿Exclusión o salida
  (Maloney)? ¿Segmentación (dualistas)? ¿Costos de la formalidad (De Soto)?
- **Brechas no descompuestas:** hay sexo y dominio como variables, pero no
  hay Oaxaca-Blinder ni Ñopo. Tampoco penalidad de la informalidad, ni
  retornos a la educación por segmento (Yamada 2007 lo pide explícitamente).
- **Diseño muestral:** los errores estándar del modelo explicativo usan HC3,
  pero no el diseño complejo de la ENAHO (estratos y conglomerados). Para
  inferencia poblacional eso subestima la incertidumbre.
- **Variables sensibles con peso visual indistinto:** en la pestaña de
  informalidad, la dependencia parcial por sexo (66 % mujeres frente a 63 %
  hombres) se dibuja con el mismo peso que tamaño de empresa (81 % frente a
  10 %). No hay marco de brechas estructurales.

### Ingeniero de ML

- **A favor:** anti-fuga, selección por CV, OOF para la matriz de confusión,
  versiones fijadas, commit y hora de los artefactos, licencia, tests de
  contrato y protocolo de despliegue. Supera a la mayoría de demos públicos.
- **Le falta:** IC o varianza entre pliegues para MAE y PR-AUC; validación
  anidada (o al menos cuantificar el optimismo); rejillas del clasificador
  auditadas; calibración con número (ECE); el rótulo del commit; limpiar el
  artefacto huérfano.
- **Ética de la focalización:** la ficha dice «señala configuraciones de
  empleo, no personas», pero **sexo y dominio geográfico son features del
  clasificador**. Falta una ablación sin sexo (¿cuánto PR-AUC se pierde?) y
  una sección de límites de la focalización algorítmica.

---

## 3. Viabilidad de la Fase 3 (comprobada con conteos, no solo con columnas)

Población: 47.899 ocupados con ingreso > 0. El cruce con los módulos 300 y
500 empata al 100 %.

| Análisis | Dato | n por celda | Veredicto |
|---|---|---|---|
| Mapa por departamento | `UBIGEO` en todos los módulos (hoy se descarta tras la ingesta) | 25 departamentos (24 + Callao); mínimo 884 (Madre de Dios), máximo 6.892 | Viable para informalidad e ingreso mediano. Cruzado por sexo, las celdas bajan a ~400: mostrar solo el agregado. **Falta confirmar** en la ficha técnica ENAHO 2025 que la inferencia anual es departamental, y verificar la licencia del GeoJSON. |
| Lengua materna | `P300A`, módulo 300: «¿Cuál es el idioma o lengua materna que aprendió en su niñez?» | Castellano 37.996 · Quechua 8.044 · Aimara 1.054 · lenguas amazónicas por separado entre 17 y 195 (todas < 200) | Viable solo **agregado en cuatro grupos**: castellano / quechua / aimara / amazónicas (≈ 667 sumadas). Ninguna lengua amazónica se muestra sola. Revisión contigo antes de publicar. |
| Autoidentificación étnica | `P558C`, módulo 500 | Mestizo 25.761 · Quechua 10.891 · Afroperuano 3.144 · Blanco 2.061 · Aimara 1.440 · Amazonía 883 · otro pueblo 40 | Viable agregado. Tema más sensible que la lengua: propuesta, no compromiso. |
| Brecha de género (Oaxaca-Blinder / Ñopo) | `sexo`, en el modelo | 27.274 hombres / 20.625 mujeres | Viable. **Riesgo:** la selección al empleo sesga la descomposición (solo se ve a quien trabaja y gana). Hay que decirlo y, si se puede, acotarlo con Heckman. |
| Penalidad de la informalidad | `informal` + `ingreso_mes` | Amplio | Viable, con advertencia de selección y sin lenguaje causal. |
| Retornos por segmento | `anios_educ` × `categoria` × `informal` | Amplio | Viable. Contraste directo con Yamada (2007) y con Psacharopoulos y Patrinos (2018). |
| Ablación sin sexo | Reentrenar el clasificador sin `sexo` | — | Barata y con alto valor ético. La propongo como candidata nueva. |

**Riesgos de método para todos:** errores estándar con diseño complejo
(`ESTRATO`, `CONGLOME` y FAC500A), no solo ponderación. La celda con n < 100
se oculta o se agrega, como pide el encargo.

---

## 4. Mapa de oportunidades (impacto × esfuerzo)

Esfuerzo: S (< medio día) · M (1–2 días) · L (> 2 días). **Riesgo de
despliegue:** «contrato» = toca `graficos.py` y su contrato (protocolo de dos
commits); «microdatos» = necesita `data/`; «artefacto» = va a un JSON hermano
(`ui_artifacts.json` no puede crecer).

| # | Propuesta | Personas | Esf. | Riesgo | Prioridad |
|---|---|---|---|---|---|
| 1 | Portada «Empieza aquí»: el Perú en 60 s, qué es la informalidad, por qué importa y recorrido guiado | Afuera ●●● · Econ ● | M | contrato | **Alta** |
| 2 | Glosario bilingüe al pasar el cursor (RUC, ENAHO, INEI, PR-AUC, dependencia parcial…), un solo módulo | Afuera ●●● · ML ● | S | bajo | **Alta** |
| 3 | Marco teórico: cuatro escuelas como tarjetas, cada una con «qué dicen nuestros datos» | Econ ●●● · Afuera ● | L (Fase 2) + M (app) | bajo | **Alta** |
| 4 | Retornos a la educación por segmento (asalariado / independiente × formal / informal) | Econ ●●● | M | microdatos, artefacto | **Alta** |
| 5 | Brecha de género Oaxaca-Blinder (+ Ñopo si da), con advertencia de selección | Econ ●●● · Afuera ● | M–L | microdatos, artefacto | **Alta** |
| 6 | Mapa por departamento (informalidad e ingreso mediano) | Afuera ●●● · Econ ●● | M | microdatos, artefacto, licencia | **Alta** |
| 7 | Penalidad o prima de la informalidad a igual perfil | Econ ●● | M | microdatos, artefacto | Media |
| 8 | Ablación sin sexo más sección de ética de la focalización | ML ●● · Econ ●● | S–M | microdatos | Media-alta |
| 9 | Brechas por lengua materna, agregadas en 4 grupos | Econ ●● | M | microdatos, sensible | Media (con tu revisión) |
| 10 | Cuantificar la incertidumbre: varianza entre pliegues o bootstrap para MAE y PR-AUC; ECE | ML ●●● | S–M | microdatos, artefacto | Media |
| 11 | Actualizar `INFORME_AUDITORIA.md` con el estado de cada hallazgo (AC-5 y AC-6 resueltos) | Econ ● · ML ●● | S | bajo | Media (barato) |
| 12 | Fuente citable para los benchmarks del INEI (NV-7) | Econ ●● | S (Fase 2) | bajo | Media (barato) |
| 13 | Rótulo del commit en la ficha («commit de los artefactos») y retirar el `.joblib` huérfano | ML ● | S | bajo | Baja |
| 14 | Arreglo de la caché de `cargar_schema()` | ML ● | S | bajo | Baja |
| 15 | Auditar las rejillas del clasificador (AC-1) y validación anidada (AC-3) | ML ●● | L (horas de CPU) | microdatos; **no** cambia el modelo desplegado salvo decisión tuya | Baja para v2 |
| 16 | Hilo narrativo: cada resultado enlaza su cruce con la literatura | Econ ●● · Afuera ● | M | bajo | Alta (después de la Fase 2) |
| 17 | Portada estática del portafolio `/predictor-ingresos/` (anti arranque en frío) | Afuera ●●● | M | fuera de este repo | Alta, pero del portafolio |

Orden sugerido: Fase 2 (3, 12) → Fase 3 (4, 5, 6, 8, 10; 7 y 9 si tú lo
apruebas) → Fase 4 (1, 2, 16 y la pestaña de investigación) → limpieza
(11, 13, 14) en commits chicos. El 15 queda fuera de v2 salvo que lo pidas.

---

## 5. Riesgos

1. **Conflicto entre el encargo y la auditoría sobre `n_jobs`.** El prompt
   v2 dice «`n_jobs=20`, no `-1`». La máquina tiene **6 núcleos físicos / 6
   lógicos** (medido). AC-4 registra una corrida de 70 minutos que se cayó
   con 20 en estos 6 núcleos. Hoy `src/comun.py:36` dice `N_JOBS = 20`, pero
   `06`, `07`, `08` y `09` lo sobrescriben con 8. **Decisión tuya:** propongo
   `min(8, os.cpu_count())` para los scripts nuevos de la Fase 3, o mantener
   20 si hay una razón que no veo.
2. **Afirmaciones frágiles hoy:** los benchmarks del INEI sin fuente (NV-7)
   y las `nota` de las referencias sin re-verificar. Si la Fase 2 encuentra
   una mal atribuida, se corrige antes de sumar citas nuevas.
3. **Cifras a recalcular si cambia algo:** cualquier número nuevo sale del
   artefacto hermano (`ui_contexto.json`). El PPT congelado mide
   `ui_artifacts.json`, así que ese archivo no se toca.
4. **Temas sensibles:** sexo, lengua materna, etnicidad y región. Siempre
   agregados, con marco de brechas estructurales y sin lectura individual.
   Lengua y etnicidad se revisan contigo antes de publicar. Hay que
   decidir si el clasificador sigue usando `sexo` (ver la propuesta 8).
5. **Selección:** toda brecha de ingreso se mide entre quienes trabajan y
   ganan. Sin decirlo, la brecha de género se lee mal.
6. **Diseño muestral:** sin estratos ni conglomerados, los intervalos de la
   Fase 3 salen demasiado estrechos.
7. **Despliegue:** la Fase 4 toca `graficos.py` y `streamlit_app.py`:
   protocolo de dos commits más gate en la URL pública, sin excepción.
8. **Ideas del encargo que conviene matizar:**
   - «Todo en español e inglés» choca con los títulos de obras publicadas
     en español (*El otro sendero*, *Desborde popular*). Van en su idioma
     original, con traducción entre corchetes, como ya prevé el barrido de la
     Fase 5.
   - Los «personajes ficticios» del Perú en 60 segundos tienen que ser
     claramente ficticios **y** no caricaturas (vendedora, taxista,
     agricultor, trabajadora del hogar). Propongo que cada uno lleve una cifra
     agregada real de su segmento, no una historia inventada con números
     inventados.

---

## 6. Decisiones del autor (24/09/2026)

- `n_jobs`: `min(8, os.cpu_count())` en todo el pipeline, incluido
  `src/comun.py`. El 20 venía de otra máquina.
- Orden: el de la sección 4. Las rejillas del clasificador (AC-1) y la
  validación anidada (AC-3) quedan fuera de la v2.
- Lengua materna: entra, agregada en 4 grupos, con sección de ética.
- **Autoidentificación étnica (`P558C`): fuera de la v2.** Queda como trabajo
  futuro, con los conteos de la sección 3 como punto de partida. Antes de
  publicarla habría que tener el marco de brechas estructurales, revisión
  externa y una decisión explícita sobre las categorías con n < 100 («otro
  pueblo», 40).
- Sexo en el clasificador: primero la ablación; la decisión se toma con el
  resultado a la vista.
- AC-5 y AC-6 se marcan como resueltos en `INFORME_AUDITORIA.md`.
- Antes de la Fase 2 va una Fase 1.5 de rendimiento, layout «de un vistazo»
  e identidad visual.

---

## Anexo A. Afirmaciones de la primera pasada que no se sostuvieron

| Afirmación | Verificación |
|---|---|
| «El título del gráfico de dominio contradice la barra resaltada» | No es bug: el título nombra el rango (máx./mín.) y la barra resaltada es el valor del perfil. Diseño intencional. |
| «El rayos X no funciona en inglés» | Funciona: S/ 849 en EN, en local y en la nube (verificado con Playwright). Fue una carrera del script. |
| «`× 1.401` con formato español en EN» | Correcto: 1,401 en ES y 1.401 en EN. |
| «El `»` del sidebar tapa la franja de cifras en móvil» | El botón es fijo y se superpone al hacer scroll. Es comportamiento nativo de Streamlit, menor; se revisa en la QA de la Fase 5. |
| «AC-5 (88,6 %) sigue mal en el README» | Ya está corregido en README (ES y EN) y en la app. Lo desactualizado es `INFORME_AUDITORIA.md`. |
| «AC-6 pendiente en `streamlit_app.py:999`» | La v1.1 reescribió el archivo y la afirmación ya no está. La app narra el hallazgo como resuelto. |
