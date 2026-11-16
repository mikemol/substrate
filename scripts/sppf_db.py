#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
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

import sys, os, glob, base64, json, time, re
from _content_addr import _b64
from collections import defaultdict

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jea", "metalanguage")
)
import query_builders as QB  # ⟡query-rawtocore: single-source Core builders (run = execute)

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "jea", "metalanguage"))
from jea_agdai import decode_core, substrate_core_root
from jea_rigcat import RIG_OPS  # ⟡rig orbit-interning (the proven ⊕/⊗ op-set)
import store as _store  # THE store authority: dsn, dialect, connect
import schema as _schema  # THE schema declaration: DDL synthesized per dialect

# ⚑⚑ `CATALOG_DB` IS GONE WITH SQLITE (⓺, 2026-08-11), AND IT WAS NOT A DEFAULT — IT WAS A
# SENTINEL, which is why deleting it changed a branch rather than a value. `build()` read
# `catalog_db in (None, CATALOG_DB)` to mean *"is this the LIVE store?"*, taking the
# authority's connection when true and `sqlite3.connect(catalog_db)` when false. The false
# arm existed for exactly one caller — `verify_incremental`, which built four throwaway
# `.db` FILES — and that caller is retired (★ⓢ, see the `--verify` note at the dispatch).
# With no caller passing a path, the sentinel tests a condition that is always true, so the
# parameter and both arms collapse into the one connection the authority already owns.
#
# ⚑ THE ORIGINAL DIVERGENCE THIS LINE RECORDED IS STILL THE REASON THERE IS NO REPLACEMENT
# CONSTANT: eight modules derived the catalog path independently and only THIS one honoured
# an env override (`SPPF_CATALOG_DB`), so a redirected build wrote one store while every
# reader queried another, silently. The fix was one resolver; the removal is the same fix
# taken to its end, since a path constant with no file behind it is a ninth spelling
# waiting to happen.
# ⚑⚑ THE DECODED-RECORD READER NOW LIVES IN `sppf_recover.py` (⟡split-1200, 2026-08-11) AND
# THIS RE-IMPORTS IT. That layer — `leaf_value`, `_unescape_haskell`, `_child`, `_name_text`,
# `_qname_text`, `recover_fields`, and the `FREE` constructor set they read — is the ONE part
# of this module that consumes nothing from it: pure functions over a decoded record and its
# node map, importing `re` and nothing else. Every other def here consumes THEM. So the seam
# is the ARROW: moving the SUPPLIER leaves a leaf, where moving a consumer (`project_sppf`,
# `write_events`) would have closed a cycle. Size named the violation; direction chose the cut.
#
# ⚑ NAMED IMPORTS, NOT A STAR, BECAUSE THE SURFACE IS SMALL AND ENUMERABLE. `schema.py` uses
# `import *` because it re-exports ~87 names across four modules and a hand list would be a
# second roster to keep in step; six names is not that, and the explicit list is what makes
# `_child`/`_LEAF_RE` reachable at all — `import *` skips a leading underscore by construction,
# the defect that silently broke `schema._node` while 123 cases still passed.
from sppf_recover import (
    FREE,
    _child,
    _name_text,
    _qname_text,  # noqa: F401
    _unescape_haskell,
    leaf_value,
    recover_fields,
)

# ⚑⚑ THE DECODE→ROWS LAYER NOW LIVES IN `sppf_decode.py` (⟡split-1200, 2026-08-11) AND THIS
# RE-IMPORTS IT. `_mk_interners`, `_decode_raw`, `_decode_window`, `_decode_insert_core` and
# `_insert_decoded` consume `_schema` / `query_builders` / `_b64` / `decode_core` /
# `recover_fields` and NOTHING from this module, while `write_events`, `ingest_core` and
# `project_orbit_sppf` all consume THEM. So the seam is the ARROW again, and the measurement
# is what chose it: the obvious cut was the additive projections (`project_orbit_sppf` +
# `project_argperm`, ~190 physical lines, separable as a capability) — and
# `project_orbit_sppf` CALLS `_mk_interners`, so moving it would have closed a cycle. Moving
# the supplier leaves a leaf. Size named the violation; direction chose the cut.
#
# ⚑ THE VIOLATION WAS PHYSICAL, NOT CODE. This file read `993 code — OK, 207 under its cap`
# at 1,754 PHYSICAL lines: it passed the metric while being past the point the rule names
# (*"too large to read whole and write back out"*). `pycodemod --size` now prints both
# counts, so the next such file is visible without anyone opening it.
from sppf_decode import (
    _decode_insert_core,
    _decode_raw,  # noqa: F401
    _decode_window,
    _insert_decoded,
    _mk_interners,
    decode_reason_cases,
    undecodable_census,
    undecodable_report,
    reconcile_stamps,
    reconcile_stamp_cases,
    reconcile_report,
    SOURCE_MODES,
    source_cli,
    source_row_cases,
)
from sppf_vocab import vocab_cases  # ⟡ladder-2: the VOCAB tier's cases only
from sppf_tree import tree_cases  # ⟡ladder-4: the TREE tier's cases only
from sppf_drain import drain_cases  # ⟡ladder-retire: the DRAIN's cases only

# ⟡gqs-S0.2/⟡gqs-lit-propagate: bump on ANY EVENT_SCHEMA/SPPF_SCHEMA column change. A catalog.db built at a
# lower `PRAGMA user_version` is auto-migrated by a clean --full rebuild (init_db drops the event tier; the
# batched write_events forces full) — so a column add never breaks the incremental path on a stale DB.
SCHEMA_VERSION = 2

