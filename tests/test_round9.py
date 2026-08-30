# -*- coding: utf-8 -*-
"""Unit tests for multilayer Round 9 features (Bivariate Choropleth & Vector Wind Streamlines)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import (
    BivariateChoroplethMap,
    BivariateMatrixColorRamp,
    WindParticleFieldMap,
    WindParticleParams,
)


class TestMultiLayerRound9(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_bivariate_choropleth_map(self) -> None:
        b_map = BivariateChoroplethMap(title="Demographic Vulnerability", var_a_label="Poverty", var_b_label="Flood")
        geom = {"type": "Polygon", "coordinates": [[[29.0, 41.0], [29.1, 41.0], [29.1, 41.1], [29.0, 41.1], [29.0, 41.0]]]}

        b_map.add_bivariate_feature("Zone1", val_a=15.0, val_b=20.0, geometry=geom)
        b_map.add_bivariate_feature("Zone2", val_a=45.0, val_b=85.0, geometry=geom)
        b_map.add_bivariate_feature("Zone3", val_a=90.0, val_b=50.0, geometry=geom)

        features = b_map.classify_and_color_features()
        self.assertEqual(len(features), 3)
        self.assertIn("bivariate_color", features[0]["properties"])
        self.assertIn("bivariate_category", features[0]["properties"])

        html_path = self.tmp / "bivariate.html"
        b_map.save_html(html_path)
        self.assertTrue(html_path.exists())

    def test_vector_wind_streamlines(self) -> None:
        w_map = WindParticleFieldMap(title="Aegean Sea Surface Winds")
        w_map.add_vector_grid_point(lat=38.5, lon=26.5, u_velocity_mps=12.5, v_velocity_mps=-8.0)
        w_map.add_vector_grid_point(lat=39.0, lon=27.0, u_velocity_mps=15.0, v_velocity_mps=-10.0)

        self.assertEqual(len(w_map.vector_grid_cells), 2)
        html = w_map.to_html()
        self.assertIn("Aegean Sea Surface Winds", html)

        out_path = self.tmp / "wind.html"
        w_map.save_html(out_path)
        self.assertTrue(out_path.exists())
