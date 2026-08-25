# -*- coding: utf-8 -*-
"""Command Line Interface for multilayer-sdk."""

from __future__ import annotations

import argparse
import json
import os
import sys
import webbrowser

from multilayer import __version__
from multilayer.core import MultiMap, SwipeMap
from multilayer.layers import TileProvider, VectorLayer


def main(args: list[str] | None = None) -> int:
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="multilayer",
        description="Pure-Python Synchronized Multi-Panel Map Visualization & Spatial Comparison CLI.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: build
    build_parser = subparsers.add_parser("build", help="Build synchronized multi-panel HTML dashboard")
    build_parser.add_argument("--layers", "-l", required=True, help="Comma-separated list of GeoJSON layer paths")
    build_parser.add_argument("--grid", "-g", default="2x2", help="Grid preset: 1x2, 2x1, 1x3, 2x2, 2x3, 2x4 (default: 2x2)")
    build_parser.add_argument("--title", "-t", default="MultiMap Workspace", help="Dashboard title")
    build_parser.add_argument("--basemap", "-b", default="carto-dark-matter", help="Basemap provider (default: carto-dark-matter)")
    build_parser.add_argument("--theme", default="dark", choices=["dark", "light"], help="Color theme (default: dark)")
    build_parser.add_argument("--out", "-o", default="multimap_dashboard.html", help="Output HTML file path")
    build_parser.add_argument("--open", action="store_true", help="Open generated HTML dashboard in default browser")

    # Subcommand: compare (Swipe Map)
    compare_parser = subparsers.add_parser("compare", help="Create split-screen curtain swipe map")
    compare_parser.add_argument("left_layer", help="Left / Before GeoJSON file path")
    compare_parser.add_argument("right_layer", help="Right / After GeoJSON file path")
    compare_parser.add_argument("--left-title", default="Before", help="Left layer title")
    compare_parser.add_argument("--right-title", default="After", help="Right layer title")
    compare_parser.add_argument("--out", "-o", default="swipe_map.html", help="Output HTML file path")
    compare_parser.add_argument("--open", action="store_true", help="Open generated swipe map in browser")

    # Subcommand: inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect GeoJSON layer features, bounding box, and properties")
    inspect_parser.add_argument("input_file", help="GeoJSON file path to inspect")

    # Subcommand: tiles
    subparsers.add_parser("tiles", help="List all built-in web map tile basemaps")

    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 0

    if parsed_args.command == "build":
        layer_paths = [p.strip() for p in parsed_args.layers.split(",") if p.strip()]
        mm = MultiMap(
            grid=parsed_args.grid,
            title=parsed_args.title,
            theme=parsed_args.theme,
            basemap=parsed_args.basemap,
        )

        for idx, lp in enumerate(layer_paths):
            if not os.path.exists(lp):
                print(f"Error: Layer file not found: {lp}", file=sys.stderr)
                return 1
            if idx < mm.panel_count:
                vlyr = VectorLayer.from_geojson(lp)
                mm.panel(idx).add_layer(vlyr)
                mm.panel(idx).title = vlyr.name

        out_path = os.path.abspath(parsed_args.out)
        mm.to_html(out_path)
        print(f"✓ Synchronized MultiMap dashboard generated: {out_path} ({os.path.getsize(out_path):,} bytes)")

        if parsed_args.open:
            webbrowser.open(f"file://{out_path}")
        return 0

    elif parsed_args.command == "compare":
        if not os.path.exists(parsed_args.left_layer) or not os.path.exists(parsed_args.right_layer):
            print("Error: One or both layer files not found.", file=sys.stderr)
            return 1

        sm = SwipeMap(
            left_layer=parsed_args.left_layer,
            right_layer=parsed_args.right_layer,
            left_title=parsed_args.left_title,
            right_title=parsed_args.right_title,
        )
        out_path = os.path.abspath(parsed_args.out)
        sm.to_html(out_path)
        print(f"✓ Split-screen Swipe Map generated: {out_path} ({os.path.getsize(out_path):,} bytes)")

        if parsed_args.open:
            webbrowser.open(f"file://{out_path}")
        return 0

    elif parsed_args.command == "inspect":
        if not os.path.exists(parsed_args.input_file):
            print(f"Error: File not found: {parsed_args.input_file}", file=sys.stderr)
            return 1
        with open(parsed_args.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        v = VectorLayer.from_geojson(data, name=parsed_args.input_file)
        feats = data.get("features", [])
        bounds = v.get_bounds()
        props_keys = set()
        for ft in feats:
            props_keys.update(ft.get("properties", {}).keys())

        print(f"Layer File     : {parsed_args.input_file}")
        print(f"Feature Count  : {len(feats):,}")
        print(f"Bounding Box   : {bounds}")
        print(f"Properties ({len(props_keys)}) : {', '.join(sorted(props_keys))}")
        return 0

    elif parsed_args.command == "tiles":
        print("Available Built-in Tile Providers in multilayer-sdk:")
        for tp in TileProvider:
            if tp != TileProvider.NONE:
                print(f"  - {tp.value:<20} : {tp.url_template}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
