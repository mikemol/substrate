#!/usr/bin/env python3
"""The {7,3} order-3 heptagonal tiling — the canonical Klein-quartic picture.

GL(3,F₂) ≅ PSL(2,7) is the (orientation-preserving) automorphism group of the
Klein quartic, the genus-3 surface tiled by 24 heptagons, 3 to a vertex. Its
universal cover is the {7,3} tiling of the hyperbolic plane, drawn here in the
Poincaré disk: a central regular heptagon reflected across its edges (each
reflection = inversion in the geodesic circle).

Tiling geometry lives in _klein.py (shared with klein_quartic_3d.py). Ties to
agda/Substrate/Algebra/F2/FanoPlane.agda and [[klein-quartic-kinematic-anatomy]].
"""

import math

from _gallery import finish, make_parser, set_style
from _klein import P, arc_points, centroid, generate_tiling

parser = make_parser("klein_quartic_tiling")
parser.add_argument("--depth", type=int, default=8, help="Reflection BFS depth.")
parser.add_argument("--max-tiles", type=int, default=1400, help="Tile cap.")
args = parser.parse_args()
set_style()

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon

tiles, _ = generate_tiling(args.depth, args.max_tiles)

fig, ax = plt.subplots(figsize=(10, 10))
ax.set_aspect("equal"); ax.axis("off")
ax.set_xlim(-1.02, 1.02); ax.set_ylim(-1.02, 1.02)
ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor="#222222", lw=1.5))

cmap = mpl.colormaps["twilight"]
for tile in tiles:
    cx, cy = centroid(tile)
    rad = math.hypot(cx, cy)  # radial distance → concentric colouring
    boundary = np.vstack([arc_points(tile[i], tile[(i + 1) % P]) for i in range(P)])
    ax.add_patch(Polygon(boundary, closed=True,
                         facecolor=cmap(0.12 + 0.8 * rad),
                         edgecolor="white", lw=0.6, alpha=0.92))

ax.set_title(f"The {{7,3}} tiling — universal cover of the Klein quartic\n"
             f"GL(3,F₂) ≅ PSL(2,7) · {len(tiles)} heptagons · 3 to a vertex",
             pad=12)

finish(fig, "klein_quartic_tiling", args)
