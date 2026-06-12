#!/usr/bin/env python3
"""Flat 2D test of the glyph geometry — verify the Euclidean construction on its
own (triangle ABC, apex C, tail CD produced through the true vertex A, filled-disc
pips at A/B) BEFORE mapping onto the 3D capsule. Renders TRUE / FALSE / UNSET with
the construction guide overlaid.

    .venv/bin/python scratch/figures/_glyph_2d.py
"""

import math
import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


def glyph_shapes(state, r):
    """Same construction as the figure. Returns (filled_polys, (A,B,C,D))."""
    e = 3.0 * r
    A = (-0.5 * e, 0.8660254 * e)                 # TRUE  (up-left)
    Bp = (0.5 * e, 0.8660254 * e)                 # FALSE (up-right)
    C = (0.0, 0.0)                                # apex
    ax, ay = C[0] - A[0], C[1] - A[1]             # produce AC beyond C, CD = CA
    L = math.hypot(ax, ay)
    D = (C[0] + e * ax / L, C[1] + e * ay / L)
    rs = 0.5 * r                                  # stroke radius
    polys = []
    a0 = math.atan2(D[1] - C[1], D[0] - C[0])     # tail = stadium (caps radius rs)
    sg, tail = 8, []
    for k in range(sg + 1):
        a = a0 - math.pi / 2 + math.pi * k / sg
        tail.append((D[0] + rs * math.cos(a), D[1] + rs * math.sin(a)))
    for k in range(sg + 1):
        a = a0 + math.pi / 2 + math.pi * k / sg
        tail.append((C[0] + rs * math.cos(a), C[1] + rs * math.sin(a)))
    polys.append(tail)

    def disc(c):
        return [(c[0] + rs * math.cos(2 * math.pi * k / 24),
                 c[1] + rs * math.sin(2 * math.pi * k / 24)) for k in range(24)]
    for pt, is_set in ((A, state == 1), (Bp, state == 0)):
        if is_set:
            polys.append(disc(pt))
    return polys, (A, Bp, C, D)


fig, axes = plt.subplots(1, 3, figsize=(9, 5))
for ax, (state, name) in zip(axes, [(1, "TRUE (b=1)"), (0, "FALSE (b=0)"), (None, "UNSET")]):
    polys, (A, Bp, C, D) = glyph_shapes(state, 1.0)
    ax.plot(*zip(A, Bp, C, A), color="0.55", lw=0.9, zorder=1)        # triangle ABC
    ax.plot(*zip(A, D), color="0.7", lw=0.7, ls="--", zorder=1)       # A–C–D line
    for p, lab in ((A, "A·true"), (Bp, "B·false"), (C, "C"), (D, "D")):
        ax.annotate(lab, p, fontsize=8, color="0.6",
                    xytext=(4, 4), textcoords="offset points")
    for poly in polys:
        ax.add_patch(Polygon(poly, closed=True, facecolor="white",
                             edgecolor="0.2", lw=0.6, zorder=2))
    ax.set_facecolor("#222"); ax.set_aspect("equal"); ax.set_title(name)
    ax.set_xlim(-3, 3); ax.set_ylim(-4, 4)
fig.tight_layout()
fig.savefig(_H / "out" / "glyph_2d.png", dpi=120)
print("wrote out/glyph_2d.png")
