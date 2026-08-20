# graficos.py — gráficos SVG puros para la app
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
"""
FASE 3 — Gráficos SVG construidos en Python (adaptado del proyecto SIS).

Funciones puras: reciben datos y la paleta activa `T`, devuelven una cadena
SVG. Ninguna toca Streamlit ni estado global. Reciben los colores como
parámetro porque el contenido viaja a un iframe que no ve el CSS del padre:
es el único mecanismo que mantiene una sola fuente de verdad de color.

Semántica de este dominio: la clase accionable es informal=1; superar el
umbral SEÑALA el caso (ámbar, focalización), no lo condena. Verde = sin señal.
"""

from __future__ import annotations

import math
from html import escape


def envolver(svg: str, css_iframe: str) -> str:
    """Empaqueta un SVG como documento para `st.components.v1.html`."""
    return (f"<!doctype html><html><head><meta charset='utf-8'/>"
            f"<style>{css_iframe}</style></head><body>{svg}</body></html>")


def _n(x: float, dec: int = 2) -> str:
    """Formato español: punto para miles, coma para decimales."""
    s = f"{x:,.{dec}f}"
    return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def _pt(cx: float, cy: float, radio: float, frac: float) -> tuple[float, float]:
    ang = math.pi * (1 + frac)
    return cx + radio * math.cos(ang), cy + radio * math.sin(ang)


def _arco(cx, cy, radio, f0, f1) -> str:
    x0, y0 = _pt(cx, cy, radio, f0)
    x1, y1 = _pt(cx, cy, radio, f1)
    grande = 1 if (f1 - f0) > 0.5 else 0
    return f"M {x0:.2f} {y0:.2f} A {radio:.2f} {radio:.2f} 0 {grande} 1 {x1:.2f} {y1:.2f}"


def _ruta(puntos, x, y) -> str:
    if not puntos:
        return ""
    d = [f"M {x(puntos[0][0]):.2f} {y(puntos[0][1]):.2f}"]
    d += [f"L {x(px):.2f} {y(py):.2f}" for px, py in puntos[1:]]
    return " ".join(d)


