#!/usr/bin/env python3
"""Octonion Cayley table relief — Blender/Cycles."""

import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(_H), str(_H.parents[1] / ".venv/lib/python3.14/site-packages")]

import numpy as np
import _blender as B
from _fano import octonion_table

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

sign, idx = octonion_table()

B.reset()
B.scene(samples=128)
B.lights(key=(6, -6, 10), key_size=10, target=(3.5, 3.5, 1))
POS = B.material("#E69F00", rough=0.4)   # materials AFTER reset (reset wipes data)
NEG = B.material("#0072B2", rough=0.4)

centers = []
for r in range(8):
    for c in range(8):
        h = float(idx[r, c])
        if h <= 0:
            continue
        B.box_cube((c, r, h / 2), (0.82, 0.82, h), POS if sign[r, c] >= 0 else NEG)
        centers.append((c, r, h))
centers = np.array(centers + [[3.5, 3.5, 0]])

B.diegetic_box((0, 7, 0, 7, 0, 7), vbias=0.3)
B.frame(centers, direction=(0.8, -1.0, 0.7), shift=(0.05, 0.12))
B.render("octonion_bl")
