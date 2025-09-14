"""
Utilidades geográficas para el proyecto Spain Wildfires.

Incluye funciones para:
- Construir el mapa {cod_prov -> nombre} a partir de un GeoJSON.
- Mapear 'idprovincia' -> 'provincia' en un DataFrame.
- Enriquecer un GeoJSON con columnas procedentes de un DataFrame (para choropleth).

Autores: Lorena Elena Mohanu · José Ancízar Arbeláez Nieto
Licencia: MIT — ver archivo LICENSE en la raíz del repositorio.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Dict, Sequence, Any, Optional

import numpy as np
import pandas as pd


# --------------------------- Helpers internos --------------------------- #

def _to_jsonable(value: Any) -> Any:
    """
    Convierte valores de NumPy/NaN a tipos nativos JSON-serializables.

    - np.integer -> int
    - np.floating -> float
    - NaN -> None
    - Resto -> tal cual
    """
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


# --------------------------- API pública --------------------------- #

def build_provinces_map(
    geojson: Dict[str, Any],
    code_key: str = "cod_prov",
    name_key: str = "name",
) -> Dict[int, str]:
    """
    Construye un diccionario {código_provincia -> nombre} a partir de un GeoJSON.

    Parámetros
    ----------
    geojson : dict
        Objeto GeoJSON con features de provincias (properties[code_key], properties[name_key]).
    code_key : str
        Nombre de la clave en properties que contiene el código de provincia.
    name_key : str
        Nombre de la clave en properties que contiene el nombre de provincia.

    Retorna
    -------
    dict[int, str]
        Mapa de códigos a nombres de provincia.
    """
    return {
        int(feat["properties"][code_key]): feat["properties"][name_key]
        for feat in geojson.get("features", [])
        if code_key in feat.get("properties", {}) and name_key in feat.get("properties", {})
    }


def map_province_names(
    df: pd.DataFrame,
    provinces_map: Dict[int, str],
    id_col: str = "idprovincia",
    name_col: str = "provincia",
) -> pd.DataFrame:
    """
    Mapea el identificador de provincia del DataFrame al nombre de provincia usando un diccionario.

    Parámetros
    ----------
    df : pd.DataFrame
        Datos de incendios con columna de id de provincia.
    provinces_map : dict[int, str]
        Diccionario {id -> nombre} generado con build_provinces_map.
    id_col : str
        Nombre de la columna con el identificador de provincia (por defecto 'idprovincia').
    name_col : str
        Nombre de la columna destino para el nombre de provincia (por defecto 'provincia').

    Retorna
    -------
    pd.DataFrame
        Copia del DataFrame con la columna `name_col` mapeada (si `id_col` existe).
    """
    out = df.copy()
    if id_col in out.columns:
        # Convertimos a entero por seguridad antes de mapear
        out[id_col] = pd.to_numeric(out[id_col], errors="coerce").astype("Int64").fillna(-1).astype(int)
        out[name_col] = out[id_col].map(provinces_map).fillna(out.get(name_col))
    return out


def enrich_geojson_with_dataframe(
    df: pd.DataFrame,
    geojson: Dict[str, Any],
    geo_name_field: str = "name",
    df_key: str = "provincia",
    columns: Optional[Sequence[str]] = None,
    deepcopy_geo: bool = True,
) -> Dict[str, Any]:
    """
    Enriquecimiento de GeoJSON con columnas provenientes de un DataFrame.

    Para cada feature del GeoJSON (properties[geo_name_field]) busca la fila df[df_key == name]
    y añade al properties todas o un subconjunto de columnas del DataFrame (según `columns`).

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame con al menos la columna `df_key` que coincida con `geo_name_field` del GeoJSON.
    geojson : dict
        Objeto GeoJSON original.
    geo_name_field : str
        Campo en properties del GeoJSON que contiene el nombre de la provincia (por defecto 'name').
    df_key : str
        Columna del DataFrame que debe coincidir con el nombre de la provincia (por defecto 'provincia').
    columns : lista de str, opcional
        Si se especifica, solo se copian estas columnas; si no, se copian todas.
    deepcopy_geo : bool
        Si True, no se muta el GeoJSON original (se hace deepcopy). Recomendado.

    Retorna
    -------
    dict
        GeoJSON enriquecido con propiedades adicionales para cada provincia.

    Notas
    -----
    - Se usan tipos nativos para asegurar compatibilidad JSON (int/float/None).
    - Si una provincia del GeoJSON no aparece en el DataFrame, se rellenan propiedades como None.
    """
    gj = deepcopy(geojson) if deepcopy_geo else geojson

    # Elegimos columnas a copiar (todas salvo la clave, si no se especifica)
    if columns is None:
        cols_to_copy = [c for c in df.columns if c != df_key]
    else:
        cols_to_copy = [c for c in columns if c in df.columns and c != df_key]

    # Preparamos un lookup para acceso O(1)
    lookup = df.set_index(df_key)[cols_to_copy] if cols_to_copy else df.set_index(df_key)

    for feature in gj.get("features", []):
        props = feature.setdefault("properties", {})
        key = props.get(geo_name_field)
        if key in lookup.index:
            row = lookup.loc[key]
            # row puede ser Series; iteramos columnas y valores
            for col in cols_to_copy:
                props[col] = _to_jsonable(row[col])
        else:
            # Si no hay coincidencia, rellenamos con None para todas las columnas copiadas
            for col in cols_to_copy:
                props[col] = None

    return gj