# --------------------------------------------------------------------------
# 1. Medidor de probabilidad de informalidad
# --------------------------------------------------------------------------
def medidor(proba: float, umbral: float, hist: dict | None, T: dict,
            ancho: int = 520, alto: int = 300) -> str:
    """
    Arco semicircular con la probabilidad de empleo informal, la marca del
    umbral y la distribución de la cohorte de fondo. Por ENCIMA del umbral el
    caso queda señalado para focalización (ámbar); por debajo, sin señal.
    """
    cx, cy, radio = ancho / 2, alto - 64, 190
    grosor = 20
    senalado = proba >= umbral
    color = T["senal_media"] if senalado else T["senal_buena"]

    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='Probabilidad de empleo informal {proba:.1%}, "
              f"umbral {umbral:.3f}'>"]

    if hist and hist.get("bordes"):
        bordes = hist["bordes"]
        totales = [a + b for a, b in zip(hist["clase_0"], hist["clase_1"])]
        techo = max(totales) or 1
        for i, total in enumerate(totales):
            if total <= 0:
                continue
            f0, f1 = bordes[i], bordes[i + 1]
            h = 26 * (total / techo)
            r_int = radio + grosor / 2 + 4
            x0, y0 = _pt(cx, cy, r_int, f0)
            x1, y1 = _pt(cx, cy, r_int, f1)
            x2, y2 = _pt(cx, cy, r_int + h, f1)
            x3, y3 = _pt(cx, cy, r_int + h, f0)
            partes.append(
                f"<path d='M {x0:.1f} {y0:.1f} L {x1:.1f} {y1:.1f} "
                f"L {x2:.1f} {y2:.1f} L {x3:.1f} {y3:.1f} Z' "
                f"fill='{T['dato_tenue']}' opacity='0.55'/>")
        # Leyenda al pie, FUERA del anillo. Antes iba junto al arco y quedaba
        # dentro de la banda de las barras (radio 204-230 desde el centro), que
        # la tapaban: el texto se leia recortado.
        ly = alto - 6
        partes.append(f"<rect x='6' y='{ly - 8}' width='9' height='9' rx='2' "
                      f"fill='{T['dato_tenue']}' opacity='0.55'/>")
        partes.append(f"<text x='20' y='{ly}' class='et' text-anchor='start'>"
                      f"distribución de la cohorte</text>")

    partes.append(f"<path d='{_arco(cx, cy, radio, 0, 1)}' fill='none' "
                  f"stroke='{T['dato_tenue']}' stroke-width='{grosor}' "
                  f"stroke-linecap='round'/>")
    p = min(max(proba, 0.0), 1.0)
    if p > 0.002:
        partes.append(f"<path d='{_arco(cx, cy, radio, 0, p)}' fill='none' "
                      f"stroke='{color}' stroke-width='{grosor}' "
                      f"stroke-linecap='round'/>")

    ux0, uy0 = _pt(cx, cy, radio - grosor / 2 - 7, umbral)
    ux1, uy1 = _pt(cx, cy, radio + grosor / 2 + 7, umbral)
    partes.append(f"<line x1='{ux0:.1f}' y1='{uy0:.1f}' x2='{ux1:.1f}' y2='{uy1:.1f}' "
                  f"stroke='{T['texto']}' stroke-width='2.5' stroke-linecap='round'/>")
    tx, ty = _pt(cx, cy, radio + grosor / 2 + 22, umbral)
    partes.append(f"<text x='{tx:.1f}' y='{ty:.1f}' class='et' "
                  f"text-anchor='middle'>umbral {_n(umbral, 3)}</text>")

    partes.append(
        f"<text x='{cx}' y='{cy - 34}' text-anchor='middle' fill='{T['texto']}' "
        f"style='font-size:52px;font-weight:600;letter-spacing:-0.03em;"
        f"font-variant-numeric:tabular-nums'>{_n(proba * 100, 1)}<tspan "
        f"style='font-size:24px;fill:{T['texto_medio']}'>%</tspan></text>")
    partes.append(
        f"<text x='{cx}' y='{cy - 12}' text-anchor='middle' class='vs'>"
        f"probabilidad de empleo informal</text>")

    partes.append(f"<text x='{cx - radio:.0f}' y='{cy + 26:.0f}' class='et' "
                  f"text-anchor='middle'>0%</text>")
    partes.append(f"<text x='{cx + radio:.0f}' y='{cy + 26:.0f}' class='et' "
                  f"text-anchor='middle'>100%</text>")
    partes.append("</svg>")
    return "".join(partes)


# --------------------------------------------------------------------------
# 2. Matriz de confusión operativa
# --------------------------------------------------------------------------
def matriz_confusion(tp: int, fp: int, tn: int, fn: int, T: dict,
                     ancho: int = 520, alto: int = 286) -> str:
    """Cuadrícula 2x2 con etiquetas operativas del problema de focalización."""
    # Cada celda lleva el nombre llano Y el técnico: quien ya sabe qué es un
    # falso negativo lo encuentra, y quien no, aprende cuál es cuál.
    celdas = [
        (tp, "Informales señalados", "verdaderos positivos",
         "señalado y es informal", T["senal_buena"], 0, 0),
        (fp, "Señalados innecesarios", "falsos positivos (falsa alarma)",
         "señalado pero es formal", T["senal_media"], 1, 0),
        (fn, "Informales sin señalar", "falsos negativos (se escapan)",
         "no señalado y es informal", T["senal_mala"], 0, 1),
        (tn, "Formales sin señalar", "verdaderos negativos",
         "no señalado y es formal", T["dato"], 1, 1),
    ]
    total = max(tp + fp + tn + fn, 1)
    cw, ch, gap = 246, 116, 10
    x0, y0 = 6, 34

    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='Matriz de resultados operativos'>"]
    partes.append(f"<text x='{x0}' y='16' class='et'>por cada 1.000 evaluados</text>")

    for valor, titulo, tecnico, sub, color, col, fila in celdas:
        x = x0 + col * (cw + gap)
        y = y0 + fila * (ch + gap)
        intensidad = min(valor / total * 2.2, 0.3)
        partes.append(
            f"<rect x='{x}' y='{y}' width='{cw}' height='{ch}' rx='8' "
            f"fill='{color}' fill-opacity='{intensidad:.3f}' "
            f"stroke='{color}' stroke-opacity='0.35'/>")
        partes.append(
            f"<text x='{x + 16}' y='{y + 40}' fill='{T['texto']}' "
            f"style='font-size:28px;font-weight:600;letter-spacing:-0.02em;"
            f"font-variant-numeric:tabular-nums'>{_n(valor, 0)}</text>")
        partes.append(f"<text x='{x + 16}' y='{y + 60}' class='vl'>"
                      f"{escape(titulo)}</text>")
        partes.append(f"<text x='{x + 16}' y='{y + 78}' class='et' "
                      f"fill='{color}'>{escape(tecnico)}</text>")
        partes.append(f"<text x='{x + 16}' y='{y + 96}' class='vs'>"
                      f"{escape(sub)}</text>")
    partes.append("</svg>")
    return "".join(partes)


