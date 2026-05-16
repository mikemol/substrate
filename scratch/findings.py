"""
Grothendieck-construction consolidation of all structural-analysis
scripts.

Each existing detector (percentile_gaps, reachability_dual,
simplicial_shape, clause_shapes) is a functor:

    Codebase → Findings_i

at some level (module-pair, module-simplex, definition-group). Taking
∫ over the level-index packages all findings into one category, where
the objects are (level, finding) pairs and a "thick point" is an
entity-tuple witnessed by multiple scripts at multiple levels.

This script:
  1. Re-implements the key analyses inline (so it's self-contained).
  2. Emits all findings as `Finding` records with a normalized
     `objects` key (frozenset of entity names).
  3. Consolidates by `objects` — counts witnesses per entity-tuple.
  4. Outputs:
     a) Ranked table of structural facts by witness count.
     b) Cross-level refinement chains (module-pair → definitions in those modules).
     c) Empty-fiber report (levels with no witnesses).

Per [[project-annealing-methodology]]: the script proposes thick
points. We don't propose specific refactors from outside the script.
"""

import re
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import FrozenSet, Tuple, Any

import numpy as np
import networkx as nx


SUBSTRATE_ROOT = Path("/home/mikemol/github/substrate/agda")


@dataclass(frozen=True)
class Finding:
    """A single structural-claim object from some source script."""
    level: str           # 'module-pair' | 'module-simplex' | 'def-group' | 'def-pair' | etc.
    kind: str            # script-specific category, e.g., 'jaccard-neighborhood-p90'
    objects: FrozenSet   # the entities the finding is about (set of names)
    metric: float        # primary numerical signal
    source: str          # which logical script emitted this finding
    extra: Tuple = field(default_factory=tuple)  # supplementary data


# ============================================================
# Parsing helpers
# ============================================================

def parse_module_path(path):
    text = path.read_text()
    m = re.search(r"^module\s+([A-Za-z0-9_.\-]+)\s+where", text, re.M)
    if not m:
        return None, ""
    name = m.group(1)
    return name, re.sub(r"\{-.*?-\}", "", re.sub(r"--.*$", "", text, flags=re.M), flags=re.S)


def module_imports(text):
    return [imp for imp in re.findall(r"^(?:open\s+)?import\s+([A-Za-z0-9_.\-]+)", text, re.M)
            if imp.startswith("Substrate.")]


def short(name):
    return name.split("::")[-1].split(".")[-1]


def jaccard(a, b):
    if not a and not b: return 1.0
    u = a | b
    return (len(a & b) / len(u)) if u else 0.0


# ============================================================
# Source 1: module-pair Jaccards at multiple levels
# ============================================================

