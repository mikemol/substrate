#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The producers: where an unordered collection becomes a stream that DECLARES its order.

⚑⚑⚑ A PRODUCER IS WHERE THE SORT IS PAID, ONCE, BY NAME. Every consumer downstream of one of
these stops re-sorting defensively, because the order arrives as data it can check. That is the
entire trade: `from_set` materializes on purpose so that nothing after it has to.

⚑⚑ AND THE TWO ADOPTION FORMS ARE A DELIBERATE PAIR, NOT A CONVENIENCE AND A SAFE VERSION.
`already` checks NOTHING, because verifying an order means consuming the stream — the exact cost
the carrier exists to avoid, and paying it would make laziness impossible. `checked` opts back in
for a producer nobody trusts, at O(1) extra state, raising on the FIRST out-of-order pair rather
than at the end. Which one a caller reaches for is a claim about the source, and it should be.

⚑⚑ `checked` RAISES MID-STREAM, WHICH IS WHY IT NAMES THE ROW INDEX. A violation is discovered
during iteration, possibly far from the call that adopted the source, so the message carries the
origin AND the position — otherwise the operator learns only that some producer somewhere lied.

⚑ EXTRACTED FROM `jea/metalanguage/sorted_stream.py` (⟡sorted-stream → ⟡typed-carrier, Ⓝ88b).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate.sort_key import Cell, OrderError, SortKey, extractor
from substrate.sorted_carrier import Sorted

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Mapping


def from_set[Row](
    items: Iterable[Row],
    key: SortKey,
    origin: str = "set",
    getter: Callable[[Row, str], Cell] | None = None,
) -> Sorted[Row]:
    """Turn an unordered collection into a stream sorted by `key`.

    ⚑ THIS MATERIALIZES ON PURPOSE. A set has no order to stream, so somebody must pay the sort
    exactly once; paying it HERE, at a named producer, is what lets every consumer stop paying it.
    """
    return Sorted(sorted(items, key=extractor(key, getter)), key, origin, getter)


def from_dict[Key, Value](
    mapping: Mapping[Key, Value],
    key: SortKey,
    origin: str = "dict",
    getter: Callable[[tuple[Key, Value], str], Cell] | None = None,
) -> Sorted[tuple[Key, Value]]:
    """Turn a mapping into a stream of `(key, value)` pairs ordered by `key` over the PAIR.

    ⚑ FIELD NAMES RESOLVE POSITIONALLY over the pair: `"0"` is the mapping key, `"1"` the value.
    """
    return Sorted(sorted(mapping.items(), key=extractor(key, getter)), key, origin, getter)


def already[Row](
    rows: Iterable[Row],
    key: SortKey,
    origin: str,
    getter: Callable[[Row, str], Cell] | None = None,
) -> Sorted[Row]:
    """Adopt a source that is ALREADY ordered — an `ORDER BY` result, an index, a merge output.

    ⚑ NOTHING IS CHECKED, DELIBERATELY. Verifying would consume the stream, which is the cost
    this carrier exists to avoid. `checked` is the opt-in form for a source you do not trust.
    """
    return Sorted(rows, key, origin, getter)


def checked[Row](
    rows: Iterable[Row],
    key: SortKey,
    origin: str,
    getter: Callable[[Row, str], Cell] | None = None,
) -> Sorted[Row]:
    """Adopt an ordered source AND assert the order as it streams, in O(1) extra state.

    ⚑ THE ASSERTION IS LAZY TOO. It compares each row to its predecessor as the row passes, so a
    liar is caught at the first bad pair without the stream ever being materialized.
    """
    compare_by = extractor(key, getter)

    def verified() -> Iterator[Row]:
        """Yield each row, refusing at the first pair that breaks the declared order."""
        previous: tuple[Cell, ...] | None = None
        for index, row in enumerate(rows):
            current = compare_by(row)
            if previous is not None and current < previous:
                msg = (
                    f"{origin}: claimed sorted by [{key}] but row {index} breaks it "
                    f"({current!r} < {previous!r})"
                )
                raise OrderError(msg)
            previous = current
            yield row

    return Sorted(verified(), key, origin, getter)
