#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A single-pass stream PLUS the order it is in PLUS where that claim came from.

⚑⚑⚑ THE CARRIER IS WHAT MAKES A REQUIREMENT PROPAGATE UPSTREAM. A function returning "a sorted
iterator" states its order in prose, so a consumer needing a different one can only re-sort
defensively. A `Sorted` carries its `SortKey` as data, so `require` can REFUSE — and the refusal
names the `origin`, because the fix belongs at the producer that made the claim, not at the call
site that noticed it was wrong.

⚑⚑ `origin` IS NOT DECORATIVE, AND THAT IS THE WHOLE REASON IT IS A FIELD. When `group` refuses,
the operator's next question is WHICH producer must change; a refusal naming only the combinator
sends them to the one place that is already correct. This is the field that turns a runtime error
into an instruction.

⚑⚑⚑ A SECOND CONSUMPTION RAISES, BECAUSE THE DEGRADED ANSWER IS SILENT. A spent generator yields
nothing the second time — so a double-consume produces an EMPTY RESULT rather than an error, and
an empty result is a plausible answer. Every refusal in this stack exists because the alternative
is not a crash but a wrong answer that looks right; single-pass-ness is that failure at its most
invisible.

⚑⚑ GENERIC OVER `Row`, SO THE CALLER'S ROWS STAY THE CALLER'S. The stream never inspects a row —
only `substrate.sort_key.extractor` does, through the `Cell` protocol. Typing the element as
`object` would make every downstream comparison `Any`, which is the cascade the split was for.

⚑⚑ AND THE `isinstance` GUARD THE ORIGINAL CARRIED IS GONE, WHICH THE TYPE GATE ESTABLISHED. It
refused a non-`SortKey` key at runtime; under an annotated signature mypy proves that branch
UNREACHABLE and refuses the file. The check was standing in for the annotation this module now
has — a runtime guard against a mistake the type system already prevents is debt, not safety.

⚑ EXTRACTED FROM `jea/metalanguage/sorted_stream.py` (⟡sorted-stream → ⟡typed-carrier, Ⓝ88b),
continuing the split that `substrate/sort_key.py` began — its docstring names this seam:
*"Nothing here streams — the carrier and the combinators are separate."*
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate.sort_key import Cell, OrderError, SortKey, extractor

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator


class Sorted[Row]:
    """A single-pass stream of rows, the order it claims, and the producer that claimed it.

    ⚑ THE CLAIM IS NOT VERIFIED HERE. Checking would consume the stream, which is the cost this
    carrier exists to avoid; `substrate.sorted_source.checked` is the opt-in paranoid form.
    """

    __slots__ = ("_consumed", "_rows", "getter", "key", "origin")

    def __init__(
        self,
        rows: Iterable[Row],
        key: SortKey,
        origin: str = "?",
        getter: Callable[[Row, str], Cell] | None = None,
    ) -> None:
        """Adopt `rows` as a stream sorted by `key`, attributed to `origin`."""
        self._rows: Iterator[Row] = iter(rows)
        self.key = key
        self.origin = origin
        self.getter = getter
        self._consumed = False

    def __iter__(self) -> Iterator[Row]:
        """Return the underlying rows, refusing a second pass.

        ⚑ THE REFUSAL IS THE POINT. A spent generator returns an empty iterator, so without this
        the second consumer gets a wrong ANSWER instead of an error.
        """
        if self._consumed:
            msg = (
                f"Sorted({self.origin!r}) already consumed — a stream is single-pass. "
                f"Materialize it with list() if you need it twice, and say why."
            )
            raise OrderError(msg)
        self._consumed = True
        return self._rows

    @property
    def consumed(self) -> bool:
        """Report whether this stream has already been iterated."""
        return self._consumed

    def __repr__(self) -> str:
        """Return the order and the single-pass state, as a reader debugging a refusal sees it."""
        state = "consumed" if self._consumed else "fresh"
        return f"Sorted({self.origin} sorted-by[{self.key}] {state})"

    def extract(self) -> Callable[[Row], tuple[Cell, ...]]:
        """Return the comparison function for this stream's own declared key."""
        return extractor(self.key, self.getter)

    def require(self, want: SortKey, who: str) -> None:
        """Refuse unless this stream's declared order supports `want`.

        ⚑⚑ THIS IS THE UPSTREAM-PROPAGATION MECHANISM. Each refusal names `origin` and says
        "push the constraint to" it, because a consumer cannot fix an order it did not create —
        the producer must sort differently, and the message has to say which producer.
        """
        if not want:
            msg = f"{who}: asked for an empty key — nothing to require"
            raise OrderError(msg)
        if not self.key:
            msg = (
                f"{who}: stream {self.origin!r} declares no order; it must be produced "
                f"sorted by [{want}] — push the constraint to {self.origin!r}"
            )
            raise OrderError(msg)
        if not self.key.covers(want):
            msg = (
                f"{who}: stream {self.origin!r} is sorted by [{self.key}], which does not "
                f"cover [{want}] (a prefix match is required) — push the constraint to "
                f"{self.origin!r}"
            )
            raise OrderError(msg)
