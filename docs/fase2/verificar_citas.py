"""Busca cada «cita textual» de fase2/eje_*.md en el texto crudo de su fuente (raw/<id>*.txt).

Normaliza lo que la extracción de PDF deforma (espacios, guiones de corte de línea,
comillas tipográficas, ligaduras) pero no el contenido: una cita que no aparece
así en el texto crudo NO cuenta como verificada.
"""
import re
import sys
import unicodedata
from pathlib import Path

BASE = Path(__file__).parent
RAW = BASE / "raw"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("­", "")
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)          # guion de corte de línea
    s = re.sub(r"[“”„«»\"'‘’`´]", "", s)
    s = re.sub(r"[–—−]", "-", s)
    s = re.sub(r"(\w)-\s+(\w)", r"\1-\2", s)           # guion con espacio del PDF
    s = re.sub(r"\s+", " ", s).lower()
    return s.strip()


def compacto(s: str) -> str:
    return re.sub(r"[\s\-]", "", s)


def cobertura(cita: str, tc: str, n: int = 5) -> float:
    """Fracción de tramos de n palabras de la cita que aparecen en el texto compacto tc."""
    pal = cita.split()
    if len(pal) <= n:
        return 1.0 if compacto(cita) in tc else 0.0
    tramos = [compacto(" ".join(pal[i:i + n])) for i in range(len(pal) - n + 1)]
    return sum(t in tc for t in tramos) / len(tramos)


_CACHE: dict = {}


def textos_raw() -> dict:
    """Texto normalizado de cada archivo crudo, calculado una sola vez."""
    if not _CACHE:
        for q in sorted(RAW.glob("*")):
            if q.suffix.lower() in (".txt", ".html", ".md", ".json"):
                t = norm(q.read_text(encoding="utf-8", errors="ignore"))
                _CACHE[q.name] = (t, compacto(t))
    return _CACHE


def estado_de(tramos: list, texto: str, tc: str | None = None) -> str:
    if not texto:
        return ""
    tc = tc if tc is not None else compacto(texto)
    if all(compacto(t) in tc for t in tramos):
        return "OK"
    segs = [segmentos(t, tc) for t in tramos]
    if all(0 < k <= 3 for k in segs):
        return f"OK_FRAG({max(segs)}seg)"
    return ""


def segmentos(cita: str, tc: str, minimo: int = 3) -> int:
    """Cuántos tramos literales consecutivos (de >= minimo palabras) arman la cita; 0 si no se puede.
    Tolera un corte de maquetación (nota al pie, dos columnas) sin aceptar una frase inventada."""
    pal = cita.split()
    i, k = 0, 0
    while i < len(pal):
        j = i
        while j < len(pal) and compacto(" ".join(pal[i:j + 1])) in tc:
            j += 1
        if j - i < min(minimo, len(pal) - i):
            return 0
        k, i = k + 1, j
    return k


def fuentes(ident: str) -> str:
    textos = []
    for p in RAW.glob("*"):
        if p.suffix.lower() in (".txt", ".html", ".md", ".json") and p.stem.lower().startswith(ident.lower()):
            textos.append(p.read_text(encoding="utf-8", errors="ignore"))
    return norm("\n".join(textos))


def citas(md: str):
    """Por bloque ###: (id, archivos raw nombrados en el bloque, cita).
    Las citas son los tramos entre «» o "" que siguen a la palabra «textual»,
    aunque ocupen varias líneas."""
    for bloque in re.split(r"\n(?=#{2,4} )", md):
        cab = bloque.split("\n", 1)[0]
        m = re.search(r"`?([a-z][a-z0-9_]{3,})`?", cab)
        ident = m.group(1) if m else ""
        nombrados = set(re.findall(r"raw/([\w.\-]+?)\.(?:txt|html|md)", bloque))
        plano = re.sub(r"\s*\n\s*", " ", bloque)
        for parte in re.split(r"(?i)textual", plano)[1:]:
            # La cita va justo después: se mira solo el primer tramo.
            parte = parte.split(":", 1)[1] if ":" in parte[:200] else parte
            for mm in re.finditer(r"«([^»]{12,}?)»|[\"“]([^\"”]{12,}?)[\"”]", parte[:1200]):
                yield ident, nombrados, (mm.group(1) or mm.group(2))


def main():
    archivos = sorted(BASE.glob("eje_*.md")) if len(sys.argv) < 2 else [BASE / a for a in sys.argv[1:]]
    malas = 0
    for f in archivos:
        vistas = set()
        for ident, nombrados, cita in citas(f.read_text(encoding="utf-8")):
            if (ident, cita) in vistas:
                continue
            vistas.add((ident, cita))
            texto = " ".join([fuentes(ident) if ident else ""] + [fuentes(n) for n in nombrados])
            c = norm(cita)
            # Las elipsis marcan un corte: se exige cada tramo por separado.
            tramos = [t.strip(" .") for t in re.split(r"\.\.\.|…|\[\.\.\.\]", c) if len(t.strip(" .")) > 8]
            tramos = [t.strip(" .,;:") for t in tramos] or [c]
            estado = estado_de(tramos, texto)
            if not estado:
                for nombre, (t, tc) in textos_raw().items():
                    e = estado_de(tramos, t, tc)
                    if e:
                        estado = f"{e}_EN:{nombre}"
                        break
            if not estado:
                estado = "SIN_RAW" if not texto else "NO_ENCONTRADA"
            if not estado.startswith("OK"):
                malas += 1
            print(f"{estado:14} {f.stem} {ident}: {cita[:90]}")
    print("problemas:", malas)


if __name__ == "__main__":
    main()
