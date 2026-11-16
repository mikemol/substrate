#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Elevation and contours over a query workload's column usage — the index-design unit.

ELEVATION is breadth: how many queries touch a column. CONTOURS are co-usage: which columns
are used TOGETHER, within one table, in one query. Breadth alone tells you which columns
deserve an index; it cannot tell you what a COMPOSITE index should contain, because that
depends on co-occurrence. So the contour, not the peak, is the unit.

⚑⚑⚑ THE NOMINATION IS THE DANGEROUS HALF, AND IT FAILS BY REPORTING TOO MUCH. A gap is a
co-occurring (predicate, projected) pair with NO composite index. If the live-index map arrives
EMPTY — the shape `scripts/query_topo.py` records as measured, an `os.path.exists` on a deleted
catalog returning an empty map — then `has_composite` answers False for every pair and the whole
output becomes a list of gaps that are not gaps. Absent-read-as-finding, in the instrument that
exists to nominate work. The functions here cannot tell an empty map from an unread one, which is
exactly why `nominate` takes the map as an ARGUMENT: the caller that opened the connection is the
only party that can distinguish those, and it must not delegate that to a default.

⚑⚑ A PK PREDICATE IS ALREADY SERVED, so it must not be nominated. On a rowid table a
primary-key predicate is already an index seek, and projecting another column is a cheap
lookup; a hand-made `(pk, other)` covering index changed neither plan nor time when measured.
That measurement was SQLite's and the planner is now postgres's — the reasoning generalises (a
key lookup is an index seek on both) but a covering index is a REAL win on postgres in a way it
was not on sqlite, because index-only scans need the visibility map. So the suppression is kept
and the SUPPRESSED SET IS RETURNED RATHER THAN DROPPED: re-measuring is owed before any contour
this nominates is acted on, and a silently-discarded suppression cannot be re-measured.

⚑ CO-OCCURRENCE IS PER-QUERY, NOT PER-EXECUTION. It weights a rare query the same as a hot one;
frequency weighting needs execution counts the interned corpus does not carry.

⚑ EXTRACTED FROM `scripts/query_topo.py` (⟡drain-query-topo). Everything here is PURE over
`QueryColumns` triples, so the whole nomination path is testable without a store — which is
what the original could not do, since its only entry point opened a connection first.
"""

from __future__ import annotations

import itertools
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping, Sequence

# A column key is `table.column`; the table is the part before the FIRST dot.
_SEP = "."


@dataclass(frozen=True, slots=True)
class QueryColumns:
    """One query's column usage: everything it touches, and the predicate subset.

    ⚑ `predicate` IS A SUBSET OF `columns`, not a disjoint set. A column used in a WHERE
    clause and also projected appears in both — and that overlap is precisely what makes a
    covering index a candidate, so separating them would destroy the signal.
    """

    name: str
    columns: frozenset[str]
    predicate: frozenset[str]


@dataclass(frozen=True, slots=True)
class Elevation:
    """Per-column breadth: queries touching it, and queries using it as a predicate."""

    column: str
    touched: int
    predicated: int


@dataclass(frozen=True, slots=True)
class Contour:
    """A same-table column pair co-occurring in some number of queries."""

    left: str
    right: str
    queries: int


@dataclass(frozen=True, slots=True)
class Gap:
    """A nominated composite/covering index: a predicate column plus a co-used column.

    ⚑ A CANDIDATE, NEVER A VERDICT. Still gated on selectivity and join direction, which live
    in the corpus's role classification rather than here.
    """

    predicate: str
    covered: str
    queries: int


def table_of(column: str) -> str:
    """Return the table part of a `table.column` key.

    ⚑ SPLIT ON THE FIRST DOT, NOT THE LAST. A schema-qualified `public.obs.uri` names table
    `public`… which is wrong, but consistently wrong in the same direction as the grouping —
    whereas splitting on the last dot would group `obs.uri` under `obs` and `public.obs.uri`
    under `public.obs`, silently splitting one table's contours into two. The corpus interns
    unqualified keys; this documents which way an unexpected one degrades.
    """
    return column.split(_SEP, maxsplit=1)[0]


def _leaf(column: str) -> str:
    """Return the bare column name — what the engine's index listing calls it."""
    return column.rsplit(_SEP, maxsplit=1)[-1]


def _elevation_rank(e: Elevation) -> tuple[int, str]:
    """Rank an elevation: most-touched first, then by name so the order is TOTAL.

    ⚑ A PARTIAL ORDER READS AS A WORKLOAD CHANGE. Two columns at equal breadth would swap
    between runs on dict iteration order alone, and a reader diffing two reports would see
    movement that no query caused.
    """
    return (-e.touched, e.column)


