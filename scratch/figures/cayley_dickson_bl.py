#!/usr/bin/env python3
"""Octonion table as a Cayley–Dickson tower — z IS the CD level. Blender/Cycles.

The CD sign cocycle factorises: e_i·e_j = (∏_L σ_L)·e_{i⊕j}, with σ_L ∈ {±1} the
sign introduced at doubling level L. Here the VERTICAL axis is the level itself, and each band's HEIGHT doubles with
the CD dimension (ℂ 1, ℍ 2, 𝕆 4): ℂ occupies |z|∈[0,1], ℍ |z|∈[1,3], 𝕆 |z|∈[3,7],
each a single hue (ℂ blue, ℍ green, 𝕆 orange). So a horizontal z=n slice is ONE
level = ONE colour for every column at that height — colour is a pure function of
z — and the dimension-doubling is legible as the band heights.

Each product is a column of height h = |result index| (e_{r⊕c}), rising (+) or
descending (−) by the product's overall sign, coloured by the level bands it
passes through — so it tops out in its OWN level's band (h=1 → ℂ, h∈[2,3] → ℍ,
h∈[4,7] → 𝕆). Column heights vary 1…7 (the result magnitude, as in octonion_bl),
z-slices stay one colour, and the band boundaries 1,3,7 are the doublings.
Position is the grid (center-out: 𝕆 on the rim).

    blender --background --python scratch/figures/cayley_dickson_bl.py
"""

import pathlib
import sys

_H = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_H))
sys.path.append(str(_H.parents[1] / ".venv/lib/python3.14/site-packages"))

import math

import numpy as np
import bpy
import bmesh
import mathutils
import _blender as B

B.OUT = _H / "out"; B.OUT.mkdir(exist_ok=True)

GLOW = None   # inset inscription glow material; built after B.reset() (which wipes data)


def glyph_shapes(state, r):
    """Euclidean boolean-coordinate mark, unit = pip radius r. Equilateral ABC on
    edge AB (= 3r), apex C below; A = TRUE (up-left), B = FALSE (up-right). Tail CD
    is AC produced beyond C with CD = CA, so its line runs through A — the pointer
    at truth. Pips: filled disc = that point set; an UNSET point renders nothing (it
    is only a conceptual placeholder). state 1 → A set (true); 0 → B set (false);
    None → neither (unset, tail only). Read invariantly under 180° flip as 'is the
    lit pip at the corner the tail points to?'. 2D (u,v): u horizontal (→ arc around
    the pawn), v vertical (→ meridian). Returns a list of point-lists."""
    e = 3.0 * r
    A = mathutils.Vector((-0.5 * e, 0.8660254 * e))   # TRUE
    Bp = mathutils.Vector((0.5 * e, 0.8660254 * e))   # FALSE
    C = mathutils.Vector((0.0, 0.0))                  # apex
    D = C + e * (C - A).normalized()                  # produce AC beyond C, CD = CA
    rs = 0.5 * r                                  # stroke radius: pip + half line-width
    shapes = []
    a0 = math.atan2((D - C).y, (D - C).x)         # tail = 2D capsule (stadium): a
    sg, tail = 8, []                              # segment with semicircle caps of
    for k in range(sg + 1):                       # radius rs ⇒ width = pip diameter 2·rs
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
        if is_set:                              # unset → placeholder only, render nothing
            shapes.append(disc(pt))
    return shapes


def inscribe(cap, bits, x, y, rad, z0, z1, updown, face, depth=0.05):
    """Engrave the 3 boolean-coordinate glyphs (b2 far tip → b0 near grid) of `bits`
    onto capsule `cap`, glowing the recess floors. Each glyph is a 2D decal CONFORMED
    to the capsule surface — wrapped over the endcaps via meridian arc-length and
    extruded along the LOCAL surface normal — so pips engrave on body and cap alike.
    Carved one glyph at a time (overlapping cutters self-intersect on stubby pawns);
    floors selected via the capsule SDF. `face` = horizontal unit toward the camera."""
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
        return pt, nr * rdir + mathutils.Vector((0.0, 0.0, nz))

    def cut_one(state, s_c):                     # carve ONE glyph with its own boolean
        verts, faces = [], []
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

    gh = 3.1 * r + 0.07                          # glyph reach along meridian + clearance
    s_lo, s_hi = 0.5 * qc + gh, S - 0.5 * qc - gh  # stay below the caps' 45th parallel
    if s_hi <= s_lo:                             # too short → centre all three on the body
        s_lo = s_hi = 0.5 * S
    order = (s_hi, 0.5 * (s_lo + s_hi), s_lo) if updown > 0 \
        else (s_lo, 0.5 * (s_lo + s_hi), s_hi)  # b2 far tip → b0 near grid
    for gi, state in enumerate(bits):
        cut_one(state, order[gi])

    cme = cap.data                              # glow recessed floors via capsule SDF
    if GLOW.name not in cme.materials:
        cme.materials.append(GLOW)
    gi = cme.materials.find(GLOW.name)
    bm = bmesh.new(); bm.from_mesh(cme); bm.normal_update()
    for f in bm.faces:
        p = f.calc_center_median()
        cz = min(max(p.z, cyl_lo), cyl_hi)
        d = mathutils.Vector((p.x - x, p.y - y, p.z - cz)); dl = d.length
        if dl < 1e-6:
            continue
        if dl - rad < -0.4 * depth and f.normal.dot(d / dl) > 0.5:
            f.material_index = gi
    bm.to_mesh(cme); bm.free()


