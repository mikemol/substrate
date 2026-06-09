#!/usr/bin/env python3
"""Klein bowl + a picture-in-picture oblique closeup of the gold-leaf facets.

Renders the main view, then a tight grazing camera on a front-exterior patch,
and composites the closeup as a PIP inset — to see whether the facet detail
persists at an oblique angle.

    blender --background --python scratch/figures/klein_closeup.py
"""

import math
import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(_H), str(_H.parents[1] / ".venv/lib/python3.14/site-packages")]

import numpy as np
import mathutils
import bpy
import _blender as B
from _klein import generate_tiling
from _lift3d import disk_height

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

LIFT = disk_height(0.5)
tiles, _ = generate_tiling(8, 1400)
tiles = [t for t in tiles if max(math.hypot(*v) for v in t) <= 0.9]
polys = [LIFT(np.array(t)) for t in tiles]

B.reset()
B.scene(samples=240)
B.lights(key=(5, -5, 9), key_size=9)
B.polys(polys, B.material("#E69F00", rough=0.45), smooth=True)
data = B.join_data()

# --- main view ---
B.driven_rig(data, direction=(0.85, -0.8, 0.9), align=(0, 0, -1))
B.render("klein_main_tmp")

# --- oblique grazing closeup on a front-exterior patch ---
cents = np.array([p.mean(axis=0) for p in polys])
i = int(np.argmin(cents[:, 1] + 0.25 * cents[:, 2]))     # front, lower exterior
target = cents[i]
eye = target + np.array([0.7, -0.45, 0.12])              # to the side, grazing
cam = bpy.context.scene.camera
cam.location = tuple(eye)
cam.rotation_euler = (mathutils.Vector(tuple(target)) -
                      mathutils.Vector(tuple(eye))).to_track_quat("-Z", "Y").to_euler()
cam.data.lens = 70
cam.data.dof.focus_distance = float(np.linalg.norm(eye - target))
cam.data.dof.aperture_fstop = 2.8
B.render("klein_zoom_tmp")

# --- composite the PIP ---
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

main = mpimg.imread(str(B.OUT / "klein_main_tmp.png"))
zoom = mpimg.imread(str(B.OUT / "klein_zoom_tmp.png"))
h, w = main.shape[:2]
fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(main); ax.set_axis_off()
iw = 0.44
iax = fig.add_axes([1 - iw - 0.025, 0.025, iw, iw])
iax.imshow(zoom); iax.set_xticks([]); iax.set_yticks([])
for s in iax.spines.values():
    s.set_edgecolor("#333333"); s.set_linewidth(2.5)
iax.set_title("oblique grazing closeup", fontsize=9, color="#333333", pad=3)
out = B.OUT / "klein_closeup.png"
fig.savefig(str(out), dpi=100); plt.close(fig)
print(f"BL_WROTE {out}")
