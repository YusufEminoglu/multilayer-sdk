# -*- coding: utf-8 -*-
"""Standalone, self-contained interactive HTML dashboard builder for MultiMap."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from multilayer.core import MultiMap, SwipeMap


def build_multimap_html(multimap: MultiMap) -> str:
    """Compile MultiMap instance into a single self-contained interactive HTML dashboard."""
    grid = multimap.grid
    panels_data: list[dict[str, Any]] = []

    for idx, panel in enumerate(multimap.panels):
        p_dict = panel.to_dict()
        p_dict["id"] = f"map-panel-{idx}"
        p_dict["index"] = idx
        panels_data.append(p_dict)

    # Initial view bounds / center
    bounds = multimap.get_bounds()
    center_lat, center_lon, initial_zoom = 38.4237, 27.1428, 13  # Default fallback (Izmir)
    if bounds:
        min_lon, min_lat, max_lon, max_lat = bounds
        center_lat = (min_lat + max_lat) / 2.0
        center_lon = (min_lon + max_lon) / 2.0

    if multimap.initial_center:
        center_lat, center_lon = multimap.initial_center
    if multimap.initial_zoom:
        initial_zoom = multimap.initial_zoom

    panels_json = json.dumps(panels_data, ensure_ascii=False)
    bounds_json = json.dumps(bounds) if bounds else "null"

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="{multimap.theme}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="generator" content="multilayer-sdk">
<title>{multimap.title}</title>

<!-- Leaflet CSS & JS CDN -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>

<style>
:root {{
  --bg-app: #08111a;
  --bg-header: #0d1e2e;
  --bg-panel: #0a1622;
  --border: #1e293b;
  --border-active: #10b981;
  --fg: #f1f5f9;
  --fg-muted: #94a3b8;
  --accent: #10b981;
  --accent-cyan: #06b6d4;
  --laser-color: #ef4444;
  --laser-glow: rgba(239, 68, 68, 0.45);
}}

[data-theme="light"] {{
  --bg-app: #f1f5f9;
  --bg-header: #ffffff;
  --bg-panel: #ffffff;
  --border: #cbd5e1;
  --border-active: #059669;
  --fg: #1e293b;
  --fg-muted: #64748b;
  --accent: #059669;
  --accent-cyan: #0891b2;
  --laser-color: #dc2626;
  --laser-glow: rgba(220, 38, 38, 0.4);
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100%; height: 100%; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg-app); color: var(--fg); }}

#app-container {{
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
}}

/* Top Control Bar */
#top-bar {{
  height: 52px;
  background: var(--bg-header);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}}

.brand-title {{
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--fg);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}}

.brand-badge {{
  background: linear-gradient(135deg, var(--accent), var(--accent-cyan));
  color: #08111a;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
}}

.actions-group {{
  display: flex;
  align-items: center;
  gap: 0.5rem;
}}

.btn {{
  background: var(--bg-panel);
  border: 1px solid var(--border);
  color: var(--fg);
  padding: 0.35rem 0.7rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  transition: all 0.15s;
}}

.btn:hover {{
  border-color: var(--accent);
  color: var(--accent);
}}

.btn.active {{
  background: rgba(16, 185, 129, 0.15);
  border-color: var(--accent);
  color: var(--accent);
}}

/* MultiMap Grid Layout */
#map-grid {{
  flex: 1;
  display: grid;
  {grid.to_css_grid()}
  gap: 4px;
  background: var(--bg-app);
  padding: 4px;
  position: relative;
}}

.map-cell {{
  position: relative;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}}

.map-cell.active-focus {{
  border-color: var(--border-active);
  box-shadow: 0 0 0 1px var(--border-active);
}}

.map-cell-header {{
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 500;
  background: rgba(10, 22, 34, 0.82);
  backdrop-filter: blur(8px);
  padding: 0.3rem 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  font-size: 0.82rem;
  font-weight: 600;
  color: #ffffff;
  pointer-events: auto;
  box-shadow: 0 2px 6px rgba(0,0,0,0.4);
}}

[data-theme="light"] .map-cell-header {{
  background: rgba(255, 255, 255, 0.9);
  color: #1e293b;
}}

.map-view {{
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}}

/* Laser Crosshair Markers */
.laser-crosshair {{
  pointer-events: none;
  z-index: 10000;
}}

.laser-dot {{
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--laser-color);
  border: 2px solid #ffffff;
  box-shadow: 0 0 10px var(--laser-glow), 0 0 20px var(--laser-glow);
  transform: translate(-50%, -50%);
}}

/* Coordinate readout footer */
#coord-bar {{
  height: 26px;
  background: var(--bg-header);
  border-top: 1px solid var(--border);
  font-family: monospace;
  font-size: 0.75rem;
  color: var(--fg-muted);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  z-index: 1000;
}}
</style>
</head>
<body>

<div id="app-container">
  <header id="top-bar">
    <div class="brand-title">
      <span class="brand-badge">{grid.preset.value}</span>
      <span>{multimap.title}</span>
    </div>

    <div class="actions-group">
      <button class="btn active" id="syncNavBtn" title="Toggle Synchronized Pan & Zoom">🔗 Sync Nav</button>
      <button class="btn active" id="laserBtn" title="Toggle Laser Pointer Crosshair">🎯 Laser Pointer</button>
      <button class="btn" id="fitBoundsBtn" title="Fit all panels to layer bounds">🔍 Zoom to Extent</button>
      <button class="btn" id="themeBtn" title="Toggle Theme">🌓 Theme</button>
      <button class="btn" id="fullscreenBtn" title="Toggle Fullscreen">⛶ Fullscreen</button>
    </div>
  </header>

  <main id="map-grid">
"""

    # Inject panel containers
    for p in panels_data:
        p_id = p["id"]
        title = p["title"]
        html_content += f"""    <div class="map-cell" id="cell-{p_id}">
      <div class="map-cell-header">{title}</div>
      <div class="map-view" id="{p_id}"></div>
    </div>\n"""

    html_content += f"""  </main>

  <footer id="coord-bar">
    <span id="coordReadout">Lat: {center_lat:.4f} &middot; Lon: {center_lon:.4f} &middot; Zoom: {initial_zoom}</span>
    <span>Synchronized Multi-Panel Map &middot; multilayer-sdk</span>
  </footer>
</div>

<script>
// --- MultiMap Initialization & Synchronization Logic ---
const panelsConfig = {panels_json};
const initialBounds = {bounds_json};
const maps = [];
const laserMarkers = [];
let syncNavActive = true;
let laserActive = true;
let isBroadcasting = false;

// Create Leaflet map instances for each panel
panelsConfig.forEach((cfg, idx) => {{
  const m = L.map(cfg.id, {{
    zoomControl: true,
    attributionControl: true
  }}).setView([{center_lat}, {center_lon}], {initial_zoom});

  // Base Tile Layer
  if (cfg.basemap && cfg.basemap.url_template) {{
    L.tileLayer(cfg.basemap.url_template, {{
      attribution: cfg.basemap.attribution || '',
      maxZoom: cfg.basemap.max_zoom || 20,
      opacity: cfg.basemap.opacity || 1.0
    }}).addTo(m);
  }}

  // Vector Layers
  (cfg.layers || []).forEach(lyr => {{
    if (lyr.type === 'vector' && lyr.data) {{
      L.geoJSON(lyr.data, {{
        style: feature => {{
          const props = feature.properties || {{}};
          return {{
            color: props._multilayer_stroke_color || lyr.stroke_color || '#3388ff',
            weight: props._multilayer_stroke_width || lyr.stroke_width || 1.5,
            opacity: lyr.stroke_opacity || 1.0,
            fillColor: props._multilayer_fill_color || lyr.fill_color || '#3388ff',
            fillOpacity: props._multilayer_fill_opacity !== undefined ? props._multilayer_fill_opacity : (lyr.fill_opacity || 0.6),
            dashArray: lyr.dash_array || null
          }};
        }},
        pointToLayer: (feature, latlng) => {{
          const props = feature.properties || {{}};
          return L.circleMarker(latlng, {{
            radius: lyr.point_radius || 6,
            fillColor: props._multilayer_fill_color || lyr.fill_color || '#3388ff',
            fillOpacity: lyr.fill_opacity || 0.8,
            color: lyr.stroke_color || '#ffffff',
            weight: lyr.stroke_width || 1.5
          }});
        }},
        onEachFeature: (feature, layer) => {{
          const props = feature.properties || {{}};
          if (lyr.tooltip_properties && lyr.tooltip_properties.length > 0) {{
            const rows = lyr.tooltip_properties.map(k => `<strong>${{k}}:</strong> ${{props[k] || ''}}`).join('<br>');
            layer.bindTooltip(rows);
          }}
        }}
      }}).addTo(m);
    }}
  }});

  // Laser Pointer Crosshair Marker
  const laserIcon = L.divIcon({{
    className: 'laser-crosshair',
    html: '<div class="laser-dot"></div>',
    iconSize: [0, 0]
  }});
  const laserMarker = L.marker([0, 0], {{ icon: laserIcon, interactive: false }}).addTo(m);
  laserMarkers.push(laserMarker);

  // Focus Highlight
  const cell = document.getElementById(`cell-${{cfg.id}}`);
  m.on('focus', () => {{
    document.querySelectorAll('.map-cell').forEach(c => c.classList.remove('active-focus'));
    if (cell) cell.classList.add('active-focus');
  }});

  // Synchronized Navigation Broadcaster
  m.on('move', () => {{
    if (!syncNavActive || isBroadcasting) return;
    isBroadcasting = true;
    const center = m.getCenter();
    const zoom = m.getZoom();

    maps.forEach((other, oIdx) => {{
      if (oIdx !== idx) {{
        other.setView(center, zoom, {{ animate: false }});
      }}
    }});

    document.getElementById('coordReadout').innerText = `Lat: ${{center.lat.toFixed(4)}} · Lon: ${{center.lng.toFixed(4)}} · Zoom: ${{zoom}}`;
    isBroadcasting = false;
  }});

  // Laser Pointer Mouse Tracker Broadcaster
  m.on('mousemove', e => {{
    if (!laserActive) return;
    const latlng = e.latlng;
    laserMarkers.forEach(lm => lm.setLatLng(latlng));
    document.getElementById('coordReadout').innerText = `Cursor: Lat ${{latlng.lat.toFixed(5)}} · Lon ${{latlng.lng.toFixed(5)}}`;
  }});

  maps.push(m);
}});

// Fit initial bounds if available
if (initialBounds) {{
  const [minLon, minLat, maxLon, maxLat] = initialBounds;
  const b = L.latLngBounds([minLat, minLon], [maxLat, maxLon]);
  maps.forEach(m => m.fitBounds(b, {{ padding: [20, 20] }}));
}}

// Toolbar Buttons
const syncBtn = document.getElementById('syncNavBtn');
syncBtn.addEventListener('click', () => {{
  syncNavActive = !syncNavActive;
  syncBtn.classList.toggle('active', syncNavActive);
}});

const laserBtn = document.getElementById('laserBtn');
laserBtn.addEventListener('click', () => {{
  laserActive = !laserActive;
  laserBtn.classList.toggle('active', laserActive);
  laserMarkers.forEach(lm => {{
    if (laserActive) lm.setOpacity(1);
    else lm.setOpacity(0);
  }});
}});

document.getElementById('fitBoundsBtn').addEventListener('click', () => {{
  if (initialBounds) {{
    const [minLon, minLat, maxLon, maxLat] = initialBounds;
    const b = L.latLngBounds([minLat, minLon], [maxLat, maxLon]);
    maps.forEach(m => m.fitBounds(b));
  }}
}});

document.getElementById('themeBtn').addEventListener('click', () => {{
  const cur = document.documentElement.getAttribute('data-theme');
  document.documentElement.setAttribute('data-theme', cur === 'light' ? 'dark' : 'light');
}});

document.getElementById('fullscreenBtn').addEventListener('click', () => {{
  if (!document.fullscreenElement) {{
    document.documentElement.requestFullscreen();
  }} else {{
    document.exitFullscreen();
  }}
}});
</script>
</body>
</html>
"""
    return html_content


