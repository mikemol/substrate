#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Classify what happened to a suite: which kind of not-ok, from its record and exit code.

⚑ THE RUN LOOP ALREADY KNEW ALL FOUR AND WROTE ONE BIT. `BROKEN`/`ok` went to the ledger, so
nothing downstream could tell a suite whose ASSERTIONS failed from one KILLED BY ITS LEASE
before it could look. MEASURED: `items.py` over a 192MB lease printed `FAILED`; it passes
67/67 at 1024. A session was spent treating a lease finding as a defect.

    ok       — reported N/N.
    cases    — reported N/M with N < M: assertions failed, look at the code.
    vacuous  — reported 0/0: asserted NOTHING (8 assertions that never ran while the gate
               said green).
    unfit    — no counted line AND killed by a signal: a LEASE finding, not a defect.
    refused  — no counted line and exit 2: a GUARD refused the invocation (unknown flag,
               unstated mutation, unstated tenant). The suite DIED ON ITS OWN HARNESS.
    unread   — it PRINTED A COUNT and neither reader could parse it. NOT the same defect as
               `silent`: `silent` sends a reader hunting a missing emitter, `unread` says the
               emitter EXISTS and its spelling is unreadable. Three suites lost 99 green
               assertions this way while being ABSENT from the census that would name them.
    silent   — no counted line, exited normally: printed nothing at all.

⚑ THE ORDER IS LOAD-BEARING. `unread` is tested BEFORE `silent` and AFTER `refused`/`unfit`:
an abort or a lease kill explains the missing record on its own, and an unparseable line does
not outrank a cause that already accounts for the silence. `refused` is tested only when
NOTHING was counted — a suite that emitted a record and then exited 2 reported its cases, so
the numbers are the verdict.

⚑⚑ AND IT IS A MODULE SO A CASE CAN REACH IT. Inline in the run loop this logic was
unreachable from any suite — the same shape that let `rename_at_source` ship a live write-path
bug through a green run. Every branch below is driven by a case.

⚑⚑⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡run-selftests-cut), and the stopping rule is
not "until the file is editable" (operator): **it is until no module can BECOME uneditable.**
A 3380-line file holding the roster, the runner, two censuses, three classifiers and its own
1000-line suite has room to accumulate 1834 findings. A module holding one classifier and its
five constants does not — there is nowhere for that debt to go.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ⚑ A CGROUP KILL IS A SIGNAL, NOT AN EXIT STATUS. `membudget` runs each suite in a
# `systemd-run` scope with `MemoryMax`; exceeding it is SIGKILL (rc -9, or 137 through a
# shell) and a timeout is SIGTERM (-15 / 143). Named rather than inlined because the set is
# the DISCRIMINATOR between "did not fit" and "failed", and a magic tuple at a call site is
# where that distinction rots.
KILL_CODES = (-9, 137, -15, 143)

# ⚑⚑⚑ EXIT 2 IS A REFUSAL, AND IT IS NOT A TEST RESULT. Every guard in this toolkit exits 2
# when the INVOCATION is wrong rather than when a check fails: `check_argv` on an unknown
# flag, `mutating_argv` on an unstated intent, `store.tenant` on an unstated tenant.
#
# ⚑ A SUITE THAT ABORTS IS WORSE THAN ONE THAT FAILS, WHICH IS WHY IT GETS ITS OWN KIND.
# Folded into `silent` it reads as "printed no counted line" — a REPORTING defect, sending a
# reader into the suite hunting a missing emitter. The actual cause is upstream and is not the
# suite's fault at all: a contract it calls refused the process.
REFUSAL_CODE = 2

