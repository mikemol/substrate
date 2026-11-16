#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The ORDER-REQUIRING combinators: the nodes that can refuse, and the reason the carrier exists.

⚑⚑⚑ EACH FUNCTION HERE IS AN ALGORITHM THAT IS ONLY CORRECT ON SORTED INPUT, AND EACH ONE SAYS SO
IN CODE RATHER THAN IN PROSE. `dedup` collapses ADJACENT duplicates, `group` cuts ADJACENT runs,
`join` advances two cursors in lockstep — every one of them silently returns a WRONG ANSWER on an
unordered stream instead of failing. That is the failure this whole stack is built against: not a
crash, but a plausible result. `Sorted.require` converts it into a refusal.

⚑⚑⚑ AND THE REFUSAL NAMES THE PRODUCER, BECAUSE THE FIX CANNOT LAND HERE. A consumer cannot repair
an order it did not create — re-sorting at the call site is precisely the defensive cost the
carrier abolishes. So `require` reports `origin` and says "push the constraint to" it: the
requirement travels UPSTREAM to the producer, which is the only place that can satisfy it.

⚑⚑ PREFIX-CONTAINMENT, NOT EQUALITY, IS THE ADMISSION RULE — and it is why `SortKey.fields` is a
LIST and not a boolean. A stream sorted by `(path, line)` groups correctly by `path` and does NOT
group correctly by `line`. A boolean `is_sorted` cannot express that distinction, so it would have
to either reject the legal case or admit the illegal one. `SortKey.covers` decides it.

⚑⚑ `group` AND `join` RESTATE THEIR OUTPUT KEY POSITIONALLY, BECAUSE THEY CHANGE THE ROW SHAPE.
Both emit pairs whose FIRST element carries the order, so the output key is spelled over that
element and the output getter reads it. Without this a grouped stream would be a dead end; with it
a grouped stream is itself a legal input to `merge` or `dedup`, and the chain composes.

⚑ EXTRACTED FROM `jea/metalanguage/sorted_stream.py` (⟡sorted-stream → ⟡typed-carrier, Ⓝ88b). The
transparent nodes that cannot refuse live in `substrate/sorted_transparent.py`; the seam between
the two modules is exactly "does this call `require`".
"""

from __future__ import annotations

import heapq
import itertools
from typing import TYPE_CHECKING

from substrate.sort_key import Cell, OrderError, SortKey, extractor
from substrate.sorted_carrier import Sorted

if TYPE_CHECKING:
    from collections.abc import Iterator


def _pair_key(key: SortKey) -> SortKey:
    """Restate `key` over the FIRST element of an emitted pair.

    ⚑ THE ROW SHAPE CHANGED, SO THE KEY MUST BE RESPELLED. `group` and `join` both emit pairs
    whose leading element carries the order; naming the fields `0.<name>` records that the order
    now lives one level in, so a downstream `covers` check compares like with like.
    """
    return SortKey(tuple((f"0.{name}", descending) for name, descending in key.fields))


def _pair_getter(row: tuple[object, ...], _name: str) -> Cell:
    """Resolve any field of a `group`/`join` output row to its leading, order-carrying element.

    ⚑ THE FIELD NAME IS DELIBERATELY IGNORED, and the underscore says so at the signature. Every
    field of the respelled key is `0.<something>`, so the whole comparison tuple resolves to the
    same leading element; the parameter exists to satisfy the getter protocol, not to select.
    """
    leading = row[0]
    if not isinstance(leading, Cell):
        msg = f"a grouped row's leading element {leading!r} does not compare"
        raise OrderError(msg)
    return leading


def merge[Row](*streams: Sorted[Row], origin: str = "merge") -> Sorted[Row]:
    """Interleave streams that share ONE declared order, carrying that order to the output.

    ⚑⚑ EVERY INPUT MUST DECLARE THE SAME KEY, NOT MERELY A COMPATIBLE ONE. Prefix-containment is
    the right rule for a consumer asking less of a stream than it offers; here the inputs are
    peers being compared to EACH OTHER, and two streams ordered by different prefixes have no
    common comparison. Equality is the honest requirement, and the refusal names the odd one out.

    ⚑ `heapq.merge` IS STDLIB AND DOES THIS. Hand-rolling a heap here would be a second
    implementation of a solved problem with no incumbent in this tree to conform to.
    """
    if not streams:
        msg = "merge: no streams"
        raise OrderError(msg)
    first = streams[0]
    key = first.key
    if not key:
        msg = f"merge: {first.origin!r} declares no order"
        raise OrderError(msg)
    for other in streams[1:]:
        if other.key != key:
            msg = (
                f"merge: {other.origin!r} is sorted by [{other.key}] but {first.origin!r} is "
                f"sorted by [{key}] — merge requires ONE order across inputs"
            )
            raise OrderError(msg)
    rows = heapq.merge(*[iter(stream) for stream in streams], key=first.extract())
    return Sorted(rows, key, origin, first.getter)


def dedup[Row](
    stream: Sorted[Row],
    on: SortKey | None = None,
    origin: str = "dedup",
) -> Sorted[Row]:
    """Collapse ADJACENT rows equal under `on`, keeping the first of each run.

    ⚑⚑ SORTEDNESS IS WHAT MAKES DISTINCT COST O(1) STATE. A general DISTINCT must remember every
    row it has seen; on a sorted stream duplicates are NEIGHBOURS, so one previous key suffices.
    That is the entire payoff of the declared order — and the reason an unordered input must be
    refused rather than tolerated, since here it would silently keep duplicates.

    ⚑ A PREFIX OF THE STREAM'S KEY IS ADMISSIBLE and keeps the first row of each group; `on`
    defaults to the full key, which is exact-duplicate removal.
    """
    want = on if on is not None else stream.key
    stream.require(want, "dedup")
    compare_by = extractor(want, stream.getter)
    key = stream.key

    def collapsed() -> Iterator[Row]:
        """Yield each row whose key differs from its predecessor's."""
        previous: tuple[Cell, ...] | None = None
        for row in stream:
            current = compare_by(row)
            if previous is None or current != previous:
                yield row
            previous = current

    return Sorted(collapsed(), key, origin, stream.getter)


