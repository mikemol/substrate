#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Count case call sites in a suite's SOURCE — the decorrelated second lens.

⚑⚑ TWO LENSES, AND THEY ANSWER DIFFERENT QUESTIONS. A run reports how many cases it REACHED;
this counts how many the source HOLDS. Their absolute values do not match — a case registered
inside a loop is ONE call site and MANY cases — so neither is a verdict alone. `reach_verdict`
compares each against its OWN history, as deltas, and the pair is what distinguishes an honest
deletion from a run that stopped reaching cases still present.

⚑ UNREADABLE IS `None`, NEVER 0. A zero here would read as "every case was deleted" and label
a genuine fewer-RAN regression as honest paydown — the false-ZERO direction this repo banks
silently. `None` means UNKNOWN and the classifier says so rather than guessing.

⚑⚑⚑ NAMES, NOT ONE NAME — AND THE ROSTER'S OWN COMMENT ONCE COMMITTED THE DEFECT IT CITES.
`census-keyed-on-one-spelling` is this repo's recorded failure, and a census over `check`
alone reads 0 for every suite spelling its helper `_ck` or `case`. The roster was written to
over-admit and then under-admitted by two: `ok` and `chk` were missing until 2026-08-25, and
five suites read a static ZERO purely because of it —

    scripts/ratchet.py     0 -> 55      scratch/tmi_index.py    0 -> 26
    scratch/tmi_status.py  0 -> 51      scratch/tmi_subject.py  0 -> 15
    scratch/prose_apex.py  0 -> 10      (plus mdstruct 69 -> 72)

Three of those were suites the reach ratchet could not classify AT ALL: with a zero static
count, `reach_verdict` cannot tell "the cases were deleted" from "the counter never saw them",
so a drop refuses UNCLASSIFIABLY.

⚑⚑ AND IT HAS UNDER-ADMITTED AGAIN, MEASURED THIS SESSION (⟡case-call-idiom). Every suite
written into `substrate/` reports its failures by appending to a list — `out.append(...)` — and
that spelling is in no roster, so twelve newly-discovered suites read `source now 0`. **A suite
recorded at zero can never regress**, which makes the second lens blind exactly where the
newest code is. `_ACCUMULATOR_CALLS` names that idiom; over-admitting is safe by construction,
because the number is only ever a delta against itself.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡run-selftests-cut). That file carries 1834
findings and the per-file gate refuses every edit to it — including the one-character repair a
live `TypeError` needs. N-splitting it is the route, and this is the next leaf: it imports
nothing but `ast`.
"""

from __future__ import annotations

import ast
from pathlib import Path

# A `check(...)`-shaped call — a case registered by an explicit assertion helper.
_CHECK_CALLS = ("check", "_check", "ck", "_ck", "case", "_case", "expect", "assert_eq", "ok", "chk")

# ⚑ THE ACCUMULATOR IDIOM, ADDED BECAUSE IT WAS MEASURED MISSING. A suite whose arms take an
# `out: list[str]` and append one line per failure registers its cases through `append`, not
# through a named helper. Twelve suites in `substrate/` are written this way and every one
# read a static count of zero.
_ACCUMULATOR_CALLS = ("append",)

CASE_CALLS = (*_CHECK_CALLS, *_ACCUMULATOR_CALLS)

# Parsed counts, keyed by path. A suite's source does not change within one run.
_CACHE: dict[str, int | None] = {}


def _called_name(node: ast.Call) -> str | None:
    """Return the bare name a call invokes, whether attribute or plain."""
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return None


def own_cases(path: str) -> int | None:
    """Return the case call sites in ONE file, or None when it cannot be parsed."""
    if path in _CACHE:
        return _CACHE[path]
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8", errors="replace"), filename=path)
    except (OSError, SyntaxError):
        _CACHE[path] = None
        return None
    n = sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and _called_name(node) in CASE_CALLS
    )
    _CACHE[path] = n
    return n
