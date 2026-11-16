#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The TRANSPARENT combinators: nodes a declared order passes through untouched.

⚑⚑⚑ AN UNMODELLED TRANSPARENT NODE IS WHERE A REQUIREMENT SILENTLY STOPS. The carrier's whole
mechanism is that a consumer's order requirement propagates upstream to the producer that must
satisfy it. That propagation walks a chain of combinators, and it can only walk PAST a node that
declares what it does to the key. A filter that returned a bare generator would break the chain —
not loudly, but by making the next `require` compare against an order nobody restated. These three
exist to be NAMED, so the walk has something to step through.

⚑⚑ AND THAT IS WHY THEY ARE A SEPARATE MODULE FROM THE ORDER-REQUIRING COMBINATORS. `merge`,
`dedup`, `group` and `join` all call `Sorted.require` and can REFUSE; not one function here can.
The split is the property, not the file size: everything in this module is total, so a reader
asking "can this call fail?" gets the answer from the import line.

⚑⚑ `project` TAKES ITS OUTPUT KEY AS A REQUIRED ARGUMENT, WHICH IS THE ONE ASYMMETRY. `where` and
`limit` cannot disturb the order — they only drop rows — so their output key is derivable. A
projection can RENAME or DROP the very field the order was on, so an inferred key there would be a
FALSE order claim entering the system through the one node that looks harmless. Guessing is the
failure mode; requiring the argument is the fix.

⚑ EXTRACTED FROM `jea/metalanguage/sorted_stream.py` (⟡sorted-stream → ⟡typed-carrier, Ⓝ88b),
completing the split that `substrate/sort_key.py`, `substrate/sorted_carrier.py` and
`substrate/sorted_source.py` began.
"""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from substrate.sorted_carrier import Sorted

if TYPE_CHECKING:
    from collections.abc import Callable

    from substrate.sort_key import SortKey


def where[Row](
    stream: Sorted[Row],
    predicate: Callable[[Row], bool],
    origin: str = "filter",
) -> Sorted[Row]:
    """Keep the rows satisfying `predicate`, carrying the input's order through unchanged.

    ⚑ DROPPING ROWS CANNOT DISTURB AN ORDER. A subsequence of a sorted sequence is sorted by the
    same key, so this node is unconditionally order-preserving and never refuses.
    """
    return Sorted((row for row in stream if predicate(row)), stream.key, origin, stream.getter)


def limit[Row](stream: Sorted[Row], count: int, origin: str = "limit") -> Sorted[Row]:
    """Take the first `count` rows, carrying the input's order through unchanged.

    ⚑⚑ THIS IS WHERE THE LAZINESS PAYS. `limit(merge(a, b), 10)` pulls about ten rows from each
    input rather than draining both, because every node between here and the producers is a
    generator. A combinator set that materialized anywhere in that chain would still give the
    right ANSWER — which is exactly why the cost has to be pinned by a case, not by inspection.
    """
    return Sorted(itertools.islice(iter(stream), count), stream.key, origin, stream.getter)


def project[Row, Out](
    stream: Sorted[Row],
    transform: Callable[[Row], Out],
    key: SortKey,
    origin: str = "project",
) -> Sorted[Out]:
    """Map every row through `transform`, declaring `key` as the output's order.

    ⚑⚑ `key` IS REQUIRED AND NEVER INFERRED. `transform` may rename or drop the field the input
    was ordered on, so carrying the input's key forward would state an order that no longer holds.
    The caller knows what the projection did; the combinator does not, and must not guess.

    ⚑ THE GETTER IS DROPPED, NOT CARRIED. The input's getter resolves fields on the INPUT row
    shape, which `transform` has just replaced; reusing it would resolve names against a shape
    that no longer exists. The output falls back to the default resolver.
    """
    return Sorted((transform(row) for row in stream), key, origin)
