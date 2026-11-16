#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""REACHES-A-STORE against DECLARES-A-TENANT — the falsifiable field, as a four-cell table.

⚑⚑⚑ THE FIELD IS FALSIFIABLE IN BOTH DIRECTIONS, WHICH IS WHAT MAKES IT A MEASUREMENT RATHER
THAN A ROSTER. OWED is a suite that reaches a store and declares nothing; STRAY is a suite that
declares a tenant and reaches no store — a declaration that is WRONG. A census that could only
report the first would be a to-do list; one that reports both can be contradicted by the tree.

⚑ OWED IS NOT A WARNING. The tenant resolver EXITS 2 on an unstated tenant, so each OWED suite
ABORTS MID-RUN if its path reaches the resolver — visible in the strongest possible sense, and
typed `refused` rather than `silent`.

⚑⚑ REACH IS MEASURED BY IMPORT CLOSURE, AND THAT BOUNDARY IS PRINTED WITH THE COUNT RATHER
THAN LEFT IN A DOCSTRING. A tool that opens a store WITHOUT importing a seed — a raw driver
call, or an inlined conditional connect — is NOT COUNTED. That is not hypothetical: exactly
such a store-reacher was measured, invisible to every import-shaped probe. A reader acting on
"0 OWED" must see that the zero is a statement about IMPORT EDGES.

⚑⚑⚑ SO NO BASELINE IS TAKEN OVER THIS CENSUS, AND THE REFUSAL NAMES ITS SUCCESSOR. Two static
readings were available and NEITHER qualifies, for OPPOSITE reasons. Strict-only would certify
away a real reacher. The union admits a suite that reading establishes is NOT one — buying a
false positive to catch a true one, and still blind to a seedless opener. Both are SOURCE
censuses sharing one blind spot, so they are CORRELATED INSTRUMENTS: their agreement is not
coverage.

⚑ THE STEP THIS OWES IS A RUNTIME LENS, NOT A THIRD STATIC ONE. The tenant resolver and the
two connect functions are the only openers; a marker emitted there and read back after a suite
runs answers *did this suite open a store, and which tenant did it name* with no import graph
involved. It would have found the missed reacher on the first run rather than the seventh
careful read.

⚑ A DEFERRED SEED IMPORT IS A CANDIDATE, NOT A DEFECT — AND THE FIRST ONES ADJUDICATED WERE
LOAD-BEARING. A function-local store import is what makes some code TESTABLE: hoisting it would
undo a fix. These rows are a READING LIST, never a repair queue.

⚑ THE LINES ARE RETURNED, NOT PRINTED, so a case can drive them.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from substrate import import_reach, tenant_pragma

# How wide the label column is, so the readings line up under each other.
_LABEL_WIDTH = 42

# How wide the tenant column is, beside a route.
_TENANT_WIDTH = 9

# The boundary this lens cannot see past, printed WITH the count rather than left in prose.
_LENS_BOUNDARY = (
    "    ⚑ REACH IS MEASURED BY IMPORT CLOSURE. A tool that opens a store without\n"
    "      importing one of {seeds} seed module(s) — a raw driver call, or an inlined\n"
    "      conditional connect — is NOT COUNTED here. This reports the import graph,\n"
    "      not store access."
)

# What an OWED row actually costs, in the words that name the fix.
_OWED_NOTE = (
    "    ⚑ OWED is not a warning: the tenant resolver EXITS 2 on an unstated\n"
    "      tenant, so each of these ABORTS mid-run if its path reaches the\n"
    "      resolver. Declare `# selftest-tenant: sandbox` (or `live`) in the\n"
    "      suite, or route the call through the resolver's `require=` form\n"
    "      where the tenant is not the operator's to pick."
)

