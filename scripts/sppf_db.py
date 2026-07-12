#!/usr/bin/env python3
"""sppf_db.py — the SPPF lives IN catalog.db, one content-addressed interner. base64 replaces the ints.

Every id is base64(the thing it addresses) — replacing the autonumber ints uniformly, so interning is
idempotent + concurrency-safe BY CONSTRUCTION (same content → same id across catalog + SPPF + every
file; INSERT OR IGNORE dedups with no autonumber coordination, no race):

  • TERM (atomic string)  → base64(text).                    Bounded ∵ a term is a bounded string.
  • PATH (a qname)        → base64(qname); segments in path_seg.
  • NODE (a symbol node)  → base64(head = kind‖role‖op‖lit).  Bounded ∵ the head is bounded.

The node is content-addressed by ITS OWN HEAD, not its subtree — you don't content-address a flattened
tree (measured: base64(head‖children) blows up to 61 MB, no bounded fixed point). Structural nodes that
share a head SHARE the symbol-node id; their distinct child-sets are PACKED as edges in node_child (the
relationships, encoded SEPARATELY). That packing IS the hash-cons — an SPPF represents a large forest
compactly by sharing symbol nodes and packing derivations. The relation carries the depth; the id never
does ("deep is a path through node_child, not a string").

STREAMED, transaction-per-file: `SqlIntern` implements the jea_pyalg.Intern interface, so we reuse
jea_agdai.core_intern_agdai per core (lift, don't re-roll) and INSERT OR IGNORE + COMMIT per file.
"""
import sqlite3, sys, os, glob, base64

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))
from jea_agdai import core_intern_agdai, substrate_core_root
CATALOG_DB = os.path.join(_ROOT, "catalog", "catalog.db")

def _b64(s): return base64.b64encode(("" if s is None else s).encode("utf-8")).decode("ascii")

SPPF_SCHEMA = """
-- terms/path_seg are the catalog's shared interner tables; create IF NOT EXISTS so sppf_db is
-- self-sufficient (a fresh db) AND shares them when streaming into catalog.db. base64 ids make the
-- rows shared-by-construction either way (base64('Substrate') is the same id in both).
CREATE TABLE IF NOT EXISTS terms      (term_id TEXT PRIMARY KEY, text TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS ix_terms_text ON terms(text);
CREATE TABLE IF NOT EXISTS path_seg   (path_id TEXT, ord INT, seg_term_id TEXT);
CREATE TABLE IF NOT EXISTS _node      (node_id TEXT PRIMARY KEY, sym TEXT, kind_id TEXT, role_id TEXT, op_term_id TEXT, op_path_id TEXT, lit_id TEXT);
CREATE INDEX IF NOT EXISTS ix_node_sym ON _node(sym);
CREATE TABLE IF NOT EXISTS node_child (node_id TEXT, ord INT, child_id TEXT);
CREATE TABLE IF NOT EXISTS _unit      (unit_id TEXT PRIMARY KEY, name_pid TEXT, root_id TEXT, file_id TEXT);
CREATE TABLE IF NOT EXISTS unit_node  (unit_id TEXT, node_id TEXT);
CREATE INDEX IF NOT EXISTS ix_nc_node  ON node_child(node_id);
CREATE INDEX IF NOT EXISTS ix_nc_child ON node_child(child_id);
CREATE INDEX IF NOT EXISTS ix_un_unit  ON unit_node(unit_id);
CREATE INDEX IF NOT EXISTS ix_un_node  ON unit_node(node_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_un_edge ON unit_node(unit_id, node_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_nc_edge ON node_child(node_id, ord, child_id);
-- path_seg idempotency: a (path_id, ord) has exactly ONE segment (base64 path_id ⟹ fixed qname ⟹
-- fixed segment sequence). WITHOUT this, streaming INSERT OR IGNORE can't dedup and re-encounters of a
-- qname duplicate its segments (path_text then GROUP_CONCATs the dups → tripled names). The shared
-- table's content-addressing REQUIRES it. (Owner reuse_catalog dedups via a Python set in one build;
-- the streaming writer needs the constraint. ⟡catalog-pathseg-unique: hoist this to reuse_catalog.)
CREATE UNIQUE INDEX IF NOT EXISTS ix_pathseg_uniq ON path_seg(path_id, ord);
-- path_text may already exist (catalog builds it); create only if absent.
CREATE VIEW IF NOT EXISTS path_text AS
  SELECT path_id, GROUP_CONCAT(seg, '.') AS text FROM (
    SELECT ps.path_id, t.text AS seg FROM path_seg ps JOIN terms t ON t.term_id=ps.seg_term_id
    ORDER BY ps.path_id, ps.ord) GROUP BY path_id;
-- compat views: the readouts (sppf_query) query THESE by their pre-interning TEXT names.
CREATE VIEW IF NOT EXISTS node AS SELECT n.node_id, n.sym, k.text AS kind, r.text AS role,
    COALESCE(pt.text, o.text) AS op, l.text AS lit
  FROM _node n JOIN terms k ON k.term_id=n.kind_id JOIN terms r ON r.term_id=n.role_id
    JOIN terms l ON l.term_id=n.lit_id
    LEFT JOIN terms o ON o.term_id=n.op_term_id LEFT JOIN path_text pt ON pt.path_id=n.op_path_id;
CREATE VIEW IF NOT EXISTS unit AS SELECT u.unit_id, pt.text AS name, u.root_id AS root_id, f.text AS path
  FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid JOIN terms f ON f.term_id=u.file_id;
CREATE VIEW IF NOT EXISTS node_fanin AS SELECT child_id AS node_id, COUNT(*) AS fanin FROM node_child GROUP BY child_id;
CREATE VIEW IF NOT EXISTS shared_subtree AS SELECT node_id, fanin FROM node_fanin WHERE fanin >= 2;
CREATE VIEW IF NOT EXISTS node_atom AS SELECT n.node_id, n.op FROM node n
  WHERE NOT EXISTS (SELECT 1 FROM node_child c WHERE c.node_id=n.node_id);
"""


