#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which side of a split-induced name clash to rename, and to what - the plan, not the write.

THE TENTH CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_pipeline.py:339-400`, W4 tick 51): the
planning half of `cure_collisions`. The write half - `rename_at_source` and the rebuild that
follows - stays with the driver. This module decides; nothing here touches a file.

THE CURE IS SCOPED TO THIS SPLIT. A tree mid-arc carries collisions the split did not cause:
measured on the `Foundation.Sum` run, four PRE-EXISTING `Algebra/Z/*` clashes from an earlier,
half-finished Z split, and curing those renamed CANONICAL integer names into garbage
across eight files. So the plan acts only when one side of the clash is a leaf THIS split just
wrote, and says why when it does not.

RENAME THE NON-CANONICAL SIDE. The leaf the split just wrote holds the name at its CANONICAL
home; renaming it would corrupt the very name the split is publishing and propagate the
corruption to every consumer. So the OTHER side moves - the one whose local definition
collides. Both sides leaves is a human's call; neither side a leaf is not this split's.

A RENAME MUST PRODUCE A LEGAL AGDA NAME. An operator's underscores are its holes; prefixing
blindly turns `_<_` into `decint-_<_`, which is not an operator at all. `spell` rebuilds the
sections around the core: `_decint-<_`. A plain name is prefixed plainly.

THE HOME IS THE CALLER'S AUTHORITY. Which module a file declares is `agda_lex.module_path`'s
question and `module_of` is supplied, never re-derived here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

# The clash as `agda_blame.parse_clash` yields it: (consumer_file, name, previous_def_file).
Clash = tuple[str, str, str]
_AGDA = ".agda"


@dataclass(frozen=True)
class Rename:
    """The cure: rename `name` at `home` (declared by `victim`) to `new`."""

    victim: str
    home: str
    name: str
    new: str


@dataclass(frozen=True)
class Skip:
    """No cure from this split, and the reason a reader can act on."""

    name: str
    reason: str


NOT_FROM_THIS_SPLIT = "is NOT from this split — leaving it alone"
BOTH_SIDES_LEAVES = "both sides are split leaves — needs a human; leaving it alone"
# ⚑ THE ORIGIN SKIPPED THIS CASE TOO, BUT NAMED THE WRONG REASON: with no leaf set at all its
# fall-through printed "both sides are split leaves". Same verdict here, honest reason.
NO_LEAVES = "no leaf set given — cannot tell which side is canonical; leaving it alone"


def spell(victim: str, name: str) -> str:
    """Return the renamed spelling: a legal operator keeps its holes, a plain name is prefixed."""
    stem = Path(victim).name.removesuffix(_AGDA).lower()
    if name.startswith("_") or name.endswith("_"):
        core = name.strip("_")
        pre = "_" if name.startswith("_") else ""
        post = "_" if name.endswith("_") else ""
        return f"{pre}{stem}-{core}{post}"
    return f"{stem}-{name}"


def plan(clash: Clash, leaves: Iterable[str], module_of: Callable[[str], str]) -> Rename | Skip:
    """Decide the cure for one clash, given the leaves THIS split wrote."""
    consumer, name, prev = clash
    leafset = {str(Path(p).resolve()) for p in leaves}
    if not leafset:
        return Skip(name, NO_LEAVES)
    c_abs, p_abs = str(Path(consumer).resolve()), str(Path(prev).resolve())
    if c_abs not in leafset and p_abs not in leafset:
        return Skip(name, NOT_FROM_THIS_SPLIT)
    if p_abs in leafset and c_abs not in leafset:
        victim = consumer
    elif c_abs in leafset and p_abs not in leafset:
        victim = prev
    else:
        return Skip(name, BOTH_SIDES_LEAVES)
    return Rename(victim=victim, home=module_of(victim), name=name, new=spell(victim, name))
