# Spain Wildfires — Dashboard y Pipeline de Datos

**Dashboard interactivo** para analizar incendios forestales en España con **Streamlit, Folium y Plotly**.
Incluye un **pipeline de preparación** de datos y un **paquete Python** (`wildfires`) con utilidades reutilizables.

**Autores:** Lorena Elena Mohanu · José Ancízar Arbeláez Nieto
**Licencia del código:** MIT (ver [`LICENSE`](./LICENSE))

---

## ✨ Funcionalidades

* Mapa **coroplético por provincia** con recursos de extinción.
* Tendencia anual de **hectáreas quemadas**.
* Barras apiladas de **recursos** (personal, pesados, aéreos).
* Ranking **Top-N provincias** por área quemada.
* **Notebooks** separados para preparación de datos y análisis/visualización.
* **Paquete** `wildfires` con módulos para I/O, limpieza, geo, agregaciones y figuras.

---

## 📦 Requisitos

* **Python** 3.10+ recomendado
* Instalar dependencias:

  ```bash
  pip install -r requirements.txt
  ```

> Asegúrate de tener los datos ubicados en:
>
> * `data/raw/incendios.csv`
> * `data/raw/spain-provinces.geojson`

---

## 🚀 Cómo ejecutar el dashboard

```bash
streamlit run app/spain_wildfires_dashboard.py
```

Se abrirá en tu navegador (o verás la URL local en consola).

---

## 📓 Notebooks

Hay **dos cuadernos** que separan claramente preparación y análisis:

* `notebooks/01_data_preparation.ipynb`
  Prepara el dataset: selección de columnas, tipado, bandera `intencionado`, mapeo de provincias y exportación a Parquet.

* `notebooks/02_analysis_and_viz.ipynb`
  Carga el Parquet procesado y genera las visualizaciones (línea, barras apiladas y top provincias).

> Si prefieres trabajar con archivos `.py` (VSCode/Jupytext), encontrarás los equivalentes listos para convertir:
>
> * `notebooks/01_data_preparation.py`
> * `notebooks/02_analysis_and_viz.py`

Ejecuta los notebooks con Jupyter:

```bash
jupyter lab notebooks/
# o
jupyter notebook notebooks/
```

---

## 🧰 Paquete `wildfires`

El paquete vive en `src/wildfires` y expone una API limpia desde `__init__.py`.

**Ejemplo de uso rápido (notebook o script):**

```python
from wildfires import Incendios

ds = Incendios("data/raw/incendios.csv", "data/raw/spain-provinces.geojson")
df = ds.dataframe()

print("Rango de años:", ds.min_max_year())
df_mapa = ds.for_map()
df_hectareas_anio = ds.burned_area_by_year()
df_recursos_anio = ds.resources_by_year()
top10 = ds.top_provinces(10)
```

### Módulos principales

* `io.py` – lectura de CSV/GeoJSON y utilidades de escritura

  * `read_wildfires_csv`, `read_geojson`, `write_parquet`, `write_csv`
* `cleaning.py` – limpieza y preparación

  * `select_columns`, `flag_intentional`, `coerce_types`, `add_hectareas_alias`, `prepare_wildfires`
* `geo.py` – utilidades geográficas/GeoJSON

  * `build_provinces_map`, `map_province_names`, `enrich_geojson_with_dataframe`
* `aggregates.py` – agregaciones para mapa y gráficos

  * `add_total_resources`, `group_by_province_for_map`,
    `aggregate_burned_area_by_year`, `aggregate_resources_by_year`,
    `top_provinces_by_burned_area`
* `plots.py` – figuras Plotly listas para usar

  * `line_hectares_by_year`, `stacked_resources_by_year`, `horizontal_top_provinces`
* `incendios.py` – clase **fachada** que orquesta todo (carga → preparación → mapeo → agregados)

---

## 🗂️ Estructura del repositorio

```
spain-wildfires/
├─ app/
│  └─ spain_wildfires_dashboard.py
├─ data/
│  ├─ raw/
│  │  ├─ incendios.csv
│  │  └─ spain-provinces.geojson
│  ├─ interim/            # (opcional) salidas intermedias
│  └─ processed/
│     └─ incendios_clean.parquet
├─ notebooks/
│  ├─ 01_data_preparation.ipynb
│  └─02_analysis_and_viz.ipynb
├─ src/
│  └─ wildfires/
│     ├─ __init__.py
│     ├─ io.py
│     ├─ cleaning.py
│     ├─ geo.py
│     ├─ aggregates.py
│     ├─ plots.py
│     └─ incendios.py
├─ LICENSE
├─ README.md
├─ requirements.txt
└─ .gitignore
```

---

## 🧪 Desarrollo y reproducibilidad (opcional)

* **Exportar datos procesados** desde el notebook 1:

  ```python
  # genera data/processed/incendios_clean.parquet
  ```
* **Exportar agregados** desde el notebook 2 (descomentando):

  ```python
  # data/interim/hectareas_por_anio.csv
  # data/interim/recursos_por_anio.csv
  # data/interim/top_10_provincias.csv
  ```

Sugerencias “pro”:

* Añade `pre-commit` (black, isort, ruff) para formateo y lint.
* Usa `Makefile` con tareas `make data`, `make app`, `make notebooks`.
* Integra GitHub Actions para checks básicos (import del paquete, lint).

---

## 🖼️ Capturas (opcional)

Crea una carpeta `docs/` y añade imágenes para el README:

```
docs/
├─ screenshot-map.png
├─ screenshot-line.png
└─ screenshot-stacked.png
```

Y referencia aquí, por ejemplo:

```md
![Mapa de medios](docs/screenshot-map.png)
```

---

## 🔗 Datos y crédito

* **Fuente de datos**: “Wildfire Spain” (Kaggle).
  Verifica la **licencia y términos de uso del dataset** en su página.

  > Nota: La **licencia del código** (MIT) no implica la del **dataset**. Respeta siempre los términos del proveedor de datos.

---

## 🧑‍💻 Autores

* **Lorena Elena Mohanu** — [GitHub](#) · [LinkedIn](#)
* **José Ancízar Arbeláez Nieto** — [GitHub](#) · [LinkedIn](#)

*(Sustituye `#` por tus perfiles si quieres enlazarlos.)*

---

## 📄 Licencia

Este repositorio se distribuye bajo la licencia **MIT**.
Consulta el archivo [`LICENSE`](./LICENSE) para más detalles.