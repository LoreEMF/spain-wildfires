"""
Agregaciones para análisis y visualización (Spain Wildfires).

Incluye utilidades para:
- Crear la métrica 'total_medios'.
- Agregar por provincia (choropleth).
- Agregar por año (hectáreas quemadas y recursos).
- Top de provincias por hectáreas quemadas.

Autores: Lorena Elena Mohanu · José Ancízar Arbeláez Nieto
Licencia: MIT — ver archivo LICENSE en la raíz del repositorio.
"""

from __future__ import annotations
from typing import Iterable, List, Tuple

import pandas as pd


# Conjunto de columnas de recursos esperado en los datos
RESOURCE_COLUMNS: Tuple[str, ...] = (
    "numeromediospersonal",
    "numeromediospesados",
    "numeromediosaereos",
)


def add_total_resources(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea la columna 'total_medios' como suma de los recursos personales, pesados y aéreos.

    Notas
    -----
    - No modifica el DataFrame original; devuelve una copia.
    - Asume que las columnas de recursos están ya en formato numérico (ver cleaning.py).
    """
    out = df.copy()
    missing = [c for c in RESOURCE_COLUMNS if c not in out.columns]
    if missing:
        raise KeyError(f"Faltan columnas de recursos: {missing}")
    out["total_medios"] = out["numeromediospersonal"] + out["numeromediospesados"] + out["numeromediosaereos"]
    return out


def group_by_province_for_map(
    df: pd.DataFrame,
    province_col: str = "provincia",
) -> pd.DataFrame:
    """
    Agrega por provincia las métricas necesarias para el mapa coroplético.

    Retorna
    -------
    pd.DataFrame
        Columnas:
        - provincia
        - total_medios
        - numeromediospersonal
        - numeromediospesados
        - numeromediosaereos
    """
    out = df.copy()
    if "total_medios" not in out.columns:
        out = add_total_resources(out)

    # Verificación de columnas de recursos
    missing = [c for c in RESOURCE_COLUMNS if c not in out.columns]
    if missing:
        raise KeyError(f"Faltan columnas de recursos para agregar por provincia: {missing}")

    agg = (
        out.groupby(province_col)
        .agg(
            total_medios=("total_medios", "sum"),
            numeromediospersonal=("numeromediospersonal", "sum"),
            numeromediospesados=("numeromediospesados", "sum"),
            numeromediosaereos=("numeromediosaereos", "sum"),
        )
        .reset_index()
    )
    return agg


def aggregate_burned_area_by_year(
    df: pd.DataFrame,
    year_col: str = "anio",
    area_col: str = "hectareas_quemadas",
    fallback_area_col: str = "perdidassuperficiales",
) -> pd.DataFrame:
    """
    Agrega las hectáreas quemadas por año.

    Parámetros
    ----------
    year_col : str
        Nombre de la columna de año.
    area_col : str
        Columna preferida (alias) para hectáreas quemadas.
    fallback_area_col : str
        Columna a usar si no existe `area_col`.

    Retorna
    -------
    pd.DataFrame
        Columnas:
        - anio
        - hectareas_quemadas
    """
    out = df.copy()
    col = area_col if area_col in out.columns else fallback_area_col
    if col not in out.columns:
        raise KeyError(f"No se encontró columna de área quemada: {area_col} ni {fallback_area_col}")

    serie = out.groupby(year_col)[col].sum().reset_index()
    # Normalizamos el nombre de la segunda columna a 'hectareas_quemadas'
    serie = serie.rename(columns={col: "hectareas_quemadas"})
    return serie


def aggregate_resources_by_year(
    df: pd.DataFrame,
    year_col: str = "anio",
    resource_cols: Iterable[str] = RESOURCE_COLUMNS,
) -> pd.DataFrame:
    """
    Agrega los recursos utilizados por año (suma por columna de recursos).

    Retorna
    -------
    pd.DataFrame
        Columnas:
        - anio
        - numeromediospersonal
        - numeromediospesados
        - numeromediosaereos
    """
    out = df.copy()
    # Validación de columnas presentes
    missing = [c for c in resource_cols if c not in out.columns]
    if missing:
        raise KeyError(f"Faltan columnas de recursos para agregar por año: {missing}")

    grp = out.groupby(year_col)[list(resource_cols)].sum().reset_index()
    return grp


def top_provinces_by_burned_area(
    df: pd.DataFrame,
    n: int = 10,
    province_col: str = "provincia",
    area_col: str = "hectareas_quemadas",
    fallback_area_col: str = "perdidassuperficiales",
    ascending: bool = False,
) -> pd.DataFrame:
    """
    Retorna el top N de provincias según hectáreas quemadas (agregado).

    Parámetros
    ----------
    n : int
        Número de provincias a retornar (por defecto 10).
    ascending : bool
        Si True, orden ascendente; si False, descendente.

    Retorna
    -------
    pd.DataFrame
        Columnas:
        - provincia
        - hectareas_quemadas
    """
    out = df.copy()
    col = area_col if area_col in out.columns else fallback_area_col
    if col not in out.columns:
        raise KeyError(f"No se encontró columna de área quemada: {area_col} ni {fallback_area_col}")

    agg = out.groupby(province_col)[col].sum().reset_index()
    agg = agg.rename(columns={col: "hectareas_quemadas"})
    agg = agg.sort_values(by="hectareas_quemadas", ascending=ascending).head(n)
    return agg
