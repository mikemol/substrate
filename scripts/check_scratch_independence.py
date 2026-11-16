#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""check_scratch_independence.py — Λ8: a promoted project makes NO LIVE scratch/ reference.

⚑⚑⚑ A SHIM. THE GATE LIVES IN THE PACKAGE NOW, IN FIVE MODULES, AND THIS FILE ONLY CALLS IT.
The origin carried 363 per-file-gate findings and so could not be edited — not even the
one-line repair to its own suite that started the ⟡drain-arc (gate-G376). It was drained,
concern by concern, each into a clean module with a differential against THIS file's own
output, and then this file was rewritten whole: the per-file gate judges NEW content, so a
clean shim lands where a patch could not (the `bibstruct` precedent).

  substrate/scratch_refs        what a reference IS — the wide scan, the narrow dependency
                                predicate, and HARD/guarded depth              (gate-G391)
  substrate/scratch_scope       `--scope <dir>… [--quiet] [--mentions]`, read-only (gate-G392)
  substrate/scratch_promotion   `--promotable <dir>`, rule 2 asked of `mypy_census` (gate-G393)
  substrate/scratch_gate        the verdict over the promoted roots            (gate-G394)
  substrate/scratch_cli         the roster and the dispatch, exit codes verbatim (gate-G395)

⚑⚑ THE ROSTER IS `substrate.promoted.ROOTS` — the authority — and it lists `substrate/`, which
the origin's frozen `ROOTS` never did. By ruling (gate-G396) the import predicate was narrowed
to a top-level `scratch` segment first, and the gate now runs over the whole promoted corpus:
its failure count over `substrate/` is the TRIAGE BASELINE, not a regression.

`ROOTS` and `_dep_sites` are re-exported here because three callers still reach them by this
module's name (`check_mypy_ratchet`, `check_scratch_runtime`, `promoted_selftest`); they retire
with those callers' own drains.

USAGE — unchanged; the pre-commit hook spells the gate `--quiet`:
  check_scratch_independence.py [--quiet|--check]     the gate over ROOTS; exit 1 on any ref
  check_scratch_independence.py --promotable <dir>    would promoting <dir> hold? exit 1 on BLOCK
  check_scratch_independence.py --scope <dir>… [--quiet] [--mentions]   read-only; always 0
  check_scratch_independence.py --selftest            the five module suites
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import scratch_cli, scratch_refs
from substrate.promoted import ROOTS

__all__ = ["ROOTS", "_dep_sites", "main"]


def _dep_sites(path: str) -> set[int]:
    """Return one file's dependency lines — the origin's spelling, for its remaining callers."""
    return set(scratch_refs.dependency_sites(Path(path)))


def _selftest() -> int:
    """Run the five module suites that replaced the origin's own."""
    from substrate import (  # noqa: PLC0415 - only the selftest needs the suites
        scratch_cli_selftest,
        scratch_gate_selftest,
        scratch_promotion_selftest,
        scratch_refs_selftest,
        scratch_scope_selftest,
    )

    codes: list[int] = [
        scratch_refs_selftest.selftest(),
        scratch_scope_selftest.selftest(),
        scratch_promotion_selftest.selftest(),
        scratch_gate_selftest.selftest(),
        scratch_cli_selftest.selftest(),
    ]
    return max(codes)


def main(argv: list[str]) -> int:
    """Dispatch to the package, or to the suites."""
    if "--selftest" in argv:
        return _selftest()
    return scratch_cli.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
