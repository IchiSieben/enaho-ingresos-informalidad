# Fase 0.1 — Inventario de los modulos ENAHO 2025 (codigo de encuesta 1031).
# Por columna: dtype, nunique, %nulos ANTES y DESPUES de convertir el centinela
# 999999/999999.9 a NaN. La diferencia entre ambos es la magnitud del problema.
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
REPORTES = RAIZ / "reports"

MODULOS = {
    "modulo02_miembros": RAW / "1031-Modulo02" / "1031-Modulo02" / "Enaho01-2025-200.csv",
    "modulo03_educacion": RAW / "1031-Modulo03" / "1031-Modulo03" / "Enaho01A-2025-300.csv",
    "modulo05_empleo": RAW / "1031-Modulo05" / "1031-Modulo05" / "Enaho01a-2025-500.csv",
    "modulo34_sumaria": RAW / "1031-Modulo34" / "1031-Modulo34" / "Sumaria-2025.csv",
    "modulo09_gasto_mant": RAW / "1031-Modulo9 y 10" / "1031-Modulo09" / "Modulo_09.csv",
    "modulo10_gasto_transp": RAW / "1031-Modulo9 y 10" / "1031-Modulo10" / "Enaho01-2025-604.csv",
}

CENTINELAS = [999999, 999999.9]
N_MUESTRA = 5000


def contar_filas(ruta: Path) -> int:
    with open(ruta, "rb") as f:
        return sum(1 for _ in f) - 1


def inventariar(nombre: str, ruta: Path) -> pd.DataFrame:
    df = pd.read_csv(ruta, sep=";", encoding="latin-1", nrows=N_MUESTRA, low_memory=False)
    filas = []
    for col in df.columns:
        s = df[col]
        nulos_antes = s.isna().mean() * 100
        s_num = pd.to_numeric(s, errors="coerce") if s.dtype == object else s
        es_centinela = s_num.isin(CENTINELAS)
        nulos_despues = (s.isna() | es_centinela).mean() * 100
        filas.append({
            "columna": col,
            "dtype": str(s.dtype),
            "nunique": s.nunique(dropna=True),
            "pct_nulos_antes": round(nulos_antes, 2),
            "pct_nulos_despues": round(nulos_despues, 2),
            "pct_centinela": round(nulos_despues - nulos_antes, 2),
            "n_centinela_muestra": int(es_centinela.sum()),
        })
    inv = pd.DataFrame(filas)
    inv.insert(0, "modulo", nombre)
    return inv


def main() -> None:
    resumen = []
    inventarios = []
    for nombre, ruta in MODULOS.items():
        n_filas = contar_filas(ruta)
        inv = inventariar(nombre, ruta)
        inventarios.append(inv)
        afectadas = inv[inv["pct_centinela"] > 0]
        resumen.append({
            "modulo": nombre,
            "archivo": ruta.name,
            "filas": n_filas,
            "columnas": len(inv),
            "cols_con_centinela": len(afectadas),
        })
        print(f"\n=== {nombre} — {ruta.name} — {n_filas:,} filas x {len(inv)} cols ===")
        if len(afectadas):
            print("Columnas con centinela 999999 en la muestra de 5.000:")
            print(afectadas[["columna", "pct_nulos_antes", "pct_nulos_despues",
                             "pct_centinela"]].to_string(index=False))
        else:
            print("Sin centinelas en la muestra.")

    pd.concat(inventarios).to_csv(REPORTES / "inventario_columnas.csv", index=False)
    pd.DataFrame(resumen).to_csv(REPORTES / "inventario_modulos.csv", index=False)
    print("\nEscrito: reports/inventario_columnas.csv y reports/inventario_modulos.csv")


if __name__ == "__main__":
    main()
