#!/usr/bin/env python3
"""query_builders.py — ⟡query-rawtocore-migration: the SINGLE SOURCE for the project's SQL read-queries as
named SQLAlchemy-Core `select()` builders. One builder is BOTH executed at the call site (via `run()`, which
compiles it to SQLite and runs it on the existing sqlite3 connection — no engine churn, result column order
preserved so Row-by-name AND positional access stay drop-in) AND interned by `query_registry.py` for
breadth = index-priority analysis. No drift-prone duplication.

`--verify` is the migration GATE: every builder is paired with its ORIGINAL raw SQL; the harness runs BOTH
against catalog.db and asserts identical row sets. Nothing migrates without passing it.

Reflection-free lightweight Tables: a SELECT compiles correctly from `Column(String)` regardless of declared
type (we never write, only read/intern). Views are modelled as Tables of their OUTPUT columns.
"""
import os, sys, argparse, sqlite3
from sqlalchemy import (MetaData, Table, Column, String, select, bindparam, func, literal, and_, or_,
                        literal_column)
from sqlalchemy.dialects import sqlite

HERE = os.path.dirname(os.path.abspath(__file__))
CATALOG_DB = os.path.join(os.path.dirname(os.path.dirname(HERE)), "catalog", "catalog.db")
_MD = MetaData()
def _T(name, *cols): return Table(name, _MD, *[Column(c, String) for c in cols])

# ── base tables ─────────────────────────────────────────────────────────────────────────────────
path_text  = _T("path_text", "path_id", "text")
terms      = _T("terms", "term_id", "text")
path_seg   = _T("path_seg", "path_id", "ord", "seg_term_id")
_unit      = _T("_unit", "unit_id", "name_pid", "root_id", "file_id", "kind_id", "module_pid", "root_lid", "copy")
_unit_cod  = _T("_unit_cod", "unit_id", "cod_ctor_id", "cod_qname_pid")
_node      = _T("_node", "node_id", "sym", "kind_id", "role_id", "op_term_id", "op_path_id", "lit_id")
node_child = _T("node_child", "node_id", "ord", "child_id")
unit_node  = _T("unit_node", "unit_id", "node_id")
unit_member= _T("unit_member", "unit_id", "ord", "member_name_pid", "member_unit_id")
obs        = _T("obs", "core_id", "local_id", "ekey")
event      = _T("event", "ekey", "ctor_id", "qname_pid", "idx")
edge       = _T("edge", "core_id", "plid", "ord", "clid")
meta       = _T("meta", "key", "value")
_orbit_def = _T("_orbit_def", "unit_id", "type_key", "graded_key", "residue", "stab")
orbit_node = _T("orbit_node", "orbit_id", "sym", "kind_id", "role_id", "op_term_id", "op_path_id", "lit_id")
orbit_member = _T("orbit_member", "orbit_id", "node_id")
# projection VIEWS as Tables (output columns) — the compat views the ad-hoc queries read
node_v     = _T("node", "node_id", "sym", "kind", "role", "op", "lit")
unit_v     = _T("unit", "unit_id", "name", "root_id", "path", "kind", "copy")
node_fanin = _T("node_fanin", "node_id", "fanin")
shared_subtree = _T("shared_subtree", "node_id", "fanin")
# reuse_catalog base tables (backing the compat VIEWS — where the path_text.path_id breadth lives)
_structs   = _T("_structs", "qname_pid", "name_id", "kind_id", "module_pid", "desc_id", "root")
_members   = _T("_members", "struct_qname_pid", "struct_root", "name_id", "ord")
_member_heads = _T("_member_heads", "struct_qname_pid", "struct_root", "head_id")
_refs      = _T("_refs", "struct_qname_pid", "ref_qname_pid")
_edges     = _T("_edges", "src_pid", "dst_pid")
_module_edges = _T("_module_edges", "src_pid", "dst_pid")
_modules   = _T("_modules", "module_pid", "purpose_id", "is_index")


def run(con, stmt, **params):
    """Compile a Core `stmt` to SQLite SQL and execute on the EXISTING sqlite3 connection. Named paramstyle
    (`:x`) so runtime binds pass as a dict; column order is preserved (drop-in for Row/positional reads)."""
    compiled = stmt.compile(dialect=sqlite.dialect(paramstyle="named"))
    p = dict(compiled.params); p.update(params)
    return con.execute(str(compiled), p)


