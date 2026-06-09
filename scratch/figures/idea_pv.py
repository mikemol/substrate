#!/usr/bin/env python3
"""The idea lattice as a cocycle tower — PyVista.

Nine levels stacked as rings (z = level); concepts as spheres coloured by tag
(invariant blue, gauge/cocycle orange, framing grey); a central spine. The
tower opens upward, so it's seated in the lower two-thirds, casting a real
shadow into the diegetic box. Parsing shared via _catalog.
"""

import math

import numpy as np

from _catalog import parse_levels
from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, title, tubes)

args = make_parser("idea_pv").parse_args()
import pyvista as pv

GAP = 1.6
COLOR = {"invariant": "#0072B2", "gauge": "#D55E00", "other": "#999999"}
levels = parse_levels()

p = scene(args)
add_lights(p)

allpts = []
for lvl, title_, concepts in levels:
    z = lvl * GAP
    n = len(concepts)
    radius = 1.0 + 0.16 * n
    for k, (name, cls) in enumerate(concepts):
        ang = 2 * math.pi * k / max(n, 1)
        c = (radius * math.cos(ang), radius * math.sin(ang), z)
        allpts.append(c)
        p.add_mesh(pv.Sphere(radius=0.28, center=c), color=COLOR[cls],
                   smooth_shading=True, specular=0.3)
# Central spine.
zmax = (len(levels) - 1) * GAP
p.add_mesh(pv.Line((0, 0, 0), (0, 0, zmax)).tube(radius=0.12), color="#cccccc")

allpts = np.array(allpts)
b = (allpts[:, 0].min(), allpts[:, 0].max(), allpts[:, 1].min(),
     allpts[:, 1].max(), 0, zmax)
diegetic_box(p, b, pad=0.12)
title(p, "The idea lattice as a cocycle tower (nine levels)\n"
         "invariant (blue) / gauge cocycle (orange) / framing (grey)")
finish(p, "idea_pv", args,
       camera=frame_camera(allpts, direction=(1, -0.85, 0.5), dist_mult=3.6),
       thirds=(0.22, 0.42))
