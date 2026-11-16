#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sorted_combinator` — the nodes that refuse, and what their refusals say.

⚑⚑⚑ EVERY ALGORITHM HERE IS SILENTLY WRONG ON UNORDERED INPUT RATHER THAN BROKEN, so each one is
pinned by a POSITIVE arm and a REFUSAL arm together. Neither alone is enough: an implementation
that dropped `require` passes every positive arm while returning plausible garbage, and one that
refused unconditionally passes every refusal arm while being useless. The pair is the case.

⚑⚑⚑ AND EACH REFUSAL IS CHECKED FOR THE PRODUCER IT NAMES, NOT MERELY FOR RAISING. The refusal's
job is to send an operator UPSTREAM to the producer that must sort differently; a message naming
only the combinator sends them to the one place that is already correct. `join`'s two-sided arm is
the sharpest form — with two candidate producers, a refusal that does not say WHICH is barely
better than none, so that arm refuses on each side in turn and reads the name back.

⚑⚑ `merge` REQUIRES EQUALITY WHERE THE OTHERS REQUIRE PREFIX-CONTAINMENT, and the arms pin the
difference. Elsewhere a consumer asks LESS of a stream than it offers, so a prefix is enough; in
`merge` the inputs are peers compared to EACH OTHER, and two streams ordered by different prefixes
have no common comparison at all.

⚑⚑ `group`'s NON-PREFIX ARM IS THE ONE THE WHOLE `SortKey`-AS-A-LIST DESIGN EXISTS FOR. A boolean
`is_sorted` cannot tell "sorted by (k, v), grouping by k" (legal, runs are contiguous) from
"grouping by v" (illegal, runs are scattered) — so it would have to admit the second and emit one
group per interruption. Silently.

⚑⚑ AND THE END-TO-END ARM MEASURES COST, WHICH NO CORRECTNESS ASSERTION CAN SEE. A fully eager
chain returns the same two rows; only the pulls separate them, which is why its sources are large
and its ceiling is derived from the algorithm rather than fitted to the observation.

⚑⚑ CELLS ARE `_Text`, NEVER BARE `str`. `Cell.__lt__` takes `object` while `str.__lt__` takes only
`str`; `substrate/sort_key_selftest.py` records the drafts that established it.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate.sort_key import UNORDERED, OrderError, SortKey
from substrate.sorted_combinator import dedup, group, join, merge
from substrate.sorted_source import already
from substrate.sorted_transparent import limit

if TYPE_CHECKING:
    from collections.abc import Iterator

    from substrate.sorted_carrier import Sorted

# ⚑ DERIVED, NOT FITTED: `merge` primes one row per source (2); each emitted row costs at most one
# further pull per side, and `dedup` looks one past the run it closes. Against two 500-row sources
# a draining chain pulls 1000, so this ceiling sits far below eager and above the honest floor.
_LAZY_PULL_CEILING = 8
_COUNTED_SOURCE_ROWS = 500
_TAKEN = 2
_CROSS_PRODUCT_PAIRS = 4
_DISTINCT_GROUPS = 2


@dataclass(frozen=True, slots=True, order=False)
class _Text:
    """A text cell whose `__lt__` accepts `object` — what the `Cell` protocol actually requires."""

    value: str

    def __lt__(self, other: object, /) -> bool:
        """Report whether this cell sorts before `other`."""
        if not isinstance(other, _Text):
            return NotImplemented
        return self.value < other.value


def _rows(*values: str) -> list[dict[str, _Text]]:
    """Return single-field mapping rows, the shape the default field resolver reads first."""
    return [{"k": _Text(v)} for v in values]


def _pairs(*values: tuple[str, str]) -> list[dict[str, _Text]]:
    """Return two-field mapping rows, for the cases where a secondary field breaks ties."""
    return [{"k": _Text(k), "v": _Text(v)} for k, v in values]


def _values(rows: list[dict[str, _Text]]) -> list[str]:
    """Return the leading field values of `rows`, which is what an ordering case asserts."""
    return [row["k"].value for row in rows]


def _empty(key: SortKey, origin: str) -> Sorted[dict[str, _Text]]:
    """Return an empty stream declaring `key`, for a refusal arm that never reaches a row."""
    return already([], key, origin)


