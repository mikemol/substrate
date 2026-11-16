# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.def_split` — which arms of one function could be lifted.

⚑⚑⚑ THE OVER-REPORT IS THE FAILURE THAT MATTERS, and it was measured before it was fixed. A
first cut walked each prior statement entirely, so every loop variable and comprehension
binding read as shared state: on a 70-arm dispatch it reported 78 locals gating 64 arms, when
the arms are independent `if` blocks that merely reuse short names like `p` and `i`. The
corrected reader finds 4. A reader that inflates the blockers turns a tractable decomposition
into a wall, which is the direction that stops work.

⚑⚑ AND THE OPPOSITE ERROR IS WORSE, so it is pinned too. Calling an arm liftable when it reads
a genuine local licenses an extraction that drags that computation with it, or breaks. The
cases assert both a true dependency IS found and a rebinding is NOT.

⚑ A NESTED DEF STILL BINDS, even inside a branch — a later arm can call it, so it is real
shared state and the inner-scope walk is kept for exactly that.
"""

from __future__ import annotations

import ast

from substrate import def_split

# Two independent arms reusing the same loop variable — NOT shared state.
_REBOUND = """
def f(args):
    for p in args:
        print(p)
    for p in args:
        print(p)
"""

# A genuine dependency: the second arm reads what the first computed.
_GENUINE = """
def f(args):
    rows = load(args)
    if rows:
        print(rows)
"""

# A nested def is callable by a later arm, so it binds.
_NESTED = """
def f(args):
    if args:
        def helper():
            return 1
    if helper():
        print(1)
"""

# Everything reads only the parameter.
_CLEAN = """
def f(args):
    if "--a" in args:
        print(1)
    if "--b" in args:
        print(2)
"""

# ⚑ THE FOUR FORMS THAT ESCAPE A BLOCK. Python has no block scope, so each of these survives
# its statement and a later arm can read it. A peer audit's checklist of binding forms a
# scanner must not misread is what surfaced them; before the fix every one read as LIFTABLE.
_FOR_TARGET = """
def f(args):
    for row in args:
        pass
    if row:
        print(1)
"""

_WITH_AS = """
def f(args):
    with open('x') as fh:
        pass
    if fh:
        print(1)
"""

_WALRUS = """
def f(args):
    if (n := load()):
        pass
    if n:
        print(1)
"""

_EXCEPT_AS = """
def f(args):
    try:
        pass
    except OSError as exc:
        pass
    if exc:
        print(1)
