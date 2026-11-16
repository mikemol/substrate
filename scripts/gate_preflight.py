#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Classify a set-ratchet gate's ADDED keys into CHURN vs GENUINELY-NEW, and emit a
paydown work queue.

WHY.  A decomposition (`X.agda` → `X/X.agda`) is CONTENT-preserving but KEY-changing:
the old census key retires and a new one is minted for a byte-identical line.  The
ratchet sees only "a key appeared" and refuses.  Worse — `ratchet.set_ratchet` returns
on `added` BEFORE reaching its paydown branch, so the churn does not merely add noise,
it BLOCKS real paydown from ever recording.  Measured on the live tree at the time this
was written: public-ratchet baseline 552, current 545 (debt DOWN 7), 14 keys paid, and
the gate reported only "7 NEW" and refused.

WHAT THIS IS NOT.  It NEVER rewrites a baseline.  Remapping keys into the baseline
would launder the debt, which is the entire point of a paydown-only ratchet.  Baselines
are read with `ratchet._read` (a pure set read); `ratchet.set_ratchet` is never called
from here — it writes on baseline-missing and on paydown.

THE CLASSIFICATION.  Keys are compared by IDENTITY — every field except the path (see
`gate_keys`), the part a file move preserves:

  CHURN          identity also appears in `paid`  ⇒ the path moved, the line did not.
                 Reported WITH its old→new pairing.  This is NOT absolution: it is
                 shown so a reviewer can confirm the pairing is real.
  GENUINELY-NEW  identity absent from `paid`      ⇒ real debt.  Head of the queue.

THE LOOP.  Report → the queue's head is genuinely-new debt → pay it down → re-run.
Each fix can reveal debt the previous state masked, so the pre-flight is re-run until
the queue is empty, not read once.

