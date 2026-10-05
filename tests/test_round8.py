# -*- coding: utf-8 -*-
"""Unit tests for multilayer Round 8 features (Temporal Range Slider & Roller Curtain Map)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import (
    RollerAngleMode,
    RollerCurtainMap,
    TemporalRangeSliderMap,
)


class TestMultiLayerRound8(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_temporal_range_slider_map(self) -> None:
        slider_map = TemporalRangeSliderMap(title="Historical Urban Growth")
        sample_geojson_1 = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [28.9, 41.0]}}],
        }
        sample_geojson_2 = {
            "type": "FeatureCollection",
            "features": [
                {"type": "Feature", "geometry": {"type": "Point", "coordinates": [28.9, 41.0]}},
                {"type": "Feature", "geometry": {"type": "Point", "coordinates": [29.0, 41.1]}},
            ],
        }

        slider_map.add_frame("2020", sample_geojson_1, summary_metric=100.0)
        slider_map.add_frame("2025", sample_geojson_2, summary_metric=250.0)

        self.assertEqual(len(slider_map.frames), 2)
        self.assertEqual(slider_map.frames[0].point_count, 1)
        self.assertEqual(slider_map.frames[1].point_count, 2)

        html_path = self.tmp / "temporal_slider.html"
        slider_map.save_html(html_path)
        self.assertTrue(html_path.exists())
        content = html_path.read_text(encoding="utf-8")
        self.assertIn("timeline-bar", content)
        self.assertIn("2020", content)

    def test_roller_curtain_map(self) -> None:
        roller = RollerCurtainMap(
            title="Satellite Comparer",
            mode=RollerAngleMode.DIAGONAL_45,
            left_layer_name="Before",
            right_layer_name="After",
        )

        html_path = self.tmp / "roller_curtain.html"
        roller.save_html(html_path)
        self.assertTrue(html_path.exists())
        content = html_path.read_text(encoding="utf-8")
        self.assertIn("roller-hud", content)
        self.assertIn("diagonal_45", content)
