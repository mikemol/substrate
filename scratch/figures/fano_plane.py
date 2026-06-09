#!/usr/bin/env python3
"""The Fano plane ℙ²(F₂) and its Singer 7-cycle.

Data is lifted verbatim from
    agda/Substrate/Algebra/F2/FanoPlane.agda
the 7 points (nonzero vectors of F₂³), the 7 lines (`line-points`), and the
`singer` order-7 automorphism (multiplication by x in F₈ = F₂[x]/(x³+x+1)).

Left panel  : the incidence diagram — 7 points on 7 lines, 3 points per line
              (6 straight lines + 1 inscribed circle through the midpoints).
Right panel : the same point positions with the Singer 7-cycle as a directed
              orbit, the canonical order-7 element of GL(3,F₂).
"""

import math

from _gallery import PALETTE, finish, make_parser, set_style
from _fano import LINES, SINGER

args = make_parser("fano_plane").parse_args()
set_style()

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch

# --- Points: the 7 nonzero vectors of F₂³ (FanoPlane.agda:42-43). ---
# Standard layout: equilateral triangle (corners = basis vectors), edge
# midpoints (pairwise sums), centroid (all-ones e₁₂₃).
R = 1.0
POS = {
    "e₁":   (0.0,  R),
    "e₂":   (-R * math.sin(math.radians(60)), -R / 2),
    "e₃":   (R * math.sin(math.radians(60)), -R / 2),
}
POS["e₁₂"]  = (((POS["e₁"][0] + POS["e₂"][0]) / 2), (POS["e₁"][1] + POS["e₂"][1]) / 2)
POS["e₁₃"]  = (((POS["e₁"][0] + POS["e₃"][0]) / 2), (POS["e₁"][1] + POS["e₃"][1]) / 2)
POS["e₂₃"]  = (((POS["e₂"][0] + POS["e₃"][0]) / 2), (POS["e₂"][1] + POS["e₃"][1]) / 2)
POS["e₁₂₃"] = (0.0, 0.0)

# --- Lines: the 7 `line-points` triples (from _fano.LINES). ---
# Six are drawn as straight segments; L₁₂-₁₃ (the three midpoints) is the
# inscribed circle.
LINES_STRAIGHT = {k: v for k, v in LINES.items() if k != "L₁₂-₁₃"}
LINE_CIRCLE = LINES["L₁₂-₁₃"]  # the inscribed circle.


def draw_points(ax):
    for name, (x, y) in POS.items():
        ax.scatter([x], [y], s=420, zorder=5, color="white",
                   edgecolors="#222222", linewidths=1.6)
        ax.text(x, y, name, ha="center", va="center", fontsize=10,
                fontweight="bold", zorder=6)


def panel_incidence(ax):
    # Straight lines: extend a touch past the endpoints for a clean look.
    for i, (lname, pts) in enumerate(LINES_STRAIGHT.items()):
        coords = [POS[p] for p in pts]
        coords.sort(key=lambda c: (c[0], c[1]))
        (x0, y0), (x1, y1) = coords[0], coords[-1]
        dx, dy = x1 - x0, y1 - y0
        ax.plot([x0 - 0.06 * dx, x1 + 0.06 * dx],
                [y0 - 0.06 * dy, y1 + 0.06 * dy],
                color=PALETTE[i % len(PALETTE)], lw=2.4, zorder=2, alpha=0.85)
    # The seventh line: inscribed circle through the three midpoints.
    cx, cy = POS["e₁₂₃"]
    rad = math.dist(POS["e₁₂"], (cx, cy))
    ax.add_patch(Circle((cx, cy), rad, fill=False, lw=2.4,
                        edgecolor=PALETTE[6], zorder=2, alpha=0.9))
    draw_points(ax)
    ax.set_title("Fano plane  ℙ²(F₂)\n7 points · 7 lines · 3 points per line")


def panel_singer(ax):
    # Faint incidence backdrop.
    for pts in LINES_STRAIGHT.values():
        coords = [POS[p] for p in pts]
        coords.sort(key=lambda c: (c[0], c[1]))
        (x0, y0), (x1, y1) = coords[0], coords[-1]
        ax.plot([x0, x1], [y0, y1], color="#cccccc", lw=1.0, zorder=1)
    cx, cy = POS["e₁₂₃"]
    ax.add_patch(Circle((cx, cy), math.dist(POS["e₁₂"], (cx, cy)),
                        fill=False, lw=1.0, edgecolor="#cccccc", zorder=1))
    # Singer orbit as curved directed arrows.
    for src, dst in SINGER.items():
        x0, y0 = POS[src]
        x1, y1 = POS[dst]
        ax.add_patch(FancyArrowPatch(
            (x0, y0), (x1, y1), connectionstyle="arc3,rad=0.22",
            arrowstyle="-|>", mutation_scale=16, lw=2.0,
            color=PALETTE[3], zorder=4, shrinkA=14, shrinkB=14))
    draw_points(ax)
    ax.set_title("Singer 7-cycle\nx · (–) in F₈ = F₂[x]/(x³+x+1),  order-7 of GL(3,F₂)")


fig, axes = plt.subplots(1, 2, figsize=(15, 7.6))
for ax in axes:
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-0.95, 1.25)
panel_incidence(axes[0])
panel_singer(axes[1])
fig.suptitle("agda/Substrate/Algebra/F2/FanoPlane.agda", fontsize=11,
             y=0.04, color="#777777")

finish(fig, "fano_plane", args)
