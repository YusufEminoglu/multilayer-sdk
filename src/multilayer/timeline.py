# -*- coding: utf-8 -*-
"""Time-Series Temporal Animator & Step-by-Step Scenario Player for multilayer-sdk."""

from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .grid import GridLayout
from .layers import VectorLayer, get_tile_provider


@dataclass
class TimeFrame:
    """A single time step or scenario frame containing spatial layers for each panel."""

    label: str
    timestamp: str = ""
    description: str = ""
    panel_layers: dict[int, list[VectorLayer]] = field(default_factory=dict)

    def add_layer(self, panel_index: int, layer: VectorLayer) -> "TimeFrame":
        if panel_index not in self.panel_layers:
            self.panel_layers[panel_index] = []
        self.panel_layers[panel_index].append(layer)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "description": self.description,
            "panels": {
                str(p_idx): [
                    {
                        "name": lyr.name,
                        "data": lyr.data,
                        "fill_color": lyr.fill_color,
                        "stroke_color": lyr.stroke_color,
                        "fill_opacity": lyr.fill_opacity,
                        "stroke_width": lyr.stroke_width,
                    }
                    for lyr in lyrs
                ]
                for p_idx, lyrs in self.panel_layers.items()
            },
        }


class TimelineMap:
    """Synchronized Multi-Panel Time-Series Map Animator and Scenario Player."""

    def __init__(
        self,
        grid: str | GridLayout = "1x2",
        title: str = "Time-Series Spatial Evolution",
        basemap: str = "carto-dark",
        fps: float = 1.0,
    ) -> None:
        self.layout = GridLayout.from_string(grid) if isinstance(grid, str) else grid
        self.title = title
        self.basemap = basemap
        self.fps = fps
        self.frames: list[TimeFrame] = []
        self.panel_titles: list[str] = [f"Panel {i+1}" for i in range(self.layout.panel_count)]

    def set_panel_title(self, panel_index: int, title: str) -> None:
        if 0 <= panel_index < len(self.panel_titles):
            self.panel_titles[panel_index] = title

    def add_frame(self, frame: TimeFrame) -> "TimelineMap":
        self.frames.append(frame)
        return self

    def create_frame(self, label: str, timestamp: str = "", description: str = "") -> TimeFrame:
        frame = TimeFrame(label=label, timestamp=timestamp, description=description)
        self.frames.append(frame)
        return frame

    def to_html(self, output_path: str | Path | None = None) -> str:
        """Compile the interactive timeline animation player to standalone HTML."""
        tile_prov = get_tile_provider(self.basemap)
        frames_payload = [f.to_dict() for f in self.frames]
        frames_json = json.dumps(frames_payload, ensure_ascii=False)
        panel_count = self.layout.panel_count

        # Compute initial center and zoom from layers
        center_lon, center_lat = 0.0, 20.0
        zoom = 2
        for f in self.frames:
            for lyrs in f.panel_layers.values():
                for lyr in lyrs:
                    bounds = lyr.get_bounds()
                    if bounds:
                        min_x, min_y, max_x, max_y = bounds
                        center_lon = (min_x + max_x) / 2.0
                        center_lat = (min_y + max_y) / 2.0
                        zoom = 12
                        break

        panel_divs = []
        for i in range(panel_count):
            p_title = html.escape(self.panel_titles[i] if i < len(self.panel_titles) else f"Panel {i+1}")
            div = f"""
            <div class="map-card" style="flex: 1; position: relative; min-width: 0; min-height: 0;">
                <div class="panel-header">{p_title}</div>
                <div id="map-panel-{i}" class="map-container" style="width: 100%; height: 100%;"></div>
            </div>"""
            panel_divs.append(div)

        joined_panels = "\n".join(panel_divs)
        grid_css = f"grid-template-columns: repeat({self.layout.cols}, 1fr); grid-template-rows: repeat({self.layout.rows}, 1fr);"

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(self.title)}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        body, html {{ width: 100%; height: 100%; overflow: hidden; background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; }}
        header {{ height: 50px; background: #1e293b; display: flex; align-items: center; justify-content: space-between; padding: 0 1.5rem; border-bottom: 1px solid #334155; }}
        header h1 {{ font-size: 1.1rem; font-weight: 600; color: #38bdf8; }}
        #grid-container {{ flex: 1; display: grid; {grid_css} gap: 6px; padding: 6px; }}
        .map-card {{ background: #000; border-radius: 6px; overflow: hidden; border: 1px solid #334155; display: flex; flex-direction: column; }}
        .panel-header {{ background: rgba(15, 23, 42, 0.85); padding: 4px 10px; font-size: 0.8rem; font-weight: 600; z-index: 1000; color: #94a3b8; border-bottom: 1px solid #334155; }}
        #timeline-controls {{ height: 60px; background: #1e293b; border-top: 1px solid #334155; display: flex; align-items: center; padding: 0 1.5rem; gap: 1rem; z-index: 2000; }}
        .btn {{ background: #0284c7; color: white; border: none; padding: 6px 14px; border-radius: 4px; font-weight: 600; cursor: pointer; }}
        .btn:hover {{ background: #0369a1; }}
        #scrubber {{ flex: 1; accent-color: #38bdf8; cursor: pointer; }}
        #frame-badge {{ background: #334155; padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; font-weight: bold; color: #38bdf8; min-width: 140px; text-align: center; }}
    </style>
</head>
<body>
    <header>
        <h1>{html.escape(self.title)}</h1>
        <div id="status-bar" style="font-size: 0.85rem; color: #94a3b8;">Frames: {len(self.frames)} | Multi-Panel Synced</div>
    </header>
    <div id="grid-container">
        {joined_panels}
    </div>
    <div id="timeline-controls">
        <button id="play-btn" class="btn">▶ Play</button>
        <button id="prev-btn" class="btn" style="background: #475569;">⏮</button>
        <button id="next-btn" class="btn" style="background: #475569;">⏭</button>
        <input type="range" id="scrubber" min="0" max="{max(0, len(self.frames) - 1)}" value="0" step="1">
        <div id="frame-badge">Frame 1/{len(self.frames)}</div>
    </div>

    <script>
        const frames = {frames_json};
        const panelCount = {panel_count};
        const tileUrl = "{tile_prov.url_template}";
        const tileAttr = "{tile_prov.attribution}";

        const maps = [];
        const geojsonLayers = Array.from({{ length: panelCount }}, () => []);
        let currentFrameIdx = 0;
        let isPlaying = false;
        let playTimer = null;

        for (let i = 0; i < panelCount; i++) {{
            const m = L.map('map-panel-' + i, {{ zoomControl: (i === 0) }}).setView([{center_lat}, {center_lon}], {zoom});
            L.tileLayer(tileUrl, {{ attribution: tileAttr, maxZoom: 19 }}).addTo(m);
            maps.push(m);

            m.on('move', () => {{
                if (m._syncing) return;
                const c = m.getCenter();
                const z = m.getZoom();
                maps.forEach((other, oIdx) => {{
                    if (oIdx !== i) {{
                        other._syncing = true;
                        other.setView(c, z, {{ animate: false }});
                        other._syncing = false;
                    }}
                }});
            }});
        }}

        function renderFrame(idx) {{
            if (idx < 0 || idx >= frames.length) return;
            currentFrameIdx = idx;
            const frame = frames[idx];
            document.getElementById('scrubber').value = idx;
            document.getElementById('frame-badge').textContent = (frame.label || 'Step ' + (idx + 1)) + (frame.timestamp ? ' (' + frame.timestamp + ')' : '');

            for (let p = 0; p < panelCount; p++) {{
                geojsonLayers[p].forEach(l => maps[p].removeLayer(l));
                geojsonLayers[p] = [];

                const pLayers = (frame.panels && frame.panels[p]) || [];
                pLayers.forEach(lyr => {{
                    if (lyr.data) {{
                        const gl = L.geoJSON(lyr.data, {{
                            style: (feat) => ({{
                                fillColor: feat.properties?._multilayer_fill_color || lyr.fill_color || '#38bdf8',
                                fillOpacity: lyr.fill_opacity || 0.7,
                                color: lyr.stroke_color || '#0284c7',
                                weight: lyr.stroke_width || 1.5
                            }})
                        }}).addTo(maps[p]);
                        geojsonLayers[p].push(gl);
                    }}
                }});
            }}
        }}

        const playBtn = document.getElementById('play-btn');
        playBtn.addEventListener('click', () => {{
            if (isPlaying) {{
                isPlaying = false;
                playBtn.textContent = '▶ Play';
                clearInterval(playTimer);
            }} else {{
                isPlaying = true;
                playBtn.textContent = '⏸ Pause';
                playTimer = setInterval(() => {{
                    currentFrameIdx = (currentFrameIdx + 1) % frames.length;
                    renderFrame(currentFrameIdx);
                }}, 1000 / {self.fps});
            }}
        }});

        document.getElementById('scrubber').addEventListener('input', (e) => {{
            renderFrame(parseInt(e.target.value, 10));
        }});

        document.getElementById('prev-btn').addEventListener('click', () => {{
            renderFrame(Math.max(0, currentFrameIdx - 1));
        }});

        document.getElementById('next-btn').addEventListener('click', () => {{
            renderFrame(Math.min(frames.length - 1, currentFrameIdx + 1));
        }});

        if (frames.length > 0) {{
            renderFrame(0);
        }}
    </script>
</body>
</html>"""

        if output_path is not None:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(html_content, encoding="utf-8")

        return html_content
