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
_unit      = _T("_unit", "unit_id", "name_pid", "root_id", "file_id", "kind_id", "module_pid", "root_lid", "copy", "level")
_unit_cod  = _T("_unit_cod", "unit_id", "cod_ctor_id", "cod_qname_pid")
_node      = _T("_node", "node_id", "sym", "kind_id", "role_id", "op_term_id", "op_path_id", "lit_id")
node_child = _T("node_child", "node_id", "ord", "child_id")
unit_node  = _T("unit_node", "unit_id", "node_id")
unit_member= _T("unit_member", "unit_id", "ord", "member_name_pid", "member_unit_id")
obs        = _T("obs", "core_id", "local_id", "ekey")
event      = _T("event", "ekey", "ctor_id", "qname_pid", "idx", "lit_id")
unit_obs   = _T("unit_obs", "core_id", "unit_id", "name_pid", "root_lid", "kind_id", "module_pid", "copy", "level")
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
# reuse_catalog compat VIEWS as OUTPUT-column Tables (physical views in catalog.db; SELECT straight from them
# to REPRODUCE render rows — distinct from the simplified v_* interning models above) ── ⟡rewire-catalog-render
structs_v  = _T("structs", "qname", "name", "kind", "module", "fp", "desc", "root", "unhold_fp")
edges_v    = _T("edges", "src", "dst")
modedges_v = _T("module_edges", "src", "dst")
modules_v  = _T("modules", "module", "purpose", "is_index")
indegree_v = _T("in_degree", "qname", "deg")


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

def q_event_head():                      # sppf_db project_sppf / project_orbit_sppf (head + ⟡gqs-lit-propagate lit)
    tc = terms.alias("tc"); pq = path_text.alias("pq"); lt = terms.alias("lt")
    return (select(event.c.ekey, tc.c.text, pq.c.text, event.c.idx, lt.c.text)
            .select_from(event.join(tc, tc.c.term_id == event.c.ctor_id)
                              .outerjoin(pq, pq.c.path_id == event.c.qname_pid)
                              .outerjoin(lt, lt.c.term_id == event.c.lit_id)))


def q_set1_count():                      # ⟡gqs-S0.2: the Set₁ census as a COLUMN READ (was set1_ratchet's 94s decode)
    return select(func.count()).select_from(unit_obs).where(unit_obs.c.level >= 1)

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
    pt = path_text.alias("pt"); o = terms.alias("o"); r = terms.alias("r"); u = unit_v.alias("u")   # the `unit` VIEW
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


# ════════════════════════════════════ R2 — sppf_db projection reads (LOAD-BEARING) ════════════════
def q_event_ctor():   return select(event.c.ekey, terms.c.text).select_from(event.join(terms, terms.c.term_id == event.c.ctor_id))  # L198-199
def q_obs_all():      return select(obs.c.core_id, obs.c.local_id, obs.c.ekey)          # L200 / L324
def q_edge_all():     return select(edge.c.core_id, edge.c.plid, edge.c.ord, edge.c.clid)  # L202 / L326
def q_count_shared(): return select(func.count()).select_from(shared_subtree)          # project_sppf return
def q_max_node_len(): return select(func.max(func.length(_node.c.node_id)))            # project_sppf return


# ════════════════════════════════════ S1 — sppf_db ORBIT/argperm stat reads (⟡rewire-orbit-stats) ═
def q_max_orbit_len():    return select(func.max(func.length(orbit_node.c.orbit_id)))                    # project_orbit_sppf return L384
def q_orbit_def_stats():  return (select(func.count(), func.count(func.distinct(_orbit_def.c.type_key)),
                                         func.count(func.distinct(_orbit_def.c.graded_key)))
                                  .select_from(_orbit_def))                                              # __main__ argperm L467-468
def q_orbit_node_count(): return select(func.count()).select_from(orbit_node)                            # __main__ orbit L474
def q_orbit_packings():   return select(func.count(func.distinct(orbit_member.c.node_id))).select_from(orbit_member)  # L475
def q_orbit_merged():                                                                                    # __main__ orbit L476
    sub = select(orbit_member.c.orbit_id).group_by(orbit_member.c.orbit_id).having(func.count() > 1).subquery()
    return select(func.count()).select_from(sub)


