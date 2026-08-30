# -*- coding: utf-8 -*-
"""Unit tests for multilayer Rounds 2 and 3 features (Globe3D, Spatial Query, DiffMap, Atlas)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import (
    AtlasGridSheet,
    DiffMap,
    Globe3DMap,
    MultiPageAtlas,
    RadialSearchMap,
    SpatialDiffResult,
    TerrainPanel3D,
)


class TestMultilayerRounds2And3(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_globe3d_rendering(self) -> None:
        g = Globe3DMap(layout="dual-horizontal")
        g.add_panel(TerrainPanel3D(title="Istanbul 3D", camera_lat=41.0, camera_lon=29.0))
        g.add_panel(TerrainPanel3D(title="Ankara 3D", camera_lat=39.9, camera_lon=32.8))

        html_file = self.tmp / "globe.html"
        g.save_html(html_file)
        self.assertTrue(html_file.exists())
        self.assertIn("Istanbul 3D", html_file.read_text(encoding="utf-8"))

    def test_radial_search_map(self) -> None:
        r_map = RadialSearchMap(center_lat=41.0, center_lon=29.0, initial_radius_meters=1500.0)
        html_file = self.tmp / "radial.html"
        r_map.save_html(html_file)
        self.assertTrue(html_file.exists())
        self.assertIn("radius-slider", html_file.read_text(encoding="utf-8"))

    def test_diff_map_rendering(self) -> None:
        d_map = DiffMap(title_a="Plan 2020", title_b="Plan 2026")
        html_file = self.tmp / "diff.html"
        d_map.save_html(html_file)
        self.assertTrue(html_file.exists())
        self.assertIn("Plan 2020", html_file.read_text(encoding="utf-8"))

    def test_multipage_atlas_generator(self) -> None:
        atlas = MultiPageAtlas(title="Regional Plan Atlas", rows=2, cols=3)
        sheets = atlas.generate_grid_index()

        self.assertEqual(len(sheets), 6)
        self.assertEqual(sheets[0].sheet_number, 1)

        geojson = atlas.to_geojson_index()
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 6)
