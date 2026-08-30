# -*- coding: utf-8 -*-
"""Hypso-Tinted Topographic Relief & Dynamic Contour Line Layer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class ContourIntervalConfig:
    minor_interval_meters: float = 10.0
    index_interval_meters: float = 50.0
    index_line_color: str = "#8b4513"  # Saddle brown
    minor_line_color: str = "#cd853f"  # Peru light brown
    hypso_color_ramp: list[str] = field(
        default_factory=lambda: [
            "#43956f", "#80b878", "#c8d886", "#fae392", "#e2a168", "#b85e43", "#ffffff"
        ]
    )


class HypsoTintedReliefMap:
    """Hypsometrically tinted elevation relief surface with labeled contour lines."""

    def __init__(
        self,
        title: str = "Topographic Elevation Relief",
        config: ContourIntervalConfig | None = None,
    ) -> None:
        self.title = title
        self.config = config or ContourIntervalConfig()
        self.contour_lines: list[dict[str, Any]] = []

    def add_contour_line(
        self,
        elevation_m: float,
        coordinates_path: Sequence[tuple[float, float]],
    ) -> None:
        is_index = (elevation_m % self.config.index_interval_meters) == 0
        self.contour_lines.append(
            {
                "elevation": float(elevation_m),
                "is_index": is_index,
                "coords": [[float(p[1]), float(p[0])] for p in coordinates_path],  # [lon, lat]
            }
        )

    def to_html(self) -> str:
        features = [
            {
                "type": "Feature",
                "properties": {
                    "elevation": c["elevation"],
                    "is_index": c["is_index"],
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": c["coords"],
                },
            }
            for c in self.contour_lines
        ]
        geojson_str = json.dumps({"type": "FeatureCollection", "features": features})

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
        const map = L.map('map').setView([41.0, 29.0], 11);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
        const geoData = {geojson_str};
        L.geoJSON(geoData, {{
            style: function(f) {{
                return {{
                    color: f.properties.is_index ? '{self.config.index_line_color}' : '{self.config.minor_line_color}',
                    weight: f.properties.is_index ? 2.5 : 1.0,
                    opacity: 0.85
                }};
            }}
        }}).addTo(map);
    </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
