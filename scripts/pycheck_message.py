#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render a refusal: bound it, count it, and route the reader by the size of the debt.

⚑⚑ A REFUSAL IS A MESSAGE WITH A SIZE, AND THAT MAKES RENDERING ITS OWN
RESPONSIBILITY. The cost lands on the CONSUMER, not the author: a hook refusal is fed
straight back into the session that triggered it, so a verbose gate spends the
reader's context to say what a bounded one would say as well. Nothing in this file
decides a verdict — it decides what a reader is told and what it costs them to be
told it, and those change for entirely different reasons than the verdict does.
"""

from __future__ import annotations

# ⚑⚑ TWO BOUNDS, BECAUSE THE TWO SURFACES HAVE DIFFERENT READERS AND ONE HAD NONE.
# `MAX_LINES` caps the DENY message, which is fed straight back into the session that
# triggered it — the tightest budget, because the reader did not ask for it and cannot
# decline it. `CHECK_FILE_LINES` caps the `--check-file` report, which a reader asked
# for deliberately and can afford more of.
#
# ⚑ MEASURED 2026-08-30: `--check-file` over an unpaid-down 2000-line module emitted
# **398 KB** — roughly a hundred thousand tokens, more than a small context window
# holds, from ONE refusal on ONE file. That path had no bound at all while the deny
# path had `MAX_LINES` from the start, so the mode a reader runs to UNDERSTAND a
# refusal was the unbounded one.
MAX_LINES = 25
CHECK_FILE_LINES = 60

# ⚑⚑ ABOVE THIS MANY FINDINGS, LISTING THEM IS THE WRONG ADVICE. A file with a
# handful of findings wants them fixed; a file with hundreds cannot be made clean in
# one edit at all, and this gate has no partial-credit path — an edit that leaves the
# file dirty is refused too, so staging does not converge. The threshold is where the
# message has to stop enumerating and start routing.
#
# ⚑ THE NUMBER IS A JUDGEMENT AND IS DELIBERATELY LOW. It only decides which ADVICE
# is printed, never a verdict, so erring toward "this needs splitting" costs a reader
# one paragraph and erring the other way costs them a day. Measured 2026-08-30: four
# small correct changes were blocked or abandoned this way, the smallest a
# single-token argv edit that needed an operator to disarm the gate.
PAYABLE_IN_ONE_EDIT = 30


def clip(report: str, limit: int) -> str:
    """Return at most `limit` non-blank lines of `report`, saying what was withheld.

    ⚑ THE COUNT IS REPORTED, NEVER SILENTLY DROPPED. A clipped report that does not
    say it was clipped is a census reporting its own boundary as the subject's — the
    defect this repo files most often. The reader is told exactly how to see the rest.
    """
    lines = [ln for ln in report.splitlines() if ln.strip()]
    if len(lines) <= limit:
        return "\n".join(lines)
    withheld = len(lines) - limit
    shown = lines[:limit]
    shown.append(
        f"  … {withheld} more line(s) withheld. A refusal is fed back into the "
        f"reader's context,\n    so it is BOUNDED — run the checker directly for "
        f"the whole report."
    )
    return "\n".join(shown)


def finding_count(report: str) -> int:
    """Return how many findings a report carries, across both checkers.

    ⚑ COUNTED FROM THE RULE-CODE LINES, not from the total line count, because
    `--pretty` renders each mypy finding across three or four lines and ruff renders a
    source excerpt per finding. A line count would report the RENDERING and call it
    the debt — which is the shape this repo files most often, a measurement of the
    instrument reported as a measurement of the subject.
    """
    lines = report.splitlines()
    ruff = sum(1 for ln in lines if ln.lstrip().startswith("--> "))
    mypy = sum(1 for ln in lines if ": error:" in ln)
    return ruff + mypy


def debt_note(report: str) -> str:
    """Return the paydown routing for a file whose debt exceeds one edit, else "".

    ⚑⚑ THE GATE ALREADY SAID THIS AND NOBODY HEARD IT. Its closing line — *a file too
    large to leave clean in one edit is not a linting problem, it is the per-file gate
    saying the file does too much* — is an INSTRUCTION, and it read as a scolding for
    most of a day before it was acted on. The reason is that it arrived identically
    whether a file had ONE finding or two thousand, so nothing in the message
    distinguished "fix this" from "this file cannot be fixed in one edit."

    ⚑⚑⚑ AND THE INCIDENCE IS INVERTED FROM THE INTENT, WHICH IS THE FINDING (cassian,
    2026-08-30): **a strict bar over an unpaid-down file blocks SMALL correct changes
    more than large risky ones**, because a one-line fix must still clear the whole
    file's debt. Measured four times in one day — a single-token argv change that
    needed an operator to disarm the gate, two ~10-line repairs abandoned, and a
    two-line fix that cost four full-file rewrites. **Staging does not help**: a
    partial edit to a dirty file is refused too, so there is no incremental path. The
    unit of repair is the whole file, always.

    ⚑ SO THE MESSAGE NAMES THE ROUTE ONLY WHEN THE ROUTE IS DIFFERENT. Below the
    threshold the reader fixes what is listed. Above it, listing findings is the wrong
    advice entirely, and the answer — measured by paperkit the same day, against 337
    findings and six edit attempts that landed zero bytes — is to extract the concern
    into a module written clean in ONE pass, leaving the monolith's debt unpaid. Not
    "pay this down"; "do not edit this file for this." This will _require_ _fully_
    splitting the monolith into smaller, independently clean modules; the monolith
    will not be editable until it can be wholly replaced.
    """
    n = finding_count(report)
    if n <= PAYABLE_IN_ONE_EDIT:
        return (
            "\n  ⚑ A file too large to leave clean in one edit is not a linting\n"
            "    problem — it is the per-file gate saying the file does too much."
        )
    return (
        f"\n  ⚑⚑ {n} FINDINGS — THIS FILE CANNOT BE MADE CLEAN IN ONE EDIT, and this\n"
        "    gate has no partial-credit path: an edit that leaves it dirty is refused\n"
        "    too, so staging a fix does not converge. The unit of repair is the WHOLE\n"
        "    file, which is why the CHEAPEST correct changes are the ones most often\n"
        "    abandoned here.\n"
        "  ⚑ DO NOT PAY THIS DOWN TO MAKE YOUR CHANGE. Extract the one concern you\n"
        "    need into a NEW module, written clean in one pass, and let the next\n"
        "    consumer import that instead. The monolith stays dirty; your fix lands.\n"
        "    This will _require_ _fully_ splitting the monolith into smaller,\n"
        "    independently clean modules; the monolith will not be editable until it\n"
        "    can be wholly replaced.\n"
        "  ⚑⚑ BUT IF THE ONLY CONSUMER IS INSIDE THIS FILE, ONE EXTRACTION STRANDS.\n"
        "    Wiring the new module in is an edit to this file, so it is refused too —\n"
        "    and you are left with a clean module nothing imports, which is a\n"
        "    built-then-orphaned rung rather than a repair. When that is the shape,\n"
        "    the move is to keep cutting until the DISPATCH moves out as well, then\n"
        "    RETIRE this file. Extracting one concern is a step; draining the file is\n"
        "    the finish -- the transaction -- and the step is incomplete until the\n"
        "    file is fully drained."
    )


def render(report: str, path: str) -> str:
    """Build the deny message: what was refused, where, and what the bar is.

    ⚑⚑⚑ THIS MESSAGE CITED A GATE THAT DOES NOT EXIST, AND A DENY MESSAGE IS THE WORST
    PLACE FOR A DANGLING POINTER — it is read at the exact moment an author is looking
    for the rule, and it is the only thing they are given. It named
    `scripts/check_ignore_holder.py` as keeping "the ONE sanctioned exception, the numpy
    `Any` boundary" honest by sole-holder + fixed-count. VERIFIED ABSENT 2026-09-02: no
    such file, and `module_importers check_ignore_holder` finds no importer of the name.

    ⚑⚑ AND THE EXEMPTION IT OFFERED DID NOT EXIST AS POLICY EITHER, which is the finding
    rather than the missing file. Establishing that took the config and the tree:

      * `[tool.ruff.lint.per-file-ignores]` carries no `Any` entry at all — every row is
        `S101`/`S603`/`FBT*`/`PLR*`, each scoped to one responsibility.
      * `[tool.mypy]` sets `disallow_any_explicit`, so the word cannot even be SPELLED,
        and its own comment refuses the escape hatch in general: *no
        `[[tool.mypy.overrides]]` section, deliberately … Relief lives on the ENUMERABLE
        side, never on the unenumerable one.*
      * There is no numpy boundary module and no `stubs/numpy`. `files = ["substrate"]`
        is the admitted set, and NOT ONE of numpy's importers is in it — measured with
        `module_importers numpy`. The gate has never once seen numpy.
      * Where the same question was actually ANSWERED — `types-networkx` — the answer was
        a STUB, and its note says why this shape is not a boundary at all: *"that is not
        a walled boundary; it is the interface itself."*

    ⚑ SO THE MESSAGE STOPS OFFERING IT, RATHER THAN RESTATING IT WITHOUT ITS ENFORCER.
    Those are two different repairs and only one is honest here. Naming an escape hatch
    in a refusal INVITES its use — an author who reads "there is one sanctioned
    exception" goes looking for the shape that qualifies, and here every such shape
    resolves to a stub or a per-responsibility entry under review. What the reader needs
    is the ENUMERABLE side's real address, which is the config, not a hatch.

    ⚑⚑ AND `warn_unused_ignores` IS NOT THE MISSING GATE UNDER ANOTHER NAME. It bounds no
    COUNT and enumerates no HOLDER; it only makes an ignore that stopped being
    load-bearing into an error, so the ignore set self-prunes. Recorded because it is the
    nearest live mechanism and would otherwise be promoted into the enforcer nobody wrote.
    """
    body = "\n".join("  " + ln for ln in clip(report, MAX_LINES).splitlines())
    named = path or "this file"
    return (
        f"pycheck: this edit leaves {named} with findings — refusing.\n{body}\n"
        "  ⚑ ZERO TOLERANCE: there is no suppression path, no exclude list, and no\n"
        "    per-file exemption for a finding. `disallow_any_explicit` means `Any`\n"
        "    cannot be spelled, and there is no `[[tool.mypy.overrides]]` section.\n"
        "  ⚑ RELIEF LIVES ON THE ENUMERABLE SIDE ONLY: a STUB that ADDS types for an\n"
        "    untyped dependency (see stubs/), or a per-RESPONSIBILITY entry in\n"
        "    pyproject.toml's per-file-ignores — each naming one file whose single job\n"
        "    is the thing the rule flags. Both are reviewed additions to that file,\n"
        "    not something this refusal grants you."
        f"{debt_note(report)}"
    )
