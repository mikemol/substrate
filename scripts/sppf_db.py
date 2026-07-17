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
from _content_addr import _b64
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jea", "metalanguage"))
import query_builders as QB               # ⟡query-rawtocore: single-source Core builders (run = execute)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))
from jea_agdai import decode_core, substrate_core_root
from jea_rigcat import RIG_OPS                       # ⟡rig orbit-interning (the proven ⊕/⊗ op-set)
CATALOG_DB = os.environ.get("SPPF_CATALOG_DB", os.path.join(_ROOT, "catalog", "catalog.db"))
FREE = {"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"}   # jea_agdai.go referential set

# ⟡gqs-S0.2/⟡gqs-lit-propagate: bump on ANY EVENT_SCHEMA/SPPF_SCHEMA column change. A catalog.db built at a
# lower `PRAGMA user_version` is auto-migrated by a clean --full rebuild (init_db drops the event tier; the
# batched write_events forces full) — so a column add never breaks the incremental path on a stale DB.
SCHEMA_VERSION = 1

EVENT_SCHEMA = """
CREATE TABLE IF NOT EXISTS terms    (term_id TEXT PRIMARY KEY, text TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS ix_terms_text ON terms(text);
CREATE TABLE IF NOT EXISTS path_seg (path_id TEXT, ord INT, seg_term_id TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS ix_pathseg_uniq ON path_seg(path_id, ord);
-- EVENT LOG (append-only source of truth). ekey = base64(the raw observation). ctor/qname interned.
-- lit_id (⟡gqs-lit-propagate): the interned literal VALUE for a Lit/PLit node ("" for non-literals). A
-- literal's value IS its identity (num 61 ≠ num 78 are distinct terms); carrying it stops distinct literals
-- collapsing in the projection (the packing key + _node.lit_id).
CREATE TABLE IF NOT EXISTS event    (ekey TEXT PRIMARY KEY, ctor_id TEXT, qname_pid TEXT, idx INT, lit_id TEXT);
CREATE TABLE IF NOT EXISTS obs      (core_id TEXT, local_id INT, ekey TEXT);      -- decoded node → its event
CREATE TABLE IF NOT EXISTS edge     (core_id TEXT, plid INT, ord INT, clid INT);  -- raw local parent→child
-- unit_id = base64(qname ‖ root) — UNIQUE PER DEFMARK (two anonymous-module defs can share a full qname;
-- reuse_catalog keys structs by (qname,root), so the unit tier must too). name_pid = base64(qname) for display.
-- level (⟡gqs-S0.2): the shim's elaborated universe level the def INHABITS (Πs peeled). level>=1 ⟺ Set₁ debt,
-- so the Set₁ census becomes a COLUMN READ (q_set1_count) instead of set1_ratchet's own 94s decode.
CREATE TABLE IF NOT EXISTS unit_obs (core_id TEXT, unit_id TEXT, name_pid TEXT, root_lid INT, kind_id TEXT, module_pid TEXT, copy INT, level INTEGER);
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
-- ⟡gqs-S1 incremental decode: per-core freshness = the .agdai's mtime AS THE RECORD VERSION. decode_core is
-- ONE shim subprocess per core (~49ms × 1910 ≈ 94s a full pass); write_events re-decodes only cores whose
-- mtime advanced since the last run and keeps the rest, so a git-commit stops re-deriving the whole SPPF.
CREATE TABLE IF NOT EXISTS core_fp (core_id TEXT PRIMARY KEY, mtime INTEGER);
"""

