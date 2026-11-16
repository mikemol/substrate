#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The build's census, READ from its own per-module logs - never a second build.

THE SIXTH CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_census.py:512-707`, W4 tick 45). The
census already exists on disk: `gen_build_makefiles` emits one `<Mod>.agdai.log` per module,
interleave-proof by construction, and only touches the core after agda exits 0 - so a missing
core IS the failure signal, dependency order is the explicit `.agdai` DAG, and incrementality
is mtime over it. A first cut recompiled 1322 leaves in dependency-blind order and could not
tell "this leaf is broken" from "its dependency was never built". A census of a build is a
READ of the build's artifacts.

THIS MODULE COMPOSES THE READERS ALREADY LANDED RATHER THAN RE-IMPLEMENTING THEM: the verdict
is `agda_blame.blame` (one implementation of own-vs-dependency), and freshness is
`log_freshness.newest_dependency` over the DAG `make` judges staleness by. ⚑ THE ORIGIN CARRIED
ITS OWN COPY OF THE FRESHNESS RULE, AND THE TWO DISAGREED: its `census_from_build` treated an
unreadable source as mtime `0.0` (so a module whose source could not be stat'd read as fresh
and could be certified `clean`), while its `log_is_fresh` treated the same case as UNSAFE and
withheld the optimistic direction. One relation, two rules. The copy is retired here: an
unreadable dependency makes the row `stale`, which is the sound direction - `stale` means
UNMEASURED, and an incomplete census is not a low count.

`stale` CONFLATES TWO STATES, and `stale_why` splits them, because three unfounded assertions
about it were made in one session (that a rebuild refreshes it, that it flattered clean, that
it would drop to ~0 - it went 78 to 80 across a full `-k` build). `blocked-upstream`: a
transitive import failed, `make -k` never attempted this module, no rebuild moves it - fix the
root. `unbuilt`: every import clean, the log simply predates a source - the one a rebuild
fixes, with WHICH source named. `no-core`: the log is fresh but the `.agdai` is absent, so the
freshness test and make's own up-to-date test DISAGREE about this module.

⚑ THE CORE PATH IS DERIVED FROM THE LOG, NEVER SPELLED. The origin's `stale_why` rebuilt it as
`_build/2.8.0/agda/...` - an agda VERSION restated in a tool, the build-figure copy the
always-loaded instructions forbid. The build writes the log beside the core (`<core>.log`), so
`core_of(log)` strips the suffix and no version is named anywhere here.

THE TREE IS ONE PARAMETER. The per-file gate refused six positional inputs, and it was right:
the log index, the DAG, the sources root and the three readers (mtime, text, existence) are
one thing - the build tree as this census sees it - so `Tree` carries them and a suite swaps
the whole vantage at once. `Tree.on_disk(root, build_dir)` is the production one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import agda_blame, log_freshness

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping

    from substrate.agda_dag import Dag

Row = tuple[str, str, str | None]
Why = tuple[str, str, str]
# Verdicts under which a module's dependants were never attempted by `make -k`.
FAILED = frozenset({"build-failed", "own", "dependency"})
_AGDA = ".agda"


def _read_on_disk(path: str) -> str | None:
    """Read a log leniently, or None where it cannot be opened."""
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _exists_on_disk(path: str) -> bool:
    """Return whether a core file is present."""
    return Path(path).exists()


@dataclass(frozen=True)
class Tree:
    """The build tree as the census reads it: the DAG, the log index, the root, three readers."""

    dag: Dag
    index: Mapping[str, str]
    sources_root: str
    mtime_of: Callable[[str], float | None] = log_freshness.mtime_on_disk
    read_text: Callable[[str], str | None] = _read_on_disk
    core_exists: Callable[[str], bool] = _exists_on_disk
    verdicts: dict[str, str] = field(default_factory=dict)

    @classmethod
    def on_disk(cls, dag: Dag, sources_root: str, build_dir: str) -> Tree:
        """Return the production tree: the sorted log index over `build_dir`, disk readers."""
        return cls(dag, log_freshness.log_index(build_dir), sources_root)


def core_of(log: str) -> str:
    """Return the `.agdai` path a `.agdai.log` describes - the log sits beside the core."""
    return log.removesuffix(".log")


def rel_of(mod: str) -> str:
    """Return a module's source path relative to the agda dir."""
    return mod.replace(".", "/") + _AGDA


def mod_of(rel: str) -> str:
    """Return the module a relative source path names (the inverse of rel_of)."""
    return rel.removesuffix(_AGDA).replace("/", ".")


def _row(mod: str, log: str, tree: Tree) -> Row | None:
    """Return one module's row, or None where its log cannot be read."""
    txt = tree.read_text(log)
    if txt is None:
        return None
    rel = rel_of(mod)
    lm = tree.mtime_of(log)
    newest, _who, missing, _n = log_freshness.newest_dependency(
        mod, tree.dag, tree.mtime_of, tree.sources_root
    )
    if lm is None or missing or lm < newest:
        return (rel, "stale", "")
    if tree.core_exists(core_of(log)):
        return (rel, "clean", "")
    kind, cited = agda_blame.blame(rel, txt)
    return (rel, kind, cited)


def census(tree: Tree) -> list[Row]:
    """Return [(rel, verdict, cited)] over every logged module: stale, clean, or blamed."""
    rows = (_row(mod, log, tree) for mod, log in sorted(tree.index.items()))
    return [r for r in rows if r is not None]


def _blocker(mod: str, dag: Dag, verdict: Mapping[str, str]) -> tuple[str | None, set[str]]:
    """Return the first transitive import with a failed verdict, and every import visited."""
    seen: set[str] = set()
    stack = list(dag.deps.get(mod, ()))
    while stack:
        d = stack.pop()
        if d in seen:
            continue
        seen.add(d)
        if verdict.get(d) in FAILED:
            return d, seen
        stack.extend(dag.deps.get(d, ()))
    return None, seen


def _newest_source(mods: Iterable[str], tree: Tree) -> str:
    """Return which of `mods` has the newest readable source, or '' if none is readable."""
    newest, who = 0.0, ""
    for d in mods:
        src = tree.dag.disk.get(d)
        t = tree.mtime_of(f"{tree.sources_root}/{src}") if src else None
        if t is not None and t > newest:
            newest, who = t, d
    return who


def stale_why(rows: Iterable[Row], tree: Tree) -> list[Why]:
    """Return [(module, cause, witness)] for every stale row; a witness is never a bare verdict."""
    verdict = {mod_of(rel): v for rel, v, _c in rows}
    out: list[Why] = []
    for mod, v in sorted(verdict.items()):
        if v != "stale":
            continue
        bad, seen = _blocker(mod, tree.dag, verdict)
        if bad:
            out.append((mod, "blocked-upstream", bad))
            continue
        log = tree.index.get(mod)
        if log is None or not tree.core_exists(core_of(log)):
            out.append((mod, "no-core", "no .agdai — compile produced no core"))
            continue
        out.append((mod, "unbuilt", _newest_source([mod, *sorted(seen)], tree) or mod))
    return out
