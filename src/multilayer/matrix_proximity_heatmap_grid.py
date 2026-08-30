# -*- coding: utf-8 -*-
"""Multi-Layer Distance Proximity Matrix & Heatmap Grid Visualizer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class ProximityZoneParams:
    distance_thresholds_meters: list[float] = field(default_factory=lambda: [250.0, 500.0, 1000.0, 2000.0])
    color_palette: list[str] = field(
        default_factory=lambda: ["#1a9850", "#91cf60", "#d9ef8b", "#fee08b", "#fc8d59", "#d73027"]
    )
    grid_cell_size_m: float = 100.0


class ProximityMatrixHeatmapMap:
    """Multi-facility Euclidean distance proximity raster & vector grid matrix map generator."""

    def __init__(
        self,
        title: str = "Multi-Facility Proximity Heatmap",
        center_lat_lon: tuple[float, float] = (41.0, 29.0),
        params: ProximityZoneParams | None = None,
    ) -> None:
        self.title = title
        self.center = center_lat_lon
        self.params = params or ProximityZoneParams()
        self.facilities: list[dict[str, Any]] = []
        self.grid_cells: list[dict[str, Any]] = []

    def add_facility(self, facility_id: str, lat: float, lon: float, facility_type: str = "HOSPITAL") -> None:
        self.facilities.append({"id": facility_id, "lat": float(lat), "lon": float(lon), "type": facility_type})

    def add_grid_cell(self, cell_id: str, lat: float, lon: float, min_distance_m: float) -> None:
        self.grid_cells.append({
            "id": cell_id,
            "lat": float(lat),
            "lon": float(lon),
            "min_dist_m": float(min_distance_m),
        })

    def to_html(self) -> str:
        fac_json = json.dumps(self.facilities)
        grid_json = json.dumps(self.grid_cells)
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
        const facilities = {fac_json};
        const grid = {grid_json};
        facilities.forEach(f => {{
            L.circleMarker([f.lat, f.lon], {{ color: '#d73027', radius: 6, fillOpacity: 0.9 }})
             .bindPopup('Facility: ' + f.id + ' (' + f.type + ')').addTo(map);
        }});
        grid.forEach(c => {{
            L.circleMarker([c.lat, c.lon], {{ color: '#1a9850', radius: 3, fillOpacity: 0.5 }})
             .bindPopup('Cell: ' + c.id + '<br>Dist: ' + c.min_dist_m + 'm').addTo(map);
        }});
    </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
