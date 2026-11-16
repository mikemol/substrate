#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.census_show` — that every cell is reported, and no count is bare.

⚑⚑ THE ALL-FOUR-CELLS CASE IS THE ONE THAT MATTERS. A renderer printing only the debt cell
cannot distinguish "everything is consistent" from "nothing was assessed" — a false ZERO gets
banked while a false positive gets investigated. `STRAY` in particular is what makes the tenant
declaration falsifiable rather than decorative, and a renderer that dropped it would quietly
convert a checkable field into an unfalsifiable one.

⚑ AND EVERY COUNT MUST CARRY ITS BOUNDARY. A `0 OWED` is a statement about two SOURCE lenses,
not about the tree; a case pins that the sentence saying so is printed with the number rather
than left in a docstring nobody reads at the terminal.

⚑⚑ THE `clear` ARM WAS AN UNSPLIT PAIR. Suppressing the quiet majority's lines and reporting
how many were suppressed are INDEPENDENT properties of the renderer — printing nothing at all
satisfies the first — and they now carry separate names, so a report that goes silent fails the
arm that says why that is wrong rather than half of an arm named for the other half.
"""

from __future__ import annotations

import sys

from substrate import census_show, tenant_census

# A path that is never opened — `render_list` prints labels only, so this stands in for one.
_UNREAD_PATH = "fixture/x.py"

# One row per verdict the renderer lists, so a dropped cell is a failing case.
_ROWS = (
    tenant_census.Row(
        label="a.py",
        declared=None,
        reaches=True,
        via=("store",),
        deferred_only=False,
        opens=frozenset({"connect"}),
    ),
    tenant_census.Row(
        label="b.py",
        declared="--sandbox",
        reaches=False,
        via=(),
        deferred_only=False,
        opens=frozenset(),
    ),
    tenant_census.Row(
        label="c.py",
        declared="--sandbox",
        reaches=True,
        via=("store",),
        deferred_only=False,
        opens=frozenset(),
    ),
    tenant_census.Row(
        label="d.py",
        declared=None,
        reaches=False,
        via=("~q",),
        deferred_only=True,
        opens=frozenset(),
    ),
    tenant_census.Row(
        label="e.py", declared=None, reaches=False, via=(), deferred_only=False, opens=frozenset()
    ),
)


def every_cell_is_reported(out: list[str]) -> int:
    """Check each verdict the census can produce appears in the rendering.

    ⚑ A CELL THAT VANISHES IS INVISIBLE, NOT ABSENT. If `STRAY` stopped being printed, a wrong
    declaration would sit forever and the census would read cleaner for it.
    """
    lines: list[str] = []
    census_show.render_tenants(list(_ROWS), lines)
    body = "\n".join(lines)
    bad = 0
    for want in ("OWED", "STRAY", "if-it-runs/inert", "declared"):
        if want not in body:
            out.append(f"selftest: verdict {want!r} was not rendered")
            bad += 1
    return bad


def the_clear_cell_is_not_listed_individually(out: list[str]) -> int:
    """Check a `clear` cell does not get a line of its own in the report.

    ⚑ `clear` IS THE CORRECT RESTING STATE and there are 122 of them on the live tree. Listing
    each would bury the four cells a reader must act on — a report whose signal is a 3% minority
    of its lines is one that gets skimmed rather than read.
    """
    lines: list[str] = []
    census_show.render_tenants(list(_ROWS), lines)
    if "  clear " in "\n".join(lines):
        out.append("selftest: a 'clear' row was listed individually")
        return 1
    return 0


def the_clear_cells_are_still_counted(out: list[str]) -> int:
    """Check the tally reports how many `clear` cells it suppressed.

    ⚑ SUPPRESSING THE LINES AND REPORTING THE COUNT ARE INDEPENDENT, AND THE CHEAPEST WAY TO
    SATISFY THE SIBLING ABOVE IS TO DROP BOTH. Printing nothing at all passes the
    not-listed-individually claim completely, so that claim on its own cannot tell a SUMMARISED
    census from a SILENT one.

    ⚑⚑ AND THE COUNT IS THE DENOMINATOR THE ACTED-ON CELLS ARE A FRACTION OF. Without it, four
    findings out of 126 and four out of five render identically — the reader loses the only
    number that says whether the tree is mostly healthy or mostly broken.
    """
    lines: list[str] = []
    census_show.render_tenants(list(_ROWS), lines)
    if "1 clear" not in "\n".join(lines):
        out.append("selftest: the 'clear' count was not reported")
        return 1
    return 0


def the_count_carries_its_boundary(out: list[str]) -> int:
    """Check the lens-boundary sentence is printed beside the tally."""
    lines: list[str] = []
    census_show.render_tenants(list(_ROWS), lines)
    body = "\n".join(lines)
    if "not coverage" not in body:
        out.append("selftest: the tally printed without naming the lenses' boundary")
        return 1
    return 0


def pragmas_names_the_silent_majority(out: list[str]) -> int:
    """Check a suite declaring neither pragma is reported as unread, not as clean."""
    lines: list[str] = []
    census_show.render_pragmas([], lines)
    body = "\n".join(lines)
    if "declare NEITHER" not in body:
        out.append("selftest: the pragma census did not name its silent majority")
        return 1
    return 0


def list_reports_its_denominator(out: list[str]) -> int:
    """Check the roster listing states how many suites it found.

    ⚑ A BARE LIST CANNOT DISTINGUISH *no matches* FROM *nothing read* — the repo's own rule
    for every census mode.
    """
    lines: list[str] = []
    census_show.render_list([("x.py", _UNREAD_PATH)], lines)
    if "1 suite(s)" not in "\n".join(lines):
        out.append("selftest: the roster listing reported no count")
        return 1
    return 0


_ARMS = (
    every_cell_is_reported,
    the_clear_cell_is_not_listed_individually,
    the_clear_cells_are_still_counted,
    the_count_carries_its_boundary,
    pragmas_names_the_silent_majority,
    list_reports_its_denominator,
)

# ⚑ THE 2 BECAME 1 + 1 AND THE TOTAL DID NOT MOVE — the invariance that makes an n-split
# auditable, since a count that changed under a rename would be a dropped or invented assertion.
_CASE_COUNT = 4 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"census-show selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"census-show selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
