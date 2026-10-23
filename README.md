<div align="center">

<img src="https://geophilo.com/assets/sdk_icons/multilayer_sdk.svg" width="128" height="128" alt="multilayer-sdk Logo" style="filter: drop-shadow(0 12px 24px rgba(16,185,129,0.3));"/>

# multilayer-sdk

**Pure-Python Synchronized Multi-Panel Map Visualization, Spatial Comparison Engine & Interactive Dashboard Builder.**

[![PyPI Version](https://img.shields.io/pypi/v/multilayer-sdk.svg?color=10b981&label=PyPI%20package)](https://pypi.org/project/multilayer-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/multilayer-sdk.svg?color=06b6d4)](https://pypi.org/project/multilayer-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

[![Documentation](https://img.shields.io/badge/docs-GEOPHILO-10b981.svg)](https://geophilo.com/multilayer-sdk/)

<br/>

<img src="https://geophilo.com/assets/sdk_icons/multilayer_sdk.svg" width="100%" alt="multilayer-sdk Architecture"/>

</div>

---

## 🌐 Live Interactive Studio & Documentation

Explore the **interactive multi-panel map simulator** and comprehensive reference manual:

👉 **[https://geophilo.com/multilayer-sdk/](https://geophilo.com/multilayer-sdk/)**

Try out real-time neon laser crosshair tracking, split-screen curtain swipe comparisons, and live choropleth classifiers directly in your browser.

---

## 🌟 Overview

**multilayer-sdk** (the headless Python core behind **02Multimap**) allows urban planners, spatial data scientists, and researchers to visualize, cross-analyze, and compare multiple spatial datasets side-by-side with millisecond synchronization.

Instead of toggling layers on and off in a single map, `multilayer` coordinates up to 8 synchronized map viewports in dynamic grids (1x2, 2x1, 1x3, 2x2, 2x3, 2x4) and exports a single self-contained HTML file for each visualization.

### ✨ Features

- **Synchronized multi-panel grids** — 2, 3, 4, 6, or 8 coordinated Leaflet viewports.
- **Bi-directional pan & zoom broadcasting** — drag or zoom any panel to move all others.
- **Neon laser crosshair tracking** — project the cursor's geographic coordinate across every panel.
- **Thematic choropleths** — quantiles, equal interval, natural breaks, standard deviation, and categorical classification.
- **Scientific color ramps** — `viridis`, `magma`, `plasma`, `inferno`, `turbo`, `cividis`, `blues`, `reds`, `greens`, `spectral`, `rdylbu`, `ylorrd`, and `pubu`.
- **Before/after comparison tools** — draggable curtain swipe, roller curtain, spyglass magnifier, diff map, and 2x2 quad sync.
- **Temporal storytelling** — animated timeline player, range-slider time series, and scroll-driven story maps.
- **Interactive dashboards** — cross-filtering sidebar widgets and live KPI metric cards.
- **Advanced spatial visualizers** — 3D globe/terrain, 3D extruded prisms, bivariate choropleths, hexbin aggregation, curved flow arcs, particle/wind fields, isochrones, hypsometric relief, proximity heatmaps, and radar POI beacons.
- **Layer & basemap subsystem** — GeoJSON, GeoDataFrame, dict, raster overlays, built-in tile providers, and custom XYZ templates.
- **Zero-JavaScript build step** — every map compiles to a single offline-capable HTML document.
- **Jupyter & Google Colab ready** — rich inline widget display via `mm.show()` / `_repr_html_()`.
- **Command line interface** — `build`, `compare`, `inspect`, and `tiles` subcommands.
- **Fully typed** — ships a `py.typed` marker and modern `X | None` annotations.

---

## 🚀 Installation

### From PyPI (recommended)

```bash
pip install multilayer-sdk
```

The core package is dependency-free and targets **Python 3.9+**.

### Optional geospatial extras

The `geo` extra adds GeoPandas, Shapely, and Matplotlib for GeoDataFrame interop and notebook workflows:

```bash
pip install "multilayer-sdk[geo]"
```

### Development install

Install the package in editable mode together with the test, lint, and packaging toolchain:

```bash
git clone https://gitlab.com/geospacephilo/multilayer-sdk.git
cd multilayer-sdk
python -m pip install -e ".[dev]"
```

The `dev` extra installs `pytest`, `pytest-cov`, `ruff`, `mypy`, `build`, and `twine`.

### Verify the installation

```bash
python -c "import multilayer as ml; print(ml.__version__)"
```

---

## ⚡ Quickstart

### 1. Build a 4-Panel Synchronized Workspace

```python
import multilayer as ml

# 1. Initialize a 4-panel (2x2) synchronized map grid
mm = ml.MultiMap(grid="2x2", title="Urban Vulnerability & Land Use Assessment", basemap="carto-dark")

# 2. Panel 1: High-resolution satellite imagery with study area boundary
mm.panel(0).title = "1. Satellite Context"
mm.panel(0).set_basemap("satellite")
mm.panel(0).add_layer("study_area.geojson", stroke_color="#38bdf8", fill_opacity=0.2)

# 3. Panel 2: Thematic choropleth of population density
vlayer = ml.VectorLayer.from_geojson("demographics.geojson")
pop_choro = ml.Choropleth.classify(vlayer, property_name="density_km2", method="quantiles", color_ramp="viridis")
mm.panel(1).title = "2. Population Density"
mm.panel(1).add_layer(pop_choro)

# 4. Panel 3: Flood hazard exposure score
risk_choro = ml.Choropleth.classify(vlayer, property_name="flood_risk_score", method="equal_interval", color_ramp="magma")
mm.panel(2).title = "3. Flood Hazard Exposure"
mm.panel(2).add_layer(risk_choro)

# 5. Panel 4: Future 2030 Master Zoning Plan
mm.panel(3).title = "4. Future Master Plan 2030"
mm.panel(3).add_layer("zoning_plan.geojson", fill_color="#10b981", fill_opacity=0.6)

# 6. Save as standalone interactive HTML dashboard
mm.to_html("urban_assessment_dashboard.html")

# 7. Render inline in Jupyter Notebook / Google Colab
mm.show()
```

### 2. Draggable Split-Screen Curtain Swipe Comparison

```python
import multilayer as ml

swipe = ml.SwipeMap(
    left_layer="landcover_2010.geojson",
    right_layer="landcover_2026.geojson",
    left_title="Historical (2010)",
    right_title="Current (2026)",
    basemap="satellite",
)

swipe.to_html("deforestation_swipe.html")
```

### 3. Thematic Choropleth from an In-Memory FeatureCollection

```python
import multilayer as ml

zones = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [28.9784, 41.0082]},
            "properties": {"name": "Historic Peninsula", "density_km2": 12500},
        }
    ],
}

layer = ml.VectorLayer.from_geojson(zones, name="Districts")
choro = ml.Choropleth.classify(
    layer,
    property_name="density_km2",
    method=ml.ClassificationMethod.QUANTILES,
    num_classes=5,
    color_ramp=ml.ColorRamp.VIRIDIS,
)
choro.to_dict()  # JSON-serializable layer payload
```

### 4. Animated Time-Series Timeline

```python
import multilayer as ml

timeline = ml.TimelineMap(grid="1x2", title="Flood Progression", fps=1.5)
timeline.set_panel_title(0, "Observed")
timeline.set_panel_title(1, "Modelled")

frame = timeline.create_frame(label="T+0h", timestamp="2026-08-30 12:00")
frame.add_layer(0, ml.VectorLayer.from_geojson("observed.geojson"))
frame.add_layer(1, ml.VectorLayer.from_geojson("modelled.geojson"))

timeline.to_html("flood_timeline.html")
```

### 5. Cross-Filtering KPI Dashboard

```python
import multilayer as ml

dash = ml.InteractiveDashboard(grid="1x2", title="Resilience Dashboard", basemap="carto-dark")
dash.add_layer(0, ml.VectorLayer.from_geojson("districts.geojson"))
dash.add_layer(1, ml.VectorLayer.from_geojson("districts.geojson"))

dash.add_metric_card(
    title="Total Population",
    property_key="population",
    aggregation="sum",
    unit="people",
    icon="👥",
)
dash.add_filter(property_key="population", label="Minimum population", filter_type="range")

dash.to_html("resilience_dashboard.html")
```

### 6. Hexagonal Point Aggregation

```python
import multilayer as ml

points = [(41.008, 28.978), (41.009, 28.979), (41.050, 29.020)]
values = [12.0, 8.0, 25.0]

hex_layer = ml.aggregate_points_to_hexbins(
    points,
    point_values=values,
    hex_radius_m=750.0,
    statistic="MEAN",  # COUNT, MEAN, SUM, or MAX
)
hex_geojson = hex_layer.to_geojson()
```

### 7. 3D Extruded Prism Map

```python
import multilayer as ml

prisms = ml.Choropleth3DMap(title="Urban Density Prisms", metric_name="Density (hab/ha)")
prisms.add_prism(
    "Kadikoy",
    [(40.99, 29.02), (41.00, 29.02), (41.00, 29.04), (40.99, 29.04)],
    metric_value=450.0,
    height_scale=0.5,
)
prisms.save_html("density_prisms_3d.html")
```

### 8. Scroll-Driven Story Map

```python
import multilayer as ml

story = ml.StoryMapScroller(story_title="Istanbul 2030", subtitle="A spatial journey")
story.add_chapter("ch1", "Historic Core", "The historic peninsula.", 41.008, 28.978, zoom=15)
story.add_chapter("ch2", "Financial District", "Rapid corridor growth.", 41.080, 29.010, zoom=14)
story.save_html("storymap.html")
```

### 9. Custom XYZ Tile Provider

```python
import multilayer as ml

custom_tiles = ml.get_tile_provider("https://tiles.example.com/{z}/{x}/{y}.png")
panel_basemap = ml.TileLayer(name="Example Tiles", url_template=custom_tiles.url_template)
```

---

## 💻 Command Line Interface (CLI)

```bash
# 1. Build a 2x2 synchronized dashboard from 4 GeoJSON files
multilayer build --layers bldgs.geojson,roads.geojson,hazard.geojson,zoning.geojson --grid 2x2 --out city_dashboard.html --open

# 2. Build a 2-panel before/after split-screen swipe comparison
multilayer compare flood_2020.geojson flood_2026.geojson --left-title "2020 Flood" --right-title "2026 Flood" --out flood_swipe.html

# 3. Inspect GeoJSON feature count, properties, and bounding box
multilayer inspect study_area.geojson

# 4. List all built-in web map tile basemaps
multilayer tiles

# 5. Show the installed version
multilayer --version
```

---

## ⚙️ Supported Grid Matrices

| Grid Preset | Layout Dimensions | Panel Count | Primary Cartographic Use Case |
| :--- | :--- | :--- | :--- |
| **`1x2`** | 1 Row $\times$ 2 Columns | 2 Panels | Before/After comparisons, Suitability vs Actual zoning |
| **`2x1`** | 2 Rows $\times$ 1 Column | 2 Panels | Vertical elevation profiles, transport corridors |
| **`1x3`** | 1 Row $\times$ 3 Columns | 3 Panels | Past $\rightarrow$ Present $\rightarrow$ Future temporal timelines |
| **`2x2`** | 2 Rows $\times$ 2 Columns | 4 Panels | 4-way evaluation (Base, Demographics, Hazards, Policy) |
| **`2x3`** | 2 Rows $\times$ 3 Columns | 6 Panels | Multi-criteria evaluation (MCDA factor grids) |
| **`2x4`** | 2 Rows $\times$ 4 Columns | 8 Panels | High-density multi-scenario sensitivity snapshots |

Custom grids can also be supplied as any `"RxC"` string or via `GridLayout(custom_rows=..., custom_cols=...)`.

---

## 📚 Public API Reference

All symbols below are importable directly from `multilayer`.

### Core containers

| Symbol | Kind | Purpose |
| :--- | :--- | :--- |
| `MultiMap` | class | Synchronized multi-panel workspace; configure panels, layers, basemaps, and export HTML. |
| `Panel` | class | A single viewport inside a `MultiMap` grid. |
| `SwipeMap` | class | Split-screen curtain swipe comparison of two layers. |
| `create_multimap` | function | Convenience factory that creates a `MultiMap` and assigns layers to panels. |
| `GridLayout` / `GridPreset` | class / enum | Grid geometry parsing, presets, and CSS generation. |

### Layers & basemaps

| Symbol | Kind | Purpose |
| :--- | :--- | :--- |
| `Layer` | abstract class | Base spatial layer contract (`to_dict`, `get_bounds`). |
| `VectorLayer` | class | GeoJSON / dict / GeoDataFrame vector layer with styling and tooltips. |
| `RasterLayer` | class | Georeferenced raster image overlay. |
| `TileLayer` | class | Web-map raster tile basemap. |
| `TileProvider` | enum | Built-in providers (OSM, CARTO, Esri, OpenTopoMap, CyclOSM). |
| `get_tile_provider` | function | Resolve a provider alias or custom XYZ URL to a `TileLayer`. |

### Thematic symbology

| Symbol | Kind | Purpose |
| :--- | :--- | :--- |
| `Choropleth` | class | Classify vector features and produce a themed `VectorLayer`. |
| `ClassificationMethod` | enum | `QUANTILES`, `EQUAL_INTERVAL`, `NATURAL_BREAKS`, `STANDARD_DEVIATION`, `CATEGORICAL`. |
| `ColorRamp` | enum | Scientific and cartographic color palettes. |
| `StyleRule` / `GraduatedStyle` / `CategoricalStyle` | dataclasses | Declarative styling rules and graduation configuration. |
| `BivariateChoroplethMap` / `BivariateMatrixColorRamp` | class / dataclass | 3x3 bivariate correlation choropleth. |

### Temporal & dashboard

| Symbol | Kind | Purpose |
| :--- | :--- | :--- |
| `TimelineMap` / `TimeFrame` | class / dataclass | Multi-panel time-series animator and scenario player. |
| `TemporalRangeSliderMap` / `TimeSliderFrame` | class / dataclass | Range-slider time-series playback map. |
| `export_time_slider_html` | function | Build and save a `TemporalRangeSliderMap` from `(label, geojson)` pairs. |
| `InteractiveDashboard` / `MetricCard` / `FilterWidget` | classes | Cross-filtering dashboard with KPI cards. |

### Comparison & 3D

| Symbol | Kind | Purpose |
| :--- | :--- | :--- |
| `DiffMap` / `SpatialDiffResult` | class / dataclass | Side-by-side geometric difference visualizer. |
| `CurtainMap` | class | Split-slider curtain reveal comparer. |
| `RollerCurtainMap` / `RollerAngleMode` / `render_roller_map_html` | class / enum / function | Angle-adjustable roller curtain comparer. |
| `SpyglassCompareMap` / `LensConfig` | class / dataclass | Circular magnifying-lens comparer. |
| `QuadSyncMap` / `QuadPanelConfig` | class / dataclass | 4-panel synchronized 2x2 map grid. |
| `Globe3DMap` / `TerrainPanel3D` | class / dataclass | Multi-panel 3D globe and terrain viewer. |
| `Choropleth3DMap` / `PrismPolygon3D` | class / dataclass | 3D extruded prism choropleth. |
| `CurvedFlowMap` / `FlowArc3D` | class / dataclass | Curved animated origin-destination flow arcs. |

### Advanced spatial visualizers

| Symbol | Kind | Purpose |
| :--- | :--- | :--- |
| `HexbinHeatmapLayer` / `HexagonCell` / `aggregate_points_to_hexbins` | classes / function | Hexagonal point aggregation with COUNT/MEAN/SUM/MAX. |
| `ParticleFlowMap` / `FlowParticleConfig` | class / dataclass | Canvas/WebGL particle flow animation. |
| `WindParticleFieldMap` / `WindParticleParams` | class / dataclass | Vector wind/current streamline field. |
| `TravelIsochroneBubbleMap` / `IsochroneBandParams` | class / dataclass | Multi-modal travel-time reachability rings. |
| `HypsoTintedReliefMap` / `ContourIntervalConfig` | class / dataclass | Hypsometric relief with contour lines. |
| `ProximityMatrixHeatmapMap` / `ProximityZoneParams` | class / dataclass | Facility distance proximity grid and heatmap. |
| `PulseRadarPoiMap` / `RadarPulseConfig` | class / dataclass | Animated radar pulse and ripple POI beacons. |
| `StoryMapScroller` / `StoryChapter` | class / dataclass | Scroll-driven narrative map. |
| `MultiPageAtlas` / `AtlasGridSheet` | class / dataclass | Printable multi-page atlas grid index. |
| `RadialSearchMap` | class | Interactive point-and-click radial buffer query. |

---

## 🧪 Development & Testing

```bash
# Run the test suite
python -m pytest -q

# Run tests with coverage (configured in pyproject.toml)
python -m pytest --cov=multilayer --cov-report=term-missing

# Lint and format
python -m ruff check .
python -m ruff format src tests
```

The project targets Python 3.9+ and is linted with Ruff (`E`, `F`, `W`, `I`, `B`, `C4`) at a 100-character line length. Tests live in `tests/` and run against `src/` via the `pythonpath` setting in `pyproject.toml`.

---

## 📄 Academic Citation

If you use **multilayer-sdk** in scientific publications, planning projects, or research, please cite:

```bibtex
@software{eminoglu2026multilayer,
  author    = {Emino{\u{g}}lu, Yusuf},
  title     = {{multilayer-sdk: Pure-Python Synchronized Multi-Panel Map Visualization, Spatial Comparison Engine, and Interactive Dashboard Builder}},
  year      = {2026},
  publisher = {PyPI - Python Package Index},
  version   = {0.12.1},
  url       = {https://gitlab.com/geospacephilo/multilayer-sdk}
}
```

---

## 📜 License

Distributed under the **MIT** License. Copyright (c) 2026 Yusuf Eminoğlu.
