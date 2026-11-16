#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Drive a catalog generation: build the store once, then render each requested target.

⚑⚑⚑ THIS IS THE `generate` CAPABILITY THE THREE CONSUMERS ACTUALLY BIND, AND NOTHING ELSE.
`scripts/gen_catalog.py`, `scripts/gen_reuse_index.py` and `scripts/gen_reuse_graph.py` each
import exactly one name from `scripts/reuse_catalog.py` — `generate` — and each passes only a
path filter, a target tuple, and a rebuild flag. The module they import is ~810 lines holding a
sqlite DDL string, five renderer bodies, an `.agdai` walk and a core deserializer; the cut is the
DRIVER, because the driver is the whole of what they bind.

⚑⚑ THE STEPS ARRIVE BY INJECTION, WHICH IS WHAT LETS THIS MODULE BE CLEAN AT ALL. Building the
projection needs `sppf_db`, connecting needs `store`, and every renderer needs `query_builders` —
all of them reached in the superseded module through four separate `sys.path` inserts into
`jea/metalanguage` and `scripts`. A driver that named any of them would inherit that hub and
could not pass this tree's per-file gate. Taking them as arguments moves the impurity to the
caller that already has it, and leaves the ORDER — the part that is actually the capability —
checkable with no store, no cores and no postgres.

⚑⚑⚑ AND THE SUPERSEDED `generate` CANNOT REACH ITS OWN RENDERERS. It calls
`_db_tier_unported("rendering the catalogs")` UNCONDITIONALLY, before the render loop, and that
function raises `SystemExit`. So every invocation of that driver refuses, on every path, for
every target — the renderers below it are unreachable through the only entry point that names
them. `ruff --select F821` confirms the loop past that refusal is dead code twice over: it reads
a name `con` that is bound nowhere in the function. The refusal is honest about the sqlite tier
being unported; what it is not honest about is being scoped, and the prose above it says the
renderers are unaffected while the code puts the refusal in front of all five.

⚑⚑ SO `render` TAKES THE REFUSAL AS AN INJECTED STEP TOO, RATHER THAN HARD-CODING EITHER ANSWER.
Deciding here that the tier is unported would freeze a fact that is owed a repair; deciding here
that it works would silently re-enable a path that writes to a store nobody reads — the failure
the refusal was added to stop, where `sqlite3.connect` CREATED a missing database and reported
success. The driver's job is the sequence; whether a step refuses belongs to the step.

⚑ THE ORDER IS BUILD-THEN-RENDER AND THE BUILD IS SKIPPABLE, which is the one piece of real
sequencing here. `reuse_db` means exactly "skip the rebuild" — it was once an `os.path.exists`
test on a catalog file, a filesystem question standing in for a store question, which stopped
being answerable when the store stopped being a file.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import catalog_targets

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def render(targets: Sequence[str], step: Callable[[str], str]) -> list[str]:
    """Render each requested target through `step`, returning one summary line apiece.

    ⚑ THE TARGETS ARE PLANNED BEFORE ANY STEP RUNS, so a mistyped target refuses BEFORE the
    expensive half rather than after it. The superseded loop indexes its renderer table inside
    the iteration, so a bad fifth target is discovered only once four catalogs have been written
    — work that then has to be judged as partial rather than simply not done.

    ⚑ IT RETURNS THE SUMMARIES RATHER THAN PRINTING THEM. All three consumers print what they get
    back, and a driver that printed would make itself undrivable by a case without capturing
    stdout — the shape that keeps a decision unreachable to anything but a subprocess.
    """
    return [step(t) for t in catalog_targets.plan(tuple(targets))]


def generate(
    targets: Sequence[str] = catalog_targets.DEFAULT,
    *,
    build: Callable[[], list[str]] | None = None,
    step: Callable[[str], str],
) -> list[str]:
    """Build the store (unless skipped), then render every requested target.

    ⚑⚑ `build` IS OPTIONAL AND ITS ABSENCE IS THE SKIP, rather than a separate boolean beside a
    step that is then ignored. A `reuse_db=True` flag passed alongside a live builder gives two
    sources for one decision, and the reader cannot tell which won; passing no builder cannot be
    misread. This is the same collapse `plan` makes for target order — one authority, not two
    spellings that may disagree.

    ⚑ THE TARGETS ARE VALIDATED EVEN WHEN A BUILD IS REQUESTED, and validated FIRST. A driver
    that walked the cores for two minutes and then refused a typo would spend the expensive half
    to report a fact it held before starting.
    """
    planned = catalog_targets.plan(tuple(targets))
    msgs: list[str] = []
    if build is not None:
        msgs.extend(build())
    msgs.extend(step(t) for t in planned)
    return msgs
