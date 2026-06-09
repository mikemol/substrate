#!/usr/bin/env python3
"""The Fano plane sitting inside its F₂³ cube — the canonical 3D origin.

The 2D Fano figure flattens away the fact that the 7 points ARE the 7 nonzero
vectors of F₂³. Here each point is placed at its actual cube corner (its bit
pattern, from _fano.POINT_VEC), the origin 000 included for context, and each of
the 7 lines {a, b, a+b} is drawn as a translucent triangle through three
corners. The Singer 7-cycle threads the nonzero corners. No gauge choice — the
coordinates are the mathematics.
"""

from _gallery import PALETTE, finish, make_parser, set_style
from _fano import LINES, POINT_VEC, SINGER
from _lift3d import diegetic_box

args = make_parser("fano_plane_3d").parse_args()
set_style()

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

fig = plt.figure(figsize=(10.5, 9.5))
ax = fig.add_subplot(111, projection="3d")

# Faint cube wireframe over F₂³.
corners = [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
cube_edges = [(a, b) for a in corners for b in corners
              if sum(abs(np.subtract(a, b))) == 1 and a < b]
ax.add_collection3d(Line3DCollection(
    [[a, b] for a, b in cube_edges], colors="#dddddd", linewidths=1.0))

# The 7 lines as translucent triangles through three corners.
for i, (lname, pts) in enumerate(LINES.items()):
    tri = [POINT_VEC[p] for p in pts]
    ax.add_collection3d(Poly3DCollection(
        [tri], facecolor=PALETTE[i % len(PALETTE)], edgecolor=PALETTE[i % len(PALETTE)],
        alpha=0.22, linewidths=1.8))

# Vertices: origin distinct, 7 nonzero points labelled.
ax.scatter(*[[0]] * 3, s=120, color="#cccccc", edgecolors="#888888", depthshade=False)
for name, vec in POINT_VEC.items():
    ax.scatter(*[[c] for c in vec], s=260, color="white", edgecolors="#222222",
               linewidths=1.4, depthshade=False, zorder=5)
    ax.text(vec[0], vec[1], vec[2] + 0.06, name, ha="center", fontsize=10,
            fontweight="bold")

# Singer 7-cycle threading the nonzero corners.
for src, dst in SINGER.items():
    a, b = np.array(POINT_VEC[src], float), np.array(POINT_VEC[dst], float)
    ax.quiver(*a, *(b - a), color=PALETTE[3], lw=1.6, arrow_length_ratio=0.12,
              alpha=0.8)

import numpy as np
ax.set_box_aspect((1, 1, 1))
ax.set_xlim(-0.15, 1.15); ax.set_ylim(-0.15, 1.15); ax.set_zlim(-0.25, 1.15)
ax.set_axis_off()
ax.view_init(elev=22, azim=35)
diegetic_box(ax, shadow_points=np.array(list(POINT_VEC.values()), float))
ax.set_title("The Fano plane inside F₂³\n"
             "7 points = nonzero vectors · 7 lines {a, b, a+b} · Singer 7-cycle",
             pad=4)

finish(fig, "fano_plane_3d", args)