# --------------------------------------------------------------------------
# 3 y 4. Curvas ROC y PR
# --------------------------------------------------------------------------
def _marco(ancho, alto, m, T, etiqueta_x, etiqueta_y, partes):
    ix, iy = ancho - m["d"] - m["i"], alto - m["s"] - m["b"]
    partes.append(f"<rect x='{m['i']}' y='{m['s']}' width='{ix}' height='{iy}' "
                  f"fill='none' stroke='{T['borde_sutil']}'/>")
    for f in (0.25, 0.5, 0.75):
        partes.append(f"<line x1='{m['i']}' y1='{m['s'] + iy * f:.1f}' "
                      f"x2='{m['i'] + ix}' y2='{m['s'] + iy * f:.1f}' "
                      f"stroke='{T['rejilla']}' stroke-dasharray='2 4'/>")
    partes.append(f"<text x='{m['i'] + ix / 2:.0f}' y='{alto - 6}' class='et' "
                  f"text-anchor='middle'>{escape(etiqueta_x)}</text>")
    partes.append(f"<text x='12' y='{m['s'] + iy / 2:.0f}' class='et' "
                  f"text-anchor='middle' transform='rotate(-90 12 "
                  f"{m['s'] + iy / 2:.0f})'>{escape(etiqueta_y)}</text>")
    return ix, iy


def curva_roc(fpr, tpr, auc: float, punto: tuple | None, T: dict,
              ancho: int = 380, alto: int = 320) -> str:
    m = {"i": 44, "d": 14, "s": 28, "b": 34}
    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='Curva ROC, AUC {auc}'>"]
    ix, iy = _marco(ancho, alto, m, T, "tasa de falsos positivos",
                    "tasa de verdaderos positivos", partes)
    x = lambda v: m["i"] + v * ix
    y = lambda v: m["s"] + (1 - v) * iy

    partes.append(f"<line x1='{x(0)}' y1='{y(0)}' x2='{x(1)}' y2='{y(1)}' "
                  f"stroke='{T['dato_tenue']}' stroke-dasharray='4 4'/>")
    partes.append(f"<path d='{_ruta(list(zip(fpr, tpr)), x, y)}' fill='none' "
                  f"stroke='{T['acento']}' stroke-width='2'/>")
    if punto:
        partes.append(f"<circle cx='{x(punto[0]):.1f}' cy='{y(punto[1]):.1f}' r='5' "
                      f"fill='{T['fondo']}' stroke='{T['texto']}' stroke-width='2'/>")
    partes.append(f"<text x='{m['i'] + 8}' y='{m['s'] + 18}' class='vl'>"
                  f"AUC {_n(auc, 4)}</text>")
    partes.append(f"<text x='{ancho - m['d']}' y='16' class='et' text-anchor='end'>"
                  f"azar = diagonal</text>")
    partes.append("</svg>")
    return "".join(partes)


