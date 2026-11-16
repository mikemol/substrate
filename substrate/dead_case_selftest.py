#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the dead-case reader against fixtures and against the live suites.

⚑⚑⚑ THE LOAD-BEARING CASE IS THE ONE THAT WAS FOUND BY HAND THREE TIMES. A `_live_cases` arm
that early-returns on an absent fixture and then opens its success list with
`("<fixture> is present", True)` carries a row that cannot fail. The fixture below is that exact
shape, transcribed rather than invented, and the reader must call its second row dead.

⚑⚑ AND THE NEGATIVE CONTROL IS WHERE THIS READER FAILS MOST CHEAPLY. A classifier that called
every case dead would satisfy every positive row above and be worthless. A live case — one whose
truth value is a CALL or a COMPARISON — is asserted NOT dead, and an early-return row (a genuine
`(prose, False)`) is asserted dead too, because a literal `False` is equally uninfluenced by the
module under test.

⚑ THE LIVE ARM READS THIS TREE'S OWN SUITES, so a green here is a claim about the population the
census reports rather than about a fixture agreeing with itself. It asserts the reader SEES cases
at all — a walk that found nothing would report zero dead and read as clean.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import dead_case

ROOT = Path(__file__).resolve().parent.parent

Case = tuple[str, bool]

# ⚑ THE MEASURED SHAPE (gate-G21, gate-G22, gate-G23). Three arms carried this verbatim.
_TEMPLATE = """
def _live_cases():
    probe = ROOT / "thing.py"
    if not probe.is_file():
        return [("thing.py is present to read", False)]
    got = read(probe)
    return [
        ("thing.py is present to read", True),
        ("the thing resolves", got is not None),
    ]
"""

_LIVE_ONLY = """
def _cases():
    return [
        ("the thing resolves", got is not None),
        ("the count matches", len(rows) == 3),
        ("the render names it", "UNDECIDED" in out),
    ]
"""

_UNDECIDED = """
def _cases():
    return [
        ("a bare name cannot be decided here", holds),
    ]
"""

_NOT_A_CASE = """
def _cases():
    wide = [("a", "b", "c")]
    return [("the real one", x == 1)]
"""

# ⚑ THE FALSE POSITIVE THE FIRST CENSUS PRODUCED, transcribed from `chirality_selftest.py`.
# A pair of bib FIELD NAMES matches the case arity exactly, and the first cut called it dead.
_FIELD_PAIR = """
def a_declared_mate_is_not_re_derived():
    edges = [("rests-on", "from"), ("from", "rests-on")]
    return [("the mate is not re-derived", got == want)]
"""

_BROKEN = "def _cases(:\n"

_TWO = 2
_THREE = 3


def _template_cases() -> list[Case]:
    """Return the cases pinning the measured template shape."""
    found = dead_case.read_source(_TEMPLATE, "fixture.py")
    bad = dead_case.dead(found)
    return [
        ("the template's three rows are all read", len(found) == _THREE),
        # ⚑ THE MEASURED ROW. Two literals: the early-return False and the success-path True.
        ("both literal rows are called dead", len(bad) == _TWO),
        (
            "the success-path presence row is dead",
            any(c.prose == "thing.py is present to read" and c.dead for c in bad),
        ),
        # ⚑ A LITERAL `False` IS EQUALLY DEAD. It cannot fail for a reason connected to the
        #   module under test either — it fails unconditionally, which is a different defect
        #   and the same classification.
        (
            "the early-return row is dead too",
            sum(1 for c in bad if c.prose == "thing.py is present to read") == _TWO,
        ),
        ("the resolving row is NOT dead", all(c.prose != "the thing resolves" for c in bad)),
        (
            "the arm is named, so a finding can be located",
            all(c.func == "_live_cases" for c in found),
        ),
    ]


def _live_shape_cases() -> list[Case]:
    """Return the negative control: a suite of genuine cases has no dead rows."""
    found = dead_case.read_source(_LIVE_ONLY, "fixture.py")
    return [
        ("three live cases are read", len(found) == _THREE),
        # ⚑ WITHOUT THIS, A CLASSIFIER RETURNING `dead` FOR EVERYTHING PASSES EVERY ROW ABOVE.
        ("no live case is called dead", len(dead_case.dead(found)) == 0),
        ("no live case is undecided", all(not c.undecided for c in found)),
    ]


