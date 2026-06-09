"""Blender/Cycles rendering substrate for the 3D figures.

Run *inside* Blender's bundled Python (itself 3.14, matching the venv):

    blender --background --python scratch/figures/<name>_bl.py

Each figure script bootstraps sys.path to reach the venv site-packages and this
directory, then imports the same pure-data builders the matplotlib/PyVista
figures use (_perm, _klein, _fano, _catalog, _graphs, _lift3d) and calls the
helpers here. Cycles gives what VTK could not give simultaneously: real
area-light soft shadows *and* correct transparency (the Fano planes tint the
floor and cast partial shadows at once), plus global illumination and DOF haze.
"""

import math

import bpy
import mathutils
import numpy as np

OUT = None  # set by boot()


# --- colour: Blender stores linear; our palette is sRGB hex. ---

def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(hex_color, alpha=1.0):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return (_srgb_to_linear(r), _srgb_to_linear(g), _srgb_to_linear(b), alpha)


PALETTE = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7",
           "#56B4E9", "#F0E442", "#999999"]


# --- scene / world ---

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def _enable_gpu():
    """Turn on a GPU compute backend if available (CUDA/OptiX/oneAPI/HIP).

    Honours env BL_BACKEND to pin one backend (so a multi-instance runner can
    send some figures to the NVIDIA card via CUDA and others to the Intel iGPU
    via ONEAPI, each in its own process — Cycles can't mix backends in one pass).
    """
    import os
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
    except Exception:
        return None
    forced = os.environ.get("BL_BACKEND")
    order = [forced] if forced else ["OPTIX", "CUDA", "ONEAPI", "HIP"]
    for backend in order:
        try:
            prefs.compute_device_type = backend
        except Exception:
            continue
        prefs.refresh_devices()
        gpus = [d for d in prefs.devices if d.type == backend]
        if gpus:
            for d in prefs.devices:
                d.use = (d.type != "CPU")
            return backend
    return None


def scene(samples=128, res=(1100, 950), bg="#e9eef5", haze=0.0):
    import os
    # Env overrides for fast iteration: BL_SAMPLES=24 BL_RES=480x400 (preview).
    samples = int(os.environ.get("BL_SAMPLES", samples))
    if os.environ.get("BL_RES"):
        w, h = os.environ["BL_RES"].lower().split("x")
        res = (int(w), int(h))
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.01
    try:
        sc.cycles.use_denoising = True
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    backend = _enable_gpu()
    sc.cycles.device = "GPU" if backend else "CPU"
    print(f"BL_DEVICE {sc.cycles.device} ({backend or 'cpu'})")
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.film_transparent = False
    # Accurate colour (no AgX desaturation of the Okabe-Ito hues).
    try:
        sc.view_settings.view_transform = "Standard"
    except Exception:
        pass
    world = bpy.data.worlds.new("w")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    bgn = nt.nodes["Background"]
    bgn.inputs[0].default_value = rgba(bg)
    bgn.inputs[1].default_value = 1.0
    if haze > 0:
        vol = nt.nodes.new("ShaderNodeVolumeScatter")
        vol.inputs["Density"].default_value = haze
        nt.links.new(vol.outputs[0], nt.nodes["World Output"].inputs["Volume"])
    return sc


