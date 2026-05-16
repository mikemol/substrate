"""
Module-level naturality-square detector for the substrate Agda codebase.

Reframing (per user, 2026-05-16): instead of writing proofs locally,
analyze the codebase's dependency graph for places where commutative
2-paths are "trying to manifest". The procedure:

1. Build module-level dependency graph (nodes = .agda files, edges = imports).
2. Apply Cuthill-McKee reordering to band the symmetrized adjacency matrix.
3. Fold the permuted matrix into quadrants — cross-quadrant edges are
   candidates for naturality squares (they don't fit the natural band).
4. Hough-style voting: enumerate 4-tuples (A, B, C, D) where A→B, A→C
   and B→D exist (or all four). The "missing corner" cases are squares
   "trying to manifest" — places where the codebase has 3 edges but
   the 4th would complete a commutative square.
"""

import re
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.csgraph import reverse_cuthill_mckee


SUBSTRATE_ROOT = Path("/home/mikemol/github/substrate/agda")


def parse_module(path: Path):
    """Extract (module_name, [imported_module]) from an Agda file."""
    text = path.read_text()
    module_match = re.search(r"^module\s+([A-Za-z0-9_.\-]+)\s+where", text, re.M)
    if not module_match:
        return None, []
    module_name = module_match.group(1)
    imports = re.findall(
        r"^(?:open\s+)?import\s+([A-Za-z0-9_.\-]+)", text, re.M
    )
    # Only keep Substrate.* imports (the rest are stdlib, not part of our graph)
    imports = [imp for imp in imports if imp.startswith("Substrate.")]
    return module_name, imports


def build_graph():
    """Walk SUBSTRATE_ROOT and build {module: [deps]} dict."""
    graph = {}
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        name, imports = parse_module(path)
        if name and name.startswith("Substrate"):
            graph[name] = imports
    return graph


def adjacency_matrix(graph):
    """Build sparse adjacency matrix. Returns (matrix, node_list)."""
    nodes = sorted(graph.keys())
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    A = lil_matrix((n, n), dtype=np.int8)
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                A[idx[src], idx[dep]] = 1
    return A.tocsr(), nodes


def symmetric(A):
    """Symmetric closure: A_sym[i,j] = max(A[i,j], A[j,i])."""
    return ((A + A.T) > 0).astype(np.int8)


def cm_reorder(A_sym):
    """Apply reverse Cuthill-McKee, return permutation."""
    return list(reverse_cuthill_mckee(A_sym))


def fold_quadrants(A_perm):
    """Split the NxN matrix into 4 quadrants and return their nnz counts."""
    n = A_perm.shape[0]
    mid = n // 2
    Q11 = A_perm[:mid, :mid].nnz
    Q12 = A_perm[:mid, mid:].nnz
    Q21 = A_perm[mid:, :mid].nnz
    Q22 = A_perm[mid:, mid:].nnz
    return (Q11, Q12, Q21, Q22), mid


def missing_corner_squares(A, nodes):
    """
    Find 4-tuples (A, B, C, D) where 3 of the 4 directed edges of the
    commutative square exist:

        A -e1-> B
        |       |
        e2     e3
        v       v
        C -e4-> D

    Square edges: A→B, A→C, B→D, C→D. The diagonal A→D is *not* an edge
    of the square — we'll filter for cases where A→D doesn't exist either
    (otherwise the square is just shadow of a triangle).

    Returns list of (missing_edge, A, B, C, D) tuples.
    """
    n = A.shape[0]
    Adense = A.toarray()
    candidates = []

    # Enumerate A and D (the source and sink of the square)
    for a in range(n):
        successors_a = set(np.where(Adense[a] == 1)[0])
        for d in range(n):
            if a == d:
                continue
            predecessors_d = set(np.where(Adense[:, d] == 1)[0])
            # Middle nodes: nodes M with A→M AND M→D
            middles = successors_a & predecessors_d
            if len(middles) < 2:
                continue
            # Pick all pairs (B, C) — each gives a full square (4 edges)
            middles_list = sorted(middles)
            for i, b in enumerate(middles_list):
                for c in middles_list[i+1:]:
                    # Full square — both paths A→B→D and A→C→D exist
                    candidates.append(("full", a, b, c, d))

    # Now find missing-corner cases: A→B, A→C, B→D exist, but C→D doesn't
    # (or symmetric)
    for a in range(n):
        successors_a = sorted(np.where(Adense[a] == 1)[0])
        for i, b in enumerate(successors_a):
            successors_b = set(np.where(Adense[b] == 1)[0])
            for c in successors_a[i+1:]:
                successors_c = set(np.where(Adense[c] == 1)[0])
                # Common downstream targets
                shared_targets = successors_b & successors_c
                # B-only targets where C→D is missing
                b_only = successors_b - successors_c - {c, a}
                c_only = successors_c - successors_b - {b, a}
                for d in b_only:
                    if d in (a, b, c):
                        continue
                    candidates.append(("missing-C->D", a, b, c, d))
                for d in c_only:
                    if d in (a, b, c):
                        continue
                    candidates.append(("missing-B->D", a, b, c, d))

    return candidates


