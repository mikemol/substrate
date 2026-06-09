#!/usr/bin/env python3
"""The S₄ permutohedron, breathing along the Fiedler eigenvector.

The 2D-ish figure embeds the permutohedron in 3-space and paints the Fiedler
value as colour. Here that scalar becomes geometry: the LiftMap `radial`
(_lift3d) displaces each vertex outward along its own direction by the Fiedler
amplitude, so the smoothest standing wave of the Cayley graph deforms the
polyhedron — it swells where φ₁ > 0 and contracts where φ₁ < 0.

This z-encoding is a gauge choice (radial displacement by a scalar); the
LiftMap label records that. Graph + spectrum core shared via _perm.
"""

from _perm import GENERATORS, Permutohedron
from _gallery import PALETTE, finish, make_parser, set_style
from _lift3d import radial, draw_graph, diegetic_box

parser = make_parser("permutohedron_s4_3d")
parser.add_argument("--amount", type=float, default=0.9,
                    help="Radial displacement scale for the Fiedler field.")
args = parser.parse_args()
set_style()

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
import numpy as np

P = Permutohedron()
LIFT = radial(args.amount)

# Base = the true 3D permutohedron coords; scalar = Fiedler eigenvector.
base = np.array([P.coords3[p] for p in P.nodes_list])
scalar = np.array([P.fiedler[P.index(p)] for p in P.nodes_list])
coords3 = LIFT(base, scalar)

idx = {p: i for i, p in enumerate(P.nodes_list)}
gen_color = {"s1": PALETTE[0], "s2": PALETTE[1], "s3": PALETTE[3]}
edges, edge_cols = [], []
for u, v, d in P.graph.edges(data=True):
    edges.append((idx[u], idx[v]))
    edge_cols.append(gen_color[d["generator"]])

fig = plt.figure(figsize=(11, 9.5))
ax = fig.add_subplot(111, projection="3d")

sc = draw_graph(ax, coords3, edges, node_color=scalar, cmap="coolwarm",
                node_size=240, edge_color=edge_cols, edge_lw=2.0,
                labels=["".join(map(str, p)) for p in P.nodes_list], label_size=6,
                depthshade=True)

cbar = fig.colorbar(sc, ax=ax, shrink=0.55, pad=0.02)
cbar.set_label("Fiedler eigenvector  φ₁  (= radial displacement)")
legend = [Line2D([0], [0], color=gen_color[g], lw=3, label=g) for g in GENERATORS]
ax.legend(handles=legend, loc="upper left", frameon=False, fontsize=10)

ax.set_box_aspect((1, 1, 0.9)); ax.set_axis_off()
ax.view_init(elev=22, azim=35)
# Diegetic box: real lit walls the object sits inside and casts shadows onto.
m = 0.3
ax.set_xlim(coords3[:, 0].min() - m, coords3[:, 0].max() + m)
ax.set_ylim(coords3[:, 1].min() - m, coords3[:, 1].max() + m)
ax.set_zlim(coords3[:, 2].min() - m, coords3[:, 2].max() + m)
diegetic_box(ax, shadow_points=coords3, wall_alpha=0.82, shadow_alpha=0.20)
ax.set_title("S₄ permutohedron — breathing along the Fiedler standing wave\n"
             f"LiftMap: {LIFT.label}", pad=4)

finish(fig, "permutohedron_s4_3d", args)
