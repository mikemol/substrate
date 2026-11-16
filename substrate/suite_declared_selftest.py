#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_declared` — the three states, STRAY, and the cycle edge.

⚑⚑ THE UNDECLARED ARM IS THE ONE THAT KEEPS THIS A CENSUS. A reader that returned only
disagreements could not distinguish "everything is consistent" from "nothing is declared yet",
and the second is the current state — a five-entry seed against a discovered population two
orders larger. A false ZERO gets banked; a false positive gets investigated.

⚑ AND STRAY IS ITS MIRROR. A declaration naming a file nobody discovered means the tool was
renamed, deleted, or lost its dispatch — a claim about something that is not there, which is
exactly the stale-ruling shape a census must surface rather than silently drop.

⚑⚑ THE SELF-INCLUSION ARM GUARDS A MEASURED INCIDENT: six generations, load 54.93, 68
processes on 10 cores, because a suite invoked the roster containing it and no source file
could say so. The runtime ppid walk refuses that only AFTER a generation has forked; this
refuses it from source, at commit time.
"""

from __future__ import annotations

import sys

from substrate import suite_declared

# ⚑⚑ THE CASES OWN THEIR EXEMPLARS RATHER THAN BORROWING LIVE ONES. Two arms below used
# to name `scripts/worklist_gate.py` — a real entry that really did declare
# `runs_roster=True`. When that declaration was found to be a FOSSIL of an edge the code
# had removed, and was corrected, arms testing this READER failed on a change to the
# DATA. A case that goes red when a stale claim is repaired is testing the roster's
# content, not the function; so the exemplars are fixtures with names no tool can own.
_FIXTURE_TABLE: dict[str, suite_declared.Declared] = {
    suite_declared.ROSTER_KEY: suite_declared.Declared(runs_roster=True, why="the roster itself"),
    "scratch/fixture_fanout.py": suite_declared.Declared(
        runs_roster=True, why="a fixture that declares it runs the roster"
    ),
    "scratch/fixture_plain.py": suite_declared.Declared(
        why="a fixture that declares no roster edge"
    ),
    "scratch/fixture_control.py": suite_declared.Declared(
        key="scratch/fixture_control.py", why="a fixture FIXTURE — a positive control"
    ),
}


def three_states(out: list[str]) -> int:
    """Check declared, fixture and undeclared are distinct states."""
    bad = 0
    rows = {
        r.label: r.state
        for r in suite_declared.standings(
            [
                "scratch/fixture_plain.py",  # declared
                "scratch/fixture_control.py",  # a FIXTURE, carried by `key`
                "scratch/nobody_assessed.py",  # undeclared
            ],
            _FIXTURE_TABLE,
        )
    }
    if rows.get("scratch/fixture_plain.py") != "declared":
        out.append(f"selftest: a declared tool is {rows.get('scratch/fixture_plain.py')!r}")
        bad += 1
    if rows.get("scratch/fixture_control.py") != "fixture":
        out.append(
            f"selftest: the fixture is {rows.get('scratch/fixture_control.py')!r}, "
            f"not its own state"
        )
        bad += 1
    if rows.get("scratch/nobody_assessed.py") != "undeclared":
        out.append("selftest: an unassessed tool is not reported as undeclared")
        bad += 1
    return bad


def undeclared_is_reported(out: list[str]) -> int:
    """Check the unassessed population appears in the rows rather than being filtered out."""
    rows = suite_declared.standings(["a.py", "b.py", "c.py"], _FIXTURE_TABLE)
    undeclared = [r for r in rows if r.state == "undeclared"]
    if len(undeclared) != 3:  # noqa: PLR2004 - the three fixtures above
        out.append(f"selftest: undeclared rows were dropped: {rows}")
        return 1
    return 0


def stray_is_surfaced(out: list[str]) -> int:
    """Check a declaration for an undiscovered file is reported, not dropped.

    ⚑ A CLAIM ABOUT A FILE THAT IS NOT THERE. Dropping it would let a declaration outlive its
    subject silently — the same defect as a ruling that outlives its row.
    """
    rows = suite_declared.standings([suite_declared.ROSTER_KEY], _FIXTURE_TABLE)
    strays = [r.label for r in rows if r.state == "STRAY"]
    if "scratch/fixture_fanout.py" not in strays:
        out.append(f"selftest: a declaration for an undiscovered file was dropped: {strays}")
        return 1
    return 0


def self_inclusion_named(out: list[str]) -> int:
    """Check a tool declaring it runs the roster is named — and the roster itself is not.

    ⚑ THE ROSTER RUNNING THE ROSTER IS NOT A CYCLE, IT IS THE TOOL. Excluding it is what keeps
    the check from firing on its own subject every run, which would train a reader to ignore
    it.
    """
    bad = 0
    named = suite_declared.self_including(
        [suite_declared.ROSTER_KEY, "scratch/fixture_fanout.py"], _FIXTURE_TABLE
    )
    if "scratch/fixture_fanout.py" not in named:
        out.append(f"selftest: a self-including tool was not named: {named}")
        bad += 1
    if suite_declared.ROSTER_KEY in named:
        out.append("selftest: the roster itself was reported as self-including")
        bad += 1
    # ⚑ AND AN UNDISCOVERED DECLARER IS NOT NAMED — the check is about what would actually
    # run, so a declaration with no live file cannot fork anything.
    if suite_declared.self_including([suite_declared.ROSTER_KEY], _FIXTURE_TABLE):
        out.append("selftest: a self-including tool that was not discovered was named")
        bad += 1
    return bad


def the_live_table_declares_no_fanout(out: list[str]) -> int:
    """Check no LIVE entry besides the roster declares it runs the roster.

    ⚑⚑⚑ THIS ARM IS THE REPAIR MADE CHECKABLE, AND IT IS AN ASSERTION ABOUT THE DATA —
    deliberately separate from the arms above, which assert about the READER and now use
    fixtures for exactly that reason. `scripts/worklist_gate.py` declared `runs_roster`
    long after its suite stopped invoking the roster: the invocation had been replaced by
    a `ratchet.check_cycle` ppid guard, and two readers went on reporting the fossil.
    Nothing could refuse it, because a declaration states what no walk derives.

    ⚑ SO WHAT IS PINNED IS THE POPULATION, NOT ANY ONE ENTRY. A future tool that
    genuinely runs the roster is a real want and this arm should then be updated
    DELIBERATELY — which is the point: the next such claim has to be argued rather than
    inherited. And a red here is not automatically a bug; it is a claim that has to be
    re-derived from the declaring tool's code before it is believed.
    """
    fanout = [
        label
        for label, d in suite_declared.DECLARED.items()
        if d.runs_roster and label != suite_declared.ROSTER_KEY
    ]
    if fanout:
        out.append(
            f"selftest: an entry declares it runs the roster — re-derive it from "
            f"that tool's code before believing it: {fanout}"
        )
        return 1
    return 0


_ARMS = (
    three_states,
    undeclared_is_reported,
    stray_is_surfaced,
    self_inclusion_named,
    the_live_table_declares_no_fanout,
)

_CASE_COUNT = 3 + 1 + 1 + 3 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-declared selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-declared selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
