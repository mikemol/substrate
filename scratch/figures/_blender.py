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


def scene(samples=128, res=(1000, 1000), bg="#e9eef5", haze=0.0):
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


def box_wire(bounds, color="#ff3333", radius=0.01, emission=3.0):
    """The 12 edges of a box (bounds = x0,x1,y0,y1,z0,z1) as glowing tubes."""
    x0, x1, y0, y1, z0, z1 = bounds
    corners = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    mat = material(color, emission=emission)
    for i, a in enumerate(corners):
        for b in corners[i + 1:]:
            if sum(1 for k in range(3) if a[k] != b[k]) == 1:
                tube(a, b, radius, mat)


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


# --- declarative rig: box + camera DRIVEN by the data's bounding box ---
# (Blender drivers evaluate headless; arithmetic expressions aren't blocked by
#  the script-autoexec security flag.) The diegetic box scales itself to 1.5x
#  the data bbox and the camera backs off along its rail to satisfy the framing
#  — so the environment reflows if the geometry changes, no per-figure tuning.

def _driver(obj, prop, index, expr, variables, data_path_obj=None):
    fc = (data_path_obj or obj).driver_add(prop, index)
    drv = fc.driver
    drv.type = "SCRIPTED"
    for name, target, path in variables:
        v = drv.variables.new()
        v.name = name
        v.type = "SINGLE_PROP"
        v.targets[0].id = target
        v.targets[0].data_path = path
    drv.expression = expr
    return fc


def join_data(name="Data"):
    """Join every mesh in the scene into one object (so its .dimensions is the
    live bounding box that the box/camera read). Call AFTER building the data
    geometry and BEFORE driven_box / driven_camera."""
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not meshes:
        return None
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    if len(meshes) > 1:
        bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = name
    return obj


def _bbox(obj):
    cs = [obj.matrix_world @ mathutils.Vector(c) for c in obj.bound_box]
    xs = [c.x for c in cs]; ys = [c.y for c in cs]; zs = [c.z for c in cs]
    center = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
    dims = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    return center, dims


# Framing policy. The diegetic box's corners are fit to TOUCH the frame edges
# (the box fills the viewport); label room is the box *interior* — the outer-
# third gap between the data and the walls, given for free by the 1.5x ratio.
# Raise MARGIN only to inset the whole box (a border outside it); 0 = touch.
MARGIN = 0.0


def _box_center_coeffs(align, factor):
    """Per-axis box-centre offset coefficient k: box_centre = data_centre + k·dim.

    Because the box is factor=1.5 x the data, the data is exactly 2/3 of the box
    per axis, so the rule-of-thirds is a *relative* constraint between them and
    placement is a per-axis index `align` ∈ {-1, 0, +1}: data flush-min (edge on
    the box's lower 1/3 line) / centred / flush-max."""
    return [-align[i] * 0.5 * (factor - 1) for i in range(3)]


def parametric_diagonal_rig(diag, r, theta_deg=5.0):
    """Closed-form soft-beam rig along a diagonal of length `diag` (generalises a
    cube's S·√3 to any box). Inputs: diagonal length, pin-hole radius r, cone
    expansion half-angle θ. Returns (d2, d1, R): pin-hole→target, light→pin-hole,
    and the light-disk radius R that sets the penumbra. Pure algebra — one sqrt,
    no solver, no branches.  Real iff diag·tanθ ≥ 5.83·r (keep r small)."""
    tan_t = math.tan(math.radians(theta_deg))
    B = r - diag * tan_t
    d2 = (-B - math.sqrt(B * B - 4.0 * r * diag * tan_t)) / (2.0 * tan_t)
    d1 = diag - d2
    R = r * diag / d2
    return d2, d1, R