# The SPPF projection tables (materialized) + the compat views sppf_query reads.
SPPF_SCHEMA = """
CREATE TABLE IF NOT EXISTS _node      (node_id TEXT PRIMARY KEY, sym TEXT, kind_id TEXT, role_id TEXT, op_term_id TEXT, op_path_id TEXT, lit_id TEXT);
CREATE TABLE IF NOT EXISTS node_child (node_id TEXT, ord INT, child_id TEXT);
CREATE TABLE IF NOT EXISTS _unit      (unit_id TEXT PRIMARY KEY, name_pid TEXT, root_id TEXT, file_id TEXT, kind_id TEXT, module_pid TEXT, root_lid INT, copy INT, level INTEGER);
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


def _drop_legacy_view(con, name):
    """Drop a legacy GROUP_CONCAT VIEW so the PK-indexed TABLE can take its place. A NO-OP once `name`
    is already the table: `DROP VIEW IF EXISTS <table>` raises OperationalError ("use DROP TABLE …") —
    the one-time view→table migration is done, so there is nothing to drop. (⟡catalog-regen-fix: this
    stale assumption crashed gen_catalog.py's SPPF walk once path_text became a table.)"""
    try:
        con.execute(f"DROP VIEW IF EXISTS {name}")
    except sqlite3.OperationalError:
        pass


def _core_ver(path):
    """The core's record-version = its .agdai mtime in ns (a `stat`, ~µs vs decode_core's ~49ms subprocess).
    agda rewrites the interface on every recompile, so an advanced mtime IS 'rebuilt since we last decoded' —
    exactly the freshness question (⟡freshness-stance). st_mtime_ns is an exact integer (no float-repr drift)."""
    return os.stat(path).st_mtime_ns


def _schema_current(con):
    """True iff catalog.db was built at the current SCHEMA_VERSION (else a column add needs a --full migration)."""
    return con.execute("PRAGMA user_version").fetchone()[0] == SCHEMA_VERSION


def _set_schema_version(con):
    con.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def _mk_interners(con):
    """The terms/path_seg interners (INSERT OR IGNORE, content-addressed). Shared by the batched write_events
    and the per-core ingest_core so the decode→rows logic is single-sourced."""
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
    return tid, pid


def _decode_insert_core(con, path, relpath, mtime, tid, pid):
    """Decode ONE core and INSERT its rows (the caller has already deleted any stale rows for this core_id).
    core_id = _b64(relpath). Returns True if ingested, False if undecodable. The SINGLE decode→rows path
    (both write_events' batched loop and ingest_core call it)."""
    try:
        dec = decode_core(path)
    except Exception:
        dec = None
    if dec is None:
        return False                              # undecodable: no rows, no version — re-attempted next run
    cid = tid(relpath)                       # intern the core path so _unit.file_id resolves in `terms`
    module = "Substrate." + relpath[:-len(".agdai")].replace(os.sep, ".")  # agdai_module (file metadata)
    mpid = pid(module)
    erows, orows, edgerows = [], [], []
    for lid, rec in dec["nodes"].items():
        ctor, qname, idx = rec.get("constructor"), rec.get("qname"), rec.get("index")
        kids = rec.get("children", [])
        litval = rec.get("lit", "")             # ⟡gqs-lit-propagate: a Lit/PLit node's VALUE (its identity)
        # THE OBSERVATION — raw record content, children = LOCAL ids, NO resolution. The lit key is added
        # ONLY when present, so non-literal ekeys stay stable (a surgical migration — only Lit/PLit ekeys change).
        obs_rec = {"c": ctor, "q": qname, "i": idx, "ch": kids}
        if litval:
            obs_rec["l"] = litval
        content = json.dumps(obs_rec, sort_keys=True, ensure_ascii=False)
        ekey = _b64(content)
        erows.append((ekey, tid(ctor), (pid(qname) if qname else None), idx, tid(litval)))
        orows.append((cid, lid, ekey))
        edgerows += [(cid, lid, o, ch) for o, ch in enumerate(kids)]
    dms = dec["defmarks"]
    root_of = {}                              # qname → root, LAST-WINS per core (matches reuse_catalog)
    for d in dms:
        root_of[d["unit"]] = d["root"]
    def uid(qn, r):
        return _b64(qn + "\x00" + str(r))
    urows = [(cid, uid(d["unit"], d["root"]), pid(d["unit"]), d["root"], tid(d.get("kind", "?")), mpid,
              1 if d.get("copy") else 0,                 # defCopy provenance: instantiation-copy vs original
              d.get("level"))                            # ⟡gqs-S0.2: elaborated universe level (level>=1 ⟺ Set₁)
             for d in dms]
    mrows = []
    for d in dms:
        su = uid(d["unit"], d["root"])
        for o, m in enumerate(d.get("members", [])):
            mr = root_of.get(m)
            mrows.append((cid, su, o, pid(m), (uid(m, mr) if mr is not None else None)))
    con.executemany("INSERT OR IGNORE INTO event       VALUES (?,?,?,?,?)", erows)
    con.executemany("INSERT OR IGNORE INTO obs         VALUES (?,?,?)",   orows)
    con.executemany("INSERT OR IGNORE INTO edge        VALUES (?,?,?,?)", edgerows)
    con.executemany("INSERT OR IGNORE INTO unit_obs    VALUES (?,?,?,?,?,?,?,?)", urows)
    con.executemany("INSERT OR IGNORE INTO unit_member VALUES (?,?,?,?,?)", mrows)
    con.execute("INSERT OR REPLACE INTO core_fp VALUES (?,?)", (cid, mtime))
    return True


def _delete_core_rows(con, core_ids):
    """Drop a set of cores' per-core rows + their core_fp (changed → re-decoded; removed → dropped)."""
    params = [(c,) for c in core_ids]
    for t in ("obs", "edge", "unit_obs", "unit_member"):
        con.executemany(f"DELETE FROM {t} WHERE core_id=?", params)
    con.executemany("DELETE FROM core_fp WHERE core_id=?", params)


def write_events(cores, con, base, full=False, prune=True, finalize=True):
    """P1: decode each core to raw OBSERVATIONS and append them as events. No interning, no resolution.

    INCREMENTAL by default (⟡gqs-S1): re-decode ONLY cores whose .agdai mtime advanced since the last run
    (per-core record-version in `core_fp`); KEEP unchanged cores' rows verbatim; DROP removed cores' rows.
    The dominant cost is decode_core — ONE shim subprocess per core (~49ms × 1910 ≈ 94s a full pass) — so
    skipping unchanged cores is the whole win. project_sppf is a pure JOIN over the event tier, so kept rows
    + freshly-decoded rows yield a projection IDENTICAL to a full rebuild (gate: `sppf_db.py --verify`).
      full=True    — clean rebuild (drop the event tier): for an EVENT-schema column change, or a shim/Agda
                     toolchain change that alters decode WITHOUT changing .agdai bytes+mtime.
      prune=False  — a FILTERED partial core set: suppress removed-core deletion (`sppf_db.py Category` must
                     not delete the rest of the corpus). The full-corpus path (empty filter / gen_catalog) prunes.
      finalize=True — run the once-after-sweep tail (event GC + path_seg dedup + refresh_path_text). The
                     per-core make ingest (ingest_core) passes finalize via a separate finalize_db step.
    """
    if not _schema_current(con):                    # ⟡gqs: schema bump / fresh DB → clean rebuild (auto-migration)
        full = True
    if full:
        for t in ("event", "obs", "edge", "unit_obs", "unit_member", "core_fp"):
            con.execute(f"DROP TABLE IF EXISTS {t}")
    _drop_legacy_view(con, "path_text")             # migrate a legacy GROUP_CONCAT view → the indexed table
    con.executescript(EVENT_SCHEMA)
    _set_schema_version(con)
    con.commit()

    # Freshness: current cores + their record-versions (mtime), vs the stored per-core versions.
    cur = {}                                        # core_id → (path, relpath, mtime)
    for path in cores:
        relpath = os.path.relpath(path, base)
        try:
            cur[_b64(relpath)] = (path, relpath, _core_ver(path))
        except OSError:
            continue                                # unreadable core: treat as absent
    stored = dict(con.execute("SELECT core_id, mtime FROM core_fp"))
    changed = [c for c, (_p, _r, m) in cur.items() if stored.get(c) != m]
    removed = [c for c in stored if c not in cur] if prune else []

    stale = set(changed) | set(removed)             # rows to delete (changed → re-decoded; removed → dropped)
    if stale:
        _delete_core_rows(con, stale); con.commit()

    tid, pid = _mk_interners(con)
    for core_id in changed:                          # decode + append ONLY the changed/new cores
        path, relpath, mtime = cur[core_id]
        _decode_insert_core(con, path, relpath, mtime, tid, pid)
        con.commit()                               # transaction per file (append-only)

    if finalize:
        if stale:                                   # GC events no longer observed by any core — bounded-growth
            con.execute("DELETE FROM event WHERE ekey NOT IN (SELECT ekey FROM obs)")   # guard; inert for the projection
            con.commit()
        _dedup_pathseg(con); con.commit()
        refresh_path_text(con)                      # materialize the indexed path_text from finalized path_seg


def refresh_path_text(con):
    """Materialize path_text (path_id → dotted qname, PK-indexed) from the finalized path_seg — the interned
    projection of the append-only path segments. Refreshed at the write_events boundary so every downstream
    join is one index seek, not a full GROUP_CONCAT view materialization per query (see EVENT_SCHEMA note).
    Idempotent (DELETE+INSERT); tolerant of a legacy path_text VIEW."""
    _drop_legacy_view(con, "path_text")
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
    for ekey, ctor, qname, idx, litval in QB.run(con, QB.q_event_head()):
        if ctor in ("Var", "PVar"):        role, op = f"db{idx}", ""
        elif ctor in FREE and qname:       role, op = "", qname
        else:                              role, op = "", (ctor or "")
        head[ekey] = ("AgdaCore", role, op, litval or "")   # ⟡gqs-lit-propagate: distinct literals → distinct packings
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
    for c, unit_id, name_pid, root_lid, kind_id, module_pid, copy, level in con.execute(
            "SELECT core_id, unit_id, name_pid, root_lid, kind_id, module_pid, copy, level FROM unit_obs"):
        rootpk = pack(c, root_lid)
        if rootpk is None: continue
        urows.append((unit_id, name_pid, rootpk, c, kind_id, module_pid, root_lid, copy, level))
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
    con.executemany("INSERT OR IGNORE INTO _unit VALUES (?,?,?,?,?,?,?,?,?)", urows)
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


def _resolve_core(path, base):
    """Map a .agda SOURCE path (what the generated per-dir `ingest:` loop passes) to its .agdai core under
    `base`; pass a .agdai through unchanged."""
    if path.endswith(".agdai"):
        return path
    src_root = os.path.join(_ROOT, "agda", "Substrate")
    rel = os.path.relpath(os.path.abspath(path), src_root)
    if rel.endswith(".agda"):
        rel = rel[:-len(".agda")] + ".agdai"
    return os.path.join(base, rel)


def ingest_core(path, catalog_db=CATALOG_DB, base=None):
    """⟡gqs-make-targets: ingest ONE core. WAL + busy_timeout so parallel `make ingest` jobs SERIALIZE their
    cheap writes on the lock (parallel DECODE, serialized INSERT) instead of failing 'database is locked'.
    Self-skips via core_fp (the agda-self-skip analogue). NO finalize — prune/GC/path_text/project are the
    once-after-sweep finalize_db step. `path` may be the .agdai core OR its .agda source (resolved to the core)."""
    base = base or substrate_core_root(os.path.join(_ROOT, "agda"))
    core = _resolve_core(path, base)
    if not os.path.exists(core):
        return                                      # not built yet — nothing to ingest
    con = sqlite3.connect(catalog_db, timeout=120)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=120000")
    had = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='unit_obs'").fetchone()
    if had and not _schema_current(con):            # a pre-existing STALE-schema DB → --init/--full must migrate
        con.close()
        sys.exit("sppf_db --ingest-core: catalog.db schema is stale — run `sppf_db.py --init` (or --full) first")
    con.executescript(EVENT_SCHEMA)
    if not _schema_current(con):                    # fresh DB → stamp the current version (idempotent under -j)
        _set_schema_version(con)
    con.commit()
    relpath = os.path.relpath(core, base); core_id = _b64(relpath)
    try:
        mtime = _core_ver(core)
    except OSError:
        con.close(); return
    row = con.execute("SELECT mtime FROM core_fp WHERE core_id=?", (core_id,)).fetchone()
    if row and row[0] == mtime:
        con.close(); return                         # self-skip: mtime unadvanced (agda-self-skip analogue)
    _delete_core_rows(con, [core_id]); con.commit()  # re-ingest: drop this core's old rows
    tid, pid = _mk_interners(con)
    _decode_insert_core(con, core, relpath, mtime, tid, pid)
    con.commit(); con.close()


def init_db(catalog_db=CATALOG_DB):
    """⟡gqs-make-targets: create the event schema + set WAL ONCE, before the parallel `make ingest` sweep
    (so no ingest job races the initial CREATE). Idempotent. ⟡gqs schema-version: a STALE-schema DB (built
    at an earlier SCHEMA_VERSION) is MIGRATED here — drop the event tier so the ingest sweep re-decodes into
    the current schema (the one-time --full-equivalent, automatic)."""
    con = sqlite3.connect(catalog_db)
    con.execute("PRAGMA journal_mode=WAL")
    if not _schema_current(con):
        for t in ("event", "obs", "edge", "unit_obs", "unit_member", "core_fp"):
            con.execute(f"DROP TABLE IF EXISTS {t}")
    con.executescript(EVENT_SCHEMA); _set_schema_version(con); con.commit(); con.close()


def finalize_db(catalog_db=CATALOG_DB, base=None, argperm=True, prune=True):
    """⟡gqs-make-targets: the ONCE-after-ingest-sweep tail — prune removed cores, GC orphan events, dedup
    path_seg, refresh path_text, then PROJECT (project_sppf [+ project_argperm]). Run after `make ingest`."""
    base = base or substrate_core_root(os.path.join(_ROOT, "agda"))
    con = sqlite3.connect(catalog_db, timeout=120)
    con.execute("PRAGMA busy_timeout=120000")
    con.executescript(EVENT_SCHEMA); con.commit()
    if prune:                                       # drop cores whose .agdai no longer exists on disk
        on_disk = {_b64(os.path.relpath(p, base))
                   for p in glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True)}
        removed = [c for (c,) in con.execute("SELECT core_id FROM core_fp") if c not in on_disk]
        if removed:
            _delete_core_rows(con, removed); con.commit()
    con.execute("DELETE FROM event WHERE ekey NOT IN (SELECT ekey FROM obs)"); con.commit()  # GC orphan events
    _dedup_pathseg(con); con.commit()
    refresh_path_text(con)
    stats = project_sppf(con)
    if argperm:
        project_argperm(con)
    con.close()
    return stats


