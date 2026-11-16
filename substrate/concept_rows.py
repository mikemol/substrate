#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Turn a concept reader's measurement into worklist rows.

⚑⚑⚑ THE EXTRACTED READERS MEASURE; THEY DO NOT REPORT TO THE WORKLIST, AND THAT GAP WAS INVISIBLE
UNTIL THE LIBRARY TRIED TO BIND THEM. Each module built during the split exposes its own reading —
`currency()`, `population()`, `caches()` — plus a `render()` for a human. **None of them exposes
the `witness(key)` the dispatch calls**: `--calls witness` over three of them returns zero defs.
Binding them produced one `Module has no attribute "witness"` per row, which is the checker
reporting a real missing layer rather than a typo.

⚑⚑ SO THE ADAPTER LIVES HERE, ONCE, RATHER THAN AS A METHOD ON EACH READER. Twenty modules each
growing a `witness()` would be twenty edits to files that are currently clean — and each edit is
a whole-file refusal risk under a gate with no partial credit. One module that knows how to turn
a rendering into rows is the same construction the ratchet family already uses: a shared body,
parameterised, rather than a copy per member.

⚑⚑ AND THE VERDICT IS DERIVED FROM THE READING, NEVER RE-COMPUTED. A reader already decides what
its findings are; an adapter that re-judged them would be a second measurement path, and the two
would disagree the first time either was fixed — the derived-view defect this arc found at every
scale. What the adapter adds is the WORKLIST framing: a part per finding, then one verdict.

⚑ AN EMPTY FINDING SET IS NOT AUTOMATICALLY CLOSED. A reader that could not measure reports so in
its own rendering, and this adapter carries that through: the distinction between *nothing found*
and *nothing looked at* is made by the reader and must survive the framing, which is exactly what
a bare `if not findings: closed` would destroy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.witness import witness_row

if TYPE_CHECKING:
    from collections.abc import Iterator

# What a rendering says when the reader could not measure. ⚑ READ FROM THE RENDERINGS, not
# invented: every module in this family spells an unmeasurable state with one of these words, and
# a verdict must not close over a reading that carries one.
UNMEASURED_WORDS = ("UNMEASURED", "UNKNOWN", "UNREAD", "UNEXERCISED", "UNGROUNDED")


@dataclass(frozen=True, slots=True)
class Reading:
    """One reader's measurement, in the shape the worklist needs."""

    # One line per finding — the population a reader must act on.
    findings: tuple[str, ...]
    # The reader's own rendering, carrying its verdict prose.
    summary: str
    # What to do about a finding, when the reader names it.
    route: str = ""

    @property
    def unmeasured(self) -> bool:
        """Report whether the reader says it could not measure.

        ⚑⚑ THE READER DECIDES THIS, NOT THE ADAPTER. An empty finding set means *nothing found*
        for a reader that ran and *nothing looked at* for one that could not — and only the
        reader knows which. Collapsing them here would reintroduce the false green at the exact
        layer built to prevent it.
        """
        return any(word in self.summary for word in UNMEASURED_WORDS)

    @property
    def closed(self) -> bool:
        """Report whether this reading closes its item."""
        return not self.findings and not self.unmeasured


def rows(key: str, reading: Reading) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield a part per finding, then the verdict — the shared body for a concept item.

    ⚑ THE PARTS COME FIRST AND THE VERDICT TRAILS, because a witness knows its verdict only after
    looking. Emitting the verdict first is the count-before-the-walk defect.
    """
    for finding in reading.findings:
        yield witness_row.part(key, finding, route=reading.route or None)

    if reading.unmeasured:
        yield witness_row.opened(key, reading.summary.strip())
        return
    if reading.findings:
        yield witness_row.opened(key, reading.summary.strip())
        return
    yield witness_row.closed(key, reading.summary.strip())


def from_render(
    key: str, summary: str, findings: tuple[str, ...] = (), route: str = ""
) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield rows from a reader's rendering and its findings.

    ⚑ THE CONVENIENCE FORM, so a binding is one call rather than a record construction at every
    site — the rendering is what every reader already produces.
    """
    yield from rows(key, Reading(findings=findings, summary=summary, route=route))


def marked(text: str, marker: str = "⚑") -> tuple[str, ...]:
    """Return the marked finding lines of a rendering.

    ⚑⚑ THE MARKER IS THE READERS' CONVENTION, and reading it is what lets one adapter serve them
    without a per-module extractor. A module prefixes a finding row with the flag and leaves
    summary lines unmarked — so the marked lines ARE the population, stated by the reader rather
    than re-derived here.

    ⚑⚑⚑ AND ONE RENDERER DIVERGED, MEASURED AND REPAIRED (⟡marker-convention). `flag_routing`
    marked only its mentions-only rows and left six unrouted gates PLAIN, so a sweep through this
    reader reported *"no finding"* over a census holding six — while its sibling `universal_flags`,
    built from the same gates, marked every row and reported all six. **The under-report is the
    direction that reads as clean.** Repaired in the RENDERER, with a case pinning it there: a
    second extractor keyed on indentation would be the rival implementation this layer exists to
    avoid.

    ⚑⚑ THE MARKER SAYS *THIS ROW IS A FINDING*; the prose after it says which kind. Expressing a
    distinction by WITHHOLDING the marker overloads it onto two jobs, and a consumer only reads
    one of them — which is exactly how the divergence stayed invisible.

    ⚑ A RENDERING WITH NO MARKED LINE IS NOT THEREBY CLEAN. It may be a clean census or an
    unmeasurable one; `Reading.unmeasured` answers that from the summary, which is why this
    returns only the population and never a verdict.
    """
    return tuple(
        line.strip().removeprefix(marker).strip()
        for line in text.splitlines()
        if line.strip().startswith(marker)
    )
