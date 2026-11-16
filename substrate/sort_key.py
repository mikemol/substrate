#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""An ORDER, as data — and the field access that reads a row under it.

⚑⚑⚑ THE ORDER IS DATA, NOT A COMMENT. A function returning "a sorted list" states its order in
prose no consumer can check; a `SortKey` can be REQUIRED, and a producer that does not supply it
refused by name. This module is the bottom of that stack: the key itself, and how a row's fields
are read for comparison. Nothing here streams — the carrier and the combinators are separate.

⚑⚑ `covers` IS A PREFIX TEST, AND STRICTER THAN IT LOOKS ON PURPOSE. `(a, b)` covers `(a,)` but
NOT `(b,)`, because sorting by `a` then `b` says nothing about the order of `b` alone. This is the
predicate that lets a consumer's requirement propagate UPSTREAM to the producer that must satisfy
it — a dict accepts any grouping at all, so the constraint never surfaces.

⚑⚑ `()` IS A LEGAL KEY AND MEANS UNORDERED — distinct from "sorted on nothing in particular". A
combinator needing an order refuses it, which is the honest failure: an unordered stream cannot
satisfy a requirement, and saying so beats returning a plausible wrong grouping.

⚑⚑⚑ AND `Cell` IS A PROTOCOL RATHER THAN `object`, WHICH IS THE WHOLE TYPING STORY. Field access
is dynamic — mapping key, then attribute, then positional index — so its result is whatever the
CALLER's row holds. Typed as `object`, every comparison downstream becomes `Any`; measured, that
is how `jea/metalanguage/sorted_stream.py` reached **411 type findings and one importer in 1,121
files**. Comparison is the only operation ever performed on a field, so that is exactly what the
type says, and structurally — `str`, `int`, `tuple` satisfy it without the caller's rows
inheriting anything from us.

⚑⚑ THE DYNAMIC ACCESS IS CONFINED TO ONE FUNCTION, AND THAT IS WHY THIS IS ITS OWN MODULE.
`getattr` is typed `Any`; binding its result before it travels is what stops the `Any` from
reaching every comparison in the package. Measured across the split: 411 findings in the
monolith, 5 in a four-layer draft, **1 here** — and that one was this line.

⚑ EXTRACTED FROM `jea/metalanguage/sorted_stream.py` (⟡sorted-stream → ⟡typed-carrier, Ⓝ31m″).
Operator, 2026-09-01, on four rewrites lost to a whole-file refusal: *"this indicates the file is
doing too much, and needs to be n-split."* The original's own section comments already named the
seams — the key, the carrier, the producers, the combinators — and every finding was in THIS one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Callable


@runtime_checkable
class Cell(Protocol):
    """A field value: something that compares.

    ⚑ STRUCTURAL, so the caller's rows satisfy it without declaring anything — which is required,
    because the rows belong to the caller and cannot be made to inherit from ours.
    """

    def __lt__(self, other: object, /) -> bool:
        """Report whether this cell sorts before `other`."""
        ...


class OrderError(Exception):
    """A declared order cannot support what a consumer asked, or a stream was consumed twice.

    ⚑ ALWAYS A REFUSAL, NEVER A DEGRADED ANSWER. A grouping performed on an unordered stream
    returns plausible groups that are silently wrong, which is worse than not running.
    """


