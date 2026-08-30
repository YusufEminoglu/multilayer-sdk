# -*- coding: utf-8 -*-
"""Multi-Modal Radial Isochrone Travel Bubble Map for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class IsochroneBandParams:
    cutoffs_minutes: list[int] = field(default_factory=lambda: [5, 10, 15, 30, 45])
    color_palette: list[str] = field(
        default_factory=lambda: ["#2ca02c", "#8c6bb1", "#41b6c4", "#fdae61", "#d7191c"]
    )
    fill_opacity: float = 0.45


class TravelIsochroneBubbleMap:
    """Interactive multi-modal concentric travel-time contour bubble map generator."""

    def __init__(
        self,
        title: str = "Multi-Modal 15-Minute City Reachability",
        center_lat_lon: tuple[float, float] = (41.0, 29.0),
        params: IsochroneBandParams | None = None,
    ) -> None:
        self.title = title
        self.center = center_lat_lon
        self.params = params or IsochroneBandParams()
        self.rings: list[dict[str, Any]] = []

    def add_isochrone_ring(
        self,
        cutoff_minutes: int,
        geometry_polygon: dict[str, Any],
        mode: str = "TRANSIT",
    ) -> None:
        self.rings.append(
            {
                "cutoff_min": int(cutoff_minutes),
                "mode": mode,
                "geometry": geometry_polygon,
            }
        )

    def to_html(self) -> str:
        rings_json = json.dumps(self.rings)
        palette_json = json.dumps(self.params.color_palette)
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
        const map = L.map('map').setView([{self.center[0]}, {self.center[1]}], 12);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
        const isochrones = {rings_json};
        const colors = {palette_json};
        isochrones.forEach((ring, idx) => {{
            const color = colors[idx % colors.length];
            L.geoJSON(ring.geometry, {{
                style: {{ color: color, weight: 2, fillOpacity: {self.params.fill_opacity} }}
            }}).bindPopup('Isochrone: ' + ring.cutoff_min + ' min (' + ring.mode + ')').addTo(map);
        }});
    </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
