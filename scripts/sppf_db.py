#!/usr/bin/env python3
"""sppf_db.py — ⟡db-contains-sppf: the SQL database CONTAINS the SPPF.

The interner's store IS the db. `jea_pyalg.Intern` hash-conses term nodes in memory (self.nodes /
self.table); here the SAME hash-cons is PERSISTED as rows — node(head) + node_child(ordered edges) —
so the pipeline's path/homotopy searches become recursive-CTE QUERIES instead of Python graph-walks:

  * fan-in (the SHARING / hash-cons corroboration signal) = COUNT over node_child.child_id
  * support of a unit (reachable subterm set) = a recursive WITH from its root over node_child
  * a shared subtree (the dedup) = node_fanin >= 2, a SELECT — not a stack-walk
  * two units' shared structure (clustering) = a JOIN of their supports

This is the TERM-level layer of the SAME hash-cons the catalog's `terms`/`path_seg` already are (the
coarse layer): `unit.root_id` points INTO the node forest, continuous with the struct catalog. The
db is the SPPF's home; writing Python over an in-memory forest is the signal it isn't interned yet.
"""
import sqlite3, sys, os, glob

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))
from jea_pysim import Corpus   # its Corpus.add_agdai drives jea_agdai.core_intern_agdai into ONE Intern

SCHEMA = """
-- ⟡db-contains-sppf, normalized like the catalog: node heads are TERM IDS (kind/role/op/lit interned
-- once — 'AgdaCore' is stored once, not per node), a dotted op/name (a qname = a PATH) is decomposed
-- into interned segments (path_seg), and compat VIEWS re-present the TEXT so the readouts are unchanged.
CREATE TABLE terms      (term_id INTEGER PRIMARY KEY, text TEXT);
CREATE UNIQUE INDEX ix_terms_text ON terms(text);
CREATE TABLE path_seg   (path_term_id INT, ord INT, seg_term_id INT);
CREATE TABLE _node      (node_id INTEGER PRIMARY KEY, kind_id INT, role_id INT, op_id INT, lit_id INT);
CREATE TABLE node_child (node_id INT, ord INT, child_id INT);
CREATE TABLE _unit      (unit_id INTEGER PRIMARY KEY, name_id INT, root_id INT, path_id INT);
-- unit_node: each unit's SUPPORT closure (the reachable subterm set), materialized ONCE via a
-- recursive WITH at build. With it the cross-unit readouts jea_pysim did in Python — extract
-- candidates, clusters, shared-fraction — are direct JOIN/GROUP BY, no per-query graph-walk.
CREATE TABLE unit_node  (unit_id INT, node_id INT);
CREATE INDEX ix_nc_node   ON node_child(node_id);
CREATE INDEX ix_nc_child  ON node_child(child_id);
CREATE INDEX ix_node_op   ON _node(op_id);
CREATE INDEX ix_unit_root ON _unit(root_id);
CREATE INDEX ix_un_unit   ON unit_node(unit_id);
CREATE INDEX ix_un_node   ON unit_node(node_id);
CREATE INDEX ix_pathseg   ON path_seg(path_term_id);
-- compat views: the pre-interning TEXT schema (the readouts query THESE).
CREATE VIEW node AS SELECT n.node_id, k.text AS kind, r.text AS role, o.text AS op, l.text AS lit
  FROM _node n JOIN terms k ON k.term_id=n.kind_id JOIN terms r ON r.term_id=n.role_id
    JOIN terms o ON o.term_id=n.op_id JOIN terms l ON l.term_id=n.lit_id;
CREATE VIEW unit AS SELECT u.unit_id, nm.text AS name, u.root_id AS root_id, p.text AS path
  FROM _unit u JOIN terms nm ON nm.term_id=u.name_id JOIN terms p ON p.term_id=u.path_id;
-- fan-in: how many parent EDGES reference a node = the sharing (hash-cons corroboration) signal.
CREATE VIEW node_fanin AS SELECT child_id AS node_id, COUNT(*) AS fanin FROM node_child GROUP BY child_id;
-- a SHARED SUBTREE = a node reachable from ≥2 parents (the dedup, as a SELECT not a Python walk).
CREATE VIEW shared_subtree AS SELECT node_id, fanin FROM node_fanin WHERE fanin >= 2;
CREATE VIEW node_atom AS SELECT n.node_id, n.op FROM node n
  WHERE NOT EXISTS (SELECT 1 FROM node_child c WHERE c.node_id=n.node_id);
-- flattening watch: op/name terms that still hold a dotted PATH (should be a path_seg, not a flat term).
CREATE VIEW flattened_terms AS SELECT text FROM terms WHERE text LIKE '%.%';
"""

