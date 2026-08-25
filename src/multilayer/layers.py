# -*- coding: utf-8 -*-
"""Spatial layer representations: Vector, Raster, Basemap Tile providers."""

from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TileProvider(str, Enum):
    """Standard web map tile providers."""

    OSM = "openstreetmap"
    CARTO_LIGHT = "carto-positron"
    CARTO_DARK = "carto-dark-matter"
    CARTO_VOYAGER = "carto-voyager"
    ESRI_SATELLITE = "esri-satellite"
    ESRI_TOPO = "esri-topo"
    OPEN_TOPO = "opentopomap"
    CYCLOSM = "cyclosm"
    NONE = "none"

    @property
    def url_template(self) -> str:
        templates = {
            TileProvider.OSM: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            TileProvider.CARTO_LIGHT: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
            TileProvider.CARTO_DARK: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            TileProvider.CARTO_VOYAGER: "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
            TileProvider.ESRI_SATELLITE: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            TileProvider.ESRI_TOPO: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
            TileProvider.OPEN_TOPO: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            TileProvider.CYCLOSM: "https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
            TileProvider.NONE: "",
        }
        return templates.get(self, "")

    @property
    def attribution(self) -> str:
        attribs = {
            TileProvider.OSM: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            TileProvider.CARTO_LIGHT: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            TileProvider.CARTO_DARK: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            TileProvider.CARTO_VOYAGER: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
            TileProvider.ESRI_SATELLITE: "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
            TileProvider.ESRI_TOPO: "Tiles &copy; Esri &mdash; Sources: GEBCO, NOAA, CHS, OSU, UNH, CSUMB, National Geographic, DeLorme, NAVTEQ, and Esri",
            TileProvider.OPEN_TOPO: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (CC-BY-SA)',
            TileProvider.CYCLOSM: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://www.cyclosm.org">CyclOSM</a>',
            TileProvider.NONE: "",
        }
        return attribs.get(self, "")


def get_tile_provider(name_or_url: str) -> TileLayer:
    """Resolve a TileLayer from a provider nickname, alias, or custom XYZ tile template URL."""
    clean = name_or_url.strip().lower()
    mapping = {
        "osm": TileProvider.OSM,
        "openstreetmap": TileProvider.OSM,
        "carto": TileProvider.CARTO_LIGHT,
        "light": TileProvider.CARTO_LIGHT,
        "carto-light": TileProvider.CARTO_LIGHT,
        "carto-positron": TileProvider.CARTO_LIGHT,
        "dark": TileProvider.CARTO_DARK,
        "carto-dark": TileProvider.CARTO_DARK,
        "carto-dark-matter": TileProvider.CARTO_DARK,
        "voyager": TileProvider.CARTO_VOYAGER,
        "carto-voyager": TileProvider.CARTO_VOYAGER,
        "satellite": TileProvider.ESRI_SATELLITE,
        "esri-satellite": TileProvider.ESRI_SATELLITE,
        "aerial": TileProvider.ESRI_SATELLITE,
        "topo": TileProvider.ESRI_TOPO,
        "esri-topo": TileProvider.ESRI_TOPO,
        "opentopo": TileProvider.OPEN_TOPO,
        "opentopomap": TileProvider.OPEN_TOPO,
        "cyclosm": TileProvider.CYCLOSM,
        "none": TileProvider.NONE,
    }
    if clean in mapping:
        provider = mapping[clean]
        return TileLayer(
            name=provider.value,
            url_template=provider.url_template,
            attribution=provider.attribution,
        )

    # Custom XYZ URL
    return TileLayer(name="Custom Tiles", url_template=name_or_url)


