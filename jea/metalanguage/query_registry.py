#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""query_registry.py — ⟡query-sppf-intern (first milestone): intern the project's SQLAlchemy-Core query
workload into the SPPF via the SAME interner that interns .py / .agdai (jea_pyalg.Intern, children-as-ids),
then read a join/filter predicate's sharing-BREADTH (node_units / fanin) as its INDEX PRIORITY.

NOT new machinery: the interner + its breadth readouts already exist (jea_pyalg.Intern.fanin,
jea_pysim.Corpus.node_units / extract_candidates). The only additions here are a ClauseLowerer — a THIRD
front-end beside jea_pyalg's Lowerer (Python AST) and CstLowerer (libcst) — that walks a SQLAlchemy
Select/ClauseElement into IR, and a ~6-line unit-register helper mirroring jea_pysim.add_file:121-128.

Reshaping discovery: the `path_text.path_id` breadth signal lives in the node/unit VIEW DEFINITIONS, not the
ad-hoc queries, so this first milestone points the lowerer at the view-def SELECTs + the existing Core sites
(where the join predicates are). GROUND TRUTH: `path_text.path_id` — the join key of the GROUP_CONCAT
`path_text` view, hand-fixed to a PK-indexed table on 2026-07-13 — is the validated indexed key
(i.e. the tool would have surfaced exactly that index). The broad ad-hoc raw→Core migration for fuller
coverage is the separate follow-on ⟡query-rawtocore-migration.

