# -*- coding: utf-8 -*-
"""Edge-case and error-path tests for the public multilayer API."""

from __future__ import annotations

import builtins
import json

import pytest

from multilayer import (
    BivariateChoroplethMap,
    Choropleth,
    ClassificationMethod,
    ColorRamp,
    Globe3DMap,
    GridLayout,
    GridPreset,
    MultiMap,
    Panel,
    RadialSearchMap,
    RasterLayer,
    RollerAngleMode,
    RollerCurtainMap,
    SwipeMap,
    TileLayer,
    TileProvider,
    VectorLayer,
    create_multimap,
    get_tile_provider,
)
from multilayer.animated_temporal_slider_map import export_time_slider_html
from multilayer.atlas_generator import MultiPageAtlas
from multilayer.cli import main as cli_main
from multilayer.hexbin_aggregation import aggregate_points_to_hexbins
from multilayer.split_view_roller_map import render_roller_map_html


def _polygon_feature(value: float = 1.0) -> dict:
    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[27.13, 38.41], [27.15, 38.41], [27.15, 38.43], [27.13, 38.41]]],
        },
        "properties": {"value": value},
    }


def _collection(*values: float) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [_polygon_feature(value) for value in values],
    }


def test_grid_layout_aliases_and_custom_dimensions():
    """Numeric/word aliases and custom ``RxC`` strings resolve correctly."""
    assert GridLayout.from_string("2").preset is GridPreset.TWO_HORIZONTAL
    assert GridLayout.from_string("two").preset is GridPreset.TWO_HORIZONTAL
    assert GridLayout.from_string("3").preset is GridPreset.THREE_HORIZONTAL
    assert GridLayout.from_string("4").preset is GridPreset.FOUR_GRID
    assert GridLayout.from_string("6").preset is GridPreset.SIX_GRID
    assert GridLayout.from_string("8").preset is GridPreset.EIGHT_GRID
    assert GridLayout.from_string("2X5").panel_count == 10
    assert GridLayout.from_string("not-a-grid").preset is GridPreset.FOUR_GRID


def test_grid_custom_override_and_css():
    """Custom row/column overrides win over the preset and produce valid CSS."""
    layout = GridLayout(preset=GridPreset.TWO_HORIZONTAL, custom_rows=3, custom_cols=4)
    assert (layout.rows, layout.cols, layout.panel_count) == (3, 4, 12)
    css = layout.to_css_grid()
    assert "repeat(4, 1fr)" in css
    assert "repeat(3, 1fr)" in css

    preset = GridPreset.TWO_VERTICAL
    assert (preset.rows, preset.cols, preset.panel_count) == (2, 1, 2)


def test_panel_layer_types_basemaps_and_bounds():
    """Panel accepts layers of each supported type and rejects unknown ones."""
    panel = Panel(title="Test")
    panel.add_layer(_collection(1.0))
    panel.add_layer(json.dumps(_polygon_feature(2.0)), name="From JSON")
    assert len(panel.layers) == 2
    assert all(isinstance(layer, VectorLayer) for layer in panel.layers)

    with pytest.raises(TypeError):
        panel.add_layer(42)

    panel.set_basemap("satellite")
    assert "World_Imagery" in panel.basemap.url_template
    replacement = TileLayer(name="Custom", url_template="https://example.com/{z}/{x}/{y}.png")
    panel.set_basemap(replacement)
    assert panel.basemap is replacement

    bounds = panel.get_bounds()
    assert bounds == (27.13, 38.41, 27.15, 38.43)
    assert "layers" in panel.to_dict()

    assert Panel().get_bounds() is None


def test_multimap_grid_inputs_and_accessors():
    """MultiMap handles presets, layouts, invalid inputs, and out-of-range panels."""
    assert MultiMap(grid=GridPreset.TWO_VERTICAL).panel_count == 2
    custom = GridLayout(custom_rows=1, custom_cols=3)
    assert MultiMap(grid=custom).panel_count == 3
    assert MultiMap(grid=123).panel_count == 4  # type: ignore[arg-type]

    mm = MultiMap(grid="1x2", title="Accessors")
    with pytest.raises(IndexError):
        mm.panel(5)

    assert mm.panel_count == 2
    assert mm.panel(0) is mm.panels[0]


def test_multimap_broadcast_layers_bounds_and_export(tmp_path):
    """Layer/basemap broadcasts, bounds union, dict export, and disk export work."""
    mm = MultiMap(grid="1x2", title="Broadcast", basemap="osm")
    mm.add_layer(_collection(1.0, 2.0))
    assert all(len(panel.layers) == 1 for panel in mm.panels)

    mm.set_basemap("satellite")
    assert all("World_Imagery" in panel.basemap.url_template for panel in mm.panels)

    assert mm.get_bounds() == (27.13, 38.41, 27.15, 38.43)
    assert mm.to_dict()["panels"][0]["title"] == "Panel 1"

    output = tmp_path / "nested" / "broadcast.html"
    html = mm.to_html(str(output))
    assert output.exists()
    assert html == output.read_text(encoding="utf-8")
    assert "<iframe" in mm._repr_html_()

    empty = MultiMap(grid="1x2")
    assert empty.get_bounds() is None