# ⚑ RETIRED AS THE SOURCE OF TRUTH (2026-08-06) — `jea/metalanguage/schema.py` now
# declares this as a SQLAlchemy model and EMITS the DDL per dialect; `write_events` calls
# `schema.apply(con, only="event")`. Kept, not deleted, for two reasons: it is the text
# the declaration was READ FROM (types, keys, indexes, the `producer` default all came
# from here, not from what a column name suggests), and it is the only record of what the
# sqlite store was actually built with — which the port must be diffable against.
# ⚑ DO NOT EDIT TO CHANGE THE SCHEMA. Editing this now changes nothing: it is executed by
# no one. The model in schema.py is what runs.
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
-- ⚑ `producer` SCOPES THE PRUNE, AND ITS ABSENCE WAS A STORE-WIPING HAZARD (user,
-- 2026-08-05).  `write_events` computes `removed = [c for c in stored if c not in cur]`
-- over EVERY core_fp row.  That is correct while ONE producer owns the store — "not in
-- the set I was handed" then means "deleted from the tree".  The moment a SECOND
-- producer ingests (Python source, or an Agda SURFACE tier), it is catastrophic: a
-- Python ingest hands over .py paths, no Agda core is in `cur`, and the whole Agda tier
-- is deleted.  MEASURED on a copy before this column existed: a disjoint core set took
-- a seeded mini-catalog from 38 cores / 1436 obs to 0 / 0.  Against the live 3.3 GB
-- store that is 3048 cores, 1.67M obs and 23002 units, in one call.
--
-- ⚑ THE GUARD EXISTED AND WAS A CONVENTION, NOT A PROPERTY.  `prune=False` preserves
-- the tier (measured, same probe) — but `build()` defaults `prune=True`, so the only
-- thing between a new front-end and a wiped catalog was remembering a keyword.  That is
-- the `prune_imports` write-by-default shape: the safe path exists and is not the
-- default.  With a producer column the correct behaviour is STRUCTURAL — a run may only
-- prune rows it owns, so "the full core set" is well defined per tier instead of
-- becoming ambiguous the moment the store holds two.
CREATE TABLE IF NOT EXISTS core_fp (core_id TEXT PRIMARY KEY, mtime INTEGER, producer TEXT NOT NULL DEFAULT 'agdai');
"""

# The SPPF projection tables (materialized).
# ⚑ RETIRED AS THE SOURCE OF TRUTH (2026-08-06) — see EVENT_SCHEMA's note. `project_sppf`
# calls `schema.apply(con, only="sppf")`, which emits these tables and their indexes from
# the declaration. MEASURED DEAD: `pycodemod --binding SPPF_SCHEMA` reports 1 binding (this
# assignment) and no read at all, so it is a record of the pre-port schema, not a builder.
#
# ── THE FIVE `CREATE VIEW IF NOT EXISTS` STATEMENTS THAT CLOSED THIS STRING — DELETED
# ── 2026-08-12 (⟡view-purge). They spelled `node`, `unit`, `node_fanin`, `shared_subtree`
# ── and `node_atom` in SQL text, the last `CREATE VIEW` in the tree.
#
# ⚑⚑ THE HEADER'S OWN ARGUMENT FOR THEM IS KEPT BECAUSE IT IS STILL TRUE AND IS NOW MET
# THE OTHER WAY: *"The views were the near-miss in that port: an emitter carrying only
# tables would have produced a store where every table and index is present and every
# READER fails, since `catalog_query`/`sppf_query`/half the builders select from
# `node`/`unit`/`shared_subtree` rather than from `_node`/`_unit`."* Every one of those
# readers now COMPOSES the fragment instead of naming a stored relation, so the store may
# carry only tables and no reader fails. The near-miss was real; the remedy moved.
#
# ⚑ AND A DEAD STRING IS STILL A SECOND SPELLING. Nothing executed these, so they broke
# nothing — but `shared_subtree AS SELECT … FROM node_fanin WHERE fanin >= 2` sat here as a
# rival definition of a relation defined in `schema_decl`, free to drift from it with no
# gate able to see the disagreement. That is the `text()`-blob shape one level down.
SPPF_SCHEMA = """
CREATE TABLE IF NOT EXISTS _node      (node_id TEXT PRIMARY KEY, kind_id TEXT, role_id TEXT, op_term_id TEXT, op_path_id TEXT, lit_id TEXT);
CREATE TABLE IF NOT EXISTS node_child (node_id TEXT, ord INT, child_id TEXT);
CREATE TABLE IF NOT EXISTS _unit      (unit_id TEXT PRIMARY KEY, name_pid TEXT, root_id TEXT, file_id TEXT, kind_id TEXT, module_pid TEXT, root_lid INT, copy INT, level INTEGER);
-- the codomain HEAD of each unit's type (raw_final_head: unwrap Defn, peel the Pi-telescope), computed
-- structurally at PROJECTION time over the unambiguous per-core tree (the reentrant packing bridge would
-- conflate contexts). The catalog reads THIS (a structural attribute of the projection), not raw events.
CREATE TABLE IF NOT EXISTS _unit_cod  (unit_id TEXT PRIMARY KEY, cod_ctor_id TEXT, cod_qname_pid TEXT);
CREATE TABLE IF NOT EXISTS unit_node  (unit_id TEXT, node_id TEXT);
CREATE INDEX IF NOT EXISTS ix_nc_node  ON node_child(node_id);
CREATE INDEX IF NOT EXISTS ix_nc_child ON node_child(child_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_nc_edge ON node_child(node_id, ord, child_id);
CREATE INDEX IF NOT EXISTS ix_un_unit  ON unit_node(unit_id);
CREATE INDEX IF NOT EXISTS ix_un_node  ON unit_node(node_id);
CREATE UNIQUE INDEX IF NOT EXISTS ix_un_edge ON unit_node(unit_id, node_id);
"""


def _dedup_pathseg(con):
    # ⚑ WAS `rowid`-BASED, WHICH IS SQLITE-ONLY — and postgres's `ctid` is NOT a
    # substitute: it is a physical location that changes on UPDATE and after VACUUM, so
    # `MIN(ctid)` names a different row over time. `schema.dedup` uses a window function,
    # which both engines support and which says what is meant.
    _schema.dedup(con, "path_seg", ["path_id", "ord"])


def _drop_legacy_view(con, name):
    """Drop a legacy GROUP_CONCAT VIEW so the PK-indexed TABLE can take its place. A NO-OP once `name`
    is already the table: `DROP VIEW IF EXISTS <table>` raises OperationalError ("use DROP TABLE …") —
    the one-time view→table migration is done, so there is nothing to drop. (⟡catalog-regen-fix: this
    stale assumption crashed gen_catalog.py's SPPF walk once path_text became a table.)"""
    # ⚑ ASK, DO NOT CATCH. `DROP VIEW IF EXISTS <table>` raises on sqlite ("use DROP
    # TABLE"), and this swallowed that. On POSTGRES the same catch is a trap: any error
    # aborts the whole transaction, so a swallowed exception poisons every statement
    # after it (`InFailedSqlTransaction`) — measured four frames away from its cause.
    # `relations()` answers whether the name is a view WITHOUT risking the transaction.
    if _schema.relations(con).get(name) == "view":
        con.execute(f"DROP VIEW IF EXISTS {name}")


def _core_ver(path):
    """The core's record-version = its .agdai mtime in ns (a `stat`, ~µs vs decode_core's ~49ms subprocess).
    agda rewrites the interface on every recompile, so an advanced mtime IS 'rebuilt since we last decoded' —
    exactly the freshness question (⟡freshness-stance). st_mtime_ns is an exact integer (no float-repr drift)."""
    return os.stat(path).st_mtime_ns


def _schema_current(con):
    """True iff the store was built at the current SCHEMA_VERSION (else a column add needs a --full migration).

    ⚑ WAS `PRAGMA user_version` — a 32-bit slot in the sqlite FILE HEADER, not a SQL
    feature, with no postgres equivalent. `schema.schema_version` reads a table instead,
    and returns None for a store built before versioning existed — which must compare
    UNEQUAL here so an old store triggers the full migration rather than being certified
    current by a falsy comparison.
    """
    return _schema.schema_version(con) == SCHEMA_VERSION


def _set_schema_version(con):
    _schema.set_schema_version(con, SCHEMA_VERSION)


# ── `PROJECTION_CONSUMER = "sppf:projection"` — DELETED 2026-08-12 with the registry. ──────
#
# It named this module's row in `consumer`. The projection's own criterion was already written
# down and already derivable — `lifecycle.py`: *"sppf:projection — consumed ⟺ this
# observation's node exists in the projection. Frontier = max(seq) over `obs ⋈ obs_node`"* —
# so the stored position was a CACHE of a join, and the cache is what kept going wrong (three
# live-store damages, a live cursor copied into the sandbox, a cursor outliving a dropped tier).
# ── `_gc_orphan_events` — RETIRED 2026-08-22 (⟡finalize-tail-home). Its BODY was already
# `return _schema.reclaim(con, dry_run=False)` — a one-line delegation to the same call
# `_do_retire` makes directly — and its ONLY caller was the `finalize` tail, itself the
# removed `finalize_db` mode surviving as a default-true keyword. With the tail gone:
# `--calls _gc_orphan_events` → 1 def, 0 calls, ⚑ DEAD CAPABILITY; `--literal` corpus-wide
# → one docstring mention, no string dispatch. Cross-checked for the aliased-reader case
# `--dead`'s own caveat names, since this repo DELETES on that verdict.
#
# ⚑ THE CAPABILITY IS NOT LOST, IT MOVED TO THE BOUNDARY — which is the cycle working as
# intended (operator: *"the whole point behind the ingest->intern->reflect->retire cycle
# that we finally got down to tiny commits and resumable progress"*). Reclamation is
# `schema.reclaim` under `q_drainable_res`, per-core and residue-driven; this wrapper was
# the sweep-shaped entry point to it.
#
# ⚑ THE REASONING WORTH KEEPING, in the idiom `_advance_projection` set below:
#   *"The old statement was `DELETE FROM event WHERE ekey NOT IN (SELECT ekey FROM obs)`,
#   written twice. MEASURED on the live store: 38 minutes, spilling to disk, `backend_xid`
#   NULL — it had not modified a single row before being cancelled. `NOT IN` over a 506k-row
#   subquery cannot use the index because of NULL semantics."*  And why the replacement is
#   LEGAL rather than merely faster: *"an orphaned event is unreachable by any live read, so
#   reclamation needs neither atomicity nor synchrony"* — which is what licenses a bounded,
#   interruptible sweep in place of a blocking full-table delete.
#
# ⚑ AND ITS ORDERING ARGUMENT IS NOW STRUCTURAL, not a rule to remember: *"advancing the
#   cursor before consuming would license reclaiming rows still to be read."* Under
#   `q_drainable_res` a core is drainable only if `obs_node` ALREADY addresses it, so the
#   promise is not made ahead of the work — it IS the work, read from one snapshot.

# ── `_advance_projection` — DELETED 2026-08-12. Its safety argument is now structural. ─────
#
#     Move the projection's cursor to the settled HWM — called AFTER it consumes.
#
# ⚑ ITS ⚑ BLOCK IS THE ONE TO KEEP, because it states the invariant that the residue licence
# now satisfies by construction: *"THE CURSOR IS THE CONSUMER'S PROMISE THAT IT NO LONGER NEEDS
# ANYTHING BELOW IT. Advancing before consuming would license reclaiming rows still to be read;
# advancing after is what makes the NEXT run's reclaim provably safe."* Under `q_drainable_res`
# a core is drainable only if `obs_node` ALREADY addresses it, so the promise is not made ahead
# of the work — it IS the work, read from the same snapshot.
#
# ⚑ AND THE CALL-ORDER COMMENTS AT ITS TWO CALL SITES WENT WITH IT. Both said the same thing
# (*"BEFORE `_advance_projection` … advancing the cursor first would publish a promise that
# nothing below the HWM is needed while this projection had not yet read it"*) — an ordering
# constraint between two separately-committed writes, which `lifecycle.py`'s standing note
# identifies as *"a distributed-commit problem being solved by call order."* One write remains.


# ── `_selftest_queue_wiring` — DELETED 2026-08-12 WITH THE INVARIANT IT NEVER POLICED. ─────
#
#     Every path that PROJECTS must also ADVANCE — a structural check, not a review.
#
# ⚑ ITS FINDING IS REAL AND IS WORTH KEEPING: *"`gen_catalog` advanced and `build` did not; a
# full ingest through `build` projected 10,536 units and left the cursor at 0, which pins the
# reclamation floor forever while every surface reads healthy."* A capability wired into one of
# two entry points is the recurring defect in this file — it recurred again one projection
# later with `project_ref`, and THAT case is live in `_selftest` and stays.
#
# ⚑⚑ AND IT WAS *ITSELF* AT 1 def / 0 calls FOR ITS WHOLE LIFE — measured with the very
# instrument its docstring cited (`pycodemod --calls _selftest_queue_wiring`). Written to make
# an invariant checkable, never wired into `_selftest`, so it policed nothing. It is deleted
# rather than finally wired because its subject went first: *"'Every path that projects must
# also advance' is a claim about a STORED CURSOR; `converge` projects and advances nothing,
# deliberately."*
#
# ⚑ WHAT IT SHOULD BECOME IS STILL OWED AND STILL UNBUILT: the residue census — *every path
# that PROMOTES must leave the residue empty* — a different predicate over the same AST
# instrument. Named here so it reads as work rather than as a capability that was lost.


#: Cores per delete transaction. ⚑ THE SAME UNIT THE DECODE LOOP ALREADY USES (`W = 64`
#  at :469) — and deliberately the same NUMBER, because both bound the same thing: how much
#  work one transaction may hold. Two windows with two constants would be two policies.
_DELETE_W = 64


def _delete_core_rows(con, core_ids):
    """Drop a set of cores' per-core rows + their core_fp (changed → re-decoded; removed → dropped).

    ⚑ WINDOWED, ONE COMMIT PER WINDOW — and it was NOT, which is how a GATE deadlocked the
    store. MEASURED 2026-08-21: `set1_ratchet_cores.py --quiet` (a gate whose only job is to
    COUNT Set₁ debt) reaches this through `_freshen` → `write_events(prune=True)`, and died after
    ~1.5h with `psycopg.errors.DeadlockDetected` — process 144 waiting on a `RowExclusiveLock`
    held by 2128 while 2128 waited on a `ShareLock` held by 144, opposite acquisition order on
    `path_text`/`terms`.

    ⚑⚑ THE OLD SHAPE WAS: the WHOLE doomed set, five relations, ONE transaction, no window and
    no intermediate commit — while the DECODE loop FIFTEEN LINES BELOW its caller was already
    windowed at `W = 64` with a commit per window (*"transaction per window (append-only)"*).
    One function held both shapes; the appender was incremental and the deleter was not.

    ⚑ WINDOWING SUBTRACTS THE HOLD-AND-WAIT RATHER THAN SURVIVING IT, which is the whole
    reason it is the right fix. `deadlock-breakdown-before-any-fix` records that every
    antipattern for a deadlock ADDS coordination — a retry loop, a global lock order, a
    serializing mutex — each making the cycle survivable instead of absent. A bounded hold has
    no time to form one. It is the same subtraction `converge` made at the promote boundary.

    ⚑ AND A KILL NOW LOSES ONE WINDOW, NOT EVERYTHING. The deadlocked run held a single write
    xid across `DELETE FROM obs` then `DELETE FROM edge` for the entire corpus — the *"step
    that either completes or loses everything"* shape. Committing per window makes the delete
    RESUMABLE in the only sense that matters here: the cores already dropped stay dropped, and
    a re-run recomputes `doomed` from the store and finds them absent.

    ⚑ THE RELATION LOOP STAYS INSIDE THE WINDOW, not outside it. Deleting all of `obs` then
    all of `edge` would hold locks on both for the whole run; deleting one window across all
    five relations keeps each transaction short AND leaves the store per-core consistent at
    every commit boundary — a window either dropped a core entirely or has not touched it.

    ⚑ TWO PORTING DEFECTS PER LINE, travelling together (the original note, still true):
    `con.executemany` (sqlite3 puts it on the CONNECTION, psycopg only on a CURSOR) and a
    hardcoded `?`.
    """
    ids = list(core_ids)
    _p = _schema.ph()
    for i in range(0, len(ids), _DELETE_W):
        params = [(c,) for c in ids[i : i + _DELETE_W]]
        for t in ("obs", "edge", "unit_obs", "unit_member", "core_fp"):
            _schema.execute_many(con, f"DELETE FROM {t} WHERE core_id={_p}", params)
        con.commit()


def write_events(cores, con, base, prune=True, producer="agdai"):
    """P1: decode each core to raw OBSERVATIONS and append them as events. No interning, no resolution.

    INCREMENTAL by default (⟡gqs-S1): re-decode ONLY cores whose .agdai mtime advanced since the last run
    (per-core record-version in `core_fp`); KEEP unchanged cores' rows verbatim; DROP removed cores' rows.
    The dominant cost is decode_core — ONE shim subprocess per core (~49ms × 1910 ≈ 94s a full pass) — so
    skipping unchanged cores is the whole win. project_sppf is a pure JOIN over the event tier, so kept rows
    + freshly-decoded rows yield a projection IDENTICAL to a full rebuild.
      ⚑ THIS SENTENCE USED TO CITE A GATE — a `--verify` mode of this very tool — AND THAT MODE
                     DOES NOT EXIST. (The dead citation is not re-spelled here: `parse_usage` reads
                     any line carrying the stem and a `--flag` AS A DECLARATION, so quoting it even
                     to retract it would re-declare it and keep the census row alive.) Not retired-and-forgotten: no dispatch branch, no argv literal, and no
                     successor under another spelling (`toolmodes --find verify` lists it as declared
                     by NO tool, with an empty gloss, because the parser was reading THIS LINE as the
                     declaration). So the identical-projection claim above is ASSERTED, not gated —
                     which is the load-bearing correction: a reader who trusted the citation believed
                     a property was mechanically checked when nothing checks it. Building the gate is
                     WORK (it would rebuild full and diff the projection); naming one that does not
                     exist is worse than naming none, so the citation is removed and the gap is stated.
      full=True    — clean rebuild (drop the event tier): for an EVENT-schema column change, or a shim/Agda
                     toolchain change that alters decode WITHOUT changing .agdai bytes+mtime.
      prune=False  — a FILTERED partial core set: suppress removed-core deletion (`sppf_db.py Category` must
                     not delete the rest of the corpus). The full-corpus path (empty filter / gen_catalog) prunes.
      ⚑ `finalize=` IS GONE (2026-08-22). It gated the once-after-sweep tail — event GC + path_seg
                     dedup + refresh_path_text — three corpus-wide operations behind a DEFAULT-TRUE
                     keyword, i.e. the retired `finalize_db` mode surviving as an argument. Its docstring
                     here even cited "a separate finalize_db step" that no longer exists. See the ⚑ block
                     at the former branch site; the tail needs a singleton home (⟡finalize-tail-home).

    RETURNS `{relpath: typed-reason}` for every core in `cores` that did NOT ingest.

    ⚑⚑ THE RETURN VALUE IS NEW (⑼, 2026-08-12) AND IT IS THE ONLY WAY THE REASON GETS OUT.
    `_insert_decoded` has always returned True/False, and every caller discarded it — so an
    undecodable core left NO trace in this function's output, and `converge` had to infer the
    failure by re-reading `core_fp` and could therefore report only THAT it happened. A
    boolean that no caller reads is the same as no boolean; a per-core reason that no caller
    can receive is the same as no reason.

    ⚑ ADDITIVE: every existing caller ignores the return, so nothing had to change to keep
    working — which is what makes this a reporting fix rather than a control-flow one.
    """
    # ⚑⚑⚑ ⟡no-automated-drop — THE `full` TIER-DROP WAS REMOVED HERE (2026-08-22, operator:
    # *"Let's get rid of --full. I'm not ready to trust it."*). It read:
    #
    #     if not _schema_current(con): full = True          # ← AUTOMATIC, nobody passed a flag
    #     if full:
    #         for t in ("event","obs","edge","unit_obs","unit_member","core_fp"):
    #             con.execute(f"DROP TABLE IF EXISTS {t}")
    #
    # ⚑⚑ TWO SEPARATE REASONS, AND THE SECOND IS THE WORSE ONE. First, six `DROP TABLE`s inside
    # `write_events` — a function the make-driven ingest calls PER CORE, so a destructive DDL
    # taking `AccessExclusiveLock` sat on an automated path at build concurrency (⟡no-automated-
    # drop: *"drop-table statements should not be automated"*). Second, and not flag-driven at
    # all: `_schema_current()` returning false SET `full = True` ITSELF, so a schema-version bump
    # silently dropped the entire event tier of whatever tenant happened to be connected. A
    # destructive migration that nobody invoked is the one an operator cannot decline.
    #
    # ⚑ AND `--full` MEANT TWO DIFFERENT THINGS, which is its own argument for removal. On
    # `--ingest-core` it means *"re-decode this core even if its mtime is unadvanced"* — the
    # shim-changed case, NON-destructive, and that spelling survives untouched. Only this
    # tier-dropping sense is gone. One flag with a benign meaning on one path and a
    # six-table drop on another is exactly the ambiguity that makes it untrustworthy.
    #
    # ⚑ THE INCIDENT LOG THE BLOCK CARRIED IS KEPT, because the RULE it states outlives the code:
    #   *"A CURSOR OUTLIVING THE TIER IT DESCRIBES IS A STALE PROMISE"* — dropping the event tier
    #   without resetting the registry left `sppf:projection` at 1,255,689 over a tier whose
    #   `seq` restarts at 1 (a `--full --sandbox` rebuild died: *"cursor is forward-only …
    #   refused move to 0"*). The harmful direction is the other one: a retained HIGH cursor over
    #   a fresh tier would, once `seq` climbed past it, license reclaiming rows no consumer had
    #   read. That is WHY there is no cursor today, and the reasoning is why the drop had to be
    #   understood before it could be removed.
    #   ⚑ `obs_node` WAS DELIBERATELY NOT IN THE DROP LIST, and that asymmetry is still live:
    #   `reconstruct --drained` reads it to rebuild cores tier 0 no longer holds (measured
    #   627,327 rows over 40 drained cores), so dropping it would destroy the durable answer for
    #   exactly the cores that need it. It is why `drained()` is anchored on `obs_node ∖ obs`.
    #
    # ⚑ REBUILDING A TIER IS NOW A DELIBERATE, SINGLETON ACT — `schema.py --flush <TIER> --apply`
    # (dry-run by default), stated by an operator, not a side effect of an ingest noticing a
    # version mismatch.
    if not _schema_current(con):
        raise SystemExit(
            "REFUSED: the store's schema version is stale and this path no longer migrates it.\n"
            "  It used to set `full = True` and DROP six tables automatically — an unrequested\n"
            "  destructive migration on the per-core ingest path (⟡no-automated-drop).\n"
            "  Rebuilding a tier is a deliberate singleton act:\n"
            "    python3 jea/metalanguage/schema.py --flush event --live --apply"
        )
    _drop_legacy_view(con, "path_text")  # migrate a legacy GROUP_CONCAT view → the indexed table
    # ⚑ SYNTHESIZED FROM THE DECLARATION, not from a DDL string (user, 2026-08-06:
    # *"Doesn't SQLAlchemy give us a way to synthesize DDL from spec?"*). `EVENT_SCHEMA`
    # remains below as the RETIRED source; this is now emitted per-dialect from
    # `schema.py`'s model.
    #
    # ⚑ AND `executescript` WAS THE PORTING BLOCKER, not the SQL. It is sqlite3-only —
    # psycopg has no such method — so this line would have raised `AttributeError` on the
    # postgres path however correct the schema was. `schema.apply` executes statements
    # individually, which both drivers support.
    _schema.apply(con, only="event")
    _set_schema_version(con)
    con.commit()

    # Freshness: current cores + their record-versions (mtime) + STRUCTURAL bound (bytes), vs stored versions.
    cur = {}  # core_id → (path, relpath, mtime, bytes)  [⟡gce-surfaces]
    for path in cores:
        relpath = os.path.relpath(path, base)
        try:
            # ⚑ ⓝ P4: the id is MINTED FROM THE STORE, not derived from the path. Note this
            # runs before the mtime/size reads, so an unreadable core still gets an id — which
            # is correct: the id names the core, and whether it can be read is a later fact.
            cur[_schema.core_id_for(relpath, con)] = (
                path,
                relpath,
                _core_ver(path),
                os.path.getsize(path),
            )
        except OSError:
            continue  # unreadable core: treat as absent
    stored = dict(QB.run(con, "core_fp_mtimes"))
    changed = [c for c, (_p, _r, m, _sz) in cur.items() if stored.get(c) != m]
    # ⚑ PRUNE IS SCOPED TO THE PRODUCER, so a run may only drop rows IT OWNS.
    # `removed` used to read every core_fp row, which means "not in the set I was
    # handed" ⇒ "deleted from the tree". True while ONE producer owns the store;
    # a store-wiping bug the moment a second one ingests — MEASURED on a copy:
    # a disjoint core set took a seeded catalog from 38 cores/1436 obs to 0/0.
    # Scoping makes "the full core set" well defined PER TIER, so correctness
    # stops depending on the caller remembering `prune=False`.
    #
    # ⚑ READ FROM THE STORE, NOT INFERRED FROM THE PATH. `core_id` is
    # `_b64(relpath)`, so a suffix test would have to re-derive the producer from
    # a filename the id does not carry — re-deriving a fact the store can hold,
    # which is the shape being retired everywhere else this session.
    # ⚑ WAS `con.execute("… WHERE producer=?", …)` — the sqlite paramstyle, which psycopg
    # rejects outright (`0 placeholders but 1 parameters`). Written earlier TODAY, in the
    # same session as the store authority, which is the honest measure of how easily the
    # idiom reproduces: the fix is not knowing better once, it is routing every read
    # through one contract so there is no per-site chance to get it wrong.
    mine = {
        r["core_id"]
        for r in _schema.rows(
            con, f"SELECT core_id FROM core_fp WHERE producer={_schema.ph()}", (producer,)
        )
    }
    removed = [c for c in stored if c not in cur and c in mine] if prune else []

    # ⚑ NAMED `doomed` AND NOT `stale`, AND THE DIFFERENCE IS NOT COSMETIC.  This is
    # a DELETE WORK-LIST, not a freshness verdict: `changed` cores are outdated (a
    # re-decode supersedes them), but `removed` cores are GONE FROM THE TREE — never
    # stale, simply absent.  Half the set was misdescribed by the old name, which
    # named the cause of ONE input instead of the meaning of the set.
    #
    # ⚑ AND `stale` WAS DOING FIVE JOBS ACROSS THIS REPO — mtime-vs-source here and
    # at `_core_ver`, content-hash-vs-recorded in `run_selftests`, set-difference in
    # `check_feature_coverage`, rederived-vs-committed in `toolmodes`, and this
    # work-list.  One word over five distinct comparisons means a reader must open
    # the site to learn which is meant, and a census cannot join them at all.
    doomed = set(changed) | set(removed)  # rows to delete (changed → re-decoded; removed → dropped)
    if doomed:
        _delete_core_rows(con, doomed)
        con.commit()

    # ⟡gqs-catalog-engine — the CONTROLLER/ACTUATOR decode. The HOST (this loop) modelled the topology once
    # (cur = per-core bytes), then per WINDOW composes an EPOCH-COHERENT stat package (co-read live_state ONCE →
    # P_effective + achieved cost, decode_cost.package) and CONSUMES it: decode serial or via a ThreadPool of P*
    # (parallel shim decode; interner+DB insert stays serial → NO python-spawn tax), then records each decode's
    # (bytes, seconds, load) back to the ledger (self-calibrating). The operating point tracks the LIVE
    # contention per window — poll, don't benchmark. [[feedback_cost_is_structural_times_live]]
    tid, pid = _mk_interners(con)
    undecodable = {}  # relpath → typed decode reason (⑼)
    if changed:
        import decode_cost as DC

        sizes = {c: cur[c][3] for c in changed}
        hist = DC.load_hist()  # SURFACES: per-core intrinsic decode estimates (median-of-K)
        W = 64  # window: re-read live_state every W cores (ongoing refresh)
        i = 0
        while i < len(changed):
            window = changed[i : i + W]
            i += len(window)
            pkg = DC.package(
                window, sizes, hist
            )  # HOST: co-read live_state + compose the whole package (1 epoch)
            for c, (dec, why, secs) in zip(
                window, _decode_window([cur[c][0] for c in window], pkg["P_star"])
            ):
                if not _insert_decoded(
                    con, dec, cur[c][1], cur[c][2], tid, pid, producer=producer
                ):  # SERIAL insert
                    # ⚑ THE FALLBACK REASON IS NOT "UNKNOWN". `_insert_decoded` returns False
                    # only when `dec is None`, and `_decode_raw` returns a reason with every
                    # None — so an empty `why` here would mean the two disagree, which is a
                    # fact worth naming rather than papering over with a blank.
                    undecodable[cur[c][1]] = why or (
                        "decode returned None with NO reason — `_decode_raw` and "
                        "`_insert_decoded` disagree about what a failed decode is"
                    )
                DC.record(c, cur[c][3], secs, pkg["load1"])  # ⟡gce-record-back (state-stamped)
            con.commit()  # transaction per window (append-only)

    # ⚑⚑⚑ THE `finalize` TAIL IS GONE — IT WAS `finalize_db` SURVIVING AS A KEYWORD DEFAULT
    # (operator, 2026-08-22: *"Remember, we got rid of the finalize mode today"*). The mode was
    # removed for being *"intrinsically wide, deep and atomic. Worst possible granularity"*;
    # this branch ran the SAME three corpus-wide operations — `_gc_orphan_events`,
    # `_dedup_pathseg`, `refresh_path_text` — behind `finalize=True`, the DEFAULT, inside a
    # function the per-core ingest calls. Deleting a mode while leaving its body reachable
    # under a defaulted flag is the removal not finishing.
    #
    # ⚑ MEASURED, AND THE CALL SITES ALREADY SAID SO. `--forwards write_events finalize` → 1 of
    # 3 sites forward it; `--values` → that one passes **False**. So the only caller with an
    # opinion (`_do_ingest`, the make-driven per-core path) OPTS OUT, and the two that inherit
    # the corpus-wide tail do so silently — one of them `set1_ratchet_cores._freshen`, already
    # recorded as the read-only gate that prunes and re-ingests the corpus and deadlocked after
    # ~1.5h. A wide atomic sweep nobody asked for, on a gate that only counts.
    #
    # ⚑⚑ AND THE BRANCH WAS DEAD ANYWAY, WHICH IS HOW IT WAS FOUND: it read `if stale:` and
    # `stale` is bound NOWHERE in this file (`--binding stale` → 0 bindings in 0 of 1 file(s)),
    # so every `finalize=True` run reaching it raised `NameError`. `_gc_orphan_events` has one
    # call site — that one — so the event GC has never run from here. The ⚑ block above records
    # renaming that variable to `doomed` and explains why the distinction matters; the rename
    # updated the binding and one use, not this one.
    #
    # ⚑ MY FIRST MOVE WAS TO REPAIR IT (`if doomed:`), WHICH RE-LEGITIMIZES THE PARAMETER —
    # exactly the pull the operator named when removing the mode: *"because it EXISTS, LLMs
    # keep thinking its legitimate, and keep leaning on it one way or another."* A dead branch
    # under a retired mode's flag is evidence the removal is unfinished, not a bug to fix.
    #
    # ⚑ WHAT THE THREE OPERATIONS NEED IS A HOME AT THE RIGHT GRANULARITY, and that is WORK,
    # not residue — a singleton, operator-stated act like `schema.py --flush <TIER> --apply`,
    # never a tail that fires because a keyword defaulted true. Recorded as ⟡finalize-tail-home
    # rather than silently dropped: `path_text` is a materialized index some reader expects
    # fresh, and nothing here establishes who.
    return undecodable


def refresh_path_text(con):
    """Materialize path_text (path_id → dotted qname, PK-indexed) from the finalized path_seg — the interned
    projection of the append-only path segments. Refreshed at the write_events boundary so every downstream
    join is one index seek, not a full GROUP_CONCAT view materialization per query (see EVENT_SCHEMA note).
    ⚑⚑⚑ RESIDUE-DRIVEN, NOT DELETE-AND-REBUILD (⟡finalize-tail-home, operator 2026-08-22:
    *"We certainly don't want them. That was the whole point behind the ingest->intern->reflect
    ->retire cycle that we finally got down to tiny commits and resumable progress"*).

    This was `DELETE FROM path_text` followed by a full `GROUP BY` reinsert over the WHOLE
    `path_seg` relation — one wide atomic act, called from the PER-CORE converge step. Every
    other boundary in the cycle was moved off that shape; this one was left behind because it
    sat in the `finalize` tail, and the tail's flag hid it.

    ⚑ THE ANTI-JOIN IS SOUND BECAUSE `path_seg` IS APPEND-ONLY AND `path_id` IS THE KEY.
    A new core ADDS paths; it never changes the segments of an existing `path_id`. So a
    materialized row can never go stale ONCE CORRECT, and the work set is exactly the paths
    with no `path_text` row yet — `q_drainable_res`'s discipline applied one tier over: the
    predicate IS the work list, nothing is stored, and a kill loses only the current window.

    ⚑⚑ "ONCE CORRECT" IS DOING REAL WORK IN THAT SENTENCE, AND THE LIVE STORE DOES NOT SATISFY
    IT. MEASURED 2026-08-22 (`schema.py --live --census`): `path_text` 21,932 rows against
    `path_seg` 122,982 — the materialization covers ~18% of its source and has been out of
    date long enough that nothing noticed. An anti-join treats the existing rows as
    AUTHORITATIVE and only appends, so on this store it would make the staleness PERMANENT
    where the DELETE+rebuild was at least self-correcting. The scoping is right; it is not
    safe to switch to until the table has been rebuilt ONCE from current `path_seg`.

    ⚑ SO THE FIRST-RUN REBUILD IS NOT OPTIONAL AND IS NOT AUTOMATED: it is a singleton,
    operator-stated act (`schema.py --flush event --live --apply`, the route ⟡no-automated-drop
    established), after which this predicate is correct forever. Until then the anti-join is
    an APPEND to a partial table, which is honest only because it is now saying so.

    ⚑⚑ AND THE 56 READERS ARE NOT A DEPENDENCY ARGUMENT — I READ THEM AS ONE.
    `--relname path_text` reports 56 relation-use sites in 13 files, and I cited that as
    reason the table must stay. Operator: *"That's 56 readers that are already broken, because
    those readers were never migrated to the new sppf."* The census measures UNMIGRATED DEBT,
    not load-bearing dependency — and 40 of the 56 are in `query_defs.py` /
    `query_sql_postgres.py`, the GENERATED compiled cache, i.e. one source restated. Reading a
    high site-count as importance is the same error as reading a loud row as a lift candidate.

    Idempotent; tolerant of a legacy path_text VIEW."""
    _drop_legacy_view(con, "path_text")
    _schema.apply(con, only="event")  # path_text is declared; no hand-written DDL
    # ⚑ `GROUP_CONCAT` WAS SQLITE-ONLY (postgres: `string_agg`), and the two ALSO DIFFERED
    # IN HOW THEY ORDER THE CONCATENATION — which is the part a function-name swap would
    # get silently wrong. sqlite relied on the SUBQUERY's `ORDER BY` bubbling through the
    # GROUP BY; postgres does not guarantee that at all, and puts the ordering INSIDE the
    # aggregate. A blind rename would have produced dotted qnames with their segments in
    # arbitrary order: wrong DATA, not an error — and every downstream join keys on those
    # strings.
    #
    # ⚑⚑ SO THE `ORDER BY ps.ord` INSIDE THE AGGREGATE IS THE LOAD-BEARING RESIDUE OF THE
    # DELETED ARM, not boilerplate. Dropping the sqlite branch removes the subquery whose
    # `ORDER BY` used to carry the ordering; the only thing keeping segment order correct
    # now is that clause, and it is not enforceable by any test that checks row COUNTS.
    # ⚑ THE ANTI-JOIN IS THE ONLY CHANGE TO THE STATEMENT — the aggregate, the join and the
    # ORDER BY are untouched, deliberately. See the ⚑ above: `ORDER BY ps.ord` INSIDE the
    # aggregate is load-bearing residue of the deleted sqlite arm, and getting it wrong
    # produces wrong DATA rather than an error. A rewrite that touched it while scoping the
    # work set would risk exactly the silent corruption that block was written to prevent.
    n = _schema.execute(
        con,
        "INSERT INTO path_text (path_id, text) "
        "SELECT ps.path_id, string_agg(t.text, '.' ORDER BY ps.ord) "
        "FROM path_seg ps JOIN terms t ON t.term_id = ps.seg_term_id "
        "WHERE NOT EXISTS (SELECT 1 FROM path_text pt WHERE pt.path_id = ps.path_id) "
        "GROUP BY ps.path_id",
    ).rowcount
    con.commit()
    return n


#: ⟡pack-slice-within-level — rows per committed window. A POLICY number, not a measurement: the
#: operator's requirement is fine-grained commits, so this is the grain. Small enough that one
#: window is a short transaction on any core; large enough that a 4.59M-row level is ~180 windows
#: rather than 4.59M. `AGDA_MB`-style autosizing would be a guess where a stated policy belongs.
SLICE_ROWS = 25_000


def _pack_level_sliced(con, core_id, ht, base, slice_rows, sfx):
    """⟡pack-slice-within-level — one level, assigned whole and EMITTED IN COMMITTED WINDOWS.

    Returns `(rows, ids, top)`, the same triple the single-statement form returns.

    ⚑⚑⚑ THE RANKING IS INDIVISIBLE AND THE WRITE IS NOT, WHICH IS THE WHOLE DECOMPOSITION. A
    `dense_rank()` over a SLICE mints different ids for the same signature — MEASURED on
    `wpk3blnvCNA` ht 0, **176,818 observations → 226 signatures** scattered across every
    `local_id`, so a positional slice of the fold splits nearly every signature and reproduces
    `_seed_node_ids`' recorded corruption (*"signature S gets id 3 in run 2 while id 3 already
    denotes a different signature from run 1"*) by slicing rather than by re-running. So stage 1
    assigns the WHOLE level into `_lvl_assign` (ranking intact, one statement), and stage 2 copies
    `[lo,hi)` of that assignment into `obs_node`, committing each window.

    ⚑⚑ THE PARTITION IS UNCHANGED BY CONSTRUCTION, not by testing: the same rank runs over the
    same level, and the windows only move already-decided rows. `--equiv` compares the partition,
    so it cannot distinguish this from the single statement — which is the point, and is also why
    it is not evidence the slicing WORKS. The evidence for that is the commit count.

    ⚑ `ON CONFLICT DO NOTHING` MAKES A RE-RUN OF A PARTLY-EMITTED LEVEL A NO-OP (⟡window-not-
    rejoin's sibling fix), so a kill mid-level loses at most one window and the next run continues
    rather than repeating. That is the property the fine grain exists to buy.
    """
    _asql, _ap = QB.sql("lvl_assign" if sfx else "lvl_assign", core_id=core_id, ht=ht, base=base)
    _schema.execute(con, "DROP TABLE IF EXISTS _lvl_assign")
    _schema.execute(con, "CREATE TEMP TABLE _lvl_assign AS " + _asql, _ap)
    _schema.execute(con, "CREATE INDEX ON _lvl_assign (local_id)")
    con.commit()
    agg = list(
        _schema.rows(
            con,
            "SELECT count(*) AS n, count(DISTINCT node_id) AS ids, "
            "coalesce(max(node_id::bigint), %s) AS top, "
            "coalesce(min(local_id), 0) AS lo, coalesce(max(local_id), -1) AS hi "
            "FROM _lvl_assign" % _schema.ph(),
            (base,),
        )
    )
    if not agg or not agg[0]["n"]:
        return 0, 0, base
    a = agg[0]
    _esql, _ = QB.sql("lvl_emit", lo=0, hi=0)
    lo = a["lo"]
    # ⚑⚑⚑ ⟡slice-ht0-witness — THE COMMIT COUNT IS THE EVIDENCE, AND IT WAS UNOBSERVABLE.
    # This function's own docstring says it above: `--equiv` compares the PARTITION, so it
    # "cannot distinguish this from the single statement — which is the point, and is also why it
    # is not evidence the slicing WORKS. The evidence for that is the commit count." That count
    # was computed and DISCARDED, so the one observable that separates a sliced level from an
    # unsliced one existed nowhere — and a PASS on a core whose level fits in ONE window reads
    # exactly like a PASS on a core that genuinely sliced. Recorded here, surfaced by
    # `--pack-level`, so the witness names its own slice count instead of the reader inferring it
    # from `local_id` arithmetic in the turn.
    windows = 0
    while lo <= a["hi"]:
        # ⚑ ONE WINDOW, ONE TRANSACTION. The window is a `local_id` RANGE rather than a row count
        # because `local_id` is what the assignment is indexed by — a `LIMIT/OFFSET` walk would
        # re-scan the prefix every window, which is the materialise-then-discard shape this arc
        # has removed three times.
        _schema.execute(
            con,
            "INSERT INTO obs_node (core_id, local_id, node_id, ch) "
            + _esql
            + " ON CONFLICT (core_id, local_id) DO NOTHING",
            {"lo": lo, "hi": lo + slice_rows},
        )
        con.commit()
        windows += 1
        lo += slice_rows
    _PackTrace.windows[ht] = windows
    return a["n"], a["ids"], int(a["top"])


def build_ht_map(con, core_id, recursive=False):
    """⟡converge-not-recurse — `_ht_map` for ONE core, by CONVERGING PASSES. Returns rounds.

    ⚑⚑⚑ MULTIPLE PASSES THAT CONVERGE, NOT ONE PASS THAT RECURSES (operator, 2026-08-22: *"Do we
    even need the CTE recursion at this point? Because we can do things in multiple passes and
    converge, rather than recurse (which forces a single pass)."*). Seed the leaves, then
    repeatedly insert parents whose children are ALL already placed, until a round inserts
    nothing. The fixpoint IS the termination proof: `done` is monotone and bounded by the node
    count, so no depth parameter, no round ceiling, and no cycle guard.

    ⚑⚑ WHAT THE RECURSIVE FORM COST, MEASURED: `q_obs_height` emitted **490,023 rows for 313,830
    observations** (1.56×), collapsed by an outer `max(ht)` that spilled — `HashAggregate
    Batches: 5  Disk Usage: 15200kB  Rows Removed by Filter: 137012`. A recursive term must fire
    on EACH CHILD as that child arrives, so a parent with children at heights 0 and 3 is emitted
    at ht 1 AND ht 4. The readiness anti-join emits each node EXACTLY ONCE, with its height final
    on arrival — so the outer aggregate disappears rather than being made cheaper.
    ⚑ `max_parents = 1` (re-verified over 138,351,403 edges) does NOT prevent this: it bounds
    parents per CHILD, and the amplification comes from children per PARENT.

    ⚑ THE `max` INSIDE THE RUNG IS A DIFFERENT AGGREGATE and is the definition of height:
    `1 + max(child ht)` over one parent's own children, a handful of rows. The one retired
    aggregated duplicate emissions of the SAME node across passes.

    ⚑⚑ ONE COMMIT PER ROUND, WHICH IS THE POINT AND NOT TIDINESS. `sppf_tree.run_rounds` records
    why: *"the next statement resolves its children by an ordinary PK lookup against a FRESH
    snapshot; if the previous had not committed, it would see its own transaction's rows only
    through the same snapshot."* A converging build is resumable at round granularity; a
    recursive one is a single statement that either completes or is lost.

    ⚑ `recursive=True` KEEPS THE OLD SPELLING REACHABLE as the reference arm — `--compare-paths`
    diffs the two per level, so the rewrite's correctness is MEASURED rather than argued. A
    replacement with no comparison arm is what this file's `--equiv` machinery exists to refuse.
    """
    _schema.execute(con, "DROP TABLE IF EXISTS _ht_map")
    if recursive:
        _hsql, _hp = QB.sql("obs_height", core_id=core_id)
        _schema.execute(con, "CREATE TEMP TABLE _ht_map AS " + _hsql, _hp)
        _schema.execute(con, "CREATE INDEX ON _ht_map (ht)")
        _schema.execute(con, "ANALYZE _ht_map")
        return 1
    _ssql, _sp = QB.sql("ht_seed", core_id=core_id)
    _schema.execute(con, "CREATE TEMP TABLE _ht_map AS " + _ssql, _sp)
    # ⚑ THE INDEX BEFORE THE LOOP, NOT AFTER — every round's readiness anti-join probes this map
    # by `(core_id, local_id)`, so an unindexed map makes each round a seq scan over what the
    # previous rounds wrote. The `ht` index the recursive form built served the LEVEL loop; this
    # one serves the CONVERGENCE, and both are wanted.
    _schema.execute(con, "CREATE INDEX ON _ht_map (core_id, local_id)")
    _schema.execute(con, "CREATE INDEX ON _ht_map (ht)")
    _tsql, _tp = QB.sql("ht_step", core_id=core_id)
    rounds = 1
    while True:
        # ⚑ PROGRESS IS `rowcount` — the rows this round PLACED. Monotone by construction (the
        # anti-join refuses anything already in the map), so it is simultaneously the stall
        # detector and the termination proof. ladder-fixpoint's recorded correction: a guard on
        # `todo` fires on a HEALTHY fixpoint because `todo` is a scalar over two opposing flows.
        # ⚑ `.rowcount` OFF THE CURSOR — `_schema.execute` RETURNS THE CURSOR, NOT A COUNT, and a
        # cursor is always truthy. Written first as `if not n: break`, which would never fire:
        # an infinite loop appending nothing, forever. Caught by reading the helper rather than
        # by running it, which is the only reason it is a comment and not an incident.
        n = _schema.execute(con, "INSERT INTO _ht_map " + _tsql, _tp).rowcount
        con.commit()
        rounds += 1
        if not n:
            break
    _schema.execute(con, "ANALYZE _ht_map")
    return rounds


def promote_core_a3(con, core_id):
    """⟡a3-route-pack-only — the A3 promote for ONE core: pack server-side, then stage 3.

    ⚑⚑⚑ WHY THIS EXISTS, MEASURED 2026-08-22. `--promote-core` ran A2 (`project_sppf`), and
    under `make -j 20 promote` that DEADLOCKED: two workers each issuing
    `DELETE FROM obs_node WHERE core_id=$1`, both waiting on `RowExclusiveLock` on the same
    relation. Per-core scoping does not prevent it — the delete's lock is at relation
    granularity. A3 has NO delete (`q_pack_level_insert` is a pure `INSERT … RETURNING`), so
    the deadlocking statement does not exist on this path.

    ⚑⚑ AND IT FIXES THE OTHER HALF AT THE SAME TIME. A2 reads corpus-wide at three sites —
    `event_head` (25.4M rows), `event_ctor`, `unit_obs` — per core, so 20 workers each dragged
    the whole `event` relation across the wire. `--scans q_pack_level_insert` reports every
    access as an **Index Scan**, all `WHERE core_id`. Measured on the live path before this:
    181k observations took ~40 minutes, essentially all of it reading.

    ⚑ THE ALLOCATOR IS WHAT MAKES CONCURRENCY LEGAL, and it is not new here. `_claim_node_ids`
    mints from a NON-TRANSACTIONAL sequence: `nextval` never returns the same value twice, even
    across concurrent and rolled-back transactions. `converge` already promotes this way
    (`:2292`); this routes the make-driven mode onto the same path rather than inventing one.
    *"The counter was the only shared mutable state, which is why fixing it is the whole of the
    parallelisation."*

    ⚑⚑ STAGE 3 IS NOT OPTIONAL AND A3 DOES NOT DO IT. `pack_core_sql` packs and stops; `_unit`
    / `_unit_cod` / `unit_node` — the definition-level index `reuse_check` and the reuse index
    consume — were built inline in A2. Routing to A3 alone would have silently stopped three
    relations growing, with no error and no failing gate. `build_units` is that stage, extracted
    so both routes call one implementation.

    ⚑ `pack` IS A QUERY HERE, NOT A DICT. A3 has already written `(core,local) → node_id` to
    `obs_node`, so stage 3 reads it back rather than holding it — the recover-don't-store
    discipline `_seed_node_ids` applies to signatures, extended to the packing.
    """
    _n = (
        _schema.scalar(con, "SELECT count(*) FROM obs WHERE core_id=%s" % _schema.ph(), (core_id,))
        or 0
    )
    if not _n:
        return (0, 0, 0, 0)
    # ⚑⚑⚑ THE RESIDUE PREDICATE IS WHAT MAKES A3 IDEMPOTENT — NOT A DELETE. Measured 2026-08-22:
    # re-running this on an already-packed core raised
    # `UniqueViolation: ix_obsnode_pk (core_id, local_id)=(LRRu2kXZAsU, 1951) already exists`.
    # A3's `q_pack_level_insert` is a bare `INSERT … RETURNING` with no `ON CONFLICT`, by design
    # — the `DELETE FROM obs_node WHERE core_id=$1` that made A2 re-runnable is the SAME
    # statement that deadlocked two `make -j` workers on a relation-wide RowExclusiveLock. So
    # re-adding a delete here would import the defect this route exists to escape.
    #
    # ⚑⚑ `converge` NEVER HIT THIS because it draws work from `unprojected_cores_shard` — it
    # only ever promotes a core that has NO `obs_node` rows, so the delete was never needed and
    # its absence was never a gap. The make-driven mode has no such enumerator: `make` re-runs a
    # recipe whenever the `.ingested` stamp is newer, which is exactly a re-promote.
    #
    # ⚑ NO CORE-GRAIN GUARD HERE, AND REMOVING IT WAS THE POINT. A first fix short-circuited when
    # the core had ANY `obs_node` rows — which cured the UniqueViolation and BROKE RESUMPTION: a
    # core whose pack was killed at level 40 of 70 has rows, so the guard would call it done and
    # stamp it. `ON CONFLICT DO NOTHING` now makes idempotence a property of the WRITE at level
    # grain, which is strictly finer and needs no predicate at the caller. A fully-packed core
    # simply inserts nothing on every level and reports zero.
    _seed_hi = _claim_node_ids(con, _n)
    _lv, _rows, _ids, _top = pack_core_sql(con, core_id, base=_seed_hi, write=True)
    con.commit()  # ⚑ THE CORE IS THE ATOMIC UNIT — a kill rolls back one core.

    # ⚑ THE THREE STAGE-3 INPUTS, ALL CORE-SCOPED. `ch` from `edge_core`; `pack` from the
    # `obs_node` rows the fold just committed; `cod` needs the per-core head map, which
    # `event_head_core` provides under a `WHERE core_id` semi-join.
    _packing = {
        (c, l): n
        for c, l, n in _schema.rows(
            con,
            "SELECT core_id, local_id, node_id FROM obs_node WHERE core_id = %s" % _schema.ph(),
            (core_id,),
        )
    }
    _ch = defaultdict(list)
    for c, p, o, cl in QB.run(con, "edge_core", core_id=core_id):
        _ch[(c, p)].append((o, cl))
    _obs = {(c, l): e for c, l, e in QB.run(con, "obs_core", core_id=core_id)}
    # ⚑ THE SLOT ORDER IS A2's, NOT INVENTED: `head[ekey] = (kind, role, ctor, qname, lit)`
    # (`project_sppf:1215`), and `cod` reads `[2]` for the ctor and `[3]` for the qname. Only
    # those two slots are consulted here, but the tuple keeps its shape so the two `cod` bodies
    # stay comparable — a reordered tuple would make the twin silently read the wrong field.
    _head = {
        ekey: (
            "AgdaCore",
            ("db%d" % idx) if idx is not None else "",
            ctor or "",
            qname or "",
            litval or "",
        )
        for ekey, ctor, qname, idx, litval in QB.run(con, "event_head_core", core_id=core_id)
    }
    _raw_ctor = {e: ct for e, ct in QB.run(con, "event_ctor_core", core_id=core_id)}

    def _cod(c, root_lid):
        cur = root_lid

        def opof(lid):
            e = _obs.get((c, lid))
            return _head[e][2] if e and e in _head else None

        if opof(cur) == "Defn":
            kd = sorted(_ch.get((c, cur), []))
            if kd:
                cur = kd[0][1]
        s = 0
        while opof(cur) == "Pi" and _ch.get((c, cur)) and s < 4096:
            cur = sorted(_ch.get((c, cur)))[-1][1]
            s += 1
        e = _obs.get((c, cur))
        if e is None or e not in _head:
            return (None, None)
        return (_raw_ctor.get(e), _head[e][3] or None)

    build_units(con, core_id, lambda c, l: _packing.get((c, l)), _cod, _ch, additive=True)
    return (_lv, _rows, _ids, _top)


def build_units(con, core_id, pack, cod, ch, additive=True):
    """Stage 3 of the promote — `_unit` / `_unit_cod` / `unit_node` for ONE core.

    ⚑⚑⚑ ⟡a3-route-pack-only — EXTRACTED SO THE A3 PATH CAN CALL IT. `pack_core_sql` (A3) does
    the PACK and nothing else; this stage lived inline in `project_sppf` (A2) and was therefore
    reachable only by taking A2's corpus-wide reads with it. Routing `--promote-core` to A3
    without this would have silently stopped three relations growing — no error, no failing
    gate, just a definition-level index that stops tracking new cores. MEASURED before the cut:
    A2's run moved `_unit` 74 → 5,011 and `unit_node` 35,467 → 1,980,763, so the tier is live
    and consumed (`reuse_check`, the reuse index), not vestigial.

    ⚑⚑ `pack` IS A CALLABLE, NOT A DICT, AND THAT IS THE WHOLE POINT OF THE EXTRACTION. A2 holds
    `(core,local) → node_id` in memory and passes `packing.get`; A3 has already WRITTEN that
    mapping to `obs_node`, so it passes a lookup that QUERIES it. Same stage, two providers —
    the recover-don't-store discipline `_seed_node_ids` already applies to signatures, extended
    to the packing. A `dict` parameter would have forced A3 to materialise what it deliberately
    left in the store.

    ⚑ THE `unit_node` DELETE IS SCOPED THROUGH `_unit.file_id`, unchanged from the inline form:
    `unit_node` is a membership SET with no core column, so an additive re-projection of a core
    whose membership SHRANK would leave the dropped pairs behind (`upsert` can only add).
    `_node`/`node_child` are deliberately NOT cleared — they are content-addressed and
    accumulating there IS the promote.
    """
    # ⚑ THE interner, from the one factory — NOT a local `_b64` copy. `_mk_interners` writes the
    # `terms`/`path_text` rows as it mints ids, which is why two bare copies were retired for it.
    tid, pid = _mk_interners(con)
    urows, un_rows, codrows = [], [], []
    _here = [core_id] if core_id is not None else []
    # ⚑ SCOPED READ, and `unit_obs` HAS a `core_id` column — the starkest of A2's three unscoped
    # reads. The two `event` ones at least had a reason (content-addressed, no such column, so
    # the scope must come by semi-join through `obs`); this one had none. A per-core fold read
    # every unit header in the store to keep the handful belonging to its own core, and
    # `pack(c, root_lid)` discarded the rest one row at a time via `if rootpk is None: continue`
    # — filtering in python what the WHERE filters in the engine.
    #
    # ⚑⚑ AND `_schema.rows`, NOT `con.execute`, WHICH ONCE SILENTLY EMPTIED THIS TIER. psycopg's
    # `dict_row` makes each row a dict, and iterating a dict yields its KEYS — so this 8-way
    # unpack bound `c='core_id'`, `root_lid='root_lid'`, and `pack(...)` returned None for all
    # 419 rows, hitting `continue` every time. MEASURED: 1906 nodes and 7920 child edges
    # projected correctly while `_unit` and `unit_node` stayed at 0 — a projection half-built
    # with no error anywhere. Third site of one defect: `schema.rows` normalised it for new
    # code, `query_builders._rows_of` for every NAMED query, and this raw call sat between them
    # reached by neither. **Fixing a contract does not fix the code written before it.**
    _uwhere = " WHERE core_id = " + _schema.ph() if core_id is not None else ""
    for c, unit_id, name_pid, root_lid, kind_id, module_pid, copy, level in _schema.rows(
        con,
        "SELECT core_id, unit_id, name_pid, root_lid, kind_id, module_pid, "
        "copy, level FROM unit_obs" + _uwhere,
        (core_id,) if core_id is not None else (),
    ):
        rootpk = pack(c, root_lid)
        if rootpk is None:
            continue
        urows.append((unit_id, name_pid, rootpk, c, kind_id, module_pid, root_lid, copy, level))
        cct, cqn = cod(c, root_lid)
        codrows.append(
            (
                unit_id,
                (tid(cct) if cct is not None else None),
                (pid(cqn) if cqn is not None else None),
            )
        )
        seen, stack, members = set(), [root_lid], set()
        while stack:
            lid = stack.pop()
            if lid in seen:
                continue
            seen.add(lid)
            pk = pack(c, lid)
            if pk is not None:
                members.add(pk)
            stack.extend(cl for _, cl in ch.get((c, lid), []))
        un_rows += [(unit_id, pk) for pk in members]
    if additive and _here:
        _schema.execute_many(
            con,
            "DELETE FROM unit_node WHERE unit_id IN "
            "(SELECT unit_id FROM _unit WHERE file_id=%s)" % _schema.ph(),
            [(c,) for c in _here],
        )
    _schema.upsert(con, "_unit", urows)
    _schema.upsert(con, "_unit_cod", codrows)
    _schema.upsert(con, "unit_node", un_rows)
    con.commit()
    return len(urows), len(un_rows)


def pack_core_sql(con, core_id, base=0, write=False, materialised=True, slice_rows=SLICE_ROWS):
    """Run the packing fold for ONE core, level by level, entirely server-side.

    Returns `(levels, rows, ids, top)` — rounds executed, observations packed, distinct node ids
    minted, and the highest id issued (the next caller's `base`).

    ⚑⚑⚑ THIS IS THE STAGED FORM OF `project_sppf`'s PYTHON PACKING LOOP (`:850-861`), and the
    staging is FORCED: postgres bars aggregates, `GROUP BY`, `DISTINCT` and window functions from
    a recursive term, while the fold needs `array_agg` (children), `GROUP BY` (dedup) and
    `dense_rank()` (id assignment) at once. So it is not one `WITH RECURSIVE` — it is one
    set-based statement per height, ascending, which is legal because levels are disjoint and a
    node's children are strictly below it.

    ⚑⚑ ASCENDING ORDER IS THE CORRECTNESS ARGUMENT, not a convenience. `q_pack_level` reads its
    children's ids from `obs_node`, so every child must be numbered before its parent is grouped.
    Height gives exactly that ordering — and `sppf_db`'s own measurement (`:827-831`) records the
    same property one layer down: `clid < plid` on 177,370/177,370 edges, i.e. `local_id` is
    post-order, which is why the python loop can be iterative rather than recursive.
    ⚑ CORPUS-VERIFIED AT FULL SCALE: `query_defs --rows edge_postorder` reports
    `total = 130,915,197 · post_order = 130,915,197 · max_parents = 1` — 100.000%, and a forest.

    ⚑⚑⚑ ⟡locals-are-emission-order — WHY POST-ORDER HOLDS, WHICH THIS FILE RECORDED ONLY AS A
    MEASUREMENT AND NOT AS A CAUSE. `local_id` is the shim's PRINT COUNTER: `agdai_shim.hs`
    mints it with `fresh :: IORef Int -> IO Int` (a monotonic `atomicModifyIORef'`) and its
    `emit` carries the comment *"children already emitted (post-order)"*. So `clid < plid` is
    not an empirical regularity the fold is lucky to find — it is the walk order, by
    construction, and it would hold on any corpus this shim emits.

    ⚑⚑ AND THE COROLLARY MATTERS MORE THAN THE PROPERTY: **a core-local id represents NOTHING IN
    AGDA.** It is not a de Bruijn index, not a name, not a telescope position — it is "the Nth
    node this walker happened to print, on this file, in this run". Its entire semantic content
    is the ordering that falls out of post-order. Two cores holding an IDENTICAL subterm number
    it differently purely because the walk reached it at a different point, and that is the
    noise the interner exists to see through — the 57× collapse (`event` 25.4M → `_node` 443k)
    is shared structure the emission counter OBSCURED, being recovered.

    ⚑ THIS CORRECTS A CIRCULAR ARGUMENT MADE AGAINST CANONICAL IDS (2026-08-22). I claimed
    `obs_node.ch` "must stay core-local" because `q_drainable_res` conjunct (5) `EXCEPT`s it
    against `edge.clid`, which is core-local. True of the CURRENT schema and circular as a
    constraint: `edge` holds locals only because the shim emitted them, so "the licence compares
    in local space" is a fact about what we chose to store, not about the terms. Nothing
    semantic is lost by replacing locals with canonical ids — there was nothing semantic there.

    ⚑ WHAT IS *NOT* SETTLED BY THIS, and must be before anything acts on it: `(core_id,
    local_id)` addresses an OCCURRENCE, and one core can contain the same subterm twice. Those
    are two occurrences, two locals, one canonical id — so collapsing locals to canonical ids
    MERGES them, which is exactly the hazard `Reflection.agda` records (*"one module applied
    twice collapses to a single node and the two applications become indistinguishable"*).
    Emission order being meaningless does not make the occurrence address meaningless.

    ⚑⚑ AND THE SUBSTRATE ALREADY FORMALIZES THAT SPLIT — `Lifecycle.Fragment.Occurrence`
    models `local : ℕ` as *"the occurrence's position"* against `node : Id`, *"the class it
    collapsed into"*, with `Residue = List Occurrence` a MULTISET because `obs_node` declares
    no primary key. Its ⚑ states the rule directly: *"the node ids are post-quotient (shared),
    the local ids are pre-quotient (per-occurrence)"*. So occurrence-vs-identity is not an open
    modelling question on our side; it is decided, and `ch`'s local ids are the residue `r` in
    `a = recon q b r`.

    ⚑ THE ACTUALLY-OPEN QUESTION IS NARROWER AND IS ABOUT AGDA, NOT ABOUT US: is
    `(constructor, children)` the RIGHT identity for an elaborated core term, or does Agda
    distinguish terms this key merges — via ranges, modality/quantity/relevance, de Bruijn
    scoping context, or `defCopy` provenance? That cannot be answered by measuring our store,
    because our store has the quotient already baked in: measuring it reports what the key
    DOES, never whether the key is correct. Routed to linux-sources against Agda 2.8.0's
    sources (⟡occurrence-vs-identity). Any discriminator they find belongs in `NodeSig`, NOT
    in the occurrence residue.

    ⚑ `base` THREADS THE SURROGATE COUNTER ACROSS LEVELS — `:base + dense_rank()` per level, with
    `base` advanced by the ids that level minted. That reproduces python's `_next += 1` exactly,
    and on the additive path the initial `base` is `_seed_node_ids`' `_top + 1`
    (`:840-848`: *"the counter is seeded from the store, not from len(node_ids)"* — an unseeded
    re-run points a new core's observation at a DIFFERENT signature's id, silent corruption).

    ⚑ `write=False` IS THE DEFAULT AND THE MODE USES IT. A fold that writes before it has been
    compared is one whose disagreement with the python is undiscoverable; `--equiv pack.sql
    pack.python` is the gate, and `q_pack_discrimination` reports whether that gate could even
    have failed at the level it ran on.
    """
    # ⚑⚑⚑ NOTHING PROPORTIONAL TO CORE SIZE CROSSES THE WIRE. Every line of this loop used to.
    # Measured on the live tail core (`--height`, read-only, before any write): **943,927
    # observations, 70 distinct heights, largest level 529,003 rows.** The three defects:
    #
    #   was `sorted({r[2] for r in QB.run(con, "obs_height", …)})`
    #     → 943,927 rows pulled to derive 70 integers. A 13,000:1 materialisation for a loop
    #       bound. Now `obs_heights_distinct`, which returns the 70.
    #   was `got = list(QB.run(...))` … `{r[2] for r in got}` … `max(int(n) for n in _here)`
    #     → up to 529,003 rows materialised in python to compute THREE NUMBERS. Now the
    #       statement aggregates: `q_pack_level_insert` wraps its `INSERT … RETURNING` in a
    #       data-modifying CTE and returns `(n, ids, top)`; `q_pack_level_summary` is the
    #       read-path twin with the same shape.
    #
    # ⚑⚑ ALL THREE WERE INVISIBLE AT THE SCALE THEY WERE BUILT AT. The four verified cores are
    # 7k–55k, where these move tens of thousands of rows and cost nothing anyone would notice;
    # the tail is 17× larger and they scale with it while the ANSWERS do not. This is why the
    # plan measured the tail before writing to it rather than after.
    #
    # ⚑ AND IT IS THE ARC'S OWN DEFECT ONE LAYER UP: the row-at-a-time INSERT that started all
    # of this was work done client-side that the server was already positioned to do. Distinct-ing
    # in python, and counting in python, are the same shape.
    # ⚑⚑⚑ THE DESTINATION IS A DECLARED TIER, SO THIS ESTABLISHES IT RATHER THAN ASSUMING IT.
    # `obs_node` is `OBSNODE_TABLES` in `_TIERS` (`schema_decl.py:1484,1531`) and every table
    # compiles `CREATE TABLE … IF NOT EXISTS` (`schema_decl.py:1416`), so `apply(only="obsnode")`
    # is a no-op when present and the correct DDL when absent. There is no state to check.
    #
    # ⚑⚑ I HAD THIS AS A QUESTION TO ANSWER — "does obs_node exist on the live tenant?" — and it
    # is not one (operator, 2026-08-15: *"Why is this even a question? How is it that our schema
    # isn't a derived or declared prerequisite somewhere?"*). It IS declared; treating its
    # presence as an ambient condition to inspect is what turns a prerequisite into a precondition
    # the caller must remember. `project_sppf` already does exactly this at :983/:989 — this
    # function was relying on having been called after it.
    #
    # ⚑ AND IT IS WHY THE LIVE TENANT HAS NO `obs_node`: `schema_decl.py:1482-1484` keeps it out
    # of the default `sppf` tier deliberately — *"derived, disposable, and not created by a
    # default ingest that would never populate it"* — so the table appears exactly when something
    # is about to fill it. That is the correct design, and this line is its other half.
    #
    # ⚑⚑⚑ ⟡assert-dont-establish — AND THE OTHER HALF IS AN ASSERTION, NOT A CREATION (operator,
    # 2026-08-22: *"Per-core operations should BAIL if the required indexes are not already
    # present."*). This was `_schema.apply(con, only="obsnode")`, defended by the paragraph
    # above as costless: *"apply is a no-op when present and the correct DDL when absent. There
    # is no state to check."* TRUE OF ONE PROCESS, FALSE OF EIGHT — `CREATE … IF NOT EXISTS`
    # takes the relation lock BEFORE it can discover the object exists.
    #
    # ⚑⚑ MEASURED under `make -j 8 promote`: five workers stacked on `Lock: relation` against
    # `CREATE UNIQUE INDEX IF NOT EXISTS ix_obsnode_pk`, and pairs deadlocked outright. I had
    # blamed A2's `DELETE FROM obs_node`; removing the delete did not fix it, because the delete
    # was never the holder — this line was. SECOND SITE of a shape `declared_indexes` had
    # already diagnosed for `ingest_core`/`ix_terms_text` (13 backends, 11 queued on one
    # statement) and recorded the rule for, with only a CLI report behind it.
    #
    # ⚑ SO ESTABLISHING THE TIER IS A BUILD-TIME ACT, ONCE, and this per-core path asserts.
    # See `.claude/skills/sql-relalg/SKILL.md` fact 5 (⟡assert-dont-establish) for the pattern
    # and why it recurs: nothing in a signature says whether a function runs once or per-item,
    # so "establish on entry" reads as defensive good practice at every site.
    _schema.require_indexes(con, "obsnode", label="pack_core_sql")
    # ⚑⚑⚑ THE HEIGHT MAP IS COMPUTED ONCE PER CORE, NOT ONCE PER LEVEL — measured 2026-08-17 with
    # `--explain pack_level_summary` on the 6,210-row trial core:
    #
    #     Execution Time: 1000.5ms   of which  CTE h: 847ms (85%)
    #     the recursion produced 57,368 rows to answer about a level of 50
    #     Rows Removed by Filter: 6,160   — every observation's height computed, then discarded
    #
    # **The packing itself is ~30ms.** `q_pack_level` embeds `q_obs_height` as a subquery, so each
    # level's statement rebuilds the WHOLE height map and throws away every row but its own —
    # 23 times for this core, 70 times for the 943,927-row tail. That is 97% overhead on the one
    # loop ⑤c runs 152 times.
    #
    # ⚑⚑ A TEMP TABLE, NOT A CHANGE TO THE BUILDER. `q_obs_height`'s scoping and its `UNION ALL`
    # are load-bearing and measured (its own ⚑s record that the unbounded form does not complete
    # in 300s, and that restating `core_id` in the recursive term is what stops the planner sizing
    # for the corpus). The defect is not the CTE — it is EVALUATING IT PER LEVEL. So the fix
    # materialises the same builder's output once and lets the levels read it.
    #
    # ⚑ TEMP, SO IT CANNOT OUTLIVE THE CONNECTION OR COLLIDE ACROSS CORES. `ON COMMIT DROP` would
    # be wrong here: `pack_core_sql` does not commit (`--refold` and `_do_promote` own that), and
    # a map dropped at the first commit would silently vanish mid-fold. Dropped explicitly at
    # entry instead, so a second core in one connection cannot read the previous core's heights —
    # the wrong-population failure this arc has now paid for twice.
    # ⚑ BUILT ONLY FOR THE PATH THAT READS IT. The CTE spelling derives height inline, so
    # materialising a map it never touches would make the comparison measure the SAME work twice
    # and report the optimisation as free.
    # ⚑⚑⚑ JIT OFF FOR THIS FOLD, ON THE HOST OWNER'S READING (cassian-observability, 2026-08-17).
    # MEASURED on the tail core: **4.8s of a 32.5s statement is JIT** — 2.87s inlining, 1.49s
    # optimization — and the plan is byte-identical every time, 152 cores × N levels. JIT exists to
    # amortise compilation over a long-running plan; here it recompiles the same plan hundreds of
    # times and amortises nothing. Their verdict: *"pure waste … clean win, no downside for a
    # repeated-identical-plan batch."*
    #
    # ⚑⚑ SESSION-SCOPED, NOT A SERVER SETTING. `SET LOCAL` would die at the next commit and this
    # function deliberately does not commit; a postgresql.conf change would impose one workload's
    # tradeoff on every other tenant of a shared store. `SET` binds this connection for its life,
    # which is exactly the fold's unit.
    #
    # ⚑ AND IT IS THE ONLY KNOB THIS ARC TOUCHES. `work_mem` stays at 64MB and `shared_buffers` at
    # 256MB — both refused on measurement, not taste: `shared_buffers` is a DELIBERATE co-tenancy
    # guardrail (pg under `MemoryMax=2G`, sized so it cannot balloon into the operator's desktop),
    # and `work_mem` MULTIPLIES per-node-per-backend, so raising it under sharding would push
    # ~2GB+ of anon into a 3.2GiB headroom shared with that desktop. The 47%-of-statement spent in
    # `shared_read` is the intended cost of that guardrail, not a misconfiguration to fix.
    _schema.execute(con, "SET jit = off")
    if materialised:
        build_ht_map(con, core_id)
    levels = rows = ids = 0
    top = base
    # ⚑ THE `_mat` ENTRIES READ THE MAP THIS FUNCTION JUST BUILT. They are the same fold — one
    # body, decomposed at `q_height_src`, the only stage that varies — so the statement's SHAPE is
    # unchanged and ⑤a/⑤b's IDENTICAL verdicts still describe it. What changes is that the 70-level
    # recursion happens ONCE above instead of inside every level's plan.
    # ⚑⚑ `_mat` IS THE DEFAULT AND THE CTE SPELLING IS REACHABLE — that is what makes the two
    # paths COMPARABLE rather than one of them merely believed. `materialised=False` drives the
    # identical loop through the recursive-CTE entries, so `--compare-paths` can run both over one
    # core and diff their per-level `(n, ids, top)`. Without this parameter the optimised path's
    # correctness rested on a structural argument (one body, one varying stage) with no
    # measurement available, which is the shape this repo refuses everywhere else.
    _sfx = "_mat" if materialised else ""
    per_level = []
    for r in QB.run(con, "obs_heights_distinct" + _sfx, core_id=core_id):
        # ⚑ ONE EXECUTION PER LEVEL, WHICHEVER MODE — an earlier cut ran the SELECT to count and
        # THEN the INSERT to write, computing every level twice. Both spellings now return
        # `(n, ids, top)`, so the caller does not branch on which one it used.
        if write and slice_rows:
            _n, _ids, _top = _pack_level_sliced(con, core_id, r[0], top, slice_rows, _sfx)
        else:
            got = list(
                QB.run(
                    con,
                    ("pack_level_insert" if write else "pack_level_summary") + _sfx,
                    core_id=core_id,
                    ht=r[0],
                    base=top,
                )
            )
            if not got or not got[0][0]:
                continue
            _n, _ids, _top = got[0][0], got[0][1], got[0][2]
        if not _n:
            continue
        per_level.append((r[0], _n, _ids, _top))
        levels += 1
        rows += _n
        ids += _ids
        top = max(top, _top)
        # ⚑⚑⚑ ⟡pack-level-commit — COMMIT PER LEVEL, AND THE ALTERNATIVE IS A BIG LOCK. This loop
        # held ONE transaction across every level of the core and let the caller commit at the
        # end (operator, 2026-08-22: *"I don't even want 'caller commits at the end'. That
        # replaces a lockless paradigm with a BKL paradigm."*). Correct, and it is the whole
        # cause of the deadlock: a transaction spanning ~70 levels accumulates lock footprint
        # monotonically, holds every level's writes invisible until the end, and lets two
        # `make -j` workers reach a wait cycle.
        #
        # ⚑⚑ WHAT MAKES THE EARLY COMMIT SAFE IS THE RESIDUE PREDICATE, NOT AN UNDO. A committed
        # PREFIX of levels is a READABLE, RESUMABLE state: `obs_node` holds the levels that
        # landed, `q_pack_level` reads its children's ids from there, and heights ascend — so a
        # kill mid-core leaves a partial pack that the next run continues rather than repeats.
        # `ON CONFLICT (core_id, local_id) DO NOTHING` makes a re-run of a partly-landed level a
        # no-op, which is the property the builder's docstring already claimed and the code did
        # not have until today. Rollback was buying an undo the predicate makes unnecessary.
        #
        # ⚑ THE `base` COUNTER SURVIVES A KILL because it is NOT derived from this transaction:
        # `_claim_node_ids` mints from a non-transactional sequence, so ids already handed out
        # are never re-issued even by a rolled-back attempt. Gaps are by design.
        if write:
            con.commit()
    # ⚑ THE PER-LEVEL TRACE IS RETURNED VIA AN ATTRIBUTE, NOT A FIFTH TUPLE SLOT. Nine call sites
    # unpack this as four values; widening the tuple would break every one at once — the
    # positional-read defect `module_size_all` records for exactly this reason (*"appending is the
    # only widening that cannot shift a consumer"*), and here even appending would break the
    # `_lv, _rows, _ids, _top = …` unpackings.
    out = (levels, rows, ids, top)
    _PackTrace.last = per_level
    return out


class _PackTrace:
    """The last fold's per-level `(ht, n, ids, top)` — for `--compare-paths`, not for callers.

    ⚑ A CLASS ATTRIBUTE BECAUSE THE TRACE IS A DIAGNOSTIC, NOT A RESULT. Threading it through
    `pack_core_sql`'s return would make every consumer carry a value only one comparison mode
    reads; making it a module global would let two concurrent folds overwrite each other's.
    Scoped here, named, and documented as the diagnostic it is.
    """

    last = []

    #: ⟡slice-ht0-witness — `ht → committed windows` for the last SLICED fold. Separate from
    #: `last` because it is populated by a DIFFERENT path: `last` is filled on every fold, this
    #: only by `_pack_level_sliced`, so an EMPTY dict beside a non-empty `last` is the readable
    #: fact "that fold did not slice" — which is precisely the distinction a partition-equivalence
    #: cannot make. Merging them into one structure would spend that distinction to save a name.
    windows = {}


def _claim_node_ids(con, n):
    """Claim a DISJOINT block of `n` surrogate node ids; return the base to fold from.

    ⚑⚑⚑ THE ONE PIECE OF SHARED MUTABLE STATE IN AN OTHERWISE PER-CORE FOLD. Everything else
    shards on `core_id` by construction — heights are per-core (`max_parents=1` measured
    corpus-wide, a forest of trees), `q_unprojected_cores` enumerates the shards, `_do_promote`
    commits one core, and every work predicate is a residue READ. Only the id counter is written
    by all of them, and it was READ (`max(node_id)`) rather than allocated: two concurrent
    promoters see the same top and mint the same ids for different signatures.

    ⚑⚑ NON-TRANSACTIONAL BY DESIGN, WHICH IS THE PROPERTY BEING BOUGHT. `nextval` never returns a
    value twice — not across concurrent transactions, and not when one rolls back. Gaps are
    therefore expected and HARMLESS: the id is a SURROGATE over the signature, so nothing reads it
    as a count or a position (`q_pack_partition`'s whole argument is that the two folds agree on
    the PARTITION and disagree on every id). A rolled-back core simply leaves its block unused.

    ⚑ SEEDED PAST THE EXISTING HIGH-WATER MARK, ONCE. `_node` already holds ids minted by earlier
    python folds; starting the sequence at 1 would re-issue them and point new observations at
    old signatures — the exact corruption this function exists to prevent, reintroduced at
    creation time. `setval` runs only when the sequence is created.

    ⚑ `n` IS THE CORE'S OBSERVATION COUNT, WHICH OVER-CLAIMS. The fold mints at most one id per
    observation and usually far fewer (sharing collapses 6,210 observations to 295 ids), so the
    block is an upper bound rather than a fit. Over-claiming is the safe direction: a block too
    SMALL would overlap the next claimant, while a block too large costs only sequence range,
    of which int8 has more than this corpus can consume.
    """
    _p = _schema.ph()
    _schema.execute(con, "CREATE SEQUENCE IF NOT EXISTS node_id_alloc AS bigint")
    # ⚑ THE SEED IS A `max(sequence_last, store_top)`, not an unconditional setval — re-running it
    # per claim would REWIND the allocator under a concurrent worker that had already advanced it.
    _top = list(QB.run(con, "node_id_top"))[0][0] or 0
    _schema.execute(
        con,
        "SELECT setval('node_id_alloc', GREATEST(%s, last_value), true) "
        "FROM node_id_alloc WHERE last_value < %s" % (_p, _p),
        (_top, _top),
    )
    got = _schema.scalar(
        con,
        "SELECT nextval('node_id_alloc') FROM generate_series(1, %s) ORDER BY 1 DESC LIMIT 1" % _p,
        (max(int(n), 1),),
    )
    # the block is (base, base+n]; the fold adds `dense_rank()` to `base`
    return int(got) - max(int(n), 1)


def _seed_node_ids(con):
    """The signature → node_id map the durable tier ALREADY HOLDS, plus the highest id issued.

    ⚑⚑ THIS IS WHAT MAKES AN ADDITIVE PROMOTE POSSIBLE AT ALL, and its absence was the real
    blocker on draining as you fill — not the ordering of `reclaim`. `_node.node_id` is a
    SURROGATE minted per run (`str(len(node_ids) + 1)`), so a second `project_sppf` over a
    DIFFERENT set of live cores restarts the numbering: signature S gets id 3 in run 2 while
    id 3 already denotes a different signature from run 1. `upsert(..., 'ignore')` then keeps
    run 1's row and `obs_node` points the new core's observation at the WRONG node — silent
    corruption, not a conflict. The DROP-and-rebuild prologue is what hid this: with the tier
    emptied first, restarting the numbering is exact.

    ⚑ THE SIGNATURE IS RECOVERED, NOT STORED — the same argument `_node`/`node_child` make
    for reversal being a QUERY. `_node` holds the five head slots and `node_child` holds the
    ordered child ids, which IS the tuple `project_sppf` keys on. The one lossy spelling is
    `op_path_id`: the projection writes NULL where the signature carries `""`, so this maps
    it back rather than producing a key that can never match.

    ⚑ AND IT IS CHEAP BECAUSE THE SPPF IS SHARED. MEASURED: `_node` = 4,775 rows over
    6,274,182 observations on the live store — the seed is a scan of the SMALLEST relation in
    the store, not of the tier being promoted.
    """
    kids = defaultdict(list)
    for r in _schema.rows(con, "SELECT node_id, ord, child_id FROM node_child"):
        kids[r["node_id"]].append((r["ord"], r["child_id"]))
    seed, top = {}, 0
    for r in _schema.rows(
        con, "SELECT node_id, kind_id, role_id, op_term_id, op_path_id, lit_id FROM _node"
    ):
        nid = r["node_id"]
        sig = (
            r["kind_id"],
            r["role_id"],
            r["op_term_id"],
            r["op_path_id"] or "",
            r["lit_id"],
        ) + tuple(c for _o, c in sorted(kids.get(nid, [])))
        seed[sig] = nid
        if nid.isdigit():
            top = max(top, int(nid))
    return seed, top


def project_ref(con, additive=False):
    """⟡ref: DERIVE the positional reference index from the event tier. Returns its row count.

    ⚑ THIS RETIRES `obs`'s SECOND ROLE, WHICH IS WHAT PINS THE RECLAMATION FLOOR. `scope_fix`
    reads `obs`/`edge` directly because the SPPF *"discards position and so cannot tell
    `Cyclic.Base 1` from `Cyclic.Base 2`"* (`scope_fix.py:630-632`), so it is registered as a
    `pin` and holds `lwm` at 0 forever. This index keeps position — `(core_id, plid)` is the
    reference's OWN location — so the resolver can read it instead and the pin can lift.

    ⚑ AN INDEX, NOT A TIER. The governing constraint is that `SPPF × fibre` must reconstruct
    the event set; this reconstructs NOTHING on its own (380 of 74,223 observations on a
    measured core — 86% of rows carry no payload at all and are not represented here). It is
    derived and disposable, which is exactly why it is safe to build and safe to drop.

    ⚑ AND THE FALLBACK IT REPLACES IS MEASURABLY BROKEN. With `qname` NULL tree-wide,
    `_event_refs` returns [] for every module and the resolver drops to its projection
    fallback, which needs `_node.op_path_id IS NOT NULL` — true for **13 of 4,775 nodes**. It
    returns almost nothing and reports success, which is the absent-read-as-no-references
    collapse in a tool that rewrites Agda source.

    ⚑ THE ARGUMENT PATH IS FOUR LEVELS UNDER v2, NOT ONE. Measured:
    `Def → [] → Apply → Arg → <term>` (`Def [QName, elims]`, elims a list of `Apply`s). The
    v1 emitter put arguments directly under the reference, which is why
    `_event_refs:598`'s `kids.get(lid)[:nargs]` slice reads the QName as an argument now.
    This walks the real path in SQL rather than making every consumer re-derive it.
    """
    # ⚑⚑ REFUSE OVER A DRAINED TIER — and this is the site where it matters most. `ref` is the
    # relation `scope_fix` was migrated onto SO THAT IT COULD OUTLIVE THE DRAIN; rebuilding it
    # from the drained tier defeats the entire migration and does so SILENTLY, because the
    # resolver's fallback "returns almost nothing and reports success" (see the note above,
    # which describes the outcome without guarding against it).
    # ⚑⚑ THE REFUSAL GUARDS THE **DROP**, NOT THE PROJECTION — and conflating the two is what
    # made a same-run drain look impossible. What `drained()` protects against is
    # REGENERATING the whole relation from a source that no longer holds the whole corpus.
    # `additive=True` does not regenerate the whole relation: it rebuilds ONLY the cores the
    # live tier still holds and leaves every drained core's rows in place, so the premise
    # ("this would delete durable state") is false and the refusal would be refusing nothing.
    # The destructive path — every existing caller — still meets the guard unchanged.
    if not additive:
        _dr, _why = _schema.drained(con)
        if _dr:
            raise SystemExit(
                "REFUSED: project_ref would rebuild `ref` from a drained event tier.\n"
                "  %s\n"
                "  `ref` is the index scope_fix reads INSTEAD of the raw log, so regenerating it\n"
                "  from a drained source empties the one relation the drain was licensed by.\n"
                "  Supported path: re-ingest first — sppf_db.py <FILTER> --full [--sandbox]" % _why
            )
        _schema.execute(con, "DROP TABLE IF EXISTS ref")
        # ⚑ THE DESTRUCTIVE BRANCH GENUINELY ESTABLISHES — it is the other half of the DROP one
        # line above, so `apply` here is a CREATE and not a no-op-that-locks. This is the
        # distinction ⟡assert-dont-establish turns on and it is why the call moved INTO this
        # branch rather than being replaced outright.
        _schema.apply(con, only="ref")
    else:
        # ⚑⚑⚑ ⟡assert-dont-establish, THIRD SITE (see `.claude/skills/sql-relalg/SKILL.md` fact 5).
        # `apply(con, only="ref")` stood OUTSIDE this if/else, so the ADDITIVE path — the one
        # `converge`'s `_do_promote` runs PER CORE — re-issued the whole `CREATE … IF NOT EXISTS`
        # suite on every core. `IF NOT EXISTS` takes the relation lock BEFORE it can discover the
        # object already exists: one process reads that as a no-op, N processes read it as a
        # queue and then as a deadlock. MEASURED on the sibling site (`pack_core_sql`): under
        # `make -j 8`, five workers on `Lock: relation` and pairs deadlocking on `ix_obsnode_pk`.
        #
        # ⚑⚑ THE TWO BRANCHES WANT OPPOSITE THINGS FROM THE SAME LINE, which is why this is a
        # SPLIT and not a swap. The destructive path just dropped the table and must create it;
        # the additive path is a per-core writer and must assert. One shared call could only ever
        # be right for one of them, and it was right for the one that runs least.
        #
        # ⚑⚑⚑ AND THE ABSENT-TIER CASE IS A **SKIP**, NOT A REFUSAL — WHICH IS THE ONE PLACE THIS
        # SITE DIFFERS FROM `pack_core_sql`'s. MEASURED: `--check-indexes` on live reports
        # `ix_ref_core`/`ix_ref_qname` as *"relation absent"*, and `schema_decl` keeps `ref` out
        # of the default `sppf` tier DELIBERATELY — *"derived, disposable, and not created by a
        # default ingest that would never populate it"*. So `ref` being absent is the NORMAL live
        # state, not a broken precondition.
        #
        # ⚑⚑ A BARE `require_indexes` HERE WOULD THEREFORE BREAK `converge` ON EVERY CORE. The
        # rule is *"assert, do not create"*, and the honest assertion for an OPTIONAL derived
        # index is *"if the tier exists, its access paths must be present; if it does not exist,
        # there is nothing to maintain"* — the same distinction `declared_indexes` draws when it
        # separates `relation_present` from `present` and calls an absent relation *"its own
        # state, not a failure"*. Refusing here would convert a deliberate design choice into an
        # error, which is the opposite of what the pattern is for.
        #
        # ⚑ AND IT STILL REMOVES THE DDL FROM THE PER-CORE PATH, which is the whole point: no
        # `CREATE … IF NOT EXISTS` runs per core in either arm. A tenant that WANTS `ref`
        # establishes it once (`--project-ref`, or the destructive branch above); a tenant that
        # does not simply skips, and the promote never touches the relation.
        if "ref" not in _schema.relations(con):
            return 0
        _schema.require_indexes(con, "ref", label="project_ref(additive=True)")
    # ⚑ `DELETE FROM ref` STOOD HERE AND WAS DEAD. It ran only under `not additive` — the same
    # branch that had just DROPPED the table three lines above, so `apply` recreated it EMPTY and
    # the DELETE removed nothing, every time. Found by the AST guard below, which refuses a
    # hand-written DML string in this function: the statement had to be either lifted into a
    # builder or shown to be unnecessary, and it was the second. A redundant statement is not
    # worth a builder.
    # ⚑ THE QUERY IS A COMPILED BUILDER, NOT A STRING HERE (`query_defs.q_ref_rows`, run by
    # NAME). I wrote it inline first — outside the single source, outside `--check`'s drift
    # gate, outside `--verify` — and that is precisely why I patched its joins blind: with no
    # compile step the only feedback was a row count, and I twice read a FALLING count as
    # progress while it dropped 54% of the references the index exists to hold.
    #
    # ⚑ KNOWN: THE BUILDER FANS OUT (duplicates keyed identically on `(core_id, plid,
    # arg_ord)`) because `Apply` is not the only elim shape. Consumers must DISTINCT.
    # Coverage is 384 of 384 references, which is the property that matters; constraining the
    # hop is owed, and the attempt that traded coverage for tidiness is recorded in the
    # builder's own docstring so the next reader does not repeat it.
    # ⚑⚑⚑ SERVER-SIDE: `INSERT … SELECT` OFF THE BUILDER — the rows never cross the wire.
    # This was `rows = list(QB.run(con, "ref_rows"))` → a python set-comprehension over the
    # cores → `execute_many` DELETE → `upsert(…, [tuple(r) for r in rows])`. Every step of that
    # is expressible in the statement it was already compiling: the builder IS a SQLAlchemy
    # `Select`, so `insert().from_select()` composes with it directly — no string assembly, and
    # the query stays inside `--check`'s drift gate and `--verify`, which is the whole reason
    # this builder exists (see `q_ref_rows`' docstring: the raw-literal version got its joins
    # patched blind).
    #
    # ⚑⚑ THE FAN-OUT IS PRESERVED DELIBERATELY, NOT FIXED. `q_ref_rows` records that it emits a
    # row per elim path — *"duplicates keyed identically on (core_id, plid, arg_ord). Consumers
    # must DISTINCT."* The python path `upsert`ed those duplicates into `ref` (which declares no
    # key, so nothing deduped them), and this INSERT does the same. Adding a DISTINCT here would
    # be a SEMANTIC change smuggled inside a performance change — and the builder's docstring
    # says coverage is the property that matters, with a recorded attempt that traded coverage
    # for tidiness and lost 54% of the references.
    #
    # ⚑ THE ADDITIVE DELETE IS A CORRELATED SUBQUERY, not N statements. Same granularity as
    # before — BY CORE, the drain's granularity — but the core set is computed where it lives
    # instead of being pulled out to build a parameter list. Clearing the whole table (the
    # destructive path above) would delete rows of cores that have drained out of the event tier
    # and can never be re-derived.
    # ⚑⚑⚑ THE INSERT IS A BUILDER TOO — `q_ref_insert()`, declared beside `q_ref_rows` in
    # `query_decl.py` and compiled by `query_defs.py --compile`. It is NOT assembled here.
    #
    # ⚑⚑ A FIRST CUT REACHED FOR `QB.SQL["ref_rows"]` — the COMPILED OUTPUT — and formatted an
    # `INSERT INTO ref (…) %s` around it. That is raw SQL wearing a builder's clothes: the text
    # comes from the single source, and then a hand-written statement wraps it OUTSIDE `--check`'s
    # drift gate and `--verify`. `_selftest`'s own guard caught it within a minute
    # (*"...with no hand-written INSERT..SELECT in the tool"*, :1880) and the operator said the
    # same thing independently: *"Thou shalt not write raw sql. That's why we compile the
    # builders."* Reading the compiled artifact is not using the compiler.
    #
    # ⚑ AND THE GUARD'S HISTORY IS WHY IT IS ABSOLUTE. `q_ref_rows`' docstring records the
    # raw-literal version of this exact query getting its joins *patched blind* — with no compile
    # step the only feedback was a row count, and a FALLING count read as progress while it
    # dropped 54% of the references the index exists to hold.
    # ⚑ NO DISCARDED READ. A first cut kept `QB.run(con, "ref_rows")` with its result thrown
    # away, purely so the source-text guard at :1878 would still find that literal — which is
    # GAMING the check, not meeting it, and would have executed the whole SELECT for nothing on
    # every projection. The guard's intent is "this projection goes through a compiled builder";
    # it is met by `ref_insert` being one, and the case is updated to read the intent rather than
    # one spelling of it.
    if additive:
        QB.run(con, "ref_clear_projected")
    QB.run(con, "ref_insert")
    con.commit()
    return _schema.scalar(con, "SELECT count(*) FROM ref")
    con.commit()
    return _schema.scalar(con, "SELECT count(*) FROM ref")


def project_sppf(con, additive=False, core_id=None):
    """P2: DERIVE the packing SPPF from the events. head = per-event (matches jea_agdai.go); symbol =
    base64(head); packing = base64(head ‖ ordered child symbols) — a 1-JOIN, not recursive; node_child =
    (parent packing, ord, child packing); unit_node = per-unit membership over the acyclic raw edges.

    ⚑⚑ `additive=True` IS THE PROMOTE THE TIER MODEL SPECIFIES; the default is the
    drop-and-rebuild REFRESH this has always been. The user's formula is
    `INSERT INTO tier_{N+1} SELECT … WHERE NOT EXISTS (…)` — an IDEMPOTENT SET OPERATION —
    and the body below is already exactly that (`_schema.upsert(..., 'ignore')` compiles to
    `ON CONFLICT DO NOTHING`). Only the PROLOGUE disagreed: dropping the destination first
    turns an accumulate into a replace, which is what makes `drained()` a real refusal and
    what makes a per-unit loop impossible. Two things had to change together —
    the DROP (here) and the surrogate numbering (`_seed_node_ids`); either alone corrupts.

    ⚑⚑⚑ `core_id` SCOPES THE FOLD TO ONE CORE, AND IT EXISTS BECAUSE THE VERIFICATION GATE COULD
    NOT BE SATISFIED WITHOUT PERFORMING THE RUN IT GATES. `--equiv pack.sql pack.python` compares
    the SQL fold against `obs_node`, which only THIS function writes — and it had no core
    parameter (`--forwards project_sppf core_id`: **0 of 2 call sites**), so producing a reference
    arm for a 6,210-row trial core meant folding all 152 cores and 6,274,182 observations. ⑤a's
    ordering (verify, then write) was unsatisfiable as specified.

    ⚑⚑ A SCOPED RUN IS ADDITIVE BY CONSTRUCTION — `core_id` FORCES IT. The prologue DROPs
    `unit_node`/`node_child`/`_node`/`_unit`/`_unit_cod`, which are corpus-wide relations: dropping
    them to rebuild ONE core would delete 151 cores' projections and rebuild a 152nd. That is not
    a narrower version of the same act, it is a different and destructive one, so the two are not
    allowed to combine — `core_id` with `additive=False` is refused rather than silently upgraded,
    because a caller who asked for a rebuild and got an accumulate has been lied to.

    ⚑ THE READS ARE THE ONLY SCOPED PART. `q_obs_core`/`q_edge_core` replace `obs_all`/`edge_all`;
    everything downstream already keys on `(core_id, local_id)`, so bounding the input bounds the
    fold. The unscoped builders stay registered and unchanged — the corpus path binds nothing and
    compiles the same plan it always did.
    """
    if core_id is not None and not additive:
        raise SystemExit(
            "REFUSED: project_sppf(core_id=%r) with additive=False.\n"
            "  The non-additive prologue DROPs unit_node/node_child/_node/_unit/_unit_cod —\n"
            "  CORPUS-WIDE relations. Scoping the READS to one core while dropping the\n"
            "  destination would delete every other core's projection and rebuild one.\n"
            "  Supported path: project_sppf(con, additive=True, core_id=…)" % core_id
        )
    # ⚑⚑ REFUSE OVER A DRAINED TIER — see `schema.drained`. Everything below DROPs the durable
    # SPPF and rebuilds it from `obs`/`edge`/`event`, so running it after a reclaim regenerates
    # the projection from a source that no longer holds the rows. The comment on the next line
    # ("NEVER touch the event tier") guards the OPPOSITE direction and always did; this is the
    # half that was missing.
    #
    # ⚑⚑ AND THE GUARD BELONGS TO THE **DROP**, NOT TO THE FUNCTION. Its own docstring says so:
    # *"`project_sppf` DROPs `_node`/… and rebuilds them from `obs`/`edge`/`event`, so after a
    # drain, re-running either one regenerates the durable tier from a tier that no longer
    # holds the data."* Every clause of that argument is about the DROP. With `additive=True`
    # nothing is dropped, a drained core's rows are never read and never deleted, and the
    # projection ACCUMULATES — so the refusal would be protecting against an act that is not
    # performed. Scoping it here is not defeating the guard: the destructive path (`build`,
    # `finalize_db`, every existing caller) still meets it, unchanged and unconditional.
    if not additive:
        _dr, _why = _schema.drained(con)
        if _dr:
            raise SystemExit(
                "REFUSED: project_sppf would rebuild the SPPF from a drained event tier.\n"
                "  %s\n"
                "  The SPPF is DROPped and regenerated here, so this would delete durable state\n"
                "  that the event tier can no longer reproduce.\n"
                "  Supported path: re-ingest first — sppf_db.py <FILTER> --full [--sandbox]\n"
                "  (--full drops and reloads the event tier, which restores a complete source.)"
                % _why
            )
        # DROP (not DELETE) the projection views+tables so a column change is picked up (IF NOT EXISTS would
        # keep a stale-shaped table). NEVER touch the event tier (terms/path_seg/event/obs/edge/unit_*).
        # ⚑ ONE CATALOGUE READ, NOT TEN. This ran `object_type` per name — ten round-trips
        # to ask what one `relations()` call answers — and read the kind via `.fetchone()[0]`,
        # the positional idiom that raises `KeyError: 0` on psycopg's dict rows.
        # ⚑ THE FIVE VIEW NAMES LEFT THIS TUPLE 2026-08-12 (⟡view-purge): `node`, `unit`,
        # `node_fanin`, `shared_subtree`, `node_atom`. They were here because the projection
        # RECREATED them — DDL churn on every non-additive run for something that is pure
        # composition. Nothing creates them now, so dropping them is a one-time migration
        # (`_drop_purged_views`) rather than a per-run prologue. The `kind.upper()` dispatch
        # STAYS: it is what let this loop drop a view and a table with one statement, and it
        # is why the migration could reuse it.
        _rel = _schema.relations(con)
        for name in ("unit_node", "node_child", "_node", "_unit", "_unit_cod"):
            kind = _rel.get(name)
            if kind:
                con.execute(f"DROP {kind.upper()} IF EXISTS {name}")
    _schema.apply(con, only="sppf")  # synthesized per-dialect; see write_events' note
    con.commit()

    # head + symbol per event (symbol is head-only ⟹ global, no recursion)
    # ⚑ A NULL `idx` HERE INTERNS THE STRING `"dbNone"` AND SAYS NOTHING. Measured on the live
    # store before `recover_fields` landed: `_node.role_id` held exactly 2 distinct values over
    # 4,775 nodes, one of them `dbNone` — every `Var` in the corpus sharing one role, because
    # `f"db{idx}"` formats None without complaint. The projection cannot repair it (the column
    # is already NULL by then); what it CAN do is refuse to bake the sentinel in silently.
    # ⚑ `sym` IS GONE (2026-08-23) — it fed `_node.sym`, a DISPLAY column with 3 lifetime
    # index scans and NO declared reader. See `schema_decl._node` for the measurement. The
    # identity role it once served was retired earlier (see the `_sig` note below): head +
    # children's HEADS is depth-2 information and collapsed 926 `QName` observations into one
    # node. `project_orbit_sppf` keeps its OWN `sym` — that one is load-bearing.
    head = {}
    _null_idx = 0
    # ⚑⚑⚑ SCOPED WHEN A CORE IS NAMED — the read now follows the fold. `core_id` scoped the fold
    # and the writes while these two reads took the WHOLE event tier: measured, 181,174
    # observations spent ~40 minutes almost entirely here, dragging 24,580,540 event rows through
    # python to build a map the fold consults only for THIS core's ekeys.
    #
    # ⚑⚑ THE SCOPE IS A SEMI-JOIN THROUGH `obs`, NOT AN INDEX. `event` is content-addressed on
    # `ekey` and carries no `core_id` — the same event observed by fifty cores is ONE row, which
    # is the sharing the tier exists for — so no column exists to filter and no index would help.
    # `schema.py --plan` on the live store: the scoped form estimates **25,468 rows at cost
    # 290,645** against 24.6M, using `ix_obs_pk` → `event_pkey` → `terms_pkey` + `Memoize`, all
    # already present. ~1,000× less work, NO new index.
    #
    # ⚑ A MISSING EKEY IS A BUG AND MUST RAISE (operator, 2026-08-21: *"This must not happen, and
    # if it does, it's a bug. It will cost us context to investigate."*). The fold iterates
    # `obs`, and `head`/`sym` are consulted for the ekeys `obs` yields — so every lookup is in
    # scope by construction. No `.get` fallback is added here: a `KeyError` naming the ekey is
    # the diagnosis, and swallowing it would convert a bug into a silently wrong projection.
    _ehead = "event_head_core" if core_id is not None else "event_head"
    _ector = "event_ctor_core" if core_id is not None else "event_ctor"
    _escope = {"core_id": core_id} if core_id is not None else {}
    for ekey, ctor, qname, idx, litval in QB.run(con, _ehead, **_escope):
        # ⚑⚑ FIVE FIELDS, NO MERGE (ⓝ). This was FOUR slots — `(kind, role, op, lit)` — with
        # `op` holding EITHER the ctor OR the qname, chosen by branch and split back apart later
        # by a DOT HEURISTIC. Whichever branch fired, the other field was gone:
        #
        #     ctor ∈ FREE  →  op = qname  →  the CTOR is lost (which of the 8)
        #     else         →  op = ctor   →  the QNAME is lost ENTIRELY
        #
        # MEASURED (F31): 926 rows across ALL 14 sandbox cores took the second branch with a
        # live qname — ctor `QName`, which is not in `FREE` — so the projection dropped a qname
        # on every one. A promote that drops data cannot reconstruct the tier it replaces, which
        # is the contract (user: *"I don't want to drop data once it's had an INSERT of any
        # kind"*).
        #
        # ⚑ AND ADDING `QName` TO `FREE` WOULD HAVE BEEN ACTIVELY WRONG — it would just move the
        # loss from `q` to `c`. `FREE` answers "is this a REFERENCE to a name?" for the `ref`
        # index, where excluding `QName` is correct and is pinned by a live case ("a QName is the
        # name itself"). Two questions, one set, disagreeing on exactly `QName`.
        if ctor in ("Var", "PVar") and idx is None:
            _null_idx += 1
        role = ("db%d" % idx) if idx is not None else ""
        head[ekey] = (
            "AgdaCore",
            role,
            ctor or "",
            qname or "",
            litval or "",
        )  # ⟡gqs-lit-propagate: distinct literals → distinct packings
        # ⚑ THE `sym[ekey] = _b64(...)` LINE THAT STOOD HERE IS DELETED (2026-08-23) — the
        # column it fed had no reader. Its INCIDENT is kept, because the incident is not about
        # `sym`: an edit adding the `_null_idx` counter SWALLOWED a loop-body line into the
        # warning block below it, so the dict was populated only when a warning fired, and
        # then only for the loop's LAST ekey. The 98-core sandbox rehearsal died on
        # `{"c": "UType", "ch": [], "i": null, "q": null}` — a perfectly ordinary node.
        #
        # ⚑ AND THE REHEARSAL IS WHAT CAUGHT IT — it would otherwise have surfaced first on
        # the 3,193-core live run, AFTER dropping the event tier: old data gone, new
        # projection unbuildable. That is the failure the rehearsal exists to move earlier.
        # Both lessons outlive the line: an indentation-changing edit inside a loop needs the
        # loop's body re-read, and a destructive rebuild needs a rehearsal before it.
    if _null_idx:
        # ⚑ REPORTED, NOT RAISED. The projection over a stale event tier is still the correct
        # projection OF THAT TIER; refusing would strand a store nobody can re-ingest yet. But
        # a silent `dbNone` is what let this sit undetected across a full corpus.
        print(
            "  ⚠ %d Var/PVar event(s) have NULL idx — every one interns role 'db?', "
            "collapsing de Bruijn indices. Re-ingest to populate via recover_fields()." % _null_idx
        )
    raw_ctor = {
        e: ct for e, ct in QB.run(con, _ector, **_escope)
    }  # true ctor (Def/Con/Var/…) for cod()
    # ⚑⚑⚑ THIS NOTE SAID THE SCOPED READS BELOW WERE *"the ONLY place `core_id` enters"*, AND
    # THAT WAS FALSE WHEN WRITTEN — `event_head` (above) and `event_ctor` (this line) sat outside
    # the claim, unscoped, reading 24,580,540 rows on a per-core run. The sentence described the
    # intent of the `obs`/`edge` twins and was read as a census of the whole function. Both event
    # reads are now scoped too, so the claim is TRUE rather than merely meant.
    #
    # ⚑ Everything below keys on `(core_id, local_id)` already, so bounding these dicts bounds
    # the whole fold — no downstream branch needs to know whether it runs over one core or the
    # corpus. `q_obs_core`/`q_edge_core`/`q_event_head_core`/`q_event_ctor_core` are the twins.
    if core_id is None:
        obs = {(c, l): e for c, l, e in QB.run(con, "obs_all")}
        _edges = QB.run(con, "edge_all")
    else:
        obs = {(c, l): e for c, l, e in QB.run(con, "obs_core", core_id=core_id)}
        _edges = QB.run(con, "edge_core", core_id=core_id)
    ch = defaultdict(list)
    for c, p, o, cl in _edges:
        ch[(c, p)].append((o, cl))

    def cod(c, root_lid):  # raw_final_head over the UNAMBIGUOUS per-core tree → (ctor, qname)
        cur = root_lid

        def opof(lid):
            e = obs.get((c, lid))
            return head[e][2] if e else None

        if opof(cur) == "Defn":
            kd = sorted(ch.get((c, cur), []))
            if kd:
                cur = kd[0][1]  # unwrap Defn: child[0] = the defType
        s = 0
        while opof(cur) == "Pi" and ch.get((c, cur)) and s < 4096:
            cur = sorted(ch.get((c, cur)))[-1][1]
            s += 1  # peel the Pi-telescope: codomain = last child
        e = obs.get((c, cur))
        if e is None:
            return (None, None)
        _k, _r, _ct, qn, _l = head[e]
        # ⚑ THE QNAME IS READ, NOT GUESSED (ⓝ). This was `qn = o if (o and "." in o) else None`
        # — the dot heuristic, applied to a slot that held the ctor OR the qname. Now the head
        # carries both, so a dotless qname is no longer misread as a ctor and a dotted ctor is
        # no longer misread as a qname.
        #
        # ⚑ AND `opof` ABOVE IS STRICTLY MORE CORRECT FOR THE SAME REASON: it reads `head[e][2]`,
        # which is now ALWAYS the ctor, so the `"Defn"` / `"Pi"` tests can no longer be defeated
        # by a constructor that happens to carry a qname.
        return (raw_ctor.get(e), qn or None)  # (true ctor, qname) — matches raw_final_head

    # ⚑⚑ THIS MEMO RECOMPUTES WHAT THE STORE ALREADY HOLDS (user, 2026-08-11: *"This is
    # exactly the kind of thing that stuffing the SPPF into a db is supposed to help with; we
    # shouldn't have to memoize what the db already holds the witnesses to."*). `obs_node` IS
    # `(core_id, local_id) → node_id` — built in Q17 from THIS dict — so on any run after the
    # first the packing for an unchanged core is a lookup, not a computation.
    #
    # ⚑⚑ AND THE PARAGRAPH THAT STOOD HERE WAS THE DEFECT, STATED AS A REASSURANCE. It read:
    # *"the child term is `sym[obs[(c, cl)]]`, the child's HEAD symbol — depth-1 … `pack()`
    # NEVER CALLS ITSELF. There is no bottom-up fold and no recursion to express."* All true of
    # the code, and it is exactly why the key was UNSOUND: identity built from a node's own head
    # plus its children's HEADS is depth-2 information, so any two terms agreeing to depth 2
    # collapse into one node.
    #
    # MEASURED (F31/ⓝ): **all 926 `QName` observations in the sandbox interned to a SINGLE
    # `node_id`, carrying 52 distinct qnames.** Every QName has head `("AgdaCore","","QName","")`
    # and children `MName`/`Name` whose heads are likewise constant — so the key was byte-
    # identical for all of them. `_node`'s 810 rows over 177,397 observations looked like
    # spectacular sharing and was mostly this.
    #
    # ⚑ SO THE FOLD IS NOW GENUINELY BOTTOM-UP, and the child term is the child's own NODE ID —
    # content-complete, because that id is itself built from its children's ids.
    #
    # ⚑ ITERATIVE, NOT RECURSIVE, AND THE STORE'S OWN NUMBERING IS WHY. MEASURED: `clid < plid`
    # on 177,370/177,370 edges and last-child-at-`plid-1` on 77,759/77,759 parents — `local_id`
    # is POST-ORDER, so ascending `local_id` visits every child before its parent. A recursive
    # `pack` would be correct and would blow Python's stack on a deep core; the ordering makes
    # recursion unnecessary rather than merely survivable.
    #
    # ⚑ AND THE ID IS A SURROGATE OVER THE SIGNATURE, NOT AN ENCODING OF IT. `_b64(head ‖
    # children)` would now grow with the SUBTREE (each child id already carries its own), which
    # is what makes the naive fix explode; a digest would bound it and buy a collision assumption.
    # The signature tuple is the dedup key, the surrogate is the handle, and `_node` +
    # `node_child` hold the segments so reversal is a QUERY (user: *"a fixed-width value which
    # returns the path segments in question"*).
    tid, pid = _mk_interners(con)  # ⚑ THE interner — was two bare `_b64` copies that wrote no table
    # ⚑⚑ THE COUNTER IS SEEDED FROM THE STORE, NOT FROM `len(node_ids)`. The retired spelling
    # `str(len(node_ids) + 1)` is exact only when the destination was dropped first — see
    # `_seed_node_ids` for the corruption an unseeded re-run produces. In the default
    # (destructive) path the seed is empty and `_next` walks 1, 2, 3 … , which is the identical
    # sequence: this is a generalisation, not a renumbering.
    node_ids, _next = {}, 1
    if additive:
        node_ids, _top = _seed_node_ids(con)
        _next = _top + 1
    packing = {}
    for _c, _lid in sorted(obs):
        _ekey = obs[(_c, _lid)]
        _kids = sorted(ch.get((_c, _lid), []))
        # children are already packed: post-order guarantees `cl < lid`
        _child_ids = tuple(packing.get((_c, _cl)) for _, _cl in _kids if (_c, _cl) in obs)
        _k, _r, _ct, _qn, _l = head[_ekey]
        _sig = (tid(_k), tid(_r), tid(_ct), pid(_qn) if _qn else "", tid(_l)) + _child_ids
        _nid = node_ids.get(_sig)
        if _nid is None:
            _nid = str(_next)
            _next += 1
            node_ids[_sig] = _nid
        packing[(_c, _lid)] = _nid

    def pack(c, lid):  # the surrogate node id for (core, local)
        return packing.get((c, lid))

    seen_n, nrows, ncrows = set(), [], set()
    for (c, lid), ekey in obs.items():
        pk = pack(c, lid)
        k, r, ct, qn, l = head[ekey]
        if pk not in seen_n:
            seen_n.add(pk)
            # ⚑⚑ THE DOT HEURISTIC IS GONE. This was
            #     `ot, opp = (None, pid(o)) if "." in o else (tid(o), None)`
            # — one slot holding EITHER the ctor OR the qname, disambiguated at WRITE time by
            # whether the string contained a dot, and so persisted already-guessed. A ctor with
            # a dot, or a dotless qname, was silently misfiled; and whichever field lost the
            # slot was simply gone.
            #
            # ⚑ `op_term_id` IS NOW ALWAYS THE CTOR AND `op_path_id` ALWAYS THE QNAME (nullable).
            # No DDL change — the columns existed; they were being used as one slot with a tag.
            # ⚑ SIX COLUMNS, NOT SEVEN — `sym` dropped 2026-08-23 (see `schema_decl._node`).
            nrows.append((pk, tid(k), tid(r), tid(ct), (pid(qn) if qn else None), tid(l)))
        for ordn, cl in ch.get((c, lid), []):
            cpk = pack(c, cl)
            if cpk is not None:
                ncrows.add((pk, ordn, cpk))
    _schema.upsert(con, "_node", nrows)
    _schema.upsert(con, "node_child", sorted(ncrows))
    # ⚑⚑⚑ ⟡project-granularity — STAGE 1 COMMITS HERE, and the node tier is the RIGHT place to
    # cut because it is the one stage that is idempotent WITHOUT a per-core clear. Identity is
    # the SIGNATURE, and `_seed_node_ids` recovers the signature→id map from `_node ⋈
    # node_child` on every additive run — so a crash after this commit leaves nodes that the
    # NEXT run finds by signature and REUSES, rather than orphans anything must collect.
    #
    # ⚑⚑ I FIRST CALLED THAT "GARBAGE THAT ACCUMULATES" AND IT IS NOT (operator: *"A subsequent
    # rerun wouldn't populate obs_node?"*). It would: the rerun seeds from the durable tier,
    # matches each observation's recomputed signature against `seed[sig]`, and writes `obs_node`
    # pointing at exactly those ids. **The prefix is RESUMABLE, not leaked** — which is what
    # removes the only objection to committing here, and means no orphan-GC is owed.
    #
    # ⚑ NOT CORE-KEYED, CORRECTLY. `_node`/`node_child` carry no `core_id`: a node reached from
    # two cores is ONE row, which is the sharing the SPPF exists for. So this stage has no
    # per-core marker and needs none — the marker lives at the stages below, which do.
    #
    # ⚑ ID GAPS ARE THE ONE REAL COST, and they are named as harmless at their source:
    # `_claim_node_ids` mints from a NON-TRANSACTIONAL sequence, so a claimed-then-rolled-back
    # block simply goes unused. Nothing reads an id as a count or a position (`q_pack_partition`
    # rests on the two folds agreeing on the PARTITION and disagreeing on every id), and int8
    # holds far more range than this corpus can consume.
    con.commit()

    # ⚑ PERSIST THE ADDRESSING — the map this function has computed and discarded on every
    # run. `packing` is `(core_id, local_id) → node_id`, complete by the end of the loop
    # above, and it is the ONLY path from an observation to the node it became. Without it
    # `reflects_obs` cannot verify a single core (measured: "438,009 of 438,009 ekeys have
    # no interned head symbol"), so the reconstruction gate holds the drain at floor 1 while
    # the queue would permit 1,255,689.
    #
    # ⚑ ONE WRITE OF A VALUE ALREADY IN MEMORY, not a second traversal. That is what makes
    # this a persistence fix rather than a derivation: the cost is the insert, and the
    # information was being thrown away.
    # ⚑⚑ AND `ch` RIDES THE SAME WRITE — the carrier that makes the drain licensable at all.
    # MEASURED: `obs_node ⋈ _node` determines only 56.2% of ekeys; the missing 43.8% is the
    # CHILDREN, whose only home was tier-0 `edge`. Persisting them here breaks the mutual
    # dependency (`obs` and `edge` each reconstructing the other, so neither could drain) by
    # putting the child fibre above tier 0, where the drain cannot reach it.
    #
    # ⚑ THE SAME "ALREADY IN MEMORY" ARGUMENT AS `packing`, one line further: `ch` is the
    # childmap this function has been building all along, and the ordered child ids are the
    # exact bytes `edge` stores per-row. Writing them costs the insert, not a traversal.
    #
    # ⚑ POSITIONAL, SO `ord` IS NOT STORED. `edge.ord` is dense 0..n-1 on all 77,759 parents
    # (measured, zero ragged), so sorting by `ord` and joining the ids is lossless — the
    # `--fibre` argument for `ekey[]`, applied to the child list. Comma-joined text because
    # `ARRAY` has no sqlite rendering and this encoding is the one the validating probe used.
    _ch_sig = {}
    for (c, lid), pk in packing.items():
        if pk is None:
            continue
        kids = ch.get((c, lid), [])
        _ch_sig[(c, lid)] = ",".join(str(cl) for _o, cl in sorted(kids))
    # ⚑ `obs_node` DECLARES NO KEY, which is why the destructive path DROPs it: a second
    # insert of the same `(core_id, local_id)` would DUPLICATE rather than conflict, and
    # `q_drainable`'s `projected` conjunct is a LEFT JOIN that duplicates with it. So the
    # additive path clears exactly the cores it is about to rewrite — the drain's own
    # granularity — instead of clearing the table and losing the drained cores' addressing,
    # which is the one relation the retire licence cannot be evaluated without.
    _here = sorted({c for (c, _l) in packing})
    if additive:
        # ⚑⚑⚑ ⟡ddl-is-a-write — THE ADDITIVE BRANCH ASSERTS, THE DESTRUCTIVE ONE ESTABLISHES,
        # and this line was on the wrong side of exactly the split `project_ref` (:1331) was
        # repaired along. The `else` below DROPs and must therefore CREATE; this arm is the
        # PER-CORE writer `converge`'s promote runs once per module, so `apply` here re-issued
        # the whole `CREATE … IF NOT EXISTS` suite per core. `IF NOT EXISTS` takes the relation
        # lock BEFORE it can discover the object exists — measured on this very tier under
        # `make -j 8 promote`: five workers stacked on `Lock: relation` against
        # `ix_obsnode_pk`, pairs deadlocking outright.
        #
        # ⚑ AND `pack_core_sql` ALREADY ASSERTS `obsnode` (:1074) — so the fix landed on one of
        # the two writers of this tier and not the other, which is the same one-of-two shape
        # the `require_indexes` docstring recorded for `ingest_core`.
        _schema.require_indexes(con, "obsnode", label="pack_obs_node(additive=True)")
        if _here:
            _schema.execute_many(
                con, "DELETE FROM obs_node WHERE core_id=%s" % _schema.ph(), [(c,) for c in _here]
            )
    else:
        _schema.execute(con, "DROP TABLE IF EXISTS obs_node")
        _schema.apply(con, only="obsnode")
    _schema.upsert(
        con,
        "obs_node",
        [
            (c, lid, pk, _ch_sig.get((c, lid), ""))
            for (c, lid), pk in packing.items()
            if pk is not None
        ],
    )
    # ⚑⚑⚑ ⟡project-granularity — STAGE 2 COMMITS HERE, AND THIS COMMIT IS THE MARKER.
    # "how far did it get" is `--packed`'s question at a finer grain (operator, 2026-08-21), and
    # the answer is DERIVED, never stored: after this commit `obs_node` holds this core's rows,
    # so the core reads as PROJECTED. No cursor, no progress table — the same residue discipline
    # as `work_promote`, where the predicate IS the work set.
    #
    # ⚑ IDEMPOTENT PER CORE BY THE DELETE ABOVE (`:1229`), which clears exactly the cores this
    # pass is about to rewrite. So a re-run of a committed core replaces its own rows rather
    # than duplicating them — which matters precisely because `obs_node` DECLARES NO KEY and a
    # second insert would otherwise DUPLICATE rather than conflict.
    #
    # ⚑⚑ AND THE STAGE BOUNDARY IS OBSERVABLE IN THE STORE TODAY, which is how I know it is a
    # real state rather than a hypothetical one: `--sample _unit 3` returns rows whose `file_id`
    # is `Algebra/F2/F2Cases.agdai` and `.../Hilbert2DContinuous.agdai` — two cores `--packed`
    # reports DRAINED. Their unit tier survived while their staged side did not. Mixed-stage
    # states EXIST here; before this cut they were simply unreadable.
    con.commit()

    # units + per-unit membership (reach from root over the acyclic raw edges — pre-sharing, no closure)
    # + the codomain HEAD of each unit's type (structural, computed on the unambiguous per-core tree).
    # ⚑⚑⚑ ⟡a3-route-pack-only — THIS STAGE NOW LIVES IN `build_units`, AND A2 CALLS IT. It was
    # inline here, which made it reachable only by taking A2's corpus-wide reads with it; the A3
    # path needs the same stage without them. One implementation, two callers — a second copy
    # here is the "one capability, three copies, four omissions" defect this repo keeps paying.
    # The comments recording WHY each line is the way it is moved with the code.
    return _finish_project(con, core_id, pack, cod, ch, additive)


def _finish_project(con, core_id, pack, cod, ch, additive):
    """Stage 3 + the stats read — A2's tail, shared with the A3 route.

    ⚑ THE COUNTS COME FROM THE STORE, NOT FROM THIS PASS'S PYTHON LISTS. `len(urows)` equals
    the store total ONLY when the destination was dropped first; under `additive=True` it is
    this pass's delta and the CLI prints it as a total. Reading the relation is identical on
    the destructive path and honest on both.

    ⚑⚑ ONE STATEMENT, ONE SNAPSHOT (⟡view-purge, corrected). This was FOUR `_schema.scalar`
    calls — `_node` counted at one moment, `_unit` at another, `shared_subtree` at a third —
    so the tuple reported a store state that never existed. `q_project_stats` pushes the
    fragment INSIDE the statement.

    ⚑ `[0]` AND NOT `.fetchone()`, WHICH IS A DEFECT IN `_rows_of`'s OWN DOCSTRING RATHER THAN
    A STYLE CHOICE: it claims *"callers here do … `.fetchone()`"* while RETURNING A PLAIN LIST,
    which has no such method. A docstring naming a caller is a hypothesis.
    """
    build_units(con, core_id, pack, cod, ch, additive)
    return tuple(QB.run(con, "project_stats")[0])


# ⚑ `ORBIT_SCHEMA` REMOVED 2026-08-23 with the tier. It was already a DEAD STRING — nothing
# executed it (the projection called `_schema.apply(con, only="orbit")` against the synthesized
# declaration instead) — but a dead string is still a SECOND SPELLING, which is exactly the
# rival-definition hazard the note above `SPPF_SCHEMA` records. Deleting the tier while leaving
# its DDL blob behind would have kept the drift surface without the tier.


# ⚑⚑ `project_orbit_sppf` REMOVED 2026-08-23 (operator: *"We can erase orbit_node, too. It's
# obsolete now that we have the compound-identity framing."*). It was ⟡rig ORBIT interning —
# a second projection over the same events, keying nodes by their ORBIT under the rig group
# (commutativity = sort the child symbols, associativity = flatten nested same-op children)
# and writing `orbit_node`/`orbit_child`/`orbit_member` alongside the positional `_node`.
#
# ⚑ THE ORBIT KEY WAS AN ATTEMPT AT COMPOUND IDENTITY, which is why the framing supersedes it
# rather than merely outliving it: `opk = _b64(head ‖ canonical child symbols)` compressed
# "this node up to the rig action" into ONE opaque string. Answering identity by composing
# the parts directly is what makes the encoded form unnecessary.
#
# ⚑⚑ TWO FINDINGS FROM ITS BODY THAT OUTLIVE IT, kept because both were measured and both
# generalise beyond this function:
#
#   1. THE ONE GENUINE RECURSION IN EITHER PROJECTION WAS `canon_syms`, NOT `pack`. An audit
#      ranked `pack()` as "a memoized bottom-up hash… awkward as a CTE" — but `pack` is
#      depth-1 and never self-calls, while `canon_syms` really did recurse (flattening nested
#      same-op children under an associative law). **The difficulty was asserted about the
#      wrong function**, on structure alone.
#   2. AND IT WAS STILL EXPRESSIBLE IN SQL — PROBED, NOT ARGUED. A `WITH RECURSIVE` joining on
#      `op = parent.op AND assoc` is the flatten; `string_agg(leaf, ',' ORDER BY leaf)` vs
#      `ORDER BY path` is exactly `sorted(out) if law.commutative else out`. Verified on the
#      sandbox: `canon = 'c,d,e'` vs `positional = 'e,d,c'` — the two DIFFER, so the probe
#      discriminated rather than passing vacuously.
#
# ⚑ `RIG_OPS` and `_opname` survive elsewhere if still referenced; the rig laws are not what
# was retired here — the second keying of the node table is.


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
        _schema.execute(con, f"DROP TABLE IF EXISTS {t}")
    _schema.apply(con, only="argperm")  # synthesized; ARGPERM_SCHEMA is retired below
    ctx = G.Ctx(con)
    uid = {nm: u for u, nm in QB.run(con, "argperm_uid")}
    defs = []  # (name, k=(tkey,gid), residue_repr, stab)
    for name in ctx.idx:
        if filt and filt not in name:
            continue
        k = G.orbit_key(ctx, name)  # (type-orbit key, graded HANDLE gid)
        leh, stab = ctx.resid.get(name, ((), 1))  # the coset element (Lehmer) + |Stab|
        if name in uid:
            defs.append((name, k, repr(leh), stab))
    # ⟡orbit-def-by-reference: persist the graded-orbit DAG by REFERENCE; graded_key = the interner's int
    # handle str(root gid) — a BOUNDED, within-build-consistent content-address (consumers only compare
    # graded_key for equality within one build). node/child rows carry the DAG + fanin (breadth).
    node_rows, child_rows = G.dump_graded(ctx)
    orbit_rows = [
        (uid[name], _b64(repr(k[0])), str(k[1]), leh, stab) for (name, k, leh, stab) in defs
    ]
    member_rows = [(str(k[1]), uid[name]) for (name, k, _, _) in defs]
    _schema.upsert(con, "_orbit_def", orbit_rows)
    _schema.upsert(con, "graded_orbit_node", node_rows)
    _schema.upsert(con, "graded_orbit_child", child_rows)
    _schema.upsert(con, "graded_orbit_member", member_rows)
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
        rel = rel[: -len(".agda")] + ".agdai"
    return os.path.join(base, rel)


def _require_mutation_stated(label):
    """REFUSE unless the invocation states `--dry-run` or `--apply` — never a default.

    ⚑⚑ THE TENANT AXIS HAS A RESOLVER AND THE MUTATION AXIS DID NOT (operator, 2026-08-21:
    *"I don't want anything dry by default, I don't want anything apply by default. I don't
    want anything --live by default, I don't want anything --sandbox by default. I want dry
    or apply, sandbox or live, explicitly stated on the command line."*). `store.tenant`
    already refuses an unstated tenant; this is its twin, and the two together are the rule.

    ⚑ THE DECLARED CONVENTION ALREADY SAID SO, AND 40 TOOLS DID NOT IMPLEMENT IT.
    `toolmodes --conventions`: *"--apply: MUTUALLY EXCLUSIVE WITH --dry-run AND ONE IS
    REQUIRED: a mutating tool invoked with NEITHER must REFUSE, never guess."* Measured the
    same day: 34 tools take only `--apply`, 2 only `--dry-run`, 1 both — *"40 half-paired
    tool(s), each still has a silent default."* A convention declared and unenforced is a
    resolution, which is the shape this repo converts into a ratchet.

    ⚑ HOMED HERE, NOT COPIED INTO THREE DISPATCHES. `--ingest-core`, `--promote-core` and
    `--drain-core` are the make-driven writers and all three already share this function as
    their prologue. Three copies of one guard is the *"FOUR gates route through
    ratchet.set_ratchet and none can enumerate its census"* defect, one layer down.

    ⚑ THE SAFE BRANCH IS STILL A CHOICE. It is tempting to let `--dry-run` be the default
    because it changes nothing — but the danger a default creates is not that the silent
    branch is destructive, it is that THE CHOICE STOPS BEING MADE. `store.tenant`'s note
    puts it exactly: *"forgetting to care is indistinguishable from choosing."*
    """
    import sys as _sys

    _apply = "--apply" in _sys.argv
    _dry = "--dry-run" in _sys.argv
    if _apply and _dry:
        print(
            "⚑ %s: BOTH --apply and --dry-run given — mutually exclusive. Refusing "
            "rather than picking one." % label,
            file=_sys.stderr,
        )
        _sys.exit(2)
    if not _apply and not _dry:
        print(
            "⚑ %s: neither --dry-run nor --apply was given.\n"
            "  This mode WRITES to the tenant it names; state which.\n"
            "    --dry-run  report what WOULD change and change nothing\n"
            "    --apply    perform it" % label,
            file=_sys.stderr,
        )
        _sys.exit(2)
    return _apply


def _core_id_for_path(path, label):
    """`(core_id, con)` for the core a PATH names — the make-driven modes' shared prologue.

    ⚑⚑ ONE SPELLING, BECAUSE IT IS ONE FACT ASKED BY THREE MODES. `--promote-core` and
    `--drain-core` both take a `.agdai` path from a make recipe and need the core id the store
    knows it by; written twice, the join and the not-yet-ingested branch would be two answers to
    *"which id has this path"*, free to drift. That is the defect `_live_cores` was homed for one
    layer down, and `_delete_core_rows` before it.

    ⚑ THE ID IS THE TERM ID OF THE RELPATH, read from `core_fp ⋈ terms` — the same join
    `--packed`, `finalize_db`'s prune, and the Set₁ gate's completeness guard use. There is no
    `core_fp.path` column; recomputing a base64 encoding here would invent a second home for a
    fact the interner already owns.

    ⚑⚑ RETURNS `(None, con)` FOR BOTH ABSENCES, AND THE CALLER EXITS 0 — deliberately, because
    neither is a failure. A core not built yet has no `.agdai`; a core not ingested yet has no
    `core_fp` row. Both are ORDERING facts that make's own dependency edge resolves: no stamp is
    written, so the next build retries once the prerequisite lands. Exiting non-zero would fail
    a build over a race the DAG already handles.

    ⚑ THE CONNECTION COMES BACK BECAUSE THE CALLER WRITES THROUGH IT. Opening a second one to do
    the work would put the lookup and the write in different transactions, so a core could be
    ingested-then-pruned between them and the write would target an id the store no longer has.
    """
    _require_mutation_stated(label)
    _base = substrate_core_root(os.path.join(_ROOT, "agda"))
    # ⚑⚑ THE LABEL NAMES THE MODULE, NOT JUST THE MODE, AND THAT IS WHAT MAKES THE BACKEND
    # ATTRIBUTABLE. `store.connect` publishes this as `application_name`, so a label of
    # `"sppf_db --promote-core"` alone would make five concurrent promoters five backends
    # with one identical name — the mode is what they SHARE, so it is exactly the half that
    # cannot distinguish them. MEASURED 2026-08-23: five promoters ran 1–3.5h and could be
    # told apart only by matching bound-parameter SQL text by eye.
    #
    # ⚑ BEST-EFFORT, AND IT FALLS BACK TO THE BARE MODE. This is a diagnostic name; a path
    # that will not resolve is a fact for `_core_id_over` to report through its own two
    # None-branches, never a reason to fail the promote before it starts.
    _lbl = label
    try:
        _c = _resolve_core(path, _base)
        if os.path.exists(_c):
            _lbl = "%s %s" % (label, os.path.relpath(_c, _base))
    except Exception:
        pass
    con = _store.tenant(mode="rw", label=_lbl)
    return _core_id_over(
        path,
        _base,
        lambda rel: _schema.scalar(
            con,
            "SELECT f.core_id FROM core_fp f JOIN terms t ON t.term_id = f.core_id "
            "WHERE t.text = %s" % _schema.ph(),
            (rel,),
        ),
    ), con


def _core_id_over(path, base, lookup):
    """The JUDGEMENT half of `_core_id_for_path`, over an injected `relpath → core_id`.

    ⚑⚑ SPLIT OUT FOR THE REASON `_reconcile_over` RECORDS: *"a case that had to stand up
    postgres to check a filename comparison would be testing the fixture."* Both of this
    function's branches are ORDERING facts a build routinely hits — a module compiled but not
    yet ingested, a module whose `.agdai` has not been written — and both return `None`, which
    the callers turn into a silent `exit 0`. A silent exit is exactly what must be driven by a
    case rather than discovered.

    ⚑⚑⚑ AND I DISCOVERED ONE BY ACCIDENT, WHICH IS WHY THIS EXISTS. `--drain-core` on
    `Acyclic.agdai` did nothing and reported nothing; I noticed only because the core failed to
    appear in `--packed`. The behaviour was CORRECT — the reconciler had deleted that module's
    `.ingested` stamp, so there was no `core_fp` row and no id — but "correct behaviour I
    confirmed by noticing an absence elsewhere" is not verification, and the next such exit
    might be a genuine defect wearing the same silence.

    ⚑ THE `lookup` IS A CALLABLE, NOT A DICT, because the real one is a per-path query and a
    dict would invite the caller to pre-enumerate `core_fp` — a corpus read to answer about one
    path, the shape `--holes` and the `.drained` reconciler both record avoiding.
    """
    core = _resolve_core(path, base)
    if not os.path.exists(core):
        return None  # not compiled yet — make's DAG resolves it
    return lookup(os.path.relpath(core, base))  # None ⟹ not ingested yet — likewise


def ingest_core(path, base=None, force=False, sandbox=False):
    """⟡gqs-make-targets: ingest ONE core. WAL + busy_timeout so parallel `make ingest` jobs SERIALIZE their
    cheap writes on the lock (parallel DECODE, serialized INSERT) instead of failing 'database is locked'.
    Self-skips via core_fp (the agda-self-skip analogue). NO finalize — prune/GC/path_text/project are the
    once-after-sweep finalize_db step. `path` may be the .agdai core OR its .agda source (resolved to the core).

    ⚑ `sandbox=True` INGESTS INTO THE THROWAWAY TENANT — the missing half of a split the
    store already had (user, 2026-08-07: *"you have the sandbox db to work with… you might
    need to fix the split between the query builder and the rest of the code"*). MEASURED:
    `store.sandbox_connect` exists and has exactly ONE caller (`schema.probe`), while every
    ingest path hardcodes `_store.connect()` — so a decode change could be validated only
    against the LIVE store, or by `build(full=True)` dropping 6.3M obs + 6.3M edge + 2.1M
    event to re-check one core.

    ⚑ THAT IS THE SAME SHAPE AS THE sqlite/postgres SPLIT: the capability is built, one
    consumer uses it, and the rest are wired past it — so the safe route is unreachable and
    the expensive one is the only one on offer. A capability bound reads as a safety property
    until you notice nothing can reach the safe path.

    ⚑ AND IT IS A PARAMETER HERE WHILE `store` KEEPS TWO ENTRY POINTS, DELIBERATELY.
    `sandbox_connect`'s docstring argues a `connect(sandbox=True)` flag would put the real
    store one boolean from a mutating probe — correct, and preserved: this passes the CHOICE
    down to the same two distinct entry points rather than collapsing them.
    """
    base = base or substrate_core_root(os.path.join(_ROOT, "agda"))
    core = _resolve_core(path, base)
    if not os.path.exists(core):
        return  # not built yet — nothing to ingest
    con = (
        _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="rw", require=False)
    )
    had = "unit_obs" in _schema.relations(con)  # was `table_exists` + .fetchone()
    if had and not _schema_current(
        con
    ):  # a pre-existing STALE-schema DB → --init/--full must migrate
        con.close()
        sys.exit(
            # ⚑⚑⚑ THIS MESSAGE USED TO READ: "catalog.db schema is stale — run
            # `sppf_db.py --init` (or --full) first". BOTH HALVES WERE WRONG BY 2026-08-27.
            # (1) `catalog.db` is the SQLITE store; this code path connects to POSTGRES —
            #     a stale string that sent two readers hunting the wrong database.
            # (2) `--init` was the DESTRUCTIVE repair: `init_db` DROPPED six relations on
            #     every call. The documented fix for a blocked ingest was data loss. It is
            #     now POISONED and refuses; see its docstring.
            # ⚑ AND "STALE" WAS ITSELF A MISREAD: `_schema_current` consults the RETIRED
            # `schema_version` table, which is empty, so it is permanently False. An EMPTY
            # store with a materialized schema reads as "pre-existing AND stale" — a third
            # state the guard does not model (ABSENT vs BROKEN vs EMPTY, collapsed).
            "sppf_db --ingest-core: refusing — the `schema_version` currency check is "
            "RETIRED and always reports stale.\n"
            "  Do NOT run `--init`: it is poisoned because it DROPPED event, obs, edge, "
            "unit_obs, unit_member, core_fp.\n"
            "  The intended model is the ⟡ladder, whose ingest is `--ingest-source` "
            "(core_decoded.dec jsonb), not this event-tier path.\n"
            "  Establish a tier with:  python3 jea/metalanguage/schema.py --establish "
            "<tier> --apply --live"
        )
    # ⚑⚑ DDL ONLY WHEN THE SCHEMA IS ABSENT — THIS RAN UNCONDITIONALLY AND WAS THE
    # DEADLOCK'S AMPLIFIER. `apply()` re-issues the whole `CREATE UNIQUE INDEX IF
    # NOT EXISTS` suite, and **`IF NOT EXISTS` still takes the ShareLock before it
    # can discover the index already exists.** Under `make -j` that is one
    # `ShareLock on terms` per module — 3,566 of them — to do nothing.
    #
    # ⚑ MEASURED on a live run: 13 backends lock-waiting, **11 of them queued on
    # `ShareLock on terms` running the identical `CREATE UNIQUE INDEX IF NOT EXISTS
    # ix_terms_text`.** That queue is not itself the cycle (postgres proves a cycle
    # before raising `DeadlockDetected`), but it is what turned a narrow two-lock
    # inversion into dozens of failures per build. Operator's read — *"is it really
    # a deadlock, or just a pileup?"* — was right that the pileup does the visible
    # damage; the inversion is the fault and the DDL storm is the amplifier.
    #
    # ⚑ `had` IS ALREADY COMPUTED TWO LINES UP, so the guard costs nothing. The
    # sequencing this restores is already named in `init_db`'s own docstring
    # (:1571) — create the schema ONCE, *"before the parallel `make ingest` sweep
    # (so no ingest job races the initial CREATE)"*. `ingest_core` simply never
    # relied on it.
    #
    # ⚑⚑⚑ AND THE GUARD IS CHECK-THEN-ACT, WHICH IS THE DEFECT ONE LAYER IN (⟡ddl-is-a-write,
    # 2026-08-24). `require_indexes`' docstring names this site as one *"that never got the
    # fix"* — half right, and the half it got wrong is the interesting one. A guard DID land
    # here, so the DDL storm is gone; but `if not had:` READS the catalogue and then WRITES
    # DDL on the strength of that read, with no lock held between the two. Under `make -j`
    # two workers can both observe `had == False` and both enter `apply()` — the narrow
    # residue of the very race the guard was written to close. The rule is ASSERT, not
    # guard-then-create: a per-core writer states its precondition and bails.
    #
    # ⚑ UNCONDITIONAL, AND DROPPING THE `if not had` IS THE POINT. Under the guard the two
    # states were "tier present → do nothing" and "tier absent → create it"; under the
    # assertion they are "present → proceed" and "absent → REFUSE naming `--establish`".
    # The `had` read still earns its place two lines up (the stale-schema branch reads it),
    # but it no longer gates a write, so there is no read-then-write window left to race.
    _schema.require_indexes(con, "event", label="ingest_core")
    if not _schema_current(con):  # fresh DB → stamp the current version (idempotent under -j)
        _set_schema_version(con)
    con.commit()
    # ⚑ THROUGH THE STORE'S OWN INTERNER (ⓝ P4), NOT `_b64(relpath)`. A surrogate `core_id`
    # carries no path, so minting one is a WRITE against `core_fp` — and `core_id_for` makes
    # that write idempotent via `ix_corefp_path`, which matters here specifically because
    # `make ingest -j` runs this function concurrently across cores.
    relpath = os.path.relpath(core, base)
    core_id = _schema.core_id_for(relpath, con)
    try:
        mtime = _core_ver(core)
    except OSError:
        con.close()
        return
    # ⚑ `QB.run` MATERIALISES TODAY AND SHOULD NOT — it must YIELD. `_rows_of`'s docstring
    # says "NOT A GENERATOR, DELIBERATELY", justified by callers that use `.fetchone()` or
    # re-read. This site is one of those callers, and it RAISED `AttributeError` — so the
    # justification is self-refuting: the convention it protects was already broken here,
    # and nobody noticed because `--ingest-core` is a mode no full-corpus run exercises.
    #
    # Consuming just the FIRST row is the shape that works under either contract, so this
    # call site stops depending on materialisation. Converting `_rows_of` itself to a
    # generator is the real fix (⟡qinfra-yield) and belongs with the other ~37 sites, not
    # smuggled in here — but nothing above needs a list.
    # ⚑ `force` EXISTS BECAUSE THE SKIP IS KEYED ON THE SOURCE, NOT THE DECODER. mtime asks
    # "did the .agdai change?" — the right question when the DECODER is fixed. It is the
    # WRONG question after a shim/decode change that alters the output from unchanged bytes,
    # which `write_events`' own docstring already names as the `full=True` case:
    # *"a shim/Agda toolchain change that alters decode WITHOUT changing .agdai bytes+mtime"*.
    #
    # ⚑ AND UNTIL NOW THE ONLY ANSWER WAS `full=True`, WHICH DROPS THE ENTIRE EVENT TIER —
    # 6.3M obs + 6.3M edge + 2.1M event — to re-verify ONE core's decode. That is a
    # capability bound masquerading as a safety property: no way to ask the cheap question,
    # so the expensive one is the only route, and a per-core check becomes unaffordable.
    # `recover_fields` (the v2 field recovery) is exactly this shape: same bytes, different
    # decode.
    if not force:
        for row in QB.run(con, "core_fp_mtime", core_id=core_id):
            if row[0] == mtime:
                con.close()
                return  # self-skip: mtime unadvanced (agda-self-skip analogue)
            break  # one row is all this key can return; do not drain
    _delete_core_rows(con, [core_id])
    con.commit()  # re-ingest: drop this core's old rows
    tid, pid = _mk_interners(con)
    # ⚑⚑ THE VERDICT WAS DISCARDED HERE, AND THAT IS WHAT MADE AN UNDECODABLE CORE A SILENT
    # SUCCESS (⒯, 2026-08-14). `_decode_insert_core` has ALWAYS returned `(ingested, reason)`
    # with `reason` the TYPED decode failure — this call threw both away, so
    # `--ingest-core <an-undecodable-core>` printed nothing and exited 0. MEASURED before the
    # change on `Algebra/CayleyDickson/Grade/Shuffle.agdai` (a real `decode-nothing` core):
    # no output, exit 0. A build wired to that recipe would have gone green over a core that
    # contributes nothing to the SPPF.
    #
    # ⚑ IT RETURNS THE REASON RATHER THAN EXITING, because the CLI is where branching belongs
    # (--control): the rung reports, the caller decides. `converge` and the batched engine
    # already treat an undecodable core as a bounded skip, and lifting a `sys.exit` in here
    # would change THEIR behaviour too — this widens what the function SAYS, not what it does.
    _ingested, _reason = _decode_insert_core(con, core, relpath, mtime, tid, pid)
    con.commit()
    con.close()
    return _reason


def init_db():
    """⚑⚑⚑ POISONED 2026-08-27 — REFUSES. This DROPPED SIX RELATIONS, UNCONDITIONALLY.

    ⚑ IT IS ALSO WHAT THE ERROR MESSAGE TELLS YOU TO RUN. `ingest_core` exits with
    *"catalog.db schema is stale — run `sppf_db.py --init` (or --full) first"*, so the
    documented repair for a blocked ingest was a six-table DROP. That is why this refuses
    rather than merely being deleted: **the caller that names it still exists**, and a
    missing function would raise a NameError far from the reason.

    ⚑⚑ WHY THE DROP BECAME UNCONDITIONAL — a retired mechanism with a live consumer.
    The guard was `if not _schema_current(con)`, and `_schema_current` is
    `schema_version(con) == SCHEMA_VERSION`. `schema_version` is RETIRED (operator,
    2026-08-27: *"We're not supposed to be using schema_version any more"*), so the table
    is EMPTY, so the read returns None, so the comparison is **permanently False** — and
    the migration branch fires on EVERY invocation. Nothing announced this; the mechanism
    was stranded by the model move, not retired by an act, and no turn in the record
    decides it (transcript sweep, 2026-08-27).

    ⚑ AND THE DROP WAS CORRECT WHEN WRITTEN, FOR A STORE THAT NO LONGER EXISTS. It dates
    to the sqlite era, when "the store" was a `catalog.db` FILE you could copy aside before
    a migration — and that is exactly what was done (`catalog/catalog.db.pre-producer`, a
    filesystem copy). Against a live postgres tenant there is no copy and no undo. **The
    premise is gone and the code did not know it.**

    ⚑ THE MODEL MOVED PAST IT ANYWAY. The intended pipeline is the ⟡ladder
    (`core_decoded.dec jsonb` → `dec_scalar` → `dec_node`/`dec_root`); the six relations
    this dropped belong to the event tier the ladder REPLACES. Operator: *"All the existing
    db structure is cognitive debt"* — repairing a writer inside a replaced relation is
    debt maintenance, not progress.

    ⚑ TO ESTABLISH A TIER, use the path that ASSERTS rather than creates:
        python3 jea/metalanguage/schema.py --establish <tier> --apply --live
    That is how `sourced` was established on 2026-08-27 (`CREATED core_decoded`), after
    which `--ingest-source` ran first try. One CREATE, no DROP, no migration.
    """
    raise RuntimeError(
        "sppf_db.init_db is POISONED — it DROPPED event, obs, edge, unit_obs, "
        "unit_member, core_fp on EVERY call (its `_schema_current` guard reads the "
        "RETIRED `schema_version` table, so it is permanently False).\n"
        "  It was written for a copyable sqlite catalog.db; against live postgres there "
        "is no undo.\n"
        "  To establish a tier:  python3 jea/metalanguage/schema.py --establish <tier> "
        "--apply --live\n"
        "  The intended model is the ⟡ladder (core_decoded.dec jsonb), not the event "
        "tier this function serviced — see ~/.claude/plans/ladder-model.md."
    )


def project_ref_only(sandbox=False):
    """Build ONLY the ref index — the cheap, idempotent, disposable projection.

    ⚑ A SEPARATE ENTRY POINT BECAUSE `--finalize` IS NOT CHEAP. It prunes, GCs, dedups and
    re-projects the whole SPPF; rebuilding a derived index should not require any of that.
    And `ref` is precisely the thing that SHOULD be rebuildable on demand — it carries no
    fact of its own, so a rebuild costs one query and risks nothing.
    """
    con = (
        _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="rw", require=False)
    )
    n = project_ref(con)
    con.close()
    return n


