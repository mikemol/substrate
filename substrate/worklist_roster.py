# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Load the live worklist roster — the hand-authored item list and its two resolution roots.

⚑⚑⚑ THIS EXISTS BECAUSE THE LOADER WAS ABOUT TO BE WRITTEN TWICE. The suite for
`worklist_predicate` needs the live roster to run its arm against, and the gate that refuses on
stale predicates needs the same roster to check. A second copy would be two rosters of one fact —
the defect this repo files repeatedly — and the copy that drifts is always the one nobody runs.

⚑⚑⚑ AND THE MACHINERY THAT USED TO BE HERE IS GONE, BECAUSE ITS PREMISE EXPIRED. This module
loaded `scripts/worklist.py` by FILE LOCATION through `importlib`, narrowed the resulting `Any`
through a `runtime_checkable` Protocol, and saved and restored `sys.path` around the exec — all of
it justified by one sentence: *"`scripts/` is not a package, so the roster is reachable only by
location."* The roster now lives in `substrate/worklist_manifest`, an ordinary package module, so
the reach is an import and every piece of that apparatus dissolves with the premise it served.

⚑⚑ THE OLD LOADER RETURNED None WHEN THE SHIM LANDED, AND THAT WAS THE MECHANISM WORKING
(gate-G221). It required the loaded module to expose `WORKLIST`; the drained `scripts/worklist.py`
IMPORTS the roster rather than defining it, so the Protocol check failed and the gate reported
UNMEASURED rather than a false zero over an empty read. A gate keyed on a LOCATION cannot follow
its subject — the honest repair is to read the subject's real home, never to aim the reader back
at the vacated one, which would go green by measuring nothing.

⚑⚑⚑ AND THE UNREADABLE CASE IS GONE RATHER THAN HANDLED, WHICH THE TYPE CHECKER FORCED ME TO SAY.
A first cut kept the `None` return and guarded it with an `isinstance` check; mypy refused it as
UNREACHABLE, because the manifest declares `WORKLIST: list[dict[str, object]]` and an import
either binds that or raises at import time. So the failure mode this module was built to report
no longer exists on this path — a missing manifest is an `ImportError` at module load, which is
louder and earlier than a `None` any caller might mistake for an empty roster. Keeping the
optional return would have been defensive code shaped by a premise the annotation retired, and
the checker caught exactly that.

⚑ WHAT THAT COSTS THE CALLER IS STATED HERE RATHER THAN DISCOVERED: `load` no longer returns
`None`, so a consumer's unreadable-roster branch is now dead and should be removed rather than
left to imply a state that cannot arise.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from substrate import worklist_manifest

#: The repo root, derived from this module's own location — the one place it is spelled.
ROOT = Path(__file__).resolve().parent.parent

#: Where `defines` predicates resolve; `grep` and `exists` resolve against ROOT.
AGDA = ROOT / "agda"


class Loaded(NamedTuple):
    """A roster and the two roots its predicates resolve against.

    ⚑ BOTH ROOTS TRAVEL WITH THE ITEMS, because `defines` resolves against the Agda tree while
    `grep`/`exists` resolve against the repo — two bases for what looks like one kind of operand.
    A consumer that took only the items would have to re-derive them, which is how a second
    authority on where the trees live gets created.
    """

    items: list[dict[str, object]]
    repo: Path
    agda: Path


def load(root: Path | None = None) -> Loaded:
    """Return the live roster and the roots its predicates resolve against.

    ⚑ THE ROOT IS AN OVERRIDE, NOT A REQUIREMENT. Callers passed one when the roster had to be
    located under a tree; the manifest is now imported, so the parameter survives only so a caller
    can resolve predicates against a different checkout. Defaulting to this module's own root
    keeps the common call site from restating a fact this file already owns.

    ⚑⚑ AN EMPTY ROSTER IS A REAL STATE AND IS RETURNED AS ONE. A manifest holding no items yields
    a `Loaded` with an empty list, never a failure — reporting emptiness as unreadability would
    make a fact about the tree indistinguishable from a broken reader, which is the collapse this
    module was originally written to prevent.
    """
    base = ROOT if root is None else root
    return Loaded(list(worklist_manifest.WORKLIST), base, base / "agda")