⟡index-weight-by-cost: breadth alone OVER-nominates. A join key is weighted by DIRECTION — an unindexed
column whose join-counterpart is ALREADY indexed is a PROBE-source: the planner SCANs its table and seeks
the indexed counterpart, so an index on the probe column is IGNORED (measured empirically on _unit.name_pid
/ event.ctor_id / _node.op_path_id — ⟡investigate-surfaced-candidates). `_roles` demotes those out of the
recommendation list; genuine candidates are unindexed columns on the SEEK side (value filter, or joined to
an unindexed column), still gated on selectivity / join-target cost. Direction needs the live index set
(catalog.db); render-table keys are accurate only against a db built with the reuse-catalog tables.
"""

import sys, os, re, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jea_pyalg import IR
from jea_pysim import Corpus, Unit
from sqlalchemy import MetaData, Table, Column, String, select

# ── lightweight (reflection-free) Tables: we intern query STRUCTURE, never execute — no DB needed ──
_MD = MetaData()


def _T(name, *cols):
    return Table(name, _MD, *[Column(c, String) for c in cols])


path_text = _T("path_text", "path_id", "text")
_unit = _T(
    "_unit",
    "unit_id",
    "name_pid",
    "root_id",
    "file_id",
    "kind_id",
    "module_pid",
    "root_lid",
    "copy",
)
_node = _T("_node", "node_id", "sym", "kind_id", "role_id", "op_term_id", "op_path_id", "lit_id")
terms = _T("terms", "term_id", "text")
unit_node = _T("unit_node", "unit_id", "node_id")
node_child = _T("node_child", "node_id", "ord", "child_id")
obs = _T("obs", "core_id", "local_id", "ekey")
event = _T("event", "ekey", "ctor_id", "qname_pid", "idx")
edge = _T("edge", "core_id", "plid", "ord", "clid")


# ── the query workload as named build-only Core select()s ──────────────────────────────────────────
# The node/unit VIEW-definition SELECTs (where path_text.path_id is joined) + the existing Core sites
# (graded_orbit.preload_cores / unit_index, autocorr_synth). Each is the STRUCTURE only.
def q_node_view():  # sppf_db `node` view: joins path_text on op_path_id
    return select(_node.c.node_id, terms.c.text, path_text.c.text).select_from(
        _node.join(terms, terms.c.term_id == _node.c.kind_id).outerjoin(
            path_text, path_text.c.path_id == _node.c.op_path_id
        )
    )


def q_unit_view():  # sppf_db `unit` view: joins path_text on name_pid
    return select(_unit.c.unit_id, path_text.c.text, terms.c.text).select_from(
        _unit.join(path_text, path_text.c.path_id == _unit.c.name_pid).join(
            terms, terms.c.term_id == _unit.c.file_id
        )
    )


def q_unit_index():  # graded_orbit.unit_index
    return select(path_text.c.text, _unit.c.file_id, _unit.c.root_lid).select_from(
        _unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)
    )


def q_preload_nodes():  # graded_orbit.preload_cores node scan
    return select(
        obs.c.core_id, obs.c.local_id, terms.c.text, path_text.c.text, event.c.idx
    ).select_from(
        obs.join(event, event.c.ekey == obs.c.ekey)
        .join(terms, terms.c.term_id == event.c.ctor_id)
        .outerjoin(path_text, path_text.c.path_id == event.c.qname_pid)
    )


def q_argperm_uid():  # sppf_db.project_argperm's uid map
    return select(_unit.c.unit_id, path_text.c.text).select_from(
        _unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)
    )


def q_orbit_def_join():  # graded_orbit.orbit_cosets / cosets_view: _orbit_def → _unit → path_text
    return select(path_text.c.text, _unit.c.unit_id).select_from(
        _unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)
    )


def q_reuse_unit_name():  # reuse_tui / reuse_catalog compat: unit name via path_text
    return select(_unit.c.unit_id, path_text.c.text).select_from(
        _unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)
    )


def q_autocorr_dupsig():  # autocorr_synth dup-signature: unit_node self-join (NO path_text — a control)
    a = unit_node.alias("a")
    b = unit_node.alias("b")
    return select(a.c.unit_id, b.c.unit_id).select_from(a.join(b, a.c.node_id == b.c.node_id))


def q_reuse_nodechild():  # a reuse query over node_child (NO path_text — a control)
    return select(unit_node.c.unit_id, node_child.c.child_id).select_from(
        unit_node.join(node_child, node_child.c.node_id == unit_node.c.node_id)
    )


BUILDERS = {
    "node_view": q_node_view,
    "unit_view": q_unit_view,
    "unit_index": q_unit_index,
    "preload_nodes": q_preload_nodes,
    "argperm_uid": q_argperm_uid,
    "orbit_def_join": q_orbit_def_join,
    "reuse_unit_name": q_reuse_unit_name,
    "autocorr_dupsig": q_autocorr_dupsig,
    "reuse_nodechild": q_reuse_nodechild,
}
# ⟡query-rawtocore-migration: the migrated ad-hoc queries (single source in query_builders) are interned
# here too — one builder is BOTH executed (via query_builders.run at the call site) AND interned for breadth.
from query_defs import (
    INTERN_BUILDERS as _QB_BUILDERS,
)  # the builder OBJECTS (⟡qinfra: compiler, not runtime)

BUILDERS.update({f"qb.{k}": v for k, v in _QB_BUILDERS.items()})


# ── ClauseLowerer: SQLAlchemy Select/ClauseElement → IR, bottom-up, interned into Corpus.I ─────────
class ClauseLowerer:
    """A third front-end beside jea_pyalg.Lowerer/CstLowerer. Head ‖ children, children-as-interned-ids —
    a Column's referential identity ('table.col') sits in `op` exactly like a free Name/Attribute; a Join /
    Compare wraps its parts as children. The interner content-addresses the shared structure; a predicate
    node (Compare over two Columns) shared across queries gets fanin/node_units breadth for free."""

    def __init__(self, I):
        self.I = I

    @staticmethod
    def _base_table(tbl):
        """resolve an Alias to its underlying Table name — an index recommendation must target the REAL
        table (unit_node), not a query-local alias (a/b), so aliased columns aggregate breadth correctly."""
        return getattr(getattr(tbl, "element", tbl), "name", getattr(tbl, "name", "?"))

    def lower(self, el):
        cn = el.__class__.__name__
        # Column (has a table + name) → the referential identity in op
        tbl = getattr(el, "table", None)
        if tbl is not None and hasattr(el, "name") and cn in ("Column",):
            return self.I.intern(IR(kind="Column", op=f"{self._base_table(tbl)}.{el.name}"))
        if cn == "Table":
            return self.I.intern(IR(kind="Table", op=el.name))
        if cn == "Join":
            op = "outer" if getattr(el, "isouter", False) else "inner"
            kids = (self.lower(el.left), self.lower(el.right), self.lower(el.onclause))
            return self.I.intern(IR(kind="Join", op=op, children=kids))
        if cn in ("BinaryExpression",):
            opn = getattr(
                getattr(el, "operator", None), "__name__", str(getattr(el, "operator", ""))
            )
            return self.I.intern(
                IR(kind="Compare", op=opn, children=(self.lower(el.left), self.lower(el.right)))
            )
        if cn in ("BooleanClauseList", "ClauseList"):  # AND/OR of predicates
            opn = getattr(getattr(el, "operator", None), "__name__", "and_")
            return self.I.intern(
                IR(kind="Bool", op=opn, children=tuple(self.lower(c) for c in el.clauses))
            )
        if hasattr(el, "get_final_froms"):  # a Select
            kids = [self.lower(c) for c in el.selected_columns]
            kids += [self.lower(f) for f in el.get_final_froms()]
            if el.whereclause is not None:
                kids.append(self.lower(el.whereclause))
            return self.I.intern(IR(kind="Select", children=tuple(kids)))
        # leaf fallback (alias-wrapped column, bindparam, literal, …): keep a stable op where possible
        if tbl is not None and hasattr(el, "name"):
            return self.I.intern(IR(kind="Column", op=f"{self._base_table(tbl)}.{el.name}"))
        return self.I.intern(
            IR(kind=cn, op=str(getattr(el, "key", "") or getattr(el, "value", "") or ""))
        )


def build_corpus(builders=BUILDERS):
    """Intern every builder as a query Unit (mirrors jea_pysim.add_file:121-128 register shape)."""
    C = Corpus()
    lw = ClauseLowerer(C.I)
    for name, fn in builders.items():
        root = lw.lower(fn())
        sup = C._support(root)
        C.units.append(
            Unit(
                name=name, path="query", lineno=-1, root=root, support=sup, depth=C._depth_map(root)
            )
        )
        uidx = len(C.units) - 1
        for nid in sup:
            C.node_units.setdefault(nid, set()).add(uidx)
    return C


def _predicate_columns(C):
    """column node-ids that appear as a child of a Compare (join onclause / filter) — the index candidates
    (a projected-only column is not one). Returns {col_nid}."""
    preds = set()
    for nid in range(C.I.size()):
        n = C.I.nodes[nid]
        if n.kind == "Compare":
            for c in n.children:
                if C.I.nodes[c].kind == "Column":
                    preds.add(c)
    return preds


def _live_indexed(colops):
    """Which 'table.column' predicate keys are ALREADY covered by an index — in the LIVE STORE.

    ⚑⚑ THIS READ A DIFFERENT STORE FROM THE ONE IT WAS REPORTING ON, AND THE REPORT INVERTED.
    It opened `catalog/catalog.db` with `sqlite3` and ran `PRAGMA index_list` — a 334 MB SQLite
    file last written two weeks before this was found — while `_selectivity` two functions down
    read live postgres via `store.connect`. TWO STORES IN ONE REPORT.

    ⚑ AND THE FAILURE WAS ASYMMETRIC AND SILENT, which is why it survived. The postgres
    relations (`_node`, `node_child`, `unit_node`, `obs_node`, `edge`, `obs`) do not exist in
    catalog.db at all, so every `PRAGMA table_info` on them returned nothing, the
    `sqlite3.OperationalError` handler swallowed the rest, `covered` stayed empty for them — and
    `_roles` classified them **candidate** by default. MEASURED against `schema.py --ddl --live`:
    `_node` has `PRIMARY KEY (node_id)`, `unit_node` has `ix_un_unit`/`ix_un_node`/`ix_un_edge`,
    `node_child` has `ix_nc_node`. **The three highest-breadth "candidates" in this report
    (breadth 12, 12, 10) were all already indexed.** A stale annotation would be bad; this was a
    false positive in the direction that GENERATES WORK — an index proposed for a column that
    already has one.

    The repair is one line of authority, not new machinery: read the DDL the live store reports,
    on the same tenant `_selectivity` probes. Absent store → empty (annotation only), which is
    the original honest fallback and is unchanged.
    """
    # ⚑ READ THE DECLARATION, NOT A RENDERED STRING. `schema_decl` holds `MD.sorted_tables`
    # (each with its PK constraint) and `INDEXES` (SQLAlchemy `Index` objects) as STRUCTURE —
    # so there is nothing to regex, and no second spelling of "what is indexed" to drift.
    # `schema.py --ddl` renders these same objects; parsing its output would be reading a
    # projection of the authority instead of the authority.
    covered = set()
    try:
        import schema_decl as _sd
    except Exception:
        return covered  # annotation only; absent → empty
    for t in getattr(getattr(_sd, "MD", None), "sorted_tables", ()) or ():
        pk = list(getattr(t.primary_key, "columns", ()) or ())
        if pk:
            covered.add(f"{t.name}.{pk[0].name}")  # a seek needs the PREFIX column
    for ix in getattr(_sd, "INDEXES", ()) or ():
        cols = list(getattr(ix, "columns", ()) or ())
        tbl = getattr(getattr(ix, "table", None), "name", None)
        if tbl and cols:
            covered.add(f"{tbl}.{cols[0].name}")
    return covered


def _join_pairs(C):
    """From each Compare node, the columns it relates: (colA_nid, colB_nid) for a join equality between two
    columns, or (col_nid, None) for a filter equality (column vs bindparam/literal). Direction is read off
    these pairs (⟡investigate-surfaced-candidates: an unindexed column whose join-counterpart is ALREADY
    indexed is a PROBE-source — the planner drives on it via a full SCAN and seeks the counterpart, so an
    index here is IGNORED; measured empirically on _unit.name_pid / event.ctor_id / _node.op_path_id)."""
    _NULLCHECK = {
        "is_",
        "is_not",
        "isnot",
        "isnull",
        "is_null",
        "notnull",
    }  # IS [NOT] NULL — no plain-index seek
    pairs = []
    for nid in range(C.I.size()):
        n = C.I.nodes[nid]
        if n.kind != "Compare":
            continue
        cols = [c for c in n.children if C.I.nodes[c].kind == "Column"]
        if len(cols) == 2:  # a join equality (col == col)
            pairs.append((cols[0], cols[1]))
        elif (
            len(cols) == 1 and n.op not in _NULLCHECK
        ):  # a VALUE filter (eq/range/in/like) — index-servable;
            pairs.append(
                (cols[0], None)
            )  # a null-check is NOT (a probe column's incidental filter)
    return pairs


def _roles(C, covered):
    """Classify each predicate-column op → 'indexed' | 'probe' | 'candidate' by join DIRECTION (not breadth):
    - indexed  : already covered by a PK/index (a validated key, e.g. the hand-done path_text.path_id).
    - probe    : unindexed, but in EVERY join it participates in the counterpart is already indexed — the
                 planner SCANs this column's table and seeks the counterpart, so an index here is ignored.
    - candidate: unindexed AND (a filter target, OR joined to an UNINDEXED column) — a genuine seek an index
                 could serve; still gated on selectivity / join-target cost before adding."""
    op = lambda nid: C.I.nodes[nid].op
    cps = {}  # colop -> list of counterpart ops (None=filter)
    for a, b in _join_pairs(C):
        cps.setdefault(op(a), []).append(op(b) if b is not None else None)
        if b is not None:
            cps.setdefault(op(b), []).append(op(a))
    roles = {}
    for colop, cc in cps.items():
        if colop in covered:
            roles[colop] = "indexed"
            continue
        has_filter = any(c is None for c in cc)
        joins = [c for c in cc if c is not None]
        roles[colop] = (
            "candidate" if (has_filter or any(c not in covered for c in joins)) else "probe"
        )
    return roles


def _filter_cols(C):
    """predicate-column ops that appear as a VALUE filter (col op value) — the selectivity-relevant ones
    (a join column's index utility is about direction, not cardinality)."""
    op = lambda nid: C.I.nodes[nid].op
    return {op(a) for a, b in _join_pairs(C) if b is None}


def _selectivity(cols, cap=2_000_000):
    """⟡index-selectivity-weight: for each BASE-table 'table.col', (n_distinct, n_rows) via a guarded
    COUNT(DISTINCT)/COUNT(*). Skips VIEWs (can't be indexed; probing one may materialize it — that's the
    separate ⟡resolve-view-columns) and tables above `cap` rows (n_distinct=None = 'too big to probe cheaply,
    left as a candidate'). Absent DB → {}. Only the columns already role='candidate' & filter-driven are passed
    in, so this runs a handful of cheap COUNTs, never a scan of event/obs/edge."""
    # ⚑ WAS A HAND-BUILT `{name: type}` FROM `sqlite_master` — the exact map
    # `schema.relations` returns, and one of five sites that spelled it independently.
    import store as _store, schema as _schema

    out = {}
    try:
        con = _store.connect(mode="ro")
    except SystemExit:
        return out  # no store yet → no index advice to give
    kinds = _schema.relations(con)

    # ⚑ THREE PORTING DEFECTS IN THESE FIVE LINES, and they are the ones a "swap the
    # connection" migration hits last:
    #   1. `con.execute(...)` — psycopg has no connection-level execute; it needs a cursor.
    #   2. `.fetchone()[0]` — `sqlite3.Row` indexes positionally, psycopg's `dict_row`
    #      yields DICTS, so `[0]` raises `KeyError: 0`. This is the row-factory
    #      incompatibility flagged when the store authority landed, now biting for real.
    #   3. `except sqlite3.OperationalError` — the module no longer imports sqlite3, so
    #      the handler itself raised `NameError` while handling an error.
    # A scalar helper hides all three; `Exception` is the honest catch because the
    # failures being tolerated here (a missing table, an unreadable column) are named
    # differently by each driver.
    def _scalar(sql):
        cur = con.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        if row is None:
            return None
        return list(row.values())[0] if isinstance(row, dict) else row[0]

    for colop in cols:
        tbl, _, col = colop.partition(".")
        if kinds.get(tbl) != "table":
            continue  # view / absent → not a base-table index target
        try:
            nrows = _scalar(f"SELECT COUNT(*) FROM {tbl}")
            if nrows > cap:
                out[colop] = (None, nrows)
                continue
            out[colop] = (_scalar(f"SELECT COUNT(DISTINCT {col}) FROM {tbl}"), nrows)
        except Exception:
            pass
    con.close()
    return out


def _cols_of(tbl):
    """The LIVE column set of one relation, or () if unknown. The check that separates a
    candidate target from a resolution — see `_why`'s alias branch."""
    try:
        import store as _store, schema as _schema

        con = _store.connect(mode="ro")
    except Exception:
        return ()
    try:
        return set(_schema.columns(con).get(tbl, ()) or ())
    except Exception:
        return ()
    finally:
        try:
            con.close()
        except Exception:
            pass


def _live_kinds():
    """{relation: 'table'|'view'} from the LIVE tenant, or {} if there is no store.

    ⚑ Same source `_selectivity` already uses (`schema.relations`), asked once for the whole
    report instead of per-probe — so the diagnosis and the measurement cannot disagree about
    what the store holds.
    """
    try:
        import store as _store, schema as _schema

        con = _store.connect(mode="ro")
    except Exception:
        return {}
    try:
        return _schema.relations(con)
    except Exception:
        return {}
    finally:
        try:
            con.close()
        except Exception:
            pass


def _declared_names():
    """Every relation the repo DECLARES — TABLES *and* VIEWS/SHADOWS.

    ⚑ `MD.tables` ALONE IS NOT THE DECLARATION, and reading it as such misclassified a real
    view as an SQL alias. MEASURED: `core_decoded_shadow` is declared
    (`CREATE OR REPLACE VIEW core_decoded_shadow AS WITH RECURSIVE …`, visible in
    `schema.py --ddl`), absent from this tenant's relation list, and therefore fell through
    `tbl not in _kinds` into the alias branch — the diagnosis naming the wrong repair for the
    one row that is genuinely ⟡resolve-view-columns' business.

    A declaration read through one of its two containers is the census-keyed-on-one-spelling
    shape: the answer looked complete because the container it asked was complete.
    """
    try:
        import schema_decl
    except Exception:
        return set()
    names = set(getattr(getattr(schema_decl, "MD", None), "tables", ()) or ())
    return names | _declared_shadows()


def _declared_shadows():
    """The declared VIEW/SHADOW names — the population ⟡resolve-view-columns actually owns."""
    try:
        import schema_decl

        return set(getattr(schema_decl, "SHADOWS", {}) or {})
    except Exception:
        return set()


# ⟡resolve-alias-columns — an `AS <name>` binding in a FROM/JOIN clause, with what it binds.
# ⚑ NOT a name-shape test. The first cut called every unresolvable prefix an "SQL alias" on the
# strength of `tbl not in _kinds`, which lumped two populations: real correlation names (`n`,
# `s`, `nf`, `pt` — bound by `AS` to a table or subquery) and RELATION references the builder
# layer defines but this tenant lacks (`structs`, `modules`, `meta`, `in_degree`, …, whose
# builders read `SELECT structs.qname FROM structs`). Those need OPPOSITE repairs: resolve an
# alias to its target; materialise or resolve a view. The compiled SQL distinguishes them
# exactly — an alias is bound, a relation reference is not — so ask it.
_AS_BIND = re.compile(r"\bAS\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\bON\b|,|\)|$)", re.I | re.M)
_FROM_TBL = re.compile(
    r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)\s+AS\s+([A-Za-z_][A-Za-z0-9_]*)", re.I
)