def build(cores, catalog_db=CATALOG_DB, base=None, orbit=False, distribute=False, argperm=False,
          full=False, prune=True):
    base = base or substrate_core_root(os.path.join(_ROOT, "agda"))
    con = sqlite3.connect(catalog_db)
    write_events(cores, con, base, full=full, prune=prune)   # P1: append-only events (source of truth)
    stats = project_sppf(con)                      # P2: the positional SPPF, DERIVED from events
    if argperm:
        project_argperm(con)                       # ⟡argperm: the per-def GRADED orbit-key (additive)
    if orbit:
        project_orbit_sppf(con, distribute=distribute)   # ⟡rig: the ORBIT projection (additive)
    con.close()
    return stats


_PROJ_TABLES = ("_node", "node_child", "_unit", "_unit_cod", "unit_node")


def _proj_digest(db):
    """Content-hash of every PROJECTION table (row-set, order-independent). The projection is what every gate/
    consumer reads; the shared event tier may carry inert orphans, so equality here is the honest S1 gate."""
    import hashlib
    con = sqlite3.connect(db)
    out = {}
    for t in _PROJ_TABLES:
        rows = sorted(con.execute(f"SELECT * FROM {t}").fetchall())
        out[t] = (len(rows), hashlib.sha1(repr(rows).encode()).hexdigest())
    con.close()
    return out


