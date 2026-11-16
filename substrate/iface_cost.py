#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""MEASURE where an `iface_dataflow` walk spends its time, and how much is re-derivation.

⚑⚑⚑ A RESOURCE-SHAPED SYMPTOM INVITES A RESOURCE-SHAPED CAUSE, AND THIS EXISTS TO REFUSE
THAT. `iface_dataflow --module scratch/agda_lex.py` was measured exiting 124 at a 600s
timeout, and the first explanation offered was a per-slot subprocess spawn tax borrowed
from a peer's `dmypy inspect` measurement. That mechanism is not in this walk at all —
nothing under `--module` shells out — so acting on it would have optimised a cost that
does not exist here. This module answers the question with counters rather than a story.

⚑⚑ THE COUNT THAT SEPARATES THE CANDIDATE CAUSES IS HOW MANY TIMES THE WALK PARSES A
CORPUS FILE, AGAINST HOW BIG THE CORPUS IS. A walk that reads each file once parses about
as many times as the corpus has files; one that re-reads the corpus per slot parses about
slots-times-that. The RATIO is the achievable speedup from memoising the parse — a number,
not a hope, and it says whether a cache is the fix BEFORE one is written.

⚑ THE COUNTER STANDS IN FRONT OF THE REAL LOADER AND DELEGATES TO IT. A counting copy of
the parse would be a second authority on what the walk reads, and the two would drift the
moment `load` learned a cache — at which point this instrument would keep reporting the
old number while looking like a measurement of the new code.

⚑ CPU TIME, NEVER WALL. A wall-clock figure from a loaded machine is not a measurement,
and this session already withdrew one for that reason. `time.process_time` excludes time
this process was descheduled, which is the quantity a concurrent build cannot touch.

⚑⚑⚑ WHAT THIS INSTRUMENT MEASURED, AND IT OVERTURNED BOTH STANDING HYPOTHESES. Run over
four modules, the cost obeys one law: **CPU is proportional to the count of owed PARAMETER
slots, each costing one full sweep of the corpus.** `_compute` returns `STATED` before
`_parameter` is ever reached, and `_return` never calls `call_sites` at all — so return
slots and annotated slots are both FREE, and only an unannotated parameter buys a sweep.
`--selftest` measures this file at ZERO sweeps for exactly that reason.

⚑⚑ THE SPAWN-TAX HYPOTHESIS DOES NOT APPLY HERE. It was carried over from a peer's
`dmypy inspect` measurement, where each invocation pays ~0.38s of interpreter startup. No
mode reached by `--module` shells out; the only `subprocess` in `iface_dataflow` is
`--sites`, a different mode. Optimising the spawn would have optimised nothing.

⚑⚑ AND THE PARSE-CACHE HYPOTHESIS IS REAL BUT SMALL — measurably smaller than its own
headline number. The redundancy ratio suggests 6x on a 6-sweep module; `--cache` measures
the ACTUAL end-to-end gain at 1.7x there and 2.1x on an 11-sweep one, verdicts identical.
The gap is the point: a sweep re-parses the corpus AND re-walks every tree in it
(`calls_in`, `binds`), and a memo removes only the first half. **A ratio derived from a
counter is an upper bound on a fix, never its value** — which is why this module runs both
arms rather than reporting the ratio and calling it a speedup.

