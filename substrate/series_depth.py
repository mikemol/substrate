#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report whether the recorded measurements are a SERIES or only a level.

⚑⚑⚑ A LEVEL ANSWERS *"where am I"*; ONLY A SERIES ANSWERS *"what moved"*. A count that changed
cannot be read as population-changed versus case-lost from one sample — and the ledger keeps ONE
snapshot, overwriting it each run, deliberately. So the depth question is asked of the TSDB, never
of the ledger: turning the ledger into a history would rebuild the storage cassian already owns,
which is the second-store defect this item is about.

⚑⚑ UNREACHABLE IS NOT ZERO, AND THAT IS THE LOAD-BEARING DISTINCTION. *"The store is down"* and
*"no sample was ever recorded"* are different facts with different remedies. An empty read has
three causes — not written, written but not yet queryable, store down — and no predicate here
distinguishes them, so the verdict names which it means and never says *failed*.

⚑⚑ THE PROBE IS REACHED THROUGH A PROTOCOL, WHICH IS NARROWER THAN A STUB AND SAYS MORE. The
origin ran `sys.path.insert` — a process-wide change made to satisfy one call — and every
attribute it then read was `Any`. A module is not usable as a type (mypy: *"perhaps you meant a
protocol matching the module structure?"*), so what is declared here is exactly the surface this
reader consults: three names. `scratch_module` supplies the object without touching `sys.path`;
the protocol supplies the type. **The dependency is now three names wide instead of a whole
module**, and adding a fourth is an edit here rather than a silent reach.

⚑ WHAT WOULD CLOSE THIS: two or more samples inside the window — a fact about whether the
emitters have run. That is work, not a wall.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Protocol, cast

from substrate import scratch_module

# The tool that owns every read of the metrics surface.
PROBE = "tsdbprobe"

# The window the depth is read over, and the series that answers it.
WINDOW = "7d"
SELECTOR = f"count_over_time(substrate_selftest_suites[{WINDOW}])"

# Two samples is the smallest population a delta can be read from.
SERIES_FLOOR = 2


class Probe(Protocol):
    """The part of the metrics probe this reader consults.

    ⚑ THREE NAMES, NOT A MODULE. A protocol states the dependency as what is actually reached, so
    a fourth attribute cannot be read without declaring it — the opposite of an untyped module
    object, where every reach is admitted and none is recorded.
    """

    DEFAULT_BASE: str
    Unreachable: type[Exception]

    def query(self, base: str, promql: str) -> object:
        """Run an instant query against the store."""
        ...

    def extract_values(self, body: object) -> list[float]:
        """Pull the sample values out of a query response."""
        ...


@dataclass(frozen=True, slots=True)
class Depth:
    """How many samples the store holds, or why that is unknown."""

    # None when the store could not be consulted — NOT zero.
    samples: int | None
    why: str

    @property
    def known(self) -> bool:
        """Report whether a depth was actually read."""
        return self.samples is not None

    @property
    def is_series(self) -> bool:
        """Report whether the depth answers a delta question.

        ⚑ AN UNKNOWN DEPTH IS NOT A SERIES AND NOT AN EMPTY ONE. It is unknown, and a caller must
        say so rather than take whichever reading is convenient.
        """
        return self.samples is not None and self.samples >= SERIES_FLOOR


def probe() -> tuple[Probe | None, str]:
    """Load the metrics probe, narrowed to the surface this reader uses.

    ⚑ THE CAST IS THE SEAM AND IT IS CONFINED TO ONE LINE. The loader returns an untyped module;
    the protocol says which of its names are consulted. Casting once here keeps every consumer
    below typed instead of spreading `Any` outward from each attribute read — the same
    construction `engine_edges` uses for the bib field roster.
    """
    found, why = scratch_module.scratch_module(PROBE)
    if found is None:
        return None, f"{PROBE} will not load: {why}"
    return cast("Probe", found), ""


def depth(base: str | None = None) -> Depth:
    """Read how many samples the store holds over the window.

    ⚑ THE STORE'S FAILURE IS THIS READER'S DATUM, so it is caught and named rather than raised.
    Unloadable, unreachable and a malformed read are three different things for an operator to
    do, and one count would report none of them.
    """
    api, missing = probe()
    if api is None:
        return Depth(samples=None, why=missing)

    where = base if base is not None else api.DEFAULT_BASE
    try:
        rows = api.query(where, SELECTOR)
        values = api.extract_values(rows)
    except api.Unreachable:
        return Depth(
            samples=None,
            why="the store is unreachable, so depth is UNKNOWN — not zero "
            "(diagnose: tsdbprobe.py --reachable)",
        )
    except Exception as exc:  # noqa: BLE001 — any read failure is a reason, never a zero
        return Depth(samples=None, why=f"the series could not be read: {exc}")

    return Depth(samples=int(max(values)) if values else 0, why="")


def render(got: Depth) -> str:
    """Render the depth, keeping unknown distinct from empty."""
    if not got.known:
        return f"  UNKNOWN — {got.why}"
    if got.is_series:
        return f"  {got.samples} sample(s) over {WINDOW}; a delta is answerable"
    return (
        f"  {got.samples} sample(s) over {WINDOW} — a level, not a series: a moved count "
        f"cannot be read as population-changed vs case-lost"
    )


if __name__ == "__main__":
    sys.stdout.write(render(depth()) + "\n")
    sys.exit(0)
