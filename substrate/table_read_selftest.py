# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.table_read` — the three header states, and the join that cannot bleed.

⚑⚑⚑ THE THREE HEADER STATES ARE THE POINT, AND THE ORIGIN COULD EXPRESS TWO. A table with a header,
a table declaring none, and a table whose header could not be read are three different facts; the
origin's bare `except Exception: pass` collapsed the last two into a zero-width header. Every arm
below that asserts `columns` is really asserting that the collapse is gone.

⚑⚑ THE CELL-BOUNDARY ARM IS THE ONE A NAIVE JOIN FAILS. Joining cells on a space lets a needle
match ACROSS a boundary — `"a b"` finding a row whose cells are `["a", "b"]` — and nothing
downstream can detect that false positive, because the row really is in the table. The separator
is a character no cell can contain, and the case proves it by asserting the cross-boundary needle
does NOT match.

⚑ AND THE SENSITIVITY ARM MUTATES THE SEPARATOR, because every other arm here uses correct data and
none of them can tell a boundary-safe join from one that happens not to collide on this fixture.

⚑⚑ THE GATE REFUSED A CASE LABEL BUILT BY IMPLICIT CONCATENATION INSIDE THE CALL (`ISC004`) — the
second time this arc. Two adjacent strings in an argument tuple are one value until a comma
appears, at which point they silently become two arguments and the case's verdict shifts position.
Labels that need composing are named first.
"""

from __future__ import annotations

import sys

from substrate import table_read as tr

#: A table with a header, one without, and one whose header could not be read.
WITH_HEADER = tr.Table(0, ("name", "home"), (("alpha", "one"), ("beta", "two")))
NO_HEADER = tr.Table(1, (), (("x", "y"),))
UNREADABLE = tr.Table(2, None, (("p", "q"),))
ALL_TABLES = [WITH_HEADER, NO_HEADER, UNREADABLE]

#: The cells and needle the boundary arms turn on — one needle spanning two cells.
SPLIT_CELLS = ["alpha", "one"]
SPANNING = "alpha one"

#: How many rows the fixture holds in total, named so the arms and the data cannot drift.
TOTAL_ROWS = 4

#: The header width of the one table that declares a header.
HEADER_COLS = 2


def _header_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the three header states the origin collapsed to two."""
    out: list[tuple[str, bool]] = []

    out.append(
        (f"a header reports its width — {WITH_HEADER.why()}", WITH_HEADER.columns == HEADER_COLS)
    )
    out.append(
        (f"a declared-headerless table reports 0 — {NO_HEADER.why()}", NO_HEADER.columns == 0)
    )
    # ⚑⚑⚑ THE REPAIR, ASSERTED. The origin returned 0 here too, so this is the ONE arm that
    # distinguishes the new reader from the old one on the defect it was built for.
    out.append(
        (
            f"an UNREADABLE header reports None, not 0 — {UNREADABLE.why()}",
            UNREADABLE.columns is None,
        )
    )
    out.append(
        (
            f"and 0 is not None: {NO_HEADER.columns} vs {UNREADABLE.columns}",
            NO_HEADER.columns != UNREADABLE.columns,
        )
    )
    # ⚑ THE ACCOUNT NAMES WHICH STATE IT IS IN, so a reader of the line does not have to know the
    # convention to act on it.
    out.append(
        (
            f"the unreadable case says so: {'UNREADABLE' in UNREADABLE.why()}",
            "UNREADABLE" in UNREADABLE.why(),
        )
    )
    out.append(
        (
            f"the headerless case says so: {'no header' in NO_HEADER.why()}",
            "no header" in NO_HEADER.why(),
        )
    )
    return out


