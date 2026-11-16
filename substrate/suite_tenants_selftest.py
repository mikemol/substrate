#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_tenants` — the four cells, and the blind spot printed beside.

⚑⚑⚑ THE LOAD-BEARING ARMS ARE THE TWO FALSIFIABLE CELLS. OWED is a suite that reaches a store
and declares nothing; STRAY is a suite that declares a tenant and reaches no store — a
declaration that is WRONG. A census reporting only the first would be a to-do list; one
reporting both can be CONTRADICTED by the tree, which is what makes it a measurement.

⚑⚑ AND THE BLIND-SPOT ARM IS WHAT KEEPS A ZERO HONEST. Reach here is measured by IMPORT
CLOSURE, so a tool opening a store without importing a seed is not counted — measured, not
hypothesised. A reader acting on "0 OWED" must see that the zero is a statement about import
edges, and a caveat parked in a docstring is exactly the shape that let such a reacher sit
unseen. The note has to be in the OUTPUT, beside the count.

⚑ THE CUT LIST IS A READING LIST, NOT A REPAIR QUEUE. A function-local store import is what
makes some code TESTABLE; hoisting it would undo a fix. The arm checks the rows say so.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import import_reach, suite_tenants

# A store seed every fixture below imports to become a reacher.
_SEED = import_reach.STORE_SEEDS[0]


def _write(root: Path, name: str, body: str) -> tuple[str, str]:
    """Write one fixture suite and return its roster row."""
    path = root / name
    path.write_text(body, encoding="utf-8")
    return (name, str(path))


def _reacher(root: Path, name: str, tenant: str = "") -> tuple[str, str]:
    """Write a suite whose module-level import reaches a store seed."""
    head = f"# selftest-tenant: {tenant}\n" if tenant else ""
    return _write(root, name, f"{head}import {_SEED}\n")


def _text(lines: list[str]) -> str:
    """Render the mode's lines the way a reader sees them."""
    return "\n".join(lines)


def a_reacher_with_no_tenant_is_owed(out: list[str]) -> int:
    """Check a store-reaching suite that declares nothing lands in OWED.

    ⚑ OWED IS NOT A WARNING: the resolver exits 2, so this suite ABORTS mid-run.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _reacher(Path(tmp), "owes.py")
        field = suite_tenants.rows([row], index={})
        if not field[0].owed:
            bad += 1
            out.append(f"selftest: an undeclared reacher was not OWED — {field[0]!r}")
    return bad


def a_reacher_with_a_tenant_is_not_owed(out: list[str]) -> int:
    """Check a store-reaching suite that declares a tenant is settled."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _reacher(Path(tmp), "paid.py", tenant="sandbox")
        field = suite_tenants.rows([row], index={})
        if field[0].owed or field[0].stray:
            bad += 1
            out.append(f"selftest: a declared reacher read owed/stray — {field[0]!r}")
    return bad


def a_declaration_with_no_reach_is_stray(out: list[str]) -> int:
    """Check a suite declaring a tenant it does not need is a STRAY.

    ⚑ THIS IS THE DIRECTION THAT MAKES THE FIELD FALSIFIABLE — a declaration that is WRONG.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _write(Path(tmp), "stray.py", "# selftest-tenant: sandbox\nx = 1\n")
        field = suite_tenants.rows([row], index={})
        if not field[0].stray:
            bad += 1
            out.append(f"selftest: a tenant with no reach was not STRAY — {field[0]!r}")
    return bad


def a_suite_reaching_nothing_and_declaring_nothing_is_quiet(out: list[str]) -> int:
    """Check the fourth cell is neither owed nor stray."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _write(Path(tmp), "quiet.py", "x = 1\n")
        field = suite_tenants.rows([row], index={})
        if field[0].owed or field[0].stray or field[0].reaches:
            bad += 1
            out.append(f"selftest: a store-free suite read {field[0]!r}")
    return bad


