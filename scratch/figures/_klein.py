"""{7,3} hyperbolic tiling geometry — shared by the 2D and 3D Klein figures.

Generates the order-3 heptagonal tiling of the Poincaré disk by reflecting a
central regular heptagon across its edges (each reflection = inversion in the
geodesic circle). Returns the tiles; the figures decide how to draw them (flat
in the disk, or lifted onto the hyperboloid).
"""

import math

import numpy as np

P, Q = 7, 3  # {7,3}

# Hyperbolic circumradius as a Euclidean radius in the disk.
_coshR = math.cos(math.pi / Q) / math.sin(math.pi / P)
R = math.acosh(_coshR)
R_VERT = math.tanh(R / 2)


def central_heptagon():
    return [
        (R_VERT * math.cos(2 * math.pi * k / P + math.pi / 2),
         R_VERT * math.sin(2 * math.pi * k / P + math.pi / 2))
        for k in range(P)
    ]


def geodesic_circle(a, b):
    """Centre/radius of the circle through a,b orthogonal to the unit circle,
    or None if it degenerates to a diameter."""
    ax_, ay = a
    bx, by = b
    A = np.array([[ax_, ay], [bx, by]], dtype=float)
    rhs = 0.5 * np.array([ax_ * ax_ + ay * ay + 1, bx * bx + by * by + 1])
    if abs(np.linalg.det(A)) < 1e-12:
        return None
    c = np.linalg.solve(A, rhs)
    rho2 = c[0] * c[0] + c[1] * c[1] - 1
    if rho2 <= 1e-12:
        return None
    return c, math.sqrt(rho2)


def _invert(z, c, rho):
    d = z - c
    s = rho * rho / (d[0] * d[0] + d[1] * d[1])
    return c + s * d


def reflect_tile(tile, a, b):
    gc = geodesic_circle(a, b)
    out = []
    if gc is None:
        d = np.array(b) - np.array(a)
        d = d / np.linalg.norm(d)
        for v in tile:
            v = np.array(v)
            out.append(tuple(2 * (v @ d) * d - v))
        return out
    c, rho = gc
    for v in tile:
        out.append(tuple(_invert(np.array(v, dtype=float), c, rho)))
    return out


def arc_points(a, b, n=24):
    """Sample points along the hyperbolic geodesic from a to b (for 2D drawing)."""
    gc = geodesic_circle(a, b)
    if gc is None:
        return np.linspace(a, b, n)
    c, rho = gc
    t0 = math.atan2(a[1] - c[1], a[0] - c[0])
    t1 = math.atan2(b[1] - c[1], b[0] - c[0])
    if t1 - t0 > math.pi:
        t1 -= 2 * math.pi
    elif t0 - t1 > math.pi:
        t1 += 2 * math.pi
    ts = np.linspace(t0, t1, n)
    return np.column_stack([c[0] + rho * np.cos(ts), c[1] + rho * np.sin(ts)])


def _key(tile):
    cx = sum(v[0] for v in tile) / P
    cy = sum(v[1] for v in tile) / P
    return (round(cx, 3), round(cy, 3))


def generate_tiling(depth=8, max_tiles=1400):
    """BFS-reflect the central heptagon to fill the disk. Returns (tiles, depth_of)."""
    central = central_heptagon()
    tiles = [central]
    seen = {_key(central): 0}
    frontier = [(central, 0)]
    while frontier and len(tiles) < max_tiles:
        tile, d = frontier.pop(0)
        if d >= depth:
            continue
        for i in range(P):
            a, b = tile[i], tile[(i + 1) % P]
            nb = reflect_tile(tile, a, b)
            if max(math.hypot(*v) for v in nb) > 0.999:
                continue
            k = _key(nb)
            if k in seen:
                continue
            seen[k] = d + 1
            tiles.append(nb)
            frontier.append((nb, d + 1))
    return tiles, seen


def centroid(tile):
    return (sum(v[0] for v in tile) / P, sum(v[1] for v in tile) / P)
