#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The two-lens ratchet over the suite-reach census: did any suite stop reaching its cases.

⚑⚑⚑ THIS IS WHERE ⟡may-write-convention CLOSES. The repair was one character —
`may_write(write)` to `may_write(write=write)` — and `scripts/run_selftests.py` carries 1832
findings, so the per-file gate refused every edit to it, INCLUDING the edit that fixes a live
`TypeError`. The regression was introduced by ⟡gate-island-promote (the facade re-exported a
keyword-only function where a positional one had lived) and it crashed `run_selftests
--selftest`, a Phase A gate.

⚑⚑ UNEDITABLE WAS NOT TERMINAL; IT WAS THE SAME SIGNAL AS EVERYWHERE ELSE IN THIS ARC — the
file is too coarse (operator: *"N-split. In DAG order."*). Three extractions, leaves first:
`reach_verdict` (the classifier, imports nothing), `reach_baseline` (the census format), then
this. The one-character fix arrives here as ordinary code.

⚑⚑⚑ AND THE FIRST CUT OF THIS MODULE DID NOT IMPORT — WHICH IS ⟡the-stranded-extraction IN ITS
SHARPEST FORM. It was written against a HYPOTHESISED callee,
`reach_verdict(label, ran, static, base) -> (kind, detail)`, transcribed from the monolith's
private function. What actually landed in `substrate/reach_verdict.py` is a richer API —
`classify` returning a `Verdict`, plus `regressions` / `may_advance` / `advanced` — so the
import raised `ImportError` at module load and every arm of this module's own suite errored
out. **A clean module nothing imports is not merely orphaned; nothing had ever RUN it**, so the
stranding hid a hard break rather than only deferring a benefit. Wiring the consumer is what
EXECUTES the module, and executing it is what tells you whether it works — the same reason a
census green is a fact about the census.

⚑ THE RATCHET IS THE PREDICATE, NOT AN INEQUALITY AGAINST A STORED MAX. What refuses is
`reach_verdict.classify`'s `shrank`/`unknown` over the PAIR (reached, call-sites); the recorded
row is the last accepted reading that predicate reads next time, and is deliberately NOT a
high-water mark — see `reach_baseline`'s header for why a maximum over suite reach could not be
honest.

⚑⚑⚑ A SUITE THAT DID NOT REPORT IS NOT IN `observed`, AND ITS BASELINE ROW SURVIVES. This is
the single most important property here and it is the opposite of what a naive implementation
does. A `refused`/`silent`/`unfit` suite reached NO countable cases, and recording that as
`reached = 0` would BANK the abort as the new reading — the ratchet would launder exactly the
defect it was built to catch, permanently, on the first run after the incident. So an absent
suite is ABSENT, not zero: its row is carried forward untouched, and the run is already red by
the verdict machinery for a different reason.
"""

from __future__ import annotations

import sys

from substrate.baseline_io import may_write
from substrate.reach_baseline import Reading, read_reach, write_reach
from substrate.reach_verdict import (
    DELETED,
    GREW,
    NEW,
    SHRANK,
    UNKNOWN,
    Verdict,
    advanced,
    classify,
    may_advance,
    regressions,
)
from substrate.reach_verdict import Reading as VerdictReading

# Kinds printed only when not quiet — they are news, not findings.
_INFORMATIONAL = (GREW, DELETED, NEW)

# What a suite reported this run: {label: (reached, static_or_None)}.
Observed = dict[str, Reading]


def _lift(rows: dict[str, Reading]) -> dict[str, VerdictReading]:
    """Lift baseline pairs into the classifier's named row type.

    ⚑ BOTH SIDES SPELL A ROW AS A TWO-TUPLE, so the plain tuples would work by structural
    accident. Naming the type at the boundary is what lets the classifier read `row.reached`
    instead of `row[0]` — the ⟡symbolic-reference-only rule applied to a module seam.
    """
    return {label: VerdictReading(*row) for label, row in rows.items()}


def _classify(observed: Observed, base: dict[str, Reading]) -> dict[str, Verdict]:
    """Return this run's verdict per suite, against the recorded census."""
    baseline = _lift(base)
    return {
        label: classify(label, VerdictReading(*row), baseline)
        for label, row in sorted(observed.items())
    }