def _alias_bindings_by_builder():
    """{builder: ({alias: {target}}, {derived-table alias})} — bindings SCOPED to the statement.

    ⟡alias-scope-per-builder. An alias is scoped to the statement that binds it, so the only
    honest resolution is per-builder. `_alias_bindings` (the corpus-wide union) answers *"what
    has `n` ever meant"*; this answers *"what does `n` mean HERE"*, which is the question a
    predicate belonging to a specific builder actually poses.

    ⚑ THE SCOPE WAS ALREADY IN THE CORPUS AND I NEARLY REBUILT IT. `Corpus.node_units` maps a
    node id → the unit indices referencing it, and `Unit.name` is the builder name — both built
    at intern time for the breadth readout. Threading the builder through is a JOIN on data
    that exists, not a second traversal of the SQL.
    """
    # ⚑ KEY ON THE NAMES THE CORPUS USES, NOT THE ONES query_defs USES. `build_corpus` interns
    # `BUILDERS`, which is nine local `q_*` builders PLUS `INTERN_BUILDERS` re-keyed as
    # `qb.<name>` (query_registry.py:90). A first cut keyed this map on the bare `<name>` and
    # every lookup missed silently — `_scoped` returned nothing for all 32 columns and the
    # unscoped fallback answered, so the output was IDENTICAL to before and the scoping looked
    # implemented. Same census-keyed-on-one-spelling shape, inside the fix for it.
    out = {}
    for name, fn in BUILDERS.items():
        try:
            sql = str(fn())
        except Exception:
            continue  # a builder that will not compile is not evidence
        local = {}
        for tbl, alias in _FROM_TBL.findall(sql):
            local.setdefault(alias, set()).add(tbl)
        subq = {a for a in _AS_BIND.findall(sql) if a not in local}
        out[name] = (local, subq)
    return out


