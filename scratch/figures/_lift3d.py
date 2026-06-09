"""The common substructure of every 3D lift in the gallery.

Faced with "which figures get a z-axis and how" — the either/or dissolves once
you see that *every* lift is the same three-part structure:

    base      : 2D positions (a graph layout) or a grid of cells
    scalar    : a field over the base  (Fiedler value, sign, birthday, depth, …)
    LiftMap   : (base_point, scalar) → (x, y, z)

A LiftMap is the gauge: it decides what height *means*. The canonical lifts
(the hyperboloid model) and the gauge lifts (Fiedler-as-height) are the SAME
interface — they differ only in whether z is fixed by the mathematics or chosen
by us. Each LiftMap carries `.label` (shown on the figure) and `.gauge`
(True = a chosen convention, False = forced by the math), so "pick + label it"
is automatic.

Recursion: a figure picks (base, scalar, liftmap); the liftmap's own either/or
(cartesian vs radial vs model-embedding) is itself dissolved into this one
LiftMap type. Same move, one level down.
"""

from __future__ import annotations

import numpy as np
# matplotlib is imported lazily inside the drawing helpers (shade_surface) so the
# pure-numpy LiftMaps can be imported under Blender's Python, which has no
# matplotlib. See shade_surface.

# --------------------------------------------------------------------------
# LiftMaps — (P: (N,2|3) array, s: (N,) scalar) -> (N,3) array
# --------------------------------------------------------------------------


def _mk(fn, label, gauge):
    fn.label = label
    fn.gauge = gauge
    return fn


def cartesian(scale=1.0):
    """z = scale · scalar.  The plain height-field / heightmap (gauge)."""
    def lift(P, s):
        P = np.asarray(P, float)
        s = np.asarray(s, float)
        return np.column_stack([P[:, 0], P[:, 1], scale * s])
    return _mk(lift, f"z = scalar  (cartesian ×{scale:g})", True)


def radial(amount=1.0):
    """Displace each base point outward along its own direction by amount·scalar.

    For a base that already lives in 3D (e.g. the permutohedron) this is a
    "breathing" deformation; the polyhedron swells where the scalar is large.
    (gauge)
    """
    def lift(P, s):
        P = np.asarray(P, float)
        if P.shape[1] == 2:
            P = np.column_stack([P, np.zeros(len(P))])
        s = np.asarray(s, float)
        n = np.linalg.norm(P, axis=1, keepdims=True)
        n[n == 0] = 1.0
        return P + amount * s[:, None] * (P / n)
    return _mk(lift, f"radial displacement by scalar  (×{amount:g})", True)


def tower(gap=1.0):
    """z = gap · scalar, but the scalar is a discrete level — a stacked tower.

    Same arithmetic as cartesian; named separately because the intent (a
    layered tower indexed by an integer level) is different. (gauge — the gap is
    a convention, the ordering is not.)
    """
    def lift(P, s):
        P = np.asarray(P, float)
        s = np.asarray(s, float)
        return np.column_stack([P[:, 0], P[:, 1], gap * s])
    return _mk(lift, f"z = level  (tower, gap {gap:g})", True)


def disk_height(scale=1.0):
    """Keep the Poincaré-disk (x,y); raise z by the hyperbolic distance ρ.

    ρ = 2·artanh(r) is the hyperbolic distance from the centre — an isometry
    invariant — so concentric rings of the {7,3} tiling rise by equal steps: a
    clean tessellated funnel. The base (x,y) staying the disk is a presentation
    choice; the height itself is metric, not arbitrary. (semi-canonical)
    """
    def lift(P, s=None):
        P = np.asarray(P, float)
        r = np.clip(np.hypot(P[:, 0], P[:, 1]), 0, 0.999999)
        return np.column_stack([P[:, 0], P[:, 1], scale * 2 * np.arctanh(r)])
    return _mk(lift, "z = hyperbolic distance ρ  (Poincaré-disk base)", False)


