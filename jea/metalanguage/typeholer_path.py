#!/usr/bin/env python3
"""typeholer_path.py -- the recursive-typeholer PATH driver (⟡typeholer-path, design
`scratch/auto_pushout_typeholer_path_design.md` §Ⓑ).

WHAT IT DOES (the vertical climb). One interning of a corpus (.py and/or Agda .agdai
cores) already surfaces every SHARED SUBTREE at every depth -- the interner is bottom-up,
so re-interning does not find NEW shapes, it re-reads them at a coarser carrier set. This
driver reads that one forest twice, two dual ways:

  1. CONTAINMENT TOWER (the refactor plan).  extract candidates = subtrees shared across
     >= F units.  A candidate whose subtree CONTAINS another candidate's subtree is a
     HIGHER RUNG (design's stated ordering).  The Hasse DAG of that containment, with each
     node's rung = its longest containment-chain height, IS the decomposition tower:
     rung 0 = shared primitives (Fin, +, *), climbing to rung k = the big shared composites
     (combine=⊗, lookup=readout, subst=coherence).  Edges = instantiation obligations:
     node_units(candidate) = the exact set of concrete units the generic would subsume.

  2. FIXPOINT ITERATE (extract -> re-intern -> extract).  The literal design loop:
     level-0 carriers = the units; level-(k+1) candidates = subtrees shared across >= F
     level-k carriers; promote those candidate roots to be the next carrier set; repeat to
     fixpoint (no new sharing) or a depth guard.  This climbs the DUAL direction -- toward
     the shared PRIMITIVE BASIS (the corpus alphabet) -- and terminates fast precisely
     because the SPPF is bottom-up-complete.

HONEST SCOPE.  The tool surfaces shared TERM SUBTREES (raw nodes: combine, lookup,
tabulate, subst, +, Fin), NOT named records.  Naming a rung's subtree into `GradedProductOver`
and writing the instance proofs is the LLM synthesis step, NOT something this driver does.
The driver produces the STRUCTURAL SKELETON of the tower -- which nodes cluster at which
rung + the per-node instantiation obligations -- and hands each rung to a human/LLM to name.
"""
import sys, os, json, argparse, glob as glob_mod
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jea_pysim as J


# --------------------------------------------------------------------------- corpus
def build_corpus(files):
    C = J.Corpus()
    for f in files:
        if f.endswith(".agdai"):
            C.add_agdai(f)
        else:
            C.add_file(f)
    return C


def _head_str(head):
    # head = (kind, op, lit); prefer the qualified op name, fall back to kind/lit
    kind, op, lit = head
    return op or lit or kind


# --------------------------------------------------------------------------- candidates
class Cand:
    __slots__ = ("nid", "units", "size", "head", "unit_ids", "support")

    def __init__(self, nid, units, size, head, unit_ids, support):
        self.nid = nid
        self.units = units            # cross-unit membership count (refactor relevance)
        self.size = size              # subtree node count
        self.head = head              # (kind, op, lit)
        self.unit_ids = unit_ids      # frozenset of original unit indices containing this subtree
        self.support = support        # frozenset of interned node ids in this subtree


def extract_cands(C, min_fanin=3, min_size=5, cross_unit=True):
    """Extract-candidate subtrees.  cross_unit=True (default) ranks by how many distinct
    UNITS contain the subtree (node_units) -- the refactor-relevant metric, since a subtree
    repeated 5x inside ONE unit is not a cross-lemma abstraction.  cross_unit=False falls
    back to raw reference fan-in (jea_pysim's extract_candidates metric)."""
    out = []
    for nid in range(C.I.size()):
        unit_ids = C.node_units.get(nid, set())
        count = len(unit_ids) if cross_unit else C.I.fanin[nid]
        if count < min_fanin:
            continue
        sup = C._support(nid)
        if len(sup) < min_size:
            continue
        nn = C.I.nodes[nid]
        out.append(Cand(nid, len(unit_ids), len(sup), (nn.kind, nn.op, nn.lit),
                        frozenset(unit_ids), frozenset(sup)))
    out.sort(key=lambda c: (-c.units, -c.size))
    return out


