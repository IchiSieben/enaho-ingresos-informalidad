# 08b_ablacion_sexo.py — ¿el clasificador necesita saber el sexo?
# Proyecto ENAHO 2025 · Yoichi Palacios Tanaka · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Grupo ENEI: Alan Nestor Cañazaca Mamani · Magdalena Quico de la Cruz · Edgar Delgado Ortega
# Licencia: Apache-2.0 (ver LICENSE)
#
# El clasificador se presenta como herramienta de focalización que «señala
# configuraciones de empleo, no personas», pero lleva `sexo` entre sus
# variables. Aquí se mide cuánto aporta. Mismo protocolo que 08 (GB con los
# hiperparámetros ganadores, mismo split y KFold), y cada variante en SU
# propio punto operativo con la regla aprobada (precisión ≥ 0,90): comparar
# las dos con el umbral de la completa sesgaría la comparación.
# Solo escribe reportes; no toca modelos, schema ni artefactos de la app.
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import average_precision_score, precision_recall_curve
from sklearn.model_selection import KFold, cross_val_predict, train_test_split
from sklearn.pipeline import Pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comun import (DIR_PROCESSED, DIR_REPORTS, N_JOBS, RUTA_CACHE_PARAMS,
                   RUTA_SCHEMA, SEMILLA, construir_preprocesador, formato_md)

K = 5
KF = KFold(n_splits=K, shuffle=True, random_state=SEMILLA)
NUMERICAS = ["anios_educ", "edad", "exper", "exper2", "horas_total"]
CATEGORICAS = ["sexo", "area", "dominio", "rama", "tamano_empresa", "categoria"]
VARIANTES = {"completa": [], "sin sexo": ["sexo"]}
PRECISION_MIN = 0.90


def umbral_operativo(y, p):
    # El menor umbral con precisión ≥ 0,90: maximiza el recall dentro de la regla.
    prec, _, umb = precision_recall_curve(y, p)
    ok = np.where(prec[:-1] >= PRECISION_MIN)[0]
    return float(umb[ok[0]])


def tasas(y, pred, w):
    # Precisión, recall y tasa de señalamiento con pesos w (w=1: muestra).
    tp = float(np.sum(w * (pred == 1) * (y == 1)))
    return {"senalados": round(float(np.sum(w * pred) / np.sum(w)), 4),
            "precision": round(tp / float(np.sum(w * pred)), 4),
            "recall": round(tp / float(np.sum(w * y)), 4)}


def t_corregido(dif, n_tr, n_te):
    # t remuestreado corregido (Nadeau y Bengio, 2003): los pliegues comparten
    # datos de entrenamiento, así que la varianza ingenua se queda corta.
    k = len(dif)
    var = (1 / k + n_te / n_tr) * np.var(dif, ddof=1)
    t = dif.mean() / np.sqrt(var)
    return float(t), float(2 * stats.t.sf(abs(t), k - 1))


