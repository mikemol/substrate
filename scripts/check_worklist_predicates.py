#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""check_worklist_predicates.py — a worklist item must point at something that still EXISTS.

⚑⚑⚑ THIS IS A REFUSAL, NOT A RATCHET, AND THE DIFFERENCE IS THE WHOLE DESIGN. A paydown-only
baseline is right for accumulated debt nobody can clear at once — the ban census, the rederive
census. A stale predicate is not debt: it is an item whose artifact was deleted or moved, and the
repair is to re-point the item, which is one edit. Banking a baseline here would make the first
stale predicate permanent by construction, so the population must be EMPTY and the gate says so.

⚑⚑ AND IT REFUSES ON A NARROWER CLASS THAN "OPEN", WHICH IS THE OPERATOR'S RULING. `gate-F93`
measured that `scripts/worklist.py --check` computes its offender list into a dead binding and
exits 0 unconditionally, so its silence was a fact about the census rather than the tree. The
ruling was to refuse — but on items whose predicate no longer RESOLVES, never on items that are
merely still open. An OPEN item with a live artifact predicate is the ordinary state of a work
list, and a gate refusing on that would refuse every commit forever.

⚑⚑⚑ THE DISTINCTION IS UNREPRESENTABLE IN THE TOOL THIS GATE COVERS, which is why the reader is
a separate module. `worklist.py`'s `status()` collapses every failure onto `False` = OPEN: its
`_defines` and `_grep` both return False on `OSError`, so *the file is gone* and *the file is
present and lacks the name* are one answer. `substrate.worklist_predicate` asks the other
question — does the REFERENT exist — and answers RESOLVES / STALE / UNDECIDABLE.

⚑ THE THIRD OUTCOME IS WHY THIS CAN REFUSE SAFELY. `manual` and `cmd0` items are UNDECIDABLE, not
stale, and never reach the refusal: blocking a commit over a human judgement nobody encoded, or
over a shell exit that cannot distinguish *not yet* from *gone*, is precisely the false refusal
the narrow class exists to avoid.

⚑ WHY A NEW FILE RATHER THAN AN EDIT TO `worklist.py`. That module carries findings the per-file
gate refuses every edit over (`swap_readiness scripts/worklist.py`), so the repair could not land
there — and the refusal is a design signal rather than an obstacle: *does the referent exist* is a
different responsibility from *is the item done*, and it belongs in its own module either way.

Usage: check_worklist_predicates.py [--quiet] [--list]
"""

from __future__ import annotations

import sys
from pathlib import Path

from scripts import ratchet
from substrate import worklist_predicate, worklist_roster

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    """Refuse when any worklist item's predicate names an artifact that no longer exists."""
    rc = ratchet.check_argv(sys.argv, {"--quiet", "--list"}, "check_worklist_predicates")
    if rc is not None:
        return int(rc)
    quiet = "--quiet" in sys.argv

    found = worklist_roster.load(ROOT)
    if found is None:
        # ⚑ A ROSTER THAT CANNOT BE READ IS UNMEASURED, NOT CLEAN, and the gate says which. An
        # exit 0 here would report an unreachable roster as a healthy one — the census-green
        # shape this gate exists to remove, committed by the gate itself.
        print("worklist-predicates: the roster could not be READ — UNMEASURED, not clean")  # noqa: T201
        return 1

    stale = worklist_predicate.stale_items(found.items, repo=found.repo, agda=found.agda)
    if not stale:
        if not quiet:
            # ⚑ THE DENOMINATOR TRAVELS WITH THE VERDICT. A bare "none stale" cannot distinguish
            # a total read from a probe that examined nothing, and this gate's whole subject is
            # a silence that meant nothing.
            print(
                f"worklist-predicates: 0 stale of {len(found.items)} item(s) — every "  # noqa: T201
                "predicate still names something that exists"
            )
        return 0

    print(
        f"worklist-predicates: {len(stale)} item(s) point at an artifact that NO LONGER "  # noqa: T201
        f"EXISTS, of {len(found.items)} declared:"
    )
    for sym, detail in stale:
        print(f"    {sym}: {detail}")  # noqa: T201
    print(
        "  ⚑ RE-POINT THE ITEM, do not delete it and do not baseline this. A stale predicate "  # noqa: T201
        "means the item's artifact moved or was removed, so the item can never be discharged "
        "as written — it reads OPEN forever, indistinguishable from work not yet done.\n"
        "  ⚑ THIS GATE REFUSES ONLY ON UNRESOLVABLE PREDICATES, never on merely-open ones. An "
        "OPEN item with a live artifact predicate is the ordinary state of a work list, and a "
        "`manual` or `cmd0` item is UNDECIDABLE and is never reported here."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
