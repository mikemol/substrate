#!/usr/bin/env python3
"""Hodge dual-grade ★ as a vertical fold tower — Blender/Cycles."""

import math
import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import numpy as np
import _blender as B

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

COUNTS = [4, 6, 4, 1]
PAIR = {0: "#D55E00", 3: "#D55E00", 1: "#0072B2", 2: "#0072B2"}
GAP = 1.3

B.reset()
B.scene(samples=128)
mats = {k: B.material(c, rough=0.4, metallic=0.1) for k, c in PAIR.items()}

allpts = []
for k in range(4):
    z = k * GAP
    n = COUNTS[k]
    radius = 0.7 + 0.16 * n
    for j in range(n):
        ang = 2 * math.pi * j / n + (math.pi / 4 if k in (1, 2) else 0)
        c = (radius * math.cos(ang), radius * math.sin(ang), z)
        allpts.append(c)
        B.sphere(c, 0.16, mats[k])
# Center pole-light: a bright white emissive axis that dominates the room.
B.tube((0, 0, 0), (0, 0, 3 * GAP), 0.05,
       B.material("#ffffff", emission=60.0, emission_color="#ffffff"))

# ★ fold arcs as bowed tubes (sampled splines via short segments).
for a, b, col in ((0, 3, "#D55E00"), (1, 2, "#0072B2")):
    cmat = B.material(col, rough=0.4)
    t = np.linspace(0, 1, 20)
    bow = 1.7 * np.sin(math.pi * t)
    pts = np.column_stack([bow, np.zeros_like(t), (a + (b - a) * t) * GAP])
    for i in range(len(pts) - 1):
        B.tube(pts[i], pts[i + 1], 0.035, cmat)

data = B.join_data()
B.driven_rig(data, direction=(1, -0.8, 0.45), align=(0, 0, -1), graze_factor=0.1)
B.render("hodge_bl")
