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
-- ⟡db-contains-sppf + ⟡sppf-op-path-ids: node heads are interned. kind/role/lit are TERM ids ('AgdaCore'
-- once, not per node). `op` is POLYMORPHIC — a constructor (atomic) OR a qname (a PATH) — so it is SPLIT:
-- op_term_id for atomic ops, op_path_id for qname paths (a surrogate path id; segments in path_seg;
-- string DERIVED via path_text, never stored flat, like the catalog). unit.name is a qname → a path id
-- too; unit.path is a FILE path → an atomic term (slashes, not a namespace path). Compat VIEWS re-present
-- TEXT so the readouts are unchanged.
CREATE TABLE terms      (term_id INTEGER PRIMARY KEY, text TEXT);
CREATE UNIQUE INDEX ix_terms_text ON terms(text);
CREATE TABLE path_seg   (path_id INT, ord INT, seg_term_id INT);
CREATE TABLE _node      (node_id INTEGER PRIMARY KEY, kind_id INT, role_id INT, op_term_id INT, op_path_id INT, lit_id INT);
CREATE TABLE node_child (node_id INT, ord INT, child_id INT);
CREATE TABLE _unit      (unit_id INTEGER PRIMARY KEY, name_pid INT, root_id INT, file_id INT);
-- unit_node: each unit's SUPPORT closure, materialized ONCE via a recursive WITH at build — so the
-- cross-unit readouts (extract/clusters/shared-fraction) are direct JOIN/GROUP BY, no per-query walk.
CREATE TABLE unit_node  (unit_id INT, node_id INT);
CREATE INDEX ix_nc_node   ON node_child(node_id);
CREATE INDEX ix_nc_child  ON node_child(child_id);
CREATE INDEX ix_node_op   ON _node(op_term_id);
CREATE INDEX ix_node_oppath ON _node(op_path_id);
CREATE INDEX ix_unit_root ON _unit(root_id);
CREATE INDEX ix_un_unit   ON unit_node(unit_id);
CREATE INDEX ix_un_node   ON unit_node(node_id);
CREATE INDEX ix_pathseg   ON path_seg(path_id);
CREATE VIEW path_text AS
  SELECT path_id, GROUP_CONCAT(seg, '.') AS text FROM (
    SELECT ps.path_id, t.text AS seg FROM path_seg ps JOIN terms t ON t.term_id=ps.seg_term_id
    ORDER BY ps.path_id, ps.ord) GROUP BY path_id;
-- compat views: the pre-interning TEXT schema (the readouts query THESE). op = the path (if a qname)
-- else the atomic term.
CREATE VIEW node AS SELECT n.node_id, k.text AS kind, r.text AS role,
    COALESCE(pt.text, o.text) AS op, l.text AS lit
  FROM _node n JOIN terms k ON k.term_id=n.kind_id JOIN terms r ON r.term_id=n.role_id
    JOIN terms l ON l.term_id=n.lit_id
    LEFT JOIN terms o ON o.term_id=n.op_term_id
    LEFT JOIN path_text pt ON pt.path_id=n.op_path_id;
CREATE VIEW unit AS SELECT u.unit_id, pt.text AS name, u.root_id AS root_id, f.text AS path
  FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid JOIN terms f ON f.term_id=u.file_id;
CREATE VIEW node_fanin AS SELECT child_id AS node_id, COUNT(*) AS fanin FROM node_child GROUP BY child_id;
CREATE VIEW shared_subtree AS SELECT node_id, fanin FROM node_fanin WHERE fanin >= 2;
CREATE VIEW node_atom AS SELECT n.node_id, n.op FROM node n
  WHERE NOT EXISTS (SELECT 1 FROM node_child c WHERE c.node_id=n.node_id);
-- flattening watch: any dotted term still held FLAT (the op/name qnames are now path ids, so what
-- remains is FILE paths — a different, non-namespace path kind — the honest residue).
CREATE VIEW flattened_terms AS SELECT text FROM terms WHERE text LIKE '%.%';
"""

def build(cores, dbpath):
    """Intern `cores` into a fresh Corpus, then persist. (jea_pysim --persist calls persist_corpus
    directly on the Corpus it already built — lift, don't re-intern.)"""
    C = Corpus()
    for c in cores:
        C.add_agdai(c)
    return persist_corpus(C, dbpath)


def persist_corpus(C, dbpath):
    """Persist an already-interned Corpus's SPPF into the db — the shared writer. jea_pysim is then a
    thin BUILDER (front-end: shim → intern → persist) and sppf_query is the analysis."""
    I = C.I
    if os.path.exists(dbpath):
        os.remove(dbpath)
    con = sqlite3.connect(dbpath)
    con.executescript(SCHEMA)
    _terms, _paths = {}, {}
    def tid(s):
        s = "" if s is None else s
        i = _terms.get(s)
        if i is None:
            i = len(_terms); _terms[s] = i
        return i
    def pid(s):                                   # a qname is a PATH: surrogate id over interned segments
        segs = tuple(tid(seg) for seg in s.split("."))
        p = _paths.get(segs)
        if p is None:
            p = len(_paths); _paths[segs] = p
        return p
    def op_ids(op):                               # op is polymorphic: a qname (path) OR an atomic ctor
        op = "" if op is None else op
        return (None, pid(op)) if "." in op else (tid(op), None)
    node_rows = []
    for i, n in enumerate(I.nodes):
        ot, opp = op_ids(n.op)
        node_rows.append((i, tid(n.kind), tid(n.role), ot, opp, tid(n.lit)))
    unit_rows = [(k, pid(u.name), u.root, tid(u.path)) for k, u in enumerate(C.units)]  # name=path, path=file term
    pathseg_rows = [(p, o, seg) for segs, p in _paths.items() for o, seg in enumerate(segs)]
    term_rows = sorted((i, s) for s, i in _terms.items())
    con.executemany("INSERT INTO terms VALUES (?,?)", term_rows)
    con.executemany("INSERT INTO path_seg VALUES (?,?,?)", pathseg_rows)
    con.executemany("INSERT INTO _node VALUES (?,?,?,?,?,?)", node_rows)
    con.executemany("INSERT INTO node_child VALUES (?,?,?)",
                    [(i, o, ch) for i, n in enumerate(I.nodes) for o, ch in enumerate(n.children)])
    con.executemany("INSERT INTO _unit VALUES (?,?,?,?)", unit_rows)
    con.commit()
    # materialize each unit's support closure ONCE (the recursive WITH the readouts would otherwise
    # re-walk per query, in Python) — the "query, don't code" enabler.
    con.execute("""
        INSERT INTO unit_node
        WITH RECURSIVE r(unit_id, node_id) AS (
          SELECT unit_id, root_id FROM _unit
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
