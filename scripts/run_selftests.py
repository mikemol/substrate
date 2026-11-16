#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run every tool's `--selftest` — discovered, never hardcoded — and rule on the result.

WHY THIS EXISTS. Every tool in this tree carries a `--selftest` whose cases are MEASURED
incidents, and for a long time nothing ran them: they were hand-run only, so a regression in
the exact machinery that encodes past damage would ship silently.

DISCOVERED, NOT LISTED. A hardcoded roster is the same defect as a hardcoded case total — it
can only ever be as current as its last edit, and this file's own frozen directory tuple hid
whole subtrees three separate times. `substrate.suite_discovery` walks for the property.

⚑ SUBPROCESS, NOT IMPORT. Several of these modules execute at import — they read `sys.argv`,
or an environment variable, or rewrite files from module scope. Importing them to call the body
directly would fire that. Each runs in its own interpreter with `--selftest`, which is also
what a person types.

⚑⚑⚑ THIS FILE IS NOW A DISPATCH, AND EVERY CAPABILITY IT HELD LIVES IN ITS OWN MODULE
(⟡retire-the-runner). The previous version carried 1,832 findings across 1,299 code lines, and
the per-file gate refuses EVERY edit to a file in that state — including the ONE KEYWORD a live
`TypeError` needed. It had reached the shape its own refusal text names: a monolith whose
cheapest correct change is the one that cannot land.

⚑⚑ THE FREEZE IS A PROPERTY OF THE CONTENT, NOT THE PATH, which is what made the retirement
possible at all. An edit is refused; a MOVE is not an edit. The old file stands at
`docs/retired/run_selftests.py.retired` as the record of what was replaced — under a top-level
directory both corpus walks skip, and with a suffix no `.py` walker can reach.

⚑ AND THE PATH IS LOAD-BEARING, SO IT DID NOT MOVE. An importer census reports ZERO import
sites for this file — a true zero and a misleading one, because it is a CLI whose population is
PATH LITERALS: 49 of them across 27 files. The pre-commit gate INVOKES this path,
`substrate.suite_declared` KEYS its roster on it, and a build census names it as a reader.
Relocating the working dispatch would leave those pointing at something that no longer answers.

⚑ THE IMPORTS ARE PACKAGE-QUALIFIED, NOT BARE-PLUS-`sys.path`. A runtime path mutation is an
import that cannot be CHECKED: it resolves against whatever the process happens to hold, so a
wrong root fails silently or succeeds against the wrong tree. `scripts` and `substrate` are
both declared packages, so both are reachable by name.

⚑ THE MODES ARE A TABLE, NOT A CHAIN OF `if`s. The chain is what kept this dispatch too complex
to land even after everything else had moved out — and a table is also what lets the flag set
and the dispatch be ONE authority rather than two kept agreeing by hand. They HAVE drifted: a
mode once dispatched at the bottom of `main` while missing from the declared set, so invoking
it refused as an unknown flag.

⚑⚑ AND THE ROSTER NOW HAS A SUITE OF ITS OWN, which it did not before. It ran every other
tool's cases and had none it could reach — which is exactly how a signature mismatch at a
module seam aborted every run, after the whole roster had already executed, with nothing able
to catch it. Its cases live in `scripts/run_selftests_selftest.py`.

Where each capability now lives:

    substrate.suite_discovery   which files ARE suites
    substrate.suite_command     how one suite is invoked
    substrate.suite_pragmas     what a suite declares to the runner
    scripts.selftest_pool       the roster fan-out, and what each suite printed
    substrate.suite_record      reading one suite's output into a result
    substrate.suite_census      the fold into the four censuses a verdict needs
    substrate.suite_report      the operator-facing verdict
    substrate.suite_reach_lens  how many cases a suite's source HOLDS
    substrate.reach_ratchet     ruling on the reach census
    substrate.suite_ledger      the recorded-run record
    substrate.suite_currency    the two diagnostic reads, --last and --reach
    substrate.suite_modes       the declarations and pragmas reads
    substrate.suite_tenants     REACHES-A-STORE against DECLARES-A-TENANT
    substrate.suite_sample      the emitted series shape
    scripts.selftest_series     pushing that series to the store

Usage: run_selftests.py [--quiet] [--times] [-jN]        (exit 1 if any suite fails)
       run_selftests.py --list           the roster discovery reached
       run_selftests.py --declarations   DECLARED intent against DISCOVERED membership
       run_selftests.py --pragmas        what each suite declares TO THE RUNNER
       run_selftests.py --tenants        REACHES-A-STORE against DECLARES-A-TENANT
       run_selftests.py --reach          the recorded reach census, without running anything
       run_selftests.py --last           is the recorded run current for this tree
       run_selftests.py --selftest       this dispatch's OWN cases
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

from scripts import ratchet, selftest_pool, selftest_series
from substrate import (
    reach_ratchet,
    suite_census,
    suite_currency,
    suite_discovery,
    suite_ledger,
    suite_modes,
    suite_reach_lens,
    suite_report,
    suite_sample,
    suite_tenants,
)

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path(__file__).resolve().parent.parent

