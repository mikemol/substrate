#!/usr/bin/env python3
"""The surreal number tree, unfolded — Blender/Cycles."""

import pathlib
import sys
from fractions import Fraction

_H = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(_H), str(_H.parents[1] / ".venv/lib/python3.14/site-packages")]

import numpy as np
import _blender as B

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)
DEPTH = 5
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

# Colour by birthday via a viridis-ish ramp.
def ramp(t):
    a, b_, c = np.array([0.27, 0.0, 0.33]), np.array([0.13, 0.57, 0.55]), np.array([0.99, 0.91, 0.14])
    col = a + (b_ - a) * (t / 0.5) if t < 0.5 else b_ + (c - b_) * ((t - 0.5) / 0.5)
    return "#%02x%02x%02x" % tuple(int(round(x * 255)) for x in col)


B.reset()
B.scene(samples=128)
B.lights(key=(3, -7, 9), key_size=10)
emat = B.material("#cccccc", rough=0.6)
for a, b in edges:
    B.tube(coord(a), coord(b), 0.02, emat)
for v, d in nodes:
    B.sphere(coord(v), 0.15, B.material(ramp(d / DEPTH), rough=0.4))

b = (coords[:, 0].min(), coords[:, 0].max(), coords[:, 1].min(), coords[:, 1].max(),
     coords[:, 2].min(), coords[:, 2].max())
B.diegetic_box(b)
B.frame(coords, direction=(0.35, -1.0, 0.5), shift=(0.0, 0.08))
B.render("surreal_bl")
