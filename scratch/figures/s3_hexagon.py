#!/usr/bin/env python3
"""The S₃ Cayley graph as a hexagon, with the braid relation highlighted.

S₃ = ⟨s₁, s₂ | s₁² = s₂² = (s₁s₂)³ = e⟩ — the adjacent transpositions
s₁ = (1 2), s₂ = (2 3) on (1,2,3). Their Cayley graph is a 6-cycle whose
edges alternate generator. The two length-3 geodesics from e to the longest
element w₀ = (3,2,1) realise the braid relation s₁s₂s₁ = s₂s₁s₂.

Mirrors the Coxeter A₂ relation verified in
    agda/Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations.agda
"""

import math

from _gallery import PALETTE, finish, make_parser, set_style

args = make_parser("s3_hexagon").parse_args()
set_style()

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from matplotlib.lines import Line2D

S1, S2 = "s₁", "s₂"


def swap(state, i, j):
    lst = list(state)
    lst[i], lst[j] = lst[j], lst[i]
    return tuple(lst)


def apply(state, gen):
    return swap(state, 0, 1) if gen == S1 else swap(state, 1, 2)


# Shortlex BFS from the identity to label each of the 6 group elements.
origin = (1, 2, 3)
words = {origin: ""}
queue = [origin]
edges = []  # (u, v, generator)
seen_edges = set()
while queue:
    cur = queue.pop(0)
    for gen in (S1, S2):
        nxt = apply(cur, gen)
        if nxt not in words:
            words[nxt] = words[cur] + gen
            queue.append(nxt)
        key = frozenset((cur, nxt))
        if key not in seen_edges:
            seen_edges.add(key)
            edges.append((cur, nxt, gen))

# Order the 6 elements around the hexagon by walking the 6-cycle from e.
order = [origin]
prev = None
cur = origin
while len(order) < 6:
    for u, v, _ in edges:
        nbr = v if u == cur else (u if v == cur else None)
        if nbr is not None and nbr != prev:
            order.append(nbr)
            prev, cur = cur, nbr
            break

POS = {}
for k, elt in enumerate(order):
    ang = math.pi / 2 + k * math.pi / 3  # start at top, go counter-clockwise
    POS[elt] = (math.cos(ang), math.sin(ang))

w0 = (3, 2, 1)  # longest element

fig, ax = plt.subplots(figsize=(8.5, 8.5))
ax.set_aspect("equal")
ax.axis("off")
ax.set_xlim(-1.55, 1.55)
ax.set_ylim(-1.5, 1.6)

gen_color = {S1: PALETTE[0], S2: PALETTE[1]}

# Edges, coloured by generator.
for u, v, gen in edges:
    (x0, y0), (x1, y1) = POS[u], POS[v]
    ax.plot([x0, x1], [y0, y1], color=gen_color[gen], lw=4.0, zorder=2,
            solid_capstyle="round")

# Braid geodesics e → w₀: s₁s₂s₁ (one way) and s₂s₁s₂ (the other).
def geodesic(first):
    path, cur = [origin], origin
    for gen in ([S1, S2, S1] if first == S1 else [S2, S1, S2]):
        cur = apply(cur, gen)
        path.append(cur)
    return path

for first, rad, col in ((S1, 0.0, "#222222"), (S2, 0.0, "#222222")):
    pass  # geodesics already coincide with hexagon edges; annotate via arrows.

# Directed arrows tracing s₁s₂s₁ and s₂s₁s₂ as the two half-loops.
for first, rad in ((S1, 0.30), (S2, -0.30)):
    path = geodesic(first)
    for a, b in zip(path, path[1:]):
        (x0, y0), (x1, y1) = POS[a], POS[b]
        ax.add_patch(FancyArrowPatch(
            (x0, y0), (x1, y1), connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>", mutation_scale=18, lw=2.0,
            color="#333333", zorder=4, shrinkA=20, shrinkB=20, alpha=0.8))

# Nodes.
for elt, (x, y) in POS.items():
    is_special = elt in (origin, w0)
    ax.scatter([x], [y], s=900, zorder=5, color="white",
               edgecolors=("#D55E00" if is_special else "#222222"),
               linewidths=(2.6 if is_special else 1.4))
    label = "e" if elt == origin else words[elt]
    ax.text(x, y, label, ha="center", va="center", fontsize=13,
            fontweight="bold", zorder=6)
    ax.text(x * 1.32, y * 1.32, str(elt), ha="center", va="center",
            fontsize=9, color="#777777", zorder=6)

legend = [
    Line2D([0], [0], color=gen_color[S1], lw=4, label="s₁ = (1 2)"),
    Line2D([0], [0], color=gen_color[S2], lw=4, label="s₂ = (2 3)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="white",
           markeredgecolor="#D55E00", markersize=14, lw=0,
           label="e  and  w₀ = (3,2,1)"),
]
ax.legend(handles=legend, loc="lower center", ncol=3, frameon=False,
          bbox_to_anchor=(0.5, -0.02), fontsize=11)
ax.set_title("S₃ Cayley graph  —  braid relation  s₁s₂s₁ = s₂s₁s₂ = w₀", pad=16)

finish(fig, "s3_hexagon", args)
