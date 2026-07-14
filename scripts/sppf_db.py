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
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jea", "metalanguage"))
import query_builders as QB               # ⟡query-rawtocore: single-source Core builders (run = execute)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))
from jea_agdai import decode_core, substrate_core_root
from jea_rigcat import RIG_OPS                       # ⟡rig orbit-interning (the proven ⊕/⊗ op-set)
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
-- unit_id = base64(qname ‖ root) — UNIQUE PER DEFMARK (two anonymous-module defs can share a full qname;
-- reuse_catalog keys structs by (qname,root), so the unit tier must too). name_pid = base64(qname) for display.
CREATE TABLE IF NOT EXISTS unit_obs (core_id TEXT, unit_id TEXT, name_pid TEXT, root_lid INT, kind_id TEXT, module_pid TEXT, copy INT);
-- member links RESOLVED at write time (qname → its defmark unit, last-wins per core, matching reuse_catalog's
-- root_of): member_unit_id is the member's unit (NULL if the member is not itself a defmark).
CREATE TABLE IF NOT EXISTS unit_member (core_id TEXT, unit_id TEXT, ord INT, member_name_pid TEXT, member_unit_id TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS ix_obs_pk    ON obs(core_id, local_id);
CREATE INDEX        IF NOT EXISTS ix_obs_ekey  ON obs(ekey);
CREATE UNIQUE INDEX IF NOT EXISTS ix_edge_pk   ON edge(core_id, plid, ord);
CREATE INDEX        IF NOT EXISTS ix_edge_child ON edge(core_id, clid);
CREATE UNIQUE INDEX IF NOT EXISTS ix_unitobs_pk ON unit_obs(unit_id);
-- path_text: a MATERIALIZED table with a PK index on path_id (was a GROUP_CONCAT VIEW). PROPER INDEXING,
-- not view-vs-table taste: EXPLAIN shows the view forces SQLite to MATERIALIZE the whole aggregation +
-- build a TEMP B-TREE for the GROUP BY on EVERY join — even a single-row keyed join (WHERE …=?) — because
-- the view's join key path_id has no index; predicate propagation cannot push through the GROUP BY. Each
-- interactive query on the node/unit views (which join path_text) paid a full-view materialization. As a
-- PK-indexed table the same join is one `SEARCH … USING INDEX (path_id=?)`. Refreshed by refresh_path_text
-- at the write_events boundary; path_seg stays the append-only source of truth, this is its interned index.
CREATE TABLE IF NOT EXISTS path_text (path_id TEXT PRIMARY KEY, text TEXT);
"""

# The SPPF projection tables (materialized) + the compat views sppf_query reads.
SPPF_SCHEMA = """
CREATE TABLE IF NOT EXISTS _node      (node_id TEXT PRIMARY KEY, sym TEXT, kind_id TEXT, role_id TEXT, op_term_id TEXT, op_path_id TEXT, lit_id TEXT);
CREATE TABLE IF NOT EXISTS node_child (node_id TEXT, ord INT, child_id TEXT);
CREATE TABLE IF NOT EXISTS _unit      (unit_id TEXT PRIMARY KEY, name_pid TEXT, root_id TEXT, file_id TEXT, kind_id TEXT, module_pid TEXT, root_lid INT, copy INT);
-- the codomain HEAD of each unit's type (raw_final_head: unwrap Defn, peel the Pi-telescope), computed
-- structurally at PROJECTION time over the unambiguous per-core tree (the reentrant packing bridge would
-- conflate contexts). The catalog reads THIS (a structural attribute of the projection), not raw events.
CREATE TABLE IF NOT EXISTS _unit_cod  (unit_id TEXT PRIMARY KEY, cod_ctor_id TEXT, cod_qname_pid TEXT);
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
    k.text AS kind, u.copy AS copy
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
    # DROP (not DELETE) the event tables so column changes take effect (terms/path_seg are shared — keep).
    for t in ("event", "obs", "edge", "unit_obs", "unit_member"):
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.execute("DROP VIEW IF EXISTS path_text")     # migrate a legacy GROUP_CONCAT view → the indexed table
    con.executescript(EVENT_SCHEMA)
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
        relpath = os.path.relpath(path, base)
        cid = tid(relpath)                       # intern the core path so _unit.file_id resolves in `terms`
        module = "Substrate." + relpath[:-len(".agdai")].replace(os.sep, ".")  # agdai_module (file metadata)
        mpid = pid(module)
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
        dms = dec["defmarks"]
        root_of = {}                              # qname → root, LAST-WINS per core (matches reuse_catalog)
        for d in dms:
            root_of[d["unit"]] = d["root"]
        def uid(qn, r):
            return _b64(qn + "\x00" + str(r))
        urows = [(cid, uid(d["unit"], d["root"]), pid(d["unit"]), d["root"], tid(d.get("kind", "?")), mpid,
                  1 if d.get("copy") else 0)                 # defCopy provenance: instantiation-copy vs original
                 for d in dms]
        mrows = []
        for d in dms:
            su = uid(d["unit"], d["root"])
            for o, m in enumerate(d.get("members", [])):
                mr = root_of.get(m)
                mrows.append((cid, su, o, pid(m), (uid(m, mr) if mr is not None else None)))
        con.executemany("INSERT OR IGNORE INTO event       VALUES (?,?,?,?)", erows)
        con.executemany("INSERT OR IGNORE INTO obs         VALUES (?,?,?)",   orows)
        con.executemany("INSERT OR IGNORE INTO edge        VALUES (?,?,?,?)", edgerows)
        con.executemany("INSERT OR IGNORE INTO unit_obs    VALUES (?,?,?,?,?,?,?)", urows)
        con.executemany("INSERT OR IGNORE INTO unit_member VALUES (?,?,?,?,?)", mrows)
        con.commit()                               # transaction per file (append-only)
    _dedup_pathseg(con); con.commit()
    refresh_path_text(con)                          # materialize the indexed path_text from finalized path_seg


def refresh_path_text(con):
    """Materialize path_text (path_id → dotted qname, PK-indexed) from the finalized path_seg — the interned
    projection of the append-only path segments. Refreshed at the write_events boundary so every downstream
    join is one index seek, not a full GROUP_CONCAT view materialization per query (see EVENT_SCHEMA note).
    Idempotent (DELETE+INSERT); tolerant of a legacy path_text VIEW."""
    con.execute("DROP VIEW IF EXISTS path_text")
    con.execute("CREATE TABLE IF NOT EXISTS path_text (path_id TEXT PRIMARY KEY, text TEXT)")
    con.execute("DELETE FROM path_text")
    con.execute("INSERT INTO path_text SELECT path_id, GROUP_CONCAT(seg, '.') FROM ("
                "SELECT ps.path_id, t.text AS seg FROM path_seg ps JOIN terms t ON t.term_id=ps.seg_term_id "
                "ORDER BY ps.path_id, ps.ord) GROUP BY path_id")
    con.commit()


def project_sppf(con):
    """P2: DERIVE the packing SPPF from the events. head = per-event (matches jea_agdai.go); symbol =
    base64(head); packing = base64(head ‖ ordered child symbols) — a 1-JOIN, not recursive; node_child =
    (parent packing, ord, child packing); unit_node = per-unit membership over the acyclic raw edges."""
    # DROP (not DELETE) the projection views+tables so a column change is picked up (IF NOT EXISTS would
    # keep a stale-shaped table). NEVER touch the event tier (terms/path_seg/event/obs/edge/unit_*).
    for name in ("node", "unit", "node_fanin", "shared_subtree", "node_atom",
                 "unit_node", "node_child", "_node", "_unit", "_unit_cod"):
        row = con.execute("SELECT type FROM sqlite_master WHERE name=?", (name,)).fetchone()
        if row: con.execute(f"DROP {row[0].upper()} IF EXISTS {name}")
    con.executescript(SPPF_SCHEMA)
    con.commit()

    # head + symbol per event (symbol is head-only ⟹ global, no recursion)
    head, sym = {}, {}
    for ekey, ctor, qname, idx in QB.run(con, QB.q_event_head()):
        if ctor in ("Var", "PVar"):        role, op = f"db{idx}", ""
        elif ctor in FREE and qname:       role, op = "", qname
        else:                              role, op = "", (ctor or "")
        head[ekey] = ("AgdaCore", role, op, "")
        sym[ekey]  = _b64("\x00".join(head[ekey]))
    raw_ctor = {e: ct for e, ct in QB.run(con, QB.q_event_ctor())}   # true constructor (Def/Con/Var/…) for cod()
    obs = {(c, l): e for c, l, e in QB.run(con, QB.q_obs_all())}
    ch = defaultdict(list)
    for c, p, o, cl in QB.run(con, QB.q_edge_all()):
        ch[(c, p)].append((o, cl))

    def cod(c, root_lid):        # raw_final_head over the UNAMBIGUOUS per-core tree → (ctor, qname)
        cur = root_lid
        def opof(lid):
            e = obs.get((c, lid)); return head[e][2] if e else None
        if opof(cur) == "Defn":
            kd = sorted(ch.get((c, cur), []))
            if kd: cur = kd[0][1]                       # unwrap Defn: child[0] = the defType
        s = 0
        while opof(cur) == "Pi" and ch.get((c, cur)) and s < 4096:
            cur = sorted(ch.get((c, cur)))[-1][1]; s += 1   # peel the Pi-telescope: codomain = last child
        e = obs.get((c, cur))
        if e is None: return (None, None)
        _k, _r, o, _l = head[e]
        qn = o if (o and "." in o) else None            # op is a qname ⟹ that's the codomain qname
        return (raw_ctor.get(e), qn)                    # (true ctor, qname) — matches raw_final_head

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

    _seen_pt = set()
    def tid(s):                                    # intern-if-missing: node kinds ("AgdaCore") / lits are
        s = "" if s is None else s                 # NOT pre-interned by write_events, so the `node` view's
        cid = _b64(s)                              # inner join on kind_id would drop every row (⟡node-view-kindid).
        if cid not in _seen_pt:
            _seen_pt.add(cid); con.execute("INSERT OR IGNORE INTO terms VALUES (?,?)", (cid, s))
        return cid
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
    # + the codomain HEAD of each unit's type (structural, computed on the unambiguous per-core tree).
    urows, un_rows, codrows = [], [], []
    childmap = ch
    for c, unit_id, name_pid, root_lid, kind_id, module_pid, copy in con.execute(
            "SELECT core_id, unit_id, name_pid, root_lid, kind_id, module_pid, copy FROM unit_obs"):
        rootpk = pack(c, root_lid)
        if rootpk is None: continue
        urows.append((unit_id, name_pid, rootpk, c, kind_id, module_pid, root_lid, copy))
        cct, cqn = cod(c, root_lid)
        codrows.append((unit_id, (tid(cct) if cct is not None else None),
                        (pid(cqn) if cqn is not None else None)))
        seen, stack, members = set(), [root_lid], set()
        while stack:
            lid = stack.pop()
            if lid in seen: continue
            seen.add(lid)
            pk = pack(c, lid)
            if pk is not None: members.add(pk)
            stack.extend(cl for _, cl in childmap.get((c, lid), []))
        un_rows += [(unit_id, pk) for pk in members]
    con.executemany("INSERT OR IGNORE INTO _unit VALUES (?,?,?,?,?,?,?,?)", urows)
    con.executemany("INSERT OR IGNORE INTO _unit_cod VALUES (?,?,?)", codrows)
    con.executemany("INSERT OR IGNORE INTO unit_node VALUES (?,?)", un_rows)
    con.commit()
    return (len(seen_n), len(urows),
            QB.run(con, QB.q_count_shared()).fetchone()[0],
            QB.run(con, QB.q_max_node_len()).fetchone()[0])


ORBIT_SCHEMA = """
CREATE TABLE IF NOT EXISTS orbit_node   (orbit_id TEXT PRIMARY KEY, sym TEXT, kind_id TEXT, role_id TEXT, op_term_id TEXT, op_path_id TEXT, lit_id TEXT);
CREATE TABLE IF NOT EXISTS orbit_child  (orbit_id TEXT, ord INT, child_id TEXT);
CREATE TABLE IF NOT EXISTS orbit_member (orbit_id TEXT, node_id TEXT);   -- positional packings this orbit merged
CREATE UNIQUE INDEX IF NOT EXISTS ix_orbit_mem   ON orbit_member(orbit_id, node_id);
CREATE INDEX        IF NOT EXISTS ix_orbit_child ON orbit_child(orbit_id);
CREATE VIEW IF NOT EXISTS orbit AS SELECT n.orbit_id, n.sym, k.text AS kind, r.text AS role,
    COALESCE(pt.text, o.text) AS op, l.text AS lit
  FROM orbit_node n JOIN terms k ON k.term_id=n.kind_id JOIN terms r ON r.term_id=n.role_id
    JOIN terms l ON l.term_id=n.lit_id
    LEFT JOIN terms o ON o.term_id=n.op_term_id LEFT JOIN path_text pt ON pt.path_id=n.op_path_id;
"""


def project_orbit_sppf(con, distribute=False):
    """⟡rig ORBIT interning — a projection over the SAME events that keys nodes by their ORBIT under the
    rig group (jea_rigcat.canonical: commutativity=sort, associativity=flatten of the rig ⊕/⊗ ops). ADDITIVE:
    orbit_node/orbit_child/orbit_member sit ALONGSIDE the positional _node (untouched). orbit_member
    back-references the positional packings each orbit merged — nothing is lost (a projection, not a rewrite).
    Same orbit ⟺ same node, provably (RIG_OPS is the substrate's proven ⊕/⊗ set)."""
    row = con.execute("SELECT type FROM sqlite_master WHERE name='orbit'").fetchone()
    if row: con.execute(f"DROP {row[0].upper()} IF EXISTS orbit")
    for t in ("orbit_node", "orbit_child", "orbit_member"):
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.executescript(ORBIT_SCHEMA)

    head = {}                                       # reload the forest (self-contained; mirrors project_sppf)
    for ekey, ctor, qname, idx in QB.run(con, QB.q_event_head()):
        if ctor in ("Var", "PVar"):    role, op = f"db{idx}", ""
        elif ctor in FREE and qname:   role, op = "", qname
        else:                          role, op = "", (ctor or "")
        head[ekey] = ("AgdaCore", role, op, "")
    sym = {e: _b64("\x00".join(h)) for e, h in head.items()}
    obs = {(c, l): e for c, l, e in QB.run(con, QB.q_obs_all())}
    ch = defaultdict(list)
    for c, p, o, cl in QB.run(con, QB.q_edge_all()):
        ch[(c, p)].append((o, cl))
    def tid(s): return _b64("" if s is None else s)
    def pid(s): return _b64(s)

    # BOTH keys at the PACKING granularity (children = head-symbols, the reentrant scheme) so orbit ⊆
    # packing: `pack` = positional (child symbols in source order, == project_sppf's _node key); `opk` =
    # ORBIT (the rig ⊕/⊗ ops flatten nested same-op + sort their child symbols). Same orbit ⟺ same opk,
    # and opk merges the reorderings/reassociations the packing keeps distinct ⟹ strictly fewer nodes.
    packing, csyms = {}, {}
    def pack(c, lid):                               # positional packing key (identical to project_sppf)
        key = (c, lid)
        if key in packing: return packing[key]
        ekey = obs.get(key)
        if ekey is None: return None
        child_syms = [sym[obs[(c, cl)]] for _, cl in sorted(ch.get(key, [])) if (c, cl) in obs]
        k, r, o, l = head[ekey]
        packing[key] = _b64("\x00".join([k, r, o, l, ",".join(child_syms)]))
        return packing[key]
    def canon_syms(c, lid):                         # canonical child head-symbol LIST under the rig group
        key = (c, lid)
        if key in csyms: return csyms[key]
        ekey = obs.get(key)
        kids = [(o_, cl) for o_, cl in sorted(ch.get(key, [])) if (c, cl) in obs]
        law = RIG_OPS.get(head[ekey][2]) if ekey else None
        if law is None:
            res = [sym[obs[(c, cl)]] for _, cl in kids]                   # non-rig: positional child symbols
        else:
            op = head[ekey][2]
            out = []
            for _, cl in kids:
                ce = obs.get((c, cl))
                if law.associative and ce is not None and head[ce][2] == op:
                    out.extend(canon_syms(c, cl))                        # flatten nested same rig op
                elif ce is not None:
                    out.append(sym[ce])
            res = sorted(out) if law.commutative else out               # sort = the Sₙ-orbit representative
        csyms[key] = res
        return res
    def opk(c, lid):                                # ORBIT key = base64(head ‖ canonical child symbols)
        ekey = obs.get((c, lid))
        if ekey is None: return None
        k, r, o, l = head[ekey]
        return _b64("\x00".join([k, r, o, l, ",".join(canon_syms(c, lid))]))

    seen_o, nrows, crows, mrows = set(), [], set(), set()
    for (c, lid), ekey in obs.items():
        okey = opk(c, lid); pk = pack(c, lid)
        k, r, o, l = head[ekey]
        if okey not in seen_o:
            seen_o.add(okey)
            ot, opp = (None, pid(o)) if "." in o else (tid(o), None)
            nrows.append((okey, sym[ekey], tid(k), tid(r), ot, opp, tid(l)))
            crows.update((okey, i, cs) for i, cs in enumerate(canon_syms(c, lid)))   # canonical child symbols
        if pk is not None: mrows.add((okey, pk))     # orbit → the positional PACKINGS it merged
    con.executemany("INSERT OR IGNORE INTO orbit_node   VALUES (?,?,?,?,?,?,?)", nrows)
    con.executemany("INSERT OR IGNORE INTO orbit_child  VALUES (?,?,?)", sorted(crows))
    con.executemany("INSERT OR IGNORE INTO orbit_member VALUES (?,?)", sorted(mrows))
    con.commit()
    return (len(seen_o),                                          # orbit-node count (the quotient)
            len(set(packing.values())),                          # positional PACKING count (the baseline)
            QB.run(con, QB.q_max_orbit_len()).fetchone()[0])


# ⟡argperm — the GRADED orbit-key per def (type-orbit + proof-orbit), from graded_orbit. ADDITIVE: a new
# _orbit_def table; the depth-1 canon_syms/opk can't carry the deep key (all Defn→[Pi,Clause] collide), so
# the def orbit lives here, not in orbit_node. Genuine arg-perm twins share graded_key; type-twins share
# type_key. Depth-3 (rig precomputed-coherence) fixpoint over the def-dependency DAG; deeper → SPPF collapse.
ARGPERM_SCHEMA = """
CREATE TABLE IF NOT EXISTS _orbit_def (unit_id TEXT PRIMARY KEY, type_key TEXT, graded_key TEXT,
                                       residue TEXT, stab INT);
CREATE INDEX IF NOT EXISTS ix_odef_type   ON _orbit_def(type_key);
CREATE INDEX IF NOT EXISTS ix_odef_graded ON _orbit_def(graded_key);
-- ⟡orbit-def-by-reference: the graded orbit as a content-addressed DAG (BY REFERENCE, not the old
-- _b64(repr(k)) inlined blob). graded_id = a stable Merkle content-address (graded_orbit.dump_graded);
-- graded_orbit_child edges reference child graded_ids; graded_orbit_member maps a graded_id → the units in
-- that orbit; graded_orbit_node.fanin = sharing BREADTH (the ⟡query-sppf-intern signal), a lookup not a scan.
CREATE TABLE IF NOT EXISTS graded_orbit_node   (graded_id TEXT PRIMARY KEY, kind TEXT, op TEXT, qname TEXT, fanin INT);
CREATE TABLE IF NOT EXISTS graded_orbit_child  (graded_id TEXT, ord INT, child_id TEXT);
CREATE TABLE IF NOT EXISTS graded_orbit_member (graded_id TEXT, unit_id TEXT);
CREATE INDEX        IF NOT EXISTS ix_gorbit_child ON graded_orbit_child(graded_id);
CREATE INDEX        IF NOT EXISTS ix_gorbit_nqn   ON graded_orbit_node(qname);
CREATE UNIQUE INDEX IF NOT EXISTS ix_gorbit_mem   ON graded_orbit_member(graded_id, unit_id);
"""

def project_argperm(con, filt=None):
    """Per-def GRADED orbit-key + coset residue (⟡graded-orbit-interner Phase C/D) → _orbit_def. Additive;
    touches no other table. residue = the telescope-permutation Lehmer code (the coset element = the wedge
    r); two defs in one type-orbit differ by their residues. Returns (n_defs, n_type_orbits, n_graded)."""
    import graded_orbit as G
    for t in ("_orbit_def", "graded_orbit_node", "graded_orbit_child", "graded_orbit_member"):
        con.execute(f"DROP TABLE IF EXISTS {t}")
    con.executescript(ARGPERM_SCHEMA)
    ctx = G.Ctx(con)
    uid = {nm: u for u, nm in QB.run(con, QB.q_argperm_uid())}
    defs = []                                                        # (name, k=(tkey,gid), residue_repr, stab)
    for name in ctx.idx:
        if filt and filt not in name:
            continue
        k = G.orbit_key(ctx, name)                                   # (type-orbit key, graded HANDLE gid)
        leh, stab = ctx.resid.get(name, ((), 1))                     # the coset element (Lehmer) + |Stab|
        if name in uid:
            defs.append((name, k, repr(leh), stab))
    # ⟡orbit-def-by-reference: persist the graded-orbit DAG by REFERENCE; graded_key = the interner's int
    # handle str(root gid) — a BOUNDED, within-build-consistent content-address (consumers only compare
    # graded_key for equality within one build). node/child rows carry the DAG + fanin (breadth).
    node_rows, child_rows = G.dump_graded(ctx)
    orbit_rows  = [(uid[name], _b64(repr(k[0])), str(k[1]), leh, stab) for (name, k, leh, stab) in defs]
    member_rows = [(str(k[1]), uid[name]) for (name, k, _, _) in defs]
    con.executemany("INSERT OR IGNORE INTO _orbit_def VALUES (?,?,?,?,?)", orbit_rows)
    con.executemany("INSERT OR IGNORE INTO graded_orbit_node   VALUES (?,?,?,?,?)", node_rows)
    con.executemany("INSERT OR IGNORE INTO graded_orbit_child  VALUES (?,?,?)", child_rows)
    con.executemany("INSERT OR IGNORE INTO graded_orbit_member VALUES (?,?)", member_rows)
    con.commit()
    return len(orbit_rows), len({r[1] for r in orbit_rows}), len({r[2] for r in orbit_rows})


def build(cores, catalog_db=CATALOG_DB, base=None, orbit=False, distribute=False, argperm=False):
    base = base or substrate_core_root(os.path.join(_ROOT, "agda"))
    con = sqlite3.connect(catalog_db)
    write_events(cores, con, base)                 # P1: append-only events (source of truth)
    stats = project_sppf(con)                      # P2: the positional SPPF, DERIVED from events
    if argperm:
        project_argperm(con)                       # ⟡argperm: the per-def GRADED orbit-key (additive)
    if orbit:
        project_orbit_sppf(con, distribute=distribute)   # ⟡rig: the ORBIT projection (additive)
    con.close()
    return stats


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    orbit = "--orbit" in sys.argv
    distribute = "--distribute" in sys.argv
    argperm = "--argperm" in sys.argv
    filt = args[0] if args else "Category"
    base = substrate_core_root(os.path.join(_ROOT, "agda"))
    cores = [c for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True)) if filt in c]
    print(f"event-sourcing {len(cores)} cores (filter={filt!r}) → catalog.db (events, then project SPPF"
          f"{', + ORBIT' if orbit else ''}) …")
    n, u, sh, mx = build(cores, orbit=orbit, distribute=distribute, argperm=argperm)
    print(f"  events → SPPF projection: {n} packings, {u} units, {sh} shared subtrees, max node_id {mx}")
    if argperm:
        con = sqlite3.connect(CATALOG_DB)
        d, t, g = QB.run(con, QB.q_orbit_def_stats()).fetchone()
        print(f"  ⟡argperm GRADED orbit: {d} defs → {t} type-orbits, {g} graded-orbits "
              f"({d-g} defs collapsed by full arg-perm equivalence; {d-t} by type/telescope alone)")
        con.close()
    if orbit:
        con = sqlite3.connect(CATALOG_DB)
        orbits = QB.run(con, QB.q_orbit_node_count()).fetchone()[0]
        packings = QB.run(con, QB.q_orbit_packings()).fetchone()[0]
        merged = QB.run(con, QB.q_orbit_merged()).fetchone()[0]
        print(f"  ⟡rig ORBIT projection: {orbits} orbit-nodes vs {packings} packings "
              f"({packings-orbits} collapsed by rig ⊕/⊗ reorder/reassoc); {merged} orbits merged ≥2 packings")
        con.close()
