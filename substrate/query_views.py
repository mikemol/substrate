# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The four decoded FROM elements the builders join, as subqueries (W39c, cut 2b).

⚑⚑ CLEANROOMED FROM `jea/metalanguage/schema_decl.py` (`node_sel`, `unit_sel`, `node_fanin_sel`,
`shared_subtree_sel`, lines 1098-1148) AS `query_decl.py` SUBQUERIES THEM (lines 351-354). Both
origins are behind the per-file gate; this rebuilds the same compositions over `query_tables`'
handles, and `query_views_selftest` compares the compiled SQL with the origin's, statement by
statement.

⚑ THEY ARE SUBQUERIES, NOT VIEWS. ⟡view-purge replaced the stored views with Core selectables so
the SQL is composed where it is used instead of frozen into a stored string; `shared_subtree` is
BUILT from `node_fanin`'s own selectable, so a change to the fanin definition propagates by
construction. The names ("node", "unit", "node_fanin", "shared_subtree") are the aliases every
builder's SQL renders.

⚑ COLUMNS ARE READ BY KEY (`.c["node_id"]`), NOT BY ATTRIBUTE. The typed column collection has
`__getitem__` and no `__getattr__`; the two resolve to the same column object and compile
identically, so the key form is the typed spelling of the same SQL.
"""

from __future__ import annotations

from sqlalchemy import func, select

from substrate import query_tables as qt

# The interned handles a decoded node or unit carries, each aliased once, as in the origin.
kind = qt.terms.alias("k")
role = qt.terms.alias("r")
lit = qt.terms.alias("l")
op = qt.terms.alias("o")
file = qt.terms.alias("f")
unit_kind = qt.terms.alias("ku")
path = qt.path_text.alias("pt")

# The fanin threshold above which a subtree counts as SHARED.
SHARED_FANIN = 2

# A node with its interned handles decoded: kind, role, operator (path or term) and literal.
node_sel = select(
    qt.node.c["node_id"],
    kind.c["text"].label("kind"),
    role.c["text"].label("role"),
    func.coalesce(path.c["text"], op.c["text"]).label("op"),
    lit.c["text"].label("lit"),
).select_from(
    qt.node.join(kind, kind.c["term_id"] == qt.node.c["kind_id"])
    .join(role, role.c["term_id"] == qt.node.c["role_id"])
    .join(lit, lit.c["term_id"] == qt.node.c["lit_id"])
    .outerjoin(op, op.c["term_id"] == qt.node.c["op_term_id"])
    .outerjoin(path, path.c["path_id"] == qt.node.c["op_path_id"])
)

# A unit with its name, file and kind decoded.
unit_sel = select(
    qt.unit.c["unit_id"],
    path.c["text"].label("name"),
    qt.unit.c["root_id"],
    file.c["text"].label("path"),
    unit_kind.c["text"].label("kind"),
    qt.unit.c["copy"],
).select_from(
    qt.unit.join(path, path.c["path_id"] == qt.unit.c["name_pid"])
    .join(file, file.c["term_id"] == qt.unit.c["file_id"])
    .outerjoin(unit_kind, unit_kind.c["term_id"] == qt.unit.c["kind_id"])
)

# How many parents each node has.
node_fanin_sel = select(
    qt.node_child.c["child_id"].label("node_id"), func.count().label("fanin")
).group_by(qt.node_child.c["child_id"])

# The nodes with more than one parent, built FROM `node_fanin`'s own selectable.
fanin = node_fanin_sel.subquery("nf")
shared_subtree_sel = select(fanin.c["node_id"], fanin.c["fanin"]).where(
    fanin.c["fanin"] >= SHARED_FANIN
)

# The FROM elements the builders join, under the names their SQL renders.
node_v = node_sel.subquery("node")
unit_v = unit_sel.subquery("unit")
node_fanin = node_fanin_sel.subquery("node_fanin")
shared_subtree = shared_subtree_sel.subquery("shared_subtree")
