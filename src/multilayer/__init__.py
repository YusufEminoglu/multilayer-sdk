# -*- coding: utf-8 -*-
"""
multilayer — Pure-Python Synchronized Multi-Panel Map Visualization & Spatial Comparison Engine.
"""

from __future__ import annotations

from multilayer.animated_temporal_slider_map import (
    TemporalRangeSliderMap,
    TimeSliderFrame,
    export_time_slider_html,
)
from multilayer.atlas_generator import AtlasGridSheet, MultiPageAtlas
from multilayer.core import MultiMap, Panel, SwipeMap, create_multimap
from multilayer.curtain_map import CurtainMap
from multilayer.dashboard import FilterWidget, InteractiveDashboard, MetricCard
from multilayer.diff_map import DiffMap, SpatialDiffResult
from multilayer.flow_arrow_curved_layer import CurvedFlowMap, FlowArc3D
from multilayer.globe3d import Globe3DMap, TerrainPanel3D
from multilayer.grid import GridLayout, GridPreset
from multilayer.hexbin_aggregation import HexagonCell, HexbinHeatmapLayer, aggregate_points_to_hexbins
from multilayer.layers import (
    Layer,
    RasterLayer,
    TileLayer,
    TileProvider,
    VectorLayer,
    get_tile_provider,
)
from multilayer.lens_magnifier_map import LensConfig, SpyglassCompareMap
from multilayer.particle_layer import FlowParticleConfig, ParticleFlowMap
from multilayer.spatial_choropleth_3d import Choropleth3DMap, PrismPolygon3D
from multilayer.spatial_query import RadialSearchMap
from multilayer.split_screen_quad_view import QuadPanelConfig, QuadSyncMap
from multilayer.split_view_roller_map import (
    RollerAngleMode,
    RollerCurtainMap,
    render_roller_map_html,
)
from multilayer.storymap_scroller import StoryChapter, StoryMapScroller
from multilayer.symbology import (
    CategoricalStyle,
    Choropleth,
    ClassificationMethod,
    ColorRamp,
    GraduatedStyle,
    StyleRule,
)
from multilayer.timeline import TimeFrame, TimelineMap

from .elevation_contour_relief_map import (
    ContourIntervalConfig,
    HypsoTintedReliefMap,
)
from .isochrone_travel_bubble_map import (
    IsochroneBandParams,
    TravelIsochroneBubbleMap,
)
from .bivariate_choropleth_map import (
    BivariateChoroplethMap,
    BivariateMatrixColorRamp,
)
from .vector_wind_streamline_animator import (
    WindParticleFieldMap,
    WindParticleParams,
)

__version__ = "0.11.0"
__author__ = "Yusuf Eminoğlu"
__email__ = "yusufeminoglu@gmail.com"

__all__ = [
    "__version__",
    "MultiMap",
    "Panel",
    "SwipeMap",
    "create_multimap",
    "TimelineMap",
    "TimeFrame",
    "InteractiveDashboard",
    "MetricCard",
    "FilterWidget",
    "Globe3DMap",
    "TerrainPanel3D",
    "RadialSearchMap",
    "DiffMap",
    "SpatialDiffResult",
    "MultiPageAtlas",
    "AtlasGridSheet",
    "ParticleFlowMap",
    "FlowParticleConfig",
    "CurtainMap",
    "HexbinHeatmapLayer",
    "HexagonCell",
    "aggregate_points_to_hexbins",
    "StoryMapScroller",
    "StoryChapter",
    # 3D Extruded Choropleth Prisms
    "Choropleth3DMap",
    "PrismPolygon3D",
    # Spyglass & Lens Comparer
    "SpyglassCompareMap",
    "LensConfig",
    # Quad-Synchronized 4-Panel Map Grid
    "QuadSyncMap",
    "QuadPanelConfig",
    # Curved Animated Flow Arcs
    "CurvedFlowMap",
    "FlowArc3D",
    # Temporal Range Slider Map
    "TemporalRangeSliderMap",
    "TimeSliderFrame",
    "export_time_slider_html",
    # Angle-Adjustable Roller Curtain Map
    "RollerCurtainMap",
    "RollerAngleMode",
    "render_roller_map_html",
    # 2D 3x3 Bivariate Matrix Choropleth Map
    "BivariateChoroplethMap",
    "BivariateMatrixColorRamp",
    # WebGL Wind & Streamline Particle Field
    "WindParticleFieldMap",
    "WindParticleParams",
    # Multi-Modal Isochrone Travel Bubble Map
    "TravelIsochroneBubbleMap",
    "IsochroneBandParams",
    # Hypso-Tinted Topographic Relief & Dynamic Contours
    "HypsoTintedReliefMap",
    "ContourIntervalConfig",
    "GridLayout",
    "GridPreset",
    "Layer",
    "VectorLayer",
    "RasterLayer",
    "TileLayer",
    "TileProvider",
    "get_tile_provider",
    "Choropleth",
    "ClassificationMethod",
    "ColorRamp",
    "StyleRule",
    "GraduatedStyle",
    "CategoricalStyle",
]
