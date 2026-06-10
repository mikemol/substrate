#!/usr/bin/env python3
"""Prototype: inset (engraved) glowing vertical text on a capsule.

Validates text->mesh, boolean DIFFERENCE engrave, glowing inset faces, vertical
layout (top->down), and the mirror case (downward capsule reads upside-down),
before applying to all 64 in cayley_dickson_bl.

    blender --background --python scratch/figures/_inscribe_test.py
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

body = B.material("#D55E00", rough=0.3, emission=5.0, emission_away=(0, -1, 0.35))
glow = B.material("#ffffff", emission=40.0)


def inscribe(target, text, rad, z_top, glow_mat, mirror=False,
             size=0.34, pitch=0.42, depth=0.08):
    """Engrave `text` vertically into the −Y front of a vertical capsule and make
    the recess floor glow. Top→down; mirror flips it upside-down."""
    chars = list(text)
    objs = []
    y_centre = -rad - 0.02 + depth                # cutter front just outside −Y face
    for i, ch in enumerate(chars):
        cu = bpy.data.curves.new("t", "FONT")
        cu.body = ch; cu.size = size; cu.extrude = depth
        cu.align_x = "CENTER"; cu.align_y = "CENTER"
        o = bpy.data.objects.new("ch", cu)
        bpy.context.scene.collection.objects.link(o)
        # face −Y, upright; mirror = upside-down (180° about the −Y facing axis)
        o.rotation_euler = (-math.pi / 2, math.pi if mirror else 0.0, 0.0)
        idx = (len(chars) - 1 - i) if mirror else i
        z = z_top - pitch * 0.6 - idx * pitch
        o.location = (0.0, y_centre, z)
        for s in bpy.context.selected_objects:
            s.select_set(False)
        o.select_set(True); bpy.context.view_layer.objects.active = o
        bpy.ops.object.convert(target="MESH")
        objs.append(o)
    for s in bpy.context.selected_objects:
        s.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    cutter = bpy.context.view_layer.objects.active
    m = target.modifiers.new("inscribe", "BOOLEAN")
    m.operation = "DIFFERENCE"; m.object = cutter; m.solver = "EXACT"
    bpy.context.view_layer.objects.active = target
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter)
    # Glow the recess floor: faces recessed inside the −Y surface, facing the lens.
    me = target.data
    if glow_mat.name not in me.materials:
        me.materials.append(glow_mat)
    gi = me.materials.find(glow_mat.name)
    bm = bmesh.new(); bm.from_mesh(me)
    for f in bm.faces:
        cen = f.calc_center_median()
        if cen.y > -rad + 0.03 and cen.y < 0 and f.normal.y < -0.3:
            f.material_index = gi
    bm.to_mesh(me); bm.free()


cap = B.capsule((0, 0, 0), (0, 0, 4.0), 0.4, body)
inscribe(cap, "e3", 0.4, 4.0, glow)

# camera head-on (−Y) on the inscription
cam = bpy.data.cameras.new("c"); cam.lens = 90
co = bpy.data.objects.new("c", cam)
bpy.context.scene.collection.objects.link(co)
bpy.context.scene.camera = co
eye, tgt = mathutils.Vector((0, -4.2, 3.5)), mathutils.Vector((0, 0, 3.5))
co.location = eye
co.rotation_euler = (tgt - eye).to_track_quat("-Z", "Y").to_euler()
B.render("inscribe_test", hdr=False)
