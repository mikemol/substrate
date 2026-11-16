#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.mypy_census`.

⚑⚑ THE CENTRAL CASE IS THE POSITIVE CONTROL, NOT THE PARSE. This census once reported **0
keys over 60 unannotated files** and that read as a clean tree: the subprocess had invoked a
`python3` without mypy installed, produced no error lines, and the parse honestly found
nothing. A census that cannot run must never be indistinguishable from a census that found
nothing, so the arm that matters plants a KNOWN error and requires it to come back.

⚑ AND THE SENTINEL IS THE OTHER HALF. `type_errors` returns `UNRUNNABLE` when mypy exits
non-census, `None` when it is absent, and a dict otherwise. A caller that treats all three as
"no errors" certifies its own blind spot — which is the defect the gate exists to catch,
committed by the gate.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import mypy_census

# A file whose error mypy cannot miss, and whose CODE is stable across versions.
_PLANTED = "x: int = 'not an int'\n"
_PLANTED_CODE = "assignment"


def _census_of(name: str, body: str) -> dict[str, list[str]] | None:
    """Write one file into a fresh tree and return the census over it.

    ⚑ A FRESH TREE PER ARM, NOT THE REPO. A census over the real corpus takes minutes and
    its result moves with every edit; these arms test the INSTRUMENT, so the input must be
    fixed and tiny. It also means the planted error cannot be confused with a real one.
    """
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / name).write_text(body, encoding="utf-8")
        return mypy_census.type_errors([name], root=root)


def positive_control(out: list[str]) -> int:
    """Plant a known type error and require the census to report it.

    ⚑ WITHOUT THIS, EVERY OTHER CASE PASSES ON A CENSUS THAT NEVER RAN. Zero findings is the
    expected result of a healthy tree AND of a broken invocation; only a case demanding a
    specific key can tell them apart.
    """
    got = _census_of("planted.py", _PLANTED)
    if got is None:
        out.append("selftest: mypy is not installed — the census cannot be verified")
        return 1
    if mypy_census.UNRUNNABLE in got:
        out.append(f"selftest: mypy could not run: {got[mypy_census.UNRUNNABLE]}")
        return 1
    if not any(k.startswith(f"{_PLANTED_CODE}::") for k in got):
        out.append(f"selftest: the planted error was not reported; keys={sorted(got)}")
        return 1
    return 0


def clean_is_empty(out: list[str]) -> int:
    """Check that a file with no type error yields no keys — the control's negative half."""
    got = _census_of("fine.py", "x: int = 1\n")
    if got is None or mypy_census.UNRUNNABLE in got:
        out.append("selftest: the clean-file arm could not run")
        return 1
    if got:
        out.append(f"selftest: a clean file produced keys: {sorted(got)}")
        return 1
    return 0


def key_shape(out: list[str]) -> int:
    """Check that keys are `<code>::<relpath>` with NO line number.

    ⚑ LINE NUMBERS CHURN ON EVERY UNRELATED EDIT ABOVE A SITE. `check_rederive_ratchet` keyed
    on them and would have fired on nearly every commit; a ratchet whose keys move is a
    ratchet that cannot record paydown.
    """
    got = _census_of("planted.py", _PLANTED)
    if not got or mypy_census.UNRUNNABLE in got:
        out.append("selftest: the key-shape arm could not run")
        return 1
    bad = 0
    for key in got:
        code, _, rel = key.partition("::")
        if not rel.endswith(".py"):
            out.append(f"selftest: key {key!r} does not end in a source path")
            bad += 1
        if any(part.isdigit() for part in rel.split(":")):
            out.append(f"selftest: key {key!r} carries a line number")
            bad += 1
        if not code:
            out.append(f"selftest: key {key!r} has no error code")
            bad += 1
    return bad


def unrunnable_is_not_clean(out: list[str]) -> int:
    """Check that a non-census mypy exit raises the sentinel rather than reading as clean.

    ⚑ A GATE THAT REPORTS 0 KEYS WHEN THE CHECKER NEVER RAN IS WORSE THAN NO GATE: it
    certifies its own blind spot. The sentinel is what lets a caller refuse.
    """
    with tempfile.TemporaryDirectory() as td:
        got = mypy_census.type_errors(["no-such-file-here.py"], root=Path(td))

    if got is None:
        out.append("selftest: the unrunnable arm could not run")
        return 1
    if mypy_census.UNRUNNABLE not in got:
        out.append(f"selftest: a missing path did not raise the sentinel; got {sorted(got)}")
        return 1
    if not got[mypy_census.UNRUNNABLE][0]:
        out.append("selftest: the sentinel carries no reason")
        return 1
    return 0


_ARMS = (positive_control, clean_is_empty, key_shape, unrunnable_is_not_clean)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"mypy-census selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"mypy-census selftest: {len(_ARMS)}/{len(_ARMS)}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
