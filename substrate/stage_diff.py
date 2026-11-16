#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read an artefact at each stage of a pipeline, so a defect in a SEAM has somewhere to be seen.

⚑⚑⚑ A SUITE OVER ONE STAGE CANNOT SEE A DEFECT THAT LIVES BETWEEN TWO. Measured: a codemod's
transform passed 23/23 while thirteen real files failed, because the defect was in the composition
transform → autofix, and no suite over either half could reach it. The prospective check caught
that the files were broken; it could not say WHICH stage broke them, and two turns went to
inference before one dump settled it in two lines of output.

⚑⚑ SO THIS IS THE INSTRUMENT THAT WAS MISSING, NOT A CONVENIENCE. A pipeline reports its OUTPUT;
a stage census reports what each stage RECEIVED and what it RETURNED, which is the only reading
that attributes a change to a stage. Without it the honest options are to bisect by hand or to
guess, and guessing is what cost the two turns.

⚑⚑⚑ AND IT IS WRITTEN HERE RATHER THAN AS A THROWAWAY PROBE BECAUSE IT ALREADY EARNED ITS KEEP
ONCE AND WAS THROWN AWAY. Operator: *"if you're going to have to write something high-quality
anyway, write it somewhere it can persist."* The version that settled the thirteen files lived in
a session scratchpad and is gone; the next reader hitting a seam would rebuild it from nothing.
**A probe worth running is a suite worth keeping** — a one-off measurement is judgement-in-the-turn
wearing a `.py` extension.

⚑ WHAT IT REPORTS IS PRESENCE AND CHANGE, NEVER A VERDICT. A stage that altered the artefact is
not thereby the culprit — a formatter SHOULD change it. What the reader needs is which stage the
change appeared at, so the question "is this stage allowed to do that" can be asked of the right
one. Reporting a verdict would decide that for them, and it is exactly the judgement a census must
not make.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# How many diff lines to carry per stage, so one large rewrite cannot bury the others.
DIFF_LINES = 12

# What a probe is reported as when the caller asked about a needle.
PRESENT = "present"
ABSENT = "ABSENT"


@dataclass(frozen=True, slots=True)
class Stage:
    """One named step of a pipeline, and the function that performs it."""

    name: str
    apply: Callable[[str], str]


@dataclass(frozen=True, slots=True)
class Step:
    """What one stage received and returned, and whether it changed anything."""

    name: str
    before: str
    after: str

    @property
    def changed(self) -> bool:
        """Report whether this stage altered the artefact at all."""
        return self.before != self.after

    @property
    def delta(self) -> int:
        """Return the line-count change this stage made, signed."""
        return len(self.after.splitlines()) - len(self.before.splitlines())

    def diff(self, limit: int = DIFF_LINES) -> tuple[str, ...]:
        """Return this stage's unified diff, bounded.

        ⚑ BOUNDED PER STAGE, NOT OVERALL. A formatter that rewrites a whole file would otherwise
        consume the budget and hide the one-line change a later stage made — which is the reading
        this instrument exists to produce.
        """
        lines = difflib.unified_diff(
            self.before.splitlines(),
            self.after.splitlines(),
            fromfile=f"before {self.name}",
            tofile=f"after {self.name}",
            lineterm="",
        )
        return tuple(list(lines)[:limit])

    def holds(self, needle: str) -> tuple[str, str]:
        """Return whether `needle` is in this stage's input and its output.

        ⚑⚑ THE PAIR IS THE POINT. `present → ABSENT` names the stage that REMOVED something, which
        is how `ruff --fix` was found deleting an import a transform had just added — a fact no
        end-to-end output could report, because the artefact simply never had it.
        """
        return (
            PRESENT if needle in self.before else ABSENT,
            PRESENT if needle in self.after else ABSENT,
        )


def run(source: str, stages: Sequence[Stage]) -> tuple[Step, ...]:
    """Return what each stage received and returned, threading the artefact through in order."""
    steps: list[Step] = []
    current = source
    for stage in stages:
        produced = stage.apply(current)
        steps.append(Step(name=stage.name, before=current, after=produced))
        current = produced
    return tuple(steps)


def changed_at(steps: Sequence[Step]) -> tuple[str, ...]:
    """Return the names of the stages that altered the artefact."""
    return tuple(step.name for step in steps if step.changed)


def lost_at(steps: Sequence[Step], needle: str) -> tuple[str, ...]:
    """Return the stages where `needle` went from present to absent.

    ⚑ THE QUESTION THAT COST TWO TURNS. *"The import is in the output of the transform and not in
    the final file"* is answerable end-to-end; *"which stage removed it"* is not, and only the
    second says what to fix.
    """
    return tuple(step.name for step in steps if needle in step.before and needle not in step.after)


def gained_at(steps: Sequence[Step], needle: str) -> tuple[str, ...]:
    """Return the stages where `needle` went from absent to present."""
    return tuple(step.name for step in steps if needle not in step.before and needle in step.after)


def render(steps: Sequence[Step], needles: Sequence[str] = ()) -> str:
    """Return the stage census as a reader sees it."""
    out: list[str] = []
    for step in steps:
        mark = "CHANGED" if step.changed else "unchanged"
        out.append(f"\n── {step.name:<20} {mark:<10} {step.delta:+d} line(s)")
        for needle in needles:
            was, now = step.holds(needle)
            arrow = "→" if was == now else "⚑ →"
            out.append(f"     {needle!r:<44} {was} {arrow} {now}")
        out.extend(f"     {line}" for line in step.diff())
    touched = changed_at(steps)
    out.append(
        f"\n{len(steps)} stage(s); {len(touched)} changed the artefact"
        f"{': ' + ', '.join(touched) if touched else ''}"
    )
    out.append(
        "   ⚑ A STAGE THAT CHANGED IT IS NOT THEREBY THE CULPRIT — a formatter SHOULD. "
        "This says WHERE\n     a change appeared, so the question of whether that stage "
        "may make it is asked of the\n     right one."
    )
    return "\n".join(out)
