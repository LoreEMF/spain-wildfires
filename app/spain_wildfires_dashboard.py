"""
-----------------------------------------------------------------------------------------------------
Dashboard de Incendios en España
-----------------------------------------------------------------------------------------------------
Este código implementa un dashboard interactivo utilizando Streamlit, Folium y Plotly,
para analizar y visualizar datos relacionados con los incendios forestales en España.
El dashboard permite explorar tendencias, distribución geográfica y el uso de recursos
para la extinción de incendios, ofreciendo insights clave para la gestión y planificación.

Autores:
    - Lorena Elena Mohanu
    - José Ancizar Arbeláez Nieto

Versión:
    2.2.0

Fecha:
    10 de diciembre de 2024

Lenguajes y Librerías Utilizadas:
    - Python 3.8+ (Creado con 3.12.6)
    - Streamlit: Framework para crear interfaces de usuario interactivas.
    - Folium: Biblioteca para generar mapas interactivos.
    - Plotly: Biblioteca para la visualización de datos avanzados.
    - Pandas: Manipulación y análisis de datos.
    - NumPy: Operaciones numéricas y cálculo eficiente.
    - JSON: Manipulación de datos GeoJSON.

Características del Código:
    - Mapa interactivo (Choropleth) que muestra los recursos utilizados en cada provincia.
    - Gráficos dinámicos para analizar tendencias anuales de hectáreas quemadas y recursos utilizados.
    - Funcionalidad de filtrado por año y tipo de causalidad de los incendios.
    - Panel lateral con controles intuitivos para personalizar la visualización de datos.
    - Expander para mostrar información adicional sobre el dashboard.

Licencia:
    MIT — ver archivo LICENSE en la raíz del repositorio.

Contacto:
    - lorena.mohanu@estudiante.uam.es
    - jose.arbelaez@estudiante.uam.es

Ejecutar código:
- streamlit run app/spain_wildfires_dashboard.py
-----------------------------------------------------------------------------------------------------
"""

from __future__ import annotations
from typing import Tuple

import streamlit as st
import folium
from streamlit_folium import st_folium

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

# Paquete interno (nuestro)
from wildfires import (
    Incendios,
    enrich_geojson_with_dataframe,
    add_total_resources,
    group_by_province_for_map,
    line_hectares_by_year,
    stacked_resources_by_year,
    horizontal_top_provinces,
)

# ----------------------------- Configuración de página ----------------------------- #
st.set_page_config(
    page_title="Spain Wildfires Dashboard",
    layout="wide",
    page_icon="🔥",
)
st.title("Incendios Forestales en España")
st.caption("Explora distribución geográfica, tendencias anuales y uso de recursos de extinción.")


# ----------------------------- Carga del dataset (cache) ----------------------------- #
@st.cache_data(show_spinner=True)
def load_dataset(csv_path: str, geojson_path: str) -> Incendios:
    """
    Carga y prepara el dataset a través de la fachada `Incendios`.
    """
    return Incendios(csv_path, geojson_path, csv_sep=";")

# Nuevas funciones añadidas para cachear y reducir la latencia
@st.cache_data(show_spinner=False)
def filter_by_year_and_intent_cached(df, year_range, show_intentional, show_non_intentional):
    y0, y1 = year_range
    mask_year = (df["anio"] >= y0) & (df["anio"] <= y1)
    if show_intentional and show_non_intentional:
        return df[mask_year]
    elif show_intentional:
        return df[mask_year & (df["intencionado"] == True)]
    else:
        return df[mask_year & (df["intencionado"] == False)]

@st.cache_data(show_spinner=False)
def map_aggregation_cached(df_filt):
    # add_total_resources() + group_by_province_for_map()
    from wildfires import add_total_resources, group_by_province_for_map
    return group_by_province_for_map(add_total_resources(df_filt))


@st.cache_data(show_spinner=False)
def enrich_geojson_cached(grouped_map_df, base_geojson):
    cols = ["provincia", "total_medios", "numeromediospersonal", "numeromediospesados", "numeromediosaereos"]
    from wildfires import enrich_geojson_with_dataframe
    return enrich_geojson_with_dataframe(
        grouped_map_df[cols],
        base_geojson,
        geo_name_field="name",
        df_key="provincia",
        columns=cols,
        deepcopy_geo=True,   # mantenemos copia para no mutar el original
    )

@st.cache_data(show_spinner=False)
def yearly_series_cached(df_filt):
    from wildfires import aggregate_burned_area_by_year, aggregate_resources_by_year
    return (
        aggregate_burned_area_by_year(df_filt),
        aggregate_resources_by_year(df_filt),
    )

# Ajusta estas rutas a tu estructura de repo
CSV_PATH = "data/raw/incendios.csv"
GEOJSON_PATH = "data/raw/spain-provinces.geojson"

ds = load_dataset(CSV_PATH, GEOJSON_PATH)
df = ds.dataframe()  # DataFrame preparado (limpieza + provincias mapeadas)


