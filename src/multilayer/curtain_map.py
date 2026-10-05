# -*- coding: utf-8 -*-
"""Spatial Split-Slider Curtain Reveal Compare Map for multilayer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class CurtainMap:
    """Side-by-side interactive split-screen curtain slider reveal map."""

    title_left: str = "Pre-Development / Historical Base"
    title_right: str = "Post-Development / New Masterplan"
    left_tile_url: str = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
    right_tile_url: str = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
    center_lat: float = 41.0082
    center_lon: float = 28.9784
    initial_zoom: int = 13
    slider_initial_position_percent: float = 50.0

    def render_html(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Curtain Compare: {self.title_left} vs {self.title_right}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; font-family: -apple-system, sans-serif; }}
    #container {{ position: relative; width: 100%; height: 100%; }}
    .map-pane {{ position: absolute; top: 0; bottom: 0; width: 100%; height: 100%; }}
    #map-left {{ clip-path: polygon(0 0, {self.slider_initial_position_percent}% 0, {self.slider_initial_position_percent}% 100%, 0 100%); z-index: 10; }}
    #map-right {{ z-index: 5; }}
    #slider-bar {{ position: absolute; top: 0; bottom: 0; left: {self.slider_initial_position_percent}%; width: 4px; background: #fff; z-index: 30; cursor: ew-resize; box-shadow: 0 0 10px rgba(0,0,0,0.5); }}
    #slider-handle {{ position: absolute; top: 50%; left: -18px; width: 40px; height: 40px; border-radius: 50%; background: #2563eb; color: #fff; display: flex; align-items: center; justify-content: center; transform: translateY(-50%); box-shadow: 0 4px 12px rgba(0,0,0,0.3); font-weight: bold; user-select: none; }}
    .curtain-label {{ position: absolute; bottom: 20px; z-index: 40; padding: 8px 16px; border-radius: 6px; font-weight: 600; font-size: 14px; backdrop-filter: blur(8px); }}
    .label-left {{ left: 20px; background: rgba(255,255,255,0.85); color: #1e293b; }}
    .label-right {{ right: 20px; background: rgba(15,23,42,0.85); color: #f8fafc; }}
  </style>
</head>
<body>
  <div id="container">
    <div id="map-left" class="map-pane"></div>
    <div id="map-right" class="map-pane"></div>
    <div id="slider-bar">
      <div id="slider-handle">⟷</div>
    </div>
    <div class="curtain-label label-left">{self.title_left}</div>
    <div class="curtain-label label-right">{self.title_right}</div>
  </div>

  <script>
    const mapLeft = L.map('map-left', {{ zoomControl: false }}).setView([{self.center_lat}, {self.center_lon}], {self.initial_zoom});
    const mapRight = L.map('map-right').setView([{self.center_lat}, {self.center_lon}], {self.initial_zoom});

    L.tileLayer('{self.left_tile_url}', {{ maxZoom: 19 }}).addTo(mapLeft);
    L.tileLayer('{self.right_tile_url}', {{ maxZoom: 19 }}).addTo(mapRight);

    // Sync cameras
    let syncing = false;
    function syncMaps(source, target) {{
      if (syncing) return;
      syncing = true;
      target.setView(source.getCenter(), source.getZoom(), {{ animate: false }});
      syncing = false;
    }}
    mapLeft.on('move', () => syncMaps(mapLeft, mapRight));
    mapRight.on('move', () => syncMaps(mapRight, mapLeft));

    // Slider Dragging
    const slider = document.getElementById('slider-bar');
    const leftPane = document.getElementById('map-left');
    let isDragging = false;

    slider.addEventListener('mousedown', () => isDragging = true);
    window.addEventListener('mouseup', () => isDragging = false);
    window.addEventListener('mousemove', (e) => {{
      if (!isDragging) return;
      const pct = Math.max(0, Math.min(100, (e.clientX / window.innerWidth) * 100));
      slider.style.left = pct + '%';
      leftPane.style.clipPath = `polygon(0 0, ${{pct}}% 0, ${{pct}}% 100%, 0 100%)`;
    }});
  </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.render_html(), encoding="utf-8")
        return out
