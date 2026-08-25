# -*- coding: utf-8 -*-
"""Thematic symbology, choropleth classification, and color palette engine."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from multilayer.layers import VectorLayer


class ColorRamp(str, Enum):
    """Scientific and cartographic color palettes."""

    VIRIDIS = "viridis"
    MAGMA = "magma"
    PLASMA = "plasma"
    INFERNO = "inferno"
    TURBO = "turbo"
    CIVIDIS = "cividis"
    BLUES = "blues"
    REDS = "reds"
    GREENS = "greens"
    SPECTRAL = "spectral"
    RDYLBU = "rdylbu"
    YLORRD = "ylorrd"
    PUBU = "pubu"

    def get_colors(self, n: int = 5) -> list[str]:
        """Return n color hex strings interpolated across the palette."""
        palettes = {
            ColorRamp.VIRIDIS: ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"],
            ColorRamp.MAGMA: ["#000004", "#51127c", "#b73779", "#fb8861", "#fcfdbf"],
            ColorRamp.PLASMA: ["#0d0887", "#6a00a8", "#b12a90", "#e16462", "#fca636"],
            ColorRamp.INFERNO: ["#000004", "#57106e", "#bb3754", "#f98e09", "#fcffa4"],
            ColorRamp.TURBO: ["#30123b", "#1ae4b6", "#a4fc3c", "#fe9b2d", "#7a0403"],
            ColorRamp.CIVIDIS: ["#00204d", "#414d6b", "#7c7b78", "#bcab67", "#ffea46"],
            ColorRamp.BLUES: ["#eff3ff", "#bdd7e7", "#6baed6", "#3182bd", "#08519c"],
            ColorRamp.REDS: ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],
            ColorRamp.GREENS: ["#edf8e9", "#bae4b3", "#74c476", "#31a354", "#006d2c"],
            ColorRamp.SPECTRAL: ["#d7191c", "#fdae61", "#ffffbf", "#abdda4", "#2b83ba"],
            ColorRamp.RDYLBU: ["#d73027", "#fc8d59", "#fee090", "#91bfdb", "#4575b4"],
            ColorRamp.YLORRD: ["#ffffb2", "#fecc5c", "#fd8d3c", "#f03b20", "#bd0026"],
            ColorRamp.PUBU: ["#f1eef6", "#bdc9e1", "#74a9cf", "#2b8cbe", "#045a8d"],
        }
        base = palettes.get(self, palettes[ColorRamp.VIRIDIS])
        if n == len(base):
            return base
        if n <= 1:
            return [base[-1]]

        # Interpolate between base colors
        def hex_to_rgb(h: str) -> tuple[int, int, int]:
            h = h.lstrip("#")
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

        def rgb_to_hex(r: int, g: int, b: int) -> str:
            return f"#{max(0, min(255, int(r))):02x}{max(0, min(255, int(g))):02x}{max(0, min(255, int(b))):02x}"

        base_rgb = [hex_to_rgb(c) for c in base]
        result: list[str] = []
        for i in range(n):
            t = i / (n - 1)
            pos = t * (len(base_rgb) - 1)
            idx = int(pos)
            frac = pos - idx
            if idx >= len(base_rgb) - 1:
                result.append(base[-1])
            else:
                c1 = base_rgb[idx]
                c2 = base_rgb[idx + 1]
                r = c1[0] + frac * (c2[0] - c1[0])
                g = c1[1] + frac * (c2[1] - c1[1])
                b = c1[2] + frac * (c2[2] - c1[2])
                result.append(rgb_to_hex(int(r), int(g), int(b)))
        return result


class ClassificationMethod(str, Enum):
    """Statistical binning and data classification methods."""

    QUANTILES = "quantiles"
    EQUAL_INTERVAL = "equal_interval"
    NATURAL_BREAKS = "natural_breaks"
    STANDARD_DEVIATION = "standard_deviation"
    CATEGORICAL = "categorical"


@dataclass
class StyleRule:
    """Styling rule for a specific classification bin."""

    label: str
    min_val: float | None
    max_val: float | None
    fill_color: str
    fill_opacity: float = 0.7
    stroke_color: str = "#333333"
    stroke_width: float = 1.0


@dataclass
class GraduatedStyle:
    """Graduated thematic styling configuration."""

    property_name: str
    method: ClassificationMethod = ClassificationMethod.QUANTILES
    num_classes: int = 5
    color_ramp: ColorRamp = ColorRamp.VIRIDIS
    custom_colors: list[str] | None = None
    rules: list[StyleRule] = field(default_factory=list)


@dataclass
class CategoricalStyle:
    """Unique values categorical styling configuration."""

    property_name: str
    color_mapping: dict[str, str] = field(default_factory=dict)
    default_color: str = "#94a3b8"


class Choropleth:
    """Generates thematic choropleth vector layers from raw GeoJSON attributes."""

    @staticmethod
    def classify(
        vector_layer: VectorLayer,
        property_name: str,
        method: ClassificationMethod | str = ClassificationMethod.QUANTILES,
        num_classes: int = 5,
        color_ramp: ColorRamp | str = ColorRamp.VIRIDIS,
        fill_opacity: float = 0.75,
        stroke_color: str = "#ffffff",
        stroke_width: float = 1.0,
        layer_name: str | None = None,
    ) -> VectorLayer:
        """Classify vector features by property and return a themed VectorLayer."""
        if isinstance(method, str):
            method = ClassificationMethod(method.lower())
        if isinstance(color_ramp, str):
            color_ramp = ColorRamp(color_ramp.lower())

        features = vector_layer.data.get("features", [])
        if not features:
            return vector_layer

        # Extract values
        values: list[float] = []
        for feat in features:
            props = feat.get("properties", {})
            val = props.get(property_name)
            if val is not None and isinstance(val, (int, float)) and not math.isnan(val):
                values.append(float(val))

        if not values:
            return vector_layer

        values.sort()
        n = len(values)
        num_classes = min(num_classes, n)
        colors = color_ramp.get_colors(num_classes)

        # Compute Breaks
        breaks: list[float] = []
        if method == ClassificationMethod.EQUAL_INTERVAL:
            min_v, max_v = values[0], values[-1]
            step = (max_v - min_v) / num_classes
            breaks = [min_v + i * step for i in range(1, num_classes)]
        elif method == ClassificationMethod.QUANTILES:
            for i in range(1, num_classes):
                idx = int((i / num_classes) * n)
                breaks.append(values[min(idx, n - 1)])
        elif method == ClassificationMethod.STANDARD_DEVIATION:
            mean = sum(values) / n
            variance = sum((x - mean) ** 2 for x in values) / n
            std = math.sqrt(variance)
            breaks = [mean - 1.5 * std, mean - 0.5 * std, mean + 0.5 * std, mean + 1.5 * std]
            breaks = [b for b in breaks if values[0] < b < values[-1]]
            num_classes = len(breaks) + 1
            colors = color_ramp.get_colors(num_classes)
        else:  # Natural Breaks fallback approximation
            for i in range(1, num_classes):
                idx = int((i / num_classes) * n)
                breaks.append(values[min(idx, n - 1)])

        # Apply per-feature color
        def get_color(val: float) -> str:
            for i, b in enumerate(breaks):
                if val <= b:
                    return colors[i]
            return colors[-1]

        styled_features: list[dict[str, Any]] = []
        for feat in features:
            fcopy = json.loads(json.dumps(feat))
            props = fcopy.setdefault("properties", {})
            val = props.get(property_name)
            if val is not None and isinstance(val, (int, float)):
                fcolor = get_color(float(val))
            else:
                fcolor = "#94a3b8"

            props["_multilayer_fill_color"] = fcolor
            props["_multilayer_fill_opacity"] = fill_opacity
            props["_multilayer_stroke_color"] = stroke_color
            props["_multilayer_stroke_width"] = stroke_width
            styled_features.append(fcopy)

        new_data = {"type": "FeatureCollection", "features": styled_features}
        name = layer_name or f"{vector_layer.name} ({property_name})"
        return VectorLayer(
            name=name,
            data=new_data,
            fill_color=colors[len(colors) // 2],
            fill_opacity=fill_opacity,
            stroke_color=stroke_color,
            stroke_width=stroke_width,
            tooltip_properties=vector_layer.tooltip_properties or [property_name],
            popup_properties=vector_layer.popup_properties,
        )
