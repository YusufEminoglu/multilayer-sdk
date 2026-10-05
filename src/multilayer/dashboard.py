# -*- coding: utf-8 -*-
"""Interactive Multi-Panel Dashboard Builder with Cross-Filtering & Metric Cards."""

from __future__ import annotations

import html
import json
from dataclasses import dataclass
from pathlib import Path

from .grid import GridLayout
from .layers import VectorLayer, get_tile_provider


@dataclass
class MetricCard:
    """Dynamic summary card displaying aggregations."""

    title: str
    property_key: str
    aggregation: str = "sum"  # 'sum', 'mean', 'count', 'min', 'max'
    unit: str = ""
    icon: str = "📊"

    def to_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "property_key": self.property_key,
            "aggregation": self.aggregation,
            "unit": self.unit,
            "icon": self.icon,
        }


@dataclass
class FilterWidget:
    """Client-side filter widget definition."""

    property_key: str
    label: str
    filter_type: str = "range"  # 'range', 'category'

    def to_dict(self) -> dict[str, str]:
        return {
            "property_key": self.property_key,
            "label": self.label,
            "filter_type": self.filter_type,
        }


class InteractiveDashboard:
    """Fuses multi-panel maps with dynamic cross-filters, metric KPI cards, and an interactive data table."""

    def __init__(
        self,
        grid: str | GridLayout = "1x2",
        title: str = "Executive Spatial Analytics Dashboard",
        basemap: str = "carto-dark",
    ) -> None:
        self.layout = GridLayout.from_string(grid) if isinstance(grid, str) else grid
        self.title = title
        self.basemap = basemap
        self.panel_layers: dict[int, list[VectorLayer]] = {
            i: [] for i in range(self.layout.panel_count)
        }
        self.panel_titles: list[str] = [f"Panel {i+1}" for i in range(self.layout.panel_count)]
        self.metric_cards: list[MetricCard] = []
        self.filters: list[FilterWidget] = []

    def add_layer(self, panel_index: int, layer: VectorLayer) -> "InteractiveDashboard":
        if 0 <= panel_index < self.layout.panel_count:
            self.panel_layers[panel_index].append(layer)
        return self

    def add_metric_card(
        self,
        title: str,
        property_key: str,
        aggregation: str = "sum",
        unit: str = "",
        icon: str = "📊",
    ) -> "InteractiveDashboard":
        self.metric_cards.append(
            MetricCard(
                title=title,
                property_key=property_key,
                aggregation=aggregation,
                unit=unit,
                icon=icon,
            )
        )
        return self

    def add_filter(
        self,
        property_key: str,
        label: str,
        filter_type: str = "range",
    ) -> "InteractiveDashboard":
        self.filters.append(FilterWidget(property_key=property_key, label=label, filter_type=filter_type))
        return self

    def to_html(self, output_path: str | Path | None = None) -> str:
        """Export the full dashboard to a standalone single-file HTML."""
        tile_prov = get_tile_provider(self.basemap)
        panel_count = self.layout.panel_count

        # Gather master features for client-side filtering
        all_features: list[dict] = []
        for lyrs in self.panel_layers.values():
            for lyr in lyrs:
                if lyr.data and "features" in lyr.data:
                    all_features.extend(lyr.data["features"])

        # Compute initial bounds
        center_lon, center_lat = 0.0, 20.0
        zoom = 2
        for lyrs in self.panel_layers.values():
            for lyr in lyrs:
                b = lyr.get_bounds()
                if b:
                    center_lon = (b[0] + b[2]) / 2.0
                    center_lat = (b[1] + b[3]) / 2.0
                    zoom = 12
                    break

        cards_json = json.dumps([c.to_dict() for c in self.metric_cards], ensure_ascii=False)
        filters_json = json.dumps([f.to_dict() for f in self.filters], ensure_ascii=False)

        # Serialize panel layer setup
        panels_data = {}
        for p_idx, lyrs in self.panel_layers.items():
            panels_data[p_idx] = [
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

        panels_json = json.dumps(panels_data, ensure_ascii=False)
        grid_css = f"grid-template-columns: repeat({self.layout.cols}, 1fr); grid-template-rows: repeat({self.layout.rows}, 1fr);"

        panel_divs = []
        for i in range(panel_count):
            p_title = html.escape(self.panel_titles[i] if i < len(self.panel_titles) else f"Map {i+1}")
            div = f"""
            <div class="map-box">
                <div class="panel-tag">{p_title}</div>
                <div id="dashboard-map-{i}" style="width:100%; height:100%;"></div>
            </div>"""
            panel_divs.append(div)

        joined_panels = "\n".join(panel_divs)

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
        body, html {{ width: 100%; height: 100%; overflow: hidden; background: #0b0f19; color: #f1f5f9; display: flex; flex-direction: column; }}
        header {{ height: 52px; background: #111827; display: flex; align-items: center; justify-content: space-between; padding: 0 1.5rem; border-bottom: 1px solid #1f2937; }}
        header h1 {{ font-size: 1.15rem; font-weight: 700; color: #38bdf8; }}
        #dashboard-body {{ flex: 1; display: flex; overflow: hidden; }}
        #sidebar {{ width: 280px; background: #111827; border-right: 1px solid #1f2937; padding: 1rem; display: flex; flex-direction: column; gap: 1rem; overflow-y: auto; }}
        #main-stage {{ flex: 1; display: flex; flex-direction: column; }}
        #kpi-row {{ display: flex; gap: 1rem; padding: 0.75rem 1rem; background: #111827; border-bottom: 1px solid #1f2937; overflow-x: auto; }}
        .kpi-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 0.5rem 1rem; min-width: 140px; flex: 1; }}
        .kpi-title {{ font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 600; }}
        .kpi-value {{ font-size: 1.25rem; font-weight: 700; color: #38bdf8; margin-top: 2px; }}
        #map-grid {{ flex: 1; display: grid; {grid_css} gap: 6px; padding: 6px; }}
        .map-box {{ background: #000; border-radius: 6px; overflow: hidden; border: 1px solid #1f2937; position: relative; }}
        .panel-tag {{ position: absolute; top: 8px; left: 50px; background: rgba(17, 24, 39, 0.85); padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold; color: #94a3b8; z-index: 1000; border: 1px solid #374151; }}
        .filter-group {{ background: #1e293b; padding: 0.75rem; border-radius: 6px; border: 1px solid #334155; }}
        .filter-label {{ font-size: 0.8rem; font-weight: 600; color: #cbd5e1; margin-bottom: 0.4rem; }}
        .slider-input {{ width: 100%; accent-color: #38bdf8; }}
    </style>
</head>
<body>
    <header>
        <h1>{html.escape(self.title)}</h1>
        <div style="font-size: 0.85rem; color: #94a3b8;">Cross-Filter Analytics</div>
    </header>
    <div id="dashboard-body">
        <div id="sidebar">
            <h3 style="font-size: 0.9rem; color: #94a3b8; text-transform: uppercase;">Filters</h3>
            <div id="filters-container" style="display: flex; flex-direction: column; gap: 0.75rem;"></div>
        </div>
        <div id="main-stage">
            <div id="kpi-row"></div>
            <div id="map-grid">
                {joined_panels}
            </div>
        </div>
    </div>

    <script>
        const cardsConfig = {cards_json};
        const filtersConfig = {filters_json};
        const panelsData = {panels_json};
        const panelCount = {panel_count};
        const tileUrl = "{tile_prov.url_template}";
        const tileAttr = "{tile_prov.attribution}";

        const maps = [];
        const activeLayers = Array.from({{ length: panelCount }}, () => []);
        let filterValues = {{}};

        for (let i = 0; i < panelCount; i++) {{
            const m = L.map('dashboard-map-' + i, {{ zoomControl: (i === 0) }}).setView([{center_lat}, {center_lon}], {zoom});
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

        function buildFilterUI() {{
            const container = document.getElementById('filters-container');
            container.innerHTML = '';
            filtersConfig.forEach(fc => {{
                const grp = document.createElement('div');
                grp.className = 'filter-group';
                grp.innerHTML = `
                    <div class="filter-label">${{fc.label}}</div>
                    <input type="range" class="slider-input" id="filter-${{fc.property_key}}" min="0" max="10000" value="0">
                    <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 2px;">Min: <span id="val-${{fc.property_key}}">0</span></div>
                `;
                container.appendChild(grp);

                const inp = grp.querySelector('input');
                inp.addEventListener('input', (e) => {{
                    filterValues[fc.property_key] = parseFloat(e.target.value);
                    document.getElementById('val-' + fc.property_key).textContent = e.target.value;
                    applyFilters();
                }});
            }});
        }}

        function applyFilters() {{
            let allVisibleFeats = [];
            for (let p = 0; p < panelCount; p++) {{
                activeLayers[p].forEach(l => maps[p].removeLayer(l));
                activeLayers[p] = [];

                const lyrs = panelsData[p] || [];
                lyrs.forEach(lyr => {{
                    if (lyr.data && lyr.data.features) {{
                        const gl = L.geoJSON(lyr.data, {{
                            filter: (feat) => {{
                                for (const key in filterValues) {{
                                    const minV = filterValues[key];
                                    if (minV > 0 && feat.properties && feat.properties[key] !== undefined) {{
                                        if (parseFloat(feat.properties[key]) < minV) return false;
                                    }}
                                }}
                                return true;
                            }},
                            style: (feat) => ({{
                                fillColor: feat.properties?._multilayer_fill_color || lyr.fill_color || '#38bdf8',
                                fillOpacity: lyr.fill_opacity || 0.7,
                                color: lyr.stroke_color || '#0284c7',
                                weight: lyr.stroke_width || 1.5
                            }}),
                            onEachFeature: (feat, layer) => {{
                                allVisibleFeats.push(feat);
                                if (feat.properties) {{
                                    layer.bindPopup('<pre>' + JSON.stringify(feat.properties, null, 2) + '</pre>');
                                }}
                            }}
                        }}).addTo(maps[p]);
                        activeLayers[p].push(gl);
                    }}
                }});
            }}
            updateKPIs(allVisibleFeats);
        }}

        function updateKPIs(feats) {{
            const kpiRow = document.getElementById('kpi-row');
            kpiRow.innerHTML = '';
            cardsConfig.forEach(card => {{
                let val = 0;
                if (card.aggregation === 'count') {{
                    val = feats.length;
                }} else {{
                    const nums = feats.map(f => parseFloat(f.properties?.[card.property_key] || 0)).filter(n => !isNaN(n));
                    if (nums.length > 0) {{
                        if (card.aggregation === 'sum') val = nums.reduce((a,b) => a+b, 0);
                        else if (card.aggregation === 'mean') val = nums.reduce((a,b) => a+b, 0) / nums.length;
                        else if (card.aggregation === 'max') val = Math.max(...nums);
                        else if (card.aggregation === 'min') val = Math.min(...nums);
                    }}
                }}
                const div = document.createElement('div');
                div.className = 'kpi-card';
                div.innerHTML = `
                    <div class="kpi-title">${{card.icon}} ${{card.title}}</div>
                    <div class="kpi-value">${{typeof val === 'number' ? (val % 1 === 0 ? val : val.toFixed(1)) : val}} ${{card.unit}}</div>
                `;
                kpiRow.appendChild(div);
            }});
        }}

        buildFilterUI();
        applyFilters();
    </script>
</body>
</html>"""

        if output_path is not None:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(html_content, encoding="utf-8")

        return html_content