"""


def _arms(src: str) -> list[def_split.Arm]:
    """Return the arms of the single function in `src`."""
    func = def_split.find(ast.parse(src), "f")
    return def_split.arms(func) if func else []


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── a rebound loop variable read only inside its own loop ──────────────
    # ⚑⚑⚑ MY FIRST VERSION OF THIS CASE ASSERTED THE OPPOSITE AND WAS WRONG. It said a
    # rebound loop variable is never shared state; Python has no block scope, so `for p in
    # args` leaks `p`, and a second loop rebinding it genuinely reads a name the first bound.
    # What is true is narrower: an arm that binds and reads the name WITHIN ITSELF depends on
    # nothing earlier. The over-report I set out to fix was real, and the fix I reached for
    # was too broad.
    rebound = _arms(_REBOUND)
    check(
        "an arm that binds and reads its own loop variable is liftable",
        passed=rebound[0].is_liftable,
    )
    # ⚑ AND THE SECOND ARM IS NOT, because `p` is in scope from the first — the honest
    # reading, even though the two loops share nothing but a name.
    check(
        "but a later arm rebinding the same name still reads it in scope",
        passed=not rebound[1].is_liftable,
    )

    # ── the genuine dependency IS found ────────────────────────────────────
    # ⚑ THE OPPOSITE ERROR. Calling this liftable licenses an extraction that breaks.
    genuine = _arms(_GENUINE)
    check("an arm reading an earlier assignment is blocked", passed=not genuine[1].is_liftable)
    check("and the blocking local is named", passed=genuine[1].reads_locals == ("rows",))

    # ── a nested def binds even inside a branch ────────────────────────────
    # ⚑ A LATER ARM CAN CALL IT, so it is real shared state however it is nested.
    nested = _arms(_NESTED)
    check("a nested def binds a name later arms depend on", passed=not nested[1].is_liftable)

    # ── a parameter is not a local ─────────────────────────────────────────
    # ⚑ EVERY ARM READS `args` AND NONE IS BLOCKED BY IT — a parameter is already available
    # to a lifted function, so counting it would report every dispatch as unliftable.
    clean = _arms(_CLEAN)
    check(
        "reading only a parameter leaves every arm liftable",
        passed=all(a.is_liftable for a in clean),
    )

    # ── the four block-escaping binding forms ──────────────────────────────
    # ⚑⚑⚑ THE DANGEROUS DIRECTION, AND ALL FOUR FAILED BEFORE A PEER AUDIT NAMED THEM.
    # Reporting these arms as liftable licenses an extraction that breaks, where the earlier
    # over-report merely wasted a look. Python has no block scope: each name survives its
    # statement, so a later arm reading it is a real dependency.
    for label, src, want in (
        ("a for-target", _FOR_TARGET, "row"),
        ("a with-as name", _WITH_AS, "fh"),
        ("a walrus binding", _WALRUS, "n"),
        # ⚑ `except ... as` IS DELETED at the end of its handler, so a later read is a
        # NameError rather than a dependency. It is bound anyway — an arm reading it is
        # broken code, and reporting it as shared state surfaces the bug rather than
        # blessing the arm as liftable.
        ("an except-as name", _EXCEPT_AS, "exc"),
    ):
        got = _arms(src)
        check(f"{label} blocks a later arm", passed=any(not a.is_liftable for a in got))
        check(f"and {label} is named as the blocker", passed=want in def_split.blockers(got))

    # ── the arm records its extent ─────────────────────────────────────────
    check(
        "an arm carries its line and length",
        passed=bool(clean) and clean[0].line > 0 and clean[0].lines >= 1,
    )

    # ── blockers rank locals, not arms ─────────────────────────────────────
    # ⚑ ONE LOCAL TURNED INTO A PARAMETER FREES EVERY ARM READING IT, so the decision count
    # is the number of locals.
    counts = def_split.blockers(genuine)
    check("blockers counts arms per local", passed=counts == {"rows": 1})

    # ── find returns None for an absent function ───────────────────────────
    check(
        "find returns None when the function is absent",
        passed=def_split.find(ast.parse("x = 1\n"), "nope") is None,
    )

    # ── the declared bounds match the measurement ──────────────────────────
    # ⚑⚑⚑ A CAVEAT LIST THAT DRIFTS FROM THE READER IS WORSE THAN NONE. It makes the tool
    # look more careful than it is while pointing away from the real gap, so each claim is
    # checked against a fixture rather than trusted as prose.
    blind_star = _arms("def f(args):\n    from mod import *\n    if q:\n        print(1)\n")
    check(
        "a star-import genuinely slips past the binder, as declared",
        passed=all(a.is_liftable for a in blind_star),
    )
    blind_exec = _arms("def f(args):\n    exec('h=1')\n    if h:\n        print(1)\n")
    check("and exec does too, as declared", passed=all(a.is_liftable for a in blind_exec))

    # ⚑ AND THE FORMS THAT WERE FIXED MUST NOT STILL BE CLAIMED AS BLIND. A function-scoped
    # import and a match capture were in an earlier draft of the caveat list and are now
    # caught; leaving them listed would be a false caveat.
    seen_import = _arms("def f(args):\n    import json\n    if json:\n        print(1)\n")
    check(
        "a function-scoped import is caught, so it is not listed as blind",
        passed=not seen_import[1].is_liftable
        and not any("import" in b and "*" not in b for b in def_split.BLIND_TO),
    )

    # ⚑ THE OVER-REPORT IS REAL AND DISCLOSED. `del x` unbinds, so a later read is a
    # NameError; the reader still calls it shared state, which blocks rather than licenses.
    deleted = _arms("def f(args):\n    x = 1\n    del x\n    if x:\n        print(1)\n")
    check(
        "a deleted name is still reported, as the over-report says",
        passed=not deleted[2].is_liftable,
    )
    check("and the over-report is declared", passed=bool(def_split.OVER_REPORTS))

    # ── the bounds travel with the answer ──────────────────────────────────
    # ⚑ A HEDGE IN PROSE DOES NOT SURVIVE A SUMMARY; A BOUND IN THE OUTPUT DOES. The whole
    # point of the discipline is that a reader who copies the counts also copies this.
    text_with_bounds = def_split.render(_arms(_CLEAN))
    check("the rendering carries the blind-spot list", passed="BLIND TO" in text_with_bounds)
    check("and names the over-report beside it", passed="OVER-REPORTS" in text_with_bounds)
    check(
        "and says which direction the over-report errs in",
        passed="never licenses a broken one" in text_with_bounds,
    )

    # ── the rendering states the planning consequence ──────────────────────
    text = def_split.render(genuine)
    check("the rendering names the blocking local", passed="rows" in text)
    check("and says the decisions are the locals", passed="decisions are the locals" in text)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
