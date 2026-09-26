# Autoría y créditos

## Autor del software (citable)

- **Yoichi Palacios Tanaka** (alias GitHub: [IchiSieben](https://github.com/IchiSieben)) —
  yoichi.palacios@gmail.com.
  Roles [CRediT](https://credit.niso.org/): conceptualización, metodología,
  software, validación, análisis formal, curación de datos, redacción,
  visualización y despliegue.

La cita formal del proyecto sale de [`CITATION.cff`](CITATION.cff). En
[`NOTICE`](NOTICE) figuran solo los autores citables del software.

## Grupo del curso (exposición y trabajo de curso)

Integrantes del grupo del curso de Machine Learning (ENEI — Escuela Nacional
de Estadística e Informática), en cuyo marco se elaboró y expuso este
proyecto:

- **Alan Nestor Cañazaca Mamani** — [github.com/alan1485](https://github.com/alan1485)
- **Magdalena Quico de la Cruz** — [github.com/mquicodelacruz-lang](https://github.com/mquicodelacruz-lang)
- **Yoichi Palacios Tanaka** — [github.com/IchiSieben](https://github.com/IchiSieben)
- **Edgar Delgado Ortega** — alias GitHub: Edo936

La regresión inicial del grupo sobre estos datos (la «autopsia» de la
sección 1 del README) fue el punto de partida del torneo: el error que
destapó estaba en los datos de origen (centinela 999999 del INEI leído como
ingreso), no en el trabajo de modelado de nadie.

## Docente

- **Orlando Advíncula Zeballos** — curso de Machine Learning, ENEI.

## Datos

Los microdatos de la ENAHO 2025 son del **INEI** (Perú) y no se
redistribuyen en este repositorio (ver [`NOTICE`](NOTICE)).

## Dónde aparece la firma

Desde la v1.2 la app no tiene barra lateral. Desde la 1.6 la autoría se
muestra así:

- **Barra superior**: solo la marca del portafolio, el monograma «iC7» de
  [ichisieben.dev](https://ichisieben.dev), con un enlace discreto
  «← ichisieben.dev» para volver. Sin créditos ni tooltip.
- **Pie de cada sección**: «Desarrollo: iC7 — Yoichi Palacios Tanaka» con
  los roles CRediT de arriba y, aparte, el grupo del curso de ML (ENEI)
  con sus nombres en el orden de este archivo y el docente al final. Los
  integrantes van sin rol porque este archivo no les asigna ninguno (lo
  verifica `tests/test_creditos.py`). También lleva el mapa de secciones,
  el límite de uso y el enlace al repositorio.
- **Cabecera de cada archivo de código**: sin cambios.