def collect_module_findings(graph, nodes):
    findings = []
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)

    out_nbr = [set() for _ in range(n)]
    in_nbr  = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                out_nbr[idx[src]].add(idx[dep])
                in_nbr[idx[dep]].add(idx[src])
    nbr_sig = [out_nbr[i] | in_nbr[i] for i in range(n)]

    # Reachability closures.
    adj = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                adj[idx[src]].add(idx[dep])
    down = [set() for _ in range(n)]
    for i in range(n):
        stack, seen = [i], set()
        while stack:
            v = stack.pop()
            if v in seen: continue
            seen.add(v); stack.extend(adj[v])
        seen.discard(i)
        down[i] = seen

    # Global base.
    reach_count = [0] * n
    for i in range(n):
        for t in down[i]:
            reach_count[t] += 1
    base_modules = set(i for i in range(n) if reach_count[i] >= n // 2)

    # Compute Jaccards at each level.
    sigs = {
        "jaccard-neighborhood":     nbr_sig,
        "jaccard-reach-raw":         down,
        "jaccard-reach-base-quotient": [s - base_modules for s in down],
    }

    for kind, sig in sigs.items():
        vals = []
        for i in range(n):
            for j in range(i + 1, n):
                vals.append(jaccard(sig[i], sig[j]))
        if not vals:
            continue
        p90 = float(np.percentile(vals, 90))
        for i in range(n):
            for j in range(i + 1, n):
                jv = jaccard(sig[i], sig[j])
                if jv >= p90:
                    findings.append(Finding(
                        level="module-pair",
                        kind=f"{kind}-p90",
                        objects=frozenset({nodes[i], nodes[j]}),
                        metric=jv,
                        source="percentile_gaps",
                    ))
    return findings, base_modules


# ============================================================
# Source 2: simplicial cliques at threshold sweeps
# ============================================================

def collect_simplex_findings(graph, nodes):
    findings = []
    idx = {n_: i for i, n_ in enumerate(nodes)}
    n = len(nodes)

    out_nbr = [set() for _ in range(n)]
    in_nbr  = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                out_nbr[idx[src]].add(idx[dep])
                in_nbr[idx[dep]].add(idx[src])
    sig = [out_nbr[i] | in_nbr[i] for i in range(n)]

    # Build similarity matrix.
    J = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            J[i, j] = J[j, i] = jaccard(sig[i], sig[j])

    for theta in [0.5, 0.7, 0.8]:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for i in range(n):
            for j in range(i + 1, n):
                if J[i, j] >= theta:
                    G.add_edge(i, j)
        for c in nx.find_cliques(G):
            if len(c) >= 3:
                findings.append(Finding(
                    level="module-simplex",
                    kind=f"max-clique-theta{theta:.1f}",
                    objects=frozenset(nodes[i] for i in c),
                    metric=float(theta),
                    source="simplicial_shape",
                ))
    return findings


# ============================================================
# Source 3: clause-shape recurrence groups (definition-level)
# ============================================================

CLAUSE_RE = re.compile(
    r"^([a-zA-Z_][a-zA-Z0-9_\-'≢≈₁₂₃₄₅₆₇₈₉₀ⁿᵐ⁻ᵖᵃˢⁱ]*)"
    r"(\s+[^\n=]+?)?\s*=\s*([^\n]*)$",
    re.M
)


def parse_definitions(text):
    defs = defaultdict(list)
    for line in text.split("\n"):
        if not line or line[0].isspace():
            continue
        m = CLAUSE_RE.match(line)
        if not m:
            continue
        name, _args, rhs = m.group(1), m.group(2), m.group(3).strip()
        if name in {"open", "import", "module", "record", "data", "field",
                    "private", "postulate", "infixl", "infixr", "infix", "where"}:
            continue
        if not rhs:
            continue
        defs[name].append(rhs)
    return defs


def shape_template(rhs):
    t = re.sub(r"[a-zA-Z_][a-zA-Z0-9_\-'≢≈₁₂₃₄₅₆₇₈₉₀ⁿᵐ⁻ᵖᵃˢⁱ]*", "_", rhs)
    return re.sub(r"\s+", " ", t).strip()


def collect_clause_findings():
    findings = []
    all_defs = {}            # qname (full-module::def) -> rhss
    qname_to_module = {}     # qname -> full module name (Substrate.X.Y)
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        for name, rhss in parse_definitions(text).items():
            qname = f"{mod}::{name}"
            all_defs[qname] = rhss
            qname_to_module[qname] = mod

    # Group by (clause_count, template_set).
    shape_to_defs = defaultdict(list)
    for qname, rhss in all_defs.items():
        if len(rhss) < 4:
            continue
        templates = frozenset(shape_template(r) for r in rhss)
        sig = (len(rhss), templates)
        shape_to_defs[sig].append(qname)

    for (count, templates), members in shape_to_defs.items():
        if len(members) >= 2:
            findings.append(Finding(
                level="def-group",
                kind=f"shape-group-{count}c",
                objects=frozenset(members),
                metric=float(len(members)),
                source="clause_shapes",
                extra=(count,),
            ))

    # All-refl-clause definitions as individual findings.
    for qname, rhss in all_defs.items():
        if len(rhss) >= 4 and all(r == "refl" for r in rhss):
            findings.append(Finding(
                level="def-single",
                kind=f"all-refl-{len(rhss)}c",
                objects=frozenset({qname}),
                metric=float(len(rhss)),
                source="clause_shapes",
                extra=(len(rhss),),
            ))
    return findings, qname_to_module


# ============================================================
# Consolidation: the Grothendieck total category
# ============================================================

def main():
    # Build module graph.
    graph = {}
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        name, text = parse_module_path(path)
        if name and name.startswith("Substrate"):
            graph[name] = module_imports(text)
    nodes = sorted(graph.keys())

    print(f"Modules: {len(nodes)}\n")

    # Collect findings from all three sources.
    findings = []
    mod_findings, base = collect_module_findings(graph, nodes)
    findings.extend(mod_findings)
    findings.extend(collect_simplex_findings(graph, nodes))
    clause_f, qname_to_module = collect_clause_findings()
    findings.extend(clause_f)

    print(f"Total findings emitted: {len(findings)}")
    print(f"  module-pair:    {sum(1 for f in findings if f.level == 'module-pair')}")
    print(f"  module-simplex: {sum(1 for f in findings if f.level == 'module-simplex')}")
    print(f"  def-group:      {sum(1 for f in findings if f.level == 'def-group')}")
    print(f"  def-single:     {sum(1 for f in findings if f.level == 'def-single')}")
    print()

    # === Refinement morphisms (Grothendieck construction): each
    # higher-level finding REFINES to the implied lower-level findings.
    # A simplex {A,B,C} witnesses pairs {A,B}, {A,C}, {B,C}. A def-group
    # spanning modules {A,B} witnesses the pair {A,B}.
    refined = list(findings)
    # Simplex → pairs.
    for f in findings:
        if f.level == "module-simplex":
            nodes_list = sorted(f.objects)
            for i in range(len(nodes_list)):
                for j in range(i + 1, len(nodes_list)):
                    refined.append(Finding(
                        level="module-pair",
                        kind=f"simplex-refinement-θ{f.metric:.1f}",
                        objects=frozenset({nodes_list[i], nodes_list[j]}),
                        metric=f.metric,
                        source="simplicial_shape",
                    ))
    # Def-group → module-pairs (every pair of distinct modules covered).
    for f in findings:
        if f.level == "def-group":
            mods = sorted({qname_to_module.get(q, q.split("::")[0]) for q in f.objects})
            for i in range(len(mods)):
                for j in range(i + 1, len(mods)):
                    refined.append(Finding(
                        level="module-pair",
                        kind=f"def-group-refinement-{int(f.metric)}m",
                        objects=frozenset({mods[i], mods[j]}),
                        metric=f.metric,
                        source="clause_shapes",
                        extra=(f.kind,),
                    ))
    findings = refined
    print(f"After refinements: {len(findings)} findings\n")

    # === Consolidate by objects (the Grothendieck thick-point computation) ===
    by_objects = defaultdict(list)
    for f in findings:
        by_objects[f.objects].append(f)

    # Witness-count distribution.
    wc_dist = Counter(len(fs) for fs in by_objects.values())
    print("=== Witness-count distribution ===")
    for wc in sorted(wc_dist.keys(), reverse=True):
        print(f"  {wc} witnesses : {wc_dist[wc]} entity-tuples")
    print()

    # === Thick points: entities witnessed ≥3 times ===
    thick = [(len(fs), objs, fs) for objs, fs in by_objects.items() if len(fs) >= 3]
    thick.sort(key=lambda x: -x[0])
    print("=== Thick points (≥3 witnesses) ===")
    for wc, objs, fs in thick[:25]:
        ent = ", ".join(short(o) for o in sorted(objs))
        srcs = ", ".join(sorted({f.source for f in fs}))
        kinds = ", ".join(sorted({f.kind for f in fs}))
        print(f"  [{wc} witnesses, {len(set(f.source for f in fs))} sources]: {{{ent}}}")
        print(f"    sources: {srcs}")
        print(f"    kinds: {kinds}")
    print()

    # === Cross-level refinement chains ===
    # For each module-pair finding, look for definition-pair / def-group
    # findings whose modules match.
    print("=== Cross-level refinements (module-pair witnessed AND has def-group inside) ===")
    module_pairs = [f for f in findings if f.level == "module-pair"]
    def_groups = [f for f in findings if f.level == "def-group"]

    def def_module(qname):
        return qname.split("::")[0]

    cross_count = 0
    for mp in module_pairs[:50]:
        if mp.metric < 0.8:  # only look at strong pairs
            continue
        mod_set = {n.split(".")[-1] for n in mp.objects}
        for dg in def_groups:
            dg_mods = {def_module(q) for q in dg.objects}
            if mod_set.issubset(dg_mods) and len(dg_mods) <= len(mod_set) + 1:
                ent = ", ".join(short(o) for o in sorted(mp.objects))
                dgent = ", ".join(short(o) for o in sorted(dg.objects))
                print(f"  module-pair {{{ent}}} (J={mp.metric:.2f})")
                print(f"    refines into def-group ({dg.kind}, {int(dg.metric)} members)")
                print(f"    {{{dgent}}}")
                cross_count += 1
                if cross_count >= 8:
                    break
        if cross_count >= 8:
            break
    print()

    # === Inverse refinements: for each thick pair, find ambient containers
    # (simplices it's a face of; def-groups whose modules span it). This is
    # the contravariant direction of the refinement morphism — given a
    # finding at level L, list all findings at level L+1 that refine TO it.
    print("=== Inverse refinements: ambient context per thick point ===")
    print("    (A thick pair → which simplices/def-groups contain it as a face?)")
    print()
    # Index simplices and def-groups by their objects sets.
    simplices = [f for f in findings if f.level == "module-simplex"]
    def_groups = [f for f in findings if f.level == "def-group"]
    pair_findings = sorted(
        ((len(fs), objs) for objs, fs in by_objects.items() if len(objs) == 2),
        key=lambda x: -x[0]
    )
    pair_findings = [(wc, objs) for wc, objs in pair_findings if wc >= 4]
    for wc, pair in pair_findings[:12]:
        ent = ", ".join(short(o) for o in sorted(pair))
        containing_simplices = [s for s in simplices if pair.issubset(s.objects)]
        spanning_defgroups = []
        for dg in def_groups:
            dg_mods = {qname_to_module.get(q, q.split("::")[0]) for q in dg.objects}
            if pair.issubset(dg_mods):
                spanning_defgroups.append(dg)
        print(f"  [{wc}-witness pair] {{{ent}}}")
        if containing_simplices:
            for s in containing_simplices[:2]:
                s_ent = ", ".join(short(o) for o in sorted(s.objects))
                print(f"    ⊂ simplex (θ={s.metric:.1f}, n={len(s.objects)}): {{{s_ent}}}")
        if spanning_defgroups:
            for dg in spanning_defgroups[:2]:
                print(f"    ⊂ def-group ({dg.kind}, {int(dg.metric)} defs)")
        if not containing_simplices and not spanning_defgroups:
            print(f"    (no ambient simplex or def-group contains this pair)")
    print()

    # === Empty fibers ===
    print("=== Empty fibers (levels with no findings or under-populated) ===")
    levels = {f.level for f in findings}
    expected_levels = {"module-pair", "module-simplex", "module-triple",
                       "def-group", "def-single", "def-pair",
                       "clause-shape-pair", "term-shape", "catalog-claim"}
    missing = expected_levels - levels
    print(f"  Currently populated levels: {sorted(levels)}")
    print(f"  Missing levels: {sorted(missing)}")
    print(f"  → Each missing level is a next-detector candidate.")


if __name__ == "__main__":
    main()
