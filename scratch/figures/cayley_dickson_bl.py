#!/usr/bin/env python3
"""Octonion table read as a Cayley–Dickson tower — Blender/Cycles.

Same signed multiplication relief as octonion_bl, but the colour says *which
doubling* each sign came from. The CD construction is ℝ→ℂ→ℍ→𝕆; in the binary
basis (idx = i XOR j) the doubling level of a unit is its bit-length
(e₀→0, e₁→1, e₂,e₃→2, e₄…e₇→3), and a product's step is the max level of its two
operands — which carves the 8×8 table into the nested ℂ/ℍ/𝕆 blocks. Each nested
step gets a palette PAIR (lighter = +sign, darker = −sign), so the sign cocycle's
contribution per doubling is legible by hue; the up/down geometry reinforces it.

    blender --background --python scratch/figures/cayley_dickson_bl.py
"""

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


def cd_step(r, c):
    """Cayley–Dickson doubling step of e_r·e_c: the max doubling level of the
    operands (bit-length). 1 = ℂ, 2 = ℍ, 3 = 𝕆 — the nested table blocks."""
    return max(int(r).bit_length(), int(c).bit_length())


# One palette PAIR per nested CD step: (+sign, −sign), Okabe-Ito, lighter = +.
CD_PAIRS = {
    1: ("#56B4E9", "#0072B2"),   # ℂ — sky / blue
    2: ("#F0E442", "#009E73"),   # ℍ — yellow / green
    3: ("#E69F00", "#D55E00"),   # 𝕆 — orange / vermillion
}

B.reset()
B.scene(samples=128)
VIEW = (0.8, -1.0, 0.7)   # camera direction (toward camera); also passed to the rig
# Material per (step, sign), away-face backlight like octonion (perceived-half 6.5).
mats = {}
for step, (cp, cm) in CD_PAIRS.items():
    mats[(step, 1)] = B.material(cp, rough=0.15, emission=6.5, emission_away=VIEW)
    mats[(step, -1)] = B.material(cm, rough=0.15, emission=6.5, emission_away=VIEW)

centers = []
for r in range(8):
    for c in range(8):
        h = float(idx[r, c])
        if h <= 0:
            continue
        # +products rise above the z=0 grid plane, −products descend below it;
        # hue = the CD doubling the sign comes from, light/dark = the sign.
        s = 1 if sign[r, c] >= 0 else -1
        B.box_cube((c, r, s * h / 2), (0.82, 0.82, h), mats[(cd_step(r, c), s)])
        centers.append((c, r, s * h))
data = B.join_data()
# Same gallery as octonion: forward a full cell off the back wall, 0.6 metal
# mirror, deep f/8 focus keeping the tiled-perspective reflections sharp.
B.driven_rig(data, direction=VIEW, align=(0, -2.0 / 3, 0),
             wall_rough=0.1, wall_metallic=0.6, fstop=8.0)
B.render("cayley_dickson_bl")
