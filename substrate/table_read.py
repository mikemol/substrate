# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read a markdown document's tables — one walk, header and rows together.

⚑⚑⚑ THE ORIGIN WALKED THE AST TWICE FOR ONE TRAVERSAL'S WORTH OF ANSWER. `tables()` reported each
table's header and size; `table_rows()` re-parsed the document to reach the cells. Both took a
path, so asking both questions about one file converted it through pandoc twice — and neither
could be tested without a document on disk.

⚑⚑ AND THE HEADER READ SWALLOWED ITS OWN FAILURE. The origin wrapped it in a bare `except
Exception: pass`, so a table whose head could not be read reported ZERO COLUMNS — indistinguishable
from a table that genuinely has no header. That is the silence class this drain exists to remove:
a reader that cannot say UNREADABLE reports its own limit as a fact about the document.

⚑ SO A HEADERLESS TABLE AND AN UNREADABLE ONE ARE DIFFERENT VALUES HERE. `header` is an empty tuple
when the table declares no head, and `None` when the head was present and could not be read. A
caller that wants to treat them alike may; one that needs to distinguish them now can.

⚑⚑ THE FILTERED READ CARRIES ITS TABLE POSITION, which the origin's docstring argues for and which
is worth keeping verbatim: a row without its table is the bare-count defect one level down. A
filtered result that says only WHAT matched, never WHERE, cannot be acted on without re-reading.

⚑ AND THE FIELD IS `position`, NOT `index`, BECAUSE THE TYPE CHECKER REFUSED THE OBVIOUS NAME. A
`NamedTuple` inherits `tuple.index`, so a field called `index` shadows a method and the annotation
collides. The origin never met this — it returned bare tuples, where a positional slot has no name
to collide with — which is a real cost of the shape it used rather than a quirk of this one.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Sequence


class Table(NamedTuple):
    """One table: its position, its header, and its rows.

    ⚑ `header` IS `None` WHEN UNREADABLE AND `()` WHEN ABSENT, and the distinction is the whole
    repair. The origin collapsed both to a zero-length header, so a reader could not tell a
    headerless table from one whose head it failed to parse.
    """

    position: int
    header: tuple[str, ...] | None
    rows: tuple[tuple[str, ...], ...]

    @property
    def columns(self) -> int | None:
        """Report the header's width, or None when the header could not be read."""
        return None if self.header is None else len(self.header)

    def why(self) -> str:
        """Return a one-line account naming every component of the read."""
        if self.header is None:
            return f"table {self.position}: {len(self.rows)} row(s), header UNREADABLE"
        if not self.header:
            return f"table {self.position}: {len(self.rows)} row(s), no header declared"
        return (
            f"table {self.position}: {len(self.rows)} row(s) x {len(self.header)} col(s), "
            f"header {list(self.header)}"
        )


def matches(cells: Sequence[str], needle: str) -> bool:
    """Report whether `needle` appears in any of `cells`, case-folded.

    ⚑ THE CELLS ARE JOINED ON A SEPARATOR NO CELL CAN CONTAIN, so a needle cannot match across a
    cell boundary and report a row that does not hold it. Joining on a space would let `"a b"`
    match a row whose cells are `["a", "b"]`, which is a false positive nothing downstream could
    detect.
    """
    return needle.casefold() in "\x00".join(cells).casefold()


def select(
    tables: Sequence[Table], *, position: int | None = None, where: str | None = None
) -> list[tuple[int, tuple[str, ...]]]:
    """Return `(table_position, cells)` for every row passing the filters.

    ⚑ THE TABLE POSITION TRAVELS WITH EVERY ROW. A filtered read that returned bare cells would say
    WHAT matched and never WHERE, so a caller could not open the result — the bare-count defect
    applied to rows.
    """
    out: list[tuple[int, tuple[str, ...]]] = []
    for table in tables:
        if position is not None and table.position != position:
            continue
        out.extend(
            (table.position, row) for row in table.rows if where is None or matches(row, where)
        )
    return out
