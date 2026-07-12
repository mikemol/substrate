#!/usr/bin/env python3
"""sppf_db.py — EVENT-SOURCED. sppf_db is an append-only WRITER of raw observations; the SPPF is the
intermediate PROJECTION derived from the events by query; the catalog + every other table become queries
against the SPPF projection.

An event = base64(one raw OBSERVATION) — the decoded node exactly as the shim emits it: {constructor,
qname, index, children:[LOCAL ids]}. Bounded by construction (one node's data, children as flat local ids,
NO resolution) — measured max ~312 chars. The 61MB "entire record" blowup came from base64-ing the
POST-PROCESSED record (children resolved to their subtree content-addresses = a Merkle hash); event
sourcing records the observation, not its post-processing. ALL structure-building — resolving refs, global
structural sharing, the SPPF packings — is the PROJECTION.

  write_events(cores)  → event / obs / edge / unit_obs      (append-only source of truth; bounded keys)
  project_sppf()       → _node / node_child / unit_node      (derived: the packing SPPF, by query)
  build(cores)         = write_events + project_sppf
"""
import sqlite3, sys, os, glob, base64, json
from collections import defaultdict

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))
from jea_agdai import decode_core, substrate_core_root
CATALOG_DB = os.path.join(_ROOT, "catalog", "catalog.db")
FREE = {"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"}   # jea_agdai.go referential set

def _b64(s): return base64.b64encode(("" if s is None else s).encode("utf-8")).decode("ascii")

EVENT_SCHEMA = """
CREATE TABLE IF NOT EXISTS terms    (term_id TEXT PRIMARY KEY, text TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS ix_terms_text ON terms(text);
CREATE TABLE IF NOT EXISTS path_seg (path_id TEXT, ord INT, seg_term_id TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS ix_pathseg_uniq ON path_seg(path_id, ord);
-- EVENT LOG (append-only source of truth). ekey = base64(the raw observation). ctor/qname interned.
CREATE TABLE IF NOT EXISTS event    (ekey TEXT PRIMARY KEY, ctor_id TEXT, qname_pid TEXT, idx INT);
CREATE TABLE IF NOT EXISTS obs      (core_id TEXT, local_id INT, ekey TEXT);      -- decoded node → its event
CREATE TABLE IF NOT EXISTS edge     (core_id TEXT, plid INT, ord INT, clid INT);  -- raw local parent→child
CREATE TABLE IF NOT EXISTS unit_obs (core_id TEXT, unit_pid TEXT, root_lid INT, kind_id TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS ix_obs_pk    ON obs(core_id, local_id);
CREATE INDEX        IF NOT EXISTS ix_obs_ekey  ON obs(ekey);
CREATE UNIQUE INDEX IF NOT EXISTS ix_edge_pk   ON edge(core_id, plid, ord);
CREATE INDEX        IF NOT EXISTS ix_edge_child ON edge(core_id, clid);
CREATE UNIQUE INDEX IF NOT EXISTS ix_unitobs_pk ON unit_obs(core_id, unit_pid);
CREATE VIEW IF NOT EXISTS path_text AS
  SELECT path_id, GROUP_CONCAT(seg, '.') AS text FROM (
    SELECT ps.path_id, t.text AS seg FROM path_seg ps JOIN terms t ON t.term_id=ps.seg_term_id
    ORDER BY ps.path_id, ps.ord) GROUP BY path_id;
"""

# The SPPF projection tables (materialized) + the compat views sppf_query reads.
SPPF_SCHEMA = """
CREATE TABLE IF NOT EXISTS _node      (node_id TEXT PRIMARY KEY, sym TEXT, kind_id TEXT, role_id TEXT, op_term_id TEXT, op_path_id TEXT, lit_id TEXT);
CREATE TABLE IF NOT EXISTS node_child (node_id TEXT, ord INT, child_id TEXT);
CREATE TABLE IF NOT EXISTS _unit      (unit_id TEXT PRIMARY KEY, name_pid TEXT, root_id TEXT, file_id TEXT, kind_id TEXT);
CREATE TABLE IF NOT EXISTS unit_node  (unit_id TEXT, node_id TEXT);
CREATE INDEX IF NOT EXISTS ix_node_sym ON _node(sym);
CREATE INDEX IF NOT EXISTS ix_nc_node  ON node_child(node_id);
CREATE INDEX IF NOT EXISTS ix_nc_child ON node_child(child_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_nc_edge ON node_child(node_id, ord, child_id);
CREATE INDEX IF NOT EXISTS ix_un_unit  ON unit_node(unit_id);
CREATE INDEX IF NOT EXISTS ix_un_node  ON unit_node(node_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_un_edge ON unit_node(unit_id, node_id);
CREATE VIEW IF NOT EXISTS node AS SELECT n.node_id, n.sym, k.text AS kind, r.text AS role,
    COALESCE(pt.text, o.text) AS op, l.text AS lit
  FROM _node n JOIN terms k ON k.term_id=n.kind_id JOIN terms r ON r.term_id=n.role_id
    JOIN terms l ON l.term_id=n.lit_id
    LEFT JOIN terms o ON o.term_id=n.op_term_id LEFT JOIN path_text pt ON pt.path_id=n.op_path_id;
CREATE VIEW IF NOT EXISTS unit AS SELECT u.unit_id, pt.text AS name, u.root_id AS root_id, f.text AS path,
    k.text AS kind
  FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid JOIN terms f ON f.term_id=u.file_id
    LEFT JOIN terms k ON k.term_id=u.kind_id;
CREATE VIEW IF NOT EXISTS node_fanin AS SELECT child_id AS node_id, COUNT(*) AS fanin FROM node_child GROUP BY child_id;
CREATE VIEW IF NOT EXISTS shared_subtree AS SELECT node_id, fanin FROM node_fanin WHERE fanin >= 2;
CREATE VIEW IF NOT EXISTS node_atom AS SELECT n.node_id, n.op FROM node n
  WHERE NOT EXISTS (SELECT 1 FROM node_child c WHERE c.node_id=n.node_id);
"""


