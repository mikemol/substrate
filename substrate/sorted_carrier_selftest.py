#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sorted_carrier` — a stream, the order it claims, and who claimed it.

⚑⚑⚑ THE SINGLE-PASS REFUSAL NEEDS A CASE PRECISELY BECAUSE ITS FAILURE MODE IS SILENT. Drop
`__iter__`'s guard and nothing raises: the second consumer receives a spent generator and reads an
EMPTY result, which is a plausible answer. So the arm below does not merely check that a second
pass raises — it checks that the FIRST pass still delivered its rows, because a carrier that
refused everything would also pass a refusal-only assertion.

⚑⚑⚑ AND `require` IS TESTED ON WHAT ITS MESSAGE SAYS, NOT ONLY ON WHETHER IT RAISES. The refusal
exists to send an operator to the PRODUCER that must change; a message naming only the combinator
leaves them at the one place that is already correct. That makes the `origin` substring a
load-bearing assertion rather than a cosmetic one — the arms below read it back.

⚑⚑ THE THREE REFUSAL BRANCHES ARE DISTINCT FAILURES AND ARE PINNED SEPARATELY: an EMPTY request
(the consumer asked for nothing), an UNORDERED stream (the producer promised nothing), and a
NON-COVERING order (the producer promised the wrong thing). Collapsing them into one "does it
raise" arm would let two of the three be deleted undetected.

⚑⚑ A STATE READ AROUND A MUTATION IS COLLECTED AS DATA BEFORE IT IS TESTED, WHICH THE TYPE GATE
ESTABLISHED. Reading `consumed`, mutating, then branching on it again is the shape a narrowing
checker proves constant — it refused the second branch as unreachable. Taking both readings first
and comparing the PAIR states the observation the case is actually making.

⚑⚑ CELLS ARE `_Text`, NEVER BARE `str`, AND THAT IS THE MODULE-FAMILY'S OWN LESSON. `Cell.__lt__`
takes `object` while `str.__lt__` takes only `str`, so a `str` is a fine cell to RECEIVE and not
one to PASS IN; `substrate/sort_key_selftest.py` records the three drafts that established it.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from substrate.sort_key import UNORDERED, OrderError, SortKey
from substrate.sorted_carrier import Sorted


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


def a_fresh_stream_yields_its_rows_once(out: list[str]) -> int:
    """Check the first pass delivers, so the refusal arm cannot be satisfied by refusing always."""
    stream: Sorted[dict[str, _Text]] = Sorted(_rows("a", "b"), SortKey.of("k"), "t")
    got = [row["k"].value for row in stream]
    if got != ["a", "b"]:
        out.append(f"selftest: the first pass produced {got!r}")
        return 1
    return 0


def a_second_consumption_refuses_rather_than_yielding_nothing(out: list[str]) -> int:
    """Check the double-consume RAISES — THE DISCRIMINATOR.

    ⚑⚑ WITHOUT THE GUARD THIS IS NOT AN ERROR BUT AN EMPTY LIST. That is the whole reason the
    check exists: a spent generator's silence looks exactly like a genuine "no rows".
    """
    stream: Sorted[dict[str, _Text]] = Sorted(_rows("a"), SortKey.of("k"), "once")
    list(stream)
    try:
        list(stream)
    except OrderError as refusal:
        if "already consumed" not in str(refusal):
            out.append(f"selftest: the second pass refused for another reason: {refusal}")
            return 1
        if "once" not in str(refusal):
            out.append(f"selftest: the refusal did not name the origin: {refusal}")
            return 1
        return 0
    out.append("selftest: a second consumption yielded silently instead of refusing")
    return 1


def consumed_reports_the_single_pass_state(out: list[str]) -> int:
    """Check the state is readable before the refusal, so a caller can avoid triggering it.

    ⚑ BOTH READINGS ARE TAKEN BEFORE EITHER IS TESTED. A property read twice around a mutation is
    the shape a narrowing checker proves constant, so the observation must be collected as data.
    """
    stream: Sorted[dict[str, _Text]] = Sorted(_rows("a"), SortKey.of("k"), "r")
    before = stream.consumed
    list(stream)
    after = stream.consumed
    if (before, after) != (False, True):
        out.append(f"selftest: consumed read {before!r} then {after!r} around one pass")
        return 1
    return 0