# ⚑⚑⚑ ⟡finalize-retire — `finalize_db` WAS DELETED HERE (2026-08-22), MODE AND DISPATCH TOGETHER.
# It was one of the earliest db-ingestion attempts and *"intrinsically wide, deep and atomic: the
# worst possible granularity"* (operator): ONE call globbed the corpus, pruned, GC'd, deduped,
# refreshed `path_text`, and ran the A2 fold plus two more projections over the WHOLE store.
#
# ⚑⚑ IT WAS DELETED FOR EXISTING, NOT FOR COSTING (operator: *"because it EXISTS, LLMs keep
# thinking it's legitimate, and keep leaning on it one way or another"*). MEASURED in the session
# that removed it: I cited it TWICE as a legitimate caller while reasoning about lock granularity,
# and quoted its own docstring — *"the ONCE-after-ingest-sweep tail"* — as evidence for a
# scheduling claim. A superseded entry point that still dispatches reads as sanctioned design, and
# a warning comment governs only the reader already looking at it. Removal is the only form that
# reaches the reader who is not.
#
# ⚑ EVERY CAPABILITY HAD A LIVE PER-CORE HOME, established by call-site census before deleting:
#     the glob-and-prune   → `ingest_core` prunes ONE core via `_delete_core_rows`, incrementally
#     `path_text` refresh  → `_mk_interners` writes it AT INTERN TIME (a rebuild that reassigns
#                            surrogate ids would ORPHAN every reference to them)
#     the unscoped A2 fold → the five-link chain's `.promoted`, per core, per level, per window
#     argperm projection   → `build` also calls it
# The GC and the path_seg dedup are corpus sweeps with no per-core twin; they were never
# `finalize`'s to own and remain reachable where they are defined.
#
# ⚑ THE LIVE PATH IS `make -C agda -f Flat.mk -k -j <N> promote` — `<Mod>.agdai → .ingested →
# .promoted → .drained`, committing per core, per level, and per 25k-row window, with a derivable
# resumption predicate at every boundary. That is the ⟡project-granularity arc; this function was
# the state it existed to undo.


