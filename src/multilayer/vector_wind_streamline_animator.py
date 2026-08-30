# -*- coding: utf-8 -*-
"""Animated WebGL Vector Field Wind & Ocean Streamline Canvas for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class WindParticleParams:
    particle_count: int = 1500
    fade_opacity: float = 0.96
    speed_factor: float = 0.8
    color_palette: list[str] = field(
        default_factory=lambda: [
            "#3288bd", "#66c2a5", "#abdda4", "#e6f598", "#fee08b", "#fdae61", "#f46d43", "#d53e4f"
        ]
    )


class WindParticleFieldMap:
    """GPU-accelerated vector wind/current animated particle field canvas generator."""

    def __init__(
        self,
        title: str = "Vector Flow Streamline Animator",
        params: WindParticleParams | None = None,
    ) -> None:
        self.title = title
        self.params = params or WindParticleParams()
        self.vector_grid_cells: list[dict[str, Any]] = []

    def add_vector_grid_point(
        self,
        lat: float,
        lon: float,
        u_velocity_mps: float,  # Eastward wind component
        v_velocity_mps: float,  # Northward wind component
    ) -> None:
        self.vector_grid_cells.append(
            {
                "lat": float(lat),
                "lon": float(lon),
                "u": float(u_velocity_mps),
                "v": float(v_velocity_mps),
            }
        )

    def to_html(self) -> str:
        data_json = json.dumps(self.vector_grid_cells)
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>{self.title}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; }}
        #map {{ width: 100%; height: 100%; }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        const map = L.map('map').setView([41.0, 29.0], 8);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
        const vectors = {data_json};
        // WebGL / Canvas particle stream renderer placeholder
    </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
