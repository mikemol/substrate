#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the kind machinery, and pin it DIFFERENTIALLY against the origin it drains.

⚑⚑⚑ A DRAIN THAT QUIETLY CHANGES ONE BEHAVIOUR IS A REWRITE WEARING A REFACTOR'S CLOTHES.
Every other case here asserts what I believe the behaviour should be; the differential cases
assert it is **the origin's**, which is a different claim and the one a replacement owes. The
origin stays in place and both implementations run over the same inputs.

⚑⚑ THE ORIGIN IS LOADED BY PATH AND READ THROUGH A `Protocol`, AND BOTH CHOICES ARE FORCED.
`.claude/agents/findings.py` is not on any import path and is not a package member, so an
ordinary import cannot reach it. And a dynamically loaded module is `Any`, so every read off
it type-checks against nothing: a misspelled attribute passes, and **a differential that
agrees with anything is worthless.** mypy refused the untyped form and naming the shape is the
repair — the same one the `climode` promotion needed, for the same reason.

⚑ AND THE THIRD OUTCOME IS CASED IN BOTH DIRECTIONS. UNRUNNABLE must never be CLOSED or OPEN,
because an absent instrument is not evidence — a case asserting only that a good command
passes would hold against a reader that scored every failure as success.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import finding_kinds

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / ".claude" / "agents" / "findings.py"

Case = tuple[str, bool]


class _Origin(Protocol):
    """The two origin readers this differential compares against.

    ⚑ NAMING THE SHAPE IS WHAT MAKES THE DIFFERENTIAL MEAN ANYTHING. Under a bare dynamic
    import both names are `Any`, so a typo compares two things that were never computed and
    the suite goes green on nothing. This also makes the differential's REACH explicit: two
    functions, and the rest of the origin is out of scope by declaration.
    """

    def _failing_case(self, out: str) -> str: ...

    def _evidence(self, out: str) -> str: ...


# A suite tail in the house shape: per-case FAIL lines, then the score LAST.
_HOUSE_TAIL = """
running the thing
FAIL a_case_that_broke: got 3 != want 4
FAIL a_second_case: got 1 != want 2
somesuite: 18/20
"""

# A refusal whose announcing line is NOT last — the shape `tail[-1]` got wrong.
_REFUSAL_TAIL = """
store.tenant: refusing an unstated tenant — pass --sandbox or --live
pass --dry-run to see WHOSE backend that PID currently is
"""

# ⚑ THE PROBE SET DELIBERATELY INCLUDES THE EMPTY AND SCORE-ONLY SHAPES, which are the
#   branches a happy-path differential never reaches.
_PROBES = (_HOUSE_TAIL, _REFUSAL_TAIL, "", "one line only\n", "somesuite: 4/4\n")


def _origin() -> _Origin | None:
    """Load the origin by path, or return None when it cannot be reached.

    ⚑ A MISSING ORIGIN IS REPORTED, NEVER SILENTLY SKIPPED. A differential that vanishes when
    its counterparty is absent is a suite whose green says nothing.
    """
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_findings", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _cannot_run_cases() -> list[Case]:
    """Return the cases pinning that an unrunnable command is UNRUNNABLE, never a verdict.

    ⚑⚑ THIS IS THE PROPERTY THE WHOLE LEDGER RESTS ON, and it binds hardest on `refuses`: a
    DELETED command exits non-zero for the wrong reason, so a reader keying on "non-zero means
    the refusal is installed" would score an absent instrument as a passing witness.
    """
    gone = ["python3", str(ROOT / "no_such_module_at_all.py")]
    absent = ["/nonexistent/binary/entirely"]
    st_code, _ = finding_kinds.selftest(absent, "n/a")
    rf_code, rf_note = finding_kinds.refuses(absent, "n/a")
    ran_and_failed, _ = finding_kinds.refuses(gone, "n/a")
    return [
        ("an unstartable command is UNRUNNABLE under selftest",
         st_code == finding_kinds.UNRUNNABLE),
        # ⚑ THE LOAD-BEARING ONE: not CLOSED, which "non-zero means refusing" would give.
        ("an unstartable command is UNRUNNABLE under refuses, NOT closed",
         rf_code == finding_kinds.UNRUNNABLE),
        ("...and the note says it did not run", "did not run" in rf_note),
        # ⚑ AND A COMMAND THAT *RAN* AND FAILED IS A GENUINE REFUSAL — the other direction,
        #   without which the case above holds for a reader returning UNRUNNABLE always.
        ("a command that RAN and exited non-zero IS a refusal",
         ran_and_failed == finding_kinds.CLOSED),
    ]


