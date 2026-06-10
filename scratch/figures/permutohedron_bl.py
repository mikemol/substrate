#!/usr/bin/env python3
"""S4 permutohedron breathing along Fiedler — Blender/Cycles.

Run:  blender --background --python scratch/figures/permutohedron_bl.py
"""

import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import numpy as np
import _blender as B
from _perm import Permutohedron
from _lift3d import radial

B.OUT = _H / "out"
B.OUT.mkdir(exist_ok=True)


def coolwarm(t):  # t in [0,1] -> blue–white–red, returned as sRGB hex
    t = max(0.0, min(1.0, t))
    lo, mid, hi = np.array([0.23, 0.30, 0.75]), np.array([0.95, 0.95, 0.95]), np.array([0.71, 0.05, 0.15])
    c = lo + (mid - lo) * (t / 0.5) if t < 0.5 else mid + (hi - mid) * ((t - 0.5) / 0.5)
    return "#%02x%02x%02x" % tuple(int(round(x * 255)) for x in c)


P = Permutohedron()
LIFT = radial(0.9)
base = np.array([P.coords3[p] for p in P.nodes_list])
scalar = np.array([P.fiedler[P.index(p)] for p in P.nodes_list])
coords = LIFT(base, scalar)
cmax = float(np.abs(scalar).max())

idx = {p: i for i, p in enumerate(P.nodes_list)}
gen_color = {"s1": B.PALETTE[0], "s2": B.PALETTE[1], "s3": B.PALETTE[3]}

B.reset()
B.scene(samples=160, haze=0.0)

mats = {g: B.material(c, rough=0.4, emission=16.0, emission_color=c)
        for g, c in gen_color.items()}
for u, v, d in P.graph.edges(data=True):
    B.tube(coords[idx[u]], coords[idx[v]], 0.012, mats[d["generator"]])
for i, p in enumerate(P.nodes_list):
    t = (scalar[i] / cmax + 1) / 2
    B.sphere(coords[i], 0.07, B.material(coolwarm(t), rough=0.35, metallic=0.1))

# Declarative rig: join the data, then let the box scale to 1.5x its bbox and
# the camera back off to frame it — both driven, no manual bounds/distance.
data = B.join_data()
B.driven_rig(data, direction=(1.0, -0.95, 0.62), graze_factor=0.1)
B.render("permutohedron_bl")
