# -*- coding: utf-8 -*-
"""Printable Cartographic Multi-Page Atlas & Map Book Layout Engine for multilayer."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class AtlasGridSheet:
    """A single page/sheet tile in the cartographic atlas book."""

    sheet_number: int
    sheet_name: str
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
    scale_representative_fraction: int = 5000  # 1:5,000


@dataclass
class MultiPageAtlas:
    """Grid index layout generator for printing map books and atlases."""

    title: str = "Regional Planning Atlas"
    rows: int = 2
    cols: int = 3
    bounds: tuple[float, float, float, float] = (40.9, 28.8, 41.1, 29.2)  # (min_lat, min_lon, max_lat, max_lon)
    sheets: list[AtlasGridSheet] = field(default_factory=list)

    def generate_grid_index(self) -> list[AtlasGridSheet]:
        min_lat, min_lon, max_lat, max_lon = self.bounds
        lat_step = (max_lat - min_lat) / self.rows
        lon_step = (max_lon - min_lon) / self.cols

        sheets: list[AtlasGridSheet] = []
        sheet_num = 1

        # Generate top-to-bottom, left-to-right
        for r in range(self.rows - 1, -1, -1):
            s_min_lat = min_lat + r * lat_step
            s_max_lat = s_min_lat + lat_step
            for c in range(self.cols):
                s_min_lon = min_lon + c * lon_step
                s_max_lon = s_min_lon + lon_step

                sheets.append(
                    AtlasGridSheet(
                        sheet_number=sheet_num,
                        sheet_name=f"Sheet {sheet_num:02d} - [{chr(65+r)}{c+1}]",
                        min_lat=round(s_min_lat, 5),
                        min_lon=round(s_min_lon, 5),
                        max_lat=round(s_max_lat, 5),
                        max_lon=round(s_max_lon, 5),
                    )
                )
                sheet_num += 1

        self.sheets = sheets
        return sheets

    def to_geojson_index(self) -> dict[str, Any]:
        """Export the atlas page index as a GeoJSON polygon feature collection."""
        if not self.sheets:
            self.generate_grid_index()

        features = []
        for s in self.sheets:
            poly_coords = [
                [
                    [s.min_lon, s.min_lat],
                    [s.max_lon, s.min_lat],
                    [s.max_lon, s.max_lat],
                    [s.min_lon, s.max_lat],
                    [s.min_lon, s.min_lat],
                ]
            ]
            features.append({
                "type": "Feature",
                "properties": {
                    "sheet_number": s.sheet_number,
                    "sheet_name": s.sheet_name,
                    "scale": f"1:{s.scale_representative_fraction:,}",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": poly_coords,
                },
            })

        return {
            "type": "FeatureCollection",
            "name": self.title,
            "features": features,
        }
