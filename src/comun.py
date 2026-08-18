# comun.py — utilidades compartidas (rutas, carga, caché de grillas)
# Proyecto ENAHO 2025 · Yoichi Palacios · https://github.com/IchiSieben/enaho-ingresos-informalidad
# Licencia: Apache-2.0 (ver LICENSE)
"""
Utilidades compartidas del proyecto ENAHO: ingreso laboral e informalidad.

Adaptado de proyecto_sis_diabetes/src/comun.py: misma mecanica de
preprocesador, contrato de features, cache de busquedas y control de tamano
de artefactos; cambian las constantes de dominio (ENAHO 2025, encuesta 1031).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RAIZ = Path(__file__).resolve().parents[1]
DIR_RAW = RAIZ / "data" / "raw"
DIR_INTERIM = RAIZ / "data" / "interim"
DIR_PROCESSED = RAIZ / "data" / "processed"
DIR_MODELS = RAIZ / "models"
DIR_REPORTS = RAIZ / "reports"
DIR_FIGURAS = DIR_REPORTS / "figuras"
RUTA_SCHEMA = DIR_MODELS / "feature_schema.json"

SEMILLA = 42
N_JOBS = 20

# Umbral de colapso en conteo ABSOLUTO (misma justificacion que en el SIS).
MIN_FRECUENCIA = 300
MAX_CATEGORIAS = 30
LIMITE_MB = 50.0

# El INEI usa 999999 (a veces 999999.9) como codigo de faltante en variables
# monetarias; anchos menores usan 9999/99999 segun el diccionario. Ampliado
# tras el barrido de la auditoria (18/08/2026): sin fuga activa hoy (las
# columnas que usan estos anchos no estan en el pipeline), es prevencion.
CENTINELAS_MONETARIOS = [999999, 999999.9, 99999, 9999]

LLAVES_PERSONA = ["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"]
LLAVES_HOGAR = ["CONGLOME", "VIVIENDA", "HOGAR"]

ETIQUETAS = {
    "anios_educ": "Años de educación aprobados",
    "edad": "Edad (años)",
    "exper": "Experiencia potencial (años)",
    "sexo": "Sexo",
    "area": "Área de residencia",
    "dominio": "Dominio geográfico",
    "rama": "Rama de actividad (agrupada)",
    "horas_total": "Horas trabajadas por semana (todas las ocupaciones)",
    "tamano_empresa": "Tamaño de la empresa (personas)",
    "categoria": "Categoría ocupacional",
    "nivel_educ": "Nivel educativo",
}

RANGOS_FORMULARIO = {
    "edad": {"min": 14, "max": 80},
    "horas_total": {"min": 4, "max": 84},
    "anios_educ": {"min": 0, "max": 18},
}

ETIQUETA_OTROS = "OTROS"

MAPA_DOMINIO = {1: "Costa Norte", 2: "Costa Centro", 3: "Costa Sur",
                4: "Sierra Norte", 5: "Sierra Centro", 6: "Sierra Sur",
                7: "Selva", 8: "Lima Metropolitana"}
MAPA_TAMANO = {1: "Hasta 20", 2: "21 a 50", 3: "51 a 100",
               4: "101 a 500", 5: "Más de 500"}
MAPA_CATEGORIA = {1: "Empleador", 2: "Independiente", 3: "Empleado",
                  4: "Obrero", 6: "Trabajador del hogar"}


def leer_enaho(ruta: Path, usecols: list[str]) -> pd.DataFrame:
    """CSV del INEI: sep=';', latin-1, llaves como texto (ceros a la izquierda)."""
    return pd.read_csv(ruta, sep=";", encoding="latin-1", usecols=usecols,
                       dtype={k: str for k in LLAVES_PERSONA}, low_memory=False)


def anios_educacion(p301a: pd.Series, p301b: pd.Series, p301c: pd.Series) -> pd.Series:
    """
    Recodificacion estandar ENAHO de P301A (nivel) + P301B/P301C (anio/grado).
    Niveles completos: primaria 6, secundaria 11, sup. tecnica 14, universitaria
    16, posgrado 18; incompletos suman el ultimo anio aprobado.
    """
    grado = p301b.fillna(p301c)
    anios = pd.Series(np.nan, index=p301a.index)
    anios[p301a.isin([1, 2, 12])] = 0
    anios[p301a == 3] = grado[p301a == 3].fillna(0)
    anios[p301a == 4] = 6
    anios[p301a == 5] = 6 + grado[p301a == 5].fillna(0)
    anios[p301a == 6] = 11
    anios[p301a == 7] = 11 + grado[p301a == 7].fillna(0)
    anios[p301a == 8] = 11 + grado[p301a == 8].fillna(3)
    anios[p301a == 9] = 11 + grado[p301a == 9].fillna(0)
    anios[p301a == 10] = 16
    anios[p301a == 11] = 18
    return anios.clip(upper=20)


def nivel_educativo_agrupado(p301a: pd.Series) -> pd.Series:
    """P301A (1-12) colapsado a 6 categorias legibles."""
    mapa = {1: "Sin nivel/inicial", 2: "Sin nivel/inicial", 12: "Sin nivel/inicial",
            3: "Primaria", 4: "Primaria",
            5: "Secundaria", 6: "Secundaria",
            7: "Superior técnica", 8: "Superior técnica",
            9: "Superior universitaria", 10: "Superior universitaria",
            11: "Posgrado"}
    return p301a.map(mapa)


def rama_agrupada(p506r4: pd.Series) -> pd.Series:
    """
    CIIU rev.4 (P506R4, 4 digitos) a grandes sectores por division (2 digitos).
    Las categorias que queden bajo MIN_FRECUENCIA se colapsan aguas abajo.
    """
    division = pd.to_numeric(p506r4, errors="coerce") // 100

    def sector(d: float) -> str | float:
        if pd.isna(d):
            return np.nan
        d = int(d)
        if d <= 3: return "Agropecuario y pesca"
        if d <= 9: return "Minería e hidrocarburos"
        if d <= 33: return "Manufactura"
        if d <= 39: return "Electricidad, gas y agua"
        if d <= 43: return "Construcción"
        if d <= 47: return "Comercio"
        if d <= 53: return "Transporte y almacenamiento"
        if d <= 56: return "Alojamiento y restaurantes"
        if d <= 63: return "Información y comunicaciones"
        if d <= 82: return "Servicios profesionales y financieros"
        if d == 84: return "Administración pública"
        if d == 85: return "Enseñanza"
        if d <= 88: return "Salud y asistencia social"
        if d in (97, 98): return "Servicio doméstico"
        return "Otros servicios"

    return division.map(sector)


# --------------------------------------------------------------------------
# Preprocesador (identico al SIS)
# --------------------------------------------------------------------------
def separar_columnas(X: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Devuelve (columnas_numericas, columnas_categoricas)."""
    numericas = [c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])]
    categoricas = [c for c in X.columns if c not in numericas]
    return numericas, categoricas


