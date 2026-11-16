#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where the worklist project and its library live — the path vocabulary, derived from one root.

⚑⚑⚑ THIS IS THE HALF THE CONSUMERS ACTUALLY REACH FOR, AND MEASURING THAT IS WHAT SPLIT IT OUT.
`substrate/attr_reads.py wg_engine.*` reports 54 attribute reads of `scripts/wg_engine.py` across
its four consumers. FORTY-SIX of them are `ROOT`, `PROJECT` or `LIBRARY` — three path constants —
and only eight reach `engine`, `run`, `_sandbox` or `scratch_size`, the subprocess machinery the
module is NAMED for. Three of the four consumers (`wg_dispatch`, `wg_profile`, and every site in
`wg_order` but one) never touch the subprocess boundary at all. A module whose name describes what
one sixth of its use is about is two responsibilities sharing a file, and the larger one is pure.

⚑⚑ SO THE COUPLING WAS BACKWARDS, NOT MERELY UNTIDY. Reaching `wg_engine.ROOT` drags in
`subprocess`, `shutil`, `tempfile` and a mutable `os.environ` read at import — for a string join.
That is why a consumer wanting a directory name inherited a subprocess-shaped dependency, and it
is the same displacement a `sys.path` insert makes: the cost lands somewhere with no idea what
asked for it.

⚑⚑ `ROOT` IS NOT RE-DERIVED HERE — IT IS `substrate.corpus.ROOT`. The superseded module computes
its own root with `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`, which is a fourth
hand-rolled spelling of a fact this tree already owns: `substrate/attr_reads.py corpus.ROOT`
reports 150 reads across 83 files. Two roots that agree today agree by coincidence — one of them
moves when a file moves, and the disagreement surfaces as a path that does not exist rather than
as a conflict anyone can see. The reuse-search fired on this before the module was written.

⚑ AND `corpus.ROOT` USES `absolute()`, NEVER `resolve()`, WHICH IS THE PROPERTY BEING INHERITED.
Following a symlink would rewrite these paths into whatever tree the checkout is linked from, so
the derivation direction matters as much as the value.

⚑ IT IMPORTS NOTHING FROM `jea/`, `scripts/` OR `scratch/`, AND NOTHING THAT SPAWNS. The whole
claim of this module is that locating the worklist is a pure fact about the tree, answerable with
no environment read, no process and no filesystem access — so a caller can ask it, and a case can
assert it, without an engine checkout present.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import corpus

if TYPE_CHECKING:
    from pathlib import Path

#: The repository root. ⚑ DERIVED, NEVER RE-COMPUTED — see the module note.
ROOT = corpus.ROOT

#: The directory name holding every catalog, relative to `ROOT`.
CATALOG = "catalog"

#: The paperkit PROJECT the gate measures — where `paper.toml` and the items live.
PROJECT = ROOT / CATALOG / "worklist"

#: The shared bibliography and figure library the project's warrants resolve against.
LIBRARY = ROOT / CATALOG / "library"


def project_for(root: Path) -> Path:
    """Locate the worklist project under an arbitrary `root`.

    ⚑ PARAMETERISED FOR THE SAME REASON `corpus` TAKES ITS ROOT AS AN ARGUMENT: the superseded
    module's constants are module-level and immutable, so a caller measuring a DIFFERENT checkout
    — a worktree, a fixture tree in a case — had no way to ask except by rebinding a global. A
    parameter is that capability without the rebind, and it is what lets this module's own suite
    run against a temporary directory rather than the live tree.
    """
    return root / CATALOG / "worklist"


def library_for(root: Path) -> Path:
    """Locate the shared library under an arbitrary `root`, the sibling of `project_for`."""
    return root / CATALOG / "library"
