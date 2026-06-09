#!/usr/bin/env python3
"""Klein quartic {7,3} hyperbolic tower — PyVista (real self-shadowing).

Same tiling (_klein) and LiftMap (_lift3d.disk_height / hyperboloid) as
klein_quartic_3d.py, rendered in VTK as one heptagon mesh: a solid Okabe-Ito
colour with white tile edges, lit so the bowl casts real shadows onto itself
and the diegetic box. Form is read from shadow and occlusion, not colour.

  --model funnel|hyperboloid   --invert
"""

import math

import numpy as np

from _klein import P, generate_tiling
from _lift3d import disk_height, hyperboloid
from _pv import add_lights, diegetic_box, finish, frame_camera, make_parser, scene, title

parser = make_parser("klein_pv")
parser.add_argument("--depth", type=int, default=8)
parser.add_argument("--max-tiles", type=int, default=1400)
parser.add_argument("--model", choices=["funnel", "hyperboloid"], default="funnel")
parser.add_argument("--invert", action="store_true")
parser.add_argument("--r-max", type=float, default=0.9)
parser.add_argument("--color", default="#E69F00", help="Okabe-Ito tile colour.")
args = parser.parse_args()

import pyvista as pv

LIFT = disk_height(0.5) if args.model == "funnel" else hyperboloid()
tiles, _ = generate_tiling(args.depth, args.max_tiles)
tiles = [t for t in tiles if max(math.hypot(*v) for v in t) <= args.r_max]
polys = [LIFT(np.array(t)) for t in tiles]
if args.invert:
    for poly in polys:
        poly[:, 2] = -poly[:, 2]

verts = np.vstack(polys)
faces = np.hstack([[P, *range(i * P, i * P + P)] for i in range(len(polys))])
mesh = pv.PolyData(verts, faces)

p = scene(args)
add_lights(p)
p.add_mesh(mesh, color=args.color, show_edges=False, smooth_shading=False,
           specular=0.2, specular_power=10, ambient=0.28, diffuse=0.85)

allz = verts[:, 2]
b = np.array([verts[:, 0].min(), verts[:, 0].max(),
              verts[:, 1].min(), verts[:, 1].max(), allz.min(), allz.max()])
diegetic_box(p, b, pad=0.16)

variant = {"funnel": "funnel", "hyperboloid": "flower (Minkowski)"}[args.model]
if args.invert:
    variant += ", inverted"
title(p, f"Klein quartic {{7,3}} - hyperbolic {variant} - {len(tiles)} heptagons\n"
         "(PyVista: real self-shadowing + SSAO + haze)")

direction = (0.85, -0.8, 0.95 if not args.invert else -0.95)
name = ("klein_pv_flower" if args.model == "hyperboloid"
        else ("klein_pv_inverted" if args.invert else "klein_pv"))
# Bowl opens upward → seat the body in the lower two-thirds (headroom above).
vbias = 0.45 if not args.invert else -0.1
finish(p, name, args, camera=frame_camera(verts, direction=direction, dist_mult=4.0),
       thirds=(0.22, vbias))