def construir_preprocesador(numericas: list[str], categoricas: list[str]) -> ColumnTransformer:
    """
    ColumnTransformer con TODO el preprocesamiento dentro. La imputacion va
    aqui y nunca antes del split: la mediana debe calcularse solo con datos de
    entrenamiento en cada pliegue.
    """
    tuberia_num = Pipeline([
        ("imputar", SimpleImputer(strategy="median")),
        ("escalar", StandardScaler()),
    ])
    return ColumnTransformer([
        ("num", tuberia_num, numericas),
        ("cat", OneHotEncoder(handle_unknown="infrequent_if_exist",
                              min_frequency=MIN_FRECUENCIA,
                              max_categories=MAX_CATEGORIAS,
                              sparse_output=False), categoricas),
    ])


# --------------------------------------------------------------------------
# Contrato de features (feature_schema.json) — identico al SIS
# --------------------------------------------------------------------------
def resumen_categorias(preprocesador: ColumnTransformer) -> pd.DataFrame:
    """Tabla de categorias supervivientes y colapsadas, desde el encoder AJUSTADO."""
    enc = preprocesador.named_transformers_["cat"]
    columnas = list(preprocesador.transformers_[1][2])
    filas = []
    for i, col in enumerate(columnas):
        infrec = enc.infrequent_categories_[i]
        n_infrec = 0 if infrec is None else len(infrec)
        total = len(enc.categories_[i])
        filas.append({
            "variable": col,
            "categorias": total,
            "sobreviven": total - n_infrec,
            "colapsadas": n_infrec,
            "agrupadas": "" if not n_infrec else ", ".join(map(str, infrec)),
        })
    return pd.DataFrame(filas)


