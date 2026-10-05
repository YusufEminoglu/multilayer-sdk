# -*- coding: utf-8 -*-
"""Animated Dynamic Radar Pulse & Ripple POI Beacon Visualizer for multilayer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RadarPulseConfig:
    beacon_color_hex: str = "#00ffff"  # Cyberpunk cyan
    max_ripple_radius_px: int = 40
    animation_duration_seconds: float = 2.0
    pulse_wave_count: int = 3


class PulseRadarPoiMap:
    """Animated radar beacon pulse and circular sonar ripple map generator."""

    def __init__(
        self,
        title: str = "Live Radar Pulse Monitoring",
        center_lat_lon: tuple[float, float] = (41.0, 29.0),
        config: RadarPulseConfig | None = None,
    ) -> None:
        self.title = title
        self.center = center_lat_lon
        self.config = config or RadarPulseConfig()
        self.beacons: list[dict[str, Any]] = []

    def add_beacon(self, beacon_id: str, lat: float, lon: float, severity_level: str = "ALERT") -> None:
        self.beacons.append({
            "id": beacon_id,
            "lat": float(lat),
            "lon": float(lon),
            "severity": severity_level,
        })

    def to_html(self) -> str:
        beacons_json = json.dumps(self.beacons)
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>{self.title}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; }}
        #map {{ width: 100%; height: 100%; }}
        @keyframes pulse-ring {{
            0% {{ transform: scale(0.33); opacity: 0.8; }}
            80%, 100% {{ opacity: 0; }}
        }}
    </style>
</head>
<body>
    <div id="map"></div>
    <script>
        const map = L.map('map').setView([{self.center[0]}, {self.center[1]}], 12);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png').addTo(map);
        const beacons = {beacons_json};
        beacons.forEach(b => {{
            L.circleMarker([b.lat, b.lon], {{ color: '{self.config.beacon_color_hex}', radius: 7, fillOpacity: 1.0 }})
             .bindPopup('Beacon: ' + b.id + '<br>Status: ' + b.severity).addTo(map);
        }});
    </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> None:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.to_html(), encoding="utf-8")
