#!/usr/bin/env python3
"""The Hodge grade ladder as a vertical tower — ★ as a fold.

dual-grade ★ : k ↦ 3 − k (agda/Substrate/WitnessTower/Hodge.agda) is an
involution. As a tower (LiftMap `tower`, z = grade) it becomes a literal fold:
grade 0 at the bottom ↔ grade 3 at the top, grade 1 ↔ grade 2 in the middle.
Each level is a ring of that grade's faces of the 3-simplex (counts 4, 6, 4, 1),
and ★ arcs connect the paired levels. The fold axis is the centre of the tower.
"""

import math

from _gallery import finish, make_parser, set_style
from _lift3d import tower, style_3d

args = make_parser("hodge_tetrahedron_3d").parse_args()
set_style()

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

LIFT = tower(1.0)
COUNTS = [4, 6, 4, 1]            # C(4,k+1): vertices, edges, faces, cell
NAMES = ["vertices", "edges", "faces", "cell"]
PAIR_COLOR = {0: "#D55E00", 3: "#D55E00", 1: "#0072B2", 2: "#0072B2"}

fig = plt.figure(figsize=(9.5, 10.5))
ax = fig.add_subplot(111, projection="3d")

# Central fold axis.
ax.plot([0, 0], [0, 0], [0, 3], color="#cccccc", lw=4, zorder=0)

pos = {}
for k in range(4):
    z = LIFT(np.array([[0.0, 0.0]]), np.array([k]))[0, 2]
    n = COUNTS[k]
    radius = 0.6 + 0.12 * n
    ring = []
    for j in range(n):
        ang = 2 * math.pi * j / n + (math.pi / 4 if k in (1, 2) else 0)
        x, y = radius * math.cos(ang), radius * math.sin(ang)
        ring.append((x, y, z))
        ax.scatter([x], [y], [z], s=150, color=PAIR_COLOR[k],
                   edgecolors="#222222", linewidths=0.6, depthshade=False, zorder=4)
    pos[k] = ring
    ax.text(radius + 0.5, 0, z, f"grade {k}\nΛ{['⁰','¹','²','³'][k]}  ({NAMES[k]}: {n})",
            fontsize=9, color="#333333", va="center")

# ★ fold arcs: 0↔3 (outer) and 1↔2 (inner), drawn as bundles of springs.
for (a, b) in ((0, 3), (1, 2)):
    za = LIFT(np.array([[0.0, 0.0]]), np.array([a]))[0, 2]
    zb = LIFT(np.array([[0.0, 0.0]]), np.array([b]))[0, 2]
    col = PAIR_COLOR[a]
    t = np.linspace(0, 1, 30)
    # a single representative ★ arc bowing out from the axis
    bow = 1.6 * np.sin(math.pi * t)
    ax.plot(bow, np.zeros_like(t), za + (zb - za) * t, color=col, lw=2.2, zorder=3)
    ax.text(1.7, 0, (za + zb) / 2, "★", color=col, fontsize=16, fontweight="bold")

ax.set_box_aspect((1, 1, 1.4)); ax.set_axis_off()
ax.view_init(elev=18, azim=35)
style_3d(ax)
ax.set_title("Hodge dual-grade ★ as a vertical fold\n"
             f"LiftMap: {LIFT.label}  ·  0↔3, 1↔2", pad=2)

finish(fig, "hodge_tetrahedron_3d", args)
