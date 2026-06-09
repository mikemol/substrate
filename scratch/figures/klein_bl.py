#!/usr/bin/env python3
"""Klein quartic {7,3} hyperbolic tower — Blender/Cycles.

blender --background --python scratch/figures/klein_bl.py
"""

import math
import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(_H), str(_H.parents[1] / ".venv/lib/python3.14/site-packages")]

import numpy as np
import _blender as B
from _klein import P, generate_tiling
from _lift3d import disk_height

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

LIFT = disk_height(0.5)
tiles, _ = generate_tiling(8, 1400)
tiles = [t for t in tiles if max(math.hypot(*v) for v in t) <= 0.9]
polys = [LIFT(np.array(t)) for t in tiles]
verts = np.vstack(polys)

B.reset()
B.scene(samples=128)
B.lights(key=(5, -5, 9), key_size=9)
B.polys(polys, B.material("#E69F00", rough=0.45), smooth=True)

b = (verts[:, 0].min(), verts[:, 0].max(), verts[:, 1].min(), verts[:, 1].max(),
     verts[:, 2].min(), verts[:, 2].max())
B.diegetic_box(b, pad=0.18)
B.frame(verts, direction=(0.85, -0.8, 0.9), dist_mult=2.9, shift=(0.05, 0.16))
B.render("klein_bl")
