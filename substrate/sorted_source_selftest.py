#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sorted_source` — where an unordered collection gains a declared order.

⚑⚑⚑ A PRODUCER MUST BE PINNED ON BOTH HALVES OF ITS CLAIM: the rows it emits AND the key it
declares. A `from_set` that sorted correctly but attached the wrong key would pass every ordering
assertion here and then cause a downstream `require` to admit an order that does not hold — the
failure lands one module away from its cause. So each arm below reads back `stream.key` as well
as the rows.

⚑⚑⚑ `already` AND `checked` DIFFER ONLY IN WHAT THEY DO WITH A LIE, so the discriminating case is
a LYING SOURCE. On out-of-order input `already` must stay silent — that is its contract, not a
bug — and `checked` must raise. An arm feeding both of them well-ordered rows cannot tell them
apart at all, which would leave the entire distinction untested.

⚑⚑ AND `checked` IS ASSERTED TO BE LAZY, WHICH IS THE PROPERTY MOST EASILY LOST. It exists to
verify in O(1) state WITHOUT materializing; an implementation that collected the rows and sorted
them to compare would return every correct answer above while destroying the reason the carrier
exists. The arm counts rows pulled from a counting source, since only the COST distinguishes them.

⚑⚑ THAT COUNT'S BOUND IS COMPUTED, NOT GUESSED, and `_LAZY_PULL_CEILING` below carries the
derivation. A bound picked to make the case pass measures nothing; one derived from the algorithm
fails the moment an implementation starts buffering.

⚑⚑ CELLS ARE `_Text`, NEVER BARE `str`. `Cell.__lt__` takes `object` while `str.__lt__` takes only
`str`, so a `str` is a cell to RECEIVE and not one to PASS IN; `substrate/sort_key_selftest.py`
records the drafts that established it.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate.sort_key import OrderError, SortKey
from substrate.sorted_source import already, checked, from_dict, from_set

if TYPE_CHECKING:
    from collections.abc import Iterator

# ⚑ THE CEILING IS DERIVED FROM THE ALGORITHM: delivering the first row costs exactly one pull,
# and a lazy verifier compares that row against a predecessor it does not yet have. One spare pull
# absorbs an implementation that primes; anything beyond that is buffering, which is the defect.
_LAZY_PULL_CEILING = 2

# ⚑ BIG ENOUGH THAT DRAINING IS VISIBLE. A two-row source cannot discriminate — a lazy verifier
# and a fully eager one both pull every row, so the case would pass on a materializing rewrite.
_COUNTED_SOURCE_ROWS = 500


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


def _values(rows: list[dict[str, _Text]]) -> list[str]:
    """Return the ordered field values of `rows`, which is what an ordering case asserts."""
    return [row["k"].value for row in rows]


def from_set_pays_the_sort_once_at_a_named_producer(out: list[str]) -> int:
    """Check an unordered input becomes ordered rows carrying the key that was asked for."""
    key = SortKey.of("k")
    stream = from_set(_rows("c", "a", "b"), key, origin="t")
    if stream.key != key:
        out.append(f"selftest: from_set declared [{stream.key}] rather than [{key}]")
        return 1
    got = _values(list(stream))
    if got != ["a", "b", "c"]:
        out.append(f"selftest: from_set produced {got!r}")
        return 1
    return 0


def from_set_orders_descending_without_negating(out: list[str]) -> int:
    """Check a DESC field reverses TEXT cells — the arm arithmetic negation cannot pass."""
    stream = from_set(_rows("a", "c", "b"), SortKey((("k", True),)), origin="t")
    got = _values(list(stream))
    if got != ["c", "b", "a"]:
        out.append(f"selftest: a descending producer emitted {got!r}")
        return 1
    return 0


def from_dict_streams_pairs_ordered_over_the_pair(out: list[str]) -> int:
    """Check a mapping becomes `(key, value)` rows whose fields resolve POSITIONALLY."""
    stream = from_dict({_Text("z"): 1, _Text("a"): 2}, SortKey.of("0"), origin="t")
    got = [(pair[0].value, pair[1]) for pair in stream]
    if got != [("a", 2), ("z", 1)]:
        out.append(f"selftest: from_dict produced {got!r}")
        return 1
    return 0


