#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.iface_readers`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321). A name the origin only
IMPORTED is taken from its own source instead (gate-G325).
"""

from __future__ import annotations

import sys

from substrate import iface_infer
from substrate.iface_readers import (
    Assignments,
    Eligibility,
    _cases_assign,
    owed_order,
    repo_local_stubs,
)


def _selftest() -> int:
    """Cases pinning each reader's predicate, each with a discriminator."""
    cases: list[tuple[str, object, object]] = list(_cases_assign())

    def check(name: str, got: object, want: object) -> None:
        cases.append((name, got, want))

    # ⚑ THE ELIGIBILITY PREDICATE and its discriminator: a fully-stated module is eligible,
    # a partly-stated one is NOT. Without the second arm the reader could say yes to all.
    # Asked as a SET so a failure prints which arm broke rather than a bare bool.
    full = Eligibility("m", "m.py", 4, 4, ())
    part = Eligibility("m", "m.py", 4, 3, ("f:2",))
    none = Eligibility("m", "m.py", 0, 0, ())
    check(
        "eligibility discriminates fully-stated from partly-stated",
        sorted(n for n, e in (("full", full), ("part", part), ("none", none)) if e.eligible),
        ["full", "none"],
    )

    # ⚑⚑ AND AN UNSTATED ASSIGNMENT ALONE MUST BLOCK ELIGIBILITY. This is the arm the reader
    # did not have: a module whose FUNCTION half is complete but which leaves a module-level
    # constant unannotated derives a stub containing `Incomplete`, and the old predicate
    # called it eligible. Asked beside its own discriminator — a stated assignment does NOT
    # block — so a predicate refusing every assignment fails too.
    check(
        "an unstated assignment blocks eligibility; a stated one does not",
        [
            Eligibility("m", "m.py", 4, 4, (), Assignments(1, 0, 1, ("A",))).eligible,
            Eligibility("m", "m.py", 4, 4, (), Assignments(1, 1, 0, ())).eligible,
        ],
        [False, True],
    )

    # ⚑ THE RANKING IS BY SLOTS OWED, NOT RATIO — the discriminator is a pair at the SAME
    # ratio (both 0%), so only the owed count can produce this order.
    small = iface_infer.interface_of_src("def f(a): ...\n", "small")
    big = iface_infer.interface_of_src("def g(a, b, c, d, e): ...\n", "big")
    check(
        "the census ranks by slots owed, not by ratio",
        [i.module for i in owed_order([small, big])],
        ["big", "small"],
    )
    check("both ranked modules sit at the same ratio", [small.ratio, big.ratio], [0.0, 0.0])

    # ⚑ THE REPO-LOCAL POPULATION EXCLUDES PACKAGE NARROWINGS — the two readers must not be
    # handed each other's population. Discriminator: psycopg/networkx are directories
    # shadowing installed packages and must be ABSENT.
    names = {m for m, _ in repo_local_stubs()}
    check(
        "repo-local stubs exclude third-party package narrowings",
        sorted(names & {"agda_lex", "tsdbprobe", "psycopg", "networkx"}),
        ["agda_lex", "tsdbprobe"],
    )

    # ⚑ EVERY REPO-LOCAL STUB RESOLVES TO A REAL SOURCE FILE — a pairing that pointed at a
    # missing module would make the census silently short.
    check(
        "every paired source exists", sorted({p.exists() for _m, p in repo_local_stubs()}), [True]
    )

    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"iface_readers selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if "--selftest" in sys.argv:
    sys.exit(_selftest())


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
