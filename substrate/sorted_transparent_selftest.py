#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sorted_transparent` — the nodes a declared order passes through.

⚑⚑⚑ THE PROPERTY UNDER TEST IS THE OUTPUT KEY, NOT THE OUTPUT ROWS. Every arm here could be
satisfied by a plain generator expression; what makes these functions worth existing is that the
order requirement can WALK THROUGH them to the producer that must satisfy it. A `where` that
returned the right rows under a dropped or altered key would break propagation silently — the
next `require` upstream would compare against an order nobody restated. So each arm reads back
`stream.key` first and the rows second.

⚑⚑⚑ AND `limit`'s REAL SUBJECT IS COST, WHICH NO CORRECTNESS ASSERTION CAN SEE. A fully eager
implementation returns exactly the same three rows; only the number of rows PULLED from the
source separates lazy from eager. That makes the counting arm the discriminator for this whole
module, and it makes the source's SIZE load-bearing — a small source cannot tell the two apart.

⚑⚑ `project` IS PINNED ON THE ARGUMENT IT REFUSES TO INFER. Its output key is required precisely
because a projection may rename or drop the ordered field; the arm below projects to a shape
where the input's key would be a LIE, and checks the declared key is the one carried. An arm that
projected order-preservingly could not distinguish "declared" from "inherited".

⚑⚑ NOTHING HERE HAS A REFUSAL ARM, AND THAT IS THE POINT RATHER THAN AN OMISSION. Every function
in this module is total: none calls `require`, none can raise. The order-requiring half of the
combinator set lives in `substrate/sorted_combinator.py`, where the refusals are the subject.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate.sort_key import SortKey
from substrate.sorted_source import already
from substrate.sorted_transparent import limit, project, where

if TYPE_CHECKING:
    from collections.abc import Iterator

# ⚑ DERIVED, NOT GUESSED: `islice` pulls exactly the rows it yields, so taking three costs three.
# One spare absorbs a generator that reads ahead to notice exhaustion; more than that is eager.
_LIMIT_PULL_CEILING = 4
_TAKEN = 3

# ⚑ BIG ENOUGH THAT DRAINING IS VISIBLE. Against a three-row source a lazy chain and a fully eager
# one pull the same rows, so the case would pass on an implementation that materializes.
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


def where_passes_the_order_through_untouched(out: list[str]) -> int:
    """Check filtering keeps the declared key — THE DISCRIMINATOR for this node.

    ⚑⚑ THE ROWS ARE THE EASY HALF. A generator expression filters correctly and carries no key at
    all; what this node exists to provide is the key a later `require` will walk back through.
    """
    key = SortKey.of("k")
    filtered = where(already(_rows("a", "b", "c"), key, "src"), lambda row: row["k"].value != "b")
    if filtered.key != key:
        out.append(f"selftest: where declared [{filtered.key}] rather than [{key}]")
        return 1
    got = _values(list(filtered))
    if got != ["a", "c"]:
        out.append(f"selftest: where produced {got!r}")
        return 1
    return 0


def where_keeps_a_descending_order_descending(out: list[str]) -> int:
    """Check the direction survives too, not merely the field names."""
    key = SortKey((("k", True),))
    filtered = where(already(_rows("c", "b", "a"), key, "src"), lambda _row: True)
    if filtered.key != key:
        out.append(f"selftest: where lost the direction: [{filtered.key}]")
        return 1
    return 0


def limit_takes_a_prefix_and_keeps_the_order(out: list[str]) -> int:
    """Check the rows and the declared key of a truncated stream."""
    key = SortKey.of("k")
    taken = limit(already(_rows("a", "b", "c", "d"), key, "src"), _TAKEN)
    if taken.key != key:
        out.append(f"selftest: limit declared [{taken.key}] rather than [{key}]")
        return 1
    got = _values(list(taken))
    if got != ["a", "b", "c"]:
        out.append(f"selftest: limit produced {got!r}")
        return 1
    return 0