Usage: iface_cost.py --counts <path> | --cache <path> | --selftest
"""

from __future__ import annotations

import sys
import time
from collections import Counter
from dataclasses import dataclass, field

from substrate import corpus, iface_dataflow

# How many of the most-re-parsed files to name — enough to see the shape, not the corpus.
_SHOWN_FILES = 8


class UnparseableModuleError(Exception):
    """The path handed to the instrument is not a module this walk can read."""

    def __init__(self, path: str) -> None:
        """Name the path that could not be parsed."""
        super().__init__(f"could not parse {path}")


@dataclass(frozen=True, slots=True)
class Cost:
    """What one walk cost, and how much of that cost was re-derivation.

    ⚑ `parses` AND `corpus_size` ARE DIFFERENT NUMBERS AND BOTH ARE KEPT, for the same
    reason `_parameter` keeps `sites` beside `reached`: either alone cannot distinguish a
    walk that reads the corpus once from one that reads it once per slot, and that
    distinction IS the finding. Their ratio is the redundancy factor.
    """

    path: str
    slots: int
    resolved: int
    cpu_seconds: float
    corpus_size: int
    per_file: Counter[str] = field(default_factory=Counter)

    @property
    def parses(self) -> int:
        """Return how many times the walk parsed a corpus file, counting repeats."""
        return sum(self.per_file.values())

    @property
    def distinct(self) -> int:
        """Return how many DISTINCT corpus files the walk parsed at least once."""
        return len(self.per_file)

    @property
    def redundancy(self) -> float:
        """Return parses per distinct file — 1.0 when nothing is re-parsed."""
        return self.parses / self.distinct if self.distinct else 0.0


class _CountingLoader:
    """Stand in front of `iface_dataflow.load`, tally every call, and delegate.

    ⚑⚑ `cached` IS WHAT MAKES THIS AN EXPERIMENT RATHER THAN A TALLY. With it set, a path
    parsed once is served from a dict on every later call — which is exactly the change a
    memoising fix would make, run WITHOUT making it. The two runs differ in one variable, so
    the difference in cpu time IS the value of that fix, measured on this corpus rather than
    projected from the redundancy ratio.

    ⚑ THE CACHE IS SOUND HERE BECAUSE THE CORPUS DOES NOT CHANGE MID-WALK. That is a fact
    about one process's lifetime, not a licence for a cache that outlives it: a memo keyed on
    a path with no content hash would answer from a stale tree the moment a file is edited
    between runs, which is the defect a cost fix must not introduce.
    """

    def __init__(self, *, cached: bool) -> None:
        """Capture the loader this instrument stands in front of."""
        self.inner = iface_dataflow.load
        self.cached = cached
        self.seen: Counter[str] = Counter()
        self.memo: dict[str, iface_dataflow.Module | None] = {}

    def __call__(self, path: str) -> iface_dataflow.Module | None:
        """Tally one call and either serve it from the memo or delegate."""
        self.seen[path] += 1
        if not self.cached:
            return self.inner(path)
        if path not in self.memo:
            self.memo[path] = self.inner(path)
        return self.memo[path]


def measure(path: str, *, cached: bool = False) -> Cost:
    """Walk one module's slots with the loader counted, and report what it cost.

    ⚑ THE LOADER IS RESTORED IN A `finally`, because a rebind that survives the call turns
    every later reader in the same process into an instrument — a measurement apparatus
    left wired into the thing it measures, attributing its counts to whatever ran next.
    """
    mod = iface_dataflow.load(path)
    if mod is None:
        raise UnparseableModuleError(path)
    paths = corpus.py_files()
    counter = _CountingLoader(cached=cached)
    iface_dataflow.load = counter
    t0 = time.process_time()
    try:
        rows = iface_dataflow.Resolver(paths).module_interface(mod)
    finally:
        iface_dataflow.load = counter.inner
        cpu = time.process_time() - t0
    done = sum(1 for r in rows if r.status in iface_dataflow.RESOLVED)
    return Cost(path, len(rows), done, cpu, len(paths), counter.seen)


def _render_counts(path: str) -> int:
    """Print the parse tally for one module's walk."""
    got = measure(path)
    sys.stdout.write(
        f"iface-cost: {got.path}\n"
        f"    slots           {got.slots}\n"
        f"    resolved        {got.resolved}\n"
        f"    cpu seconds     {got.cpu_seconds:.2f}  (process_time, not wall)\n"
        f"    corpus files    {got.corpus_size}\n"
        f"    parses          {got.parses}\n"
        f"    distinct files  {got.distinct}\n"
        f"    redundancy      {got.redundancy:.1f}x  (parses per distinct file; 1.0 = "
        f"each file read once)\n"
        "  ⚑ REDUNDANCY IS THE ACHIEVABLE SPEEDUP FROM MEMOISING THE PARSE, not a quality\n"
        "  score. A walk near 1.0 cannot be made faster by caching trees; one at 40x is\n"
        "  spending 39 of every 40 parses re-deriving a tree it already built.\n"
    )
    for name, n in got.per_file.most_common(_SHOWN_FILES):
        sys.stdout.write(f"    {n:6d}  {name}\n")
    return 0


def _render_cache(path: str) -> int:
    """Run the same walk twice, memoised and not, and print the difference.

    ⚑⚑ TWO RUNS DIFFERING IN ONE VARIABLE, IN ONE PROCESS. Comparing a cached run here
    against an uncached run from an earlier invocation would compare two machine states as
    well as two algorithms, and the machine moves — this session already withdrew a figure
    for exactly that. Both arms run back to back on the same corpus in the same interpreter.

    ⚑ THE SLOT VERDICTS ARE COMPARED, NOT JUST THE CLOCKS. A cache that changed an ANSWER
    would be a wrong fix reported as a fast one, and a timing-only comparison cannot see it.
    """
    cold = measure(path, cached=False)
    warm = measure(path, cached=True)
    speedup = cold.cpu_seconds / warm.cpu_seconds if warm.cpu_seconds else 0.0
    sys.stdout.write(
        f"iface-cache: {path} — the SAME walk, memoised and not.\n"
        f"    slots                {cold.slots}\n"
        f"    parses               {cold.parses} (both arms — the memo serves calls, it "
        f"does not remove them)\n"
        f"    distinct files       {cold.distinct}\n"
        f"    cpu, no memo         {cold.cpu_seconds:.2f}s\n"
        f"    cpu, memoised        {warm.cpu_seconds:.2f}s\n"
        f"    speedup              {speedup:.1f}x\n"
        f"    resolved, no memo    {cold.resolved} of {cold.slots}\n"
        f"    resolved, memoised   {warm.resolved} of {warm.slots}\n"
    )
    if (cold.resolved, cold.slots) != (warm.resolved, warm.slots):
        sys.stdout.write(
            "  ⚑ THE MEMO CHANGED AN ANSWER, which makes it a WRONG fix rather than a fast\n"
            "  one. Report this rather than the speedup.\n"
        )
        return 1
    sys.stdout.write(
        "  ⚑ THE VERDICTS ARE IDENTICAL, so the memo is a pure cost change on this corpus.\n"
        "  It is keyed on a PATH and lives for one walk; anything outliving the process\n"
        "  needs a content hash, or it answers from a tree the file no longer has.\n"
    )
    return 0


def main(argv: list[str]) -> int:
    """Dispatch one mode; 2 on an unusable command line.

    ⚑⚑ `--selftest` IS DISPATCHED FROM THE `__main__` GUARD, NOT FROM HERE. A branch inside this
    function returns, and `return` is invalid at module level — so `module_trim` could not re-home
    the cases while their dispatch lived in a function body (gate-G327). Rewriting the branch to
    `sys.exit` was refused for a better reason: a reachable `SystemExit` takes the exit decision
    from anything that imports this module (gate-G329). Moving the dispatch into the guard, where
    the block never runs on import, is the repair that costs neither property.
    """
    rest = [a for a in argv[1:] if not a.startswith("-")]
    if "--cache" in argv and rest:
        return _render_cache(rest[0])
    if "--counts" in argv and rest:
        return _render_counts(rest[0])
    sys.stdout.write(__doc__ or "")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