def _alias_bindings():
    """{alias: target} over every compiled builder — `FROM x AS a` / `JOIN y AS b`.

    ⚑ THE COMPILED SQL IS THE AUTHORITY, not the interned Column nodes: the corpus keeps
    `table.col` ops and discards the FROM structure, so the binding an alias carries is simply
    not present at that layer. A subquery alias (`AS nf` over a derived table) resolves to no
    single relation and is reported as such rather than guessed.

    ⚑ THIS IS THE UNSCOPED VIEW and it is retained deliberately as the FALLBACK: when a column
    cannot be attributed to a builder, a corpus-wide candidate set is still more than nothing —
    provided it is reported as ambiguous rather than resolved. `_alias_bindings_by_builder` is
    the one to prefer.
    """
    out, subq = {}, set()
    try:
        import query_defs as _qd
    except Exception:
        return out, subq
    for name in sorted(getattr(_qd, "INTERN_BUILDERS", {}) or {}):
        try:
            sql = str(_qd.INTERN_BUILDERS[name]())
        except Exception:
            continue  # a builder that will not compile is not evidence
        # ⚑ RESOLVE WITHIN A BUILDER, THEN UNION — never union first. An alias is scoped to the
        # statement that binds it, so a cross-builder union answers "what has `r` ever meant"
        # when the question is "what does `r` mean where THIS predicate lives".
        # MEASURED: the first cut unioned first and reported `r.lid` as "RESOLVED to terms.lid"
        # — but `terms` has columns (term_id, text) and no `lid` at all. It had matched
        # `JOIN terms AS r` in one builder and applied it to a predicate from another. A
        # confident resolution to a column that does not exist is worse than no resolution.
        local = {}
        for tbl, alias in _FROM_TBL.findall(sql):
            local.setdefault(alias, set()).add(tbl)
        for alias, tbls in local.items():
            out.setdefault(alias, set()).update(tbls)
        for alias in _AS_BIND.findall(sql):
            if alias not in local:
                subq.add(alias)
    # an alias that is ALSO a derived-table alias somewhere is not cleanly resolvable
    for a in list(out):
        if a in subq and len(out[a]) == 1:
            out[a].add("(subquery)")
    return out, subq


_MIN_ROWS = 1000  # a table below this is scanned instantly — an index is moot
_MIN_DISTINCT = (
    25  # a typical equality match ≈ 1/n_distinct of rows (uniform est.); <25 → >4%/value, a
)