def verify_incremental(cores, base):
    """GATE: an incremental rebuild yields a projection IDENTICAL to a full rebuild — across all four paths
    (skip / add / remove / re-decode-changed). Returns [(name, ok, detail), …]."""
    import tempfile, shutil
    d = tempfile.mkdtemp(prefix="sppf_s1_verify_")
    checks = []
    try:
        full_db = os.path.join(d, "full.db")
        build(cores, catalog_db=full_db, base=base, full=True)      # reference: one clean full rebuild
        ref = _proj_digest(full_db)

        # A. SKIP — full(S) then incremental(S) is a no-op; kept rows preserve the projection.
        a_db = os.path.join(d, "a.db"); shutil.copy(full_db, a_db)
        build(cores, catalog_db=a_db, base=base)
        checks.append(("skip (no-op)", _proj_digest(a_db) == ref, ""))

        # B. ADD — full(S[:k]) then incremental(S) decodes the new cores + keeps the old == full(S).
        k = max(1, len(cores) // 2)
        b_db = os.path.join(d, "b.db")
        build(cores[:k], catalog_db=b_db, base=base, full=True)
        build(cores, catalog_db=b_db, base=base)
        checks.append((f"add ({len(cores)-k} new)", _proj_digest(b_db) == ref, ""))

        # C. REMOVE — full(S) then incremental(S[:-1]) prunes the dropped core == full(S[:-1]).
        c_db = os.path.join(d, "c.db"); less_db = os.path.join(d, "less.db")
        build(cores, catalog_db=c_db, base=base, full=True)
        build(cores[:-1], catalog_db=c_db, base=base)               # prune the last core
        build(cores[:-1], catalog_db=less_db, base=base, full=True)
        checks.append(("remove (prune)", _proj_digest(c_db) == _proj_digest(less_db), ""))

        # D. CHANGED — full(S), poison one core's stored version, incremental(S) re-decodes it == full(S).
        e_db = os.path.join(d, "e.db")
        build(cores, catalog_db=e_db, base=base, full=True)
        con = sqlite3.connect(e_db)
        one = con.execute("SELECT core_id FROM core_fp LIMIT 1").fetchone()[0]
        con.execute("UPDATE core_fp SET mtime=-1 WHERE core_id=?", (one,)); con.commit(); con.close()
        build(cores, catalog_db=e_db, base=base)                    # re-decodes the poisoned core
        checks.append(("changed (re-decode)", _proj_digest(e_db) == ref, ""))
        return checks
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    orbit = "--orbit" in sys.argv
    distribute = "--distribute" in sys.argv
    argperm = "--argperm" in sys.argv
    full = "--full" in sys.argv
    base = substrate_core_root(os.path.join(_ROOT, "agda"))
    # ⟡gqs-make-targets: per-core make-driven ingest. `catalog` = --init → (make -j ingest → --ingest-core per
    # file) → --finalize. Each ingest is WAL-serialized (parallel decode, serialized insert); one project pass.
    if "--init" in sys.argv:
        init_db(); sys.exit(0)
    if "--ingest-core" in sys.argv:
        ingest_core(sys.argv[sys.argv.index("--ingest-core") + 1], base=base); sys.exit(0)
    if "--finalize" in sys.argv:
        finalize_db(base=base, argperm=argperm); sys.exit(0)
    if "--verify" in sys.argv:                       # ⟡gqs-S1 gate: incremental projection == full projection
        filt = args[0] if args else "Category"       # small subtree keeps the 4-build gate fast
        cores = [c for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True)) if filt in c]
        print(f"⟡gqs-S1 verify: incremental vs full over {len(cores)} cores (filter={filt!r}) …")
        checks = verify_incremental(cores, base)
        ok = all(o for _, o, _ in checks)
        for name, o, _det in checks:
            print(f"  [{'PASS' if o else 'FAIL'}] {name}")
        print("⟡gqs-S1 verify: " + ("ALL PASS — incremental ≡ full" if ok else "FAILED"))
        sys.exit(0 if ok else 1)
    filt = args[0] if args else "Category"
    cores = [c for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True)) if filt in c]
    print(f"event-sourcing {len(cores)} cores (filter={filt!r}) → catalog.db (events, then project SPPF"
          f"{', + ORBIT' if orbit else ''}) …")
    n, u, sh, mx = build(cores, orbit=orbit, distribute=distribute, argperm=argperm,
                         full=full, prune=(filt == ""))
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
