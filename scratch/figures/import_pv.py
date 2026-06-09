#!/usr/bin/env python3
"""Substrate package import graph in 3D — PyVista.

Package-level graph (_graphs.package_import_graph), 3D spring layout, node radius
∝ module count, edges as tubes. Real shadows in the diegetic box.
"""

import numpy as np

from _graphs import package_import_graph
from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, title, tubes, PALETTE)

args = make_parser("import_pv").parse_args()
import networkx as nx
import pyvista as pv

G, pkg_modules, edges, n_files = package_import_graph()
nodes = list(G.nodes())
nidx = {n: i for i, n in enumerate(nodes)}
pos = nx.spring_layout(G, dim=3, seed=3, k=1.5, iterations=300, weight="weight")
coords = np.array([pos[n] for n in nodes]) * 7.0
pkgs = sorted(nodes, key=lambda q: pkg_modules[q], reverse=True)
color_of = {q: PALETTE[i % len(PALETTE)] for i, q in enumerate(pkgs)}
mx = max(pkg_modules.values())

p = scene(args)
add_lights(p)
tubes(p, coords, [(nidx[a], nidx[b]) for a, b in G.edges()], radius=0.018)
for q in nodes:
    rad = 0.14 + 0.4 * (pkg_modules[q] / mx)
    p.add_mesh(pv.Sphere(radius=rad, center=coords[nidx[q]]), color=color_of[q],
               smooth_shading=True, specular=0.3)

b = (coords[:, 0].min(), coords[:, 0].max(), coords[:, 1].min(),
     coords[:, 1].max(), coords[:, 2].min(), coords[:, 2].max())
diegetic_box(p, b, pad=0.15)
title(p, f"Substrate import graph in 3D - {n_files} modules, "
         f"{G.number_of_nodes()} packages\nnode size proportional to module count")
finish(p, "import_pv", args,
       camera=frame_camera(coords, direction=(1, -0.9, 0.55), dist_mult=3.2))
