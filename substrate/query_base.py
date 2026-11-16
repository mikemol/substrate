# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The plain base-table reads, as builders (W39c, family R1 base + reuse_tui + core_fp).

⚑⚑ CLEANROOMED FROM `jea/metalanguage/query_decl.py` (`q_pathtext_all` … `q_meta_failed`,
~3118-3148; `q_node_child_edges` … `q_core_count`, ~3466-3487; `q_core_fp_*`, ~3493-3504).
`query_base_selftest` compares each builder's rendered SQL with the origin's.

⚑ TWO ARE ORDER-SENSITIVE (`q_unit_member`, `q_node_child_edges`): their consumers build ordered
lists from the row order, so the `ORDER BY` is part of the answer, not presentation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import bindparam, func, select

from substrate import query_tables as qt
from substrate import query_views as qv
from substrate.query_ops import eq

if TYPE_CHECKING:
    from sqlalchemy.sql.selectable import Select


def q_pathtext_all() -> Select:
    """Select every interned path with its text."""
    return select(qt.path_text.c["path_id"], qt.path_text.c["text"])


def q_terms_all() -> Select:
    """Select every interned term with its text."""
    return select(qt.terms.c["term_id"], qt.terms.c["text"])


def q_unit_fields() -> Select:
    """Select each unit's identity fields: name, kind, module and root."""
    u = qt.unit.c
    return select(u["unit_id"], u["name_pid"], u["kind_id"], u["module_pid"], u["root_lid"])


def q_unit_cod() -> Select:
    """Select each unit's codomain constructor and qualified name."""
    u = qt.unit_cod.c
    return select(u["unit_id"], u["cod_ctor_id"], u["cod_qname_pid"])


def q_unit_member() -> Select:
    """Select every unit member in unit and member order (ORDER-SENSITIVE)."""
    m = qt.unit_member.c
    return select(m["unit_id"], m["ord"], m["member_name_pid"], m["member_unit_id"]).order_by(
        m["unit_id"], m["ord"]
    )


def q_meta_failed() -> Select:
    """Select the recorded `failed` meta value."""
    return select(qt.meta.c["value"]).where(eq(qt.meta.c["key"], "failed"))


def q_node_child_edges() -> Select:
    """Select every parent/child edge in child order (ORDER-SENSITIVE)."""
    c = qt.node_child.c
    return select(c["node_id"], c["child_id"]).order_by(c["node_id"], c["ord"])


def q_shared_subtree() -> Select:
    """Select the shared subtrees at or above a caller-bound fanin (`min_fanin`)."""
    s = qv.shared_subtree.c
    return select(s["node_id"], s["fanin"]).where(s["fanin"] >= bindparam("min_fanin"))


def q_defcopy_units() -> Select:
    """Select the units that are definition copies."""
    return select(qt.unit.c["unit_id"]).where(eq(qt.unit.c["copy"], "1"))


def q_unit_node_all() -> Select:
    """Select every unit/node membership."""
    return select(qt.unit_node.c["unit_id"], qt.unit_node.c["node_id"])


def q_core_count() -> Select:
    """Count the distinct cores (files) the units come from."""
    return select(func.count(func.distinct(qt.unit.c["file_id"])))


def q_core_fp_ids() -> Select:
    """Select every fingerprinted core."""
    return select(qt.core_fp.c["core_id"])


def q_core_fp_mtimes() -> Select:
    """Select every fingerprinted core with its recorded mtime."""
    return select(qt.core_fp.c["core_id"], qt.core_fp.c["mtime"])


def q_core_fp_mtime() -> Select:
    """Select one core's recorded mtime (`core_id` bound by the caller)."""
    return select(qt.core_fp.c["mtime"]).where(eq(qt.core_fp.c["core_id"], bindparam("core_id")))