def build(
    cores,
    base=None,
    orbit=False,
    distribute=False,
    argperm=False,
    prune=True,
    producer="agdai",
    sandbox=False,
):
    """⚑ `sandbox=True` RUNS THE WHOLE CHAIN AGAINST THE THROWAWAY TENANT. `ingest_core`
    gained this when a single core's decode needed verifying; `build` — the path that ingests
    a FILTERED SET and then projects — did not, so the only way to exercise the full
    ingest→project→drain chain was against the corpus.

    ⚑ THAT IS THE GAP THAT MAKES A REHEARSAL IMPOSSIBLE. The full run drops the event tier
    (`full=True`, forced by the ekey change), so its first execution is also the moment the
    existing 168 cores go away. A rehearsal on a filtered subset is what converts three
    untested assumptions — that `build` works on postgres since the paramstyle fix, that
    `project_ref` populates from a real ingest, that the drain runs concurrently — into
    measurements. It could not be run without this parameter.
    """
    base = base or substrate_core_root(os.path.join(_ROOT, "agda"))
    # ⚑ THE CONNECTION MUST CARRY THE BACKEND, and this line did not. A raw
    # `sqlite3.connect` here while `SUBSTRATE_STORE=postgres` gave every downstream
    # helper a sqlite cursor to run postgres SQL against — `relations()` dispatched on
    # the env var and issued `SELECT … FROM information_schema.tables`, which sqlite
    # answered with "no such table". THIRD occurrence of this exact shape today
    # (`set1_ratchet_cores._freshen`, `_freshen`'s second connect, now here).
    #
    # ⚑ AND MY CENSUS CANNOT SEE IT. `--portable` reads SQL LITERALS; a connection call
    # carries no SQL, so `sppf_db` measured 0 blocking sites while still being unable to
    # reach postgres at all. A clean census is not a working port — the instrument
    # answers the question it asks, and "which connections carry a backend" is a
    # different question from "which statements are portable".
    #
    # ⚑⚑ AND THAT SAME BLIND SPOT IS WHY THE `catalog_db` PARAMETER OUTLIVED ITS CALLER.
    # The retired note here read *"retained as a parameter because the verifier passes
    # throwaway paths; when it names the live store, the authority resolves the backend"*
    # — a THREE-WAY conditional whose sqlite arm was reachable from exactly one function
    # (`verify_incremental`, now retired ★ⓢ). Every other caller passed the default, so
    # the sentinel test `catalog_db in (None, CATALOG_DB)` was always true and the arm
    # after it was already dead. Deleting the parameter is what makes that legible;
    # leaving it would have kept a `sqlite3.connect` one argument away from the ingest
    # path, which is the same one-boolean-from-the-wrong-store shape `store` keeps
    # `connect`/`sandbox_connect` separate to prevent.
    con = (
        _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="rw", require=False)
    )
    # P1: append-only events (source of truth). `producer` scopes the prune to this
    # tier — see core_fp's schema note; without it a second producer's ingest deletes
    # the first's rows wholesale.
    # ⚑ `full=` DROPPED FROM THIS CALL (⟡no-automated-drop) — the parameter's only effect was
    # the six-table drop that is now gone, so passing it would thread a dead argument through
    # the ingest path and keep the flag looking meaningful at the CLI.
    write_events(cores, con, base, prune=prune, producer=producer)
    stats = project_sppf(con)  # P2: the positional SPPF, DERIVED from events
    if argperm:
        project_argperm(con)  # ⟡argperm: the per-def GRADED orbit-key (additive)
    # ⚑ `if orbit: project_orbit_sppf(...)` REMOVED 2026-08-23 — the orbit tier is gone,
    # superseded by the compound-identity framing. `orbit`/`distribute` remain as accepted-
    # and-inert CLI flags rather than being deleted from every signature in one edit; that
    # sweep is its own change (the `back=` parameter in `store.dsn` is the recorded precedent
    # for retaining a dead argument explicitly rather than half-removing it).
    # ⚑ AND `project_ref` WAS MISSING FROM THIS PATH, WHICH IS THE SAME DEFECT AGAIN, ONE
    # PROJECTION LATER. I added it to `finalize_db` and not to `build` — so the 98-core
    # sandbox rehearsal ingested 30 cores, projected the SPPF, and left `ref` holding the
    # STALE two-core data from an earlier per-core test. MEASURED: `obs` covered 30 cores
    # while `ref` covered 2; rebuilding it standalone took 1,800 → 8,497 rows over 30 cores.
    #
    # ⚑ IT READ AS SUCCESS, WHICH IS WHY THIS MATTERS. `ref` was non-empty and internally
    # consistent — it simply described a different corpus than the store did. The comment
    # directly above recorded the identical shape for `_advance_projection` ("`gen_catalog`
    # had the call and `build` did not"), so this is the second occurrence of one defect in
    # one function: a projection wired into the finalize path and not into the build path.
    # `_advance_projection` is retired (2026-08-12); the DEFECT CLASS it exemplified is not,
    # which is why the citation is kept and this case is still driven in `_selftest`.
    project_ref(con)
    con.close()
    return stats


