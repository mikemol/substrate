#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The leaf-verify ledger - `.leaf-verify.tsv`, the persisted build census, read and written ONCE.

THE FIRST CUT OF THE DRAIN'S FIFTH FILE (`catalog/library/figures.py:41,716,729,1105`, W4 tick 58),
and it retires a residue the fourth file left: the `split_pipeline` shim spelled its own
`_read_ledger` / `_write_ledger` / `_need_ledger` at tick 55, and `figures` spelled `_read` /
`census_stamp` / `census_is_current` over the same bytes - two readers of one file, keyed on the
same `#stamp` line, each padding short rows its own way. This module is the one spelling.

THE FORMAT, as the writer emits it: a first line `#stamp<TAB><count>:<newest-mtime>` from
`agda_tree_state.tree_stamp`, then one `path<TAB>verdict<TAB>cited` row per module, `cited` empty
when the verdict names no dependency. A reader pads a short row rather than refusing it - the
origin's readers did, and a ledger written before `cited` existed still reads.

THE STAMP IS THE LEDGER'S AGE, AND A CENSUS THAT STRADDLED AN EDIT MEASURES NEITHER TREE. The
writer refuses to bank when the tree moved during the run; the reader compares the recorded stamp
to the tree NOW, so a downstream figure inherits staleness instead of quoting a number that has
aged. `is_current` is pure over two strings so a suite can drive both verdicts without a tree.

`log_for` is a BINDING over `log_freshness.log_index`: the per-module `.agdai.log` lives under a
core root whose Agda version is DISCOVERED by walking `_build`, never named - two figures once
wrote a literal `2.8.0` and every failure then classified as the fallback kind, silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from substrate.agda_build_census import mod_of

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

# One census row: (source path, verdict, cited dependency or '').
Row = tuple[str, str, str]
STAMP_PREFIX = "#stamp"
# The default location, relative to the repo root.
LEDGER = Path("agda") / ".leaf-verify.tsv"


def read(path: str | Path) -> tuple[str | None, list[Row]]:
    """Return (stamp, rows) from a ledger; stamp is None when no `#stamp` line leads it."""
    stamp: str | None = None
    rows: list[Row] = []
    with Path(path).open(encoding="utf-8") as fh:
        for ln in fh:
            if ln.startswith("#"):
                if stamp is None and ln.startswith(STAMP_PREFIX):
                    stamp = ln[len(STAMP_PREFIX) :].strip() or None
                continue
            if not ln.strip():
                continue
            f = [*ln.rstrip("\n").split("\t"), "", ""][:3]
            rows.append((f[0], f[1], f[2]))
    return stamp, rows


def write(path: str | Path, stamp: str, rows: Sequence[tuple[str, str, str | None]]) -> bool:
    """Persist the census under its stamp; return False when the write failed (not a verdict)."""
    try:
        with Path(path).open("w", encoding="utf-8") as fh:
            fh.write(f"{STAMP_PREFIX}\t{stamp}\n")
            fh.writelines(f"{p}\t{v}\t{c or ''}\n" for p, v, c in rows)
    except OSError:
        return False
    return True


def stamp_of(path: str | Path) -> str | None:
    """Return the recorded stamp, or None when the ledger is absent or carries none."""
    if not Path(path).exists():
        return None
    stamp, _rows = read(path)
    return stamp


def is_current(have: str | None, now: str) -> tuple[bool, str]:
    """Return (ok, detail): the ledger describes the tree iff its stamp is the tree's stamp now."""
    if have is None:
        return False, "no leaf-verify ledger on disk -- the census has never run"
    if have != now:
        return False, (
            "the leaf-verify ledger declares itself STALE "
            f"(recorded {have}, tree is {now}); every figure read from it is fiction"
        )
    return True, f"ledger stamp {have} matches the tree"


def log_for(rel: str, index: Mapping[str, str]) -> str | None:
    """Return the `.agdai.log` for an agda-relative source, or None when the build has none."""
    return index.get(mod_of(rel))
