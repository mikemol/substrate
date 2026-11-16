# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The reuse-catalogue RENDER reads, as builders (W39c, family S2).

⚑⚑ CLEANROOMED FROM `jea/metalanguage/query_decl.py` (`q_structs_index` … `q_modedges_all`,
~3052-3114). They SELECT straight from the compat views' output shapes (`structs`, `edges`,
`module_edges`, `modules`, `in_degree`), positionally, as `reuse_catalog`'s renderers read them.
`query_render_selftest` compares each builder's rendered SQL with the origin's.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select

from substrate import query_tables as qt
from substrate.query_ops import eq

if TYPE_CHECKING:
    from sqlalchemy.sql.selectable import Select

# How many of the most-referenced structs the usage page lists.
INDEGREE_TOP = 20

_s = qt.structs_v.c
_e = qt.edges_v.c


def q_structs_index() -> Select:
    """Select name, kind, module and description of every struct (render_index)."""
    return select(_s["name"], _s["kind"], _s["module"], _s["desc"])


def q_structs_namemod() -> Select:
    """Select name and module of every struct (render_index)."""
    return select(_s["name"], _s["module"])


def q_structs_fpnamemod() -> Select:
    """Select fingerprint, name and module of every struct (render_index)."""
    return select(_s["fp"], _s["name"], _s["module"])


def q_modules_index() -> Select:
    """Select module and purpose of every INDEX module (render_index)."""
    m = qt.modules_v.c
    return select(m["module"], m["purpose"]).where(eq(m["is_index"], 1))


def q_structs_qnamekind() -> Select:
    """Select qualified name and kind of every struct (render_graph, render_usage)."""
    return select(_s["qname"], _s["kind"])


def q_edges_all() -> Select:
    """Select every struct edge (render_graph)."""
    return select(_e["src"], _e["dst"])


def q_sitemap() -> Select:
    """Select every struct with its in-degree, zero when it has none (render_sitemap)."""
    deg = qt.indegree_v
    return select(
        _s["qname"],
        _s["module"],
        _s["name"],
        func.coalesce(deg.c["deg"], 0).label("indeg"),
    ).select_from(qt.structs_v.outerjoin(deg, eq(deg.c["qname"], _s["qname"])))


def q_structs_count() -> Select:
    """Count the structs (render_usage)."""
    return select(func.count()).select_from(qt.structs_v)


def q_edges_dst_distinct() -> Select:
    """Select every distinct edge target (render_usage)."""
    return select(_e["dst"]).distinct()


def q_edges_src_distinct() -> Select:
    """Select every distinct edge source (render_usage)."""
    return select(_e["src"]).distinct()


def q_structs_qname() -> Select:
    """Select every struct's qualified name (render_usage)."""
    return select(_s["qname"])


def q_indegree_top() -> Select:
    """Select the most-referenced structs, most first, ties by name (ORDER-SENSITIVE)."""
    deg = qt.indegree_v.c
    return (
        select(deg["qname"], deg["deg"])
        .order_by(deg["deg"].desc(), deg["qname"])
        .limit(INDEGREE_TOP)
    )


def q_modedges_all() -> Select:
    """Select every module edge (render_import)."""
    m = qt.modedges_v.c
    return select(m["src"], m["dst"])
