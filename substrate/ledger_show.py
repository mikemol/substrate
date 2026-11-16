#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print the label ledger's build history — the CLI over `substrate.label_ledger`.

⚑ THE CLI IS ITS OWN MODULE BECAUSE THE READER SHOULD NOT PRINT. `label_ledger` returns data;
this decides how to render it. The same split as `gen_selftest_mk` / `selftest_mk`, and for the
same reason — a library that formatted would be untestable without capturing stdout.

    ledger_show.py                      # every label, most recent run first
    ledger_show.py --since 24h          # only what ran in the last day
    ledger_show.py --prefix selftest:   # one namespace
    ledger_show.py --since 2h --prefix claim:

⚑⚑ THIS EXISTS BECAUSE THE QUESTION WAS BEING ASKED WITH `python3 -c`, which the no-chaining
hook refuses — correctly: an inline script dies with the turn and the next reader re-derives it
differently. A mode that does not exist is WORK, not grounds for a shell composition.

⚑ AND IT REPORTS THE WINDOW IT APPLIED, always. An empty result under a window is *"nothing ran
in this period"*; an empty result without one is *"this label has no history"*. Printing the
cutoff is what keeps a reader from collapsing those two into "the suite is missing".

⚑ `flag` AND `age` ARE PUBLIC BECAUSE CASES EXERCISE THEM. Leading-underscore was a reflex, not
a decision: a helper a suite must reach is part of the interface, and hiding it only forces the
suite to reach through the privacy marker.
"""

from __future__ import annotations

import sys
import time

from substrate import label_ledger

_HEADER = f"{'label':<44} {'age':>10} {'wall_s':>8} {'peak_mb':>8}"

# Age-rendering thresholds. Named because a bare 3600 in a comparison is a magic value, and
# because the two units are the whole content of `age`.
_HOUR, _DAY = 3600, 86400


def flag(argv: list[str], name: str) -> str | None:
    """Return a `--name value` or `--name=value` argument, or None.

    ⚑ BOTH SPELLINGS BIND. This repo's convention is `--flag=value` (`worklist_gate` records
    two refused guesses at it), but a reader arriving from another tool types the spaced form.
    Accepting one only would let the other ride through and be silently discarded.
    """
    for i, arg in enumerate(argv):
        if arg == name and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith(name + "="):
            return arg.split("=", 1)[1]
    return None


def age(stamp: int, now: float) -> str:
    """Render how long ago a run finished.

    ⚑ EPOCH-0 RENDERS AS `unstamped`, NEVER AS A NUMBER. That sentinel is how `label_ledger`
    keeps a timestampless row out of every window; turning it into `20000d` would present an
    absence of measurement as a measurement.
    """
    if stamp <= 0:
        return "unstamped"
    secs = int(now - stamp)
    if secs < _HOUR:
        return f"{secs // 60}m"
    if secs < _DAY:
        return f"{secs // _HOUR}h"
    return f"{secs // _DAY}d"


def main(argv: list[str]) -> int:
    """Render the ledger under the requested window and prefix."""
    prefix = flag(argv, "--prefix") or ""
    spec = flag(argv, "--since")
    since = label_ledger.parse_since(spec) if spec else 0

    rows = label_ledger.latest(prefix=prefix, since=since)
    now = time.time()

    scope = f"prefix {prefix!r}" if prefix else "all labels"
    window = f"since {spec} (epoch {since})" if spec else "all history"
    sys.stdout.write(f"ledger {label_ledger.ledger_path()} — {scope}, {window}\n")

    if not rows:
        # ⚑ THE TWO EMPTINESSES ARE DIFFERENT AND ARE REPORTED DIFFERENTLY. Under a window,
        # empty means nothing ran in that period; with no window it means no history at all.
        # Collapsing them would let "the build has not run" read as "the suite does not exist".
        if spec:
            sys.stdout.write("  no runs in this window (the label may still have history)\n")
        else:
            sys.stdout.write("  no runs recorded\n")
        return 0

    sys.stdout.write(_HEADER + "\n")

    # ⚑ THE SORT KEY IS A NAMED FUNCTION, NOT A LAMBDA, because an untyped lambda makes the
    # expression `Any` and poisons the call under `disallow_any_expr`. The typed boundary is
    # cheaper than the ignore it would otherwise need.
    def newest_first(label: str) -> int:
        """Sort key: most recently finished first."""
        return -rows[label].stamp

    for label in sorted(rows, key=newest_first):
        run = rows[label]
        sys.stdout.write(f"{label:<44} {age(run.stamp, now):>10} {run.wall:>8.2f} {run.peak:>8d}\n")
    sys.stdout.write(f"  {len(rows)} label(s)\n")
    return 0


# ⚑⚑ `--selftest` DELEGATES TO THE SIBLING SUITE RATHER THAN EXITING 0 (⟡last-retire).
# Discovery sees this module as a suite, and a no-op `0` made it report NOTHING — which the
# outcome classifier calls `silent`. Under a bare `touch` that stamped green; a module whose
# cases live in a sibling must RUN that sibling.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import ledger_show_selftest

        sys.exit(ledger_show_selftest.selftest())
    sys.exit(main(sys.argv))