def _polarity_cases() -> list[Case]:
    """Return the cases pinning that the two behavioural kinds are exact duals."""
    ok = ["python3", "-c", "pass"]
    bad = ["python3", "-c", "raise SystemExit(3)"]
    return [
        ("selftest CLOSES on exit 0",
         finding_kinds.selftest(ok, "x")[0] == finding_kinds.CLOSED),
        ("selftest OPENS on non-zero",
         finding_kinds.selftest(bad, "x")[0] == finding_kinds.OPEN),
        ("refuses CLOSES on non-zero",
         finding_kinds.refuses(bad, "x")[0] == finding_kinds.CLOSED),
        # ⚑⚑ THE INVERSION IS THE POINT: a refusal that exits 0 is GONE, not passing.
        ("refuses OPENS on exit 0 — the refusal is GONE",
         finding_kinds.refuses(ok, "x")[0] == finding_kinds.OPEN),
        ("...and says so in words a reader can act on",
         "GONE" in finding_kinds.refuses(ok, "x")[1]),
    ]


def _vacuity_cases() -> list[Case]:
    """Return the cases pinning the two non-behavioural kinds and their honesty."""
    return [
        ("standing always holds",
         finding_kinds.standing("a fact")[0] == finding_kinds.CLOSED),
        ("unwitnessed is ALWAYS unrunnable, never closed",
         finding_kinds.unwitnessed("a gap")[0] == finding_kinds.UNRUNNABLE),
        # ⚑ THE KIND MUST BE LEGIBLE IN THE MESSAGE, since a reader scanning a roster sees
        #   the text and not the code.
        ("standing names itself", "STANDING" in finding_kinds.standing("a fact")[1]),
        ("unwitnessed names itself", "UNWITNESSED" in finding_kinds.unwitnessed("g")[1]),
    ]


def _citation_cases() -> list[Case]:
    """Return the cases pinning that the citation readers quote the RIGHT line.

    ⚑ BOTH WERE `tail[-1]` AND BOTH WERE WRONG FOR OPPOSITE REASONS. A house suite ends with
    its SCORE, so the failing case is never last; a refusing command routinely ends with a
    help hint. Asserting the correct line is chosen is the whole repair.
    """
    case = finding_kinds.failing_case(_HOUSE_TAIL)
    refusal = finding_kinds.evidence(_REFUSAL_TAIL)
    return [
        ("the FAIL line is quoted, not the score", "a_case_that_broke" in case),
        ("...and the score is carried ALONGSIDE, since only it says how many",
         "18/20" in case),
        ("...and further failures are counted rather than dropped", "more" in case),
        # ⚑ THE REFUSAL LINE IS FIRST HERE AND THE HINT IS LAST — the measured shape.
        ("the announcing line is quoted, not the trailing hint", "refusing" in refusal),
        ("...and the incidental last line is NOT what got quoted",
         "--dry-run" not in refusal),
        # ⚑⚑ A MISS IS FLAGGED, NEVER SILENTLY PASSED OFF AS THE GUARD SPEAKING.
        ("a tail with no refusal word says so",
         "no refusal line found" in finding_kinds.evidence("just some chatter\n")),
        ("an empty read is a fact about the OUTPUT",
         "exit code is the whole evidence" in finding_kinds.evidence("")),
        # ⚑ AND A SCORE WITH NO FAIL LINE ADMITS THE GAP rather than pretending to cite.
        ("a score with no FAIL line admits the gap",
         "NO `FAIL <case>` line" in finding_kinds.failing_case("somesuite: 4/9\n")),
    ]


def _differential_cases() -> list[Case]:
    """Run the ORIGIN's readers beside the module's over the same inputs.

    ⚑⚑⚑ THIS IS WHAT A DRAIN OWES. A module that agrees with its own fixtures and disagrees
    with the tool it replaces has not been verified — the citation readers are pure functions
    of a string, so agreement is checkable by a program rather than by my reading of them.
    """
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    same_case = all(
        origin._failing_case(p) == finding_kinds.failing_case(p)  # noqa: SLF001
        for p in _PROBES)
    same_ev = all(
        origin._evidence(p) == finding_kinds.evidence(p)  # noqa: SLF001
        for p in _PROBES)
    return [
        ("the origin loaded, so this differential means something", True),
        ("failing_case agrees with the origin on every probe", same_case),
        ("evidence agrees with the origin on every probe", same_ev),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (_cannot_run_cases() + _polarity_cases() + _vacuity_cases()
             + _citation_cases() + _differential_cases())
    bad = [label for label, holds in cases if not holds]
    print(f"finding_kinds: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
