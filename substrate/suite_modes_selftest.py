#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_modes` — the three states, and the boundary each read names.

⚑⚑⚑ THE LOAD-BEARING ARM IS THAT THE UNDECLARED COUNT REACHES THE OUTPUT. A mode listing only
disagreements cannot distinguish "everything is consistent" from "nothing is declared", and a
false ZERO gets banked while a false positive gets investigated. These modes report their OWN
boundary in the text a reader sees at the terminal — not in a docstring nobody opens.

⚑ THE COUNTS ARE DERIVED, NEVER TYPED. A figure restated beside the code that derives it is the
drift this repo has measured across four files, one of them the gate that ENFORCED the value it
misquoted — so the arms check that the printed number tracks the population it describes.

⚑ AND THE STRAY ARM IS THE FINDING DIRECTION. A declaration naming a tool discovery did not
find means the tool was renamed, deleted, or lost its dispatch: a claim about a file that is not
there, which a census must SURFACE rather than drop.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import suite_declared, suite_modes

# ⚑ THE SELF-INCLUSION EXEMPLAR IS A FIXTURE, NOT A LIVE ENTRY. The arm that uses it
# below records why: naming a real declaration made this case's subject depend on that
# declaration staying as it was, and the one it named turned out to be a fossil.
_FANOUT_TABLE: dict[str, suite_declared.Declared] = {
    suite_declared.ROSTER_KEY: suite_declared.Declared(runs_roster=True, why="the roster itself"),
    "scratch/fixture_fanout.py": suite_declared.Declared(
        runs_roster=True, why="a fixture that declares it runs the roster"
    ),
}


def _suites(names: list[str]) -> list[tuple[str, str]]:
    """Build a roster of `(label, path)` from bare labels."""
    return [(name, name) for name in names]


def _joined(lines: list[str]) -> str:
    """Render a mode's lines as one blob, the way a reader sees them."""
    return "\n".join(lines)


def the_undeclared_population_is_reported(out: list[str]) -> int:
    """Check a tool nobody has assessed is COUNTED, not omitted.

    ⚑ A MODE LISTING ONLY DISAGREEMENTS cannot tell "all consistent" from "nothing declared".
    """
    bad = 0
    text = _joined(suite_modes.declaration_lines(_suites(["nobody/looked.py"])))
    if "UNDECLARED" not in text:
        bad += 1
        out.append(f"selftest: an unassessed tool produced no UNDECLARED line — {text!r}")
    return bad


def the_undeclared_count_tracks_the_population(out: list[str]) -> int:
    """Check the printed count is DERIVED from the roster rather than restated."""
    bad = 0
    labels = ["a/one.py", "a/two.py", "a/three.py"]
    text = _joined(suite_modes.declaration_lines(_suites(labels)))
    if f"{len(labels)} UNDECLARED" not in text:
        bad += 1
        out.append(f"selftest: three unassessed tools did not report 3 UNDECLARED — {text!r}")
    return bad


def a_declared_tool_is_named_as_settled(out: list[str]) -> int:
    """Check a tool the roster declares is reported as ok rather than as undeclared."""
    bad = 0
    text = _joined(suite_modes.declaration_lines(_suites([suite_declared.ROSTER_KEY])))
    if f"  ok         {suite_declared.ROSTER_KEY}" not in text:
        bad += 1
        out.append(f"selftest: the declared roster key did not read as settled — {text!r}")
    return bad


def a_declaration_for_an_absent_tool_is_a_finding(out: list[str]) -> int:
    """Check a declaration naming a tool discovery did not find is SURFACED.

    ⚑ THE STALE-RULING SHAPE: a claim about a file that is not there.
    """
    bad = 0
    text = _joined(suite_modes.declaration_lines(_suites(["nothing/declared.py"])))
    if "FINDING" not in text:
        bad += 1
        out.append(f"selftest: the declared roster's absent tools produced no FINDING — {text!r}")
    return bad


