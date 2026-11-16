#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report whether each witness carries a measured grade rather than a bare pass/fail bit.

⚑⚑⚑ THE ORIGIN'S PREDICATE WAS INERT, AND THE MEASUREMENT IS ONE QUERY. It read
`getattr(fn, "_graded", False)`, and `--literal _graded` finds exactly ONE site in the whole
tree: that read itself. **Nothing sets the attribute anywhere**, so the item reports every witness
ungraded no matter what the tree does — it can neither close nor discriminate. That is the third
instance of the pattern its own docstring names, failing permanently-RED where the other two
failed permanently-green.

⚑⚑ AND THE SUBJECT IS REAL WHILE THE ARTIFACT IS ABSENT. A grade is the engine's ladder rung
(`broken` -1 … `imported` 4), and `behavioral` is established BY MUTATION: corrupt an input, the
check must flip red. That sweep is `paperkit.grader`, it produces grade RECORDS, and this repo has
never run it against its own witnesses — MEASURED: no grade artifact, no reader, no call site.

⚑⚑⚑ SO THE HONEST VERDICT IS UNMEASURED, NOT OPEN-WITH-A-COUNT. Reporting *"N witnesses report a
bit"* would state a population derived from an attribute nobody writes; reporting *"0 ungraded"*
would be worse. **An item whose evidence does not exist is unmeasurable, and saying so is the
finding** — the same disposition `T28-edges` reached when its question turned out to be
unanswerable as posed.

⚑ WHAT WOULD CLOSE IT: running the engine's sweep over this project and reading the records back,
at which point `engine_grades.below(FLOOR)` names exactly which rungs fail and the count becomes
real. That is work, not a wall.

⚑⚑ THE FIGURE COMES FROM `warrant_records` AND THE EXCEPTION FROM `warrant_bib` (gate-G209). The
engine half — `records` / `claim_of` / `tag` — imports paperkit at module scope and lives in its
own module; `WarrantError` stays with the config half precisely so a caller catching it need not
import the engine to name the exception it is catching. Reading both from one module is what made
`scratch/bibstruct.py` unreachable in every mode without a paperkit venv.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.witness import witness_row
from mikemol.witness.warrant_bib import WarrantError

from substrate import corpus, engine_grades, warrant_records

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

# Where a mutation sweep would deposit its per-claim grade records. ⚑ NAMED SO THE ABSENCE IS
# CHECKABLE: a witness that merely said "no grades" could not be distinguished from one that never
# looked, and the path is what makes the claim falsifiable when the sweep does run.
RECORDS = ("catalog", "worklist", "grades.json")


def records_path(root: Path | None = None) -> Path:
    """Return where this project's grade records would live."""
    return (root if root is not None else corpus.ROOT).joinpath(*RECORDS)


def graded() -> tuple[bool, str]:
    """Report whether measured grades are available, and why when they are not.

    ⚑ TWO FACTS, NOT ONE FLAG. *"the sweep has not run"* and *"the sweep ran and every witness is
    ungraded"* call for entirely different work, and a bare boolean makes them the same row.
    """
    where = records_path()
    if not where.exists():
        return False, (
            f"no grade records at {'/'.join(RECORDS)} — the engine's mutation sweep "
            f"has not run against this project's witnesses"
        )
    return True, ""


def witness(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the verdict for witnesses carrying a measured grade."""
    available, why = graded()
    if not available:
        # ⚑ UNMEASURED, NOT SATISFIED, AND NOT A COUNT. The origin emitted a population read off
        # an attribute nothing writes; the honest report is that the evidence does not exist.
        yield witness_row.part(
            key, "/".join(RECORDS), route="run the engine's mutation sweep over this project"
        )
        yield witness_row.opened(
            key,
            f"{why} — the claim is UNMEASURED, not satisfied. A grade is established by "
            f"MUTATION (corrupt the input, the check must flip red), which is the mechanism "
            f"that finds an inert predicate without someone happening to notice an "
            f"implausible number",
        )
        return

    try:
        want = warrant_records.tag(key, figure)
    except WarrantError as exc:
        yield witness_row.opened(key, f"the claim carries no [{figure}=N] tag: {exc}")
        return

    # ⚑ THE FAILING RUNGS ARE DERIVED FROM THE ENGINE, never listed here. A local blacklist would
    # admit every future rung by default — the engine's own argument for `below`.
    failing = engine_grades.below()
    yield witness_row.opened(
        key,
        f"grade records exist but no reader consumes them yet; the rungs below "
        f"{engine_grades.FLOOR} are {', '.join(failing)} and the claim expects {want}",
    )
