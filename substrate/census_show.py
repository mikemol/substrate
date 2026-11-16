#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render the suite censuses — the read-only half of what `run_selftests` reported.

⚑⚑ THESE MODES RUN NOTHING, WHICH IS WHY THEY SURVIVE THE DISPATCH CUT (⟡runner-roster-cut).
`run_selftests` held four census modes beside its roster runner, and only the runner is the
thing being removed: `--tenants`, `--pragmas` and `--list` are SOURCE reads that answer what a
suite declares, not what it did. Keeping them in a file whose reason to exist is going away
would strand them.

    census_show.py --tenants     # reaches-a-store vs declares-a-tenant, the 2x2
    census_show.py --pragmas     # what each suite declares to the runner
    census_show.py --list        # the discovered roster

⚑⚑⚑ AND THE LOGIC WAS ALREADY EXTRACTED — THIS WIRES AN ORPHANED RUNG RATHER THAN REBUILDING.
`substrate.tenant_census` was built to 12/12 cases and measured with ZERO consumers by three
decorrelated lenses; `run_selftests.cmd_tenants` continued to run an OLDER implementation of
the same census, one still carrying the hand-written `IF_IT_RUNS_RULINGS` table the extracted
module replaced with a two-lens join. So the duplication was not merely redundant: the copy in
use was the worse one.

⚑ THE VERDICT VOCABULARY IS THE MODULE'S, NOT RESTATED HERE. `Row.verdict` owns the
classification (`OWED` / `STRAY` / `if-it-runs/opens` / `if-it-runs/inert` / `declared` /
`clear`); this prints what it returns. A renderer that re-derived the verdict would be a second
authority on the same question — the drift this repo keeps paying for.

⚑ AND EVERY COUNT IS PRINTED WITH ITS BOUNDARY. A `0 OWED` here is a statement about IMPORT
CLOSURE plus a name-keyed call lens; a store opened through a raw driver call is invisible to
both (measured: `query_defs._cost_connect`). Coverage is the union of blind spots, so the
census reports that union rather than claiming to close it.
"""

from __future__ import annotations

import sys

from mikemol.corpus import suite_discovery, suite_pragmas

from substrate import (
    corpus,
    promoted,
    store_reach,
    tenant_census,
    tenant_pragma,
)

# The verdicts worth listing individually, in the order a reader should see them: the debt
# first, then the falsifying cell, then the rows needing adjudication.
_LISTED = ("OWED", "STRAY", "if-it-runs/opens", "if-it-runs/inert", "declared")


def _by_label(row: tenant_census.Row) -> str:
    """Sort key: the suite's label.

    ⚑ A NAMED FUNCTION, NOT A LAMBDA, because an untyped lambda makes the sorted() expression
    `Any` and poisons it under `disallow_any_expr`.
    """
    return row.label


def render_tenants(rows: list[tenant_census.Row], out: list[str]) -> None:
    """Render the tenant 2x2 and its boundary."""
    by: dict[str, list[tenant_census.Row]] = {}
    for r in rows:
        by.setdefault(r.verdict, []).append(r)

    for verdict in _LISTED:
        for r in sorted(by.get(verdict, []), key=_by_label):
            via = "→".join(r.via) if r.via else "-"
            opens = (" opens " + ",".join(sorted(r.opens))) if r.opens else ""
            out.append(f"  {verdict:<18} {r.label:<42} via {via}{opens}")

    tally = ", ".join(f"{len(by.get(v, []))} {v}" for v in _LISTED)
    clear = len(by.get("clear", []))
    out.append(f"  {len(rows)} discovered: {tally}, {clear} clear")
    # ⚑ THE BOUNDARY IS PRINTED WITH THE COUNT, NOT LEFT IN A DOCSTRING. A reader acting on
    # "0 OWED" must see that the zero is a statement about what two SOURCE lenses can see.
    out.append(
        "    ⚑ BOTH LENSES ARE SOURCE CENSUSES. Import closure answers what importing"
        "\n      a suite executes; the call lens answers whether a file on that route"
        "\n      NAMES a store-opener. A raw driver call naming neither is invisible to"
        "\n      both — their agreement is not coverage."
    )


def render_pragmas(suites: list[tuple[str, str]], out: list[str]) -> None:
    """Render what each suite declares to the runner."""
    rows = [
        (label, suite_pragmas.requires(path), tenant_pragma.tenant(path)) for label, path in suites
    ]
    with_req = [r for r in rows if r[1]]
    with_ten = [r for r in rows if r[2]]

    for label, req, _ten in sorted(with_req):
        out.append(f"  requires   {label:<42} {', '.join(req)}")
    for label, _req, ten in sorted(with_ten):
        out.append(f"  tenant     {label:<42} {ten}")
    out.append(
        f"  {len(rows)} discovered, {len(with_req)} declare a dependency, "
        f"{len(with_ten)} declare a tenant"
    )
    # ⚑ THE SILENT MAJORITY IS NAMED AS UNREAD, NEVER AS CLEAN. A suite declaring neither
    # pragma is not thereby known to need neither — nobody has asked.
    neither = len([r for r in rows if not r[1] and not r[2]])
    out.append(
        f"    ⚑ {neither} suite(s) declare NEITHER. That is not a clean tree: this"
        "\n      reports what a suite SAYS, and cannot tell 'needs nothing' from"
        "\n      'never asked'."
    )


def render_list(suites: list[tuple[str, str]], out: list[str]) -> None:
    """Render the discovered roster."""
    for label, _path in suites:
        out.append(f"  {label}")
    out.append(f"{len(suites)} suite(s)")


def main(argv: list[str]) -> int:
    """Dispatch to one census and print it."""
    suites = suite_discovery.discover(corpus.ROOT)
    out: list[str] = []

    if "--tenants" in argv:
        index = store_reach.module_index(corpus.ROOT, promoted.POPULATION)
        render_tenants(tenant_census.census(suites, index), out)
    elif "--pragmas" in argv:
        render_pragmas(suites, out)
    elif "--list" in argv:
        render_list(suites, out)
    else:
        out.append("usage: census_show.py {--tenants|--pragmas|--list}")
        sys.stdout.write("\n".join(out) + "\n")
        return 2

    sys.stdout.write("\n".join(out) + "\n")
    return 0


# ⚑⚑ `--selftest` DELEGATES TO THE SIBLING SUITE RATHER THAN EXITING 0 (⟡last-retire).
# Discovery sees this module as a suite, and a no-op `0` made it report NOTHING — which the
# outcome classifier calls `silent`. Under a bare `touch` that stamped green; a module whose
# cases live in a sibling must RUN that sibling.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import census_show_selftest

        sys.exit(census_show_selftest.selftest())
    sys.exit(main(sys.argv))
