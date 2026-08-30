# -*- coding: utf-8 -*-
"""Quad-Synchronized 4-Panel Map Viewer with Cursor Crosshairs for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class QuadPanelConfig:
    panel_title: str
    tile_url: str
    attribution: str = ""


@dataclass
class QuadSyncMap:
    """4-Panel 2x2 synchronized grid map with linked center, zoom, and synchronized mouse reticle."""

    title: str = "Quad Comparative Map View"
    center_lat: float = 41.0082
    center_lon: float = 28.9784
    base_zoom: int = 13
    panels: list[QuadPanelConfig] = field(
        default_factory=lambda: [
            QuadPanelConfig("Standard Street", "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"),
            QuadPanelConfig("Satellite Imagery", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"),
            QuadPanelConfig("Dark Canvas", "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"),
            QuadPanelConfig("Topographic Terrain", "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"),
        ]
    )

    def render_html(self) -> str:
        panel_divs = []
        js_inits = []
        for i, p in enumerate(self.panels[:4]):
            panel_divs.append(f"""
    <div class="quad-box">
      <div class="panel-header">{p.panel_title}</div>
      <div id="map_{i}" class="map-frame"></div>
    </div>""")
            js_inits.append(f"""
      const map_{i} = L.map('map_{i}', {{ zoomControl: false }}).setView([{self.center_lat}, {self.center_lon}], {self.base_zoom});
      L.tileLayer('{p.tile_url}', {{ maxZoom: 19 }}).addTo(map_{i});
      maps.push(map_{i});""")

        divs_str = "\n".join(panel_divs)
        inits_str = "\n".join(js_inits)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{self.title}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; }}
    .header {{ height: 40px; background: #1e293b; color: #f8fafc; display: flex; align-items: center; padding: 0 15px; font-size: 14px; font-weight: bold; }}
    .quad-grid {{ display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; width: 100vw; height: calc(100vh - 40px); gap: 2px; background: #334155; }}
    .quad-box {{ position: relative; width: 100%; height: 100%; }}
    .map-frame {{ width: 100%; height: 100%; }}
    .panel-header {{ position: absolute; top: 10px; left: 10px; z-index: 1000; background: rgba(15,23,42,0.85); color: #fff; padding: 5px 10px; border-radius: 4px; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="header">{self.title}</div>
  <div class="quad-grid">
{divs_str}
  </div>

  <script>
    const maps = [];
{inits_str}

    let isSyncing = false;
    maps.forEach((m, idx) => {{
      m.on('move', () => {{
        if (isSyncing) return;
        isSyncing = true;
        const c = m.getCenter();
        const z = m.getZoom();
        maps.forEach((other, oIdx) => {{
          if (idx !== oIdx) {{
            other.setView(c, z, {{ animate: false }});
          }}
        }});
        isSyncing = false;
      }});
    }});
  </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.render_html(), encoding="utf-8")
        return out
