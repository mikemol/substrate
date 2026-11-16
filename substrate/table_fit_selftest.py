# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.table_fit` — the verdict that names whose fact it is.

⚑⚑⚑ THE ARM THAT MATTERS IS THE ONE SEPARATING A DEFECT IN THE DOCUMENT FROM A DEFECT IN THE
READER. The origin read a table's header inside a bare `except Exception: pass`, so an unreadable
head fell through to the empty-header branch and it reported *"pipe tables require a header row"* —
a confident diagnosis about the TABLE when the fact was about the READ. A missing answer is
recoverable; a wrong cause sends someone to edit a table that was fine.

⚑⚑ SO PRECEDENCE IS CASED, NOT JUST CLASSIFICATION. A table can be unreadable AND hold a block
cell, and reporting the block would be a claim built on a partial read. The unreadable verdict has
to win, and only a case with both conditions true at once shows that it does.

⚑ AND THE SENSITIVITY ARM FORCES THE STATE THE OTHERS CANNOT REACH: every arm below feeds a
correct `Table`, so none of them shows that `blocked` reads `header` rather than guessing from the
flags. Mutating a passing table's header must change the verdict.

⚑⚑ THE GATE REFUSED A SPLIT CASE LABEL AGAIN (`ISC004`, third time this arc, same construct in the
same position). Two adjacent strings inside `out.append` are one value until a comma appears, at
which point the verdict silently becomes the third argument. It is a habit of mine rather than
three accidents, so labels needing composition are named before the call, every time.
"""

from __future__ import annotations

import sys

from substrate import table_fit as tf
from substrate.table_read import Table

#: A table that a pipe writer can express: a header and ordinary cells.
FINE = Table(0, ("name", "home"), (("alpha", "one"),))

#: A table declaring no header — pipe tables require one.
HEADERLESS = Table(1, (), (("x", "y"),))

#: A table whose header could not be read — a fact about the reader, not the table.
UNREADABLE = Table(2, None, (("p", "q"),))

#: How many of the three fixtures a pipe writer must refuse.
BLOCKED_COUNT = 2


def _reason_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for each reason a pipe writer refuses a table."""
    out: list[tuple[str, bool]] = []

    out.append((f"an ordinary table is not blocked: {tf.blocked(FINE)}", tf.blocked(FINE) is None))
    out.append(
        (
            f"a headerless table is blocked: {tf.blocked(HEADERLESS)}",
            tf.blocked(HEADERLESS) is tf.Reason.NO_HEADER,
        )
    )
    out.append(
        (
            f"a block cell blocks: {tf.blocked(FINE, cell_blocks=True)}",
            tf.blocked(FINE, cell_blocks=True) is tf.Reason.BLOCK,
        )
    )
    out.append(
        (
            f"a hard line break blocks: {tf.blocked(FINE, cell_breaks=True)}",
            tf.blocked(FINE, cell_breaks=True) is tf.Reason.LINE_BREAK,
        )
    )
    return out


def _attribution_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the reader-versus-document distinction.

    ⚑⚑⚑ THIS IS THE REPAIR. The origin could only say NO_HEADER, so an unreadable head was
    reported as a defect the author should fix. These arms assert the two are different values
    AND that the verdict says which kind it is, because a caller acting on the wrong one edits
    a table that was never broken.
    """
    out: list[tuple[str, bool]] = []

    unreadable = tf.blocked(UNREADABLE)
    out.append(
        (
            f"an unreadable header is its own reason: {unreadable}",
            unreadable is tf.Reason.UNREADABLE,
        )
    )
    out.append(
        (
            f"and is NOT the headerless reason: {unreadable} vs {tf.blocked(HEADERLESS)}",
            unreadable is not tf.blocked(HEADERLESS),
        )
    )

    reader = tf.Verdict(2, "(no header)", tf.Reason.UNREADABLE)
    doc = tf.Verdict(1, "(no header)", tf.Reason.NO_HEADER)
    out.append(
        (
            f"the unreadable verdict knows it is about the reader: {reader.about_the_reader}",
            reader.about_the_reader,
        )
    )
    out.append(
        (
            f"and the headerless one knows it is not: {doc.about_the_reader}",
            not doc.about_the_reader,
        )
    )
    # ⚑ AND THE ACCOUNT SAYS SO IN WORDS, so a reader of one line does not need the convention.
    out.append((f"the account names the reader: {reader.why()[-24:]!r}", "READER" in reader.why()))
    out.append(
        (f"and names the table for the other: {doc.why()[-24:]!r}", "about the table" in doc.why())
    )
    return out


def _precedence_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the order in which reasons are decided.

    ⚑⚑ A TABLE CAN BE UNREADABLE *AND* HOLD A BLOCK CELL, and reporting the block would be a
    verdict computed over a table the reader could not fully see. Only a case with both conditions
    true at once distinguishes correct precedence from a lucky ordering.
    """
    out: list[tuple[str, bool]] = []

    both = tf.blocked(UNREADABLE, cell_blocks=True, cell_breaks=True)
    out.append((f"unreadable wins over a block cell: {both}", both is tf.Reason.UNREADABLE))

    # ⚑ AND HEADERLESS WINS OVER A CELL DEFECT TOO — the table cannot be a pipe table at all, so
    # naming a cell would report the reparable symptom over the disqualifying one.
    headerless_and_block = tf.blocked(HEADERLESS, cell_blocks=True)
    out.append(
        (
            f"headerless wins over a block cell: {headerless_and_block}",
            headerless_and_block is tf.Reason.NO_HEADER,
        )
    )

    # ⚑ AND A BLOCK OUTRANKS A BREAK, which is arbitrary but must be STABLE — a caller comparing
    # two runs needs the same table to report the same reason.
    both_cells = tf.blocked(FINE, cell_blocks=True, cell_breaks=True)
    out.append((f"a block outranks a break, stably: {both_cells}", both_cells is tf.Reason.BLOCK))
    return out


