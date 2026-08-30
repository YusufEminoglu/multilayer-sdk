# Changelog

All notable changes to this project will be documented in this file.

## [0.12.0] - 2026-08-30
### Added
- **Multi-Layer Distance Proximity Matrix & Heatmap Grid (`matrix_proximity_heatmap_grid.py`)**: Added `ProximityMatrixHeatmapMap` for multi-facility Euclidean distance rasterization and zone thresholds.
- **Animated Dynamic Radar Pulse & Ripple POI Beacon Visualizer (`animated_pulse_radar_poi_map.py`)**: Added `PulseRadarPoiMap` generating animated beacon pulses and sonar ripples on POIs.

## [0.11.0] - 2026-08-30
### Added
- **Multi-Modal Radial Travel Isochrone Bubble Map (`isochrone_travel_bubble_map.py`)**: Added `TravelIsochroneBubbleMap` generating multi-cutoff reachability rings and popup time indicators.
- **Hypso-Tinted Topographic Relief & Dynamic Contour Layer (`elevation_contour_relief_map.py`)**: Added `HypsoTintedReliefMap` styling index and minor elevation contour lines.

## [0.10.0] - 2026-08-30
### Added
- **2D 3x3 Bivariate Matrix Choropleth Map Visualizer (`bivariate_choropleth_map.py`)**: Added `BivariateChoroplethMap` for dual-variable spatial correlation analytics and dynamic 3x3 matrix legends.
- **Animated WebGL Vector Field Wind & Ocean Streamline Canvas (`vector_wind_streamline_animator.py`)**: Added `WindParticleFieldMap` animating meteorological velocity fields.

## [0.9.0] - 2026-08-30
### Added
- **Interactive Time-Series Temporal Range Slider Map (`animated_temporal_slider_map.py`)**: Added `TemporalRangeSliderMap` for interactive time-lapse map frame playback and metric charting.
- **Angle-Adjustable Roller Curtain Map Comparer (`split_view_roller_map.py`)**: Added `RollerCurtainMap` supporting vertical, horizontal, diagonal, and circular aperture layer wipe comparisons.

## [0.8.0] - 2026-08-30
### Added
- **Quad-Synchronized 4-Panel Map Grid (`split_screen_quad_view.py`)**: Added `QuadSyncMap` rendering a 2x2 multi-basemap grid with linked center, zoom, and mouse reticle.
- **Curved Animated Flow Arcs Visualizer (`flow_arrow_curved_layer.py`)**: Added `CurvedFlowMap` computing quadratic Bézier flight/commuter arcs and GeoJSON/MapLibre line layers.

## [0.7.0] - 2026-08-30
### Added
- **3D Extruded Polygon Choropleth / Prism Maps (`spatial_choropleth_3d.py`)**: Added `Choropleth3DMap` rendering MapLibre GL 3D extruded prism polygons scaled by thematic indicators.
- **Interactive Spyglass & Lens Comparer (`lens_magnifier_map.py`)**: Added `SpyglassCompareMap` with circular mouse-tracking magnifying glass layer overlay.

## [0.6.0] - 2026-08-30
### Added
- **Hexagonal Spatial Aggregation Grid & Hexbin Heatmaps (`hexbin_aggregation.py`)**: Added `aggregate_points_to_hexbins` supporting COUNT, MEAN, SUM metrics and GeoJSON Polygon export.
- **Scroll-Driven Narrative Scrollytelling Map (`storymap_scroller.py`)**: Added `StoryMapScroller` and `StoryChapter` creating interactive scroll-synchronized camera flyovers.

## [0.5.0] - 2026-08-30
### Added
- **Animated Vector Particle Flow Map (`particle_layer.py`)**: Added `ParticleFlowMap` and `FlowParticleConfig` with Canvas/WebGL particle animations.
- **Spatial Curtain Split-Slider Reveal Map (`curtain_map.py`)**: Added `CurtainMap` with interactive synchronized side-by-side curtain wipe reveal.

## [0.4.0] - 2026-08-30

### Added
- **3D Globe & Synchronized Terrain Viewer (`globe3d.py`)**: Added `Globe3DMap` and `TerrainPanel3D` for multi-viewport WebGL 3D terrain exploration.
- **Interactive Spatial Radius Query Tool (`spatial_query.py`)**: Added `RadialSearchMap` with draggable radius controls and live KPI aggregation.
- **Synchronized Difference Map (`diff_map.py`)**: Added `DiffMap` for visual side-by-side / overlay change comparison.
- **Multi-Page Cartographic Atlas Generator (`atlas_generator.py`)**: Added `MultiPageAtlas` grid index and sheet layout generator.

## [0.2.0] - 2026-08-30

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-30

### Added
- **Time-Series Map Animator & Scenario Player (`timeline.py`)**:
  - `TimelineMap` & `TimeFrame`: Multi-step scenario and temporal progression deck.
  - Interactive playback controls: Play/Pause, variable speed (FPS), step buttons, interactive time scrubber bar, and active timestamp badge overlays.
- **Cross-Filtering Interactive Dashboard Builder (`dashboard.py`)**:
  - `InteractiveDashboard`: Synchronizes multi-panel maps with real-time sidebar range/category filters and metric KPI cards (`MetricCard`, `FilterWidget`).
  - Dynamic on-the-fly aggregations (Sum, Mean, Min, Max, Count) connected directly to filtered GeoJSON features and interactive popups.

## [0.1.0] - 2026-08-26

### Added
- **Core MultiMap Workspace Container**:
  - Configurable 2, 3, 4, 6, and 8-panel synchronized map grids (`1x2`, `2x1`, `1x3`, `2x2`, `2x3`, `2x4`).
  - Bi-directional navigation broadcasting (pan/zoom synchronization).
  - Real-time neon laser pointer crosshair cursor tracking across all panels.
  - Automatic union bounding box calculation from spatial layers.
  - Jupyter Notebook & Google Colab inline widget rendering (`_repr_html_()` and `.show()`).
- **Curtain Swipe Comparison (`SwipeMap`)**:
  - Interactive draggable split-screen slider for before/after temporal change detection.
- **Layer & Basemap Subsystem**:
  - `VectorLayer`: GeoJSON, GeoDataFrame, and dictionary feature collections with tooltip/popup inspectors.
  - `TileLayer`: Built-in providers for OpenStreetMap, CartoDB Positron, CartoDB Dark Matter, CartoDB Voyager, Esri Satellite, Esri Topo, OpenTopoMap, CyclOSM, and custom XYZ URLs.
  - `RasterLayer`: Georeferenced image bounds overlays.
- **Thematic Symbology & Classification (`Choropleth`)**:
  - Statistical binning: Quantiles, Equal Interval, Natural Breaks, Standard Deviation, and Categorical.
  - Scientific palettes: Viridis, Magma, Plasma, Inferno, Turbo, Cividis, Blues, Reds, Greens, Spectral, RdYlBu, YlOrRd, PuBu.
- **Self-Contained Offline HTML Builder**:
  - Single-file zero-dependency dashboard export with theme toggle (Dark / Light), fullscreen, and coordinate readouts.
- **Command Line Interface (`multilayer`)**:
  - Subcommands: `build`, `compare`, `inspect`, `tiles`, and `version`.
- **Documentation & CI/CD**:
  - GitHub Pages interactive documentation with live canvas multi-panel simulator.
  - GitHub Actions multi-OS / Python 3.9–3.13 matrix testing workflow.
  - PyPI Trusted Publisher workflow.