def main() -> None:
    df = pd.read_parquet(DIR_PROCESSED / "torneo_frame.parquet").dropna(subset=["informal"])
    y = df["informal"].astype(int)
    idx_tr, _ = train_test_split(df.index, test_size=0.2,
                                 random_state=SEMILLA, stratify=y)
    y_tr = y.loc[idx_tr].to_numpy()
    sexo = df.loc[idx_tr, "sexo"].to_numpy()
    peso = df.loc[idx_tr, "FAC500A"].astype(float).to_numpy()

    params = json.loads(RUTA_CACHE_PARAMS.read_text(encoding="utf-8"))["clasif_gb"]["params"]
    params = {k.replace("modelo__", ""): v for k, v in params.items()}
    umbral_schema = json.loads(RUTA_SCHEMA.read_text(encoding="utf-8"))["clasificador"]["punto_operativo"]["umbral"]
    pliegues = list(KF.split(idx_tr))

    resumen, grupos, por_pliegue = [], [], {}
    for nombre, quitar in VARIANTES.items():
        num = [c for c in NUMERICAS if c not in quitar]
        cat = [c for c in CATEGORICAS if c not in quitar]
        pipe = Pipeline([
            ("prep", construir_preprocesador(num, cat)),
            ("modelo", GradientBoostingClassifier(random_state=SEMILLA, **params)),
        ])
        p = cross_val_predict(pipe, df.loc[idx_tr, num + cat], y_tr, cv=KF,
                              n_jobs=N_JOBS, pre_dispatch="n_jobs",
                              method="predict_proba")[:, 1]
        por_pliegue[nombre] = np.array([average_precision_score(y_tr[te], p[te])
                                        for _, te in pliegues])
        u = umbral_operativo(y_tr, p)
        pred = (p >= u).astype(int)
        glob = tasas(y_tr, pred, np.ones_like(peso))
        resumen.append({"variante": nombre, "PRAUC_cv": round(average_precision_score(y_tr, p), 4),
                        "PRAUC_desv_pliegues": round(float(por_pliegue[nombre].std(ddof=1)), 4),
                        "umbral_propio": round(u, 4), **glob})
        for g in sorted(np.unique(sexo)):
            m = sexo == g
            for base, w in [("muestra", np.ones(m.sum())), ("ponderado", peso[m])]:
                grupos.append({"variante": nombre, "sexo": g, "base": base, "n": int(m.sum()),
                               **tasas(y_tr[m], pred[m], w)})
        print(resumen[-1], flush=True)

    dif = por_pliegue["completa"] - por_pliegue["sin sexo"]
    n_te = len(y_tr) // K
    t, pval = t_corregido(dif, len(y_tr) - n_te, n_te)
    tabla, tabla_g = pd.DataFrame(resumen), pd.DataFrame(grupos)
    n_txt = f"{len(y_tr):,}".replace(",", ".")

    md = ["# Ablación: el clasificador sin `sexo`\n",
          "Generado por `src/08b_ablacion_sexo.py`. Mismo protocolo que la "
          "ablación estructural: GB con los hiperparámetros ganadores, mismo "
          "split y KFold de 5 pliegues, predicciones fuera de pliegue sobre "
          f"entrenamiento (n = {n_txt}). Cada variante se evalúa en su propio "
          "punto operativo con la regla aprobada, precisión ≥ 0,90 (el umbral "
          f"de la completa reproduce el del schema, {umbral_schema}).\n",
          "## Rendimiento global (muestra)\n", formato_md(tabla),
          f"\nDiferencia de PR-AUC por pliegue (completa − sin sexo): media "
          f"{dif.mean():.4f}, positiva en {int((dif > 0).sum())}/{K} pliegues. "
          f"t remuestreado corregido (Nadeau y Bengio, 2003) = {t:.2f}, "
          f"p = {pval:.3f}. Se lee igual que la rejilla ampliada de E9: "
          "diferencia sistemática, magnitud irrelevante.\n",
          "## Por sexo, cada variante en su punto operativo\n",
          "«muestra» = sin ponderar; «ponderado» = con FAC500A (población).\n",
          formato_md(tabla_g),
          "\nLectura: la decisión de mantener o retirar `sexo` es del autor. "
          "Este reporte mide el costo predictivo y cómo cambian las tasas de "
          "error por grupo; no afirma que alguna variante sea «justa».\n"]
    (DIR_REPORTS / "ablacion_sexo.md").write_text("\n".join(md), encoding="utf-8")
    tabla_g.to_csv(DIR_REPORTS / "ablacion_sexo_grupos.csv", index=False)
    print(f"\numbral schema {umbral_schema}")
    print(f"dif media {dif.mean():.4f}  t_corr={t:.2f}  p={pval:.3f}")
    print(tabla.to_string(index=False))
    print(tabla_g.to_string(index=False))


if __name__ == "__main__":
    main()