def _dedup_pathseg(con):
    con.execute("""DELETE FROM path_seg WHERE rowid NOT IN
                   (SELECT MIN(rowid) FROM path_seg GROUP BY path_id, ord)""")


def write_events(cores, con, base):
    """P1: decode each core to raw OBSERVATIONS and append them as events. No interning, no resolution."""
    con.executescript(EVENT_SCHEMA)
    for t in ("event", "obs", "edge", "unit_obs"):
        con.execute(f"DELETE FROM {t}")
    con.commit()
    seen_t = set()
    def tid(s):
        s = "" if s is None else s
        cid = _b64(s)
        if cid not in seen_t:
            seen_t.add(cid); con.execute("INSERT OR IGNORE INTO terms VALUES (?,?)", (cid, s))
        return cid
    def pid(s):
        cid = _b64(s)
        for o, seg in enumerate(s.split(".")):
            con.execute("INSERT OR IGNORE INTO path_seg VALUES (?,?,?)", (cid, o, tid(seg)))
        return cid
    for path in cores:
        try:
            dec = decode_core(path)
        except Exception:
            continue
        cid = tid(os.path.relpath(path, base))   # intern the core path so _unit.file_id resolves in `terms`
        erows, orows, edgerows = [], [], []
        for lid, rec in dec["nodes"].items():
            ctor, qname, idx = rec.get("constructor"), rec.get("qname"), rec.get("index")
            kids = rec.get("children", [])
            # THE OBSERVATION — raw record content, children = LOCAL ids, NO resolution.
            content = json.dumps({"c": ctor, "q": qname, "i": idx, "ch": kids}, sort_keys=True, ensure_ascii=False)
            ekey = _b64(content)
            erows.append((ekey, tid(ctor), (pid(qname) if qname else None), idx))
            orows.append((cid, lid, ekey))
            edgerows += [(cid, lid, o, ch) for o, ch in enumerate(kids)]
        urows = [(cid, pid(name), root, tid(kind))
                 for (name, root, kind) in ((d["unit"], d["root"], d.get("kind", "?"))
                                            for d in dec["defmarks"]) ]
        con.executemany("INSERT OR IGNORE INTO event    VALUES (?,?,?,?)", erows)
        con.executemany("INSERT OR IGNORE INTO obs      VALUES (?,?,?)",   orows)
        con.executemany("INSERT OR IGNORE INTO edge     VALUES (?,?,?,?)", edgerows)
        con.executemany("INSERT OR IGNORE INTO unit_obs VALUES (?,?,?,?)", urows)
        con.commit()                               # transaction per file (append-only)
    _dedup_pathseg(con); con.commit()


