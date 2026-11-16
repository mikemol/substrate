#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.reach_baseline` — round-trip, degradation, and the header.

⚑⚑ THE ROUND-TRIP IS THE LOAD-BEARING ARM. A baseline that reads back differently than it was
written silently RELABELS DEBT: the next run sees phantom additions AND phantom paydown, and a
paydown-only ratchet banks the phantom permanently. `baseline_io`'s suite carries the same arm
for the same reason — this is the second census format in the tree, so it needs its own.

⚑ AND THE `None` COLUMN IS WHERE A ROUND-TRIP BREAKS. A suite whose source could not be
counted records an EMPTY third field, and reading that back as `0` rather than `None` would
turn "unknown" into "zero call sites" — which `reach_verdict` classifies as `deleted` instead
of `unknown`, i.e. a refusal silently becomes a pass.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import reach_baseline

# A census exercising both column shapes: a counted suite and an uncountable one.
_CENSUS: dict[str, reach_baseline.Reading] = {
    "b.py": (10, None),
    "a.py": (50, 48),
    "c.py": (97, 96),
}


def round_trip(out: list[str]) -> int:
    """Check a census survives write-then-read byte-for-byte in meaning.

    ⚑ INCLUDING THE `None`. An empty third column must read back as `None`, never `0` — see
    the module docstring: that substitution turns a refusal into a pass.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        path = str(Path(d) / "reach.tsv")
        reach_baseline.write_reach(path, _CENSUS)
        got = reach_baseline.read_reach(path)
    if got != _CENSUS:
        out.append(f"selftest: the census did not round-trip: {got!r}")
        bad += 1
    if got.get("b.py", (0, 0))[1] is not None:
        out.append("selftest: an empty static column read back as a number, not None")
        bad += 1
    return bad


def absent_reads_empty(out: list[str]) -> int:
    """Check an unreadable path reads as empty rather than raising.

    ⚑ EMPTY IS THE CORRECT DEGRADATION: every row then classifies as `new` — recorded, never
    refused. A first sighting is not a loss, so a missing baseline cannot manufacture one.
    """
    with tempfile.TemporaryDirectory() as d:
        got = reach_baseline.read_reach(str(Path(d) / "no-such-file.tsv"))
    if got != {}:
        out.append(f"selftest: a missing baseline did not read as empty: {got!r}")
        return 1
    return 0


def malformed_is_skipped(out: list[str]) -> int:
    """Check a partial or hand-edited row degrades to a missing row, not a crash.

    ⚑ THE FILE IS DERIVED AND REWRITTEN ON EVERY ACCEPTED RUN, so a torn write is reachable.
    A gate that CRASHES is strictly worse than one that refuses — the traceback is not a
    verdict, and nothing downstream can read it as one.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "reach.tsv"
        path.write_text(
            "# a comment\n\ngood.py\t42\t40\ntorn.py\nnonnumeric.py\tmany\t40\n", encoding="utf-8"
        )
        got = reach_baseline.read_reach(str(path))
    if got != {"good.py": (42, 40)}:
        out.append(f"selftest: malformed rows were not skipped cleanly: {got!r}")
        bad += 1
    return bad


def header_states_the_semantics(out: list[str]) -> int:
    """Check the minted file carries its own explanation.

    ⚑ THE HEADER IS WHERE THIS FORMAT'S ONE SUBTLETY LIVES — that it is NOT a high-water
    mark. A reader who opens the file must not have to find the writing module to learn that,
    because the natural misreading (a max) is the one that fixes a permanent floor.
    """
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "reach.tsv"
        reach_baseline.write_reach(str(path), _CENSUS)
        text = path.read_text(encoding="utf-8")
    if "NOT a high-water mark" not in text:
        out.append("selftest: the minted file does not state that it is not a maximum")
        bad += 1
    if "never hand-edited" not in text:
        out.append("selftest: the minted file does not say it is derived")
        bad += 1
    return bad


def sorted_output(out: list[str]) -> int:
    """Check rows are written sorted, so an accepted run makes a minimal diff."""
    with tempfile.TemporaryDirectory() as d:
        path = Path(d) / "reach.tsv"
        reach_baseline.write_reach(str(path), _CENSUS)
        rows = [
            ln.split("\t")[0]
            for ln in path.read_text(encoding="utf-8").splitlines()
            if ln and not ln.startswith("#")
        ]
    if rows != sorted(rows):
        out.append(f"selftest: rows are not sorted: {rows!r}")
        return 1
    return 0


_ARMS = (
    round_trip,
    absent_reads_empty,
    malformed_is_skipped,
    header_states_the_semantics,
    sorted_output,
)

_CASE_COUNT = 2 + 1 + 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"reach-baseline selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"reach-baseline selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