class SqlIntern:
    """jea_pyalg.Intern interface, content-addressed (base64), streaming into catalog.db."""
    def __init__(self, con):
        self.con = con
        self.trows, self.prows, self.nrows, self.ncrows = [], [], [], []
        self._seen_t, self._seen_n, self._seen_e = set(), set(), set()
        self._sym_of = {}         # packing node_id -> its reentrant symbol base64(head) (bounded base case)

    def tid(self, s):             # a TERM (atomic string) — content-addressed base64 (bounded, shared)
        s = "" if s is None else s
        cid = _b64(s)
        if cid not in self._seen_t:
            self._seen_t.add(cid); self.trows.append((cid, s))
        return cid

    def pid(self, s):             # a qname is a PATH: id = base64(qname); segments live in path_seg
        cid = _b64(s)
        for o, seg in enumerate(s.split(".")):
            self.prows.append((cid, o, self.tid(seg)))
        return cid

    def intern(self, node):       # node = IR; node.children = child NODE ids (packing ids) we returned
        # base64 of the UNIQUE key (head + child refs) — replacing ONLY the autonumber. The key's child
        # refs are the children's SYMBOLS (base64(head)), the bounded reentrant base case — so the key
        # is normalized (not self-referentially composite → not the 61MB blowup) yet still DISTINGUISHES
        # by (head, immediate-child-heads). The RELATIONSHIPS (which specific child packing) live in the
        # node_child BRIDGE. A node is the SPPF PACKING; its `sym` is the reentrant symbol it packs under.
        sym = _b64("\x00".join([node.kind, node.role, node.op, node.lit]))
        child_syms = [self._sym_of[ch] for ch in node.children]
        nid = _b64("\x00".join([node.kind, node.role, node.op, node.lit, ",".join(child_syms)]))
        self._sym_of[nid] = sym
        if nid not in self._seen_n:
            self._seen_n.add(nid)
            op = node.op or ""
            ot, opp = (None, self.pid(op)) if "." in op else (self.tid(op), None)
            self.nrows.append((nid, sym, self.tid(node.kind), self.tid(node.role), ot, opp, self.tid(node.lit)))
        for o, ch in enumerate(node.children):      # BRIDGE: this packing → the SPECIFIC child packing
            e = (nid, o, ch)
            if e not in self._seen_e:
                self._seen_e.add(e); self.ncrows.append(e)
        return nid                # the packing id; parents embed its SYMBOL (via _sym_of) → bounded

    def size(self): return len(self._seen_n)

    def flush(self):              # transaction-per-file: INSERT OR IGNORE + COMMIT
        c = self.con
        c.executemany("INSERT OR IGNORE INTO terms    VALUES (?,?)",       self.trows)
        c.executemany("INSERT OR IGNORE INTO path_seg VALUES (?,?,?)",     self.prows)
        c.executemany("INSERT OR IGNORE INTO _node    VALUES (?,?,?,?,?,?,?)", self.nrows)
        c.executemany("INSERT OR IGNORE INTO node_child VALUES (?,?,?)",   self.ncrows)
        c.commit()
        self.trows, self.prows, self.nrows, self.ncrows = [], [], [], []