def hyperboloid(r_max=0.92):
    """Lift a Poincaré-disk point to the upper hyperboloid (Minkowski model).

    z is NOT chosen — it is fixed by the hyperbolic metric: a disk point at
    Euclidean radius r sits at hyperbolic distance ρ = 2·artanh(r), and the
    hyperboloid embedding is (sinh ρ·cosθ, sinh ρ·sinθ, cosh ρ). The scalar
    argument is ignored. (canonical — gauge = False)

    Points past r_max (near the ideal boundary, where z→∞) should be dropped by
    the caller; `keep(P)` returns the boolean mask.
    """
    def lift(P, s=None):
        P = np.asarray(P, float)
        x, y = P[:, 0], P[:, 1]
        r = np.hypot(x, y)
        r = np.clip(r, 0, 0.999999)
        rho = 2 * np.arctanh(r)
        theta = np.arctan2(y, x)
        return np.column_stack([np.sinh(rho) * np.cos(theta),
                                np.sinh(rho) * np.sin(theta),
                                np.cosh(rho)])
    lift.keep = lambda P: np.hypot(np.asarray(P)[:, 0], np.asarray(P)[:, 1]) <= r_max
    return _mk(lift, "hyperboloid (Minkowski model) — z fixed by the metric", False)


# --------------------------------------------------------------------------
# Drawing helpers
# --------------------------------------------------------------------------


def setup_axes(ax, title=None):
    ax.set_box_aspect((1, 1, 0.7))
    ax.set_axis_off()
    if title:
        ax.set_title(title, pad=6)


# --------------------------------------------------------------------------
# Depth cues — lighting, drop-shadows, translucent panes ("qlight + vis")
# --------------------------------------------------------------------------


def style_3d(ax, persp=True, panes_transparent=True):
    """Perspective projection + see-through axis panes so nothing is occluded."""
    if persp:
        try:
            ax.set_proj_type("persp")
        except Exception:
            pass
    if panes_transparent:
        for a in (ax.xaxis, ax.yaxis, ax.zaxis):
            try:
                a.set_pane_color((1.0, 1.0, 1.0, 0.0))
            except Exception:
                pass
            try:
                a.line.set_color((0, 0, 0, 0.15))
            except Exception:
                pass


def floor_plane(ax, z=0.0, color="#e8e8e8", alpha=0.30, grid=True):
    """A translucent reference floor at height z spanning the current xy box."""
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    xl, yl = ax.get_xlim(), ax.get_ylim()
    verts = [[(xl[0], yl[0], z), (xl[1], yl[0], z),
              (xl[1], yl[1], z), (xl[0], yl[1], z)]]
    ax.add_collection3d(Poly3DCollection(verts, facecolor=color, alpha=alpha,
                                         edgecolor="none", zorder=-20))


def floor_shadow(ax, coords3, z=None, color="#000000", alpha=0.13, size=70):
    """Project points straight down onto the floor as soft shadows (depth cue)."""
    coords3 = np.asarray(coords3, float)
    if z is None:
        z = ax.get_zlim()[0]
    ax.scatter(coords3[:, 0], coords3[:, 1], np.full(len(coords3), z),
               c=color, alpha=alpha, s=size, edgecolors="none",
               depthshade=False, zorder=-10)


def shade_surface(ax, Z, cmap="viridis", azdeg=315, altdeg=45, vert_exag=1.0,
                  extent=None, alpha=1.0, blend_mode="soft", color_by=None,
                  diverging=False):
    """plot_surface with a directional LightSource — hillshaded, reads as relief.

    color_by: if given, colour the surface by this field (e.g. a signed phase)
    while the height stays Z — so a non-negative |amplitude| surface can still
    show sign as colour. diverging: symmetric colour norm centred at 0.
    """
    import matplotlib as mpl
    from matplotlib.colors import LightSource, Normalize
    Z = np.asarray(Z, float)
    ny, nx = Z.shape
    if extent is None:
        X, Y = np.meshgrid(np.arange(nx), np.arange(ny))
    else:
        x0, x1, y0, y1 = extent
        X, Y = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
    ls = LightSource(azdeg, altdeg)
    cm = mpl.colormaps[cmap] if isinstance(cmap, str) else cmap
    src = Z if color_by is None else np.asarray(color_by, float)
    if diverging:
        a = max(abs(src.min()), abs(src.max())) or 1.0
        norm = Normalize(-a, a)
    else:
        norm = Normalize(src.min(), src.max()) if src.max() > src.min() else None
    if color_by is None:
        rgb = ls.shade(Z, cmap=cm, norm=norm, vert_exag=vert_exag, blend_mode=blend_mode)
        rgb[..., 3] = alpha
        facecolors = rgb
    else:
        base = cm(norm(src))[..., :3]
        rgb = ls.shade_rgb(base, Z, vert_exag=vert_exag, blend_mode=blend_mode)
        facecolors = np.concatenate([rgb, np.full(Z.shape + (1,), alpha)], axis=-1)
    return ax.plot_surface(X, Y, Z, facecolors=facecolors, linewidth=0,
                           antialiased=True, shade=False, rstride=1, cstride=1)


