# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The reuse-catalogue compat views, as interning builders (W39c, the first builder family).

⚑⚑ CLEANROOMED FROM `jea/metalanguage/query_decl.py` (`v_members` … `v_modules`, ~2544-2588). The
origin is behind the per-file gate; `query_catalog_selftest` compares each builder's rendered SQL
with the origin's.

⚑ THESE ARE INDEX-BREADTH MODELS, NOT THE STORED VIEWS. Each reproduces a compat view's FROM/JOIN
structure — the join predicates are the `path_text.path_id` breadth the index planner reads — over
the reuse-catalogue base tables. `v_structs`' `fp` projection is a LITERAL in the origin too: the
real view's fingerprint is a correlated subquery over `_members`/`_member_heads` that adds no
`path_text` join, so for the index-breadth purpose a projected literal is faithful.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import literal, select

from substrate import query_tables as qt

if TYPE_CHECKING:
    from sqlalchemy import Table
    from sqlalchemy.sql.selectable import Select


def v_structs() -> Select:
    """`structs` — qualified name, name, kind, module, description; `path_text` joined twice."""
    s = qt.structs
    pq = qt.path_text.alias("pq")
    pm = qt.path_text.alias("pm")
    name = qt.terms.alias("n")
    kind = qt.terms.alias("k")
    desc = qt.terms.alias("d")
    return select(
        pq.c["text"], name.c["text"], kind.c["text"], pm.c["text"], desc.c["text"], literal("fp")
    ).select_from(
        s.join(pq, pq.c["path_id"] == s.c["qname_pid"])
        .join(name, name.c["term_id"] == s.c["name_id"])
        .join(kind, kind.c["term_id"] == s.c["kind_id"])
        .join(pm, pm.c["path_id"] == s.c["module_pid"])
        .join(desc, desc.c["term_id"] == s.c["desc_id"])
    )


def v_members() -> Select:
    """`members` — the struct's member names in order; `path_text` joined once."""
    psq = qt.path_text.alias("psq")
    name = qt.terms.alias("n")
    x = qt.members
    return select(psq.c["text"], name.c["text"], x.c["ord"]).select_from(
        x.join(psq, psq.c["path_id"] == x.c["struct_qname_pid"]).join(
            name, name.c["term_id"] == x.c["name_id"]
        )
    )


def v_refs() -> Select:
    """`refs` — which struct references which qualified name; `path_text` joined twice."""
    psq = qt.path_text.alias("psq")
    pr = qt.path_text.alias("pr")
    x = qt.refs
    return select(psq.c["text"], pr.c["text"]).select_from(
        x.join(psq, psq.c["path_id"] == x.c["struct_qname_pid"]).join(
            pr, pr.c["path_id"] == x.c["ref_qname_pid"]
        )
    )


def _pair(x: Table) -> Select:
    """`(src, dst)` text for a `(src_pid, dst_pid)` edge relation; `path_text` joined twice."""
    ps = qt.path_text.alias("ps")
    pd = qt.path_text.alias("pd")
    return select(ps.c["text"], pd.c["text"]).select_from(
        x.join(ps, ps.c["path_id"] == x.c["src_pid"]).join(pd, pd.c["path_id"] == x.c["dst_pid"])
    )


def v_edges() -> Select:
    """`edges` — struct-to-struct edges by qualified name."""
    return _pair(qt.edges)


def v_module_edges() -> Select:
    """`module_edges` — module-to-module edges by path."""
    return _pair(qt.module_edges)


def v_modules() -> Select:
    """`modules` — each module's path, purpose and index flag; `path_text` joined once."""
    pm = qt.path_text.alias("pm")
    purpose = qt.terms.alias("p")
    x = qt.modules
    return select(pm.c["text"], purpose.c["text"], x.c["is_index"]).select_from(
        x.join(pm, pm.c["path_id"] == x.c["module_pid"]).join(
            purpose, purpose.c["term_id"] == x.c["purpose_id"]
        )
    )
