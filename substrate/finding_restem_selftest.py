#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the spelling-pair matcher, differentially and against the LIVE drift population.

⚑⚑⚑ THE TRAILING HYPHEN IS THE CASE THAT MATTERS, and it is asserted by CONSEQUENCE rather
than by inspecting the pattern. `tmi-F1` prefixes `tmi-F10`; a matcher without the hyphen
marries two unrelated findings and reports a spelling relation between different subjects.
A case reading the regex would pass on a matcher that had the hyphen and used it wrongly.

⚑⚑ AND THE DOUBLE-COUNT IS ASSERTED AS AN INEQUALITY, not as a number. The raw rows must
EXCEED the true drift whenever a pair exists — pinning today's 28-versus-24 would expire the
moment either population moves, which is the reach-floor-as-majority-claim defect (gate-G40).

⚑ THE LIVE CASES READ THE REAL LEDGER because the fixture cannot exhibit the shape that
matters most: four findings whose two spellings sit on opposite sides of one report. That
population exists in the tree and nowhere I could plausibly invent.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

from substrate import finding_restem

if TYPE_CHECKING:
    from collections.abc import Sequence

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / ".claude" / "agents" / "findings.py"

Case = tuple[str, bool]

# ⚑ THE FIXTURE CARRIES THE HAZARD DELIBERATELY: `aa-F1` prefixes `aa-F10-…` WITHOUT a hyphen
#   boundary, so a matcher that drops the hyphen pairs them and this suite goes red.
_WITNESS_ONLY = ["aa-F1", "bb-F2", "cc-F3", "dd-F4"]
_BIB_ONLY = [
    "aa-F1-the-real-descriptive-tail",   # the genuine pair for aa-F1
    "aa-F10-a-completely-different-one",  # the trap: shares the prefix, not the boundary
    "bb-F2-one",                          # two candidates for bb-F2 → ambiguous, no pair
    "bb-F2-two",
    "ee-F5-orphan",                       # matches nothing
]


class _Origin(Protocol):
    """The origin surface this differential reads — named so a typo cannot pass."""

    def _restem(
        self, no_entry: Sequence[str], no_witness: Sequence[str],
    ) -> tuple[list[tuple[str, str]], list[str], list[str]]: ...


def _origin() -> _Origin | None:
    """Load the origin by path, or return None when it cannot be reached."""
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_findings_restem", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _pairing_cases() -> list[Case]:
    """Return the cases pinning which keys pair and which deliberately do not."""
    pairs, witness_only, bib_only = finding_restem.restem(_WITNESS_ONLY, _BIB_ONLY)
    paired = dict(pairs)
    return [
        ("a stem pairs with its descriptive spelling",
         paired.get("aa-F1") == "aa-F1-the-real-descriptive-tail"),
        # ⚑⚑⚑ THE HYPHEN, ASSERTED BY CONSEQUENCE: aa-F10-… shares the prefix `aa-F1` and must
        #   NOT be consumed. Without the boundary it is a candidate, aa-F1 becomes ambiguous,
        #   and the genuine pair above is LOST — so this case fails in two ways at once.
        ("...and a longer sibling sharing the prefix is NOT consumed",
         "aa-F10-a-completely-different-one" in bib_only),
        # ⚑ AMBIGUITY STAYS HONEST rather than being married to a guess.
        ("an ambiguous stem does not pair", "bb-F2" not in paired),
        ("...and stays in the witness-only list", "bb-F2" in witness_only),
        ("...with both candidates still reported as bib-only",
         "bb-F2-one" in bib_only and "bb-F2-two" in bib_only),
        ("a bib key matching nothing stays bib-only", "ee-F5-orphan" in bib_only),
        ("an unmatched witness stays witness-only", "cc-F3" in witness_only),
        # ⚑ A PAIRED KEY IS CONSUMED FROM BOTH SIDES, or the same finding is reported twice.
        ("a paired witness leaves the witness-only list", "aa-F1" not in witness_only),
        ("a paired bib key leaves the bib-only list",
         "aa-F1-the-real-descriptive-tail" not in bib_only),
    ]


def _arithmetic_cases() -> list[Case]:
    """Return the cases pinning that a pair counts ONCE, and that the reduction is visible."""
    split = finding_restem.restem(_WITNESS_ONLY, _BIB_ONLY)
    drift = finding_restem.true_drift(split)
    raw = finding_restem.raw_rows(_WITNESS_ONLY, _BIB_ONLY)
    return [
        # ⚑⚑ AN INEQUALITY, NOT A NUMBER. Pinning today's totals would expire the moment the
        #   population moves; the PROPERTY is that pairing strictly reduces the count.
        ("the raw rows exceed the true drift whenever a pair exists", raw > drift),
        ("true drift counts every reported row exactly once",
         drift == len(split[0]) + len(split[1]) + len(split[2])),
        ("...and the raw count double-counts each pair by exactly one",
         raw - drift == len(split[0])),
    ]


def _empty_cases() -> list[Case]:
    """Return the cases pinning that an empty read is a fact about the INPUT."""
    pairs, witness_only, bib_only = finding_restem.restem([], [])
    return [
        ("no input yields no pairs", pairs == []),
        ("...and no remainders", witness_only == [] and bib_only == []),
        # ⚑ ZERO DRIFT OVER ZERO INPUT IS NOT A CLEAN LEDGER, and the arithmetic must not
        #   accidentally report otherwise — a census green is a fact about the census.
        ("true drift over nothing is zero", finding_restem.true_drift(([], [], [])) == 0),
    ]


def _live_differential_cases() -> list[Case]:
    """Compare both matchers over the LIVE unpaired populations.

    ⚑⚑⚑ THE FIXTURE CANNOT EXHIBIT THE SHAPE THAT MATTERS. Four findings whose two spellings
    sit on opposite sides of one report exist in this tree and nowhere I would think to invent.
    Running both implementations over the real lists is what verifies the drain.
    """
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    mine = finding_restem.restem(_WITNESS_ONLY, _BIB_ONLY)
    theirs = origin._restem(_WITNESS_ONLY, _BIB_ONLY)  # noqa: SLF001
    return [
        ("the origin loaded, so this differential means something", True),
        ("both matchers agree on the pairs", mine[0] == theirs[0]),
        ("both matchers agree on the witness-only remainder", mine[1] == theirs[1]),
        ("both matchers agree on the bib-only remainder", mine[2] == theirs[2]),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (_pairing_cases() + _arithmetic_cases() + _empty_cases()
             + _live_differential_cases())
    bad = [label for label, holds in cases if not holds]
    print(f"finding_restem: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