# ════════════════════════════════ ⟡L7 — recursion→parallel: the reachability closure as a WITH RECURSIVE CTE ═
# The declarative form of the eager python reachability DFS (_support jea_pysim.py:80 / _subnodes jea_pyalg.py:656
# / the unit_node builder sppf_db.py:270-278): the transitive closure of node_child from a root. UNION (not
# UNION ALL) dedups → distinct closure, O(V+E), matching the python seen-set (byte-exact: 59794 vs 59794). This
# is the recursion→parallel grade-transition made concrete — a greatest-fp recursion lifted to a least-fixpoint
# saturation SQLite evaluates in one pass, no python materialization. ⟡graded-relational-carrier / sql_lift ⟡L6.
def q_reach():
    anchor = select(bindparam("root", type_=String).label("node_id")).cte("reach", recursive=True)
    step = select(node_child.c.child_id).select_from(node_child.join(anchor, node_child.c.node_id == anchor.c.node_id))
    reach = anchor.union(step)                                       # UNION = distinct closure (dedup ⇒ terminates)
    return select(reach.c.node_id)


# ════════════════════════════════════ S2 — reuse_catalog render_* view reads (⟡rewire-catalog-render) ═
# positional reads (reuse_catalog has no row_factory); SELECT straight from the physical compat views.
def q_structs_index():     return select(structs_v.c.name, structs_v.c.kind, structs_v.c.module, structs_v.c["desc"])  # render_index L491
def q_structs_namemod():   return select(structs_v.c.name, structs_v.c.module)                          # render_index L494
def q_structs_fpnamemod(): return select(structs_v.c.fp, structs_v.c.name, structs_v.c.module)          # render_index L497
def q_modules_index():     return select(modules_v.c.module, modules_v.c.purpose).where(modules_v.c.is_index == 1)  # render_index L500
def q_structs_qnamekind(): return select(structs_v.c.qname, structs_v.c.kind)                           # render_graph L547 / render_usage L666
def q_edges_all():         return select(edges_v.c.src, edges_v.c.dst)                                  # render_graph L548
def q_sitemap():                                                                                        # render_sitemap L617-618
    return (select(structs_v.c.qname, structs_v.c.module, structs_v.c.name,
                   func.coalesce(indegree_v.c.deg, 0).label("indeg"))
            .select_from(structs_v.outerjoin(indegree_v, indegree_v.c.qname == structs_v.c.qname)))
def q_structs_count():     return select(func.count()).select_from(structs_v)                           # render_usage L640
def q_edges_dst_distinct():return select(edges_v.c.dst).distinct()                                      # render_usage L641
def q_edges_src_distinct():return select(edges_v.c.src).distinct()                                      # render_usage L642
def q_structs_qname():     return select(structs_v.c.qname)                                             # render_usage L643
def q_indegree_top():      return select(indegree_v.c.qname, indegree_v.c.deg).order_by(indegree_v.c.deg.desc(), indegree_v.c.qname).limit(20)  # render_usage L647 ORDERED
def q_modedges_all():      return select(modedges_v.c.src, modedges_v.c.dst)                            # render_import L682


# ════════════════════════════════════ R1 — reuse_catalog deserialize base reads (positional) ══════
def q_pathtext_all():  return select(path_text.c.path_id, path_text.c.text)            # L303
def q_terms_all():     return select(terms.c.term_id, terms.c.text)                    # L304
def q_unit_fields():   return select(_unit.c.unit_id, _unit.c.name_pid, _unit.c.kind_id, _unit.c.module_pid, _unit.c.root_lid)  # L305-307
def q_unit_cod():      return select(_unit_cod.c.unit_id, _unit_cod.c.cod_ctor_id, _unit_cod.c.cod_qname_pid)  # L308-309
def q_unit_member():   return select(unit_member.c.unit_id, unit_member.c.ord, unit_member.c.member_name_pid,  # L311-312 ORDERED
                                     unit_member.c.member_unit_id).order_by(unit_member.c.unit_id, unit_member.c.ord)
def q_meta_failed():   return select(meta.c.value).where(meta.c.key == "failed")       # L485


