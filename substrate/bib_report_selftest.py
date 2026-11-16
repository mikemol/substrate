# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.bib_report` — and the load-bearing one is a zero.

⚑⚑⚑ THE CASE THAT MATTERS ASSERTS TWO ZEROS ARE DIFFERENT. `0 of 84` is a probe that covered 84
entries and found nothing; `0 of 0` is a probe that found nothing because it read nothing. Without
the denominator they print identically, and the second gets banked as a clean bill of health — the
census-green-is-a-fact-about-the-census defect, which is exactly what the origin's `--roundtrip`
comment records paying for.

⚑⚑ SO `total` IS CASED IN BOTH DIRECTIONS, because a predicate that is only ever checked on the
happy path is a predicate whose false branch nothing has run.

⚑ AND THE PLURALISATION CASES ARE NOT PEDANTRY — the origin spells this six times, and one of the
six tests a different boundary because its denominator excludes the entry itself. Six copies is six
chances to be off by one.
"""

from __future__ import annotations

from substrate import bib_report


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the two zeros are distinguishable ────────────────────────────────────
    # ⚑⚑⚑ THE WHOLE REASON THIS MODULE EXISTS. Both find nothing; only one of them looked.
    covered = bib_report.Census("orphans", found=0, population=84)
    empty = bib_report.Census("orphans", found=0, population=0)
    check("a zero over a real population is TOTAL", passed=covered.total)
    check("a zero over an EMPTY population is not", passed=not empty.total)
    check("and the two summary lines differ", passed=covered.line() != empty.line())
    check("the covered line names its denominator", passed="84" in covered.line())
    check("and the empty line does not claim coverage", passed="of 0" in empty.line())

    # ⚑ A NON-ZERO FINDING IS NOT TOTAL EITHER — the predicate must not read as "healthy".
    check(
        "a read that found rows is not TOTAL",
        passed=not bib_report.Census("orphans", found=3, population=84).total,
    )

    # ── the summary line's shape ─────────────────────────────────────────────
    check("the line leads with the subject", passed=covered.line().startswith("orphans:"))
    check("and reads `n of m`", passed="0 of 84" in covered.line())

    # ── pluralisation, at both boundaries ────────────────────────────────────
    check("one entry is singular", passed=bib_report.entry_word(1) == "entry")
    check("zero entries is plural", passed=bib_report.entry_word(0) == "entries")
    check("two entries is plural", passed=bib_report.entry_word(2) == "entries")
    check(
        "and the summary line uses it",
        passed=bib_report.Census("x", found=0, population=1).line().endswith("1 entry"),
    )

    # ── elision SAYS it elided ───────────────────────────────────────────────
    # ⚑ A TRUNCATED VALUE THAT DOES NOT SAY SO is a value the reader quotes as complete.
    long = "x" * (bib_report.VALUE_WIDTH + 20)
    check("an over-long value is cut", passed=len(bib_report.elide(long)) < len(long))
    check("and marked as cut", passed=bib_report.elide(long).endswith(bib_report.ELIDED))
    check(
        "a value at the width is untouched",
        passed=bib_report.elide("y" * bib_report.VALUE_WIDTH) == "y" * bib_report.VALUE_WIDTH,
    )
    check(
        "and carries no elision mark",
        passed=not bib_report.elide("short").endswith(bib_report.ELIDED),
    )

    # ── the row shapes ───────────────────────────────────────────────────────
    got = bib_report.rows([("K", "a claim")])
    check(
        "a row is indented and aligned",
        passed=got[0].startswith("  K" + " " * (bib_report.KEY_WIDTH - 1)),
    )
    check("and carries the value", passed=got[0].endswith("a claim"))
    check(
        "a long value is elided in the row",
        passed=bib_report.rows([("K", long)])[0].endswith(bib_report.ELIDED),
    )

    edges = bib_report.edge_rows([("from", "A", "B")])
    check("an edge row shows the direction", passed="->" in edges[0])
    check("and names both ends", passed="A" in edges[0] and "B" in edges[0])

    # ⚑ AN ORPHAN ROW IS SHAPED LIKE AN EDGE ROW, so its suffix is the only thing saying what is
    # wrong with it. Without that, a reader must infer the failure from the mode name.
    dangling = bib_report.dangling_rows([("from", "A", "GONE")])
    check("a dangling row says why it is listed", passed="no such entry" in dangling[0])
    check(
        "and is marked distinctly from a healthy edge",
        passed="⚠" in dangling[0] and "⚠" not in edges[0],
    )

    # ── empty inputs produce no rows, not a blank line ───────────────────────
    check("no pairs gives no rows", passed=bib_report.rows([]) == ())
    check("no edges gives no rows", passed=bib_report.edge_rows([]) == ())

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-report selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
