#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Fold per-checker tristates into one verdict, and say what did not run.

⚑⚑ THIS IS A FOLD, AND THE DEFECT IT REPLACES WAS A FIRST-HIT RETURN. `analyze_python`
ran each checker and RETURNED ON THE FIRST `None`, discarding findings an earlier
checker had already produced. MEASURED on `def broken(`: ruff exits 1 with
`invalid-syntax` — a real refusal — and mypy exits 2, honestly UNKNOWN, and the hook
reported UNKNOWN while printing only mypy's report. **A refusal was overwritten by a
later checker's inability to run**, decided by roster order rather than by evidence.

⚑ SO THE COMPOSITE MUST BE ORDER-INDEPENDENT, which is the property this module has
and a first-hit return cannot have. Every arm below is decided from the SET of
outcomes; permuting the roster cannot change the verdict.

⚑⚑⚑ THE THREE ARMS, AND WHY EACH ONE IS NOT THE OTHER TWO.

  * **ANY findings → refuse.** A finding is MONOTONE evidence: a checker ran, saw the
    content, and objected. Nothing an un-run checker might have said can retract that,
    so an UNKNOWN beside it cannot soften the verdict. This is the arm the defect
    inverted.
  * **NO findings, ANY could-not-run → UNKNOWN.** This is the arm that looks like a
    pass and must not be one. A clean read from a PARTIAL roster is a fact about the
    census, not about the file: the checker that did not run is exactly the one that
    might have objected. Reporting `True` here banks partial coverage as a pass —
    `census-green-is-a-fact-about-the-census`, which this repo files more often than
    any other defect. It stays UNKNOWN, so it fails OPEN and ANNOUNCES.
  * **Every checker ran, none objected → clean.** The only verdict that asserts
    coverage, and it now asserts it truthfully.

⚑⚑ THE ALL-UNKNOWN CASE IS NOT A SPECIAL CASE — it falls out of arm two. A roster
where nothing ran has no findings and at least one could-not-run, so it is UNKNOWN and
announces, exactly as before. That the general rule SUBSUMES it is the evidence the
rule is the right one rather than a patch shaped around the instance.

⚑⚑⚑ AND THE BLINDNESS RIDES WITH THE REFUSAL, NOT THROUGH `_announce_inert`. That
notice fires ONCE PER PROCESS (`_PYCHECK_HOOK_NOTIFIED`), which is correct for a
standing condition — the venv is missing, say so once — and WRONG for a per-write
refusal: the second refused file in a session would carry a silent partial-coverage
claim. So arm one appends the blindness to the REPORT, where it is bounded by `clip`
and read at the moment it matters.
"""

from __future__ import annotations

# A checker's outcome, as `run_checker` returns it: the tristate and its report.
Outcome = tuple[bool | None, str]

# What the composite returns: the same shape, one level up.
Composite = tuple[bool | None, str]


def blindness_note(unknown: list[str]) -> str:
    """Return the partial-coverage warning for the checkers in `unknown`, else "".

    ⚑ THE REPORTS, NOT THE NAMES, ARE WHAT A READER CAN ACT ON. `run_checker` already
    renders each `None` as a sentence naming the checker and why it could not run
    (`mypy is not installed in the project venv`, `mypy exited 2: <detail>`), so this
    joins those rather than re-deriving a name from them.

    ⚑⚑ IT SAYS THE COVERAGE IS PARTIAL, WHICH IS THE HALF A BARE LIST WOULD OMIT. An
    author reading a refusal assumes the roster ran; the finding they are looking at is
    real either way, but the ABSENCE of others below it is not evidence of their
    silence. Without this line the refusal makes a coverage claim it cannot support.
    """
    if not unknown:
        return ""
    body = "\n".join(f"    - {u}" for u in unknown)
    return (
        "\n--- coverage ---\n"
        "  ⚑ PARTIAL: this verdict rests on the checkers that RAN. These did not:\n"
        f"{body}\n"
        "    The findings above are real. What those checkers would have said is\n"
        "    UNKNOWN — a clean line below is not evidence they were silent."
    )


def compose(outcomes: list[tuple[str, Outcome]]) -> Composite:
    """Fold `(name, (ok, report))` pairs into one verdict for the file.

    ⚑ ORDER-INDEPENDENT BY CONSTRUCTION: both partitions are built before any arm is
    chosen, so no outcome can pre-empt another by arriving first. That is the whole
    repair — the previous code decided inside the loop.

    ⚑⚑ AN EMPTY ROSTER IS UNKNOWN, NOT CLEAN. Zero checkers finding zero problems is
    the degenerate partial-coverage case, and reading it as a pass would make a
    misconfigured roster indistinguishable from a green one.
    """
    findings = [report for _n, (ok, report) in outcomes if ok is False]
    unknown = [report for _n, (ok, report) in outcomes if ok is None]
    if findings:
        return False, "\n".join(findings) + blindness_note(unknown)
    if unknown:
        # ⚑ THE UNKNOWN REPORTS ARE JOINED RATHER THAN FIRST-WINS, so an inert
        # announcement names EVERY checker that could not run. The previous return
        # showed whichever one the loop reached first.
        return None, "; ".join(unknown)
    if not outcomes:
        return None, "no checker was configured to run"
    return True, ""