# b-tree seek isn't worth it (⟡investigate-surfaced-candidates: _unit.copy = 2 distinct)
def index_report(C):
    preds = _predicate_columns(C)
    colops = {C.I.nodes[nid].op for nid in preds}
    covered = _live_indexed(colops)
    roles = _roles(C, covered)
    fcols = _filter_cols(C)
    # ⟡probe-join-keys — PROBE EVERY CANDIDATE, not only value filters.
    #
    # ⚑ THE OLD RESTRICTION (`and op in fcols`) RESTED ON A TRUE STATEMENT THAT DOES NOT IMPLY
    # IT. `_filter_cols` says *"a join column's index utility is about direction, not
    # cardinality"* — correct, and `_roles` already decides direction: a join key reaches
    # `candidate` only when its counterpart is UNINDEXED, i.e. the planner cannot seek past it.
    # But "direction decides IF an index could serve" and "cardinality decides WHETHER IT IS
    # WORTH ADDING" are different questions, and the second was simply never asked for these.
    #
    # MEASURED: six candidates — node_child.node_id, obs.local_id, obs_node.local_id,
    # obs_node.node_id, edge.clid, edge.plid (Σbreadth 26) — sit on REAL base tables with REAL
    # columns, several already carrying indexes, and were reported as unmeasured for a reason
    # that was never about them. A recommendation with no cardinality behind it is the
    # hardcoded-scalar shape: an index proposed without the number that justifies it.
    #
    # ⚑ THE SAFETY PROPERTIES ARE `_selectivity`'s, NOT THIS CALLER'S, and they are unchanged:
    # it skips anything `kinds` does not call a `table` (so no view is materialized by a probe)
    # and returns (None, nrows) above `cap` rather than scanning. Widening the INPUT cannot
    # make it probe something it already refuses. What it costs is a few extra cheap COUNTs.
    sel = _selectivity({op for op in colops if roles.get(op) == "candidate"})
    # ⚑ WHY A CANDIDATE CARRIES NO MEASUREMENT — FOUR CAUSES, NOT ONE.  The report printed
    # "(view / absent-in-this-db — resolve to base: ⟡resolve-view-columns)" for EVERY candidate
    # with an empty note, which is an `else` branch narrating a cause it never determined.
    # MEASURED against `schema.py --relations/--columns --live`: of the 29 rows so labelled,
    # `node_child.node_id`, `obs_node.local_id`, `edge.clid`, `edge.plid` are REAL COLUMNS ON
    # REAL BASE TABLES — they were never probed because they are JOIN keys, so `op in fcols`
    # excluded them from `_selectivity` before views entered the question at all.
    #
    # Reporting all four as "resolve the view" sends a reader to fix a view that does not
    # exist, and hides that ⟡resolve-view-columns' true population is far smaller than 29.
    # A diagnosis is a claim; this one must be derived.
    _kinds = _live_kinds()
    _aliases, _subq = _alias_bindings()
    _by_builder = _alias_bindings_by_builder()
    _uname = {i: u.name for i, u in enumerate(C.units)}

    def _scoped(tbl, col, builders):
        """⟡alias-scope-per-builder — resolve `tbl` within the builders this column occurs in.

        Returns (note, resolved_target) or (None, None) when scope does not settle it. A single
        target that AGREES across every owning builder, and whose relation actually has `col`,
        is a resolution; anything else stays ambiguous and says why.
        """
        seen, unbound = set(), []
        for b in builders:
            local, subq = _by_builder.get(b, ({}, set()))
            if tbl in local:
                seen |= local[tbl]
            elif tbl in subq:
                seen.add("(subquery)")
            else:
                unbound.append(b)
        if not seen:
            return None, None
        if len(seen) == 1:
            t = next(iter(seen))
            if t == "(subquery)":
                return (
                    "alias over a DERIVED table in its own builder(s) — no base relation to "
                    "index; the cost lives in the subquery"
                ), None
            if _kinds.get(t) == "table" and col in _cols_of(t):
                where = f" in {len(builders)} builder(s)" if len(builders) > 1 else ""
                return (
                    f"alias → {t}.{col} — RESOLVED per-builder{where}; re-key the predicate "
                    f"to {t}.{col} and it becomes probeable"
                ), f"{t}.{col}"
            if _kinds.get(t) == "table":
                return (
                    f"alias → {t} in its builder(s), but {t} has no column {col!r} — the "
                    f"predicate and the binding disagree"
                ), None
            return f"alias → {t} — not a base table here ({_kinds.get(t, 'absent')})", None
        # ⚑ DISAGREEMENT ACROSS OWNING BUILDERS IS THE HONEST ANSWER, not a majority pick. The
        # same alias genuinely means different relations in different statements; one column
        # key cannot carry two resolutions, and choosing one would look resolved and be wrong
        # half the time — the `r.lid → terms.lid` failure, one scope narrower.
        return (
            f"alias means {len(seen)} different things across its own builder(s) "
            f"({', '.join(sorted(seen)[:4])}) — the column key cannot carry both"
        ), None

    def _why(op, builders=()):
        tbl, _, _col = op.partition(".")
        if op in sel:
            return None  # measured — the caller renders it
        if tbl not in _kinds:
            # ⚑ ASK THE DECLARATION, DO NOT GUESS FROM THE NAME. A first cut inferred "alias"
            # from string shape (short/lowercase), which is a heuristic about spelling standing
            # in for a fact the tree owns: `schema_decl` knows every relation this repo COMMITS
            # to, so a name in it is declared-but-absent from this tenant, and a name in neither
            # is an SQL correlation alias the corpus never resolved.
            if tbl in _declared_shadows():
                return (
                    "declared VIEW/SHADOW, absent from this tenant — resolve to base "
                    "columns: ⟡resolve-view-columns"
                )
            if tbl in _declared_names():
                return "declared TABLE, absent from this tenant — nothing here to probe"
            # ⟡alias-scope-per-builder — ASK THE OWNING BUILDERS FIRST. The corpus-wide union
            # below is the fallback, and it can only ever report ambiguity honestly; scope is
            # what turns a candidate set into a resolution.
            _note, _ = _scoped(tbl, _col, builders)
            if _note:
                return _note
            # ⟡resolve-alias-columns — the unscoped fallback (reports ambiguity, never resolves).
            tgts = _aliases.get(tbl)
            if tgts:
                if len(tgts) == 1:
                    t = next(iter(tgts))
                    base = f"alias → {t}"
                    if _kinds.get(t) == "table":
                        # ⚑ VERIFY THE COLUMN BEFORE CLAIMING RESOLUTION. A single target is not
                        # proof: the union is still cross-builder, and an alias reused with a
                        # different binding elsewhere yields a target whose columns do not
                        # include this one. Checking against the LIVE column set is what turns
                        # "one candidate target" into a resolution — and what caught `r.lid →
                        # terms.lid`, where `terms` is (term_id, text).
                        if _col in _cols_of(t):
                            return (
                                f"{base}.{_col} — RESOLVED to a base table; re-key the "
                                f"predicate to {t}.{_col} and it becomes probeable"
                            )
                        return (
                            f"{base}, but {t} has no column {_col!r} — the alias is REUSED "
                            f"with different bindings across builders; needs per-builder "
                            f"scope, not a corpus-wide map"
                        )
                    return f"{base} — resolves to a non-table ({_kinds.get(t, 'absent here')})"
                # ⚑ AMBIGUOUS IS A FINDING, NOT A PICK. The same short alias binds different
                # targets in different builders (`n` → _node here, terms there). Resolving it
                # needs the BUILDER as context, which this column-keyed report does not carry —
                # so name the ambiguity rather than choose one and look resolved.
                return (
                    f"alias bound to {len(tgts)} different targets across builders "
                    f"({', '.join(sorted(tgts)[:4])}…) — ambiguous without builder context"
                )
            if tbl in _subq:
                return (
                    "alias over a DERIVED table (subquery) — no base relation to index; "
                    "the cost lives in the subquery"
                )
            # ⚑ A USE WHOSE DEF IS A RE-DERIVATION — NOT AN ABSENT RELATION.
            #
            # These read as "unresolved" only under a store-shaped question. The right frame is
            # def/use (operator, 2026-08-20: *"This feels more SSA-shaped than anything"*):
            # `modules_index` is `SELECT modules.* FROM modules`, a USE whose reaching DEF is
            # `view.modules` — a compiled projection over `_modules`. There is a definition; it
            # is simply not a stored relation.
            #
            # MEASURED, and it refutes the ⟡viewdef-vs-tenant framing outright: `_modules`,
            # `_structs`, `_refs` exist in NEITHER postgres tenant (live: 28 relations, sandbox:
            # 34) NOR catalog.db (28 relations) — `--rows view.modules` fails with
            # `UndefinedTable: relation "_modules" does not exist`. Nothing lost them; per the
            # operator, **that family is re-derived from the SPPF rather than stored**. So there
            # is no view to materialise and no tenant to blame.
            #
            # An index recommendation is therefore not the right question for these at all: you
            # cannot index a projection that is recomputed. Say that, rather than reporting a
            # gap in this tool.
            _defs = [
                b
                for b, (loc, _s) in _by_builder.items()
                if b.endswith("." + tbl) or b == f"view.{tbl}" or b == f"qb.view.{tbl}"
            ]
            if _defs:
                return (
                    f"USE of a re-derived relation — its DEF is {_defs[0]}, a compiled "
                    f"projection, not a stored table. Nothing to index: the def is "
                    f"recomputed (⟡sppf-rederived, not ⟡resolve-view-columns)."
                )
            return (
                "prefix resolves to no stored relation and no alias binding — likely a "
                "re-derived (SPPF) relation whose DEF this map does not carry; NOT a "
                "verdict that the tree lacks it"
            )
        if _kinds.get(tbl) != "table":
            return "VIEW — resolve to base columns: ⟡resolve-view-columns"
        if op not in fcols:
            return "join key, not a value filter — selectivity not probed (⟡probe-join-keys)"
        return "probe returned nothing (table unreadable, or column missing)"

    rows = []
    for nid in preds:
        op = C.I.nodes[nid].op
        role = roles.get(op, "candidate")
        note = ""
        if role == "candidate" and op in sel:  # base-table VALUE filter → weigh cardinality
            nd, nr = sel[op]
            if nd is None:
                note = f"{nr} rows — too big to probe"
            elif nr < _MIN_ROWS:
                role, note = "low-selectivity", f"{nr}-row table (index moot)"
            elif nd < _MIN_DISTINCT:
                role, note = (
                    "low-selectivity",
                    f"{nd} distinct / {nr} rows (~{nr // max(nd, 1)}/value)",
                )
            else:
                note = f"{nd} distinct / {nr} rows (selective)"
        elif role == "candidate":
            # the builders this predicate actually occurs in — `node_units` already holds it
            note = _why(op, {_uname[u] for u in C.node_units.get(nid, ()) if u in _uname}) or ""
        rows.append(
            (len(C.node_units.get(nid, ())), op, role, note)
        )  # (breadth, colop, role, note)
    _rank = {
        "candidate": 0,
        "indexed": 1,
        "low-selectivity": 2,
        "probe": 3,
    }  # actionable → validated → demoted
    rows.sort(key=lambda r: (_rank[r[2]], -r[0], r[1]))
    return rows


