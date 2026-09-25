# Fase 2 — material de verificación

Lo que respalda `docs/MARCO_TEORICO.md`, `docs/MATRIZ_AFIRMACIONES.md` y
`docs/PROPUESTA_REFERENCIAS.md`.

- `BRIEF_SUBAGENTES.md`: las reglas que siguió cada uno de los siete ejes.
- `eje_1.md` … `eje_7.md`: el informe de cada eje, con las citas textuales.
- `raw/` (**no se versiona**: son textos de terceros): el texto crudo de cada
  fuente, del que salen las citas. Solo existe en la máquina donde se hizo la
  revisión.
- `verificar_citas.py`: busca cada cita de los `eje_*.md` en `raw/`. Normaliza
  lo que deforma la extracción de PDF (espacios, guiones de corte, comillas);
  acepta una cita partida en hasta 3 tramos literales por notas al pie o por
  columnas (`OK_FRAG`), nunca una paráfrasis.
- `_verificacion.txt`: la salida del script, 2026-09-25.

## Cómo se adjudicaron los 31 casos no encontrados

El script extrae todo lo que va entre comillas después de «textual», así que
también atrapa prosa. Revisión manual, uno por uno:

- **Falsos positivos (no son citas):** paráfrasis en español, prosa del propio
  agente (bloque `oit_17ciet` del eje 1), texto de la app entre comillas,
  fragmentos de encabezado.
- **Genuinas con el texto deformado:** Mincer (1974), donde el OCR lee «In Y»
  por «ln Y»; el encabezado JSTOR de Breiman (2001), sacado del PDF;
  «redundant encodings» de Barocas, Hardt y Narayanan.
- **Una cita mal transcrita:** Blau y Kahn (2017). El eje 4 escribió
  «provide empirical evidence on the levels and trends…». El resumen dice
  «we provide new empirical evidence on the extent of and trends in the gender
  wage gap, which declined considerably over this period». Corregida en la
  matriz.
- **Duan (1983):** sin copia abierta ni resumen (Semantic Scholar, Unpaywall y
  Crossref). Solo se verificaron los metadatos; la app le atribuye únicamente el
  nombre del método, que es el título del artículo.
