# -*- coding: utf-8 -*-
"""Interactive Circular Spyglass / Magnifying Glass Map Comparer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LensConfig:
    radius_pixels: int = 150
    border_width_px: int = 3
    border_color: str = "#38bdf8"
    magnification_zoom_offset: int = 2


@dataclass
class SpyglassCompareMap:
    """Interactive circular magnifying lens comparing two layers/basemaps on mouse hover."""

    title: str = "Spyglass Comparison Map"
    center_lat: float = 41.0082
    center_lon: float = 28.9784
    base_zoom: int = 13
    primary_tile_url: str = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
    spyglass_tile_url: str = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    lens_config: LensConfig = field(default_factory=LensConfig)

    def render_html(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{self.title}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; }}
    #base-map {{ width: 100%; height: 100%; }}
    #lens {{
      position: absolute;
      width: {self.lens_config.radius_pixels * 2}px;
      height: {self.lens_config.radius_pixels * 2}px;
      border-radius: 50%;
      border: {self.lens_config.border_width_px}px solid {self.lens_config.border_color};
      box-shadow: 0 0 25px rgba(0,0,0,0.6);
      overflow: hidden;
      pointer-events: none;
      z-index: 1000;
      transform: translate(-50%, -50%);
      display: none;
    }}
    #lens-map {{ width: 100vw; height: 100vh; position: absolute; }}
  </style>
</head>
<body>
  <div id="base-map"></div>
  <div id="lens"><div id="lens-map"></div></div>

  <script>
    const baseMap = L.map('base-map').setView([{self.center_lat}, {self.center_lon}], {self.base_zoom});
    L.tileLayer('{self.primary_tile_url}', {{ maxZoom: 19 }}).addTo(baseMap);

    const lens = document.getElementById('lens');
    const lensMap = L.map('lens-map', {{ zoomControl: false, attributionControl: false }}).setView([{self.center_lat}, {self.center_lon}], {self.base_zoom + self.lens_config.magnification_zoom_offset});
    L.tileLayer('{self.spyglass_tile_url}', {{ maxZoom: 19 }}).addTo(lensMap);

    baseMap.on('mousemove', (e) => {{
      lens.style.display = 'block';
      lens.style.left = e.containerPoint.x + 'px';
      lens.style.top = e.containerPoint.y + 'px';
      
      const lensMapDiv = document.getElementById('lens-map');
      lensMapDiv.style.left = (-e.containerPoint.x + {self.lens_config.radius_pixels}) + 'px';
      lensMapDiv.style.top = (-e.containerPoint.y + {self.lens_config.radius_pixels}) + 'px';

      lensMap.setView(e.latlng, baseMap.getZoom() + {self.lens_config.magnification_zoom_offset});
    }});

    baseMap.on('mouseout', () => {{ lens.style.display = 'none'; }});
  </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.render_html(), encoding="utf-8")
        return out