# The suites that still report by PROSE rather than a typed record. Paydown-only.
LEGACY_BASELINE = ROOT / "scripts" / "selftest_contract_baseline.txt"

# ⚑ THE REACH CENSUS. PER-SUITE `total`, ratcheted UP — the polarity is INVERTED from the debt
# ratchet beside it. That sibling censuses DEBT, which may only shrink; this censuses REACH,
# which may only grow. Same discipline, inequality the other way up, which is why it is not a
# `set_ratchet` call: honest growth mints a new key there and would be refused as debt.
REACH_BASELINE = ROOT / "scripts" / "selftest_reach_baseline.tsv"

# This run's outcome per suite, for the staleness reader.
LEDGER = ROOT / ".selftest-last.tsv"

# A roster of suites, as `(label, path)`.
Suites = list[tuple[str, str]]


def say(line: str) -> None:
    """Emit one line to the operator."""
    sys.stdout.write(f"{line}\n")


def discover() -> Suites:
    """Return `[(label, path)]` for every file that IS a suite."""
    return suite_discovery.discover(ROOT)


def _write_ledger(suites: Suites, census: suite_census.Census) -> None:
    """Record this run's outcome. A ledger write must never fail a suite run."""
    body = suite_ledger.render(
        suites, (census.passed, census.declared), census.kinds, set(census.broken)
    )
    try:
        LEDGER.write_text(body, encoding="utf-8")
    except OSError:
        # ⚑ SAID, NOT SWALLOWED. A run whose outcome went unrecorded reads to `--last` as
        # never measured, and a reader deserves to know which of the two they are looking at.
        say("  ledger: not written — this run's outcome is unrecorded for --last")


def _emit(suites: Suites, census: suite_census.Census) -> None:
    """Push this run's counts to the store.

    ⚑ UNCONDITIONAL. A measurement you must remember to ask for is a level with extra steps —
    the same defect the series exists to fix. `--times` PRINTS; the series RECORDS.
    """
    rows = {
        label: suite_sample.Row(row.passed, row.declared, row.skipped)
        for label, row in census.counts.items()
    }
    selftest_series.emit(
        suite_sample.Sample(
            suites=len(suites),
            cases=census.passed,
            declared=census.declared,
            at=time.time(),
            per_suite=rows,
            seconds=dict(census.seconds),
            broken=census.broken,
        ),
        say,
    )


def _readings(census: suite_census.Census, suites: Suites) -> dict[str, tuple[int, int | None]]:
    """Pair each suite's REACHED count with what its source HOLDS.

    ⚑⚑ THE READING IS A PAIR, AND THAT IS WHAT MAKES A DROP CLASSIFIABLE. `reached` is how many
    cases the RUN registered; the second lens is how many the SOURCE holds. They move together
    on an honest deletion and COME APART on the defect — a suite that still contains its cases
    and stopped reaching them, which is the only thing that refuses.
    """
    paths = dict(suites)
    return {
        label: (reached, suite_reach_lens.static_cases(paths[label]))
        for label, reached in census.reach.items()
        if label in paths
    }


def _rule(census: suite_census.Census, suites: Suites, *, quiet: bool) -> int:
    """Rule on the two independent censuses this run produced."""
    # ⚑ THE TRANSITIONAL READER IS A RATCHET, NOT A FALLBACK. Every suite it reads is DEBT,
    # enumerated by name in a paydown-only baseline, and it REFUSES on growth. A SET, not a
    # count: a bare number cannot catch swap-gaming.
    contract_rc = ratchet.set_ratchet(
        census.legacy,
        str(LEGACY_BASELINE),
        "selftest-contract",
        quiet,
        noun="suite(s) still reporting by PROSE instead of a typed record",
        refuse_hint="A suite's result is a RECORD, not a line to regex. Emit it with "
        "`rungs.Cases(key=...).report()` (which does it for you) or "
        "`rungs.emit_record(passed, total)`. Do NOT add a key here — the "
        "census may only be PAID DOWN.",
    )
    # ⚑⚑⚑ THE REACH GATE RUNS BEFORE THE FAILURE BLOCK and its code is folded in at BOTH
    # exits, because a run can be reach-regressed and case-green simultaneously — that is the
    # whole defect. Inside the failure branch it would be visible only when something else had
    # already gone red.
    # ⚑⚑ AND `quiet` GOES BY NAME. A positional boolean against a keyword-only parameter is
    # the exact `TypeError` that retired the file this one replaces — a bare `True` at a call
    # site says nothing about what it decides, and its sibling decides whether a gate WRITES.
    reach_rc = reach_ratchet.reach_ratchet(
        _readings(census, suites), str(REACH_BASELINE), quiet=quiet
    )
    # ⚑ `or` RATHER THAN A PICK: two independent verdicts, neither subsuming the other. Every
    # suite can pass every case it RAN while one silently stopped reaching a third of them.
    return contract_rc or reach_rc