def limit_keeps_the_upstream_chain_lazy(out: list[str]) -> int:
    """Check the source is NOT drained — the arm no correctness assertion can replace.

    ⚑⚑ AN EAGER IMPLEMENTATION PASSES EVERY OTHER ARM IN THIS FILE. `limit` exists so that a
    bounded consumer costs a bounded amount of upstream work; take that away and the answers are
    all still right while the reason for the whole carrier is gone.
    """
    pulled: list[str] = []

    def counted() -> Iterator[dict[str, _Text]]:
        """Yield many ordered rows, recording each one that is actually consumed."""
        for index in range(_COUNTED_SOURCE_ROWS):
            pulled.append("row")
            yield {"k": _Text(f"k{index:03d}")}

    got = _values(list(limit(already(counted(), SortKey.of("k"), "big"), _TAKEN)))
    if got != ["k000", "k001", "k002"]:
        out.append(f"selftest: the limited chain produced {got!r}")
        return 1
    if len(pulled) > _LIMIT_PULL_CEILING:
        out.append(f"selftest: limit drained the source; pulled {len(pulled)}")
        return 1
    return 0


def project_declares_its_output_key_rather_than_inheriting_one(out: list[str]) -> int:
    """Check the DECLARED key is carried where the input's would be a lie — THE DISCRIMINATOR.

    ⚑⚑ THE PROJECTION BELOW RENAMES THE ORDERED FIELD. An implementation that carried the input's
    key forward would attach `k` to rows that no longer have one, and the false claim would only
    surface at a downstream `require` — one module away from the node that invented it.
    """
    out_key = SortKey.of("renamed")
    projected = project(
        already(_rows("a", "b"), SortKey.of("k"), "src"), lambda row: {"renamed": row["k"]}, out_key
    )
    if projected.key != out_key:
        out.append(f"selftest: project declared [{projected.key}] rather than [{out_key}]")
        return 1
    got = [row["renamed"].value for row in projected]
    if got != ["a", "b"]:
        out.append(f"selftest: project produced {got!r}")
        return 1
    return 0


def project_can_declare_a_stream_unordered(out: list[str]) -> int:
    """Check a projection that DESTROYS the order can say so, which is the honest case."""
    projected = project(
        already(_rows("a", "b"), SortKey.of("k"), "src"), lambda row: row["k"].value, SortKey.of()
    )
    if projected.key:
        out.append(f"selftest: an unordered projection declared [{projected.key}]")
        return 1
    if list(projected) != ["a", "b"]:
        out.append("selftest: the unordered projection altered its rows")
        return 1
    return 0


def project_does_not_carry_the_input_getter_to_a_new_row_shape(out: list[str]) -> int:
    """Check the input's field resolver is DROPPED, since it reads a shape that is now gone.

    ⚑ A GETTER IS BOUND TO A ROW SHAPE. Carrying one across a projection would resolve the output
    key's names against the input's layout, which is a wrong answer rather than an error.
    """

    def by_name(row: dict[str, _Text], name: str) -> _Text:
        """Resolve a field on the INPUT shape — meaningless once the rows are replaced."""
        return row[name]

    projected = project(
        already(_rows("a"), SortKey.of("k"), "src", by_name),
        lambda row: {"renamed": row["k"]},
        SortKey.of("renamed"),
    )
    if projected.getter is not None:
        out.append("selftest: project carried the input's getter onto a new row shape")
        return 1
    return 0


_ARMS = (
    where_passes_the_order_through_untouched,
    where_keeps_a_descending_order_descending,
    limit_takes_a_prefix_and_keeps_the_order,
    limit_keeps_the_upstream_chain_lazy,
    project_declares_its_output_key_rather_than_inheriting_one,
    project_can_declare_a_stream_unordered,
    project_does_not_carry_the_input_getter_to_a_new_row_shape,
)

_CASE_COUNT = 2 + 1 + 2 + 2 + 2 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sorted-transparent selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sorted-transparent selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
