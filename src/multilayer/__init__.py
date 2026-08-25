# -*- coding: utf-8 -*-
"""
multilayer — Pure-Python Synchronized Multi-Panel Map Visualization & Spatial Comparison Engine.
"""

from __future__ import annotations

from multilayer.core import MultiMap, Panel, SwipeMap, create_multimap
from multilayer.grid import GridLayout, GridPreset
from multilayer.layers import (
    Layer,
    RasterLayer,
    TileLayer,
    TileProvider,
    VectorLayer,
    get_tile_provider,
)
from multilayer.symbology import (
    CategoricalStyle,
    Choropleth,
    ClassificationMethod,
    ColorRamp,
    GraduatedStyle,
    StyleRule,
)

__version__ = "0.1.0"
__author__ = "Yusuf Eminoğlu"
__email__ = "yusufeminoglu@gmail.com"

__all__ = [
    "MultiMap",
    "Panel",
    "SwipeMap",
    "create_multimap",
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
    "__version__",
]