def curva_pr(recall, precision, auc: float, base: float, punto: tuple | None,
             T: dict, ancho: int = 380, alto: int = 320) -> str:
    m = {"i": 44, "d": 14, "s": 28, "b": 34}
    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='Curva precisión-recall, AUC {auc}'>"]
    ix, iy = _marco(ancho, alto, m, T, "recall (clase informal)", "precisión", partes)
    x = lambda v: m["i"] + v * ix
    y = lambda v: m["s"] + (1 - v) * iy

    partes.append(f"<line x1='{x(0)}' y1='{y(base)}' x2='{x(1)}' y2='{y(base)}' "
                  f"stroke='{T['dato_tenue']}' stroke-dasharray='4 4'/>")
    partes.append(f"<text x='{x(1) - 4:.0f}' y='{y(base) - 6:.0f}' class='et' "
                  f"text-anchor='end'>base {_n(base, 4)}</text>")
    partes.append(f"<path d='{_ruta(list(zip(recall, precision)), x, y)}' fill='none' "
                  f"stroke='{T['acento']}' stroke-width='2'/>")
    if punto:
        partes.append(f"<circle cx='{x(punto[0]):.1f}' cy='{y(punto[1]):.1f}' r='5' "
                      f"fill='{T['fondo']}' stroke='{T['texto']}' stroke-width='2'/>")
    partes.append(f"<text x='{m['i'] + 8}' y='{m['s'] + 18}' class='vl'>"
                  f"AUC {_n(auc, 4)}</text>")
    partes.append("</svg>")
    return "".join(partes)


# --------------------------------------------------------------------------
# 4b. Curva precisión–cobertura con el umbral activo marcado
# --------------------------------------------------------------------------
def curva_precision_cobertura(recall, precision, punto, presets, curva, T: dict,
                              ancho: int = 520, alto: int = 320) -> str:
    """
    El trade-off del umbral, VISTO. `punto` es (recall, precisión) del umbral
    activo; `presets` es [(nombre, índice en la curva)] para marcar los cortes
    ya elegidos. Se dibuja aquí y no se reusa `curva_pr` porque esta curva sale
    de las probabilidades out-of-fold del umbral, no del conjunto de prueba.
    """
    m = {"i": 52, "d": 96, "s": 30, "b": 38}
    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='Curva precisión contra cobertura; el umbral activo "
              f"señala una precisión de {punto[1]:.2f} y una cobertura de "
              f"{punto[0]:.2f}'>"]
    ix, iy = _marco(ancho, alto, m, T, "cobertura: informales que sí se señalan",
                    "acierto de lo señalado", partes)
    x = lambda v: m["i"] + v * ix
    y = lambda v: m["s"] + (1 - v) * iy

    partes.append(f"<path d='{_ruta(list(zip(recall, precision)), x, y)}' "
                  f"fill='none' stroke='{T['acento']}' stroke-width='2'/>")

    # Los preajustes caen cerca unos de otros y sus etiquetas se pisaban
    # («PUNTO OPERATIVO» sobre «MÁX. F1», ilegibles). Se agrupan los que estén
    # a menos de 14 px en vertical y se dibuja UNA etiqueta con ambos nombres;
    # los que quedan sueltos se separan alternando arriba/abajo.
    marcas = [(nombre, x(recall[i]), y(precision[i]))
              for nombre, i in presets if 0 <= i < len(recall)]
    marcas.sort(key=lambda m: m[2])
    grupos: list[list] = []
    for marca in marcas:
        if grupos and abs(marca[2] - grupos[-1][-1][2]) < 14:
            grupos[-1].append(marca)
        else:
            grupos.append([marca])

    for k, grupo in enumerate(grupos):
        for _, px, py in grupo:
            partes.append(f"<circle cx='{px:.1f}' cy='{py:.1f}' r='3.5' "
                          f"fill='{T['dato']}' opacity='0.85'/>")
        nombre = " · ".join(g[0] for g in grupo)
        px, py = grupo[0][1], sum(g[2] for g in grupo) / len(grupo)
        dy = -8 if k % 2 == 0 else 14           # alterna para no encadenar choques
        # si la etiqueta no cabe a la derecha, se ancla a la izquierda del punto
        cabe = px + 10 + _ancho_texto(nombre, 10) < ancho - m["d"]
        partes.append(
            f"<text x='{px + (10 if cabe else -10):.1f}' y='{py + dy:.1f}' "
            f"class='et' text-anchor='{'start' if cabe else 'end'}'>"
            f"{escape(nombre)}</text>")

    px, py = x(punto[0]), y(punto[1])
    partes.append(f"<line x1='{px:.1f}' y1='{m['s']}' x2='{px:.1f}' "
                  f"y2='{m['s'] + iy}' stroke='{T['texto']}' stroke-width='1' "
                  f"stroke-dasharray='3 3' opacity='0.5'/>")
    partes.append(f"<circle cx='{px:.1f}' cy='{py:.1f}' r='7' "
                  f"fill='{T['fondo']}' stroke='{T['texto']}' stroke-width='2.5'/>")
    partes.append(f"<text x='{m['i'] + 8}' y='{m['s'] + 18}' class='vl'>"
                  f"acierto {_n(punto[1] * 100, 1)} % · cobertura {_n(punto[0] * 100, 1)} %</text>")
    partes.append("</svg>")
    return "".join(partes)