# --------------------------------------------------------------------------- containment tower
def containment_dag(cands):
    """Build the Hasse DAG of subtree-containment among candidates.
      direct[A] = candidates B (!=A) with B.nid in A.support and NO intermediate candidate
                  C with B in C.support and C in A.support  (transitive reduction).
    Returns (direct: nid->list[nid], rung: nid->int).  rung = longest containment chain BELOW
    the node (leaves/primitives = 0), so a higher rung is a bigger shared composite."""
    by_nid = {c.nid: c for c in cands}
    ids = set(by_nid)
    # who does A strictly contain (any depth)?
    below = {}
    for c in cands:
        below[c.nid] = {b for b in ids if b != c.nid and b in c.support}
    # transitive reduction: keep B as a DIRECT child of A iff no C in below[A] also has B in below[C]
    direct = {}
    for a, bs in below.items():
        red = []
        for b in bs:
            if not any((c != b and b in below[c]) for c in bs):
                red.append(b)
        # order children by size desc for stable readable output
        red.sort(key=lambda n: -by_nid[n].size)
        direct[a] = red
    # rung = longest chain height over `below` (memoised)
    rung = {}

    def height(a):
        if a in rung:
            return rung[a]
        rung[a] = 0  # guard (DAG, no cycles, but be safe)
        h = 0
        for b in below[a]:
            h = max(h, height(b) + 1)
        rung[a] = h
        return h

    for a in ids:
        height(a)
    return direct, rung, below


# --------------------------------------------------------------------------- fixpoint iterate
def fixpoint_iterate(C, min_fanin=3, min_size=5, max_depth=8):
    """The literal extract -> re-intern -> extract loop.  carriers_0 = the units' supports;
    candidates_k = subtrees contained in >= F carriers_(k-1); carriers_k = those candidate
    subtrees; iterate to fixpoint (candidate set stops changing) or max_depth.
    Climbs toward the shared PRIMITIVE BASIS (the dual of the containment tower)."""
    # carrier = (root_nid, support_set)
    carriers = [(u.root, u.support) for u in C.units]
    levels = []
    seen = None
    for depth in range(max_depth):
        # count, for every node, how many carriers' supports contain it
        cnt = defaultdict(int)
        for _, sup in carriers:
            for n in sup:
                cnt[n] += 1
        carrier_roots = {r for r, _ in carriers}
        cands = []
        for nid, ct in cnt.items():
            if ct < min_fanin or nid in carrier_roots:
                continue
            sup = C._support(nid)
            if len(sup) < min_size:
                continue
            nn = C.I.nodes[nid]
            cands.append((nid, ct, len(sup), (nn.kind, nn.op, nn.lit)))
        cands.sort(key=lambda t: (-t[1], -t[2]))
        sig = frozenset(c[0] for c in cands)
        if not cands or sig == seen:
            break                                  # fixpoint / empty
        seen = sig
        levels.append({"depth": depth + 1, "n_carriers": len(carriers), "candidates": cands})
        # promote: the new carriers are the candidate subtrees
        carriers = [(nid, C._support(nid)) for nid, _, _, _ in cands]
    return levels


# --------------------------------------------------------------------------- assembly
def build_path(C, min_fanin=3, min_size=5, cross_unit=True, max_depth=8):
    cands = extract_cands(C, min_fanin, min_size, cross_unit)
    direct, rung, below = containment_dag(cands)
    by_nid = {c.nid: c for c in cands}
    max_rung = max(rung.values()) if rung else 0

    # group candidates by rung
    rungs = defaultdict(list)
    for c in cands:
        rungs[rung[c.nid]].append(c)
    for r in rungs:
        rungs[r].sort(key=lambda c: (-c.units, -c.size))

    unit_names = [f"{u.path.split('/')[-1]}::{u.name}" for u in C.units]

    result = {
        "corpus": {"units": len(C.units), "nodes": C.I.size(),
                   "params": {"min_fanin": min_fanin, "min_size": min_size,
                              "cross_unit": cross_unit}},
        "n_candidates": len(cands),
        "max_rung": max_rung,
        "containment_tower": [],
        "fixpoint_iterate": fixpoint_iterate(C, min_fanin, min_size, max_depth),
    }

    for r in range(max_rung + 1):
        entries = []
        for c in rungs.get(r, []):
            entries.append({
                "node": c.nid,
                "head": _head_str(c.head),
                "units": c.units,                    # how many concrete units contain it
                "size": c.size,
                "contains": [by_nid[b].nid for b in direct[c.nid]],           # direct lower rungs
                "contains_heads": sorted({_head_str(by_nid[b].head) for b in direct[c.nid]}),
                "obligations": sorted(unit_names[i] for i in c.unit_ids),      # units the generic subsumes
            })
        result["containment_tower"].append({"rung": r, "n": len(entries), "candidates": entries})
    return result, unit_names


