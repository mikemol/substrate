#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Ask whether a witness command exits the way its KIND requires, at FILING time.

⚑⚑⚑ THE UNIT IS "POLARITY", NOT "REGISTRATION", AND THAT SPLIT IS THE WHOLE POINT
(Ⓝ137-prime ⟡findings-drain, step 1). The origin's `register` does four things: validate
the kind's SHAPE, probe its POLARITY, render a lambda as source text, and splice that text
into its own file. Only the second is a question about the world; the other three are about
the ledger's storage. Draining them together would carry a self-modifying writer into a
clean module for no reason.

⚑⚑ WHY THIS MODULE EXISTS AT ALL — THE GUARD IS RIGHT AND ITS COVERAGE IS PARTIAL. The
origin probes `refuses:` and `selftest:` and NOT `mode:`, so a `mode:` witness can be born
reporting the opposite of the finding it was filed to hold. That is not hypothetical:
`gate-F55` registered `mode:scratch/findings.py:--register`, whose predicate asserts the
flag is UNDOCUMENTED, against a finding whose whole content is that the flag IS documented
(as a redirect). It registered clean and only a manual run caught it.

⚑ SO `mode` IS PROBED HERE, AND THE PREDICATE IS UNAMBIGUOUS RATHER THAN HEURISTIC. The
origin's `_mode_undocumented` returns 0 on EXACTLY ONE path — the DOCUMENTED branch. Both
"still dispatches undocumented" and "the mode is GONE" return 1, deliberately (a finding is
not closed by the deletion of its subject). So `rc == 0` at filing time means one thing, and
the refusal can say which.

⚑⚑⚑ AND THE BOUNDARY IS STATED RATHER THAN QUIETLY EXCEEDED. This detects WRONG POLARITY,
never "census-ness". Nothing in a command's TEXT distinguishes a census (reports a VALUE,
exits 0 on zero rows exactly as on a hit) from a predicate (reports an EXIT CODE) — so a
static check is impossible in principle, and a census whose zero result happens to exit
non-zero would still register as `refuses:` and still be a category error. What this DOES
guarantee is that no witness is born reporting the opposite of its own finding, which is the
shape that actually cost a false verdict.

⚑ A COMMAND THAT CANNOT RUN IS REFUSED TOO, NOT WAVED THROUGH. `run` returns rc=None when
the process could not start; registering then files a witness that reports 2 forever while
looking mechanical. An absent instrument is not evidence.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

# ⚑ THE KINDS THIS MODULE CAN PROBE, AND IT IS NOT EVERY KIND. `standing` holds at 0
# unconditionally and `unwitnessed` reports 2 by definition, so neither has a polarity a
# command could contradict — probing them would assert a property they do not claim. A kind
# absent from here is UNPROBED, which is a different fact from PROBED-AND-CLEAN, and `probe`
# returns None for both. The caller must not read that None as a pass.
PROBED: tuple[str, ...] = ("refuses", "selftest", "mode")

_REFUSAL_WORDS: tuple[str, ...] = (
    "refus",
    "error",
    "abort",
    "denied",
    "must ",
    "requires",
    "not permitted",
    "unstated",
    "no such",
)


@dataclass(frozen=True)
class Run:
    """Hold one command's outcome. `rc is None` means the process never started."""

    rc: int | None
    out: str


