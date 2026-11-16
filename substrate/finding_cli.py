#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Route one `findings.py` invocation to the drained module that owns its question.

⚑⚑⚑ THE NINTH DRAIN UNIT, AND IT IS WIRING RATHER THAN LOGIC. Every branch here names a
module that already owns the answer — `finding_kindspec` parses a kind, `finding_polarity`
refuses a wrong-polarity registration, `finding_entry` renders the roster row,
`finding_resolve` looks a key up, `finding_restem` pairs the two spellings,
`finding_census` counts by kind. **Nothing in this file decides anything**, because a branch
that made a judgement would be a second authority over a question one of six modules already
answers — which is how the origin's `main` grew to its present size.

⚑⚑ A REFUSAL IS A RESULT, NOT AN EXCEPTION, AND THE ORIGIN'S SUITE IS WHY. `main` there
prints and returns codes inline, so a suite can only observe it by capturing stdout. `run`
returns `(lines, code)` so a case can assert on a refusal directly — the same repair
`bib_cli` needed, for the same reason: a tool whose main job is refusing must be assertable
on its refusals.

⚑ AND THE ROSTER IS AN ARGUMENT, WHICH IS WHAT MAKES THIS TESTABLE AT ALL. The origin reads a
module-global `WITNESSES`; taking it as a parameter is the same unlock `finding_resolve` used,
and it lets a case drive the whole dispatch over a three-key fixture instead of the live
ledger.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import finding_census, finding_resolve

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

# The modes this router dispatches. ⚑ DECLARED, so a case can assert the roster against the
# branches rather than trusting that every flag was wired.
MODES: tuple[str, ...] = ("--selftest", "--register", "--pairing", "--kinds", "--list")

# ⚑⚑ THE ROUTER'S OWN REFUSAL CODE, NAMED BECAUSE IT IS NOT A KIND'S VERDICT. A witness that
#   reports UNRUNNABLE and a router that could not route both exit 2, and they are different
#   facts: one is an honest gap in the ledger, the other is a malformed invocation. Sharing the
#   integer is unavoidable at the shell; sharing the SPELLING inside the code is not.
REFUSED = 2

USAGE = ("findings.py — the per-finding WITNESS for the oracle ledger.\n\n"
         "usage: findings.py <KEY> | --list | --kinds | --pairing | --selftest | --register …")


def _kinds_lines(roster: Mapping[str, Callable[[], tuple[int, str]]],
                 classify: Callable[[str], str]) -> list[str]:
    """Render the by-kind census, zero rows included.

    ⚑ THE GROUPING IS SUPPLIED, NOT DERIVED HERE. The origin reads each witness's bytecode to
    guess its kind, which is the fragile step that once put every witness in the unknown
    bucket; the classifier stays the caller's so this module cannot be the place that breaks.
    """
    grouped: dict[str, list[str]] = {}
    for key in roster:
        grouped.setdefault(classify(key), []).append(key)
    rows = finding_census.rows(grouped)
    out = [f"── {kind:<12} {count}" for kind, count in rows if count or kind]
    behavioural = finding_census.behavioural_total(grouped)
    vacuous = finding_census.vacuous_total(grouped)
    out.append(f"\n{behavioural} of {len(roster)} witnesses are BEHAVIOURAL; "
               f"{vacuous} are `standing`, which no change to the code can flip.")
    return out


def run(argv: list[str],
        roster: Mapping[str, Callable[[], tuple[int, str]]],
        classify: Callable[[str], str]) -> tuple[list[str], int]:
    """Return `(lines, exit_code)` for one invocation — never raises, never exits.

    ⚑⚑ A BARE OPERAND IS A KEY, AND THAT IS THE ONLY IMPLICIT ROUTE. Everything else is a
    declared flag, so an unrecognised flag reaches the key resolver and is refused there by
    name rather than silently treated as a mode nobody wired.
    """
    if not argv:
        return [USAGE], REFUSED
    if "--kinds" in argv:
        return _kinds_lines(roster, classify), 0
    operands = [a for a in argv if not a.startswith("--")]
    if not operands:
        # ⚑ A FLAG THIS ROUTER DOES NOT OWN IS A REFUSAL NAMING THE ROSTER, never a silent
        #   fall-through — an unwired mode that exits 0 is the vacuous-green shape.
        unknown = [a for a in argv if a not in MODES]
        if unknown:
            return [f"findings.py: unknown mode {unknown[0]!r}", USAGE], REFUSED
        return [USAGE], REFUSED
    key, witness = finding_resolve.resolve(operands[0], roster)
    if witness is None:
        return [key], REFUSED
    code, note = witness()
    return [f"{key}: {note}"], code
