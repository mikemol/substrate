#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Does a module's build log describe TODAY's tree - the freshness predicate, inputs supplied.

THE FIFTH CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_census.py:228-351`, W4 tick 44). A
log is fresh when its mtime is at least the newest mtime of the module's own source and every
TRANSITIVE import; measured, 1770 of 2810 logs were stale. The rule existed inside
`census_from_build` as a closure over its locals, so `--diagnose` - which also reads logs - had
no way to ask, and classified `Core.agda` from a log written BEFORE the edit that broke it.
The predicate was not wrong; it was reading a different tree.

THREE SILENT FAILURES ARE RECORDED IN THE ORIGIN AND EACH IS A CASE HERE. A module name derived
by string surgery was not a key of the DAG, so the walk visited nothing, `newest` stayed 0.0,
and every log read fresh; an `agda/` prefix added instead of read made every lookup miss; and
a bare `except: pass` around `getmtime` swallowed every miss so `newest` stayed 0.0 again. So
the DAG's own `src_to_mod` resolves the module, misses are COUNTED, and an unresolved dependency
makes the verdict UNSAFE rather than imprecise - `newest` is then a lower bound, "fresh" may be
wrong while "stale" is still sound, and the optimistic direction is withheld.

EVERY INPUT IS A PARAMETER. The DAG is `substrate.agda_dag.Dag` - `disk` (module -> source
relpath under the agda dir), `deps` (module -> direct imports) and `src_to_mod` - THE parsed
import graph. ⚑ A first cut of this module (tick 44) declared its OWN `Dag` with the same
three fields: a reinvention, caught one cut later when the reuse-search found `agda_dag`
already carrying `rdeps` and `src_to_mod` as well, and retired here (gate-G430 residue).
`mtime_of(path)` returns None where the origin's `getmtime` raised; the log index is a mapping
the caller builds ONCE - the origin's `_log_index` was a recursive glob per call and 71% of a
912-second suite (13,335 calls to find one file by name), and the fix was memoisation, not
parallelism: before reaching for concurrency, check whether the work is repeated.
`log_index(build_dir)` is that one walk, with the `Substrate`-anchored module naming and
first-writer-wins kept.

THE `why` CARRIES NUMBERS, NOT JUST THE BIT: a fresh/stale verdict that disagrees with the
compiler leaves nowhere to go but a REPL, so the newest dependency and both mtimes ride along.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from substrate.agda_dag import Dag

LOG_SUFFIX = ".agdai.log"
# The top-level package every build log path is anchored on when named as a module.
ANCHOR = "Substrate"
AGDA_PREFIX = "agda/"

Verdict = tuple[bool, str | None, dict[str, object]]


def log_index(build_dir: str | Path) -> dict[str, str]:
    """Walk `_build` ONCE: module name -> its `.agdai.log` path, first writer wins."""
    idx: dict[str, str] = {}
    for p in sorted(Path(build_dir).rglob(f"*{LOG_SUFFIX}")):
        parts = list(p.relative_to(build_dir).parts)
        if ANCHOR in parts:
            parts = parts[parts.index(ANCHOR) :]
        mod = ".".join(parts)[: -len(LOG_SUFFIX)]
        idx.setdefault(mod, str(p))
    return idx


def mtime_on_disk(path: str) -> float | None:
    """Return a path's mtime, or None where stat fails - the production reader."""
    try:
        return Path(path).stat().st_mtime
    except OSError:
        return None


def newest_dependency(
    mod: str, dag: Dag, mtime_of: Callable[[str], float | None], sources_root: str
) -> tuple[float, str | None, int, int]:
    """Return (newest mtime, its module, unreadable count, modules seen) over the closure."""
    seen: set[str] = set()
    stack = [mod]
    newest, culprit, missing = 0.0, None, 0
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        src = dag.disk.get(cur)
        if src:
            t = mtime_of(str(Path(sources_root) / src))
            if t is None:
                missing += 1
            elif t > newest:
                newest, culprit = t, cur
        stack.extend(dag.deps.get(cur, ()))
    return newest, culprit, missing, len(seen)


def freshness(
    mod: str, log: str | None, dag: Dag, mtime_of: Callable[[str], float | None], sources_root: str
) -> Verdict:
    """Return (fresh?, log, why) for a resolved module and its log path."""
    if not log:
        return (False, None, {"why": "no build log for this module"})
    lm = mtime_of(log)
    if lm is None:
        return (False, log, {"why": "log unreadable"})
    newest, culprit, missing, n = newest_dependency(mod, dag, mtime_of, sources_root)
    if missing:
        return (
            False,
            log,
            {
                "why": f"{missing} of {n} dependency source(s) could not be read "
                f"— freshness unsafe, treating as STALE"
            },
        )
    return (
        lm >= newest,
        log,
        {"log_mtime": lm, "newest_dep_mtime": newest, "newest_dep": culprit, "n_deps": n},
    )


def log_is_fresh(
    src_rel: str,
    dag: Dag,
    index: Mapping[str, str],
    mtime_of: Callable[[str], float | None],
    sources_root: str,
) -> Verdict:
    """Return (fresh?, log, why) for one source path, resolved through the DAG's own index."""
    rel = src_rel.removeprefix(AGDA_PREFIX)
    mod = dag.src_to_mod.get(rel)
    if not mod:
        return (
            False,
            None,
            {
                "why": f"{src_rel} is not in the import DAG — cannot judge "
                f"freshness (verdict withheld)"
            },
        )
    return freshness(mod, index.get(mod), dag, mtime_of, sources_root)
