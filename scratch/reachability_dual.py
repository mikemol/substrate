"""
Reachability-based (top-down) analysis, dual to the local-similarity
(bottom-up) pass in path2_analysis.py / simplicial_shape.py.

Per the user's homology/cohomology framing (2026-05-16):
  - Local observations (Jaccard on direct neighborhoods) = homology.
    What we SEE directly in the graph.
  - Reachability / common-base analysis = a step toward cohomology.
    What CONNECTS observations via shared substructure.
  - Catalog claims (theorems) = full cohomology.
    Gauge-invariant functions on cycles. (Not computed here; see N.)

Per [[feedback-lem-in-graph-analysis]]: absence of direct edge ≠
disconnection. Two modules with disjoint direct neighborhoods may
share an extensive common base (reaching the same global primitives)
which IS structural connection. This script computes that.

Metrics:
  1. Raw reachability Jaccard: |closure(A) ∩ closure(B)| / |closure(A) ∪ closure(B)|.
     High = modules share much downward structure (including base).
  2. Base-quotient Jaccard: same but the GLOBAL BASE (modules
     reached by ≥90% of nodes) is subtracted from both sets first.
     Reveals NON-TRIVIAL shared structure beyond what everyone shares.
  3. Containment ratio: |closure(A) ∩ closure(B)| / |closure(A)|.
     Asymmetric: "how much of A's dependencies does B subsume?"
"""

import re
from pathlib import Path
from collections import defaultdict

import numpy as np


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


def downward_closure(graph, idx, n):
    """For each module, compute set of all modules transitively reached."""
    closure = [set() for _ in range(n)]
    nodes = sorted(graph.keys())
    # Build adjacency.
    adj = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                adj[idx[src]].add(idx[dep])

    # DFS from each node.
    def dfs(start):
        stack = [start]
        seen = set()
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            stack.extend(adj[v])
        seen.discard(start)
        return seen

    for i in range(n):
        closure[i] = dfs(i)
    return closure