def merge_interleaves_streams_sharing_one_order(out: list[str]) -> int:
    """Check the positive half: rows interleave and the shared key is carried out."""
    key = SortKey.of("k")
    merged = merge(already(_rows("a", "c"), key, "A"), already(_rows("b", "d"), key, "B"))
    if merged.key != key:
        out.append(f"selftest: merge declared [{merged.key}] rather than [{key}]")
        return 1
    got = _values(list(merged))
    if got != ["a", "b", "c", "d"]:
        out.append(f"selftest: merge produced {got!r}")
        return 1
    return 0


def merge_refuses_inputs_in_different_orders_and_names_the_odd_one(out: list[str]) -> int:
    """Check peers must agree EXACTLY, and that the divergent producer is the one named."""
    try:
        merge(
            already(_rows("a"), SortKey.of("k"), "prod-A"),
            already(_pairs(("a", "x")), SortKey.of("k", "v"), "prod-B"),
        )
    except OrderError as refusal:
        if "prod-B" not in str(refusal):
            out.append(f"selftest: the refusal did not name the divergent input: {refusal}")
            return 1
        if "ONE order" not in str(refusal):
            out.append(f"selftest: merge refused for another reason: {refusal}")
            return 1
        return 0
    out.append("selftest: merge accepted inputs in two different orders")
    return 1


def merge_refuses_an_unordered_input_and_no_streams_at_all(out: list[str]) -> int:
    """Check the two degenerate inputs are refusals rather than empty successes."""
    try:
        merge(_empty(UNORDERED, "prod-U"))
    except OrderError as refusal:
        if "declares no order" not in str(refusal) or "prod-U" not in str(refusal):
            out.append(f"selftest: the unordered input refused oddly: {refusal}")
            return 1
    else:
        out.append("selftest: merge accepted an unordered input")
        return 1
    try:
        merge(origin="empty")
    except OrderError:
        return 0
    out.append("selftest: merge accepted no streams at all")
    return 1


def dedup_collapses_adjacent_duplicates(out: list[str]) -> int:
    """Check the positive half over the stream's full declared key."""
    key = SortKey.of("k")
    collapsed = dedup(already(_rows("a", "a", "b", "b", "b", "c"), key, "src"))
    if collapsed.key != key:
        out.append(f"selftest: dedup declared [{collapsed.key}] rather than [{key}]")
        return 1
    got = _values(list(collapsed))
    if got != ["a", "b", "c"]:
        out.append(f"selftest: dedup produced {got!r}")
        return 1
    return 0


def dedup_on_a_prefix_keeps_the_first_row_of_each_group(out: list[str]) -> int:
    """Check a PREFIX is admissible and selects the run leader, not an arbitrary member."""
    rows = _pairs(("a", "1"), ("a", "2"), ("b", "3"))
    collapsed = dedup(already(rows, SortKey.of("k", "v"), "src"), on=SortKey.of("k"))
    got = [(row["k"].value, row["v"].value) for row in collapsed]
    if got != [("a", "1"), ("b", "3")]:
        out.append(f"selftest: the prefix dedup produced {got!r}")
        return 1
    return 0


def dedup_refuses_a_non_prefix_and_names_the_producer(out: list[str]) -> int:
    """Check the refusal half, and that it sends the reader to the producer that must change."""
    try:
        list(dedup(_empty(SortKey.of("k", "v"), "prod-D"), on=SortKey.of("v")))
    except OrderError as refusal:
        if "does not cover" not in str(refusal):
            out.append(f"selftest: dedup refused for another reason: {refusal}")
            return 1
        if "push the constraint to 'prod-D'" not in str(refusal):
            out.append(f"selftest: the refusal did not send the reader upstream: {refusal}")
            return 1
        return 0
    out.append("selftest: dedup accepted a non-prefix key")
    return 1


def group_cuts_adjacent_runs_when_the_key_is_a_prefix(out: list[str]) -> int:
    """Check the positive half: contiguous runs, each with its key and its rows."""
    rows = _pairs(("x", "1"), ("x", "2"), ("y", "3"))
    grouped = list(group(already(rows, SortKey.of("k", "v"), "src"), SortKey.of("k")))
    sizes = [len(members) for _run_key, members in grouped]
    if sizes != [2, 1]:
        out.append(f"selftest: the run sizes are {sizes!r}")
        return 1
    leaders = [members[0]["k"].value for _run_key, members in grouped]
    if leaders != ["x", "y"]:
        out.append(f"selftest: the run leaders are {leaders!r}")
        return 1
    return 0


