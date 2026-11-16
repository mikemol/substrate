#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.iface_dataflow`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321). A name the origin only
IMPORTED is taken from its own source instead (gate-G325).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from substrate.iface_dataflow import (
    RETURN_SLOT,
    Computed,
    Resolver,
    _cases_given,
    _cases_index,
    _fn_of,
    _shape,
    _slot,
    binds,
    call_sites,
    calls_in,
    default_of,
    from_source,
    unreached_kind,
)


def _selftest() -> int:
    """Cases pinning the bottoming-out reach, the join, the cycle report and the kinds."""
    cases: list[tuple[str, object, object]] = [*_cases_given(), *_cases_index()]

    def check(name: str, got: object, want: object) -> None:
        cases.append((name, got, want))

    def slot(src: str, name: str, func: str, param: str) -> Computed:
        return _slot(src, name, func, param)

    # ⚑ B1 REACHED THROUGH A CALL SITE — the forward direction, one hop.
    check(
        "a literal call-site argument bottoms out",
        _shape(slot('def f(a):\n    return 1\nf("x")\n', "m", "f", "a")),
        ("COMPUTED", "str"),
    )
    # ⚑ THE DISCRIMINATOR: no call site at all does NOT come back as a type, never `Any`,
    # never a guess. It is now UNCALLED rather than UNRESOLVED — a named fact about the
    # corpus boundary. Without this arm the predicate could be saying COMPUTED to
    # everything.
    check(
        "a slot no one calls does NOT bottom out",
        slot("def f(a):\n    return 1\n", "d", "f", "a").status,
        "UNCALLED",
    )

    # ⚑ B3 THROUGH A CALL SITE: typeshed's answer, not one we derived.
    check(
        "a typed-surface argument bottoms out",
        _shape(
            slot('import os\ndef f(a):\n    return 1\nf(os.path.join("x", "y"))\n', "t", "f", "a")
        ),
        ("COMPUTED", "str"),
    )

    # ⚑ B2 SHORT-CIRCUITS: an annotated slot is STATED and no corpus walk is needed.
    check(
        "an annotated slot is STATED, not recomputed",
        slot("def f(a: int) -> bool:\n    return True\n", "a", "f", "a").status,
        "STATED",
    )

    # ⚑ B4 — the BACKWARD direction, with NO call site at all. This is the case that
    # proves the reader is not merely reading arguments; the discriminator above proves
    # it is not merely answering COMPUTED unconditionally.
    body = slot('def f(a):\n    return a.endswith(".py")\n', "b", "f", "a")
    check(
        "the body's own requirement resolves a slot with no callers",
        (body.status, body.computed, body.witnesses[0].kind),
        ("COMPUTED", "str", "body-requires"),
    )

    # ⚑ THE JOIN REPORTS DISAGREEMENT RATHER THAN PICKING ONE.
    conf = slot('def f(a):\n    return 1\nf("x")\nf(3)\n', "c", "f", "a")
    check(
        "disagreeing witnesses are a CONFLICT, not an averaged pick",
        (conf.status, conf.types),
        ("CONFLICT", ("int", "str")),
    )
    check("a conflicted slot yields NO single computed type", conf.computed, None)

    # ⚑ THE CYCLE MUST BE NAMED. Two functions passing each other's parameter through
    # have no bottom, and the walk must terminate saying so rather than recursing.
    cyc = slot("def f(a):\n    return g(a)\ndef g(b):\n    return f(b)\n", "y", "f", "a")
    check(
        "a slot whose only evidence loops back terminates without a type",
        (cyc.status in ("CYCLE", "UNRESOLVED"), cyc.computed),
        (True, None),
    )

    # ⚑ THE RETURN SLOT IS COMPUTED SEPARATELY — the output half, labelled apart.
    check(
        "a return bottoms out on its own return expressions",
        slot('def f(a):\n    return "s"\n', "r", "f", RETURN_SLOT).computed,
        "str",
    )
    check(
        "a return of an unresolved parameter is UNRESOLVED, not `Any`",
        slot("def f(a):\n    return a\n", "r2", "f", RETURN_SLOT).status,
        "UNRESOLVED",
    )
    # ⚑⚑ THE PARTIAL RETURN, and it is the case that caught a live WRONG ANSWER. A function
    # returning `something-unresolved` OR `None` had its unresolved arm filtered away, the
    # survivors read unanimous, and the slot reported a confident `NoneType` — inverting
    # the truth, since `None` is the fallback. A majority vote over the arms you happen to
    # understand is not a join.
    part = slot(
        "def f(a):\n    if a:\n        return a.x\n    return None\n", "r3", "f", RETURN_SLOT
    )
    check(
        "a return whose arms are only PARTLY resolved does not vote",
        (part.status, part.computed),
        ("UNRESOLVED", None),
    )

    # ⚑ THE KEYWORD EDGE COUNTS AS MUCH AS THE POSITIONAL ONE — under-counting it would
    # report a witnessed slot as dead.
    check(
        "a keyword argument is an edge too",
        slot('def f(a, b):\n    return 1\nf(1, b="s")\n', "k", "f", "b").computed,
        "str",
    )

    # ⚑ ONE SITE IS ONE WITNESS, EVEN WHEN ITS PATH IS SPELLED TWO WAYS. Measured live:
    # `here` arrives relative while `corpus.py_files` yields absolute, so a name-equality
    # de-duplication missed and every in-module call site was counted TWICE. Duplication
    # inflates agreement, and had the two readings ever disagreed it would have
    # manufactured a CONFLICT out of a single site.
    dup_src = 'def f(a):\n    return 1\nf("x")\n'
    here = from_source(dup_src, "scripts/dup_probe.py")
    if here is None:
        raise TypeError(dup_src)
    check(
        "a call site reached under two path spellings is ONE witness",
        len(call_sites("f", [str(Path(here.path).absolute())], here)),
        1,
    )

    # ⚑⚑ A SHARED NAME IS NOT A SHARED DEF. Measured live: `scan` has THREE defs in this
    # corpus and 35 calls, and the first cut credited them all to whichever def it was
    # resolving — so a slot came back "witnessed" by a module calling a different function.
    # A foreign witness does not merely add noise; it can agree and yield a confident WRONG
    # type carrying a `file:line` that reads as proof.
    #
    # ⚑ ASKED AS A SET so a failure names WHICH arm broke, and so all three directions are
    # pinned at once: a predicate answering False to everything would silently empty every
    # slot's evidence, and one answering True to everything restores the original defect.
    stranger = from_source('f("x")\n', "other/stranger.py")
    importer = from_source('from home import f\nf("x")\n', "other/importer.py")
    if stranger is None or importer is None:
        raise TypeError(dup_src)
    check(
        "only modules that can REACH the def are witnesses",
        sorted(
            n
            for n, m, h in (
                ("stranger", stranger, "home.py"),
                ("importer", importer, "home.py"),
                ("home", here, here.path),
            )
            if binds(m, "f", h)
        ),
        ["home", "importer"],
    )

    # ⚑⚑⚑ THE THREE UNREACHED KINDS, ASKED AS ONE MAPPING so a failure names which arm
    # broke and so the DISCRIMINATORS are unmissable: a classifier answering DEFAULTED to
    # everything, or UNCALLED to everything, fails here rather than in one omitted case.
    # This is the split the module exists for — the retired single string said "DEAD or
    # reached only dynamically" for all three at once.
    kinds = {
        # a default: determined AT THE DEF, no caller owes it — not dead
        "defaulted": unreached_kind(_fn_of("def f(a=None):\n    return 1\n", "f"), "a", 0)[0],
        # a KEYWORD-ONLY default: the parallel `kw_defaults` list with its `None` holes,
        # the half a positionals-only reader would report as dead
        "kwonly-default": unreached_kind(_fn_of("def f(*, a=None):\n    return 1\n", "f"), "a", 0)[
            0
        ],
        # nothing in the corpus calls it: a fact about the BOUNDARY, not about the slot
        "uncalled": unreached_kind(_fn_of("def f(a):\n    return 1\n", "f"), "a", 0)[0],
        # callers exist and none bind it, with no default: a LATENT TypeError
        "omitted": unreached_kind(_fn_of("def f(a):\n    return 1\n", "f"), "a", 3)[0],
        # ⚑ THE DISCRIMINATOR ACROSS THE SEAM: a default OUTRANKS the site count, because
        # the def determines the slot no matter who calls it. Were the order reversed this
        # arm would read OMITTED and a live parameter would be reported as a bug.
        "defaulted-and-called": unreached_kind(
            _fn_of("def f(a=None):\n    return 1\n", "f"), "a", 3
        )[0],
    }
    check(
        "the three unreached kinds are separated, and a default outranks the sites",
        kinds,
        {
            "defaulted": "DEFAULTED",
            "kwonly-default": "DEFAULTED",
            "uncalled": "UNCALLED",
            "omitted": "OMITTED",
            "defaulted-and-called": "DEFAULTED",
        },
    )

    # ⚑ THE DEFAULT IS RETURNED AS AN EXPRESSION WITH A LINE, not a bool — the note names a
    # `file:line` a reader can check, which is this module's whole discipline. Asked with
    # TWO parameters so the right-alignment of `args.defaults` is pinned: `b` has the
    # default and `a` does not, and an off-by-one would swap them.
    two = _fn_of("def f(a, b=3):\n    return 1\n", "f")
    got_b = default_of(two, "b")
    check(
        "a default is located, and an undefaulted sibling is NOT",
        (ast.unparse(got_b) if got_b is not None else None, default_of(two, "a")),
        ("3", None),
    )

    # ⚑⚑ A `__main__` GUARD IS A STATIC CALL SITE, AND THIS OVERTURNED THE PREMISE THE
    # SPLIT WAS COMMISSIONED ON. The guard's call was assumed invisible to the index,
    # motivating a fourth "dynamic entry" kind. `ast.walk` descends into the guard body, so
    # the call is seen — and `main(argv=None)` reads DEFAULTED, not dead, for the same
    # reason `scan(paths=None)` does. A kind with no instance is a hypothesis.
    guard = 'def main(argv=None):\n    return 0\nif __name__ == "__main__":\n    main()\n'
    gmod = from_source(guard, "g.py")
    if gmod is None:
        raise TypeError(guard)
    check(
        "a __main__ guard's call is seen, and the slot reads DEFAULTED not dead",
        (len(calls_in(gmod, "main")), Resolver(["g.py"]).resolve(gmod, "main", "argv").status),
        (1, "DEFAULTED"),
    )

    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"iface_dataflow selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if "--selftest" in sys.argv:
    sys.exit(_selftest())


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
