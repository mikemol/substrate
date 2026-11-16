#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report whether the leaf-verify ledger describes the tree it claims to describe.

⚑⚑⚑ THIS IS THE ITEM EVERY DOWNSTREAM FIGURE INHERITS FROM, AND IT IS A MEASUREMENT, NOT A
PROJECTION. The ledger records the stamp of the tree it was built against; the tree can be
re-stamped now. If the two differ, **every figure read from that ledger is fiction** — so a
downstream witness inherits staleness rather than quoting a number that has aged out from under
it.

⚑⚑ THE STAMP EXISTS BECAUSE A CENSUS THAT STRADDLES AN EDIT MEASURES NEITHER TREE. Recorded in
the tool that owns it: a `--rewire-only` repair rewrote 7 files mid-census, so the early rows
measured the pre-repair tree and the later rows the post-repair one — *"a blend with no referent,
and nothing in the tool would have said so."* Comparing stamps is what makes that reportable
instead of invisible.

⚑ THE THREE STATES ARE DISTINCT AND THE ORIGIN COLLAPSED TWO OF THEM INTO ONE BOOLEAN. A ledger
that has never been built, a ledger that has gone stale, and a current ledger call for three
different actions — run the census, re-run it, read it — and `(ok, detail)` makes the first two
the same row for anything that branches on the flag rather than reading the prose.

⚑ AND THE ORIGIN READ A 218 KB FILE TWICE TO GET ITS FIRST LINE. `_read(LEDGER).splitlines()[0]
if _read(LEDGER) else ""` calls the reader on both sides of the conditional. The stamp is the
first line, so one bounded read answers it.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, cast

from substrate import corpus, scratch_module

# The tool that owns the tree fingerprint.
STAMPER = "split_census"

# Where the census records what it measured, and the tree it stamps.
LEDGER = ("agda", ".leaf-verify.tsv")
TREE = "agda"

# The ledger's own header: `#stamp <count>:<newest-mtime>`.
STAMP_RE = re.compile(r"#stamp\s+(\S+)")


class State(Enum):
    """What a reader may conclude about the ledger.

    ⚑ THREE STATES, NOT A BOOLEAN. ABSENT and STALE both mean *"do not read the figures"*, but
    one is a census to run and the other a census to re-run — and a caller branching on a flag
    cannot tell them apart without parsing the prose beside it.
    """

    CURRENT = "current"
    STALE = "stale"
    ABSENT = "absent"
    UNMEASURED = "unmeasured"


class Stamper(Protocol):
    """The part of the census tool this reader consults."""

    def tree_stamp(self, root: str = ...) -> str:
        """Return a fingerprint of the tree's content state."""
        ...


@dataclass(frozen=True, slots=True)
class Currency:
    """The ledger's state, and the stamps that decided it."""

    state: State
    # What the ledger says it measured, when it says anything.
    recorded: str | None
    # What the tree stamps to now, when it could be read.
    tree: str | None
    why: str

    @property
    def readable(self) -> bool:
        """Report whether figures read from this ledger mean anything."""
        return self.state is State.CURRENT


def ledger_path() -> str:
    """Return the ledger's absolute path."""
    return str(corpus.ROOT.joinpath(*LEDGER))


def recorded_stamp() -> str | None:
    """Read the stamp the ledger recorded, or None when it declares none.

    ⚑ ONE BOUNDED READ, NOT TWO WHOLE-FILE READS. The stamp is the first line of a 218 KB file;
    the origin read the entire thing on both sides of a conditional to reach it.
    """
    path = corpus.ROOT.joinpath(*LEDGER)
    if not path.exists():
        return None
    with path.open(encoding="utf-8", errors="replace") as handle:
        first = handle.readline()
    found = STAMP_RE.match(first)
    return found.group(1) if found else None


def stamper() -> tuple[Stamper | None, str]:
    """Load the tool that fingerprints the tree."""
    found, why = scratch_module.scratch_module(STAMPER)
    if found is None:
        return None, f"{STAMPER} will not load: {why}"
    return cast("Stamper", found), ""


def currency() -> Currency:
    """Report whether the ledger is current, and why when it is not.

    ⚑ THE STAMPER'S ABSENCE IS UNMEASURED, NOT STALE. Being unable to fingerprint the tree means
    the comparison did not happen — reporting that as staleness would name a defect in the
    ledger on the strength of a defect in the reader.
    """
    recorded = recorded_stamp()
    if recorded is None:
        return Currency(
            state=State.ABSENT,
            recorded=None,
            tree=None,
            why=f"no leaf-verify ledger at {'/'.join(LEDGER)} — the census has never run",
        )

    api, missing = stamper()
    if api is None:
        return Currency(state=State.UNMEASURED, recorded=recorded, tree=None, why=missing)

    now = api.tree_stamp(TREE)
    if recorded != now:
        return Currency(
            state=State.STALE,
            recorded=recorded,
            tree=now,
            why=f"the ledger declares itself STALE (recorded {recorded}, tree is "
            f"{now}); every figure read from it is fiction",
        )
    return Currency(
        state=State.CURRENT,
        recorded=recorded,
        tree=now,
        why=f"ledger stamp {recorded} matches the tree",
    )


def render(got: Currency) -> str:
    """Render the verdict, naming the state as well as the reason."""
    return f"  {got.state.value.upper()} — {got.why}"


if __name__ == "__main__":
    sys.stdout.write(render(currency()) + "\n")
    sys.exit(0)
