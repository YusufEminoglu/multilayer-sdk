# -*- coding: utf-8 -*-
"""Curved Animated Flow Arcs & Origin-Destination Migration Visualizer for multilayer."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class FlowArc3D:
    flow_id: str
    origin_lat_lon: tuple[float, float]
    destination_lat_lon: tuple[float, float]
    flow_volume: float
    color_hex: str = "#f59e0b"
    arc_height_factor: float = 0.25


@dataclass
class CurvedFlowMap:
    """WebGL animated curved flow lines connecting origin-destination nodes."""

    title: str = "Inter-City Commuter Migration Flows"
    center_lat: float = 41.0082
    center_lon: float = 28.9784
    base_zoom: int = 7
    flows: list[FlowArc3D] = field(default_factory=list)

    def add_flow(
        self,
        flow_id: str,
        origin_lat_lon: tuple[float, float],
        destination_lat_lon: tuple[float, float],
        flow_volume: float,
        color_hex: str = "#f59e0b",
    ) -> None:
        self.flows.append(
            FlowArc3D(
                flow_id=flow_id,
                origin_lat_lon=origin_lat_lon,
                destination_lat_lon=destination_lat_lon,
                flow_volume=flow_volume,
                color_hex=color_hex,
            )
        )

    def _sample_bezier_arc(self, o: tuple[float, float], d: tuple[float, float], num_pts: int = 20) -> list[list[float]]:
        # Midpoint with perpendicular offset for visual curve
        lat1, lon1 = o
        lat2, lon2 = d
        mid_lat = (lat1 + lat2) / 2.0
        mid_lon = (lon1 + lon2) / 2.0

        d_lat = lat2 - lat1
        d_lon = lon2 - lon1
        dist = math.hypot(d_lat, d_lon)

        # Control point elevated perpendicularly
        ctrl_lat = mid_lat - (d_lon * 0.2)
        ctrl_lon = mid_lon + (d_lat * 0.2)

        curve_pts = []
        for i in range(num_pts + 1):
            t = i / float(num_pts)
            # Quadratic Bézier: B(t) = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
            lat_t = ((1 - t) ** 2) * lat1 + 2 * (1 - t) * t * ctrl_lat + (t**2) * lat2
            lon_t = ((1 - t) ** 2) * lon1 + 2 * (1 - t) * t * ctrl_lon + (t**2) * lon2
            curve_pts.append([round(lon_t, 5), round(lat_t, 5)])

        return curve_pts

    def to_geojson(self) -> dict[str, Any]:
        features = []
        for fl in self.flows:
            coords = self._sample_bezier_arc(fl.origin_lat_lon, fl.destination_lat_lon)
            features.append({
                "type": "Feature",
                "properties": {
                    "id": fl.flow_id,
                    "volume": fl.flow_volume,
                    "color": fl.color_hex,
                    "stroke_width": max(1.5, min(8.0, fl.flow_volume * 0.5)),
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords,
                },
            })
        return {"type": "FeatureCollection", "features": features}

    def render_html(self) -> str:
        gj_str = json.dumps(self.to_geojson())
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{self.title}</title>
  <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.css" />
  <script src="https://unpkg.com/maplibre-gl@3.6.2/dist/maplibre-gl.js"></script>
  <style>
    body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; font-family: sans-serif; }}
    #map {{ width: 100%; height: 100%; background: #0b0f19; }}
    .title-box {{ position: absolute; top: 15px; left: 15px; background: rgba(11,15,25,0.85); color: #fff; padding: 12px 18px; border-radius: 8px; font-size: 14px; font-weight: bold; z-index: 100; border: 1px solid #334155; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div class="title-box">{self.title}</div>
  <script>
    const data = {gj_str};
    const map = new maplibregl.Map({{
      container: 'map',
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [{self.center_lon}, {self.center_lat}],
      zoom: {self.base_zoom}
    }});

    map.on('load', () => {{
      map.addSource('flows', {{ type: 'geojson', data: data }});
      map.addLayer({{
        id: 'flow-lines',
        type: 'line',
        source: 'flows',
        layout: {{ 'line-join': 'round', 'line-cap': 'round' }},
        paint: {{
          'line-color': ['get', 'color'],
          'line-width': ['get', 'stroke_width'],
          'line-opacity': 0.85
        }}
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