def test_multimap_show_fallback_without_ipython(monkeypatch, capsys):
    """``show`` prints a summary when IPython is unavailable."""
    mm = MultiMap(grid="1x2", title="No Notebook")
    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> object:
        if name.startswith("IPython"):
            raise ImportError("IPython is not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    mm.show()
    captured = capsys.readouterr()
    assert "MultiMap(" in captured.out
    assert "No Notebook" in captured.out


def test_create_multimap_skips_layers_beyond_panel_count():
    """Factory stops assigning layers once every panel is filled."""
    mm = create_multimap(
        layers=[_collection(1.0), _collection(2.0), _collection(3.0)],
        grid="1x2",
        title="Two Panels",
    )
    assert mm.panel_count == 2
    assert [len(panel.layers) for panel in mm.panels] == [1, 1]
    assert mm.panel(0).title == "Panel 1"


def test_swipe_map_empty_and_partial_layers(tmp_path):
    """SwipeMap handles missing layers and dict inputs without failing."""
    empty = SwipeMap()
    assert empty.get_bounds() is None
    assert "<html" in empty.to_html()
    assert "<iframe" in empty._repr_html_()

    partial = SwipeMap(left_layer=_collection(1.0))
    assert partial.get_bounds() == (27.13, 38.41, 27.15, 38.43)
    output = tmp_path / "swipe.html"
    assert "swipe" in partial.to_html(str(output)).lower()
    assert output.exists()


def test_tile_providers_and_custom_urls():
    """Built-in providers expose templates/attribution, and custom URLs pass through."""
    assert TileProvider.NONE.url_template == ""
    assert TileProvider.NONE.attribution == ""
    assert "openstreetmap.org" in TileProvider.OSM.url_template
    assert "OpenStreetMap" in TileProvider.OSM.attribution

    custom = get_tile_provider("https://tiles.example.com/{z}/{x}/{y}.png")
    assert custom.name == "Custom Tiles"
    assert custom.url_template.startswith("https://tiles.example.com/")

    none_provider = get_tile_provider("none")
    assert none_provider.url_template == ""


def test_vector_layer_source_normalisation_and_errors(tmp_path):
    """VectorLayer normalises files, JSON strings, Features, and raw geometries."""
    path = tmp_path / "zones.geojson"
    path.write_text(json.dumps(_collection(1.0)), encoding="utf-8")
    from_file = VectorLayer.from_geojson(str(path))
    assert from_file.name == "zones"
    assert len(from_file.data["features"]) == 1

    from_json = VectorLayer.from_geojson(json.dumps(_polygon_feature(5.0)))
    assert from_json.data["type"] == "FeatureCollection"

    from_feature = VectorLayer.from_geojson(_polygon_feature(3.0))
    assert from_feature.data["features"][0]["type"] == "Feature"

    point_geometry = {"type": "Point", "coordinates": [29.0, 41.0]}
    from_geometry = VectorLayer.from_geojson(point_geometry)
    assert from_geometry.data["features"][0]["geometry"]["type"] == "Point"

    with pytest.raises(ValueError):
        VectorLayer.from_geojson(123)  # type: ignore[arg-type]

    assert VectorLayer().get_bounds() is None


def test_vector_layer_from_geodataframe_protocol():
    """Objects exposing ``__geo_interface__`` are accepted; others are rejected."""

    class FakeGeoDataFrame:
        __geo_interface__ = _collection(2.0)

    layer = VectorLayer.from_geodataframe(FakeGeoDataFrame(), name="GDF")
    assert layer.name == "GDF"
    assert len(layer.data["features"]) == 1

    with pytest.raises(TypeError):
        VectorLayer.from_geodataframe(object())


def test_raster_layer_bounds_and_dict():
    """Raster overlays normalise their corner bounds regardless of orientation."""
    raster = RasterLayer(
        name="Overlay", url="https://example.com/a.png", bounds=((30.0, 40.0), (10.0, 20.0))
    )
    assert raster.get_bounds() == (20.0, 10.0, 40.0, 30.0)
    assert raster.to_dict()["type"] == "raster"


def test_color_ramp_edge_sizes():
    """Palette interpolation handles exact, tiny, and expanded colour counts."""
    assert ColorRamp.VIRIDIS.get_colors(5) == ColorRamp.VIRIDIS.get_colors()
    assert ColorRamp.VIRIDIS.get_colors(1) == ["#fde725"]
    interpolated = ColorRamp.MAGMA.get_colors(7)
    assert len(interpolated) == 7
    assert all(color.startswith("#") and len(color) == 7 for color in interpolated)


def test_choropleth_methods_and_noop_paths():
    """All classification methods run and non-numeric/empty inputs are returned as-is."""
    layer = VectorLayer.from_geojson(_collection(1.0, 2.0, 3.0, 4.0, 5.0))

    std = Choropleth.classify(layer, "value", method=ClassificationMethod.STANDARD_DEVIATION)
    assert "_multilayer_fill_color" in std.data["features"][0]["properties"]

    natural = Choropleth.classify(layer, "value", method="natural_breaks", num_classes=3)
    assert len(natural.data["features"]) == 5

    assert Choropleth.classify(VectorLayer(), "value") is not None
    assert Choropleth.classify(layer, "missing_property") is layer

    non_numeric = VectorLayer.from_geojson(
        {"type": "FeatureCollection", "features": [_polygon_feature("text")]}  # type: ignore[arg-type]
    )
    assert Choropleth.classify(non_numeric, "value") is non_numeric


def test_hexbin_empty_and_aggregate_statistics():
    """Hexbin aggregation handles empty input and SUM/MAX/COUNT statistics."""
    empty = aggregate_points_to_hexbins([])
    assert empty.total_hexagons == 0
    assert empty.cells == []
    assert empty.to_geojson() == {"type": "FeatureCollection", "features": []}

    points = [(41.0, 29.0), (41.0001, 29.0001)]
    values = [2.0, 3.0]

    summed = aggregate_points_to_hexbins(points, values, hex_radius_m=1000.0, statistic="SUM")
    assert summed.cells[0].aggregated_metric_value == 5.0

    maximum = aggregate_points_to_hexbins(points, values, hex_radius_m=1000.0, statistic="MAX")
    assert maximum.cells[0].aggregated_metric_value == 3.0

    counted = aggregate_points_to_hexbins(points, hex_radius_m=1000.0, statistic="COUNT")
    assert counted.cells[0].point_count == 2

    ring = counted.to_geojson()["features"][0]["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1]


def test_atlas_geojson_index_triggers_generation():
    """Requesting the GeoJSON index lazily generates the default sheet grid."""
    atlas = MultiPageAtlas(rows=2, cols=2)
    geojson = atlas.to_geojson_index()
    assert len(atlas.sheets) == 4
    assert len(geojson["features"]) == 4
    assert geojson["name"] == atlas.title
    ring = geojson["features"][0]["geometry"]["coordinates"][0]
    assert ring[0] == ring[-1]


def test_bivariate_empty_classification():
    """Bivariate classification returns an empty list when there are no features."""
    bivariate = BivariateChoroplethMap()
    assert bivariate.classify_and_color_features() == []


def test_globe3d_quad_layout():
    """The quad layout emits a two-row CSS grid."""
    html = Globe3DMap(layout="quad").to_html()
    assert "grid-template-rows: 1fr 1fr" in html


def test_radial_search_add_layer():
    """RadialSearchMap accumulates target GeoJSON layers."""
    search = RadialSearchMap()
    search.add_layer(_collection(1.0))
    search.add_layer(_collection(2.0))
    assert len(search.geojson_target_layers) == 2
    assert "radius-slider" in search.to_html()


def test_module_level_helpers_write_files(tmp_path):
    """Convenience helpers create their output files and return paths."""
    slider_path = export_time_slider_html(
        [("2020", _collection(1.0)), ("2025", _collection(1.0, 2.0))],
        tmp_path / "slider.html",
        title="Helper Slider",
    )
    assert slider_path.exists()
    assert "Helper Slider" in slider_path.read_text(encoding="utf-8")

    roller = RollerCurtainMap(mode=RollerAngleMode.CIRCULAR_APERTURE)
    assert "circular_aperture" in roller.to_html()

    roller_path = render_roller_map_html(
        "Before", "After", tmp_path / "roller.html", mode=RollerAngleMode.HORIZONTAL
    )
    assert roller_path.exists()
    assert "horizontal" in roller_path.read_text(encoding="utf-8")


def test_cli_error_paths_and_version(capsys):
    """CLI reports missing files, prints help with no command, and supports --version."""
    assert cli_main([]) == 0
    assert "usage:" in capsys.readouterr().out.lower()

    with pytest.raises(SystemExit) as excinfo:
        cli_main(["--version"])
    assert excinfo.value.code == 0

    assert cli_main(["build", "--layers", "does_not_exist.geojson"]) == 1
    assert cli_main(["compare", "missing_a.geojson", "missing_b.geojson"]) == 1
    assert cli_main(["inspect", "missing.geojson"]) == 1