# --------------------------------------------------------------------------
# 5. Curva de calibración
# --------------------------------------------------------------------------
def curva_calibracion(bins: list[dict], T: dict,
                      ancho: int = 380, alto: int = 320) -> str:
    m = {"i": 44, "d": 14, "s": 28, "b": 34}
    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='Curva de calibración'>"]
    ix, iy = _marco(ancho, alto, m, T, "probabilidad predicha",
                    "frecuencia observada", partes)
    x = lambda v: m["i"] + v * ix
    y = lambda v: m["s"] + (1 - v) * iy

    partes.append(f"<line x1='{x(0)}' y1='{y(0)}' x2='{x(1)}' y2='{y(1)}' "
                  f"stroke='{T['dato_tenue']}' stroke-dasharray='4 4'/>")
    partes.append(f"<text x='{x(1) - 4:.0f}' y='{y(1) + 16:.0f}' class='et' "
                  f"text-anchor='end'>calibración perfecta</text>")
    pares = [(b["proba_media"], b["frecuencia_observada"]) for b in bins]
    partes.append(f"<path d='{_ruta(pares, x, y)}' fill='none' "
                  f"stroke='{T['acento']}' stroke-width='2'/>")
    for px, py in pares:
        partes.append(f"<circle cx='{x(px):.1f}' cy='{y(py):.1f}' r='3.5' "
                      f"fill='{T['acento']}'/>")
    partes.append("</svg>")
    return "".join(partes)


# --------------------------------------------------------------------------
# 6. Importancia por permutación
# --------------------------------------------------------------------------
def _ancho_texto(txt: str, px: float = 11.0) -> float:
    """
    Ancho aproximado de una cadena en px. Sin acceso al motor de fuentes, 0,56
    em por carácter es una sobreestimación segura para la sans de la app: vale
    para reservar margen y que nada quede cortado.
    """
    return len(str(txt)) * px * 0.56


def _truncar(txt: str, ancho_max: float, px: float = 11.0) -> str:
    """Recorta con elipsis para que quepa. El texto completo va en <title>."""
    if _ancho_texto(txt, px) <= ancho_max:
        return txt
    cabe = max(int(ancho_max / (px * 0.56)) - 1, 4)
    return txt[:cabe].rstrip() + "…"