# Why the deferred-import rows are a reading list rather than a repair queue.
_CUT_HEAD = (
    "  ⚑ DEFERRED SEED IMPORTS — {n} module(s) import a store seed from INSIDE a\n"
    "    function, so import-closure reach CANNOT SEE PAST THEM. Every suite whose\n"
    "    chain runs through one may be under-reported above."
)
_CUT_NOTE = (
    "    ⚑ CANDIDATES, NOT DEFECTS — and the first ones adjudicated were\n"
    "      LOAD-BEARING: a function-local store import is what makes some code\n"
    "      TESTABLE, and hoisting it would undo a fix. A READING LIST, never a\n"
    "      repair queue."
)


@dataclass(frozen=True, slots=True)
class Row:
    """One suite's cell: does it reach a store, and does it say which tenant."""

    label: str
    reaches: bool
    tenant: str | None
    via: tuple[str, ...]

    @property
    def owed(self) -> bool:
        """Reaches a store and declares nothing — this suite ABORTS mid-run."""
        return self.reaches and not self.tenant

    @property
    def stray(self) -> bool:
        """Declares a tenant and reaches no store — a declaration that is WRONG."""
        return bool(self.tenant) and not self.reaches


def rows(suites: list[tuple[str, str]], index: dict[str, Path] | None = None) -> list[Row]:
    """Read every suite's reach and declaration into the four-cell field."""
    table = import_reach.module_index() if index is None else index
    out: list[Row] = []
    for label, path in suites:
        reach = import_reach.store_reach(Path(path), table)
        out.append(
            Row(
                label=label,
                reaches=reach.reaches,
                tenant=tenant_pragma.tenant(path),
                via=tuple(reach.via),
            )
        )
    return out


def _route(via: tuple[str, ...]) -> str:
    """Render the chain by which a suite reaches a store."""
    return "→".join(via)


def lines(suites: list[tuple[str, str]], index: dict[str, Path] | None = None) -> list[str]:
    """Render the field, its counts, and the boundary of what the lens can see."""
    field = rows(suites, index)
    owed = sorted((row.label, row.via) for row in field if row.owed)
    paid = sorted(
        (row.label, row.tenant or "", row.via) for row in field if row.reaches and row.tenant
    )
    stray = sorted((row.label, row.tenant or "") for row in field if row.stray)
    silent = [row for row in field if not row.reaches and not row.tenant]

    out = [f"  OWED       {label:<{_LABEL_WIDTH}} via {_route(via)}" for label, via in owed]
    out += [
        f"  declared   {label:<{_LABEL_WIDTH}} {tenant:<{_TENANT_WIDTH}} via {_route(via)}"
        for label, tenant, via in paid
    ]
    out += [
        f"  STRAY      {label:<{_LABEL_WIDTH}} {tenant} — declares a tenant, reaches no store"
        for label, tenant in stray
    ]
    out.append(
        f"  {len(field)} discovered: {len(owed)} OWED, {len(paid)} declared, "
        f"{len(stray)} STRAY, {len(silent)} reach no store"
    )
    if owed:
        out.append(_OWED_NOTE)
    out.append(_LENS_BOUNDARY.format(seeds=len(import_reach.STORE_SEEDS)))
    return out


def cut_lines(index: dict[str, Path] | None = None) -> list[str]:
    """Render the modules whose deferred seed imports truncate the reach walk.

    ⚑⚑ THE CUTS ARE SCANNED OVER EVERY LOCAL MODULE, NOT JUST THE SUITES, AND THAT IS THE
    WHOLE POINT. The import that once hid several suites lived in a module that HAPPENS to be
    a suite — but nothing makes that necessary. A deferred seed import in ANY module on a
    chain truncates every suite behind it, so restricting this scan to suites would reproduce
    the defect one level out: a census blind exactly where the last one was.
    """
    table = import_reach.module_index() if index is None else index
    cuts = sorted(
        (module, sorted(import_reach.deferred_seed_imports(path)))
        for module, path in table.items()
        if import_reach.deferred_seed_imports(path)
    )
    if not cuts:
        return []
    out = [_CUT_HEAD.format(n=len(cuts))]
    out += [f"    cut  {module:<40} defers {', '.join(seeds)}" for module, seeds in cuts]
    out.append(_CUT_NOTE)
    return out
