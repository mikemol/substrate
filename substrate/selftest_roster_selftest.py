#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the roster comparison, DIFFERENTIALLY, and pin that UNDECLARED is not a failure.

⚑⚑⚑ THE FOUR DISAGREEMENT CLASSES EACH GET A CASE, AND SO DOES AGREEMENT. A suite asserting
only that disagreements are caught cannot tell a working reader from one that fails everything
— and this reader's whole value is that its verdicts are distinguishable from each other.

⚑⚑ `undeclared` IS ASSERTED AS ITS OWN OUTCOME, twice: it must appear in the rows, and it must
NOT appear among the failures. A row-set listing only disagreements cannot distinguish *every
tool is consistent* from *nothing is declared yet*, so hiding it would let an all-undeclared
roster read clean while counting it would inflate the defect count with paydown.

⚑ AND THE UNION IS ASSERTED FROM BOTH SIDES. Walking only declarations misses a discovered
tool nobody declared; walking only discovery misses a declaration the runner cannot reach.
Each is invisible from the other side, so a fixture exercising one direction proves nothing
about the other.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import selftest_decl, selftest_roster

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / "scripts" / "climode.py"

Case = tuple[str, bool]


class _Origin(Protocol):
    """The origin surface this differential reads — named so a typo cannot pass."""

    def Selftest(self, **kwargs: object) -> object: ...  # noqa: N802 — origin's spelling

    def selftest_rows(
        self,
        declared: dict[str, object],
        discovered: list[str],
    ) -> list[tuple[str, str, bool | None, str]]: ...


def _origin() -> _Origin | None:
    """Load the origin by path, or return None when it cannot be reached."""
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_climode_roster", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _declared() -> dict[str, selftest_decl.Selftest]:
    """Build a roster covering agreement plus every disagreement class."""
    return {
        "agrees.py": selftest_decl.Selftest(),
        "unreachable.py": selftest_decl.Selftest(),
        "says-none.py": selftest_decl.Selftest(state="none", why="a pure data module"),
        "a-fixture.py": selftest_decl.Selftest(state="fixture"),
        "self-contradicting.py": selftest_decl.Selftest(state="none"),
        "absent-both.py": selftest_decl.Selftest(state="none", why="nothing to run"),
    }


# ⚑ `unreachable.py` IS DECLARED AND NOT HERE; `says-none.py` AND `a-fixture.py` ARE HERE AND
#   SHOULD NOT BE; `stranger.py` IS HERE AND DECLARED NOWHERE. One fixture, four classes.
_DISCOVERED = ["agrees.py", "says-none.py", "a-fixture.py", "stranger.py"]


def _by_tool(found: list[selftest_roster.Row]) -> dict[str, selftest_roster.Row]:
    """Index rows by tool — safe here because this reader emits exactly one row each."""
    return {row.tool: row for row in found}


def _agreement_cases() -> list[Case]:
    """Return the cases pinning that a consistent declaration passes."""
    rows = _by_tool(selftest_roster.rows(_declared(), _DISCOVERED))
    return [
        # ⚑ THE ACCEPT DIRECTION FIRST — without it a reader that failed everything would
        #   satisfy every disagreement case below.
        ("a declared suite that discovery reached AGREES", rows["agrees.py"].ok is True),
        ("...carrying no complaint", rows["agrees.py"].why == ""),
        ("a declared absence nobody discovered also agrees", rows["absent-both.py"].ok is True),
    ]