def barras_importancia(variables, media, desviacion, T: dict, unidad: str = "",
                       ancho: int = 520, etiquetas: dict | None = None) -> str:
    etiquetas = etiquetas or {}
    n = len(variables)
    fila, arriba = 30, 30
    alto = arriba + n * fila + 18
    # Margenes CALCULADOS, no fijos: con 210 px a la izquierda etiquetas como
    # «Horas trabajadas por semana (todas las ocupaciones)» se cortaban, y con
    # 16 px a la derecha se cortaba el valor («13…» en vez de 131,2).
    tope_izq = ancho * 0.42          # más allá, la barra se queda sin sitio
    textos_izq = [_truncar(str(etiquetas.get(v, v)), tope_izq - 18)
                  for v in variables]
    izq = min(max([_ancho_texto(t) for t in textos_izq] + [90]) + 18, tope_izq)
    textos_der = [_n(m, 3) if abs(m) < 100 else _n(m, 1) for m in media]
    der = max([_ancho_texto(t, 11) for t in textos_der] + [40]) + 14
    ix = ancho - izq - der
    techo = max([m + d for m, d in zip(media, desviacion)] + [1e-9])
    piso = min(list(media) + [0.0])
    span = (techo - piso) or 1.0
    cero = izq + (0 - piso) / span * ix

    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='Importancia por permutación'>"]
    if unidad:
        partes.append(f"<text x='{ancho - der}' y='16' class='et' "
                      f"text-anchor='end'>{escape(unidad)}</text>")
    partes.append(f"<line x1='{cero:.1f}' y1='{arriba - 8}' x2='{cero:.1f}' "
                  f"y2='{alto - 18}' stroke='{T['borde']}'/>")

    for i, (v, mu, sd) in enumerate(zip(variables, media, desviacion)):
        y = arriba + i * fila
        largo = (mu - 0) / span * ix
        despreciable = abs(mu) <= sd
        color = T["dato_tenue"] if despreciable else T["acento"]
        x_ini = min(cero, cero + largo)
        partes.append(f"<rect x='{x_ini:.1f}' y='{y:.1f}' width='{abs(largo):.1f}' "
                      f"height='15' rx='2' fill='{color}'/>")
        e0 = cero + (mu - sd) / span * ix
        e1 = cero + (mu + sd) / span * ix
        partes.append(f"<line x1='{e0:.1f}' y1='{y + 7.5:.1f}' x2='{e1:.1f}' "
                      f"y2='{y + 7.5:.1f}' stroke='{T['texto_medio']}' stroke-width='1.5'/>")
        for ex in (e0, e1):
            partes.append(f"<line x1='{ex:.1f}' y1='{y + 3:.1f}' x2='{ex:.1f}' "
                          f"y2='{y + 12:.1f}' stroke='{T['texto_medio']}' stroke-width='1.5'/>")
        completa = str(etiquetas.get(v, v))
        partes.append(f"<text x='{izq - 12}' y='{y + 12:.1f}' class='vs' "
                      f"text-anchor='end'>{escape(textos_izq[i])}"
                      f"<title>{escape(completa)}</title></text>")
        txt = _n(mu, 3) if abs(mu) < 100 else _n(mu, 1)
        anclaje_x = max(e1, cero + abs(largo)) + 8
        partes.append(f"<text x='{anclaje_x:.1f}' y='{y + 12:.1f}' class='vs' "
                      f"fill='{T['texto_tenue'] if despreciable else T['texto']}'>"
                      f"{txt}</text>")
    # Al pie y pegado al borde izquierdo: con `izq` calculado puede ser ancho y
    # esta nota se saldria del lienzo.
    partes.append(f"<text x='4' y='{alto - 4}' class='et'>"
                  f"barra atenuada = indistinguible de cero (media dentro de "
                  f"±1 desviación)</text>")
    partes.append("</svg>")
    return "".join(partes)