# ════════════════════════════════════ M1 — path_text.path_id carriers ════════════════════════════
def q_node_head():                       # reuse_tui db_rows L92-96
    o = terms.alias("o"); r = terms.alias("r")
    return (select(_node.c.node_id, path_text.c.text, o.c.text, r.c.text)
            .select_from(_node.outerjoin(path_text, path_text.c.path_id == _node.c.op_path_id)
                              .outerjoin(o, o.c.term_id == _node.c.op_term_id)
                              .outerjoin(r, r.c.term_id == _node.c.role_id)))

def q_unit_names():                      # reuse_tui db_rows L149
    return (select(_unit.c.unit_id, path_text.c.text)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid)))

def q_event_head():                      # sppf_db project_sppf L190-192 / project_orbit_sppf L316-318
    tc = terms.alias("tc"); pq = path_text.alias("pq")
    return (select(event.c.ekey, tc.c.text, pq.c.text, event.c.idx)
            .select_from(event.join(tc, tc.c.term_id == event.c.ctor_id)
                              .outerjoin(pq, pq.c.path_id == event.c.qname_pid)))

def q_argperm_uid():                     # sppf_db project_argperm preload L420-421
    return (select(_unit.c.unit_id, path_text.c.text)
            .select_from(_unit.join(path_text, path_text.c.path_id == _unit.c.name_pid))
            .where(_unit.c.copy == "0"))

def q_deserialize_oppath():              # reuse_catalog deserialize_from_projection L315-317
    p2 = path_text.alias("p2")
    return (select(unit_node.c.unit_id, p2.c.text)
            .select_from(unit_node.join(_node, _node.c.node_id == unit_node.c.node_id)
                                  .join(p2, p2.c.path_id == _node.c.op_path_id))
            .where(_node.c.op_path_id.isnot(None)))

def q_reuse_rows(has_copy, limit=None):  # sppf_query reuse_rows L86-96 (DYNAMIC → conditional builder)
    pt = path_text.alias("pt"); o = terms.alias("o"); r = terms.alias("r"); u = _unit.alias("u")
    nd = _node.alias("nd"); un = unit_node.alias("un")
    head = func.coalesce(func.nullif(pt.c.text, ""), o.c.text, r.c.text, "?").label("head")
    units = func.count(func.distinct(un.c.unit_id)).label("units")
    copies = (func.sum(func.coalesce(u.c.copy, 0)) if has_copy else literal_column("NULL")).label("copies")
    stmt = (select(un.c.node_id.label("node_id"), head, units, copies)
            .select_from(un.join(nd, nd.c.node_id == un.c.node_id)
                           .join(u, u.c.unit_id == un.c.unit_id)
                           .outerjoin(pt, pt.c.path_id == nd.c.op_path_id)
                           .outerjoin(o, o.c.term_id == nd.c.op_term_id)
                           .outerjoin(r, r.c.term_id == nd.c.role_id))
            .where(nd.c.node_id.in_(select(node_child.c.node_id)))
            .group_by(un.c.node_id).having(units >= bindparam("min_units"))
            .order_by(units.desc()))
    if limit is not None:
        stmt = stmt.limit(int(limit))
    return stmt


# ════════════════════════════════════ M2 — VIEW models (interned for breadth, NOT executed) ═══════
# The compat VIEWS carry most of the path_text.path_id breadth (each joins it, often ×2). Modelled by their
# FROM/JOIN structure — the join predicates ARE the breadth signal; the GROUP_CONCAT fp/unhold_fp projections
# (structs) are correlated subqueries over _members/_member_heads (NO path_text), so they are simplified to a
# projected literal here — faithful for the index-breadth purpose (they add no path_text.path_id join).
def _a(t, n): return t.alias(n)
def v_structs():                         # reuse_catalog `structs` — path_text ×2 (qname_pid, module_pid)
    s = _structs; pq = _a(path_text, "pq"); pm = _a(path_text, "pm")
    n = _a(terms, "n"); k = _a(terms, "k"); d = _a(terms, "d")
    return (select(pq.c.text, n.c.text, k.c.text, pm.c.text, d.c.text, literal("fp"))
            .select_from(s.join(pq, pq.c.path_id == s.c.qname_pid).join(n, n.c.term_id == s.c.name_id)
                          .join(k, k.c.term_id == s.c.kind_id).join(pm, pm.c.path_id == s.c.module_pid)
                          .join(d, d.c.term_id == s.c.desc_id)))
