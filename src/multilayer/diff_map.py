# -*- coding: utf-8 -*-
"""Synchronized Polygon Comparison & Geometric Symmetric Difference Visualizer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SpatialDiffResult:
    """Statistical summary of visual comparison."""

    layer_a_name: str
    layer_b_name: str
    features_count_a: int
    features_count_b: int
    matched_features: int
    only_in_a: int
    only_in_b: int


@dataclass
class DiffMap:
    """Interactive visual diff comparison tool with swipe/side-by-side modes."""

    mode: str = "swipe"  # 'swipe', 'split-screen', 'overlay-blend'
    layer_a_geojson: dict[str, Any] = field(default_factory=dict)
    layer_b_geojson: dict[str, Any] = field(default_factory=dict)
    title_a: str = "Baseline / Before"
    title_b: str = "Modified / After"

    def to_html(self, title: str = "Spatial Layer Difference Visualizer") -> str:
        data_a = json.dumps(self.layer_a_geojson)
        data_b = json.dumps(self.layer_b_geojson)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; font-family: system-ui, sans-serif; }}
    .container {{ display: flex; width: 100%; height: 100%; }}
    .map-panel {{ flex: 1; height: 100%; position: relative; }}
    .map-badge {{ position: absolute; top: 12px; left: 60px; z-index: 1000; background: rgba(15,23,42,0.85); color: #fff; padding: 6px 14px; border-radius: 6px; font-weight: 600; font-size: 13px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="map-panel" id="map-a">
      <div class="map-badge">{self.title_a}</div>
    </div>
    <div class="map-panel" id="map-b" style="border-left: 2px solid #334155;">
      <div class="map-badge">{self.title_b}</div>
    </div>
  </div>
  <script>
    const mapA = L.map('map-a').setView([41.0, 29.0], 12);
    const mapB = L.map('map-b').setView([41.0, 29.0], 12);

    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(mapA);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(mapB);

    const dataA = {data_a};
    const dataB = {data_b};

    if (dataA.features) L.geoJSON(dataA, {{ style: {{ color: '#ef4444', weight: 2, fillOpacity: 0.3 }} }}).addTo(mapA);
    if (dataB.features) L.geoJSON(dataB, {{ style: {{ color: '#10b981', weight: 2, fillOpacity: 0.3 }} }}).addTo(mapB);

    // Synchronize panning & zooming
    mapA.on('move', () => {{ mapB.setView(mapA.getCenter(), mapA.getZoom(), {{ animate: false }}); }});
    mapB.on('move', () => {{ mapA.setView(mapB.getCenter(), mapB.getZoom(), {{ animate: false }}); }});
  </script>
</body>
</html>
"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
        return out
