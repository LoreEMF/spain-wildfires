"""
Figuras Plotly para el proyecto Spain Wildfires.

Incluye:
- Línea temporal de hectáreas quemadas por año.
- Barras apiladas de recursos por año.
- Barras horizontales Top-N por provincia.

Autores: Lorena Elena Mohanu · José Ancízar Arbeláez Nieto
Licencia: MIT — ver archivo LICENSE en la raíz del repositorio.
"""

from __future__ import annotations
from typing import Iterable, Mapping, Optional, Sequence

import pandas as pd
import plotly.graph_objects as go


def line_hectares_by_year(
    df: pd.DataFrame,
    year_col: str = "anio",
    area_col: str = "hectareas_quemadas",
    fallback_area_col: str = "perdidassuperficiales",
    title: Optional[str] = None,
) -> go.Figure:
    """
    Crea una figura de línea con las hectáreas quemadas agregadas por año.

    Parámetros
    ----------
    df : pd.DataFrame
        Datos con columnas de año y área quemada.
    year_col : str
        Nombre de la columna que contiene el año.
    area_col : str
        Columna preferida (alias) para el área quemada ('hectareas_quemadas').
    fallback_area_col : str
        Columna a usar si no existe `area_col` (por compatibilidad).
    title : str, opcional
        Título de la figura.

    Retorna
    -------
    go.Figure
        Figura de líneas lista para usarse en Streamlit o notebooks.
    """
    col = area_col if area_col in df.columns else fallback_area_col
    if col not in df.columns:
        raise KeyError(f"No se encontró columna de área quemada: {area_col} ni {fallback_area_col}")

    serie = df.groupby(year_col)[col].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=serie[year_col],
            y=serie[col],
            mode="lines+markers",
            name="Hectáreas quemadas",
            hovertemplate="%{y:,.0f} ha<extra></extra>",
        )
    )
    fig.update_layout(
        title=title or "Hectáreas quemadas por año (España)",
        xaxis_title="Año",
        yaxis_title="Hectáreas",
        margin=dict(t=60, l=10, r=10, b=10),
    )
    # Formato de ticks con separador de miles
    fig.update_yaxes(tickformat=",.0f")
    return fig


def stacked_resources_by_year(
    df: pd.DataFrame,
    year_col: str = "anio",
    resource_cols: Sequence[str] = ("numeromediospersonal", "numeromediospesados", "numeromediosaereos"),
    rename_map: Optional[Mapping[str, str]] = None,
    title: Optional[str] = None,
) -> go.Figure:
    """
    Crea barras apiladas con los recursos utilizados por año.

    Parámetros
    ----------
    df : pd.DataFrame
        Datos con columna de año y columnas de recursos.
    year_col : str
        Nombre de la columna que contiene el año.
    resource_cols : lista/tupla de str
        Columnas de recursos a apilar.
    rename_map : dict[str,str], opcional
        Mapa para renombrar etiquetas de leyenda (p. ej. {'numeromediospersonal':'Personal'}).
    title : str, opcional
        Título de la figura.

    Retorna
    -------
    go.Figure
        Figura de barras apiladas.
    """
    missing = [c for c in resource_cols if c not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas de recursos: {missing}")

    grp = df.groupby(year_col)[list(resource_cols)].sum().reset_index()

    fig = go.Figure()
    for col in resource_cols:
        name = rename_map.get(col, col) if rename_map else col
        fig.add_trace(
            go.Bar(
                x=grp[year_col],
                y=grp[col],
                name=name,
                hovertemplate="%{y:,.0f}<extra></extra>",
            )
        )
    fig.update_layout(
        title=title or "Recursos utilizados por año",
        barmode="stack",
        xaxis_title="Año",
        yaxis_title="Cantidad de recursos",
        margin=dict(t=60, l=10, r=10, b=10),
    )
    fig.update_yaxes(tickformat=",.0f")
    return fig


def horizontal_top_provinces(
    df: pd.DataFrame,
    n: int = 10,
    province_col: str = "provincia",
    area_col: str = "hectareas_quemadas",
    fallback_area_col: str = "perdidassuperficiales",
    title: Optional[str] = None,
) -> go.Figure:
    """
    Crea barras horizontales con el Top-N de provincias por hectáreas quemadas (agregado).

    Lógica de orden:
    1) Se calcula el Top-N en orden descendente (provincias con mayor área).
    2) Luego se ordena ascendente para que la barra más larga quede abajo (lectura natural).

    Parámetros
    ----------
    df : pd.DataFrame
        Datos con provincia y área quemada.
    n : int
        Número de provincias a mostrar (por defecto 10).
    province_col : str
        Columna con el nombre de la provincia.
    area_col : str
        Columna preferida (alias) para área quemada.
    fallback_area_col : str
        Columna a usar si no existe `area_col`.
    title : str, opcional
        Título de la figura.

    Retorna
    -------
    go.Figure
        Figura de barras horizontales.
    """
    col = area_col if area_col in df.columns else fallback_area_col
    if col not in df.columns:
        raise KeyError(f"No se encontró columna de área quemada: {area_col} ni {fallback_area_col}")

    agg = df.groupby(province_col)[col].sum().reset_index(name="hectareas_quemadas")
    top = agg.sort_values("hectareas_quemadas", ascending=False).head(n)
    top = top.sort_values("hectareas_quemadas", ascending=True)

    fig = go.Figure(
        data=[
            go.Bar(
                x=top["hectareas_quemadas"],
                y=top[province_col],
                orientation="h",
                name="Hectáreas",
                hovertemplate="%{x:,.0f} ha<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=title or f"Top {n} provincias por hectáreas quemadas",
        xaxis_title="Hectáreas",
        yaxis_title="Provincia",
        margin=dict(t=60, l=10, r=10, b=10),
    )
    fig.update_xaxes(tickformat=",.0f")
    return fig
