#!/usr/bin/env python3
"""The surreal number tree, unfolded — PyVista.

x = value, z = birthday, y = unfolding room. Nodes are spheres coloured by
birthday; edges are tubes. Real shadows into the diegetic box.
"""

from fractions import Fraction

import numpy as np

from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, spheres, title, tubes)

parser = make_parser("surreal_pv")
parser.add_argument("--depth", type=int, default=5)
args = parser.parse_args()
import pyvista as pv

DEPTH = args.depth
INF = None


def simplest(lo, hi, v, side):
    if side == "L":
        return v - 1 if lo is INF else (lo + v) / Fraction(2)
    return v + 1 if hi is INF else (v + hi) / Fraction(2)


nodes, edges = [], []
stack = [(Fraction(0), INF, INF, 0)]
while stack:
    v, lo, hi, d = stack.pop()
    nodes.append((v, d))
    if d < DEPTH:
        lv = Fraction(simplest(lo, hi, v, "L")); rv = Fraction(simplest(lo, hi, v, "R"))
        edges.append((v, lv)); edges.append((v, rv))
        stack.append((lv, lo, v, d + 1)); stack.append((rv, v, hi, d + 1))

by_depth = {}
for v, d in nodes:
    by_depth.setdefault(d, []).append(v)
yof = {}
for d, vs in by_depth.items():
    vs = sorted(vs); n = len(vs)
    for i, v in enumerate(vs):
        yof[(d, v)] = (i - (n - 1) / 2) * (2.4 / max(n, 1))
depth_of = {v: d for v, d in nodes}


def coord(v):
    d = depth_of[v]
    return (float(v), yof[(d, v)], float(d) * 0.8)


coords = np.array([coord(v) for v, _ in nodes])
idx = {v: i for i, (v, _) in enumerate(nodes)}

p = scene(args)
add_lights(p)
tube_edges = [(idx[a], idx[b]) for a, b in edges]
tubes(p, coords, tube_edges, radius=0.02)
spheres(p, coords, scalars=[d for _, d in nodes], cmap="viridis", radius=0.16)

b = (coords[:, 0].min(), coords[:, 0].max(), coords[:, 1].min(),
     coords[:, 1].max(), coords[:, 2].min(), coords[:, 2].max())
diegetic_box(p, b, pad=0.12)
title(p, "The surreal number tree, unfolded by birthday\n"
         "x = value, z = birthday, y = unfolding room")
finish(p, "surreal_pv", args,
       camera=frame_camera(coords, direction=(0.4, -1.0, 0.45), dist_mult=3.6))
