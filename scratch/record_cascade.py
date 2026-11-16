#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""record_cascade.py — MECHANICAL atomic-cascade scope for a RECORD reparameterize
(set1-carrier-always-parameterize), from the CURRENT typechecked .agdai cores (NOT grep).
Generalizes uparrow_refactor_path.py to any record: pass the record's qname; it derives the
target set (the record + every `Record.*` projection/constructor, by prefix), harvests the
real elaborated referenced-qname set per def (the _FREE kinds) via jea_agdai.decode_core, and:

  CONSUMERS = every def referencing a target qname (excluding the record's own internals).
  DAG       = consumer→consumer coupling (A→B iff A references B); SCC = atomic cluster.
  LAYERS    = topological layering = the dependency-ordered migration sequence.
  ⚑ FORCED-RECORD consumers (kind=Record/Data that TAKE the target) are flagged — each
    forces its OWN sub-cascade (e.g. reparameterizing CommutativeMonoid forces RGradedMonoid);
    re-run this tool on that record to get its layer.

Usage:  python3 scratch/record_cascade.py Substrate.Category.CommutativeMonoid.CommutativeMonoid
"""
import sys, subprocess
from pathlib import Path
from collections import defaultdict

ROOT = Path("/home/mikemol/github/substrate")
sys.path.insert(0, str(ROOT / "jea" / "metalanguage"))
import jea_agdai as J

BUILD = ROOT / "agda" / "_build" / "2.8.0" / "agda"
_FREE = {"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"}

REC = sys.argv[1] if len(sys.argv) > 1 else "Substrate.Category.CommutativeMonoid.CommutativeMonoid"
# targets: the record + all its projections/constructor (Record.*) — matched by prefix at ref time
TARGET_PREFIX = REC + "."
def is_target(q):
    return q == REC or q.startswith(TARGET_PREFIX)


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
    short = REC.rsplit(".", 1)[-1]
    # pre-filter files by name (cheap); decode only those cores
    try:
        files = subprocess.check_output(
            ["rg", "-l", rf"\b{short}\b", "-g", "*.agda", str(ROOT / "agda" / "Substrate")]
        ).decode().split()
    except subprocess.CalledProcessError:
        files = []
    unit_refs, unit_file, unit_kind = {}, {}, {}
    decoded = 0
    for f in files:
        rel = Path(f).relative_to(ROOT / "agda").with_suffix(".agdai")
        cp = BUILD / rel
        if not cp.exists():
            continue
        core = J.decode_core(str(cp))
        if core is None:
            continue
        decoded += 1
        nodes = core["nodes"]
        for d in core["defmarks"]:
            u = d["unit"]
            unit_refs[u] = refs(nodes, d["root"])
            unit_file[u] = str(rel)
            unit_kind[u] = d.get("kind")

    # consumers = defs referencing a target, minus the record's OWN internal defs (deleted/edited WITH it)
    consumers = {u for u, rs in unit_refs.items()
                 if any(is_target(r) for r in rs) and not is_target(u)}
    edges = {u: {r for r in unit_refs[u] if r in consumers and r != u} for u in consumers}

    # Tarjan SCC
    idx, low, onstk, stk, comps, counter = {}, {}, {}, [], [], [0]
    sys.setrecursionlimit(20000)

    def strong(v):
        idx[v] = low[v] = counter[0]; counter[0] += 1
        stk.append(v); onstk[v] = True
        for w in edges[v]:
            if w not in idx:
                strong(w); low[v] = min(low[v], low[w])
            elif onstk.get(w):
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = stk.pop(); onstk[w] = False; comp.append(w)
                if w == v:
                    break
            comps.append(comp)

    for v in consumers:
        if v not in idx:
            strong(v)

    comp_of = {u: i for i, c in enumerate(comps) for u in c}
    cedges = defaultdict(set)
    for u in consumers:
        for w in edges[u]:
            if comp_of[u] != comp_of[w]:
                cedges[comp_of[u]].add(comp_of[w])
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

    nfiles = len(set(unit_file[u] for u in consumers))
    forced = sorted(u for u in consumers if unit_kind.get(u) in ("Record", "Data"))
    print(f"# record_cascade: {short} — {len(consumers)} consumer def(s) across {nfiles} files "
          f"({decoded} cores decoded)")
    print(f"# ⚑ FORCED-RECORD consumers (each forces its OWN sub-cascade — re-run on it): "
          f"{[u.rsplit('.',1)[-1] for u in forced] or 'none'}")
    print(f"# ATOMIC UNIT = all {len(consumers)} consumers + the record itself, one commit.\n")
    for lv in sorted(layers):
        here = layers[lv]
        nunits = sum(len(c) for c in here)
        print(f"## LAYER {lv} ({len(here)} cluster(s), {nunits} def(s))")
        for c in sorted(here, key=lambda c: (-len(c), min(unit_file[u] for u in c))):
            files_in = sorted(set(unit_file[u] for u in c))
            tag = f"  ⟲ CYCLE/{len(c)}" if len(c) > 1 else ""
            print(f"  {files_in}{tag}")
            for u in sorted(c):
                touched = sorted(s.replace(REC + ".", ".").replace(REC, "«self»")
                                 for s in unit_refs[u] if is_target(s))
                k = unit_kind.get(u) or "?"
                print(f"      [{k:8}] {u.rsplit('.',1)[-1]:32} ⟵ {touched}")
        print()


if __name__ == "__main__":
    main()