def cd_mult(level, i, j):
    """e_i·e_j in the 2^level Cayley–Dickson algebra (binary basis). Returns
    (index, total_sign, sigma) where sigma[L] is the ± introduced at doubling L.
    Recursion: (a,b)(c,d) = (ac − d̄b, da + bc̄), conj(e_m)=−e_m for m≠0."""
    if level == 0:
        return 0, 1, {}
    half = 1 << (level - 1)
    iu, ju = i >= half, j >= half
    il, jl = (i - half if iu else i), (j - half if ju else j)
    if not iu and not ju:                       # both lower
        k, s, sig = cd_mult(level - 1, il, jl); sig[level] = 1; return k, s, sig
    if not iu and ju:                           # i lower, j upper → e_jl·e_il, upper
        k, s, sig = cd_mult(level - 1, jl, il); sig[level] = 1; return k + half, s, sig
    if iu and not ju:                           # i upper, j lower → e_il·conj(e_jl)
        cj = 1 if jl == 0 else -1
        k, s, sig = cd_mult(level - 1, il, jl); sig[level] = cj; return k + half, s * cj, sig
    cj = 1 if jl == 0 else -1                    # both upper → −conj(e_jl)·e_il, lower
    k, s, sig = cd_mult(level - 1, jl, il); sl = -cj; sig[level] = sl; return k, s * sl, sig


# One saturated Okabe-Ito hue per CD level — colour == level, full stop. The sign
# is geometry (above/below the grid plane), never colour, so a z-slice is one hue.
LEVEL_HUE = {1: "#0072B2", 2: "#009E73", 3: "#D55E00"}   # ℂ blue, ℍ green, 𝕆 orange

B.reset()
B.scene(samples=128, haze=0.04)               # volumetric haze → bloom near lights
GLOW = B.material("#ffffff", emission=200.0)  # inset inscription glow (bloom seed)
VIEW = (0.8, -1.0, 0.7)   # camera direction (toward camera); also passed to the rig
# Per band: the camera-aware away-gate masked to ONE axis chosen by the per-level
# sign — emission &= (my-normal-axis == sign-axis). σ_L=+ glows from the back (+Y)
# away-face, σ_L=− from the left (−X). The away-gate keeps it off the lens; no
# camera change needed.
SIGN_AXIS = {1: (0, 1, 0), -1: (1, 0, 0)}   # +: +Y back  ;  −: −X left
level_mat = {(L, sd): B.material(c, rough=0.3, emission=24.0,
                                 emission_away=VIEW, emission_axis=SIGN_AXIS[sd])
             for L, c in LEVEL_HUE.items() for sd in (1, -1)}

# Center-out layout: reorder each axis so the CD level forms a VALLEY (low centre,
# high ends), so the 𝕆 step rides the rim and the structure grows centre-out.
AXIS = [4, 5, 2, 0, 1, 3, 6, 7]   # unit at each axis slot (levels 3,3,2,0,1,2,3,3)
pos = [0] * 8
for slot, u in enumerate(AXIS):
    pos[u] = slot

BOUND = [0, 1, 3, 7]   # level z-boundaries = max result index per level; heights 1,2,4
for r in range(8):
    for c in range(8):
        h, s, sigma = cd_mult(3, r, c)
        if h <= 0:
            continue
        updown = 1 if s >= 0 else -1             # overall product sign: up (+) / down (−)
        # Show ONLY the top doubling of each bar — the segment in the unit's own
        # level band (L = h.bit_length(), z = [BOUND[L-1], h]) — so each column is
        # just its top-level cap, clearing the lower bands' occlusion.
        L = h.bit_length()
        z0, z1 = BOUND[L - 1], h
        sd = 1 if sigma[L] > 0 else -1            # per-level sign σ_L → which side glows
        x, y, mat = pos[c], pos[r], level_mat[(L, sd)]
        # One-mesh capsule spanning [z0, z1] on the updown side — no cylinder/cap
        # seam, so the backlight gate gradients smoothly over the pawn.
        cap = B.capsule((x, y, updown * z0), (x, y, updown * z1), 0.4, mat)
        # Inscribe the 3 boolean-coordinate glyphs of the result unit h = r⊕c
        # (b2 top → b0 bottom): bit set above the unit's highest 1 is UNSET. Engraved
        # + glowing, facing the camera, rotation-invariant (no flip on downward pawns).
        u = r ^ c
        bl = u.bit_length()
        bits = [(((u >> p) & 1) if p < bl else None) for p in (2, 1, 0)]
        inscribe(cap, bits, x, y, 0.4, z0, z1, updown, VIEW)
data = B.join_data()
# Same gallery as octonion: forward a full cell off the back wall, 0.6 metal
# mirror, deep f/8 focus keeping the tiled-perspective reflections sharp.
B.driven_rig(data, direction=VIEW, align=(0, -2.0 / 3, 0),
             wall_rough=0.1, wall_metallic=1.0, fstop=16.0, wall_span=10.0)
B.render("cayley_dickson_bl")