def run(suites: Suites) -> int:
    """Run every suite, fold the results, and return the run's exit code."""
    quiet = "--quiet" in sys.argv
    jobs = selftest_pool.jobs(sys.argv)
    census = selftest_pool.run_all(suites, jobs=jobs, root=ROOT)

    if not quiet:
        broken = set(census.broken)
        for label, _path in suites:
            row = census.counts.get(label)
            if row is not None and label not in broken:
                say(suite_report.passing_line(label, row))
    if "--times" in sys.argv:
        for line in suite_report.slowest_lines(census.seconds, jobs):
            say(line)

    _write_ledger(suites, census)
    _emit(suites, census)
    verdict = _rule(census, suites, quiet=quiet)

    if census.failed:
        for line in suite_report.failure_lines(census, len(suites)):
            say(line)
        return 1
    say(suite_report.summary_line(census, len(suites)))
    return verdict


def declarations(suites: Suites) -> int:
    """Report DECLARED intent against DISCOVERED membership."""
    for line in suite_modes.declaration_lines(suites):
        say(line)
    return 0


def pragmas(suites: Suites) -> int:
    """Report what each suite declares TO THE RUNNER."""
    for line in suite_modes.pragma_lines(suites):
        say(line)
    return 0


def tenants(suites: Suites) -> int:
    """Report REACHES-A-STORE against DECLARES-A-TENANT, and the cuts the lens cannot see."""
    for line in [*suite_tenants.lines(suites), *suite_tenants.cut_lines()]:
        say(line)
    return 0


def reach(suites: Suites) -> int:
    """Report the recorded reach census WITHOUT running anything."""
    verdict = suite_currency.reach(
        suites, str(REACH_BASELINE), os.path.relpath(REACH_BASELINE, ROOT)
    )
    for line in verdict.lines:
        say(line)
    return verdict.code


def last(suites: Suites) -> int:
    """Report whether the recorded run still describes today's tree."""
    try:
        body = LEDGER.read_text(encoding="utf-8")
    except OSError:
        say(suite_currency.NEVER_RUN)
        return 1
    verdict = suite_currency.currency(body, suites)
    for line in verdict.lines:
        say(line)
    return verdict.code


def listing(suites: Suites) -> int:
    """Print the roster discovery reached."""
    for label, _path in suites:
        say(f"  {label}")
    say(f"{len(suites)} suite(s)")
    return 0


def own_cases(_suites: Suites) -> int:
    """Run this dispatch's OWN cases.

    ⚑ THE IMPORT IS DEFERRED because the suite imports THIS module: at module scope the two
    would be a cycle, and the cases are only needed on the one invocation that asks for them.
    """
    from scripts import run_selftests_selftest  # noqa: PLC0415

    return run_selftests_selftest.selftest()


# ⚑⚑ ONE AUTHORITY FOR THE FLAG SET **AND** THE DISPATCH — a table cannot drift from itself.
MODES: dict[str, Callable[[Suites], int]] = {
    "--declarations": declarations,
    "--pragmas": pragmas,
    "--tenants": tenants,
    "--reach": reach,
    "--list": listing,
    "--last": last,
    "--selftest": own_cases,
}

# The flags that modify a run rather than selecting a mode.
MODIFIERS = {"--quiet", "--times"}

# This tool's whole flag surface, DERIVED from the table rather than restated beside it.
KNOWN_FLAGS = set(MODES) | MODIFIERS


def _guards() -> int | None:
    """Run the invocation guards, returning an exit code when one refuses.

    ⚑⚑⚑ THE CYCLE GUARD IS THE CALLER HALF OF A SYMMETRIC PAIR. This roster runs every tool's
    `--selftest`, and one of those tools' suites runs THIS roster — so the roster contains its
    own caller, and each generation forks a whole set of concurrent runs. Measured off a live
    process tree: load 54.93 with 68 processes on 10 cores, four generations deep.

    ⚑ BOTH ENDS CHECK, AND THAT IS NOT REDUNDANT. Guarding only the callee still lets this
    fork a generation before anything refuses; guarding only the caller lets a hand-run callee
    re-enter. The edge is removed only when both ends decline it.

    ⚑ THE MARKER IS THE SCRIPT PATH, NOT A FLAG STRING — a marker carrying arguments also
    matches the shell wrapper that LAUNCHED this process, so a tool would refuse its own first
    invocation.
    """
    # ⚑ `-jN` IS VALUE-BEARING, so it is split off before the membership test: the flag
    # contract compares bare flags and would reject `-j8` as unknown.
    argv = [a for a in sys.argv if not (a == "-j" or (a.startswith("-j") and a[2:].isdigit()))]
    rc = ratchet.check_argv(argv, KNOWN_FLAGS, "run_selftests")
    if rc is not None:
        return rc
    return ratchet.check_cycle("run_selftests.py", "run_selftests")


def main() -> int:
    """Dispatch one invocation of the runner."""
    rc = _guards()
    if rc is not None:
        return rc
    suites = discover()
    for flag, mode in MODES.items():
        if flag in sys.argv:
            return mode(suites)
    return run(suites)


if __name__ == "__main__":
    sys.exit(main())