def run(argv: list[str], cwd: str, timeout: int = 300) -> Run:
    """Execute one command. Never raise: a failure to START is a Run with rc=None."""
    try:
        p = subprocess.run(  # noqa: S603
            argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return Run(None, str(e))
    return Run(p.returncode, (p.stdout or "") + (p.stderr or ""))


def evidence(out: str) -> str:
    """Return the line most likely to BE the refusal, not merely the last line printed.

    ⚑ THIS DOES NOT DECIDE A VERDICT AND MUST NOT. Scoring an exit code by message text is
    the confusion the kind split exists to end — a refusal whose wording changes is still a
    refusal. This only chooses which line to QUOTE, so a miss degrades the citation and
    never the finding.
    """
    lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
    if not lines:
        return "(no output — the exit code is the whole evidence)"
    for ln in lines:
        low = ln.lower()
        if any(w in low for w in _REFUSAL_WORDS):
            return ln[:160]
    return f"(no refusal line found; last output: {lines[-1][:110]})"


def _did_not_run(argv: list[str], out: str) -> str:
    """Return the refusal for a command that never started."""
    return (
        "the command for this witness DID NOT RUN, so it would report 2 forever while "
        f"looking mechanical — an absent instrument is not evidence:\n"
        f"    {' '.join(argv)}\n    {out[:200]}"
    )


def _refuses_but_passes(argv: list[str], out: str) -> str:
    """Return the refusal for a `refuses:` command that currently exits 0."""
    return (
        "this `refuses:` command EXITS 0 RIGHT NOW, so the witness would be born reporting "
        f"*the refusal is GONE* about a finding you are filing as true:\n"
        f"    {' '.join(argv)}\n"
        "⚑ TWO CAUSES, AND THEY NEED DIFFERENT ANSWERS. (a) The refusal genuinely is not "
        "installed — then the finding is OPEN and `refuses:` is right but premature. (b) "
        "This is a CENSUS, not a predicate: it reports a VALUE and exits 0 whether it finds "
        "zero rows or many, so no exit code can carry the claim. Its honest kind is "
        "`unwitnessed`, naming the census value as the discriminating quantity no "
        f"registered kind reads.\n    last output: {evidence(out)}"
    )


def _selftest_but_fails(argv: list[str], rc: int, out: str) -> str:
    """Return the refusal for a `selftest:` command that currently exits non-zero."""
    return (
        f"this `selftest:` command EXITS {rc} RIGHT NOW, so the witness would be born "
        "OPEN — file the finding only once the mechanism it asserts actually holds, or use "
        f"`unwitnessed` if no command can carry the claim:\n"
        f"    {' '.join(argv)}\n    {evidence(out)}"
    )


def _mode_wrong_polarity(argv: list[str], out: str) -> str:
    """Return the refusal the origin lacks: `gate-F55` is the measured case for it."""
    return (
        "this `mode:` witness reports DOCUMENTED RIGHT NOW, so it would be born asserting "
        f"the flag is UNDOCUMENTED about a finding you are filing as true:\n"
        f"    {' '.join(argv)}\n"
        "⚑ TWO CAUSES. (a) The mode genuinely IS documented and your finding is about "
        "something else — a flag documented as a REDIRECT is the measured case "
        "(`gate-F55`): the doc is CORRECT and the flag is not dispatched, which no `mode:` "
        "predicate can express. Its honest kind is `unwitnessed`. (b) You named the wrong "
        f"TOOL or FLAG.\n    last output: {evidence(out)}"
    )


def probe(argv: list[str], kind: str, cwd: str) -> str | None:
    """Return None if `argv` exits the way `kind` requires, else a REFUSAL string.

    ⚑ None IS RETURNED FOR TWO DIFFERENT REASONS AND THE CALLER MUST NOT CONFLATE THEM:
    the kind was probed and its polarity is right, OR the kind is not in `PROBED` and no
    polarity claim was made at all. `probes(kind)` is the discriminator.
    """
    if kind not in PROBED:
        return None
    r = run(argv, cwd)
    if r.rc is None:
        return _did_not_run(argv, r.out)
    if kind == "refuses" and r.rc == 0:
        return _refuses_but_passes(argv, r.out)
    if kind == "selftest" and r.rc != 0:
        return _selftest_but_fails(argv, r.rc, r.out)
    if kind == "mode" and r.rc == 0:
        return _mode_wrong_polarity(argv, r.out)
    return None


def probes(kind: str) -> bool:
    """Return whether `kind` carries a polarity this module can contradict."""
    return kind in PROBED
