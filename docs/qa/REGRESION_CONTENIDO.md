# Regresión de contenido — v1.1 vs HEAD (v1.2), harness endurecido

## Método

`docs/qa/regresion_contenido.py` (Playwright) extrae el texto visible de las 5
secciones de la app en ES/EN, para v1.1 (worktree en un puerto propio) y para
el HEAD actual (commit `8a279e2`), y compara por líneas normalizadas.

Endurecido en esta ronda respecto de la versión que produjo `triage.md`:

1. **Espera por estabilidad, no por tiempo fijo** (`esperar_texto_estable`):
   se relee texto principal + oculto hasta que dos lecturas consecutivas
   (~1 s de separación) coinciden, hasta 8 intentos. Ataca directamente el
   no-determinismo que `triage.md` había medido (mismo conteo de líneas
   variando 102→111→125 entre corridas idénticas).
2. **Toggles**: se abre `st.toggle` (`key="maq_motor"`, «Ver el motor» / "Open
   the engine") además de expanders y popovers, antes de leer el DOM.
3. **Contenido oculto con CSS leído por `textContent`** (`texto_oculto`):
   las seis estaciones del viaje del dato ya no usan un
   `st.segmented_control` — en HEAD viven las seis a la vez en el DOM como
   `.viaje-det-0`…`.viaje-det-5`, ocultas por CSS — y las etiquetas del
   embudo (`svg text`). `inner_text` no las ve; `textContent` sí.
4. **Doble extracción por sección + unión**: cada sección se visita dos veces
   (recargando la URL/reclicando el nav) y se toma la unión de líneas de
   ambas corridas, para no depender de que una sola pasada capture todo.
5. **Todas las tabs**, incluida Acto 2 del torneo y la cola de
   `seccion_auditoria` (ya cubierto por el barrido genérico de
   `button[role="tab"]`, ahora con la espera de estabilidad detrás).
6. **NBSP → espacio** antes de normalizar (ya estaba en el archivo).

## Resultado por idioma

Se sirvió v1.1 (worktree en `SP/v11`) en `:8611` y HEAD en `:8612`, ambos con
el Python de este repo (`.venv`), y se extrajo dos veces cada sección en cada
idioma (12 extracciones ES + 12 EN por versión). Servidores detenidos por PID
al terminar (24708 y 10380 en el momento del apagado; ninguno de los puertos
del usuario, 8502/8503, ni el 8599, fue tocado).

| Sección | ES (v1.1→actual) | EN (v1.1→actual) |
|---|---|---|
| ingreso | 106→137 líneas | 106→147 líneas |
| informalidad | 134→231 líneas | 134→231 líneas |
| torneo | 112→159 líneas | 112→159 líneas |
| ficha | 179→154 líneas | 179→154 líneas |
| maquinas | 173→135 líneas | 173→130 líneas |

El informe completo (cambios/falta/nuevo por sección e idioma) quedó en
`SP/regresion/informe_v2.md` (no versionado, es de trabajo).

## Clasificación de lo que aparece como "falta"

Se revisó cada bloque "Falta" de las 5 secciones × 2 idiomas contra
`git show HEAD:app/streamlit_app.py` y los artefactos en `reports/`/`models/`.
Conclusión: **no hay pérdida de contenido real (clase b) confirmada.** Todo lo
que aparece como "falta" cae en una de estas dos clases:

### (a) Intencional — reword/movido/eliminado a propósito
Ya documentado en `triage.md` y reconfirmado aquí: chrome de sidebar
(`AUTORÍA`/`AUTHORS`, `EN · English`→`EN`), iconos material que alternan según
estado abierto/cerrado, `Detalle técnico · <sección>` → `Detalle técnico`
genérico (decisión documentada en el propio docstring de `cabecera()`),
versión `v1.1`→`v1.2`, créditos `Hecho por ... ichi7.dev` →
`Desarrollo: iC7 ... ichisieben.dev` (mismo contenido, marca/dominio nuevos),
autoría del curso fragmentada en líneas + bloque "Roles (CRediT)", y los
títulos largos de nav reemplazados por keys cortas (el texto largo sigue en
el eyebrow/cabecera, visible en "Cambió").

### (c) Gap del extractor — el texto existe en el código actual, confirmado por grep
- **torneo**: las tres líneas de "Acto 2 · El diagnóstico" (`_acto_diagnostico`,
  líneas 1643-1677 de `app/streamlit_app.py`) — confirmado en el código
  (no es un iframe: `html()` es un wrapper local de `st.markdown`, no
  `st.components.v1.html`), pero el clic a esa tab específica no llega a
  re-renderizar dentro de la ventana de estabilidad en todas las corridas.
- **maquinas**: TODO el contenido de "falta" en esta sección reaparece,
  verbatim, en el bloque "Nuevo" de la misma corrida — solo que reagrupado en
  bloques largos sin salto de línea (p. ej. `1 · Microdatos INEI` +
  `Qué entra` + su párrafo aparecen concatenados como
  `"1Microdatos INEIQué entraTres archivos..."`). Es un efecto de leer
  `.viaje-det-i` con `textContent` (no inserta separadores entre bloques como
  sí hace `innerText`), no una pérdida: mismo contenido, distinta
  segmentación en líneas. Mismo patrón para las etiquetas del embudo
  (`svg text`): aparecen sí, pero como fragmentos.
- **ficha**: la cola de `seccion_auditoria()` (líneas ~2051+: "Antes de
  publicar...", "Qué encontró la auditoría...", enlace a
  `INFORME_AUDITORIA.md`) — confirmado presente en el código; sigue siendo
  contenido tardío dentro de la tab `t_lim`, dependiente de timing de
  re-render pese a la espera de estabilidad.
- **ingreso/informalidad/torneo**: el popover "Detalle técnico" con el texto
  largo de imputación/deflactación — confirmado idéntico byte a byte en el
  código; algunas corridas no llegan a abrirlo a tiempo.
- **toggle `maq_motor`**: se agregó el clic, pero el selector no coincidió de
  forma confiable con el DOM real de `st.toggle` en todas las corridas
  (verificado con una sonda aparte: el testid/rol exacto del toggle no
  siempre expone `aria-checked` de forma estable en el primer render). El
  contenido detrás del toggle (curvas de dependencia parcial, las tres citas
  Friedman/Hastie/Molnar) por eso sigue apareciendo como "falta" en algunas
  corridas — es contenido real y presente en el código
  (líneas 3228 en adelante), no una pérdida.

## Conclusión

Cero hallazgos de clase (b). El harness quedó más robusto (poll de
estabilidad, toggles, lectura de contenido oculto por CSS, doble corrida +
unión) pero **no llegó a determinismo total**: el "Acto 2" del torneo, la cola
de auditoría en Ficha y el popover "Detalle técnico" siguen dependiendo de que
el re-render de Streamlit termine dentro de la ventana de espera. Si se quiere
cerrar esto del todo, el siguiente paso sería reemplazar el polling de texto
estable por una espera activa del selector específico de cada bloque (p. ej.
`page.wait_for_selector('.viaje-det-0', state="attached")` antes de leer) en
vez de un timeout global por sección.