def driven_box(data, factor=1.5, align=(0, 0, 0), color="#dadada",
               floor_only=False, spots=True, spot_deg=5.0, spot_energy=300.0,
               pinhole=0.012):
    """Floor + two back walls driven to box = factor x data, with the data
    placed per the `align` thirds-index on each axis (see _box_center_coeffs).

    `spots`: the box's default museum lighting — a spotlight at each of the 8
    box corners aimed at the opposing corner (through the centre), a tight
    `spot_deg`° cone. Positions are driven, so the rig reflows with the box."""
    (cx, cy, cz), (dx, dy, dz) = _bbox(data)
    f = factor
    c = (cx, cy, cz); dd = (dx, dy, dz)
    k = _box_center_coeffs(align, f)
    D = {"dx": ("dx", data, "dimensions[0]"), "dy": ("dy", data, "dimensions[1]"),
         "dz": ("dz", data, "dimensions[2]")}
    import os
    if os.environ.get("BL_DEBUG"):
        box_wire((cx-dx/2, cx+dx/2, cy-dy/2, cy+dy/2, cz-dz/2, cz+dz/2), "#00cc44")
        bc = [c[i] + k[i]*dd[i] for i in range(3)]
        box_wire((bc[0]-0.5*f*dx, bc[0]+0.5*f*dx, bc[1]-0.5*f*dy, bc[1]+0.5*f*dy,
                  bc[2]-0.5*f*dz, bc[2]+0.5*f*dz), "#ff3333")
    mat = material(color, rough=0.9)

    def lin(const, coef, dim):                  # location channel: const + coef·dim
        if abs(coef) < 1e-12:
            return str(const), []
        return f"{const} + ({coef})*{dim}", [D[dim]]

    def sca(coef, dim):                         # scale (half-extent) channel
        return f"({coef})*{dim}", [D[dim]]

    def plane(name, rot, locx, locy, locz, scx, scy):
        bpy.ops.mesh.primitive_plane_add()
        o = bpy.context.active_object; o.name = name; o.rotation_euler = rot
        o.data.materials.append(mat)
        for i, (e, v) in enumerate((locx, locy, locz)):
            _driver(o, "location", i, e, v)
        for i, (e, v) in enumerate((scx, scy)):
            _driver(o, "scale", i, e, v)

    plane("floor", (0, 0, 0),
          lin(cx, k[0], "dx"), lin(cy, k[1], "dy"), lin(cz, k[2] - 0.5*f, "dz"),
          sca(0.5*f, "dx"), sca(0.5*f, "dy"))
    if not floor_only:
        plane("back", (math.pi/2, 0, 0),
              lin(cx, k[0], "dx"), lin(cy, k[1] + 0.5*f, "dy"), lin(cz, k[2], "dz"),
              sca(0.5*f, "dx"), sca(0.5*f, "dz"))
        plane("left", (0, math.pi/2, 0),
              lin(cx, k[0] - 0.5*f, "dx"), lin(cy, k[1], "dy"), lin(cz, k[2], "dz"),
              sca(0.5*f, "dz"), sca(0.5*f, "dy"))

    if spots:
        # Museum: a dark room so the box spot rig reads.
        w = bpy.context.scene.world
        if w and w.use_nodes and w.node_tree.nodes.get("Background"):
            w.node_tree.nodes["Background"].inputs[1].default_value = 0.0
        dims3 = ("dx", "dy", "dz")
        # Box-centre target (driven), aimed-through by every corner spot.
        focus = bpy.data.objects.new("BoxFocus", None)
        bpy.context.scene.collection.objects.link(focus)
        focus.location = tuple(c[i] + k[i] * dd[i] for i in range(3))
        for i in range(3):
            e, v = lin(c[i], k[i], dims3[i])
            _driver(focus, "location", i, e, v)
        # Soft-beam rig (closed form): R sets the penumbra (→ emitter radius).
        diag = math.sqrt(sum((factor * dd[i]) ** 2 for i in range(3)))
        _, _, R_disk = parametric_diagonal_rig(diag, pinhole * diag, spot_deg)

        # A corner touches a rendered wall iff it's on the floor (sz=-1), the
        # back wall (sy=+1) or the left wall (sx=-1); the lone open corner
        # (+1,-1,+1) faces the camera. Keep a spot only if BOTH its source and
        # its target corner touch a wall — no light from the camera point, none
        # aimed into the camera.
        def on_wall(t):
            return t[2] == -1 or t[1] == 1 or t[0] == -1

        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    s = (sx, sy, sz)
                    if not on_wall(s) or not on_wall((-sx, -sy, -sz)):
                        continue
                    ld = bpy.data.lights.new("boxspot", "SPOT")
                    ld.spot_size = math.radians(2.0 * spot_deg)   # full cone = 2θ
                    ld.spot_blend = 0.35
                    ld.shadow_soft_size = R_disk                  # penumbra
                    ld.energy = spot_energy
                    lo = bpy.data.objects.new("boxspot", ld)
                    bpy.context.scene.collection.objects.link(lo)
                    lo.location = tuple(c[i] + (k[i] + s[i] * 0.5 * f) * dd[i] for i in range(3))
                    for i in range(3):       # corner = box_centre + s·half_extent
                        e, v = lin(c[i], k[i] + s[i] * 0.5 * f, dims3[i])
                        _driver(lo, "location", i, e, v)
                    con = lo.constraints.new("TRACK_TO")
                    con.target = focus
                    con.track_axis = "TRACK_NEGATIVE_Z"
                    con.up_axis = "UP_Y"


