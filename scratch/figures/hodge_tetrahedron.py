#!/usr/bin/env python3
"""Hodge duality on the 3-simplex — the dual-grade involution ★.

`dual-grade n k = n − k` from
    agda/Substrate/WitnessTower/Hodge.agda
is an involution (★★ = id) pairing grade k with grade n−k. At n = 3 (the
tetrahedron) it pairs vertices ↔ cell (0↔3) and edges ↔ faces (1↔2).

Left  : a regular tetrahedron with a highlighted vertex ↔ opposite-face Hodge
        pair (the 0 ↔ 3 / 1 ↔ 2 duality made geometric).
Right : the grade ladder 0–1–2–3 with the ★ involution arcs and the simplex
        face counts C(4, k+1) = 4, 6, 4, 1.
"""

import numpy as np

from _gallery import finish, make_parser, set_style

args = make_parser("hodge_tetrahedron").parse_args()
set_style()

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Regular tetrahedron vertices.
V = np.array([
    [1, 1, 1],
    [1, -1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
], dtype=float)
FACES = [(1, 2, 3), (0, 2, 3), (0, 1, 3), (0, 1, 2)]  # face i is opposite vertex i


def panel_tetra(ax):
    # All faces, faint; the face opposite V0 highlighted (Hodge dual of V0).
    for fi, f in enumerate(FACES):
        tri = V[list(f)]
        hot = (fi == 0)
        ax.add_collection3d(Poly3DCollection(
            [tri], facecolor=("#D55E00" if hot else "#56B4E9"),
            edgecolor="#222222", alpha=(0.45 if hot else 0.12), linewidths=1.2))
    # Edges.
    for i in range(4):
        for j in range(i + 1, 4):
            ax.plot(*zip(V[i], V[j]), color="#222222", lw=1.4, alpha=0.5)
    # Vertices; V0 highlighted as the dual of the opposite face.
    for i, p in enumerate(V):
        hot = (i == 0)
        ax.scatter(*p, s=(260 if hot else 150),
                   color=("#D55E00" if hot else "white"),
                   edgecolors="#222222", linewidths=1.4, depthshade=False, zorder=5)
        ax.text(*(p * 1.18), f"V{i}", ha="center", va="center", fontsize=11,
                fontweight="bold")
    # Centroid of the opposite face + the duality arrow.
    fc = V[list(FACES[0])].mean(axis=0)
    ax.plot(*zip(V[0], fc), color="#D55E00", lw=2.2, ls="--")
    ax.text(*(fc * 1.3 + np.array([0, 0, -0.15])), "★", color="#D55E00",
            fontsize=18, ha="center")
    ax.set_title("3-simplex:  vertex V0  ★→  opposite face\n(grade 0 ↔ grade 3)")
    ax.set_box_aspect((1, 1, 1)); ax.set_axis_off()
    ax.view_init(elev=18, azim=30)
    lim = 1.5
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)


def panel_ladder(ax):
    ax.set_xlim(-1, 4); ax.set_ylim(-1.4, 1.9); ax.axis("off")
    grades = [0, 1, 2, 3]
    counts = [4, 6, 4, 1]          # C(4, k+1): vertices, edges, faces, cell
    names = ["vertices", "edges", "faces", "cell"]
    dims = [1, 3, 3, 1]            # dim Λ^k(R³) = C(3,k)
    xs = grades
    sup = ["⁰", "¹", "²", "³"]
    for k in grades:
        ax.scatter([xs[k]], [0], s=1700, color="white", edgecolors="#222222",
                   linewidths=1.8, zorder=4)
        ax.text(xs[k], 0, f"Λ{sup[k]}",
                ha="center", va="center", fontsize=13, fontweight="bold", zorder=5)
        ax.text(xs[k], -0.55, f"grade {k}\n{names[k]}: {counts[k]}\ndim {dims[k]}",
                ha="center", va="top", fontsize=9, color="#333333")
    # The ★ involution arcs, curving upward: 0↔3 (outer) and 1↔2 (inner).
    for (a, b, rad, col) in ((0, 3, -0.45, "#D55E00"), (1, 2, -0.6, "#0072B2")):
        ax.add_patch(FancyArrowPatch(
            (xs[a], 0.12), (xs[b], 0.12), connectionstyle=f"arc3,rad={rad}",
            arrowstyle="<|-|>", mutation_scale=16, lw=2.2, color=col, zorder=3))
        mid = (xs[a] + xs[b]) / 2
        apex = 0.12 + abs(rad) * abs(xs[b] - xs[a]) / 2
        ax.text(mid, apex + 0.06, "★", ha="center", va="bottom", color=col,
                fontsize=16, fontweight="bold")
    ax.set_title("dual-grade ★ :  k ↦ 3 − k   (involution, ★★ = id)")


fig = plt.figure(figsize=(15, 7))
ax1 = fig.add_subplot(121, projection="3d")
ax2 = fig.add_subplot(122)
panel_tetra(ax1)
panel_ladder(ax2)
fig.suptitle("Hodge duality on the 3-simplex "
             "(agda/Substrate/WitnessTower/Hodge.agda)", fontsize=12, y=1.0)

finish(fig, "hodge_tetrahedron", args)
