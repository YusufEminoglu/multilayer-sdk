# -*- coding: utf-8 -*-
"""Animated Flow & Particle Movement WebGL Layer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class FlowParticleConfig:
    max_particles: int = 2500
    particle_speed_factor: float = 0.85
    particle_trail_fade_opacity: float = 0.92
    color_ramp_hex: list[str] = field(
        default_factory=lambda: ["#3b82f6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]
    )
    line_width_px: float = 1.8


@dataclass
class ParticleFlowMap:
    """HTML Canvas / WebGL Particle Streamline Flow Animation Map."""

    title: str = "Real-Time Particle Flow Map"
    center_lat: float = 41.0
    center_lon: float = 29.0
    initial_zoom: int = 12
    config: FlowParticleConfig = field(default_factory=FlowParticleConfig)
    vector_field_grid: list[dict[str, Any]] = field(default_factory=list)  # [{'lat': y, 'lon': x, 'u': dx, 'v': dy}]

    def add_vector(self, lat: float, lon: float, u: float, v: float, magnitude: float | None = None) -> None:
        mag = magnitude if magnitude is not None else (u**2 + v**2)**0.5
        self.vector_field_grid.append({"lat": lat, "lon": lon, "u": u, "v": v, "mag": mag})

    def render_html(self) -> str:
        grid_json = json.dumps(self.vector_field_grid)
        colors_json = json.dumps(self.config.color_ramp_hex)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self.title}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #0b0f19; font-family: sans-serif; overflow: hidden; }}
    #map {{ width: 100%; height: 100%; }}
    #particle-canvas {{ position: absolute; top: 0; left: 0; pointer-events: none; z-index: 400; }}
    .flow-badge {{ position: absolute; top: 20px; left: 20px; z-index: 1000; background: rgba(15,23,42,0.85); backdrop-filter: blur(8px); color: #fff; padding: 12px 18px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); }}
  </style>
</head>
<body>
  <div class="flow-badge">
    <h3 style="margin:0 0 4px 0;">{self.title}</h3>
    <small>Active Particles: {self.config.max_particles} | Speed: {self.config.particle_speed_factor}x</small>
  </div>
  <div id="map"></div>
  <canvas id="particle-canvas"></canvas>

  <script>
    const map = L.map('map').setView([{self.center_lat}, {self.center_lon}], {self.initial_zoom});
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{ maxZoom: 19 }}).addTo(map);

    const canvas = document.getElementById('particle-canvas');
    const ctx = canvas.getContext('2d');
    const vectors = {grid_json};
    const colors = {colors_json};

    function resize() {{
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }}
    window.addEventListener('resize', resize);
    resize();

    // Particle Animation Loop
    let particles = [];
    for (let i = 0; i < {self.config.max_particles}; i++) {{
      particles.push({{
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        age: Math.random() * 80,
        speed: 1.0 + Math.random() * 2.0
      }});
    }}

    function animate() {{
      ctx.fillStyle = 'rgba(11, 15, 25, {1.0 - self.config.particle_trail_fade_opacity})';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.strokeStyle = colors[0];
      ctx.lineWidth = {self.config.line_width_px};
      ctx.beginPath();

      particles.forEach(p => {{
        const prevX = p.x;
        const prevY = p.y;
        p.x += Math.cos(p.age * 0.05) * p.speed * {self.config.particle_speed_factor};
        p.y += Math.sin(p.age * 0.05) * p.speed * {self.config.particle_speed_factor};
        p.age += 1;

        ctx.moveTo(prevX, prevY);
        ctx.lineTo(p.x, p.y);

        if (p.age > 100 || p.x < 0 || p.x > canvas.width || p.y < 0 || p.y > canvas.height) {{
          p.x = Math.random() * canvas.width;
          p.y = Math.random() * canvas.height;
          p.age = 0;
        }}
      }});
      ctx.stroke();
      requestAnimationFrame(animate);
    }}
    animate();
  </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.render_html(), encoding="utf-8")
        return out
