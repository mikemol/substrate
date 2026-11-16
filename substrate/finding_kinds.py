#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The KIND MACHINERY of the oracle ledger — what makes a witness falsifiable.

⚑⚑⚑ WHY THIS IS A MODULE (gate-G56). `.claude/agents/findings.py` is 7,054 lines and the
per-file gate refuses every edit to it, so five separate findings — gate-G53, gate-G54, and
earlier Ⓝ162⁗ and Ⓝ164 — were filed naming that gate as a wall. That was wrong: this repo has
a PROCEDURE for an unwritable file and has completed it once. `scratch/bibstruct.py` was 2,300
lines carrying 1,367 findings, was drained into seventeen clean modules, and **the gate then
ACCEPTED a whole-file rewrite it had refused to edit**, because the gate judges the NEW content.
Unwritable is the trigger for a drain, never a finding.

⚑⚑ AND THE SHAPE IS NOT `bibstruct`'s, WHICH IS WHY THE FIVE RESTATEMENTS MISREAD IT. Measured
rather than assumed: `module_outline` reports 20 definitions over those 7,054 lines and
`pycodemod --types` reports FOUR mypy codes, so the debt is mechanical ruff style rather than
structural. `pycodemod --binding WITNESSES` reports ONE binding at line 466, live to end of file.
The file is ~470 lines of kind machinery, ~5,900 lines of `WITNESSES` dict literal, and ~700
lines of readers — **a ROSTER SHARING A HOME WITH ITS BODIES**, which is exactly the split
`catalog/library/items.py` already made when its witnesses moved to the keyed library. One
`module_outline` call showed this; quoting the 7,451 figure instead made an easier shape look
like the harder one.

⚑ THIS UNIT IS THE KINDS, AND IT IS THE RIGHT FIRST CUT because it is the half that is CODE.
The eleven builders reach `_run`, `_failing_case` and `_evidence` and nothing else — verified
with `--source` on each, not inferred — so they lift out whole while the roster stays put.

⚑⚑⚑ THE LOAD-BEARING PROPERTY ACROSS EVERY KIND: **A COMMAND THAT CANNOT RUN IS 2, NEVER 0 AND
NEVER 1.** An absent instrument is not evidence. It binds hardest on `refuses`, where a DELETED
command exits non-zero for the wrong reason and would otherwise read as a passing refusal.

⚑⚑ AND THE VERDICT IS DECIDED BY THE EXIT CODE BEFORE ANY TEXT IS READ. `evidence` and
`failing_case` choose which line to QUOTE and never what the verdict IS — scoring an exit code
by message text is the confusion the selftest/refuses split exists to end, so a miss in either
reader degrades the citation and can never move the finding.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

# ⚑ THE LEDGER'S COMMANDS ARE RELATIVE TO THE REPO ROOT, so the runner pins cwd rather than
#   trusting the caller's. A witness that passes from one directory and fails from another is
#   not a witness.
ROOT = Path(__file__).resolve().parent.parent

# How long one witness command may take before it is reported as not having run.
TIMEOUT = 300

Verdict = tuple[int, str]

# ⚑⚑ THE THREE OUTCOMES ARE A VOCABULARY, NOT MAGIC NUMBERS — and naming them is what lets a
#   reader assert on the DISTINCTION rather than on an integer. The origin spells these as bare
#   0/1/2 at every return, so its own suite cannot say "this must not be UNRUNNABLE" without
#   restating the encoding. The per-file gate asked for these by refusing the literals.
# ⚑ AND UNRUNNABLE IS NOT A DEGREE OF OPEN. It is the third outcome: an absent instrument is
#   not evidence either way, which is why it can never collapse into CLOSED or OPEN.
CLOSED = 0
OPEN = 1
UNRUNNABLE = 2

# ⚑ WORDS A REFUSAL ANNOUNCES ITSELF WITH. Not a verdict input — see the module docstring.
_REFUSAL_WORDS: tuple[str, ...] = (
    "refus", "error", "abort", "denied", "must ", "requires", "not permitted",
    "unstated", "no such",
)