def group[Row](
    stream: Sorted[Row], by: SortKey, origin: str = "group"
) -> Sorted[tuple[tuple[Cell, ...], list[Row]]]:
    """Cut the stream into ADJACENT runs sharing a `by` key, yielding `(keytuple, rows)`.

    ⚑⚑⚑ THIS IS THE CALL THE PREFIX RULE EXISTS FOR. A run-based GROUP BY is correct exactly when
    every row of a group is contiguous, which holds when `by` is a PREFIX of the stream's order
    and fails otherwise — silently, by emitting one group per interruption. The refusal here is
    the requirement that flows furthest upstream, because satisfying it means changing how the
    producer sorted.

    ⚑ EACH GROUP IS MATERIALIZED, the stream of groups is not. The buffer is bounded by the
    largest single run rather than by the relation, which is the honest cost of a run-based group.
    """
    stream.require(by, "group")
    compare_by = extractor(by, stream.getter)

    def runs() -> Iterator[tuple[tuple[Cell, ...], list[Row]]]:
        """Yield each adjacent run as its key and its materialized rows."""
        for run_key, run in itertools.groupby(iter(stream), key=compare_by):
            yield (run_key, list(run))

    return Sorted(runs(), _pair_key(by), origin, _pair_getter)


def join[Left, Right](
    left: Sorted[Left],
    right: Sorted[Right],
    on: SortKey,
    origin: str = "join",
) -> Sorted[tuple[Left, Right]]:
    """Equijoin two ordered streams in ONE pass, yielding every matching `(lrow, rrow)` pair.

    ⚑⚑⚑ THE CONSTRAINT PROPAGATES TO TWO PRODUCERS AT ONCE, which is the case that makes the
    `origin` field indispensable. A hash join needs no order and builds a table; a sort-merge join
    needs no table and instead needs BOTH sides ordered by `on`. When one side is not, the operator
    must be told WHICH — a refusal saying only "join requires sorted input" leaves two candidates
    and no way to choose between them.

    ⚑⚑ EACH SIDE IS REQUIRED SEPARATELY AND IN ORDER, so the message names exactly one producer.
    Checking both and reporting a combined failure would reintroduce the ambiguity.

    ⚑ MATCHING RUNS PRODUCE A FULL CROSS-PRODUCT, as SQL does. The right-hand run is buffered —
    bounded by the largest run, not the relation, which is the honest cost of an equijoin.
    """
    left.require(on, "join(left)")
    right.require(on, "join(right)")
    left_by = extractor(on, left.getter)
    right_by = extractor(on, right.getter)

    def matched() -> Iterator[tuple[Left, Right]]:
        """Advance both cursors in lockstep, emitting the cross-product of each equal run."""
        left_runs = itertools.groupby(iter(left), key=left_by)
        right_runs = itertools.groupby(iter(right), key=right_by)
        left_head = next(left_runs, None)
        right_head = next(right_runs, None)
        while left_head is not None and right_head is not None:
            left_key, left_run = left_head
            right_key, right_run = right_head
            if left_key < right_key:
                left_head = next(left_runs, None)
            elif right_key < left_key:
                right_head = next(right_runs, None)
            else:
                buffered = list(right_run)
                for left_row in left_run:
                    for right_row in buffered:
                        yield (left_row, right_row)
                left_head = next(left_runs, None)
                right_head = next(right_runs, None)

    return Sorted(matched(), _pair_key(on), origin, _pair_getter)
