#!/usr/bin/env python3
"""Agda structural-similarity clusters in a 3D force layout.

Same similarity graph as the 2D figure (_graphs.similarity_graph), but laid out
with a 3D spring embedding so the orbits become separated clouds in space.
Node colour = connected component, size = degree.
"""

from _gallery import PALETTE, finish, make_parser, set_style
from _graphs import similarity_graph
from _lift3d import style_3d, floor_shadow

parser = make_parser("similarity_clusters_3d")
parser.add_argument("--glob", default="agda/Substrate/Groups/**/*.agda")
parser.add_argument("--threshold", type=float, default=0.55)
args = parser.parse_args()
set_style()

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import networkx as nx
import numpy as np

G = similarity_graph(args.glob, args.threshold)
if G.number_of_edges() == 0:
    raise SystemExit(f"No pairs above threshold {args.threshold} for {args.glob}")

comps = sorted(nx.connected_components(G), key=len, reverse=True)
comp_of = {n: ci for ci, comp in enumerate(comps) for n in comp}
pos = nx.spring_layout(G, dim=3, seed=7, k=1.1, iterations=250, weight="weight")
deg = dict(G.degree())

fig = plt.figure(figsize=(11, 10))
ax = fig.add_subplot(111, projection="3d")

for u, v, d in G.edges(data=True):
    p, q = pos[u], pos[v]
    ax.plot(*zip(p, q), color="#cccccc",
            lw=0.5 + 2.5 * (d["weight"] - args.threshold), alpha=0.6)
for n in G.nodes():
    x, y, z = pos[n]
    ax.scatter([x], [y], [z], s=80 + 50 * deg[n],
               color=PALETTE[comp_of[n] % len(PALETTE)], edgecolors="#222222",
               linewidths=0.6, depthshade=False)

for ci, comp in enumerate(comps):
    if len(comp) < 3:
        continue
    rep = max(comp, key=lambda n: deg[n])
    x, y, z = pos[rep]
    ax.text(x, y, z, f"  {rep} (+{len(comp)-1})", fontsize=8,
            color=PALETTE[ci % len(PALETTE)], fontweight="bold")

coords = np.array([pos[n] for n in G.nodes()])
floor_shadow(ax, coords, z=coords[:, 2].min() - 0.15, alpha=0.10, size=90)
ax.set_axis_off()
ax.view_init(elev=20, azim=40)
style_3d(ax)
ax.set_title(f"Agda similarity clusters in 3D  (score ≥ {args.threshold})\n"
             f"{G.number_of_nodes()} modules · {len(comps)} orbits "
             f"({args.glob})", pad=4)

finish(fig, "similarity_clusters_3d", args)