# --------------------------------------------------------------------------
# 7. Situador de cohorte
# --------------------------------------------------------------------------
def situador(valor: float, percentiles: dict, etiqueta: str, T: dict,
             ancho: int = 520, alto: int = 62) -> str:
    p5, p25, p50, p75, p95 = (float(percentiles[k]) for k in ("5", "25", "50", "75", "95"))
    lo, hi = min(p5, valor), max(p95, valor)
    span = (hi - lo) or 1.0
    izq, der = 16, 16
    ix = ancho - izq - der
    x = lambda v: izq + (v - lo) / span * ix
    yb = 38

    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='{escape(etiqueta)}: {valor} frente a la cohorte'>"]
    partes.append(f"<text x='{izq}' y='14' class='et'>{escape(etiqueta)}</text>")
    partes.append(f"<line x1='{x(p5):.1f}' y1='{yb}' x2='{x(p95):.1f}' y2='{yb}' "
                  f"stroke='{T['dato_tenue']}' stroke-width='3' stroke-linecap='round'/>")
    partes.append(f"<rect x='{x(p25):.1f}' y='{yb - 5}' width='{x(p75) - x(p25):.1f}' "
                  f"height='10' rx='3' fill='{T['dato_tenue']}' opacity='0.9'/>")
    partes.append(f"<line x1='{x(p50):.1f}' y1='{yb - 8}' x2='{x(p50):.1f}' "
                  f"y2='{yb + 8}' stroke='{T['dato']}' stroke-width='2'/>")
    partes.append(f"<circle cx='{x(valor):.1f}' cy='{yb}' r='6' fill='{T['acento']}' "
                  f"stroke='{T['fondo']}' stroke-width='2'/>")
    partes.append(f"<text x='{x(valor):.1f}' y='{yb - 14}' class='vs' "
                  f"text-anchor='middle' fill='{T['acento_alto']}'>{_n(valor, 1)}</text>")
    partes.append(f"<text x='{x(p50):.1f}' y='{alto - 2}' class='et' "
                  f"text-anchor='middle'>mediana {_n(p50, 1)}</text>")
    partes.append("</svg>")
    return "".join(partes)


# --------------------------------------------------------------------------
# 8. Perfil de dependencia parcial
# --------------------------------------------------------------------------
def dependencia_parcial(valores, efecto, tipo: str, etiqueta: str, T: dict,
                        marca=None, ancho: int = 520, alto: int = 200,
                        formato_y: str = "prob",
                        mostrar_etiqueta: bool = True) -> str:
    m = {"i": 52, "d": 16, "s": 26, "b": 44}
    ix, iy = ancho - m["i"] - m["d"], alto - m["s"] - m["b"]
    lo, hi = min(efecto), max(efecto)
    if hi - lo < 1e-9:
        lo, hi = lo - 0.01, hi + 0.01
    pad = (hi - lo) * 0.12
    lo, hi = lo - pad, hi + pad
    y = lambda v: m["s"] + (1 - (v - lo) / (hi - lo)) * iy

    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='Dependencia parcial de {escape(etiqueta)}'>"]
    # Cuando la app ya puso un título-oración encima, repetir aquí la etiqueta
    # de la variable es ruido: dos títulos para un solo gráfico.
    if mostrar_etiqueta:
        partes.append(f"<text x='{m['i']}' y='14' class='et'>"
                      f"{escape(etiqueta)}</text>")
    for f in (0, 0.5, 1.0):
        vy = m["s"] + f * iy
        partes.append(f"<line x1='{m['i']}' y1='{vy:.1f}' x2='{m['i'] + ix}' "
                      f"y2='{vy:.1f}' stroke='{T['rejilla']}' stroke-dasharray='2 4'/>")
        val = hi - f * (hi - lo)
        txt = f"{_n(val * 100, 1)} %" if formato_y == "prob" else _n(val, 0)
        partes.append(f"<text x='{m['i'] - 8}' y='{vy + 4:.1f}' class='vs' "
                      f"text-anchor='end'>{txt}</text>")

    if tipo == "numerico":
        vlo, vhi = float(min(valores)), float(max(valores))
        span = (vhi - vlo) or 1.0
        x = lambda v: m["i"] + (float(v) - vlo) / span * ix
        partes.append(f"<path d='{_ruta(list(zip(valores, efecto)), x, y)}' fill='none' "
                      f"stroke='{T['acento']}' stroke-width='2'/>")
        for v in (vlo, (vlo + vhi) / 2, vhi):
            partes.append(f"<text x='{x(v):.1f}' y='{alto - 22}' class='vs' "
                          f"text-anchor='middle'>{_n(v, 0)}</text>")
        if marca is not None:
            try:
                mx = x(float(marca))
                partes.append(f"<line x1='{mx:.1f}' y1='{m['s']}' x2='{mx:.1f}' "
                              f"y2='{m['s'] + iy}' stroke='{T['texto']}' "
                              f"stroke-width='1.5' stroke-dasharray='3 3'/>")
                partes.append(f"<text x='{mx:.1f}' y='{alto - 6}' class='et' "
                              f"text-anchor='middle'>este caso</text>")
            except (TypeError, ValueError):
                pass
    else:
        n = len(valores)
        bw = ix / max(n, 1)
        for i, (v, e) in enumerate(zip(valores, efecto)):
            bx = m["i"] + i * bw
            es_marca = marca is not None and str(v) == str(marca)
            color = T["acento"] if es_marca else T["dato_tenue"]
            # <title> = tooltip nativo del navegador, dos renglones: el dato
            # leido en palabras y que significa estar por encima o por debajo.
            pico = max(efecto)
            relacion = ("es el valor más alto del gráfico"
                        if e >= pico - 1e-9 else
                        f"queda {_n((pico - e) * 100, 0)} puntos por debajo del "
                        f"valor más alto")
            tip = (f"{escape(str(v))}: {_n(e * 100, 1)} % de probabilidad estimada\n"
                   f"{relacion}"
                   + (" · es el valor de tu perfil" if es_marca else ""))
            partes.append(f"<rect x='{bx + bw * 0.15:.1f}' y='{y(e):.1f}' "
                          f"width='{bw * 0.7:.1f}' height='{m['s'] + iy - y(e):.1f}' "
                          f"rx='2' fill='{color}'><title>{tip}</title></rect>")
            if n <= 12 or es_marca:
                corta = str(v)[:14]
                partes.append(f"<text x='{bx + bw / 2:.1f}' y='{alto - 24}' class='et' "
                              f"text-anchor='end' transform='rotate(-40 "
                              f"{bx + bw / 2:.1f} {alto - 24})'>{escape(corta)}</text>")
    partes.append("</svg>")
    return "".join(partes)


