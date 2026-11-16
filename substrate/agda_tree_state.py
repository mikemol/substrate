#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Two reads of the Agda tree's STATE: its content stamp, and the leaves a split emitted.

THE SEVENTH CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_census.py:786-848`, W4 tick 46).
Both are enumerations over the source tree, and both go through
`substrate.agda_files.agda_files` - THE enumeration authority - where the origin's
`tree_stamp` had a fourth private walk (`os.walk` plus `endswith`, `_build` filtered by
substring) beside the three the authority's docstring already counts.

`tree_stamp` IS THE STRADDLED-MEASUREMENT GUARD. A census taken across a mutation measures
neither state: a `--rewire-only` repair - 7 files rewritten, 42 imports pruned - was applied
WHILE a ~1322-compile census ran, so its early rows measured the pre-repair tree and its later
rows the post-repair one, a blend with no referent, and nothing in the tool would have said so.
The stamp (file count and newest mtime) is written into a ledger and re-checked at the end of a
run, so a census that straddles an edit REPORTS it rather than being quoted as fact. ⚑ THE
INSTRUMENT IS RIGHT FOR A LOCAL TREE AND WRONG ACROSS A REPO BOUNDARY: mtimes do not survive a
fetch, and a file can be rewritten to identical count with different bytes - the bazel intake
records that a content hash is the instrument for a foreign corpus. The mtime reader is a
parameter so a stamp over a different instrument is the same function.

`leaves` IS A READ OF AN EXISTING CONVENTION, NOT A SIXTH RECONSTRUCTION. The population had
no name, so every question about it was rebuilt - `git status`, a `git cat-file` against a
stash SHA (which cannot hold untracked files), a directory glob (which also catches earlier
splits), mtimes - producing four confident wrong verdicts, one of them "88% failure, serious
regression". A leaf identifies ITSELF: `split_lemmas` stamps each emitted file with the
`MARKER`, the same signal `rewire_to_leaves._is_leaf` keys on, and the head of the file is
where it sits. Deriving the population from the tree means it does not go stale between
sittings.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from substrate.agda_files import agda_files
from substrate.log_freshness import mtime_on_disk

if TYPE_CHECKING:
    from collections.abc import Callable

# The provenance marker `split_lemmas` stamps into every leaf it emits.
MARKER = "⟡cap-128-forcing"
# How much of a file's head carries the marker - the origin's read window.
HEAD_BYTES = 2048


def tree_stamp(root: str, mtime_of: Callable[[str], float | None] = mtime_on_disk) -> str:
    """Return `<count>:<newest mtime>` over every `.agda` under `root`, `_build` excluded."""
    files = agda_files(root)
    newest = max((t for t in map(mtime_of, files) if t is not None), default=0.0)
    return f"{len(files)}:{newest:.0f}"


def modules_under(root: str, prefix: str) -> list[str]:
    """Return every module under `prefix.` - the leaf set a consumed parent's directory holds.

    ⚑ `split_unblock._under` (cut 11, tick 52) walked the directory by hand; the enumeration
    authority already excludes `_build` and sorts, so this is the same read through it. The
    empty list carries the origin's two meanings at once - no such directory, or a directory
    with no sources - which `rewire_ready` distinguishes downstream as NO LEAF SET.
    """
    base = Path(root) / prefix.replace(".", "/")
    if not base.is_dir():
        return []
    rels = (Path(p).relative_to(root) for p in agda_files(str(base)))
    return sorted(".".join(r.with_suffix("").parts) for r in rels)


def leaves(root: str) -> list[str]:
    """Return every source under `root` whose head carries the split provenance marker."""
    out: list[str] = []
    for p in agda_files(root):
        try:
            with Path(p).open(encoding="utf-8", errors="replace") as f:
                head = f.read(HEAD_BYTES)
        except OSError:
            continue
        if MARKER in head:
            out.append(p)
    return out