def extraer_features(pipeline_ajustado: Pipeline, X_entrenamiento: pd.DataFrame) -> list[dict]:
    """Lista de features del schema a partir del pipeline YA AJUSTADO."""
    prep = pipeline_ajustado.named_steps["prep"]
    numericas = list(prep.transformers_[0][2])
    categoricas = list(prep.transformers_[1][2])
    enc = prep.named_transformers_["cat"]

    features = []

    for col in numericas:
        serie = X_entrenamiento[col].dropna()
        override = RANGOS_FORMULARIO.get(col, {})
        minimo = override.get("min", float(serie.min()))
        maximo = override.get("max", float(serie.max()))
        mediana = float(serie.median())
        entrada = {
            "nombre": col,
            "tipo": "numerico",
            "min": round(float(minimo), 2),
            "max": round(float(maximo), 2),
            "default": round(min(max(mediana, minimo), maximo), 2),
            "etiqueta": ETIQUETAS.get(col, col),
        }
        if col in RANGOS_FORMULARIO:
            entrada["nota"] = (
                f"El rango del formulario ({minimo}–{maximo}) es más estrecho que el "
                f"del entrenamiento ({serie.min():.0f}–{serie.max():.0f}). El modelo se "
                "entrenó con los datos intactos; el formulario no ofrece valores "
                "implausibles presentes en la fuente."
            )
        features.append(entrada)

    for i, col in enumerate(categoricas):
        infrec = enc.infrequent_categories_[i]
        infrec = [] if infrec is None else [str(c) for c in infrec]
        supervivientes = [str(c) for c in enc.categories_[i] if str(c) not in set(infrec)]
        opciones = supervivientes + ([ETIQUETA_OTROS] if infrec else [])

        conteos = X_entrenamiento[col].astype(str).value_counts()
        default = next((o for o in conteos.index if o in set(supervivientes)),
                       opciones[0] if opciones else "")

        entrada = {
            "nombre": col,
            "tipo": "categorico",
            "opciones": opciones,
            "default": str(default),
            "etiqueta": ETIQUETAS.get(col, col),
        }
        if infrec:
            entrada["agrupadas_en_otros"] = sorted(infrec)
            entrada["nota_otros"] = (
                f"«{ETIQUETA_OTROS}» agrupa {len(infrec)} categorías con menos de "
                f"{MIN_FRECUENCIA} registros en el entrenamiento; el modelo no las "
                "distingue entre sí."
            )
        features.append(entrada)

    return features


RUTA_CACHE_PARAMS = DIR_MODELS / "_hiperparametros.json"


def escribir_json_atomico(ruta: Path, texto: str) -> None:
    """
    Escribe a <ruta>.tmp y os.replace al destino: si la maquina se cuelga a
    mitad de la escritura (ya paso dos veces en este portafolio), el archivo
    publicado nunca queda truncado.
    """
    tmp = ruta.with_suffix(ruta.suffix + ".tmp")
    tmp.write_text(texto, encoding="utf-8")
    os.replace(tmp, ruta)


