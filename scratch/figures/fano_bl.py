#!/usr/bin/env python3
"""Fano plane in F2^3 — Blender/Cycles: transparency AND shadows together.

The VTK wall was that order-independent transparency fought cast shadows. In
Cycles both are correct at once: the translucent teal Fano planes tint the
floor *and* cast partial shadows, inside the full diegetic box.

Run:  blender --background --python scratch/figures/fano_bl.py
"""

import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import numpy as np
import _blender as B
from _fano import LINES, POINT_VEC, SINGER

B.OUT = _H / "out"
B.OUT.mkdir(exist_ok=True)

POINT_C, ORIGIN_C, LINE_C, SINGER_C, CUBE_C = (
    "#0072B2", "#999999", "#009E73", "#D55E00", "#cfcfcf")
V = {k: np.array(v, float) for k, v in POINT_VEC.items()}

B.reset()
B.scene(samples=200)

# Cube scaffold.
cube_mat = B.material(CUBE_C, rough=0.6)
corners = [np.array([x, y, z], float) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
for a in corners:
    for b in corners:
        if abs(np.sum(np.abs(a - b)) - 1) < 1e-9 and tuple(a) < tuple(b):
            B.tube(a, b, 0.006, cube_mat)

# The 7 Fano lines as translucent triangles (real Cycles transparency), cycled
# through the Okabe-Ito palette in SINGER 7-cycle order — the colour progression
# tracks the same cyclic symmetry drawn as the Singer orbit below (line k is the
# k-th Singer image of the base line).
OKABE7 = ["#E69F00", "#56B4E9", "#009E73", "#F0E442",
          "#0072B2", "#D55E00", "#CC79A7"]
by_set = {frozenset(tri): tri for tri in LINES.values()}
cur = frozenset(next(iter(LINES.values())))
for i in range(7):
    tri = by_set[cur]
    B.polys([np.array([V[t] for t in tri])],
            B.material(OKABE7[i], rough=0.3, alpha=0.45), smooth=True)
    cur = frozenset(SINGER[p] for p in cur)

# Points (blue) + origin (grey).
pmat = B.material(POINT_C, rough=0.35, metallic=0.1)
for v in V.values():
    B.sphere(v, 0.055, pmat)
B.sphere((0, 0, 0), 0.035, B.material(ORIGIN_C, rough=0.5))

# Singer 7-cycle.
smat = B.material(SINGER_C, rough=0.4)
order = ["e₁"]
while len(order) < 7:
    order.append(SINGER[order[-1]])
for a, b in zip(order, order[1:] + order[:1]):
    B.tube(V[a], V[b], 0.011, smat)

data = B.join_data()
B.driven_rig(data, direction=(1, -0.9, 0.55))
B.render("fano_bl")
