#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_marker` — the mark, the stack, and what it must survive.

⚑⚑⚑ THE INHERITANCE CASE IS THE ONE THE GUARD EXISTS FOR. The cycle crosses `subprocess`
boundaries — a suite invokes a roster that contains it — so a module-level flag would guard one
interpreter and let the fan-out proceed. Measured off a live process tree, the unguarded form
reached FOUR GENERATIONS at load 54.93 with 68 concurrent processes.

⚑⚑ AND THE ACCUMULATION IS NOT COSMETIC. A boolean answers the guard and none of the diagnostic
questions; the stack is what tells a reader WHICH suites are nested when a refusal surprises
them, and re-entering the same label twice is recorded twice because that IS the cycle.

⚑ EVERY CASE RESTORES THE ENVIRONMENT. A test that leaves the mark set makes every later test in
the same process read as inside a suite — a fixture leak that would turn the whole run green for
the wrong reason.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from substrate import suite_marker

# The probe a child process runs: import the module and report the mark through its exit code.
# ⚑ THE CHILD IMPORTS THE MODULE ITSELF rather than being told the answer, so this exercises the
# same read a real guarded tool performs.
_PROBE = (
    "import sys; sys.path.insert(0, {root!r}); "
    "from substrate import suite_marker; "
    "sys.exit(0 if suite_marker.in_suite() else 1)"
)

# The repo root, so the child can import the package without an install.
_ROOT = str(Path(__file__).absolute().parent.parent)


def _clear() -> None:
    """Remove the mark, so a case starts outside any suite."""
    os.environ.pop(suite_marker.MARK, None)


def _child_sees_the_mark() -> bool:
    """Run a child process and report whether it read the mark."""
    result = subprocess.run(  # noqa: S603 — argv is this interpreter and a module constant
        [sys.executable, "-c", _PROBE.format(root=_ROOT)], check=False, capture_output=True
    )
    return result.returncode == 0


def an_unmarked_process_is_not_in_a_suite(out: list[str]) -> int:
    """Check the default state is outside."""
    _clear()
    bad = 0
    try:
        if suite_marker.in_suite():
            out.append("selftest: an unmarked process read as inside a suite")
            bad += 1
        if suite_marker.stack():
            out.append(f"selftest: an unmarked process reported {suite_marker.stack()!r}")
            bad += 1
    finally:
        _clear()
    return bad


def entering_marks_the_process(out: list[str]) -> int:
    """Check the mark is set and the label is readable."""
    _clear()
    bad = 0
    try:
        suite_marker.enter_suite("alpha")
        if not suite_marker.in_suite():
            out.append("selftest: entering did not mark the process")
            bad += 1
        if suite_marker.stack() != ("alpha",):
            out.append(f"selftest: the stack read as {suite_marker.stack()!r}")
            bad += 1
    finally:
        _clear()
    return bad


def entering_twice_stacks_rather_than_replaces(out: list[str]) -> int:
    """Check a second entry appends.

    ⚑ REPLACING WOULD HIDE THE CYCLE. Re-entering is exactly the event a reader is trying to
    see, and a stack that overwrites reports one entry for any depth.
    """
    _clear()
    try:
        suite_marker.enter_suite("alpha")
        suite_marker.enter_suite("beta")
        if suite_marker.stack() != ("alpha", "beta"):
            out.append(f"selftest: the stack read as {suite_marker.stack()!r}")
            return 1
    finally:
        _clear()
    return 0


def a_repeated_label_is_recorded_twice(out: list[str]) -> int:
    """Check re-entering one label is visible as a repeat.

    ⚑ THE CYCLE IS THE SUBJECT. Deduplicating here would erase the only evidence that a suite
    re-entered itself, which is the condition the guard was built for.
    """
    _clear()
    try:
        suite_marker.enter_suite("alpha")
        suite_marker.enter_suite("alpha")
        if suite_marker.stack() != ("alpha", "alpha"):
            out.append(f"selftest: a repeat read as {suite_marker.stack()!r}")
            return 1
    finally:
        _clear()
    return 0


def the_mark_is_inherited_by_a_child_process(out: list[str]) -> int:
    """Check a subprocess sees the mark its parent set.

    ⚑⚑ THE CASE THE WHOLE DESIGN RESTS ON, and the one a module-level flag fails. The cycle is a
    process tree, not a call stack: without inheritance the guard holds in the parent and every
    child re-enters freely, which is the four-generation fan-out that was measured.
    """
    _clear()
    try:
        suite_marker.enter_suite("outer")
        if not _child_sees_the_mark():
            out.append("selftest: a child process did not inherit the mark")
            return 1
    finally:
        _clear()
    return 0


def an_unmarked_parents_child_is_clean(out: list[str]) -> int:
    """Check a child of an unmarked process reads clean — the inheritance control.

    ⚑ WITHOUT THIS, A CHILD THAT ALWAYS REPORTED "inside" would pass the case above. The pair
    says the mark is TRANSMITTED rather than assumed.
    """
    _clear()
    if _child_sees_the_mark():
        out.append("selftest: an unmarked parent's child read as inside a suite")
        return 1
    return 0


_ARMS = (
    an_unmarked_process_is_not_in_a_suite,
    entering_marks_the_process,
    entering_twice_stacks_rather_than_replaces,
    a_repeated_label_is_recorded_twice,
    the_mark_is_inherited_by_a_child_process,
    an_unmarked_parents_child_is_clean,
)

_CASE_COUNT = 2 + 2 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-marker selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-marker selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