class Layer(ABC):
    """Abstract spatial layer representation."""

    name: str
    visible: bool = True
    opacity: float = 1.0

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Convert layer to JSON-serializable dictionary."""
        pass

    @abstractmethod
    def get_bounds(self) -> tuple[float, float, float, float] | None:
        """Return (min_lon, min_lat, max_lon, max_lat) bounding box, or None if global/empty."""
        pass


@dataclass
class TileLayer(Layer):
    """Web map raster tile basemap layer."""

    name: str = "OpenStreetMap"
    url_template: str = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    attribution: str = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    min_zoom: int = 0
    max_zoom: int = 20
    visible: bool = True
    opacity: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "tile",
            "name": self.name,
            "url_template": self.url_template,
            "attribution": self.attribution,
            "min_zoom": self.min_zoom,
            "max_zoom": self.max_zoom,
            "visible": self.visible,
            "opacity": self.opacity,
        }

    def get_bounds(self) -> tuple[float, float, float, float] | None:
        return None


@dataclass
class VectorLayer(Layer):
    """Vector geometry layer supporting GeoJSON, GeoPandas, and shape dictionaries."""

    name: str = "Vector Layer"
    data: dict[str, Any] = field(default_factory=lambda: {"type": "FeatureCollection", "features": []})
    fill_color: str = "#3388ff"
    fill_opacity: float = 0.6
    stroke_color: str = "#2255bb"
    stroke_width: float = 1.5
    stroke_opacity: float = 1.0
    dash_array: str | None = None
    point_radius: float = 6.0
    tooltip_properties: list[str] = field(default_factory=list)
    popup_properties: list[str] = field(default_factory=list)
    visible: bool = True
    opacity: float = 1.0

    @classmethod
    def from_geojson(
        cls,
        geojson_source: str | dict[str, Any],
        name: str = "Vector Layer",
        **style_kwargs: Any,
    ) -> VectorLayer:
        """Create VectorLayer from GeoJSON file path, JSON string, or python dictionary."""
        if isinstance(geojson_source, str):
            if os.path.exists(geojson_source):
                with open(geojson_source, "r", encoding="utf-8") as f:
                    parsed = json.load(f)
                if not name or name == "Vector Layer":
                    name = os.path.splitext(os.path.basename(geojson_source))[0]
            else:
                parsed = json.loads(geojson_source)
        elif isinstance(geojson_source, dict):
            parsed = geojson_source
        elif hasattr(geojson_source, "__geo_interface__"):
            parsed = geojson_source.__geo_interface__
        else:
            raise ValueError(f"Unsupported GeoJSON data source: {type(geojson_source)}")

        # Normalize to FeatureCollection
        if parsed.get("type") == "Feature":
            parsed = {"type": "FeatureCollection", "features": [parsed]}
        elif parsed.get("type") in ["Point", "LineString", "Polygon", "MultiPoint", "MultiLineString", "MultiPolygon"]:
            parsed = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": parsed, "properties": {}}]}

        return cls(name=name, data=parsed, **style_kwargs)

    @classmethod
    def from_geodataframe(cls, gdf: Any, name: str = "GeoDataFrame Layer", **style_kwargs: Any) -> VectorLayer:
        """Create VectorLayer from a GeoPandas GeoDataFrame."""
        if hasattr(gdf, "__geo_interface__"):
            geojson_data = gdf.__geo_interface__
            return cls(name=name, data=geojson_data, **style_kwargs)
        raise TypeError("Object does not implement __geo_interface__ (is GeoPandas installed?)")

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "vector",
            "name": self.name,
            "data": self.data,
            "fill_color": self.fill_color,
            "fill_opacity": self.fill_opacity,
            "stroke_color": self.stroke_color,
            "stroke_width": self.stroke_width,
            "stroke_opacity": self.stroke_opacity,
            "dash_array": self.dash_array,
            "point_radius": self.point_radius,
            "tooltip_properties": self.tooltip_properties,
            "popup_properties": self.popup_properties,
            "visible": self.visible,
            "opacity": self.opacity,
        }

    def get_bounds(self) -> tuple[float, float, float, float] | None:
        """Compute bounding box (min_lon, min_lat, max_lon, max_lat) from features."""
        features = self.data.get("features", [])
        if not features:
            return None

        coords_flat: list[tuple[float, float]] = []

        def extract_coords(geom: dict[str, Any]) -> None:
            if not geom or "coordinates" not in geom:
                return
            raw = geom["coordinates"]

            def recurse(node: Any) -> None:
                if isinstance(node, (list, tuple)) and len(node) >= 2 and isinstance(node[0], (int, float)) and isinstance(node[1], (int, float)):
                    coords_flat.append((float(node[0]), float(node[1])))
                elif isinstance(node, (list, tuple)):
                    for item in node:
                        recurse(item)

            recurse(raw)

        for feat in features:
            extract_coords(feat.get("geometry", {}))

        if not coords_flat:
            return None

        lons = [c[0] for c in coords_flat]
        lats = [c[1] for c in coords_flat]
        return min(lons), min(lats), max(lons), max(lats)


@dataclass
class RasterLayer(Layer):
    """Georeferenced raster image overlay layer."""

    name: str = "Raster Overlay"
    url: str = ""
    bounds: tuple[tuple[float, float], tuple[float, float]] = ((0.0, 0.0), (1.0, 1.0))
    visible: bool = True
    opacity: float = 0.85

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "raster",
            "name": self.name,
            "url": self.url,
            "bounds": self.bounds,
            "visible": self.visible,
            "opacity": self.opacity,
        }

    def get_bounds(self) -> tuple[float, float, float, float] | None:
        (lat1, lon1), (lat2, lon2) = self.bounds
        return min(lon1, lon2), min(lat1, lat2), max(lon1, lon2), max(lat1, lat2)
