#!/usr/bin/env python3
"""Octonion table as a Cayley–Dickson tower — z IS the CD level. Blender/Cycles.

The CD sign cocycle factorises: e_i·e_j = (∏_L σ_L)·e_{i⊕j}, with σ_L ∈ {±1} the
sign introduced at doubling level L. Here the VERTICAL axis is the level itself:
ℂ occupies |z|∈[0,1], ℍ |z|∈[1,2], 𝕆 |z|∈[2,3], each a single hue
(ℂ blue, ℍ green, 𝕆 orange). So a horizontal z=n slice is ONE level = ONE colour,
for every column at that height — colour is a pure function of z.

For each product e_r·e_c, every doubling level L it spans (1 … max operand level)
gets a segment in level L's band, placed ABOVE the grid plane if σ_L = + and BELOW
if σ_L = −. So the per-level sign is read as up/down per band, while the colour
stays locked to the level. Position is the grid (center-out: 𝕆 on the rim); the
result unit is e_{r⊕c} (recoverable from position).

    blender --background --python scratch/figures/cayley_dickson_bl.py
    BL_MAXIMAL=1 ...   # only the top doubling's band (line-of-sight freed)
"""

import os
import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import numpy as np
import _blender as B

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)


def cd_mult(level, i, j):
    """e_i·e_j in the 2^level Cayley–Dickson algebra (binary basis). Returns
    (index, total_sign, sigma) where sigma[L] is the ± introduced at doubling L.
    Recursion: (a,b)(c,d) = (ac − d̄b, da + bc̄), conj(e_m)=−e_m for m≠0."""
    if level == 0:
        return 0, 1, {}
    half = 1 << (level - 1)
    iu, ju = i >= half, j >= half
    il, jl = (i - half if iu else i), (j - half if ju else j)
    if not iu and not ju:                       # both lower
        k, s, sig = cd_mult(level - 1, il, jl); sig[level] = 1; return k, s, sig
    if not iu and ju:                           # i lower, j upper → e_jl·e_il, upper
        k, s, sig = cd_mult(level - 1, jl, il); sig[level] = 1; return k + half, s, sig
    if iu and not ju:                           # i upper, j lower → e_il·conj(e_jl)
        cj = 1 if jl == 0 else -1
        k, s, sig = cd_mult(level - 1, il, jl); sig[level] = cj; return k + half, s * cj, sig
    cj = 1 if jl == 0 else -1                    # both upper → −conj(e_jl)·e_il, lower
    k, s, sig = cd_mult(level - 1, jl, il); sl = -cj; sig[level] = sl; return k, s * sl, sig


# One saturated Okabe-Ito hue per CD level — colour == level, full stop. The sign
# is geometry (above/below the grid plane), never colour, so a z-slice is one hue.
LEVEL_HUE = {1: "#0072B2", 2: "#009E73", 3: "#D55E00"}   # ℂ blue, ℍ green, 𝕆 orange

B.reset()
B.scene(samples=128)
VIEW = (0.8, -1.0, 0.7)   # camera direction (toward camera); also passed to the rig
MAXIMAL = bool(os.environ.get("BL_MAXIMAL"))   # show only the top doubling's band
level_mat = {L: B.material(c, rough=0.3, emission=1.8) for L, c in LEVEL_HUE.items()}

# Center-out layout: reorder each axis so the CD level forms a VALLEY (low centre,
# high ends), so the 𝕆 step rides the rim and the structure grows centre-out.
AXIS = [4, 5, 2, 0, 1, 3, 6, 7]   # unit at each axis slot (levels 3,3,2,0,1,2,3,3)
pos = [0] * 8
for slot, u in enumerate(AXIS):
    pos[u] = slot

for r in range(8):
    for c in range(8):
        h, s, sigma = cd_mult(3, r, c)
        if h <= 0:
            continue
        maxlev = max(int(r).bit_length(), int(c).bit_length())   # levels this product spans
        for L in range(1, maxlev + 1):
            if MAXIMAL and L != maxlev:
                continue
            side = 1 if sigma[L] > 0 else -1     # σ_L: + above the grid plane, − below
            B.box_cube((pos[c], pos[r], side * (L - 0.5)), (0.82, 0.82, 0.9),
                       level_mat[L])
data = B.join_data()
# Same gallery as octonion: forward a full cell off the back wall, 0.6 metal
# mirror, deep f/8 focus keeping the tiled-perspective reflections sharp.
B.driven_rig(data, direction=VIEW, align=(0, -2.0 / 3, 0),
             wall_rough=0.1, wall_metallic=0.6, fstop=8.0)
B.render("cayley_dickson_bl")
