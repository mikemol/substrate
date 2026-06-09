#!/usr/bin/env python3
"""S₄ permutohedron, breathing along Fiedler — PyVista (real shadows).

Same data as permutohedron_s4_3d.py (the _perm core, radial LiftMap on the
Fiedler field), but rendered with VTK: PBR spheres + tubes inside a diegetic
box, lit by a key light that casts a real shadow onto the floor and walls, with
screen-space ambient occlusion deepening the contacts.
"""

import numpy as np

from _perm import GENERATORS, Permutohedron
from _lift3d import radial
from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, spheres, title, tubes, PALETTE)

parser = make_parser("permutohedron_pv")
parser.add_argument("--amount", type=float, default=0.9)
args = parser.parse_args()

P = Permutohedron()
LIFT = radial(args.amount)
base = np.array([P.coords3[p] for p in P.nodes_list])
scalar = np.array([P.fiedler[P.index(p)] for p in P.nodes_list])
coords = LIFT(base, scalar)

idx = {p: i for i, p in enumerate(P.nodes_list)}
gen_color = {"s1": PALETTE[0], "s2": PALETTE[1], "s3": PALETTE[3]}
edges = [(idx[u], idx[v]) for u, v, _ in P.graph.edges(data=True)]
edge_cols = [gen_color[d["generator"]] for _, _, d in P.graph.edges(data=True)]

p = scene(args)
add_lights(p)

c = np.abs(scalar).max()
tubes(p, coords, edges, edge_cols, radius=0.012)
spheres(p, coords, scalars=scalar, cmap="coolwarm", radius=0.07, clim=(-c, c))

b = np.array([coords[:, 0].min(), coords[:, 0].max(),
              coords[:, 1].min(), coords[:, 1].max(),
              coords[:, 2].min(), coords[:, 2].max()])
diegetic_box(p, b, pad=0.18)
title(p, "S4 permutohedron - breathing along the Fiedler standing wave\n"
         "(PyVista: PBR + cast shadows + SSAO)")

finish(p, "permutohedron_pv", args,
       camera=frame_camera(coords, direction=(1.0, -0.95, 0.62), dist_mult=5.4))
