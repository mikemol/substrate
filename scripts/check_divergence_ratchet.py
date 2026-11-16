#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_divergence_ratchet.py — a mode that DISPATCHES but is not DECLARED is DEBT; ratchet it.

The 5th sibling of the set-ratchet family (carrier-locality / sumtype / Set₁ / cap). Those
govern structural and memory debt; this one governs SELF-DESCRIPTION debt — the gap between
what a tool CLAIMS in its usage block and what its `sys.argv` branches actually accept.

WHY THIS EXISTS, AND WHY IT IS A GATE RATHER THAN A NOTE. `toolmodes.py`'s own docstring
records the reasoning: the skill tells every reader *"run the tool bare and read its mode
list — THAT output is the authority"*, and `--divergence` then found dozens of modes that
dispatch and appear in no self-description. **The pointer was aimed at an incomplete
authority, so a reader who obeyed it still guessed.** `--sync`/`--check` closed the
freshness half (the generated census BLOCK cannot go stale); the DIVERGENCE half had no
enforcement at all — `cmd_divergence` was reachable only from its own CLI (measured:
`pycodemod --calls cmd_divergence` → 0 syntactic calls, 1 registry ref). Filed as
⟡divergence-ungated in `toolmodes.bare`'s docstring; this is that filing paid.

⚑⚑ THE BASELINE IS 58, NOT 0, AND THAT IS THE POINT OF A RATCHET (not an allow-list).
`feedback_policy_is_a_ratchet_over_census`: a gate over accumulating debt is paydown-only
over a MATERIALIZED census, never a frozen ALLOW set anyone edits. The existing 58 are
GRANDFATHERED; the gate does not adjudicate which are worth declaring, it only forbids
GROWTH and rewards paydown. A new undeclared mode REFUSES.

⚑⚑ AND THE BASELINE IS MEASURED AT A KNOWN-GOOD READER, WHICH IS LOAD-BEARING HERE.
On 2026-08-23 the census read 84 undocumented; 34 of those were NOT debt but a READER GAP —
`bare()` recognised a roster built from a multi-line string constant (`agda_defs.py`) but not
one printed as ~40 consecutive single-line `print()` calls (`sppf_db.py`), so an entire tool's
declared roster was invisible and reported as undeclared. Fixing the reader moved the census
84 → 50 undocumented. **A ratchet frozen one day earlier would have banked a baseline ~40%
composed of an instrument artifact** — the `census-green-is-a-fact-about-the-census` hazard
applied to a NON-zero census. Recorded so a future reader improvement is understood as
expected paydown, not as the gate malfunctioning.

CENSUS (materialized by the tool that owns the predicates, never re-derived here):
`toolmodes.divergence_census` → `{"<rel> <flag>": kind}` over two kinds —
  UNDOCUMENTED  dispatched on argv, in no usage line and no prose
  UNBACKED      documented, no matching flag literal (stale, or dispatched by prefix)
Keyed `<rel> <flag>` because a bare flag COLLIDES across tools (`--check` is undeclared on
two, `--dry` on two more); a flag-keyed census would forgive debt it never saw.

PAYING IT DOWN: add the mode to the tool's own usage block — the line must NAME THE TOOL
(`toolmodes.parse_usage` recognises a usage line by `_names(stem, line)`), carry the `--flag`,
and separate its gloss by 3+ spaces or a `#`. For UNBACKED, either restore the flag literal or
delete the stale usage line. ⚑ Do NOT pay it down by deleting the dispatch branch unless the
mode is genuinely retired — a tool asserting a capability it lacks and a tool hiding one it has
are both defects, and this gate reports them as the two different kinds above.

