#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.iface_bottom`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321).
"""

from __future__ import annotations

import sys

from substrate.iface_bottom import (
    ELEMENT_OF,
    PINNING_METHODS,
    STR_ARGUMENT_CALLS,
    TYPED_RETURNS,
    _Check,
    _expr,
    _fn,
    _named,
    default_type,
    given_type,
    required_of,
    returns_none,
)


def _cases_forward(check: _Check) -> None:
    """Pin the FORWARD kinds — B1 literals, B3 surfaces, B5 element access."""
    # ⚑ B1 and its DISCRIMINATOR. A bare name has no given type, so the predicate cannot be
    # answering "yes" to every expression — which is the failure a one-armed case hides.
    check("a string literal bottoms out on B1", _named(given_type(_expr('"x"'), "w")), "str")
    check("a bare NAME does not bottom out", given_type(_expr("x"), "w"), None)

    # ⚑ B3 and its DISCRIMINATOR: a call to an UNKNOWN name is not a typed surface.
    check(
        "a typed-surface call bottoms out on B3",
        _named(given_type(_expr('os.path.join("a", "b")'), "w")),
        "str",
    )
    check(
        "a call to an unknown callee does NOT bottom out",
        given_type(_expr("my_helper(1)"), "w"),
        None,
    )

    # ⚑ THE KIND IS CARRIED, because forward and backward evidence must stay distinguishable
    # downstream — collapsing them is what would let a conflict read as agreement.
    lit = given_type(_expr('"x"'), "w")
    surf = given_type(_expr("len(x)"), "w")
    check(
        "the two forward kinds are labelled apart",
        [lit and lit.kind, surf and surf.kind],
        ["literal", "typed-surface"],
    )

    # ⚑ B5 — SUBSCRIPT OF A KNOWN ELEMENT TYPE. The live shape is `carrier_of`'s
    # `parts[0].split()[0]`, which the reader could not type at all.
    check(
        "subscripting a str-split result yields str",
        _named(given_type(_expr("t.split()[0]"), "w")),
        "str",
    )
    # ⚑ ITS DISCRIMINATORS, AND THEY CARRY THE ACTUAL RISK. A SLICE is not an element — it
    # is another sequence — so reading the two alike would report `str` for a `list[str]`.
    check(
        "a SLICE is not an element and does not bottom out",
        given_type(_expr("t.split()[1:]"), "w"),
        None,
    )
    # ⚑ AND A RECEIVER WHOSE TYPE IS UNKNOWN CANNOT YIELD AN ELEMENT TYPE, so the arm is
    # not simply answering `str` to every subscript it is shown.
    check(
        "subscripting an UNKNOWN receiver does not bottom out",
        given_type(_expr("mystery[0]"), "w"),
        None,
    )
    # ⚑ A TYPE WITH NO ELEMENT ENTRY STAYS SILENT: a dict subscript is a VALUE lookup and a
    # set has no positional member, so neither may be answered from `ELEMENT_OF`.
    check(
        "subscripting a dict-returning surface does not bottom out",
        given_type(_expr("dict(x)[0]"), "w"),
        None,
    )


def _cases_display(check: _Check) -> None:
    """Pin element-refined displays — the arm that must not vote on partial arms."""
    check(
        "a list display of unknowns stays coarse",
        _named(given_type(_expr("[a, b]"), "w")),
        "list[Any]",
    )
    # ⚑ THE REFINEMENT: every element bottoms out, so the display states more than `Any`.
    check(
        "a tuple of literals is spelled positionally",
        _named(given_type(_expr('(True, "s")'), "w")),
        "tuple[bool, str]",
    )
    check(
        "a list of agreeing literals refines its element type",
        _named(given_type(_expr('["a", "b"]'), "w")),
        "list[str]",
    )
    # ⚑⚑ THE DISCRIMINATOR THAT MATTERS MOST, and it is the `carrier_of` inversion in a new
    # position: a display whose elements only PARTLY bottom out must keep the COARSE type,
    # never refine on the arms it happened to understand.
    check(
        "a tuple with one unresolved element stays coarse",
        _named(given_type(_expr("(True, whatever)"), "w")),
        "tuple[Any, ...]",
    )
    check(
        "a list whose elements DISAGREE stays coarse",
        _named(given_type(_expr('["a", 1]'), "w")),
        "list[Any]",
    )
    # ⚑ AND AN EMPTY DISPLAY HAS NO ELEMENT EVIDENCE AT ALL, so it must not refine to a
    # spurious `tuple[]` — the shape a naive `all()` over an empty list would produce.
    check(
        "an empty tuple display stays coarse",
        _named(given_type(_expr("()"), "w")),
        "tuple[Any, ...]",
    )
    # ⚑ THE NESTING IS REAL, not a special case: an element that is itself a display is
    # typed by the same floor, which is what makes `(True, ["a"])` more than a coarse tuple.
    check(
        "a nested display element is typed by the same floor",
        _named(given_type(_expr('(True, ["a"])'), "w")),
        "tuple[bool, list[str]]",
    )


def _cases_default(check: _Check) -> None:
    """Pin B2d — typing a default expression, and the PARTIAL flag that keeps `None` honest.

    ⚑ THE PARAMETER→DEFAULT LOOKUP IS NOT TESTED HERE BECAUSE IT IS NOT DONE HERE.
    `iface_dataflow.default_of` owns that alignment and carries its own cases for the
    right-aligned positional list and the parallel keyword-only holes. These cases pin what
    this module actually decides: what a default EXPRESSION is worth as evidence.
    """
    # ⚑ THE LIVE SHAPE: `scan(paths=None)`, read as DEAD while the def stated the arm.
    none_def = default_type(_expr("None"), "p.py")
    check(
        "a None default is a witness AND is marked partial",
        (_named(none_def), none_def is not None and none_def.partial),
        ("NoneType", True),
    )
    # ⚑ ITS DISCRIMINATOR: a NON-None default is the total answer the default can give, so
    # the partial flag must not be set on everything — a flag that is always True carries
    # no information and would make every defaulted slot unresolvable.
    real = default_type(_expr('"x"'), "p.py")
    check(
        "a non-None default is NOT partial",
        (_named(real), real is not None and real.partial),
        ("str", False),
    )
    # ⚑ THE KIND IS ITS OWN, so a reader can tell evidence the DEF supplies from evidence a
    # CALLER passes — the same separation the forward and backward kinds already carry.
    check(
        "a default is labelled as its own kind", none_def is not None and none_def.kind, "default"
    )
    # ⚑ A DEFAULT THIS FLOOR CANNOT TYPE IS NOT A WITNESS. `= SOME_CONST` states an arm
    # whose type is unknown, and emitting anything for it would invent one.
    check(
        "a default whose own type is unknown yields no witness",
        default_type(_expr("SOME_CONST"), "p.py"),
        None,
    )
    # ⚑ A NON-TRIVIAL DEFAULT IS TYPED BY THE SAME FLOOR, not by a second ladder — and a
    # `= ()` default is a TOTAL answer, so it must not inherit the `None` arm's partiality.
    empty = default_type(_expr("()"), "p.py")
    check(
        "a non-None default expression uses the same floor and is total",
        (_named(empty), empty is not None and empty.partial),
        ("tuple[Any, ...]", False),
    )


def _cases_noreturn(check: _Check) -> None:
    """Pin the `None` return — and the four shapes that are NOT one."""
    # ⚑ THE LIVE SHAPE: `kahn_check(disk, deps)` calls a helper and ends. Its stub says None.
    check(
        "a body that ends with no valued return is None",
        _named(returns_none(_fn("def f(a):\n    g(a)\n"), "p.py")),
        "None",
    )
    check(
        "a bare `return` is still a None return",
        _named(returns_none(_fn("def f(a):\n    if a:\n        return\n"), "p.py")),
        "None",
    )
    # ⚑ DISCRIMINATOR 1 — a VALUED return means the slot is the join of those returns, and
    # this rule must stay out of it entirely.
    check(
        "a function WITH a valued return is not a None return",
        returns_none(_fn('def f(a):\n    return "s"\n'), "p.py"),
        None,
    )
    # ⚑ DISCRIMINATOR 2 — a GENERATOR returns an iterator; typing it `None` would be a
    # confident wrong answer with a file:line, the class this module refuses.
    check(
        "a generator is NOT a None return",
        returns_none(_fn("def f(a):\n    yield a\n"), "p.py"),
        None,
    )
    # ⚑ DISCRIMINATOR 3 — a function whose only exit RAISES never returns a value at all.
    # `gen_build_makefiles.jobs` raises on two arms and lives beside the two functions this
    # rule was written for, so this is a live near-miss rather than a hypothetical.
    check(
        "a raise-only function is NOT a None return",
        returns_none(_fn('def f(a):\n    raise SystemExit("no")\n'), "p.py"),
        None,
    )
    # ⚑ DISCRIMINATOR 4 — `while True:` with no break does not fall off its end.
    check(
        "a non-breaking infinite loop is NOT a None return",
        returns_none(_fn("def f(a):\n    while True:\n        g(a)\n"), "p.py"),
        None,
    )
    # ⚑ AND ITS OWN COUNTER-ARM: the same loop WITH a break does fall through.
    check(
        "an infinite loop that CAN break is a None return",
        _named(returns_none(_fn("def f(a):\n    while True:\n        break\n"), "p.py")),
        "None",
    )
    # ⚑⚑ A NESTED def's `yield` IS NOT THIS FUNCTION'S. `ast.walk` descends into inner
    # scopes, so the generator test would misfire on any function defining a generator
    # helper — a shape this corpus's makefile generator actually contains.
    check(
        "an inner generator does not make the OUTER function one",
        _named(returns_none(_fn("def f(a):\n    def g():\n        yield 1\n    h(g)\n"), "p.py")),
        "None",
    )
    # ⚑ THE SAME SCOPE RULE FOR RETURNS: an inner def's valued return is not this slot's.
    check(
        "an inner function's valued return is not the outer's",
        _named(returns_none(_fn("def f(a):\n    def g():\n        return 1\n    h(g)\n"), "p.py")),
        "None",
    )


def _cases_required(check: _Check) -> None:
    """Pin B4 — the backward direction, in both grammatical positions."""
    # ⚑ B4 and its DISCRIMINATOR: a body that does nothing with the parameter requires
    # nothing of it, so the backward reader must return EMPTY rather than a default.
    fn = _fn('def f(a):\n    return a.endswith(".py")\n')
    check(
        "the body's `.endswith` pins the parameter to str",
        [(w.type_name, w.kind) for w in required_of(fn, "a", "p.py")],
        [("str", "body-requires")],
    )
    check(
        "a body that uses the parameter for nothing requires nothing",
        required_of(_fn("def f(a):\n    return 1\n"), "a", "p.py"),
        [],
    )
    check(
        "a DIFFERENT parameter's pin is not attributed to this one",
        required_of(fn, "b", "p.py"),
        [],
    )

    # ⚑ B4b — THE ARGUMENT POSITION, the arm whose absence made the worked case disagree
    # with its authored stub. This is the live shape from `promotion_report`.
    arg = _fn("def f(c):\n    return os.path.join(root, c)\n")
    check(
        "a parameter passed to a str-argument surface is pinned by the body",
        [(w.type_name, w.detail) for w in required_of(arg, "c", "p.py")],
        [("str", "passed to join()")],
    )
    # ⚑ ITS DISCRIMINATOR, AND IT IS THE ONE THAT MATTERS: a surface that accepts ANYTHING
    # must NOT pin. `len(x)` takes any Sized and `str(x)` takes everything, so reading the
    # RETURN table as an ARGUMENT table would manufacture `str` for unconstrained slots —
    # the exact over-claim this whole toolkit exists to refuse.
    check(
        "a surface that accepts anything pins NOTHING",
        required_of(_fn("def f(c):\n    return len(c)\n"), "c", "p.py"),
        [],
    )
    # ⚑ AND A PARAMETER THE CALL DOES NOT MENTION IS UNTOUCHED, so the arm cannot be
    # crediting every parameter of a function that happens to contain a path call.
    check(
        "a parameter absent from the pinning call is not pinned",
        required_of(_fn("def f(c, d):\n    return os.path.join(root, c)\n"), "d", "p.py"),
        [],
    )
    # ⚑⚑ THE DEFAULT MUST NOT LEAK INTO B4. Folding `= None` into the body requirement
    # would sit `NoneType` beside `str` and manufacture a CONFLICT out of an ordinary
    # `str | None` parameter — a disagreement invented by the reader, not found in the tree.
    check(
        "a None default does not enter the body requirement",
        [
            w.type_name
            for w in required_of(_fn('def f(a=None):\n    return a.endswith("x")\n'), "a", "p.py")
        ],
        ["str"],
    )


def _selftest() -> int:
    """Run cases pinning each bottom kind, each with a discriminator that must NOT bottom."""
    cases: list[tuple[str, object, object]] = []

    def check(name: str, got: object, want: object) -> None:
        cases.append((name, got, want))

    _cases_forward(check)
    _cases_display(check)
    _cases_default(check)
    _cases_noreturn(check)
    _cases_required(check)

    # ⚑ THE TABLES ARE THE FLOOR AND MUST BE NON-EMPTY — an emptied table would make every
    # slot unresolved while the suite still passed on the shape cases above.
    check(
        "all four bottom tables are populated",
        [bool(TYPED_RETURNS), bool(PINNING_METHODS), bool(STR_ARGUMENT_CALLS), bool(ELEMENT_OF)],
        [True, True, True, True],
    )

    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"iface_bottom selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.stdout.write(__doc__ or "")
    sys.exit(2)
