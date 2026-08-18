# 00_extraer_diccionario.py — extrae el diccionario ENAHO a texto consultable
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
# Extrae el texto del diccionario ENAHO 2025 a un .txt consultable con grep.
# El PDF es el mismo en todos los modulos; basta extraerlo una vez.
from pathlib import Path

from pypdf import PdfReader

RAIZ = Path(__file__).resolve().parents[1]
PDF = RAIZ / "data" / "raw" / "1031-Modulo05" / "1031-Modulo05" / "Diccionario_2025.pdf"
SALIDA = RAIZ / "data" / "interim" / "diccionario_2025.txt"

lector = PdfReader(PDF)
print(f"Paginas: {len(lector.pages)}")

lineas = []
for i, pagina in enumerate(lector.pages):
    lineas.append(f"\n===== PAGINA {i + 1} =====\n")
    lineas.append(pagina.extract_text() or "")

SALIDA.write_text("\n".join(lineas), encoding="utf-8")
print(f"Escrito: {SALIDA}")
