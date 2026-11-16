#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""set1_consolidate.py — ⟡set1-consolidate-report: the operationalized dedup, applied to the Set₁ ratchet.

Groups every remaining Set₁ (level≥1) def by the CANONICAL RECORD its TYPE inhabits — the record whose
carrier-reparameterize (Set-field → type-parameter, set1-carrier-always-parameterize) would drain the whole
orbit of instances — ranked by defs-drained. Turns the name-heuristic "unclassified" bucket (set1_sweep's
blind spot) into a structure-driven consolidation worklist:
    "reparameterize RECORD X → drains N Set₁ defs: [instances]".

THE SIGNAL (correct, semantic — not the shared-subtree AST floor): a Set₁ record-instance
`F2-CommutativeMonoid : CommutativeMonoid F₂ …` inhabits the record `CommutativeMonoid`. The def's core is a
`Defn [type, clause]`; `type`'s HEAD symbol IS the inhabited record. Grouping by that head reproduces the
research's ~5-6 canonical records (CommutativeMonoid / LanguageWitness / PrimeFactoredGauge / DescentTree …),
where a shared-subtree grouping fragments each record's orbit across universal Fin/Vec/Product nodes.

REUSES (no new engine — FIND is already built):
  * jea_agdai.decode_core — the ONE canonical shim-decode (⟡lift-shared-core-machinery): cwd + locale
    invariants in one place; returns {defmarks:[rec,…], nodes:{id:rec}}, qname refs intact.
  * graded_orbit.orbit_cosets — the MERGE-vs-parameterize graded verdict (from `_orbit_def`, populated by
    sppf_db.py --argperm / ⟡orbit-projections-on); degrades gracefully to no graded tag when absent.

