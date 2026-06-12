#!/usr/bin/env python3
"""Diagnostic: glyphs CONFORMED to the capsule surface (folded over the endcaps),
extruded along the local surface normal — not cut by a flat slab. A TALL capsule
and a SHORT (band-1-like) capsule, each TRUE/FALSE/UNSET spread, to confirm the
pips engrave on body AND cap.

    blender --background --python scratch/figures/_glyph_test.py
"""

import math
import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import mathutils
import bpy
import bmesh
import _blender as B

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)
B.reset()
B.scene(samples=128)
VIEW = (0.0, -1.0, 0.25)
body = B.material("#D55E00", rough=0.3, emission=6.0, emission_away=VIEW)
glow = B.material("#ffffff", emission=60.0)


def glyph_shapes(state, r):
    """2D glyph in (u,v): u horizontal (→ arc around), v vertical (→ meridian).
    Filled disc at A (true) / B (false); unset → nothing. Stroke radius rs = r/2."""
    e = 3.0 * r
    A = mathutils.Vector((-0.5 * e, 0.8660254 * e))
    Bp = mathutils.Vector((0.5 * e, 0.8660254 * e))
    C = mathutils.Vector((0.0, 0.0))
    D = C + e * (C - A).normalized()
    rs = 0.5 * r
    shapes = []
    a0 = math.atan2((D - C).y, (D - C).x)
    sg, tail = 8, []
    for k in range(sg + 1):
        a = a0 - math.pi / 2 + math.pi * k / sg
        tail.append((D.x + rs * math.cos(a), D.y + rs * math.sin(a)))
    for k in range(sg + 1):
        a = a0 + math.pi / 2 + math.pi * k / sg
        tail.append((C.x + rs * math.cos(a), C.y + rs * math.sin(a)))
    shapes.append(tail)

    def disc(c):
        return [(c.x + rs * math.cos(2 * math.pi * k / 14),
                 c.y + rs * math.sin(2 * math.pi * k / 14)) for k in range(14)]
    for pt, is_set in ((A, state == 1), (Bp, state == 0)):
        if is_set:
            shapes.append(disc(pt))
    return shapes


def inscribe(cap, bits, x, y, rad, z0, z1, updown, face, depth=0.05):
    n = mathutils.Vector((face[0], face[1], 0.0)).normalized()
    nperp = mathutils.Vector((-n.y, n.x, 0.0))
    r = rad * math.radians(22.5) / 2.0           # pip edge at ±22.5° arc ⇒ 45° glyph
    z_lo, z_hi = min(updown * z0, updown * z1), max(updown * z0, updown * z1)
    cyl_lo, cyl_hi = z_lo + rad, z_hi - rad
    qc = rad * math.pi / 2.0
    bodyL = cyl_hi - cyl_lo
    S = 2 * qc + bodyL                           # pole-to-pole meridian arc length

    def meridian(s):                             # arc s from bottom pole → (z, ring_r, n_rad, n_z)
        s = min(max(s, 0.0), S)
        if s < qc:
            al = s / rad
            return (cyl_lo - rad * math.cos(al), rad * math.sin(al), math.sin(al), -math.cos(al))
        if s < qc + bodyL:
            return (cyl_lo + (s - qc), rad, 1.0, 0.0)
        be = (s - qc - bodyL) / rad
        return (cyl_hi + rad * math.sin(be), rad * math.cos(be), math.cos(be), math.sin(be))

    def surf(u, v, s_c):                         # glyph (u,v) → (surface point, normal)
        z, rr, nr, nz = meridian(s_c + v)
        ang = u / rr if rr > 0.06 else 0.0
        rdir = math.cos(ang) * n + math.sin(ang) * nperp
        pt = mathutils.Vector((x + rr * rdir.x, y + rr * rdir.y, z))
        nrm = nr * rdir + mathutils.Vector((0.0, 0.0, nz))
        return pt, nrm

    def cut_one(state, s_c):                     # carve ONE glyph (own boolean → no
        verts, faces = [], []                    # cross-glyph cutter self-intersection)
        for pts in glyph_shapes(state, r):
            k = len(pts); st = len(verts)
            dat = [surf(updown * u, updown * v, s_c) for (u, v) in pts]
            for (pt, nrm) in dat:
                verts.append(tuple(pt + depth * nrm))
            for (pt, nrm) in dat:
                verts.append(tuple(pt - depth * nrm))
            faces.append(list(range(st, st + k)))
            faces.append(list(range(st + 2 * k - 1, st + k - 1, -1)))
            for i in range(k):
                j = (i + 1) % k
                faces.append([st + i, st + j, st + k + j, st + k + i])
        if not faces:
            return
        me = bpy.data.meshes.new("cut"); me.from_pydata(verts, [], faces); me.update()
        bm0 = bmesh.new(); bm0.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm0, faces=bm0.faces)
        bm0.to_mesh(me); bm0.free()
        cutter = bpy.data.objects.new("cut", me)
        bpy.context.scene.collection.objects.link(cutter)
        m = cap.modifiers.new("inscribe", "BOOLEAN")
        m.operation = "DIFFERENCE"; m.object = cutter; m.solver = "EXACT"
        bpy.context.view_layer.objects.active = cap
        bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.data.objects.remove(cutter)

    gh = 2.6 * r + 0.5 * r + 0.07                # glyph reach + clearance
    s_lo, s_hi = 0.5 * qc + gh, S - 0.5 * qc - gh  # stay below the caps' 45th parallel
    if s_hi <= s_lo:                             # capsule too short → centre all three
        s_lo = s_hi = 0.5 * S
    order = (s_hi, 0.5 * (s_lo + s_hi), s_lo) if updown > 0 \
        else (s_lo, 0.5 * (s_lo + s_hi), s_hi)  # b2 far tip → b0 near grid
    for gi, state in enumerate(bits):
        cut_one(state, order[gi])
    cme = cap.data
    if glow.name not in cme.materials:
        cme.materials.append(glow)
    gi2 = cme.materials.find(glow.name)
    bm = bmesh.new(); bm.from_mesh(cme); bm.normal_update()
    for f in bm.faces:                           # recessed floor via capsule SDF
        p = f.calc_center_median()
        cz = min(max(p.z, cyl_lo), cyl_hi)
        d = mathutils.Vector((p.x - x, p.y - y, p.z - cz)); dl = d.length
        if dl < 1e-6:
            continue
        if dl - rad < -0.4 * depth and f.normal.dot(d / dl) > 0.5:
            f.material_index = gi2
    bm.to_mesh(cme); bm.free()


# Isolate the SHORT capsule (band [0,1]) up close: does inscribe destroy it?
for xi, z1 in ((0.0, 3.0), (1.7, 1.0)):          # TALL and SHORT (band-1-like)
    cap = B.capsule((xi, 0, 0), (xi, 0, z1), 0.4, body)
    inscribe(cap, [1, 0, None], xi, 0.0, 0.4, 0.0, z1, 1, VIEW)

cam = bpy.data.cameras.new("c"); cam.lens = 42
co = bpy.data.objects.new("c", cam)
bpy.context.scene.collection.objects.link(co); bpy.context.scene.camera = co
tgt = mathutils.Vector((0.85, 0, 1.1))
eye = tgt + 6.5 * mathutils.Vector(VIEW).normalized()
co.location = eye
co.rotation_euler = (tgt - eye).to_track_quat("-Z", "Y").to_euler()
B.render("glyph_test", hdr=False)