def upward_closure(graph, idx, n):
    """For each module, compute set of all modules that transitively reach it."""
    rev_adj = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                rev_adj[idx[dep]].add(idx[src])

    closure = [set() for _ in range(n)]

    def dfs(start):
        stack = [start]
        seen = set()
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            stack.extend(rev_adj[v])
        seen.discard(start)
        return seen

    for i in range(n):
        closure[i] = dfs(i)
    return closure


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
    idx = {nd: i for i, nd in enumerate(nodes)}
    n = len(nodes)
    short = lambda i: nodes[i].split(".")[-1]

    down = downward_closure(graph, idx, n)
    up = upward_closure(graph, idx, n)
    print(f"Computed reachability closures for {n} modules.\n")

    # Identify the global base: modules reached by ≥90% of the others.
    reach_count = [0] * n
    for i in range(n):
        for tgt in down[i]:
            reach_count[tgt] += 1
    threshold = int(0.5 * n)  # reached by ≥50% of nodes
    base_modules = set(i for i in range(n) if reach_count[i] >= threshold)
    print(f"=== Global base (modules reached by ≥{threshold} of {n}) ===")
    for i in sorted(base_modules, key=lambda x: -reach_count[x]):
        print(f"  reach-count={reach_count[i]:2d}: {nodes[i]}")
    print()

    # Three Jaccard variants.
    n_pairs = (n * (n - 1)) // 2
    raw_J = np.zeros((n, n))
    base_J = np.zeros((n, n))  # base-quotient
    cont_A = np.zeros((n, n))  # containment: |A ∩ B| / |A|

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            di, dj = down[i], down[j]
            raw_J[i, j] = jaccard(di, dj)
            di_q = di - base_modules
            dj_q = dj - base_modules
            base_J[i, j] = jaccard(di_q, dj_q)
            cont_A[i, j] = len(di & dj) / max(len(di), 1)

    print("=== Downward-reachability Jaccard (raw) — top 15 pairs ===")
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            pairs.append((raw_J[i, j], i, j))
    pairs.sort(reverse=True)
    for j_val, a, b in pairs[:15]:
        print(f"  J={j_val:.2f}  {short(a):30s} ⇄ {short(b)}")
    print()

    print("=== Downward-reachability Jaccard (BASE-QUOTIENT) — top 15 pairs ===")
    print("  After subtracting the global base from both closures.")
    print("  Reveals non-trivial shared structure.")
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            pairs.append((base_J[i, j], i, j))
    pairs.sort(reverse=True)
    for j_val, a, b in pairs[:20]:
        if j_val == 0:
            break
        print(f"  J={j_val:.2f}  {short(a):30s} ⇄ {short(b)}")
    print()

    # Containment: which modules subsume which?
    print("=== Containment ratios — modules whose deps are contained in others ===")
    print("  cont(A→B) = |down(A) ∩ down(B)| / |down(A)|  (= 1 iff A ⊆ B)")
    print()
    # For each pair, find cases where cont(A→B) = 1 OR cont(B→A) = 1 but not both equal.
    interesting = []
    for i in range(n):
        for j in range(i+1, n):
            ci, cj = cont_A[i, j], cont_A[j, i]
            if ci == 1.0 and cj == 1.0:
                continue  # identical closures
            if ci >= 0.9 or cj >= 0.9:
                interesting.append((max(ci, cj), ci, cj, i, j))
    interesting.sort(reverse=True)
    for _, ci, cj, a, b in interesting[:15]:
        if ci > cj:
            print(f"  cont={ci:.2f}: {short(a):30s} ⊆ {short(b)}  (cont B→A = {cj:.2f})")
        else:
            print(f"  cont={cj:.2f}: {short(b):30s} ⊆ {short(a)}  (cont A→B = {ci:.2f})")
    print()

    # Specific re-examination: V4-Embedding cluster ↔ Stab-S3-* family
    print("=== V4-Embedding cluster vs Stab-S3-* family (base-quotient) ===")
    print("  Earlier (Jaccard on neighborhoods): J ≤ 0.25 — looked disconnected.")
    print("  Now (Jaccard on reachability, base-subtracted): ?")
    print()
    triangle = [
        "Substrate.Groups.V4-Embedding",
        "Substrate.Groups.SemidirectProduct",
        "Substrate.Groups.V4-Normality",
    ]
    stab = [
        "Substrate.Groups.Stab-S3",
        "Substrate.Groups.Stab-S3-Restrict",
        "Substrate.Groups.Stab-S3-Extend",
        "Substrate.Groups.Stab-S3-Iso",
        "Substrate.Groups.Stab-S3-Hom",
    ]
    triangle_i = [idx[m] for m in triangle if m in idx]
    stab_i = [idx[m] for m in stab if m in idx]

    print("  Raw reachability Jaccard (includes base):")
    for a in triangle_i:
        for b in stab_i:
            print(f"    {short(a):30s} ⇄ {short(b):30s}  J={raw_J[a, b]:.2f}")
    print()
    print("  Base-quotient Jaccard (base subtracted):")
    for a in triangle_i:
        for b in stab_i:
            print(f"    {short(a):30s} ⇄ {short(b):30s}  J={base_J[a, b]:.2f}")
    print()

    # Stab-S3 bowtie revisited under reachability.
    print("=== Stab-S3-* family under reachability ===")
    print("  (At neighborhood-Jaccard: bowtie of two 3-simplices, J(Stab-S3, Extend)=0.44)")
    print("  At raw reachability:")
    for i, a in enumerate(stab_i):
        for b in stab_i[i+1:]:
            print(f"    {short(a):30s} ⇄ {short(b):30s}  J={raw_J[a, b]:.2f}")
    print("  At base-quotient reachability:")
    for i, a in enumerate(stab_i):
        for b in stab_i[i+1:]:
            print(f"    {short(a):30s} ⇄ {short(b):30s}  J={base_J[a, b]:.2f}")
    print()


if __name__ == "__main__":
    main()
