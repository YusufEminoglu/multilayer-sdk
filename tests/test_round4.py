# -*- coding: utf-8 -*-
"""Unit tests for multilayer Round 4 features (Particle Flow Map & Curtain Compare Map)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from multilayer import CurtainMap, FlowParticleConfig, ParticleFlowMap


class TestMultilayerRound4(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_particle_flow_map(self) -> None:
        p_map = ParticleFlowMap(title="Wind Trajectories", center_lat=39.0, center_lon=35.0)
        p_map.add_vector(39.1, 35.2, u=2.5, v=-1.2)
        p_map.add_vector(39.3, 35.5, u=3.1, v=0.5)

        html_file = self.tmp / "particles.html"
        p_map.save_html(html_file)
        self.assertTrue(html_file.exists())
        self.assertIn("particle-canvas", html_file.read_text(encoding="utf-8"))

    def test_curtain_compare_map(self) -> None:
        c_map = CurtainMap(title_left="Satellite 2020", title_right="Satellite 2026")
        html_file = self.tmp / "curtain.html"
        c_map.save_html(html_file)
        self.assertTrue(html_file.exists())
        self.assertIn("slider-handle", html_file.read_text(encoding="utf-8"))
