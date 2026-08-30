# -*- coding: utf-8 -*-
"""Unit tests for multilayer Round 5 features (Hexbin Heatmap & StoryMap Scroller)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import (
    HexbinHeatmapLayer,
    StoryChapter,
    StoryMapScroller,
    aggregate_points_to_hexbins,
)


class TestMultilayerRound5(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_hexbin_aggregation(self) -> None:
        pts = [
            (41.008, 28.978),
            (41.009, 28.979),
            (41.010, 28.980),
            (41.050, 29.020),
        ]
        vals = [10.0, 20.0, 30.0, 50.0]

        hex_layer = aggregate_points_to_hexbins(pts, point_values=vals, hex_radius_m=1000.0, statistic="MEAN")
        self.assertIsInstance(hex_layer, HexbinHeatmapLayer)
        self.assertGreater(hex_layer.total_hexagons, 0)
        self.assertEqual(len(hex_layer.cells), hex_layer.total_hexagons)

        geojson = hex_layer.to_geojson()
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertGreater(len(geojson["features"]), 0)

    def test_storymap_scroller(self) -> None:
        sm = StoryMapScroller(story_title="Istanbul Masterplan 2030")
        sm.add_chapter("ch1", "Historical Center", "Exploring the historic peninsula.", 41.008, 28.978, zoom=15)
        sm.add_chapter("ch2", "New Financial District", "Rapid growth in the financial corridor.", 41.080, 29.010, zoom=14)

        self.assertEqual(len(sm.chapters), 2)
        html_file = self.tmp / "storymap.html"
        sm.save_html(html_file)

        self.assertTrue(html_file.exists())
        content = html_file.read_text(encoding="utf-8")
        self.assertIn("Historical Center", content)
        self.assertIn("IntersectionObserver", content)
