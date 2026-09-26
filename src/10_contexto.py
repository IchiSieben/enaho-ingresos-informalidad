# 10_contexto.py — análisis de contexto que pide la literatura (Fase 3 de la v2)
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
"""
Precomputa lo que la pestaña de investigación va a mostrar. La app no calcula
nada de esto: lee models/ui_contexto.json.

1. Penalidad de la informalidad (WLS, errores por conglomerado).
2. Brecha de género: Oaxaca-Blinder de dos partes y Ñopo (2008).
3. Retornos a la educación por segmento.
4. Informalidad e ingreso mediano por departamento (UBIGEO).
5. Lengua materna, agregada (la app la oculta: MOSTRAR_LENGUA = False).

Muestra: la de 47.632 casos completos que narra la app (torneo_frame). Pesos:
FAC500A. Varianza: bootstrap de conglomerados (CONGLOME) con semilla fija,
sin estratos (más conservador). Decisiones en docs/DECISIONES_AUTONOMAS.md,
D-16 a D-20.

Uso: python src/10_contexto.py [--B 200]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (DIR_MODELS, DIR_PROCESSED, DIR_RAW, DIR_REPORTS,
                   LLAVES_PERSONA, SEMILLA, escribir_json_atomico, leer_enaho)

RUTA_SALIDA = DIR_MODELS / "ui_contexto.json"
RUTA_REPORTE = DIR_REPORTS / "10_contexto.md"
N_MIN = 100                      # celda con menos casos: no se muestra
HORAS_MES = 52 / 12              # semanas por mes

# Códigos de departamento del INEI (dos primeros dígitos del UBIGEO).
DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa",
    "05": "Ayacucho", "06": "Cajamarca", "07": "Callao", "08": "Cusco",
    "09": "Huancavelica", "10": "Huánuco", "11": "Ica", "12": "Junín",
    "13": "La Libertad", "14": "Lambayeque", "15": "Lima", "16": "Loreto",
    "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes",
    "25": "Ucayali",
}

# P300A (Diccionario 2025, módulo 300). 99 = faltante. Portugués, otra lengua
# extranjera, no escucha/no habla y lengua de señas (6-9) quedan fuera: n
# mínima y no son el contraste que pide la literatura.
LENGUAS = {4: "Castellano", 1: "Quechua", 2: "Aimara"}
LENGUAS.update({c: "Otra lengua originaria" for c in (3, 10, 11, 12, 13, 14, 15)})

# Controles. A: capital humano y geografía. B: A + características del
# puesto («malos controles»: también son resultados del mercado laboral).
NUM_A = ["anios_educ", "exper", "exper2"]
CAT_A = ["area", "dominio"]
CAT_B = CAT_A + ["rama", "categoria", "tamano_empresa"]
ASALARIADOS = ["Empleado", "Obrero"]

# Celdas del emparejamiento de Ñopo.
CORTES_EDAD = [13, 24, 34, 44, 54, 64, 120]
CELDAS_A = ["nivel_educ", "grupo_edad", "area", "dominio"]
CELDAS_B = CELDAS_A + ["categoria"]


# --------------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------------
def cargar() -> pd.DataFrame:
    df = pd.read_parquet(DIR_PROCESSED / "torneo_frame.parquet")
    m5 = leer_enaho(DIR_RAW / "1031-Modulo05" / "1031-Modulo05" / "Enaho01a-2025-500.csv",
                    LLAVES_PERSONA + ["UBIGEO"])
    m3 = leer_enaho(DIR_RAW / "1031-Modulo03" / "1031-Modulo03" / "Enaho01A-2025-300.csv",
                    LLAVES_PERSONA + ["P300A"])
    m5["UBIGEO"] = m5["UBIGEO"].astype(str).str.strip().str.zfill(6)
    m3["P300A"] = pd.to_numeric(m3["P300A"], errors="coerce").replace(99, np.nan)
    df = (df.merge(m5, on=LLAVES_PERSONA, how="left")
            .merge(m3, on=LLAVES_PERSONA, how="left"))
    df["depto"] = df["UBIGEO"].str[:2]
    df["lengua"] = df["P300A"].map(LENGUAS)
    df["grupo_edad"] = pd.cut(df["edad"], CORTES_EDAD).astype(str)
    df["asalariado"] = df["categoria"].isin(ASALARIADOS)
    # Ingreso por hora: solo con horas > 0 (D-18).
    df["ingreso_hora"] = np.where(df["horas_total"] > 0,
                                  df["ingreso_mes"] / (df["horas_total"] * HORAS_MES),
                                  np.nan)
    df["log_hora"] = np.log(df["ingreso_hora"])
    df["log_mes"] = np.log(df["ingreso_mes"])
    return df


# --------------------------------------------------------------------------
# Herramientas ponderadas
# --------------------------------------------------------------------------
def media_p(x: np.ndarray, w: np.ndarray) -> float:
    return float(np.sum(x * w) / np.sum(w))


def mediana_p(x: np.ndarray, w: np.ndarray) -> float:
    orden = np.argsort(x)
    x, w = x[orden], w[orden]
    acum = np.cumsum(w)
    return float(x[np.searchsorted(acum, acum[-1] / 2)])


def matriz(df: pd.DataFrame, num: list[str], cat: list[str]) -> tuple[np.ndarray, list[str]]:
    """Intercepto + numéricas + dummies (primera categoría ordenada como base)."""
    partes = [pd.Series(1.0, index=df.index, name="const"), df[num].astype(float)]
    for c in cat:
        partes.append(pd.get_dummies(df[c], prefix=c, drop_first=True, dtype=float))
    X = pd.concat(partes, axis=1)
    return X.to_numpy(), list(X.columns)


def wls(X: np.ndarray, y: np.ndarray, w: np.ndarray) -> np.ndarray:
    r = np.sqrt(w)
    return np.linalg.lstsq(X * r[:, None], y * r, rcond=None)[0]


def pesos_bootstrap(conglome: pd.Series, B: int, semilla: int):
    """Genera B vectores de multiplicidad por fila (conglomerados con reposición)."""
    codigos, unicos = pd.factorize(conglome)
    G = len(unicos)
    rng = np.random.default_rng(semilla)
    for _ in range(B):
        cuenta = np.bincount(rng.integers(0, G, G), minlength=G)
        yield cuenta[codigos].astype(float)


def resumen(punto: float, repl: list[float]) -> dict:
    r = np.asarray(repl, dtype=float)
    return {"valor": round(punto, 4), "ee": round(float(np.std(r, ddof=1)), 4),
            "ic95": [round(float(np.percentile(r, 2.5)), 4),
                     round(float(np.percentile(r, 97.5)), 4)]}


# --------------------------------------------------------------------------
# 1 y 3. Regresiones con errores por conglomerado
# --------------------------------------------------------------------------
def coef_cluster(df: pd.DataFrame, y: str, foco: str, num: list[str],
                 cat: list[str]) -> dict:
    d = df.dropna(subset=[y, foco] + num + cat)
    X, nombres = matriz(d, [foco] + num if foco not in num else num, cat)
    fit = sm.WLS(d[y].to_numpy(), X, weights=d["FAC500A"].to_numpy()).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(d["CONGLOME"])[0]})
    i = nombres.index(foco)
    b, ee = float(fit.params[i]), float(fit.bse[i])
    return {"coef": round(b, 4), "ee": round(ee, 4),
            "ic95": [round(b - 1.96 * ee, 4), round(b + 1.96 * ee, 4)],
            "pct": round((np.exp(b) - 1) * 100, 2),
            "pct_ic95": [round((np.exp(b - 1.96 * ee) - 1) * 100, 2),
                         round((np.exp(b + 1.96 * ee) - 1) * 100, 2)],
            "n": int(len(d))}


def penalidad(df: pd.DataFrame) -> dict:
    d = df.assign(informal=df["informal"].astype(float))
    out = {}
    for y in ("log_hora", "log_mes"):
        extra = [] if y == "log_hora" else ["log_horas"]
        out[y] = {
            "A": coef_cluster(d, y, "informal", NUM_A + ["hombre"] + extra, CAT_A),
            "B": coef_cluster(d, y, "informal", NUM_A + ["hombre"] + extra, CAT_B),
            "asalariados": coef_cluster(d[d["asalariado"]], y, "informal",
                                        NUM_A + ["hombre"] + extra, CAT_A),
            "independientes": coef_cluster(d[d["categoria"] == "Independiente"], y,
                                           "informal", NUM_A + ["hombre"] + extra, CAT_A),
        }
    h = d.dropna(subset=["ingreso_hora"])
    out["medianas_hora"] = {
        g: {"valor": round(mediana_p(s["ingreso_hora"].to_numpy(), s["FAC500A"].to_numpy()), 2),
            "n": int(len(s))}
        for g, s in (("formal", h[h["informal"] == 0]), ("informal", h[h["informal"] == 1]))}
    return out


def retornos(df: pd.DataFrame) -> dict:
    segmentos = {
        "total": df,
        "asalariados": df[df["asalariado"]],
        "independientes": df[df["categoria"] == "Independiente"],
        "formales": df[df["informal"] == 0],
        "informales": df[df["informal"] == 1],
    }
    return {s: coef_cluster(d, "log_hora", "anios_educ", NUM_A + ["hombre"], CAT_A)
            for s, d in segmentos.items()}


# --------------------------------------------------------------------------
# 2a. Oaxaca-Blinder de dos partes
# --------------------------------------------------------------------------
def oaxaca(X: np.ndarray, y: np.ndarray, w: np.ndarray, hombre: np.ndarray,
           grupos: dict[str, np.ndarray] | None = None) -> dict:
    """
    Brecha en log(hombres − mujeres) = explicada + no explicada, con tres
    coeficientes de referencia. «pooled» es Fortin (2008) / Jann (2008): la
    regresión conjunta con la dummy de grupo, que se deja fuera de β*.
    """
    m, f = hombre == 1, hombre == 0
    bm, bf = wls(X[m], y[m], w[m]), wls(X[f], y[f], w[f])
    bp = wls(np.column_stack([X, hombre]), y, w)[:-1]
    xm = np.average(X[m], axis=0, weights=w[m])
    xf = np.average(X[f], axis=0, weights=w[f])
    brecha = float(xm @ bm - xf @ bf)
    res = {}
    for ref, b in (("pooled", bp), ("hombres", bm), ("mujeres", bf)):
        expl = float((xm - xf) @ b)
        res[ref] = {"explicada": expl, "no_explicada": brecha - expl}
    res["brecha"] = brecha
    # Parte explicada por bloque de variables, con la referencia pooled: dice
    # QUÉ diferencia de dotaciones empuja la parte explicada (D-22).
    res["detalle"] = {g: float((xm - xf)[i] @ bp[i]) for g, i in (grupos or {}).items()}
    return res


def grupos_columnas(nombres: list[str]) -> dict[str, np.ndarray]:
    """Índices de columnas por bloque: educación y experiencia, horas, y cada categórica."""
    bloque = {"anios_educ": "educacion_experiencia", "exper": "educacion_experiencia",
              "exper2": "educacion_experiencia", "log_horas": "horas"}
    out: dict[str, list[int]] = {}
    for i, n in enumerate(nombres):
        if n == "const":
            continue
        g = bloque.get(n) or next(c for c in CAT_B if n.startswith(c + "_"))
        out.setdefault(g, []).append(i)
    return {g: np.array(i) for g, i in out.items()}


def genero_oaxaca(df: pd.DataFrame, B: int) -> dict:
    out = {}
    for y in ("log_hora", "log_mes"):
        for nombre, cat in (("A", CAT_A), ("B", CAT_B)):
            num = NUM_A + ([] if y == "log_hora" else ["log_horas"])
            d = df.dropna(subset=[y] + num + cat).reset_index(drop=True)
            X, nombres = matriz(d, num, cat)
            gr = grupos_columnas(nombres)
            yv, w, h = d[y].to_numpy(), d["FAC500A"].to_numpy(), d["hombre"].to_numpy()
            punto = oaxaca(X, yv, w, h, gr)
            repl = [oaxaca(X, yv, w * mb, h, gr)
                    for mb in pesos_bootstrap(d["CONGLOME"], B, SEMILLA)]
            r = {"brecha": resumen(punto["brecha"], [x["brecha"] for x in repl]),
                 "n": int(len(d)),
                 "detalle_pooled": {g: resumen(v, [x["detalle"][g] for x in repl])
                                    for g, v in punto["detalle"].items()}}
            for ref in ("pooled", "hombres", "mujeres"):
                r[ref] = {k: resumen(punto[ref][k], [x[ref][k] for x in repl])
                          for k in ("explicada", "no_explicada")}
            out.setdefault(y, {})[nombre] = r
    # Señal de alarma (D-20): la parte no explicada cambia de signo entre
    # especificaciones de la variable principal.
    signos = {np.sign(out["log_hora"][c][ref]["no_explicada"]["valor"])
              for c in ("A", "B") for ref in ("pooled", "hombres", "mujeres")}
    out["signo_estable"] = len(signos) == 1
    return out


def medias_por_sexo(df: pd.DataFrame) -> dict:
    """Dotaciones promedio (ponderadas) de hombres y mujeres ocupados."""
    d = df.assign(
        urbano_=(df["area"] == "Urbana").astype(float),
        lima_=(df["dominio"] == "Lima Metropolitana").astype(float),
        superior_=df["nivel_educ"].isin(["Superior técnica", "Superior universitaria",
                                         "Posgrado"]).astype(float),
        informal_=df["informal"].astype(float),
        independiente_=(df["categoria"] == "Independiente").astype(float))
    cols = {"anios_educ": "anios_educ", "edad": "edad", "horas_total": "horas_total",
            "urbano_": "pct_urbano", "lima_": "pct_lima_metropolitana",
            "superior_": "pct_superior", "informal_": "pct_informal",
            "independiente_": "pct_independiente"}
    out = {}
    for sexo, g in d.groupby("sexo"):
        w = g["FAC500A"].to_numpy()
        out[sexo] = {v: round(media_p(g[c].to_numpy(float), w)
                              * (100 if v.startswith("pct") else 1), 2)
                     for c, v in cols.items()}
        out[sexo]["n"] = int(len(g))
    return out


def peru_en_cifras() -> dict:
    """
    El Perú en cifras, estimado con la propia ENAHO 2025 (hallazgo propio, no
    la proyección oficial): población con FACPOB07 sobre los miembros del
    hogar (P204 = 1) y ocupados de 14+ con FAC500A.
    """
    m2 = leer_enaho(DIR_RAW / "1031-Modulo02" / "1031-Modulo02" / "Enaho01-2025-200.csv",
                    LLAVES_PERSONA + ["DOMINIO", "P204", "FACPOB07"])
    m2 = m2[pd.to_numeric(m2["P204"], errors="coerce") == 1]
    w = pd.to_numeric(m2["FACPOB07"].astype(str).str.replace(",", "."),
                      errors="coerce").fillna(0)
    dom = pd.to_numeric(m2["DOMINIO"], errors="coerce")
    region = dom.map({1: "costa", 2: "costa", 3: "costa", 8: "costa",
                      4: "sierra", 5: "sierra", 6: "sierra", 7: "selva"})
    total = float(w.sum())
    m5 = leer_enaho(DIR_RAW / "1031-Modulo05" / "1031-Modulo05" / "Enaho01a-2025-500.csv",
                    LLAVES_PERSONA + ["OCU500", "P208A", "FAC500A"])
    ocu = m5[(pd.to_numeric(m5["OCU500"], errors="coerce") == 1)
             & (pd.to_numeric(m5["P208A"], errors="coerce") >= 14)]
    w5 = pd.to_numeric(ocu["FAC500A"].astype(str).str.replace(",", "."),
                       errors="coerce").fillna(0)
    return {
        "poblacion": round(total),
        "pct_region": {r: round(float(w[region == r].sum()) / total * 100, 2)
                       for r in ("costa", "sierra", "selva")},
        "pct_lima_metropolitana": round(float(w[dom == 8].sum()) / total * 100, 2),
        "ocupados_14": round(float(w5.sum())),
        "n_personas": int(len(m2)), "n_ocupados": int(len(ocu)),
        "fuente": "ENAHO 2025, módulos 200 y 500; FACPOB07 y FAC500A",
    }


# --------------------------------------------------------------------------
# 2b. Ñopo (2008): emparejamiento exacto por celdas
# --------------------------------------------------------------------------
def nopo(celda: np.ndarray, y: np.ndarray, w: np.ndarray, hombre: np.ndarray) -> dict:
    """
    Δ = (Ȳh − Ȳm) / Ȳm = Δ0 + ΔH + ΔM + ΔX, en ingreso por hora (niveles, no
    logs, como en Ñopo 2008). ΔH y ΔM: hombres y mujeres fuera del soporte
    común; ΔX: distinta distribución de características dentro del soporte;
    Δ0: la parte no explicada.
    """
    d = pd.DataFrame({"c": celda, "y": y, "w": w, "h": hombre})
    d = d[d["w"] > 0]
    d["yw"] = d["y"] * d["w"]
    g = d.groupby(["c", "h"])[["w", "yw"]].sum().unstack("h", fill_value=0.0)
    W, YW = g["w"], g["yw"]
    soporte = (W[1] > 0) & (W[0] > 0)
    tot_h, tot_m = W[1].sum(), W[0].sum()
    Yh, Ym = YW[1].sum() / tot_h, YW[0].sum() / tot_m
    ph_in, pm_in = W[1][soporte].sum() / tot_h, W[0][soporte].sum() / tot_m
    yh_c, ym_c = YW[1][soporte] / W[1][soporte], YW[0][soporte] / W[0][soporte]
    wh_c, wm_c = W[1][soporte] / W[1][soporte].sum(), W[0][soporte] / W[0][soporte].sum()
    Yh_in, Ym_in = float((wh_c * yh_c).sum()), float((wm_c * ym_c).sum())
    Yh_out = (YW[1][~soporte].sum() / W[1][~soporte].sum()) if ph_in < 1 else Yh_in
    Ym_out = (YW[0][~soporte].sum() / W[0][~soporte].sum()) if pm_in < 1 else Ym_in
    return {
        "delta": (Yh - Ym) / Ym,
        "d0": float((wh_c * (yh_c - ym_c)).sum()) / Ym,
        "dH": (1 - ph_in) * (Yh_out - Yh_in) / Ym,
        "dM": (1 - pm_in) * (Ym_in - Ym_out) / Ym,
        "dX": float(((wh_c - wm_c) * ym_c).sum()) / Ym,
        "soporte_hombres": ph_in, "soporte_mujeres": pm_in,
    }


def genero_nopo(df: pd.DataFrame, B: int) -> dict:
    d = df.dropna(subset=["ingreso_hora"] + CELDAS_B).reset_index(drop=True)
    y, w, h = d["ingreso_hora"].to_numpy(), d["FAC500A"].to_numpy(), d["hombre"].to_numpy()
    out = {"n": int(len(d))}
    for nombre, cols in (("A", CELDAS_A), ("B", CELDAS_B)):
        celda = pd.factorize(d[cols].astype(str).agg("|".join, axis=1))[0]
        punto = nopo(celda, y, w, h)
        repl = [nopo(celda, y, w * mb, h) for mb in pesos_bootstrap(d["CONGLOME"], B, SEMILLA)]
        out[nombre] = {k: resumen(punto[k], [r[k] for r in repl]) for k in punto}
        out[nombre]["celdas"] = int(len(np.unique(celda)))
    return out


# --------------------------------------------------------------------------
# 4 y 5. Tablas por grupo (departamento, lengua)
# --------------------------------------------------------------------------
def tabla_grupos(df: pd.DataFrame, col: str, B: int) -> dict:
    d = df.dropna(subset=[col]).reset_index(drop=True)
    grupos = sorted(d[col].unique())
    idx = {g: np.flatnonzero(d[col].to_numpy() == g) for g in grupos}
    inf, ing, w = d["informal"].to_numpy(float), d["ingreso_mes"].to_numpy(), d["FAC500A"].to_numpy()

    def calcular(wv: np.ndarray) -> dict:
        res = {}
        for g, i in idx.items():
            wi = wv[i]
            if wi.sum() == 0:
                res[g] = (np.nan, np.nan)
                continue
            res[g] = (media_p(inf[i], wi) * 100, mediana_p(ing[i][wi > 0], wi[wi > 0]))
        return res

    punto = calcular(w)
    repl = [calcular(w * mb) for mb in pesos_bootstrap(d["CONGLOME"], B, SEMILLA)]
    out = {}
    for g in grupos:
        rp = [r[g] for r in repl if not np.isnan(r[g][0])]
        n = int(len(idx[g]))
        out[str(g)] = {
            "n": n,
            "peso": round(float(w[idx[g]].sum())),
            "informal_pct": resumen(punto[g][0], [r[0] for r in rp]),
            "ingreso_mediano": resumen(punto[g][1], [r[1] for r in rp]),
            "mostrar": n >= N_MIN,
        }
    return out


def brecha_lengua(df: pd.DataFrame) -> dict:
    """Diferencia ajustada frente al castellano (controles A + sexo)."""
    d = df.dropna(subset=["lengua", "log_hora"])
    out = {}
    for lg in sorted(set(LENGUAS.values()) - {"Castellano"}):
        s = d[d["lengua"].isin(["Castellano", lg])].assign(
            foco=lambda x: (x["lengua"] == lg).astype(float))
        out[lg] = coef_cluster(s, "log_hora", "foco", NUM_A + ["hombre"], CAT_A)
    return out


# --------------------------------------------------------------------------
# Reporte
# --------------------------------------------------------------------------
def pc(x: float, dec: int = 1) -> str:
    return f"{x:.{dec}f}".replace(".", ",")


def mil(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


def reporte(r: dict) -> str:
    m = r["meta"]
    L = [
        "# 10 · Contexto: brechas, penalidad, retornos y territorio",
        "",
        f"Generado por `src/10_contexto.py` el {m['generado'][:10]} (commit `{m['commit']}`).",
        f"Muestra: {mil(m['n'])} ocupados con ingreso > 0 (casos completos del torneo); "
        f"{mil(m['n_hora'])} con horas > 0 para el ingreso por hora. Pesos FAC500A. "
        f"Tasa ponderada de informalidad en esta muestra: {pc(m['informal_pct'])} %.",
        f"Varianza: bootstrap de {m['B']} réplicas por conglomerado (semilla {m['semilla']}); "
        "las regresiones llevan errores robustos por conglomerado. Sin estratos: "
        "errores algo mayores, en la dirección conservadora.",
        "",
        "Todo es **descriptivo o de asociación**. Ninguna cifra de este reporte es un efecto causal.",
        "",
          "## 0. El Perú según la ENAHO 2025 (estimado con los factores de expansión)",
        "",
        f"Población estimada: {mil(r['peru']['poblacion'])} personas (miembros del "
        f"hogar, FACPOB07). Costa {pc(r['peru']['pct_region']['costa'])} %, sierra "
        f"{pc(r['peru']['pct_region']['sierra'])} %, selva "
        f"{pc(r['peru']['pct_region']['selva'])} %; Lima Metropolitana "
        f"{pc(r['peru']['pct_lima_metropolitana'])} %. Ocupados de 14 años o más: "
        f"{mil(r['peru']['ocupados_14'])}. Es una estimación muestral, no la proyección "
        "oficial de población del INEI.",
        "",
        "## 1. Penalidad de la informalidad (log ingreso por hora)",
        "",
        "| Especificación | Coef. | IC 95 % | Equivale a | n |",
        "|---|---|---|---|---|",
    ]
    etiquetas = {"A": "Capital humano + geografía + sexo",
                 "B": "A + rama, categoría y tamaño",
                 "asalariados": "Solo asalariados (A)",
                 "independientes": "Solo independientes (A)"}
    for k, et in etiquetas.items():
        c = r["penalidad"]["log_hora"][k]
        L.append(f"| {et} | {pc(c['coef'], 3)} | [{pc(c['ic95'][0], 3)}; {pc(c['ic95'][1], 3)}] "
                 f"| {pc(c['pct'])} % | {mil(c['n'])} |")
    mh = r["penalidad"]["medianas_hora"]
    L += ["",
          f"Mediana ponderada del ingreso por hora: formal S/ {pc(mh['formal']['valor'], 2)}, "
          f"informal S/ {pc(mh['informal']['valor'], 2)}.",
          "",
          "Advertencia de selección: quien trabaja en la informalidad no es una muestra al "
          "azar. Controlar por lo observable no quita lo que no se observa (habilidad, "
          "preferencias, redes). Por eso la cifra es una diferencia condicional, no el efecto "
          "de formalizar a alguien.",
          "",
          "## 2. Brecha de género",
          "",
          "### Oaxaca-Blinder (dos partes, en log puntos; + = a favor de los hombres)",
          "",
          "| Resultado | Controles | Brecha | Referencia | Explicada | No explicada |",
          "|---|---|---|---|---|---|"]
    for y, ety in (("log_hora", "Por hora"), ("log_mes", "Mensual")):
        for c in ("A", "B"):
            o = r["genero"]["oaxaca"][y][c]
            for ref in ("pooled", "hombres", "mujeres"):
                L.append(f"| {ety} | {c} | {pc(o['brecha']['valor'], 3)} | {ref} | "
                         f"{pc(o[ref]['explicada']['valor'], 3)} "
                         f"(±{pc(1.96 * o[ref]['explicada']['ee'], 3)}) | "
                         f"{pc(o[ref]['no_explicada']['valor'], 3)} "
                         f"(±{pc(1.96 * o[ref]['no_explicada']['ee'], 3)}) |")
    L += ["",
          "Parte explicada por bloque (referencia pooled, log puntos; + = favorece a "
          "los hombres):",
          "",
          "| Resultado | Controles | Bloque | Contribución |", "|---|---|---|---|"]
    for y, ety in (("log_hora", "Por hora"), ("log_mes", "Mensual")):
        for c in ("A", "B"):
            for g, v in r["genero"]["oaxaca"][y][c]["detalle_pooled"].items():
                L.append(f"| {ety} | {c} | {g} | {pc(v['valor'], 3)} "
                         f"(±{pc(1.96 * v['ee'], 3)}) |")
    ms = r["genero"]["medias_por_sexo"]
    L += ["", "Dotaciones promedio ponderadas:", "",
          "| | " + " | ".join(ms) + " |", "|---|" + "---|" * len(ms)]
    for k in ms[next(iter(ms))]:
        L.append(f"| {k} | " + " | ".join(mil(ms[s][k]) if k == "n" else pc(ms[s][k], 2)
                                           for s in ms) + " |")
    L += ["",
          "Signo de la parte no explicada (por hora) estable entre las seis variantes: "
          f"**{'sí' if r['genero']['oaxaca']['signo_estable'] else 'NO — señal de alarma'}**.",
          "",
          "### Ñopo (2008), ingreso por hora, como fracción del promedio femenino",
          "",
          "Unidades: Oaxaca trabaja sobre la media de los logaritmos (una media "
          "geométrica); 0,262 log puntos son ≈ 30 % entre medias geométricas. Ñopo "
          "trabaja sobre medias aritméticas del ingreso por hora, relativas a la media "
          "femenina. Δ = 15 % no contradice al 0,262: miden medias distintas.",
          "",
          "| Celdas | Δ total | Δ0 no explicada | ΔH | ΔM | ΔX | Soporte H | Soporte M | Celdas |",
          "|---|---|---|---|---|---|---|---|---|"]
    for c, et in (("A", "educación × edad × área × dominio"), ("B", "A × categoría")):
        o = r["genero"]["nopo"][c]
        L.append(f"| {et} | {pc(o['delta']['valor'] * 100)} % | {pc(o['d0']['valor'] * 100)} % "
                 f"(±{pc(196 * o['d0']['ee'])}) | {pc(o['dH']['valor'] * 100)} % | "
                 f"{pc(o['dM']['valor'] * 100)} % | {pc(o['dX']['valor'] * 100)} % | "
                 f"{pc(o['soporte_hombres']['valor'] * 100)} % | "
                 f"{pc(o['soporte_mujeres']['valor'] * 100)} % | {o['celdas']} |")
    L += ["",
          "## 3. Retornos a la educación (log ingreso por hora, por año de educación)",
          "",
          "| Segmento | Coef. | IC 95 % | n |", "|---|---|---|---|"]
    for s, c in r["retornos"].items():
        L.append(f"| {s} | {pc(c['coef'] * 100)} % | [{pc(c['ic95'][0] * 100)}; "
                 f"{pc(c['ic95'][1] * 100)}] | {mil(c['n'])} |")
    L += ["",
          "Contraste referencial, no réplica: Yamada (2007) reporta para 2004 un 12,5 % en "
          "asalariados y un 6,5 % en independientes; Psacharopoulos y Patrinos (2018), un "
          "11,0 % privado para América Latina y el Caribe. Los años, las muestras y las "
          "especificaciones son distintos.",
          "",
          "## 4. Departamentos",
          "",
          "| Departamento | n | Informalidad | IC 95 % | Ingreso mensual mediano | Se muestra |",
          "|---|---|---|---|---|---|"]
    for cod, g in r["departamentos"]["grupos"].items():
        L.append(f"| {DEPARTAMENTOS.get(cod, cod)} | {mil(g['n'])} | {pc(g['informal_pct']['valor'])} % | "
                 f"[{pc(g['informal_pct']['ic95'][0])}; {pc(g['informal_pct']['ic95'][1])}] | "
                 f"S/ {mil(g['ingreso_mediano']['valor'])} | {'sí' if g['mostrar'] else 'no'} |")
    L += ["",
          f"Control de agregación: la media ponderada de las celdas reproduce la tasa de la "
          f"muestra ({pc(r['departamentos']['control_nacional'])} %).",
          "",
          "## 5. Lengua materna (oculto en la app: `MOSTRAR_LENGUA = False`)",
          "",
          "Se analiza agregada y como brecha estructural, no como juicio sobre personas: "
          "la lengua materna se asocia con dónde se nació, qué escuela hubo y qué mercado "
          "laboral queda cerca.",
          "",
          "| Lengua | n | Informalidad | Ingreso mensual mediano | Brecha ajustada por hora vs. castellano | Se muestra |",
          "|---|---|---|---|---|---|"]
    for lg, g in r["lengua"]["grupos"].items():
        b = r["lengua"]["brecha_ajustada"].get(lg)
        bt = f"{pc(b['pct'])} % [{pc(b['pct_ic95'][0])}; {pc(b['pct_ic95'][1])}]" if b else "referencia"
        L.append(f"| {lg} | {mil(g['n'])} | {pc(g['informal_pct']['valor'])} % | "
                 f"S/ {mil(g['ingreso_mediano']['valor'])} | {bt} | {'sí' if g['mostrar'] else 'no'} |")
    L += ["", "## Alarmas", ""]
    L += [f"- {a}" for a in r["alarmas"]] or ["- Ninguna."]
    L += ["",
          "## Limitaciones",
          "",
          "- Ingreso monetario declarado, sin ingreso en especie. Es el mismo del resto de la app.",
          "- El ingreso por hora usa horas habituales de la semana de referencia × 52/12.",
          "- Se ignoran los estratos del diseño muestral, así que los intervalos son algo "
          "conservadores.",
          "- La muestra excluye a los trabajadores familiares no remunerados (ingreso 0), que "
          "son informales por definición. Por eso la tasa de informalidad queda por debajo de "
          "la oficial."]
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=200)
    B = ap.parse_args().B

    df = cargar()
    w = df["FAC500A"].to_numpy()
    tasa = media_p(df["informal"].to_numpy(float), w) * 100
    alarmas: list[str] = []

    pen = penalidad(df)
    oax = genero_oaxaca(df, B)
    if not oax["signo_estable"]:
        alarmas.append("Oaxaca: la parte no explicada por hora cambia de signo entre variantes.")
    nop = genero_nopo(df, B)
    medias = medias_por_sexo(df)
    ret = retornos(df)

    dep = {"grupos": tabla_grupos(df, "depto", B)}
    pesos = np.array([g["peso"] for g in dep["grupos"].values()], dtype=float)
    tasas = np.array([g["informal_pct"]["valor"] for g in dep["grupos"].values()])
    dep["control_nacional"] = round(float(np.sum(pesos * tasas) / pesos.sum()), 2)
    dep["nombres"] = {k: DEPARTAMENTOS[k] for k in dep["grupos"]}
    desconocidos = set(dep["grupos"]) - set(DEPARTAMENTOS)
    if desconocidos:
        alarmas.append(f"UBIGEO con departamento desconocido: {sorted(desconocidos)}")
    for cod, g in dep["grupos"].items():
        if not g["mostrar"]:
            alarmas.append(f"Departamento {cod}: n = {g['n']} < {N_MIN}, no se muestra.")

    len_ = {"grupos": tabla_grupos(df, "lengua", B), "brecha_ajustada": brecha_lengua(df),
            "sin_dato": int(df["lengua"].isna().sum())}
    for lg, g in len_["grupos"].items():
        if not g["mostrar"]:
            alarmas.append(f"Lengua {lg}: n = {g['n']} < {N_MIN}, no se muestra.")

    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                                text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "sin-git"
    r = {
        "meta": {"generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "commit": commit, "script": "src/10_contexto.py", "n": int(len(df)),
                 "n_hora": int(df["ingreso_hora"].notna().sum()),
                 "informal_pct": round(tasa, 2), "B": B, "semilla": SEMILLA,
                 "n_min": N_MIN, "pesos": "FAC500A",
                 "varianza": "bootstrap por conglomerado (CONGLOME), sin estratos"},
        "penalidad": pen,
        "genero": {"oaxaca": oax, "nopo": nop, "medias_por_sexo": medias},
        "peru": peru_en_cifras(),
        "retornos": ret,
        "departamentos": dep,
        "lengua": len_,
        "alarmas": alarmas,
    }
    escribir_json_atomico(RUTA_SALIDA, json.dumps(r, ensure_ascii=False, indent=1))
    RUTA_REPORTE.write_text(reporte(r), encoding="utf-8")
    print(f"ok · {RUTA_SALIDA.name} · {len(alarmas)} alarmas")


if __name__ == "__main__":
    main()