_ROLE_LABEL = {
    "indexed": "indexed (validated)",
    "probe": "probe-source — index IGNORED (counterpart indexed)",
    "low-selectivity": "low-selectivity — index won't help (demoted)",
    "candidate": "CANDIDATE (seek)",
}


def _print_report(C):
    rows = index_report(C)
    print(
        f"⟡index-weight-by-cost — breadth × join-DIRECTION × selectivity over {len(C.units)} interned "
        f"query builders, {C.I.size()} interned nodes\n"
    )
    print("  breadth  join/filter-predicate key         role / note")
    print("  -------  --------------------------------  -----------")
    for breadth, op, role, note in rows:
        lab = _ROLE_LABEL[role] + (f"  [{note}]" if note else "")
        print(f"  {breadth:>5}    {op:<32}  {lab}")
    cands = [(b, op, note) for b, op, role, note in rows if role == "candidate"]
    idxd = [op for _, op, role, _ in rows if role == "indexed"]
    probes = [op for _, op, role, _ in rows if role == "probe"]
    lowsel = [op for _, op, role, _ in rows if role == "low-selectivity"]
    print(
        f"\n  → {len(cands)} genuine NOT-INDEXED candidate(s) after DIRECTION × SELECTIVITY weighting; "
        f"{len(probes)} probe-source(s) + {len(lowsel)} low-selectivity DEMOTED "
        f"(⟡investigate-surfaced-candidates: neither a full-scan probe column nor a low-cardinality filter "
        f"gets used by the planner — measured)."
    )
    print(f"     validated indexes: {', '.join(idxd) or '(none)'}")
    if probes:
        print(f"     demoted probe-sources: {', '.join(probes)}")
    if lowsel:
        print(f"     demoted low-selectivity filters: {', '.join(lowsel)}")
    if cands:
        print("     candidates (rank by breadth; base-table filters carry measured selectivity):")
        # ⚑ NO FALLBACK DIAGNOSIS. This printed "(view / absent-in-this-db — resolve to base:
        # ⟡resolve-view-columns)" whenever `note` was empty — an `else` branch asserting one
        # cause for four, and wrong for the base-table join keys. `index_report` now DERIVES
        # the reason; an empty note here means the deriver itself had nothing, which is a gap
        # in the deriver and says so rather than inventing a cause.
        for b, op, note in cands:
            print(f"       breadth {b:>2}  {op:<28}  {note or '⚑ no diagnosis (gap in _why)'}")
    print(
        f"  COVERAGE: view-def + Core builders (the signal-carrying set); ⟡query-rawtocore-migration widened it."
    )


