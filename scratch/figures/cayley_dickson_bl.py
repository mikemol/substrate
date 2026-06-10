#!/usr/bin/env python3
"""Octonion table as a Cayley–Dickson tower — z IS the CD level. Blender/Cycles.

The CD sign cocycle factorises: e_i·e_j = (∏_L σ_L)·e_{i⊕j}, with σ_L ∈ {±1} the
sign introduced at doubling level L. Here the VERTICAL axis is the level itself, and each band's HEIGHT doubles with
the CD dimension (ℂ 1, ℍ 2, 𝕆 4): ℂ occupies |z|∈[0,1], ℍ |z|∈[1,3], 𝕆 |z|∈[3,7],
each a single hue (ℂ blue, ℍ green, 𝕆 orange). So a horizontal z=n slice is ONE
level = ONE colour for every column at that height — colour is a pure function of
z — and the dimension-doubling is legible as the band heights.

Each product is a column of height h = |result index| (e_{r⊕c}), rising (+) or
descending (−) by the product's overall sign, coloured by the level bands it
passes through — so it tops out in its OWN level's band (h=1 → ℂ, h∈[2,3] → ℍ,
h∈[4,7] → 𝕆). Column heights vary 1…7 (the result magnitude, as in octonion_bl),
z-slices stay one colour, and the band boundaries 1,3,7 are the doublings.
Position is the grid (center-out: 𝕆 on the rim).

    blender --background --python scratch/figures/cayley_dickson_bl.py
"""

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
# Per band: the camera-aware away-gate masked to ONE axis chosen by the per-level
# sign — emission &= (my-normal-axis == sign-axis). σ_L=+ glows from the back (+Y)
# away-face, σ_L=− from the left (−X). The away-gate keeps it off the lens; no
# camera change needed.
SIGN_AXIS = {1: (0, 1, 0), -1: (1, 0, 0)}   # +: +Y back  ;  −: −X left
level_mat = {(L, sd): B.material(c, rough=0.3, emission=5.0,
                                 emission_away=VIEW, emission_axis=SIGN_AXIS[sd])
             for L, c in LEVEL_HUE.items() for sd in (1, -1)}

# Center-out layout: reorder each axis so the CD level forms a VALLEY (low centre,
# high ends), so the 𝕆 step rides the rim and the structure grows centre-out.
AXIS = [4, 5, 2, 0, 1, 3, 6, 7]   # unit at each axis slot (levels 3,3,2,0,1,2,3,3)
pos = [0] * 8
for slot, u in enumerate(AXIS):
    pos[u] = slot

BOUND = [0, 1, 3, 7]   # level z-boundaries = max result index per level; heights 1,2,4
for r in range(8):
    for c in range(8):
        h, s, sigma = cd_mult(3, r, c)
        if h <= 0:
            continue
        updown = 1 if s >= 0 else -1             # overall product sign: up (+) / down (−)
        # Show ONLY the top doubling of each bar — the segment in the unit's own
        # level band (L = h.bit_length(), z = [BOUND[L-1], h]) — so each column is
        # just its top-level cap, clearing the lower bands' occlusion.
        L = h.bit_length()
        z0, z1 = BOUND[L - 1], h
        sd = 1 if sigma[L] > 0 else -1            # per-level sign σ_L → which side glows
        B.box_cube((pos[c], pos[r], updown * (z0 + z1) / 2.0),
                   (0.82, 0.82, z1 - z0), level_mat[(L, sd)])
data = B.join_data()
# Same gallery as octonion: forward a full cell off the back wall, 0.6 metal
# mirror, deep f/8 focus keeping the tiled-perspective reflections sharp.
B.driven_rig(data, direction=VIEW, align=(0, -2.0 / 3, 0),
             wall_rough=0.1, wall_metallic=0.6, fstop=8.0)
B.render("cayley_dickson_bl")
