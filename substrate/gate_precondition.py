#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report the gated-commit precondition against the roster the hook actually declares.

⚑⚑⚑ THE ORIGIN STATED THE RULE IN ITS OWN DOCSTRING AND THEN BROKE IT ON THE NEXT LINE. It says
*"the population is parsed from the hook, never restated"* — recording that the bar had already
been wrong TWICE, because *"all 21"* counted only the unconditional gates while six conditional
ones sat outside, three of them red. The very next statement is
`tracked = ["A5", "R8", "G1", "G6", "R2-SWEEP", "R9-residue", "S1", "T12"]`: a hand-typed list of
eight. MEASURED: `build_census --gates` declares **35** gates from the hook's own `run` call
sites. **A frozen roster cannot be wrong about what it lists, only about what it omits** — which
is why the failure recurred twice and why it is invisible from inside the list.

⚑⚑ AND THE TWO POPULATIONS ARE DIFFERENT KINDS, WHICH IS THE HARDER HALF. The hook declares
GATES; this worklist tracks ITEMS; some items correspond to a gate, some gates have no item, and
nothing joins them. So the honest report is not one number: it is the roster, the tracked set,
and **the difference in both directions** — a gate no item covers is unmonitored, and an item
naming no gate is measuring something the commit path will not enforce.

⚑ THIS WITNESS DOES NOT RUN THE GATES, AND THAT IS DELIBERATE. Running 35 gates inside a check
the gate itself runs is a loop, and several are multi-minute. It reports the PRECONDITION and
defers the verdict to the commit — the layer that can actually refuse.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass

from substrate import corpus

# The tool that owns the gate roster. ⚑ IT IS ASKED, NEVER RESTATED — the whole item.
CENSUS = ("scripts", "build_census.py")
ROSTER_MODE = "--gates"

# How a phase header and a gate row are spelled in that tool's output.
PHASE_PREFIX = "== Phase "
GATE_PREFIX = "· "

# How many names a summary line shows before eliding. ⚑ NAMED: the number appears in a slice AND
# in the comparison that decides whether to elide, and two spellings of one bound is how a report
# starts claiming "…" over a list it showed in full.
SHOWN = 6


@dataclass(frozen=True, slots=True)
class Roster:
    """The declared gates, or why they could not be read."""

    gates: tuple[str, ...]
    phases: tuple[str, ...]
    why: str

    @property
    def known(self) -> bool:
        """Report whether the roster was actually read."""
        return not self.why


def _parse(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Pull the gate names and phase labels out of the census output."""
    gates: list[str] = []
    phases: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith(PHASE_PREFIX):
            phases.append(line.removeprefix(PHASE_PREFIX).strip())
        elif line.startswith(GATE_PREFIX):
            gates.append(line.removeprefix(GATE_PREFIX).strip())
    return tuple(gates), tuple(phases)


def roster() -> Roster:
    """Read the gate roster from the tool that derives it from the hook.

    ⚑ THE SUBPROCESS IS THE POINT, NOT AN ACCIDENT. The census derives the roster by reading the
    hook's `run` call sites; importing it would bind whatever it held at import time, and asking
    it fresh is what keeps this reader from becoming the ninth frozen copy.
    """
    where = corpus.ROOT.joinpath(*CENSUS)
    if not where.exists():
        return Roster(
            gates=(), phases=(), why=f"no census tool at {'/'.join(CENSUS)} — the roster is UNREAD"
        )

    try:
        done = subprocess.run(
            [sys.executable, str(where), ROSTER_MODE],  # noqa: S603
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return Roster(gates=(), phases=(), why=f"the census would not run: {exc}")

    if done.returncode != 0:
        return Roster(
            gates=(),
            phases=(),
            why=f"the census exited {done.returncode}: {done.stderr.strip()[:200]}",
        )

    gates, phases = _parse(done.stdout)
    if not gates:
        return Roster(
            gates=(), phases=phases, why="the census declared no gate — UNREAD, not an empty roster"
        )
    return Roster(gates=gates, phases=phases, why="")


@dataclass(frozen=True, slots=True)
class Coverage:
    """How a tracked item set lines up against the declared roster."""

    declared: tuple[str, ...]
    tracked: tuple[str, ...]
    # Declared gates no tracked item names — the direction the origin could not see.
    unmonitored: tuple[str, ...]
    # Tracked items naming no declared gate.
    unenforced: tuple[str, ...]


def coverage(tracked: tuple[str, ...], declared: tuple[str, ...]) -> Coverage:
    """Compare a tracked set against the declared roster, BOTH directions.

    ⚑⚑ ONE DIRECTION IS THE DEFECT THAT RECURRED. A frozen list is never wrong about the entries
    it holds; it goes wrong by OMITTING, and only the declared-minus-tracked difference can see
    that. Reporting the other direction too is what catches an item that has outlived its gate.
    """
    have = set(tracked)
    known = set(declared)
    return Coverage(
        declared=declared,
        tracked=tracked,
        unmonitored=tuple(sorted(known - have)),
        unenforced=tuple(sorted(have - known)),
    )


def _summarise(names: tuple[str, ...], what: str) -> str:
    """Render one difference line, eliding past the shown bound."""
    shown = ", ".join(names[:SHOWN])
    more = " …" if len(names) > SHOWN else ""
    return f"  ⚑ {len(names)} {what}: {shown}{more}"


def render(got: Roster, seen: Coverage | None = None) -> str:
    """Render the precondition, keeping unread distinct from clean."""
    if not got.known:
        return f"  UNREAD — {got.why}"

    head = (
        f"  {len(got.gates)} declared gate(s) across {len(got.phases)} phase(s), "
        f"read from {'/'.join(CENSUS)} {ROSTER_MODE}"
    )
    if seen is None:
        return head

    out = [head, f"  {len(seen.tracked)} tracked item(s)"]
    if seen.unmonitored:
        out.append(_summarise(seen.unmonitored, "declared gate(s) no tracked item names"))
    if seen.unenforced:
        out.append(_summarise(seen.unenforced, "tracked item(s) naming no declared gate"))
    return "\n".join(out)


if __name__ == "__main__":
    _got = roster()
    sys.stdout.write(render(_got) + "\n")
    sys.exit(0)
