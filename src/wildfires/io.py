"""
Módulo de Entrada/Salida (I/O) para el proyecto Spain Wildfires.

Proporciona funciones para leer el CSV de incendios y el GeoJSON de provincias.

Autores: Lorena Elena Mohanu · José Ancízar Arbeláez Nieto
Licencia: MIT — ver archivo LICENSE en la raíz del repositorio.
"""

from __future__ import annotations

import json
from typing import Any, Dict

import pandas as pd


def read_wildfires_csv(path: str, sep: str = ";", encoding: str | None = None, **read_csv_kwargs) -> pd.DataFrame:
    """
    Lee el archivo CSV de incendios y devuelve un DataFrame.

    Parámetros
    ----------
    path : str
        Ruta al archivo CSV de incendios (por ejemplo, 'data/raw/incendios.csv').
    sep : str
        Separador de columnas en el CSV. Por defecto ';' (como los datos originales de incendios).
    encoding : str | None
        Codificación del archivo. Déjalo en None si no es necesario; usa 'utf-8' o 'latin-1' si procede.
    **read_csv_kwargs
        Parámetros adicionales que se pasan a `pandas.read_csv` (por ejemplo, dtype=...).

    Retorna
    -------
    pd.DataFrame
        DataFrame con los datos crudos de incendios.
    """
    df = pd.read_csv(path, sep=sep, encoding=encoding, **read_csv_kwargs)
    return df


def read_geojson(path: str, encoding: str = "utf8") -> Dict[str, Any]:
    """
    Lee un archivo GeoJSON (provincias de España) y devuelve el objeto dict.

    Parámetros
    ----------
    path : str
        Ruta al archivo GeoJSON (por ejemplo, 'data/raw/spain-provinces.geojson').
    encoding : str
        Codificación usada al abrir el archivo. Por defecto 'utf8'.

    Retorna
    -------
    dict
        Objeto Python (dict) con el contenido del GeoJSON.
    """
    with open(path, "r", encoding=encoding) as f:
        data = json.load(f)
    return data

def write_parquet(df: pd.DataFrame, path: str, **to_parquet_kwargs) -> None:
    """
    Guarda un DataFrame en formato Parquet.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame a guardar.
    path : str
        Ruta de salida (por ejemplo, 'data/processed/incendios_clean.parquet').
    **to_parquet_kwargs
        Parámetros adicionales que se pasan a `DataFrame.to_parquet`.

    Comentario
    ----------
    Parquet es eficiente en espacio y lectura rápida; útil para flujos reproducibles
    (notebooks, dashboard).
    """
    df.to_parquet(path, index=False, **to_parquet_kwargs)


def write_csv(df: pd.DataFrame, path: str, sep: str = ",", index: bool = False, encoding: str = "utf-8", **to_csv_kwargs) -> None:
    """
    Guarda un DataFrame en CSV.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame a guardar.
    path : str
        Ruta de salida (por ejemplo, 'data/interim/incendios_clean.csv').
    sep : str
        Separador a usar (por defecto ',').
    index : bool
        Si se guardan los índices del DataFrame (por defecto False).
    encoding : str
        Codificación del archivo (por defecto 'utf-8').
    **to_csv_kwargs
        Parámetros adicionales que se pasan a `DataFrame.to_csv`.
    """
    df.to_csv(path, sep=sep, index=index, encoding=encoding, **to_csv_kwargs)