def _verdicts_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the whole-document pass."""
    out: list[tuple[str, bool]] = []

    got = tf.verdicts(
        [(FINE, False, False), (HEADERLESS, False, False), (UNREADABLE, False, False)]
    )
    out.append((f"only the blocked tables produce verdicts: {len(got)}", len(got) == BLOCKED_COUNT))
    out.append(
        (
            f"and they carry their positions: {[v.position for v in got]}",
            [v.position for v in got] == [1, 2],
        )
    )
    out.append(
        (
            f"the fine table produces nothing: {[v.position for v in got]}",
            all(v.position != 0 for v in got),
        )
    )

    # ⚑ THE LABEL COMES FROM THE HEADER when there is one, so a reader can find the table without
    # a line number the AST does not carry.
    labelled = tf.verdicts([(Table(0, ("name", "home"), ()), True, False)])
    out.append(
        (
            f"a labelled verdict quotes its header: {labelled[0].label!r}",
            "name" in labelled[0].label,
        )
    )
    out.append(
        (
            f"and a headerless one says so: {tf.label_for(HEADERLESS)!r}",
            tf.label_for(HEADERLESS) == "(no header)",
        )
    )
    return out


def _sensitivity_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving `blocked` READS the header rather than guessing.

    ⚑⚑ EVERY ARM ABOVE FEEDS A CORRECT TABLE, so none of them shows that the header field is
    consulted at all — a `blocked` that ignored it and answered from the flags alone would pass
    the reason arms and fail only here. Mutating a passing table's header must change the verdict.
    """
    out: list[tuple[str, bool]] = []

    passing = tf.blocked(FINE)
    mutated = tf.blocked(Table(FINE.position, None, FINE.rows))
    label = f"a passing table stops passing when its header goes unreadable: {passing} -> {mutated}"

    out.append((label, passing is None and mutated is tf.Reason.UNREADABLE))
    return out


def _control_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the negative controls.

    ⚑ A CHECKER THAT BLOCKED EVERYTHING would pass every reason arm, so an ordinary table must
    produce no verdict — and an empty document must produce an empty list rather than raising.
    """
    out: list[tuple[str, bool]] = []

    out.append((f"an empty document yields no verdicts: {tf.verdicts([])}", tf.verdicts([]) == []))
    clean = tf.verdicts([(FINE, False, False)])
    out.append((f"a document of fine tables yields none either: {clean}", clean == []))
    # ⚑ AND A LONG HEADER IS TRUNCATED rather than dropped — a label is for finding the table,
    # so an unbounded one would push the reason off the line that carries it.
    long_header = Table(0, ("x" * 80,), ())
    out.append(
        (
            f"a long header is truncated: {len(tf.label_for(long_header))}",
            len(tf.label_for(long_header)) == tf.LABEL_WIDTH,
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _reason_cases()
        + _attribution_cases()
        + _precedence_cases()
        + _verdicts_cases()
        + _sensitivity_cases()
        + _control_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"table-fit selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