def group_declares_an_output_key_over_its_new_row_shape(out: list[str]) -> int:
    """Check a grouped stream is composable — the reason the key is respelled positionally.

    ⚑⚑ WITHOUT THE RESPELLING A GROUPED STREAM IS A DEAD END. Its rows are pairs, so a key naming
    the ORIGINAL fields would resolve against a shape that no longer exists; the `0.` prefix says
    the order now lives in the leading element, and lets `dedup` or `merge` consume the result.
    """
    grouped = group(already(_rows("x", "y"), SortKey.of("k"), "src"), SortKey.of("k"))
    if grouped.key.names != ("0.k",):
        out.append(f"selftest: a grouped stream declared {grouped.key.names!r}")
        return 1
    collapsed = list(dedup(grouped))
    if len(collapsed) != _DISTINCT_GROUPS:
        out.append(f"selftest: a grouped stream did not compose into dedup: {len(collapsed)}")
        return 1
    return 0


def group_refuses_a_non_prefix_and_names_the_producer(out: list[str]) -> int:
    """Check THE DISCRIMINATOR the list-valued key exists for.

    ⚑⚑ A BOOLEAN `is_sorted` CANNOT REFUSE THIS. Sorted by `k` says nothing about the order of
    `v`, so a run-based grouping on `v` emits one group per interruption — plausible output,
    silently wrong. Only prefix-containment separates it from the legal case above.
    """
    try:
        list(group(_empty(SortKey.of("k"), "prod-G"), SortKey.of("v")))
    except OrderError as refusal:
        if "does not cover" not in str(refusal):
            out.append(f"selftest: group refused for another reason: {refusal}")
            return 1
        if "push the constraint to 'prod-G'" not in str(refusal):
            out.append(f"selftest: the refusal did not send the reader upstream: {refusal}")
            return 1
        return 0
    out.append("selftest: group accepted a non-prefix key")
    return 1


def group_refuses_an_unordered_stream(out: list[str]) -> int:
    """Check a producer that promised nothing is refused, and is named."""
    try:
        list(group(_empty(UNORDERED, "prod-U"), SortKey.of("k")))
    except OrderError as refusal:
        if "declares no order" not in str(refusal) or "prod-U" not in str(refusal):
            out.append(f"selftest: the unordered group refused oddly: {refusal}")
            return 1
        return 0
    out.append("selftest: group accepted an unordered stream")
    return 1


def join_matches_runs_in_one_pass(out: list[str]) -> int:
    """Check the positive half over two ordered sides."""
    left = already(_pairs(("k", "L1"), ("m", "L2")), SortKey.of("k"), "L")
    right = already(_pairs(("k", "R1"), ("m", "R2")), SortKey.of("k"), "R")
    got = [(lrow["v"].value, rrow["v"].value) for lrow, rrow in join(left, right, SortKey.of("k"))]
    if got != [("L1", "R1"), ("L2", "R2")]:
        out.append(f"selftest: join produced {got!r}")
        return 1
    return 0


def join_yields_the_cross_product_within_a_matching_run(out: list[str]) -> int:
    """Check a run against a run is every pair, as SQL gives — not a positional zip."""
    left = already(_pairs(("k", "L1"), ("k", "L2")), SortKey.of("k"), "L")
    right = already(_pairs(("k", "R1"), ("k", "R2")), SortKey.of("k"), "R")
    got = list(join(left, right, SortKey.of("k")))
    if len(got) != _CROSS_PRODUCT_PAIRS:
        out.append(f"selftest: a 2x2 run produced {len(got)} pair(s), not a cross-product")
        return 1
    return 0


