# -*- coding: utf-8 -*-
"""Hexagonal Spatial Aggregation Grid & Metric Choropleth for multilayer."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


@dataclass
class HexagonCell:
    hex_id: str
    center_lat: float
    center_lon: float
    boundary_polygon: list[tuple[float, float]]
    point_count: int
    aggregated_metric_value: float
    color_hex: str = "#3b82f6"


@dataclass
class HexbinHeatmapLayer:
    layer_name: str
    hex_radius_meters: float
    aggregation_statistic: str  # 'COUNT', 'MEAN', 'SUM', 'MAX'
    total_hexagons: int
    cells: list[HexagonCell]

    def to_geojson(self) -> dict[str, Any]:
        features = []
        for c in self.cells:
            # Leaflet / GeoJSON expects [lon, lat]
            poly_coords = [[round(pt[1], 5), round(pt[0], 5)] for pt in c.boundary_polygon]
            # Ensure closed
            if poly_coords and poly_coords[0] != poly_coords[-1]:
                poly_coords.append(poly_coords[0])

            features.append({
                "type": "Feature",
                "properties": {
                    "hex_id": c.hex_id,
                    "count": c.point_count,
                    "value": round(c.aggregated_metric_value, 2),
                    "fill": c.color_hex,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [poly_coords],
                },
            })
        return {"type": "FeatureCollection", "features": features}


def aggregate_points_to_hexbins(
    points_lat_lon: Sequence[tuple[float, float]],
    point_values: Sequence[float] | None = None,
    hex_radius_m: float = 500.0,
    statistic: str = "COUNT",
) -> HexbinHeatmapLayer:
    """Aggregate dense spatial points into regular hexagonal lattice bins."""
    pts = list(points_lat_lon)
    vals = list(point_values) if point_values is not None else [1.0] * len(pts)
    n = len(pts)
    if n == 0:
        return HexbinHeatmapLayer("HexbinLayer", hex_radius_m, statistic, 0, [])

    # Approx degree conversions (1 deg lat ~ 111,000m)
    d_lat_deg = hex_radius_m / 111000.0
    d_lon_deg = hex_radius_m / (111000.0 * math.cos(math.radians(pts[0][0])))

    # Hexagonal grid cell width and height
    h_spacing = 1.5 * d_lat_deg
    w_spacing = math.sqrt(3.0) * d_lon_deg

    bins: dict[tuple[int, int], list[float]] = {}

    for i in range(n):
        lat, lon = pts[i]
        val = vals[i]

        r = int(round(lat / h_spacing))
        c = int(round((lon - (0.5 * (r % 2) * w_spacing)) / w_spacing))
        key = (r, c)
        bins.setdefault(key, []).append(val)

    hex_cells: list[HexagonCell] = []
    stat_upper = statistic.upper()

    for (r, c), bin_vals in bins.items():
        c_lat = r * h_spacing
        c_lon = c * w_spacing + (0.5 * (r % 2) * w_spacing)
        cnt = len(bin_vals)

        if stat_upper == "MEAN":
            metric_val = sum(bin_vals) / max(1, cnt)
        elif stat_upper == "SUM":
            metric_val = sum(bin_vals)
        elif stat_upper == "MAX":
            metric_val = max(bin_vals)
        else:  # COUNT
            metric_val = float(cnt)

        # Generate 6 vertices for flat-topped hexagon
        poly_pts = []
        for angle_deg in range(0, 360, 60):
            rad = math.radians(angle_deg + 30)
            vx = c_lat + d_lat_deg * math.sin(rad)
            vy = c_lon + d_lon_deg * math.cos(rad)
            poly_pts.append((vx, vy))

        # Color ramp mapping
        color = "#10b981" if cnt < 5 else ("#f59e0b" if cnt < 15 else "#ef4444")

        hex_cells.append(
            HexagonCell(
                hex_id=f"hex_{r}_{c}",
                center_lat=c_lat,
                center_lon=c_lon,
                boundary_polygon=poly_pts,
                point_count=cnt,
                aggregated_metric_value=metric_val,
                color_hex=color,
            )
        )

    return HexbinHeatmapLayer(
        layer_name="HexbinHeatmap",
        hex_radius_meters=hex_radius_m,
        aggregation_statistic=stat_upper,
        total_hexagons=len(hex_cells),
        cells=hex_cells,
    )
