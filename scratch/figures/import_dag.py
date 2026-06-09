#!/usr/bin/env python3
"""Package-level import graph of the Substrate Agda tree.

Parses `open import Substrate.…` / `import Substrate.…` lines across
agda/Substrate (the same import-edge extraction used by
scripts/audit_import_reach.py) and aggregates to the top-level package
(Substrate.Algebra, .Category, .Groups, …). Nodes are packages sized by module
count; directed edges are weighted by the number of cross-package imports.

A full 1300-module graph is unreadable, so this shows the load-bearing
package-level skeleton instead.
"""

from _gallery import PALETTE, finish, make_parser, set_style
from _graphs import package_import_graph

args = make_parser("import_dag").parse_args()
set_style()

import matplotlib.pyplot as plt
import networkx as nx

G, pkg_modules, edges, n_files = package_import_graph()
agda_files = [None] * n_files  # only the count is used below

fig, ax = plt.subplots(figsize=(13, 11))
pos = nx.spring_layout(G, seed=3, k=1.4, iterations=300,
                       weight="weight")

pkgs = sorted(G.nodes(), key=lambda p: pkg_modules[p], reverse=True)
color_of = {p: PALETTE[i % len(PALETTE)] for i, p in enumerate(pkgs)}
max_w = max(edges.values())

# Directed edges, width ∝ import count.
for a, b, d in G.edges(data=True):
    (x0, y0), (x1, y1) = pos[a], pos[b]
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color="#bbbbbb",
                                lw=0.4 + 4.0 * d["weight"] / max_w,
                                shrinkA=22, shrinkB=22, alpha=0.6))

# Nodes, area ∝ module count.
for p in G.nodes():
    x, y = pos[p]
    ax.scatter([x], [y], s=200 + 40 * pkg_modules[p], color=color_of[p],
               edgecolors="#222222", linewidths=1.0, zorder=3)
    ax.text(x, y, f"{p}\n({pkg_modules[p]})", ha="center", va="center",
            fontsize=8.5, fontweight="bold", zorder=4)

ax.set_axis_off()
ax.set_title(f"Substrate import graph — package level\n"
             f"{len(agda_files)} modules → {G.number_of_nodes()} packages · "
             f"node area ∝ module count · edge width ∝ cross-package imports "
             f"(cf. scripts/audit_import_reach.py)", fontsize=12)

finish(fig, "import_dag", args)
