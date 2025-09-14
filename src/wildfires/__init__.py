"""
Paquete `wildfires` — utilidades para el proyecto Spain Wildfires.

Este paquete expone una API pública estable para cargar, limpiar, enriquecer y
visualizar datos de incendios forestales en España. Los nombres de las funciones
están en inglés; la documentación y los comentarios en español.

Autores: Lorena Elena Mohanu · José Ancízar Arbeláez Nieto
Licencia: MIT — ver archivo LICENSE en la raíz del repositorio.
"""

from __future__ import annotations

# -------------------- Fachada de alto nivel --------------------
from .incendios import Incendios

# -------------------- Entrada/Salida (I/O) ---------------------
from .io import (
    read_wildfires_csv,
    read_geojson,
    write_parquet,
    write_csv,
)

# -------------------- Limpieza/Preparación ---------------------
from .cleaning import (
    select_columns,
    flag_intentional,
    coerce_types,
    add_hectareas_alias,
    prepare_wildfires,
)

# -------------------- Geografía/GeoJSON ------------------------
from .geo import (
    build_provinces_map,
    map_province_names,
    enrich_geojson_with_dataframe,
)

# -------------------- Agregaciones -----------------------------
from .aggregates import (
    add_total_resources,
    group_by_province_for_map,
    aggregate_burned_area_by_year,
    aggregate_resources_by_year,
    top_provinces_by_burned_area,
)

# -------------------- Gráficos (Plotly) ------------------------
from .plots import (
    line_hectares_by_year,
    stacked_resources_by_year,
    horizontal_top_provinces,
)

# Versión del paquete (útil para reproducibilidad en notebooks/README)
__version__ = "0.1.0"

# Límite explícito de la API pública; ayuda a autocompletado y claridad
__all__ = [
    # Fachada
    "Incendios",
    # I/O
    "read_wildfires_csv",
    "read_geojson",
    "write_parquet",
    "write_csv",
    # Cleaning
    "select_columns",
    "flag_intentional",
    "coerce_types",
    "add_hectareas_alias",
    "prepare_wildfires",
    # Geo
    "build_provinces_map",
    "map_province_names",
    "enrich_geojson_with_dataframe",
    # Aggregates
    "add_total_resources",
    "group_by_province_for_map",
    "aggregate_burned_area_by_year",
    "aggregate_resources_by_year",
    "top_provinces_by_burned_area",
    # Plots
    "line_hectares_by_year",
    "stacked_resources_by_year",
    "horizontal_top_provinces",
    # Meta
    "__version__",
]
