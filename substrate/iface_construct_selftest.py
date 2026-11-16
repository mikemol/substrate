#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.iface_construct`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321). A name the origin only
IMPORTED is taken from its own source instead (gate-G325).
"""

from __future__ import annotations

import sys

from substrate.iface_construct import (
    _cases_assignments,
    _cases_dependency,
    _cases_oracle,
    _cases_probe,
    _cases_shape,
)


def _selftest() -> int:
    """Run cases pinning the shape test, the walk, the batching, the census and the oracle."""
    cases: list[tuple[str, object, object]] = []
    for maker in (_cases_shape, _cases_assignments, _cases_probe, _cases_dependency, _cases_oracle):
        cases += maker()

    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"iface_construct selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if "--selftest" in sys.argv:
    sys.exit(_selftest())


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
