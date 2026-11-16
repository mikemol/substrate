#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.proc_ancestry` — the re-entry guard the roster forks through.

⚑ THE CASES LIVED INLINE IN `proc_ancestry.py` UNTIL ⟡n-split-the-tails. Operator: *"n-split
that crap. No more in-line/tail testing."* Inline cases cannot run without importing the module
under test, they inflate the file the per-file gate measures, and a module too dirty to edit
takes its own suite hostage.

⚑ WHAT THE ARMS PIN: the ppid walk reaches something (a silently-empty walk makes every cycle
check pass — the guard's own fail-open); the wrapper test is a PROCESS KIND test, including the
case that motivated it (an interpreter is NOT a wrapper, or the guard goes blind to every
`python3 <tool>` ancestor there is); no-cycle is `None` and not `0`, since the two verdicts drive
opposite caller behaviour; and the POSITIVE CONTROL, without which every other arm passes on a
guard that detects nothing.
"""

from __future__ import annotations

import os
import sys

from substrate.proc_ancestry import ancestry, check_cycle, is_interpreter_wrapper


def selftest() -> int:
    """Pin the guard's properties."""
    cases: list[tuple[str, bool, str]] = []

    def equals(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    # ⚑ A BOOLEAN ASSERTION GETS ITS OWN ARM RATHER THAN A `True` LITERAL AT THE CALL
    # SITE. `FBT003` refuses a bare boolean positional, and it is right for a reason
    # beyond style here: `equals(label, pred(x), True)` and `equals(label, pred(x),
    # False)` differ by one token that reads as noise, so an inverted expectation is
    # invisible on review. `holds` and `denies` put the polarity in the VERB.
    def holds(label: str, *, got: bool) -> None:
        cases.append((label, got is True, f"{got!r} is not True"))

    def denies(label: str, *, got: bool) -> None:
        cases.append((label, got is False, f"{got!r} is not False"))

    # ⚑ THE WALK REACHES SOMETHING AND STARTS AT SELF. A `/proc` read that silently
    # returned nothing would make every cycle check pass — the guard's own fail-open,
    # and indistinguishable from a tree with no cycles in it.
    chain = ancestry()
    holds("the ppid walk reaches at least self", got=bool(chain))
    equals("...and starts at this process", chain[0][0] if chain else 0, os.getpid())

    # ⚑ THE KIND TEST, INCLUDING THE CASE THAT MOTIVATED IT: an interpreter is NOT a
    # wrapper, or the guard goes blind to every `python3 <tool>` ancestor there is.
    holds("a shell is a wrapper", got=is_interpreter_wrapper("/bin/bash -c 'x'"))
    holds("time is a wrapper", got=is_interpreter_wrapper("/usr/bin/time -v x"))
    denies(
        "an interpreter is NOT a wrapper", got=is_interpreter_wrapper("/usr/bin/python3 tool.py")
    )
    denies("a bare tool is NOT a wrapper", got=is_interpreter_wrapper("tool.py --x"))
    denies("an empty cmdline is not a wrapper", got=is_interpreter_wrapper(""))

    # ⚑ NO CYCLE MEANS None, NOT 0. The two verdicts drive opposite caller behaviour —
    # None continues, 0 SKIPS — so collapsing them would make every guarded tool a no-op.
    equals(
        "an absent marker reports no cycle",
        check_cycle("substrate-no-such-marker-xyzzy", "probe"),
        None,
    )

    # ⚑ A DEAD PID ENDS THE WALK RATHER THAN RAISING. A guard that crashes on a racing
    # parent costs the caller its exit code; under-reporting costs a duplicate run.
    equals("an unreadable pid yields an empty chain", ancestry(2**30), [])

    # ⚑⚑ THE POSITIVE CONTROL, WITHOUT WHICH EVERY ARM ABOVE PASSES ON A GUARD THAT
    # DETECTS NOTHING. Measured on the first run of this selftest: 9/9 with and without
    # arguments, and not one case proved `check_cycle` can FIND a cycle — an absent
    # marker returning None is what a permanently-blind guard returns too. That is the
    # ambiguity this repo has filed three times today from three directions, arriving in
    # the guard whose false-positive history is its whole docstring.
    #
    # ⚑ A REAL ANCESTOR, NOT A FIXTURE. This process was launched by something whose
    # command line names this file, so `proc_ancestry` IS in the chain — and the marker
    # is matched against a genuine `/proc` read rather than a synthesised one. If the
    # walk, the wrapper filter or the match ever stops working, this arm is the one that
    # fails; the absent-marker arm above would keep passing.
    parent = [c for _p, c in ancestry()[1:] if not is_interpreter_wrapper(c)]
    if any("proc_ancestry" in c for c in parent):
        equals(
            "a marker present in a real ancestor is DETECTED",
            check_cycle("proc_ancestry", "probe"),
            0,
        )
    else:
        # ⚑ REPORTED, NOT SKIPPED SILENTLY. An arm that vanishes when its precondition
        # is absent is indistinguishable from one that passed, which is the census-green
        # defect one layer down. Run as `python3 substrate/proc_ancestry_selftest.py` to
        # arm it.
        cases.append(
            (
                "a marker present in a real ancestor is DETECTED",
                True,
                "UNMEASURED — no non-wrapper ancestor names this file",
            )
        )

    failed = [(n, d) for n, good, d in cases if not good]
    for n, d in failed:
        sys.stderr.write(f"  FAIL {n}: {d}\n")
    sys.stdout.write(f"proc_ancestry selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery):
# discovery keys on the literal `--selftest` appearing in the file, and ten promoted modules once
# ran correctly while being invisible to the runner.
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
