#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read an interned query corpus into `QueryColumns` — the adapter, and only the adapter.

The interned corpus holds one Unit per query builder, each with a support set of node ids over a
shared intern table. A `Column` node carries `table.column` in its `op`; the predicate subset is
whichever of those ids appear as a child of a `Compare` (a join onclause or a filter). This turns
that into the flat triples `substrate.column_contours` consumes.

⚑⚑⚑ A QUERY THAT TOUCHES NO COLUMN IS DROPPED, AND THAT IS A COVERAGE FACT, NOT A NO-OP. It
means the builder interned without any resolvable `Column` node — a `SELECT count(*)`, or a
lowering that failed to bind. Either way the census's DENOMINATOR shrinks silently: the report
says "N builders" where N is the number that produced columns, not the number that exist. So
`read_corpus` returns the dropped names ALONGSIDE the rows rather than filtering them away. An
incomplete census is not a low count, and the only way to tell them apart is to name what fell out.

⚑⚑ THE PREDICATE SET IS AN INTERSECTION OVER NODE IDS, NOT OVER COLUMN STRINGS. The same column
string interns to several ids across queries; asking "is this COLUMN a predicate" globally would
mark it a predicate in every query once it is a predicate in any. The membership test is taken
per-unit, over the id, before the id is resolved to its string.

⚑ THE CORPUS SHAPE IS A PROTOCOL, NOT AN IMPORT. The interning layer lives in a module carrying
hundreds of findings, and this repo's per-file gate stages a new module's transitive imports —
so importing it by package path refuses a file that is itself clean. Structural typing states
exactly what this adapter reads (a kind, an op, a name, a support) and nothing else, which is
also the honest description: the adapter does not need the corpus, only those four attributes.

⚑ EXTRACTED FROM `scripts/query_topo.py` (⟡drain-query-topo).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from substrate.column_contours import QueryColumns

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

# The node kind whose `op` carries a `table.column` key.
COLUMN_KIND = "Column"


class Node(Protocol):
    """The node shape this adapter reads: a kind, and an op that may be empty."""

    @property
    def kind(self) -> str:
        """The node's kind — `Column` for the ones this adapter collects."""

    @property
    def op(self) -> str:
        """The `table.column` key, or empty when the lowering bound no relation."""


class Unit(Protocol):
    """The unit shape this adapter reads: a name, and the node ids it spans."""

    @property
    def name(self) -> str:
        """The query builder's name."""

    @property
    def support(self) -> Iterable[int]:
        """The intern node ids this query spans."""


def unit_columns(
    unit: Unit, nodes: Mapping[int, Node], predicate_ids: frozenset[int]
) -> QueryColumns:
    """Return one query's column usage.

    ⚑ AN EMPTY `op` IS SKIPPED, not recorded as a column named "". A Column node without an op
    is one the lowering could not bind to a relation, and admitting it would create a phantom
    table (everything before the first dot of "" is ""), collecting unrelated columns into one
    contour group.
    """
    columns: set[str] = set()
    predicate: set[str] = set()
    for nid in unit.support:
        n = nodes.get(nid)
        if n is None or n.kind != COLUMN_KIND or not n.op:
            continue
        columns.add(n.op)
        if nid in predicate_ids:
            predicate.add(n.op)
    return QueryColumns(unit.name, frozenset(columns), frozenset(predicate))


def read_corpus(
    units: Iterable[Unit],
    nodes: Mapping[int, Node],
    predicate_ids: frozenset[int],
) -> tuple[list[QueryColumns], tuple[str, ...]]:
    """Return `(rows, names_with_no_columns)` for every unit in the corpus.

    ⚑ THE SECOND ELEMENT IS THE COVERAGE RESIDUE and it must reach the report. A builder that
    contributed no column still exists; counting only the first element makes the denominator a
    fact about what parsed rather than about the workload.
    """
    rows: list[QueryColumns] = []
    empty: list[str] = []
    for u in units:
        qc = unit_columns(u, nodes, predicate_ids)
        if qc.columns:
            rows.append(qc)
        else:
            empty.append(qc.name)
    return rows, tuple(empty)