def selftest():
    """⚑ THIS SUITE PASSED AND WAS UNREADABLE.  It asserted and printed `PASS
    ⟡index-weight-by-cost selftest:` — prose — while `run_selftests` learned every
    result from a `selftest: N/M` regex, so eleven real verifications reported
    SILENT and contributed to no total.

    ⚑ AND A COUNT MEANS ONE CASE PER ASSERTION, NOT A FORMAT-STRING EDIT.  Under
    `assert`, the FIRST failure aborts and the rest never run — so the count and
    the verification arrive together: `check` records every case, and a failing
    ground truth no longer hides the nine behind it.

    ⚑ THE STORE-DEPENDENT HALF IS A DECLARED SKIP.  The demotion ground truths
    need the LIVE index set and row counts; on a store without them the old code
    silently skipped the whole block behind an `if` and still printed `PASS`.  They
    are now counted as SKIPPED with a reason — unrun, and said so."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "scratch"))
    import rungs

    check = rungs.Cases(key="jea/metalanguage/query_registry.py")
    skipped, why = 0, []
    C = build_corpus()
    rows = index_report(C)
    check("the index report has predicate columns", bool(rows), True)
    role = {op: r for _, op, r, _ in rows}
    breadth = {op: b for b, op, _, _ in rows}
    # ground truth 1: path_text.path_id is the validated indexed key, shared across many builders.
    check(
        "path_text.path_id is the validated INDEXED key", role.get("path_text.path_id"), "indexed"
    )
    check("...shared across ≥2 builders", breadth.get("path_text.path_id", 0) >= 2, True)
    # ground truth 2 (⟡investigate-surfaced-candidates): the high-breadth NOT-INDEXED probe-sources and the
    # low-cardinality filter are DEMOTED — an index on them is ignored (measured). DIRECTION classifies the
    # probe-sources 'probe'; SELECTIVITY classifies _unit.copy (2 distinct / 18269) 'low-selectivity'. Both
    # must be EXCLUDED from recommendations. (Needs the live index set + rows.)
    if role.get("path_text.path_id") == "indexed":
        cands = {op for _, op, r, _ in rows if r == "candidate"}
        for spurious in ("_unit.name_pid", "event.ctor_id", "_node.op_path_id"):
            check(
                f"{spurious} is DEMOTED to 'probe' (its counterpart is indexed)",
                role.get(spurious),
                "probe",
            )
            check(f"...so {spurious} is not recommended", spurious in cands, False)
        check(
            "_unit.copy (2 distinct / 18269 rows) is demoted by SELECTIVITY",
            role.get("_unit.copy"),
            "low-selectivity",
        )
        check("...so _unit.copy is not recommended", "_unit.copy" in cands, False)
        # ⟡probe-join-keys — ground truth 3: a JOIN KEY on a base table carries a MEASUREMENT.
        # ⚑ `_selectivity` was fed only value filters (`op in fcols`), on the true-but-
        # insufficient ground that a join column's index utility is about DIRECTION. Direction
        # decides IF an index could serve (and `_roles` already ran it); cardinality decides
        # WHETHER IT IS WORTH ADDING. Six base-table join keys were reported unmeasured for a
        # reason that was never about them. If this restriction returns, `note` goes empty and
        # the diagnosis silently degrades to a cause the column does not have.
        _note = {op: n for _, op, _r, n in rows}
        # ⚑ THE WITNESS MOVED WHEN ⟡index-coverage-wrong-store LANDED, and that is the gate
        # working. This asserted on `node_child.node_id`, a CANDIDATE only because coverage was
        # read from a dead SQLite file; with the declaration as authority it is `indexed`
        # (ix_nc_node) and correctly carries no cardinality. The PROPERTY under test — a
        # base-table JOIN key gets PROBED rather than excused — is unchanged, so it moves to a
        # join key that is genuinely unindexed. Re-pinning the old witness would have asserted
        # the false positive.
        check(
            "obs_node.local_id (a JOIN key on a base table) carries a measurement",
            bool(_note.get("obs_node.local_id")),
            True,
        )
        check(
            "...and it is a cardinality readout, not a 'not probed' excuse",
            "distinct" in (_note.get("obs_node.local_id") or ""),
            True,
        )
        # ⚑ AND THE OVERSIZED ONES MUST STILL SAY SO RATHER THAN GUESS. edge.* is ~64M rows,
        # above `cap`: the honest output is "too big to probe", never a fabricated estimate.
        check(
            "edge.clid is reported as too big to probe, not estimated",
            "too big to probe" in (_note.get("edge.clid") or ""),
            True,
        )
        # ⟡resolve-alias-columns — ground truth 4: a RESOLUTION must name a column that EXISTS.
        # ⚑ The first cut unioned alias bindings across builders and reported `r.lid` as
        # "RESOLVED to terms.lid" — but `terms` is (term_id, text) and has no `lid`. It had
        # matched `JOIN terms AS r` in one builder and applied it to a predicate from another.
        # A confident resolution to a nonexistent column is worse than none: it sends a reader
        # to re-key a predicate onto a column the table does not have.
        _rl = _note.get("r.lid") or ""
        check(
            "r.lid is NOT resolved to a column that does not exist",
            "RESOLVED to a base table" in _rl,
            False,
        )
        check(
            "...it is reported as ambiguous or unresolved instead",
            ("ambiguous" in _rl) or ("no column" in _rl) or ("unresolved" in _rl),
            True,
        )
        # ⟡alias-scope-per-builder — ground truth 5: SCOPE MUST ACTUALLY BIND.
        # ⚑ The first cut keyed the per-builder map on `query_defs.INTERN_BUILDERS`' bare names
        # while `build_corpus` interns them as `qb.<name>` (plus nine local `q_*`). Every lookup
        # missed, `_scoped` returned None for all 32 columns, the unscoped fallback answered —
        # and the output was BYTE-IDENTICAL to before. A scoping layer that silently never binds
        # is indistinguishable from one that works, so the case asserts a column scope RESOLVES
        # that the corpus-wide view could only call ambiguous.
        _nk = _note.get("n.kids") or ""
        check(
            "n.kids resolves via per-builder scope (was corpus-wide ambiguous)",
            "ambiguous" in _nk,
            False,
        )
        check("...to its own builder's derived table", "DERIVED table" in _nk, True)
        check(
            "the per-builder map is keyed as the corpus names them",
            any(k.startswith("qb.") for k in _alias_bindings_by_builder()),
            True,
        )
        # ⟡sppf-rederived — ground truth 6: a USE names its reaching DEF, not a tool gap.
        # ⚑ `modules.is_index` / `structs.qname` were reported as "unresolved prefix … a gap in
        # _alias_bindings". They are neither absent nor a gap: `modules_index` is
        # `SELECT modules.* FROM modules`, a USE whose DEF is `view.modules` — a compiled
        # projection. MEASURED: `_modules`/`_structs` exist in NO tenant (live 28, sandbox 34)
        # and NOT in catalog.db (28) — `--rows view.modules` raises UndefinedTable — because
        # that family is RE-DERIVED from the SPPF rather than stored. An index recommendation
        # is not the right question for a projection that is recomputed, and reporting it as a
        # gap in this tool blamed the instrument for a design.
        _mi = _note.get("modules.is_index") or ""
        check("modules.is_index names its reaching DEF", "DEF is" in _mi, True)
        check("...and says a re-derived def is not indexable", "Nothing to index" in _mi, True)
        # ⟡index-coverage-wrong-store — ground truth 7: COVERAGE COMES FROM THE LIVE AUTHORITY.
        # ⚑ `_live_indexed` read `catalog/catalog.db` via sqlite3 — a 334MB file two weeks
        # stale — while `_selectivity` read live postgres. TWO STORES IN ONE REPORT. The
        # postgres relations do not exist in catalog.db at all, so every PRAGMA returned
        # nothing, the OperationalError handler swallowed it, and `_roles` defaulted them to
        # `candidate`. MEASURED against `schema.py --ddl --live`: `_node` has PRIMARY KEY
        # (node_id); `unit_node` has ix_un_unit/ix_un_node; `node_child` has ix_nc_node — yet
        # all three were the report's HIGHEST-BREADTH candidates (12, 12, 10). A false positive
        # in the direction that generates work: an index proposed for a column that has one.
        # Candidates fell 32 → 26 when the authority was corrected.
        for _already in (
            "_node.node_id",
            "unit_node.unit_id",
            "unit_node.node_id",
            "node_child.node_id",
        ):
            check(
                f"{_already} is INDEXED per the declaration, not a candidate",
                role.get(_already),
                "indexed",
            )
            check(f"...so {_already} is not recommended", _already in cands, False)
    else:
        # ⚑ THE COUNT TRACKS THE BLOCK. 8 demotion cases + 3 ⟡probe-join-keys cases; a skip
        # count that drifts from the guarded block under-reports what went unrun, which is the
        # same silent-skip defect this docstring records.
        skipped += 26
        why.append(
            "the live index set is absent, so the DIRECTION/SELECTIVITY demotion, "
            "⟡probe-join-keys, ⟡resolve-alias-columns, ⟡alias-scope-per-builder, "
            "⟡sppf-rederived and ⟡index-coverage-wrong-store ground truths "
            "cannot be measured"
        )
    print("⟡index-weight-by-cost selftest:")
    print(
        f"  path_text.path_id = validated indexed key (breadth "
        f"{breadth.get('path_text.path_id', 0)}); the "
        f"high-breadth probe-sources (_unit.name_pid, event.ctor_id, _node.op_path_id) are DEMOTED by "
        f"DIRECTION and _unit.copy by SELECTIVITY (2 distinct) — all excluded from recommendations, "
        f"reproducing the ⟡investigate-surfaced-candidates measurement by construction."
    )
    return check.report(skipped=skipped, reason="; ".join(why) or None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--index-report",
        action="store_true",
        help="rank join/filter predicate keys by breadth × join-DIRECTION (probe-sources demoted)",
    )
    ap.add_argument(
        "--selftest",
        action="store_true",
        help="ground-truth: path_text.path_id validated-indexed; measured probe-sources demoted",
    )
    # ⚑ `--candidates` — THE ACTIONABLE HALF, AS A MODE. The full report is ~75 lines of which
    # the last ~32 are what a reader acts on, and asking for them was a `| tail` — which the
    # no-chaining hook refuses, correctly: "show me the candidates grouped by why they are
    # unmeasured" is a QUESTION the tool should answer, not a slice of its output.
    # Grouping by cause is the point: the causes have DIFFERENT repairs, and the old single
    # label hid that ⟡resolve-view-columns owns far fewer rows than it appeared to.
    ap.add_argument(
        "--candidates",
        action="store_true",
        help="just the not-indexed candidates, grouped by WHY each is unmeasured",
    )
    a = ap.parse_args()
    if a.candidates:
        _rows = index_report(build_corpus())
        _c = [(b, op, note) for b, op, role, note in _rows if role == "candidate"]
        groups = {}
        for b, op, note in _c:
            groups.setdefault(note or "⚑ no diagnosis (gap in _why)", []).append((b, op))
        print(
            f"{len(_c)} not-indexed candidate(s), by cause — each cause has a DIFFERENT repair:\n"
        )
        for cause in sorted(groups, key=lambda k: (-sum(b for b, _ in groups[k]), k)):
            members = sorted(groups[cause], key=lambda t: (-t[0], t[1]))
            print(
                f"  ── {cause}   [{len(members)} column(s), Σbreadth {sum(b for b, _ in members)}]"
            )
            for b, op in members:
                print(f"       breadth {b:>2}  {op}")
            print()
        sys.exit(0)
    # ⚑ THE SUITE'S EXIT CODE IS THE PROCESS'S.  This called `selftest()` and
    # returned 0 regardless — so even once the suite counted, a FAILING case
    # would have exited green.  `report()` already returns 0/1; propagate it.
    if a.selftest:
        sys.exit(selftest())
    _print_report(build_corpus())


# selftest-tenant: sandbox
# ⚑ ⟡tenant-pragma — `run_selftests._tenant` reads this and appends the flag. `store.tenant`
# exits 2 on an unstated tenant since ⟡tenant-mandatory (2026-08-24); SANDBOX because a suite
# that reaches the LIVE store can corrupt the corpus it exists to check.
if __name__ == "__main__":
    main()
