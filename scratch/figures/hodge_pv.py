#!/usr/bin/env python3
"""Hodge dual-grade ★ as a vertical fold tower — PyVista.

Four grade rings (z = grade) with face counts 4,6,4,1; ★ pairs them 0↔3 and
1↔2 (Okabe-Ito orange / blue), drawn as bowed tubes folding across the central
axis. Seated low (a tower opening upward), real shadows in the diegetic box.
"""

import math

import numpy as np

from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, title)

args = make_parser("hodge_pv").parse_args()
import pyvista as pv

COUNTS = [4, 6, 4, 1]
PAIR_COLOR = {0: "#D55E00", 3: "#D55E00", 1: "#0072B2", 2: "#0072B2"}
GAP = 1.3

p = scene(args)
add_lights(p)

allpts = []
for k in range(4):
    z = k * GAP
    n = COUNTS[k]
    radius = 0.7 + 0.16 * n
    for j in range(n):
        ang = 2 * math.pi * j / n + (math.pi / 4 if k in (1, 2) else 0)
        c = (radius * math.cos(ang), radius * math.sin(ang), z)
        allpts.append(c)
        p.add_mesh(pv.Sphere(radius=0.16, center=c), color=PAIR_COLOR[k],
                   smooth_shading=True, specular=0.3)

p.add_mesh(pv.Line((0, 0, 0), (0, 0, 3 * GAP)).tube(radius=0.05), color="#cccccc")

# ★ fold arcs: bowed tubes from grade a to grade b.
for a, b, col in ((0, 3, "#D55E00"), (1, 2, "#0072B2")):
    t = np.linspace(0, 1, 40)
    bow = 1.7 * np.sin(math.pi * t)
    pts = np.column_stack([bow, np.zeros_like(t), (a + (b - a) * t) * GAP])
    p.add_mesh(pv.Spline(pts, 80).tube(radius=0.04), color=col)

allpts = np.array(allpts)
b = (-2, 2, -2, 2, 0, 3 * GAP)
diegetic_box(p, b, pad=0.12)
title(p, "Hodge dual-grade * as a vertical fold (0<->3, 1<->2)\n"
         "Lambda^0..Lambda^3 over the 3-simplex")
finish(p, "hodge_pv", args,
       camera=frame_camera(allpts, direction=(1, -0.8, 0.45), dist_mult=3.8),
       thirds=(0.22, 0.4))