def the_self_including_edge_is_named(out: list[str]) -> int:
    """Check a tool declaring it runs the roster is named STATICALLY.

    ⚑ THIS IS THE HALF A PROCESS-TREE WALK CANNOT BE: it refuses at commit time, before a
    generation has forked.

    ⚑⚑ THE EXEMPLAR IS A FIXTURE AND THE ASSERTION IS UNCONDITIONAL — both changed here,
    and the second matters more. This arm named `scripts/worklist_gate.py`, a live entry,
    and guarded itself with `if including and …`: so on the day that declaration was
    corrected (it was a fossil — the invocation had been replaced by a ppid guard) the
    arm would have gone VACUOUS, passing while asserting nothing. A case whose subject is
    supplied by the data it tests can stop testing without ever going red.
    """
    bad = 0
    labels = [suite_declared.ROSTER_KEY, "scratch/fixture_fanout.py"]
    including = suite_declared.self_including(labels, _FANOUT_TABLE)
    text = _joined(suite_modes.declaration_lines(_suites(labels), _FANOUT_TABLE))
    if not including:
        bad += 1
        out.append("selftest: the fixture declarer was not read as self-including")
    if "SELF-INCLUDING" not in text:
        bad += 1
        out.append(f"selftest: a self-including tool was not named — {text!r}")
    return bad


def the_roster_is_not_reported_against_itself(out: list[str]) -> int:
    """Check the roster tool is excluded from its own self-inclusion check.

    ⚑ RUNNING THE ROSTER IS WHAT IT *IS* — reporting it would be a false finding out of the
    reader built to prevent the fork bomb.
    """
    bad = 0
    if suite_declared.ROSTER_KEY in suite_declared.self_including(
        [suite_declared.ROSTER_KEY], _FANOUT_TABLE
    ):
        bad += 1
        out.append("selftest: the roster was reported as self-including")
    return bad


def _pragma_suite(root: Path, name: str, body: str) -> tuple[str, str]:
    """Write a fixture suite carrying pragmas and return its roster row."""
    path = root / name
    path.write_text(body, encoding="utf-8")
    return (name, str(path))


def a_declared_dependency_is_reported(out: list[str]) -> int:
    """Check a suite naming a package it needs is listed."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _pragma_suite(Path(tmp), "needs.py", "# selftest-requires: numpy\nx = 1\n")
        text = _joined(suite_modes.pragma_lines([row]))
        if "requires" not in text or "numpy" not in text:
            bad += 1
            out.append(f"selftest: a declared dependency was not reported — {text!r}")
    return bad


def a_declared_tenant_is_reported(out: list[str]) -> int:
    """Check a suite naming the store it wants is listed."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _pragma_suite(Path(tmp), "tenant.py", "# selftest-tenant: sandbox\nx = 1\n")
        text = _joined(suite_modes.pragma_lines([row]))
        if "tenant" not in text or "sandbox" not in text:
            bad += 1
            out.append(f"selftest: a declared tenant was not reported — {text!r}")
    return bad


def the_silent_majority_is_named_as_unread(out: list[str]) -> int:
    """Check a suite declaring NEITHER pragma is reported as unasked, not as clean.

    ⚑ "NEEDS NOTHING" AND "NEVER ASKED" ARE DIFFERENT, and this mode can only see the second.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _pragma_suite(Path(tmp), "quiet.py", "x = 1\n")
        text = _joined(suite_modes.pragma_lines([row]))
        if "NEITHER" not in text or "never asked" not in text:
            bad += 1
            out.append(f"selftest: a pragma-less suite was not named as unread — {text!r}")
    return bad


def an_empty_roster_still_states_its_boundary(out: list[str]) -> int:
    """Check both reads name their boundary even over no suites.

    ⚑ AN EMPTY POPULATION IS WHERE A CENSUS MOST LOOKS CLEAN, so it is where the boundary
    statement matters most.
    """
    bad = 0
    for name, lines in (
        ("declarations", suite_modes.declaration_lines([])),
        ("pragmas", suite_modes.pragma_lines([])),
    ):
        if "⚑" not in _joined(lines):
            bad += 1
            out.append(f"selftest: the {name} read over an empty roster stated no boundary")
    return bad


_ARMS = (
    the_undeclared_population_is_reported,
    the_undeclared_count_tracks_the_population,
    a_declared_tool_is_named_as_settled,
    a_declaration_for_an_absent_tool_is_a_finding,
    the_self_including_edge_is_named,
    the_roster_is_not_reported_against_itself,
    a_declared_dependency_is_reported,
    a_declared_tenant_is_reported,
    the_silent_majority_is_named_as_unread,
    an_empty_roster_still_states_its_boundary,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-modes selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-modes selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
