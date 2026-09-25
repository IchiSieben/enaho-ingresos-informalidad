# Fase 1.5 — Informe de cierre (v1.2)

> Autoría: Yoichi Palacios Tanaka, con el grupo ENEI (Alan Nestor Cañazaca
> Mamani, Magdalena Quico de la Cruz, Edgar Delgado Ortega). Docente: Orlando
> Advíncula Zeballos.
>
> Toda cifra de este informe sale de un script de `docs/qa/` o de
> `tests/test_color.py`. Los JSON crudos están en `docs/qa/rendimiento/`.

## 1. Qué cambió

- **Sin sidebar.** Barra superior pegajosa con marca (tooltip con grupo y
  docente), sección, idioma y tema. La autoría completa va al pie de cada
  sección. La regla de firma quedó escrita en `AUTHORS.md`.
- **Enlaces profundos.** `?sec=`, `?lang=` y `?theme=` conviven sin pisarse,
  con guarda de re-clic (`required=True`). Se sincronizan a mano porque
  `bind="query-params"` escribe la etiqueta formateada (`?sec=Model+card`) y
  no el valor. Hay dos pruebas: `tests/test_enlaces.py` (AppTest) y
  `docs/qa/probar_enlaces.py` (Chromium, 10/10).
- **Cero iframes.** Los gráficos son SVG en línea vía `st.markdown`. El Sankey
  (plotly) pasa a ser un embudo SVG propio, con el porqué de cada recorte
  legible y el % sobre el total crudo. `plotly` sale de `requirements.txt`.
- **Teal como único acento de interacción** en claro y oscuro, en AA. «Bueno»
  deja de ser teal: pasa a violeta en claro y oscuro, y a verde en Terminal,
  cuyo acento es azul. Ver §4.
- **De un vistazo:**
  - Ingreso e Informalidad usan formulario compacto y fragmentos
    (`@st.fragment`).
  - Torneo, Ficha y Cómo se hizo muestran 1 visual + 3 cifras + 1 frase, con
    el detalle en `st.tabs`.
  - En la Ficha, el resumen responde «¿Es demasiado bueno el clasificador?»,
    que es el destino del botón «¿Por qué tan alto?».
- **Animaciones de entrada ≤ 250 ms**, solo al entrar a la sección. Un rerun
  de slider no las repite (`.quieto`). Se respeta `prefers-reduced-motion`.

## 2. Rendimiento antes / después

Local, Chromium headless, 1440×900 (`medir_rendimiento.py`, 5 rondas).

| Métrica | Antes (v1.1) | Después (v1.2) |
|---|---|---|
| iframes: ingreso / informalidad / torneo / ficha / máquinas | 4 / 12 / 2 / 3 / 11 | **0 / 0 / 0 / 0 / 0** |
| Requests al cargar | 162 | 152 |
| Requests por slider: ingreso / informalidad | 3 / 6 (todas a Google Fonts) | **0 / 0** |
| Requests al cambiar a informalidad / máquinas | 37 / 48 | 3 / 1 |
| Rerun por slider, mediana: ingreso | 0,819 s | 0,724 s |
| Rerun por slider, mediana: informalidad | 0,920 s | 0,866 s |
| Cambio de sección: ingreso / informalidad / torneo / ficha / máquinas | 1,05 / 1,33 / 1,38 / 1,15 / 1,44 s | 0,59 / 0,98 / 0,85 / 0,92 / 1,06 s |
| Carga inicial | 4,0 s | 5,5–8,4 s (ver nota) |

**Nota sobre los tiempos locales.** La medición de «después» se hizo con la
CPU al 97 %, ocupada por procesos ajenos a esta app: otros dos servidores
Streamlit y un scraper. El tiempo hasta que aparece la barra varió de 2,2 s a
8,6 s entre tres cargas idénticas. Por eso la carga inicial no es comparable y
no se reporta como regresión ni como mejora.

Sí son comparables, porque no dependen de la carga de la máquina:

- el número de iframes;
- el número de requests;
- las fuentes descargadas por slider.

**Nube.** La medición de «antes» está en `antes_nube.json`: carga de 18,4 s,
263 requests y rerun de slider de 1,1–1,2 s. La de «después» se repite al
desplegar la v1.2, porque requiere el push. Incluye la medición de «Cómo se
hizo» que pidió el autor.

**`st.cache_data` para los SVG: no se agregó.** Medido con cProfile sobre un
rerun con cachés calientes:

| Sección | Rerun | Generación de SVG |
|---|---|---|
| Informalidad | 176 ms | 13,6 ms (7,7 %) |
| Cómo se hizo | 201 ms | 9,7 ms (4,8 %) |
| Ficha | 53 ms | 1,3 ms (2,4 %) |

Cachear eso no mueve la aguja y agrega claves de caché que invalidar al
cambiar de tema o de idioma.

## 3. De un vistazo

Borde inferior (px) de cada elemento clave contra el alto del viewport
(`medir_vistazo.py`). Cabe si pregunta, controles, respuesta y gráfico clave
quedan por encima del pliegue.

| Sección | 1366×768 antes | 1366×768 después | 1440×900 antes | 1440×900 después |
|---|---|---|---|---|
| Ingreso | no (controles hasta 1601) | **sí** (máx. 685) | no (1583) | **sí** (685) |
| Informalidad | no (controles hasta 1438) | **sí** (755) | no (1438) | **sí** (759) |
| Torneo | no (sin resumen; gráfico en 2304) | **sí** (572) | no (2266) | **sí** (572) |
| Ficha | no (sin resumen; gráfico en 1417) | **sí** (607) | no (1417) | **sí** (607) |
| Cómo se hizo | no (sin resumen) | **sí** (506) | no (792) | **sí** (506) |

