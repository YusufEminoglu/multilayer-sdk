# -*- coding: utf-8 -*-
"""Grid layout definitions and matrix configuration for MultiMap panels."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GridPreset(str, Enum):
    """Supported coordinated multi-panel grid presets."""

    TWO_HORIZONTAL = "1x2"
    TWO_VERTICAL = "2x1"
    THREE_HORIZONTAL = "1x3"
    FOUR_GRID = "2x2"
    SIX_GRID = "2x3"
    EIGHT_GRID = "2x4"

    @property
    def rows(self) -> int:
        return int(self.value.split("x")[0])

    @property
    def cols(self) -> int:
        return int(self.value.split("x")[1])

    @property
    def panel_count(self) -> int:
        return self.rows * self.cols


@dataclass
class GridLayout:
    """Manages panel geometry, CSS grid configurations, and responsive matrix sizing."""

    preset: GridPreset = GridPreset.FOUR_GRID
    custom_rows: int | None = None
    custom_cols: int | None = None

    @property
    def rows(self) -> int:
        return self.custom_rows if self.custom_rows is not None else self.preset.rows

    @property
    def cols(self) -> int:
        return self.custom_cols if self.custom_cols is not None else self.preset.cols

    @property
    def panel_count(self) -> int:
        return self.rows * self.cols

    @classmethod
    def from_string(cls, grid_str: str) -> GridLayout:
        """Parse grid string such as '1x2', '2x2', '2x3', '2x4' or '4'."""
        clean = grid_str.strip().lower()
        if clean in [e.value for e in GridPreset]:
            return cls(preset=GridPreset(clean))
        if clean in ["2", "two"]:
            return cls(preset=GridPreset.TWO_HORIZONTAL)
        if clean in ["3", "three"]:
            return cls(preset=GridPreset.THREE_HORIZONTAL)
        if clean in ["4", "four"]:
            return cls(preset=GridPreset.FOUR_GRID)
        if clean in ["6", "six"]:
            return cls(preset=GridPreset.SIX_GRID)
        if clean in ["8", "eight"]:
            return cls(preset=GridPreset.EIGHT_GRID)

        if "x" in clean:
            parts = clean.split("x")
            try:
                r, c = int(parts[0]), int(parts[1])
                return cls(custom_rows=r, custom_cols=c)
            except ValueError:
                pass
        return cls(preset=GridPreset.FOUR_GRID)

    def to_css_grid(self) -> str:
        """Return CSS grid-template-columns and grid-template-rows declaration."""
        return f"grid-template-columns: repeat({self.cols}, 1fr); grid-template-rows: repeat({self.rows}, 1fr);"
