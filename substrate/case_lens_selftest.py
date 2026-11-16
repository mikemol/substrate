#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.case_lens` — the roster, the None contract, and the fixed zeros.

⚑⚑ THE `None`-NOT-ZERO ARM IS THE LOAD-BEARING ONE. A zero from an unparseable file reads as
"every case was deleted", which turns a genuine fewer-RAN regression into honest paydown. That
is the false-ZERO direction this repo banks silently, and it is why the counter's contract is
three-valued rather than two.

⚑ AND THE ACCUMULATOR ARM PINS A FIX TO A MEASURED BLIND SPOT. Twelve suites in `substrate/`
report failures by `out.append(...)` and read a static count of ZERO under the pre-split
roster — and a suite recorded at zero can never regress, so the second lens was blind exactly
where the newest code is.

⚑⚑⚑ TWO ARMS HERE WERE UNSPLIT FAMILIES, AND THEY WERE UNSPLIT IN DIFFERENT WAYS. `None`-not-zero
fused two INDEPENDENT failure modes — a file that cannot be parsed and a file that is not there —
which reach different branches and can be handled one without the other. `live_suites` fused a
GUARDED pair: the lens reading was reached only when the location check held, which is a premise,
not a fusion. Both are now separate arms and `FAMILY` carries the edge.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import witness_family

from substrate import case_lens, corpus

# Suites written in the accumulator idiom, which the pre-split roster could not see.
_ACCUMULATOR_SUITES = (
    "reach_verdict_selftest.py",
    "reach_baseline_selftest.py",
    "reach_ratchet_selftest.py",
    "type_gate_selftest.py",
)

# A source using the named-helper idiom.
_HELPER_SRC = """
def ok(label, cond):
    pass

def suite():
    ok("one", True)
    ok("two", True)
    chk("three", True)
"""

# A source using the accumulator idiom, as every substrate/ suite is written.
_ACCUM_SRC = """
def arm(out):
    out.append("first")
    out.append("second")
"""


def unparseable_is_none(out: list[str]) -> int:
    """Check a file that is PRESENT but cannot be parsed counts None, never 0.

    ⚑ ZERO IS A MEASUREMENT AND NONE IS ITS ABSENCE. A file whose syntax the lens cannot read
    holds an unknown number of cases; reporting 0 states a fact the lens did not establish, and a
    census summing those reads a broken file as a clean one — the report-presence-never-absence
    shape, inside a counter.
    """
    with tempfile.TemporaryDirectory() as d:
        broken = Path(d) / "broken.py"
        broken.write_text("def (:\n", encoding="utf-8")
        if case_lens.own_cases(str(broken)) is not None:
            out.append("selftest: an unparseable file did not count None")
            return 1
    return 0


def a_missing_file_is_none_not_zero(out: list[str]) -> int:
    """Check a path that does not exist counts None, never 0.

    ⚑ A DIFFERENT FAILURE MODE FROM UNPARSEABLE, REACHING A DIFFERENT BRANCH, AND NEITHER GUARDS
    THE OTHER. Unparseable is a parser refusing a file it read; missing is the read itself
    failing, and an implementation can get one right and the other wrong — a bare
    `except SyntaxError` catches the first and lets the second raise, while a blanket
    `except Exception: return 0` gets both wrong in the silent direction. Sharing a name meant
    the report could never say which branch had broken.
    """
    with tempfile.TemporaryDirectory() as d:
        missing = Path(d) / "absent.py"
        if case_lens.own_cases(str(missing)) is not None:
            out.append("selftest: a missing file did not count None")
            return 1
    return 0


def helper_idiom_counted(out: list[str]) -> int:
    """Check named assertion helpers are counted, including the late-added spellings."""
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "helper.py"
        src.write_text(_HELPER_SRC, encoding="utf-8")
        got = case_lens.own_cases(str(src))
    # Three `ok`/`chk` CALLS; the `def ok` is a definition, not a call.
    want = 3
    if got != want:
        out.append(f"selftest: the helper idiom counted {got}, not {want}")
        return 1
    return 0


def accumulator_idiom_counted(out: list[str]) -> int:
    """Check the `out.append(...)` idiom registers cases.

    ⚑ THE FIX FOR A MEASURED ZERO. Without `append` in the roster this reads 0, and a suite
    recorded at zero can never regress.
    """
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "accum.py"
        src.write_text(_ACCUM_SRC, encoding="utf-8")
        got = case_lens.own_cases(str(src))
    if got != 2:  # noqa: PLR2004 - two appends in the fixture above
        out.append(f"selftest: the accumulator idiom counted {got}, not 2")
        return 1
    return 0


