#!/usr/bin/env python3
"""Octonion Cayley table as a 3D relief — PyVista.

Bars rise from the z=0 floor; height = product index e_k, colour = sign of the
product (Okabe-Ito orange +, blue −). Real shadows into the diegetic box.
Table from _fano.octonion_table.
"""

import numpy as np

from _fano import octonion_table
from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, title)

args = make_parser("octonion_pv").parse_args()
import pyvista as pv

sign, idx = octonion_table()
POS, NEG = "#E69F00", "#0072B2"

p = scene(args)
add_lights(p)

centers = []
for r in range(8):
    for c in range(8):
        h = float(idx[r, c])
        if h <= 0:
            continue
        cube = pv.Cube(center=(c, r, h / 2), x_length=0.82, y_length=0.82, z_length=h)
        p.add_mesh(cube, color=(POS if sign[r, c] >= 0 else NEG),
                   smooth_shading=False, specular=0.2, ambient=0.3)
        centers.append((c, r, h))

centers = np.array(centers)
diegetic_box(p, (0, 7, 0, 7, 0, 7), pad=0.14)
title(p, "Octonion Cayley table relief - height = product index e_k\n"
         "colour = sign (orange +, blue -); floor flush at 0")
finish(p, "octonion_pv", args,
       camera=frame_camera(np.vstack([centers, [[3.5, 3.5, 0]]]),
                           direction=(0.8, -1.0, 0.7), dist_mult=3.2),
       thirds=(0.2, 0.28))
