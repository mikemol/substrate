#!/usr/bin/env python3
"""Structural-similarity clusters among Agda modules.

Drives the existing multi-scale similarity tool
    scripts/agda_similarity.py --csv
(no scoring is reimplemented here) over a subtree, builds a graph whose edges
are file pairs scoring above a threshold, and lays it out force-directed.
Connected components are the similarity orbits — e.g. the Z₂/Z₄/Z₅/Z₇-Coxeter
ladder collapses to one tight clique.

Node colour = connected component; node size = degree.
"""

from _gallery import PALETTE, finish, make_parser, set_style
from _graphs import similarity_graph

parser = make_parser("similarity_clusters")
parser.add_argument("--glob", default="agda/Substrate/Groups/**/*.agda",
                    help="Glob of files to compare (default: the Groups subtree).")
parser.add_argument("--threshold", type=float, default=0.55,
                    help="Minimum similarity score for an edge (default 0.55).")
args = parser.parse_args()
set_style()

import matplotlib.pyplot as plt
import networkx as nx

G = similarity_graph(args.glob, args.threshold)

if G.number_of_edges() == 0:
    raise SystemExit(f"No pairs above threshold {args.threshold} for {args.glob}")

# Connected components = similarity orbits; colour and keep the larger ones.
comps = sorted(nx.connected_components(G), key=len, reverse=True)
comp_of = {}
for ci, comp in enumerate(comps):
    for n in comp:
        comp_of[n] = ci

fig, ax = plt.subplots(figsize=(13, 10))
pos = nx.spring_layout(G, seed=7, k=1.1, iterations=300, weight="weight")

# Edges, thicker for higher similarity.
for u, v, d in G.edges(data=True):
    ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]],
            color="#cccccc", lw=0.5 + 3.0 * (d["weight"] - args.threshold), zorder=1)

# Nodes.
deg = dict(G.degree())
for n in G.nodes():
    x, y = pos[n]
    ax.scatter([x], [y], s=80 + 50 * deg[n],
               color=PALETTE[comp_of[n] % len(PALETTE)],
               edgecolors="#222222", linewidths=0.8, zorder=3)

# Label one representative (highest-degree node) per component, offset above
# the cluster centroid so labels never collide with the blob.
import numpy as np
for ci, comp in enumerate(comps):
    if len(comp) < 2:
        continue
    rep = max(comp, key=lambda n: deg[n])
    cx = np.mean([pos[n][0] for n in comp])
    cy = max(pos[n][1] for n in comp)
    others = len(comp) - 1
    tag = rep + (f"  (+{others})" if others else "")
    ax.text(cx, cy + 0.09, tag, fontsize=9, ha="center", va="bottom", zorder=5,
            fontweight="bold", color=PALETTE[ci % len(PALETTE)],
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.8))

ax.set_axis_off()
n_named = sum(1 for c in comps if len(c) >= 3)
ax.set_title(f"Agda structural-similarity clusters  "
             f"(score ≥ {args.threshold},  {args.glob})\n"
             f"{G.number_of_nodes()} modules · {len(comps)} components · "
             f"{n_named} orbits of size ≥ 3   "
             f"(scripts/agda_similarity.py)", fontsize=12)

finish(fig, "similarity_clusters", args)
