#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Witness a mode that DISPATCHES while appearing in no self-description.

⚑⚑⚑ THE VERDICT USED TO BE A DISJUNCTION, AND NO CARE AT THE FILING SITE COULD FIX IT. The
origin's message read *"<tool> <mode> is documented (or no longer dispatched)"* — one green
covering two OPPOSITE states. `--divergence` lists only tools that HAVE a divergence, so a mode's
absence from that output means either *it is documented* or *the tool, or the mode, is gone*, and
the witness reported both identically. That is `census-green-is-a-fact-about-the-census` written
into the verdict STRING, where the filer cannot reach it: every finding of this kind inherited the
ambiguity no matter how carefully it was registered.

⚑⚑ THE SPLIT USES A SECOND, DECORRELATED LENS. `--divergence` answers *does this mode DIVERGE*;
`--find <mode>` answers *is this mode DECLARED ANYWHERE, and by which tool*. Absence-from-divergence
plus presence-in-find is DOCUMENTED; absence from BOTH is DELETED. Two lenses, because one census
cannot distinguish *nothing to report* from *nothing to read*.

⚑⚑⚑ AND A DELETED MODE IS **OPEN**, NEVER CLOSED. The finding recorded that a CAPABILITY THE TOOL
HAS is undiscoverable, and the repair it names is a usage line. If the mode vanished, the repair
did not land — the subject did. Reading that as closed would let a finding be retired by DELETING
the thing it is about: the cheapest possible false green, and the one a ratchet must never grant.

⚑ THIS IS THE PREDICATE `Ⓝ162⁗ ⟡probe-the-mode-kind` NEEDS, AND THE PROPERTY IS WHY. `CLOSED` is
returned on EXACTLY ONE path — the DOCUMENTED branch. Both *still dispatches undocumented* and
*the mode is GONE* return `OPEN`. So `rc == CLOSED` at filing time means one thing, which is what
makes a registration-time polarity arm a GUARD rather than a heuristic.

⚑⚑ THE RUNNER IS A PARAMETER, AND THE GATE ASKED FOR THAT TOO. A first cut let the suite
monkeypatch the imported `run`, which mypy refused — a module does not export what it imports.
Reading the refusal as a limit would have produced a `# type: ignore`; reading it as a DESIGN
SIGNAL produced injection, which is better on its own terms: the two lenses are this witness's
real dependency, so naming them in the signature makes the seam explicit and lets a case drive
every outcome without reaching into module state that a later case then inherits.

⚑⚑ THE TWO ROW READERS ARE PUBLIC FOR THE SAME REASON. They carry the two defects this module
exists because of, so they ARE the testable surface rather than internals: a helper whose recorded
failure mode must be cased is part of the interface.

⚑ PARSE THE TOOL'S ROWS, NEVER PATTERN-MATCH ITS RENDERING. The origin's first cut substringed the
block for `"UNDOCUMENTED  " + mode + " "` and returned a FALSE ZERO on all three findings it was
written to hold: the rows are column-aligned with a variable run of spaces, so the test matched
nothing while the row sat in the output. A renderer changes its spacing and a substring witness
silently passes. Both readers here split into fields, and the field COUNTS are named rather than
spelled as bare integers — an arity is part of a row's shape, not a magic number.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from substrate.finding_kinds import CLOSED, OPEN, UNRUNNABLE, run

if TYPE_CHECKING:
    from substrate.finding_kinds import Verdict

# The reader that owns the roster-vs-dispatch relation. Re-deriving it here would be a second
# authority for one relation — the divergence question is exactly what this mode computes.
DIVERGENCE = ("python3", "scratch/toolmodes.py", "--divergence")

# The decorrelated second lens: is the mode DECLARED anywhere, and by which tool.
FIND = ("python3", "scratch/toolmodes.py", "--find")

# The row marker `--divergence` uses to open a per-tool block.
TOOL_MARK = "── "

# The field a divergence row leads with when the mode dispatches undeclared.
UNDOCUMENTED = "UNDOCUMENTED"

# A divergence row is `<verdict> <mode> …` — the two fields that reader needs present.
DIVERGENCE_ARITY = 2

# A declaration row is `<mode> on <path> [source] …` — three fields before the optional source.
DECLARATION_ARITY = 3

# What a declaration row means when it names no source for the declaration.
UNSTATED = "(source unstated)"