def already_adopts_a_source_without_touching_it(out: list[str]) -> int:
    """Check adoption is transparent for a source that is genuinely ordered."""
    key = SortKey.of("k")
    stream = already(_rows("a", "b"), key, "t")
    if stream.key != key or stream.origin != "t":
        out.append(f"selftest: already declared [{stream.key}] from {stream.origin!r}")
        return 1
    got = _values(list(stream))
    if got != ["a", "b"]:
        out.append(f"selftest: already altered the rows: {got!r}")
        return 1
    return 0


def already_stays_silent_on_a_lying_source(out: list[str]) -> int:
    """Check `already` does NOT verify — its contract, and half THE DISCRIMINATOR.

    ⚑⚑ THIS SILENCE IS DELIBERATE AND MUST BE PINNED. Verifying here would consume the stream,
    which is the cost the carrier exists to avoid; a future author who "fixed" this into a check
    would silently make every adoption eager, and only this arm would notice.
    """
    got = _values(list(already(_rows("b", "a"), SortKey.of("k"), "liar")))
    if got != ["b", "a"]:
        out.append(f"selftest: already reordered or refused a lying source: {got!r}")
        return 1
    return 0


def checked_refuses_the_first_out_of_order_pair(out: list[str]) -> int:
    """Check `checked` raises where `already` stayed silent — the other half of the pair.

    ⚑⚑ THE MESSAGE MUST CARRY THE ORIGIN AND THE ROW INDEX. The violation surfaces mid-iteration,
    possibly far from the call that adopted the source, so a refusal without both leaves the
    operator knowing only that some producer somewhere lied.
    """
    try:
        list(checked(_rows("b", "a"), SortKey.of("k"), "liar"))
    except OrderError as refusal:
        if "breaks it" not in str(refusal):
            out.append(f"selftest: checked refused for another reason: {refusal}")
            return 1
        if "liar" not in str(refusal):
            out.append(f"selftest: the refusal did not name the origin: {refusal}")
            return 1
        if "row 1" not in str(refusal):
            out.append(f"selftest: the refusal did not name the position: {refusal}")
            return 1
        return 0
    out.append("selftest: checked accepted an out-of-order source")
    return 1


def checked_passes_an_honest_source_through(out: list[str]) -> int:
    """Check the positive half, so the refusal arm cannot be met by refusing everything."""
    got = _values(list(checked(_rows("a", "b", "c"), SortKey.of("k"), "t")))
    if got != ["a", "b", "c"]:
        out.append(f"selftest: checked altered an honest source: {got!r}")
        return 1
    return 0


def checked_verifies_lazily_rather_than_materializing(out: list[str]) -> int:
    """Check verification costs O(1) state and does NOT drain the source — THE DISCRIMINATOR.

    ⚑⚑ AN EAGER IMPLEMENTATION RETURNS EVERY CORRECT ANSWER ABOVE. Collecting the rows and
    sorting them to compare would satisfy both the acceptance and the refusal arms while
    destroying the property the whole carrier exists for; only the COST separates them.
    """
    pulled: list[str] = []

    def counted() -> Iterator[dict[str, _Text]]:
        """Yield many ordered rows, recording each one that is actually consumed."""
        for index in range(_COUNTED_SOURCE_ROWS):
            pulled.append("row")
            yield {"k": _Text(f"k{index:03d}")}

    stream = checked(counted(), SortKey.of("k"), "big")
    first = next(iter(stream))
    if first["k"].value != "k000":
        out.append(f"selftest: the first checked row is {first['k'].value!r}")
        return 1
    if len(pulled) > _LAZY_PULL_CEILING:
        out.append(f"selftest: checked drained the source; pulled {len(pulled)}")
        return 1
    return 0


_ARMS = (
    from_set_pays_the_sort_once_at_a_named_producer,
    from_set_orders_descending_without_negating,
    from_dict_streams_pairs_ordered_over_the_pair,
    already_adopts_a_source_without_touching_it,
    already_stays_silent_on_a_lying_source,
    checked_refuses_the_first_out_of_order_pair,
    checked_passes_an_honest_source_through,
    checked_verifies_lazily_rather_than_materializing,
)

_CASE_COUNT = 2 + 1 + 1 + 3 + 1 + 4 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sorted-source selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sorted-source selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
