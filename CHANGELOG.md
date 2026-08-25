# Changelog

All notable changes to **multilayer-sdk** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