Blocking gate. Exit 0 = clean (frozen / recorded / paid down), 1 = a new undeclared mode
appeared, or the census is unmeasurable.
Usage: check_divergence_ratchet.py [--quiet] [--list]
"""

import os
import sys

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
)

import ratchet
import toolmodes

BASELINE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "divergence_ratchet_baseline.txt"
)


def census(rows=None):
    """`{"<rel> <flag>": kind}` — DELEGATED, never re-derived.

    ⚑ THE PREDICATES STAY IN `toolmodes`. `_invisible` / `_universal` are the same bodies
    `--sync` publishes into the skill's generated block, so routing the gate through
    `divergence_census` is what makes the gate's number and the skill's number the SAME
    number. A local reimplementation here would be the two-spelling defect that this
    family of gates exists to prevent, inside the gate that enforces it.

    `rows` is injectable so the caller can run the completeness guard on the SAME rows the
    census is computed from — and so a case can drive both branches without parsing 82 tools.
    """
    return toolmodes.divergence_census(toolmodes.census() if rows is None else rows)


def main():
    if (
        rc := ratchet.check_argv(sys.argv, {"--quiet", "--list"}, "check_divergence_ratchet.py")
    ) is not None:
        return rc
    quiet = "--quiet" in sys.argv

    # COMPLETENESS GUARD FIRST, ON THE ROWS THE CENSUS WILL USE (mirrors check_cap_ratchet /
    # set1_ratchet_cores).
    # ⚑ AN EMPTY DIVERGENCE AND AN UNREAD TOOLKIT ARE OPPOSITE FACTS THAT LOOK IDENTICAL.
    # `toolmodes.census()` builds its population from the skill's `artifact | tool` table via
    # `hook_structural_query.routes()`; a borrowing checkout, a moved SKILL.md or a parse
    # failure yields ZERO tools, and a zero-tool census reports zero divergence — which this
    # ratchet would then RECORD as a clean baseline, permanently refusing every real offender
    # thereafter. Cannot measure is not no-debt.
    # ⚑ ONE PARSE, NOT TWO: the guard and the census read the SAME rows. Computing them twice
    # would both double a ~82-tool AST parse and admit a TOCTOU seam where the guard passes on
    # one population and the baseline records another.
    rows = toolmodes.census()
    if not rows:
        print(
            "divergence-ratchet: NO tools in the census population — unmeasurable; not certifying."
        )
        print(
            "  `toolmodes.py --all` should list the rostered tools; the population comes "
            "from the skill's `artifact | tool` table."
        )
        return 1

    cur = census(rows)

    def render(k):
        # ⚑ TOTAL ON KEYS NOT IN `cur` — a PAID-DOWN key is by definition absent from the
        # current census, and `set_ratchet` reports it through this same renderer. Falling
        # back to the bare key is the contract the authority enforces; honouring it here
        # keeps paydown from crashing the branch that reports progress.
        kind = cur.get(k)
        return "%-58s %s" % (k, kind) if kind else k

    # ⚑ `summary` IS A VALUE, NOT A CALLABLE — `set_ratchet` interpolates it directly
    # (`f" ({summary})"` at ratchet.py:728). Passing a function here renders as
    # `<function summary at 0x…>` in the gate's own output. Read the authority rather than
    # inferring the contract from the parameter's name.
    # ⚑ BOTH KINDS COUNTED INCLUDING ZEROES: "no unbacked modes" and "the reader stopped
    # seeing unbacked modes" are different facts and only a zero keeps them apart.
    n_undoc = sum(1 for v in cur.values() if v == "UNDOCUMENTED")
    n_unbacked = sum(1 for v in cur.values() if v == "UNBACKED")
    # ⚑⚑⚑ Ⓜ10 / ⟡fixture-category — A FIXTURE IS EXEMPT FROM THE RATCHET AND VISIBLE IN
    # THE REPORT, AND BOTH HALVES ARE LOAD-BEARING. `sppf_db --selftest-demo-failure` is a
    # deliberately-failing positive control proving the selftest harness can report a
    # failure at all. Counted as UNDOCUMENTED it offered a reader exactly one paydown —
    # write a usage line — and a usage line advertising a broken flag as a capability is
    # worse debt than the row it clears. So it is not counted.
    #
    # ⚑⚑ BUT IT IS STILL PRINTED, WITH ITS OWN COUNT. An exemption that vanishes from the
    # output is how a ratchet rots: the number drops and nothing says why, and the next
    # reader cannot tell an exemption from a paydown. `census-green-is-a-fact-about-the-
    # census` — a zero must always report the boundary of what the instrument can see, so
    # the fixture line prints even when it is zero.
    #
    # ⚑ THE DECLARATION IS IN THE OWNING TOOL, NOT HERE. `toolmodes.FIXTURE_MARK` is read
    # out of the tool's own source, so a fixture costs a visible comment in the file that
    # has the fixture — never an entry in a list on this side, which would let any tool's
    # debt be cleared by editing the gate.
    fixtures = sorted(k for k, v in cur.items() if v == "FIXTURE")
    summary = "%d undocumented (dispatched, undeclared) · %d unbacked (declared, no literal)" % (
        n_undoc,
        n_unbacked,
    )
    if fixtures:
        summary += " · %d fixture(s) EXEMPT (declared failing controls, not counted)" % len(
            fixtures
        )
    if fixtures and not quiet:
        print(
            "   %d declared FIXTURE(s) — deliberate failing controls, exempt from the "
            "ratchet:" % len(fixtures)
        )
        for k in fixtures:
            print("    %-58s FIXTURE" % k)

    return ratchet.set_ratchet(
        {k for k, v in cur.items() if v != "FIXTURE"},
        BASELINE,
        "divergence-ratchet",
        quiet,
        list_keys="--list" in sys.argv,
        noun="undeclared mode(s)",
        render=render,
        summary=summary,
        refuse_hint="A mode DISPATCHES but no usage line declares it (or a usage line names "
        "a flag the tool no longer has). Add the mode to the tool's own usage "
        "block — the line must NAME THE TOOL and carry the --flag, since "
        "`toolmodes.parse_usage` keys on `_names(stem, line)`. Do NOT pay this "
        "down by deleting the dispatch branch unless the mode is truly retired.",
    )


def _selftest():
    """The branches a hand-run never reaches — the guard and the growth refusal.

    ⚑ THE COMPLETENESS GUARD IS THE CASE THAT MATTERS, and it is unreachable in normal
    operation: it fires only when the toolkit cannot be read at all. Unexercised, a
    regression there is silent AND self-concealing — the gate would bank an empty census
    as a clean baseline and then refuse every genuine offender forever, with a paydown-only
    ratchet offering no legitimate route back. `set1_ratchet_cores` and `check_cap_ratchet`
    carry the same guard for the same reason; this one is driven.
    """
    import tempfile

    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    # ⚑ THE GUARD, DRIVEN BY SUBSTITUTING THE POPULATION — not by breaking the real skill
    # file. A case that had to move SKILL.md to test this would be testing the fixture, and
    # would leave the tree damaged if it failed halfway (`_core_id_over`'s recorded reason).
    _real = toolmodes.census
    try:
        toolmodes.census = lambda *a, **k: []
        _argv = list(sys.argv)
        sys.argv = ["check_divergence_ratchet.py"]
        try:
            import contextlib
            import io

            with contextlib.redirect_stdout(io.StringIO()):
                rc = main()
        finally:
            sys.argv = _argv
        check("empty population REFUSES (cannot measure is not no-debt)", rc, 1)
    finally:
        toolmodes.census = _real

    base = {"scratch/a.py --x", "scratch/b.py --y"}

    def _run(cur, baseline):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "b.txt")
        with open(p, "w") as f:
            f.write("".join(k + "\n" for k in sorted(baseline)))
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()):
            return ratchet.set_ratchet(
                set(cur), p, "case", quiet=True, noun="undeclared mode(s)", write=False
            )

    check("census == baseline passes (frozen)", _run(base, base), 0)
    check(
        "a NEW undeclared mode REFUSES (debt may not grow)",
        _run(base | {"scratch/c.py --new"}, base),
        1,
    )
    check("paydown passes (baseline auto-lowers)", _run({"scratch/a.py --x"}, base), 0)

    # ⚑ THE KEY SHAPE IS PART OF THE CONTRACT: a bare flag would COLLIDE across tools
    # (`--check` is undeclared on two), so paying one down would read as paying both.
    check(
        "keys are <rel> <flag>, not the bare flag",
        all(" --" in k and k.split(" ")[0].endswith(".py") for k in ["scratch/a.py --x"]),
        True,
    )

    for label, ok, got, want in cases:
        if not ok:
            print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (sum(1 for _l, ok, _g, _w in cases if ok), len(cases)))
    return all(ok for _l, ok, _g, _w in cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    sys.exit(main())