def build(cores, dbpath):
    C = Corpus()
    for c in cores:
        C.add_agdai(c)
    I = C.I
    if os.path.exists(dbpath):
        os.remove(dbpath)
    con = sqlite3.connect(dbpath)
    con.executescript(SCHEMA)
    _terms = {}
    def tid(s):
        s = "" if s is None else s
        i = _terms.get(s)
        if i is None:
            i = len(_terms); _terms[s] = i
        return i
    node_rows = [(i, tid(n.kind), tid(n.role), tid(n.op), tid(n.lit)) for i, n in enumerate(I.nodes)]
    unit_rows = [(k, tid(u.name), u.root, tid(u.path)) for k, u in enumerate(C.units)]
    # ⟡ flattening watch: decompose dotted op/name terms (a qname IS a path) into interned segments.
    dotted = {s for s in _terms if "." in s and "/" not in s}      # qnames, not filesystem paths
    pathseg_rows = [(_terms[s], o, tid(seg)) for s in dotted for o, seg in enumerate(s.split("."))]
    term_rows = sorted((i, s) for s, i in _terms.items())
    con.executemany("INSERT INTO terms VALUES (?,?)", term_rows)
    con.executemany("INSERT INTO path_seg VALUES (?,?,?)", pathseg_rows)
    con.executemany("INSERT INTO _node VALUES (?,?,?,?,?)", node_rows)
    con.executemany("INSERT INTO node_child VALUES (?,?,?)",
                    [(i, o, ch) for i, n in enumerate(I.nodes) for o, ch in enumerate(n.children)])
    con.executemany("INSERT INTO _unit VALUES (?,?,?,?)", unit_rows)
    con.commit()
    # materialize each unit's support closure ONCE (the recursive WITH the readouts would otherwise
    # re-walk per query, in Python) — the "query, don't code" enabler.
    con.execute("""
        INSERT INTO unit_node
        WITH RECURSIVE r(unit_id, node_id) AS (
          SELECT unit_id, root_id FROM unit
          UNION
          SELECT r.unit_id, ch.child_id FROM node_child ch JOIN r ON ch.node_id = r.node_id)
        SELECT unit_id, node_id FROM r;""")
    con.commit()
    stats = (I.size(), len(C.units),
             con.execute("SELECT COUNT(*) FROM shared_subtree").fetchone()[0],
             con.execute("SELECT COUNT(*) FROM unit_node").fetchone()[0])
    con.close()
    return stats

# ─── the SEARCHES, AS SQL (what used to be Python graph-walks over the in-memory interner) ───
Q_SUPPORT = """  -- support of a unit's root = its reachable subterm set (a recursive WITH, not a stack)
WITH RECURSIVE supp(node_id) AS (
  SELECT root_id FROM unit WHERE name = :name
  UNION
  SELECT c.child_id FROM node_child c JOIN supp s ON c.node_id = s.node_id)
SELECT COUNT(*) FROM supp;"""

Q_TOP_SHARED = """  -- the most-shared subtrees (the corroborated structure) — the dedup's raw signal
SELECT s.node_id, n.op, s.fanin FROM shared_subtree s JOIN node n ON n.node_id=s.node_id
ORDER BY s.fanin DESC LIMIT :k;"""

if __name__ == "__main__":
    filt = sys.argv[1] if len(sys.argv) > 1 else "Category"
    db = os.path.join(_ROOT, "catalog", "sppf.db")
    root = os.path.join(_ROOT, "agda", "_build")
    vers = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d, "agda")))
    base = os.path.join(root, vers[-1], "agda", "Substrate")
    cores = [c for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True)) if filt in c]
    print(f"interning {len(cores)} cores (filter={filt!r}) INTO the db …")
    nodes, units, shared, closure = build(cores, db)
    print(f"  db contains: {nodes} SPPF nodes, {units} units, {shared} shared subtrees, "
          f"{closure} unit-node support pairs -> {db}")