def _select_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for row selection and its filters."""
    out: list[tuple[str, bool]] = []

    every = tr.select(ALL_TABLES)
    out.append((f"an unfiltered read returns every row: {len(every)}", len(every) == TOTAL_ROWS))
    # ⚑⚑ EVERY ROW CARRIES ITS TABLE. A filtered result that said only WHAT matched could not be
    # opened by the caller — the bare-count defect applied to rows.
    out.append(
        (
            f"and every row names its table: {[p for p, _ in every]}",
            [p for p, _ in every] == [0, 0, 1, 2],
        )
    )

    one = tr.select(ALL_TABLES, position=1)
    out.append((f"a position filter selects one table: {one}", one == [(1, ("x", "y"))]))

    found = tr.select(ALL_TABLES, where="ALPHA")
    out.append((f"a needle matches case-insensitively: {found}", found == [(0, ("alpha", "one"))]))

    both = tr.select(ALL_TABLES, position=0, where="two")
    out.append((f"filters compose: {both}", both == [(0, ("beta", "two"))]))
    return out


def _boundary_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the cell-boundary join a naive separator gets wrong.

    ⚑⚑⚑ THE FALSE POSITIVE NOTHING DOWNSTREAM CAN DETECT. If cells join on a space, the needle
    `"alpha one"` matches a row whose cells are `["alpha", "one"]` — and the row really IS in the
    table, so no consumer can tell the match was spurious. The separator must be a character a
    cell cannot contain.
    """
    out: list[tuple[str, bool]] = []

    inside = tr.matches(SPLIT_CELLS, "alpha")
    out.append((f"a needle inside one cell matches: {inside}", inside))

    spanning = tr.matches(SPLIT_CELLS, SPANNING)
    out.append((f"a needle spanning two cells does NOT: {spanning}", not spanning))

    # ⚑ AND THE SAME TEXT MATCHES WHEN IT REALLY IS ONE CELL, which is the control proving the
    # arm above rejects for the right reason rather than rejecting everything.
    whole = tr.matches([SPANNING], SPANNING)
    out.append((f"but does when the cell holds it whole: {whole}", whole))
    return out


def _sensitivity_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the boundary arms would CATCH a naive separator.

    ⚑⚑ EVERY ARM ABOVE USES THE REAL JOIN, so none of them shows that the separator choice is
    load-bearing rather than incidental. This computes what a space-joined matcher WOULD answer
    and asserts it differs — if the two agreed, the boundary arms would be passing for a reason
    unrelated to the separator.
    """
    out: list[tuple[str, bool]] = []

    real = tr.matches(SPLIT_CELLS, SPANNING)
    naive = SPANNING.casefold() in " ".join(SPLIT_CELLS).casefold()

    out.append(
        (
            f"a space join WOULD match where the real one does not: {naive} vs {real}",
            naive and not real,
        )
    )
    return out


def _control_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the negative controls.

    ⚑ A MATCHER THAT ACCEPTED EVERYTHING would pass every positive arm above, so an absent needle
    must return nothing — and an empty table list must select nothing rather than raising.
    """
    out: list[tuple[str, bool]] = []

    absent = tr.select(ALL_TABLES, where="nothing like this")
    out.append((f"an absent needle selects nothing: {absent}", absent == []))
    out.append((f"an empty table list selects nothing: {tr.select([])}", tr.select([]) == []))
    # ⚑ A POSITION THAT NAMES NO TABLE returns empty rather than the whole set — an off-by-one in
    # the filter would silently widen a targeted read.
    unmatched = tr.select(ALL_TABLES, position=99)
    out.append((f"an unmatched position selects nothing: {unmatched}", unmatched == []))
    # ⚑ AND AN EMPTY NEEDLE MATCHES EVERY ROW, which is the honest reading of a substring test
    # and worth pinning so nobody "fixes" it into a refusal a caller does not expect.
    blank = tr.select(ALL_TABLES, where="")
    out.append((f"an empty needle matches all: {len(blank)}", len(blank) == TOTAL_ROWS))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _header_cases()
        + _select_cases()
        + _boundary_cases()
        + _sensitivity_cases()
        + _control_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"table-read selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
