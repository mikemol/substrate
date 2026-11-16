#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Pin the bib check guard, against the defect that produced it.

⚑⚑⚑ THE LOAD-BEARING CASE IS THIS SESSION'S OWN MANGLED CHECK. gate-F91's bib entry lost its
`--name` flag in transit, leaving `refuses:python3 substrate/drain_leverage.py <candidate>`.
That command DOES exit non-zero, so no exit-code test catches it — argparse rejects the stray
positional. The guard's job is not to catch that one (it cannot: the polarity is right), and a
case says so explicitly, because a guard credited with a catch it did not make is worse than
an absent guard.

⚑⚑ WHAT THE GUARD DOES CATCH IS THE POLARITY INVERSION, which is the half that IS mechanical:
a `refuses:` check whose command exits 0, or a `selftest:` check whose command fails. Both are
asserted here against real commands rather than fixtures, because the probe runs a subprocess
and a fake would test the fake.

⚑ AND THE FALL-THROUGH CASES CARRY EQUAL WEIGHT. `item:`, `unwitnessed` and `standing` are all
legitimate checks and none names a command, so a guard that refused them would break every
entry this session filed. Each is asserted to pass untouched.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import bib_check

ROOT = str(Path(__file__).resolve().parent.parent)

Case = tuple[str, bool]


def _parse_cases() -> list[Case]:
    """Return the cases pinning which checks name a command, and how it is read."""
    flagged = bib_check.command_of("refuses:python3 tool.py --name x")
    plain = bib_check.command_of("selftest:true")
    return [
        ("a refuses: check names a command", flagged is not None),
        ("its kind is carried", flagged is not None and flagged.kind == "refuses"),
        # ⚑ THE WHOLE-FIELD PARSE IS THE FIX. `ITEM_CHECK`'s non-whitespace-only pattern would
        #   stop at the first space and probe `python3` alone — a different command entirely.
        (
            "the argv runs to the END of the field, flags included",
            flagged is not None and flagged.argv == ("python3", "tool.py", "--name", "x"),
        ),
        ("a selftest: check names a command", plain is not None),
        ("its kind is carried too", plain is not None and plain.kind == "selftest"),
    ]


def _fallthrough_cases() -> list[Case]:
    """Return the cases pinning that a non-command check is left alone."""
    return [
        ("an item: check names no command", bib_check.command_of("item:gate-F1") is None),
        ("unwitnessed names no command", bib_check.command_of("unwitnessed") is None),
        ("standing names no command", bib_check.command_of("standing") is None),
        ("an empty command is NOT a command", bib_check.command_of("refuses:   ") is None),
        # ⚑ THE GUARD MUST FALL THROUGH, not merely fail to parse — every entry filed this
        #   session carries `unwitnessed` or `item:`, and refusing them would break the ledger.
        ("an item: check is not refused", bib_check.refusal("item:gate-F1", ROOT) is None),
        ("unwitnessed is not refused", bib_check.refusal("unwitnessed", ROOT) is None),
        ("standing is not refused", bib_check.refusal("standing", ROOT) is None),
    ]


def _polarity_cases() -> list[Case]:
    """Return the cases pinning the inversion the guard exists to catch."""
    wrong_refuses = bib_check.refusal("refuses:true", ROOT)
    wrong_selftest = bib_check.refusal("selftest:false", ROOT)
    return [
        # ⚑ A `refuses:` COMMAND THAT PASSES would be written asserting the refusal is gone.
        ("a refuses: check whose command exits 0 is REFUSED", wrong_refuses is not None),
        # ⚑ THE CASE QUOTES THE MODULE'S OWN WORDS, CASE-SENSITIVELY. A first cut spelled
        #   this lowercase and failed against a message written in caps — an assertion about
        #   text must quote the text rather than paraphrase it.
        (
            "the refusal says the entry is the durable record",
            wrong_refuses is not None and "THE DURABLE RECORD" in wrong_refuses,
        ),
        ("a selftest: check whose command fails is REFUSED", wrong_selftest is not None),
        (
            "a refuses: check whose command fails PASSES",
            bib_check.refusal("refuses:false", ROOT) is None,
        ),
        (
            "a selftest: check whose command exits 0 PASSES",
            bib_check.refusal("selftest:true", ROOT) is None,
        ),
        # ⚑ A COMMAND THAT CANNOT RUN is refused rather than waved through.
        (
            "an unrunnable command is REFUSED",
            bib_check.refusal("refuses:substrate-no-such-command-at-all", ROOT) is not None,
        ),
    ]


def _bound_cases() -> list[Case]:
    """State what this guard does NOT catch, so it is never credited with the catch.

    ⚑⚑ gate-F91's ACTUAL DEFECT IS OUT OF REACH AND MUST BE SAID SO. The mangled check exits
    non-zero for an argparse reason, which is the polarity `refuses:` requires — so the probe
    passes it, correctly. No exit code distinguishes *the tool refused* from *argparse
    refused*, and a guard claiming to catch it would be asserting a discrimination it cannot
    make. That is the finding restated at the guard layer, not a gap in the implementation.
    """
    mangled = "refuses:python3 substrate/drain_leverage.py no-such-candidate-at-all"
    intended = "refuses:python3 substrate/drain_leverage.py --name no-such-candidate-at-all"
    return [
        ("the mangled check parses as a command", bib_check.command_of(mangled) is not None),
        ("the INTENDED check passes the guard", bib_check.refusal(intended, ROOT) is None),
        # The honest statement of the bound: both spellings pass, and only a human sees why.
        (
            "the MANGLED check also passes — the guard cannot see the difference",
            bib_check.refusal(mangled, ROOT) is None,
        ),
        (
            "and the two argv differ, which is what a reader CAN see",
            bib_check.command_of(mangled) != bib_check.command_of(intended),
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _parse_cases() + _fallthrough_cases() + _polarity_cases() + _bound_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"bib_check: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