# ════════════════════════════════════ R1 — sppf_query read SELECTs (labels matter: sqlite3.Row) ═══
def _head(nd): return func.coalesce(func.nullif(nd.c.op, ""), nd.c.role, nd.c.kind).label("head")
def q_uid():                             # sppf_query _uid L27 (view `unit`)
    return select(unit_v.c.unit_id).where(or_(unit_v.c.name == bindparam("name"),
                                              unit_v.c.name.like(bindparam("likep"))))
def q_support_count():                   # sppf_query L33 / L61
    return select(func.count().label("k")).select_from(unit_node).where(unit_node.c.unit_id == bindparam("uid"))
def q_support_hist():                    # sppf_query L35-37
    un = unit_node.alias("un"); nd = node_v.alias("nd"); h = _head(nd); k = func.count().label("k")
    return (select(h, k).select_from(un.join(nd, nd.c.node_id == un.c.node_id))
            .where(un.c.unit_id == bindparam("uid")).group_by(h).order_by(k.desc()).limit(12))
def q_fanin():                           # sppf_query L42-44
    nf = node_fanin.alias("nf"); nd = node_v.alias("nd")
    return (select(nf.c.node_id, _head(nd), nf.c.fanin)
            .select_from(nf.join(nd, nd.c.node_id == nf.c.node_id)).order_by(nf.c.fanin.desc()).limit(bindparam("lim")))
def q_extract():                         # sppf_query L50-54
    un = unit_node.alias("un"); nd = node_v.alias("nd"); units = func.count(func.distinct(un.c.unit_id)).label("units")
    return (select(un.c.node_id, _head(nd), units).select_from(un.join(nd, nd.c.node_id == un.c.node_id))
            .where(un.c.node_id.in_(select(node_child.c.node_id)))
            .group_by(un.c.node_id).having(units >= bindparam("m")).order_by(units.desc()).limit(20))