def the_live_suites_are_where_the_census_expects_them(out: list[str]) -> int:
    """Check each accumulator-idiom suite is at the path this module names.

    ⚑ THE LOCATION CLAIM ITS SIBLING RESTS ON, AND IT WAS RUN WITHOUT BEING COUNTED. A suite that
    moved or was renamed makes the lens reading unaskable rather than failing — so fusing the two
    let a MISSING file and a BLIND lens reach the reader under one name, when they call for
    opposite repairs (fix this fixture list, versus fix the roster).
    """
    bad = 0
    for name in _ACCUMULATOR_SUITES:
        if not (corpus.ROOT / "substrate" / name).is_file():
            out.append(f"selftest: {name} is not where the census expects it")
            bad += 1
    return bad


def live_suites_are_visible(out: list[str]) -> int:
    """Check the promoted suites now report a non-zero source count.

    ⚑ THIS IS THE ARM THAT WOULD HAVE CAUGHT THE BLIND SPOT. It reads REAL files rather than
    a fixture, so it fails if the roster ever stops recognising the idiom this package is
    written in — which is precisely how `ok` and `chk` went missing for five suites.

    ⚑⚑ IT RESTS ON THE LOCATION ARM, AND THAT EDGE USED TO BE A `continue`. A file that is not
    there reads as zero cases here, so without the sibling holding, a blind roster and a stale
    fixture list are the same red — and only one of them is about the lens.
    """
    bad = 0
    for name in _ACCUMULATOR_SUITES:
        path = corpus.ROOT / "substrate" / name
        if not path.is_file():
            continue
        got = case_lens.own_cases(str(path))
        if not got:
            out.append(
                f"selftest: {name} reads {got!r} case call-site(s) — the second lens is blind to it"
            )
            bad += 1
    return bad


# ⚑⚑ THE FAMILY IS HERE FOR THE PREMISE EDGE. `live_suites_are_visible` is only a statement about
# the LENS while its subjects are on disk; that condition lived as a `continue` inside one arm,
# where it was reached, run, and absent from both the roster and the count.
FAMILY = witness_family.of(
    key="case-lens",
    apex="the case lens says what it counted and what it could NOT count — three-valued, so a "
    "file it failed to read never enters a census as a clean zero",
    subject="the source idioms a suite in this tree registers cases with",
    members=(
        witness_family.Member(
            name="unparseable_is_none", claim="a present-but-unparseable file counts None, never 0"
        ),
        witness_family.Member(
            name="a_missing_file_is_none_not_zero",
            claim="a path that does not exist counts None, never 0 — a different branch from "
            "unparseable, which an implementation can get right one way and not the other",
        ),
        witness_family.Member(
            name="helper_idiom_counted",
            claim="named assertion helpers are counted, late-added spellings included",
        ),
        witness_family.Member(
            name="accumulator_idiom_counted",
            claim="the out.append idiom registers cases, fixing a measured zero",
        ),
        witness_family.Member(
            name="the_live_suites_are_where_the_census_expects_them",
            claim="each accumulator-idiom suite is at the path this module names",
            cases=len(_ACCUMULATOR_SUITES),
        ),
        witness_family.Member(
            name="live_suites_are_visible",
            claim="the promoted suites read a non-zero source count on the REAL tree, which is "
            "what fails if the roster stops recognising this package's own idiom",
            cases=len(_ACCUMULATOR_SUITES),
            premises=("the_live_suites_are_where_the_census_expects_them",),
        ),
    ),
)

_ARMS = (
    unparseable_is_none,
    a_missing_file_is_none_not_zero,
    helper_idiom_counted,
    accumulator_idiom_counted,
    the_live_suites_are_where_the_census_expects_them,
    live_suites_are_visible,
)

# ⚑ TWO MOVEMENTS, AND THEY ARE DIFFERENT KINDS. The `None` arm's 2 became 1 + 1 — a faithful
# split, total unchanged. The `live_suites` arm's location check was an assertion that RAN and was
# never counted, so naming it adds `len(_ACCUMULATOR_SUITES)` — a finding about the old number.
_CASE_COUNT = FAMILY.count


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"case-lens selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"case-lens selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