def _contour_rank(c: Contour) -> tuple[int, str, str]:
    """Rank a contour: most-frequent first, then by the pair's names."""
    return (-c.queries, c.left, c.right)


def _gap_rank(g: Gap) -> tuple[int, str, str]:
    """Rank a covering candidate: most-frequent first, then by the pair's names."""
    return (-g.queries, g.predicate, g.covered)


def elevations(queries: Iterable[QueryColumns]) -> list[Elevation]:
    """Return every column's breadth, most-touched first."""
    touched: Counter[str] = Counter()
    predicated: Counter[str] = Counter()
    for q in queries:
        touched.update(q.columns)
        predicated.update(q.predicate)
    rows = [Elevation(c, n, predicated.get(c, 0)) for c, n in touched.items()]
    return sorted(rows, key=_elevation_rank)


def _by_table(columns: frozenset[str]) -> dict[str, set[str]]:
    """Group a query's columns by their table."""
    out: dict[str, set[str]] = defaultdict(set)
    for c in columns:
        out[table_of(c)].add(c)
    return out


def contours(queries: Iterable[QueryColumns]) -> list[Contour]:
    """Return same-table column pairs co-occurring in a query, most-frequent first.

    ⚑ PAIRS ARE SORTED WITHIN THEMSELVES, so the two orderings of a pair are one contour rather
    than two half-counted ones. A composite index over both columns is a single object either
    way; a census that counted them separately would halve every contour it found.
    """
    co: Counter[tuple[str, str]] = Counter()
    for q in queries:
        for cols in _by_table(q.columns).values():
            co.update(itertools.combinations(sorted(cols), 2))
    rows = [Contour(a, b, n) for (a, b), n in co.items()]
    return sorted(rows, key=_contour_rank)


def covering_pairs(queries: Iterable[QueryColumns]) -> list[Gap]:
    """Return ORDERED (predicate, co-used) same-table pairs — covering-index candidates.

    ⚑ ORDER MATTERS HERE AND NOT IN `contours`, and conflating the two is the easy error. A
    composite index's usefulness is symmetric in which columns it holds; a COVERING index is
    not — the predicate must lead, or the index cannot be seeked. So this returns both
    orderings of a pair when both columns are predicates, and that is not double counting.
    """
    cover: Counter[tuple[str, str]] = Counter()
    for q in queries:
        for cols in _by_table(q.columns).values():
            for p in q.predicate & cols:
                for other in cols - {p}:
                    cover[(p, other)] += 1
    rows = [Gap(p, o, n) for (p, o), n in cover.items()]
    return sorted(rows, key=_gap_rank)


def has_composite(
    live: Mapping[str, Sequence[tuple[str, str, str]]], left: str, right: str
) -> bool:
    """Report whether a composite index's first two columns are exactly this pair.

    ⚑ FIRST TWO COLUMNS ONLY, AS A SET. An index over three columns serves a predicate on its
    first with the second co-used, and the leading pair is what decides that; comparing as a
    set is right because the engine can seek one and filter the other either way once both are
    in the prefix.
    """
    want = {_leaf(left), _leaf(right)}
    return any({c1, c2} == want for c1, c2, _ in live.get(table_of(left), []))


@dataclass(frozen=True, slots=True)
class Nomination:
    """The split of covering candidates into nominated gaps and suppressed ones.

    ⚑ THE SUPPRESSED SETS ARE CARRIED, NOT DROPPED. A key-predicate contour is suppressed on a
    measurement taken against a different planner (see the module docstring); keeping it
    visible is what makes re-measuring possible instead of merely owed.
    """

    gaps: tuple[Gap, ...]
    key_served: tuple[Gap, ...]
    indexed: tuple[Gap, ...]


def nominate(
    pairs: Iterable[Gap], live: Mapping[str, Sequence[tuple[str, str, str]]], keys: frozenset[str]
) -> Nomination:
    """Partition covering candidates into gaps, key-served, and already-indexed.

    A pair is a GAP when its predicate is not a UNIQUE/PK key and no composite index already
    leads with the pair. Every other pair lands in one of the two suppressed buckets rather
    than vanishing.

    ⚑ EVERY PAIR REACHES EXACTLY ONE BUCKET, and the selftest asserts that. A filter chain that
    drops a pair on two conditions at once reports a smaller population than it examined, and
    the discrepancy is invisible in a ranked list.
    """
    gaps: list[Gap] = []
    key_served: list[Gap] = []
    indexed: list[Gap] = []
    for g in pairs:
        if g.predicate in keys:
            key_served.append(g)
        elif has_composite(live, g.predicate, g.covered):
            indexed.append(g)
        else:
            gaps.append(g)
    return Nomination(tuple(gaps), tuple(key_served), tuple(indexed))
