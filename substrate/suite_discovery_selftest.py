#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_discovery` — both entry spellings, and the real population.

⚑⚑ THE POPULATION ARM READS THE REAL TREE, NOT A FIXTURE, and that is deliberate. Every
recorded failure of this predicate was a population that silently SHRANK — three suites erased
by requiring a local body, one by anchoring on the `__main__` idiom, two directories missed by
a frozen roster. None showed as a failure; each showed as a smaller green total that nobody
had a prior for. A fixture pins the logic and cannot catch a walk that stops one directory
short.

⚑ NO CROSS-IMPLEMENTATION ARM HERE. Comparing against the pre-split `discover()` means running
it as a subprocess (it lives in an unpackaged 1834-finding file), which needs an `S603`
exemption — and a per-file exemption over a file that also holds unit cases would grant it to
both responsibilities. That comparison belongs in `promote_agree`, which owns the exemption
because running prior implementations is its ONE job (⟡reach-agreement).
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus, suite_discovery

# Sources exercising each entry-point spelling, and the two ways to fail the predicate.
_MAIN_GUARD = 'if __name__ == "__main__":\n    sys.exit(_selftest())\n'
_ARGV_GUARD = 'if "--selftest" in sys.argv:\n    sys.exit(_selftest())\n'
_FLAG_IN_GUARD = 'if __name__ == "__main__":\n    sys.exit(0 if "--selftest" in sys.argv else 1)\n'
_BODY = "def _selftest():\n    return 0\n\n"
_PLAIN_CLI = 'if __name__ == "__main__":\n    sys.exit(main(sys.argv))\n'

# Suites this package holds, which the walk must find.
_KNOWN = ("substrate/suite_outcome_selftest.py", "substrate/reach_ratchet_selftest.py")


def entry_spellings(out: list[str]) -> int:
    """Check both live dispatch idioms are admitted.

    ⚑ `dagcone.py` CALLS `_selftest()` UNCONDITIONALLY and never names the flag; `schema.py`
    names the flag and holds no local body. Requiring either alone erases the other — both
    measured, both live.
    """
    bad = 0
    for label, src in (
        ("a __main__ guard with a local body", _BODY + _MAIN_GUARD),
        ("a bare `--selftest in sys.argv` dispatch", _BODY + _ARGV_GUARD),
        ("a flag-naming dispatch with no local body", _FLAG_IN_GUARD),
    ):
        if not suite_discovery.is_suite(src):
            out.append(f"selftest: {label} was not admitted")
            bad += 1
    return bad


def halves_are_refused(out: list[str]) -> int:
    """Check neither half alone counts as a suite.

    ⚑ THE ENTRY POINT ALONE ADMITS EVERY CLI IN THE TREE; the body alone admits implementation
    halves that cannot be invoked and report SILENT while their cases pass under a parent —
    the measured double-count that started this predicate's history.
    """
    bad = 0
    if suite_discovery.is_suite(_BODY):
        out.append("selftest: a body with no dispatch was admitted as a suite")
        bad += 1
    if suite_discovery.is_suite(_PLAIN_CLI):
        out.append("selftest: a plain CLI entry point was admitted as a suite")
        bad += 1
    return bad


def skips_are_applied(out: list[str]) -> int:
    """Check vendored and snapshot subtrees are walked past."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "tools").mkdir()
        (root / "tools" / "real.py").write_text(_BODY + _MAIN_GUARD, encoding="utf-8")
        for skipped in (".venv", ".edit-snapshots", "__pycache__"):
            (root / "tools" / skipped).mkdir()
            (root / "tools" / skipped / "copy.py").write_text(_BODY + _MAIN_GUARD, encoding="utf-8")
        found = {label for label, _p in suite_discovery.discover(root)}
    if found != {"tools/real.py"}:
        out.append(f"selftest: the walk did not skip vendored subtrees: {sorted(found)}")
        return 1
    return 0


def roots_are_discovered(out: list[str]) -> int:
    """Check top-level roots are discovered, not frozen.

    ⚑ THE FROZEN FORM UNDER-REPORTED THREE TIMES, most recently missing a directory that did
    not exist when the tuple was written. A roster can only ever be as current as its last
    edit.

    ⚑⚑⚑ THIS CASE USED TO ASSERT THAT `agda` WAS SKIPPED, AND THAT ASSERTION WAS THE ROSTER'S —
    NOT A PROPERTY OF DISCOVERY. Ⓑ19 deleted the name list (operator: *"`_SKIP_TOP` should be
    replaced with `.gitignore`"*), because `find agda docs -name '*.py'` returns nothing: those
    directories contribute zero suites whether walked or not, so excluding them bought walk time
    and carried a stale name. **Keeping the case would have pinned the roster in place through its
    test**, which is how a deleted mechanism comes back.

    ⚑⚑ WHAT SURVIVES IS SPLIT OUT AND STILL ASSERTED. The DOTFILE rule is a real, live exclusion
    with a different owner, so it keeps its own check rather than riding along in a compound
    condition that a roster change silently changed the meaning of.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for name in ("brand_new", "agda", ".hidden"):
            (root / name).mkdir()
        got = suite_discovery.roots(root)
    if "brand_new" not in got:
        out.append(f"selftest: a new top-level directory was not discovered: {got}")
        bad += 1
    # ⚑ A DOTFILE IS STILL SKIPPED — the one name-based rule that remains, and it is not a roster.
    if ".hidden" in got:
        out.append(f"selftest: a dot-prefixed root was discovered: {got}")
        bad += 1
    # ⚑ AND A TRACKED, SUITELESS DIRECTORY IS NOW ADMITTED, deliberately. `is_suite` is the
    # predicate; a directory holding no Python costs a walk and yields nothing.
    if "agda" not in got:
        out.append(f"selftest: a tracked root was excluded by a roster that should be gone: {got}")
        bad += 1
    return bad


def live_population(out: list[str]) -> int:
    """Check the walk finds this package's own suites in the real tree.

    ⚑ A POSITIVE CONTROL OVER REAL FILES. Zero suites is what a broken walk returns AND what a
    correct walk returns over an empty tree; only naming files that must be found separates
    them.
    """
    bad = 0
    found = {label for label, _p in suite_discovery.discover(corpus.ROOT)}
    if not found:
        out.append("selftest: the walk found no suites at all")
        return 1
    for known in _KNOWN:
        if known not in found:
            out.append(f"selftest: the walk missed {known}")
            bad += 1
    return bad


_ARMS = (
    entry_spellings,
    halves_are_refused,
    skips_are_applied,
    roots_are_discovered,
    live_population,
)

_CASE_COUNT = 3 + 2 + 1 + 2 + len(_KNOWN)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-discovery selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-discovery selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
