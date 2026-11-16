#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Arms for `substrate.size_budget` — the incident-halved per-file line budget."""

from __future__ import annotations

import sys

from substrate.size_budget import (
    INCIDENT_HALVINGS,
    OVERLARGE_LINES,
    budget_for,
    entrypoint_finding,
    explain,
    incidents_for,
)

#: A file with no recorded incident, used to pin the unhalved branch.
_CLEAN = "scratch/some_untouched_tool.py"
#: A file with two recorded incidents — the deepest halving in the table.
_TWICE = "jea/metalanguage/schema.py"


def a_file_with_no_incidents_keeps_the_corpus_budget(out: list[str]) -> int:
    """⚑ The default branch must be the declared threshold, not a silently-derived one."""
    cap, hits = budget_for(_CLEAN)
    if (cap, hits) != (OVERLARGE_LINES, 0):
        out.append(f"expected ({OVERLARGE_LINES}, 0) for a clean file, got ({cap}, {hits})")
        return 1
    return 0


def each_recorded_incident_halves_the_budget(out: list[str]) -> int:
    """⚑ POSITIVE CONTROL that the ratchet actually bites, per its recorded count."""
    cap, hits = budget_for(_TWICE)
    expected = OVERLARGE_LINES >> INCIDENT_HALVINGS[_TWICE]
    if hits != INCIDENT_HALVINGS[_TWICE] or cap != expected:
        out.append(
            f"{_TWICE}: expected cap {expected} at {INCIDENT_HALVINGS[_TWICE]} incident(s),"
            f" got cap {cap} at {hits}"
        )
        return 1
    if cap >= OVERLARGE_LINES:
        out.append(f"a halved budget ({cap}) is not below the corpus one ({OVERLARGE_LINES})")
        return 1
    return 0


def a_key_matches_on_the_relative_suffix_not_an_absolute_path(out: list[str]) -> int:
    """⚑ A RATCHET THAT QUIETLY STOPS RATCHETING IS WORSE THAN NONE — the number still prints.

    The census runs from several working directories; if only an exact relative key matched,
    every absolute-path caller would silently get the unhalved budget.
    """
    absolute = "/home/someone/checkout/" + _TWICE
    if incidents_for(absolute) != INCIDENT_HALVINGS[_TWICE]:
        out.append(f"an absolute path did not match its key: {absolute}")
        return 1
    return 0


def a_suffix_match_does_not_fire_on_a_partial_segment(out: list[str]) -> int:
    """⚑ `…/not_schema.py` must not inherit `schema.py`'s halving.

    Matching a bare string suffix rather than a path-boundary one would tighten the budget of
    an unrelated file, and an unexplained cap is the finding a reader dismisses.
    """
    if incidents_for("jea/metalanguage/not_schema.py") != 0:
        out.append("a partial-segment path inherited an unrelated file's incident count")
        return 1
    return 0


def a_file_under_budget_gets_no_explanation(out: list[str]) -> int:
    """⚑ An explanation for a passing file would make every file look like a finding."""
    if explain(_CLEAN, 10) != "":
        out.append(f"a 10-line file was explained as over budget: {explain(_CLEAN, 10)!r}")
        return 1
    return 0


def an_over_budget_explanation_names_the_halving(out: list[str]) -> int:
    """⚑ "over cap" reads as a fact about SIZE; this one is about size AND history.

    A reader who cannot see the halving compares the count to the corpus number and concludes
    the census is broken rather than that the file has a record.
    """
    cap, _hits = budget_for(_TWICE)
    why = explain(_TWICE, cap + 1)
    if not why:
        out.append("a file one line over its halved budget was not reported")
        return 1
    if "halved" not in why or str(cap) not in why:
        out.append(f"the explanation does not name the halved budget: {why!r}")
        return 1
    return 0


def a_second_main_guard_is_reported_at_any_size(out: list[str]) -> int:
    """⚑ THE MEASURED INCIDENT: a second guard after a `sys.exit` is dead code that looks live.

    It must not be folded into the line threshold, or it hides in exactly the large files where
    it already hid once.
    """
    if entrypoint_finding([1245]) != "":
        out.append("a single __main__ guard was reported as a defect")
        return 1
    got = entrypoint_finding([1245, 2820])
    if "1245" not in got or "2820" not in got:
        out.append(f"the finding does not name both guard sites: {got!r}")
        return 1
    return 0


_ARMS = (
    a_file_with_no_incidents_keeps_the_corpus_budget,
    each_recorded_incident_halves_the_budget,
    a_key_matches_on_the_relative_suffix_not_an_absolute_path,
    a_suffix_match_does_not_fire_on_a_partial_segment,
    a_file_under_budget_gets_no_explanation,
    an_over_budget_explanation_names_the_halving,
    a_second_main_guard_is_reported_at_any_size,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 1 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"size-budget selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"size-budget selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
