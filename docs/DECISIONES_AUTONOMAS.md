# Decisiones autónomas (rama `v2-autonomo`)

Decisiones tomadas sin el autor presente, a partir del 26/09/2026. Cada una
dice qué se eligió, qué se descartó y cómo revertirla. Todo vive en la rama
`v2-autonomo`; `main` y la app pública no se tocaron.

## Fase 2 · hotfix de citas (commit `ce5ee21`)

**D-01 · Criterio del test de `ref()`.** Se añadió el campo `verificacion`
(`contenido` | `metadatos`) a cada referencia de `app/referencias.py`. El test
`tests/test_referencias_verificadas.py` acepta `metadatos` solo para los ids
de una lista blanca con justificación; hoy solo `duan1983` (la app le
atribuye únicamente el nombre del método, que es el título del artículo).
- Descartado: exigir `contenido` a todas (obligaría a quitar Duan, que es la
  cita correcta del método) y verificar por afirmación en vez de por
  referencia (la matriz ya lo hace a mano; el test cubre lo automatizable).
- Revertir: borrar el test y el campo (`git revert ce5ee21` deshace todo el
  hotfix; para solo el test, borrar `tests/test_referencias_verificadas.py`).

**D-02 · Alcance de `inei_informal`.** La frase «se validó contra la tasa
oficial» pasó a decir que es un contraste de referencia, no una validación:
la tasa oficial (70,2 %) sale de la EPEN y la nuestra de la ENAHO.
- Descartado: buscar una tasa oficial calculada sobre la ENAHO para comparar
  la misma encuesta. Queda como tarea abierta: no se sabe si el INEI la
  publica.
- Revertir: la frase está en dos sitios de `app/streamlit_app.py` (buscar
  «No es una validación contra la misma fuente»).

**Nota.** `docs/fase2/verificar_citas.py` informa 31 problemas en los
borradores de `docs/fase2/` (sin texto crudo o sin coincidencia). No se
corrigieron: son los borradores de la investigación, no los entregables.
`verificar_entregables.py` (la matriz y el marco) da 0 problemas.

## Fase 1.6 · A. Identidad y créditos

**D-03 · Dominio.** `ichi7.dev` no resuelve. El autor confirmó que su dominio
es `ichisieben.dev` y se usa en la barra, el pie, el README y AUTHORS.md
(CITATION.cff ya lo tenía).

**D-04 · Marca.** Solo el monograma (caja + «iC7» en JetBrains Mono, el mismo
dibujo de `Landing/src/components/Nav.astro`) y el enlace «← ichisieben.dev».
No lleva la palabra «IchiSieben» al lado, como sí la lleva el landing, para
no competir con las pestañas. La fuente se carga con `text=iC7`, solo 3 glifos.
- Revertir o ajustar: `marca_barra()` en `app/streamlit_app.py`.

**D-05 · Roles en el pie.** AUTHORS.md solo asigna roles (CRediT) al autor
del software. Esos roles van en la línea «Desarrollo». Los integrantes del
grupo van sin rol, en el orden de AUTHORS.md, y el docente al final. Lo
vigila `tests/test_creditos.py`.
- Descartado: atribuir la «regresión inicial» a alguien en particular.
  AUTHORS.md la atribuye al grupo.

**D-06 · Enlaces al portafolio con `target="_top"`.** En Community Cloud la
app corre dentro de un iframe. Un enlace normal abriría el portafolio dentro
de ese marco.
