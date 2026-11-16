#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `scripts/run_selftests` — the dispatch, and the contracts it must keep.

⚑⚑⚑ THE LOAD-BEARING ARM IS THE KEYWORD ONE, AND IT IS WHY THIS SUITE EXISTS. The monolith this
dispatch replaced died on `may_write(True)` — a boolean passed POSITIONALLY into a parameter
that had become keyword-only. That failure was invisible to every existing case because nothing
could reach the runner's own dispatch: it had no suite, and the file carried too many findings
to grow one. A signature mismatch at a module seam is exactly what a case can pin and a reader
cannot — and it aborted every run AFTER the whole roster had already executed, so the cost of
not catching it was the entire suite's wall time, every time.

⚑⚑ IT IS CHECKED ON THE SIGNATURE, NOT BY MAKING THE BAD CALL. Writing the offending call to
watch it raise is itself the banned shape — a bare boolean positional says nothing about what it
decides — so the arm reads the PARAMETER KIND. That is also the stronger check: it fails when
the parameter merely becomes positional-CAPABLE, before any caller has made the mistake.

⚑⚑ THE FLAG-TABLE ARMS PIN A DRIFT THAT ALREADY HAPPENED. The declared flag set and the mode
dispatch were two lists kept agreeing by hand, and they came apart: a mode dispatched at the
bottom of `main` while missing from the set, so invoking it refused as an unknown flag. Deriving
one from the other makes that unrepresentable — and these arms say so out loud, since a
derivation can always be undone by the next editor. BOTH directions are checked: a census that
only ever tests its positive case cannot tell "correctly empty" from "never populated".

⚑ A THIRD FLAG-TABLE ARM WAS WRITTEN AND DELETED, AND THE DELETION IS THE FINDING. "Every mode
is callable" is UNREACHABLE: the table's declared type already says so, and the checker said the
branch could not run. An arm a type makes unfalsifiable is ceremony — it reads as coverage and
asserts nothing, which is the manufactured-green shape this repo keeps paying for.

⚑ AND THE PATH ARM IS THE RETIREMENT'S OWN PRECONDITION. An importer census reports ZERO import
sites for the runner, which is TRUE and MISLEADING: it is a CLI whose consumers are PATH
LITERALS, including the pre-commit gate that invokes it and the roster that keys on it. If that
path stops answering, those break silently — so the case is on the PATH, not on a name.

⚑ THIS SUITE LIVES BESIDE THE TOOL, NOT UNDER `substrate/`, AND THAT WAS FORCED RATHER THAN
CHOSEN. The typed frontier follows imports, so a case module there naming `scripts.run_selftests`
would pull the whole dispatch into a bar it does not yet meet. The suite belongs with its
subject.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

from scripts import run_selftests
from substrate import corpus, reach_ratchet, suite_declared

# How `inspect` spells a keyword-only parameter, compared as text so this check does not import
# a name whose type carries `Any` into every expression around it.
_KEYWORD_ONLY = "KEYWORD_ONLY"


def the_path_the_consumers_name_is_the_one_that_answers(out: list[str]) -> int:
    """Check the dispatch still lives where every path literal expects it.

    ⚑ THE ROSTER KEYS ON THIS PATH. Half its consumers are string literals, so a rename is
    invisible to an importer census and breaks a pre-commit gate.
    """
    bad = 0
    here = Path(run_selftests.__file__).resolve()
    expected = (corpus.ROOT / suite_declared.ROSTER_KEY).resolve()
    if here != expected:
        out.append(f"selftest: the runner is at {here}, but the roster names {expected}")
        bad += 1
    return bad


def the_flag_set_covers_every_mode(out: list[str]) -> int:
    """Check every dispatched mode is a declared flag.

    ⚑ THE MEASURED DRIFT: a mode dispatched while missing from the declared set refused as an
    unknown flag — a mode running with an arity nobody declared.
    """
    bad = 0
    undeclared = sorted(set(run_selftests.MODES) - run_selftests.KNOWN_FLAGS)
    if undeclared:
        out.append(f"selftest: dispatched but not declared: {undeclared}")
        bad += 1
    return bad