def v_members():                         # `members` — path_text ×1
    x = _members; psq = _a(path_text, "psq"); n = _a(terms, "n")
    return (select(psq.c.text, n.c.text, x.c.ord)
            .select_from(x.join(psq, psq.c.path_id == x.c.struct_qname_pid).join(n, n.c.term_id == x.c.name_id)))
def v_refs():                            # `refs` — path_text ×2
    x = _refs; psq = _a(path_text, "psq"); pr = _a(path_text, "pr")
    return (select(psq.c.text, pr.c.text)
            .select_from(x.join(psq, psq.c.path_id == x.c.struct_qname_pid).join(pr, pr.c.path_id == x.c.ref_qname_pid)))
def v_edges():                           # `edges` — path_text ×2
    x = _edges; ps = _a(path_text, "ps"); pd = _a(path_text, "pd")
    return (select(ps.c.text, pd.c.text)
            .select_from(x.join(ps, ps.c.path_id == x.c.src_pid).join(pd, pd.c.path_id == x.c.dst_pid)))
def v_module_edges():                    # `module_edges` — path_text ×2
    x = _module_edges; ps = _a(path_text, "ps"); pd = _a(path_text, "pd")
    return (select(ps.c.text, pd.c.text)
            .select_from(x.join(ps, ps.c.path_id == x.c.src_pid).join(pd, pd.c.path_id == x.c.dst_pid)))
def v_modules():                         # `modules` — path_text ×1
    x = _modules; pm = _a(path_text, "pm"); p = _a(terms, "p")
    return (select(pm.c.text, p.c.text, x.c.is_index)
            .select_from(x.join(pm, pm.c.path_id == x.c.module_pid).join(p, p.c.term_id == x.c.purpose_id)))
def v_orbit():                           # sppf_db `orbit` — path_text ×1 (op_path_id)
    n = orbit_node; k = _a(terms, "k"); r = _a(terms, "r"); l = _a(terms, "l"); o = _a(terms, "o"); pt = _a(path_text, "pt")
    return (select(n.c.orbit_id, n.c.sym, k.c.text, r.c.text, o.c.text, l.c.text)
            .select_from(n.join(k, k.c.term_id == n.c.kind_id).join(r, r.c.term_id == n.c.role_id)
                          .join(l, l.c.term_id == n.c.lit_id).outerjoin(o, o.c.term_id == n.c.op_term_id)
                          .outerjoin(pt, pt.c.path_id == n.c.op_path_id)))


# ════════════════════════════════════ R1 — reuse_tui remaining read SELECTs ═══════════════════════
def q_node_child_edges():                # reuse_tui L87 — ORDER-SENSITIVE (builds ordered child lists)
    return select(node_child.c.node_id, node_child.c.child_id).order_by(node_child.c.node_id, node_child.c.ord)
def q_shared_subtree():                  # reuse_tui L98-99 — value binds via run(..., min_fanin=…)
    return select(shared_subtree.c.node_id, shared_subtree.c.fanin).where(shared_subtree.c.fanin >= bindparam("min_fanin"))
def q_defcopy_units():                   # reuse_tui L153-154
    return select(_unit.c.unit_id).where(_unit.c.copy == "1")
def q_unit_node_all():                   # reuse_tui L156
    return select(unit_node.c.unit_id, unit_node.c.node_id)
def q_core_count():                      # reuse_tui L173
    return select(func.count(func.distinct(_unit.c.file_id)))


# builders as nullary thunks for INTERNING by query_registry (parameterized ones bound with a
# representative shape; the bound value is a bindparam node, structure-only — breadth is unaffected).
INTERN_BUILDERS = {
    "node_head": q_node_head, "unit_names": q_unit_names, "event_head": q_event_head,
    "argperm_uid": q_argperm_uid, "deserialize_oppath": q_deserialize_oppath,
    "reuse_rows": lambda: q_reuse_rows(True),
    "node_child_edges": q_node_child_edges, "shared_subtree": q_shared_subtree,
    "defcopy_units": q_defcopy_units, "unit_node_all": q_unit_node_all, "core_count": q_core_count,
    "view.structs": v_structs, "view.members": v_members, "view.refs": v_refs, "view.edges": v_edges,
    "view.module_edges": v_module_edges, "view.modules": v_modules, "view.orbit": v_orbit,
}