class Runner(Protocol):
    """How this witness reaches a lens — named so a case can supply one without patching."""

    def __call__(self, *cmd: str) -> tuple[int | None, str]:
        """Return `(rc, output)`, with `rc is None` when the command did not run at all."""
        ...


def diverges(out: str, stem: str, mode: str) -> bool:
    """Report whether `--divergence` carries an UNDOCUMENTED row for this tool and mode.

    ⚑ THE BLOCK STRUCTURE IS LOAD-BEARING. Rows are grouped under a `── <path>` header, so a row
    matching `mode` under a DIFFERENT tool says nothing about this one. Tracking the current
    block is what stops a shared flag spelling (`--check`, `--apply`) answering for every tool
    that declares it.
    """
    in_tool = False
    for line in out.splitlines():
        if line.startswith(TOOL_MARK):
            in_tool = line[len(TOOL_MARK):].strip().endswith(stem)
            continue
        if not in_tool:
            continue
        parts = line.split()
        if len(parts) >= DIVERGENCE_ARITY and parts[0] == UNDOCUMENTED and parts[1] == mode:
            return True
    return False


def declares(parts: list[str], stem: str, mode: str) -> bool:
    """Report whether one `--find` row is THIS tool declaring THIS mode.

    ⚑ EVERY FIELD IS CHECKED, INCLUDING THE PATH. `--find`'s output carries a `⚑ NOT on:` line
    listing every OTHER tool by path, so a test that skips the path match reports a mode as
    declared by the one tool explicitly said not to have it.
    """
    if len(parts) < DECLARATION_ARITY or parts[0] != mode or parts[1] != "on":
        return False
    return Path(parts[2]).name == stem


def declared_by(out: str, stem: str, mode: str) -> str | None:
    """Return the source `--find` credits for this tool's declaration, or None if absent.

    ⚑ PARSE THE ROW, NEVER SUBSTRING THE BLOCK — see `declares` for the negative-list hazard
    that makes the per-field test load-bearing rather than fastidious.
    """
    for line in out.splitlines():
        parts = line.split()
        if declares(parts, stem, mode):
            return parts[DECLARATION_ARITY] if len(parts) > DECLARATION_ARITY else UNSTATED
    return None


def mode_undocumented(tool: str, mode: str, runner: Runner = run) -> Verdict:
    """Report OPEN while `mode` dispatches in `tool` but appears in no self-description.

    Three outcomes, and the third is the reason this reader can be trusted:

    - **OPEN** — the mode still dispatches undocumented (the finding stands), OR the mode is
      GONE (the subject was deleted, so the repair did not land).
    - **CLOSED** — the mode is DECLARED by this tool. The only green path.
    - **UNRUNNABLE** — a lens did not run, so DOCUMENTED cannot be distinguished from DELETED.
      ⚑ Withheld rather than guessed: the whole point of the second lens is that one census
      cannot separate those two, and a lens that failed leaves exactly that gap open.
    """
    rc, out = runner(*DIVERGENCE)
    if rc is None:
        return UNRUNNABLE, f"toolmodes --divergence did not run: {out[:120]}"
    stem = Path(tool).name

    if diverges(out, stem, mode):
        return OPEN, f"{stem} {mode} still dispatches with no self-description"

    # ⚑ REACHING HERE MEANS ONLY "no divergence row", which is the AMBIGUOUS half. The second
    #   lens decides which of the two opposite states produced it.
    rc2, found = runner(*FIND, mode)
    if rc2 is None:
        return UNRUNNABLE, (
            f"{stem} {mode} has no divergence row, but toolmodes --find did not run, so "
            f"DOCUMENTED cannot be distinguished from DELETED: {found[:100]}"
        )

    source = declared_by(found, stem, mode)
    if source is not None:
        return CLOSED, f"{stem} {mode} is DOCUMENTED — declared {source}"

    # ⚑ NOT CLOSED. A finding is not closed by the deletion of its subject.
    return OPEN, (
        f"{stem} {mode} is GONE — no divergence row AND no declaration in toolmodes --find. "
        f"The finding recorded an UNDOCUMENTED CAPABILITY; if the mode was removed, the repair "
        f"it names did not land, the subject did. Re-key or retire this finding deliberately — "
        f"do not read this as documented."
    )