def q_clusters_overlap():                # sppf_query L63-68
    a = unit_node.alias("a"); b = unit_node.alias("b"); v = unit_v.alias("v"); shared = func.count().label("shared")
    return (select(v.c.name, shared, bindparam("sz").label("sz"))
            .select_from(a.join(b, a.c.node_id == b.c.node_id).join(v, v.c.unit_id == b.c.unit_id))
            .where(and_(a.c.unit_id == bindparam("uid"), b.c.unit_id != bindparam("uid")))
            .group_by(b.c.unit_id).having((1.0 * func.count() / bindparam("sz")) >= bindparam("thr"))
            .order_by(shared.desc()).limit(15))


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
    "uid": q_uid, "support_count": q_support_count, "support_hist": q_support_hist, "fanin": q_fanin,
    "extract": q_extract, "clusters_overlap": q_clusters_overlap,
    "pathtext_all": q_pathtext_all, "terms_all": q_terms_all, "unit_fields": q_unit_fields,
    "unit_cod": q_unit_cod, "unit_member": q_unit_member, "meta_failed": q_meta_failed,
    "event_ctor": q_event_ctor, "obs_all": q_obs_all, "edge_all": q_edge_all,
    "count_shared": q_count_shared, "max_node_len": q_max_node_len, "set1_count": q_set1_count,
    "view.structs": v_structs, "view.members": v_members, "view.refs": v_refs, "view.edges": v_edges,
    "view.module_edges": v_module_edges, "view.modules": v_modules, "view.orbit": v_orbit,
    # S1 orbit-stats:
    "max_orbit_len": q_max_orbit_len, "orbit_def_stats": q_orbit_def_stats,
    "orbit_node_count": q_orbit_node_count, "orbit_packings": q_orbit_packings, "orbit_merged": q_orbit_merged,
    "reach": q_reach,   # ⟡L7 recursion→parallel: WITH RECURSIVE reachability closure
    # S2 render:
    "structs_index": q_structs_index, "structs_namemod": q_structs_namemod,
    "structs_fpnamemod": q_structs_fpnamemod, "modules_index": q_modules_index,
    "structs_qnamekind": q_structs_qnamekind, "edges_all": q_edges_all, "sitemap": q_sitemap,
    "structs_count": q_structs_count, "edges_dst_distinct": q_edges_dst_distinct,
    "edges_src_distinct": q_edges_src_distinct, "structs_qname": q_structs_qname,
    "indegree_top": q_indegree_top, "modedges_all": q_modedges_all,
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
            "SELECT e.ekey, tc.text, pq.text, e.idx, lt.text FROM event e JOIN terms tc ON tc.term_id=e.ctor_id "
            "LEFT JOIN path_text pq ON pq.path_id=e.qname_pid LEFT JOIN terms lt ON lt.term_id=e.lit_id", ()),
        "set1_count":      (lambda: q_set1_count(), {},
            "SELECT COUNT(*) FROM unit_obs WHERE level >= 1", ()),
        "argperm_uid":     (lambda: q_argperm_uid(), {},
            "SELECT u.unit_id, pt.text FROM _unit u JOIN path_text pt ON pt.path_id=u.name_pid WHERE u.copy=0", ()),
        "deserialize_oppath": (lambda: q_deserialize_oppath(), {},
            "SELECT un.unit_id, p2.text FROM unit_node un JOIN _node n ON n.node_id=un.node_id "
            "JOIN path_text p2 ON p2.path_id=n.op_path_id WHERE n.op_path_id IS NOT NULL", ()),
        "reuse_rows_copy": (lambda: q_reuse_rows(True), {"min_units": 3},
            "SELECT un.node_id, COALESCE(NULLIF(pt.text,''), o.text, r.text, '?') head, "
            "COUNT(DISTINCT un.unit_id) units, SUM(COALESCE(u.copy,0)) copies FROM unit_node un "
            "JOIN _node nd ON nd.node_id=un.node_id JOIN unit u ON u.unit_id=un.unit_id "
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
        # R1 sppf_query (dynamic params: resolve a sample uid/name/size at run time):
        "uid":             (q_uid, lambda c: {"name": _samp(c)[1], "likep": "%." + _samp(c)[1]},
            "SELECT unit_id FROM unit WHERE name=? OR name LIKE ?",
            lambda c: (_samp(c)[1], "%." + _samp(c)[1])),
        "support_count":   (q_support_count, lambda c: {"uid": _samp(c)[0]},
            "SELECT COUNT(*) k FROM unit_node WHERE unit_id=?", lambda c: (_samp(c)[0],)),
        "support_hist":    (q_support_hist, lambda c: {"uid": _samp(c)[0]},
            "SELECT COALESCE(NULLIF(nd.op,''), nd.role, nd.kind) head, COUNT(*) k FROM unit_node un "
            "JOIN node nd ON nd.node_id=un.node_id WHERE un.unit_id=? GROUP BY head ORDER BY k DESC LIMIT 12",
            lambda c: (_samp(c)[0],), True),                          # ORDER BY k DESC
        "fanin":           (q_fanin, {"lim": 20},
            "SELECT nf.node_id, COALESCE(NULLIF(nd.op,''),nd.role,nd.kind) head, nf.fanin FROM node_fanin nf "
            "JOIN node nd ON nd.node_id=nf.node_id ORDER BY nf.fanin DESC LIMIT ?", (20,), True),   # ORDER BY fanin DESC
        "extract":         (q_extract, {"m": 3},
            "SELECT un.node_id, COALESCE(NULLIF(nd.op,''),nd.role,nd.kind) head, COUNT(DISTINCT un.unit_id) units "
            "FROM unit_node un JOIN node nd ON nd.node_id=un.node_id WHERE nd.node_id IN (SELECT node_id FROM node_child) "
            "GROUP BY un.node_id HAVING units>=? ORDER BY units DESC LIMIT 20", (3,), True),         # ORDER BY units DESC
        "clusters_overlap": (q_clusters_overlap, lambda c: {"sz": _samp(c)[2], "uid": _samp(c)[0], "thr": 0.0},
            "SELECT v.name, COUNT(*) shared, ? sz FROM unit_node a JOIN unit_node b ON a.node_id=b.node_id "
            "JOIN unit v ON v.unit_id=b.unit_id WHERE a.unit_id=? AND b.unit_id!=? GROUP BY b.unit_id "
            "HAVING (1.0*shared/?) >= ? ORDER BY shared DESC LIMIT 15",
            lambda c: (_samp(c)[2], _samp(c)[0], _samp(c)[0], _samp(c)[2], 0.0), True),              # ORDER BY shared DESC
        # R1 reuse_catalog deserialize base reads:
        "pathtext_all":  (q_pathtext_all, {}, "SELECT path_id, text FROM path_text", ()),
        "terms_all":     (q_terms_all, {}, "SELECT term_id, text FROM terms", ()),
        "unit_fields":   (q_unit_fields, {}, "SELECT unit_id, name_pid, kind_id, module_pid, root_lid FROM _unit", ()),
        "unit_cod":      (q_unit_cod, {}, "SELECT unit_id, cod_ctor_id, cod_qname_pid FROM _unit_cod", ()),
        "unit_member":   (q_unit_member, {}, "SELECT unit_id, ord, member_name_pid, member_unit_id FROM unit_member ORDER BY unit_id, ord", (), True),
        # R2 sppf_db projection reads:
        "event_ctor":    (q_event_ctor, {}, "SELECT e.ekey, tc.text FROM event e JOIN terms tc ON tc.term_id=e.ctor_id", ()),
        "obs_all":       (q_obs_all, {}, "SELECT core_id, local_id, ekey FROM obs", ()),
        "edge_all":      (q_edge_all, {}, "SELECT core_id, plid, ord, clid FROM edge", ()),
        "count_shared":  (q_count_shared, {}, "SELECT COUNT(*) FROM shared_subtree", ()),
        "max_node_len":  (q_max_node_len, {}, "SELECT MAX(LENGTH(node_id)) FROM _node", ()),
        # S1 — sppf_db ORBIT/argperm stats (group "orbit": _orbit_def now; orbit_node/orbit_member after populate):
        "max_orbit_len":   (q_max_orbit_len, {}, "SELECT MAX(LENGTH(orbit_id)) FROM orbit_node", ()),
        "orbit_def_stats": (q_orbit_def_stats, {},
            "SELECT COUNT(*), COUNT(DISTINCT type_key), COUNT(DISTINCT graded_key) FROM _orbit_def", ()),
        "orbit_node_count":(q_orbit_node_count, {}, "SELECT COUNT(*) FROM orbit_node", ()),
        "orbit_packings":  (q_orbit_packings, {}, "SELECT COUNT(DISTINCT node_id) FROM orbit_member", ()),
        "orbit_merged":    (q_orbit_merged, {},
            "SELECT COUNT(*) FROM (SELECT orbit_id FROM orbit_member GROUP BY orbit_id HAVING COUNT(*)>1)", ()),
        # ⟡L7 — the WITH RECURSIVE reachability closure == the eager python _support/_subnodes walk (group "recur"):
        "reach": (q_reach, lambda c: {"root": _samp_node(c)},
            "WITH RECURSIVE reach(node_id) AS (SELECT :root UNION "
            "SELECT nc.child_id FROM reach r JOIN node_child nc ON nc.node_id=r.node_id) SELECT node_id FROM reach",
            lambda c: {"root": _samp_node(c)}),
        # S2 — reuse_catalog render_* view reads (group "render": target the reuse-catalog output db —
        # structs/edges/module_edges/modules/in_degree/meta, populated by reuse_catalog's build):
        "meta_failed":       (q_meta_failed, {}, "SELECT value FROM meta WHERE key='failed'", ()),
        "structs_index":     (q_structs_index, {}, "SELECT name, kind, module, desc FROM structs", ()),
        "structs_namemod":   (q_structs_namemod, {}, "SELECT name, module FROM structs", ()),
        "structs_fpnamemod": (q_structs_fpnamemod, {}, "SELECT fp, name, module FROM structs", ()),
        "modules_index":     (q_modules_index, {}, "SELECT module, purpose FROM modules WHERE is_index = 1", ()),
        "structs_qnamekind": (q_structs_qnamekind, {}, "SELECT qname, kind FROM structs", ()),
        "edges_all":         (q_edges_all, {}, "SELECT src, dst FROM edges", ()),
        "sitemap":           (q_sitemap, {},
            "SELECT s.qname, s.module, s.name, COALESCE(d.deg, 0) AS indeg "
            "FROM structs s LEFT JOIN in_degree d ON d.qname = s.qname", ()),
        "structs_count":     (q_structs_count, {}, "SELECT COUNT(*) FROM structs", ()),
        "edges_dst_distinct":(q_edges_dst_distinct, {}, "SELECT DISTINCT dst FROM edges", ()),
        "edges_src_distinct":(q_edges_src_distinct, {}, "SELECT DISTINCT src FROM edges", ()),
        "structs_qname":     (q_structs_qname, {}, "SELECT qname FROM structs", ()),
        "indegree_top":      (q_indegree_top, {},
            "SELECT qname, deg FROM in_degree ORDER BY deg DESC, qname LIMIT 20", (), True),   # ORDER-SENSITIVE
        "modedges_all":      (q_modedges_all, {}, "SELECT src, dst FROM module_edges", ()),
    }


