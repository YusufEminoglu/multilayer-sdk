# -*- coding: utf-8 -*-
"""Unit tests for multilayer Round 11 features (Proximity Matrix Heatmap & Pulse Radar POI)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import (
    ProximityMatrixHeatmapMap,
    PulseRadarPoiMap,
    RadarPulseConfig,
)


class TestMultiLayerRound11(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_proximity_matrix_heatmap(self) -> None:
        p_map = ProximityMatrixHeatmapMap(title="Hospital Accessibility Matrix")
        p_map.add_facility("City_Hospital", 41.02, 28.97, "HOSPITAL")
        p_map.add_grid_cell("Cell_1", 41.03, 28.98, 1200.0)

        self.assertEqual(len(p_map.facilities), 1)
        self.assertEqual(len(p_map.grid_cells), 1)
        html = p_map.to_html()
        self.assertIn("Hospital Accessibility Matrix", html)

        out_path = self.tmp / "prox.html"
        p_map.save_html(out_path)
        self.assertTrue(out_path.exists())

    def test_animated_pulse_radar_poi(self) -> None:
        r_map = PulseRadarPoiMap(title="Maritime Beacons", config=RadarPulseConfig(beacon_color_hex="#ff0055"))
        r_map.add_beacon("Lighthouse_A", 41.25, 29.10, "ACTIVE_BEACON")

        self.assertEqual(len(r_map.beacons), 1)
        html = r_map.to_html()
        self.assertIn("Maritime Beacons", html)

        out_path = self.tmp / "radar.html"
        r_map.save_html(out_path)
        self.assertTrue(out_path.exists())