def driven_camera(data, direction=(1.0, -0.9, 0.62), margin=MARGIN, lens=50,
                  sensor=36, fstop=2.0, factor=1.5, align=(0, 0, 0)):
    """Frame the diegetic box with Blender's *native* fit.

    Object.camera_fit_coords(depsgraph, corners) returns the exact camera
    location that frames given world points, with sensor / lens / aspect handled
    by Blender — so there is no hand-rolled fov/shift arithmetic (the thing that
    kept going wrong). The box is centred in frame; the `align` thirds-index
    places the data within the box, which lands the data on a viewport third
    without any lens shift. `margin` inflates the fit target so the box keeps a
    label border."""
    (cx, cy, cz), (dx, dy, dz) = _bbox(data)
    f = factor
    c = (cx, cy, cz); dd = (dx, dy, dz)
    k = _box_center_coeffs(align, f)
    bc = [c[i] + k[i] * dd[i] for i in range(3)]            # box centre
    inflate = 1.0 / (1.0 - margin)                         # leave a label border
    half = [0.5 * f * dd[i] * inflate for i in range(3)]
    corners = [v for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)
               for v in (bc[0] + sx * half[0], bc[1] + sy * half[1], bc[2] + sz * half[2])]

    d = np.asarray(direction, float); d = d / np.linalg.norm(d)
    cam = bpy.data.cameras.new("c")
    cam.lens = lens
    cam.sensor_width = sensor
    cam.dof.use_dof = True
    cam.dof.aperture_fstop = fstop
    o = bpy.data.objects.new("c", cam)
    bpy.context.scene.collection.objects.link(o)
    bpy.context.scene.camera = o
    o.rotation_euler = mathutils.Vector(tuple(d)).to_track_quat("Z", "Y").to_euler()
    bpy.context.view_layer.update()
    loc, _ = o.camera_fit_coords(bpy.context.evaluated_depsgraph_get(), corners)
    o.location = loc
    cam.dof.focus_distance = (mathutils.Vector(loc) - mathutils.Vector(bc)).length
    return o


def driven_rig(data, direction=(1.0, -0.9, 0.62), align=(0, 0, 0), factor=1.5,
               margin=MARGIN, floor_only=False, color="#dadada"):
    """Box (drivers) + camera (native fit), sharing factor/align."""
    driven_box(data, factor=factor, align=align, color=color, floor_only=floor_only)
    return driven_camera(data, direction=direction, margin=margin, factor=factor,
                         align=align)


def _overlay_thirds(path):
    """Draw the rule-of-thirds grid + power-point ticks on the rendered PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg
    img = mpimg.imread(path)
    h, w = img.shape[:2]
    fig = plt.figure(figsize=(w / 100, h / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.set_axis_off()
    for fr in (1 / 3, 2 / 3):
        ax.axvline(fr * w, color="#ff2222", lw=0.8, alpha=0.55)
        ax.axhline(fr * h, color="#ff2222", lw=0.8, alpha=0.55)
    for fx in (1 / 3, 2 / 3):
        for fy in (1 / 3, 2 / 3):
            ax.plot(fx * w, fy * h, "+", color="#ff2222", ms=12, mew=1.5)
    ax.set_xlim(0, w); ax.set_ylim(h, 0)
    fig.savefig(path, dpi=100); plt.close(fig)


def render(name):
    import os
    sc = bpy.context.scene
    path = str(OUT / f"{name}.png")
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    if os.environ.get("BL_DEBUG"):
        _overlay_thirds(path)
    print(f"BL_WROTE {path}")
