#!/usr/bin/env python3
"""Agda structural-similarity clusters in 3D — Blender/Cycles."""

import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(_H), str(_H.parents[1] / ".venv/lib/python3.14/site-packages")]

import numpy as np
import networkx as nx
import _blender as B
from _graphs import similarity_graph

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

G = similarity_graph("agda/Substrate/Groups/**/*.agda", 0.55)
comps = sorted(nx.connected_components(G), key=len, reverse=True)
comp_of = {n: i for i, c in enumerate(comps) for n in c}
nodes = list(G.nodes())
nidx = {n: i for i, n in enumerate(nodes)}
pos = nx.spring_layout(G, dim=3, seed=7, k=1.1, iterations=250, weight="weight")
coords = np.array([pos[n] for n in nodes]) * 6.0

B.reset()
B.scene(samples=128)
B.lights(key=(6, -6, 10), key_size=10)
mats = [B.material(B.PALETTE[i % len(B.PALETTE)], rough=0.4, metallic=0.1) for i in range(len(comps))]
emat = B.material("#bbbbbb", rough=0.6)
for u, v in G.edges():
    B.tube(coords[nidx[u]], coords[nidx[v]], 0.02, emat)
for n in nodes:
    B.sphere(coords[nidx[n]], 0.13, mats[comp_of[n]])

b = (coords[:, 0].min(), coords[:, 0].max(), coords[:, 1].min(), coords[:, 1].max(),
     coords[:, 2].min(), coords[:, 2].max())
B.diegetic_box(b)
B.frame(coords, direction=(1, -0.9, 0.55), shift=(0.05, 0.05))
B.render("similarity_bl")
