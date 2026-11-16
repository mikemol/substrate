#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Is every suite ok at its current content state — answered from the build, not by running.

⚑⚑⚑ THIS IS THE BACK-EDGE, EXTRACTED AND CUT (⟡worklist-reads-build). The recursion diagram in
`worklist_gate` names `worklist_gate --selftest` → `run_selftests --quiet` as the cycle, four
generations deep at load 54.93 with 68 concurrent processes. The edge is not a direct call: the
paperkit witness `catalog.library.items.SUITE` imported `run_selftests`, read its ledger, and
**ran the missing suites itself** through `rungs.execute`. A witness was a second dispatcher.

⚑⚑ SO THE FIX IS NOT A BETTER GUARD, IT IS REMOVING THE SECOND DISPATCHER (operator: *"I don't
want any of the tools doing recursive dispatching or running of suites without that rolling
through `make`"*). Two reasons, and the second is the stronger one:

    recursion   a guard at an entry point dies when a new entrance forgets it; there is no
                entrance here at all once the fan-out has one owner.
    parallelism `make` runs the DAG in POSET order at the jobserver's width, with membudget's
                lease and claim gates deciding real concurrency. A hand-rolled loop is a TOTAL
                order — strictly less parallel, and it was never the point of the witness.

⚑⚑⚑ AND THIS MODULE ONLY READS. It cannot start a build, which is what makes it safe to call
from inside a suite: the recursion the guard existed for is not merely guarded here, it is
UNREACHABLE. A reader that could also derive would need the subprocess exemption and would put
a fan-out back inside a witness — the same shape one indirection later.

⚑ THE MEMO CONTRACT IS PRESERVED EXACTLY, because it was always a build system's contract
(user, recorded in the witness this replaces: *"we ought to be able to memoize a witness's
response given its input and its code state. So something stale is just...a cache miss"*). A
suite's verdict is a pure function of its source; the stamp is that memo, keyed by mtime; and
`make` is what derives a miss. The prior implementation carried a per-suite content sha to say
the same thing — a second implementation of what the build already decides.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from mikemol.corpus import suite_discovery

from substrate import corpus, stamp_read

# The generated makefile a reader is pointed at when a stamp is missing.
MAKEFILE = "Selftest.mk"

# The kind that means a suite is fine. Every other kind is reported with its name.
OK = "ok"

# ⚑ NOT ONE OF `suite_outcome`'s SEVEN KINDS, DELIBERATELY. A suite with no fresh stamp has no
# reading at all, and the absence has three causes the stamp cannot separate — never run, ran
# and failed (the wrapper stamps only on success), or cleaned. Folding it into `silent` or
# `cases` would name a cause the evidence does not support.
UNRUN = "unrun"


@dataclass(frozen=True, slots=True)
class Row:
    """One suite's standing: its label, the kind it earned, and whether that reading is fresh."""

    label: str
    kind: str
    fresh: bool


def rows() -> list[Row]:
    """Read every suite's standing from the build's stamps."""
    out = []
    for label, path in suite_discovery.discover(corpus.ROOT):
        stamp = stamp_read.read(label, path)
        if stamp is None or not stamp.fresh:
            out.append(Row(label=label, kind=UNRUN, fresh=False))
        else:
            out.append(Row(label=label, kind=stamp.kind, fresh=True))
    return out


def not_ok(rows_in: list[Row]) -> list[Row]:
    """Return the suites that are not ok — including those with no fresh reading."""
    return [r for r in rows_in if r.kind != OK]


def main(argv: list[str]) -> int:
    """Report every suite's standing from the stamps."""
    del argv
    got = rows()
    bad = not_ok(got)
    for row in bad:
        sys.stdout.write(f"  {row.kind:<10} {row.label}\n")
    sys.stdout.write(f"  {len(got)} suite(s), {len(bad)} not ok\n")
    if not bad:
        return 0
    # ⚑ `unrun` IS REPORTED SEPARATELY FROM A FAILURE KIND, because the next action differs:
    # an unrun suite needs the build, a `cases` suite needs its code read.
    unrun = len([r for r in bad if r.kind == UNRUN])
    sys.stdout.write(
        f"    ⚑ {unrun} have NO fresh reading — run `make -f {MAKEFILE}`;\n"
        f"      the rest carry a kind from their last run.\n"
    )
    return 1


# ⚑⚑ `--selftest` DELEGATES TO THE SIBLING SUITE RATHER THAN EXITING 0 (⟡last-retire).
# Discovery sees this module as a suite, and a no-op `0` would report NOTHING — which the
# outcome classifier calls `silent`, and which a bare stamp could never expose.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import suite_witness_selftest

        sys.exit(suite_witness_selftest.selftest())
    sys.exit(main(sys.argv))
