# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read the cell properties a pipe-table verdict needs, off the markdown AST.

⚑⚑⚑ THIS IS THE HALF `table_fit` DELIBERATELY DOES NOT OWN. That module holds the PRECEDENCE — an
unreadable header outranks a missing one, which outranks a block cell, which outranks a line break
— and takes the cell facts as flags so it stays testable without pandoc. Nothing supplied those
flags: `module_importers substrate.table_fit` reported ONE import site, its own suite. The
precedence was built and reachable by nothing, so the capability was half drained and read as
whole.

⚑⚑ WIDTH IS NOT THE ONLY REASON, AND ASSUMING IT WAS COST TWO SEARCHES (operator, 2026-08-01:
*"sounds like width isn't the problem, then"*). MEASURED: at `--columns=2000` the plan still emits
multiline tables, so a width-only explanation is exhausted and the bisection correctly REFUSED
rather than returning a boundary that does not exist. The pipe format cannot express certain
content at any budget:

  * a cell holding a BLOCK — multiple paragraphs, a list, a fenced block — because pipe cells are
    single-line inline content by construction;
  * a cell holding a HARD LINE BREAK;
  * a table with NO header row, which pipe tables require.

Anything else is a width question, and that is `md_width`'s.

⚑ IT READS THE AST RATHER THAN THE EMITTED TEXT, so it says WHICH table and WHICH cause instead of
leaving a reader to infer a mechanism from a symptom — the error made four times in one sitting
before the tool could answer it.

⚑⚑ AND A STRUCTURE IT CANNOT READ IS REPORTED, NEVER ASSUMED FINE. The origin wrapped its header
read in a bare `except Exception: pass`, so a table whose head could not be walked fell through to
an empty header and was reported as *no header row* — a confident verdict built on a failed read.
Here `None` and `()` are different answers, and `table_fit.Reason` maps them to different outcomes.
"""

from __future__ import annotations

from typing import NamedTuple

import panflute

#: The block kinds a pipe cell CAN hold. Anything else is a block that pipe syntax cannot express.
INLINE_BLOCKS = (panflute.Plain, panflute.Para)


class Cells(NamedTuple):
    """What one table's cells hold, as the flags a verdict needs.

    ⚑ `readable` IS A SEPARATE FACT FROM THE TWO DEFECTS. A table whose structure could not be
    walked has unknown cells, and reporting `blocks=False, breaks=False` for it would be a clean
    bill of health issued by a reader that saw nothing.
    """

    readable: bool
    blocks: bool
    breaks: bool

    def why(self) -> str:
        """Return a one-line account of what was found."""
        if not self.readable:
            return "the table's structure could not be walked"
        found = [
            name
            for name, seen in (("a block cell", self.blocks), ("a hard line break", self.breaks))
            if seen
        ]
        return " and ".join(found) if found else "nothing that blocks pipe syntax"


def _cell_blocks(cell: panflute.TableCell) -> bool:
    """Report whether `cell` holds content pipe syntax cannot express.

    ⚑ TWO CONDITIONS, AND THE SECOND IS EASY TO MISS. A cell holding a single non-inline block is
    blocked, and so is a cell holding SEVERAL inline blocks — two paragraphs are two blocks even
    when each one alone would fit.
    """
    blocks = list(cell.content)
    if any(not isinstance(b, INLINE_BLOCKS) for b in blocks):
        return True
    return len(blocks) > 1


def _cell_breaks(cell: panflute.TableCell) -> bool:
    """Report whether `cell` holds a hard line break."""
    for block in cell.content:
        if isinstance(block, INLINE_BLOCKS) and any(
            isinstance(el, panflute.LineBreak) for el in block.content
        ):
            return True
    return False


def _cells_of(table: panflute.Table) -> list[panflute.TableCell]:
    """Return every body cell of `table`."""
    return [cell for body in table.content for row in body.content for cell in row.content]


def read(table: panflute.Table) -> Cells:
    """Return the cell flags for `table`, or an unreadable verdict when it will not walk.

    ⚑⚑ THE WALK IS GUARDED AND THE GUARD REPORTS. panflute's table shape varies with the reader
    version, and a structure this cannot traverse is a fact about the READ — so it comes back as
    `readable=False` rather than as two comfortable falses.
    """
    try:
        cells = _cells_of(table)
    except (AttributeError, TypeError):
        return Cells(readable=False, blocks=False, breaks=False)
    return Cells(
        readable=True,
        blocks=any(_cell_blocks(c) for c in cells),
        breaks=any(_cell_breaks(c) for c in cells),
    )


def header_cells(table: panflute.Table) -> tuple[str, ...] | None:
    """Return the header row's cell texts, `()` when absent, or None when unreadable.

    ⚑⚑⚑ THE THREE OUTCOMES ARE THE WHOLE POINT, AND THE ORIGIN HAD TWO. It caught every exception
    and fell through to an empty header, so *could not read the head* and *there is no head*
    produced the same verdict — `no header row` — on tables that differ in what a reader must do
    next.
    """
    try:
        rows = list(table.head.content)
    except AttributeError:
        return None
    if not rows:
        return ()
    return tuple(panflute.stringify(cell).strip() for cell in rows[0].content)


def tables(doc: panflute.Doc) -> list[panflute.Table]:
    """Return every table in `doc`, in document order."""
    found: list[panflute.Table] = []

    def collect(el: panflute.Element, _doc: panflute.Doc) -> None:
        """Append `el` when it is a table."""
        if isinstance(el, panflute.Table):
            found.append(el)

    doc.walk(collect)
    return found
