#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_baseline_health.py — a ratchet's BASELINE is itself an artifact, and it can rot.

⚑ WHY THIS GATE EXISTS.  Every other gate in this hook measures the TREE.  This one measures
the GATES — specifically, whether each ratchet's baseline can support the verdict its gate
returns.  Measured 2026-08-20, five ratchets had NO baseline file at all, and `set_ratchet`'s
no-baseline branch does this:

    if not os.path.exists(baseline_path):
        if not write:
            print(f"{label}: no baseline … — would record {len(cur)} {noun}")
            return 0                        # ← EXIT 0, whatever it just measured

So `check_mypy_ratchet --quiet` exits 0 while reporting 116 unrecorded type errors, and the
hook prints a green line.  "The type gate passes" then means "the ratchet has never been
baselined", which is a fact about the CENSUS, not about the tree — this repo's
`census-green-is-a-fact-about-the-census` failure, live, in five gates at once.

⚑⚑ AND THE OBVIOUS-LOOKING SIBLING CONDITION IS NOT A DEFECT — IT IS THE STRONGEST SETTING.
A baseline file that EXISTS AT ZERO BYTES reads as the empty set, so `added = cur` and EVERY
offender is a NEW key: the gate refuses everything and forgives nothing.  That is a
ZERO-TOLERANCE ratchet, and it is self-maintaining — `paid` is always empty, so the
`write and not added` guard can never quietly lower it into forgiving something.  An operator
who wants no grandfathering wants exactly this.

  ABSENT  →  a free pass.        REFUSED here.
  EMPTY   →  zero tolerance.     ACCEPTED here, and reported as the strong setting.

Conflating the two is the whole point of this gate: they look alike in a directory listing
(`0` vs no row) and they are opposite in effect.  `scripts/gate_census.py --baselines` is the
enumerating reader; this is the blocking gate over the same derivation.

⚑ NOT A RATCHET, DELIBERATELY.  A ratchet over baseline-health would need a baseline, which
is the regress this gate exists to stop.  It is a pure 0-tolerance violation gate: ABSENT is
refused, and the paydown is to mint the baseline ON THE COMMIT PATH (never by hand — setting
SUBSTRATE_RATCHET_WRITE=1 banks a census against a tree nothing has approved).

Blocking gate. Exit 0 = every ratchet's baseline can support its verdict, 1 = at least one
gate is returning a verdict its baseline cannot support.
Usage: check_baseline_health.py [--quiet] [--list]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ratchet
import gate_census


def census():
    """{'<script>::<baseline>'} for every ratchet whose baseline is a DEFECT.

    ⚑ THE PREDICATE IS `state.is_defect`, NOT A NAME COMPARISON.  This read
    `state == "ABSENT"` and was correct — but it encoded "which states are violations" HERE,
    while five other sites encoded their own answers to their own questions about the same
    four strings.  Three of those got it wrong.  The property now lives on
    `ratchet.BaselineState`, so this gate and every reader agree by construction rather than
    by everyone remembering the same rule.

    EMPTY is the zero-tolerance setting and is not debt; UNREAD is a fact about this reader
    (a baseline path that is not a string literal) and must not be reported as a fact about
    the gate — that is the method-vs-substrate collapse, and a gate that counted its own
    parse gaps as violations would be the worst instance of it.  Both are now encoded as
    `is_defect=False` on the states themselves.
    """
    return {
        "%s::%s" % (rel, b)
        for rel, b, state, _keys in gate_census.baseline_health()
        if state.is_defect
    }


def unread():
    """The rows this reader could not resolve — reported, never counted as violations."""
    return [
        (rel, b)
        for rel, b, state, _k in gate_census.baseline_health()
        if state is ratchet.BaselineState.UNREAD
    ]


def strong():
    """The zero-tolerance baselines — reported as a GOOD state, not a finding."""
    return [
        (rel, b)
        for rel, b, state, _k in gate_census.baseline_health()
        if state is ratchet.BaselineState.EMPTY
    ]


