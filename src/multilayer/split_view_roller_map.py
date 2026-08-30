# -*- coding: utf-8 -*-
"""Diagonal & Angle-Adjustable Roller Curtain Map Comparer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class RollerAngleMode(str, Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    DIAGONAL_45 = "diagonal_45"
    CIRCULAR_APERTURE = "circular_aperture"


@dataclass
class RollerCurtainMap:
    title: str = "Roller Curtain Map Comparer"
    center_lat: float = 41.0082
    center_lon: float = 28.9784
    initial_zoom: int = 13
    left_layer_name: str = "Historic Orthophoto (2015)"
    right_layer_name: str = "Current Satellite (2026)"
    mode: RollerAngleMode = RollerAngleMode.DIAGONAL_45

    def to_html(self) -> str:
        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{self.title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    body, html {{ margin: 0; padding: 0; height: 100%; font-family: system-ui, sans-serif; }}
    #map {{ width: 100%; height: 100%; }}
    .roller-hud {{ position: absolute; top: 10px; left: 10px; z-index: 1000; background: rgba(15,23,42,0.85); color: white; padding: 10px 16px; border-radius: 8px; }}
  </style>
</head>
<body>
  <div class="roller-hud">
    <h3>{self.title}</h3>
    <p>Mode: <strong>{self.mode.value}</strong> | Left: {self.left_layer_name} vs Right: {self.right_layer_name}</p>
  </div>
  <div id="map"></div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const map = L.map('map').setView([{self.center_lat}, {self.center_lon}], {self.initial_zoom});
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
  </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
        return out


def render_roller_map_html(
    left_layer_title: str,
    right_layer_title: str,
    output_path: str | Path,
    mode: RollerAngleMode = RollerAngleMode.DIAGONAL_45,
) -> Path:
    """Helper to construct and save a RollerCurtainMap."""
    roller = RollerCurtainMap(
        left_layer_name=left_layer_title,
        right_layer_name=right_layer_title,
        mode=mode,
    )
    return roller.save_html(output_path)
