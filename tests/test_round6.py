# -*- coding: utf-8 -*-
"""Unit tests for multilayer Round 6 features (3D Choropleth Prism Map & Spyglass Comparer)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import (
    Choropleth3DMap,
    LensConfig,
    PrismPolygon3D,
    SpyglassCompareMap,
)


class TestMultilayerRound6(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_3d_choropleth_prism_map(self) -> None:
        c3d = Choropleth3DMap(title="Istanbul Population Density")
        c3d.add_prism("District_Kadikoy", [(40.99, 29.02), (41.00, 29.02), (41.00, 29.04), (40.99, 29.04)], metric_value=450.0, height_scale=0.5)
        c3d.add_prism("District_Besiktas", [(41.04, 29.00), (41.05, 29.00), (41.05, 29.02), (41.04, 29.02)], metric_value=320.0, height_scale=0.5)

        self.assertEqual(len(c3d.prisms), 2)
        geojson = c3d.to_geojson()
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 2)
        self.assertGreater(geojson["features"][0]["properties"]["height"], 100.0)

        html_path = self.tmp / "choropleth3d.html"
        c3d.save_html(html_path)
        self.assertTrue(html_path.exists())
        self.assertIn("maplibregl", html_path.read_text(encoding="utf-8"))

    def test_spyglass_lens_map(self) -> None:
        spy = SpyglassCompareMap(
            title="Satellite vs Street View",
            center_lat=41.008,
            center_lon=28.978,
            lens_config=LensConfig(radius_pixels=180, border_color="#ef4444"),
        )

        html_path = self.tmp / "spyglass.html"
        spy.save_html(html_path)
        self.assertTrue(html_path.exists())
        content = html_path.read_text(encoding="utf-8")
        self.assertIn("lens", content)
        self.assertIn("mousemove", content)
