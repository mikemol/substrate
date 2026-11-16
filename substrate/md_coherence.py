# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Compare a plan and a worklist in BOTH directions, reporting three populations and no verdict.

⚑⚑⚑ MUTUAL CONSISTENCY IS NOT COVERAGE, which is why this reports three populations and never
collapses them:

  · **orphans** — in the WORKLIST, never mentioned in the plan. The item has no recorded
    evidence, so its figures are unsourced.
  · **unwitnessed** — in the PLAN, never in the worklist. A measured finding nobody scheduled,
    and the dominant direction when this was first run by hand: three plan items had no todo.
  · **dangling** — a `§N` the worklist cites that the plan does not have as a section. A
    citation to nothing reads as provenance.

⚑⚑ A FALSE DANGLING IS THE WORSE DIRECTION, AND THE ORIGIN MEASURED WHY. The audit's whole value
is that a non-zero count means ACT, so one bogus row teaches the reader to skim it. Keying only on
`^#+ N.` reported `§6d` as a reference to nothing on a citation that was exactly right, because
this corpus numbers sub-findings as BOLD paragraphs — `**6d. Armed but not firing**`, `**9a.**`,
`**7b-bis.**` — a deliberate convention, since a sub-finding is part of its parent's argument.
Both spellings count here, and `-bis` / `-part2` suffixes are admitted because the corpus writes
them.

⚑ SECTION NUMBERS COME FROM THE TEXT, NOT FROM A MARKDOWN AST. Routing this through a pandoc
reader made the whole coherence audit require panflute — and this is precisely the query that must
work in a bare environment, because it is what a GATE would call. The fenced-code hazard an AST
reader exists to dodge cannot arise: a fence containing `### 62. …` is not a thing this corpus
produces.

⚑⚑⚑ AND THE KNOWN DEFECT IS THE POPULATION, NOT THE COMPARISON (gate-F59). Run against ONE
worklist while the tree carries six ledgers, the `unwitnessed` column fills with labels that are
registered and answering elsewhere — `gate-F55` through `gate-F58` all reported as in-plan-with-no-
item while every one of them resolves. So this takes the worklist labels as a SET the caller
assembles from however many ledgers it has, rather than reading one file and calling the remainder
a finding. A reader whose population is narrower than the question asked of it reports its own
boundary as a fact about the subject.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, NamedTuple

from mikemol.mdstruct import labels as md_labels

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

#: A `§N` citation, in either the bare or the sectioned spelling the corpus writes.
CITED = re.compile(r"§(\d{1,2}[a-z]?(?:-\w+)?)")

#: A numbered heading — the ordinary section spelling.
HEADING = re.compile(r"^#+\s+§?(\d{1,2}[a-z]?(?:-\w+)?)\.", re.MULTILINE)

#: A bold sub-finding — the convention that made a correct citation read as dangling.
SUBFINDING = re.compile(r"^\*\*§?(\d{1,2}[a-z]?(?:-\w+)?)\.", re.MULTILINE)


class Report(NamedTuple):
    """Three populations, each a different fact, deliberately not summed.

    ⚑ THE THREE ARE DIFFERENT REPAIRS. An orphan wants evidence written, an unwitnessed finding
    wants scheduling, and a dangling citation wants either a section or a corrected reference.
    A single count would say only that something is wrong.
    """

    orphans: tuple[str, ...]
    unwitnessed: tuple[str, ...]
    dangling: tuple[str, ...]

    @property
    def clean(self) -> bool:
        """Report whether all three populations are empty."""
        return not (self.orphans or self.unwitnessed or self.dangling)

    def why(self) -> str:
        """Return a one-line account naming each non-empty population."""
        parts = [
            f"{len(rows)} {name}"
            for name, rows in (
                ("orphan(s)", self.orphans),
                ("unwitnessed", self.unwitnessed),
                ("dangling", self.dangling),
            )
            if rows
        ]
        return ", ".join(parts) if parts else "coherent in both directions"


def labels(lines: Iterable[str]) -> set[str]:
    """Return every label mentioned anywhere in `lines`.

    ⚑ THE GRAMMAR IS `md_labels`', NEVER RE-DERIVED HERE. That module owns which tokens are
    labels and which are excluded, and a second spelling of the rule is how a family gets dropped
    from one reader while the other still sees it.
    """
    return {label for line in lines for label in md_labels.labels_in(line)}


def sections(text: str) -> set[str]:
    """Return every section number the document DEFINES, in both spellings."""
    return {m.group(1) for m in HEADING.finditer(text)} | {
        m.group(1) for m in SUBFINDING.finditer(text)
    }


def citations(text: str) -> set[str]:
    """Return every section number the document CITES."""
    return {m.group(1) for m in CITED.finditer(text)}


def compare(
    plan_lines: Sequence[str], worklist_labels: Iterable[str], worklist_text: str
) -> Report:
    """Return the three populations, given the plan's lines and the worklist's labels and text.

    ⚑⚑⚑ THE WORKLIST'S LABELS ARE A SET THE CALLER SUPPLIES, WHICH IS THE gate-F59 REPAIR. Reading
    one worklist while the tree carries six ledgers made every label registered elsewhere read as
    unwitnessed, and the fix is not a better reader — it is admitting that the population is the
    caller's to assemble. A reader that owns its own narrower population reports that boundary as
    a fact about the subject.

    ⚑ THE PLAN ARRIVES AS LINES AND THE WORKLIST AS TEXT because they are asked different
    questions: the plan is scanned per line for labels and as a whole for section definitions,
    while the worklist is scanned only for what it cites. Taking both as paths is what made the
    origin untestable.
    """
    plan_labels = labels(plan_lines)
    worklist = set(worklist_labels)
    plan_text = "\n".join(plan_lines)

    return Report(
        orphans=tuple(sorted(worklist - plan_labels)),
        unwitnessed=tuple(sorted(plan_labels - worklist)),
        dangling=tuple(sorted(citations(worklist_text) - sections(plan_text))),
    )
