#!/usr/bin/env python3
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
`path_text` view, hand-fixed to a PK-indexed table on 2026-07-13 — must rank #1 by join-predicate breadth
(i.e. the tool would have surfaced exactly that index). The broad ad-hoc raw→Core migration for fuller
coverage is the separate follow-on ⟡query-rawtocore-migration.
"""
import sys, os, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from jea_pyalg import IR
from jea_pysim import Corpus, Unit
from sqlalchemy import MetaData, Table, Column, String, select

# ── lightweight (reflection-free) Tables: we intern query STRUCTURE, never execute — no DB needed ──
_MD = MetaData()
def _T(name, *cols): return Table(name, _MD, *[Column(c, String) for c in cols])
path_text  = _T("path_text", "path_id", "text")
_unit      = _T("_unit", "unit_id", "name_pid", "root_id", "file_id", "kind_id", "module_pid", "root_lid", "copy")
_node      = _T("_node", "node_id", "sym", "kind_id", "role_id", "op_term_id", "op_path_id", "lit_id")
terms      = _T("terms", "term_id", "text")
unit_node  = _T("unit_node", "unit_id", "node_id")
node_child = _T("node_child", "node_id", "ord", "child_id")
obs        = _T("obs", "core_id", "local_id", "ekey")
event      = _T("event", "ekey", "ctor_id", "qname_pid", "idx")
edge       = _T("edge", "core_id", "plid", "ord", "clid")

# ── the query workload as named build-only Core select()s ──────────────────────────────────────────
# The node/unit VIEW-definition SELECTs (where path_text.path_id is joined) + the existing Core sites
# (graded_orbit.preload_cores / unit_index, autocorr_synth). Each is the STRUCTURE only.
def q_node_view():          # sppf_db `node` view: joins path_text on op_path_id
    return (select(_node.c.node_id, terms.c.text, path_text.c.text)
            .select_from(_node.join(terms, terms.c.term_id == _node.c.kind_id)
                              .outerjoin(path_text, path_text.c.path_id == _node.c.op_path_id)))
def q_unit_view():          # sppf_db `unit` view: joins path_text on name_pid
    return (select(_unit.c.unit_id, path_text.c.text, terms.c.text)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)
                              .join(terms, terms.c.term_id == _unit.c.file_id)))
def q_unit_index():         # graded_orbit.unit_index
    return (select(path_text.c.text, _unit.c.file_id, _unit.c.root_lid)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))
def q_preload_nodes():      # graded_orbit.preload_cores node scan
    return (select(obs.c.core_id, obs.c.local_id, terms.c.text, path_text.c.text, event.c.idx)
            .select_from(obs.join(event, event.c.ekey == obs.c.ekey)
                            .join(terms, terms.c.term_id == event.c.ctor_id)
                            .outerjoin(path_text, path_text.c.path_id == event.c.qname_pid)))
def q_argperm_uid():        # sppf_db.project_argperm's uid map
    return (select(_unit.c.unit_id, path_text.c.text)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))
def q_orbit_def_join():     # graded_orbit.orbit_cosets / cosets_view: _orbit_def → _unit → path_text
    return (select(path_text.c.text, _unit.c.unit_id)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))
def q_reuse_unit_name():    # reuse_tui / reuse_catalog compat: unit name via path_text
    return (select(_unit.c.unit_id, path_text.c.text)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))
def q_autocorr_dupsig():    # autocorr_synth dup-signature: unit_node self-join (NO path_text — a control)
    a = unit_node.alias("a"); b = unit_node.alias("b")
    return (select(a.c.unit_id, b.c.unit_id)
            .select_from(a.join(b, a.c.node_id == b.c.node_id)))
def q_reuse_nodechild():    # a reuse query over node_child (NO path_text — a control)
    return (select(unit_node.c.unit_id, node_child.c.child_id)
            .select_from(unit_node.join(node_child, node_child.c.node_id == unit_node.c.node_id)))

BUILDERS = {
    "node_view": q_node_view, "unit_view": q_unit_view, "unit_index": q_unit_index,
    "preload_nodes": q_preload_nodes, "argperm_uid": q_argperm_uid, "orbit_def_join": q_orbit_def_join,
    "reuse_unit_name": q_reuse_unit_name, "autocorr_dupsig": q_autocorr_dupsig, "reuse_nodechild": q_reuse_nodechild,
}
# ⟡query-rawtocore-migration: the migrated ad-hoc queries (single source in query_builders) are interned
# here too — one builder is BOTH executed (via query_builders.run at the call site) AND interned for breadth.
from query_builders import INTERN_BUILDERS as _QB_BUILDERS
BUILDERS.update({f"qb.{k}": v for k, v in _QB_BUILDERS.items()})

# ── ClauseLowerer: SQLAlchemy Select/ClauseElement → IR, bottom-up, interned into Corpus.I ─────────
class ClauseLowerer:
    """A third front-end beside jea_pyalg.Lowerer/CstLowerer. Head ‖ children, children-as-interned-ids —
    a Column's referential identity ('table.col') sits in `op` exactly like a free Name/Attribute; a Join /
    Compare wraps its parts as children. The interner content-addresses the shared structure; a predicate
    node (Compare over two Columns) shared across queries gets fanin/node_units breadth for free."""
    def __init__(self, I): self.I = I

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
            opn = getattr(getattr(el, "operator", None), "__name__", str(getattr(el, "operator", "")))
            return self.I.intern(IR(kind="Compare", op=opn,
                                    children=(self.lower(el.left), self.lower(el.right))))
        if cn in ("BooleanClauseList", "ClauseList"):          # AND/OR of predicates
            opn = getattr(getattr(el, "operator", None), "__name__", "and_")
            return self.I.intern(IR(kind="Bool", op=opn, children=tuple(self.lower(c) for c in el.clauses)))
        if hasattr(el, "get_final_froms"):                     # a Select
            kids = [self.lower(c) for c in el.selected_columns]
            kids += [self.lower(f) for f in el.get_final_froms()]
            if el.whereclause is not None:
                kids.append(self.lower(el.whereclause))
            return self.I.intern(IR(kind="Select", children=tuple(kids)))
        # leaf fallback (alias-wrapped column, bindparam, literal, …): keep a stable op where possible
        if tbl is not None and hasattr(el, "name"):
            return self.I.intern(IR(kind="Column", op=f"{self._base_table(tbl)}.{el.name}"))
        return self.I.intern(IR(kind=cn, op=str(getattr(el, "key", "") or getattr(el, "value", "") or "")))


def build_corpus(builders=BUILDERS):
    """Intern every builder as a query Unit (mirrors jea_pysim.add_file:121-128 register shape)."""
    C = Corpus(); lw = ClauseLowerer(C.I)
    for name, fn in builders.items():
        root = lw.lower(fn())
        sup = C._support(root)
        C.units.append(Unit(name=name, path="query", lineno=-1, root=root, support=sup,
                            depth=C._depth_map(root)))
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
    """best-effort: which 'table.column' predicate keys are ALREADY covered by an index in catalog.db
    (PK or any index's first column). Annotation only; absent DB → empty."""
    import sqlite3
    db = os.path.join(os.path.dirname(os.path.dirname(HERE)), "catalog", "catalog.db")
    covered = set()
    if not os.path.exists(db): return covered
    con = sqlite3.connect(db)
    for tbl in {op.split(".")[0] for op in colops}:
        try:
            for r in con.execute(f"PRAGMA table_info({tbl})"):
                if r[5]:                                        # pk flag
                    covered.add(f"{tbl}.{r[1]}")
            for idx in con.execute(f"PRAGMA index_list({tbl})"):
                info = list(con.execute(f"PRAGMA index_info({idx[1]})"))
                if info: covered.add(f"{tbl}.{info[0][2]}")     # first indexed column
        except sqlite3.OperationalError:
            pass
    con.close(); return covered


def index_report(C):
    preds = _predicate_columns(C)
    rows = []                                                   # (breadth, colop, indexed?)
    colops = {C.I.nodes[nid].op for nid in preds}
    covered = _live_indexed(colops)
    for nid in preds:
        op = C.I.nodes[nid].op
        breadth = len(C.node_units.get(nid, ()))               # # distinct queries using this predicate key
        rows.append((breadth, op, op in covered))
    rows.sort(key=lambda r: (-r[0], r[1]))
    return rows


def _print_report(C):
    rows = index_report(C)
    print(f"⟡query-sppf-intern index-from-breadth — {len(C.units)} interned query builders "
          f"(view-def SELECTs + Core sites), {C.I.size()} interned nodes\n")
    print("  breadth  join/filter-predicate key         index status")
    print("  -------  --------------------------------  ------------")
    for breadth, op, indexed in rows:
        print(f"  {breadth:>5}    {op:<32}  {'indexed' if indexed else 'NOT INDEXED — candidate'}")
    if rows:
        top = rows[0]
        print(f"\n  → top join-predicate by breadth: {top[1]} (breadth {top[0]}). "
              f"COVERAGE: view-def + Core builders only (the signal-carrying set); the broad ad-hoc raw→Core "
              f"migration (⟡query-rawtocore-migration) widens it.")


def selftest():
    C = build_corpus()
    rows = index_report(C)
    assert rows, "index report must have predicate columns"
    top_op = rows[0][1]
    assert top_op == "path_text.path_id", f"ground truth: path_text.path_id must rank #1 by breadth, got {top_op}"
    # the shared predicate node is interned ONCE and carries cross-query breadth ≥ 2
    assert rows[0][0] >= 2, "path_text.path_id must be shared across ≥2 query builders"
    # a control predicate that appears in exactly one builder has breadth 1 (no over-merge)
    assert any(b == 1 for b, _, _ in rows), "single-use predicates keep breadth 1 (no spurious merge)"
    print("PASS ⟡query-sppf-intern selftest:")
    print(f"  path_text.path_id ranks #1 by join-predicate breadth ({rows[0][0]} builders) — the tool would "
          f"have surfaced the hand-done path_text PK-index fix.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index-report", action="store_true", help="rank join/filter predicate keys by breadth")
    ap.add_argument("--selftest", action="store_true", help="ground-truth: path_text.path_id ranks #1")
    a = ap.parse_args()
    if a.selftest: selftest(); return
    _print_report(build_corpus())


if __name__ == "__main__":
    main()
