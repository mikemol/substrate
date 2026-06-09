#!/usr/bin/env python3
"""The surreal number tree, unfolded into 3D by birthday.

The 2D figure puts value on x and birthday on y, which crowds the dense day-N
row. Lifting birthday to z (the LiftMap `cartesian` over the depth scalar)
frees the y-axis to *unfold* each level — siblings spread out by their rank — so
the late-birthday numbers no longer collide. x is still the number line, z is
still the birthday; y is the unfolding room.
"""

from fractions import Fraction

from _gallery import finish, make_parser, set_style
from _lift3d import style_3d, floor_shadow

parser = make_parser("surreal_tree_3d")
parser.add_argument("--depth", type=int, default=5, help="Birthdays 0..depth.")
args = parser.parse_args()
set_style()

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

DEPTH = args.depth
INF = None


def simplest(lo, hi, v, side):
    if side == "L":
        return v - 1 if lo is INF else (lo + v) / Fraction(2)
    return v + 1 if hi is INF else (v + hi) / Fraction(2)


# Build the tree (value, depth, parent_value).
nodes = []
edges = []
root = (Fraction(0), INF, INF, 0)
stack = [root]
while stack:
    v, lo, hi, d = stack.pop()
    nodes.append((v, d))
    if d < DEPTH:
        lv = Fraction(simplest(lo, hi, v, "L"))
        rv = Fraction(simplest(lo, hi, v, "R"))
        edges.append((v, lv)); edges.append((v, rv))
        stack.append((lv, lo, v, d + 1))
        stack.append((rv, v, hi, d + 1))

# Unfold: within each birthday, spread nodes along y by rank (value order).
by_depth = {}
for v, d in nodes:
    by_depth.setdefault(d, []).append(v)
yof = {}
for d, vs in by_depth.items():
    vs_sorted = sorted(vs)
    n = len(vs_sorted)
    for i, v in enumerate(vs_sorted):
        yof[(d, v)] = (i - (n - 1) / 2) * (1.6 / max(n, 1))
depth_of = {v: d for v, d in nodes}


def label(fr):
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"


def coord(v):
    d = depth_of[v]
    return float(v), yof[(d, v)], float(d)


fig = plt.figure(figsize=(13, 9))
ax = fig.add_subplot(111, projection="3d")
cmap = mpl.colormaps["viridis"].resampled(DEPTH + 1)

for pv, cv in edges:
    x0, y0, z0 = coord(pv)
    x1, y1, z1 = coord(cv)
    ax.plot([x0, x1], [y0, y1], [z0, z1], color="#cccccc", lw=0.8, zorder=1)

for v, d in nodes:
    x, y, z = coord(v)
    ax.scatter([x], [y], [z], s=200, color=cmap(d), edgecolors="#222222",
               linewidths=0.6, depthshade=False, zorder=3)
    if d <= 3:
        ax.text(x, y, z + 0.12, label(v), fontsize=7, ha="center", zorder=4)

all_coords = np.array([coord(v) for v, _ in nodes])
floor_shadow(ax, all_coords, z=-0.3, alpha=0.08, size=80)
ax.set_xlabel("value")
ax.set_zlabel("birthday")
ax.set_yticks([])
ax.set_box_aspect((2, 1, 1))
ax.view_init(elev=18, azim=-60)
style_3d(ax)
ax.set_title("The surreal number tree, unfolded by birthday\n"
             "x = value · z = birthday · y = unfolding room (LiftMap: cartesian over depth)",
             pad=4)

finish(fig, "surreal_tree_3d", args)
