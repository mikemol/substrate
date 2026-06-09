#!/usr/bin/env python3
"""The idea lattice as a cocycle tower — Blender/Cycles."""

import math
import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(_H), str(_H.parents[1] / ".venv/lib/python3.14/site-packages")]

import numpy as np
import _blender as B
from _catalog import parse_levels

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

GAP = 1.6
levels = parse_levels()

B.reset()
B.scene(samples=128)
B.lights(key=(6, -6, 12), key_size=11, target=(0, 0, 7))
mat = {"invariant": B.material("#0072B2", rough=0.4, metallic=0.1),
       "gauge": B.material("#D55E00", rough=0.4, metallic=0.1),
       "other": B.material("#999999", rough=0.5)}

allpts = []
for lvl, _t, concepts in levels:
    z = lvl * GAP
    n = len(concepts)
    radius = 1.0 + 0.16 * n
    for k, (name, cls) in enumerate(concepts):
        ang = 2 * math.pi * k / max(n, 1)
        c = (radius * math.cos(ang), radius * math.sin(ang), z)
        allpts.append(c)
        B.sphere(c, 0.26, mat[cls])
zmax = (len(levels) - 1) * GAP
B.tube((0, 0, 0), (0, 0, zmax), 0.1, B.material("#cccccc", rough=0.6))

data = B.join_data()
B.driven_rig(data, direction=(1, -0.85, 0.5), align=(0, 0, -1), shift=(0.05, 0.18))
B.render("idea_bl")