def _project_to_plane(P, plane_pt, normal, light):
    """Project points P (…,3) onto a plane along the light travel direction."""
    P = np.asarray(P, float)
    N = np.asarray(normal, float)
    L = np.asarray(light, float)
    denom = L @ N
    if abs(denom) < 1e-9:
        return None
    t = ((np.asarray(plane_pt, float) - P) @ N) / denom
    return P + t[..., None] * L


def diegetic_box(ax, light=(0.45, 0.55, -0.75), wall_color="#d9d9d9",
                 wall_alpha=0.95, shadow_polys=None, shadow_points=None,
                 shadow_alpha=0.16, walls=("floor", "back", "left")):
    """Replace the abstract axis panes with real, lit box geometry.

    Builds a corner diorama (floor + two back walls) as Poly3DCollections that
    z-sort with the object — so the object sits *inside* the box, occludes the
    walls, and (via projective shadows) casts onto floor and walls. The axis
    markup stops floating and becomes part of the rendered space.

    Pass the object's polygons (shadow_polys: list of (N,3)) and/or node points
    (shadow_points: (M,3)); they are projected along `light` onto each wall.
    """
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import matplotlib.colors as mcolors

    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); z0, z1 = ax.get_zlim()
    L = np.asarray(light, float); L = L / np.linalg.norm(L)

    plane = {
        "floor": (np.array([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]),
                  (0.0, 0.0, 1.0), (0.0, 0.0, z0)),
        "back":  (np.array([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]),
                  (0.0, -1.0, 0.0), (0.0, y1, 0.0)),
        "left":  (np.array([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)]),
                  (1.0, 0.0, 0.0), (x0, 0.0, 0.0)),
    }
    base = mcolors.to_rgba(wall_color, wall_alpha)
    quads = [plane[w][0] for w in walls]
    lit = light_polys(quads, [base] * len(quads), light=-L, ambient=0.5)
    ax.add_collection3d(Poly3DCollection(quads, facecolors=lit,
                                         edgecolors="#b0b0b0", linewidths=0.8,
                                         zorder=-50))

    def _inbounds(pts, w):
        if w == "floor":
            return ((pts[:, 0] >= x0) & (pts[:, 0] <= x1) &
                    (pts[:, 1] >= y0) & (pts[:, 1] <= y1))
        if w == "back":
            return ((pts[:, 0] >= x0) & (pts[:, 0] <= x1) &
                    (pts[:, 2] >= z0) & (pts[:, 2] <= z1))
        return ((pts[:, 1] >= y0) & (pts[:, 1] <= y1) &
                (pts[:, 2] >= z0) & (pts[:, 2] <= z1))

    for w in walls:
        _, N, pt = plane[w]
        if shadow_polys:
            sh = [pr for poly in shadow_polys
                  if (pr := _project_to_plane(poly, pt, N, L)) is not None
                  and _inbounds(pr, w).all()]
            if sh:
                ax.add_collection3d(Poly3DCollection(
                    sh, facecolors=(0, 0, 0, shadow_alpha), edgecolors="none",
                    zorder=-40))
        if shadow_points is not None and len(shadow_points):
            pr = _project_to_plane(np.asarray(shadow_points, float), pt, N, L)
            if pr is not None:
                keep = pr[_inbounds(pr, w)]
                if len(keep):
                    ax.scatter(keep[:, 0], keep[:, 1], keep[:, 2],
                               c=(0, 0, 0, shadow_alpha), s=70, edgecolors="none",
                               depthshade=False, zorder=-40)

    style_3d(ax, persp=True, panes_transparent=True)


