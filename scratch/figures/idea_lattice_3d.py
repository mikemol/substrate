#!/usr/bin/env python3
"""The idea lattice as a literal cocycle tower.

The 2D figure stacks the nine levels as horizontal bands. Here the LiftMap
`tower` (_lift3d) sends each level to its own height z = level, and the
concepts of a level are arranged on a ring at that height — so the
"five-cocycle tower" the catalogue describes becomes an actual tower. Gauge
concepts (the cocycles) glow orange against the invariant blue, and a central
spine threads the levels.

Parsing shared with idea_lattice.py via _catalog.
"""

import math

from _gallery import GAUGE_COLOR, INVARIANT_COLOR, finish, make_parser, set_style
from _catalog import parse_levels, short_name
from _lift3d import tower, style_3d

parser = make_parser("idea_lattice_3d")
parser.add_argument("--gap", type=float, default=1.6, help="Vertical gap between levels.")
args = parser.parse_args()
set_style()

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

OTHER_COLOR = "#999999"
color_of = {"gauge": GAUGE_COLOR, "invariant": INVARIANT_COLOR, "other": OTHER_COLOR}
LIFT = tower(args.gap)

levels = parse_levels()
n_levels = len(levels)

fig = plt.figure(figsize=(11, 11))
ax = fig.add_subplot(111, projection="3d")

# Central spine threading the levels.
zs = [LIFT(np.array([[0.0, 0.0]]), np.array([lvl]))[0, 2] for lvl, _, _ in levels]
ax.plot([0] * n_levels, [0] * n_levels, zs, color="#cccccc", lw=6,
        solid_capstyle="round", zorder=0)

for lvl, title, concepts in levels:
    n = len(concepts)
    z = LIFT(np.array([[0.0, 0.0]]), np.array([lvl]))[0, 2]
    radius = 1.0 + 0.18 * n
    for k, (name, cls) in enumerate(concepts):
        ang = 2 * math.pi * k / max(n, 1)
        x, y = radius * math.cos(ang), radius * math.sin(ang)
        ax.scatter([x], [y], [z], s=130, color=color_of[cls],
                   edgecolors="#222222", linewidths=0.6, depthshade=False, zorder=4)
        ax.text(x * 1.12, y * 1.12, z, short_name(name), fontsize=5,
                ha="center", va="center", color="#333333")
    ax.text(0, 0, z, f"L{lvl}", fontsize=11, fontweight="bold", ha="center",
            va="center", color="#222222", zorder=6)

ax.set_box_aspect((1, 1, 1.6))
ax.set_axis_off()
ax.view_init(elev=24, azim=30)
style_3d(ax)
legend = [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=INVARIANT_COLOR,
           markersize=11, label="invariant"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor=GAUGE_COLOR,
           markersize=11, label="gauge (cocycle)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor=OTHER_COLOR,
           markersize=11, label="framing"),
]
ax.legend(handles=legend, loc="upper left", frameon=False, fontsize=10)
ax.set_title("The idea lattice as a cocycle tower (catalog/idea_lattice.md)\n"
             f"LiftMap: {LIFT.label}", pad=4)

finish(fig, "idea_lattice_3d", args)
