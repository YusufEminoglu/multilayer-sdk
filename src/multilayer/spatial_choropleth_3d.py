# -*- coding: utf-8 -*-
"""3D Extruded Polygon Choropleth / Prism Map WebGL Renderer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class PrismPolygon3D:
    feature_id: str
    boundary_polygon: list[tuple[float, float]]  # (lat, lon)
    metric_value: float
    extrusion_height_m: float
    color_hex: str = "#3b82f6"


@dataclass
class Choropleth3DMap:
    """Interactive 3D extruded prism polygon thematic choropleth map."""

    title: str = "3D Urban Density Prism Map"
    metric_name: str = "Density (hab/ha)"
    prisms: list[PrismPolygon3D] = field(default_factory=list)

    def add_prism(
        self,
        feature_id: str,
        coordinates_lat_lon: Sequence[tuple[float, float]],
        metric_value: float,
        height_scale: float = 10.0,
        color_hex: str = "#3b82f6",
    ) -> None:
        poly = list(coordinates_lat_lon)
        self.prisms.append(
            PrismPolygon3D(
                feature_id=feature_id,
                boundary_polygon=poly,
                metric_value=metric_value,
                extrusion_height_m=max(5.0, metric_value * height_scale),
                color_hex=color_hex,
            )
        )

    def to_geojson(self) -> dict[str, Any]:
        features = []
        for p in self.prisms:
            coords = [[round(pt[1], 5), round(pt[0], 5)] for pt in p.boundary_polygon]
            if coords and coords[0] != coords[-1]:
                coords.append(coords[0])

            features.append({
                "type": "Feature",
                "properties": {
                    "id": p.feature_id,
                    "value": round(p.metric_value, 2),
                    "height": round(p.extrusion_height_m, 1),
                    "color": p.color_hex,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords],
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
    #map3d {{ width: 100%; height: 100%; background: #0f172a; }}
    .legend {{ position: absolute; bottom: 20px; right: 20px; background: rgba(15,23,42,0.85); color: #fff; padding: 15px; border-radius: 8px; font-size: 13px; z-index: 100; }}
  </style>
</head>
<body>
  <div id="map3d"></div>
  <div class="legend"><strong>{self.title}</strong><br>{self.metric_name}</div>
  <script>
    const data = {gj_str};
    const map = new maplibregl.Map({{
      container: 'map3d',
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [data.features[0].geometry.coordinates[0][0][0], data.features[0].geometry.coordinates[0][0][1]],
      zoom: 13,
      pitch: 55,
      bearing: -20
    }});

    map.on('load', () => {{
      map.addSource('prisms', {{ type: 'geojson', data: data }});
      map.addLayer({{
        id: '3d-prisms',
        type: 'fill-extrusion',
        source: 'prisms',
        paint: {{
          'fill-extrusion-color': ['get', 'color'],
          'fill-extrusion-height': ['get', 'height'],
          'fill-extrusion-base': 0,
          'fill-extrusion-opacity': 0.85
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
