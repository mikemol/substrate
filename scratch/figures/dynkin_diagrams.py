#!/usr/bin/env python3
"""Dynkin diagrams of the crystallographic Cartan types.

A `CartanType` (agda/Substrate/Category/CartanType.agda) is a rank plus a
Coxeter matrix m : Fin rank → Fin rank → ℕ with m i i = 1, symmetric, and
m i j ≥ 2 off-diagonal. Its Dynkin diagram draws one node per simple root and a
bond of multiplicity {1,2,3} between roots i,j according to
m i j ∈ {3,4,6} (and no bond when m i j = 2).

A contact sheet of the finite types A–G. Bond multiplicity = number of lines;
the arrow on B/C/F/G points toward the short root.
"""

from _gallery import PALETTE, finish, make_parser, set_style

args = make_parser("dynkin_diagrams").parse_args()
set_style()

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow

# Each diagram: node positions + bonds (i, j, multiplicity, arrow_dir).
# arrow_dir: 0 none, +1 i→j, -1 j→i (toward the short root).
NODE = "#0072B2"


def line(n):
    return {i: (i, 0.0) for i in range(n)}


DIAGRAMS = {
    "A₄": (line(5), [(i, i + 1, 1, 0) for i in range(4)]),
    "B₄": (line(4), [(0, 1, 1, 0), (1, 2, 1, 0), (2, 3, 2, +1)]),
    "C₄": (line(4), [(0, 1, 1, 0), (1, 2, 1, 0), (2, 3, 2, -1)]),
    "D₅": ({0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0.6), 4: (3, -0.6)},
           [(0, 1, 1, 0), (1, 2, 1, 0), (2, 3, 1, 0), (2, 4, 1, 0)]),
    "E₆": ({0: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0), 4: (4, 0), 5: (2, 1)},
           [(0, 1, 1, 0), (1, 2, 1, 0), (2, 3, 1, 0), (3, 4, 1, 0), (2, 5, 1, 0)]),
    "E₇": ({i: (i, 0) for i in range(6)} | {6: (2, 1)},
           [(i, i + 1, 1, 0) for i in range(5)] + [(2, 6, 1, 0)]),
    "E₈": ({i: (i, 0) for i in range(7)} | {7: (2, 1)},
           [(i, i + 1, 1, 0) for i in range(6)] + [(2, 7, 1, 0)]),
    "F₄": (line(4), [(0, 1, 1, 0), (1, 2, 2, +1), (2, 3, 1, 0)]),
    "G₂": (line(2), [(0, 1, 3, +1)]),
}


def draw_bond(ax, p, q, mult, arrow):
    (x0, y0), (x1, y1) = p, q
    # Offsets perpendicular to the bond for double/triple lines.
    import math
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ox, oy = -dy / L, dx / L
    offs = {1: [0.0], 2: [-0.06, 0.06], 3: [-0.09, 0.0, 0.09]}[mult]
    for off in offs:
        ax.plot([x0 + ox * off, x1 + ox * off], [y0 + oy * off, y1 + oy * off],
                color="#222222", lw=1.6, zorder=1)
    if arrow:
        # Arrowhead at the centre pointing toward the short root.
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        sgn = arrow
        ax.add_patch(FancyArrow(
            mx - sgn * dx * 0.12, my - sgn * dy * 0.12,
            sgn * dx * 0.22, sgn * dy * 0.22,
            width=0.0, head_width=0.16, head_length=0.13,
            length_includes_head=True, color="#222222", zorder=3))


fig, axes = plt.subplots(3, 3, figsize=(13.5, 9))
for ax, (name, (nodes, bonds)) in zip(axes.flat, DIAGRAMS.items()):
    for (i, j, mult, arrow) in bonds:
        draw_bond(ax, nodes[i], nodes[j], mult, arrow)
    for i, (x, y) in nodes.items():
        ax.scatter([x], [y], s=170, color=NODE, edgecolors="#222222",
                   linewidths=1.2, zorder=4)
    xs = [p[0] for p in nodes.values()]
    ys = [p[1] for p in nodes.values()]
    ax.set_xlim(min(xs) - 0.6, max(xs) + 0.6)
    ax.set_ylim(min(ys) - 0.9, max(ys) + 0.9)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(name, fontsize=15)

fig.suptitle("Dynkin diagrams of the finite Cartan types\n"
             "bond multiplicity from m_ij ∈ {3,4,6};  arrow → short root "
             "(agda/Substrate/Category/CartanType.agda)",
             fontsize=12, y=1.0)

finish(fig, "dynkin_diagrams", args)
