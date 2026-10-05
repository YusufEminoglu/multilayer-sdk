# -*- coding: utf-8 -*-
"""Unit tests for multilayer Round 10 features (Isochrone Bubble Map & Hypso Relief Contours)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import (
    HypsoTintedReliefMap,
    TravelIsochroneBubbleMap,
)


class TestMultiLayerRound10(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_travel_isochrone_bubble_map(self) -> None:
        b_map = TravelIsochroneBubbleMap(title="15-Minute City Paris", center_lat_lon=(48.85, 2.35))
        poly = {"type": "Polygon", "coordinates": [[[2.30, 48.80], [2.40, 48.80], [2.40, 48.90], [2.30, 48.90], [2.30, 48.80]]]}

        b_map.add_isochrone_ring(15, poly, mode="WALK")
        b_map.add_isochrone_ring(30, poly, mode="TRANSIT")

        self.assertEqual(len(b_map.rings), 2)
        html = b_map.to_html()
        self.assertIn("15-Minute City Paris", html)

        out_path = self.tmp / "bubble.html"
        b_map.save_html(out_path)
        self.assertTrue(out_path.exists())

    def test_hypso_tinted_relief_map(self) -> None:
        r_map = HypsoTintedReliefMap(title="Alps Topographic Relief")
        path1 = [(45.0, 6.0), (45.1, 6.1), (45.2, 6.2)]
        path2 = [(45.0, 6.1), (45.1, 6.2), (45.2, 6.3)]

        r_map.add_contour_line(elevation_m=100.0, coordinates_path=path1)
        r_map.add_contour_line(elevation_m=500.0, coordinates_path=path2)

        self.assertEqual(len(r_map.contour_lines), 2)
        html = r_map.to_html()
        self.assertIn("Alps Topographic Relief", html)

        out_path = self.tmp / "relief.html"
        r_map.save_html(out_path)
        self.assertTrue(out_path.exists())