def project_sppf(con):
    """P2: DERIVE the packing SPPF from the events. head = per-event (matches jea_agdai.go); symbol =
    base64(head); packing = base64(head ‖ ordered child symbols) — a 1-JOIN, not recursive; node_child =
    (parent packing, ord, child packing); unit_node = per-unit membership over the acyclic raw edges."""
    for name in ("node", "unit", "node_fanin", "shared_subtree", "node_atom"):
        row = con.execute("SELECT type FROM sqlite_master WHERE name=?", (name,)).fetchone()
        if row: con.execute(f"DROP {row[0].upper()} IF EXISTS {name}")
    con.executescript(SPPF_SCHEMA)
    for t in ("unit_node", "node_child", "_node", "_unit"):
        con.execute(f"DELETE FROM {t}")
    con.commit()

    # head + symbol per event (symbol is head-only ⟹ global, no recursion)
    head, sym = {}, {}
    for ekey, ctor, qname, idx in con.execute(
            "SELECT e.ekey, tc.text, pq.text, e.idx FROM event e JOIN terms tc ON tc.term_id=e.ctor_id "
            "LEFT JOIN path_text pq ON pq.path_id=e.qname_pid"):
        if ctor in ("Var", "PVar"):        role, op = f"db{idx}", ""
        elif ctor in FREE and qname:       role, op = "", qname
        else:                              role, op = "", (ctor or "")
        head[ekey] = ("AgdaCore", role, op, "")
        sym[ekey]  = _b64("\x00".join(head[ekey]))
    obs = {(c, l): e for c, l, e in con.execute("SELECT core_id, local_id, ekey FROM obs")}
    ch = defaultdict(list)
    for c, p, o, cl in con.execute("SELECT core_id, plid, ord, clid FROM edge"):
        ch[(c, p)].append((o, cl))

    packing = {}
    def pack(c, lid):                              # base64(head ‖ ordered child symbols) for (core, local)
        key = (c, lid)
        if key in packing: return packing[key]
        ekey = obs.get(key)
        if ekey is None: return None
        kids = sorted(ch.get(key, []))
        child_syms = [sym[obs[(c, cl)]] for _, cl in kids if (c, cl) in obs]
        k, r, o, l = head[ekey]
        pk = _b64("\x00".join([k, r, o, l, ",".join(child_syms)]))
        packing[key] = pk
        return pk

    def tid(s):                                    # heads already in `terms`; base64 is deterministic
        return _b64("" if s is None else s)
    def pid(s):
        return _b64(s)

    seen_n, nrows, ncrows = set(), [], set()
    for (c, lid), ekey in obs.items():
        pk = pack(c, lid)
        k, r, o, l = head[ekey]
        if pk not in seen_n:
            seen_n.add(pk)
            ot, opp = (None, pid(o)) if "." in o else (tid(o), None)
            nrows.append((pk, sym[ekey], tid(k), tid(r), ot, opp, tid(l)))
        for ordn, cl in ch.get((c, lid), []):
            cpk = pack(c, cl)
            if cpk is not None:
                ncrows.add((pk, ordn, cpk))
    con.executemany("INSERT OR IGNORE INTO _node VALUES (?,?,?,?,?,?,?)", nrows)
    con.executemany("INSERT OR IGNORE INTO node_child VALUES (?,?,?)", sorted(ncrows))

    # units + per-unit membership (reach from root over the acyclic raw edges — pre-sharing, no closure)
    urows, un_rows = [], []
    childmap = ch
    for c, unit_pid, root_lid, kind_id in con.execute(
            "SELECT core_id, unit_pid, root_lid, kind_id FROM unit_obs"):
        rootpk = pack(c, root_lid)
        if rootpk is None: continue
        uid = unit_pid
        urows.append((uid, unit_pid, rootpk, c, kind_id))
        seen, stack, members = set(), [root_lid], set()
        while stack:
            lid = stack.pop()
            if lid in seen: continue
            seen.add(lid)
            pk = pack(c, lid)
            if pk is not None: members.add(pk)
            stack.extend(cl for _, cl in childmap.get((c, lid), []))
        un_rows += [(uid, pk) for pk in members]
    con.executemany("INSERT OR IGNORE INTO _unit VALUES (?,?,?,?,?)", urows)
    con.executemany("INSERT OR IGNORE INTO unit_node VALUES (?,?)", un_rows)
    con.commit()
    return (len(seen_n), len(urows),
            con.execute("SELECT COUNT(*) FROM shared_subtree").fetchone()[0],
            con.execute("SELECT MAX(LENGTH(node_id)) FROM _node").fetchone()[0])


def build(cores, catalog_db=CATALOG_DB, base=None):
    base = base or substrate_core_root(os.path.join(_ROOT, "agda"))
    con = sqlite3.connect(catalog_db)
    write_events(cores, con, base)                 # P1: append-only events (source of truth)
    stats = project_sppf(con)                      # P2: the SPPF, DERIVED from events
    con.close()
    return stats


if __name__ == "__main__":
    filt = sys.argv[1] if len(sys.argv) > 1 else "Category"
    base = substrate_core_root(os.path.join(_ROOT, "agda"))
    cores = [c for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True)) if filt in c]
    print(f"event-sourcing {len(cores)} cores (filter={filt!r}) → catalog.db (events, then project SPPF) …")
    n, u, sh, mx = build(cores)
    print(f"  events → SPPF projection: {n} packings, {u} units, {sh} shared subtrees, max node_id {mx}")
