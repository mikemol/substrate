#!/usr/bin/env python3
"""Octonion Cayley table relief — Blender/Cycles."""

import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import numpy as np
import _blender as B
from _fano import octonion_table

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

sign, idx = octonion_table()

B.reset()
B.scene(samples=128)
VIEW = (0.8, -1.0, 0.7)   # camera direction (toward camera); also passed to the rig
# Perceived-brightness half of the original 30: sRGB γ≈2.2 ⇒ ×(½)^2.2 ≈ 0.22.
POS = B.material("#E69F00", rough=0.15, emission=6.5, emission_away=VIEW)
NEG = B.material("#0072B2", rough=0.15, emission=6.5, emission_away=VIEW)

centers = []
for r in range(8):
    for c in range(8):
        h = float(idx[r, c])
        if h <= 0:
            continue
        # Sign lives in the geometry: +products rise ABOVE the z=0 grid plane,
        # −products descend BELOW it (no gravity to respect in 3-space). Height
        # = which unit e_h the product is; colour reinforces the sign.
        s = 1 if sign[r, c] >= 0 else -1
        B.box_cube((c, r, s * h / 2), (0.82, 0.82, h), POS if s > 0 else NEG)
        centers.append((c, r, s * h))
data = B.join_data()
# Pull the bars forward (−Y, toward the camera) off the back wall so the
# away-face backlight isn't pooling on it: the box's nested rule-of-thirds is 9
# cells/axis, one align unit = box/6 = 1.5 cells, so a cell = align 2/3. A full
# cell forward (two half-cells) = align −2/3; forward (off the +Y wall) is negative.
B.driven_rig(data, direction=VIEW, align=(0, -2.0 / 3, 0), wall_rough=0.1)
B.render("octonion_bl")