# --------------------------------------------------------------------------- human render
def _dedupe_by_head(entries):
    """Collapse alpha/position variants that share (head, size) into one row with a
    multiplicity, so the human tree is readable.  Keeps max units + union of obligations."""
    groups = {}
    for e in entries:
        key = (e["head"], e["size"])
        g = groups.get(key)
        if g is None:
            groups[key] = {"head": e["head"], "size": e["size"], "mult": 1,
                           "units": e["units"], "contains_heads": set(e["contains_heads"]),
                           "obligations": set(e["obligations"])}
        else:
            g["mult"] += 1
            g["units"] = max(g["units"], e["units"])
            g["contains_heads"] |= set(e["contains_heads"])
            g["obligations"] |= set(e["obligations"])
    rows = list(groups.values())
    rows.sort(key=lambda g: (-g["units"], -g["size"]))
    return rows


def render_human(result):
    L = []
    c = result["corpus"]
    L.append(f"corpus: {c['units']} units, {c['nodes']} interned nodes "
             f"(min_fanin={c['params']['min_fanin']}, min_size={c['params']['min_size']}, "
             f"cross_unit={c['params']['cross_unit']})")
    L.append(f"{result['n_candidates']} shared-subtree candidates; "
             f"containment tower height = {result['max_rung']}")
    L.append("")
    L.append("=== CONTAINMENT TOWER (the refactor plan: rung 0 primitives -> apex composites) ===")
    L.append("    each row = a shared subtree the driver surfaces; a human/LLM names it into a record.")
    for band in result["containment_tower"]:
        r = band["rung"]
        rows = _dedupe_by_head(band["candidates"])
        if not rows:
            continue
        L.append(f"\n  rung {r}  ({band['n']} candidate nodes, {len(rows)} distinct heads):")
        for g in rows:
            mult = f" x{g['mult']}" if g["mult"] > 1 else ""
            low = (" <- " + ", ".join(sorted(g["contains_heads"]))) if g["contains_heads"] else ""
            L.append(f"      {g['head']:<42}{mult:<5} in {g['units']} units, size {g['size']}{low}")
            if g["obligations"]:
                obs = ", ".join(sorted(g["obligations"])[:6])
                more = "" if len(g["obligations"]) <= 6 else f" (+{len(g['obligations'])-6})"
                L.append(f"          obligations: {obs}{more}")
    L.append("")
    L.append("=== FIXPOINT ITERATE (extract -> re-intern -> extract; dual: toward the primitive basis) ===")
    if not result["fixpoint_iterate"]:
        L.append("  (empty)")
    for lvl in result["fixpoint_iterate"]:
        heads = defaultdict(int)
        for nid, ct, sz, head in lvl["candidates"]:
            heads[_head_str(head)] += 1
        top = sorted(heads.items(), key=lambda kv: -kv[1])[:8]
        L.append(f"  level {lvl['depth']}: {lvl['n_carriers']} carriers -> "
                 f"{len(lvl['candidates'])} shared subtrees; top heads: "
                 + ", ".join(f"{h}({n})" for h, n in top))
    L.append(f"  -> converged after {len(result['fixpoint_iterate'])} level(s) (SPPF is bottom-up complete).")
    return "\n".join(L)


# --------------------------------------------------------------------------- CLI
def expand(paths):
    out = []
    for p in paths:
        if any(ch in p for ch in "*?["):
            out.extend(glob_mod.glob(p, recursive=True))
        else:
            out.append(p)
    return sorted(set(out))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="Python files/globs and/or Agda .agdai cores")
    ap.add_argument("--min-fanin", type=int, default=3,
                    help="min UNITS sharing a subtree for it to be a candidate (default 3)")
    ap.add_argument("--min-size", type=int, default=5,
                    help="min subtree node count (trivial-node gate, default 5)")
    ap.add_argument("--raw-fanin", action="store_true",
                    help="rank by raw reference fan-in (incl. intra-unit repeats) instead of cross-unit membership")
    ap.add_argument("--max-depth", type=int, default=8, help="fixpoint-iterate depth guard (default 8)")
    ap.add_argument("--json", action="store_true", help="emit the rung-DAG as JSON (the LLM accelerator)")
    args = ap.parse_args(argv)

    files = expand(args.files)
    if not files:
        ap.error("no input files")
    C = build_corpus(files)
    result, _ = build_path(C, args.min_fanin, args.min_size,
                           cross_unit=not args.raw_fanin, max_depth=args.max_depth)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
