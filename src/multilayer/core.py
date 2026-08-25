# -*- coding: utf-8 -*-
"""Core MultiMap and Panel container classes."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from multilayer.grid import GridLayout, GridPreset
from multilayer.html_builder import build_multimap_html, build_swipe_map_html
from multilayer.layers import Layer, TileLayer, VectorLayer, get_tile_provider


@dataclass
class Panel:
    """Individual map viewport within a MultiMap grid."""

    title: str = "Map Panel"
    basemap: TileLayer = field(default_factory=lambda: get_tile_provider("carto-dark-matter"))
    layers: list[Layer] = field(default_factory=list)
    opacity: float = 1.0
    sync_nav: bool = True

    def add_layer(self, layer: Layer | str | dict[str, Any], **kwargs: Any) -> Panel:
        """Add a vector or tile layer to this panel."""
        if isinstance(layer, Layer):
            self.layers.append(layer)
        elif isinstance(layer, (str, dict)):
            v_layer = VectorLayer.from_geojson(layer, **kwargs)
            self.layers.append(v_layer)
        else:
            raise TypeError(f"Unsupported layer type: {type(layer)}")
        return self

    def set_basemap(self, basemap_or_name: TileLayer | str) -> Panel:
        """Set or change the background basemap provider for this panel."""
        if isinstance(basemap_or_name, TileLayer):
            self.basemap = basemap_or_name
        elif isinstance(basemap_or_name, str):
            self.basemap = get_tile_provider(basemap_or_name)
        return self

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "basemap": self.basemap.to_dict() if self.basemap else None,
            "layers": [lyr.to_dict() for lyr in self.layers],
            "opacity": self.opacity,
            "sync_nav": self.sync_nav,
        }

    def get_bounds(self) -> tuple[float, float, float, float] | None:
        """Calculate union bounding box of all layers in this panel."""
        boxes = [lyr.get_bounds() for lyr in self.layers if lyr.get_bounds() is not None]
        if not boxes:
            return None
        min_lon = min(b[0] for b in boxes)
        min_lat = min(b[1] for b in boxes)
        max_lon = max(b[2] for b in boxes)
        max_lat = max(b[3] for b in boxes)
        return min_lon, min_lat, max_lon, max_lat


class MultiMap:
    """Master synchronized multi-panel map container."""

    def __init__(
        self,
        grid: str | GridPreset | GridLayout = "2x2",
        title: str = "MultiMap Spatial Workspace",
        theme: str = "dark",
        basemap: str | TileLayer = "carto-dark-matter",
        initial_center: tuple[float, float] | None = None,
        initial_zoom: int | None = None,
    ) -> None:
        if isinstance(grid, str):
            self.grid = GridLayout.from_string(grid)
        elif isinstance(grid, GridPreset):
            self.grid = GridLayout(preset=grid)
        elif isinstance(grid, GridLayout):
            self.grid = grid
        else:
            self.grid = GridLayout(preset=GridPreset.FOUR_GRID)

        self.title = title
        self.theme = theme
        self.default_basemap = get_tile_provider(basemap) if isinstance(basemap, str) else basemap
        self.initial_center = initial_center
        self.initial_zoom = initial_zoom

        # Initialize panels to match grid layout
        self.panels: list[Panel] = []
        for i in range(self.grid.panel_count):
            self.panels.append(
                Panel(
                    title=f"Panel {i + 1}",
                    basemap=self.default_basemap,
                )
            )

    @property
    def panel_count(self) -> int:
        return len(self.panels)

    def panel(self, index: int) -> Panel:
        """Access a specific panel by 0-based index."""
        if 0 <= index < len(self.panels):
            return self.panels[index]
        raise IndexError(f"Panel index {index} out of range (0 to {len(self.panels)-1})")

    def add_layer(self, layer: Layer | str | dict[str, Any], panel_index: int | None = None, **kwargs: Any) -> MultiMap:
        """Add a layer to a specific panel or to all panels if panel_index is None."""
        if panel_index is not None:
            self.panel(panel_index).add_layer(layer, **kwargs)
        else:
            for p in self.panels:
                p.add_layer(layer, **kwargs)
        return self

    def set_basemap(self, basemap_or_name: TileLayer | str, panel_index: int | None = None) -> MultiMap:
        """Set basemap for a specific panel or all panels."""
        if panel_index is not None:
            self.panel(panel_index).set_basemap(basemap_or_name)
        else:
            for p in self.panels:
                p.set_basemap(basemap_or_name)
        return self

    def get_bounds(self) -> tuple[float, float, float, float] | None:
        """Calculate union bounding box of all panels."""
        boxes = [p.get_bounds() for p in self.panels if p.get_bounds() is not None]
        if not boxes:
            return None
        min_lon = min(b[0] for b in boxes)
        min_lat = min(b[1] for b in boxes)
        max_lon = max(b[2] for b in boxes)
        max_lat = max(b[3] for b in boxes)
        return min_lon, min_lat, max_lon, max_lat

    def to_html(self, output_path: str | None = None) -> str:
        """Compile MultiMap to standalone interactive HTML and optionally save to file."""
        html_str = build_multimap_html(self)
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_str)
        return html_str

    def to_dict(self) -> dict[str, Any]:
        """Convert MultiMap configuration to dictionary."""
        return {
            "title": self.title,
            "theme": self.theme,
            "grid": self.grid.preset.value,
            "panels": [p.to_dict() for p in self.panels],
            "bounds": self.get_bounds(),
        }

    def _repr_html_(self) -> str:
        """Direct inline HTML representation inside Jupyter Notebook / Google Colab."""
        html_data = self.to_html()
        escaped = html_data.replace('"', '&quot;')
        return f'<iframe srcdoc="{escaped}" width="100%" height="600px" style="border:1px solid #1e293b;border-radius:8px;"></iframe>'

    def show(self) -> None:
        """Display inline widget in Jupyter Notebook environments."""
        try:
            from IPython.display import HTML, display
            display(HTML(self._repr_html_()))
        except ImportError:
            print(f"MultiMap({self.grid.preset.value}, panels={len(self.panels)}, title='{self.title}')")


class SwipeMap:
    """Split-screen 2-panel curtain swipe comparison map."""

    def __init__(
        self,
        left_layer: Layer | str | dict[str, Any] | None = None,
        right_layer: Layer | str | dict[str, Any] | None = None,
        left_title: str = "Before (2020)",
        right_title: str = "After (2026)",
        title: str = "Swipe Map Comparison",
        basemap: str | TileLayer = "carto-dark-matter",
    ) -> None:
        self.left_layer = VectorLayer.from_geojson(left_layer) if isinstance(left_layer, (str, dict)) else left_layer
        self.right_layer = VectorLayer.from_geojson(right_layer) if isinstance(right_layer, (str, dict)) else right_layer
        self.left_title = left_title
        self.right_title = right_title
        self.title = title
        self.basemap = get_tile_provider(basemap) if isinstance(basemap, str) else basemap

    def get_bounds(self) -> tuple[float, float, float, float] | None:
        boxes: list[tuple[float, float, float, float]] = []
        if self.left_layer and self.left_layer.get_bounds():
            boxes.append(self.left_layer.get_bounds())  # type: ignore
        if self.right_layer and self.right_layer.get_bounds():
            boxes.append(self.right_layer.get_bounds())  # type: ignore
        if not boxes:
            return None
        return min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)

    def to_html(self, output_path: str | None = None) -> str:
        html_str = build_swipe_map_html(self)
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_str)
        return html_str

    def _repr_html_(self) -> str:
        html_data = self.to_html()
        escaped = html_data.replace('"', '&quot;')
        return f'<iframe srcdoc="{escaped}" width="100%" height="600px" style="border:1px solid #1e293b;border-radius:8px;"></iframe>'


def create_multimap(
    layers: list[Layer | str | dict[str, Any]] | None = None,
    grid: str = "2x2",
    title: str = "MultiMap Workspace",
    basemap: str = "carto-dark-matter",
) -> MultiMap:
    """Convenience factory to quickly create a MultiMap and assign layers to panels."""
    m = MultiMap(grid=grid, title=title, basemap=basemap)
    if layers:
        for idx, lyr in enumerate(layers):
            if idx < m.panel_count:
                m.panel(idx).add_layer(lyr)
                if hasattr(lyr, "name") and lyr.name:
                    m.panel(idx).title = lyr.name
    return m