# ----------------------------- Filtros (sidebar) ----------------------------- #
st.sidebar.header("Filtros")

def filter_by_year_and_intent(
    df, year_range: Tuple[int, int], show_intentional: bool, show_non_intentional: bool
):
    """
    Filtra por rango de años e intención (intencionados/no intencionados).
    """
    y0, y1 = year_range
    mask_year = (df["anio"] >= y0) & (df["anio"] <= y1)

    if show_intentional and show_non_intentional:
        return df[mask_year]
    elif show_intentional:
        return df[mask_year & (df["intencionado"] == True)]
    else:
        return df[mask_year & (df["intencionado"] == False)]

# Rango de años
if ds.min_year is not None and ds.max_year is not None:
    default_end = min(ds.min_year + 10, ds.max_year)
    year_range = st.sidebar.slider(
        "Rango de años",
        min_value=int(ds.min_year),
        max_value=int(ds.max_year),
        value=(int(ds.min_year), int(default_end)),
        step=1,
    )
else:
    st.warning("No se detectaron años válidos en el dataset.")
    st.stop()

# Intencionado / No intencionado
show_intentional = st.sidebar.checkbox("Mostrar intencionados", value=True)
show_non_intentional = st.sidebar.checkbox("Mostrar no intencionados", value=True)

if not show_intentional and not show_non_intentional:
    st.warning("⚠️ Selecciona al menos un tipo de causalidad para visualizar datos.")
    st.stop()

df_filt = filter_by_year_and_intent_cached(df, year_range, show_intentional, show_non_intentional)


# ----------------------------- Mapa coroplético (Folium) ----------------------------- #
def create_choropleth(grouped_map_df, geojson):
    """
    Crea un mapa coroplético de 'total_medios' enriqueciendo el GeoJSON
    con las columnas del DataFrame agregado por provincia.
    """
    # Enriquecemos el GeoJSON con las columnas que usará el tooltip/popup
    cols = ["provincia", "total_medios", "numeromediospersonal", "numeromediospesados", "numeromediosaereos"]
    gj = enrich_geojson_cached(grouped_map_df, ds.geojson)

    m = folium.Map(location=[40.2, -3.7], zoom_start=5)

    folium.Choropleth(
        geo_data=gj,
        name="Medios usados en incendios",
        data=grouped_map_df,
        columns=["provincia", "total_medios"],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Total de Medios Utilizados",
    ).add_to(m)

    tooltip = folium.GeoJsonTooltip(
        fields=["name", "total_medios", "numeromediospersonal", "numeromediospesados", "numeromediosaereos"],
        aliases=["Provincia:", "Total de Medios:", "Personal:", "Medios Pesados:", "Medios Aéreos:"],
        localize=True,
        sticky=False,
        labels=True,
        style="background-color:#F7F7F7; border:1px solid #333; border-radius:3px; padding:6px;",
        max_width=600,
    )
    popup = folium.GeoJsonPopup(fields=["name"], aliases=["Provincia:"], max_width=400)

    folium.GeoJson(
        gj,
        style_function=lambda x: {
            "fillColor": "transparent" if x["properties"].get("total_medios") is None else "transparent",
            "color": "black",
            "fillOpacity": 0.7,
            "weight": 0.5,
        },
        tooltip=tooltip,
        popup=popup,
        name="Detalles",
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


# ----------------------------- Layout principal ----------------------------- #
col1, col2 = st.columns([3, 1], gap="large")

with col1:
    st.subheader("Mapa de medios utilizados")

    # Agregación para mapa a partir del DF filtrado
    df_map  = map_aggregation_cached(df_filt)
    mapa = create_choropleth(df_map, ds.geojson)
    st_folium(mapa, height=600, use_container_width=True)

    st.subheader("Tendencias de hectáreas quemadas")
    st.plotly_chart(line_hectares_by_year(df_filt), use_container_width=True)

    st.subheader("Recursos utilizados por año")
    rename_map = {
        "numeromediospersonal": "Personal",
        "numeromediospesados": "Pesados",
        "numeromediosaereos": "Aéreos",
    }
    st.plotly_chart(
        stacked_resources_by_year(df_filt, rename_map=rename_map),
        use_container_width=True,
    )

with col2:
    st.subheader("Ranking (Top 10)")
    st.plotly_chart(horizontal_top_provinces(df_filt, n=10), use_container_width=True)

    st.subheader("Acerca del dashboard")
    st.markdown(
        """
        Este dashboard analiza los incendios forestales en España, mostrando patrones
        espaciales y temporales y el uso de recursos de extinción.
        """
    )
    st.markdown("**Integrantes:** Lorena Elena Mohanu · José Ancízar Arbeláez Nieto")
    st.markdown(
        "[Fuente de datos (Kaggle): Wildfire Spain](https://www.kaggle.com/datasets/patrilc/wildfirespain)",
        unsafe_allow_html=True,
    )
