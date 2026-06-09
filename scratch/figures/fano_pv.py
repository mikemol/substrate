#!/usr/bin/env python3
"""The Fano plane inside its F₂³ cube — PyVista (real shadows), with a key.

Colour scheme (see the legend):
  blue spheres   — the 7 points = nonzero vectors of F₂³, labelled e1…e7
  grey sphere    — the origin 0
  teal triangles — the 7 Fano lines {a, b, a+b} (the 2-dim subspaces)
  orange tubes   — the Singer 7-cycle (order-7 automorphism of GL(3,F₂))
  pale tubes     — the 12 cube edges (the F₂³ scaffold)
"""

import numpy as np

from _fano import LINES, POINT_VEC, SINGER
from _pv import (add_labels, add_lights, diegetic_box, finish, frame_camera,
                 legend, make_parser, scene, title)

args = make_parser("fano_pv").parse_args()
import pyvista as pv

POINT_C, ORIGIN_C, LINE_C, SINGER_C, CUBE_C = (
    "#0072B2", "#999999", "#009E73", "#D55E00", "#cfcfcf")

V = {k: np.array(v, float) for k, v in POINT_VEC.items()}
pts = np.array(list(V.values()))
names = list(V.keys())  # e₁ … e₁₂₃

p = scene(args)
add_lights(p)
p.enable_depth_peeling(10)

# Cube scaffold: the 12 edges of F₂³.
corners = [np.array([x, y, z], float) for x in (0, 1) for y in (0, 1) for z in (0, 1)]
for a in corners:
    for b in corners:
        if abs(np.sum(np.abs(a - b)) - 1) < 1e-9 and tuple(a) < tuple(b):
            p.add_mesh(pv.Line(a, b).tube(radius=0.006), color=CUBE_C)

# The 7 Fano lines: translucent teal triangles with a bright edge, so each
# line's three corners visibly land on three spheres (not a wall smudge).
for tri in LINES.values():
    face = np.array([V[t] for t in tri])
    mesh = pv.PolyData(face, np.array([3, 0, 1, 2]))
    p.add_mesh(mesh, color=LINE_C, opacity=0.45, show_edges=True,
               edge_color="#00624b", line_width=5, ambient=0.45,
               smooth_shading=True)

# The 7 points (blue) and the origin (grey).
for name, v in V.items():
    p.add_mesh(pv.Sphere(radius=0.055, center=v), color=POINT_C,
               smooth_shading=True, specular=0.2)
p.add_mesh(pv.Sphere(radius=0.035, center=(0, 0, 0)), color=ORIGIN_C,
           smooth_shading=True)

# Singer 7-cycle as a threaded orange tube.
order = ["e₁"]
while len(order) < 7:
    order.append(SINGER[order[-1]])
for a, b in zip(order, order[1:] + order[:1]):
    p.add_mesh(pv.Line(V[a], V[b]).tube(radius=0.011), color=SINGER_C)

# Vertex labels showing the F₂³ bit pattern: position i shown if that basis
# vector is present, "-" if absent.  e(1,-,3) = basis 1 + basis 3 = (1,0,1).
def bitlabel(vec):
    return "e(" + ",".join(str(i + 1) if b else "-" for i, b in enumerate(vec)) + ")"

add_labels(p, list(V.values()) + [(0, 0, 0)],
           [bitlabel(POINT_VEC[n]) for n in names] + [bitlabel((0, 0, 0))])

# Floor only: with no back walls, the translucent Fano planes can't read as
# "behind the walls" — they float clearly in front, over their floor shadow.
diegetic_box(p, (0, 1, 0, 1, 0, 1), pad=0.3, floor_only=True)
legend(p, [("point e_i", POINT_C), ("origin 0", ORIGIN_C),
           ("Fano line", LINE_C), ("Singer 7-cycle", SINGER_C),
           ("cube edge", CUBE_C)])
title(p, "The Fano plane inside F2^3 - 7 points, 7 lines, Singer 7-cycle")
# transparency=True → skip SSAO/DOF so depth-peeling (OIT) composites the
# translucent Fano planes over the floor correctly.
finish(p, "fano_pv", args, transparency=True,
       camera=frame_camera(pts, direction=(1, -0.9, 0.6), dist_mult=4.4))
