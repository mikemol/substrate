#!/usr/bin/env python3
"""The {7,3} tiling lifted into 3D — funnel, flower, or inverted.

Three LiftMap gauges, all over the same tiling geometry (_klein):

  --model funnel       z = hyperbolic distance ρ  (clean wedding-cake tower)
  --model hyperboloid  z = cosh ρ (Minkowski model) — outer tiles bloom into a
                       flower as cosh explodes near the ideal boundary
  --invert             negate z so the centre is the peak and the rim hangs
                       below (an inverted funnel / vortex)

Tiles are directionally lit by face normal (_lift3d.light_polys) and cast a soft
shadow on the floor, so the surface reads as solid relief rather than a flat
wireframe. Geometry shared with klein_quartic_tiling.py.
"""

import math

from _gallery import finish, make_parser, set_style
from _klein import P, generate_tiling
from _lift3d import disk_height, diegetic_box, hyperboloid, light_polys

parser = make_parser("klein_quartic_3d")
parser.add_argument("--depth", type=int, default=8)
parser.add_argument("--max-tiles", type=int, default=1400)
parser.add_argument("--model", choices=["funnel", "hyperboloid"], default="funnel")
parser.add_argument("--invert", action="store_true",
                    help="Flip z so the base is the peak (inverted funnel).")
parser.add_argument("--r-max", type=float, default=0.9)
args = parser.parse_args()
set_style()

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

LIFT = disk_height() if args.model == "funnel" else hyperboloid()
tiles, _ = generate_tiling(args.depth, args.max_tiles)
tiles = [t for t in tiles if max(math.hypot(*v) for v in t) <= args.r_max]

polys = [LIFT(np.array(tile)) for tile in tiles]
if args.invert:
    for p in polys:
        p[:, 2] = -p[:, 2]

zvals = np.array([p[:, 2].mean() for p in polys])
zlo, zhi = zvals.min(), zvals.max()
cmap = mpl.colormaps["twilight"]
base = [cmap(0.12 + 0.8 * (z - zlo) / (zhi - zlo + 1e-9)) for z in zvals]
# Directional lighting: flat tiles become a lit relief.
lit = light_polys(polys, base, light=(0.35, 0.2, 0.9), ambient=0.45)

fig = plt.figure(figsize=(11, 10))
ax = fig.add_subplot(111, projection="3d")
ax.add_collection3d(Poly3DCollection(polys, facecolors=lit, edgecolors="white",
                                     linewidths=0.4, alpha=0.97))

xy = np.vstack(polys)[:, :2]
span = np.abs(xy).max()
allz = np.vstack(polys)[:, 2]
ax.set_xlim(-span, span); ax.set_ylim(-span, span)
ax.set_zlim(allz.min() - 0.15, allz.max() + 0.15)
ax.set_box_aspect((1, 1, 0.75))
ax.set_axis_off()

# Diegetic box: the tiling sits inside a lit room and casts heptagon shadows
# onto its floor and walls.
diegetic_box(ax, shadow_polys=polys, shadow_alpha=0.05, wall_alpha=0.8)
ax.view_init(elev=34 if not args.invert else -28, azim=30)

variant = ("flower (Minkowski hyperboloid, z = cosh ρ)" if args.model == "hyperboloid"
           else ("inverted funnel" if args.invert else "funnel"))
name = ("klein_quartic_flower" if args.model == "hyperboloid"
        else ("klein_quartic_inverted" if args.invert else "klein_quartic_3d"))
ax.set_title(f"Klein quartic {{7,3}} — {variant} — {len(tiles)} heptagons\n"
             f"LiftMap: {LIFT.label}", pad=4)

finish(fig, name, args)
