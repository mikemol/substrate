#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read `membudget`'s label ledger — the build history of every non-agda leased run.

⚑⚑ THIS IS THE AGGREGATE VANTAGE, AND IT ALREADY EXISTED (operator: *"notice that `make`
stuffs a bunch of stuff into postgres for each agda file. that's not an accident. We can do
the same thing with build history."*). I had claimed a roster runner was needed because *"each
recipe is independent, nothing sees all 140 results"* — false. Every recipe routes through
`membudget run`, which appends a row keyed by LABEL. The cross-suite view is the LEDGER, read
after the fact, not a process that watches the runs happen.

⚑ SO A RUNNER IS NOT THE ONLY THING WITH A WHOLE-ROSTER VIEW, and that is what lets the
dispatch move to `make`: poset-order execution (maximal feasible parallelism, claim-serialized
only where an artefact demands it) with the aggregate read recovered from history rather than
from a total-order walk.

⚑⚑ ABSENCE MEANS "DID NOT PASS", AND THAT IS A PROPERTY OF THE WRITER, NOT AN ASSUMPTION HERE.
`membudget`'s `_record_time` runs only on the success path — a failed or OOM-killed run appends
nothing (its own note: *"a failed/OOM-killed run is not representative"*). So a label with a row
inside the window passed inside the window. ⚑ The converse is WEAKER and must be reported as
such: an absent label is *never ran, ran and failed, or ran before the window* — three causes,
one observation, and naming one would be the unestablished-cause error.

⚑ THE WINDOW IS THE WHOLE POINT. `membudget peaks` aggregates over ALL history, so a suite that
passed once in June reads identical to one that passed this morning. A freshness gate cannot be
built on that. `parse_since` is what makes "did this pass RECENTLY" askable.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path

# Where `membudget` writes it. ⚑ MACHINE-LOCAL AND OUTSIDE THE REPO, deliberately: timing and
# peak-memory are hardware-specific, so this is never committed and never shared between hosts.
# `MEMBUDGET_LABEL_LEDGER` overrides, and the selftest uses that rather than a fixture path
# baked in here.
DEFAULT_LEDGER = Path.home() / ".cache" / "membudget" / "labels.tsv"

# The columns `_record_time` appends, in order. Named so a reader never indexes by number.
_LABEL, _WALL, _PEAK, _STAMP = 0, 1, 2, 3

# ⚑ THE STAMP IS THE LAST COLUMN A WINDOW NEEDS, so a row must reach it to be usable. The two
# trailing fields (user, sys) came later and their absence is fine; a missing stamp is not.
_MIN_FIELDS = _STAMP + 1

# Durations `parse_since` accepts, as seconds. A bare integer is an absolute epoch.
_UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400}

# ⚑ THE MESSAGE IS A CONSTANT so the raise site stays one short line.
_EMPTY_SPEC = "empty since-spec"


@dataclass(frozen=True)
class Run:
    """One recorded run: a label, when it finished, and what it cost.

    ⚑ A ROW WITH NO TIMESTAMP IS NOT RECENT. Rows written before the stamp column existed
    carry an empty field; treating those as epoch-0 keeps them out of every window, which is
    the conservative direction — an unmeasured time must never read as a fresh pass.
    """

    label: str
    stamp: int
    wall: float
    peak: int


def ledger_path() -> Path:
    """Return the ledger `membudget` is writing on this machine."""
    env = os.environ.get("MEMBUDGET_LABEL_LEDGER")
    return Path(env) if env else DEFAULT_LEDGER


def parse_since(spec: str, now: float | None = None) -> int:
    """Turn a window spec into an epoch cutoff: `30m`, `2h`, `7d`, or a bare epoch.

    ⚑ A DURATION IS RELATIVE TO NOW AND AN INTEGER IS ABSOLUTE, because a gate wants the first
    ("passed in the last hour") and a test wants the second (a fixed cutoff over a fixture, so
    the case does not depend on when it runs).
    """
    moment = time.time() if now is None else now
    text = spec.strip()
    if not text:
        raise ValueError(_EMPTY_SPEC)
    unit = _UNITS.get(text[-1])
    if unit is not None:
        return int(moment - float(text[:-1]) * unit)
    return int(text)


def _row(line: str) -> Run | None:
    """Parse one ledger line, or None if it is not a usable row."""
    parts = line.rstrip("\n").split("\t")
    if len(parts) < _MIN_FIELDS or not parts[_LABEL]:
        return None
    try:
        stamp = int(parts[_STAMP]) if parts[_STAMP] else 0
        wall = float(parts[_WALL]) if parts[_WALL] else 0.0
        peak = int(parts[_PEAK]) if parts[_PEAK] else 0
    except ValueError:
        return None
    return Run(parts[_LABEL], stamp, wall, peak)


def runs(path: Path | None = None, prefix: str = "", since: int = 0) -> list[Run]:
    """Return the recorded runs, optionally narrowed by label prefix and by window.

    ⚑ THE PREFIX IS A PREFIX, matching `membudget peaks`, because labels are namespaced
    (`selftest:`, `claim:`, `gate:`, `item:`) and a class of work is exactly what a caller
    wants. A second selector grammar here would be a second spelling of one question.
    """
    src = ledger_path() if path is None else path
    if not src.exists():
        return []
    out = []
    with src.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            run = _row(line)
            if run is None:
                continue
            if prefix and not run.label.startswith(prefix):
                continue
            if run.stamp < since:
                continue
            out.append(run)
    return out


def latest(path: Path | None = None, prefix: str = "", since: int = 0) -> dict[str, Run]:
    """Return the most recent run per label.

    ⚑ THIS IS THE SHAPE A FRESHNESS GATE READS. It asks "did each declared suite pass inside
    the window", which is a question about the LAST run, not about an aggregate — a suite with
    forty stale rows and no fresh one must read as absent, and a max over all history cannot
    say that.
    """
    best: dict[str, Run] = {}
    for run in runs(path, prefix, since):
        held = best.get(run.label)
        if held is None or run.stamp >= held.stamp:
            best[run.label] = run
    return best