# --------------------------------------------------------------------------
# 9. Barras de MAE del torneo (nuevo en este proyecto)
# --------------------------------------------------------------------------
def barras_mae(ids: list[str], maes: list[float], destacado: str, T: dict,
               ancho: int = 640) -> str:
    """MAE_cv por especificación, la desplegada resaltada en acento."""
    n = len(ids)
    fila, arriba = 32, 28
    alto = arriba + n * fila + 26
    izq, der = 60, 70
    ix = ancho - izq - der
    techo = max(maes) * 1.02

    partes = [f"<svg viewBox='0 0 {ancho} {alto}' role='img' "
              f"aria-label='MAE por especificación del torneo'>"]
    partes.append(f"<text x='{ancho - der}' y='14' class='et' text-anchor='end'>"
                  f"MAE de validación cruzada (S/) — menor es mejor</text>")
    for i, (id_, mae) in enumerate(zip(ids, maes)):
        y = arriba + i * fila
        largo = mae / techo * ix
        es = id_ == destacado
        color = T["acento"] if es else T["dato_tenue"]
        partes.append(f"<text x='{izq - 10}' y='{y + 15}' class='vl' "
                      f"text-anchor='end' fill='{T['texto'] if es else T['texto_medio']}'"
                      f">{escape(id_)}</text>")
        partes.append(f"<rect x='{izq}' y='{y}' width='{largo:.1f}' height='18' "
                      f"rx='3' fill='{color}'/>")
        etiqueta = _n(mae, 0) + (" · desplegada" if es else "")
        partes.append(f"<text x='{izq + largo + 8:.1f}' y='{y + 14}' class='vs' "
                      f"fill='{T['acento_alto'] if es else T['texto_medio']}'>"
                      f"{etiqueta}</text>")
    partes.append("</svg>")
    return "".join(partes)
