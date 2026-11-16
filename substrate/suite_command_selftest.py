#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_command` — above all, the tenant on BOTH branches.

⚑⚑⚑ THE ASYMMETRY ARM IS THE RECORDED DEFECT AND THE REASON THIS MODULE EXISTS. The pre-split
builder assembled the inner argv twice — plainly, and again inside the `uv` branch — so a fix
applied to one branch worked for every suite EXCEPT the ones declaring a dependency. That is
invisible unless a fixture declares BOTH a tenant and a dep, which is exactly what these cases
do. A suite running against an undeclared tenant returns plausible rows nobody can
distinguish.

⚑ AND THE LEASE'S ABSENCE MUST BE VISIBLE. When the wrapper is missing the suite still runs,
but a case pins that the budgeted form differs from the bare one — a guard that degrades to
measuring nothing is worse than one that fails.
"""

from __future__ import annotations

import os
import stat
import sys
import tempfile
from pathlib import Path

from substrate import suite_command

# A suite declaring BOTH a tenant and a dependency — the fixture the asymmetry needs.
_BOTH = "# selftest-tenant: sandbox\n# selftest-requires: numpy\n"

# A suite declaring only a tenant.
_TENANT_ONLY = "# selftest-tenant: live\n"

# A suite declaring nothing.
_BARE = "print('hi')\n"

_PY = "/usr/bin/python3"

# A stand-in lease wrapper that simply execs what it is given.
_WRAPPER_SRC = '#!/bin/sh\nexec "$@"\n'

# ⚑ THE LEDGER IS POINTED AT A FIXTURE, NEVER AT THIS MACHINE'S HISTORY. `label_ledger` reads
# this knob, so the sizing arms below assert arithmetic rather than whatever the host happens to
# have recorded — a case keyed on live peaks would pass or fail by machine.
_LEDGER_ENV = "MEMBUDGET_LABEL_LEDGER"

# The peak the ceiling arm plants, above `label_lease`'s own 384 default.
_HEAVY_PEAK = 420


def _tree(d: str, src: str, *, with_wrapper: bool) -> tuple[str, Path]:
    """Write a fixture suite and optionally an executable lease wrapper."""
    root = Path(d)
    suite = root / "suite.py"
    suite.write_text(src, encoding="utf-8")
    if with_wrapper:
        (root / "scripts").mkdir(exist_ok=True)
        wrapper = root / "scripts" / "membudget"
        wrapper.write_text(_WRAPPER_SRC, encoding="utf-8")
        wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
    return (str(suite), root)


def tenant_on_both_branches(out: list[str]) -> int:
    """Check the declared tenant survives the dependency branch.

    ⚑ THE MEASURED DEFECT. With a dep declared the builder takes the `uv` path; the tenant
    flag must still be there, or every dependency-declaring suite silently runs untenanted.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        suite, root = _tree(d, _BOTH, with_wrapper=False)
        argv = suite_command.command(suite, _PY, root)
        if "--sandbox" not in argv:
            out.append(f"selftest: the tenant was dropped on the dep branch: {argv}")
            bad += 1
        if "--selftest" not in argv:
            out.append(f"selftest: the selftest flag was dropped: {argv}")
            bad += 1
    with tempfile.TemporaryDirectory() as d:
        suite, root = _tree(d, _TENANT_ONLY, with_wrapper=False)
        argv = suite_command.command(suite, _PY, root)
        if "--live" not in argv:
            out.append(f"selftest: the tenant was dropped on the plain branch: {argv}")
            bad += 1
    return bad


def deps_are_supplied(out: list[str]) -> int:
    """Check a declared dependency becomes a `--with` flag when uv is available.

    ⚑ SUPPLYING THE DEP IS THE FIX; EXEMPTING THE SUITE IS NOT. A suite that SKIPs on a
    missing dependency scores as a pass-shaped absence — 300 real assertions were not running.

    ⚑ CONDITIONAL ON `uv` BEING PRESENT, and the case says so rather than asserting a
    machine-dependent fact. Without uv the bare branch is CORRECT, not a failure.
    """
    if suite_command.uv_path() is None:
        return 0
    with tempfile.TemporaryDirectory() as d:
        suite, root = _tree(d, _BOTH, with_wrapper=False)
        argv = suite_command.command(suite, _PY, root)
    if "--with" not in argv or "numpy" not in argv:
        out.append(f"selftest: a declared dependency was not supplied: {argv}")
        return 1
    return 0


def budget_wraps_when_present(out: list[str]) -> int:
    """Check the lease wrapper is used when it exists, and skipped when it does not."""
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        suite, root = _tree(d, _BARE, with_wrapper=True)
        argv = suite_command.command(suite, _PY, root)
        if "run" not in argv or "--" not in argv:
            out.append(f"selftest: the lease wrapper was not applied: {argv}")
            bad += 1
        if not any(a.startswith("selftest:") for a in argv):
            out.append(f"selftest: the lease carries no label: {argv}")
            bad += 1
    with tempfile.TemporaryDirectory() as d:
        suite, root = _tree(d, _BARE, with_wrapper=False)
        argv = suite_command.command(suite, _PY, root)
        if argv[0] != _PY:
            out.append(f"selftest: a missing wrapper still produced a budgeted argv: {argv}")
            bad += 1
    return bad


