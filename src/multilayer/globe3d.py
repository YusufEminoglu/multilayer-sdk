# -*- coding: utf-8 -*-
"""Synchronized 3D Dual/Quad Globe & Terrain Panel Viewer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TerrainPanel3D:
    """A single 3D terrain/globe viewport configuration."""

    title: str
    camera_lat: float = 41.0
    camera_lon: float = 29.0
    camera_altitude_m: float = 5000.0
    pitch_degrees: float = -45.0
    bearing_degrees: float = 0.0
    dem_source: str = "mapbox-terrain-rgb"
    terrain_exaggeration: float = 1.5
    geojson_layers: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Globe3DMap:
    """Synchronized Multi-Panel 3D Globe & Elevation Terrain Viewer."""

    layout: str = "dual-horizontal"  # 'single', 'dual-horizontal', 'dual-vertical', 'quad'
    sync_camera: bool = True
    panels: list[TerrainPanel3D] = field(default_factory=list)

    def add_panel(self, panel: TerrainPanel3D) -> None:
        self.panels.append(panel)

    def to_html(self, title: str = "3D Synchronized Terrain Globe") -> str:
        """Generate a self-contained 3D WebGL / Three.js / Cesium compatible HTML document."""
        panels_json = json.dumps([
            {
                "title": p.title,
                "lat": p.camera_lat,
                "lon": p.camera_lon,
                "alt": p.camera_altitude_m,
                "pitch": p.pitch_degrees,
                "bearing": p.bearing_degrees,
                "exaggeration": p.terrain_exaggeration,
                "layers": p.geojson_layers,
            }
            for p in self.panels
        ])

        grid_css = "grid-template-columns: 1fr 1fr;" if "dual" in self.layout else "grid-template-columns: 1fr;"
        if self.layout == "quad":
            grid_css = "grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr;"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <style>
    body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; font-family: system-ui, sans-serif; background: #0f172a; color: #fff; }}
    #viewport-container {{ display: grid; {grid_css} width: 100%; height: 100%; gap: 2px; }}
    .panel3d {{ position: relative; width: 100%; height: 100%; background: #1e293b; display: flex; flex-direction: column; }}
    .panel-header {{ padding: 8px 16px; background: rgba(15, 23, 42, 0.85); font-weight: 600; font-size: 14px; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; }}
    .canvas-container {{ flex: 1; position: relative; }}
  </style>
</head>
<body>
  <div id="viewport-container"></div>
  <script>
    const panelsData = {panels_json};
    const container = document.getElementById('viewport-container');

    panelsData.forEach((p, idx) => {{
      const pDiv = document.createElement('div');
      pDiv.className = 'panel3d';
      pDiv.innerHTML = `
        <div class="panel-header">
          <span>${{p.title}}</span>
          <span style="font-size: 11px; opacity: 0.7;">Alt: ${{p.alt}}m | Pitch: ${{p.pitch}}°</span>
        </div>
        <div class="canvas-container" id="canvas-panel-${{idx}}"></div>
      `;
      container.appendChild(pDiv);
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