def light_polys(polys, base_rgba, light=(0.4, 0.25, 0.9), ambient=0.5):
    """Shade a list of 3D polygons by face normal · light direction.

    Turns a flat Poly3DCollection ("unlit") into a directionally-lit surface.
    abs() of the dot so both winding orientations are lit consistently.
    """
    light = np.asarray(light, float)
    light = light / np.linalg.norm(light)
    out = []
    for poly, col in zip(polys, base_rgba):
        v = np.asarray(poly, float)
        n = np.cross(v[1] - v[0], v[2] - v[0])
        ln = np.linalg.norm(n)
        b = ambient if ln < 1e-12 else ambient + (1 - ambient) * abs((n / ln) @ light)
        r, g, bl = col[:3]
        a = col[3] if len(col) > 3 else 1.0
        out.append((r * b, g * b, bl * b, a))
    return out


def draw_graph(ax, coords3, edges, node_color="#0072B2", node_size=120,
               edge_color="#bbbbbb", edge_lw=1.2, labels=None, label_size=7,
               cmap=None, depthshade=False):
    """Draw a lifted graph: coords3 is an (N,3) array, edges a list of (i,j)."""
    coords3 = np.asarray(coords3, float)
    # Edges first (behind nodes).
    if isinstance(edge_color, (list, np.ndarray)):
        for (i, j), col in zip(edges, edge_color):
            ax.plot(*zip(coords3[i], coords3[j]), color=col, lw=edge_lw, alpha=0.8)
    else:
        for i, j in edges:
            ax.plot(*zip(coords3[i], coords3[j]), color=edge_color, lw=edge_lw,
                    alpha=0.7)
    sc = ax.scatter(coords3[:, 0], coords3[:, 1], coords3[:, 2],
                    c=node_color, cmap=cmap, s=node_size, depthshade=depthshade,
                    edgecolors="#222222", linewidths=0.8, zorder=5)
    if labels:
        for (x, y, z), txt in zip(coords3, labels):
            ax.text(x, y, z, txt, fontsize=label_size, ha="center", va="center")
    return sc


def height_surface(ax, Z, cmap="viridis", stride=1, edgecolor="none",
                   alpha=1.0, extent=None):
    """Plot a 2D array Z as a 3D surface over its integer grid."""
    Z = np.asarray(Z, float)
    ny, nx = Z.shape
    if extent is None:
        X, Y = np.meshgrid(np.arange(nx), np.arange(ny))
    else:
        x0, x1, y0, y1 = extent
        X, Y = np.meshgrid(np.linspace(x0, x1, nx), np.linspace(y0, y1, ny))
    return ax.plot_surface(X, Y, Z, cmap=cmap, rstride=stride, cstride=stride,
                           edgecolor=edgecolor, linewidth=0.2, alpha=alpha,
                           antialiased=True)


def signed_bars(ax, heights, signs, pos_color="#D55E00", neg_color="#0072B2"):
    """3D bars rising from the z = 0 floor; height = |heights|, colour = sign.

    Keeping every bar above 0 means the axis-box floor sits flush at z = 0; the
    sign lives in colour (red +, blue −) rather than in downward bars.
    """
    heights = np.asarray(heights, float)
    signs = np.asarray(signs)
    ny, nx = heights.shape
    xs, ys, zs, dz, cols = [], [], [], [], []
    for r in range(ny):
        for c in range(nx):
            xs.append(c); ys.append(r); zs.append(0.0)
            dz.append(abs(heights[r, c]) if heights[r, c] != 0 else 1e-6)
            cols.append(pos_color if signs[r, c] >= 0 else neg_color)
    ax.bar3d(xs, ys, zs, 0.85, 0.85, dz, color=cols, edgecolor="#222222",
             linewidth=0.3, shade=True)
