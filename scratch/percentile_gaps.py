"""
Percentile-based gap analysis on the substrate Agda dependency graph.

Instead of arbitrary "top N" cuts, select pairs by percentile of the
Jaccard similarity distribution. For each high-similarity pair, show
the SYMMETRIC DIFFERENCE of their closures — the structural gap that,
if patched, would unify them.

Three Jaccard distributions are computed:
  1. Neighborhood-Jaccard (bottom-up, direct in+out neighbors).
  2. Reachability-Jaccard raw (top-down, full downward closure).
  3. Reachability-Jaccard base-quotient (closure minus global base).

For each, we report:
  - Distribution stats (mean, median, 90/95/99 percentiles).
  - All pairs above the 90th percentile.
  - For each such pair, the symmetric difference (the GAP).
  - Per-gap-element categorization (which side has it; what it imports).
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
    g = {}
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        name, imports = parse_module(path)
        if name and name.startswith("Substrate"):
            g[name] = imports
    return g


def jaccard(a, b):
    if not a and not b: return 1.0
    u = a | b
    if not u: return 0.0
    return len(a & b) / len(u)


def downward_closure(graph, idx, n):
    adj = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                adj[idx[src]].add(idx[dep])
    closure = [set() for _ in range(n)]
    for i in range(n):
        stack = [i]; seen = set()
        while stack:
            v = stack.pop()
            if v in seen: continue
            seen.add(v)
            stack.extend(adj[v])
        seen.discard(i)
        closure[i] = seen
    return closure


def main():
    graph = build_graph()
    nodes = sorted(graph.keys())
    idx = {nd: i for i, nd in enumerate(nodes)}
    n = len(nodes)
    short = lambda i: nodes[i].split(".")[-1] if isinstance(i, int) else i.split(".")[-1]

    # Neighborhoods (direct in + out).
    out_nbr = [set() for _ in range(n)]
    in_nbr  = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                out_nbr[idx[src]].add(idx[dep])
                in_nbr[idx[dep]].add(idx[src])
    nbr_sig = [out_nbr[i] | in_nbr[i] for i in range(n)]

    # Reachability.
    down = downward_closure(graph, idx, n)

    # Global base: modules reached by ≥50% of nodes.
    reach_count = [0] * n
    for i in range(n):
        for tgt in down[i]:
            reach_count[tgt] += 1
    base_modules = set(i for i in range(n) if reach_count[i] >= n // 2)
    print(f"Base ({len(base_modules)} modules, reached by ≥{n//2}/{n}): "
          f"{[short(i) for i in sorted(base_modules, key=lambda x: -reach_count[x])]}")
    print()

    # === Three Jaccard distributions ===
    def compute_jaccards(sig):
        pairs = []
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((jaccard(sig[i], sig[j]), i, j))
        return pairs

    sigs = {
        "neighborhood": nbr_sig,
        "reach-raw":    down,
        "reach-base-quotient": [s - base_modules for s in down],
    }

    for name, sig in sigs.items():
        pairs = compute_jaccards(sig)
        values = np.array([p[0] for p in pairs])
        print(f"=== {name} ===")
        print(f"  N pairs: {len(pairs)}")
        print(f"  Mean: {values.mean():.3f}  Median: {np.median(values):.3f}  Max: {values.max():.3f}")
        p50, p75, p90, p95, p99 = np.percentile(values, [50, 75, 90, 95, 99])
        print(f"  P50: {p50:.3f}  P75: {p75:.3f}  P90: {p90:.3f}  P95: {p95:.3f}  P99: {p99:.3f}")
        # Pairs ≥ P90.
        above_p90 = sorted((p for p in pairs if p[0] >= p90), reverse=True)
        print(f"  Pairs ≥ P90 ({p90:.3f}): {len(above_p90)}")
        for j_val, a, b in above_p90:
            gap_a = sig[a] - sig[b]
            gap_b = sig[b] - sig[a]
            sym_diff_size = len(gap_a) + len(gap_b)
            intersection = sig[a] & sig[b]
            print(f"    J={j_val:.2f} (gap={sym_diff_size}): {short(a):28s} ⇄ {short(b)}")
            if sym_diff_size > 0 and sym_diff_size <= 10:
                if gap_a:
                    print(f"        {short(a):28s} has, {short(b):28s} lacks: "
                          f"{{{', '.join(short(x) for x in sorted(gap_a))}}}")
                if gap_b:
                    print(f"        {short(b):28s} has, {short(a):28s} lacks: "
                          f"{{{', '.join(short(x) for x in sorted(gap_b))}}}")
        print()


if __name__ == "__main__":
    main()
