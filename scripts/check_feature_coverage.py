#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Assert that every Scenario in `features/` is implemented by a named test.

WHY. Prose specs drift from code silently — that is their whole failure mode. This gate
makes the spec and the tests one artifact: a `Scenario:` with no test that names it is an
orphan, and the commit stops.

⚑ SCOPE — `features/` ONLY, and this is a PRECEDENT rather than a claim of coverage. The
first version named `el-atlas/features/` in this section while `FEATURES` pointed at
`features/`, so a reader could reasonably conclude its 52 scenarios were guarded. They
are not, and they should not be: they describe el-atlas DOMAIN semantics (chart
involutions, exp/log conjugacy), el-atlas has no test suite, and no test names any of
them — so extending this gate there would either fail permanently or demand 52 fake
tests. Measured: 52 scenarios in `features/` (2 files, all implemented), 52 in
`el-atlas/features/` (10 files, guarded by nothing, correctly).
**A docstring naming a directory is a scope claim, and scope claims drift silently
because nothing parses them.**

The link is deliberately a NAME, not a decorator or a step-definition binding. A
decorator would require pytest-bdd (not installed, and unavailable to a hook in a bare
environment); a name costs nothing and is greppable in both directions.

COUNTED, never a frozen list — the same shape as the selftests' derived `N/M` and the
ratchets' materialized census. There is no ALLOW-list of "scenarios we decided not to
test": a scenario is implemented, or it is deleted from the spec, or the gate fails.

Usage: `check_feature_coverage.py [--quiet]` — exit 1 on any orphan.

⚑ THE SCANNING LIVES IN `gherkin_scan`, and the split was the harness's advice: this file
refused on a `list[Any]` leak from `re.findall`, and the pattern plus its narrowing is a
different responsibility from deciding whether the link holds.

⚑ `absolute()`, NEVER `resolve()`. `PTH100` recommends `Path.resolve()` as
`os.path.abspath`'s replacement and it is NOT one: `resolve()` FOLLOWS SYMLINKS.
"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts import gherkin_scan, ratchet

ROOT = Path(__file__).absolute().parent.parent
FEATURES = ROOT / "features"
TESTS = ROOT / "tests"


def _orphan_lines(orphans: list[str], spec: dict[str, str]) -> list[str]:
    """Render scenarios the spec declares and no test names."""
    if not orphans:
        return []
    head = f"feature-coverage: BROKEN — {len(orphans)} Scenario(s) with no test:"
    tail = (
        "  Implement it (a test whose docstring quotes `Scenario: <text>`) or delete "
        "it from the spec. There is no exemption list."
    )
    return [head, *(f"    ~ {spec[n]}: {n}" for n in orphans), tail]


def _stale_lines(stale: list[str]) -> list[str]:
    """Render tests naming a scenario the spec no longer declares.

    ⚑ A test that survives a spec edit silently stops meaning anything — drift in the
    other direction, which is why the link is checked both ways.
    """
    if not stale:
        return []
    head = (
        f"feature-coverage: BROKEN — {len(stale)} test(s) name a Scenario the spec no longer has:"
    )
    tail = (
        "  Restore the Scenario, or update the test's docstring. A test naming a "
        "scenario nobody declares has stopped meaning anything."
    )
    return [head, *(f"    ? {n}" for n in stale), tail]


def main() -> int:
    """Report orphans and stale tests; exit 1 if either exists.

    ⚑ STALE MUST FAIL TOO. This used to report both and `return 1 if orphans else 0`, so
    the link was enforced in ONE direction only: deleting a Scenario from the spec left
    its test naming nothing and the gate stayed GREEN. Coverage could therefore shrink
    toward zero without ever failing — the gate would have kept saying "clean (0
    scenarios, all implemented)", which is true and worthless. A bidirectional link that
    only fails one way is a one-directional link with extra output.
    """
    rc = ratchet.check_argv(sys.argv, {"--quiet"}, "check_feature_coverage")
    if rc is not None:
        return rc
    spec = gherkin_scan.declared(FEATURES)
    have = gherkin_scan.quoted(TESTS)
    orphans = sorted(n for n in spec if n not in have)
    stale = sorted(n for n in have if n not in spec)

    lines = [*_orphan_lines(orphans, spec), *_stale_lines(stale)]
    if not lines and "--quiet" not in sys.argv:
        lines.append(f"feature-coverage: clean ({len(spec)} scenario(s), all implemented).")
    if lines:
        sys.stdout.write("\n".join(lines) + "\n")
    return 1 if (orphans or stale) else 0


if __name__ == "__main__":
    sys.exit(main())
