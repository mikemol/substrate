#!/usr/bin/env python3
"""sppf_query.py — ⟡jea-pysim-query-db: jea_pysim's readouts, AS SQL over the resident SPPF.

The catalog_query analogue for the SPPF (scripts/sppf_db.py). jea_pysim computed support / fan-in /
shared-subtrees / extract-candidates / clusters as PYTHON graph-walks over an in-memory interner;
here each is a SELECT/JOIN/GROUP BY over the db that CONTAINS the SPPF. A new SPPF question is a
SELECT, not a new pass. (If a question needs Python, the SPPF model isn't expressive enough — the
same test the catalog uses.)

  support <unit>      support size + the head-op histogram of a unit's subterms   (was _support walk)
  fanin [k]           the most-shared nodes (fan-in = hash-cons corroboration)     (was I.fanin scan)
  extract [minunits]  subtrees shared by ≥ minunits distinct units (the apex)      (was the extract pass)
  clusters <unit> [t] units whose support overlaps <unit> by ≥ t fraction          (was the cluster pass)
  reuse [minunits]    consolidation candidates + the defCopy verdict (CONSOLIDATED/DUP/MIXED)
  sql "<query>"       arbitrary READ-ONLY SQL over the SPPF db
"""
import sqlite3, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jea", "metalanguage"))
import query_builders as QB               # ⟡query-rawtocore: single-source Core builders (run = execute)

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "catalog", "catalog.db")

def _con():
    if not os.path.exists(DB):
        sys.exit(f"no SPPF db at {DB} — build it: python3 scripts/sppf_db.py <filter>")
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def _uid(c, name):
    r = QB.run(c, "uid", name=name, likep="%."+name).fetchone()
    return r["unit_id"] if r else None

def cmd_support(c, a):
    uid = _uid(c, a[0])
    if uid is None: sys.exit(f"no unit matching {a[0]!r}")
    n = QB.run(c, "support_count", uid=uid).fetchone()["k"]
    print(f"support: {n} interned subterm nodes")
    for r in QB.run(c, "support_hist", uid=uid):
        print(f"   {r['k']:4d}  {r['head'][:60]}")

def cmd_fanin(c, a):
    k = int(a[0]) if a else 15
    for r in QB.run(c, "fanin", lim=k):
        print(f"  fan-in {r['fanin']:5d}  node {str(r['node_id'])[:10]:>10}  {r['head'][:55]}")

def cmd_extract(c, a):
    # the parametric-helper apex: a subtree shared across ≥ minunits DISTINCT units — a GROUP BY.
    m = int(a[0]) if a else 3
    for r in QB.run(c, "extract", m=m):
        print(f"  in {r['units']:4d} units  node {str(r['node_id'])[:10]:>10}  {r['head'][:50]}")

def cmd_clusters(c, a):
    uid = _uid(c, a[0])
    if uid is None: sys.exit(f"no unit matching {a[0]!r}")
    thr = float(a[1]) if len(a) > 1 else 0.6
    sz = QB.run(c, "support_count", uid=uid).fetchone()["k"]
    # coherent fraction = |shared| / |support(u)| — a JOIN + GROUP BY, not a pairwise Python pass.
    for r in QB.run(c, "clusters_overlap", sz=sz, uid=uid, thr=thr):
        print(f"   {r['shared']*1.0/sz:.2f}  ({r['shared']}/{sz})  {r['name'].split('.')[-1]}")

def has_copy(c):
    """is the defCopy provenance column present? (a catalog.db built with the current sppf_db)."""
    return any(r["name"] == "copy" for r in c.execute("PRAGMA table_info(_unit)"))

def reuse_rows(c, min_units=3, limit=None):
    """Consolidation candidates AS ONE query (no re-intern): composite subtrees shared by ≥min_units
    DISTINCT units, each with the defCopy verdict — all instances are module-instantiation copies ⇒
    CONSOLIDATED; none are ⇒ genuine DUP (independent originals sharing structure = the target); else
    MIXED. copies is NULL and verdict '?' if the db predates the copy column."""
    # single-source: two static named variants (⟡qinfra ⟡q-reuse-rows-copy/-nocopy); lim=-1 ≡ no limit.
    out = []
    name = "reuse_rows_copy" if has_copy(c) else "reuse_rows_nocopy"
    for r in QB.run(c, name, min_units=min_units, lim=(-1 if limit is None else int(limit))):
        cc = r["copies"]
        verdict = ("?" if cc is None else "CONSOLIDATED" if cc == r["units"]
                   else "DUP" if cc == 0 else "MIXED")
        out.append({"node_id": r["node_id"], "head": r["head"] or "?",
                    "units": r["units"], "copies": cc, "verdict": verdict})
    return out

def cmd_reuse(c, a):
    m = int(a[0]) if a else 3
    if not has_copy(c):
        print("  ⚠ this catalog.db has no defCopy provenance — rebuild it (python3 scripts/sppf_db.py \"\") "
              "for the consolidated-vs-dup verdict; showing counts only.\n")
    for r in reuse_rows(c, m, limit=25):
        mark = {"CONSOLIDATED": "✓", "DUP": "✗", "MIXED": "·"}.get(r["verdict"], "?")
        cp = "" if r["copies"] is None else f" ({r['copies']}/{r['units']} copies)"
        print(f"  {mark} {r['verdict']:12s} {r['units']:4d} units{cp}  {r['head'][:44]}")

def cmd_sql(c, a):
    for row in c.execute(a[0]):
        print("  " + " | ".join(str(x) for x in row))

CMDS = {"support": cmd_support, "fanin": cmd_fanin, "extract": cmd_extract,
        "clusters": cmd_clusters, "reuse": cmd_reuse, "sql": cmd_sql}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.exit(f"usage: sppf_query.py <{'|'.join(CMDS)}> [args]")
    c = _con()
    CMDS[sys.argv[1]](c, sys.argv[2:])
