#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A result row readable BY NAME, with the column tuple interned once per result set.

⚑⚑⚑ NAMES ARE THE POINT, AND THE ARGUMENT FOR THEM IS ABOUT WHAT THE CODE CAN THEN TELL YOU
rather than about tidiness (operator, 2026-08-06: *"I'll actually push that we migrate to names
here. My reasoning is forward-looking: By using names, it's easier for us to structurally trace
for reuse"*). Two consequences, both measured:

  * A named read is STRUCTURALLY TRACEABLE — a column-keyed census finds every consumer of that
    column. A positional read is opaque: nothing can resolve `row[2]` without reading the SELECT
    and counting, so it severs a column from its consumers and defeats the reuse-search this
    repo runs on.
  * A positional read SILENTLY SHIFTS when a SELECT gains a column. `core_fp` gained a column and
    an existing `row[2]` against it then read a different field with no error. A named read fails
    loudly or keeps working; there is no third outcome where it quietly means something else.

⚑⚑ THE FIRST CUT OF THIS YIELDED BARE TUPLES, arguing that positional rows port the existing
`row[0]` call sites unchanged. That is a COST argument, not a reason — the same shape as
preserving any defect because touching it is work — and it is recorded here rather than dropped
because the argument is genuinely tempting and will be made again.

⚑ POSITIONAL ACCESS IS KEPT SO THE MIGRATION CAN BE INCREMENTAL. Making names the ONLY access
would require converting every positional reader in one commit, and an atomic rewrite of every
reader is the migration that stalls. ⚑ That tolerance is a RAMP, NOT THE DESTINATION: new code
reads by name, and the positional sites are debt with a name rather than an idiom to preserve.

⚑⚑⚑ THE KEYS ARE SHARED ACROSS A RESULT SET, NOT STORED PER ROW, AND THAT IS A MEMORY FACT
RATHER THAN A STYLE ONE. Every row of one query has the SAME columns, so the key tuple is a
property of the CURSOR: interning one tuple per query and pointing every row at it costs one
pointer per row instead of a per-row mapping — and these result sets run to millions of rows.
`columns` is therefore built once by the reader and passed in, never derived per row.

⚑⚑ AND THE PREDECESSOR SUBCLASSED `tuple`, WHICH IS THE ONE SHAPE THAT CANNOT CARRY THIS. A
tuple subclass cannot declare a non-empty `__slots__` — its storage is fixed at allocation — so
the shared key tuple had to live in an undeclared attribute that no checker could see, and the
type reported that attribute as missing at every use. A slotted record holds both the values and
the shared key tuple honestly, and costs one object rather than one object plus a hidden dict.

⚑ IT REACHES FOR NOTHING. No driver, no connection, no declaration — a row is assembled from a
key tuple and a value sequence, so every case runs with the store unreachable and the type can
be constructed by any reader that has columns and values, whatever produced them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence


@dataclass(frozen=True, slots=True)
class Row:
    """One result row: the shared column tuple, and this row's values in that order.

    ⚑ THE COLUMNS ARE A TUPLE AND THE VALUES A TUPLE, both frozen, because a row handed to a
    caller must not be editable behind the reader that produced it — and because the column
    tuple is SHARED by every row of the result set, so a mutation would rewrite the columns of
    rows already yielded.
    """

    columns: tuple[str, ...]
    values: tuple[object, ...]

    def __getitem__(self, key: str | int) -> object:
        """Return one field, by column name or, transitionally, by position.

        ⚑ AN UNKNOWN NAME RAISES `KeyError` NAMING THE COLUMNS THAT ARE THERE. A reader chasing a
        renamed column otherwise learns only that its key was absent, and has to go read the
        SELECT to find what it should have asked for.
        """
        if isinstance(key, str):
            try:
                index = self.columns.index(key)
            except ValueError:
                msg = f"{key!r} not in row; columns are {list(self.columns)}"
                raise KeyError(msg) from None
            return self.values[index]
        return self.values[key]

    def __len__(self) -> int:
        """Return how many fields this row carries."""
        return len(self.values)

    def __iter__(self) -> Iterator[object]:
        """Iterate the values in column order, so unpacking works as it did for a tuple."""
        return iter(self.values)

    def keys(self) -> tuple[str, ...]:
        """Return the column names, in declared order."""
        return self.columns

    def get(self, key: str | int, default: object = None) -> object:
        """Return one field, or `default` when the column is absent.

        ⚑ THE DEFAULT IS THE CALLER'S TO STATE. A reader that wants a missing column to be an
        error uses the subscript; one that wants a fallback says which. Folding a default into
        the subscript would make an absent column indistinguishable from a stored `None`.
        """
        try:
            return self[key]
        except (KeyError, IndexError):
            return default

    def as_dict(self) -> dict[str, object]:
        """Return this row as a fresh `{column: value}` mapping."""
        return dict(zip(self.columns, self.values, strict=True))


def build(columns: tuple[str, ...], values: Sequence[object]) -> Row:
    """Assemble one row against an already-interned column tuple.

    ⚑⚑ THE COLUMN TUPLE IS PASSED IN RATHER THAN DERIVED, WHICH IS THE WHOLE MEMORY ARGUMENT. A
    builder that computed the columns per row would allocate one tuple per row across result sets
    of millions — the reader interns it once from the cursor description and hands the same
    object to every row.

    ⚑ AN ARITY MISMATCH REFUSES RATHER THAN TRUNCATING. A row with fewer values than columns
    would answer every name up to the short point and raise for the rest, so the failure would
    surface at whichever column a caller happened to read first — naming the column rather than
    the mismatch that caused it.
    """
    row = tuple(values)
    if len(row) != len(columns):
        msg = (
            f"row has {len(row)} value(s) against {len(columns)} column(s) {list(columns)}. "
            f"A mismatch is refused here rather than answering the names that happen to line up, "
            f"because a truncated row fails at whichever column is read first."
        )
        raise ValueError(msg)
    return Row(columns=columns, values=row)
