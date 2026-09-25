"""Segunda pasada: las citas de MATRIZ_AFIRMACIONES.md y las cifras de literatura de
MARCO_TEORICO.md contra el texto crudo de SU fuente (alias explícitos, sin buscar en
todos los archivos: esa búsqueda ya dio un falso positivo)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from verificar_citas import compacto, norm, segmentos, textos_raw  # noqa: E402

DOCS = Path(__file__).parents[1]

# id de la referencia -> prefijo del archivo crudo, cuando no coinciden.
ALIAS = {
    "inei_empleo_2025": ["inei_q4_2025", "inei_informe_empleo"],
    "oit2018_mujeres_hombres": ["ilo2018"], "oit2018": ["ilo2018"],
    "oit1972kenya": ["ilo1972kenya"], "oit_17ciet": ["icls21_2023", "oit17ciet"],
    "inei_informal": ["inei_csei_2022_2024"],
    "nopo_atal_winder2009": ["nopo_atal_winder"], "blaukahn2017": ["blaukahn2017"],
    "arpi2018": ["etnia_peru"], "barocas2023": ["barocas"],
    # Citas de segunda mano, declaradas así en la matriz: el crudo es el de quien cita.
    "lewis1954": ["laportashleifer2014"], "portescastellsbenton1989": ["chen2012"],
    "guntherlaunov2012": ["gl_iza"], "nopo_saavedra_torero2004": ["nopo_saavedra_torero"],
    "esparta_rivera2020": ["mtpe_brecha"], "iza3151_2007": ["iza_informal_penalty"],
}

# Adjudicadas a mano (motivo al lado). No se aceptan otras.
ADJUDICADAS = {
    "p(1) ln y=6.20+.107s+.081t-.0012t2 .285": "OCR de Mincer (1974): el crudo lee «In Y»",
    "p(3) ln y= f(d3) + .068t- .0009t2 + 1.207 ln w .525": "OCR de Mincer (1974): el crudo lee «In Y»",
    "discontinuous": "término de búsqueda sin resultado (fila 6), no una cita",
}


def texto_de(ids: list[str]) -> str:
    prefijos = [p for i in ids for p in ALIAS.get(i, [i])]
    return " ".join(t for nombre, (t, _) in textos_raw().items()
                    if any(nombre.lower().startswith(p.lower()) for p in prefijos))


def ids_en(celda: str) -> list[str]:
    return re.findall(r"[a-z][a-z0-9_]{3,}", celda.lower())


def citas_matriz():
    malas = 0
    for linea in (DOCS / "MATRIZ_AFIRMACIONES.md").read_text(encoding="utf-8").splitlines():
        if not re.match(r"\|\s*\d+\s*\|", linea):
            continue
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        num, fuente, cita = c[0], c[3], c[7]
        tramos = re.findall(r"«([^»]{12,}?)»|\"([^\"]{12,}?)\"", cita)
        for par in tramos:
            q = norm(par[0] or par[1])
            texto = texto_de(ids_en(fuente))
            partes = [t.strip(" .,;:") for t in re.split(r"\.\.\.|…", q) if len(t.strip(" .,;:")) > 8]
            if q in ADJUDICADAS:
                estado = "ADJUDICADA"
            elif not texto:
                estado = "SIN_RAW"
            elif all(compacto(p) in compacto(texto) for p in partes):
                estado = "OK"
            elif all(0 < segmentos(p, compacto(texto)) <= 3 for p in partes):
                estado = "OK_FRAG"
            else:
                estado = "NO_ENCONTRADA"
            if estado not in ("OK", "OK_FRAG", "ADJUDICADA"):
                malas += 1
            print(f"matriz #{num:>3} {estado:13} [{fuente[:28]}] {q[:80]}")
    return malas


def cifras_marco():
    """Cifras de la columna «Qué dice la literatura» de las tablas del marco."""
    malas = 0
    for linea in (DOCS / "MARCO_TEORICO.md").read_text(encoding="utf-8").splitlines():
        if not linea.startswith("|") or linea.startswith("|---"):
            continue
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        if len(c) < 5 or c[0].lower().startswith("hallazgo"):
            continue
        lit, refs = c[1], c[4]
        texto = texto_de(ids_en(refs))
        tc = compacto(texto)
        for cifra in re.findall(r"\d+(?:[.,]\d+)?", lit):
            if len(cifra.replace(",", "").replace(".", "")) < 2 or re.fullmatch(r"(19|20)\d\d", cifra):
                continue      # años y dígitos sueltos (numeración) no se verifican aquí
            variantes = {cifra, cifra.replace(",", "."), cifra.replace(".", ",")}
            if re.match(r"0[.,]", cifra):      # los papers en inglés escriben .285 por 0,285
                variantes |= {cifra[1:].replace(",", ".")}
            ok = texto and any(v in tc for v in variantes)
            if not ok:
                malas += 1
                print(f"marco  {'SIN_RAW' if not texto else 'CIFRA_NO_ESTA':13} {cifra:>6} [{refs[:40]}] {lit[:90]}")
    return malas


if __name__ == "__main__":
    a = citas_matriz()
    b = cifras_marco()
    print(f"citas de la matriz con problema: {a} · cifras del marco sin respaldo: {b}")
