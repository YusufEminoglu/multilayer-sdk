# -*- coding: utf-8 -*-
"""Unit tests for multilayer-sdk."""

from __future__ import annotations

import json
import os
import tempfile

from multilayer import (
    Choropleth,
    ClassificationMethod,
    ColorRamp,
    GridLayout,
    MultiMap,
    SwipeMap,
    VectorLayer,
    create_multimap,
    get_tile_provider,
)
from multilayer.cli import main as cli_main


def sample_geojson() -> dict:
    """Generate sample GeoJSON FeatureCollection."""
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
                "properties": {"id": 1, "name": "Zone A", "pop_density": 1250.0, "risk_score": 0.82},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[27.16, 38.44], [27.18, 38.44], [27.18, 38.46], [27.16, 38.46], [27.16, 38.44]]
                    ],
                },
                "properties": {"id": 2, "name": "Zone B", "pop_density": 450.0, "risk_score": 0.34},
            },
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[27.19, 38.47], [27.21, 38.47], [27.21, 38.49], [27.19, 38.49], [27.19, 38.47]]
                    ],
                },
                "properties": {"id": 3, "name": "Zone C", "pop_density": 890.0, "risk_score": 0.58},
            },
        ],
    }


def test_grid_layouts():
    """Test grid preset parsing and dimensions."""
    g2 = GridLayout.from_string("1x2")
    assert g2.rows == 1 and g2.cols == 2 and g2.panel_count == 2

    g4 = GridLayout.from_string("2x2")
    assert g4.rows == 2 and g4.cols == 2 and g4.panel_count == 4

    g6 = GridLayout.from_string("2x3")
    assert g6.rows == 2 and g6.cols == 3 and g6.panel_count == 6

    g8 = GridLayout.from_string("2x4")
    assert g8.rows == 2 and g8.cols == 4 and g8.panel_count == 8


def test_vector_layer_and_bounds():
    """Test vector layer creation and bounding box computation."""
    data = sample_geojson()
    v = VectorLayer.from_geojson(data, name="Study Area")
    assert v.name == "Study Area"
    assert len(v.data["features"]) == 3

    bounds = v.get_bounds()
    assert bounds is not None
    min_lon, min_lat, max_lon, max_lat = bounds
    assert min_lon == 27.13 and min_lat == 38.41
    assert max_lon == 27.21 and max_lat == 38.49


def test_tile_providers():
    """Test standard tile providers resolution."""
    osm = get_tile_provider("openstreetmap")
    assert "openstreetmap.org" in osm.url_template

    carto_dark = get_tile_provider("carto-dark")
    assert "dark_all" in carto_dark.url_template

    satellite = get_tile_provider("satellite")
    assert "World_Imagery" in satellite.url_template


def test_choropleth_classification():
    """Test choropleth classification with different statistical methods."""
    data = sample_geojson()
    v = VectorLayer.from_geojson(data)

    # Quantiles
    c_quant = Choropleth.classify(v, "pop_density", method=ClassificationMethod.QUANTILES, num_classes=3, color_ramp=ColorRamp.VIRIDIS)
    assert len(c_quant.data["features"]) == 3
    assert "_multilayer_fill_color" in c_quant.data["features"][0]["properties"]

    # Equal Interval
    c_eq = Choropleth.classify(v, "risk_score", method="equal_interval", num_classes=3, color_ramp="plasma")
    assert len(c_eq.data["features"]) == 3


def test_multimap_assembly_and_html_export():
    """Test building a 4-panel MultiMap and compiling to HTML."""
    data = sample_geojson()
    v1 = VectorLayer.from_geojson(data, name="Raw Layer")
    v2 = Choropleth.classify(v1, "pop_density", color_ramp="viridis")
    v3 = Choropleth.classify(v1, "risk_score", color_ramp="magma")

    mm = MultiMap(grid="2x2", title="Urban Vulnerability Analysis", basemap="carto-dark")
    assert mm.panel_count == 4

    mm.panel(0).title = "Base Zones"
    mm.panel(0).add_layer(v1)

    mm.panel(1).title = "Population Density"
    mm.panel(1).add_layer(v2)

    mm.panel(2).title = "Risk Index"
    mm.panel(2).add_layer(v3)

    mm.panel(3).title = "Satellite Context"
    mm.panel(3).set_basemap("satellite")
    mm.panel(3).add_layer(v1)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "test_dashboard.html")
        html_out = mm.to_html(out_file)

        assert os.path.exists(out_file)
        assert len(html_out) > 500
        assert "map-panel-0" in html_out
        assert "Urban Vulnerability Analysis" in html_out
        assert "laser-crosshair" in html_out


def test_swipe_map_export():
    """Test split-screen SwipeMap creation and HTML export."""
    data = sample_geojson()
    v1 = VectorLayer.from_geojson(data, name="Before 2020", fill_color="#ef4444")
    v2 = VectorLayer.from_geojson(data, name="After 2026", fill_color="#3b82f6")

    sm = SwipeMap(left_layer=v1, right_layer=v2, left_title="2020", right_title="2026")
    with tempfile.TemporaryDirectory() as tmpdir:
        out_file = os.path.join(tmpdir, "test_swipe.html")
        html_out = sm.to_html(out_file)

        assert os.path.exists(out_file)
        assert "slider" in html_out
        assert "2020" in html_out and "2026" in html_out


def test_cli_execution():
    """Test CLI commands execution."""
    data = sample_geojson()
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, "data.geojson")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f)

        # Inspect
        ret = cli_main(["inspect", fpath])
        assert ret == 0

        # Tiles
        ret = cli_main(["tiles"])
        assert ret == 0

        # Build
        out_html = os.path.join(tmpdir, "out_cli.html")
        ret = cli_main(["build", "--layers", fpath, "--grid", "1x2", "--out", out_html])
        assert ret == 0
        assert os.path.exists(out_html)

        # Compare
        out_swipe = os.path.join(tmpdir, "out_swipe.html")
        ret = cli_main(["compare", fpath, fpath, "--out", out_swipe])
        assert ret == 0
        assert os.path.exists(out_swipe)


def test_create_multimap_helper():
    """Test create_multimap factory function."""
    data = sample_geojson()
    v1 = VectorLayer.from_geojson(data, name="L1")
    v2 = VectorLayer.from_geojson(data, name="L2")

    mm = create_multimap(layers=[v1, v2], grid="1x2", title="Factory MultiMap")
    assert mm.panel_count == 2
    assert mm.panel(0).title == "L1"
    assert mm.panel(1).title == "L2"
    assert len(mm.panel(0).layers) == 1

