#!/usr/bin/env python3
"""Klein bowl in the tenebrist museum box + an in-scene picture-in-picture.

The geometry is built ONCE (one set of facet polys in one scene) and presented
through TWO cameras: a wide museum-diorama view (driven_rig — black room, corner
+ edge spots firing through the diegetic box) and a second camera grazing a
front-exterior patch for a tight read on the gold-leaf faceting. `render_pip`
composites the closeup as a picture-in-picture entirely inside Blender's
compositor — a filtered Scale, so the inset stays anti-aliased (unlike a
nearest-neighbour numpy paste, which stair-steps the thin facet silhouettes).

    blender --background --python scratch/figures/klein_closeup_bl.py
"""

import math
import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import numpy as np
import mathutils
import bpy
import _blender as B

from _klein import generate_tiling
from _lift3d import disk_height

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

LIFT = disk_height(0.5)
tiles, seen = generate_tiling(8, 1400)
tiles = [t for t in tiles if max(math.hypot(*v) for v in t) <= 0.9]


def _key(t):                               # match _klein._key (centroid, 3 dp)
    cx = sum(v[0] for v in t) / 7; cy = sum(v[1] for v in t) / 7
    return (round(cx, 3), round(cy, 3))


# The bowl is 5 nested cycles (BFS rings of the 7-fold reflection). Colour each
# ring with an Okabe-Ito band, hot centre → cool rim, so the *nesting* that
# generates the structure is evident at a glance (depth = temperature).
RING = ["#D55E00", "#E69F00", "#F0E442", "#009E73", "#0072B2"]

# ── one scene, geometry built once ──────────────────────────────────────────
B.reset()
B.scene(samples=384)                       # dark museum → denoiser + more samples
for depth, col in enumerate(RING):
    grp = [LIFT(np.array(t)) for t in tiles if seen[_key(t)] == depth]
    if grp:
        # Interior (concave) faces glow faintly in the ring's own colour — a soft
        # inner light bouncing into the seams where facets diverge.
        B.polys(grp, B.material(col, rough=0.45, emission=0.05,
                                emission_backface=True), smooth=True)
data = B.join_data()

# View 1 — the full museum diorama (diegetic box, corner + edge spots, blackout).
main_cam = B.driven_rig(data, direction=(0.85, -0.8, 0.9), align=(0, 0, -1))

# View 2 — a second camera grazing a front-exterior patch of the SAME geometry.
cents = np.array([LIFT(np.array(t)).mean(axis=0) for t in tiles])
target = cents[int(np.argmin(cents[:, 1] + 0.25 * cents[:, 2]))]
eye = target + np.array([0.7, -0.45, 0.12])
icd = bpy.data.cameras.new("inset")
icd.lens = 70
icd.dof.use_dof = True
icd.dof.focus_distance = float(np.linalg.norm(eye - target))
icd.dof.aperture_fstop = 5.6               # mild DOF — the facets stay sharp
inset_cam = bpy.data.objects.new("inset_cam", icd)
bpy.context.collection.objects.link(inset_cam)
inset_cam.location = tuple(eye)
inset_cam.rotation_euler = (mathutils.Vector(tuple(target)) -
                            mathutils.Vector(tuple(eye))).to_track_quat("-Z", "Y").to_euler()

# Both views of the one in-memory scene, composited in Blender (filtered, AA-clean).
# The inset hole-punches the box walls (excluded from its view layer only), so the
# closeup sees straight through to the facets while the main keeps the diorama.
B.render_pip("klein_closeup", main_cam, inset_cam, frac=0.42,
             inset_hide=("DiegeticBox",))