Self-contained (no reuse_tui / no Textual on the import path); read-only; prints to stdout.
"""
import os, sys, glob
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGDA = os.path.join(ROOT, "agda")
BUILD = os.path.join(AGDA, "_build", "2.8.0", "agda")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))

# Heads that are NOT consolidation targets: the def's type resolves to a universe / bound var / a
# universal Foundation primitive (a genuinely Vec/Fin/Nat-typed Set₁ def is a floor leaf, not a record orbit).
_LEAF_HEADS = {"(Sort)", "(Var)", None}
_FLOOR_PREFIXES = ("Substrate.Foundation.",)


def type_head(nodes, root):
    """The HEAD symbol of a def's TYPE = the record/data it inhabits. `root` is a `Defn [type, clause]`;
    peel the type node through Pi (codomain = last child) / App (function = first child) to the head
    Def/Con/Prim qname. Returns '(Sort)' for a Set-valued leaf, '(Var)' for a bound head, None on failure."""
    n = nodes.get(root) or nodes.get(str(root))
    if not n:
        return None
    kids = n.get("children") or []
    cur = kids[0] if (n.get("constructor") == "Defn" and kids) else root
    for _ in range(300):
        n = nodes.get(cur) or nodes.get(str(cur))
        if not n:
            return None
        ctor, kids = n.get("constructor"), (n.get("children") or [])
        if ctor in ("Def", "Con", "Prim", "PrimSort"):
            return n.get("qname")
        if ctor == "Sort":
            return "(Sort)"
        if ctor == "Var":
            return "(Var)"
        if ctor == "Pi":
            cur = kids[-1] if kids else None
        elif ctor in ("App", "Apply", "Abs"):
            cur = kids[0] if kids else None
        elif kids:
            cur = kids[0]
        else:
            return f"({ctor})"
        if cur is None:
            return None
    return None


def enumerate_set1():
    """[(qname, module, level, kind, thead, is_copy)] for every Set₁ (level≥1) def, via decode_core.
    is_copy = a module-instantiation/re-export COPY (drains derivatively when its ORIGINAL is edited)."""
    import jea_agdai as J
    out = []
    cores = sorted(glob.glob(os.path.join(BUILD, "**", "*.agdai"), recursive=True))
    for i, c in enumerate(cores):
        if i % 200 == 0:
            print(f"#   … {i}/{len(cores)} cores", file=sys.stderr)
        core = J.decode_core(c)
        if core is None:
            continue
        nodes = core["nodes"]
        rel = os.path.relpath(c, BUILD)
        mod = rel[:-len(".agdai")].replace(os.sep, ".")
        for d in core["defmarks"]:
            if isinstance(d.get("level"), int) and d["level"] >= 1:
                out.append((d["unit"], mod, d["level"], d.get("kind"),
                            type_head(nodes, d["root"]), bool(d.get("copy"))))
    return out


def qname_file(qn):
    """Resolve a record qname → its .agda file (longest existing module prefix). No reuse_tui/Textual."""
    if not qn or "." not in qn:
        return "?"
    parts = qn.split(".")
    for i in range(len(parts) - 1, 0, -1):
        f = os.path.join(AGDA, *parts[:i]) + ".agda"
        if os.path.exists(f):
            return os.path.relpath(f, ROOT)
    return "?"


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--min-drain", type=int, default=2, help="min instances for a record to list")
    args = ap.parse_args()

    print("# ⟡set1-consolidate-report — enumerating Set₁ defs via decode_core …", file=sys.stderr)
    s1 = enumerate_set1()
    S1 = {q for (q, *_ ) in s1}
    mods = {m for (_q, m, *_ ) in s1}
    n_orig = sum(1 for r in s1 if not r[5])
    n_copy = sum(1 for r in s1 if r[5])
    print(f"# {len(s1)} Set₁ (level≥1) defmarks across {len(mods)} modules "
          f"({n_orig} originals + {n_copy} re-export copies)", file=sys.stderr)

    # optional graded MERGE/parameterize verdict (needs _orbit_def; degrades to {} without it)
    graded_by_qname = {}
    try:
        import sqlite3, graded_orbit
        con = sqlite3.connect(os.path.join(ROOT, "catalog", "catalog.db"))
        cosets = graded_orbit.orbit_cosets(con) or {}
        graded_by_qname = {v["qname"]: v for v in cosets.values() if v.get("qname")}
    except Exception:
        pass

    # group Set₁ defs by the record their TYPE inhabits
    by_head = defaultdict(list)      # thead -> [(qname, module, kind, is_copy)]
    for (q, m, lvl, kind, thead, is_copy) in s1:
        by_head[thead].append((q, m, kind, is_copy))

    def norig(insts):
        return sum(1 for _q, _m, _k, cp in insts if not cp)

    records, leaves, floor = {}, {}, {}   # thead -> instances
    for thead, insts in by_head.items():
        if thead in _LEAF_HEADS or (isinstance(thead, str) and thead.startswith("(")):
            leaves[thead] = insts
        elif isinstance(thead, str) and thead.startswith(_FLOOR_PREFIXES):
            floor[thead] = insts
        else:
            records[thead] = insts

    def graded_verdict(qs):
        """MERGE if a type-orbit over these qnames collapses graded-keys (ng<n); else parameterize.
        Empty until _orbit_def is populated (⟡orbit-projections-on)."""
        by_tk = defaultdict(set)
        n = 0
        for q in qs:
            g = graded_by_qname.get(q)
            if not g:
                continue
            n += 1
            by_tk[g["type_key"]].add(g["graded_key"])
        if not n:
            return None
        ng = sum(len(v) for v in by_tk.values())
        return "graded-merge" if ng < n else "graded-param"

    ranked = sorted(records.items(), key=lambda kv: (-norig(kv[1]), -len(kv[1])))
    listed = [(h, i) for h, i in ranked if norig(i) >= args.min_drain]
    d_orig = sum(norig(i) for h, i in listed)
    d_copy = sum(len(i) - norig(i) for h, i in listed)
    print(f"\n# ═══ Set₁ CONSOLIDATION WORKLIST — {len(listed)} canonical records drain {d_orig} originals "
          f"(+{d_copy} re-export copies) — reparameterize the record's Set-carrier → the orbit lands at Set₀ ═══\n")
    for thead, insts in listed[:args.top]:
        origs = [q for q, _m, _k, cp in insts if not cp]
        ncp = len(insts) - len(origs)
        modspan = len({m for _q, m, _k, _c in insts})
        gv = graded_verdict([q for q, _m, _k, _c in insts])
        g = f"  [{gv}]" if gv else ""
        short = thead.rsplit(".", 1)[-1]
        cp = f" +{ncp}cp" if ncp else ""
        print(f"{len(origs):4}{cp:>6}  reparameterize  {short}{g}")
        print(f"        record: {thead.replace('Substrate.', '')}")
        print(f"        home-file: {qname_file(thead)}   spans {modspan} modules")
        show = sorted(set(origs))[:8]
        print(f"        drains: {', '.join(q.rsplit('.', 1)[-1] for q in show)}"
              f"{' …+%d' % (len(set(origs)) - 8) if len(set(origs)) > 8 else ''}")

    # the retype/leaf bucket (X-stated = Set, Het* type-equalities): type-head is a Sort/Var, not a record
    n_leaf = sum(len(i) for i in leaves.values())
    n_floor = sum(len(i) for i in floor.values())
    n_singleton = sum(len(i) for h, i in records.items() if norig(i) < args.min_drain)
    print(f"\n# ── retype/leaf bucket (type-head = Sort/Var — the `X-stated=Set` / Het* class): "
          f"{n_leaf} defs ──")
    for thead, insts in sorted(leaves.items(), key=lambda kv: -len(kv[1])):
        ex = ", ".join(q.rsplit(".", 1)[-1] for q, _m, _k, _c in insts[:4])
        print(f"    {len(insts):4}  {thead!s:8}  e.g. {ex}")
    print(f"\n# ── Foundation-primitive-typed (floor leaves, not record orbits): {n_floor} defs "
          f"across {len(floor)} heads ──")
    print(f"# ── record singletons (<{args.min_drain} originals — not orbit targets): {n_singleton} defs "
          f"across {sum(1 for h,i in records.items() if norig(i)<args.min_drain)} records ──")
    print(f"\n# TOTAL {len(s1)} Set₁ defmarks = {d_orig}+{d_copy}cp in listed records + "
          f"{n_singleton} record-singletons + {n_leaf} retype/leaf + {n_floor} floor")


if __name__ == "__main__":
    main()