def build(cores, catalog_db=CATALOG_DB):
    con = sqlite3.connect(catalog_db)
    # reset sppf objects so the schema rebuilds cleanly regardless of prior state (the sppf tables are
    # fully rebuilt each run, so DROP — not DELETE — picks up any column/definition change). Drop the
    # right kind (a name may be a stale TABLE from old iterations or a VIEW/table from this schema).
    # NEVER drop terms/path_seg (shared with the catalog).
    for name in ("node", "unit", "path_text", "node_fanin", "shared_subtree", "node_atom",
                 "unit_node", "node_child", "_node", "_unit"):
        row = con.execute("SELECT type FROM sqlite_master WHERE name=?", (name,)).fetchone()
        if row:
            con.execute(f"DROP {row[0].upper()} IF EXISTS {name}")
    con.commit()
    # self-heal any path_seg duplication (from a pre-unique-index build) BEFORE the schema's UNIQUE index
    # is created — but path_seg must exist first, so ensure the shared tables, then dedup, then the rest.
    con.executescript("CREATE TABLE IF NOT EXISTS terms (term_id TEXT PRIMARY KEY, text TEXT);"
                      "CREATE TABLE IF NOT EXISTS path_seg (path_id TEXT, ord INT, seg_term_id TEXT);")
    con.execute("""DELETE FROM path_seg WHERE rowid NOT IN
                   (SELECT MIN(rowid) FROM path_seg GROUP BY path_id, ord)""")
    con.commit()
    con.executescript(SPPF_SCHEMA)
    sql = SqlIntern(con)
    units, un_rows = [], []
    for path in cores:
        try:
            rep = core_intern_agdai(path, sql)
        except Exception:
            sql.flush(); continue
        um = rep.get("unit_members", {})
        for name, root in rep["units"]:
            units.append((name, root, path))
            uid = _b64(name)
            un_rows += [(uid, nid) for nid in um.get(name, ())]   # membership, captured pre-sharing
        sql.flush()                          # one transaction per file
    urows = [(_b64(n), sql.pid(n), r, sql.tid(p)) for (n, r, p) in units]
    sql.con.executemany("INSERT OR IGNORE INTO terms VALUES (?,?)", sql.trows)
    sql.con.executemany("INSERT OR IGNORE INTO path_seg VALUES (?,?,?)", sql.prows)
    con.executemany("INSERT OR IGNORE INTO _unit VALUES (?,?,?,?)", urows)
    # unit_node = per-unit SUPPORT as intern-time MEMBERSHIP (rep.unit_members), NOT a closure over the
    # shared bridge. Closure would cross-product/cycle through shared packings (it filled the disk); the
    # membership was captured on the acyclic original term, so it is the correct, bounded support set.
    con.executemany("INSERT OR IGNORE INTO unit_node VALUES (?,?)", un_rows)
    con.commit()
    stats = (sql.size(), len(units),
             con.execute("SELECT COUNT(*) FROM shared_subtree").fetchone()[0],
             con.execute("SELECT MAX(LENGTH(node_id)) FROM _node").fetchone()[0])
    con.close()
    return stats


if __name__ == "__main__":
    filt = sys.argv[1] if len(sys.argv) > 1 else "Category"
    base = substrate_core_root(os.path.join(_ROOT, "agda"))
    cores = [c for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True)) if filt in c]
    print(f"streaming {len(cores)} cores (filter={filt!r}) INTO catalog.db (shared base64 interner) …")
    n, u, sh, maxlen = build(cores)
    print(f"  catalog.db now contains: {n} SPPF nodes, {u} units, {sh} shared subtrees; MAX node_id len={maxlen}")
