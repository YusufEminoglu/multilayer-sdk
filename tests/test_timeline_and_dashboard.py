# -*- coding: utf-8 -*-
"""Unit tests for TimelineMap and InteractiveDashboard in multilayer-sdk."""

from __future__ import annotations

import os
import tempfile
import pytest

from multilayer import (
    FilterWidget,
    InteractiveDashboard,
    MetricCard,
    TimeFrame,
    TimelineMap,
    VectorLayer,
)


@pytest.fixture
def sample_geojson():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[27.13, 38.41], [27.15, 38.41], [27.15, 38.43], [27.13, 38.43], [27.13, 38.41]]
                    ],
                },
                "properties": {"id": 1, "name": "Zone A", "population": 12000, "risk_score": 0.8},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[27.16, 38.44], [27.18, 38.44], [27.18, 38.46], [27.16, 38.46], [27.16, 38.44]]
                    ],
                },
                "properties": {"id": 2, "name": "Zone B", "population": 4500, "risk_score": 0.3},
            },
        ],
    }


def test_timeline_map_creation_and_export(sample_geojson):
    v1 = VectorLayer.from_geojson(sample_geojson, name="Phase 1")
    v2 = VectorLayer.from_geojson(sample_geojson, name="Phase 2", fill_color="#ef4444")

    tm = TimelineMap(grid="1x2", title="Disaster Progression", basemap="carto-dark", fps=2.0)
    tm.set_panel_title(0, "Observation Panel")
    tm.set_panel_title(1, "Prediction Panel")

    f1 = tm.create_frame(label="T+0h", timestamp="2026-08-30 12:00", description="Initial state")
    f1.add_layer(0, v1).add_layer(1, v1)

    f2 = tm.create_frame(label="T+6h", timestamp="2026-08-30 18:00", description="Expanded hazard")
    f2.add_layer(0, v1).add_layer(1, v2)

    assert len(tm.frames) == 2
    assert tm.frames[0].label == "T+0h"
    assert tm.frames[1].label == "T+6h"

    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "timeline.html")
        html_str = tm.to_html(out_html)

        assert os.path.exists(out_html)
        assert "timeline-controls" in html_str
        assert "Disaster Progression" in html_str
        assert "play-btn" in html_str


def test_interactive_dashboard_creation_and_export(sample_geojson):
    v = VectorLayer.from_geojson(sample_geojson, name="Urban Districts")

    dash = InteractiveDashboard(grid="1x2", title="Urban Resilience Master Dashboard", basemap="carto-dark")
    dash.add_layer(0, v)
    dash.add_layer(1, v)

    dash.add_metric_card(title="Total Population", property_key="population", aggregation="sum", unit="people", icon="👥")
    dash.add_metric_card(title="Avg Risk", property_key="risk_score", aggregation="mean", unit="idx", icon="⚠️")

    dash.add_filter(property_key="population", label="Min Population Filter", filter_type="range")
    dash.add_filter(property_key="risk_score", label="Min Risk Score", filter_type="range")

    assert len(dash.metric_cards) == 2
    assert len(dash.filters) == 2

    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "dashboard.html")
        html_str = dash.to_html(out_html)

        assert os.path.exists(out_html)
        assert "Urban Resilience Master Dashboard" in html_str
        assert "kpi-card" in html_str
        assert "Total Population" in html_str
        assert "filters-container" in html_str