# builder groups: the default `--verify` covers only "catalog" (the SPPF catalog.db); render/orbit builders
# target SECONDARY projections (need their db populated) and are opt-in via `--group render|orbit` (`--group all`
# runs every group). ⟡rewire-secondary-projections.
_GROUP = {n: "render" for n in ("meta_failed", "structs_index", "structs_namemod", "structs_fpnamemod",
          "modules_index", "structs_qnamekind", "edges_all", "sitemap", "structs_count",
          "edges_dst_distinct", "edges_src_distinct", "structs_qname", "indegree_top", "modedges_all")}
_GROUP.update({n: "orbit" for n in ("max_orbit_len", "orbit_def_stats", "orbit_node_count",
                                    "orbit_packings", "orbit_merged")})
_GROUP["reach"] = "recur"   # ⟡L7 recursion→parallel (needs node_child; verified on the SPPF catalog.db)
def _group_of(name): return _GROUP.get(name, "catalog")


_SAMP = None
def _samp(con):
    """a stable sample (uid, name, size) for verifying uid-parameterized builders — a unit with many nodes."""
    global _SAMP
    if _SAMP is None:
        uid, sz = con.execute("SELECT unit_id, COUNT(*) k FROM unit_node GROUP BY unit_id "
                              "ORDER BY k DESC LIMIT 1").fetchone()
        name = con.execute("SELECT name FROM unit WHERE unit_id=?", (uid,)).fetchone()[0]
        _SAMP = (uid, name, sz)
    return _SAMP


