#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run the whole suite roster concurrently and hand back what each suite printed.

⚑ SUBPROCESS, NOT IMPORT, AND THAT IS NOT A STYLE CHOICE. Several suites execute at import —
they read `sys.argv`, or an environment variable, or rewrite files from module scope. Importing
one to call its body would fire exactly what the isolation exists to prevent. Each runs in its
OWN interpreter with `--selftest`, which is also what a person types, so the runner measures
the same thing a hand-run does.

⚑⚑ IT LIVES IN `scripts/`, NOT `substrate/`, AND THAT IS A CORRECTION RATHER THAN A PREFERENCE.
A `substrate/suite_runner.py` existed and was DELETED under ⟡last-retire, because `make` now
owns the roster fan-out for the build path — poset order, jobserver width, membudget's lease
and claim gates — and `substrate.suite_run` was narrowed to running exactly ONE suite. This
module is the CLI roster's fan-out, which is a different consumer with a different owner: it
answers "run everything now and rule on it", which is what the pre-commit gate invokes. Naming
that difference is what keeps this from being the deleted module returning under a new spelling.

⚑ PARALLEL BECAUSE THE WORK IS GENUINELY DISTINCT, AND THAT WAS CHECKED SECOND, NOT FIRST. A
serial loop left nine of ten cores idle — measured at ~1.0x utilisation. But a recorded 100x
defect in this repo LOOKED like a concurrency problem and was REPEATED WORK: parallelising it
would have made the same mistake run faster. Here each suite is a different module read once,
so concurrency is the right lever — and the timing report exists so that claim stays checkable
rather than assumed.

⚑ EVERY SUITE LEASES FROM THE ONE LEDGER. Starting a worker per core, each of which walks the
whole tree, is exactly the concurrent-memory case the repo's RAM semaphore was built for: a
lease means the next one WAITS instead of the box OOMing. The invocation is
`substrate.suite_command`'s — including the declared-dependency and tenant flags, which a
collector that took a bare script path and wrapped it itself would have dropped on the way
through.

⚑⚑ THE RESULTS ARE SORTED BY THE POPULATION, NOT ASKED OF THE POOL. Well-formedness is the
CONSUMER's to establish: a runner whose output reorders itself between runs is insufficiently
well-formed. Results stream as they land, which keeps a partial run readable; the artefact is
ordered because every result carries its key.

⚑ BARE `-j` MEANS ALL CORES, AND IT DELIBERATELY DOES NOT READ THE BUILD'S JOB AUTHORITY. That
one bounds concurrent Agda compiles, whose leases the RAM semaphore arbitrates. These are
python suites. Same flag letter, different population — binding them together would be one
spelling for two intents, which is the drift the single-authority rule exists to stop, running
the other way.

⚑ A LAUNCH FAILURE IS A RESULT, NOT AN EXCEPTION. Raising would turn one unrunnable suite into
NO results at all — the shape that makes a whole green run vanish rather than one row go red.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner).
"""

from __future__ import annotations

import concurrent.futures
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mikemol.fence import git_env  # noqa: E402

from substrate import suite_census, suite_command  # noqa: E402


def jobs(argv: list[str]) -> int:
    """Return the worker count: `-jN`, else one per core."""
    for arg in argv:
        if arg == "-j":
            return os.cpu_count() or 1
        if arg.startswith("-j") and arg[2:].isdigit():
            return max(1, int(arg[2:]))
    return os.cpu_count() or 1


def _label_of(run: suite_census.Run) -> str:
    """Sort key: a run is ordered by the suite it reports on."""
    return run.label


def run_one(label: str, path: str, root: Path) -> suite_census.Run:
    """Run ONE suite in its own interpreter and capture what it printed.

    ⚑ `GIT_*` IS STRIPPED FROM THE SUITE'S ENVIRONMENT (2026-09-23): under the pre-commit hook git
    exports `GIT_DIR`/`GIT_INDEX_FILE`, and a suite that builds a git fixture would otherwise act on
    THIS repository. See `substrate/git_env`.
    """
    argv = suite_command.command(path, sys.executable, root)
    started = time.monotonic()
    try:
        done = subprocess.run(
            argv, cwd=root, capture_output=True, text=True, check=False, env=git_env.clean_env()
        )
    except OSError as exc:
        return suite_census.Run(
            label=label,
            output=f"could not launch: {exc}",
            returncode=1,
            seconds=time.monotonic() - started,
        )
    return suite_census.Run(
        label=label,
        output=(done.stdout or "") + (done.stderr or ""),
        returncode=done.returncode,
        seconds=time.monotonic() - started,
    )


def execute(suites: list[tuple[str, str]], jobs: int, root: Path) -> list[suite_census.Run]:
    """Run every suite concurrently and return the captured runs, in roster order."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        futures = [pool.submit(run_one, label, path, root) for label, path in suites]
        runs = [future.result() for future in futures]
    return sorted(runs, key=_label_of)


def run_all(suites: list[tuple[str, str]], jobs: int, root: Path) -> suite_census.Census:
    """Run every suite and fold the results into one census."""
    return suite_census.fold(execute(suites, jobs, root))