def every_declared_flag_is_a_mode_or_a_modifier(out: list[str]) -> int:
    """Check the flag set holds nothing the tool cannot act on — the other direction."""
    bad = 0
    orphaned = sorted(
        run_selftests.KNOWN_FLAGS - set(run_selftests.MODES) - run_selftests.MODIFIERS
    )
    if orphaned:
        out.append(f"selftest: declared but neither a mode nor a modifier: {orphaned}")
        bad += 1
    return bad


def the_mode_table_is_not_empty(out: list[str]) -> int:
    """Check the dispatch offers modes at all.

    ⚑ AN EMPTY TABLE MAKES BOTH SET ARMS PASS VACUOUSLY. Two green readings over nothing is
    the census-green-is-a-fact-about-the-census shape, so the population needs its own arm.
    """
    bad = 0
    if not run_selftests.MODES:
        out.append("selftest: the mode table is EMPTY — both flag arms pass over nothing")
        bad += 1
    return bad


def _keyword_only(func: object, name: str) -> bool:
    """Report whether `func` takes `name` as a keyword-ONLY parameter."""
    if not callable(func):
        return False
    found = inspect.signature(func).parameters.get(name)
    return found is not None and str(found.kind) == _KEYWORD_ONLY


def the_reach_gate_takes_its_booleans_by_name(out: list[str]) -> int:
    """Check the reach ratchet's booleans are keyword-ONLY.

    ⚑⚑⚑ THIS IS THE CRASH, PINNED. The retired runner passed these positionally, and the
    resulting `TypeError` aborted every run after the whole roster had already executed. A bare
    boolean at a call site says nothing about what it decides, and one of these decides whether
    a gate WRITES a baseline.
    """
    bad = 0
    for name in ("quiet", "write"):
        if not _keyword_only(reach_ratchet.reach_ratchet, name):
            out.append(
                f"selftest: reach_ratchet's `{name}` is not keyword-only — a bare "
                f"positional boolean is exactly the call that retired the old runner"
            )
            bad += 1
    return bad


def discovery_finds_this_suite(out: list[str]) -> int:
    """Check the runner's own discovery reaches this file.

    ⚑ A SUITE DISCOVERY CANNOT SEE IS NOT FAILING — IT IS ABSENT, and a shrinking population
    reads as a smaller green total rather than as a loss.
    """
    bad = 0
    labels = {label for label, _path in run_selftests.discover()}
    mine = str(Path(__file__).resolve().relative_to(corpus.ROOT))
    if mine not in labels:
        out.append(f"selftest: discovery did not reach {mine}")
        bad += 1
    return bad


def discovery_finds_the_roster_itself(out: list[str]) -> int:
    """Check discovery reaches the runner, which the roster declares as its own key."""
    bad = 0
    labels = {label for label, _path in run_selftests.discover()}
    if suite_declared.ROSTER_KEY not in labels:
        out.append(f"selftest: discovery did not reach {suite_declared.ROSTER_KEY}")
        bad += 1
    return bad


def the_roster_is_not_empty(out: list[str]) -> int:
    """Check discovery returns a population at all.

    ⚑ AN EMPTY ROSTER RUNS GREEN. Every count is zero, nothing fails, and the verdict reads
    like a clean tree — which is why the population itself needs an assertion.
    """
    bad = 0
    if not run_selftests.discover():
        out.append("selftest: discovery returned NO suites — an empty roster runs green")
        bad += 1
    return bad


def the_baselines_resolve_inside_the_repo(out: list[str]) -> int:
    """Check both ratchet baselines resolve under the repo, not beside a moved file."""
    bad = 0
    for name, path in (
        ("legacy", run_selftests.LEGACY_BASELINE),
        ("reach", run_selftests.REACH_BASELINE),
    ):
        if not path.is_relative_to(corpus.ROOT):
            out.append(f"selftest: the {name} baseline resolves outside the repo: {path}")
            bad += 1
    return bad


_ARMS = (
    the_path_the_consumers_name_is_the_one_that_answers,
    the_flag_set_covers_every_mode,
    every_declared_flag_is_a_mode_or_a_modifier,
    the_mode_table_is_not_empty,
    the_reach_gate_takes_its_booleans_by_name,
    discovery_finds_this_suite,
    discovery_finds_the_roster_itself,
    the_roster_is_not_empty,
    the_baselines_resolve_inside_the_repo,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"run-selftests selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"run-selftests selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