def build_swipe_map_html(swipe_map: SwipeMap) -> str:
    """Compile a 2-panel curtain swipe split-screen map into self-contained HTML."""
    left_lyr = swipe_map.left_layer.to_dict() if swipe_map.left_layer else None
    right_lyr = swipe_map.right_layer.to_dict() if swipe_map.right_layer else None

    left_json = json.dumps(left_lyr, ensure_ascii=False) if left_lyr else "null"
    right_json = json.dumps(right_lyr, ensure_ascii=False) if right_lyr else "null"

    bounds = swipe_map.get_bounds()
    center_lat, center_lon, zoom = 38.4237, 27.1428, 13
    if bounds:
        min_lon, min_lat, max_lon, max_lat = bounds
        center_lat = (min_lat + max_lat) / 2.0
        center_lon = (min_lon + max_lon) / 2.0

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{swipe_map.title} — Swipe Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body, #map {{ width: 100%; height: 100%; overflow: hidden; }}
#slider {{
  position: absolute;
  top: 0; bottom: 0; left: 50%;
  width: 4px;
  background: #ffffff;
  z-index: 1000;
  cursor: ew-resize;
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
}}
#slider-handle {{
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 40px; height: 40px;
  border-radius: 50%;
  background: #10b981;
  color: #ffffff;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; font-size: 18px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.5);
}}
.label-chip {{
  position: absolute; top: 16px; z-index: 999;
  background: rgba(0,0,0,0.75); color: #fff;
  padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600;
}}
#left-chip {{ left: 16px; }}
#right-chip {{ right: 16px; }}
</style>
</head>
<body>
<div id="left-chip" class="label-chip">{swipe_map.left_title}</div>
<div id="right-chip" class="label-chip">{swipe_map.right_title}</div>
<div id="slider"><div id="slider-handle">⇄</div></div>
<div id="map"></div>

