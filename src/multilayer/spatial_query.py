# -*- coding: utf-8 -*-
"""Interactive Buffer & Radius Search Widget for multilayer."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RadialSearchMap:
    """Interactive point-and-click radial buffer query tool."""

    center_lat: float = 41.0
    center_lon: float = 29.0
    initial_radius_meters: float = 1000.0
    max_radius_meters: float = 10000.0
    geojson_target_layers: list[dict[str, Any]] = field(default_factory=list)

    def add_layer(self, geojson_data: dict[str, Any]) -> None:
        self.geojson_target_layers.append(geojson_data)

    def to_html(self, title: str = "Interactive Spatial Radius Filter") -> str:
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
    #map {{ width: 100%; height: 100%; }}
    #control-box {{ position: absolute; top: 16px; right: 16px; z-index: 1000; background: rgba(255,255,255,0.95); padding: 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); min-width: 240px; }}
    .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 700; }}
    .kpi-val {{ font-size: 24px; font-weight: 800; color: #0284c7; margin-bottom: 8px; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div id="control-box">
    <div class="kpi-title">Buffer Radius</div>
    <div style="display:flex; align-items:center; gap:8px;">
      <input type="range" id="radius-slider" min="100" max="{int(self.max_radius_meters)}" step="100" value="{int(self.initial_radius_meters)}" style="flex:1;" />
      <span id="radius-label" style="font-weight:600; font-size:13px;">{int(self.initial_radius_meters)}m</span>
    </div>
    <div class="kpi-title" style="margin-top:12px;">Contained Features</div>
    <div class="kpi-val" id="count-kpi">0</div>
  </div>
  <script>
    const map = L.map('map').setView([{self.center_lat}, {self.center_lon}], 13);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png', {{ maxZoom: 19 }}).addTo(map);

    let centerLatLng = [{self.center_lat}, {self.center_lon}];
    let radius = {self.initial_radius_meters};
    const circle = L.circle(centerLatLng, {{ radius: radius, color: '#0284c7', fillColor: '#38bdf8', fillOpacity: 0.25 }}).addTo(map);
    const centerMarker = L.marker(centerLatLng, {{ draggable: true }}).addTo(map);

    const slider = document.getElementById('radius-slider');
    const label = document.getElementById('radius-label');

    slider.addEventListener('input', (e) => {{
      radius = parseFloat(e.target.value);
      label.innerText = radius + 'm';
      circle.setRadius(radius);
    }});

    centerMarker.on('drag', (e) => {{
      circle.setLatLng(e.latlng);
    }});

    map.on('click', (e) => {{
      centerMarker.setLatLng(e.latlng);
      circle.setLatLng(e.latlng);
    }});
  </script>
</body>
</html>
"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
        return out