def busqueda_cacheada(clave: str, ejecutar) -> tuple[dict, float, float, bool]:
    """
    Ejecuta la busqueda de hiperparametros o la recupera de disco. Borrar
    `models/_hiperparametros.json` fuerza el recalculo.
    `ejecutar` debe devolver (best_params, best_score, segundos).
    """
    cache = {}
    if RUTA_CACHE_PARAMS.exists():
        cache = json.loads(RUTA_CACHE_PARAMS.read_text(encoding="utf-8"))
    if clave in cache:
        e = cache[clave]
        return e["params"], e["score"], e["segundos"], True

    params, score, segundos = ejecutar()
    DIR_MODELS.mkdir(parents=True, exist_ok=True)
    cache[clave] = {"params": params, "score": score, "segundos": segundos}
    escribir_json_atomico(RUTA_CACHE_PARAMS,
                          json.dumps(cache, indent=2, ensure_ascii=False))
    return params, score, segundos, False


def guardar_schema(clave: str, contenido: dict) -> None:
    """Escribe/actualiza una seccion de feature_schema.json sin pisar la otra."""
    DIR_MODELS.mkdir(parents=True, exist_ok=True)
    schema = {}
    if RUTA_SCHEMA.exists():
        schema = json.loads(RUTA_SCHEMA.read_text(encoding="utf-8"))
    schema[clave] = contenido
    escribir_json_atomico(RUTA_SCHEMA,
                          json.dumps(schema, indent=2, ensure_ascii=False))


def importancia_por_variable(pipeline_ajustado: Pipeline) -> pd.Series:
    """Suma la importancia de las columnas one-hot de vuelta a su variable."""
    prep = pipeline_ajustado.named_steps["prep"]
    modelo = pipeline_ajustado.named_steps["modelo"]
    nombres = prep.get_feature_names_out()
    importancias = pd.Series(modelo.feature_importances_, index=nombres)

    numericas = list(prep.transformers_[0][2])
    categoricas = list(prep.transformers_[1][2])

    agregada = {}
    for col in numericas:
        agregada[col] = float(importancias.get(f"num__{col}", 0.0))
    for col in categoricas:
        prefijo = f"cat__{col}_"
        agregada[col] = float(importancias[[n for n in nombres
                                            if n.startswith(prefijo)]].sum())
    return pd.Series(agregada).sort_values(ascending=False)


def guardar_con_limite(objeto, ruta: Path, limite_mb: float = LIMITE_MB) -> float:
    """Guarda con compress=3 y devuelve el tamano en MB."""
    DIR_MODELS.mkdir(parents=True, exist_ok=True)
    joblib.dump(objeto, ruta, compress=3)
    return ruta.stat().st_size / 1024 ** 2


def escalera_reduccion(params_base: dict, prefijo: str) -> list[dict]:
    """Candidatos mas ligeros si el artefacto supera el limite de tamano."""
    escalones = []
    for hojas in (20, 50, 100, 200):
        p = dict(params_base)
        p[f"{prefijo}min_samples_leaf"] = hojas
        escalones.append(p)
    for hojas in (100, 200):
        for arboles in (200, 100):
            p = dict(params_base)
            p[f"{prefijo}min_samples_leaf"] = hojas
            p[f"{prefijo}n_estimators"] = arboles
            escalones.append(p)
    return escalones


def formato_md(df: pd.DataFrame, index: bool = False) -> str:
    d = df.reset_index() if index else df
    cols = [str(c) for c in d.columns]
    out = ["| " + " | ".join(cols) + " |",
           "|" + "|".join("---" for _ in cols) + "|"]
    for _, f in d.iterrows():
        out.append("| " + " | ".join(str(v) for v in f) + " |")
    return "\n".join(out) + "\n"
