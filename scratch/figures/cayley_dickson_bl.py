#!/usr/bin/env python3
"""Octonion table as a Cayley–Dickson tower — each pillar banded by the SIGN each
doubling contributes. Blender/Cycles.

The CD sign cocycle factorises: e_i·e_j = (∏_L σ_L) · e_{i⊕j}, where σ_L ∈ {±1}
is the sign introduced at doubling level L (ℂ, ℍ, 𝕆). So each product pillar is
split into three bands — ℂ at the base (z=0 grid plane), ℍ in the middle, 𝕆 at
the tip — and each band answers, for that range: *which CD level am I, and what
sign does that doubling contribute?* Colour = level (ℂ blue, ℍ green, 𝕆 orange),
shade = that level's sign (light = +, dark = −). The up/down of the whole pillar
is the product of the three, the overall sign.

Layout is center-out (axis reordered so the CD level forms a valley): the 𝕆 step
rides the rim, the structure grows centre-out. Height = which unit e_h (= i⊕j).

    blender --background --python scratch/figures/cayley_dickson_bl.py
    BL_MAXIMAL=1 ...   # show only the top doubling's band (line-of-sight freed)
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


def _mix(hexc, t, tgt):
    """Blend hexc a fraction t toward target rgb tgt (lighten/darken)."""
    rgb = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(v + (tv - v) * t) for v, tv in zip(rgb, tgt))


# ONE Okabe-Ito hue per CD level (colour == level); within a level a light shade
# (σ = +) and dark shade (σ = −) of that SAME hue (shade == the level's sign).
_BASE = {1: "#0072B2", 2: "#009E73", 3: "#D55E00"}   # ℂ blue, ℍ green, 𝕆 orange
CD_PAIRS = {L: (_mix(c, 0.3, (255, 255, 255)), _mix(c, 0.6, (0, 0, 0)))
            for L, c in _BASE.items()}   # σ=+ : saturated hue ; σ=− : deep/dark hue

B.reset()
B.scene(samples=128)
VIEW = (0.8, -1.0, 0.7)   # camera direction (toward camera); also passed to the rig
MAXIMAL = bool(os.environ.get("BL_MAXIMAL"))   # show only the top doubling's band
# One material per CD-pair tone (6); uniform emission so each band glows its hue
# toward the camera — this is a colour-coded figure, colour must read.
tone_mat = {}
for c0, c1 in CD_PAIRS.values():
    for col in (c0, c1):
        tone_mat.setdefault(col, B.material(col, rough=0.3, emission=1.2))

# Center-out layout: reorder each axis so the CD level forms a VALLEY (low centre,
# high ends), so the 𝕆 step rides the rim and the structure grows centre-out.
AXIS = [4, 5, 2, 0, 1, 3, 6, 7]   # unit at each axis slot (levels 3,3,2,0,1,2,3,3)
pos = [0] * 8
for slot, u in enumerate(AXIS):
    pos[u] = slot

centers = []
for r in range(8):
    for c in range(8):
        h, s, sigma = cd_mult(3, r, c)
        if h <= 0:
            continue
        # Three bands = the per-level sign cocycle: ℂ(σ1) at the base → ℍ(σ2) →
        # 𝕆(σ3) at the tip. Colour = level, shade = that level's sign; the pillar
        # rises (+) or descends (−) by the product s = σ1·σ2·σ3.
        sgn = 1 if s >= 0 else -1
        hb = h / 3.0
        top = max(int(r).bit_length(), int(c).bit_length()) - 1   # max level involved
        for k in range(3):
            if MAXIMAL and k != top:
                continue
            col = CD_PAIRS[k + 1][0 if sigma[k + 1] > 0 else 1]
            B.box_cube((pos[c], pos[r], sgn * (k + 0.5) * hb), (0.82, 0.82, hb),
                       tone_mat[col])
        centers.append((pos[c], pos[r], sgn * h))
data = B.join_data()
# Same gallery as octonion: forward a full cell off the back wall, 0.6 metal
# mirror, deep f/8 focus keeping the tiled-perspective reflections sharp.
B.driven_rig(data, direction=VIEW, align=(0, -2.0 / 3, 0),
             wall_rough=0.1, wall_metallic=0.6, fstop=8.0)
B.render("cayley_dickson_bl")
