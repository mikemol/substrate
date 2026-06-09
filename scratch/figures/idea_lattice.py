#!/usr/bin/env python3
"""The substrate idea lattice as a layered cocycle tower.

Parses catalog/idea_lattice.md — its nine structural-dependence levels and the
concepts on each, tagged `[gauge]` (an operational degree of freedom) or
`[invariant]` (gauge-invariant content). Renders the levels as horizontal bands
(top = foundations, bottom = the M41 stack), one node per concept, coloured by
tag. This is the visible five-cocycle tower the catalogue describes.
"""

from _gallery import GAUGE_COLOR, INVARIANT_COLOR, finish, make_parser, set_style
from _catalog import parse_levels, short_name

args = make_parser("idea_lattice").parse_args()
set_style()

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch

OTHER_COLOR = "#999999"

levels = parse_levels()
color_of = {"gauge": GAUGE_COLOR, "invariant": INVARIANT_COLOR, "other": OTHER_COLOR}

fig, ax = plt.subplots(figsize=(15, 11))
max_w = max(len(c) for _, _, c in levels)
row_h = 1.0

for num, title, concepts in levels:
    y = -num * row_h
    # Level band + label.
    ax.add_patch(FancyBboxPatch((-0.4, y - 0.36), max_w + 0.6, 0.72,
                                boxstyle="round,pad=0.02", linewidth=0,
                                facecolor=("#f4f4f4" if num % 2 == 0 else "#ffffff"),
                                zorder=0))
    short = (title[:40] + "…") if len(title) > 41 else title
    ax.text(-0.6, y, f"L{num}", ha="right", va="center", fontsize=12,
            fontweight="bold", color="#333333")
    ax.text(max_w + 0.5, y, short, ha="left", va="center", fontsize=8,
            color="#777777")
    # Concept nodes, centred within the band.
    n = len(concepts)
    x0 = (max_w - n) / 2
    for k, (name, cls) in enumerate(concepts):
        x = x0 + k
        ax.scatter([x], [y], s=260, color=color_of[cls], edgecolors="#222222",
                   linewidths=0.8, zorder=3)
        ax.text(x, y - 0.26, short_name(name), ha="center", va="top", fontsize=5.6,
                rotation=40, color="#333333")
    # Faint spine connecting consecutive level centroids.
    if num > 0:
        ax.plot([max_w / 2, max_w / 2], [y + row_h - 0.36, y + 0.36],
                color="#dddddd", lw=8, zorder=-1, solid_capstyle="round")

ax.set_xlim(-2.5, max_w + 4)
ax.set_ylim(-len(levels) * row_h + 0.4, 0.8)
ax.set_axis_off()

legend = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=INVARIANT_COLOR,
           markersize=12, label="invariant (load-bearing structure)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor=GAUGE_COLOR,
           markersize=12, label="gauge (operational choice / cocycle)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor=OTHER_COLOR,
           markersize=12, label="framing"),
]
ax.legend(handles=legend, loc="lower center", ncol=3, frameon=False,
          bbox_to_anchor=(0.5, -0.02), fontsize=10)
ax.set_title("The substrate idea lattice — nine levels, the five-cocycle tower\n"
             "(catalog/idea_lattice.md)", fontsize=13, pad=12)

finish(fig, "idea_lattice", args)