def the_owed_row_is_printed_with_its_route(out: list[str]) -> int:
    """Check an OWED row names HOW the suite reaches a store, not just that it does."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _reacher(Path(tmp), "owes.py")
        text = _text(suite_tenants.lines([row], index={}))
        if "OWED" not in text or _SEED not in text:
            bad += 1
            out.append(f"selftest: the OWED row named no route — {text!r}")
    return bad


def an_owed_row_earns_the_abort_warning(out: list[str]) -> int:
    """Check the output says OWED means the suite ABORTS, not that it is untidy."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _reacher(Path(tmp), "owes.py")
        if "ABORTS" not in _text(suite_tenants.lines([row], index={})):
            bad += 1
            out.append("selftest: an OWED census printed no abort warning")
    return bad


def a_clean_field_prints_no_abort_warning(out: list[str]) -> int:
    """Check the warning appears only when something is OWED — the other direction."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _write(Path(tmp), "quiet.py", "x = 1\n")
        if "ABORTS" in _text(suite_tenants.lines([row], index={})):
            bad += 1
            out.append("selftest: a clean field printed the abort warning anyway")
    return bad


def the_lens_boundary_is_printed_with_the_count(out: list[str]) -> int:
    """Check the import-closure boundary is in the OUTPUT, beside the numbers.

    ⚑ A ZERO HERE IS A STATEMENT ABOUT IMPORT EDGES, and a caveat parked in a docstring is
    what let a real store-reacher sit unseen.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        row = _write(Path(tmp), "quiet.py", "x = 1\n")
        text = _text(suite_tenants.lines([row], index={}))
        if "IMPORT CLOSURE" not in text or "NOT COUNTED" not in text:
            bad += 1
            out.append(f"selftest: the lens boundary was not printed — {text!r}")
    return bad


def the_counts_partition_the_population(out: list[str]) -> int:
    """Check every discovered suite lands in exactly one of the four cells."""
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rows = [
            _reacher(root, "owes.py"),
            _reacher(root, "paid.py", tenant="sandbox"),
            _write(root, "stray.py", "# selftest-tenant: live\nx = 1\n"),
            _write(root, "quiet.py", "x = 1\n"),
        ]
        field = suite_tenants.rows(rows, index={})
        cells = (
            sum(1 for row in field if row.owed)
            + sum(1 for row in field if row.stray)
            + sum(1 for row in field if row.reaches and row.tenant)
            + sum(1 for row in field if not row.reaches and not row.tenant)
        )
        if cells != len(rows):
            bad += 1
            out.append(f"selftest: {len(rows)} suites landed in {cells} cells")
    return bad


def an_empty_cut_scan_prints_nothing(out: list[str]) -> int:
    """Check a table with no deferred imports produces no rows rather than an empty header."""
    bad = 0
    if suite_tenants.cut_lines(index={}):
        bad += 1
        out.append("selftest: an empty cut scan still printed a header")
    return bad


def a_deferred_seed_import_is_a_reading_list(out: list[str]) -> int:
    """Check a module deferring a seed import is listed AND named as a candidate.

    ⚑ CANDIDATES, NOT DEFECTS — the first ones adjudicated were LOAD-BEARING.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = root / "cutter.py"
        path.write_text(f"def go():\n    import {_SEED}\n    return {_SEED}\n", encoding="utf-8")
        text = _text(suite_tenants.cut_lines(index={"cutter": path}))
        if "cutter" not in text or "CANDIDATES, NOT DEFECTS" not in text:
            bad += 1
            out.append(f"selftest: the cut list read {text!r}")
    return bad


_ARMS = (
    a_reacher_with_no_tenant_is_owed,
    a_reacher_with_a_tenant_is_not_owed,
    a_declaration_with_no_reach_is_stray,
    a_suite_reaching_nothing_and_declaring_nothing_is_quiet,
    the_owed_row_is_printed_with_its_route,
    an_owed_row_earns_the_abort_warning,
    a_clean_field_prints_no_abort_warning,
    the_lens_boundary_is_printed_with_the_count,
    the_counts_partition_the_population,
    an_empty_cut_scan_prints_nothing,
    a_deferred_seed_import_is_a_reading_list,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-tenants selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-tenants selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO DISCOVERY SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
