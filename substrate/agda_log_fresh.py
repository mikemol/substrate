# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decide whether a per-module build log is evidence about TODAY's Agda tree.

Extracted from `scratch/split_census.py` as part of ⟡drain-split-census. One
responsibility: index the build's `.agdai.log` artifacts by module, and decide whether one
of them still describes the sources it was written from.

⚑ THE FRESHNESS RULE EXISTED AND `diagnose` DID NOT USE IT. The census computes
`log_mtime >= max(own source, every TRANSITIVE import)` and measured that 1770 of 2810
logs were stale (§52) — but it kept the rule as a closure over its own locals, so
`--diagnose`, which also reads logs, had no way to ask. MEASURED consequence (§66, C2's
false NEGATIVE): `Core.agda` was classified `other` from a log written BEFORE the edit
that broke it, while a live compile showed the `[FileNotFound]` plainly. **The predicate
was not wrong; it was reading a different tree.** That is the §6d class exactly — one
relation, two consumers, the second re-deriving nothing because it did not know the first
had it.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import corpus
from substrate.agda_import_dag import import_dag

if TYPE_CHECKING:
    from collections.abc import Mapping

_LOG_SUFFIX = ".agdai.log"
_LOG_INDEX: dict[str, dict[str, str]] = {}


def log_index(root: str = "agda") -> Mapping[str, str]:
    """Return `module name -> its .agdai.log path`. ONE walk of `_build/`, memoised.

    ⚑ THIS WAS A RECURSIVE GLOB PER CALL, AND IT WAS 71% OF THE SELFTEST SUITE. MEASURED
    with cProfile over `worklist_gate._selftest()`: the freshness predicate ran 13,335
    times for 646s of a 912s run, each call issuing a recursive glob for `<mod>.agdai.log`
    — 6.4M `_iglob` frames, 42.7M `_rlistdir`, 49.8M path joins, to find ONE file by name.

    ⚑ AND THE FIX IS NOT PARALLELISM, WHICH IS WHAT WAS CONSIDERED FIRST. Threading would
    have run 13,335 redundant tree walks on ten cores instead of one; the work was
    REPEATED, not large. Same shape as the blast radius re-running `parse_tree()` once per
    query (§55: 300s -> 2.7s when memoised at its owner) — *before reaching for
    concurrency, check whether the work is repeated.*

    ⚑ MEMOISED PER ROOT, AND DELIBERATELY NOT INVALIDATED. A build that adds logs
    mid-process would be a straddled measurement, which the tree stamp already refuses at
    the census layer. A stale index within one process is the same class as a straddled
    ledger, so the honest scope is the process.
    """
    cached = _LOG_INDEX.get(root)
    if cached is not None:
        return cached
    index: dict[str, str] = {}
    base = Path(root) / "_build"
    for dirpath, _dirs, files in os.walk(base):
        for name in files:
            if not name.endswith(_LOG_SUFFIX):
                continue
            # `_build/<hash>/agda/Substrate/…/X.agdai.log` -> `Substrate.….X`
            parts = list(Path(dirpath, name).relative_to(base).parts)
            if "Substrate" in parts:
                parts = parts[parts.index("Substrate") :]
            module = ".".join(parts)[: -len(_LOG_SUFFIX)]
            # First writer wins, matching the glob-era `hits[0]`.
            index.setdefault(module, str(Path(dirpath, name)))
    _LOG_INDEX[root] = index
    return index


def _mtime(path: Path) -> float | None:
    """Return `path`'s mtime, or None when it cannot be read. A MISS IS NOT A ZERO.

    ⚑ THE ORIGIN SWALLOWED EVERY `OSError` AND SUBSTITUTED 0.0, WHICH INVERTED THE VERDICT.
    A bare `except: pass` over the whole measurement left `newest` at 0.0, making
    `log_mtime >= newest` true for EVERY log — the guard-degrades-to-nothing class (§52),
    and the reason the first fix looked like it had not applied. Returning None makes the
    miss COUNTABLE by the caller instead of indistinguishable from an epoch timestamp.
    """
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def log_is_fresh(
    src_rel: str,
    root: str = "agda",
) -> tuple[bool, str | None, dict[str, object]]:
    """Return `(fresh?, log_path|None, why)` for one source file's build log.

    ⚑ THE DOCSTRING ONCE SAID `(fresh?, log_path)` WHILE THE CODE RETURNED THREE, and
    nothing caught it: the tuple was widened mid-debug and neither the four `return`s nor
    the summary line were updated consistently. **That is the defect that prompted the mypy
    gate** (operator, 2026-08-01: *"have we reached a point where we should be using [a
    type checker]"*) — a signature change verified only by running it. The annotation here
    is that verification, standing.

    ⚑ REPORT THE NUMBERS, NOT JUST THE BIT. A bare fresh/stale verdict that disagrees with
    the compiler leaves nowhere to go but a REPL — which is where this exact question sent
    its author. Naming the newest dependency and both mtimes makes the disagreement
    diagnosable from the same command.
    """
    disk, deps, _rdeps, src_to_mod = import_dag()
    # ⚑ RESOLVE THE MODULE THROUGH THE DAG'S OWN INDEX, NOT BY STRING SURGERY. The origin's
    # first cut derived the module name by hand — strip `.agda`, swap `/`->`.`, drop a
    # leading `agda.` — and the result was NOT a key of `disk`, so the dependency walk
    # visited nothing and every log read "fresh". `import_dag` publishes `src_to_mod` for
    # exactly this; deriving a key a second way is how two spellings of one relation start
    # disagreeing (§6d).
    module = src_to_mod.get(src_rel.removeprefix("agda/"))
    if not module:
        return (
            False,
            None,
            {
                "why": f"{src_rel} is not in the import DAG — "
                f"cannot judge freshness (verdict withheld)"
            },
        )
    log = log_index(root).get(module)
    if not log:
        return False, None, {"why": "no build log for this module"}
    log_mtime = _mtime(Path(log))
    if log_mtime is None:
        return False, log, {"why": "log unreadable"}

    seen: set[str] = set()
    stack = [module]
    newest, culprit, missing = 0.0, "", 0
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        src = disk.get(current)
        if src:
            when = _mtime(corpus.ROOT / "agda" / src)
            if when is None:
                missing += 1
            elif when > newest:
                newest, culprit = when, current
        stack.extend(deps.get(current, ()))

    # ⚑ AN UNRESOLVED DEPENDENCY MAKES THE VERDICT UNSAFE, NOT MERELY IMPRECISE. If any
    # source could not be stat'd, `newest` is a LOWER BOUND, so "fresh" may be wrong while
    # "stale" is still sound. Withhold the optimistic direction.
    if missing:
        return (
            False,
            log,
            {
                "why": f"{missing} of {len(seen)} dependency source(s) "
                f"could not be read — freshness unsafe, "
                f"treating as STALE"
            },
        )
    return (
        log_mtime >= newest,
        log,
        {
            "log_mtime": log_mtime,
            "newest_dep_mtime": newest,
            "newest_dep": culprit,
            "n_deps": len(seen),
        },
    )