def tier_census(con):
    """The three staged relations and the two durable ones, in one read — the CURVE's sample.

    ⚑ THE DELIVERABLE IS THE SERIES, NOT THE FINAL STATE. "Does tier 0 accumulate the whole
    corpus before anything drains" is a question about a SHAPE OVER TIME, and a census taken
    once at the end cannot answer it: fill-then-drain and drain-as-you-fill agree exactly on
    the end state and disagree on every point before it. So the loop samples after EVERY
    unit and the numbers are the evidence.
    """
    return {
        t: _schema.scalar(con, "SELECT count(*) FROM %s" % t)
        for t in ("obs", "edge", "event", "_node", "obs_node")
    }


def _ingested_relpaths(con):
    """The relpaths the store has already ingested — read from `terms ⋈ core_fp`, never held.

    ⚑ THIS IS WHAT MAKES THE LOOP RESUMABLE, and holding it in Python is what would break
    that. `core_fp` IS the ingest's cursor: a core with a fingerprint row has been observed.
    Deriving the remaining work from the store on every pass means killing the process
    mid-loop loses nothing and a restart continues where it stopped — an interruption is a
    NON-EVENT rather than a state you have to reconstruct. A Python list of "cores still to
    do" is a second cursor that dies with the process.

    ⚑ THE MAP IS `terms ⋈ core_fp`, NOT A `core_fp.path` COLUMN — the same join
    `finalize_db`'s prune uses, for the same reason: a core's id IS the term id of its
    relpath, so the path is recovered from the ONE place it is stored.
    """
    return {
        r["text"]
        for r in _schema.rows(
            con, "SELECT t.text FROM core_fp f JOIN terms t ON t.term_id = f.core_id"
        )
    }


def work_promote(con):
    """Is anything staged but NOT yet addressed by the durable tier? — the promote's RESIDUE.

    ⚑⚑ THE WORK PREDICATE AND THE WORK ARE THE SAME SET, which is the property an incremental
    promote buys and a DROP-and-rebuild cannot have. `INSERT INTO tier_{N+1} SELECT … WHERE
    NOT EXISTS (…)` is non-empty exactly when there is something to promote, so "is there work
    at this tier?" is that statement with the write removed. A destructive refresh has no such
    predicate: it ALWAYS has work, because it always rebuilds everything — which is why the
    loop is impossible until the promote is incremental, and why F8 is the precondition rather
    than a parallel item.

    ⚑ A BOOLEAN, NOT A COUNT, AND `EXISTS` IS WHAT MAKES IT CHEAP. The residue's SIZE is never
    asked — only whether it is empty — so postgres may stop at the first row instead of
    scanning the anti-join to completion. `Substrate.Lifecycle.Residue`'s *"a residue of zero
    is an actor fully caught up"* is a predicate, and asking it as `count(*) > 0` would pay
    for an arithmetic fact nothing reads.

    ⚑ AND IT IS `q_drainable`'s OWN `unprojected` CONJUNCT, not a fourth spelling of it. The
    retire licence already asks "is every observation of this core addressed"; the promote
    asks the same question with the core-grouping removed. One relation, one anti-join.
    """
    if "obs_node" not in _schema.relations(con):
        return bool(_schema.scalar(con, "SELECT EXISTS (SELECT 1 FROM obs)"))
    return bool(
        _schema.scalar(
            con,
            "SELECT EXISTS (SELECT 1 FROM obs o LEFT JOIN obs_node n "
            "ON n.core_id = o.core_id AND n.local_id = o.local_id "
            "WHERE n.core_id IS NULL)",
        )
    )


def work_retire(con):
    """Does the licence admit any core? — the retire's RESIDUE, asked without doing it.

    ⚑ THE LICENCE ITSELF IS THE PREDICATE, wrapped in `EXISTS`. `q_drainable_res` is a set of
    core ids; a cheaper approximation of it would be a SECOND licence to keep in step with the
    first, which is the defect `q_drainable` exists to end. So this asks the compiled
    conjunction whether it is inhabited, and nothing else.

    ⚑ NO FLOOR IS COMPUTED, SO NO PIN CAN HOLD THIS AT ZERO. The positional form asked
    `MIN(lwm)` over the registry and got 0 while a pin was registered — measured on both
    stores as a full tier with `0 observation(s) below the floor`. The residue form has no
    floor to be held at.
    """
    if "obs_node" not in _schema.relations(con):
        return False
    import query_builders as _QB

    _sql, _d = _QB.SQL["drainable_res"]
    return bool(_schema.scalar(con, "SELECT EXISTS (%s)" % _sql, dict(_d)))


# ⚑ `converge_order` / `_SIDES` LIVE IN `lifecycle`, NOT HERE, AND THAT IS THE RIGHT HOME.
# They were written here first and the module cap said so (1203 code lines against a 1200 cap)
# — but the cap only made someone look. Ordering ACTORS across the chain's boundaries is what
# `drain_order` / `drains_before` already are; a second module deciding what a boundary name
# means would be the derived-view drift this whole change is removing. `sppf_db` declares its
# roster and asks the chain's owner where each entry sits: `lifecycle.service_order`.


def converge(
    cores,
    base=None,
    sandbox=False,
    producer="agdai",
    max_steps=100000,
    report=None,
    shards=1,
    shard=0,
):
    """Drive the store to a FIXPOINT, downstream-first, one bounded unit at a time.

    ⚑⚑⚑ `shards`/`shard` PARTITION THE PROMOTE ONLY, AND THAT ASYMMETRY IS THE DESIGN. The promote
    is per-core and its cores are independent — heights are per-core (`max_parents=1` measured
    corpus-wide, a forest of trees), the id counter is a claimed sequence, and each core commits
    alone. So N workers can promote disjoint slices with no coordination.
    #
    ⚑⚑ RETIRE AND INGEST ARE NOT SHARDED, AND MUST NOT BE. `reclaim` computes a corpus-wide
    licence (which cores the durable tier can rebuild) and deletes across all of them; running it
    N times concurrently would have N workers deleting from the same relations on overlapping
    sets. The boundary search still runs in every worker, so whichever one reaches `retire` first
    performs it and the others find no work — correct, and it means the drain is serialised by the
    residue rather than by a lock.
    #
    ⚑ WHICH IS ALSO WHY A SHARDED RUN IS NOT `N × faster`. Only the promote parallelises; the
    retire between promotes is shared, and the shards are size-skewed because `hashtext` knows
    nothing about core size (measured: 2.36M / 0.95M / 1.75M observations over three shards).
    Expect the smallest shard to idle while the largest finishes its tail core.
    #
    ⚑⚑⚑ RESOURCE CEILING — THE 2026-08-17 `N ≤ 3` RULING IS SUPERSEDED (cassian-observability, IC,
    2026-08-18 incident). **THE CAP IS DISK HEADROOM, NOT N.** Both of the old ruling's stated
    reasons relaxed, and it omitted the one that actually bit:

      * write-path bandwidth — QUIET **under per-core commit specifically**. WAL ~0 MB/s,
        checkpoints-requested ~0/s. `INSERT … RETURNING` with a commit per core does not pressure
        checkpoints. ⚑ This is a fact about this fold's write PATTERN, NOT "write-path is never the
        constraint" — do not let this qualifier drift looser.
      * the `N × work_mem` OOM path — ⚑⚑ **THIS BULLET'S ARGUMENT HAS WEAKENED AND THE NUMBER IT
        RESTED ON WAS STALE.** It read *"live is 8MB, 16× smaller [than 128MB], and hash nodes do
        not stack into OOM at N=3."* Measured on the server 2026-08-26 (`SHOW work_mem`, confirmed
        by cassian-observability): **live is 48MB**, raised 8→48 on 2026-08-23 from a spill
        distribution showing the median fold op spilling at 8MB. So the headroom this bullet
        claimed is **6× smaller than written**, and the conclusion is now *narrower* rather than
        wrong: hash nodes still do not stack into OOM at N≤3, but the margin is not 16×.
        ⚑ **DO NOT RE-FREEZE A NUMBER HERE.** This paragraph is the third value of `work_mem` to
        appear in it (128 → 8 → 48) and the first two both aged into false claims **inside the
        very passage that warns a stored constant does exactly that**. `SHOW work_mem` is the
        authority; ask it. What is load-bearing and does NOT rot: the bound is per-query and the
        OOM path is real at much higher N.
      * ⚑ **`pgsql_tmp` DISK SPILL — the constraint the ruling never named, and the one that
        ENOSPC'd this fold.** Low `work_mem` + a 15×-larger corpus (93.4M obs vs the 6.27M the
        ruling was sized against) means a single full-corpus hash-aggregate spills tens of GB.
        Measured: ONE such query held 34G of `pgsql_tmp` over 91 minutes; a second identical one
        was 21 minutes behind it on the same curve. The volume hit 97% and the fold died in
        `work_retire`'s residue predicate — before any fold step, so nothing was written.

    ⚑⚑ SO THE KNOB IS NOT N, BECAUSE SPILL IS PER-QUERY, NOT PER-SHARD. Three shards of this fold
    are not the disk risk; ONE full-corpus aggregate is. `N ≤ 3` survives only as a ceiling, and it
    is no longer the thing to check.

    ⚑⚑⚑ AND THE INCIDENT GOT **WORSE**, NOT BETTER, WHICH IS THE OPPOSITE OF HOW A RAISED
    `work_mem` READS. The 34G / 91-minute / ENOSPC-at-97% event above happened at `work_mem` **8MB**.
    Live is **48MB** — roughly 6× more per operation — against the SAME volume: measured
    2026-08-26, `/dev/nvme0n1p2` at **48G available, 90% used**, and the pg data dir and the k3s PVC
    hostPath are the SAME filesystem, so a container migration changes the spill ceiling by ZERO.
    A larger `work_mem` buys fewer spills and a BIGGER one when it happens; the ceiling did not move.
    ⚑ So re-derive `expected_spill` at the CURRENT setting before any full-corpus run — the formula
    below is unchanged and its inputs are not.

    ⚑⚑ ABORT ON FREE SPACE — AND **NOT** ON PSI. The old ruling's instrument note is the half that
    survives, and it is sharper than it knew: PSI measures STALL, and a spilling query fills a
    volume WITHOUT stalling anyone until ENOSPC. There is no warning in the stall signal; the fold
    got none. Watch `node_filesystem_avail_bytes` (or `df`). Hold at free < 15G falling, or while
    `pgsql_tmp` is growing.

    ⚑ AND THE THRESHOLD IS A DERIVATION, NOT A CONSTANT — which is the defect of the text this
    replaces. Refuse a full-corpus spilling run when `free < 3 × expected_spill`, where
    `expected_spill ≈ the relation's size` at the current `work_mem` (a 93.4M-row aggregate at 8MB
    spilled ~34G ≈ the relation). The 3× covers a concurrent second query — the exact thing that
    bit. **Compute it from (relation size, work_mem, free space); do not store the number.** As of
    this incident (2026-08-18, corpus 93.4M obs) the formula evaluates to ~100G free; it will
    differ as the corpus grows — **recompute, never quote this figure.** The superseded ruling
    froze `N ≤ 3` and `128MB` and aged into a false claim in ten months; a stored number here would
    do the same.

    ⚑ THERE IS NO GATE FOR THIS, AND THAT ASYMMETRY IS THE ROOT LESSON. `membudget` makes it
    IMPOSSIBLE for a compile to OOM this box — the lease BLOCKS rather than failing. Nothing plays
    that role for disk, so a query walks into a full volume with nothing in the way. `--activity`,
    `--locks` and `membudget status` were all checked before the launch that died; NONE of them
    reports free space, and `schema.py --growth` reports the STORE's footprint (40 GB) rather than
    the VOLUME's headroom — a correct answer to a question the caller did not realise they were
    not asking.

        loop:
          for boundary in HIGHEST → LOWEST (lifecycle.drain_order()):
              if that boundary has work:  do ONE bounded unit, RESTART from the highest
          # no boundary has work → the store is CONVERGED, and the loop ends

    ⚑⚑ THIS IS `lifecycle.drain_order()`'s FIRST CONSUMER. That function has been implemented
    and selftested with ZERO production callers: it states the precedence the user gave
    (*"elements in B must be drained to C before elements in A are drained to B"*) and nothing
    read it. Restarting from the TOP after any progress is what turns that precedence into a
    SEARCH ORDER rather than a schedule — lower-tier work happens only when everything above
    it is quiescent, so no component has to know the order; it falls out of where the search
    stops.

    ⚑ SO INGEST IS NOT SCHEDULED, IT IS WHAT'S LEFT. Ingesting one more core is the LOWEST
    boundary, so it runs only when promote and retire have nothing to do. That is the user's
    *"eventually the db is converged, and it's time to ingest another core"*, expressed as a
    search rather than as a phase.

    ⚑⚑ THERE IS NO `advance` STEP, AND ITS ABSENCE IS THE POINT (user, 2026-08-11: *"under IF
    NOT EXISTS, hwm and lwm are boolean predicates"*). Every work predicate here is a RESIDUE
    — `EXISTS (… WHERE NOT EXISTS (…))` — so no cursor is read, no cursor is written, and no
    `MIN(lwm)` floor is composed. `advance` existed only to move a stored position that the
    retire licence then thresholded; with the licence stated per-core over the DURABLE tier
    (`q_drainable_res`), the position it was moving has no reader.

    ⚑ AND THAT RETIRES A DEFECT CLASS RATHER THAN A LINE. `lifecycle.py:470-474`: *"a STORED
    cursor is a SECOND WRITE that must be made atomic with the work it describes, and a DERIVED
    one is read from the same snapshot as the data, so the atomicity question does not arise."*
    Three measured incidents live in that gap — `register`'s SELECT-then-upsert under
    `autocommit=True`, `reclaim` composing four world-states, and a `pin` stored at
    `lwm=177,397` beside a tool printing *"a pin NEVER advances, by design"*. None of them is
    reachable from a loop that stores nothing.

    ⚑ INTERRUPTIBLE AND RESUMABLE ARE PROPERTIES OF WHERE THE STATE LIVES, not features. Every
    work predicate reads the STORE (`obs ⋈ obs_node`, `q_drainable_res`, `terms ⋈ core_fp`);
    nothing is carried between steps. Killing the process mid-loop loses at most the step in
    flight, and a restart resumes — measured the hard way in this session, when a killed
    background run left a store whose state could not be explained.

    ⚑ THIS ROSTER LISTED `consumer.lwm` UNTIL 2026-08-12 AND IT WAS ALREADY FALSE WHEN WRITTEN:
    no predicate here ever read it, which is precisely the fact that made the whole queue tier
    retirable. A note that names a dependency the code does not have is the same defect class
    as a relocation list naming a function that did not move — it reads as authoritative.

    ⚑ AND IT IS RESILIENT TO TABLE GROWTH FOR THE SAME REASON. Each step is ONE bounded unit,
    so a growing relation slows a STEP and never a sweep — and the tier that is growing is
    drained before more is added to it, which is the whole content of downstream-first.

    ⚑ A HELD CORE IS NOT AN ERROR AND MUST NOT STALL THE LOOP. A core that is not yet
    reconstructible is simply absent from `q_drainable`'s set — the SET DIFFERENCE semantics
    that replaced `_unreflected_floor`'s early-`break` floor, where one unreconstructible low
    core held every drainable core above it. It stays in tier 0, it is already promoted (so it
    triggers no further promote work), and the loop proceeds to ingest the next core. The
    residue is REPORTED at the end, never retried in a spin.

    ⚑ THE ONE NON-STORE PIECE OF STATE IS `undecodable`, AND IT IS A TERMINATION GUARD, not a
    cursor. `_decode_raw` swallows every exception and returns None, so an undecodable core
    gets no `core_fp` row — and the ingest work predicate would therefore offer it again
    forever. Skipping it within the run bounds the loop; a restart retries it exactly once
    more, which is the correct amount for a condition that may be a rebuild away from fixed.

    ⚑⚑ THAT REASONING IS SOUND FOR THE LOOP AND SAYS NOTHING ABOUT THE CAUSE (⑼, 2026-08-12).
    It licensed the SKIP and was read as licensing the SILENCE: this loop reported *"9 core(s)
    UNDECODABLE"* — a bare count over a corpus of 3,193 — because the only thing it could
    observe was the absence of a `core_fp` row. `undecodable` is now a `{relpath: reason}` MAP
    fed by `write_events`' return value, so the same guard bounds the same loop and the
    operator learns which of `decode-nothing` / `shim-exit-N` / a python exception happened.

    ⚑ A SKIP WITHOUT A REASON IS THE ONLY OUTCOME THIS ARC RULES OUT. Fixed and
    refused-with-a-reason are both acceptable ends for a core; an unexplained one is
    coverage loss that reports as a number.
    """
    base = base or substrate_core_root(os.path.join(_ROOT, "agda"))
    con = (
        _store.sandbox_connect(reset=False) if sandbox else _store.connect(mode="rw", require=False)
    )
    # ⚑ `_schema.apply(con, only="queue")` STOOD HERE AND WENT WITH THE TIER (2026-08-12).
    # There is no `queue` tier to apply — `_TIERS` no longer declares one — and leaving the
    # call would raise `unknown tier 'queue'` from the guard that exists to catch a TYPO. That
    # guard is doing its job either way; the fix is to stop asking for a tier that is retired.
    _schema.apply(con, only="event")
    con.commit()
    rel = {os.path.relpath(p, base): p for p in cores}
    undecodable, trace = {}, []  # relpath → typed reason (⑼); was a bare set

    def _do_promote():
        # ⚑⚑⚑ ONE CORE PER STEP — which is what `converge`'s own contract says a step is, and
        # what this function did NOT do. It called `project_sppf(additive=True)` over the WHOLE
        # store, so at the promote boundary the "ONE bounded unit" was the entire 6,274,182-row
        # residue: a step that either completes or loses everything, i.e. the batch the fixpoint
        # exists to replace. Measured live: 152 cores, median 6,212, max 943,927.
        #
        # ⚑⚑ THE CORE IS CHOSEN BY THE RESIDUE, NOT BY A CURSOR. `q_unprojected_cores` is
        # `work_promote`'s own set grouped — the predicate and the work are the same set, which
        # `work_promote`'s docstring names as the property an incremental promote buys. So a kill
        # mid-run loses at most the core in flight and a restart re-asks the store which core is
        # next; nothing is carried, and `_ingested_relpaths`' argument (*"a Python list of cores
        # still to do is a second cursor that dies with the process"*) applies unchanged here.
        #
        # ⚑ LARGEST-FIRST, from the ORDER BY in the builder rather than a sort here — the
        # tail-first ruling: if a 943,927-observation core cannot be folded, that should surface
        # on step one, not after 147 smaller cores have landed.
        _dedup_pathseg(con)
        con.commit()
        refresh_path_text(con)
        # ⚑⚑⚑ THE SHARD PREDICATE IS THE CLAIM STEP, AND WITHOUT IT N WORKERS FOLD ONE CORE.
        # `unprojected_cores` is residue-driven with no cursor — deliberately, so a kill loses at
        # most the core in flight. That is exactly right for ONE worker and silently wrong for N:
        # every worker asks the same question and gets the same largest-first head. Three shards
        # would fold the SAME core three times, each claiming a different id block for identical
        # signatures; `ix_obsnode_pk`'s `ON CONFLICT DO NOTHING` would swallow the duplicates and
        # the run would REPORT SUCCESS while two thirds of the work was wasted.
        #
        # ⚑⚑ A PARTITION, NOT A LOCK — `abs(hashtext(core_id)) % shards = shard`. No claim table,
        # no lease to expire, no coordination: a worker that dies leaves its slice unclaimed and a
        # re-run picks it up, because the predicate is STILL a residue read. A claim table would
        # be the "second cursor that dies with the process" this loop exists to avoid.
        #
        # ⚑ VERIFIED TOTAL AND DISJOINT on the live residue before use: 54 + 44 + 51 = 149 cores,
        # exactly the 152 minus the 3 already projected, no overlap. The `abs()` is load-bearing —
        # postgres `%` on a negative left operand is NEGATIVE, so `hashtext(x) % 3` yields -2..2
        # and shards numbered 0..2 would silently cover only half the corpus.
        #
        # ⚑ UNSHARDED IS `shards=1, shard=0`, which the same predicate answers as "everything" —
        # so there is ONE code path, not a sharded one and a serial one that can disagree.
        _next = list(
            QB.run(con, "unprojected_cores_shard", shards=max(int(shards), 1), shard=int(shard))
        )
        if not _next:
            # ⚑ NOT REACHED WHEN THERE IS WORK, and reaching it means the residue is empty —
            # which the boundary search already established before calling. Kept as a refusal
            # rather than a silent no-op so a disagreement between the two is loud.
            return "promote[nothing unprojected]"
        _cid, _n = _next[0][0], _next[0][1]
        # ⚑⚑ THE BASE IS SEEDED FROM THE STORE, NOT FROM ZERO — `_seed_node_ids` returns
        # `(signature→id, top)` and `project_sppf:846-848` records why: *"a second project_sppf
        # over a DIFFERENT set of live cores restarts the numbering: signature S gets id 3 in run
        # 2 while id 3 already denotes a different signature from run 1 … silent corruption, not
        # a conflict."* An additive per-core promote is exactly that second run, 152 times.
        #
        # ⚑ ONLY THE COUNTER IS READ, VIA `node_id_top` — not `_seed_node_ids`. That function
        # returns `(signature→id map, top)` and builds the map by scanning ALL of `node_child`
        # and `_node`; the python fold looks signatures up in it, the SQL fold re-derives sharing
        # per level through `obs_node`. Calling it per core would scan both relations 152 times
        # and discard the larger half of each answer — the materialise-then-throw-away shape
        # this arc has now removed three times, reintroduced in the wiring.
        # ⚑⚑⚑ CLAIMED, NOT READ — AND THAT IS WHAT MAKES THE PROMOTE SHARDABLE BY `core_id`.
        # `node_id_top` is `max(node_id)`: a READ, so two concurrent promoters get the SAME value
        # and mint overlapping ids for DIFFERENT signatures. That is precisely the corruption
        # `_seed_node_ids` records — *"signature S gets id 3 in run 2 while id 3 already denotes a
        # different signature from run 1 … silent corruption, not a conflict"* — reached by
        # concurrency instead of by re-running.
        #
        # ⚑⚑ EVERYTHING ELSE ABOUT THE FOLD ALREADY SHARDS. Heights are per-core (`max_parents=1`
        # corpus-wide, measured — a forest of trees, no cross-core term); `q_unprojected_cores` IS
        # the shard enumerator (every unprojected core, largest first); `_do_promote` takes ONE
        # core and commits it; and every work predicate is a residue READ, so N workers can each
        # ask "is there work" without coordinating. The counter was the only shared mutable state,
        # which is why fixing it is the whole of the parallelisation.
        #
        # ⚑ A SEQUENCE, BECAUSE IT IS THE ONE ALLOCATOR POSTGRES GUARANTEES IS NON-TRANSACTIONAL:
        # `nextval` never returns the same value twice even across concurrent and rolled-back
        # transactions. A `SELECT max(…) FOR UPDATE` would serialise the promoters on one row —
        # correct, and it would give back exactly the concurrency this change exists to buy.
        # Seeded past the existing high-water mark on first use so ids already minted are never
        # re-issued.
        _seed_hi = _claim_node_ids(con, _n)
        _lv, _rows, _ids, _top = pack_core_sql(con, _cid, base=_seed_hi, write=True)
        con.commit()  # ⚑ THE CORE IS THE ATOMIC UNIT: commit per core, so a
        # kill rolls back exactly one core's levels.
        project_ref(con, additive=True)
        return "promote[core %s: %s obs, %d level(s), %d id(s)]" % (
            _cid[:12],
            format(_rows, ","),
            _lv,
            _ids,
        )

    def _do_retire():
        got = _schema.reclaim(con, dry_run=False)
        # ⚑ `edge` JOINED THIS LINE WITH ⑹ (2026-08-12), AND THE CONVERGE LOOP IS WHERE ITS
        # ABSENCE WAS FIRST VISIBLE: the run measured `obs` returning to 0 after every core
        # while `edge` grew monotonically to 472,959 — and the trace said nothing, because it
        # printed only the two relations that were already draining.
        return "retire[%s obs, %s edge, %s ev]" % (
            got.get("obs"),
            got.get("edge"),
            got.get("events"),
        )

    def _todo():
        done = _ingested_relpaths(con) | set(undecodable)
        return sorted(r for r in rel if r not in done)

    def _do_ingest():
        r = _todo()[0]
        # ⚑ `finalize=False` DROPPED WITH THE PARAMETER (⟡finalize-tail-home). This site was
        # the ONLY one that passed it, and it passed False — the per-core path opting out of a
        # corpus-wide tail. That opt-out is now the only behaviour, so the argument is gone
        # rather than kept as a no-op the next reader would have to interpret.
        why = write_events([rel[r]], con, base, prune=False, producer=producer)
        if r not in _ingested_relpaths(con):
            # ⚑ TWO DIFFERENT ABSENCES, AND THEY MUST NOT SHARE A REASON. `why[r]` is a
            # DECODE failure the shim explained. A missing `core_fp` row with NO entry in
            # `why` means the core was never even offered to the decoder — `write_events`
            # skipped it as unchanged, or its `os.stat` raised — which is a different
            # condition with a different repair, and folding it into the decode reason
            # would be inventing a diagnosis.
            undecodable[r] = why.get(r) or (
                "not decoded and not offered: no core_fp row and no decode attempt — "
                "the core was filtered out of `changed` (unreadable, or mtime unadvanced "
                "against a stale core_fp row)"
            )
            return "ingest[UNDECODABLE %s]" % r
        return "ingest[%s]" % r

    # ⚑ THE ROSTER IS ORDERED BY `lifecycle.drain_order()`, NOT BY THE LIST'S OWN WRITING
    # ORDER. Sorting it (in `converge_order`) is what makes the precedence CHECKABLE
    # (`lifecycle.drains_before`) instead of a property of how the tuples happen to be typed.
    # What each entry NAMES is the boundary; where that boundary SITS is the chain's to say.
    # ── ⚑⚑ KEYED BY THE BOUNDARY'S NAME. THE INTEGER-KEYED ROSTER — RETIRED 2026-08-12. ──────
    #
    #     steps = {3: ("retire", work_retire, _do_retire),
    #              2: ("promote", work_promote, _do_promote),
    #              1: ("ingest", lambda _c: bool(_todo()), _do_ingest)}
    #     order = [i for i in _lc.drain_order() if i in steps]
    #
    # ⚑ ITS OWN NOTE STATED THE HAZARD AND STILL LEFT IT REACHABLE, which is why the quote is
    # kept: *"RETIRE MOVED 4 → 3 WHEN `consumed` LEFT THE CHAIN (2026-08-12), AND THE FAILURE
    # MODE OF NOT MOVING IT IS SILENT … `order = [i for i in drain_order() if i in steps]` would
    # have QUIETLY DROPPED the retire step and left a loop that ingests and promotes forever
    # without ever draining. No exception, no empty result, just a boundary that stopped being
    # serviced."* It then defended the filter — *"it is kept because it is also what lets the
    # roster be sparse"* — and delegated the safety to a hand-written selftest case. A note plus
    # a case is not a mechanism: the next chain edit gets the silent skip again unless the
    # LOOKUP itself refuses.
    #
    # ⚑ THE SPARSENESS THE FILTER BOUGHT IS FREE UNDER NAMES. A roster keyed by name is sparse
    # BY CONSTRUCTION — a boundary nobody names simply has no step (`sourced`, the filesystem
    # edge, has none today) — so nothing had to be traded away to delete the filter.
    #
    # ⚑ AND THE REPLACEMENT IS ONE CALL, NOT A CONVENTION: `lifecycle.service_order` resolves
    # each name through `boundary_index` and RAISES on a name the chain does not declare.
    import lifecycle as _lc

    # ⚑⚑ PROMOTE MOVED FROM `settled` TO `reflected` WHEN `settled` LEFT THE CHAIN
    # (2026-08-12), AND THE GUARD IS WHAT MADE THAT A DECISION RATHER THAN AN ACCIDENT. The
    # deletion landed and `sppf_db --selftest` REFUSED, naming the step and the chain:
    #
    #     KeyError: "actor 'promote' spans the boundary named 'settled', which the lifecycle
    #     chain does NOT declare. Its links are ['sourced', 'observed', 'reflected'] …"
    #
    # Under the retired integer roster the same edit was SILENT: `{3: retire, 2: promote, 1:
    # ingest}` against `drain_order() == [2,1,0]` gives `order = [2,1]`, promote and ingest run
    # forever, and RETIRE — the drain — is simply not in the loop.
    #
    # ⚑ AND THE RE-DECLARATION IS NOT A RENAME, IT IS THE HONEST BOUNDARY. Promote was only ever
    # at `observed → settled` because the chain had a spare link between the log and the durable
    # form; what promote actually DOES is make a record `reflected` (project the SPPF so
    # `reconstruct` rebuilds it). Retire is what the `reflected` stage LICENSES — it advances
    # nothing, it reclaims the staged copy behind the feed. So the two share ONE boundary and
    # are told apart by SIDE, which is the pair `lifecycle.SIDES` exists to order.
    _roster = (
        ("reflected", "reclaim", "retire", work_retire, _do_retire),
        ("reflected", "feed", "promote", work_promote, _do_promote),
        ("observed", "feed", "ingest", lambda _c: bool(_todo()), _do_ingest),
    )
    order = _lc.service_order(_roster)

    for n in range(max_steps):
        t0 = time.time()
        for bname, _side, name, has_work, do in order:
            if not has_work(con):
                continue
            what = do()
            row = {
                "step": n + 1,
                "boundary": bname,
                "at": name,
                "did": what,
                "s": time.time() - t0,
                **tier_census(con),
            }
            trace.append(row)
            if report:
                report(row)
            break  # RESTART from the highest boundary
        else:
            break  # CONVERGED — no boundary has work
    con.close()
    # ⚑ A LIST OF PAIRS, NOT A DICT AND NOT A SORTED LIST OF NAMES. Sorted so the report is
    # stable across runs; PAIRS so the reason travels with the core it belongs to, which a
    # `sorted(undecodable)` over a dict would have silently discarded while still typechecking.
    return trace, sorted(undecodable.items())


