# color.py — contraste WCAG y distinguibilidad bajo daltonismo
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Utilidades puras (sin Streamlit) para verificar la paleta: las usan los tests
y el reporte de color de la fase. Nada aquí se llama en caliente.

- Contraste: fórmula de luminancia relativa de WCAG 2.x.
- Daltonismo: matrices de Machado, Oliveira y Fernandes (2009) con severidad
  1,0, aplicadas en RGB lineal.
- Distancia: ΔE en OKLab (Ottosson, 2020), más uniforme que RGB para juzgar
  si dos colores se confunden.
"""

from __future__ import annotations

import math

# Machado et al. (2009), severidad 1,0.
CVD = {
    "protanopia": ((0.152286, 1.052583, -0.204868),
                   (0.114503, 0.786281, 0.099216),
                   (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968),
                     (0.280085, 0.672501, 0.047413),
                     (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779),
                   (-0.078411, 0.930809, 0.147602),
                   (0.004733, 0.691367, 0.303900)),
}


def _hex(c: str) -> tuple[float, float, float]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))


def _lin(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def luminancia(c: str) -> float:
    r, g, b = (_lin(v) for v in _hex(c))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: str, b: str) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _simular(c: str, tipo: str) -> tuple[float, float, float]:
    rgb = [_lin(v) for v in _hex(c)]
    m = CVD[tipo]
    return tuple(min(max(sum(m[i][j] * rgb[j] for j in range(3)), 0.0), 1.0)
                 for i in range(3))


def _oklab(rgb_lin: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = rgb_lin
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def delta_e(a: str, b: str, tipo: str | None = None) -> float:
    """ΔE OKLab entre dos colores, opcionalmente vistos con un tipo de CVD."""
    if tipo:
        pa, pb = _oklab(_simular(a, tipo)), _oklab(_simular(b, tipo))
    else:
        pa = _oklab(tuple(_lin(v) for v in _hex(a)))
        pb = _oklab(tuple(_lin(v) for v in _hex(b)))
    return math.dist(pa, pb)