def lease_is_overridable(out: list[str]) -> int:
    """Check the per-suite lease reads its env knob, defaulting to the shim's own number."""
    bad = 0
    saved = os.environ.pop(suite_command.SUITE_MB_ENV, None)
    try:
        if suite_command.suite_mb() != suite_command.DEFAULT_SUITE_MB:
            out.append("selftest: the unconfigured lease is not the documented default")
            bad += 1
        os.environ[suite_command.SUITE_MB_ENV] = "1024"
        if suite_command.suite_mb() != "1024":
            out.append("selftest: the lease env knob was ignored")
            bad += 1
    finally:
        os.environ.pop(suite_command.SUITE_MB_ENV, None)
        if saved is not None:
            os.environ[suite_command.SUITE_MB_ENV] = saved
    return bad


def suite_path_is_present(out: list[str]) -> int:
    """Check the suite's own path reaches the argv on every branch."""
    bad = 0
    for src in (_BARE, _BOTH):
        with tempfile.TemporaryDirectory() as d:
            suite, root = _tree(d, src, with_wrapper=True)
            argv = suite_command.command(suite, _PY, root)
            if suite not in argv:
                out.append(f"selftest: the suite path is missing from the argv: {argv}")
                bad += 1
    return bad


def _sized(label_src: str, peak: str | None) -> str:
    """Return the lease a fixture ledger yields for one suite, with the env restored after.

    ⚑ SHARED BECAUSE FOUR ARMS NEED THE SAME SCAFFOLD and four copies of an env save/restore is
    how one of them ends up leaking a knob into the arms that follow.
    """
    saved_ledger = os.environ.get(_LEDGER_ENV)
    try:
        with tempfile.TemporaryDirectory() as d:
            ledger = Path(d) / "labels.tsv"
            if peak is not None:
                label = suite_command.label_of(label_src)
                ledger.write_text(f"{label}\t1.0\t{peak}\t1700000000\n", encoding="utf-8")
            os.environ[_LEDGER_ENV] = str(ledger)
            return suite_command.suite_mb(label_src)
    finally:
        os.environ.pop(_LEDGER_ENV, None)
        if saved_ledger is not None:
            os.environ[_LEDGER_ENV] = saved_ledger


def the_lease_is_sized_from_recorded_peaks(out: list[str]) -> int:
    """Check a label with history is sized from its own maximum, not the flat default.

    ⚑⚑⚑ THE ARM THE FLAT CONSTANT COULD NOT HAVE. Before the wiring, every one of ~234 suites
    leased the same number while the ledger held hundreds of runs each — the instrument measured
    correctly and nothing consumed the measurement (gate-G374). This asserts the join exists.
    """
    saved = os.environ.pop(suite_command.SUITE_MB_ENV, None)
    try:
        got = _sized("x_selftest.py", "90")
    finally:
        if saved is not None:
            os.environ[suite_command.SUITE_MB_ENV] = saved
    if got != "128":
        out.append(f"selftest: a 90MB peak sized to {got!r}, expected the 128 bucket")
        return 1
    return 0


def an_unmeasured_label_takes_the_floor(out: list[str]) -> int:
    """Check a label the ledger has never seen falls back rather than failing.

    ⚑ THE ORDINARY FIRST-RUN STATE, and the direction that must never raise: a sizing reader
    that died on a missing history would take down the work it sizes.
    """
    saved = os.environ.pop(suite_command.SUITE_MB_ENV, None)
    try:
        got = _sized("never_seen_selftest.py", None)
    finally:
        if saved is not None:
            os.environ[suite_command.SUITE_MB_ENV] = saved
    if got != suite_command.DEFAULT_SUITE_MB:
        out.append(f"selftest: an unmeasured label sized to {got!r}, expected the floor")
        return 1
    return 0


def an_explicit_size_beats_history(out: list[str]) -> int:
    """Check `SELFTEST_MB` overrides a sized label — an instruction, not a suggestion.

    ⚑ THE ORDERING IS THE DESIGN. A caller naming a size did so for a reason history cannot see,
    so a ledger that silently won would be the clamp defect one layer up.
    """
    os.environ[suite_command.SUITE_MB_ENV] = "777"
    try:
        got = _sized("x_selftest.py", "90")
    finally:
        os.environ.pop(suite_command.SUITE_MB_ENV, None)
    if got != "777":
        out.append(f"selftest: an explicit lease lost to history: {got!r}")
        return 1
    return 0


def the_ceiling_admits_a_heavy_suite(out: list[str]) -> int:
    """Check a peak above `label_lease`'s own ceiling is not clamped below the measured need.

    ⚑⚑ MEASURED, AND THE REASON THIS MODULE RAISES THE CEILING. The `sync_verdict` pair peaks
    near 400MB, which the sizer's default 384 would clamp BELOW what the suite is known to use —
    a lease knowingly smaller than the need, which is a kill rather than a slowdown.
    """
    saved = os.environ.pop(suite_command.SUITE_MB_ENV, None)
    try:
        got = _sized("heavy_selftest.py", str(_HEAVY_PEAK))
    finally:
        if saved is not None:
            os.environ[suite_command.SUITE_MB_ENV] = saved
    if int(got) < _HEAVY_PEAK:
        out.append(f"selftest: a {_HEAVY_PEAK}MB peak leased {got!r} — below the need")
        return 1
    return 0


_ARMS = (
    tenant_on_both_branches,
    deps_are_supplied,
    budget_wraps_when_present,
    lease_is_overridable,
    suite_path_is_present,
    the_lease_is_sized_from_recorded_peaks,
    an_unmeasured_label_takes_the_floor,
    an_explicit_size_beats_history,
    the_ceiling_admits_a_heavy_suite,
)

_CASE_COUNT = 3 + 1 + 3 + 2 + 2 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-command selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-command selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