def main():
    rc = ratchet.check_argv(sys.argv, {"--quiet", "--list"}, "check_baseline_health")
    if rc is not None:
        return rc
    quiet = "--quiet" in sys.argv
    rows = gate_census.baseline_health()
    bad = sorted(census())
    unr = unread()
    zt = strong()

    if "--list" in sys.argv:
        print("%-40s %-34s %-7s %s" % ("gate", "baseline", "state", "keys"))
        for rel, b, state, keys in rows:
            # ⚑ THE MARK IS FOR DEFECTS, AND EMPTY IS NOT ONE.  `!= "ok"` flagged all eight
            # zero-tolerance rows, contradicting the summary THREE LINES BELOW that calls them
            # the strong setting — the same collapse `gate_census --baselines` made in its
            # headline, here in the gate that gets every other reading right. A ⚑ beside a
            # baseline granting no exceptions teaches the reader that strictness is debt.
            # Now asked of the state rather than re-derived from its name.
            print(
                "%-40s %-34s %-7s %d%s"
                % (rel, b, state, keys, "   ⚑" if state.deserves_mark else "")
            )
        print(
            "\n%d ratchet baseline(s): %s."
            % (
                len(rows),
                ", ".join(
                    "%d %s" % (sum(1 for r in rows if r[2] == s), s.name)
                    for s in ratchet.BaselineState.all()
                ),
            )
        )
        return 0

    if zt and not quiet:
        print(
            "baseline-health: %d ZERO-TOLERANCE baseline(s) — empty, so every offender is a "
            "NEW key and nothing is grandfathered. This is the STRONG setting, not a defect:"
            % len(zt)
        )
        for rel, b in zt:
            print("    ∅ %s  (%s)" % (b, rel))

    if unr and not quiet:
        print(
            "baseline-health: %d baseline path(s) this reader could not resolve — a fact "
            "about the READER, not the gate:" % len(unr)
        )
        for rel, b in unr:
            print("    ? %s  %s" % (rel, b))

    if bad:
        print(
            "baseline-health: BROKEN — %d ratchet(s) have NO baseline, so `set_ratchet` "
            "takes the `no baseline -> record and pass` branch and the gate EXITS 0 "
            "REGARDLESS of what it measured:" % len(bad)
        )
        for k in bad:
            rel, b = k.split("::", 1)
            print("    + %s  (%s)" % (b, rel))
        print("  A green verdict from these gates is a fact about the CENSUS, not the tree.")
        print("  PAYDOWN: mint the baseline ON THE COMMIT PATH — `git commit` is the promotion")
        print("  gate. Setting SUBSTRATE_RATCHET_WRITE=1 by hand banks a census against a tree")
        print("  nothing has approved (the `--no-verify` shape). Enumerate first:")
        print("      python3 scripts/gate_census.py --baselines")
        return 1

    if not quiet:
        print(
            "baseline-health: %d ratchet baseline(s), none absent "
            "(%d zero-tolerance, %d unread)." % (len(rows), len(zt), len(unr))
        )
    return 0


def _selftest():
    """⚑ THE THREE STATES MUST STAY DISTINGUISHABLE. This gate's entire value is that ABSENT
    and EMPTY look alike and mean opposite things; a change that collapsed them would make it
    either refuse the strong setting or pass a free pass."""
    sys.path.insert(
        0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch")
    )
    import rungs

    check = rungs.Cases(key="scripts/check_baseline_health.py")
    rows = gate_census.baseline_health()
    check("baseline health yields rows", len(rows) > 0, True)
    states = {r[2] for r in rows}
    check(
        "every state is one of the four known kinds",
        sorted(s for s in states if s not in ("ok", "EMPTY", "ABSENT", "UNREAD")),
        [],
    )
    # ⚑ EMPTY MUST NOT ENTER THE CENSUS. If it ever does, this gate would refuse the
    # zero-tolerance setting an operator deliberately chose — inverting its own purpose.
    check(
        "the census counts ABSENT only, never EMPTY",
        [k for k in census() if any(k == "%s::%s" % (r, b) for r, b in strong())],
        [],
    )
    check(
        "UNREAD is not counted as a violation",
        [k for k in census() if any(k == "%s::%s" % (r, b) for r, b in unread())],
        [],
    )
    return check.report()


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.exit(main())