def _disagreement_cases() -> list[Case]:
    """Return the cases pinning each of the four disagreement classes separately."""
    rows = _by_tool(selftest_roster.rows(_declared(), _DISCOVERED))
    return [
        ("a declared suite discovery cannot reach FAILS", rows["unreachable.py"].ok is False),
        (
            "...naming the dispatch the runner does not recognise",
            "cannot reach it" in rows["unreachable.py"].why,
        ),
        ("a declared absence that discovery FOUND fails", rows["says-none.py"].ok is False),
        ("...saying the declaration and the tree disagree", "disagree" in rows["says-none.py"].why),
        # ⚑⚑ A FIXTURE IN THE ROSTER MAKES THE GATE RED BY DESIGN — it is a positive control
        #   invoked BY the runner's suite, never a member of the roster it controls for.
        ("a fixture inside the roster fails", rows["a-fixture.py"].ok is False),
        ("...naming it as red by design", "red by design" in rows["a-fixture.py"].why),
        # ⚑ AND A SELF-CONTRADICTING DECLARATION FAILS ON ITS OWN CONTRACT, before any
        #   comparison with the tree — the two checks are independent.
        (
            "a declaration that contradicts itself fails first",
            rows["self-contradicting.py"].ok is False,
        ),
        (
            "...on its own contract rather than on discovery",
            "no `why`" in rows["self-contradicting.py"].why,
        ),
    ]


def _undeclared_cases() -> list[Case]:
    """Return the cases pinning that UNDECLARED is its own outcome, both directions."""
    found = selftest_roster.rows(_declared(), _DISCOVERED)
    rows = _by_tool(found)
    failures = selftest_roster.failing(found)
    gaps = selftest_roster.unmeasured(found)
    failed_tools = {row.tool for row in failures}
    gap_tools = {row.tool for row in gaps}
    return [
        ("a discovered tool nobody declared gets a row", "stranger.py" in rows),
        ("...as UNDECLARED rather than a failure", rows["stranger.py"].ok is None),
        ("...and the predicate says so", rows["stranger.py"].undeclared),
        # ⚑⚑ BOTH DIRECTIONS. Counting it inflates the defect count with paydown; hiding it
        #   lets an all-undeclared roster read clean.
        ("it is NOT among the failures", "stranger.py" not in failed_tools),
        ("...but IS among the unmeasured", "stranger.py" in gap_tools),
        ("the two populations do not overlap", failed_tools.isdisjoint(gap_tools)),
    ]


def _union_cases() -> list[Case]:
    """Return the cases pinning that the walk covers both sides, not one."""
    rows = _by_tool(selftest_roster.rows(_declared(), _DISCOVERED))
    return [
        # ⚑ EACH DIRECTION IS INVISIBLE FROM THE OTHER SIDE, so both must be asserted.
        ("a DECLARED tool absent from discovery appears", "unreachable.py" in rows),
        ("a DISCOVERED tool absent from the declarations appears", "stranger.py" in rows),
        ("every declared tool appears", all(tool in rows for tool in _declared())),
        ("every discovered tool appears", all(tool in rows for tool in _DISCOVERED)),
    ]


def _differential_cases() -> list[Case]:
    """Compare the promoted reader with the origin's over the same roster.

    ⚑⚑⚑ THE VERDICTS ARE COMPARED, NOT THE WORDING. A promotion owes agreement on what each
    tool's state IS; the messages are rewritten prose and pinning them would make any
    rewording read as a behaviour change.
    """
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    mine = {row.tool: (row.state, row.ok) for row in selftest_roster.rows(_declared(), _DISCOVERED)}
    theirs_decl = {
        "agrees.py": origin.Selftest(),
        "unreachable.py": origin.Selftest(),
        "says-none.py": origin.Selftest(state="none", why="a pure data module"),
        "a-fixture.py": origin.Selftest(state="fixture"),
        "self-contradicting.py": origin.Selftest(state="none"),
        "absent-both.py": origin.Selftest(state="none", why="nothing to run"),
    }
    theirs = {
        tool: (state, ok)
        for tool, state, ok, _why in origin.selftest_rows(theirs_decl, _DISCOVERED)
    }
    return [
        ("the origin loaded, so this differential means something", True),
        ("every tool's STATE and VERDICT agree with the origin", mine == theirs),
        # ⚑ AND THE POPULATIONS MATCH, so an extra or missing row would not hide behind a
        #   per-tool comparison over the intersection.
        ("the row populations are identical", set(mine) == set(theirs)),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (
        _agreement_cases()
        + _disagreement_cases()
        + _undeclared_cases()
        + _union_cases()
        + _differential_cases()
    )
    bad = [label for label, holds in cases if not holds]
    print(f"selftest_roster: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