def repr_shows_the_order_and_whether_the_stream_is_spent(out: list[str]) -> int:
    """Check the debugging surface carries both facts a reader of a refusal needs."""
    stream: Sorted[dict[str, _Text]] = Sorted(_rows("a"), SortKey.of("k"), "shown")
    fresh = repr(stream)
    if "fresh" not in fresh or "shown" not in fresh or "k" not in fresh:
        out.append(f"selftest: a fresh repr is {fresh!r}")
        return 1
    list(stream)
    spent = repr(stream)
    if "consumed" not in spent:
        out.append(f"selftest: a spent repr is {spent!r}")
        return 1
    return 0


def extract_compares_by_the_streams_own_key(out: list[str]) -> int:
    """Check the carrier hands out a comparison built from the order it declares."""
    stream: Sorted[dict[str, _Text]] = Sorted(_rows("a"), SortKey.of("k"), "t")
    if stream.extract()({"k": _Text("a")}) != (_Text("a"),):
        out.append("selftest: extract() did not read the declared field")
        return 1
    unordered: Sorted[dict[str, _Text]] = Sorted(_rows("a"), UNORDERED, "t")
    if unordered.extract()({"k": _Text("a")}) != ():
        out.append("selftest: an unordered stream extracted a non-empty comparison")
        return 1
    return 0


def require_admits_a_prefix_of_the_declared_order(out: list[str]) -> int:
    """Check the positive half, so the refusal arms cannot be met by refusing everything."""
    stream: Sorted[dict[str, _Text]] = Sorted([], SortKey.of("a", "b"), "t")
    for want in (SortKey.of("a"), SortKey.of("a", "b")):
        try:
            stream.require(want, "case")
        except OrderError as refusal:
            out.append(f"selftest: a covered order [{want}] was refused: {refusal}")
            return 1
    return 0


def require_refuses_an_empty_request(out: list[str]) -> int:
    """Check a consumer asking for nothing is refused rather than trivially satisfied."""
    stream: Sorted[dict[str, _Text]] = Sorted([], SortKey.of("a"), "t")
    try:
        stream.require(UNORDERED, "case")
    except OrderError as refusal:
        if "nothing to require" not in str(refusal):
            out.append(f"selftest: the empty request refused for another reason: {refusal}")
            return 1
        return 0
    out.append("selftest: an empty requirement was silently satisfied")
    return 1


def require_refuses_an_unordered_stream_and_names_its_producer(out: list[str]) -> int:
    """Check a producer that promised NOTHING is refused, and is the one named."""
    stream: Sorted[dict[str, _Text]] = Sorted([], UNORDERED, "prod-U")
    try:
        stream.require(SortKey.of("a"), "case")
    except OrderError as refusal:
        if "declares no order" not in str(refusal):
            out.append(f"selftest: the unordered stream refused for another reason: {refusal}")
            return 1
        if "prod-U" not in str(refusal):
            out.append(f"selftest: the refusal did not name the producer: {refusal}")
            return 1
        return 0
    out.append("selftest: an unordered stream satisfied an order requirement")
    return 1


def require_refuses_a_non_covering_order_and_names_its_producer(out: list[str]) -> int:
    """Check a producer that promised the WRONG order is refused — THE DISCRIMINATOR.

    ⚑⚑ THIS IS THE ARM A PERMISSIVE `covers` FAILS. A stream sorted by `a` says nothing about the
    order of `b` alone, so a consumer told its `(b,)` requirement is met gets a silently wrong
    grouping instead of an instruction naming the producer it must change.
    """
    stream: Sorted[dict[str, _Text]] = Sorted([], SortKey.of("a", "b"), "prod-N")
    try:
        stream.require(SortKey.of("b"), "case")
    except OrderError as refusal:
        if "does not cover" not in str(refusal):
            out.append(f"selftest: the non-prefix refused for another reason: {refusal}")
            return 1
        if "push the constraint to 'prod-N'" not in str(refusal):
            out.append(f"selftest: the refusal did not send the reader upstream: {refusal}")
            return 1
        return 0
    out.append("selftest: a non-covering order satisfied the requirement")
    return 1


_ARMS = (
    a_fresh_stream_yields_its_rows_once,
    a_second_consumption_refuses_rather_than_yielding_nothing,
    consumed_reports_the_single_pass_state,
    repr_shows_the_order_and_whether_the_stream_is_spent,
    extract_compares_by_the_streams_own_key,
    require_admits_a_prefix_of_the_declared_order,
    require_refuses_an_empty_request,
    require_refuses_an_unordered_stream_and_names_its_producer,
    require_refuses_a_non_covering_order_and_names_its_producer,
)

_CASE_COUNT = 1 + 3 + 2 + 4 + 2 + 2 + 2 + 3 + 3


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sorted-carrier selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sorted-carrier selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
