#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where the arc's documents live — resolved from where this tool IS, not where it was called.

⚑⚑⚑ `abspath` DOES NOT RESOLVE SYMLINKS, AND THAT BROKE A CONSUMER SILENTLY. The original
derived its root as `dirname(dirname(abspath(__file__)))` and inserted `<root>/scripts` onto the
path so a bare `from climode import Mode` would resolve. Adopted BY SYMLINK from another repo,
`__file__` is the SYMLINK's path — so the root became the *consumer's* repo and the insert
pointed at a directory with no `climode` in it. Reported by cassian-observability (2026-08-31)
as `ModuleNotFoundError: No module named 'climode'` on every invocation.

⚑⚑ AND THE REPORTED CAUSE WAS WRONG IN A WAY WORTH KEEPING. It was filed as in-flight breakage
from this repo's ongoing n-split — *"the split has already broken cassian's adopted mdstruct in
place"* — under a real general rule (a consumer on a shared filesystem executes a peer's WORKING
TREE, not its commits, so a refactor is a live breaking change with no commit boundary).
MEASURED three ways: direct invocation from a foreign CWD WORKS; the same file through a symlink
FAILS; and the split had touched nothing in `scratch/`. **The defect was latent for every
symlink-adopter since `climode` was introduced.** A true rule applied to a case it does not
cover produces a confident wrong cause — which is the shape both repos keep filing.

⚑ SO THE FIX IS `resolve()`, NOT A PATH SHIM. A shim would make the import work while leaving
the tool wrong about its own home; every other root-derived path — the plan, the worklist —
would still point into the consumer's tree.

⚑ EXTRACTED FROM `scratch/mdstruct.py` (⟡mdstruct-n-split / ⟡realpath-root-sweep), file-per-mode.
⚑ ANY TOOL DERIVING A ROOT FROM `abspath(__file__)` HAS THE SAME LATENT BREAK; this is one
instance, and the sweep for the rest is owed.
"""

from __future__ import annotations

from pathlib import Path

# ⚑ `resolve()`, WHICH FOLLOWS SYMLINKS, is the whole point of this module. This file's real
# home decides the repo root, so a symlinked invocation resolves the tool's own tree rather than
# the caller's.
ROOT = Path(__file__).resolve().parent.parent

# Where the arc's plan may be. ⚑ THE RECORD LIVES OUTSIDE THE REPO in the second form —
# untracked, ungated, unsnapshotted — which is the untracked-work hazard applied to the arc's
# OWN RECORD: the document saying what was measured and why is the one nothing versions.
PLAN_CANDIDATES = (
    ROOT / "catalog" / "plan.md",
    Path("~/.claude/plans/radiant-weaving-dawn.md").expanduser(),
)

# Where the worklist may be.
WORKLIST_CANDIDATES = (
    ROOT / "catalog" / "worklist.md",
    ROOT / "worklist.md",
)


def plan() -> Path | None:
    """Return the plan document, or None when none of the candidates exists."""
    return next((p for p in PLAN_CANDIDATES if p.exists()), None)


def worklist() -> Path | None:
    """Return the worklist document, or None when none of the candidates exists."""
    return next((p for p in WORKLIST_CANDIDATES if p.exists()), None)


def docs() -> tuple[Path | None, Path | None, list[str]]:
    """Return `(plan, worklist, notes)` — where the record actually is.

    ⚑ A MISSING DOCUMENT IS REPORTED, NOT CRASHED ON. `None` plus a note says which record is
    absent, so "the worklist has no file" is a stated fact rather than a traceback — and a
    document living OUTSIDE the repo is named as such, because that is a property a reader
    acting on its contents needs to know.
    """
    found_plan, found_worklist = plan(), worklist()
    notes = []
    if found_plan is None:
        notes.append("no plan document at any candidate path")
    elif ROOT not in found_plan.parents:
        notes.append(f"the plan is OUTSIDE the repo: {found_plan}")
    if found_worklist is None:
        notes.append("no worklist document at any candidate path")
    return found_plan, found_worklist, notes
