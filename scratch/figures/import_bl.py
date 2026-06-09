#!/usr/bin/env python3
"""Substrate package import graph in 3D — Blender/Cycles."""

import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(_H), str(_H.parents[1] / ".venv/lib/python3.14/site-packages")]

import numpy as np
import networkx as nx
import _blender as B
from _graphs import package_import_graph

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

G, pkg_modules, edges, n_files = package_import_graph()
nodes = list(G.nodes())
nidx = {n: i for i, n in enumerate(nodes)}
pos = nx.spring_layout(G, dim=3, seed=3, k=1.5, iterations=300, weight="weight")
coords = np.array([pos[n] for n in nodes]) * 7.0
pkgs = sorted(nodes, key=lambda q: pkg_modules[q], reverse=True)
color_of = {q: B.PALETTE[i % len(B.PALETTE)] for i, q in enumerate(pkgs)}
mx = max(pkg_modules.values())

B.reset()
B.scene(samples=128)
B.lights(key=(6, -6, 10), key_size=11)
emat = B.material("#bbbbbb", rough=0.6)
for a, b in G.edges():
    B.tube(coords[nidx[a]], coords[nidx[b]], 0.018, emat)
for q in nodes:
    rad = 0.14 + 0.42 * (pkg_modules[q] / mx)
    B.sphere(coords[nidx[q]], rad, B.material(color_of[q], rough=0.4, metallic=0.1))

data = B.join_data()
B.driven_rig(data, direction=(1, -0.9, 0.55), shift=(0.05, 0.05))
B.render("import_bl")
