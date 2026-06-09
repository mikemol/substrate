#!/usr/bin/env python3
"""S₄ permutohedron harmonics as a rectified standing-wave surface — PyVista.

height = |amplitude| (floor flush at 0), colour = signed phase (diverging), over
the 24 chambers × low harmonics. Real shadows in the diegetic box. _perm core.
"""

import numpy as np

from _perm import Permutohedron
from _pv import (add_lights, diegetic_box, finish, frame_camera, make_parser,
                 scene, surface, title)

parser = make_parser("spectrum_pv")
parser.add_argument("--modes", type=int, default=8)
args = parser.parse_args()
import pyvista as pv

P = Permutohedron()
order = sorted(P.nodes_list, key=lambda q: (P.dist[q], q))
rows = [P.index(q) for q in order]
M = P.eigenvectors[np.ix_(rows, np.arange(args.modes))].T  # modes × chambers
absM = np.abs(M)
a = float(np.abs(M).max())

xs = np.linspace(0, 8, M.shape[1])
ys = np.linspace(0, 3, M.shape[0])

p = scene(args)
add_lights(p)
surface(p, absM, cmap="coolwarm", scalars=M, clim=(-a, a), x=xs, y=ys)

# A flat carpet wants a floor, not tall walls.
diegetic_box(p, (0, 8, 0, 3, 0, absM.max()), pad=0.12, floor_only=True)
title(p, "S4 permutohedron harmonics - height = |amplitude| (floor at 0)\n"
         "colour = sign; chambers x low harmonics")
finish(p, "spectrum_pv", args,
       camera=frame_camera(np.array([[0, 0, 0], [8, 3, absM.max()]]),
                           direction=(0.45, -0.85, 0.95), dist_mult=2.6),
       thirds=(0.2, 0.18))