# ⚑⚑⚑ THE EVIDENCE-OF-INTENT PREDICATE, NOT A SPELLING TABLE. Three suites printed
# `selftest: N of M` — matching neither the typed record nor the `N/M` reader — and all three
# classified `silent`: 15, 33 and 51 green assertions, none read.
#
# ⚑⚑ THE TEMPTING FIX IS THE WRONG ONE. Widening the reader to accept `N of M` converts three
# known instances into a FOURTH ACCEPTED SPELLING and leaves the class exactly as open — the
# next suite spells it `N passed, M total`. The defect is that UNPARSEABLE OUTPUT HAS NO
# VERDICT, not that this particular spelling went unparsed.
#
# ⚑ SO WHAT COUNTS AS EVIDENCE IS A SHAPE, NOT A VOCABULARY: two integers in one line, on a
# line that also names this contract. `N of M`, `N passed, M total`, `N ok / M run`,
# `[12/34] done` all satisfy it and none is listed.
#
# ⚑⚑ CO-OCCURRENCE IN ANY ORDER, AND THE STARVE HARNESS FORCED THAT. A first cut required the
# contract word BEFORE both integers and read `18 cases ok of 20 run` as SILENT — the count
# leads, the word follows. "The word comes first" is itself an unstated spelling rule.
INTENT_WORD = re.compile(r"(?i)\b(selftests?|cases?|passed|tests?|assertions?)\b")
INTENT_ARITY = re.compile(r"\b\d+\b(?:\D+?)\b\d+\b")


@dataclass(frozen=True, slots=True)
class Reported:
    """What a suite's own record said — or that there was no record to read.

    ⚑⚑ `PLR0913` FIRED AN EIGHTH TIME IN THIS ARC AND MEANT THE SAME THING AGAIN: `matched`,
    `ok` and `all_` are ONE value nobody had named. They are only ever read together, they are
    meaningless apart (`ok=3` says nothing without `all_`), and the pre-split signature took
    them as three positionals — `verdict_kind(m, 3, 4, 0)` says nothing at a call site about
    which integer is which.

    ⚑ `matched` IS NOT DERIVABLE FROM THE OTHERS. A suite that reported `0/0` is `vacuous`;
    one that reported nothing is `silent` — and both would present as zeros. The flag is what
    separates a record that says nothing from the absence of a record.
    """

    matched: bool
    ok: int = 0
    all_: int = 0

    @classmethod
    def none(cls) -> Reported:
        """No record was read from this suite's output."""
        return cls(matched=False)


def unreadable_output(out: str, result: re.Pattern[str]) -> str | None:
    """Return the line that emitted an unparseable count, or None.

    ⚑ A LINE, NEVER A BOOLEAN: a bare True cannot be acted on, and the next question is always
    *what did it print*.

    ⚑⚑⚑ IT IS ASKED ONLY WHEN BOTH READERS CAME BACK EMPTY, which is what makes it a
    conjunction rather than a second parser. A suite whose record was read never reaches here,
    so this can neither create nor suppress a verdict on a suite that reported.

    ⚑⚑ LEGITIMATELY-UNCOUNTABLE IS NOT SILENT, AND CONFLATING THEM FIRES ON CORRECT TOOLS.
    `jea_circuit`'s denominator is a keyword-argument DEFAULT and `check_mypy_ratchet`
    registers via bare `cases.append` with no helper — neither has a count to print, so
    NEITHER EMITS THE EVIDENCE and neither is named. The separation is not a carve-out: it
    falls out of the predicate, because a suite producing no count produces no unparsed count.

    ⚑ A DECLARED SKIP IS NOT SILENT EITHER. A suite whose dependency is missing prints SKIP
    and returns True — a DECLARED vacuous pass versus an UNREAD one — and a SKIP line carries
    no two-integer count, so it does not satisfy the evidence half.
    """
    for line in out.splitlines():
        if INTENT_WORD.search(line) and INTENT_ARITY.search(line) and not result.search(line):
            return line.strip()
    return None


def verdict_kind(
    reported: Reported, returncode: int, *, out: str = "", result: re.Pattern[str] | None = None
) -> str:
    """Return which kind of outcome a suite had."""
    if reported.matched:
        if reported.all_ == 0:
            return "vacuous"
        return "cases" if reported.ok != reported.all_ else "ok"
    if returncode in KILL_CODES:
        return "unfit"
    if returncode == REFUSAL_CODE:
        return "refused"
    if result is not None and unreadable_output(out, result):
        return "unread"
    return "silent"
