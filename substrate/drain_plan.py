# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print the drain queue: which candidates can be drained today, cheapest first.

The CLI over `drain_queue`'s join. It takes the candidate population from
`drain_leverage` — the names reached under a `sys.path` insert — and reports them ordered
by what draining each would COST, with the unstartable ones naming the files they wait on.

⚑ THIS IS THE FIRST OUTPUT OF THE DRAIN ARC AN OPERATOR CAN ACT ON. The value ranking says
what draining a name FINISHES and selects the hardest work first; the cost ordering says
what it COSTS and selects what can begin. Neither replaces the other, and this prints the
second because it is the one a plan starts from.

⚑⚑ AND `--blockers` IS THE MODE THAT MATTERS WHEN NOTHING IS STARTABLE, which is the
measured state. It inverts the queue: rather than which drain is cheapest, which FILE's
paydown releases the most drains. The queue's head is a run of one-file one-site drains
whose blockers repeat, so a plan walking the queue pays for each drain separately while a
plan walking the blockers pays once and collects several.

⚑⚑ THE CENSUS RUNS mypy OVER THE CORPUS AND IS SLOW BY CONSTRUCTION. That is the price of
asking the checker rather than keeping a curated list of clean files, which would be a
second authority drifting from the gate the moment anyone edits one. A cached answer here
would be exactly that list under another name.

⚑ AND IT REFUSES RATHER THAN GUESSING WHEN THE CHECKER CANNOT RUN. An absent or failed
mypy makes editability UNKNOWN, and a queue that reported every candidate as startable in
that case would be reading its own blindness as a clean board.
"""

from __future__ import annotations

import sys

from substrate import corpus, drain_blockers, drain_leverage, drain_order, drain_queue

_USAGE = """\
usage: drain_plan.py [--blockers] [--top N] [--all]

Print the sys.path drain queue, most tractable first.

  --blockers  invert it: which FILE's paydown releases the most drains
  --top N     how many rows to print (default 20)
  --all       include candidates blocked by a dirty consumer

⚑ ORDERED BY COST, NOT VALUE. What draining a name RETIRES is `drain_leverage`'s
  question; the two are read together, never summed.
"""

_DEFAULT_TOP = 20


def candidates() -> list[str]:
    """Return the names reached under an insert, as the drain population.

    ⚑ TAKEN FROM THE READER THAT OWNS IT, never re-derived. `drain_leverage.candidates`
    already excludes stdlib and derives the set from the corpus rather than a roster, and
    a second derivation here would be the rival-implementation shape this toolkit files
    most often.
    """
    found = drain_leverage.consumers(drain_leverage.population())
    return sorted(drain_leverage.candidates(found))


def _top(argv: list[str]) -> int | None:
    """Return the row limit, or None when `--top` was given without a number."""
    if "--top" not in argv:
        return _DEFAULT_TOP
    at = argv.index("--top")
    if at + 1 >= len(argv) or not argv[at + 1].isdigit():
        return None
    return int(argv[at + 1])


def main(argv: list[str]) -> int:
    """Print the drain queue, or report why editability cannot be known."""
    if "--help" in argv or "-h" in argv:
        sys.stdout.write(_USAGE)
        return 0

    top = _top(argv)
    if top is None:
        sys.stderr.write("drain_plan: --top needs a number\n")
        return 2

    names = candidates()
    try:
        rows, own = drain_queue.queue(names, corpus.ROOT)
    except drain_queue.CensusUnavailableError as exc:
        sys.stderr.write(f"drain_plan: {exc}\n")
        return 2

    if "--blockers" in argv:
        # ⚑ THE OWN-FINDING COUNT COMES FROM THE SAME CENSUS THE QUEUE ALREADY RAN, so the
        # column costs nothing extra and cannot disagree with the dirty set it annotates.
        # A second run would be two authorities on one question.
        sys.stdout.write(drain_blockers.render(rows, top, own) + "\n")
        return 0

    shown = rows if "--all" in argv else [r for r in rows if r.startable]
    sys.stdout.write(drain_order.render(shown, top) + "\n")
    # ⚑ THE FILTERED VIEW MUST NAME ITS OWN POPULATION, OR IT CONTRADICTS ITSELF. The
    # render counts what it was HANDED, so a startable-only view over a fully-blocked
    # board printed `0 candidate(s)` beside a line saying every candidate is waiting —
    # two sentences about different sets, reading as one. An empty filtered view is a
    # fact about the FILTER until it says how many were filtered out.
    if not shown and rows:
        sys.stdout.write(
            f"   ⚑ 0 of {len(rows)} candidate(s) are startable: each waits on a "
            f"consumer's own paydown. `--blockers` ranks what to pay down first.\n"
        )
    elif not rows:
        sys.stdout.write(
            "   ⚑ no candidates at all — `drain_leverage` found no bare name reached "
            "under an insert, which is a fact about that reader, not an empty tree.\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
