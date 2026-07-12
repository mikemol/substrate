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
  sql "<query>"       arbitrary READ-ONLY SQL over the SPPF db
"""
import sqlite3, sys, os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "catalog", "catalog.db")

def _con():
    if not os.path.exists(DB):
        sys.exit(f"no SPPF db at {DB} — build it: python3 scripts/sppf_db.py <filter>")
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def _uid(c, name):
    r = c.execute("SELECT unit_id FROM unit WHERE name=? OR name LIKE ?", (name, "%."+name)).fetchone()
    return r["unit_id"] if r else None

def cmd_support(c, a):
    uid = _uid(c, a[0])
    if uid is None: sys.exit(f"no unit matching {a[0]!r}")
    n = c.execute("SELECT COUNT(*) k FROM unit_node WHERE unit_id=?", (uid,)).fetchone()["k"]
    print(f"support: {n} interned subterm nodes")
    for r in c.execute("""SELECT COALESCE(NULLIF(nd.op,''), nd.role, nd.kind) head, COUNT(*) k
                          FROM unit_node un JOIN node nd ON nd.node_id=un.node_id
                          WHERE un.unit_id=? GROUP BY head ORDER BY k DESC LIMIT 12""", (uid,)):
        print(f"   {r['k']:4d}  {r['head'][:60]}")

def cmd_fanin(c, a):
    k = int(a[0]) if a else 15
    for r in c.execute("""SELECT nf.node_id, COALESCE(NULLIF(nd.op,''),nd.role,nd.kind) head, nf.fanin
                          FROM node_fanin nf JOIN node nd ON nd.node_id=nf.node_id
                          ORDER BY nf.fanin DESC LIMIT ?""", (k,)):
        print(f"  fan-in {r['fanin']:5d}  node {str(r['node_id'])[:10]:>10}  {r['head'][:55]}")

def cmd_extract(c, a):
    # the parametric-helper apex: a subtree shared across ≥ minunits DISTINCT units — a GROUP BY.
    m = int(a[0]) if a else 3
    for r in c.execute("""SELECT un.node_id, COALESCE(NULLIF(nd.op,''),nd.role,nd.kind) head,
                                 COUNT(DISTINCT un.unit_id) units
                          FROM unit_node un JOIN node nd ON nd.node_id=un.node_id
                          WHERE nd.node_id IN (SELECT node_id FROM node_child)   -- composite (has children)
                          GROUP BY un.node_id HAVING units >= ? ORDER BY units DESC LIMIT 20""", (m,)):
        print(f"  in {r['units']:4d} units  node {str(r['node_id'])[:10]:>10}  {r['head'][:50]}")

def cmd_clusters(c, a):
    uid = _uid(c, a[0])
    if uid is None: sys.exit(f"no unit matching {a[0]!r}")
    thr = float(a[1]) if len(a) > 1 else 0.6
    sz = c.execute("SELECT COUNT(*) k FROM unit_node WHERE unit_id=?", (uid,)).fetchone()["k"]
    # coherent fraction = |shared| / |support(u)| — a JOIN + GROUP BY, not a pairwise Python pass.
    for r in c.execute("""SELECT v.name, COUNT(*) shared, ? sz
                          FROM unit_node a JOIN unit_node b ON a.node_id=b.node_id
                          JOIN unit v ON v.unit_id=b.unit_id
                          WHERE a.unit_id=? AND b.unit_id!=?
                          GROUP BY b.unit_id HAVING (1.0*shared/?) >= ?
                          ORDER BY shared DESC LIMIT 15""",
                       (sz, uid, uid, sz, thr)):
        print(f"   {r['shared']*1.0/sz:.2f}  ({r['shared']}/{sz})  {r['name'].split('.')[-1]}")

def cmd_sql(c, a):
    for row in c.execute(a[0]):
        print("  " + " | ".join(str(x) for x in row))

CMDS = {"support": cmd_support, "fanin": cmd_fanin, "extract": cmd_extract,
        "clusters": cmd_clusters, "sql": cmd_sql}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in CMDS:
        sys.exit(f"usage: sppf_query.py <{'|'.join(CMDS)}> [args]")
    c = _con()
    CMDS[sys.argv[1]](c, sys.argv[2:])
