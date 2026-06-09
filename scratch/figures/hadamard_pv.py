#!/usr/bin/env python3
"""Walsh–Hadamard terraced landscape — PyVista (real shadows on the steppes).

height h(k,x) = Σᵢ 2⁻ⁱ·(−1)^(kᵢxᵢ): a self-similar terraced surface (the
recursion grade carves the steppes). Lit so the terraces cast real shadows.
"""

import numpy as np

from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, surface, title)

parser = make_parser("hadamard_pv")
parser.add_argument("--n", type=int, default=5)
args = parser.parse_args()
import pyvista as pv


def terraced_walsh(n):
    N = 2 ** n
    H = np.zeros((N, N))
    for k in range(N):
        for x in range(N):
            h = 0.0
            for i in range(n):
                ki = (k >> (n - 1 - i)) & 1
                xi = (x >> (n - 1 - i)) & 1
                h += (2.0 ** (-i)) * (-1 if (ki & xi) else 1)
            H[k, x] = h
    return H


H = terraced_walsh(args.n)
N = 2 ** args.n
# Scale x/y to a sensible footprint vs height (range ~[-2,2]).
xs = np.linspace(0, 6, N)
ys = np.linspace(0, 6, N)

p = scene(args)
add_lights(p)
surface(p, H, cmap="twilight_shifted", x=xs, y=ys)

allpts = np.array([[0, 0, H.min()], [6, 6, H.max()]])
diegetic_box(p, (0, 6, 0, 6, H.min(), H.max()), pad=0.12, floor_only=True)
title(p, f"Walsh-Hadamard terraces, level n = {args.n}  ({N}x{N})\n"
         "height = sum 2^-i (-1)^(ki xi) - recursion grade -> steppes")
finish(p, "hadamard_pv", args,
       camera=frame_camera(allpts, direction=(0.55, -0.7, 1.05), dist_mult=2.9),
       thirds=(0.2, 0.18))