def print_matrix_ascii(A, nodes, perm=None, abbrev_len=22):
    """Print a small ASCII visualization of the matrix."""
    n = A.shape[0]
    if perm is None:
        perm = list(range(n))
    A_perm = A[perm, :][:, perm]
    Adense = A_perm.toarray()
    print()
    print(" " * (abbrev_len + 1) + "".join(f"{i%10}" for i in range(n)))
    for i in range(n):
        row = "".join("X" if Adense[i, j] else "." for j in range(n))
        label = nodes[perm[i]][-abbrev_len:].rjust(abbrev_len)
        print(f"{label} {row}")


def main():
    print("Building dependency graph...")
    graph = build_graph()
    print(f"  Found {len(graph)} modules")

    A, nodes = adjacency_matrix(graph)
    print(f"  Adjacency matrix: {A.shape[0]}x{A.shape[1]}, nnz = {A.nnz}")

    A_sym = symmetric(A)
    perm = cm_reorder(A_sym)
    print(f"  Cuthill-McKee permutation computed")

    print("\n=== CM-ordered modules ===")
    for i, p in enumerate(perm):
        print(f"  {i:3d}  {nodes[p]}")

    print("\n=== ASCII adjacency (CM order, directed) ===")
    print_matrix_ascii(A, nodes, perm)

    print("\n=== Quadrant fold (CM order, directed) ===")
    A_perm = A[perm, :][:, perm]
    (Q11, Q12, Q21, Q22), mid = fold_quadrants(A_perm)
    print(f"  Split at row/col {mid} ({nodes[perm[mid-1]]} | {nodes[perm[mid]]})")
    print(f"  Q11 (top-left,    upper × upper) : {Q11} edges")
    print(f"  Q12 (top-right,   upper × lower) : {Q12} edges  <-- cross-quadrant")
    print(f"  Q21 (bottom-left, lower × upper) : {Q21} edges  <-- cross-quadrant")
    print(f"  Q22 (bottom-right,lower × lower) : {Q22} edges")
    print(f"  Total cross-quadrant: {Q12 + Q21} / {A.nnz} ({100*(Q12+Q21)/A.nnz:.0f}%)")

    print("\n=== Missing-corner naturality squares ===")
    cands = missing_corner_squares(A, nodes)
    fulls = [c for c in cands if c[0] == "full"]
    missing = [c for c in cands if c[0] != "full"]
    print(f"  Full squares (4 edges, commuting candidates): {len(fulls)}")
    print(f"  Missing-corner squares (3-of-4 edges):        {len(missing)}")

    # Hough-style voting: each missing-corner square votes for the
    # missing edge. Aggregate votes by (source, target).
    print("\n=== Hough vote: which missing edges are most suggested? ===")
    vote = defaultdict(list)
    for kind, a, b, c, d in missing:
        if kind == "missing-C->D":
            # C->D missing. Square: A->B, A->C, B->D, [C->D missing]
            vote[(c, d)].append((a, b))
        elif kind == "missing-B->D":
            # B->D missing. Square: A->B, A->C, [B->D missing], C->D
            vote[(b, d)].append((a, c))
    ranked = sorted(vote.items(), key=lambda kv: -len(kv[1]))
    print(f"  --- Top 15 most-voted-for missing edges ---")
    short = lambda n: nodes[n].split(".")[-1]
    for (src, tgt), supporters in ranked[:15]:
        print(f"    {len(supporters):3d} votes:  {short(src):28s} ->X  {short(tgt):28s}")
        if len(supporters) >= 3:
            sample = supporters[:3]
            print(f"             via parallel paths through: " +
                  ", ".join(f"({short(a)}, {short(b)})" for a, b in sample))

    # Asymmetry detection: find edges that go "backwards" relative to CM order,
    # i.e., cross-quadrant in the Q21 region. These edges are NOT typological
    # backward (that'd be a cycle — impossible in Agda), but they are
    # "off-band" — they connect distant parts of the dependency lattice.
    print("\n=== Off-band edges (Q21, lower-left quadrant) ===")
    print(f"  --- These connect modules far apart in CM order. ---")
    A_perm = A[perm, :][:, perm]
    Adense_perm = A_perm.toarray()
    n = A.shape[0]
    mid = n // 2
    off_band = []
    for i in range(mid, n):
        for j in range(mid):
            if Adense_perm[i, j]:
                off_band.append((perm[i], perm[j], i - j))
    off_band.sort(key=lambda x: -x[2])
    for src, tgt, dist in off_band:
        print(f"    distance {dist:2d}:  {short(src):28s} -> {short(tgt):28s}")


if __name__ == "__main__":
    main()
