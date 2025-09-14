"""
Funciones de limpieza y preparación de datos para el proyecto Spain Wildfires.

Proporciona funciones para limpiar, tipificar y enriquecer los datos de incendios.

Autores: Lorena Elena Mohanu · José Ancízar Arbeláez Nieto
Licencia: MIT — ver archivo LICENSE en la raíz del repositorio.
"""

from __future__ import annotations
from typing import Sequence, Optional

import numpy as np
import pandas as pd


# Conjunto por defecto de columnas de interés
DEFAULT_COLUMNS: tuple[str, ...] = (
    "anio",
    "idpeligro",
    "idprovincia",
    "provincia",
    "numeromediospersonal",
    "numeromediospesados",
    "numeromediosaereos",
    "perdidassuperficiales",
    "idcausa",
)


def select_columns(df: pd.DataFrame, columns: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """
    Selecciona un subconjunto de columnas si existen en el DataFrame.

    Parámetros
    ----------
    df : pd.DataFrame
        Datos crudos de incendios.
    columns : lista de str, opcional
        Columnas a conservar. Si no se especifica, se usan DEFAULT_COLUMNS.

    Retorna
    -------
    pd.DataFrame
        DataFrame con columnas filtradas (solo las presentes).
    """
    cols = list(columns) if columns is not None else list(DEFAULT_COLUMNS)
    present = [c for c in cols if c in df.columns]
    return df[present].copy()


def flag_intentional(
    df: pd.DataFrame,
    causa_col: str = "idcausa",
    out_col: str = "intencionado",
    lower: int = 400,
    upper: int = 499,
) -> pd.DataFrame:
    """
    Crea la bandera de incendios intencionados en rango [lower, upper] según 'idcausa'.

    Si la columna 'idcausa' no existe, marca todo como False para mantener compatibilidad.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    causa_col : str
        Nombre de la columna que contiene el código de causa.
    out_col : str
        Nombre de la columna de salida para la bandera booleana.
    lower, upper : int
        Rango inclusivo que define "intencionado".

    Retorna
    -------
    pd.DataFrame
        DataFrame con la columna booleana `out_col`.
    """
    out = df.copy()
    if causa_col in out.columns:
        out[out_col] = out[causa_col].between(lower, upper, inclusive="both")
    else:
        out[out_col] = False
    return out


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ajusta tipos y valores nulos en columnas clave:
    - 'idpeligro': rellena NaN con -1 y castea a int
    - 'idprovincia': castea a int
    - 'perdidassuperficiales': si existe, asegura numérico (sin NaN para alias)

    Retorna
    -------
    pd.DataFrame
        DataFrame con tipos consistentes.
    """
    out = df.copy()

    if "idpeligro" in out.columns:
        # todo lo que no pueda convertirse (texto raro, vacíos) se vuelve NaN (float), 
        # luego rellena NaN con -1 y finalmente castea a int
        out["idpeligro"] = pd.to_numeric(out["idpeligro"], errors="coerce").fillna(-1).astype(int)

    if "idprovincia" in out.columns:
        out["idprovincia"] = pd.to_numeric(out["idprovincia"], errors="coerce").fillna(-1).astype(int)

    if "perdidassuperficiales" in out.columns:
        out["perdidassuperficiales"] = pd.to_numeric(out["perdidassuperficiales"], errors="coerce")

    # Medios: convertimos a numérico por si vienen como texto
    for col in ("numeromediospersonal", "numeromediospesados", "numeromediosaereos"):
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0)

    return out


def add_hectareas_alias(
    df: pd.DataFrame,
    source: str = "perdidassuperficiales",
    target: str = "hectareas_quemadas",
) -> pd.DataFrame:
    """
    Crea un alias semántico 'hectareas_quemadas' desde 'perdidassuperficiales'.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    source : str
        Columna origen (p. ej. 'perdidassuperficiales').
    target : str
        Nombre de la nueva columna alias.

    Retorna
    -------
    pd.DataFrame
        DataFrame con la columna alias añadida (0 si no existe source).
    """
    out = df.copy()
    if source in out.columns:
        out[target] = out[source].fillna(0)
    else:
        out[target] = 0
    return out


def prepare_wildfires(
    df_raw: pd.DataFrame,
    columns: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """
    Pipeline mínimo de preparación: seleccionar columnas, marcar intencionados,
    ajustar tipos y crear alias 'hectareas_quemadas'.

    Parámetros
    ----------
    df_raw : pd.DataFrame
        Datos crudos de incendios (CSV leído).
    columns : lista de str, opcional
        Columnas a conservar.

    Retorna
    -------
    pd.DataFrame
        DataFrame listo para agregaciones/visualizaciones.
    """
    df = select_columns(df_raw, columns=columns)
    df = flag_intentional(df)          # 'intencionado' True/False
    df = coerce_types(df)              # tipos consistentes
    df = add_hectareas_alias(df)       # alias semántico para gráficos
    return df
