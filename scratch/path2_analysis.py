"""
Path-of-length-2 analysis with neighborhood-compression.

Per user (2026-05-16): edges alone find only near-perfect code. The
real structural signal is in A² (2-paths) and the mediator-overlap.

For each (X, Y) where A²[X, Y] >= 2: there are multiple intermediates
M₁, M₂, ... mediating X→M→Y. The "cycle is trying to manifest" signal
strength is the pairwise neighborhood overlap of the mediators —
high overlap means M₁ and M₂ are doing the same role, just routed
differently. That's a unification candidate.

Hierarchical indexing via Weisfeiler-Lehman color refinement:
- Level 0: each node's color = its kind (here: just "module").
- Level k: each node's color = hash(color_{k-1}(node), sorted [color_{k-1}(neighbor)]).
- Two nodes equivalent at level k = role-isomorphic up to depth k.
- After log(N) rounds, colors stabilize. Equivalence classes = structural roles.

Outputs:
  1. Top A² cells (most-mediated 2-paths).
  2. Mediator-overlap ranking for each top cell.
  3. WL color classes — nodes that are role-equivalent.
"""

import re
import hashlib
from pathlib import Path
from collections import defaultdict, Counter

import numpy as np
from scipy.sparse import lil_matrix, csr_matrix


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


def adjacency_matrix(graph):
    nodes = sorted(graph.keys())
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    A = lil_matrix((n, n), dtype=np.int8)
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                A[idx[src], idx[dep]] = 1
    return A.tocsr(), nodes


def jaccard(set_a, set_b):
    if not set_a and not set_b:
        return 1.0
    u = set_a | set_b
    if not u:
        return 0.0
    return len(set_a & set_b) / len(u)


def main():
    graph = build_graph()
    A, nodes = adjacency_matrix(graph)
    n = len(nodes)
    print(f"Built graph: {n} modules, {A.nnz} edges")

    # Out- and in-neighborhoods.
    Adense = A.toarray().astype(int)
    out_nbr = [set(np.where(Adense[i] == 1)[0]) for i in range(n)]
    in_nbr = [set(np.where(Adense[:, i] == 1)[0]) for i in range(n)]

    # A² = paths-of-length-2.
    A2 = Adense @ Adense
    # Set diagonal to 0 (self-loops via 2-path are usually noise).
    np.fill_diagonal(A2, 0)

    short = lambda i: nodes[i].split(".")[-1]

    # === Top A² cells ===
    print("\n=== Top 2-path cells (X → M → Y count) ===")
    cells = [(A2[x, y], x, y) for x in range(n) for y in range(n) if A2[x, y] >= 2]
    cells.sort(reverse=True)
    for count, x, y in cells[:15]:
        # Find the mediators.
        mediators = sorted(out_nbr[x] & in_nbr[y])
        med_names = [short(m) for m in mediators]
        print(f"  A²={count:2d}:  {short(x):30s} ~~> {short(y):30s}")
        print(f"           via: {', '.join(med_names)}")

    # === Mediator-overlap ranking ===
    print("\n=== Mediator-overlap signal (Jaccard) per high-A² cell ===")
    print("    For each (X, Y) with multiple mediators, pairwise Jaccard")
    print("    of mediators' OUT-neighborhoods. High = M's do same role.")
    print()
    overlap_signals = []
    for count, x, y in cells:
        mediators = sorted(out_nbr[x] & in_nbr[y])
        if len(mediators) < 2:
            continue
        pair_scores = []
        for i, m1 in enumerate(mediators):
            for m2 in mediators[i+1:]:
                j = jaccard(out_nbr[m1] - {y}, out_nbr[m2] - {y})
                pair_scores.append((j, m1, m2))
        if pair_scores:
            avg_overlap = sum(s for s, _, _ in pair_scores) / len(pair_scores)
            max_overlap = max(s for s, _, _ in pair_scores)
            overlap_signals.append((max_overlap, avg_overlap, x, y, count, pair_scores))

    overlap_signals.sort(reverse=True)
    print(f"  --- Top 12 cells by max mediator-overlap ---")
    for max_o, avg_o, x, y, count, pairs in overlap_signals[:12]:
        print(f"  max={max_o:.2f} avg={avg_o:.2f} A²={count}:  "
              f"{short(x):28s} ~~> {short(y):28s}")
        top_pairs = sorted(pairs, reverse=True)[:3]
        for j, m1, m2 in top_pairs:
            print(f"      Jaccard={j:.2f}: {short(m1):28s} ⇄ {short(m2)}")

    # === Weisfeiler-Lehman color refinement ===
    print("\n=== WL color refinement (hierarchical role identification) ===")
    # Color by both in- and out-neighborhoods (capture directed structure).
    color = [0] * n  # initial: all same
    for level in range(1, 6):
        new_colors_raw = []
        for i in range(n):
            sig = (color[i],
                   tuple(sorted(color[j] for j in out_nbr[i])),
                   tuple(sorted(color[j] for j in in_nbr[i])))
            new_colors_raw.append(sig)
        # Compact to small ints.
        unique = {}
        new_color = []
        for s in new_colors_raw:
            if s not in unique:
                unique[s] = len(unique)
            new_color.append(unique[s])
        if new_color == color:
            print(f"  Stabilized at level {level} with {len(set(color))} classes.")
            break
        color = new_color
    else:
        print(f"  Reached level 5 with {len(set(color))} classes (not yet stabilized).")

    # Group nodes by final color.
    groups = defaultdict(list)
    for i, c in enumerate(color):
        groups[c].append(i)

    print()
    print("  --- WL equivalence classes (size >= 2) ---")
    for c, ns in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(ns) >= 2:
            print(f"    class {c} ({len(ns)} members):")
            for i in ns:
                print(f"      {nodes[i]}")

    # === Singletons in WL but with high mediator-overlap counterpart ===
    print("\n  --- Singletons whose closest WL neighbor has shared mediator role ---")
    print("  (Where one module is 'unique' in WL but has heavy overlap with")
    print("   another module that mediates the same 2-paths.)")
    # For each module that's a singleton, find its closest peer by neighborhood
    # Jaccard.
    singletons = [i for i, c in enumerate(color) if len(groups[c]) == 1]
    closest_peer = []
    for i in singletons:
        best_j = -1
        best_score = 0.0
        for k in range(n):
            if k == i:
                continue
            score = (jaccard(out_nbr[i], out_nbr[k]) +
                     jaccard(in_nbr[i], in_nbr[k])) / 2
            if score > best_score:
                best_score = score
                best_j = k
        if best_j >= 0 and best_score > 0.2:
            closest_peer.append((best_score, i, best_j))
    closest_peer.sort(reverse=True)
    for score, i, k in closest_peer[:10]:
        print(f"    Jaccard={score:.2f}:  {short(i):30s} ⇄ {short(k)}")


if __name__ == "__main__":
    main()
