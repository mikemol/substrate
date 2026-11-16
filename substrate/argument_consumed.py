#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report whether a filtering mode CONSUMES its argument or merely accepts it.

⚑⚑⚑ FOUND BY USING THE TOOL. `--items T12` returned all nineteen rows: the key was accepted and
never read. Same class as a `--queit` typo running a gate verbose-but-passing — **an argument the
CLI takes and ignores, whose output still looks like an answer.** Nothing about the run says the
filter did not apply; the reader supplies that belief themselves.

⚑⚑ SO IT IS MEASURED BEHAVIOURALLY, NEVER BY PRESENCE. The tempting check is *"does the dispatch
mention its argument"*, and this arc has paid repeatedly for censuses that verify presence rather
than behaviour — the armed-but-inert snapshot guards being the sharpest. This RUNS the mode with
a key and asks whether the output NARROWED: a filter that is present and unwired fails, and a
filter implemented some other way passes.

⚑ THE ROW GRAMMAR IS ANCHORED, NOT PREFIXED. A `startswith("item ")` test matches both the
declaration row `item T17: DECLARED` and the verdict row `item T17: closed …`, so one asked-for
key yields two rows and any count over them is doubled. The key is parsed out and compared, which
answers *"whose row is this"* rather than *"does this line look like a row"*.

⚑ A MODE THAT RETURNS NOTHING IS NOT A NARROW ONE. Zero rows for a key that exists is a different
failure from every row coming back, and collapsing them would report a broken mode as a working
filter.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import contextlib
import io
import re
import sys
from dataclasses import dataclass
from typing import Protocol, cast

from substrate import gate_module

# The tool whose filtering mode this exercises. ⚑ IT LIVES IN `scripts/`, so it loads through
# `gate_module`, not `scratch_module` — the two loaders are directory-specific by construction,
# and reaching for the wrong one reports a present tool as absent (measured, first run).
GATE = "worklist_gate"

# A key whose row is stable enough to assert on.
PROBE = "T17"

# How a row names the item it is about.
ROW_RE = re.compile(r"^item\s+(\S+?):")


class Gate(Protocol):
    """The part of the worklist gate this witness drives."""

    def items(self, keys: list[str]) -> object:
        """Report the named items."""
        ...


@dataclass(frozen=True, slots=True)
class Narrowing:
    """What a filtered run reported."""

    asked: str
    # Keys the run reported on, in the order seen.
    reported: tuple[str, ...]
    why: str

    @property
    def known(self) -> bool:
        """Report whether the mode could be exercised."""
        return not self.why

    @property
    def answered(self) -> bool:
        """Report whether the asked-for key came back at all."""
        return self.asked in self.reported

    @property
    def unasked(self) -> tuple[str, ...]:
        """Return the keys that came back without being asked for."""
        return tuple(sorted({key for key in self.reported if key != self.asked}))

    @property
    def consumed(self) -> bool:
        """Report whether the argument narrowed the output.

        ⚑ BOTH HALVES ARE REQUIRED. A run reporting nothing narrows perfectly and answers
        nothing; a run reporting everything answers and narrows nothing. Only the conjunction is
        the property.
        """
        return self.known and self.answered and not self.unasked


def gate() -> tuple[Gate | None, str]:
    """Load the gate whose mode is exercised."""
    found, why = gate_module.gate_module(GATE)
    if found is None:
        return None, f"{GATE} will not load: {why}"
    return cast("Gate", found), ""


def keys_in(text: str) -> tuple[str, ...]:
    """Return the item keys a run reported, one per key.

    ⚑ DEDUPLICATED BY KEY, NOT BY LINE. One item emits several rows — a declaration and a verdict
    — so counting lines reports two answers where one key was asked about, and the doubling looks
    exactly like an unconsumed filter.
    """
    seen: list[str] = []
    for line in text.splitlines():
        found = ROW_RE.match(line.strip())
        if found and found.group(1) not in seen:
            seen.append(found.group(1))
    return tuple(seen)


def narrowing(probe: str = PROBE) -> Narrowing:
    """Run the filtering mode with one key and report what came back."""
    api, missing = gate()
    if api is None:
        return Narrowing(asked=probe, reported=(), why=missing)

    buffer = io.StringIO()
    # ⚑ THE MODE MAY EXIT; ITS OUTPUT STILL COUNTS. A gate refusing after printing has still
    # answered the question this reader asks, and letting the exit propagate would report an
    # exercised mode as unexercised.
    with contextlib.suppress(BaseException), contextlib.redirect_stdout(buffer):
        api.items([probe])

    return Narrowing(asked=probe, reported=keys_in(buffer.getvalue()), why="")


def render(got: Narrowing) -> str:
    """Render the verdict, keeping unexercised distinct from unconsumed."""
    if not got.known:
        return f"  UNEXERCISED — {got.why}"
    if not got.answered:
        return (
            f"  the mode does not report {got.asked} at all "
            f"({len(got.reported)} other key(s) came back)"
        )
    if got.unasked:
        return (
            f"  the key is accepted and NOT consumed: asking for {got.asked} returned "
            f"{len(got.reported)} key(s), {len(got.unasked)} unasked"
        )
    return f"  the mode answers about {got.asked} alone"


if __name__ == "__main__":
    sys.stdout.write(render(narrowing()) + "\n")
    sys.exit(0)
