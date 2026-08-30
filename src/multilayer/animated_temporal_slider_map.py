# -*- coding: utf-8 -*-
"""Interactive Time-Series Temporal Range Slider Map for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class TimeSliderFrame:
    timestamp_label: str  # e.g., "2020", "2021", "2022"
    geojson_data: dict[str, Any]
    point_count: int
    summary_metric: float = 0.0


@dataclass
class TemporalRangeSliderMap:
    title: str = "Temporal Time-Series Map"
    center_lat: float = 41.0082
    center_lon: float = 28.9784
    initial_zoom: int = 12
    playback_speed_ms: int = 800
    frames: list[TimeSliderFrame] = field(default_factory=list)

    def add_frame(
        self,
        timestamp_label: str,
        geojson_data: dict[str, Any],
        summary_metric: float = 0.0,
    ) -> None:
        features = geojson_data.get("features", [])
        self.frames.append(
            TimeSliderFrame(
                timestamp_label=timestamp_label,
                geojson_data=geojson_data,
                point_count=len(features),
                summary_metric=summary_metric,
            )
        )

    def to_html(self) -> str:
        frames_json = json.dumps([
            {
                "label": f.timestamp_label,
                "data": f.geojson_data,
                "metric": f.summary_metric,
            }
            for f in self.frames
        ])

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{self.title}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <style>
    body, html {{ margin: 0; padding: 0; height: 100%; font-family: system-ui, sans-serif; }}
    #map {{ width: 100%; height: calc(100% - 70px); }}
    #timeline-bar {{ height: 70px; background: #0f172a; color: white; display: flex; align-items: center; justify-content: center; gap: 16px; padding: 0 20px; }}
    #slider {{ width: 50%; }}
    .badge {{ background: #3b82f6; padding: 4px 12px; border-radius: 9999px; font-weight: bold; }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div id="timeline-bar">
    <button id="btn-play" style="background:#22c55e; color:white; border:none; padding:8px 16px; border-radius:6px; cursor:pointer;">▶ Play</button>
    <input type="range" id="slider" min="0" max="{max(0, len(self.frames) - 1)}" value="0" />
    <span class="badge" id="frame-label">{self.frames[0].timestamp_label if self.frames else 'N/A'}</span>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const frames = {frames_json};
    const map = L.map('map').setView([{self.center_lat}, {self.center_lon}], {self.initial_zoom});
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);

    let currentLayer = null;
    function renderFrame(idx) {{
      if (!frames[idx]) return;
      if (currentLayer) map.removeLayer(currentLayer);
      currentLayer = L.geoJSON(frames[idx].data).addTo(map);
      document.getElementById('frame-label').innerText = frames[idx].label;
    }}
    if (frames.length > 0) renderFrame(0);
  </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
        return out


def export_time_slider_html(
    frames_dict: Sequence[tuple[str, dict[str, Any]]],
    output_path: str | Path,
    title: str = "Temporal Time-Series Map",
) -> Path:
    """Utility function to create and save a TemporalRangeSliderMap."""
    slider_map = TemporalRangeSliderMap(title=title)
    for label, data in frames_dict:
        slider_map.add_frame(label, data)
    return slider_map.save_html(output_path)
