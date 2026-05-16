"""
Voronoi/Delaunay-dual analysis of the substrate Agda dependency graph.

The Voronoi view (path2_analysis.py) gave us neighborhood Jaccard
distances. The Delaunay dual interprets those distances geometrically:
modules are vertices, edges connect vertices in adjacent Voronoi
cells (low Jaccard distance), n-simplices are (n+1)-cliques of
mutually-adjacent modules.

The simplicial complex (set of all simplices) is the SHAPE of the
codebase's structural backbone. Each maximal simplex is one
aspect-cluster; the complex's face-incidence structure records the
lift relations between aspect-clusters of different orders.

Outputs:
  1. Pairwise Jaccard similarity matrix (sorted).
  2. The Jaccard-similarity graph at multiple thresholds θ ∈ {0.5, 0.7, 0.9, 1.0}.
  3. Maximal cliques per threshold (= simplices of the Delaunay complex).
  4. Face-incidence: which simplices contain which other simplices
     as proper faces (the "bridge between orders" candidates).
"""

import re
from pathlib import Path
from collections import defaultdict
from itertools import combinations

import numpy as np
import networkx as nx


SUBSTRATE_ROOT = Path("/home/mikemol/github/substrate/agda")


def parse_module(path):
    text = path.read_text()
    m = re.search(r"^module\s+([A-Za-z0-9_.\-]+)\s+where", text, re.M)
    if not m:
        return None, []
    name = m.group(1)
    imports = re.findall(
        r"^(?:open\s+)?import\s+([A-Za-z0-9_.\-]+)", text, re.M
    )
    imports = [imp for imp in imports if imp.startswith("Substrate.")]
    return name, imports


def build_graph():
    graph = {}
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        name, imports = parse_module(path)
        if name and name.startswith("Substrate"):
            graph[name] = imports
    return graph


def jaccard(a, b):
    if not a and not b:
        return 1.0
    u = a | b
    if not u:
        return 0.0
    return len(a & b) / len(u)


