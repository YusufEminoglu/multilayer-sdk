# -*- coding: utf-8 -*-
"""Unit tests for multilayer Round 7 features (Quad Sync Map & Curved Flow Arcs)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import (
    CurvedFlowMap,
    FlowArc3D,
    QuadPanelConfig,
    QuadSyncMap,
)


class TestMultilayerRound7(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_quad_sync_map(self) -> None:
        panels = [
            QuadPanelConfig("Street", "https://tile.a.org/{z}/{x}/{y}.png"),
            QuadPanelConfig("Satellite", "https://tile.b.org/{z}/{x}/{y}.png"),
            QuadPanelConfig("Zoning", "https://tile.c.org/{z}/{x}/{y}.png"),
            QuadPanelConfig("Flood", "https://tile.d.org/{z}/{x}/{y}.png"),
        ]
        quad = QuadSyncMap(title="Comparative Urban Resilience", panels=panels)

        html_path = self.tmp / "quad.html"
        quad.save_html(html_path)
        self.assertTrue(html_path.exists())
        content = html_path.read_text(encoding="utf-8")
        self.assertIn("quad-grid", content)
        self.assertIn("map_0", content)
        self.assertIn("map_3", content)
        self.assertIn("isSyncing", content)

    def test_curved_flow_arcs(self) -> None:
        flow_map = CurvedFlowMap(title="Commuter Corridor Arcs")
        flow_map.add_flow("Flow_Ankara_Istanbul", (39.93, 32.85), (41.01, 28.97), flow_volume=12.5)
        flow_map.add_flow("Flow_Izmir_Istanbul", (38.42, 27.14), (41.01, 28.97), flow_volume=8.0)

        self.assertEqual(len(flow_map.flows), 2)
        geojson = flow_map.to_geojson()
        self.assertEqual(geojson["type"], "FeatureCollection")
        self.assertEqual(len(geojson["features"]), 2)
        self.assertGreater(len(geojson["features"][0]["geometry"]["coordinates"]), 5)

        html_path = self.tmp / "flows.html"
        flow_map.save_html(html_path)
        self.assertTrue(html_path.exists())
        self.assertIn("flow-lines", html_path.read_text(encoding="utf-8"))
