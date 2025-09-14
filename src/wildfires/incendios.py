"""
Incendios — Fachada de alto nivel para el dataset de incendios en España.

Orquesta la carga, preparación y enriquecimiento de datos (CSV + GeoJSON), y
expone métodos convenientes para obtener agregaciones típicas (por provincia,
por año, top de provincias, etc.), reutilizando los módulos del paquete.

Autores: Lorena Elena Mohanu · José Ancízar Arbeláez Nieto
Licencia: MIT — ver archivo LICENSE en la raíz del repositorio.
"""

from __future__ import annotations
from typing import Tuple, Optional

import pandas as pd

# Dependencias internas del paquete
from .io import read_wildfires_csv, read_geojson, write_parquet
from .cleaning import prepare_wildfires
from .geo import build_provinces_map, map_province_names
from .aggregates import (
    add_total_resources,
    group_by_province_for_map,
    aggregate_burned_area_by_year,
    aggregate_resources_by_year,
    top_provinces_by_burned_area,
)


class Incendios:
    """
    Gestor de datos de incendios forestales (carga, preparación y enriquecimiento).

    Atributos
    ---------
    df_raw : pd.DataFrame
        Datos crudos leídos del CSV.
    geojson : dict
        Objeto GeoJSON cargado (provincias).
    provinces_map : dict[int,str]
        Mapa {cod_prov -> nombre_provincia}.
    df : pd.DataFrame
        Datos preparados (columnas seleccionadas, tipos, alias y provincias mapeadas).
    years : list[int]
        Lista de años presentes en el dataset.
    min_year, max_year : Optional[int]
        Año mínimo y máximo (o None si el dataset está vacío).
    """

    def __init__(
        self,
        csv_path: str,
        geojson_path: str,
        *,
        csv_sep: str = ";",
        csv_encoding: Optional[str] = None,
    ) -> None:
        """
        Inicializa el dataset: lee CSV y GeoJSON, limpia y mapea provincias.

        Parámetros
        ----------
        csv_path : str
            Ruta al archivo CSV de incendios.
        geojson_path : str
            Ruta al archivo GeoJSON de provincias.
        csv_sep : str
            Separador del CSV (por defecto ';', como en tus datos originales).
        csv_encoding : str | None
            Codificación del CSV (por ejemplo 'utf-8' o 'latin-1').
        """
        # 1) Carga de datos (sale de tu pd.read_csv y json.load originales)
        self.df_raw = read_wildfires_csv(csv_path, sep=csv_sep, encoding=csv_encoding)
        self.geojson = read_geojson(geojson_path)

        # 2) Preparación (sale de tu selección de columnas, intencionado, tipos, alias)
        df_prepared = prepare_wildfires(self.df_raw)

        # 3) Provincias (sale de tu dict {cod_prov:name} + map a 'provincia')
        self.provinces_map = build_provinces_map(self.geojson)
        self.df = map_province_names(df_prepared, self.provinces_map)

        # 4) Rango de años (sale de tu min/max sobre 'anio')
        if "anio" in self.df.columns and not self.df.empty:
            self.years = sorted(self.df["anio"].dropna().astype(int).unique().tolist())
            self.min_year = int(self.years[0]) if self.years else None
            self.max_year = int(self.years[-1]) if self.years else None
        else:
            self.years = []
            self.min_year = None
            self.max_year = None

    # --------------------------- API de consulta --------------------------- #

    def min_max_year(self) -> Tuple[Optional[int], Optional[int]]:
        """Devuelve (mínimo año, máximo año)."""
        return self.min_year, self.max_year

    def dataframe(self) -> pd.DataFrame:
        """
        Devuelve el DataFrame preparado (inmutable por contrato de uso).
        Nota: si necesitas mutar, haz una copia externa: `df = ds.dataframe().copy()`.
        """
        return self.df

    # --------------------------- Agregaciones útiles --------------------------- #

    def for_map(self) -> pd.DataFrame:
        """
        Devuelve el DataFrame agregado por provincia con 'total_medios' y desgloses,
        listo para alimentar el choropleth.
        """
        return group_by_province_for_map(add_total_resources(self.df))

    def burned_area_by_year(self) -> pd.DataFrame:
        """
        Devuelve las hectáreas quemadas agregadas por año (usa alias 'hectareas_quemadas' si existe).
        """
        return aggregate_burned_area_by_year(self.df)

    def resources_by_year(self) -> pd.DataFrame:
        """
        Devuelve los recursos de extinción agregados por año (personal, pesados, aéreos).
        """
        return aggregate_resources_by_year(self.df)

    def top_provinces(self, n: int = 10) -> pd.DataFrame:
        """
        Devuelve el Top-N de provincias por hectáreas quemadas (agregado).
        """
        return top_provinces_by_burned_area(self.df, n=n)

    # --------------------------- Persistencia opcional --------------------------- #

    def to_parquet(self, path: str, **kwargs) -> None:
        """
        Guarda el DataFrame preparado en formato Parquet (útil para pipelines reproducibles).
        """
        write_parquet(self.df, path, **kwargs)


if __name__ == "__main__":
    # Ejemplo de uso rápido (puedes eliminar esta sección si prefieres un módulo sin ejecución directa).
    ds = Incendios("data/raw/incendios.csv", "data/raw/spain-provinces.geojson")
    print("Rango de años:", ds.min_max_year())
    print(ds.for_map().head())
    print(ds.resources_by_year().head())
    print(ds.top_provinces(5))
