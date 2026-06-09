"""PyVista rendering substrate for the 3D figures — real lighting & shadows.

Matplotlib's 3D is painter's-algorithm: no true occlusion, no cast shadows, no
ambient occlusion. This module is the drop-in *rendering* layer that the 3D
figures use instead, while reusing all the existing *data* shadows (the pure-
numpy LiftMaps in _lift3d, and the _perm / _klein / _fano / _catalog / _graphs
builders). Only the draw step changes.

What you get for free here: VTK shadow maps (`enable_shadows`), screen-space
ambient occlusion (`enable_ssao`), PBR materials, anti-aliasing, and a genuine
diegetic box — floor + walls are real meshes that occlude and catch the
object's real shadow.

Renders headless (the VTK wheel ships EGL/OSMesa); `--interactive` opens a
window. Output is PNG (VTK is a raster renderer).
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True

FIGURES_DIR = Path(__file__).resolve().parent
DEFAULT_OUT = FIGURES_DIR / "out"
REPO_ROOT = FIGURES_DIR.parent.parent

PALETTE = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7",
           "#56B4E9", "#F0E442", "#999999"]


def make_parser(name: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=f"{name}.py", description=f"Render {name} (PyVista).")
    p.add_argument("--interactive", action="store_true", help="Open a window instead of saving.")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--size", type=int, default=1200, help="Render size (px, square-ish).")
    p.add_argument("--no-shadows", action="store_true")
    p.add_argument("--no-ssao", action="store_true")
    p.add_argument("--no-haze", action="store_true", help="Disable depth-of-field haze.")
    p.add_argument("--edl", action="store_true",
                   help="Add eye-dome lighting (strong depth edges, but darkens colours).")
    return p


def scene(args, window=None):
    win = window or (int(args.size * 1.15), args.size)
    p = pv.Plotter(off_screen=not args.interactive, window_size=win, lighting="none")
    p.set_background("white")
    return p


def add_lights(p, key=(6, -4, 9), fill=(-7, -3, 5), softness=3.5, n_key=10,
               key_intensity=0.95):
    """A *wide* key light (a disk of jittered samples → penumbra) + fill + ambient.

    A single directional light casts hard, penumbra-less shadows. Spreading the
    key into `n_key` lights over a disk of radius `softness` (world units),
    perpendicular to the key direction, makes each cast a slightly-offset hard
    shadow whose union is a soft-edged shadow with real penumbra. `softness`
    controls how wide the source is.
    """
    key = np.asarray(key, float)
    kdir = key / np.linalg.norm(key)
    a = np.array([0.0, 0.0, 1.0])
    if abs(kdir @ a) > 0.9:
        a = np.array([1.0, 0.0, 0.0])
    u = np.cross(kdir, a); u /= np.linalg.norm(u)
    v = np.cross(kdir, u)
    for i in range(n_key):
        ang = 2 * np.pi * i / n_key
        pos = key + softness * (np.cos(ang) * u + np.sin(ang) * v)
        p.add_light(pv.Light(position=tuple(pos), focal_point=(0, 0, 0),
                             color="white", intensity=key_intensity / n_key,
                             positional=False))
    p.add_light(pv.Light(position=fill, focal_point=(0, 0, 0), color="white",
                         intensity=0.32, positional=False))
    p.add_light(pv.Light(position=(0, 0, 10), focal_point=(0, 0, 0), color="white",
                         intensity=0.18, positional=False))


def diegetic_box(p, bounds, pad=0.12, color="#dcdcdc", floor_only=False):
    """Floor + two back walls as real meshes — the object's true shadow lands here.

    bounds = (xmin,xmax,ymin,ymax,zmin,zmax). Walls placed at xmin, ymax, zmin.
    """
    x0, x1, y0, y1, z0, z1 = bounds
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    x0 -= pad * dx; x1 += pad * dx; y0 -= pad * dy; y1 += pad * dy; z0 -= pad * dz
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    cz = (z0 + z1) / 2
    floor = pv.Plane(center=(cx, cy, z0), direction=(0, 0, 1),
                     i_size=(x1 - x0), j_size=(y1 - y0))
    p.add_mesh(floor, color=color, ambient=0.3, diffuse=0.8, specular=0.0)
    if not floor_only:
        back = pv.Plane(center=(cx, y1, cz), direction=(0, 1, 0),
                        i_size=(x1 - x0), j_size=(z1 - z0))
        left = pv.Plane(center=(x0, cy, cz), direction=(1, 0, 0),
                        i_size=(y1 - y0), j_size=(z1 - z0))
        for w in (back, left):
            p.add_mesh(w, color=color, ambient=0.28, diffuse=0.75, specular=0.0)


def spheres(p, coords, scalars=None, cmap="coolwarm", radius=0.06, color=None,
            clim=None):
    pts = pv.PolyData(np.asarray(coords, float))
    if scalars is not None:
        pts["s"] = np.asarray(scalars, float)
    glyph = pts.glyph(geom=pv.Sphere(radius=radius, theta_resolution=24,
                                     phi_resolution=24), scale=False, orient=False)
    kw = dict(smooth_shading=True, specular=0.3, specular_power=15)
    if scalars is not None:
        p.add_mesh(glyph, scalars="s", cmap=cmap, clim=clim, show_scalar_bar=False, **kw)
    else:
        p.add_mesh(glyph, color=color or PALETTE[0], **kw)
    return glyph


def tubes(p, coords, edges, colors=None, radius=0.012):
    coords = np.asarray(coords, float)
    if colors is None:
        colors = ["#888888"] * len(edges)
    for (i, j), col in zip(edges, colors):
        seg = pv.Line(coords[i], coords[j]).tube(radius=radius, n_sides=12)
        p.add_mesh(seg, color=col, smooth_shading=True, specular=0.2)


def surface(p, Z, cmap="viridis", scalars=None, clim=None, color=None,
            x=None, y=None):
    """A height field Z (2D array) as a real lit surface."""
    Z = np.asarray(Z, float)
    ny, nx = Z.shape
    if x is None:
        x = np.arange(nx, dtype=float)
    if y is None:
        y = np.arange(ny, dtype=float)
    X, Y = np.meshgrid(x, y)
    grid = pv.StructuredGrid(X, Y, Z)
    sc = (Z if scalars is None else np.asarray(scalars, float)).ravel(order="F")
    grid["c"] = sc
    kw = dict(smooth_shading=True, specular=0.15)
    if color is not None:
        p.add_mesh(grid, color=color, **kw)
    else:
        p.add_mesh(grid, scalars="c", cmap=cmap, clim=clim, show_scalar_bar=False, **kw)
    return grid


def frame_camera(points, direction=(1.0, -0.9, 0.62), dist_mult=4.6):
    """Inset rule-of-thirds framing: eye placed along `direction` at dist_mult·R.

    Larger dist_mult → more margin (subject stays inside the inner cells rather
    than bleeding to the border). The off-centre placement is done in finish()
    via the camera window centre.
    """
    points = np.asarray(points, float)
    focal = points.mean(axis=0)
    R = float(np.linalg.norm(points - focal, axis=1).max()) or 1.0
    d = np.asarray(direction, float)
    d = d / np.linalg.norm(d)
    eye = focal + d * dist_mult * R
    return [tuple(eye), tuple(focal), (0, 0, 1)]


def title(p, text, size=18):
    p.add_text(text, position="upper_left", font_size=size // 2, color="#222222")


def add_labels(p, points, names, font_size=20, color="#111111"):
    """Floating text labels at 3D points (always visible, on a soft pill)."""
    poly = pv.PolyData(np.asarray(points, float))
    p.add_point_labels(
        poly, [str(n) for n in names], font_size=font_size, text_color=color,
        shape="rounded_rect", shape_color="white", shape_opacity=0.6,
        margin=3, point_size=0, always_visible=True, bold=True,
        render_points_as_spheres=False)


def legend(p, entries, face="circle", loc="upper right", size=(0.24, None)):
    """A colour key. entries: list of (label, color)."""
    w, h = size
    if h is None:
        h = 0.05 + 0.04 * len(entries)
    p.add_legend(labels=[(lbl, col) for lbl, col in entries], bcolor="white",
                 border=True, face=face, size=(w, h), loc=loc,
                 background_opacity=0.85)


def finish(p, name, args, camera=None, thirds=(0.2, 0.15), haze=True,
           transparency=False):
    """Stack every depth cue VTK gives us, then frame and render.

    Cues, all guarded so one failing backend pass doesn't sink the image:
    cast shadows, SSAO (contact darkening), eye-dome lighting (depth-edge
    relief), depth-of-field (aerial haze on far geometry), a gradient sky
    background, and rule-of-thirds framing via the camera window centre.

    transparency=True: the figure uses depth-peeling (translucent meshes), so
    SSAO and depth-of-field are skipped — those two rebuild the render-pass
    chain and break order-independent transparency (the floor would show no
    tint under a translucent plane). Shadows + AA stay; they're compatible.
    """
    if transparency:
        args = argparse.Namespace(**{**vars(args), "no_ssao": True, "no_haze": True})
    # Gentle atmosphere: pale sky above, near-white below.
    try:
        p.set_background("#f4f5f7", top="#dbe4ef")
    except Exception:
        pass
    if camera is not None:
        p.camera_position = camera
    if thirds is not None:
        try:
            p.camera.SetWindowCenter(*thirds)
        except Exception:
            pass

    if not args.no_ssao:
        try:
            p.enable_ssao(radius=0.5, bias=0.01)
        except Exception:
            pass
    if args.edl:
        try:
            p.enable_eye_dome_lighting()
        except Exception:
            pass
    if not args.no_shadows:
        try:
            p.enable_shadows()
        except Exception:
            pass
    try:
        p.enable_anti_aliasing("ssaa")
    except Exception:
        pass
    if haze and not args.no_haze:
        try:
            p.enable_depth_of_field()
        except Exception:
            pass

    if args.interactive:
        p.show()
        return
    args.out.mkdir(parents=True, exist_ok=True)
    path = args.out / f"{name}.png"
    p.screenshot(str(path), transparent_background=False)
    print(f"  wrote {path}  ({path.stat().st_size:,} bytes)")
