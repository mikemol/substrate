#!/usr/bin/env python3
"""Agda structural-similarity clusters in 3D — PyVista.

The same similarity graph (_graphs.similarity_graph), 3D spring layout, nodes as
spheres coloured by connected component (Okabe-Ito), edges as tubes. Real
shadows in the diegetic box.
"""

import numpy as np

from _graphs import similarity_graph
from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, title, tubes, PALETTE)

parser = make_parser("similarity_pv")
parser.add_argument("--glob", default="agda/Substrate/Groups/**/*.agda")
parser.add_argument("--threshold", type=float, default=0.55)
args = parser.parse_args()
import networkx as nx
import pyvista as pv

G = similarity_graph(args.glob, args.threshold)
if G.number_of_edges() == 0:
    raise SystemExit("no edges above threshold")

comps = sorted(nx.connected_components(G), key=len, reverse=True)
comp_of = {n: i for i, c in enumerate(comps) for n in c}
nodes = list(G.nodes())
nidx = {n: i for i, n in enumerate(nodes)}
pos = nx.spring_layout(G, dim=3, seed=7, k=1.1, iterations=250, weight="weight")
coords = np.array([pos[n] for n in nodes]) * 6.0

p = scene(args)
add_lights(p)
tubes(p, coords, [(nidx[u], nidx[v]) for u, v in G.edges()], radius=0.02)
for n in nodes:
    p.add_mesh(pv.Sphere(radius=0.13, center=coords[nidx[n]]),
               color=PALETTE[comp_of[n] % len(PALETTE)], smooth_shading=True,
               specular=0.3)

b = (coords[:, 0].min(), coords[:, 0].max(), coords[:, 1].min(),
     coords[:, 1].max(), coords[:, 2].min(), coords[:, 2].max())
diegetic_box(p, b, pad=0.15)
title(p, f"Agda similarity clusters in 3D (score >= {args.threshold})\n"
         f"{G.number_of_nodes()} modules, {len(comps)} orbits")
finish(p, "similarity_pv", args,
       camera=frame_camera(coords, direction=(1, -0.9, 0.55), dist_mult=3.4))
