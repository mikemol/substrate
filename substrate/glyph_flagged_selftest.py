# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.glyph_flagged` — over a REAL checker report, not an invented one.

⚑⚑⚑ THE LIVE ARM RUNS THE CHECKER AND READS ITS ACTUAL OUTPUT. A fixture of my own devising
proves the regex handles messages I wrote; only the real report proves it handles the ones ruff
emits, and the whole point of this module is that the escape set must be the checker's rather
than mine.

⚑⚑⚑ AND THE SUBJECT IT READS IS PLANTED, BECAUSE A BORROWED ONE GETS PAID DOWN (gate-G377). This
arm used to run the checker over `scripts/worklist.py`, a tree file that carried ambiguous glyphs
— and it went red when that file was CLEANED. Both live arms failed together, correctly: an empty
report flags nothing, and the iota control that exists to catch an empty-set reader cannot fire
against an empty report either. The suite had been measuring the tree's tidiness rather than its
own reader, and the failure was tree hygiene reported as a regression.

⚑⚑ WHAT IS SYNTHETIC IS THE SUBJECT, NOT THE REPORT, AND THAT IS THE WHOLE DISTINCTION. ruff
still reads the planted file and emits its own RUF001/2/3 rows in its own wording, so the parse
is verified against the emitter exactly as before. What changed is that the arm can no longer be
cleared by someone tidying an unrelated file — it fails only if the reader breaks or the checker's
message shape moves, which are the two things it exists to detect.

⚑⚑⚑ AND THE POSITION SPLIT IS CASED IN ALL THREE DIRECTIONS, because it is the distinction that
decides whether escaping is SAFE. A string finding is escapable, a docstring finding is
escapable, a COMMENT finding is not — a named escape there is literal backslash-N text, and the
round-trip check cannot catch it since both sides decode identically. A reader that collapsed the
three would satisfy every count-based arm while licensing a silent corruption.

⚑⚑ EVERY VERDICT PRINTS ITS COMPONENTS (gate-G204). A case that asserted only a count could not
distinguish an empty finding list from a failed parse — both give zero — so each arm names the
characters, the Unicode names, or the unconfirmed rows it is asserting about.

⚑ THE NAME CROSS-CHECK IS CASED IN BOTH DIRECTIONS. A reader that accepted every row would
satisfy the positive arms while silently escaping the wrong character, so a deliberately
mismatched row is checked to land in `mismatched` rather than in either character set.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

from substrate import corpus
from substrate import glyph_flagged as gf

#: The checker that owns the verdict.
CHECKER = corpus.ROOT / "scripts" / "pycheck_show.py"

#: ⚑ THE PLANTED SUBJECT, CARRYING A KNOWN AMBIGUOUS GLYPH IN A DOCSTRING. The iota is the
#: character the positive control below asserts, so the two are written together — a control whose
#: subject could stop carrying it is the defect this file just paid for. A docstring position is
#: chosen because it is ESCAPABLE, which is what lets the clearable arm mean something.
_PLANTED_SUBJECT = '"""A planted subject: \N{GREEK CAPITAL LETTER IOTA} is ambiguous with I."""\n'

#: One real docstring message, quoted verbatim from a `pycheck_show` run, as the parse fixture.
REAL_ROW = (
    "RUF002 Docstring contains ambiguous `\N{GREEK CAPITAL LETTER IOTA}` "
    "(GREEK CAPITAL LETTER IOTA). Did you mean `I` (LATIN CAPITAL LETTER I)?"
)

#: The same shape as a STRING finding and as a COMMENT finding — the two positions that decide
#: whether a named escape reaches the character at all.
STRING_ROW = (
    "RUF001 String contains ambiguous `\N{DOUBLE-STRUCK CAPITAL Z}` "
    "(DOUBLE-STRUCK CAPITAL Z). Did you mean `Z` (LATIN CAPITAL LETTER Z)?"
)
COMMENT_ROW = (
    "RUF003 Comment contains ambiguous `\N{DIVIDES}` (DIVIDES). "
    "Did you mean `I` (LATIN CAPITAL LETTER I)?"
)


