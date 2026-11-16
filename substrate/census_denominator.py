#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which reported totals state their population and which are bare counts.

⚑⚑⚑ THERE ARE NO SWEEPS, ONLY CENSUSES, AND THE DISTINCTION IS TWO FAILURE MODES. A CENSUS has a
denominator, so it can be INCOMPLETE — and incompleteness is a finding, reportable and refusable.
A SWEEP has only a traversal, so it can be BLIND — and **blindness reads as success**, because
nothing separates *"found nothing"* from *"looked at nothing"*. `44 in-place editor(s); 44 armed`
is a census; `2927 unused imports dropped` is a sweep — 2927 of how many?

⚑⚑ THE ORIGIN REFUSED TO REPORT A FIGURE, AND THE REFUSAL WAS CORRECT. Its regex cut matched any
format string containing `"of"` and returned ZERO — on the same day a live sweep was watched
printing `0 dead renaming clause(s) across 0 file(s)`. **A predicate reporting its subject absent
on the day the subject was demonstrated is an inert guard**, and closing the item against that
number would have banked a false zero into a paydown-only baseline: debt that can never
legitimately be paid. It raised instead, and named the missing instrument.

⚑⚑ THIS IS THAT INSTRUMENT, AND IT IS STRUCTURAL BECAUSE THE QUESTION IS. *"Does this print state
its population"* is a question about the ARGUMENTS to a call, not about the text of a file — the
same reason a name in a docstring is not a call. The read walks each reporting call and asks
whether a count-bearing message also carries its denominator.

⚑ THE VERDICT IS A FLOOR, NOT A TOTAL. A message assembled across several statements, or built
from a variable this reader cannot follow, is reported UNDECIDED rather than counted either way —
so the census can be incomplete, which is exactly the property it is measuring for.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved — and
it closes that item's stated blocker rather than restating the refusal.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# The calls that report a result to a reader.
REPORTERS = ("print", "write", "stdout", "stderr")

# A message carries a count when it interpolates a value beside a countable noun, or spells one.
COUNT_RE = re.compile(r"\{[^{}]*\}|%[sd]|\b\d+\b")

# It carries its denominator when it says what the count is OUT OF.
DENOMINATOR_RE = re.compile(r"\bof\b|\bacross\b|\bout of\b|/")


@dataclass(frozen=True, slots=True)
class Report:
    """One reported message, and whether it names its population."""

    path: str
    line: int
    message: str

    @property
    def counts(self) -> bool:
        """Report whether the message carries a count at all."""
        return bool(COUNT_RE.search(self.message))

    @property
    def bounded(self) -> bool:
        """Report whether the message says what the count is out of."""
        return bool(DENOMINATOR_RE.search(self.message))

    @property
    def bare(self) -> bool:
        """Report the defect: a count with no population.

        ⚑ A MESSAGE WITH NO COUNT IS NOT A SWEEP. Prose, a header, a path — none of them owe a
        denominator, and flagging them would bury the rows that do.
        """
        return self.counts and not self.bounded


def _message(node: ast.Call) -> str | None:
    """Return the literal text a reporting call emits, or None when it is not decidable.

    ⚑ UNDECIDABLE IS NOT COMPLIANT. A message built from a variable, or joined across statements,
    cannot be read here — and guessing either way is what produced the false zero this module
    replaces.
    """
    if not node.args:
        return None
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        return first.value
    if isinstance(first, ast.JoinedStr):
        parts = []
        for piece in first.values:
            if isinstance(piece, ast.Constant) and isinstance(piece.value, str):
                parts.append(piece.value)
            else:
                parts.append("{}")
        return "".join(parts)
    return None


def _reports(node: ast.Call) -> bool:
    """Report whether a call emits to a reader."""
    target = node.func
    if isinstance(target, ast.Name):
        return target.id in REPORTERS
    if isinstance(target, ast.Attribute):
        holder = target.value
        holder_name = (
            holder.attr
            if isinstance(holder, ast.Attribute)
            else (holder.id if isinstance(holder, ast.Name) else "")
        )
        return target.attr in REPORTERS or holder_name in REPORTERS
    return False


def reports(path: Path, label: str) -> tuple[Report, ...]:
    """Read every decidable reporting message in one file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (OSError, SyntaxError):
        return ()

    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _reports(node):
            continue
        text = _message(node)
        if text is not None:
            out.append(Report(path=label, line=node.lineno, message=text))
    return tuple(out)


def bare(rows: tuple[Report, ...]) -> tuple[Report, ...]:
    """Return the counts reported without a population."""
    return tuple(row for row in rows if row.bare)


def render(rows: tuple[Report, ...], label: str) -> str:
    """Render the census — with its own denominator, necessarily."""
    if not rows:
        return f"  {label}: no decidable report — UNMEASURED, not clean"

    counting = tuple(row for row in rows if row.counts)
    missing = bare(rows)
    if not missing:
        return (
            f"  {label}: {len(counting)} of {len(counting)} counting report(s) "
            f"state their population"
        )

    out = [f"  {label}: {len(missing)} of {len(counting)} counting report(s) are bare:"]
    out.extend(f"    ⚑ {row.path}:{row.line}  {row.message.strip()[:72]}" for row in missing)
    return "\n".join(out)


if __name__ == "__main__":
    from substrate import corpus

    _target = sys.argv[1] if len(sys.argv) > 1 else "scratch/drop_dead_renames.py"
    _rows = reports(corpus.ROOT / _target, _target)
    sys.stdout.write(render(_rows, _target) + "\n")
    sys.exit(0)
