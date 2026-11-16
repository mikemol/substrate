#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run ONE suite, classify what happened, and write the stamp — as a record, not a marker.

⚑⚑⚑ THE STAMP HOLDS THE OUTCOME, BECAUSE THE STAMP IS OURS TO DEFINE (operator: *"that stamp
can hold whatever you want it to, though? It can be JSON."*). A first cut wrote an empty
`touch` marker and a SECOND `.outcome` file beside it, on the reasoning that "a stamp cannot
hold a kind". It can: `make` requires only that the file EXIST and be newer than its source,
and is indifferent to the contents. Two files carrying one fact is the duplication this repo
keeps paying for — and the pair could drift, since nothing made them atomic.

⚑⚑ WHAT THE KIND BUYS OVER pass/fail. `make` knows two states; `suite_outcome` names seven,
and three are not defects at all:

    unfit    KILLED by its memory lease — raise the lease, do not read the code
    refused  a GUARD refused the invocation (exit 2) — died on its own harness
    vacuous  reported 0/0 — asserted NOTHING

⚑ AND `vacuous` IS DECIDED WITHOUT CONSULTING THE EXIT CODE — verified in `verdict_kind`, whose
`reported.matched` branch returns before `returncode` is read. So a suite can report 0/0 and
return SUCCESS, and a bare marker would be byte-identical to a real pass. MEASURED on the first
run through this recipe: `suite_run.py` itself classified `silent` because it had no selftest
body — a roster member asserting nothing, which the old `touch` would have marked done.

⚑⚑ EVERY PIECE ALREADY EXISTED, UNJOINED. `suite_record.read_result` parses the `#row` line a
suite prints and classifies it; `suite_outcome` owns the vocabulary; `membudget` records wall
and peak per label. What nothing did was RUN a suite and put the kind where a later reader
could find it — so the classifier was reachable only from a roster runner, which is the thing
being removed.

    suite_run.py <path> <stamp> [<label>]

⚑ IT IS ONE SUITE, NEVER A ROSTER. `make` owns the fan-out (poset order, jobserver width,
membudget's lease and claim gates); this owns what happens to one of them. A version that
looped over suites would be the runner again, one rename later.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from mikemol.fence import git_env
from mikemol.fence import label_lease as fence_label_lease

from substrate import corpus, label_lease, label_ledger, suite_record

# The kinds that mean the suite is fine. Everything else is reported and fails the target.
_OK = ("ok",)

# ⚑ THE TIME BUDGET (W3, ruled 2026-09-20: keep a multi-minute fold on the roster and size the
# lease for TIME too). This runner had no timeout, so a hung suite hung the build and an honest
# 511 s fold was indistinguishable from a hang. The deadline is sized per label from the SAME
# ledger the memory lease reads — twice the slowest recorded run, rounded up to a minute — with
# an explicit `SELFTEST_TIMEOUT_S` winning outright, as `SELFTEST_MB` does for memory.
TIMEOUT_ENV = "SELFTEST_TIMEOUT_S"
DEFAULT_TIMEOUT_S = 600
# The kind a run that overran its deadline is reported as.
TIMED_OUT = "timeout"


def timeout_for(label: str) -> fence_label_lease.Deadline:
    """Return the wall-time budget for one label: explicit, else from history, else the default.

    ⚑ SWAPPED TO mtools' PORT (W25, 2026-10-02): `label_lease.deadline`'s shell-CLI path was
    already swapped onto `mikemol.fence.label_lease` in scripts/membudget; this is the matching
    Python-side swap. mtools' `Deadline` carries no `label` field (the warning moved to the free
    function `deadline_warning(label, got)`, read at the one call site in `run` below), and
    `deadline` itself takes parsed ROWS plus a `Guard`, not a path and two positional integers.
    `label_lease.child_cpu()` below is UNCHANGED and UNRELATED: it is substrate's own
    `resource.getrusage` helper measuring the actual subprocess's CPU delta, never something
    `label_lease.deadline` computed, so there was nothing there to swap.
    """
    named = os.environ.get(TIMEOUT_ENV)
    if named:
        cap = int(named)
        return fence_label_lease.Deadline(timeout_s=cap, cap_s=cap)
    rows = fence_label_lease.read_rows(label_ledger.ledger_path())
    guard = fence_label_lease.Guard(default_s=DEFAULT_TIMEOUT_S)
    return fence_label_lease.deadline(rows, label, guard)


# `<path> <stamp>` — the positionals the recipe always supplies; a label may follow.
_MIN_ARGS = 2

# Where an optional label sits, when given.
_LABEL_AT = 2


def stamp_body(label: str, kind: str, ok: int, total: int) -> str:
    """Render the stamp's contents: one JSON object, one line.

    ⚑ JSON RATHER THAN A TSV ROW, because this stamp is read by a program that must not guess
    a column order, and because a field added later (a duration, a reason) must not shift what
    an existing reader parses.
    """
    record: dict[str, str | int] = {"label": label, "kind": kind, "ok": ok, "total": total}
    return json.dumps(record, sort_keys=True) + "\n"


def write_stamp(stamp: str, label: str, kind: str, ok: int, total: int) -> None:
    """Write the stamp `make` depends on, carrying this run's outcome."""
    path = Path(stamp)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(stamp_body(label, kind, ok, total), encoding="utf-8")


def run(path: str, stamp: str, label: str) -> tuple[int, str]:
    """Run one suite, stamp the outcome, and return its exit code and kind.

    ⚑ THE STAMP IS WRITTEN ONLY ON `ok`. `make` treats a present, newer-than-source stamp as
    done, so writing one for a failed run would mark the target satisfied and the next build
    would skip it. A failure must leave NO stamp — that is what makes the build re-run it.

    ⚑ OUTPUT IS CAPTURED AND RE-EMITTED, NEVER SWALLOWED. The classifier needs the text and a
    reader needs to see the failure, so this reads it and prints it back rather than choosing.

    ⚑ `GIT_*` IS STRIPPED FROM THE SUITE'S ENVIRONMENT (2026-09-23): under a git hook those
    variables would point a suite's git fixture at THIS repository (`substrate/git_env`).
    """
    budget = timeout_for(label)
    warning = fence_label_lease.deadline_warning(label, budget)
    if warning is not None:
        sys.stderr.write(warning + "\n")
    before = label_lease.child_cpu()
    try:
        proc = subprocess.run(
            [sys.executable, path, "--selftest"],
            capture_output=True,
            text=True,
            check=False,
            cwd=str(corpus.ROOT),
            timeout=budget.timeout_s,
            env=git_env.clean_env(),
        )
    except subprocess.TimeoutExpired as hung:
        # ⚑ A HANG IS REPORTED AS ITS OWN KIND, never as `cases`. The deadline that killed it is
        # named beside the history it came from, so a reader can tell "slower than ever" from
        # "hung" — and no stamp is written, so `make` re-runs it.
        # ⚑ AND THE CPU IT SPENT IS ON THE LINE (ruled 2026-09-20, W8): the wall guard is not the
        # timing gate. A kill after 600 s wall and 590 s CPU is a runaway; after 600 s wall and
        # 2 s CPU it is a hang. Same kind, different next step, and only the CPU figure says which.
        # typeshed types the partial output as `bytes | None`; what the suite managed to print
        # before the deadline is re-emitted, never swallowed.
        partial = hung.stdout
        if partial is not None:
            sys.stdout.write(partial.decode("utf-8", "replace"))
        spent = label_lease.child_cpu() - before
        sys.stderr.write(
            f"suite-run: {label} — {TIMED_OUT} after {budget.timeout_s}s wall, "
            f"{spent:.1f}s CPU (slowest recorded run: "
            f"{'none' if budget.slowest_s is None else f'{budget.slowest_s:.0f}s'}"
            f" wall, {'none' if budget.cpu_s is None else f'{budget.cpu_s:.0f}s'}"
            " CPU)\n"
        )
        return 1, TIMED_OUT
    body = proc.stdout + proc.stderr
    sys.stdout.write(body)

    result = suite_record.read_result(body, proc.returncode)

    if result.kind not in _OK:
        # ⚑ THE KIND IS THE ACTIONABLE HALF, so it is on stderr where a build log keeps it.
        # "FAILED" sends a reader to the code; `unfit` sends them to the lease.
        sys.stderr.write(
            f"suite-run: {label} — {result.kind} ({result.reported.ok}/{result.reported.all_})\n"
        )
        return 1, result.kind

    write_stamp(stamp, label, result.kind, result.reported.ok, result.reported.all_)
    return 0, result.kind


def main(argv: list[str]) -> int:
    """Run the suite named on the command line."""
    args = [a for a in argv[1:] if not a.startswith("-")]
    if len(args) < _MIN_ARGS:
        sys.stderr.write("usage: suite_run.py <suite-path> <stamp> [<label>]\n")
        return 2

    path, stamp = args[0], args[1]
    label = args[_LABEL_AT] if len(args) > _LABEL_AT else str(Path(path))
    code, _kind = run(path, stamp, label)
    return code


# ⚑⚑ `--selftest` DELEGATES TO THE SIBLING SUITE RATHER THAN EXITING 0 (⟡last-retire).
# Discovery sees this module as a suite (an entry point plus the flag), and a no-op `0` made it
# report NOTHING — which `suite_run` itself now classifies as `silent`. It caught its own
# author on the first run through the new recipe. A module whose cases live in a sibling must
# RUN that sibling, not quietly succeed: exiting 0 while asserting nothing is the shape a bare
# stamp could never expose.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import suite_run_selftest

        sys.exit(suite_run_selftest.selftest())
    sys.exit(main(sys.argv))