def main():
    graph = build_graph()
    nodes = sorted(graph.keys())
    n = len(nodes)
    idx = {nd: i for i, nd in enumerate(nodes)}
    short = lambda i: nodes[i].split(".")[-1]

    # Build directed adjacency.
    out_nbr = [set() for _ in range(n)]
    in_nbr  = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                out_nbr[idx[src]].add(idx[dep])
                in_nbr[idx[dep]].add(idx[src])

    # Combined neighborhood signature for Jaccard: in ∪ out neighbors.
    # (We include "self" implicitly via the role of the module.)
    sig = [out_nbr[i] | in_nbr[i] for i in range(n)]

    # Pairwise Jaccard matrix.
    J = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            J[i, j] = jaccard(sig[i], sig[j])
            J[j, i] = J[i, j]

    print(f"Built Jaccard matrix on {n} modules.")
    print()

    # === Threshold sweep: at each θ, find maximal cliques ===
    thresholds = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5]
    print("=== Maximal cliques at successively lower θ (Delaunay simplices) ===")
    print()
    complexes_by_theta = {}
    for theta in thresholds:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for i in range(n):
            for j in range(i + 1, n):
                if J[i, j] >= theta:
                    G.add_edge(i, j)
        cliques = sorted(
            (sorted(c) for c in nx.find_cliques(G) if len(c) >= 2),
            key=lambda c: (-len(c), c),
        )
        complexes_by_theta[theta] = cliques
        print(f"--- θ = {theta:.2f} ({G.number_of_edges()} edges, "
              f"{len(cliques)} non-trivial maximal cliques) ---")
        for c in cliques[:15]:
            dim = len(c) - 1
            names = ", ".join(short(i) for i in c)
            print(f"  {dim}-simplex ({len(c)} verts):  {{{names}}}")
        if len(cliques) > 15:
            print(f"  ... and {len(cliques) - 15} more.")
        print()

    # === Face-incidence: simplices at higher θ ⊆ simplices at lower θ ===
    # (Higher θ = stricter similarity; cliques are smaller. As θ falls,
    # cliques grow. Faces of large cliques are themselves cliques.)
    print("=== Face-incidence (bridge candidates) ===")
    print("  A k-simplex S at θ₁ is a FACE of an l-simplex T at θ₂ < θ₁")
    print("  if vertices(S) ⊂ vertices(T). The 'bridge across orders'")
    print("  is the inclusion S ↪ T.")
    print()

    # For each pair (high-θ clique, low-θ clique), check subset.
    # Focus on θ=1.0 cliques as faces of larger θ=0.7 cliques.
    high_simplices = complexes_by_theta[1.0]
    print(f"Looking at θ=1.0 simplices ({len(high_simplices)} found) embedded in θ=0.7 simplices:")
    print()
    for high in high_simplices:
        high_set = set(high)
        names_h = "{" + ", ".join(short(i) for i in high) + "}"
        # Find proper supersets at lower theta.
        bridges = []
        for theta_low in [0.9, 0.8, 0.7, 0.6, 0.5]:
            for low in complexes_by_theta[theta_low]:
                if high_set < set(low):
                    bridges.append((theta_low, low))
            if bridges:
                break
        if bridges:
            theta_low, low = bridges[0]
            names_l = "{" + ", ".join(short(i) for i in low) + "}"
            extra = set(low) - high_set
            print(f"  {len(high)-1}-simplex {names_h}")
            print(f"    bridges UP to {len(low)-1}-simplex {names_l}  at θ={theta_low}")
            print(f"    adding vertices: {{{', '.join(short(i) for i in sorted(extra))}}}")
            print()
        else:
            print(f"  {len(high)-1}-simplex {names_h} is MAXIMAL (no proper superset clique)")
            print()

    # === The "Stab-S3-* family" check: is it really a 4-simplex? ===
    print("=== Stab-S3-* family: is it a 4-simplex at any threshold? ===")
    stab_modules = [i for i, n in enumerate(nodes) if "Stab-S3" in n]
    print(f"  Stab-S3-* modules: {[short(i) for i in stab_modules]}")
    print(f"  Pairwise Jaccard within family:")
    for i, a in enumerate(stab_modules):
        for b in stab_modules[i+1:]:
            print(f"    {short(a):30s} ⇄ {short(b):30s}  J={J[a, b]:.2f}")
    min_j = min(J[a, b] for i, a in enumerate(stab_modules) for b in stab_modules[i+1:])
    print(f"  Minimum within-family Jaccard: {min_j:.2f}")
    print(f"  → forms a 4-simplex at any θ ≤ {min_j:.2f}")
    print()

    # === The (V4-Embedding, SemidirectProduct, V4-Normality) triangle ===
    print("=== V4-Embedding/SemidirectProduct/V4-Normality triangle ===")
    triangle_names = ["Substrate.Groups.V4-Embedding",
                      "Substrate.Groups.SemidirectProduct",
                      "Substrate.Groups.V4-Normality"]
    triangle = [idx[m] for m in triangle_names if m in idx]
    for i, a in enumerate(triangle):
        for b in triangle[i+1:]:
            print(f"    {short(a):30s} ⇄ {short(b):30s}  J={J[a, b]:.2f}")
    min_j = min(J[a, b] for i, a in enumerate(triangle) for b in triangle[i+1:])
    print(f"  Minimum within-triangle Jaccard: {min_j:.2f}")
    print(f"  → forms a 2-simplex (triangle) at any θ ≤ {min_j:.2f}")
    print()

    # === Cross-cluster bridge: triangle <-> Stab-S3-* ===
    print("=== Bridge: triangle <-> Stab-S3-* family ===")
    print("  Pairwise Jaccard between triangle and Stab-S3-* family:")
    bridge_pairs = []
    for a in triangle:
        for b in stab_modules:
            bridge_pairs.append((J[a, b], a, b))
    bridge_pairs.sort(reverse=True)
    for j, a, b in bridge_pairs:
        print(f"    {short(a):30s} <-> {short(b):30s}  J={j:.2f}")
    print()


if __name__ == "__main__":
    main()
