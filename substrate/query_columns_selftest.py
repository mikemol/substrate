#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.query_columns` — the denominator, and the per-unit predicate scope.

⚑⚑⚑ THE PREDICATE-SCOPE ARM IS THE ONE A PLAUSIBLE IMPLEMENTATION FAILS. If `obs.uri` is a
predicate in query A and merely projected in query B, resolving predicate-ness by COLUMN STRING
rather than by NODE ID marks it a predicate in B too — and B then contributes covering-index
candidates it does not justify. Nothing in the output says which query supplied a pair, so the
over-nomination is unattributable and looks like broad, well-corroborated demand.

⚑⚑ THE DROPPED-BUILDER ARM PROTECTS A DENOMINATOR. A builder that interns no column vanishes
from the rows; if it also vanishes from the return value, the report's "N builders" silently
becomes "N builders that parsed". An incomplete census is not a low count.

⚑ AND THE EMPTY-`op` ARM BLOCKS A PHANTOM TABLE. An unbound Column node admitted as a column
named "" groups under table "" — collecting columns from unrelated queries into one contour.

⚑ THE FIXTURES ARE PLAIN DATACLASSES, NOT SUBCLASSES of the adapter's Protocols, and that is
deliberate: structural conformance is what the adapter actually requires of the real corpus,
which likewise does not inherit from anything here. A nominal fixture would prove the adapter
works on a type only this file can produce.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from substrate import query_columns as qc


@dataclass(frozen=True, slots=True)
class _N:
    """A stand-in intern node."""

    kind: str
    op: str


@dataclass(frozen=True, slots=True)
class _U:
    """A stand-in interned unit."""

    name: str
    support: tuple[int, ...]


# Node ids 1 and 2 are both `obs.uri`; 1 is a predicate node, 2 is a projection node. That
# duplication is the whole point — the same column string interned under two ids.
_NODES: dict[int, _N] = {
    1: _N("Column", "obs.uri"),
    2: _N("Column", "obs.uri"),
    3: _N("Column", "obs.kind"),
    4: _N("Compare", ""),
    5: _N("Column", ""),  # an unbound Column — no relation resolved
    6: _N("Literal", "7"),
}

_PREDICATE_IDS = frozenset({1})

_A = _U("q_pred", (1, 3))  # uses obs.uri AS A PREDICATE
_B = _U("q_proj", (2, 3))  # uses the SAME COLUMN, projected only
_EMPTY = _U("q_count", (4, 6))  # interns no column at all
_UNBOUND = _U("q_unbound", (5,))  # only an unbound Column


def a_predicate_in_one_query_is_not_one_in_another(out: list[str]) -> int:
    """Check predicate-ness is resolved per NODE ID, not per column string.

    ⚑ THE DISCRIMINATOR OF THIS WHOLE MODULE. Both units mention `obs.uri`; only the first
    supplies a predicate node id. A string-keyed implementation returns `obs.uri` as a predicate
    in both and every arm but this one still passes.
    """
    a = qc.unit_columns(_A, _NODES, _PREDICATE_IDS)
    b = qc.unit_columns(_B, _NODES, _PREDICATE_IDS)
    if a.predicate != frozenset({"obs.uri"}):
        out.append(f"selftest: the predicate query read predicates {sorted(a.predicate)}")
        return 1
    if b.predicate:
        out.append(
            f"selftest: a projection-only query claimed predicates "
            f"{sorted(b.predicate)} — predicate-ness leaked across queries"
        )
        return 1
    return 0


def the_predicate_set_is_a_subset_of_the_columns(out: list[str]) -> int:
    """Check a predicate column is also reported as touched."""
    a = qc.unit_columns(_A, _NODES, _PREDICATE_IDS)
    if not a.predicate <= a.columns:
        out.append("selftest: a predicate column is not among the columns touched")
        return 1
    return 0


def an_unbound_column_is_not_a_column(out: list[str]) -> int:
    """Check a Column node with an empty op yields no column — no phantom table.

    ⚑ ADMITTING IT WOULD NOT ERROR. It would create a table named "" whose contours pool columns
    from every query with an unbound node, and those contours would look like genuine co-usage.
    """
    got = qc.unit_columns(_UNBOUND, _NODES, _PREDICATE_IDS)
    if got.columns:
        out.append(f"selftest: an unbound Column produced {sorted(got.columns)}")
        return 1
    return 0


def a_non_column_node_is_ignored(out: list[str]) -> int:
    """Check Compare and Literal nodes contribute nothing."""
    got = qc.unit_columns(_EMPTY, _NODES, _PREDICATE_IDS)
    if got.columns or got.predicate:
        out.append("selftest: a non-Column node contributed a column")
        return 1
    return 0


def a_dropped_builder_is_named_not_silent(out: list[str]) -> int:
    """Check a column-less builder is reported rather than merely absent.

    ⚑ THE FAILURE IS A SHRINKING DENOMINATOR. Without the second return value the report counts
    only what parsed and calls it the workload.
    """
    rows, empty = qc.read_corpus((_A, _EMPTY, _B, _UNBOUND), _NODES, _PREDICATE_IDS)
    if [r.name for r in rows] != ["q_pred", "q_proj"]:
        out.append(f"selftest: rows read as {[r.name for r in rows]}")
        return 1
    if set(empty) != {"q_count", "q_unbound"}:
        out.append(
            f"selftest: dropped builders read as {sorted(empty)}, "
            "want both the column-less and the unbound one"
        )
        return 1
    return 0


def an_unknown_node_id_does_not_raise(out: list[str]) -> int:
    """Check a support id absent from the node table is skipped, not fatal.

    A corpus read against a partially-preloaded intern table is a real shape; aborting the whole
    census on one missing id would turn a partial reading into no reading.
    """
    got = qc.unit_columns(_U("q_gap", (1, 999)), _NODES, _PREDICATE_IDS)
    if got.columns != frozenset({"obs.uri"}):
        out.append(f"selftest: an unknown node id changed the result to {sorted(got.columns)}")
        return 1
    return 0


_ARMS = (
    a_predicate_in_one_query_is_not_one_in_another,
    the_predicate_set_is_a_subset_of_the_columns,
    an_unbound_column_is_not_a_column,
    a_non_column_node_is_ignored,
    a_dropped_builder_is_named_not_silent,
    an_unknown_node_id_does_not_raise,
)

# ⚑ DERIVED FROM `_ARMS`, NEVER TYPED — a hand-kept count is a second roster that drifts.
_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"query-columns selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"query-columns selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