def run(*argv: str) -> tuple[int | None, str]:
    """Return `(rc, stdout+stderr)` for one command under ROOT. Never raises.

    ⚑ `rc is None` MEANS THE PROCESS NEVER STARTED, and that is a distinct outcome from any
    exit code it could have produced. Collapsing it into a number is how an absent instrument
    starts reading as a measurement.
    """
    try:
        done = subprocess.run(argv, cwd=ROOT, capture_output=True,  # noqa: S603
                              text=True, timeout=TIMEOUT, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, str(exc)
    return done.returncode, (done.stdout or "") + (done.stderr or "")


def failing_case(out: str) -> str:
    """Return the line most likely to BE the failure, for a suite reporting `n/m` LAST.

    ⚑ THE DUAL OF `evidence`, AND IT NEEDS ITS OWN READER RATHER THAN A SHARED ONE. `evidence`
    hunts the words a REFUSAL uses; a house suite's failing case reads `FAIL <name>: <got> !=
    <want>` and contains none of them, so it would fall through to the same last line the
    repair exists to avoid. Sharing one reader would mean matching a union of vocabularies
    against both, which is how a reader starts quoting a refusal word out of a test name.

    ⚑⚑ AND `tail[-1]` IS RELIABLY WRONG HERE RATHER THAN OCCASIONALLY. The house suites print
    per-case `FAIL <name>: <why>` lines and THEN a `<suite>: n/m` score, so the last non-blank
    line is ALWAYS the score: an auditor is handed arithmetic and never told which case failed,
    while the failure sits on the lines immediately above where `tail[-1]` cannot look.

    ⚑ THE SCORE IS REPORTED ALONGSIDE, NEVER INSTEAD. `n/m` is the only line saying HOW MANY
    failed, so dropping it to show one case trades a useless citation for a partial one.
    """
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines:
        return "(no output — the exit code is the whole evidence)"
    fails = [ln for ln in lines if ln.startswith("FAIL ")]
    score = next((ln for ln in reversed(lines)
                  if "/" in ln and ln.rstrip().rsplit("/", 1)[-1].isdigit()), None)
    if fails:
        more = "" if len(fails) == 1 else f" (+{len(fails) - 1} more failing case(s))"
        tail = "" if not score else f" [{score[:40]}]"
        return f"{fails[0][:140]}{more}{tail}"
    if score:
        return (f"{score[:80]} — ⚑ the suite reported a score but NO `FAIL <case>` line, so "
                "which case failed is not in this output")
    return f"(no FAIL line and no score; last output: {lines[-1][:110]})"


def evidence(out: str) -> str:
    """Return the line most likely to BE the refusal, not merely the last line printed.

    ⚑⚑ THE DEFECT THIS REPLACED WAS `tail[-1]`, MEASURED ON THIS LEDGER'S OWN WITNESSES:
    `sql-F9` exited 2 with a tail of *"pass --dry-run to see WHOSE backend that PID currently
    is"*, and `sql-F38` exited 1 with a tail of `^` — a SQL error caret. Both verdicts were
    RIGHT and both citations USELESS: an auditor sees a plausible sentence that does not
    establish which guard fired, and cannot tell a refusal from an unrelated failure.

    ⚑ A MISS IS FLAGGED RATHER THAN HIDDEN. Falling back to the last line silently would hand
    a reader an incidental line as though it were the guard speaking, which is the defect one
    layer down.
    """
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines:
        return "(no output — the exit code is the whole evidence)"
    for line in lines:
        low = line.lower()
        if any(word in low for word in _REFUSAL_WORDS):
            return line[:160]
    return f"(no refusal line found; last output: {lines[-1][:110]})"


def selftest(cmd: list[str], note: str) -> Verdict:
    """Report CLOSED(0) while `cmd` exits 0 — the witness that a mechanism WORKS.

    ⚑ `mode:` IS NOT THIS, AND THE DIFFERENCE COST A FALSE GREEN. `mode:TOOL:FLAG` asks whether
    a mode is DOCUMENTED, which is the wrong question for a finding about whether a mechanism
    works. Registering `swarm-F12` — the cgroup memory cap is enforced and its abandoned scopes
    are reaped — as `mode:scripts/cgroup-scope:selftest` returned 0 saying *"selftest is
    documented"*: true, unfalsifiable against the claim, and green for an unrelated reason. A
    cap that is SET but NOT ENFORCED would have passed identically.
    """
    code, out = run(*cmd)
    spelled = " ".join(cmd)
    if code is None:
        return UNRUNNABLE, f"{spelled} did not run: {out[:120]}"
    if code == 0:
        return CLOSED, f"{spelled} PASSES — {note}"
    return OPEN, f"{spelled} exits {code} — {failing_case(out)}"


def refuses(cmd: list[str], note: str) -> Verdict:
    """Report CLOSED(0) while `cmd` exits NON-ZERO — the witness for an installed REFUSAL.

    ⚑⚑ THE EXACT DUAL OF `selftest`, AND ITS ABSENCE IS WHY A WHOLE CLASS SAT AS `standing`.
    A large share of this ledger asserts that a repair LANDED, and here a repair overwhelmingly
    takes the form of a refusal: `schema.py --cancel` refuses a bare PID, `store.tenant` exits 2
    on an unstated tenant. For each, the mechanism HOLDS precisely when the command FAILS — so
    `selftest:` is unregisterable (it demands 0) and the filer falls back to `standing`, which
    asserts only that the finding is still written down.

    ⚑⚑⚑ EXIT 0 IS THE OPEN VERDICT HERE, AND THE INVERSION IS THE POINT. If the command
    SUCCEEDS the refusal is GONE — reverted, weakened, or routed around — and the finding is
    open. A witness that cannot distinguish those is the vacuity this kind exists to end.
    """
    code, out = run(*cmd)
    spelled = " ".join(cmd)
    if code is None:
        return UNRUNNABLE, f"{spelled} did not run: {out[:120]}"
    if code != 0:
        return CLOSED, f"REFUSES (exit {code}) — {note} — {evidence(out)}"
    return OPEN, (f"{spelled} EXITS 0 — the refusal this finding records is GONE (reverted, "
                  f"weakened or routed around): {note}")


def standing(note: str) -> Verdict:
    """Report a measured FACT, which holds (0) until a measurement overturns it.

    ⚑ VACUOUS BY CONSTRUCTION, AND THE LEDGER SAYS SO IN ITS OWN LEGEND. No change to the code
    can flip this, so it is legitimate ONLY for a measured fact — never for a claim that a
    repair landed, which it cannot see reverted.
    """
    return CLOSED, f"STANDING — {note}"


def unwitnessed(note: str) -> Verdict:
    """Report an honest gap: no command distinguishes true from false. ALWAYS 2.

    ⚑ THE THIRD OUTCOME IS THE WHOLE VALUE. A judgement or a lesson that no command can check
    is not thereby false, and filing it as `standing` would report a gap as a fact.
    """
    return UNRUNNABLE, f"UNWITNESSED — {note}"