@dataclass(frozen=True)
class SortKey:
    """An ORDER, as data: `fields` is primary-first, each `(name, descending)`."""

    fields: tuple[tuple[str, bool], ...] = ()

    @staticmethod
    def of(*names: str) -> SortKey:
        """Return an ascending key on each named field, primary first — the common case."""
        return SortKey(tuple((name, False) for name in names))

    @property
    def names(self) -> tuple[str, ...]:
        """Return the field names, primary first, without their directions."""
        return tuple(name for name, _descending in self.fields)

    def __bool__(self) -> bool:
        """Report whether this key orders anything at all."""
        return bool(self.fields)

    def __len__(self) -> int:
        """Return how many fields this key orders by."""
        return len(self.fields)

    def covers(self, other: SortKey) -> bool:
        """Report whether sorting by this key also sorts by `other` — a PREFIX test.

        ⚑ DIRECTION IS PART OF THE ANSWER: `(path ASC)` does not cover `(path DESC)`.
        """
        if len(other) > len(self):
            return False
        return self.fields[: len(other)] == other.fields

    def truncate(self, n: int) -> SortKey:
        """Return this key's first `n` fields — the order a consumer of a prefix may claim."""
        return SortKey(self.fields[:n])

    def __str__(self) -> str:
        """Return the key as a reader sees it in a refusal message."""
        if not self.fields:
            return "<unordered>"
        return ", ".join(f"{name}{' DESC' if desc else ''}" for name, desc in self.fields)


UNORDERED = SortKey(())


@dataclass(frozen=True, order=False)
class Rev:
    """A comparison-inverting wrapper for a DESCENDING field.

    ⚑ DESCENDING IS NOT NEGATION HERE. Negating works for numerics and fails for strings; a
    wrapper inverts the comparison itself and assumes nothing about the type.
    """

    value: Cell

    def __lt__(self, other: object, /) -> bool:
        """Report whether this sorts before `other` — inverted."""
        if not isinstance(other, Rev):
            return NotImplemented
        return other.value < self.value

    def __le__(self, other: object, /) -> bool:
        """Report whether this sorts at or before `other` — inverted."""
        if not isinstance(other, Rev):
            return NotImplemented
        return not self.value < other.value

    def __eq__(self, other: object) -> bool:
        """Report whether two wrapped cells are equal."""
        return isinstance(other, Rev) and self.value == other.value

    def __hash__(self) -> int:
        """Return a hash consistent with equality."""
        return hash(("Rev", self.value))


def as_cell(value: object) -> Cell:
    """Return `value` as a comparable cell, refusing one that cannot be ordered.

    ⚑ THE CHECK IS AT THE BOUNDARY, WHERE THE DYNAMIC ACCESS HAPPENS. Everything downstream then
    holds a `Cell` rather than an `object`, which is what stops the `Any` from propagating — and
    a field that cannot be compared is a fact about the ROW, reported here rather than as an
    obscure `TypeError` inside a sort three layers up.
    """
    if isinstance(value, Cell):
        return value
    msg = f"field value of type {type(value).__name__} does not compare; it cannot be sorted on"
    raise OrderError(msg)


def default_get(row: object, name: str) -> Cell:
    """Return field `name` of `row` — mappings, then attributes, then positional tuples.

    ⚑ THE THREE SHAPES ARE TRIED IN THIS ORDER DELIBERATELY. A NamedTuple is both a tuple and an
    attribute holder; resolving by name first means a caller's field name wins over a positional
    index that happens to parse as one.
    """
    if isinstance(row, dict):
        return as_cell(row[name])
    if hasattr(row, name):
        # ⚑ BOUND AS `object` BEFORE IT TRAVELS. `getattr` is typed `Any`, and passing that
        # straight into a call propagates it; annotating the binding confines the dynamic
        # access to this one line — which is the whole reason the field layer is its own module.
        attribute: object = getattr(row, name)
        return as_cell(attribute)
    if name.isdigit() and isinstance(row, tuple):
        return as_cell(row[int(name)])
    msg = f"cannot resolve field {name!r} on {type(row).__name__}; pass getter="
    raise OrderError(msg)


def extractor[Row](
    key: SortKey,
    getter: Callable[[Row, str], Cell] | None = None,
) -> Callable[[Row], tuple[Cell, ...]]:
    """Return the comparison tuple for a row under `key`."""
    get: Callable[[Row, str], Cell] = getter if getter is not None else default_get
    fields = key.fields

    def compare_by(row: Row) -> tuple[Cell, ...]:
        """Return this row's comparison tuple."""
        return tuple(Rev(get(row, name)) if desc else get(row, name) for name, desc in fields)

    return compare_by
