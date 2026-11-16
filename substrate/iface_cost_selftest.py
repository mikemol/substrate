#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.iface_cost`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321). A name the origin only
IMPORTED is taken from its own source instead (gate-G325).
"""

from __future__ import annotations

import sys

from substrate import iface_dataflow
from substrate.iface_cost import (
    measure,
)


def _selftest() -> int:
    """Pin that the instrument reports counts the walk actually incurred.

    ⚑ THE CASES ASK FOR RELATIONS, NOT CONSTANTS. A pinned number here would be a fact
    about today's corpus size, and it would go red on the next file added — a suite that
    fails for a reason unrelated to what it checks teaches its reader to skip it.
    """
    before = iface_dataflow.load
    got = measure(__file__)
    cases: list[tuple[str, object, object]] = [
        ("the loader is restored after a measurement", iface_dataflow.load is before, True),
        ("the corpus is non-empty", got.corpus_size > 0, True),
        # ⚑⚑ THIS FILE COSTS ZERO CORPUS SWEEPS, AND THAT IS THE WHOLE FINDING RATHER THAN
        # a degenerate fixture. Every public parameter here is annotated, so `_compute`
        # returns STATED before `_parameter` ever reaches `call_sites` — which is precisely
        # the mechanism `--cache` and the annotate-to-generate arc are both about. A case
        # demanding `parses > 0` would fail on a fully-annotated module, i.e. would go red
        # exactly when the module got BETTER.
        ("a fully annotated module sweeps the corpus zero times", got.parses, 0),
        ("parses are attributed to distinct paths", got.parses >= got.distinct, True),
        ("every resolved slot is a slot", got.resolved <= got.slots, True),
    ]
    bad = [(name, a, b) for name, a, b in cases if a != b]
    for name, a, b in bad:
        sys.stdout.write(f"    FAIL {name}: {a!r} != {b!r}\n")
    sys.stdout.write(f"iface-cost selftest: {len(cases) - len(bad)}/{len(cases)} pass\n")
    return 1 if bad else 0


if "--selftest" in sys.argv:
    raise SystemExit(_selftest())


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
