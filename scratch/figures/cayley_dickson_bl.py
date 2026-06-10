#!/usr/bin/env python3
"""Octonion table as a Cayley–Dickson tower — each pillar a barcode of its
construction. Blender/Cycles.

𝕆 = ℍ⊕ℍ, ℍ = ℂ⊕ℂ, ℂ = ℝ⊕ℝ — the doubling nests three deep. In the binary basis
(idx = i XOR j) a unit's address is its 3 bits: bit 0 = which ℝ-in-ℂ, bit 1 =
which ℂ-in-ℍ, bit 2 = which ℍ-in-𝕆. So each product pillar is split into THREE
stacked bands — ℂ at the base (the z=0 grid plane), ℍ in the middle, 𝕆 at the tip
— and within each band the tone (light/dark of that level's palette pair) says
which half of that doubling the unit lies in. Read a pillar base→tip and you read
its construction ℝ→ℂ→ℍ→𝕆.

Layout is center-out: the axis is reordered so the CD level forms a valley (low at
the centre), so the 𝕆 step rides the rim and the structure grows centre-out.
Height = which unit e_h (the result), sign = up (+) / down (−) about the grid
plane, in the same backlit 0.6-mirror gallery as octonion_bl.

    blender --background --python scratch/figures/cayley_dickson_bl.py
"""

import os
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

def _mix(hexc, t, tgt):
    """Blend hexc a fraction t toward target rgb tgt (lighten/darken)."""
    rgb = [int(hexc[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(v + (tv - v) * t) for v, tv in zip(rgb, tgt))


# ONE Okabe-Ito hue per CD level, so colour == level. The two halves (bit) are a
# light shade (bit 0) and a dark shade (bit 1) of that SAME hue — shade == which
# half — instead of two different hues that don't read as one level.
_BASE = {1: "#0072B2", 2: "#009E73", 3: "#D55E00"}   # ℂ blue, ℍ green, 𝕆 orange
CD_PAIRS = {L: (_mix(c, 0.55, (255, 255, 255)), _mix(c, 0.4, (0, 0, 0)))
            for L, c in _BASE.items()}

B.reset()
B.scene(samples=128)
VIEW = (0.8, -1.0, 0.7)   # camera direction (toward camera); also passed to the rig
MAXIMAL = bool(os.environ.get("BL_MAXIMAL"))   # show only each unit's top band
# One material per CD-pair tone (6), each with the away-face backlight (6.5).
tone_mat = {}
for c0, c1 in CD_PAIRS.values():
    for col in (c0, c1):
        tone_mat.setdefault(col, B.material(col, rough=0.15, emission=6.5,
                                            emission_away=VIEW))

# Center-out layout: reorder each axis so the CD level forms a VALLEY — lowest at
# the centre, highest at the ends — so the 𝕆 step rides the rim and the structure
# grows centre-out, not corner-to-corner.
AXIS = [4, 5, 2, 0, 1, 3, 6, 7]   # unit at each axis slot (levels 3,3,2,0,1,2,3,3)
pos = [0] * 8
for slot, u in enumerate(AXIS):
    pos[u] = slot

centers = []
for r in range(8):
    for c in range(8):
        h = int(idx[r, c])
        if h <= 0:
            continue
        s = 1 if sign[r, c] >= 0 else -1
        # Three stacked bands = the result unit's CD address: ℂ(bit0) at the base
        # (grid plane) → ℍ(bit1) → 𝕆(bit2) at the tip; tone = which half.
        # BL_MAXIMAL: show only the unit's TOP band (its highest set bit) — what
        # the maximal doubling ADDS — floating at its level's height, so the lower
        # levels go empty and line-of-sight opens up through them.
        hb = h / 3.0
        top = h.bit_length() - 1
        for k in range(3):
            if MAXIMAL and k != top:
                continue
            col = CD_PAIRS[k + 1][(h >> k) & 1]
            B.box_cube((pos[c], pos[r], s * (k + 0.5) * hb), (0.82, 0.82, hb),
                       tone_mat[col])
        centers.append((pos[c], pos[r], s * h))
data = B.join_data()
# Same gallery as octonion: forward a full cell off the back wall, 0.6 metal
# mirror, deep f/8 focus keeping the tiled-perspective reflections sharp.
B.driven_rig(data, direction=VIEW, align=(0, -2.0 / 3, 0),
             wall_rough=0.1, wall_metallic=0.6, fstop=8.0)
B.render("cayley_dickson_bl")