# ── the verify REGISTRY: name → (builder callable, verify-kwargs, original raw SQL, raw params) ──
# `run(builder(**bkw))` rows MUST equal `con.execute(raw, rp)` rows (as a multiset).
def _reg():
    return {
        "node_head":       (lambda: q_node_head(), {},
            "SELECT n.node_id, pt.text, o.text, r.text FROM _node n "
            "LEFT JOIN path_text pt ON pt.path_id=n.op_path_id "
            "LEFT JOIN terms o ON o.term_id=n.op_term_id LEFT JOIN terms r ON r.term_id=n.role_id", ()),
        "unit_names":      (lambda: q_unit_names(), {},
            "SELECT u.unit_id, pt.text FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid", ()),
        "event_head":      (lambda: q_event_head(), {},
            "SELECT e.ekey, tc.text, pq.text, e.idx FROM event e JOIN terms tc ON tc.term_id=e.ctor_id "
            "LEFT JOIN path_text pq ON pq.path_id=e.qname_pid", ()),
        "argperm_uid":     (lambda: q_argperm_uid(), {},
            "SELECT u.unit_id, pt.text FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid WHERE u.copy=0", ()),
        "deserialize_oppath": (lambda: q_deserialize_oppath(), {},
            "SELECT un.unit_id, p2.text FROM unit_node un JOIN _node n ON n.node_id=un.node_id "
            "JOIN path_text p2 ON p2.path_id=n.op_path_id WHERE n.op_path_id IS NOT NULL", ()),
        "reuse_rows_copy": (lambda: q_reuse_rows(True), {"min_units": 3},
            "SELECT un.node_id, COALESCE(NULLIF(pt.text,''), o.text, r.text, '?') head, "
            "COUNT(DISTINCT un.unit_id) units, SUM(COALESCE(u.copy,0)) copies FROM unit_node un "
            "JOIN _node nd ON nd.node_id=un.node_id JOIN _unit u ON u.unit_id=un.unit_id "
            "LEFT JOIN path_text pt ON pt.path_id=nd.op_path_id LEFT JOIN terms o ON o.term_id=nd.op_term_id "
            "LEFT JOIN terms r ON r.term_id=nd.role_id WHERE nd.node_id IN (SELECT node_id FROM node_child) "
            "GROUP BY un.node_id HAVING units>=? ORDER BY units DESC", (3,)),
        # R1 reuse_tui:
        "node_child_edges": (lambda: q_node_child_edges(), {},
            "SELECT node_id, child_id FROM node_child ORDER BY node_id, ord", (), True),   # ORDER-SENSITIVE
        "shared_subtree":  (q_shared_subtree, {"min_fanin": 2},
            "SELECT node_id, fanin FROM shared_subtree WHERE fanin>=?", (2,)),
        "defcopy_units":   (lambda: q_defcopy_units(), {},
            "SELECT unit_id FROM _unit WHERE copy=1", ()),
        "unit_node_all":   (lambda: q_unit_node_all(), {},
            "SELECT unit_id, node_id FROM unit_node", ()),
        "core_count":      (lambda: q_core_count(), {},
            "SELECT COUNT(DISTINCT file_id) FROM _unit", ()),
    }


def verify(con, only=None):
    reg = _reg(); ok = 0; fail = []
    for name, entry in reg.items():
        build, bkw, raw, rp = entry[:4]; ordered = entry[4] if len(entry) > 4 else False
        if only and name not in only: continue
        nr = list(map(tuple, run(con, build(), **bkw).fetchall()))
        orr = list(map(tuple, con.execute(raw, rp).fetchall()))
        new = nr if ordered else sorted(nr)          # ORDER-SENSITIVE consumers: compare in order
        old = orr if ordered else sorted(orr)
        if new == old:
            ok += 1; print(f"  ✓ {name:22s} {len(new)} rows — Core == raw")
        else:
            fail.append(name)
            print(f"  ✗ {name:22s} MISMATCH: Core {len(new)} rows vs raw {len(old)} rows")
            for a, b in zip(new[:3], old[:3]):
                if a != b: print(f"      Core {a}\n      raw  {b}")
    print(f"\n{'PASS' if not fail else 'FAIL'} — {ok}/{len([n for n in reg if not only or n in only])} builders result-equivalent"
          + (f"; failures: {fail}" if fail else ""))
    return not fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="assert each builder's rows == its original raw SQL")
    ap.add_argument("--only", nargs="*", help="verify only these builder names")
    a = ap.parse_args()
    con = sqlite3.connect(CATALOG_DB)
    if a.verify:
        sys.exit(0 if verify(con, set(a.only) if a.only else None) else 1)
    ap.print_help()


if __name__ == "__main__":
    main()