def _render(verdicts: dict[str, Verdict], *, quiet: bool) -> None:
    """Print the partition. Refusals print even when quiet."""
    if not quiet:
        for label, verdict in verdicts.items():
            if verdict.kind in _INFORMATIONAL:
                sys.stdout.write(f"  reach {verdict.kind:<8} {label:<42} {verdict.detail}\n")
    for label, verdict in verdicts.items():
        if verdict.kind == SHRANK:
            sys.stdout.write(f"  reach SHRANK   {label:<42} {verdict.detail}\n")
    for label, verdict in verdicts.items():
        if verdict.kind == UNKNOWN:
            sys.stdout.write(f"  reach UNKNOWN  {label:<42} {verdict.detail}\n")


def _refuse(count: int) -> int:
    """Print the refusal and return 1."""
    sys.stdout.write(
        f"selftest-reach: BROKEN — {count} suite(s) reached FEWER cases than "
        f"recorded, with the cases still in the source:\n"
        "  ⚑ THIS IS NOT AN ASSERTION FAILURE. Each suite above printed a GREEN `N/N`;\n"
        "    the loss is in the DENOMINATOR, which no pass count can show. A case\n"
        "    aborted the body (a swallowed exception, an early return) and everything\n"
        "    after it became dead text.\n"
        "  ⚑ DO NOT lower this baseline to make it pass. If the cases were genuinely "
        "deleted,\n    deleting the call sites is what makes the census read `deleted` "
        "instead.\n"
    )
    return 1


def _summarise(observed: Observed) -> None:
    """Print the accepted-run summary, with the boundary of what it counted."""
    known = sum(1 for _r, static in observed.values() if static is not None)
    sys.stdout.write(
        f"selftest-reach: {len(observed)} suite(s) reported a count; {known} classifiable "
        f"by source, {len(observed) - known} not.\n"
        "    ⚑ SUITES THAT DID NOT REPORT ARE ABSENT FROM THIS CENSUS, not zero — they "
        "are\n      caught as `refused`/`silent`/`unfit` by the verdict machinery, and "
        "their\n      recorded reading is carried forward UNCHANGED so an abort cannot "
        "bank itself.\n"
    )


def _record(baseline_path: str, base: dict[str, Reading], observed: Observed) -> None:
    """Write this run's readings over the recorded census.

    ⚑ THE MERGE IS `reach_verdict.advanced`, NOT A DICT SPLAT RE-DERIVED HERE. The
    absent-suite rule — a suite missing from `observed` keeps its row — lives in exactly one
    place, and this seam only lifts into that function's row type and back out again.
    """
    merged = advanced(_lift(base), _lift(observed))
    write_reach(
        baseline_path,
        {
            label: (row.reached, row.static)
            for label, row in merged.items()
            if row.reached is not None
        },
    )


def reach_ratchet(
    observed: Observed, baseline_path: str, *, quiet: bool = False, write: bool | None = None
) -> int:
    """Rule on this run's reach census. 0 = pass, 1 = reach regressed.

    ⚑ WRITING IS OPT-IN VIA THE SHARED RESOLVER, NOT A SECOND CONVENTION. `may_write` is THE
    authority (`SUBSTRATE_RATCHET_WRITE`, set by the commit path), and re-deriving the guard
    here is precisely the opt-out that let `set1_ratchet_cores` bank debt on a plain `--quiet`
    read while six siblings were safe.

    ⚑⚑ `write` IS KEYWORD-ONLY, WHICH IS THE WHOLE POINT OF THE MOVE. The pre-split caller
    passed it positionally into a function that had become keyword-only, and that mismatch is
    the `TypeError` this extraction exists to fix. `FBT001` refuses a boolean positional
    because a bare `reach_ratchet(obs, path, True)` says nothing about what the True means —
    and this particular boolean decides whether a gate WRITES.

    ⚑ THE CENSUS ADVANCES ONLY WHEN NOTHING REGRESSED, mirroring `set_ratchet`'s rule that
    paydown cannot record while a new key is present. Recording a mixed run would bank the
    growth and leave the regression un-refusable next time.
    """
    permitted = may_write(write=write)
    base = read_reach(baseline_path)
    verdicts = _classify(observed, base)

    _render(verdicts, quiet=quiet)

    if may_advance(verdicts) and permitted:
        _record(baseline_path, base, observed)

    refusing = regressions(verdicts)
    if refusing:
        return _refuse(len(refusing))
    if not quiet:
        _summarise(observed)
    return 0