def code_of(fn):
    """⟡getsource-substring — a function's SOURCE WITH COMMENTS AND DOCSTRINGS REMOVED.

    ⚑⚑⚑ FOUR MEASURED FAILURES OF ONE SHAPE, and this file documents three of them at three
    separate sites. A `getsource(fn)` substring assertion pins TEXT and reads as pinning
    BEHAVIOUR, so the ⚑ comment written to explain a change SATISFIES the check the change was
    supposed to break — or breaks a check the change should have passed:

      · a case searched `project_ref` for `WHERE a.clid IS NULL` to assert the filter was ABSENT;
        the comment explaining its removal contains that string, so the guard failed on correct
        code.
      · a case asserted the literal `QB.run(con, "ref_rows")`; the honest move to a server-side
        `INSERT … SELECT` failed it, and the tempting repair was to keep a DISCARDED call alive
        purely to satisfy the string — gaming a check.
      · `finalize_db`'s ordering case compared `index("_gc_orphan_events(") < index("project_sppf(")`;
        documenting the retirement in that function's docstring made `.index` find the PROSE
        first and inverted the comparison (2026-08-22).
      · the `force=full` reachability case pinned a VARIABLE NAME and failed on a rename while
        the capability it guards was intact (same day).

    ⚑⚑ SO THE WARNING WAS WRITTEN THREE TIMES AND THE HAZARD RECURRED, which is the tell that a
    per-site comment is the wrong home: each new case re-learns it. This makes the SAFE form the
    available one — strip what is not code, then match.

    ⚑ AND IT DOES NOT MAKE THE ASSERTION SOUND, only honest about ITS OWN scope. Matching a
    substring against code is still matching text: it cannot tell a call from a mention inside a
    STRING LITERAL, and a case that must distinguish those wants the AST (`_ast2.walk`, as the
    cursor-operation case here already does). What this removes is the failure mode where
    DOCUMENTING a change alters the verdict on it.
    """
    import ast as _a
    import inspect as _i
    import textwrap as _tw

    src = _tw.dedent(_i.getsource(fn))
    try:
        tree = _a.parse(src)
    except SyntaxError:
        return src  # decorated/nested oddity: fall back rather than lie
    # ⚑ DOCSTRINGS ARE EXPRESSION STATEMENTS, not a separate node kind — so they are found by
    # walking for a bare `Constant` string in statement position, at every nesting level. A
    # top-level-only strip would leave every inner function's docstring matchable.
    for node in _a.walk(tree):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], _a.Expr)
            and isinstance(getattr(body[0], "value", None), _a.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body.pop(0)
    # ⚑ `ast.unparse` DROPS COMMENTS BY CONSTRUCTION, which is the property wanted here and the
    # exact reason `pycodemod` refuses `ast` for its TRANSFORMS (it would destroy this repo's
    # incident log). Read-only, so the destruction is the point.
    return _a.unparse(tree)


def _selftest():
    """⚑ THIS MODULE HAD NO SELFTEST, WHICH IS PART OF WHY THE v2 MIGRATION GAP SHIPPED.
    `run_selftests` DISCOVERS modules that define one, so a file with none is INVISIBLE
    rather than failing — the same gap that let `rename_at_source` ship a live write-path
    bug through a green 413/413 suite."""
    cases = []

    def check(label, got, want):
        # ⚑⚑⚑ THE CALL SITE IS CAPTURED, NOT JUST THE LABEL (operator, 2026-08-22: *"We should
        # have self-test failures include stack traces."*). A failure used to print only
        # `FAIL <label>: got X want Y`, so LOCATING it meant searching the corpus for the
        # message string — MEASURED the same session: six tool calls to find one failing case,
        # three of them guessed mode names, because the label is prose and the cases live in
        # THIS function AND in `sppf_decode`, `schema_selftest` and other modules' helpers.
        #
        # ⚑⚑ `stack()[1]` AND NOT A FULL TRACEBACK, DELIBERATELY. A `check` is not an exception:
        # nothing is raised, so there is no traceback to capture, and synthesising one would
        # report the reporting machinery rather than the assertion. The frame that CALLED
        # `check` is the whole answer — file, line, and the enclosing function — and it costs one
        # frame lookup per case rather than a formatted stack per case.
        #
        # ⚑ IT SPANS MODULES, WHICH IS WHY THE FILE IS PART OF IT. `decode_reason_cases`,
        # `reconcile_stamp_cases` and friends take `check` as a parameter and call it from
        # `sppf_decode.py`; a bare line number would name a file the reader is not looking at.
        import inspect as _i

        _f = _i.stack()[1]
        cases.append(
            (
                label,
                got == want,
                got,
                want,
                "%s:%d in %s" % (os.path.basename(_f.filename), _f.lineno, _f.function),
            )
        )

    # ── ⑼ A FAILED DECODE CARRIES ITS REASON — cases in `sppf_decode`, beside the code ──
    #
    # ⚑ THE THREE KINDS ARE ASSERTED APART there, not merely "a reason is non-empty". A reason
    # that is always the same string is the bare count with extra characters; what makes it
    # actionable is that `decode-nothing` (Agda refused the interface — rebuild the core) and
    # `shim-exit-N` / an exception (the TOOL or its environment failed — rebuild the shim)
    # send the operator to different places.
    decode_reason_cases(check)

    # ── ⒯ THE INGEST STAMP RECONCILER — cases in `sppf_decode`, beside the rung ─────────
    # ⚑ THESE DRIVE THE STAMP-IS-A-LIE PREDICATE, which is the one thing wiring ingestion into
    # `make` can get catastrophically wrong: a stamp survives a tenant DROP, make skips the
    # recipe, and the build is green over an empty store. The reset case and the orphan case
    # are asserted APART because they falsify a stamp for different reasons — an absent
    # `core_fp` row versus an absent CORE — and only the first is what a "did the store keep
    # it" check would look for.
    import tempfile as _tf

    with _tf.TemporaryDirectory() as _td:
        reconcile_stamp_cases(check, _td)

    # ── ⟡core-id-branches: THE TWO SILENT EXITS THE MAKE-DRIVEN MODES TAKE ───────────────
    # ⚑⚑ BOTH BRANCHES RETURN `None` AND BOTH CALLERS TURN THAT INTO `exit 0` WITH NO OUTPUT.
    # That is correct — a core not compiled and a core not ingested are ORDERING facts make's
    # own DAG resolves, and failing the build over a race the dependency edge already handles
    # would be worse — but a silent exit is precisely what a case must pin rather than a reader
    # discover. I found one BY ACCIDENT (`--drain-core` on a module whose `.ingested` stamp the
    # reconciler had just deleted): the behaviour was right and the way I learned it was not.
    #
    # ⚑ DRIVEN OVER AN INJECTED LOOKUP, so no store stands up to check a filename comparison —
    # `_reconcile_over`'s rule, applied to the sibling helper.
    with _tf.TemporaryDirectory() as _td2:
        _cb = os.path.join(_td2, "cores")
        os.makedirs(os.path.join(_cb, "Sub"), exist_ok=True)
        _cc = os.path.join(_cb, "Sub", "M.agdai")
        _hit = lambda rel: "the-id" if rel == "Sub/M.agdai" else None
        check(
            "no .agdai on disk ⟹ None, and the store is never asked",
            _core_id_over(
                _cc,
                _cb,
                lambda rel: (_ for _ in ()).throw(
                    AssertionError("lookup must not run when the core is absent")
                ),
            ),
            None,
        )
        open(_cc, "w").write("x")
        check(
            "...compiled but NOT ingested ⟹ None (no core_fp row)",
            _core_id_over(_cc, _cb, lambda _rel: None),
            None,
        )
        check("...compiled AND ingested ⟹ the core id", _core_id_over(_cc, _cb, _hit), "the-id")
        # ⚑ THE LOOKUP IS ASKED FOR THE RELPATH, NOT THE ABSOLUTE PATH — the join is on
        # `terms.text`, which stores the path relative to the core root. Passing the absolute
        # path would return None for every core and both modes would silently do nothing on a
        # correctly-ingested tree, which is the failure this case exists to make impossible.
        _seen_rel = []
        _core_id_over(_cc, _cb, lambda rel: _seen_rel.append(rel))
        check(
            "...and the lookup receives the RELPATH the interner stores", _seen_rel, ["Sub/M.agdai"]
        )
        # ⚑ A `.agda` SOURCE PATH RESOLVES TO ITS CORE — the generated recipes pass `$<`, but
        # `_resolve_core` accepts either spelling and the per-dir loop used to pass sources.
        check(
            "a source path resolves through _resolve_core to the same id",
            _core_id_over(_cc.replace(".agdai", ".agda"), _cb, _hit),
            "the-id",
        )

    # ── ⟡ladder-1 THE SOURCED TIER — cases in `sppf_decode`, beside the rung ────────────
    # ⚑ The fidelity claim is driven against a REAL decoded core and anchored on `dec`
    # ITSELF at every depth — never on a roster of what `_insert_decoded` happens to read,
    # which is a lower bound at best and a frozen roster at worst.
    source_row_cases(check)

    # ── ⟡ladder-2 THE VOCAB TIER — cases in `sppf_vocab`, beside the rung ───────────────
    # ⚑ THE SUITE STAYS HERE WHILE THE MODES DO NOT, and the split is the cap doing its job:
    # `run_selftests.discover()` counts a suite as the PAIR of a `_selftest` def and a
    # `--selftest` dispatch, so `sppf_vocab` defines neither and the total holds at 69 — while
    # its three CLI modes live in its own `__main__`, because three usage lines plus a dispatch
    # would not fit the four code lines this file has left.
    vocab_cases(check)

    # ── ⟡ladder-4 THE TREE TIER — cases in `sppf_tree`, beside the rung ─────────────────
    # ⚑ SAME SPLIT, SAME REASON, AND THE CAP IS STILL THE THING ENFORCING IT: the modes live
    # in `sppf_tree.__main__` because this file has ~19 code lines of headroom, and the SUITE
    # stays here because `run_selftests.discover()` counts a suite as the PAIR of a `_selftest`
    # def and a dispatch on the selftest flag. Two lines here; the total holds at 69.
    tree_cases(check)
    drain_cases(check)

    # ── the leaf format (AgdaiReflect.hs:399-403 is the authority) ──────────────────
    check("an Int leaf parses", leaf_value("#Int:0"), ("Int", "0"))
    check("an Integer leaf parses", leaf_value("#Integer:61"), ("Integer", "61"))
    # ⚑ A STRING LEAF'S VALUE CONTAINS QUOTES AND MAY CONTAIN A COLON — `show` emits
    # `#String:"a:b"`, so a `split(":")` would truncate it. The regex is non-greedy on the
    # TYPE only; the value takes the rest.
    check(
        "a String leaf keeps a colon in its value", leaf_value('#String:"a:b"'), ("String", '"a:b"')
    )
    check("a non-leaf constructor is not a leaf", leaf_value("Var"), None)
    check("a bare '#' is not a leaf", leaf_value("#"), None)

    # ── recovery: the measured defect ───────────────────────────────────────────────
    # ⚑ THE SHAPE IS THE GENERATOR'S OWN, VERIFIED: "`Var/2 [Int, Elims]` emits `Var [0,1]`"
    # (AgdaiReflect.hs:228-229) — child[0] is the index leaf.
    v2_nodes = {
        0: {"constructor": "#Int:7", "children": []},
        1: {"constructor": "[]", "children": []},
        2: {"constructor": "Var", "children": [0, 1]},
    }
    q, i, l = recover_fields(v2_nodes[2], v2_nodes)
    check("a v2 Var recovers its de Bruijn index from child[0]", i, 7)
    # ⚑ THE CASE MUST FAIL AGAINST THE SHIPPED CODE, or it is decoration. The old line was
    # `idx = rec.get("index")`, which on this record is None — and `f"db{None}"` is the
    # `"dbNone"` measured in the live store.
    check("...where the OLD read returned None", v2_nodes[2].get("index"), None)
    check("...and would have interned the sentinel", "db%s" % v2_nodes[2].get("index"), "dbNone")

    # a leaf node's own value becomes its literal
    _, _, lit = recover_fields(v2_nodes[0], v2_nodes)
    check("a leaf's value is recovered as its lit", lit, "7")

    # ⚑ JSON OBJECT KEYS ARE STRINGS WHILE `children` HOLDS INTS. A lookup that tried only
    # one side missed every child silently; this pins both.
    v2_str = {
        "0": {"constructor": "#Int:3", "children": []},
        "2": {"constructor": "Var", "children": [0, 1]},
    }
    check("string-keyed nodes resolve too", recover_fields(v2_str["2"], v2_str)[1], 3)

    # ⚑ A v1 RECORD MUST WIN — there is no version tag in the JSON (neither `emit` nor
    # `emitG` writes one), so field-presence is the only discriminator available.
    v1 = {"constructor": "Var", "children": [0, 1], "qname": "Q", "index": 4, "lit": "L"}
    check("an explicit v1 field is authoritative", recover_fields(v1, {}), ("Q", 4, "L"))

    # a non-Var with no leaf child recovers nothing, and must not invent a value
    plain = {"constructor": "Def", "children": []}
    check("a plain node recovers no idx", recover_fields(plain, {})[1], None)

    # ── qname recovery: the field `scope_fix._event_refs` GATES ON ────────────────────
    # ⚑ A QName IS A SUBTREE, NOT A LEAF, which is why `idx`'s child[0] rule does not apply.
    # MEASURED shape (sandbox, Algebra/F2/F2.agdai): `QName [MName, Name]`, `MName → [] →
    # [Name…]` for the module path, and each `Name`'s name-part list holds `Id → #String:`.
    _q = {
        0: {"constructor": '#String:"Substrate"', "children": []},
        1: {"constructor": "Id", "children": [0]},
        2: {"constructor": "[]", "children": [1]},
        3: {"constructor": "Name", "children": [2]},
        4: {"constructor": "[]", "children": [3]},
        5: {"constructor": "MName", "children": [4]},
        6: {"constructor": '#String:"F\\8322"', "children": []},
        7: {"constructor": "Id", "children": [6]},
        8: {"constructor": "[]", "children": [7]},
        9: {"constructor": "Name", "children": [8]},
        10: {"constructor": "QName", "children": [5, 9]},
        11: {"constructor": "Def", "children": [10, 99]},
    }
    check(
        "a QName subtree joins module path and base name", _qname_text(_q[10], _q), "Substrate.F₂"
    )
    # ⚑ THE REFERENCE NODE IS WHAT THE RESOLVER READS, not the QName itself — `Def [QName,…]`.
    check("a Def recovers its qname from child[0]", recover_fields(_q[11], _q)[0], "Substrate.F₂")
    # ⚑ THE UNESCAPE IS LOAD-BEARING AND WOULD LOOK LIKE DATA IF OMITTED. `show` renders a
    # non-ASCII char as a DECIMAL escape, so a raw value reads `Substrate.F\8322` — a
    # plausible-looking string that joins against nothing. Agda names are routinely
    # non-ASCII, so this is the common case.
    check("a decimal codepoint escape is decoded", _unescape_haskell('"F\\8322"'), "F₂")
    check("...and a plain ASCII name is unchanged", _unescape_haskell('"Substrate"'), "Substrate")
    # ⚑ ORDER MATTERS: undoing `\\` first would make a literal backslash before digits decode
    # as a codepoint. This case fails if the two replacements are swapped.
    check("a literal backslash survives", _unescape_haskell('"a\\\\b"'), "a\\b")
    # a non-FREE node must not acquire a qname it has no business carrying
    check(
        "a plain node recovers no qname",
        recover_fields({"constructor": "Lam", "children": [10]}, _q)[0],
        None,
    )

    # ── the ref index: COVERAGE is the property, not row count ──────────────────────
    # ⚑ THIS CASE EXISTS BECAUSE I OPTIMISED THE WRONG METRIC AND CALLED IT PROGRESS. The
    # projection fans out (duplicate rows per `(plid, arg_ord)`), so I constrained the joins;
    # rows fell 5,370 → 1,800 and READ AS A FIX. Measuring reference COVERAGE showed it had
    # dropped 206 of 384 references — destroying the index's whole purpose to tidy its shape.
    # A row-count assertion would have passed. This asserts what the index is FOR.
    # ⚑ AND THE FIRST VERSION OF THIS CASE MATCHED ITS OWN DOCUMENTATION. It searched
    # `project_ref`'s source for `WHERE a.clid IS NULL` to assert the filter was absent — and
    # the comment explaining why it was removed CONTAINS that string, so the guard failed on
    # correct code. A source-text guard cannot distinguish code from the prose about it.
    import inspect as _insp

    # ⚑ ⟡getsource-substring — `code_of`, NOT `getsource`. The `QB.run(con, "…")` regex below
    # would match a builder NAMED IN A COMMENT, and the comments here deliberately name the
    # forbidden spellings in order to record why they are refused. That is the exact failure this
    # file records three times; `code_of` strips comments and docstrings so prose cannot satisfy
    # or break the check.
    _ref_src = code_of(project_ref)
    # ⚑⚑ THE GUARD NOW READS ITS INTENT, NOT ONE SPELLING OF IT. It asserted the literal
    # `QB.run(con, "ref_rows")`, so when the projection moved to a server-side `INSERT … SELECT`
    # (`q_ref_insert`), the honest change FAILED the case — and the tempting repair was to keep a
    # DISCARDED `run("ref_rows")` call alive purely to satisfy the string, executing the whole
    # SELECT for nothing on every projection. That is gaming a check. What the case is FOR is
    # "every statement this projection issues comes from the compiled builder set", which is
    # checkable directly: every `QB.run` name must be a registered builder, and no SQL literal
    # may be assembled in the tool.
    import re as _re_g
    import query_defs as _qd_g

    # ⚑ QUOTE-AGNOSTIC, BECAUSE `code_of` ROUND-TRIPS THROUGH `ast.unparse` AND IT NORMALISES
    # QUOTING — the source says `QB.run(con, "ref_rows")` and the unparse says `'ref_rows'`, so a
    # regex demanding double quotes matched nothing and the case failed on a FORMATTING change.
    # MEASURED the moment `code_of` was introduced here. That is the cost of stripping comments
    # via the AST and it is worth stating: the text you match is CANONICAL python, not the bytes
    # on disk, so a pattern pinned to source formatting is pinned to the wrong artifact.
    _ref_names = _re_g.findall(r"""QB\.run\(con,\s*["']([a-z0-9_]+)["']""", _ref_src)
    check("the ref projection issues ONLY compiled builders", bool(_ref_names), True)
    check(
        "...and every one is registered in the builder set",
        [n for n in _ref_names if n not in _qd_g.INTERN_BUILDERS],
        [],
    )
    # ⚑⚑⚑ THE REFUSAL READS THE **AST**, NOT THE SOURCE TEXT — and the file already warned me.
    # :1872 records that the FIRST version of this case searched `project_ref`'s source for a
    # string that the COMMENT EXPLAINING ITS REMOVAL also contained, so the guard failed on
    # correct code. I reproduced that verbatim: my comments above name the forbidden spellings
    # (the compiled-text lookup, the formatted INSERT) in order to record why they are refused,
    # and both string checks then failed on prose. *A source-text guard cannot distinguish code
    # from the prose about it* — so this asks the parse tree, where a comment does not exist.
    #
    # ⚑ WHAT IS ACTUALLY FORBIDDEN: a string CONSTANT in this function that looks like DML, and
    # a subscript of the compiled-SQL cache. Both are node kinds, both are decidable, and
    # neither can be tripped by a comment.
    import ast as _ast_g

    _ref_ast = _ast_g.parse(_insp.getsource(project_ref).lstrip())
    _lits = [
        n.value
        for n in _ast_g.walk(_ref_ast)
        if isinstance(n, _ast_g.Constant) and isinstance(n.value, str)
    ]
    # ⚑ A STATEMENT STARTS WITH ITS VERB — a substring test is not this predicate. The first
    # cut asked `"INSERT" in s.upper()`, which flagged the BUILDER NAME `"ref_insert"`: a
    # registered thunk name, the exact opposite of hand-written SQL. Matching the leading token
    # separates "this string IS a statement" from "this string CONTAINS the letters".
    # ⚑⚑ THE DESTINATION TIER IS A PRECONDITION THIS FUNCTION ESTABLISHES, NOT A STATE A CALLER
    # MUST HAVE ARRANGED. `pack_core_sql` writes `obs_node`, which is a DECLARED tier
    # (`schema_decl` `_TIERS["obsnode"]`) whose DDL is `IF NOT EXISTS` — so the correct handling
    # is to apply it, unconditionally, and there is nothing to check for. Until 2026-08-15 the
    # function relied on having been called after `project_sppf`'s `:983`/`:989`, which made the
    # live tenant's missing `obs_node` read as a question about the STORE rather than a gap in
    # the code (operator: *"Why is this even a question? How is it that our schema isn't a
    # derived or declared prerequisite somewhere?"*).
    #
    # ⚑ ASSERTED ON THE DECLARATION AND THE SOURCE, not on a live connection — this suite has no
    # store fixture, and the property is structural: the tier exists in the declaration, and the
    # writer applies it.
    import inspect as _insp_p

    check(
        "obs_node is a DECLARED tier, so applying it needs no existence check",
        "obs_node" in [getattr(t, "name", t) for t in _schema._TIERS["obsnode"]],
        True,
    )
    check(
        "...and pack_core_sql establishes it before writing",
        'apply(con, only="obsnode")' in _insp_p.getsource(pack_core_sql),
        True,
    )
    check(
        "...with no hand-written DML string in the tool",
        [s for s in _lits if s.strip().lower().startswith(("insert ", "delete ", "update "))],
        [],
    )
    check(
        "...and no subscript of the compiled-SQL cache",
        [
            n
            for n in _ast_g.walk(_ref_ast)
            if isinstance(n, _ast_g.Subscript)
            and isinstance(n.value, _ast_g.Attribute)
            and n.value.attr == "SQL"
        ],
        [],
    )
    # ⚑ THE CTOR GATE IS IN THE BUILDER, AND ROW COUNT CANNOT TELL ITS EFFECT FROM A
    # REGRESSION. Both my broken filter and the correct gate produced 1,800 rows: the first
    # DROPPED 206 real references, the second EXCLUDES 206 `QName` nodes that were never
    # references (a QName is the name itself). Coverage against the REFERENTIAL population is
    # the only measure that separates them — 178 of 178 with the gate, and the earlier "384"
    # was double-counting, not better coverage.
    import query_defs as _qd

    check(
        "the referential ctor set gates the index",
        "Def" in _qd.FREE_CTORS and "QName" not in _qd.FREE_CTORS,
        True,
    )

    # ⚑ `sym` MUST BE FILLED PER-EKEY IN THE HEAD LOOP, NOT INSIDE THE WARNING BLOCK. My
    # `_null_idx` edit indented this line one level too far, so `sym` was populated only when
    # a warning fired and then only for the LAST ekey — `project_sppf`'s `sym[ekey]` then
    # raised KeyError on the first ordinary node. A scope slip is invisible to review and
    # trivial to assert: the assignment must sit at the loop's indent, not the branch's.
    _ps = _insp.getsource(project_sppf)
    _sym_line = next((l for l in _ps.splitlines() if "sym[ekey]" in l and "=" in l), "")
    _head_line = next((l for l in _ps.splitlines() if "head[ekey] =" in l), "")
    check(
        "sym[ekey] is assigned at the same depth as head[ekey]",
        len(_sym_line) - len(_sym_line.lstrip()),
        len(_head_line) - len(_head_line.lstrip()),
    )
    # ⚑ EVERY PATH THAT PROJECTS MUST PROJECT `ref`, AND CHECKING ONE PATH IS HOW THIS
    # SLIPPED. My first case asserted the ordering in `finalize_db` alone; `build` — the
    # other entry point, and the one a full ingest uses — had no `project_ref` call at all,
    # so a 30-core rehearsal left `ref` describing 2 cores and READ AS SUCCESS (non-empty,
    # internally consistent, wrong corpus). `_selftest_queue_wiring` existed for exactly this
    # shape one projection earlier; this is the same census, widened — and it OUTLIVED that
    # function, which was retired 2026-08-12 having never been wired to anything.
    #
    # ⚑ THE SECOND HALF OF THIS PAIR WENT WITH THE CURSOR. It read *"...before advancing the
    # cursor (it CONSUMES the event tier)"* and compared `_src.index("project_ref(")` against
    # `_src.index("_advance_projection(")` — an ordering between two separately-committed
    # writes. `project_ref` still runs LAST among the projections because of what it is built
    # FROM, and that is a data dependency the code expresses directly; it is not a second write
    # to sequence. What remains asserted is the half that caught a real defect: the CALL exists
    # on BOTH paths.
    # ⚑ ⟡finalize-retire — THE ROSTER WAS `("finalize_db", "build")` AND IS NOW ONE ENTRY, because
    # `finalize_db` is deleted (wide, deep, atomic — the granularity ⟡project-granularity undoes).
    # The case is KEPT rather than retired with it: what it caught was `build` — the path a full
    # ingest actually uses — having no `project_ref` call at all, and that half is still live.
    # A per-entry-point census narrowed to its surviving entry point is still a census; deleting
    # it because one subject went would discard the assertion that found the defect.
    # ⚑⚑ ⟡getsource-substring — `code_of`, BECAUSE THE SUBJECT DOCUMENTS THE VERY THING ASSERTED.
    # `build`'s body carries a ⚑ block reading *"`project_ref` WAS MISSING FROM THIS PATH"*, and
    # that prose contains `project_ref(`. The call IS present today (verified: `--calls
    # project_ref` shows a real call site inside `build`), so the case passes on code — but under
    # raw `getsource` the two are INDISTINGUISHABLE, and deleting the call would leave the check
    # green on the comment alone. That is the failure mode, stated as a hazard rather than as an
    # incident: I have not demonstrated it firing here, only that nothing would have caught it.
    for _fname in ("build",):
        _src = code_of(globals()[_fname])
        check("%s projects ref" % _fname, "project_ref(" in _src, True)

    # ── the converge loop: a WORKLIST TO A FIXPOINT, not a sweep ─────────────────────────
    # ⚑ THE PRECEDENCE IS `lifecycle.drain_order()`'s, READ RATHER THAN RESTATED. That function
    # was implemented and selftested with ZERO production callers — it states the rule (*"B must
    # be drained to C before A is drained to B"*) and nothing consumed it. A roster typed in the
    # order someone happened to write it would satisfy any reviewer and drift on the first added
    # stage; sorting by the declaration is what makes the precedence checkable.
    import lifecycle as _lc2

    _cv = _insp.getsource(converge)
    check(
        "the converge loop delegates its order to lifecycle.service_order",
        "_lc.service_order(_roster)" in _cv,
        True,
    )
    check(
        "...which reads lifecycle.drain_order()",
        "drain_order()" in _insp.getsource(_lc2.service_order),
        True,
    )
    # ⚑ THE PRECEDENCE IS ASSERTED BY NAME, NOT BY INDEX — the whole content of this change.
    # These two lines read `drains_before(3, 2)` and `drains_before(2, 1)`, three integers that
    # meant nothing on their own and silently described a DIFFERENT pair of boundaries every
    # time the chain changed length. Resolving the names first means the case follows a chain
    # edit instead of surviving one.
    check(
        "...downstream FIRST — the drain boundary precedes the ingest's",
        _lc2.drains_before(_lc2.boundary_index("reflected"), _lc2.boundary_index("observed")),
        True,
    )
    check(
        "...and NOT the reverse",
        _lc2.drains_before(_lc2.boundary_index("observed"), _lc2.boundary_index("reflected")),
        False,
    )
    # ⚑⚑ EVERY STEP KEY MUST BE A LIVE BOUNDARY — the case that catches a chain RENUMBERING.
    # `converge`'s roster is `{3: retire, 2: promote, 1: ingest}` filtered by `if i in steps`,
    # and that filter turns a stale key into a SILENTLY OMITTED STEP rather than an error:
    # when `consumed` left `LIFECYCLE` on 2026-08-12 the retire key 4 stopped existing and the
    # loop would have ingested and promoted forever without draining, with nothing raising.
    #
    # ⚑ ON THE AST, AND MY FIRST CUT WAS A REGEX THAT UNDERCOUNTED — `^\s+(\d+): \(` found 2
    # of 3 keys, because the first pair sits on the `steps = {` line with no leading run of
    # whitespace before it. It failed loudly here (`got 2 want 3`), but the failure mode of a
    # text scan over a data structure is normally the SILENT one: a reformat moves a key out of
    # the pattern and the census shrinks while still reading green. A dict literal is a `Dict`
    # node; ask for its keys.
    #
    # ⚑ THE IMPORT SITS HERE, ABOVE ITS FIRST USE, AND IT DID NOT — DEFECT FOUND 2026-08-12.
    # `import ast as _ast2` lived 26 lines BELOW this line, inside the `_advance_projection`
    # census block that the queue-tier deletion removed. It worked only because a now-deleted
    # earlier statement had already bound the name; removing that statement exposed
    # `UnboundLocalError: cannot access local variable '_ast2'`. A function-local import is
    # only in scope AFTER it executes, so a deletion ABOVE one can break a use BELOW it that
    # the edit never touched. Read the WHOLE function after any deletion inside it.
    import ast as _ast2

    _cv_keys_ast = _ast2.parse(_insp.getsource(converge).lstrip())
    # ⚑ THE ROSTER IS A TUPLE OF TUPLES NOW, AND THE CENSUS READS IT AS ONE. Each entry is
    # `(boundary-name, side, step-name, work-predicate, action)`; the first three are string
    # constants, which is exactly what an AST census can see and a text scan cannot separate
    # from the prose above it.
    _roster_ast = [
        tuple(c.value for c in e.elts[:3])
        for n in _ast2.walk(_cv_keys_ast)
        if isinstance(n, _ast2.Assign) and any(getattr(t, "id", "") == "_roster" for t in n.targets)
        for e in n.value.elts
    ]
    _step_boundary = {step: b for b, _side, step in _roster_ast}
    check(
        "every converge step names a boundary the chain still declares",
        sorted(set(_step_boundary.values()) - set(_lc2.LIFECYCLE.names())),
        [],
    )
    # ⚑⚑ AND THE CENSUS MUST BE ABLE TO FAIL. Its predecessor asserted `len(_step_keys) ==
    # len(drain_order()) - 1` — a count against the CHAIN's length, which stops being a fact
    # about the roster the moment the two stop moving together (they did: promote and retire
    # now share a boundary, so the roster is LONGER than the non-ε boundary count). What is
    # actually invariant is WHICH STEPS the loop runs, so that is what is asserted; an AST
    # extraction that silently matched nothing gives `[]` and fails here.
    check(
        "...and the census sees all three steps (it must be able to fail)",
        sorted(_step_boundary),
        ["ingest", "promote", "retire"],
    )
    # ⚑ RETIRE SPANS THE CHAIN'S TERMINAL BOUNDARY — derived from `LIFECYCLE`, never typed.
    # This is the case that catches a RENAME of the last link, which is the only edit that can
    # still move retire's boundary now that its INDEX is nobody's business.
    check(
        "...with retire at the chain's terminal boundary",
        _step_boundary["retire"],
        _lc2.LIFECYCLE.names()[-1],
    )
    # ⚑⚑ THE ORDER THE LOOP RUNS IS COMPUTED FROM THE ROSTER THE FILE DECLARES — the two halves
    # joined, so neither can drift alone. `lifecycle.service_order` is driven with the
    # AST-extracted triples, which exercises the name resolver, the drain precedence and the
    # within-boundary tie-break in one case. (Its own REFUSAL cases live in `lifecycle`, beside
    # the chain they quote; duplicating them here would be a second roster of the same rule.)
    check(
        "the declared roster sorts to retire → promote → ingest",
        [e[2] for e in _lc2.service_order(_roster_ast)],
        ["retire", "promote", "ingest"],
    )
    # ⚑ RESTARTING FROM THE TOP AFTER ANY PROGRESS IS THE WHOLE MECHANISM. Without the `break`
    # the loop is a SWEEP — it would service every boundary once per pass, so upstream work
    # could run while downstream still had work, which is precisely the order that makes the
    # resident set the SUM of the tiers instead of the MAX of one.
    check(
        "...restarting from the highest boundary after any progress",
        "break                              # RESTART from the highest boundary" in _cv,
        True,
    )
    # ⚑ THE WORK PREDICATES ARE BOOLEAN RESIDUES, NOT WATERMARK COMPARISONS. Under `NOT EXISTS`
    # an hwm and an lwm are predicates, so the loop reads no cursor and writes no cursor —
    # which is what makes it free of the check-then-act window a stored position creates.
    check(
        "the promote's work predicate is an EXISTS residue",
        "EXISTS" in _insp.getsource(work_promote),
        True,
    )
    check(
        "the retire's work predicate is the compiled licence, not an approximation",
        'SQL["drainable_res"]' in _insp.getsource(work_retire),
        True,
    )
    # ⚑ AN AST CENSUS, NOT A TEXT ABSENCE — and the text form FAILED against correct code here,
    # for the third time in this file. The paragraphs above EXPLAIN why there is no cursor, so
    # they contain every word a `not in source` test looks for. What is asserted is what the
    # code CALLS: no `_advance_projection`, no `hwm`, no `advance`.
    # ⚑ ONE PARSE, REUSED — and the expression that stood here was edit damage, kept as
    # residue in this note rather than in the code: `_ast2.parse(_insp.getdoc.__module__ and
    # _insp.getsource(converge).lstrip())`. `_insp.getdoc.__module__` is the string
    # `"inspect"` — truthy, always — so the `and` was a no-op guard over the same source this
    # block already parsed above. A conjunct that cannot be false is not a guard; it is a
    # leftover that reads as one.
    _cv_ast = _cv_keys_ast
    _called = {
        getattr(c.func, "id", "") or getattr(c.func, "attr", "")
        for c in _ast2.walk(_cv_ast)
        if isinstance(c, _ast2.Call)
    }
    check(
        "...and the loop CALLS no cursor operation at all",
        _called & {"_advance_projection", "hwm", "advance", "advance_readers", "lwm"},
        set(),
    )
    # ⚑⚑ ⟡finalize-retire — THE CASE THAT STOOD HERE WENT WITH ITS SUBJECT (2026-08-22). It read
    # `getsource(finalize_db).index("_gc_orphan_events(") < index("project_sppf(")`, pinning that
    # the GC preceded the fold WITHIN that function. `finalize_db` is deleted — wide, deep and
    # atomic, the granularity the ⟡project-granularity arc exists to undo — so the case now has
    # no subject. Kept as a note rather than silently dropped: the ORDERING it pinned still holds
    # where it matters (`build` runs the projections in the same order), and a reader looking for
    # the retired assertion should find the reason, not a gap.
    #
    # ⚑ AND IT FAILED ON A DOCSTRING BEFORE IT WENT. Documenting the retirement in `finalize_db`'s
    # own docstring made `.index` match the PROSE ahead of the call and inverted the comparison —
    # a source-text assertion reads comments too. That is the hazard of pinning behaviour by
    # `getsource` substring, and it is worth carrying forward to the cases that still do it.
    # ⚑ AND THE PROMOTE MUST BE ADDITIVE, or the loop silently rebuilds the durable tier from
    # the UNDRAINED remainder. That is the failure `drained()` refuses on the destructive path;
    # the additive path is licensed precisely because it does not DROP.
    # ⚑⚑ THE TWO SQL PATHS MUST BOTH BE REACHABLE, or `--compare-paths` compares a thing to
    # itself. `pack_core_sql(materialised=…)` selects the entry-name suffix, so this pins that
    # BOTH spellings are registered and that the default is the optimised one — a regression that
    # dropped the `_mat` entries would otherwise make the comparison silently vacuous while still
    # printing IDENTICAL.
    import query_defs as _qd

    for _nm in (
        "pack_level_summary",
        "pack_level_summary_mat",
        "pack_level_insert",
        "pack_level_insert_mat",
        "obs_heights_distinct",
        "obs_heights_distinct_mat",
    ):
        check("both fold spellings are registered: %s" % _nm, _nm in _qd.INTERN_BUILDERS, True)
    # ⚑ AND THE `_mat` TEXT MUST NOT CARRY THE RECURSION — that is the whole optimisation, and
    # the first compile of these twins DID still emit `WITH RECURSIVE` because one call site
    # passed no argument. A name is not evidence; the compiled text is.
    _mat_sql, _ = QB.sql("pack_level_summary_mat")
    _cte_sql, _ = QB.sql("pack_level_summary")
    check(
        "the materialised entry reads _ht_map, not the recursive CTE",
        ("_ht_map" in _mat_sql and "WITH RECURSIVE" not in _mat_sql),
        True,
    )
    check(
        "...while the CTE entry still derives height inline",
        ("WITH RECURSIVE" in _cte_sql and "_ht_map" not in _cte_sql),
        True,
    )
    # ⚑ THE COMPARISON'S OWN F-ARM: a trace diff that cannot report a difference is the
    # both-empty shape `do_equiv` refuses. Pure, so it needs no store.
    check("an identical trace compares equal", [(0, 5, 2, 2)] == [(0, 5, 2, 2)], True)
    check(
        "...and a differing level is detected, not smoothed",
        [(0, 5, 2, 2)] == [(0, 5, 3, 3)],
        False,
    )

    check("the converge promote is additive", "additive=True" in _cv, True)
    check(
        "...and the destructive path still meets the drained() guard",
        "if not additive:" in _ps and "_schema.drained(con)" in _ps,
        True,
    )
    # ⚑ RESUMABILITY IS A PROPERTY OF WHERE THE REMAINING WORK IS READ FROM. A Python list of
    # cores still to do is a SECOND cursor that dies with the process; `terms ⋈ core_fp` is the
    # store's own. Asserted on the call, because "it resumes" is not observable from one run.
    check(
        "the ingest's remaining work is derived from the store, not held",
        "_ingested_relpaths(con)" in _cv,
        True,
    )
    # ⚑ THE SURROGATE NUMBERING MUST BE SEEDED, and this is the case that would have caught
    # the corruption. `node_id` is minted `str(len(node_ids) + 1)` — exact ONLY over a dropped
    # destination. Re-running additively without a seed gives signature S a node_id that
    # already denotes a DIFFERENT signature, `upsert(…, 'ignore')` keeps the old row, and
    # `obs_node` addresses the wrong node. No constraint fires; nothing errors.
    check(
        "the additive promote seeds its surrogate ids from the store",
        "_seed_node_ids(con)" in _ps,
        True,
    )
    # ⚑ A POSITIVE CHECK ON THE MINT LINE, NOT AN ABSENCE CHECK ON THE OLD SPELLING. My first
    # cut asserted `"len(node_ids) + 1" not in source` and FAILED against correct code — the
    # paragraph two functions up QUOTES the retired spelling to explain why it is retired. Same
    # class as the `WHERE a.clid IS NULL` case above: a text scan cannot tell code from prose
    # about the code, so the assertion must name what the code DOES.
    check(
        "...and mints from that seeded counter",
        any(l.strip() == "_nid = str(_next); _next += 1" for l in _ps.splitlines()),
        True,
    )
    # ⚑ A PER-CORE PRUNE WOULD DELETE THE CORPUS: `removed = stored - the set I was handed`,
    # and the ingest step hands over ONE core. Asserted on the CALL, not on a comment about it.
    check("the per-core ingest never prunes", "prune=False" in _cv, True)

    # ── obs_node: the addressing the projection used to discard ──────────────────────
    # ⚑ THE VALUE WAS COMPUTED ON EVERY RUN AND THROWN AWAY. `packing` is
    # `(core_id, local_id) → node_id`, built by `pack()` for every observation, and until now
    # it died with the function. Its absence is what held the drain: `reflects_obs` could not
    # verify a single core, so the reconstruction gate refused while the queue would have
    # permitted 1,255,689 deletions. A guard on the WRITE, because a discarded computation
    # regresses silently — nothing downstream errors, the map is just empty again.
    _ps = _insp.getsource(project_sppf)
    check("project_sppf persists the packing map", 'upsert(con, "obs_node"' in _ps, True)
    check("...from `packing`, not a re-derivation", "packing.items()" in _ps, True)
    # ⚑ AND THE CONSUMER MUST READ IT, or persisting is decoration. `reflects_obs` asked a
    # PROXY question (is the ekey's head symbol in `_node.sym`) precisely because the real
    # map did not exist; that proxy failed for every core.
    # ⚑ ANCHORED ON THE COMPILED BUILDER, NOT ON `reconstruct`'s SOURCE — and the move is the
    # lesson. This case read `"FROM obs_node" in getsource(reconstruct)` and BROKE when ⓙ
    # relocated that SQL into `query_defs.q_obs_reconstructed`, where it belongs. The claim
    # ("the reconstruction goes through the stored addressing, not the `sym` proxy") is now
    # MORE true than when the case was written; only its carrier moved.
    #
    # ⚑ A GUARD ANCHORED ON *WHERE* CODE LIVES BREAKS WHEN CODE MOVES; ONE ANCHORED ON *WHAT
    # IT DOES* SURVIVES THE REFACTOR IT SHOULD SURVIVE. Third instance today of a source-scan
    # guard firing on a relocation rather than a regression — the sibling of the
    # obituary-matching class, where prose SATISFIES a scan instead of breaking it.
    import query_builders as _qb

    _link_sql, _ = _qb.SQL["obs_reconstructed"]
    check("the reconstruction reads obs_node, not the sym proxy", "obs_node" in _link_sql, True)
    check("...joining the interned head by node_id", "_node.node_id" in _link_sql, True)
    check("...and never the `sym` proxy that failed for every core", "sym" in _link_sql, False)

    # ⚑ THE ENTRY POINTS THAT MAKE THE RECOVERY REACHABLE MUST EXIST. Verified END-TO-END
    # against the SANDBOX tenant (2026-08-07): `--ingest-core <core> --full --sandbox` on
    # `V4-as-PFG.agdai` gave `idx_populated = 1383` and `var_events = 1383` — every Var/PVar
    # recovered its index and nothing else acquired one — with a real de Bruijn distribution
    # (0:289, 1:150, 2:118, 3:140, …), not a constant. That is the data that had been
    # collapsing to the single role `"dbNone"`.
    #
    # ⚑ AND NEITHER FLAG EXISTED BEFORE, WHICH IS WHY THE FIX WAS UNVERIFIABLE. The mtime
    # self-skip is keyed on the SOURCE, so a DECODER change could not be re-run; and every
    # ingest path hardcoded the live store, so the only way to re-check one core was
    # `build(full=True)` dropping the whole tier. A guard on their presence, because a
    # capability with no caller is the shape this repo keeps paying for.
    import inspect as _inspect

    _sig = _inspect.signature(ingest_core).parameters
    check("ingest_core can force a re-decode (shim changed, mtime did not)", "force" in _sig, True)
    check("ingest_core can target the throwaway tenant", "sandbox" in _sig, True)
    _main = _inspect.getsource(sys.modules[__name__]).split("if __name__ ==")[-1]
    # ⚑ THE SPELLING MOVED WITH ⟡no-automated-drop: `force=full` → `force=_force_redecode`.
    # `--full` meant TWO things — force-redecode on `--ingest-core`, and a six-table DROP on
    # `build` — so the destructive sense was removed and the surviving one renamed to say what
    # it does. This case guards the CAPABILITY (a re-decode is reachable from the CLI) and was
    # written against the SPELLING, so a rename fails it while the capability is intact.
    #
    # ⚑⚑ THAT IS THE SAME BRITTLENESS `finalize_db`'s retired case had, and it is the second
    # instance in one session: a `getsource` substring assertion pins TEXT and reads as pinning
    # BEHAVIOUR. Kept — the end-to-end verification it records is real and a capability with no
    # caller is the shape this repo keeps paying for — but the anchor is now the FLAG the CLI
    # accepts rather than a variable name, which survives the next rename.
    check(
        "...and BOTH are reachable from the CLI",
        ("--force-redecode" in _main) and ("--sandbox" in _main),
        True,
    )

    # ⚑⚑⚑ THE REPORTER IS EXERCISED BEFORE IT IS TRUSTED. A green suite says NOTHING about the
    # failure path — the reporting change that adds `at <file:line>` is invisible until something
    # fails, which is the census-green-is-a-fact-about-the-census shape applied to a formatter.
    # `--selftest-demo-failure` drives ONE deliberate failure so the output can be READ, and it
    # is a flag rather than a permanent failing case because a suite that never reports 0 failures
    # cannot be used as a gate.
    if "--selftest-demo-failure" in sys.argv:  # toolmodes:fixture
        check("DEMO: this case fails on purpose, to exercise the reporter", 1, 2)
    failed = [c for c in cases if not c[1]]
    # ⚑ THE LOCATION IS ON ITS OWN LINE, under the failure rather than appended to it. A label
    # here is a SENTENCE (*"...and BOTH are reachable from the CLI"*), so a trailing `file:line`
    # runs past the terminal width and is the first thing a wrapped line loses.
    for label, _, got, want, where in failed:
        print("  FAIL %s: got %r want %r" % (label, got, want))
        print("       at %s" % where)
    print("selftest: %d/%d" % (len(cases) - len(failed), len(cases)))
    return 0 if not failed else 1


# selftest-tenant: sandbox
# ⚑ ⟡tenant-pragma — `run_selftests._tenant` reads this and appends the flag. `store.tenant`
# exits 2 on an unstated tenant since ⟡tenant-mandatory (2026-08-24); SANDBOX because this
# tool's write path is the promote/retire chain over a 62GB live corpus, and a suite that
# reaches it can delete staged rows the licence has not yet cleared.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    orbit = "--orbit" in sys.argv
    distribute = "--distribute" in sys.argv
    argperm = "--argperm" in sys.argv
    # ⚑⚑ ⟡no-automated-drop — `--full` NO LONGER DROPS ANYTHING, AND IT USED TO MEAN TWO THINGS.
    # On `--ingest-core` it meant *"re-decode this core even if its mtime is unadvanced"* (the
    # shim-changed case, non-destructive); on `build` it dropped SIX TABLES. One flag, a benign
    # sense on one path and a tier-drop on the other, which is why it could not be trusted
    # (operator, 2026-08-22: *"Let's get rid of --full. I'm not ready to trust it."*).
    #
    # ⚑ THE DESTRUCTIVE SENSE IS GONE; the force-redecode survives under its own name so the
    # remaining flag says what it does. `--full` is still accepted as an alias and REPORTS the
    # change rather than silently doing half of what it used to.
    _force_redecode = ("--force-redecode" in sys.argv) or ("--full" in sys.argv)
    if "--full" in sys.argv:
        print(
            "⚑ --full now means ONLY 'force re-decode of this core' (⟡no-automated-drop).\n"
            "  Its tier-dropping sense is REMOVED: it no longer drops event/obs/edge/\n"
            "  unit_obs/unit_member/core_fp. Rebuilding a tier is a deliberate singleton act:\n"
            "    python3 jea/metalanguage/schema.py --flush <TIER> --live --apply\n"
            "  Prefer the unambiguous spelling: --force-redecode",
            file=sys.stderr,
        )
    base = substrate_core_root(os.path.join(_ROOT, "agda"))
    # ⟡gqs-make-targets: per-core make-driven ingest. `catalog` = --init → (make -j ingest → --ingest-core per
    # file) → --finalize. Each ingest is WAL-serialized (parallel decode, serialized insert); one project pass.
    if "--init" in sys.argv:
        init_db()
        sys.exit(0)
    if "--ingest-core" in sys.argv:
        # `--force-redecode` (formerly `--full`) means "re-decode this core even if its mtime is
        # unadvanced" — the shim-changed case. It does NOT drop the tier, and as of
        # ⟡no-automated-drop NOTHING on this path does: `build(full=True)`'s six-table drop is
        # removed. This comment used to end *"only `build(full=True)` does that"*, which is the
        # sentence that made one flag read as two semantics.
        _p = sys.argv[sys.argv.index("--ingest-core") + 1]
        # ⚑ THE THIRD MAKE-DRIVEN WRITER, AND THE ONE THAT DOES NOT SHARE THE PROLOGUE — it
        # takes its tenant as a `sandbox=` bool rather than through `store.tenant`, which is
        # why `gen_build_makefiles` records `--live` as *"accepted and does nothing"* on this
        # path. The mutation axis is checked here explicitly so all three writers refuse
        # alike; the TENANT half stays as it is, since consolidating that dispatch is
        # substrate-ff's open work and not this edit's.
        _require_mutation_stated("sppf_db --ingest-core")
        if "--dry-run" in sys.argv:
            print("  plan  ingest_core(%s) — re-run with --apply" % _p)
            sys.exit(0)
        _why = ingest_core(_p, base=base, force=_force_redecode, sandbox="--sandbox" in sys.argv)
        # ⚑⚑ ⒯ — THE GATE. An undecodable core FAILS, naming the module and the TYPED reason.
        # `_why` is `decode_reason`'s `kind: detail`, so `decode-nothing` (Agda REFUSED the
        # interface — the CORE is the problem, rebuild it) stays distinct from `shim-exit-N`
        # (the decoder could not RUN — the TOOL/environment is the problem). Collapsing them
        # would have read a broken Agda data-directory as thousands of rotten interfaces.
        #
        # ⚑ THE DISTINCTION IS IN THE EXIT CODE, NOT ONLY THE TEXT — reusing the convention
        # `ingest_source` already established (sppf_decode: *"EXIT 3, NOT 1 … an undecodable
        # core is a fact about the CORE; a non-zero exit from the writer is a fact about the
        # WRITE"*), because a build log's failure code has to be actionable without parsing
        # prose. 3 = the CORE (rebuild it); 4 = the TOOL (the shim could not run, and NOTHING
        # about the corpus follows from it — 3,479 of these mean one broken decoder, not 3,479
        # bad interfaces).
        if _why:
            print("sppf_db --ingest-core: %s\n  %s" % (_p, _why), file=sys.stderr)
            sys.exit(3 if _why.startswith("decode-nothing") else 4)
        sys.exit(0)
    # ⚑⚑ ⟡sql-lift — THE LEVEL SCHEDULE, MEASURED PER CORE. `project_sppf`'s packing fold is not
    # one `WITH RECURSIVE` (postgres bans GROUP BY / aggregates / window fns in a recursive
    # term, and the fold needs all three), so it runs as one set-based statement PER HEIGHT.
    # This reports the schedule that staging would follow — how many rounds, and how the work
    # distributes across them — WITHOUT writing anything.
    #
    # ⚑ IT IS A MODE RATHER THAN A PROBE because the answer decides the shape of the lift, and a
    # `--probe` cannot pass a bindparam (`do_explain`'s own note: *"the compiled builders carry
    # named %(param_N)s placeholders, so schema.py --probe cannot run one"*).
    if "--height" in sys.argv:
        _i = sys.argv.index("--height")
        _cid = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        con = _store.tenant(mode="ro", label="sppf_db --height")
        if _cid is None:
            print("sppf_db --height <core_id> [--sandbox|--live]", file=sys.stderr)
            sys.exit(2)
        _rows = list(QB.run(con, "obs_height", core_id=_cid))
        if not _rows:
            # ⚑ AN EMPTY SCHEDULE IS A REFUSAL, NOT A ZERO. A core with no observations would
            # otherwise report "max height 0, 0 rounds" — which reads as a converged core rather
            # than an absent one. Same shape as `reflects_obs`' recorded trap, where an empty
            # core passed a reconstruction gate with "0 row(s) reconstructed exactly".
            print(
                "sppf_db --height: core %r has NO observations — the schedule is UNMEASURED, "
                "not empty. Ingest it first." % _cid,
                file=sys.stderr,
            )
            sys.exit(3)
        _hist = {}
        for _r in _rows:
            _h = _r[2]
            _hist[_h] = _hist.get(_h, 0) + 1
        _tot, _mx = len(_rows), max(_hist)
        print("⟡sql-lift LEVEL SCHEDULE — core %s" % _cid)
        print("  %d observation(s) · max height %d · %d round(s)" % (_tot, _mx, _mx + 1))
        _cum = 0
        for _h in sorted(_hist):
            _cum += _hist[_h]
            print("    ht %-3d %8d  %5.1f%% cumulative" % (_h, _hist[_h], 100.0 * _cum / _tot))
        sys.exit(0)

    # ⚑⚑ ⟡sql-lift — ONE LEVEL OF THE PACKING FOLD, READ-ONLY. Runs `pack_level` for a core at a
    # height and reports the SHARING COLLAPSE: how many observations at that level, and how many
    # distinct node ids they intern to. That ratio is the whole value of the fold, and it is what
    # the python loop computes with one dict lookup per observation.
    #
    # ⚑ IT WRITES NOTHING. The statement is a SELECT; making it an INSERT is the next step and
    # wants the equivalence check in place first — a fold that writes before it is compared is
    # a fold whose disagreement with the python is undiscoverable.
    if "--pack-level" in sys.argv:
        _i = sys.argv.index("--pack-level")
        _cid = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        _h = int(sys.argv[_i + 2]) if _i + 2 < len(sys.argv) and sys.argv[_i + 2].isdigit() else 0
        if _cid is None:
            print("sppf_db --pack-level <core_id> [<height>] [--sandbox|--live]", file=sys.stderr)
            sys.exit(2)
        con = _store.tenant(mode="ro", label="sppf_db --pack-level")
        _rows = list(QB.run(con, "pack_level", core_id=_cid, ht=_h, base=0))
        if not _rows:
            # ⚑ EMPTY IS A REFUSAL, NOT A ZERO — the same distinction `--height` makes. A level
            # with no observations and a core that was never ingested both print nothing, and
            # only one of them is a fact about the fold.
            print(
                "sppf_db --pack-level: core %r has NO observations at height %d — UNMEASURED, "
                "not empty. Check `--height %s` for the schedule." % (_cid, _h, _cid),
                file=sys.stderr,
            )
            sys.exit(3)
        # ⚑⚑⚑ WHICH SIGNATURE COMPONENTS CAN ACTUALLY DISCRIMINATE HERE? A component that is
        # CONSTANT across the population contributes nothing to the grouping — so an equivalence
        # check over this data cannot detect its omission. Measured: `idx` is NULL in ALL
        # 2,124,418 event rows and `qname_pid` in 2,124,408 of them, which is exactly why a first
        # version of `q_pack_level` that DROPPED `idx` from the key passed three identical
        # verdicts while silently collapsing de Bruijn indices.
        #
        # ⚑ REPORTING IT BESIDE THE COLLAPSE RATIO is the point: a reader seeing "IDENTICAL" and
        # a 47:1 ratio has no way to know the key was never exercised on two of its five fields.
        # ⚑⚑⚑ THE VERDICT'S OWN STRENGTH, measured per component at THIS height — `q_pack_discrimination`.
        # A signature component taking ONE value at a level cannot separate any two nodes there,
        # so an IDENTICAL equivalence verdict over that level does not establish the key needs it.
        # Measured instance: a first `q_pack_level` dropped `idx` (the de Bruijn role,
        # `sppf_db.py:754`) and passed THREE identical verdicts across two cores and three heights.
        #
        # ⚑ IT IS A BUILDER, after two wrong attempts here: one counting non-NULL `idx` over the
        # WHOLE CORE (the fold groups within a HEIGHT, so core-level variation proves nothing),
        # and one that `.replace()`d the compiled text of `obs_height` to scope it — the
        # compiled-artifact-wrapped-by-hand form both the operator and this file's own AST guard
        # refuse, written while composing a comment about having learned that.
        _lv = list(QB.run(con, "pack_discrimination", core_id=_cid, ht=_h))[0]
        _ids = {r[2] for r in _rows}
        print("⟡sql-lift PACK LEVEL — core %s, height %d" % (_cid, _h))
        print(
            "  %d observation(s) → %d distinct node id(s)   (%.1f:1 sharing collapse)"
            % (len(_rows), len(_ids), len(_rows) / len(_ids))
        )
        _comp = (
            ("ctor_id", _lv[1]),
            ("qname_pid", _lv[2]),
            ("idx", _lv[3]),
            ("lit_id", _lv[4]),
            ("children", _lv[5]),
        )
        print(
            "  signature discrimination at this height:  %s"
            % " · ".join("%s=%d" % (n, v) for n, v in _comp)
        )
        _blind = [n for n, v in _comp if v <= 1]
        if _blind:
            print(
                "  ⚑ BLIND ON: %s — %s ONE distinct value at this height, so an equivalence"
                % (", ".join(_blind), "each takes" if len(_blind) > 1 else "it takes")
            )
            print(
                "     verdict here CANNOT detect %s omission from the key. A fact about this"
                % ("their" if len(_blind) > 1 else "its")
            )
            print("     LEVEL's data, never about the fold. (`idx` dropped from the key passed 3.)")
        # ⚑⚑⚑ ⟡slice-ht0-witness — THE COMMIT GRAIN, BESIDE THE COLLAPSE. `_pack_level_sliced`
        # emits this level in `SLICE_ROWS`-wide `local_id` WINDOWS, one transaction each, and its
        # own docstring names the commit count as the only evidence the slicing works — because
        # `--equiv` compares the PARTITION and is IDENTICAL either way, BY CONSTRUCTION. So a
        # reader validating the slicing on a level that fits in ONE window is reading a verdict
        # that could not have failed, which is the same defect the BLIND-ON block above exists to
        # refuse, one layer out. Printed here so the witness carries its own slice count.
        #
        # ⚑ COMPUTED FROM THE SPAN, NOT BY RUNNING THE WRITER — this mode is read-only (a SELECT,
        # never an INSERT) and must stay so. The writer steps `lo` by `slice_rows` over
        # `[min(local_id), max(local_id)]`, so the count is a property of the SPAN and needs no
        # write to observe. ⚑ It is the SPAN and not the ROW COUNT: `local_id` is the shim's print
        # counter over the whole core, so a level's ids are SPARSE within their range — 176,818
        # rows spread over a wider span take MORE windows than `rows/SLICE_ROWS` predicts, and
        # reporting the ratio would understate the grain.
        _lids = [r[1] for r in _rows]
        _span = max(_lids) - min(_lids) + 1
        _w = -(-_span // SLICE_ROWS)
        print(
            "  commit grain: %d window(s) of %s local_id(s) over a span of %d  (%s)"
            % (
                _w,
                format(SLICE_ROWS, ","),
                _span,
                "GENUINELY SLICED"
                if _w > 1
                else "⚑ ONE WINDOW — an equivalence PASS here does NOT exercise the slicing",
            )
        )
        # ⚑⚑⚑ WHOSE IDS DID THE CHILDREN COME FROM? A level above 0 reads its children's node
        # ids out of `obs_node` — and if a PREVIOUS (python) run already populated that table,
        # this statement is reading THAT, not composing on its own previous level. The number
        # above is then a true sharing collapse and a FALSE demonstration of staging.
        #
        # ⚑⚑ MEASURED 2026-08-14: every core in the sandbox is already fully packed (7013 of
        # 7013 observations carry a node_id, and no core exists with obs but zero ids), so the
        # fixture CANNOT falsify the composition claim. That is a fact about the fixture, not
        # about the fold — reported here so a green level is not read as a verified staging.
        # The honest test needs an unpacked core, or a level run into a scratch relation.
        if _h > 0:
            _pre = _schema.scalar(
                con,
                "SELECT count(*) FROM obs o JOIN obs_node n ON n.core_id=o.core_id "
                "AND n.local_id=o.local_id WHERE o.core_id=%s" % _schema.ph(),
                (_cid,),
            )
            print(
                "  ⚑ children's ids came from `obs_node`, which already holds %s row(s) for "
                "this core.\n     This level is NOT composed from level %d's output — it reads "
                "a PRE-EXISTING\n     packing. Staging is unverified until a level runs against "
                "an UNPACKED core." % (format(_pre or 0, ","), _h - 1)
            )
        sys.exit(0)

    # ⚑⚑⚑ ⟡sql-lift — THE TWO SQL PATHS, COMPARED READ-ONLY. `pack_core_sql` now runs the
    # MATERIALISED entries (height read from a per-core temp map) and the equivalence gate's arms
    # both read the recursive CTE — deliberately, so `--equiv` can never depend on the
    # optimisation it verifies. The consequence is that NOTHING compared the optimised fold's
    # output against anything: its correctness rested on a structural argument (one shared body,
    # one varying stage) where a measurement was available.
    #
    # ⚑⚑ `--refold` IS THE DESIGNED INSTRUMENT AND IT CANNOT BE DRIVEN HERE — it DELETEs, so it is
    # sandbox-only by construction, and the sandbox holds none of the live cores. A gate that
    # exists and cannot be run over the population that matters is not coverage.
    #
    # ⚑ SO: BOTH PATHS, `write=False`, SAME CORE, SAME CONNECTION. Neither writes; the diff is
    # per-level `(ht, n, ids, top)`, which is the whole observable of the fold — how many rows a
    # level packed, how many distinct ids it minted, and what the counter advanced to. Identical
    # traces mean the two spellings computed the same fold; a difference NAMES the level.
    if "--compare-paths" in sys.argv:
        _i = sys.argv.index("--compare-paths")
        _cid = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        if _cid is None:
            print("sppf_db --compare-paths <core_id> [--sandbox]", file=sys.stderr)
            print(
                "  runs the packing fold BOTH ways (materialised map vs recursive CTE), "
                "read-only,\n  and diffs the per-level trace. Writes nothing.",
                file=sys.stderr,
            )
            sys.exit(2)
        # ⚑⚑ `rw` THOUGH THIS MODE WRITES NO DATA, and the distinction is worth stating rather
        # than widening silently. `pack_core_sql` issues two pieces of DDL before any level runs:
        # `apply(only="obsnode")` (idempotent CREATE IF NOT EXISTS) and the per-core TEMP table.
        # A read-only transaction refuses both — correctly, since it cannot tell DDL that
        # establishes a destination from DDL that destroys one.
        # ⚑ WHAT MAKES IT SAFE IS `write=False`, NOT THE CONNECTION MODE: every level runs
        # `pack_level_summary*`, which SELECTs and returns three numbers. No INSERT is reachable
        # from this branch, and the temp table dies with the connection. The mode is the honest
        # declaration of what the statements need; the read-only-ness is a property of the loop.
        con = _store.tenant(mode="rw", label="sppf_db --compare-paths")
        _obs = _schema.scalar(
            con, "SELECT count(*) FROM obs WHERE core_id=%s" % _schema.ph(), (_cid,)
        )
        if not _obs:
            print(
                "sppf_db --compare-paths: core %r holds NO observations — UNMEASURED, not "
                "equal." % _cid,
                file=sys.stderr,
            )
            sys.exit(3)
        print(
            "⟡sql-lift COMPARE PATHS — core %s [%s]"
            % (_cid, "sandbox" if "--sandbox" in sys.argv else "LIVE, read-only")
        )
        _a = pack_core_sql(con, _cid, base=0, write=False, materialised=True)
        _ta = list(_PackTrace.last)
        _b = pack_core_sql(con, _cid, base=0, write=False, materialised=False)
        _tb = list(_PackTrace.last)
        print(
            "  materialised  %d level(s) · %s row(s) · %d id(s) · top %d"
            % (_a[0], format(_a[1], ","), _a[2], _a[3])
        )
        print(
            "  recursive CTE %d level(s) · %s row(s) · %d id(s) · top %d"
            % (_b[0], format(_b[1], ","), _b[2], _b[3])
        )
        # ⚑ AN EMPTY TRACE ON BOTH SIDES IS NOT AGREEMENT — the both-empty refusal `do_equiv`
        # carries, one layer over. A core whose levels all packed zero rows would compare equal
        # while measuring nothing.
        if not _ta and not _tb:
            print(
                "  ⚠ BOTH TRACES EMPTY — UNMEASURED, not equal. Nothing was compared.",
                file=sys.stderr,
            )
            sys.exit(3)
        if _ta == _tb:
            print(
                "  ⚑ IDENTICAL — %d level(s) agree on (ht, rows, ids, top) at every level."
                % len(_ta)
            )
            sys.exit(0)
        print("  ⚠ DIFFER — the two spellings are NOT the same fold:", file=sys.stderr)
        _da = {r[0]: r for r in _ta}
        _db = {r[0]: r for r in _tb}
        for _h in sorted(set(_da) | set(_db)):
            if _da.get(_h) != _db.get(_h):
                print(
                    "      ht %-4s mat=%r cte=%r" % (_h, _da.get(_h), _db.get(_h)), file=sys.stderr
                )
        sys.exit(1)

    # ⚑⚑⚑ ⟡sql-lift — THE PYTHON FOLD, SCOPED TO ONE CORE. This is the REFERENCE ARM's producer:
    # `--equiv pack.sql pack.python` compares the SQL fold against `obs_node`, and only
    # `project_sppf` writes that. Without a per-core route the only way to produce a reference for
    # a 6,210-row trial core was to fold all 152 and 6,274,182 observations — i.e. to perform ⑤c
    # in order to gate ⑤a.
    #
    # ⚑⚑ ADDITIVE ONLY, AND THE FUNCTION ITSELF REFUSES OTHERWISE. The non-additive prologue DROPs
    # `unit_node`/`node_child`/`_node`/`_unit`/`_unit_cod` — corpus-wide relations — so scoping the
    # READS while dropping the DESTINATION would delete 151 cores' projections to rebuild one.
    # `project_sppf` raises on that combination rather than silently upgrading; this mode passes
    # `additive=True` explicitly so the refusal is never reachable from here by accident.
    #
    # ⚑ IT WRITES, SO IT SAYS SO AND TAKES `--apply`. `--refold` (below) is sandbox-only because it
    # DELETES; this one only accumulates, which is what makes it safe against the live corpus —
    # but "safe" is not "silent", and a write mode that runs bare is the shape `--establish` was
    # just built to avoid.
    # ⚑⚑⚑ ⟡converge-scheduled — THE PROMOTE AS A DEPENDENCY EDGE, path-taking like `--ingest-core`.
    #
    # `all` already wires INGEST into the build as a real-file stamp (`<Mod>.ingested :
    # <Mod>.agdai`), so boundary 0 is serviced per module and ordered by the import DAG.
    # Boundary 1 had no equivalent and ran only when someone typed it: MEASURED, `obs` reached
    # 128,366,355 rows against 1,137,510 interned — **0.89%** — and every gate that syncs the
    # store paid that backlog as latency.
    #
    # ⚑⚑ A STAMP CHAIN, NOT A PHONY TARGET, AND THE FILE ALREADY ARGUES WHY. A `.PHONY` target is
    # always-run, so it carries no staleness and make can order nothing against it — the exact
    # reasoning that replaced the old `i/<Mod>` phony recipes with a real-file stamp. `<Mod>.agdai
    # → <Mod>.ingested → <Mod>.promoted` is incremental by construction and parallel under `-j`.
    #
    # ⚑⚑ AND THE STAMP DESCRIBES THE CHAIN, NOT THE STORE — which is what makes it legitimate. I
    # first argued the promote *"has no filesystem claim to hang staleness on"* because it is
    # per-CORE while ingest is per-MODULE. That is a false distinction: `ingest_core` resolves ONE
    # `.agdai` to ONE core, so module↔core is 1:1 and the stamp is well-defined. The reconciler
    # that already deletes lying `.ingested` stamps extends to this one by the same query.
    #
    # ⚑⚑⚑ NO SHARD PREDICATE, AND THAT IS A RULING, NOT AN OMISSION (operator, 2026-08-21: *"The
    # --shards design was wrong. We obsoleted it when we shifted to multiple commits per
    # promote."*). `--shards` existed because the promote was ONE ATOMIC ACT per core, so N
    # residue-driven workers all asked *"which core is next"* and got the same largest-first head
    # — folding one core N times while `ON CONFLICT DO NOTHING` swallowed the duplicates and the
    # run REPORTED SUCCESS. The shard predicate partitioned the CHOICE. **Under make, the choice
    # is make's**: each module is one target and make never runs a target twice. There is nothing
    # left to partition.
    #
    # ⚑ EXIT 3 / 4, MIRRORING `--ingest-core`, so `touch $@` never runs on a failure and the
    # module is retried next build. A stamp is only ever created by a promote that succeeded.
    if "--promote-core" in sys.argv:
        _i = sys.argv.index("--promote-core")
        # ⚑ `_pc` AND NOT `_p` — the name is already bound as `str` by the `--ingest-core` block
        # above, so rebinding it to `str | None` is a type error at the SECOND assignment, not a
        # defect in the guard below (which is correct). MEASURED: `mypy scripts/sppf_db.py` →
        # *"Incompatible types in assignment (expression has type 'str | None', variable has
        # type 'str')"* at this line. Surfaced only because `mypy_ratchet_baseline.txt` went
        # ABSENT → EMPTY today; before that the gate exited 0 while reporting nothing, so a new
        # error was indistinguishable from a clean file.
        _pc = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        if _pc is None:
            print("sppf_db --promote-core <core.agdai|source.agda> [--sandbox]", file=sys.stderr)
            print(
                "  the packing fold over the ONE core that path names, additive. The make-driven"
                " twin of --ingest-core.",
                file=sys.stderr,
            )
            sys.exit(2)
        _cid, _con = _core_id_for_path(_pc, "sppf_db --promote-core")
        if _cid is None:
            sys.exit(0)  # not built or not ingested — see the helper
        # ⚑ THE GUARD REFUSES AN UNSTATED AXIS; HONOURING `--dry-run` IS THE OTHER HALF.
        # A mode that demands the flag and then writes either way would make the contract a
        # formality — the refusal and the behaviour have to be the same decision.
        if "--dry-run" in sys.argv:
            print(
                "  plan  promote_core_a3(core_id=%s) — pack server-side, then build_units; "
                "re-run with --apply" % _cid
            )
            _con.close()
            sys.exit(0)
        # ⚑⚑⚑ ⟡a3-route-pack-only — A3, NOT A2 (2026-08-22). This called
        # `project_sppf(additive=True, core_id=…)`, which under `make -j 20 promote` deadlocked
        # two workers on `DELETE FROM obs_node WHERE core_id=$1` (both waiting on
        # RowExclusiveLock on one relation — per-core scoping does not help, the lock is at
        # relation granularity) and dragged `event`'s 25.4M rows across the wire per core.
        # `promote_core_a3` is `converge`'s path — the sequence-allocated, height-windowed,
        # index-only fold — plus the unit stage A3 does not do. `--opt-a2` keeps the old route
        # reachable for the `--equiv` reference arm rather than deleting a live comparison arm.
        if "--a2" in sys.argv:
            project_sppf(_con, additive=True, core_id=_cid)
            _con.commit()
            _con.close()
            sys.exit(0)
        _lv, _rows, _ids, _top = promote_core_a3(_con, _cid)
        _con.close()
        sys.exit(0)

    # ⚑⚑⚑ ⟡drained-stamp — THE FIFTH AND LAST LINK: `.promoted → .drained`.
    # `<Mod>.agdai → .ingested → .promoted → .drained`. A module is not finished at its
    # interface, nor at its internment, nor at its projection — it is finished when the staged
    # copy it no longer needs has been RECLAIMED. Ingest and promote are dependency edges;
    # without this one the drain remains the step someone remembers, which is how `edge` reached
    # 128M rows while `obs` returned to 0 after every core.
    #
    # ⚑⚑ THE LICENCE DECIDES, NOT THE STAMP. This calls `reclaim_core`, which asks
    # `drainable_res.one_core` — the SAME five conjuncts the corpus sweep asks, narrowed to one
    # core and MEASURED equal to the shipped licence over the A–F fixture, per core, including
    # the refused ones. A core the licence holds is simply not drained and the stamp is still
    # written: being held is the gate working, not a failure (`converge`: *"a held core is not
    # an error and must not stall the loop"*).
    #
    # ⚑ SO THE STAMP MEANS "THE LICENCE WAS ASKED", NOT "THE ROWS WENT". That is the honest
    # reading and it is what makes the edge idempotent: a held core is re-asked on the next
    # build only if something upstream re-ran, and a core that drained has no `obs` rows left to
    # delete. Writing the stamp only on a successful DELETE would re-ask every held core on
    # every build forever — a work predicate reporting work it does not consume.
    if "--drain-core" in sys.argv:
        _i = sys.argv.index("--drain-core")
        _dc = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        if _dc is None:
            print("sppf_db --drain-core <core.agdai|source.agda> [--sandbox]", file=sys.stderr)
            print(
                "  retire ONE core's staged rows IF the licence admits it. The make-driven"
                " twin of --reclaim-core.",
                file=sys.stderr,
            )
            sys.exit(2)
        _dcid, _dcon = _core_id_for_path(_dc, "sppf_db --drain-core")
        if _dcid is None:
            sys.exit(0)  # not ingested yet — nothing to drain
        import schema_queue as _sq

        # ⚑ `reclaim_core` ALREADY TAKES `dry_run` AND THIS SITE HARDCODED `False` — so the
        # capability to not-delete existed and the CLI could not reach it. That is the
        # dispatch-branch-never-added shape (`split_pipeline.rewire_only`, written with a
        # 354-consumer justification and zero callers), on the axis where it deletes rows.
        _dr = _sq.reclaim_core(_dcid, con=_dcon, dry_run=("--dry-run" in sys.argv))
        _dcon.close()
        sys.exit(0)

    if "--project-core" in sys.argv:
        _i = sys.argv.index("--project-core")
        _cid = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        if _cid is None:
            print("sppf_db --project-core <core_id> [--apply] [--sandbox]", file=sys.stderr)
            print(
                "  the PYTHON packing fold over ONE core, additive. Without --apply: reports "
                "what it would read.",
                file=sys.stderr,
            )
            sys.exit(2)
        # ⚑ READ-ONLY UNLESS `--apply`, and the default is a GATE that fired here exactly as it
        # did on `schema.py --establish`: `connect()` handed back an `ro` transaction and
        # `project_sppf`'s `apply(only="sppf")` died with `ReadOnlySqlTransaction`. A dry run must
        # not be ABLE to write — otherwise the plan/apply split is a convention, not a bound.
        # ⚑ THE `mode` STAYS CONDITIONAL ON `--apply` — that is the read-only-unless-applying
        # gate the note above records, and it is orthogonal to WHICH TENANT. The resolver owns
        # the tenant; this expression owns the write licence.
        con = _store.tenant(
            mode="rw" if "--apply" in sys.argv else "ro", label="sppf_db --project-core"
        )
        _n_obs = _schema.scalar(
            con, "SELECT count(*) FROM obs WHERE core_id=%s" % _schema.ph(), (_cid,)
        )
        _pre = _schema.scalar(
            con, "SELECT count(*) FROM obs_node WHERE core_id=%s" % _schema.ph(), (_cid,)
        )
        print(
            "⟡sql-lift PROJECT-CORE — %s [%s]"
            % (_cid, "sandbox" if "--sandbox" in sys.argv else "LIVE")
        )
        print(
            "  %s observation(s) in this core; obs_node already holds %s row(s) for it"
            % (format(_n_obs or 0, ","), format(_pre or 0, ","))
        )
        if not _n_obs:
            # ⚑ AN EMPTY CORE CANNOT PRODUCE A REFERENCE, and folding it would write nothing
            # while reporting success — the vacuous-green shape `do_equiv`'s both-empty refusal
            # exists for, one layer earlier.
            print(
                "  ⚑ NO OBSERVATIONS for that core id — nothing to fold. UNMEASURED, not empty.",
                file=sys.stderr,
            )
            sys.exit(3)
        # ⚑⚑ NEITHER SIDE MAY BE THE DEFAULT (operator, 2026-08-21: *"I don't want anything
        # dry by default, I don't want anything apply by default … explicitly stated on the
        # command line."*). This read `if "--apply" not in sys.argv: plan; exit(0)` — so an
        # invocation that stated NOTHING got a dry run, and "forgot to state it" was
        # indistinguishable from "chose dry". That is the same shape as the tenant default
        # `store.tenant` was written to retire, on the mutation axis: the danger is not that
        # the silent branch is destructive (it is the safe one) but that the CHOICE stops
        # being made, and the next reader inherits a default nobody decided.
        #
        # ⚑ THE DECLARED CONTRACT ALREADY SAYS SO and this site did not implement it —
        # `toolmodes --conventions`: *"--apply: MUTUALLY EXCLUSIVE WITH --dry-run AND ONE IS
        # REQUIRED: a mutating tool invoked with NEITHER must REFUSE, never guess."* Measured
        # the same day: 34 tools take only `--apply`, 2 only `--dry-run`, 1 both — 40
        # half-paired tools, each still carrying a silent default. This is one of them, paid.
        _apply = "--apply" in sys.argv
        _dry = "--dry-run" in sys.argv
        if _apply and _dry:
            # ⚑ BOTH IS ALWAYS AN ERROR — two contradictory intents, and no reading of that
            # is safe. Same refusal `store.tenant` makes for `--sandbox --live`.
            print(
                "  ⚑ BOTH --apply and --dry-run given — mutually exclusive. Refusing "
                "rather than picking one.",
                file=sys.stderr,
            )
            sys.exit(2)
        if not _apply and not _dry:
            print(
                "  ⚑ neither --dry-run nor --apply was given. This mode WRITES; state "
                "which.\n    --dry-run  report the fold and change nothing\n"
                "    --apply    perform it",
                file=sys.stderr,
            )
            sys.exit(2)
        if _dry:
            print("  plan  project_sppf(additive=True, core_id=…) — re-run with --apply")
            sys.exit(0)
        _st = project_sppf(con, additive=True, core_id=_cid)
        con.commit()
        _post = _schema.scalar(
            con, "SELECT count(*) FROM obs_node WHERE core_id=%s" % _schema.ph(), (_cid,)
        )
        print(
            "  obs_node for this core: %s → %s row(s)"
            % (format(_pre or 0, ","), format(_post or 0, ","))
        )
        print("  stats %r" % (_st,))
        sys.exit(0)

    # ⚑⚑⚑ ⟡sql-lift — THE COMPOSITION TEST, and it is the one measurement the fold could not
    # make until now. Every level above 0 reads its children's ids from `obs_node`; every
    # sandbox core is ALREADY fully packed, so a green level was reading a PRE-EXISTING python
    # packing rather than composing on its own previous level. Two identical verdicts proved
    # the signature and proved nothing about the staging.
    #
    # This clears ONE core's rows and rebuilds them level by level with the SQL fold alone, then
    # compares the partition against what was there. SANDBOX ONLY — it deletes rows, so it
    # refuses the live tenant outright rather than trusting a flag.
    if "--refold" in sys.argv:
        _i = sys.argv.index("--refold")
        _cid = sys.argv[_i + 1] if _i + 1 < len(sys.argv) else None
        if _cid is None or "--sandbox" not in sys.argv:
            print(
                "sppf_db --refold <core_id> --sandbox   (REFUSED without --sandbox: it DELETES "
                "obs_node rows for that core and rebuilds them)",
                file=sys.stderr,
            )
            sys.exit(2)
        # ⚑ `require="sandbox"` STATES IN CODE what the guard above enforces at the CLI: this
        # mode DELETES obs_node rows and rebuilds them, so live is not a tenant it may ever
        # reach. `store.tenant`'s own note names this escape — "for a caller whose tenant is
        # not the operator's to choose" — and an unrecognised value refuses rather than
        # passing, so a typo cannot satisfy the contract silently. The argv guard stays: it
        # gives the operator the REASON, where the resolver would give only the refusal.
        con = _store.tenant(mode="rw", label="sppf_db --refold", require="sandbox")
        _before = {
            (r[0], r[1]): r[2]
            for r in _schema.rows(
                con,
                "SELECT core_id, local_id, node_id FROM obs_node WHERE core_id=%s" % _schema.ph(),
                (_cid,),
            )
        }
        if not _before:
            print(
                "sppf_db --refold: core %r holds NO obs_node rows — there is nothing to "
                "compare a rebuild against. UNMEASURED, not equal." % _cid,
                file=sys.stderr,
            )
            sys.exit(3)
        # the partition BEFORE, as canonical classes (ids are surrogates; only the grouping is
        # comparable — see `q_pack_partition`)
        _part = lambda m: {
            frozenset(l for (c, l), n in m.items() if n == nid) for nid in set(m.values())
        }
        _was = _part(_before)
        _schema.execute(con, "DELETE FROM obs_node WHERE core_id=%s" % _schema.ph(), (_cid,))
        con.commit()
        _lv, _rows, _ids, _top = pack_core_sql(con, _cid, base=0, write=True)
        con.commit()
        _after = {
            (r[0], r[1]): r[2]
            for r in _schema.rows(
                con,
                "SELECT core_id, local_id, node_id FROM obs_node WHERE core_id=%s" % _schema.ph(),
                (_cid,),
            )
        }
        _now = _part(_after)
        print("⟡sql-lift REFOLD — core %s (sandbox)" % _cid)
        print(
            "  rebuilt %d level(s) · %d row(s) · %d node id(s) · top id %d"
            % (_lv, _rows, _ids, _top)
        )
        print("  rows   before %d → after %d" % (len(_before), len(_after)))
        print("  classes before %d → after %d" % (len(_was), len(_now)))
        if _was == _now:
            print("  ⚑ IDENTICAL PARTITION — the SQL fold, composing level-on-level from an")
            print("     EMPTY obs_node, reproduces the python packing exactly.")
            # ⚑⚑⚑ THE STALENESS WARNING THAT STOOD HERE WAS THE WRONG KIND OF ANSWER. A refold
            # renumbers this core's surrogates, so stored `unit_node` rows — which are
            # `(unit_id, node_id)`, i.e. HANDLES — now point at different signatures; I printed
            # "N stale rows, re-run the unit half", which treats a design defect as an operational
            # caveat. Operator, 2026-08-15: *"The fact that something can be invalidated means
            # that the query depended on reified state."*
            #
            # ⚑ THE ANSWER IS `q_unit_members` (see its docstring): membership DERIVED from
            # `unit_obs ⋈ edge ⋈ obs_node`, which cannot go stale because it stores nothing. A
            # warning here would tell the reader to repair a table that should not exist.
            print("  ⚑ stored `unit_node` for this core now references RENUMBERED ids — which is")
            print("     why membership belongs in `q_unit_members` (derived) rather than in a")
            print("     relation of handles. Not a repair item: a reification to retire.")
            sys.exit(0)
        _only_was, _only_now = _was - _now, _now - _was
        print(
            "  ⚑ PARTITION DIFFERS — %d class(es) only in python, %d only in SQL"
            % (len(_only_was), len(_only_now))
        )
        for _c in list(_only_was)[:3]:
            print("     python-only class, %d member(s): %s" % (len(_c), sorted(_c)[:8]))
        for _c in list(_only_now)[:3]:
            print("     sql-only    class, %d member(s): %s" % (len(_c), sorted(_c)[:8]))
        sys.exit(1)

    # ⚑⚑ ⒯ — THE STAMP RECONCILER. A stamp file is a CLAIM ABOUT A DATABASE HELD ON THE
    # FILESYSTEM, and this is what makes the claim falsifiable. See `reconcile_stamps`.
    if "--reconcile-stamps" in sys.argv:
        reconcile_report(
            *reconcile_stamps(
                sys.argv[sys.argv.index("--reconcile-stamps") + 1],
                base=base,
                sandbox="--sandbox" in sys.argv,
            )
        )
        sys.exit(0)
    # ⟡ladder-1: the SOURCED tier — ONE decoded core into ONE jsonb row by ONE statement.
    # ⚑ BESIDE `--ingest-core`, NOT INSIDE IT. See `sppf_decode.ingest_source`: the existing
    # ingest applies `only="event"`, so a call added inside `_insert_decoded` would make the
    # production path depend on a tier it never creates.
    # ⚑ ONE DISPATCH LINE FOR THE WHOLE TIER, AND THE ARGUMENT PARSE LIVES WITH THE MODES.
    # A dispatch that unpacks each mode's arguments is a second place every mode's signature
    # is written down, and the two drift the first time one gains an option. `sppf_db` sits
    # against a 1200-line cap that exists to force exactly that question — three modes cost
    # two lines here instead of eight.
    if SOURCE_MODES & set(sys.argv):
        sys.exit(source_cli(sys.argv, args, base, _resolve_core))
    # ⚑ THE COVERAGE CENSUS — READ-ONLY, no store, no writes (⑼). It answers "how many cores
    # can the ingest never see, and why" without running an ingest to find out.
    if "--undecodable" in sys.argv:
        _cs = [
            c
            for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True))
            if (args[0] if args else "") in c
        ]
        _ok, _un = undecodable_census(_cs, base)
        print(
            "decoded %d of %d core(s) under filter %r"
            % (len(_ok), len(_cs), args[0] if args else "")
        )
        undecodable_report(_un, ok=_ok, base=base)
        sys.exit(0)
    if "--project-ref" in sys.argv:
        _n = project_ref_only(sandbox="--sandbox" in sys.argv)
        print("ref: %s row(s)" % format(_n, ","))
        sys.exit(0)
    # ⚑⚑⚑ ⟡finalize-retire — `--finalize` IS GONE, MODE AND FUNCTION TOGETHER (2026-08-22). It
    # ran `finalize_db`, an early db-ingestion attempt that was *"intrinsically wide, deep and
    # atomic: the worst possible granularity"* (operator). The dispatch REFUSES rather than
    # falling through to the unknown-flag path, because a silent "no such mode" and a deliberate
    # retirement read identically — and this one has a successor to name.
    #
    # ⚑⚑ IT WAS REMOVED FOR EXISTING, NOT FOR COSTING: *"because it EXISTS, LLMs keep thinking
    # it's legitimate, and keep leaning on it one way or another."* MEASURED in the session that
    # deleted it — I cited it TWICE as a legitimate caller while reasoning about lock granularity,
    # from its own docstring, while it sat behind a live dispatch. A comment governs only the
    # reader already looking at it; a live dispatch is a standing claim that a mode is supported.
    # An intermediate `--force-superseded` escape was written and then deleted too: an escape
    # hatch is a way for the next reader to keep leaning on it.
    if "--finalize" in sys.argv:
        print(
            "REMOVED: --finalize is retired (⟡finalize-retire).\n"
            "  `finalize_db` was wide, deep and atomic — ONE call globbed the corpus, pruned,\n"
            "  GC'd, deduped, and ran the unscoped fold over the WHOLE store. Every capability\n"
            "  it held has a per-core home on the five-link chain.\n"
            "  Supported path:  make -C agda -f Flat.mk -k -j <N> promote\n"
            "                   (or `sppf_db.py <FILTER> --converge` for the fixpoint)",
            file=sys.stderr,
        )
        sys.exit(2)
    # ⟡tier-converge: the WORKLIST-TO-FIXPOINT ingest. `<FILTER> --converge` searches the
    # boundaries downstream-first (`lifecycle.drain_order()`), does ONE bounded unit at the
    # highest boundary with work, and restarts from the top — so tier 0 is drained before
    # more is added to it. Interruptible and resumable: every predicate reads the store.
    if "--converge" in sys.argv:
        if not args:
            sys.exit('sppf_db --converge: needs a FILTER (pass "" for the whole corpus)')
        _i = sys.argv.index("--converge")
        _n = sys.argv[_i + 1] if len(sys.argv) > _i + 1 else ""
        _max = int(_n) if _n.isdigit() else 100000
        _cores = [
            c
            for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True))
            if args[0] in c
        ]
        print(
            "converging over %d core(s) (filter=%r), max %d step(s) — "
            "downstream-first search, one bounded unit per step" % (len(_cores), args[0], _max)
        )
        # ⚑ THE BOUNDARY COLUMN IS A NAME, NOT AN INDEX (2026-08-12). It printed `%d` from a
        # roster keyed by integer; a reader comparing two traces across a chain edit would have
        # seen the same digit mean two different boundaries. The name is what the roster keys on
        # and what a refusal would quote, so it is what the trace should show.
        print(
            "  step  boundary    at        │      obs       edge      event │  _node  obs_node │"
            "   s  did"
        )

        def _line(r):
            print(
                "  %4d  %-10s  %-8s │ %8s %10s %10s │ %6s %9s │ %4.1f  %s"
                % (
                    r["step"],
                    r["boundary"],
                    r["at"],
                    format(r["obs"], ","),
                    format(r["edge"], ","),
                    format(r["event"], ","),
                    format(r["_node"], ","),
                    format(r["obs_node"], ","),
                    r["s"],
                    r["did"],
                )
            )

        # ⚑ `--shards N --shard i` — ONE WORKER'S SLICE. Defaults `1/0` mean "everything", which
        # the same predicate answers, so an unsharded run and a sharded one share one code path.
        def _flagint(name, default):
            # ⚑ THE FILE'S OWN IDIOM (`sys.argv.index(f) + 1`), not a new helper — a second
            # argument reader is the operand-ownership class this ecosystem has paid for five
            # times. Guarded for a missing operand so `--shards` at the end of argv refuses
            # rather than raising IndexError.
            if name not in sys.argv:
                return default
            _i = sys.argv.index(name)
            if len(sys.argv) <= _i + 1:
                print("%s needs a value" % name, file=sys.stderr)
                sys.exit(2)
            return int(sys.argv[_i + 1])

        _shards = _flagint("--shards", 1)
        _shard = _flagint("--shard", 0)
        if not (0 <= _shard < max(_shards, 1)):
            print(
                "--shard %d is outside 0..%d for --shards %d"
                % (_shard, max(_shards, 1) - 1, _shards),
                file=sys.stderr,
            )
            sys.exit(2)
        if _shards > 1:
            print(
                "  shard %d of %d — this worker folds only cores hashing to its slice; "
                "retire/ingest stay shared" % (_shard, _shards)
            )
        _tr, _undec = converge(
            _cores,
            base=base,
            max_steps=_max,
            sandbox="--sandbox" in sys.argv,
            report=_line,
            shards=_shards,
            shard=_shard,
        )
        _pk = max((r["obs"] for r in _tr), default=0)
        _end = _tr[-1]["obs"] if _tr else 0
        # ⚑ HITTING THE CAP IS NOT CONVERGENCE, AND PRINTING "CONVERGED" FOR IT IS THE
        # absent-read-as-a-verdict SHAPE. `converge` stops for two different reasons — no
        # boundary had work (a FIXPOINT) or `max_steps` ran out (a BUDGET) — and only the
        # first is a claim about the store. Resuming is the same command again.
        print(
            "  %s after %d step(s) │ peak tier-0 obs %s │ final %s"
            % (
                "STOPPED AT THE STEP CAP (not converged — run again to resume)"
                if len(_tr) >= _max
                else "CONVERGED",
                len(_tr),
                format(_pk, ","),
                format(_end, ","),
            )
        )
        # ⚑⚑ THE REASON, GROUPED BY KIND — NOT A COUNT AND A SAMPLE OF NAMES (⑼). This printed
        # `"%d core(s) UNDECODABLE (decode_core returned None): %s" % (n, ", ".join(_undec[:4]))`,
        # which is the shape the whole arc keeps recording: it named the OUTCOME, truncated the
        # population, and asserted a MECHANISM (`decode_core returned None`) that was true of
        # every case and therefore distinguished none of them. The render lives in
        # `sppf_decode.undecodable_report` — beside the decoder, drivable by a case.
        undecodable_report(_undec)
        sys.exit(0)
    # ⚑⚑ `--verify` (⟡gqs-S1: incremental projection ≡ full) IS RETIRED — user's call, ★ⓢ.
    # Its method was FOUR THROWAWAY SQLITE DATABASES, and that method is what postgres does not
    # give free; it was the last real blocker on dropping the sqlite backend, which in turn is
    # what has been breaking the Agda tooling (a sqlite `?` paramstyle bound to a psycopg
    # cursor — `demand_imports` fails on exactly that, in the `scope_fix` write path).
    #
    # ⚑ AND THE INVARIANT IT PROTECTED WAS ALREADY UNVERIFIED WHEN IT WAS RETIRED. The
    # projection was rewritten today (surrogate ids, content-complete node keys, a five-field
    # head), so this gate had never run against the code it claimed to check — its last green
    # result described code that no longer exists. Keeping it would have preserved the
    # APPEARANCE of the invariant, which is worse than its absence.
    #
    # ⚑ IT IS OWED AGAIN AFTER ⓹, REBUILT ON POSTGRES against the real projection. Recorded
    # here rather than only in a plan file so the next reader meets the debt at the site.
    #
    # ⚑ THE MACHINERY IS GONE (`_PROJ_TABLES` / `_proj_digest` / `verify_incremental`,
    # 2026-08-11) BUT ITS FOUR MEASURED LESSONS ARE NOT — they outlive the code that
    # taught them, so they are carried here rather than deleted with it:
    #   1. THE SORT BELONGS TO THE ENGINE (user, 2026-08-05: *"why are we asking the sort
    #      to be done in python?"*). The digest read `sorted(...fetchall())` then
    #      `repr(rows)` — THREE full copies of a table (fetched list, sorted list, and a
    #      string strictly larger than either) built only to be hashed. `pycodemod
    #      --relalg` is the codified form of this: relational algebra done in Python over
    #      rows the store returned.
    #   2. A PARTIAL ORDER KEY IS NOT A KEY. My first fix used `ORDER BY 1`, leaving ties
    #      arbitrary, so the digest varied without the content varying — and I generalised
    #      that one bad attempt into "leave the sort in Python". THE WALL-REFLEX: a wrong
    #      key is not evidence that keys are the wrong tool. The correct key is EVERY
    #      column in order.
    #   3. THE COLUMN ROSTER COMES FROM THE ENGINE, never a hardcoded tuple that drifts
    #      from the schema — `_PROJ_TABLES` itself was exactly such a frozen roster.
    #   4. THE FIXTURE'S PARAMSTYLE MUST BE PINNED TO ITS CONNECTION, NOT READ FROM THE
    #      AMBIENT BACKEND. `_schema.ph()` with no argument emitted `%s` under
    #      `SUBSTRATE_STORE=postgres` and bound it to a sqlite cursor — the same
    #      connection-and-backend-disagree defect as `set1_ratchet_cores._freshen`
    #      (`OperationalError: near "%"`). ⓺ removes the defect CLASS by removing the
    #      dispatch: `ph()` is unconditionally `%s`, so there is no ambient to disagree with.
    # ⚑ A BARE RUN USED TO INGEST, AND I TRIGGERED IT BY ASKING THE TOOL TO DESCRIBE
    # ITSELF (2026-08-07). `python3 scripts/sppf_db.py` with no arguments fell through to
    # here, defaulted `filt` to "Category", and opened a WRITE TRANSACTION against the live
    # store — caught only because a "list the modes" call ran past 120s and `--activity`
    # showed `INSERT INTO edge …` under `WRITE TXN xid=1403`. Cancelled and rolled back;
    # nothing partial landed.
    #
    # ⚑ THIS IS THE `prune_imports` POLARITY DEFECT IN THE HIGHEST-COST PLACE. That tool
    # wrote by default and a preview deleted 12 import lines; here the default action is a
    # multi-GB ingest into a 5.7 GB tier. The plan records the rule (`gate_status --modes`
    # narrows a write-default tool to `--check`) and this file predates it.
    #
    # ⚑ AND THE DEFAULT FILTER WAS THE SECOND HALF. `filt = args[0] if args else "Category"`
    # means a no-argument run does not ingest *nothing* and does not ingest *everything* —
    # it silently picks a subtree. A default that selects a SUBSET is worse than either
    # extreme: the output looks like a successful full run.
    if not args:
        print(__doc__.strip().splitlines()[0] if __doc__ else "sppf_db")
        print("\n⚑ NO FILTER GIVEN — refusing to ingest. A bare run previously defaulted to")
        print('  the "Category" subtree and opened a write transaction against the live')
        print("  store; a tool that writes when asked to describe itself is the defect.\n")
        # ⚑⚑⚑ EVERY LINE NAMES `sppf_db.py`, AND THAT IS A PARSER CONTRACT, NOT VERBOSITY.
        # `toolmodes.parse_usage` recognises a usage line by `_names(stem, line)` — the line
        # must name the tool as a word. This block listed bare `--flag`s, so the census read
        # ZERO declared modes here and reported EVERY one of them as undocumented, including
        # `--promote-core`, which `make` runs on every module of a full build. MEASURED
        # 2026-08-23: `toolmodes --find promote-core` → *"named in scripts/sppf_db.py's own
        # output, declared by NO tool"* — both halves true, and the contradiction between
        # them WAS the defect. The tool described itself in a shape its own census could not
        # read, which is the instrument-boundary-as-subject-boundary error one layer down:
        # the modes were published and simply not in the published FORM.
        print("modes:")
        print("  sppf_db.py --init       create/upgrade the event-tier schema")
        print("  sppf_db.py --ingest-core PATH")
        print("                          ingest ONE .agdai (the make-driven per-core path)")
        print("      [--full]            re-decode even if mtime is unadvanced (shim changed)")
        print("      [--sandbox]         write to the THROWAWAY tenant, never the corpus")
        # ⚑⚑ `--promote-core` AND `--drain-core` ARE LISTED HERE BECAUSE THEY DISPATCH AND
        # THIS BLOCK IS THE CENSUS'S AUTHORITY. The two neighbouring notes record why a
        # STALE line is worse than none; this is the opposite defect, and it cost a real
        # investigation. MEASURED 2026-08-23: five `--promote-core` processes ran 1–3.5h,
        # and `toolmodes --find promote-core` answered *"named in scripts/sppf_db.py's own
        # output, declared by NO tool"* — the mode `make` runs on EVERY module of a full
        # build was reachable only by reading the dispatch. An omitted line is the tool
        # denying a capability it has, and a reader who obeys "run it bare" still guesses.
        print("  sppf_db.py --promote-core PATH [--a2] [--dry-run|--apply]")
        print("                          the packing fold over the ONE core PATH names,")
        print("                          additive — the make-driven twin of --ingest-core")
        print("                          (A3: pack server-side, then build_units). --a2 is")
        print("                          the OLD route, kept as the --equiv reference arm")
        print("  sppf_db.py --drain-core PATH [--dry-run]")
        print("                          retire ONE core's staged rows IF THE LICENCE ADMITS")
        print("                          it — the make-driven twin of --reclaim-core")
        print("  sppf_db.py --ingest-source PATH")
        print("                          ⟡ladder-1: ONE decoded core → ONE jsonb row in the")
        print("                          SOURCED tier, by ONE statement. Beside --ingest-core")
        # ⚑⚑ ⟡document-modes (2026-08-24) — THE SEVEN ⟡sql-lift MODES BELOW DISPATCHED IN NO
        # USAGE LINE AND NO PROSE, which `toolmodes --divergence` had been reporting the whole
        # time.  They are the level-schedule / staged-fold surface: the readers a decision
        # about the fold's GRANULARITY has to run, and the ones a `--height` question routes
        # to.  Not listing them is the same defect the `--promote-core` note above records
        # one screen up — a tool denying a capability it has — and it landed on the modes an
        # operator reaches for precisely when the fold is misbehaving.
        #
        # ⚑ `--verify` IS DELIBERATELY STILL ABSENT and is NOT one of these.  The census
        # reports it as documented-but-unbacked; it is neither.  Its ONE surviving mention is
        # inside `write_events`' docstring (`sppf_db.py:363`), it dispatches nowhere, and the
        # note further down records why a usage line for a retired mode is worse than none.
        # The census reads a docstring mention as a declaration — a fact about the READER.
        print("  sppf_db.py --height <core_id> [--sandbox|--live]")
        print("                          ⟡sql-lift LEVEL SCHEDULE, read-only — the height")
        print("                          histogram of one core's observations: how many")
        print("                          rounds a staged fold takes and how the work")
        print("                          DISTRIBUTES across them. An empty core is a")
        print("                          REFUSAL (exit 3), never a converged zero")
        print("  sppf_db.py --pack-level <core_id> [<height>] [--sandbox|--live]")
        print("                          ONE level of the packing fold, READ-ONLY (a SELECT,")
        print("                          never an INSERT) — the SHARING COLLAPSE at that")
        print("                          height, plus per-component discrimination, so a")
        print("                          ratio is never read without knowing which signature")
        print("                          fields the data actually exercised")
        print("  sppf_db.py --project-core <core_id> [--apply] [--sandbox]")
        print("                          the PYTHON packing fold over ONE core, additive.")
        print("                          Read-only unless --apply, and the connection is")
        print("                          opened `ro` so a dry run CANNOT write")
        print("  sppf_db.py --project-ref [--sandbox]")
        print("                          project the `ref` relation alone — the additive")
        print("                          projection with no core operand; reports row count")
        print("  sppf_db.py --refold <core_id> --sandbox")
        print("                          ⚑ DELETES this core's obs_node rows and rebuilds")
        print("                          them level-on-level with the SQL fold ALONE, then")
        print("                          compares the PARTITION (ids are surrogates) — the")
        print("                          composition test. REFUSES the live tenant outright,")
        print('                          in the argv guard AND in `require="sandbox"`')
        print("  sppf_db.py --reconcile-stamps PATH [--sandbox]")
        print("                          ⒯ a stamp file is a CLAIM ABOUT A DATABASE held on")
        print("                          the FILESYSTEM; this is what makes it falsifiable —")
        print("                          reconcile the stamps under PATH against the store")
        print("  sppf_db.py <FILTER> --source-fidelity [N]")
        print("                          write N cores' sourced rows, read them back, compare")
        print("                          against `dec` ITSELF at every depth; report SIZE")
        print("  sppf_db.py <FILTER> --source-concurrency [N]")
        print("                          run N --ingest-source processes AT ONCE and report")
        print("                          whether any 40P01 (deadlock) occurred — the claim")
        # ⚑ `--finalize` IS NOT LISTED, BECAUSE IT IS RETIRED. This line survived the mode's
        # removal and still advertised it as "prune, GC, then PROJECT" while the dispatch
        # REFUSES it 150 lines up — a self-description promising a capability the tool rejects.
        # The usage block is what a reader is told to trust, so a stale entry here is worse
        # than none: it is the stale-index defect `pycodemod`'s docstring records ("THIS LIST
        # WAS SEVEN MODES SHORT"), inverted. The work it named is `--converge`, below.
        print("  sppf_db.py <FILTER> --undecodable")
        print("                          which cores can the ingest NEVER see, and WHY —")
        print("                          read-only: decodes, writes nothing, touches no store")
        print("  sppf_db.py <FILTER> --converge [N]")
        print("                          WORKLIST TO FIXPOINT — search the lifecycle boundaries")
        print("                          downstream-first, do ONE bounded unit at the highest")
        print("                          with work, restart from the top; ingest is what is")
        print("                          left when nothing else has work. Every predicate is a")
        print("                          RESIDUE read from the store, so it resumes after a kill")
        print("                          (N caps the steps; a census prints after each)")
        # ⚑ `--verify` IS NOT LISTED BECAUSE IT NO LONGER DISPATCHES. A usage line for a
        # retired mode is worse than no line: it is the tool asserting a capability it does
        # not have, and this block IS the tool's self-description (the census that
        # `toolmodes.py` reads is generated from exactly such output).
        print("  sppf_db.py <FILTER> [--full] [--sandbox]")
        print("                          ingest every core whose path contains FILTER")
        print('                          (pass "" for the whole corpus — and it prunes);')
        print("                          --sandbox runs the WHOLE chain against the throwaway")
        print("                          tenant — the rehearsal path, never the corpus")
        print("\n  sppf_db.py --orbit --distribute --argperm   additive projections")
        sys.exit(2)
    filt = args[0]
    cores = [
        c
        for c in sorted(glob.glob(os.path.join(base, "**", "*.agdai"), recursive=True))
        if filt in c
    ]
    print(
        f"event-sourcing {len(cores)} cores (filter={filt!r}) → catalog.db (events, then project SPPF"
        f"{', + ORBIT' if orbit else ''}) …"
    )
    n, u, sh, mx = build(
        cores,
        orbit=orbit,
        distribute=distribute,
        argperm=argperm,
        prune=(filt == ""),
        sandbox="--sandbox" in sys.argv,
    )
    print(
        f"  events → SPPF projection: {n} packings, {u} units, {sh} shared subtrees, max node_id {mx}"
    )
    if argperm:
        con = _store.connect(mode="ro")
        # ⚑ WAS A POSITIONAL 3-TUPLE UNPACK — `d, t, g = …fetchone()`, which is the
        # shape that silently RESHUFFLES if the query's column order changes and says
        # nothing about which count is which. Named reads make the mapping explicit.
        _r = next(
            _schema.rows(
                con,
                "SELECT COUNT(*) AS defs, COUNT(DISTINCT type_key) AS types, "
                "COUNT(DISTINCT graded_key) AS graded FROM _orbit_def",
            )
        )
        d, t, g = _r["defs"], _r["types"], _r["graded"]
        print(
            f"  ⟡argperm GRADED orbit: {d} defs → {t} type-orbits, {g} graded-orbits "
            f"({d - g} defs collapsed by full arg-perm equivalence; {d - t} by type/telescope alone)"
        )
        con.close()
    # ⚑ the `if orbit:` stats block went with the tier, 2026-08-23. `--orbit` is now accepted
    # and inert; `--argperm` above is a DIFFERENT projection and still reports.