⚑ HONEST LIMITATION.  If a name MOVES and a genuinely-new violation of the SAME identity
appears elsewhere in the same run, both classify as churn.  Mitigation: churn is never
auto-absolved, and a 1→2 fan-out shows as a count asymmetry in the pairing (one old path,
two new).  `--strict` reports any such asymmetry as suspect rather than churn.
"""

import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import gate_keys  # noqa: E402
import ratchet  # noqa: E402
from gate_keys import SCHEMA  # noqa: E402


def live_census(gate):
    """The gate's CURRENT census, via its own census function — never re-implemented.

    A second implementation of a gate's predicate is precisely the drift this tool
    exists to prevent, so each gate's own code is the authority.
    """
    if gate == "public":
        from check_public_ratchet import census

        return set(census())
    if gate == "sumtype":
        from check_sumtype_ratchet import census

        return set(census())
    if gate == "ban":
        from check_ban_ratchet import census

        return set(census())
    if gate == "claims":
        from check_claims import census

        return set(census())  # census() returns a dict; its KEYS are the census
    if gate == "carrier-locality":
        # No census() exists: the gate's census is its LIVE-EXEMPTION set, computed by
        # scan/judge (carved out of main() for exactly this reuse).
        from check_carrier_locality import scan, judge

        carrier_decls, opsigs = scan()
        return set(judge(carrier_decls, opsigs)[4])
    raise KeyError(gate)


Verdict = collections.namedtuple(
    "Verdict", "gate base cur added paid churn genuinely_new suspect real_paydown"
)


def moved_from(old_path, new_path):
    """Is `new_path` a plausible destination for `old_path` under a decomposition?

    ⚑ IDENTITY ALONE IS NOT ENOUGH, and assuming it was is a false-absolution bug this
    tool hit on its first live run: `ClosureCapstone.agda::Substrate.Foundation.Eq::using`
    was called churn because SOME unrelated file importing `Foundation.Eq` had moved.
    A common identity (`Foundation.Eq::using` appears in hundreds of files) would launder
    every new violation that shares it — exactly what must never happen.

    The decomposition shapes this tool exists for are path-LOCAL:
        X.agda        -> X/Leaf.agda      (a monolith split into its own directory)
        Dir/X.agda    -> Dir/Y.agda       (a leaf renamed within its directory)
    Both keep the old file's directory as a prefix of the new one, or share a parent.
    Anything else is not a move we can evidence, so it is not churn.
    """
    if old_path == new_path:
        return False
    old_stem = old_path[:-5] if old_path.endswith(".agda") else old_path
    # X.agda -> X/anything.agda : the monolith-to-directory split.
    if new_path.startswith(old_stem + os.sep):
        return True
    # Same directory, different file: a rename in place.
    return os.path.dirname(old_path) == os.path.dirname(new_path)


def classify(gate, base, cur, strict=False):
    """Partition `cur - base` into churn and genuinely-new. Pure; no I/O."""
    added, paid = cur - base, base - cur
    paid_by_ident = collections.defaultdict(list)
    for k in paid:
        try:
            paid_by_ident[gate_keys.identity(gate, k)].append(gate_keys.path_of(gate, k))
        except gate_keys.MalformedKey:
            continue  # a malformed baseline key cannot pair anything

    churn, genuinely_new, suspect = {}, [], {}
    consumed = set()  # paid keys accounted for by a churn pairing

    for k in sorted(added):
        try:
            new_path, ident = gate_keys.parse(gate, k)
        except gate_keys.MalformedKey:
            genuinely_new.append(k)  # unparseable ⇒ never silently absolved
            continue
        # Pair ONLY with an old path this key could actually have moved from.
        old_paths = [p for p in paid_by_ident.get(ident, ()) if moved_from(p, new_path)]
        if not old_paths:
            genuinely_new.append(k)
            continue
        # A 1-old → N-new fan-out means at most one of the N is the move; the rest are
        # new violations wearing a moved name.  Under --strict that is suspect, not churn.
        rival = sum(
            1
            for a in added
            if a != k
            and _same_ident(gate, a, ident)
            and any(moved_from(p, gate_keys.path_of(gate, a)) for p in old_paths)
        )
        if strict and rival >= len(old_paths):
            suspect[k] = old_paths
        else:
            churn[k] = old_paths
            for p in old_paths:
                consumed.add(gate_keys.rekey(gate, k, p))
    return Verdict(gate, base, cur, added, paid, churn, genuinely_new, suspect, paid - consumed)


def _same_ident(gate, key, ident):
    try:
        return gate_keys.identity(gate, key) == ident
    except gate_keys.MalformedKey:
        return False


def report(v, quiet=False):
    """Print the verdict + work queue. Returns the queue length."""
    spec = SCHEMA[v.gate]
    net = len(v.cur) - len(v.base)
    arrow = "DOWN" if net < 0 else ("UP" if net > 0 else "level")
    print(
        f"\n=== {v.gate}: baseline {len(v.base)} → current {len(v.cur)} "
        f"({arrow} {abs(net)})   added {len(v.added)}  paid {len(v.paid)}"
    )

    if v.genuinely_new:
        print(
            f"  ⚑ GENUINELY NEW — {len(v.genuinely_new)} {spec.noun} (QUEUE HEAD, pay these down):"
        )
        for k in v.genuinely_new:
            print(f"      + {k}")
    if v.suspect:
        print(
            f"  ⚠ SUSPECT — {len(v.suspect)} added key(s) share an identity with a moved "
            f"key but outnumber it (a move cannot account for all):"
        )
        for k, olds in sorted(v.suspect.items()):
            print(f"      ? {k}\n          moved-from: {', '.join(olds)}")
    if v.churn and not quiet:
        shown = sorted(v.churn.items())
        cap = 10
        print(
            f"  CHURN — {len(v.churn)} key(s): path moved, line did not "
            f"(shown for confirmation, NOT absolved):"
        )
        for k, olds in shown[:cap]:
            print(
                f"      ~ {k}\n          was: {', '.join(olds[:3])}"
                f"{f' (+{len(olds) - 3} more candidates)' if len(olds) > 3 else ''}"
            )
        if len(shown) > cap:
            # No silent truncation: say what was dropped and how to see it.
            print(
                f"      … {len(shown) - cap} more churn key(s) not shown "
                f"(re-run with --all to list them)."
            )

    if v.added and v.real_paydown:
        print(
            f"  BLOCKED PAYDOWN: {len(v.real_paydown)} genuine paydown(s) cannot record "
            f"while ADDED is non-empty (ratchet.py returns on `added` before the "
            f"paydown branch)."
        )

    queue = len(v.genuinely_new) + len(v.suspect)
    if queue == 0:
        if v.added:
            print(
                "  → every added key is accounted for as churn; the queue is EMPTY for "
                "this gate. The remaining refusal is key-churn, not new debt."
            )
        else:
            print("  → clean: nothing added.")
    return queue


def main():
    argv = sys.argv[1:]
    quiet = "--quiet" in argv
    strict = "--strict" in argv
    gates = []
    if "--gate" in argv:
        gates = [argv[argv.index("--gate") + 1]]
    else:
        gates = [g for g in SCHEMA if os.path.exists(SCHEMA[g].baseline)]

    total_queue = 0
    for gate in gates:
        spec = SCHEMA[gate]
        if not os.path.exists(spec.baseline):
            print(
                f"\n=== {gate}: no baseline at {spec.baseline} — skipped "
                f"(a first run would RECORD one; that is set_ratchet's job, not ours)."
            )
            continue
        base = ratchet._read(spec.baseline)  # pure read; never _write
        cur = live_census(gate)
        total_queue += report(classify(gate, base, cur, strict), quiet)

    print(f"\nWORK QUEUE: {total_queue} item(s) of genuinely-new debt across {len(gates)} gate(s).")
    if total_queue:
        print(
            "Pay down the queue head, then RE-RUN — a fix can reveal debt the "
            "previous state masked."
        )
    return 1 if total_queue else 0


def _selftest():
    """Counted — a hardcoded total once hid an added case (prune_imports.py:332)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    P = "public"
    # The five real churn pairs measured on the live tree (X.agda -> X/X.agda).
    base = {
        "agda/Substrate/Algebra/F2/Linear.agda::Linear",
        "agda/Substrate/Algebra/Q.agda::ℚ",
        "agda/Substrate/Algebra/Quotient.agda::Quotient",
        "agda/Substrate/Algebra/Quotient.agda::Canonical",
        "agda/Substrate/Category/CategoryOf.agda::CategoryOf",
    }
    cur = {
        "agda/Substrate/Algebra/F2/Linear/Linear.agda::Linear",
        "agda/Substrate/Algebra/Q/Rat.agda::ℚ",
        "agda/Substrate/Algebra/Quotient/Quotient.agda::Quotient",
        "agda/Substrate/Algebra/Quotient/Canonical.agda::Canonical",
        "agda/Substrate/Category/CategoryOf/CategoryOf.agda::CategoryOf",
    }
    v = classify(P, base, cur)
    check("5 real moves all classify as churn", len(v.churn), 5)
    check("...and none as genuinely-new", v.genuinely_new, [])

    # The two real genuinely-new keys: identities absent from the baseline entirely.
    v2 = classify(
        P,
        base,
        cur
        | {
            "agda/Substrate/Algebra/Wedge/Graded/DivStr.agda::GradedDivStr",
            "agda/Substrate/Algebra/Wedge/Graded/Wedge.agda::GradedWedge",
        },
    )
    check(
        "GradedDivStr/GradedWedge are genuinely-new, not churn",
        sorted(gate_keys.identity(P, k)[0] for k in v2.genuinely_new),
        ["GradedDivStr", "GradedWedge"],
    )
    check("...and the 5 churn are still churn alongside them", len(v2.churn), 5)

    # Reversed schema: sumtype is name::path, so a move must still pair.
    v3 = classify("sumtype", {"Crumb::agda/Substrate/Old.agda"}, {"Crumb::agda/Substrate/New.agda"})
    check("reversed sumtype key: a move is churn", len(v3.churn), 1)
    check("reversed sumtype key: nothing genuinely-new", v3.genuinely_new, [])
    v4 = classify(
        "sumtype",
        {"Crumb::agda/Substrate/Old.agda"},
        {"Crumb::agda/Substrate/Old.agda", "Widget::agda/Substrate/New.agda"},
    )
    check(
        "reversed schema still catches a NEW name",
        v4.genuinely_new,
        ["Widget::agda/Substrate/New.agda"],
    )

    # Adversarial: a move PLUS a new violation of the same identity.
    adv_b, adv_c = {"old.agda::X"}, {"new.agda::X", "evil.agda::X"}
    v5 = classify(P, adv_b, adv_c)
    check(
        "known limitation: same-identity fan-out reads as churn (documented)",
        (len(v5.churn), v5.genuinely_new),
        (2, []),
    )
    v6 = classify(P, adv_b, adv_c, strict=True)
    check(
        "--strict flags the fan-out as SUSPECT instead of absolving it",
        (len(v6.suspect), len(v6.churn)),
        (2, 0),
    )

    # Paydown with nothing added must produce an empty queue.
    v7 = classify(P, {"a.agda::X", "b.agda::Y"}, {"a.agda::X"})
    check("pure paydown: empty queue", (v7.genuinely_new, len(v7.churn)), ([], 0))
    check("pure paydown: 1 key paid", len(v7.paid), 1)

    # Genuinely-new with no moves at all.
    v8 = classify(P, {"a.agda::X"}, {"a.agda::X", "b.agda::Y"})
    check("new debt with no moves is never churn", v8.genuinely_new, ["b.agda::Y"])

    # An unparseable key must never be silently absolved.
    v9 = classify(P, set(), {"no-separator"})
    check("malformed added key is queued, not absolved", v9.genuinely_new, ["no-separator"])

    # ⚑ MEASURED REGRESSION (first live run): a COMMON identity must not launder a new
    # violation in an unrelated file.  `ClosureCapstone.agda::Substrate.Foundation.Eq::using`
    # was called churn merely because some OTHER file importing Foundation.Eq had moved.
    # Foundation.Eq carries 1632 ban keys (10.5% of all ban debt), so identity alone
    # absolves at enormous scale.  The path-plausibility test (`moved_from`) is what
    # stops it, and this case pins that.
    B = "ban"
    v10 = classify(
        B,
        {"agda/Substrate/Algebra/Z.agda::Substrate.Foundation.Eq::using"},
        {"agda/Substrate/Linguistic/ClosureCapstone.agda::Substrate.Foundation.Eq::using"},
    )
    check(
        "common identity does NOT absolve an unrelated file's new violation",
        (len(v10.churn), len(v10.genuinely_new)),
        (0, 1),
    )
    # ...while a REAL split of that same module still pairs.
    v11 = classify(
        B,
        {"agda/Substrate/Algebra/Z.agda::Substrate.Foundation.Eq::using"},
        {"agda/Substrate/Algebra/Z/Int.agda::Substrate.Foundation.Eq::using"},
    )
    check(
        "a real X.agda -> X/Leaf.agda split still pairs as churn",
        (len(v11.churn), v11.genuinely_new),
        (1, []),
    )
    check("moved_from: monolith split", moved_from("a/X.agda", "a/X/Leaf.agda"), True)
    check("moved_from: same-dir rename", moved_from("a/X.agda", "a/Y.agda"), True)
    check("moved_from: unrelated file", moved_from("a/X.agda", "b/Z.agda"), False)
    check("moved_from: identity is not a move", moved_from("a/X.agda", "a/X.agda"), False)

    ok = sum(1 for _, good, _, _ in cases if good)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"gate_preflight selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv else main())