def material(color, rough=0.5, alpha=1.0, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new("m")
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba(color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = rgba(color)
        b.inputs["Emission Strength"].default_value = emission
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
    return mat


# --- primitives ---

def sphere(center, radius, mat, seg=32, ring=16):
    bpy.ops.mesh.primitive_uv_sphere_add(location=tuple(center), radius=radius,
                                         segments=seg, ring_count=ring)
    o = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def tube(a, b, radius, mat, verts=14):
    a = np.asarray(a, float); b = np.asarray(b, float)
    vec = b - a
    length = float(np.linalg.norm(vec))
    if length < 1e-9:
        return None
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length,
                                        location=tuple((a + b) / 2), vertices=verts)
    o = bpy.context.active_object
    o.rotation_euler = mathutils.Vector(vec).to_track_quat("Z", "Y").to_euler()
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def polys(faces_xyz, mat, smooth=False):
    """faces_xyz: list of (k,3) vertex arrays — one convex polygon each."""
    verts, faces = [], []
    for poly in faces_xyz:
        base = len(verts)
        verts.extend([tuple(v) for v in poly])
        faces.append(tuple(range(base, base + len(poly))))
    mesh = bpy.data.meshes.new("p")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new("p", mesh)
    bpy.context.scene.collection.objects.link(o)
    if smooth:
        for pgon in mesh.polygons:
            pgon.use_smooth = True
    o.data.materials.append(mat)
    return o


def box_cube(center, size, mat):
    bpy.ops.mesh.primitive_cube_add(location=tuple(center))
    o = bpy.context.active_object
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    o.data.materials.append(mat)
    return o


# --- diegetic box (floor + two back walls), real Cycles shadow-catchers ---

def diegetic_box(bounds, factor=1.5, vbias=0.0, color="#dadada", floor_only=False):
    """A box `factor`x the object (default 1.5x → object fills the inner 2/3,
    walls at the outer third: a 3-D rule-of-thirds). vbias in [-1,1] shifts the
    object within the box vertically — vbias>0 gives headroom above (object
    sits low, for things that open upward)."""
    x0, x1, y0, y1, z0, z1 = bounds

    def expand(a, b, vb=0.0):
        m = (factor - 1.0) * (b - a)          # total extra margin on this axis
        return a - m * (0.5 - vb * 0.5), b + m * (0.5 + vb * 0.5)
    x0, x1 = expand(x0, x1)
    y0, y1 = expand(y0, y1)
    z0, z1 = expand(z0, z1, vbias)
    mat = material(color, rough=0.9)
    cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2

    def plane(center, rot, sx, sy):
        bpy.ops.mesh.primitive_plane_add(location=center)
        o = bpy.context.active_object
        o.rotation_euler = rot
        o.scale = (sx / 2, sy / 2, 1)
        o.data.materials.append(mat)
    plane((cx, cy, z0), (0, 0, 0), x1 - x0, y1 - y0)            # floor
    if not floor_only:
        plane((cx, y1, cz), (np.pi / 2, 0, 0), x1 - x0, z1 - z0)  # back wall
        plane((x0, cy, cz), (0, np.pi / 2, 0), z1 - z0, y1 - y0)  # left wall


# --- lights: a big area light → real soft shadows with penumbra ---

def lights(key=(6, -5, 9), key_energy=1500, key_size=8, fill=(-7, -3, 5),
           fill_energy=300, target=(0, 0, 0)):
    def area(loc, energy, size, name):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy; ld.size = size
        o = bpy.data.objects.new(name, ld)
        bpy.context.scene.collection.objects.link(o)
        o.location = loc
        d = mathutils.Vector(target) - mathutils.Vector(loc)
        o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    area(key, key_energy, key_size, "key")
    area(fill, fill_energy, key_size * 0.7, "fill")


# --- camera: rule-of-thirds via lens shift, optional DOF haze ---

def frame(points, direction=(1.0, -0.9, 0.62), fill=0.58, lens=50, sensor=36,
          shift=(0.07, -0.07), dof=True, fstop=2.0, dist_mult=None):
    """Rule-of-thirds viewport framing.

    `fill` is the fraction of the frame half-height the object's outermost point
    reaches: ~0.58 keeps the bulk inward of the third-cell centres while the one
    extreme touches the rule-of-thirds region; `shift` (lens shift) offsets the
    subject to a power point. Pass dist_mult to override the auto distance.
    """
    points = np.asarray(points, float)
    focal = points.mean(axis=0)
    R = float(np.linalg.norm(points - focal, axis=1).max()) or 1.0
    d = np.asarray(direction, float); d = d / np.linalg.norm(d)
    if dist_mult is not None:
        dist = dist_mult * R
    else:
        half_fov = math.atan(sensor / (2.0 * lens))
        dist = R / (fill * math.tan(half_fov))
    loc = focal + d * dist

    cam = bpy.data.cameras.new("c")
    cam.lens = lens
    cam.shift_x, cam.shift_y = shift
    if dof:
        cam.dof.use_dof = True
        cam.dof.focus_distance = float(np.linalg.norm(loc - focal))
        cam.dof.aperture_fstop = fstop
    o = bpy.data.objects.new("c", cam)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.scene.camera = o
    o.location = tuple(loc)
    dd = mathutils.Vector(tuple(focal)) - mathutils.Vector(tuple(loc))
    o.rotation_euler = dd.to_track_quat("-Z", "Y").to_euler()
    return o


def render(name):
    sc = bpy.context.scene
    path = str(OUT / f"{name}.png")
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"BL_WROTE {path}")
