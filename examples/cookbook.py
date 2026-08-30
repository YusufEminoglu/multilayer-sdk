# -*- coding: utf-8 -*-
"""multilayer Cookbook — Multi-Panel Maps, 3D Globe & Curtain Compare."""

import multilayer

# 1. Curtain Map (Before vs After)
curtain = multilayer.CurtainMap(title_left="Baseline 2020", title_right="Masterplan 2026")
html_str = curtain.render_html()
print(f"Curtain Map HTML generated ({len(html_str)} chars)")

# 2. Particle Flow Map
flow = multilayer.ParticleFlowMap(title="Wind Vector Particles")
flow.add_vector(41.0, 29.0, u=2.5, v=1.1)
print(f"Particle Map vector count: {len(flow.vector_field_grid)}")

# 3. Multi-Page Atlas Generator
atlas = multilayer.MultiPageAtlas(title="Regional Plan Atlas", rows=2, cols=3)
sheets = atlas.generate_grid_index()
print(f"Generated Atlas Sheets: {len(sheets)}")