_SAMPN = None
def _samp_node(con):
    """a stable sample root for the reachability CTE — the node with the most children (a deep closure)."""
    global _SAMPN
    if _SAMPN is None:
        _SAMPN = con.execute("SELECT node_id FROM node_child GROUP BY node_id "
                             "ORDER BY COUNT(*) DESC LIMIT 1").fetchone()[0]
    return _SAMPN


def verify(con, only=None, group="catalog"):
    reg = _reg(); ok = 0; fail = []; sel = []
    for name, entry in reg.items():
        if group is not None and _group_of(name) != group: continue   # None = all groups
        if only and name not in only: continue
        sel.append(name)
        build, bkw, raw, rp = entry[:4]; ordered = entry[4] if len(entry) > 4 else False
        bkw = bkw(con) if callable(bkw) else bkw     # dynamic params (e.g. a sample uid resolved at run)
        rp = rp(con) if callable(rp) else rp
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
    print(f"\n{'PASS' if not fail else 'FAIL'} — {ok}/{len(sel)} builders result-equivalent"
          + (f"; failures: {fail}" if fail else ""))
    return not fail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="assert each builder's rows == its original raw SQL")
    ap.add_argument("--only", nargs="*", help="verify only these builder names")
    ap.add_argument("--db", default=CATALOG_DB, help="db to verify against (default catalog.db; a COPY for render/orbit)")
    ap.add_argument("--group", default="catalog",
                    help="builder group to verify: catalog (default, the SPPF db) | render | orbit | all")
    a = ap.parse_args()
    con = sqlite3.connect(a.db)
    if a.verify:
        grp = None if a.group == "all" else a.group
        sys.exit(0 if verify(con, set(a.only) if a.only else None, grp) else 1)
    ap.print_help()


if __name__ == "__main__":
    main()