def join_advances_past_non_matching_runs_on_both_sides(out: list[str]) -> int:
    """Check each cursor can advance alone, so neither side stalls the other."""
    left = already(_pairs(("a", "L"), ("c", "L")), SortKey.of("k"), "L")
    right = already(_pairs(("b", "R"), ("d", "R")), SortKey.of("k"), "R")
    if list(join(left, right, SortKey.of("k"))):
        out.append("selftest: fully disjoint sides produced pairs")
        return 1
    inner = already(_pairs(("a", "L"), ("b", "L"), ("c", "L")), SortKey.of("k"), "L2")
    outer = already(_pairs(("b", "R")), SortKey.of("k"), "R2")
    got = [lrow["k"].value for lrow, _rrow in join(inner, outer, SortKey.of("k"))]
    if got != ["b"]:
        out.append(f"selftest: the interleaved join matched {got!r}")
        return 1
    return 0


def join_refuses_on_either_side_and_says_which(out: list[str]) -> int:
    """Check THE DISCRIMINATOR for the two-producer case.

    ⚑⚑ WITH TWO CANDIDATE PRODUCERS A REFUSAL THAT DOES NOT NAME ONE IS BARELY BETTER THAN NONE.
    Each side is refused in turn here, and each refusal must name the side that actually failed —
    a message naming both, or neither, leaves the operator guessing which to re-sort.
    """
    try:
        join(_empty(SortKey.of("k"), "prod-L"), _empty(SortKey.of("v"), "prod-R"), SortKey.of("k"))
    except OrderError as refusal:
        if "prod-R" not in str(refusal):
            out.append(f"selftest: the right-side refusal named the wrong producer: {refusal}")
            return 1
    else:
        out.append("selftest: join accepted an unsorted right side")
        return 1
    try:
        join(
            _empty(SortKey.of("v"), "prod-L2"), _empty(SortKey.of("k"), "prod-R2"), SortKey.of("k")
        )
    except OrderError as refusal:
        if "prod-L2" not in str(refusal):
            out.append(f"selftest: the left-side refusal named the wrong producer: {refusal}")
            return 1
        return 0
    out.append("selftest: join accepted an unsorted left side")
    return 1


def a_merge_dedup_limit_chain_stays_lazy_end_to_end(out: list[str]) -> int:
    """Check the composed chain does bounded upstream work — the cost arm for this module.

    ⚑⚑ EVERY OTHER ARM HERE PASSES ON A FULLY EAGER IMPLEMENTATION. The chain returns the same
    two rows whether it pulls six upstream rows or a thousand; only the count distinguishes them,
    which is why the sources are large enough for the difference to be visible.
    """
    pulled: list[str] = []

    def counted(tag: str) -> Iterator[dict[str, _Text]]:
        """Yield many ordered rows, recording each one that is actually consumed."""
        for index in range(_COUNTED_SOURCE_ROWS):
            pulled.append(tag)
            yield {"k": _Text(f"k{index:03d}")}

    key = SortKey.of("k")
    chain = limit(
        dedup(merge(already(counted("a"), key, "A"), already(counted("b"), key, "B")), on=key),
        _TAKEN,
    )
    got = _values(list(chain))
    if got != ["k000", "k001"]:
        out.append(f"selftest: the chain produced {got!r}")
        return 1
    if len(pulled) > _LAZY_PULL_CEILING:
        out.append(f"selftest: the chain drained its sources; pulled {len(pulled)}")
        return 1
    return 0


_ARMS = (
    merge_interleaves_streams_sharing_one_order,
    merge_refuses_inputs_in_different_orders_and_names_the_odd_one,
    merge_refuses_an_unordered_input_and_no_streams_at_all,
    dedup_collapses_adjacent_duplicates,
    dedup_on_a_prefix_keeps_the_first_row_of_each_group,
    dedup_refuses_a_non_prefix_and_names_the_producer,
    group_cuts_adjacent_runs_when_the_key_is_a_prefix,
    group_declares_an_output_key_over_its_new_row_shape,
    group_refuses_a_non_prefix_and_names_the_producer,
    group_refuses_an_unordered_stream,
    join_matches_runs_in_one_pass,
    join_yields_the_cross_product_within_a_matching_run,
    join_advances_past_non_matching_runs_on_both_sides,
    join_refuses_on_either_side_and_says_which,
    a_merge_dedup_limit_chain_stays_lazy_end_to_end,
)

_CASE_COUNT = 2 + 2 + 2 + 2 + 1 + 2 + 2 + 2 + 2 + 2 + 1 + 1 + 2 + 4 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sorted-combinator selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sorted-combinator selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
