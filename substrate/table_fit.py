# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decide which tables a pipe writer cannot express, and say WHY.

⚑⚑⚑ WIDTH IS NOT THE ONLY REASON, AND ASSUMING IT WAS COST TWO SEARCHES. Measured on this repo's
own plan: at a column budget of two thousand it still emits multiline tables, so a width-only
explanation is exhausted and a bisection looking for a width boundary is looking for something
that is not there. The pipe format cannot express certain CONTENT at any budget.

⚑⚑ THE THREE STRUCTURAL REASONS, and each is a property of a cell or of the table rather than of
the page width: a cell holding a BLOCK (a list, a fenced block, several paragraphs), a cell holding
a HARD LINE BREAK, and a table with NO header row. Anything else is a width question, and the
distinction matters because only one of the two is fixable by a setting.

⚑⚑⚑ AND THE ORIGIN TURNED ITS OWN BLINDNESS INTO A DIAGNOSIS ABOUT THE DOCUMENT (gate-G240, one
consequence worse). It read the header inside a bare `except Exception: pass`, so an unreadable
head fell through to the empty-header branch and the tool reported *"pipe tables require a header
row"* — naming a defect in the DOCUMENT when the fact was about the READER. A missing answer is
recoverable; a confident wrong cause sends the reader to edit a table that was fine.

⚑ SO AN UNREADABLE HEADER IS ITS OWN VERDICT HERE. `Reason.UNREADABLE` is distinct from
`Reason.NO_HEADER`, and a caller that wants to treat them alike may — but it must choose to.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Sequence

    from substrate.table_read import Table

#: How much of a header to quote when naming which table a verdict is about.
LABEL_WIDTH = 22


class Reason(StrEnum):
    """Why a table cannot be emitted as a pipe table.

    ⚑ THE UNREADABLE CASE IS A REASON, NOT AN ABSENCE. The origin collapsed it into NO_HEADER and
    thereby blamed the document for the reader's failure — the one outcome worse than saying
    nothing, because it directs a repair at something that is not broken.
    """

    BLOCK = "cell holds a block (list, fence, or several paragraphs)"
    LINE_BREAK = "cell holds a hard line break"
    NO_HEADER = "pipe tables require a header row and this table declares none"
    UNREADABLE = "the header could not be read, so no verdict is available for this table"


class Verdict(NamedTuple):
    """One table that cannot be emitted as a pipe table, and the reason.

    ⚑ `label` IS THE HEADER TEXT, TRUNCATED, so a reader can find the table without a line number
    the AST does not carry. `position` is what makes it unambiguous when two tables share a header.
    """

    position: int
    label: str
    reason: Reason

    @property
    def about_the_reader(self) -> bool:
        """Report whether this verdict describes the READER rather than the document.

        ⚑ THE PROPERTY A CALLER NEEDS BEFORE ACTING. Three of the four reasons are facts about the
        table and are repairable by editing it; the fourth is a fact about the read and is not.
        Presenting them in one list without this distinction is what made the origin's output
        actionable-looking and wrong.
        """
        return self.reason is Reason.UNREADABLE

    def why(self) -> str:
        """Return a one-line account naming the table, the reason, and whose fact it is."""
        whose = "⚑ about the READER" if self.about_the_reader else "about the table"
        return f"table {self.position} ({self.label!r}): {self.reason.value} — {whose}"


def label_for(table: Table) -> str:
    """Return a short quotable label for `table`, from its header when it has one."""
    if not table.header:
        return "(no header)"
    return " | ".join(cell[:LABEL_WIDTH] for cell in table.header)


def blocked(table: Table, *, cell_blocks: bool = False, cell_breaks: bool = False) -> Reason | None:
    """Return why `table` cannot be a pipe table, or None when nothing blocks it.

    ⚑⚑ THE CELL PROPERTIES ARRIVE AS FLAGS RATHER THAN BEING RE-DERIVED HERE, because reading them
    needs the panflute AST and this module must stay testable without pandoc. The caller that owns
    the AST answers *does any cell hold a block* and *does any cell hold a break*; this owns the
    PRECEDENCE, which is the part a reader has to agree on.

    ⚑ AND THE ORDER IS DELIBERATE: an unreadable header is reported before anything else, because
    a verdict computed over a table the reader could not fully see is not a verdict about that
    table. Reporting a cell defect while unable to read the header would be a confident claim built
    on a partial read.
    """
    if table.header is None:
        return Reason.UNREADABLE
    if not table.header:
        return Reason.NO_HEADER
    if cell_blocks:
        return Reason.BLOCK
    if cell_breaks:
        return Reason.LINE_BREAK
    return None


def verdicts(tables: Sequence[tuple[Table, bool, bool]]) -> list[Verdict]:
    """Return one `Verdict` per table that cannot be emitted as a pipe table.

    ⚑ TABLES THAT CAN BE EMITTED PRODUCE NOTHING, so an empty result means every table fits — and
    the caller must state its denominator, because an empty list from a document with no tables at
    all says something entirely different.
    """
    out: list[Verdict] = []
    for table, has_blocks, has_breaks in tables:
        reason = blocked(table, cell_blocks=has_blocks, cell_breaks=has_breaks)
        if reason is not None:
            out.append(Verdict(table.position, label_for(table), reason))
    return out