def _undecided_cases() -> list[Case]:
    """Return the cases pinning that a bare name is UNDECIDED, not cleared."""
    found = dead_case.read_source(_UNDECIDED, "fixture.py")
    return [
        ("the bare-name case is read", len(found) == 1),
        # ⚑ A FACT ABOUT THIS READER. Deciding it needs the binding traced, and nothing here
        #   traces bindings — so it must not be reported as live.
        ("a bare name is UNDECIDED", found[0].undecided),
        ("an undecided case is not dead", not found[0].dead),
    ]


def _shape_cases() -> list[Case]:
    """Return the cases pinning what does NOT count as a case tuple."""
    found = dead_case.read_source(_NOT_A_CASE, "fixture.py")
    broken = dead_case.read_source(_BROKEN, "fixture.py")
    pairs = dead_case.read_source(_FIELD_PAIR, "fixture.py")
    return [
        ("a three-element tuple is not a case", len(found) == 1),
        ("the real case is read", found[0].prose == "the real one"),
        ("the real case is live", not found[0].dead),
        # ⚑⚑ THE MEASURED FALSE POSITIVE. Two (str, str) field-name pairs sit beside one real
        #   case; the first cut read all three and called two of them dead. The narrowing is
        #   what makes the reported population a defect count rather than an arity count.
        ("a (str, str) pair is refused, not counted", len(pairs) == 1),
        ("the one real case beside it survives", pairs[0].prose == "the mate is not re-derived"),
        ("and it is live", not pairs[0].dead),
        # ⚑ AND IT MUST NOT BE LAUNDERED INTO THE HONEST-GAP COLUMN. Reporting a non-case as
        #   UNDECIDED would move the false positive rather than remove it.
        ("a refused pair is not reported UNDECIDED either", not pairs[0].undecided),
        # ⚑ UNPARSEABLE SOURCE READS EMPTY, and the render says an empty read is a fact about
        #   the WALK — so the two halves together keep a crash from banking as clean.
        ("unparseable source reads as no cases", len(broken) == 0),
    ]


def _render_cases() -> list[Case]:
    """Return the cases pinning that the census states what it could not decide."""
    made = (
        dead_case.Case("a.py", "arm", "a real one", "live"),
        dead_case.Case("a.py", "arm", "a literal one", "literal"),
        dead_case.Case("a.py", "arm", "a bare name", "undecided"),
    )
    out = dead_case.render(made)
    empty = dead_case.render(())
    return [
        ("the render names the CANNOT FAIL row", "CANNOT FAIL" in out),
        # ⚑ PRINTED EVEN AT ZERO — a skipped shape is a different fact from a cleared one.
        ("the render names the UNDECIDED row", "UNDECIDED" in out),
        ("the dead case is spelled out", "a literal one" in out),
        ("the undecided case is spelled out", "a bare name" in out),
        ("an empty census is a fact about the WALK", "fact about the WALK" in empty),
    ]


def _live_cases() -> list[Case]:
    """Read this tree's own suites, so the census is about the population it reports."""
    where = ROOT / "substrate"
    if not where.is_dir():
        return [("the promoted package is present to census", False)]
    found = dead_case.census(ROOT)
    suites = {c.suite for c in found}
    return [
        # ⚑ THE WALK MUST FIND CASES. A reader that saw none would report zero dead and read as
        #   a clean bill of health — the shape this module exists to make unrepresentable.
        ("the live census reads cases", len(found) > 0),
        ("it reads them across many suites", len(suites) > 1),
        ("this suite is among them", "dead_case_selftest.py" in suites),
        # Every case carries one of exactly three verdicts; a fourth would silently escape both
        # the dead count and the undecided count.
        (
            "every verdict is one of the three declared",
            all(c.verdict in {"live", "literal", "undecided"} for c in found),
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (
        _template_cases()
        + _live_shape_cases()
        + _undecided_cases()
        + _shape_cases()
        + _render_cases()
        + _live_cases()
    )
    bad = [label for label, holds in cases if not holds]
    print(f"dead_case: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
