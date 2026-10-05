# -*- coding: utf-8 -*-
"""2D 3x3 Bivariate Matrix Choropleth Map Visualizer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BivariateMatrixColorRamp:
    # 3x3 matrix colors: row = Var A (low, med, high), col = Var B (low, med, high)
    matrix_3x3: list[list[str]] = field(
        default_factory=lambda: [
            ["#e8e8e8", "#b0d5df", "#64acbe"],  # Low Var A (Low B, Med B, High B)
            ["#e4acac", "#ad9ea5", "#627f8c"],  # Med Var A
            ["#c85a5a", "#985356", "#574249"],  # High Var A
        ]
    )


class BivariateChoroplethMap:
    """Interactive 3x3 Bivariate Matrix Choropleth map generator showing correlation between two spatial variables."""

    def __init__(
        self,
        title: str = "Bivariate Spatial Correlation Map",
        var_a_label: str = "Income Level",
        var_b_label: str = "Flood Hazard Index",
        color_ramp: BivariateMatrixColorRamp | None = None,
    ) -> None:
        self.title = title
        self.var_a_label = var_a_label
        self.var_b_label = var_b_label
        self.color_ramp = color_ramp or BivariateMatrixColorRamp()
        self.features: list[dict[str, Any]] = []

    def add_bivariate_feature(
        self,
        feature_id: str,
        val_a: float,
        val_b: float,
        geometry: dict[str, Any],
        properties: dict[str, Any] | None = None,
    ) -> None:
        props = dict(properties or {})
        props["id"] = feature_id
        props["val_a"] = float(val_a)
        props["val_b"] = float(val_b)
        self.features.append({"type": "Feature", "id": feature_id, "properties": props, "geometry": geometry})

    def classify_and_color_features(self) -> list[dict[str, Any]]:
        """Assign 3x3 quantile matrix color codes to all features."""
        if not self.features:
            return []

        vals_a = sorted(f["properties"]["val_a"] for f in self.features)
        vals_b = sorted(f["properties"]["val_b"] for f in self.features)

        q1_a, q2_a = vals_a[len(vals_a) // 3], vals_a[(2 * len(vals_a)) // 3]
        q1_b, q2_b = vals_b[len(vals_b) // 3], vals_b[(2 * len(vals_b)) // 3]

        for f in self.features:
            va = f["properties"]["val_a"]
            vb = f["properties"]["val_b"]

            row = 0 if va <= q1_a else (1 if va <= q2_a else 2)
            col = 0 if vb <= q1_b else (1 if vb <= q2_b else 2)

            color = self.color_ramp.matrix_3x3[row][col]
            f["properties"]["bivariate_color"] = color
            f["properties"]["bivariate_category"] = f"A{row+1}_B{col+1}"

        return self.features

    def to_html(self) -> str:
        self.classify_and_color_features()
        data_json = json.dumps({"type": "FeatureCollection", "features": self.features})

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
        .bivariate-legend {{
            position: absolute; bottom: 25px; right: 25px; z-index: 1000;
            background: white; padding: 12px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        const map = L.map('map').setView([41.0, 29.0], 11);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
        const geoData = {data_json};
        L.geoJSON(geoData, {{
            style: function(feature) {{
                return {{
                    fillColor: feature.properties.bivariate_color || '#999',
                    weight: 1, color: '#fff', fillOpacity: 0.85
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
