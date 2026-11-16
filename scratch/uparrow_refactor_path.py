#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""uparrow_refactor_path.py — the MECHANICAL shortest-path plan for the UPArrow→UPArrowP
dissolution, derived from the CURRENT typechecked .agdai cores (not grep, not the stale
catalog). Mirrors gen_warrants.py: decode each core via jea_agdai, harvest the real
elaborated referenced-qname set per definition (the _FREE referential kinds), then:

  1. CONSUMERS  = every def whose type/body references a UPArrow-tier target qname
                  (the record + its Source/Target/Witness projections + constructor + the
                   UniversalProperty alias + trivial-UP).
  2. DAG        = consumer→consumer edges (A→B iff A references the def B, both consumers)
                  — the migration-COUPLING graph: B's signature change forces A to adapt.
  3. SCCs       = atomic must-migrate-together clusters (a cycle = one commit).
  4. LAYERS     = a topological layering of the condensation = the dependency-ordered
                  migration sequence (layer 0 = migrate first, depends on nothing else).

Output: the layered plan + per-consumer the exact target symbols it touches (edit surface).
"""
import sys, subprocess
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/mikemol/github/substrate")
sys.path.insert(0, str(ROOT / "jea" / "metalanguage"))
import jea_agdai as J

BUILD = ROOT / "agda" / "_build" / "2.8.0" / "agda"
_FREE = {"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"}
P = "Substrate.Category.UniversalProperty."
TARGETS = {
    P + "UPArrow", P + "UPArrow.constructor",
    P + "UPArrow.Source", P + "UPArrow.Target", P + "UPArrow.Witness",
    P + "Source", P + "Target", P + "Witness",
    P + "UniversalProperty", P + "trivial-UP",
}


def refs(nodes, root):
    seen, out, stk = set(), set(), [root]
    while stk:
        nid = stk.pop()
        if nid in seen or nid not in nodes:
            continue
        seen.add(nid)
        n = nodes[nid]
        if n.get("constructor") in _FREE and n.get("qname"):
            out.add(n["qname"])
        stk += n.get("children", [])
    return out


def main():
    files = subprocess.check_output(
        ["rg", "-l", r"\bUPArrow\b|\bUniversalProperty\b", "-g", "*.agda", str(ROOT / "agda" / "Substrate")]
    ).decode().split()
    unit_refs, unit_file = {}, {}
    decoded, skipped = 0, []
    for f in files:
        rel = Path(f).relative_to(ROOT / "agda").with_suffix(".agdai")
        cp = BUILD / rel
        if not cp.exists():
            skipped.append(str(rel) + " (no core)")
            continue
        core = J.decode_core(str(cp))
        if core is None:
            skipped.append(str(rel) + " (decode Nothing)")
            continue
        decoded += 1
        nodes = core["nodes"]
        for d in core["defmarks"]:
            u = d["unit"]
            unit_refs[u] = refs(nodes, d["root"])
            unit_file[u] = str(rel)

    # exclude the record's OWN components (deleted WITH the record, not migrated as consumers)
    RECORD_INTERNAL = {
        P + "UPArrow", P + "UPArrow.constructor", P + "UPArrow.Source",
        P + "UPArrow.Target", P + "UPArrow.Witness", P + "Source", P + "Target",
        P + "Witness", P + "UniversalProperty",
    }
    consumers = {u for u, rs in unit_refs.items()
                 if (rs & TARGETS) and u not in RECORD_INTERNAL}
    edges = {u: {r for r in unit_refs[u] if r in consumers and r != u} for u in consumers}

    # Tarjan SCC
    idx = {}
    low = {}
    onstk = {}
    stk = []
    comps = []
    counter = [0]
    import sys as _s
    _s.setrecursionlimit(10000)

    def strong(v):
        idx[v] = low[v] = counter[0]
        counter[0] += 1
        stk.append(v)
        onstk[v] = True
        for w in edges[v]:
            if w not in idx:
                strong(w)
                low[v] = min(low[v], low[w])
            elif onstk.get(w):
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = stk.pop()
                onstk[w] = False
                comp.append(w)
                if w == v:
                    break
            comps.append(comp)

    for v in consumers:
        if v not in idx:
            strong(v)

    comp_of = {}
    for i, c in enumerate(comps):
        for u in c:
            comp_of[u] = i
    # condensation edges + indegree for layering
    cedges = defaultdict(set)
    for u in consumers:
        for w in edges[u]:
            if comp_of[u] != comp_of[w]:
                cedges[comp_of[u]].add(comp_of[w])
    # layer by longest-dependency-depth (a comp migrates AFTER the comps it depends on)
    depth = {}

    def dep(ci):
        if ci in depth:
            return depth[ci]
        depth[ci] = 0
        depth[ci] = 1 + max((dep(cj) for cj in cedges[ci]), default=-1)
        return depth[ci]

    for ci in range(len(comps)):
        dep(ci)

    layers = defaultdict(list)
    for ci, c in enumerate(comps):
        layers[depth[ci]].append(c)

    # ---- report ----
    print(f"# UPArrow→UPArrowP shortest-path refactor plan (mechanical, from {decoded} cores)")
    print(f"# consumers (defs still on the UPArrow tier): {len(consumers)}  "
          f"across {len(set(unit_file[u] for u in consumers))} files")
    if skipped:
        print(f"# skipped cores: {len(skipped)} -> {skipped[:4]}")
    print()
    for lv in sorted(layers):
        comps_here = layers[lv]
        nunits = sum(len(c) for c in comps_here)
        print(f"## LAYER {lv}  ({len(comps_here)} cluster(s), {nunits} def(s)) — migrate after layer {lv-1}")
        # sort clusters: multi-def (cycles=atomic) first
        for c in sorted(comps_here, key=lambda c: (-len(c), min(unit_file[u] for u in c))):
            files_in = sorted(set(unit_file[u] for u in c))
            tag = f"  ⟲ CYCLE/{len(c)}" if len(c) > 1 else ""
            print(f"  cluster{tag}: {len(c)} def(s) in {files_in}")
            for u in sorted(c):
                touched = sorted(s.replace(P, "") for s in (unit_refs[u] & TARGETS))
                print(f"      {u.replace(P,'')}  ⟵ {touched}")
        print()


if __name__ == "__main__":
    main()
