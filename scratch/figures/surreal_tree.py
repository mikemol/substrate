#!/usr/bin/env python3
"""The surreal number tree, stratified by birthday.

Conway's {L | R} construction (agda/Substrate/Algebra/Quotient/Surreal.agda):
day 0 has just 0; each later day the simplest new number is born in every gap.
The finite stages are exactly the dyadic rationals. Each node's left child is
the simplest number below it (within its bounds), its right child the simplest
above — which is the midpoint of the bounding interval, or an integer ±1 step
at the open ends.

Plotted with x = the number's value and y = −birthday, so the horizontal axis
*is* the number line and depth *is* the birthday: the tree fills the line by
dyadic bisection.
"""

from fractions import Fraction

from _gallery import finish, make_parser, set_style

args = make_parser("surreal_tree").parse_args()
set_style()

import matplotlib.pyplot as plt
import matplotlib as mpl

DEPTH = 4  # birthdays 0..DEPTH

INF = None  # sentinel for ±∞ bounds


def simplest(lo, hi, v, side):
    """Value of a child: midpoint if bounded, else an integer ±1 step."""
    if side == "L":
        return v - 1 if lo is INF else (lo + v) / Fraction(2)
    else:
        return v + 1 if hi is INF else (v + hi) / Fraction(2)


# Build the tree: each node (value, lo, hi, depth), children to DEPTH.
nodes = []   # (value, depth)
edges = []   # (value_parent, value_child)
root = (Fraction(0), INF, INF, 0)
stack = [root]
while stack:
    v, lo, hi, d = stack.pop()
    nodes.append((v, d))
    if d < DEPTH:
        lv = simplest(lo, hi, v, "L")
        rv = simplest(lo, hi, v, "R")
        edges.append((v, lv)); edges.append((v, rv))
        stack.append((Fraction(lv), lo, v, d + 1))
        stack.append((Fraction(rv), v, hi, d + 1))

depth_of = {v: d for (v, d) in nodes}


def label(fr: Fraction) -> str:
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"


fig, ax = plt.subplots(figsize=(15, 8))
cmap = mpl.colormaps["viridis"].resampled(DEPTH + 1)

# Edges.
for pv, cv in edges:
    ax.plot([float(pv), float(cv)], [-depth_of[pv], -depth_of[cv]],
            color="#bbbbbb", lw=1.0, zorder=1)

# Nodes coloured by birthday.
for v, d in nodes:
    ax.scatter([float(v)], [-d], s=520, color=cmap(d), edgecolors="#222222",
               linewidths=1.0, zorder=3)
    ax.text(float(v), -d, label(v), ha="center", va="center", fontsize=8,
            fontweight="bold", color=("white" if d >= 2 else "#111111"), zorder=4)

ax.set_yticks([-d for d in range(DEPTH + 1)])
ax.set_yticklabels([f"day {d}" for d in range(DEPTH + 1)])
ax.set_xlabel("value  (x-axis is the number line)")
ax.set_title("The surreal number tree, stratified by birthday  "
             "({L | R}, agda/Substrate/Algebra/Quotient/Surreal.agda)")
ax.grid(axis="x", color="#eeeeee")
ax.set_axisbelow(True)
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)

finish(fig, "surreal_tree", args)
