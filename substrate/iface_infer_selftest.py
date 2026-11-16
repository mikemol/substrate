#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.iface_infer`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321).
"""

from __future__ import annotations

import sys

from substrate.iface_infer import (
    interface_of_src,
    narrowing,
)


def _selftest() -> int:
    """Cases pinning the floor, the readers, and that each predicate discriminates."""
    cases: list[tuple[str, object, object]] = []

    def check(name: str, got: object, want: object) -> None:
        cases.append((name, got, want))

    typed = "def f(a: int, b: str) -> bool: ...\n"
    bare = "def f(a, b): ...\n"
    half = "def f(a: int, b) -> bool: ...\n"

    # ⚑ THE FLOOR, STATED AS A CASE. A fully annotated source derives a complete interface;
    # an unannotated one derives nothing, however hard inference tries.
    check("a fully annotated function is completely inferable", interface_of_src(typed).ratio, 1.0)
    # ⚑ DISCRIMINATOR: without this the ratio could return 1.0 for everything.
    check("an unannotated function states nothing", interface_of_src(bare).ratio, 0.0)
    check(
        "a partly annotated function states exactly its stated slots",
        (interface_of_src(half).stated, interface_of_src(half).slots),
        (2, 3),
    )

    # ⚑ THE HOLLOW SPELLINGS ARE BOTH RECOGNISED — the two-spelling cross-check.
    check(
        "an `Any` annotation is not a claim",
        interface_of_src("def f(a: Any) -> Any: ...\n").stated,
        0,
    )
    check(
        "an `Incomplete` annotation is not a claim",
        interface_of_src("def f(a: Incomplete) -> Incomplete: ...\n").stated,
        0,
    )

    # ⚑ DISCRIMINATOR PAIR for the implicit-parameter rule.
    cls = "class C:\n    def m(self, a: int) -> None: ...\n"
    check("`self` is not an annotation slot", interface_of_src(cls).slots, 2)
    check(
        "a class method is reported under its class",
        [s.name for s in interface_of_src(cls).symbols],
        ["C", "C.m"],
    )

    # ⚑ EVERY ARITY KIND COUNTS — the under-counting this guards against reads as BETTER
    # annotation than the truth, which is the dangerous direction.
    star = "def f(p, /, a, *args, k, **kw): ...\n"
    check("positional-only, star and kwargs all carry slots", interface_of_src(star).slots, 6)

    # ⚑ DISCRIMINATOR: a private name is not interface, a dunder is.
    mixed = "def _hidden(a): ...\ndef shown(a): ...\n"
    check(
        "a private function is not interface",
        [s.name for s in interface_of_src(mixed).symbols],
        ["shown"],
    )
    check(
        "a dunder method IS interface",
        [s.name for s in interface_of_src("class C:\n    def __init__(self, a): ...\n").symbols],
        ["C", "C.__init__"],
    )

    # ⚑ THE EMPTY-MODULE RULE, and its discriminator: no slots is not zero percent.
    check(
        "a module with no slots is not reported as unannotated",
        interface_of_src("X = 1\n").ratio,
        1.0,
    )

    # ⚑ THE FLOOR IS ITEMIZED, NOT SCALAR — the property that makes reader 3 a work queue.
    check(
        "the floor names the symbols it could not state",
        [s.name for s in interface_of_src(half).hollow],
        ["f"],
    )
    check(
        "a complete module has an EMPTY floor", [s.name for s in interface_of_src(typed).hollow], []
    )

    # ⚑ THE NARROWING READER, with its discriminator: a stub covering everything narrows
    # nothing, so the mode cannot be answering "yes" to every input.
    up = "def a(): ...\ndef b(): ...\ndef c(): ...\n"
    check(
        "a narrowing names what the upstream has and we do not",
        narrowing(up, "def a(): ...\n"),
        ("b", "c"),
    )
    check("a stub covering the whole upstream narrows nothing", narrowing(up, up), ())

    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"iface_infer selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.stdout.write(__doc__ or "")
    sys.exit(2)