<script>
const map = L.map('map').setView([{center_lat}, {center_lon}], {zoom});
L.tileLayer('{swipe_map.basemap.url_template}', {{ attribution: '{swipe_map.basemap.attribution}' }}).addTo(map);

const leftData = {left_json};
const rightData = {right_json};

let leftLayer, rightLayer;

if (leftData && leftData.data) {{
  leftLayer = L.geoJSON(leftData.data, {{
    style: {{ color: leftData.stroke_color || '#ef4444', fillColor: leftData.fill_color || '#ef4444', fillOpacity: 0.7 }}
  }}).addTo(map);
}}

if (rightData && rightData.data) {{
  rightLayer = L.geoJSON(rightData.data, {{
    style: {{ color: rightData.stroke_color || '#3b82f6', fillColor: rightData.fill_color || '#3b82f6', fillOpacity: 0.7 }}
  }}).addTo(map);
}}

// Slider curtain logic
const slider = document.getElementById('slider');
let isDragging = false;

function updateCurtain(x) {{
  slider.style.left = x + 'px';
  if (leftLayer && leftLayer.getContainer) {{
    const container = leftLayer.getContainer();
    if (container) container.style.clip = `rect(0px, ${{x}}px, 99999px, 0px)`;
  }}
}}

slider.addEventListener('mousedown', () => isDragging = true);
window.addEventListener('mouseup', () => isDragging = false);
window.addEventListener('mousemove', e => {{
  if (!isDragging) return;
  updateCurtain(e.clientX);
}});
</script>
</body>
</html>
"""
    return html