def _parse_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the message parse."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    found = gf.flagged_in(REAL_ROW)
    check(
        f"a docstring message parses as ESCAPABLE — {found.why()}",
        passed=found.escapable == frozenset({"\N{GREEK CAPITAL LETTER IOTA}"}),
    )
    check(
        f"and nothing is unconfirmed ({len(found.mismatched)} row(s))", passed=not found.mismatched
    )

    # ⚑⚑ THE SUGGESTION IS NOT A FLAGGED CHARACTER. The message also names the Latin letter it
    # suggests — parsing that as flagged would escape ordinary ASCII throughout the record.
    check("the suggested replacement is NOT collected", passed="I" not in found.escapable)

    strung = gf.flagged_in(STRING_ROW)
    check(
        f"a string message parses as ESCAPABLE — {strung.why()}",
        passed=strung.escapable == frozenset({"\N{DOUBLE-STRUCK CAPITAL Z}"}),
    )

    # ⚑⚑⚑ THE COMMENT ARM IS THE ONE THAT MATTERS. A named escape in a comment is literal text,
    # so this character must NOT reach the escapable set — and the verdict must say the file is
    # not clearable by escaping alone.
    noted = gf.flagged_in(COMMENT_ROW)
    check(
        f"a comment message is NOT escapable — {noted.why()}",
        passed=not noted.escapable and noted.comment_only == frozenset({"\N{DIVIDES}"}),
    )
    check("and it blocks: escaping alone cannot clear the file", passed=not noted.clearable)

    # ⚑ A CHARACTER IN BOTH POSITIONS LANDS IN BOTH SETS, which is the case a caller must handle:
    # the string occurrences are escapable while the comment ones are not.
    both = gf.flagged_in(STRING_ROW + "\n" + COMMENT_ROW)
    check(
        f"both positions are reported together — {both.why()}",
        passed=bool(both.escapable) and bool(both.comment_only) and not both.clearable,
    )

    # ⚑⚑⚑ THE NAME CROSS-CHECK, DISPROOF SIDE. A row whose printed name does not match the
    # parsed character must land in `mismatched`, or a wrong parse would look like a right one.
    lying = "RUF001 contains ambiguous `\N{DOUBLE-STRUCK CAPITAL Z}` (LATIN CAPITAL LETTER Z)"
    liar = gf.flagged_in(lying)
    check(
        f"a name mismatch is carried, not silently accepted — {liar.why()}",
        passed=not liar.escapable and len(liar.mismatched) == 1,
    )
    check(
        "and the unconfirmed row names both sides",
        passed=liar.mismatched[0][1] == "LATIN CAPITAL LETTER Z",
    )
    check("and an unconfirmed row blocks too", passed=not liar.clearable)

    check("an empty report yields nothing", passed=gf.flagged_in("").escapable == frozenset())
    # ⚑ AND A REPORT WITH NO AMBIGUITY FINDINGS ALSO YIELDS NOTHING — the two are the same
    # answer, which is why the caller must look at the report's own exit rather than at this set.
    check(
        "a report with only line-length findings yields nothing",
        passed=gf.flagged_in("E501 Line too long (102 > 100)").escapable == frozenset(),
    )

    return out


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` over the checker's real output for a PLANTED subject.

    ⚑⚑⚑ THIS IS THE ARM THAT DECIDES THE ESCAPE SET. It runs the checker and reads what it
    actually said, so the set is derived rather than authored — and every component is printed.

    ⚑ THE SUBJECT IS WRITTEN HERE AND REMOVED WITH THE TEMPORARY DIRECTORY, so the arm leaves
    nothing on disk. A suite that leaves an artefact poisons its own next run, and the failure
    signature is a count that moves between identical runs.
    """
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    if not CHECKER.exists():
        return [("the checker is absent, so the live arm is SKIPPED, not passed", True)]

    with tempfile.TemporaryDirectory() as where:
        planted = Path(where) / "glyph_subject.py"
        planted.write_text(_PLANTED_SUBJECT, encoding="utf-8")
        ran = subprocess.run(  # noqa: S603 — a fixed argv, no shell, both operands are our paths
            [sys.executable, str(CHECKER), str(planted)],
            capture_output=True,
            text=True,
            check=False,
            cwd=corpus.ROOT,
        )
    report = ran.stdout + ran.stderr
    check(
        f"the checker produced a report ({len(report)} chars, exit {ran.returncode})",
        passed=bool(report),
    )

    found = gf.flagged_in(report)
    check(f"the live report flags characters — {found.why()}", passed=bool(found.escapable))
    # ⚑ AN UNCONFIRMED ROW BLOCKS: escaping on a set this reader could not confirm would apply
    # the wrong transformation to a record nobody re-reads.
    check(
        f"and every row is name-confirmed ({len(found.mismatched)} unconfirmed)",
        passed=not found.mismatched,
    )

    # ⚑⚑ EVERY ESCAPABLE CHARACTER MUST BE NAMEABLE, or the escape route does not close the
    # findings and the caller needs the other remedy. Asked before any write, never during one.
    unnamed = sorted(c for c in found.escapable if unicodedata.name(c, "") == "")
    check(
        f"every escapable character is nameable ({len(unnamed)} without a name)", passed=not unnamed
    )

    # ⚑ THE POSITIVE CONTROL: a reader that returned the empty set would satisfy a
    # carelessly-written arm, so assert the set actually contains a character known to be in the
    # subject — the Greek iota `_PLANTED_SUBJECT` is written to carry.
    iota = "\N{GREEK CAPITAL LETTER IOTA}"
    check(
        f"and it contains the iota the subject is known to carry ({iota in found.escapable})",
        passed=iota in found.escapable,
    )

    # ⚑⚑ AND THE PLANTED SUBJECT IS CLEARABLE BY CONSTRUCTION, which is now an ASSERTION rather
    # than a report. Against a borrowed subject this was a measurement about the tree — it would
    # go red the day someone wrote a flagged glyph into a comment, which is information and not a
    # regression. Against a subject this file writes, the position is known: one docstring glyph,
    # no comment glyph, so escaping alone must clear it.
    check(
        f"the planted subject is clearable by escaping alone: clearable={found.clearable}, "
        f"{len(found.comment_only)} comment-only",
        passed=found.clearable and not found.comment_only,
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _parse_cases() + _live_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"glyph-flagged selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
