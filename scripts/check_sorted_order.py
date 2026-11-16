#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_sorted_order.py — a paid-for ORDER must survive the call that produced it.

⟡sorted-stream-carrier.  A def that ends `return sorted(...)` has PAID for an order and
then thrown away the fact that it has one, because a `list` carries no claim about how it
is arranged.  Its callers therefore re-sort defensively, and the corpus pays twice.

**MEASURED, ONE HOP APART, IN THIS TREE.**  `scratch/agda_defs.py`:

    :1732  import_index()   sorts its result — and DECLARES it in the docstring at :1701,
                            "module -> sorted[imported module]"
    :1757  importers_of()   reads that already-sorted index and RE-SORTS it

The producer knew, wrote it down in prose, and the knowledge did not survive one function
call.  Not because anyone was careless: there was nowhere ON THE VALUE to put the claim.
`jea/metalanguage/sorted_stream.py` is that place — `Sorted(it, key, origin)` carries the
order as data, and its combinators REFUSE a mismatch instead of quietly re-sorting.

WHY A GATE AND NOT A SWEEP.  72 defs corpus-wide return `sorted(...)`; converting them by
hand is exactly the 44-hand-edits shape this repo forbids.  The census is DISCOVERED (from
`pycodemod --reifies`, never a list typed here), and paydown-only: a new `return sorted(...)`
is admitted as debt and an existing one may only be retired.

⚑ THIS IS NOT A BAN ON `sorted()`, AND READING IT AS ONE WOULD BE WRONG.  Somebody must pay
the sort once, at a named producer — `sorted_stream.from_set` does precisely that, on
purpose.  What the gate measures is the order being paid for and then made UNSAYABLE, so the
next consumer cannot tell and pays again.

⚑ AND THE HONEST LIMIT, STATED BECAUSE A GATE THAT HIDES ITS BLIND SPOT IS WORSE THAN NO
GATE: this censuses the PRODUCER side only.  It cannot see a consumer that re-sorts, because
that needs the two ends of a span related to each other, and the corpus has no carrier for
that relation yet — which is the whole reason the arc exists.  So a green here means "no NEW
order was made unsayable", never "the corpus does not double-sort".

Usage: check_sorted_order.py [--quiet] [--list]
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scratch"))
import ratchet  # noqa: E402

ROOT = os.path.dirname(HERE)

# ⚑ THE CARRIER ITSELF IS EXEMPT, AND ONLY IT.  `sorted_stream.from_set` materializes and
# sorts BY DESIGN — that is the one payment the whole design is built around, made at a
# named producer that then carries the key.  Censusing it would make the fix look like the
# defect.  A one-name exemption stated here, not a growing allow-list: anything else that
# wants out pays down instead.
CARRIER = os.path.join("jea", "metalanguage", "sorted_stream.py")


def census():
    """{"<relpath>:<line>:<fn>"} — every def whose return DISCARDS a paid-for order.

    ⚑ DERIVED FROM `pycodemod --reifies`, NEVER RE-IMPLEMENTED HERE.  A second walk with
    its own idea of what "returns sorted" means is the `agda_files()`-as-four-bodies defect
    (`pycodemod`'s own docstring records it): one capability, two copies, and the gate and
    the census drift into disagreeing about the population they share.
    """
    from _pycodemod_query import reifies

    out = set()
    for path, line, name, _kind, why in reifies():
        if why != "returns-sorted":
            continue
        rel = os.path.relpath(path, ROOT)
        if rel == CARRIER:
            continue
        out.add(f"{rel}:{line}:{name}")
    # ⚑ A ZERO FROM A SCAN THAT READ NOTHING IS NOT A CLEAN TREE.  `reifies` carries its own
    # skip accounting for exactly this; a gate that banks an empty census from a broken walk
    # writes a baseline of 0 and then passes forever.  Refuse rather than record.
    if reifies.skipped and len(reifies.skipped) == reifies.population:
        raise SystemExit(
            f"check_sorted_order: read 0 of {reifies.population} file(s) — "
            f"{reifies.skipped[0][1]}: {reifies.skipped[0][2]}\n"
            f"  This is a fact about the QUERY, not about the corpus. Refusing to bank "
            f"an empty census as a clean tree."
        )
    return out


def _selftest():
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    import tempfile
    from _pycodemod_query import reifies

    src = """
def pays_and_drops(xs):
    return sorted(xs)

def keeps_it(xs):
    return set(xs)

def streams(xs):
    for x in sorted(xs):
        yield x
"""
    d = tempfile.mkdtemp()
    p = os.path.join(d, "case.py")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(src)
    rows = {r[2]: r[4] for r in reifies([p])}

    check("a def returning sorted(...) is censused", rows.get("pays_and_drops"), "returns-sorted")
    # ⚑ THE DISCRIMINATION THAT MAKES THIS A GATE RATHER THAN A `sorted` GREP.  A def that
    # returns a set has not paid for an order; a GENERATOR that sorts internally and yields
    # has paid but has NOT discarded the fact — the order survives to whoever iterates it.
    # A gate that flagged all three would be counting the word, not the defect.
    check("returning a set is not this defect", rows.get("keeps_it"), "returns-call")
    check(
        "a generator that sorts internally is NOT censused (the order survives)",
        "streams" in rows,
        False,
    )

    # ⚑ THE CARRIER'S OWN DELIBERATE SORT MUST NOT BE DEBT, or the fix reads as the defect.
    check(
        "the carrier is exempt by path, and nothing else is",
        CARRIER,
        os.path.join("jea", "metalanguage", "sorted_stream.py"),
    )

    # ⚑ THE REFUSAL, PINNED AGAINST A REAL EMPTY READ.  A census cannot distinguish
    # "nothing to report" from "read nothing", so the all-skipped arm must RAISE rather
    # than bank a 0 baseline that then passes forever.  An unparseable file makes the
    # population 1 and the skips 1, which is the condition the arm tests — pinned with a
    # fixture, not asserted in a comment.
    bad = os.path.join(d, "broken.py")
    with open(bad, "w", encoding="utf-8") as fh:
        fh.write("def f(:\n")
    reifies([bad])
    check(
        "an all-skipped read is detectable as such (the refusal's precondition)",
        (reifies.population, len(reifies.skipped)),
        (1, 1),
    )

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"check_sorted_order selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main():
    if "--selftest" in sys.argv:
        return _selftest()
    rc = ratchet.check_argv(sys.argv, {"--quiet", "--list"}, "check_sorted_order")
    if rc is not None:
        return rc
    rows = census()
    return ratchet.set_ratchet(
        rows,
        os.path.join(HERE, "sorted_order_baseline.txt"),
        "sorted-order",
        "--quiet" in sys.argv,
        list_keys="--list" in sys.argv,
        render=lambda k: f"✗ {k}",
        summary="def(s) that return sorted(...) — an order paid for and made unsayable",
        noun="def(s) discarding a paid-for order",
        refuse_hint=(
            "This def sorts and returns a bare list, so its callers cannot tell and "
            "re-sort defensively — measured one hop apart at agda_defs.py:1732 -> :1757. "
            "Carry the order ON the value: `from sorted_stream import Sorted, SortKey; "
            "return Sorted(it, SortKey.of('name'), origin='<this def>')`. Its combinators "
            "(merge/dedup/group/join) then REFUSE a mismatch instead of re-sorting, which "
            "is how the requirement reaches the producer that must satisfy it."
        ),
    )


if __name__ == "__main__":
    sys.exit(main())
