# -*- coding: utf-8 -*-
"""Interactive Scroll-Driven Narrative Scrollytelling Map for multilayer."""

from __future__ import annotations

import html
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence


@dataclass
class StoryChapter:
    chapter_id: str
    title: str
    narrative_markdown: str
    camera_center_lat: float
    camera_center_lon: float
    camera_zoom: int = 14
    active_layer_opacity: float = 1.0


@dataclass
class StoryMapScroller:
    """Scroll-driven multi-panel spatial narrative experience."""

    story_title: str = "Urban Evolution Story"
    subtitle: str = "A deep spatial journey through our masterplan"
    chapters: list[StoryChapter] = field(default_factory=list)

    def add_chapter(
        self,
        chapter_id: str,
        title: str,
        narrative: str,
        lat: float,
        lon: float,
        zoom: int = 14,
    ) -> None:
        self.chapters.append(
            StoryChapter(
                chapter_id=chapter_id,
                title=title,
                narrative_markdown=narrative,
                camera_center_lat=lat,
                camera_center_lon=lon,
                camera_zoom=zoom,
            )
        )

    def render_html(self) -> str:
        chapters_json = json.dumps([
            {
                "id": ch.chapter_id,
                "title": ch.title,
                "lat": ch.camera_center_lat,
                "lon": ch.camera_center_lon,
                "zoom": ch.camera_zoom,
            }
            for ch in self.chapters
        ])

        cards_html = []
        for idx, ch in enumerate(self.chapters):
            safe_title = html.escape(ch.title)
            safe_body = html.escape(ch.narrative_markdown).replace("\n", "<br>")
            cards_html.append(f"""    <section class="step" data-step="{idx}" id="{ch.chapter_id}">
      <div class="card">
        <h2>{safe_title}</h2>
        <p>{safe_body}</p>
      </div>
    </section>""")

        joined_cards = "\n".join(cards_html)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self.story_title}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body, html {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0b0f19; color: #fff; }}
    #map-fixed {{ position: fixed; top: 0; left: 0; width: 100%; height: 100vh; z-index: 1; }}
    #story-scroll {{ position: relative; z-index: 10; width: 420px; margin-left: 40px; pointer-events: none; }}
    .step {{ min-height: 90vh; display: flex; align-items: center; padding: 20px 0; }}
    .card {{ background: rgba(15, 23, 42, 0.88); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.12); padding: 24px; border-radius: 12px; pointer-events: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }}
    .card h2 {{ margin: 0 0 10px 0; font-size: 1.25rem; color: #38bdf8; }}
    .card p {{ font-size: 0.9rem; line-height: 1.5; color: #cbd5e1; }}
  </style>
</head>
<body>
  <div id="map-fixed"></div>
  <div id="story-scroll">
{joined_cards}
  </div>

  <script>
    const chapters = {chapters_json};
    const map = L.map('map-fixed', {{ zoomControl: false }}).setView([chapters[0].lat, chapters[0].lon], chapters[0].zoom);
    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{ maxZoom: 19 }}).addTo(map);

    // Scroll observer
    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          const idx = parseInt(entry.target.getAttribute('data-step'), 10);
          const ch = chapters[idx];
          map.flyTo([ch.lat, ch.lon], ch.zoom, {{ duration: 1.8 }});
        }}
      }});
    }}, {{ threshold: 0.6 }});

    document.querySelectorAll('.step').forEach(step => observer.observe(step));
  </script>
</body>
</html>"""

    def save_html(self, output_path: str | Path) -> Path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(self.render_html(), encoding="utf-8")
        return out
