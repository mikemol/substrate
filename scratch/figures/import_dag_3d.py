#!/usr/bin/env python3
"""The Substrate package import graph in a 3D force layout.

Same package-level graph as the 2D figure (_graphs.package_import_graph), laid
out with a 3D spring embedding: the high-fan-in packages (Algebra, Category,
Foundation) settle into the core, the leaves orbit outside. Node size ∝ module
count, edge width ∝ cross-package imports.
"""

from _gallery import PALETTE, finish, make_parser, set_style
from _graphs import package_import_graph
from _lift3d import style_3d, floor_shadow

args = make_parser("import_dag_3d").parse_args()
set_style()

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import networkx as nx
import numpy as np

G, pkg_modules, edges, n_files = package_import_graph()
pos = nx.spring_layout(G, dim=3, seed=3, k=1.5, iterations=300, weight="weight")
pkgs = sorted(G.nodes(), key=lambda p: pkg_modules[p], reverse=True)
color_of = {p: PALETTE[i % len(PALETTE)] for i, p in enumerate(pkgs)}
max_w = max(edges.values())

fig = plt.figure(figsize=(12, 11))
ax = fig.add_subplot(111, projection="3d")

for a, b, d in G.edges(data=True):
    p, q = pos[a], pos[b]
    ax.plot(*zip(p, q), color="#cccccc",
            lw=0.4 + 3.5 * d["weight"] / max_w, alpha=0.5)
for p in G.nodes():
    x, y, z = pos[p]
    ax.scatter([x], [y], [z], s=120 + 35 * pkg_modules[p], color=color_of[p],
               edgecolors="#222222", linewidths=0.8, depthshade=False)
    ax.text(x, y, z, f"  {p} ({pkg_modules[p]})", fontsize=7.5, fontweight="bold")

coords = np.array([pos[p] for p in G.nodes()])
floor_shadow(ax, coords, z=coords[:, 2].min() - 0.15, alpha=0.10, size=110)
ax.set_axis_off()
ax.view_init(elev=20, azim=35)
style_3d(ax)
ax.set_title(f"Substrate import graph in 3D — {n_files} modules → "
             f"{G.number_of_nodes()} packages\n"
             "node size ∝ module count · edge width ∝ cross-package imports", pad=4)

finish(fig, "import_dag_3d", args)