La tabla corresponde a ES, tema claro. En EN con Terminal (fuente mono, más
ancha) también caben las cinco secciones en los dos tamaños:

- Torneo: 598 px.
- Ficha: 677 px.
- Cómo se hizo: 533 px.

Informalidad es la más justa: 755 de 768 px.

Capturas: 5 secciones × ES/EN × claro/terminal × 2 tamaños = 40 PNG
(`docs/qa/capturar_secciones.py`).

**Móvil (390×844, claro ES).**

- Ninguna sección tiene scroll horizontal de página. Las pestañas y las tablas
  desbordan dentro de su propio contenedor con scroll.
- Las cifras del resumen se apilan bajo el gráfico.
- La barra queda en tres filas (marca e idioma, tema, secciones). Por eso en
  móvil deja de ser pegajosa.
- Limitación: el viaje del dato de «Cómo se hizo» escala a todo el ancho y
  sus rótulos quedan ilegibles a 390 px. Las cifras de debajo siguen leyéndose.
  Pendiente para la QA de la Fase 5.

## 4. Contraste y daltonismo

Contraste WCAG sobre la paleta activa. ΔE OKLab es la distancia mínima entre
los cuatro colores semánticos (acento, bueno, medio, malo), simulando cada
tipo de daltonismo. Umbral del test: 0,10 («distinto lado a lado»).

| Tema | acento / fondo | acento_alto / fondo | botón / acento | peor par de texto | ΔE mín. (normal · protanopia · deuteranopia · tritanopia) |
|---|---|---|---|---|---|
| claro | 4,92:1 | 6,85:1 | 5,47:1 | 4,68:1 (acento / superficie_alta) | 0,162 · 0,116 · 0,117 · 0,118 |
| oscuro | 10,35:1 | 13,02:1 | 9,09:1 | 4,82:1 (senal_mala / superficie_alta) | 0,200 · 0,163 · 0,128 · 0,140 |
| terminal | 7,69:1 | 13,73:1 | 7,69:1 | 5,04:1 (texto_tenue / superficie_alta) | 0,228 · 0,115 · 0,136 · 0,109 |

Todos los pares de tinta × fondo pasan AA (≥ 4,5:1). Terminal conserva su
identidad: acento azul, cifras en ámbar y fuente mono.

## 5. Arranque en frío

La cifra que importa es la de Streamlit Community Cloud. Antes: 18,4 s de
carga inicial, medida con `medir_rendimiento.py`. Después: se mide con
`docs/qa/medir_frio.py` después del despliegue. Separa servidor recién
levantado de navegador nuevo sobre servidor caliente.

Lo que la v1.2 quita del arranque:

- plotly, que ya no se importa ni se instala;
- los iframes, cada uno con su propio documento y su `@import` de Google
  Fonts.

## 6. Notas honestas

1. **`st.html` elimina el SVG entero en 1.61** (el div llega vacío).
   - Antes se afirmó que conservaba `<title>` y SMIL. **Esa afirmación era
     falsa.**
   - Los gráficos y el CSS van por `st.markdown(unsafe_allow_html=True)`.
     Verificado en Chromium: ese camino conserva `<title>`, `<animate>`,
     `<animateMotion>`, clases, `style` y `aria-label`.
2. **`bind="query-params"` serializa la etiqueta, no el valor.** Se reemplazó
   por sincronización manual (§1).
3. **Límites de AppTest.**
   - No reescribe la URL.
   - Llama a `format_func` fuera del contexto del script, así que en EN
     compara etiquetas en español.
   - Por eso los clics en EN se prueban en Chromium y no en pytest.
4. **Transiciones limitadas.** Cada rerun reemplaza el DOM del gráfico, así
   que no hay interpolación entre estados. La animación de entrada solo corre
   al cambiar de sección.
5. **Una regla vieja pisaba la barra.**
   - Antes se dijo que `stButtonGroup` no existía en 1.61. **Era falso.** La
     regla `section[data-testid="stMain"] [data-testid="stButtonGroup"]
     button` (padding de 18 px), escrita cuando el selector de tema vivía en
     el sidebar, se aplicaba a la barra superior.
   - Consecuencia: en Terminal EN la barra se partía en dos filas.
   - Arreglo: las reglas de la barra ganan por especificidad.
6. **Widgets nativos en los temas oscuros.**
   - Streamlit pinta slider, toggle y radio con el `primaryColor` del
     `config.toml`, que es el teal del tema claro.
   - En Oscuro y Terminal esos tres controles siguen en teal. Los iconos de
     ayuda y el subrayado de las pestañas ya siguen a la paleta.
   - Resolverlo del todo requiere un tema de Streamlit por tema de la app,
     que hoy no se puede cambiar en caliente.
7. **Cifras escritas a mano que quedan en el texto.** Rompen la regla «ningún
   número visible se escribe a mano» y se resuelven en la Fase 2/4
   (precomputarlas en `src/09`):
   - 24,6 % en especie (Torneo y Ficha);
   - 2,6 puntos del premio urbano;
   - 67,3 % de la tasa reconstruida;
   - 6.500 trabajadores familiares no remunerados;
   - 0,94 de la ablación, en la nota de la tabla;
   - 0,2 % de experiencia negativa.

   Las cifras del INEI (70,2 %, 88,6 %, 15,6 %) son citas externas con su
   referencia, no cálculos propios.
