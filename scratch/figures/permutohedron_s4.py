#!/usr/bin/env python3
"""The S₄ permutohedron — the truncated octahedron Cayley graph.

24 vertices = permutations of (1,2,3,4), embedded as 4-vectors projected onto
the 3-space orthogonal to (1,1,1,1) (the true permutohedral geometry). Edges =
the adjacent-transposition Cayley graph, coloured by generator s₁/s₂/s₃.
Vertices coloured by the Fiedler Laplacian eigenvector — the smoothest standing
wave on the manifold.

Graph + spectrum construction lifted from `SpectralManifold` in
scratch/eliza/13.py (see _perm.py).
"""

from _perm import GENERATORS, Permutohedron
from _gallery import PALETTE, finish, make_parser, set_style

args = make_parser("permutohedron_s4").parse_args()
set_style()

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers 3d projection)
import numpy as np

P = Permutohedron()
gen_color = {"s1": PALETTE[0], "s2": PALETTE[1], "s3": PALETTE[3]}

fig = plt.figure(figsize=(11, 9.5))
ax = fig.add_subplot(111, projection="3d")

# Edges, coloured by generator.
for u, v, data in P.graph.edges(data=True):
    x0, y0, z0 = P.coords3[u]
    x1, y1, z1 = P.coords3[v]
    ax.plot([x0, x1], [y0, y1], [z0, z1],
            color=gen_color[data["generator"]], lw=2.2, alpha=0.85)

# Vertices, coloured by the Fiedler eigenvector.
xs, ys, zs, cs = [], [], [], []
for p in P.nodes_list:
    x, y, z = P.coords3[p]
    xs.append(x); ys.append(y); zs.append(z)
    cs.append(P.fiedler[P.index(p)])
sc = ax.scatter(xs, ys, zs, c=cs, cmap="coolwarm", s=240, depthshade=False,
                edgecolors="#222222", linewidths=1.0, zorder=5)

# Small permutation labels at each vertex.
for p in P.nodes_list:
    x, y, z = P.coords3[p]
    ax.text(x, y, z + 0.06, "".join(map(str, p)), ha="center", va="bottom",
            fontsize=7, color="#333333")

cbar = fig.colorbar(sc, ax=ax, shrink=0.55, pad=0.02)
cbar.set_label("Fiedler eigenvector  φ₁  (λ₁ = %.3f)" % P.eigenvalues[1])

legend = [Line2D([0], [0], color=gen_color[g], lw=3,
                 label=f"{g[0]}{chr(0x2080 + int(g[1]))} = ({g[1]} {int(g[1])+1})")
          for g in GENERATORS]
ax.legend(handles=legend, loc="upper left", frameon=False, fontsize=10)

ax.set_title("S₄ permutohedron  (truncated octahedron)\n"
             "24 chambers · adjacent-transposition Cayley graph · Fiedler colouring",
             pad=8)
ax.set_box_aspect((1, 1, 1))
ax.view_init(elev=22, azim=35)
ax.set_axis_off()

finish(fig, "permutohedron_s4", args)
