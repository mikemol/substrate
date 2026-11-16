#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.stub_top_type`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321). A name the origin only
IMPORTED is taken from its own source instead (gate-G325).
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate.stub_top_type import (
    derived_of,
    findings,
    slots,
    top_slots,
)


def _selftest() -> int:
    """Cases pinning that DERIVABLE is reported and UNDERIVABLE is not."""
    cases: list[tuple[str, object, object]] = []

    def check(name: str, got: object, want: object) -> None:
        cases.append((name, got, want))

    stub = (
        "NEXT: object\nHEADER: _HeaderLike\nSUFFIX: str\nSECTION: builtins.object\nCOUNT: object\n"
    )

    check(
        "annotated module-level names are read",
        [s.name for s in slots(stub)],
        ["NEXT", "HEADER", "SUFFIX", "SECTION", "COUNT"],
    )

    # ⚑ THE TOP TYPE IN BOTH SPELLINGS, and the DISCRIMINATORS beside it: a named Protocol and
    # a concrete builtin are not the top type. Without these a predicate answering "yes" to
    # everything would pass the positive case.
    check(
        "both spellings of the top type are found",
        [s.name for s in top_slots(stub)],
        ["NEXT", "SECTION", "COUNT"],
    )
    check(
        "a named Protocol is NOT the top type",
        [s.name for s in top_slots("HEADER: _HeaderLike\n")],
        [],
    )
    check("a concrete type is NOT the top type", [s.name for s in top_slots("SUFFIX: str\n")], [])

    # ⚑⚑ THE ONE-SIDED VERDICT, BOTH HALVES. `NEXT` bottoms out and is DEBT; `COUNT` does not
    # and must stay silent. Asking only the first would pass a reader that reports everything.
    derived = {
        "NEXT": ("re.Pattern[str]", "scratch/agda_lex.py:59"),
        "SECTION": ("re.Pattern[str]", "scratch/agda_lex.py:1106"),
    }
    got = findings(stub, derived)
    check("a derivable object slot is reported as debt", [f.name for f in got], ["NEXT", "SECTION"])
    check(
        "an UNRESOLVED object slot is NOT reported", [f.name for f in got if f.name == "COUNT"], []
    )
    check("a finding carries the derived type", next(f.derived for f in got), "re.Pattern[str]")
    check(
        "a finding carries a file:line witness",
        next(f.witness for f in got),
        "scratch/agda_lex.py:59",
    )
    check("a finding carries the stub's own line", next(f.stub_line for f in got), 1)

    # ⚑ A DECISION IS NEVER A FINDING, even when the derivation could name it. This is the
    # `HEADER` case: it is not spelled `object`, so it is outside the population entirely.
    check(
        "a Protocol slot is not reported even if derived",
        findings("HEADER: _HeaderLike\n", {"HEADER": ("X", "f.py:1")}),
        (),
    )

    # ⚑ AND A STUB THAT WILL NOT PARSE DECLARES NO SLOTS RATHER THAN RAISING — the same
    # absent-vs-unreadable care `stub_declines` records. The caller that owns the parse
    # verdict is `check_stub_authority`, which already fails on it.
    check("an unparseable stub yields no slots", slots("def f(x: int -> None: ...\n"), ())

    # ⚑⚑ THE LIVE TREE IS THE DISCRIMINATOR THE FIXTURES CANNOT BE. Every repo stub is now
    # repaired, so each must report ZERO — a reader that flagged indiscriminately would fail
    # here while passing every case above. `agda_lex` is the sharpest of the four: it still
    # HOLDS a declined slot (`HEADER`), so a zero here says the reader distinguishes a
    # refusal from debt on real source rather than on a fixture.
    root = Path(__file__).absolute().parent.parent
    live = [
        ("stubs/agda_lex.pyi", "scratch/agda_lex.py"),
        ("stubs/check_carrier_locality.pyi", "scripts/check_carrier_locality.py"),
        ("stubs/gen_build_makefiles.pyi", "scripts/gen_build_makefiles.py"),
    ]
    for rel_stub, rel_mod in live:
        stub_p, mod_p = root / rel_stub, root / rel_mod
        if not (stub_p.is_file() and mod_p.is_file()):
            continue
        got_live = findings(
            stub_p.read_text(encoding="utf-8", errors="replace"), derived_of(str(mod_p))
        )
        check(f"{rel_stub} has no derivable object left", [f.name for f in got_live], [])

    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"stub_top_type selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if "--selftest" in sys.argv:
    sys.exit(_selftest())


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
