#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.chirality` — including the Ⓝ170 counterexample that bounds the theorem.

⚑⚑⚑ THE LOAD-BEARING PAIR IS `free_chaining_never_contradicts` AND `pinned_odd_cycle_contradicts`.
Together they are the whole content of ⟡paradox-freedom: a graph whose edges are FREE to take any
chirality is always satisfiable (the all-completer reading is a solution, always), while a graph
whose edges are PINNED by their kind can carry an odd cycle and be refuted. So *"no paradox is
constructible under klein-four chaining alone"* is TRUE for the free system and FALSE the moment a
pin enters — and the second arm is the constructive witness, not an argument.

⚑⚑ THE THREE-WAY VERDICT IS TESTED AS A RENDERING OBLIGATION, not just a return value. A reader that
computes three causes and prints two is the census-green failure with extra steps, so the arm reads
the rendered lines.

⚑ AND `solutions` IS NEVER 1. An arm pins that, because a reader reporting a unique assignment would
be claiming an absolute orientation the structure does not carry — the sigma flip is always free.
"""

from __future__ import annotations

import sys

from substrate import chirality

# A path: two completer edges in a row. Consistent, one component.
_PATH = (("rests-on", "a", "b"), ("rests-on", "b", "c"))

# ⚑⚑ THE COUNTEREXAMPLE. A triangle whose kind-bits sum to 1 around the cycle: two completers
# and one predictor. No perspective assignment satisfies all three, and it is minimal.
_ODD_TRIANGLE = (("rests-on", "a", "b"), ("rests-on", "b", "c"), ("from", "a", "c"))

# The same triangle with an even bit-sum — consistent, so the refutation above is about the PINS and
# not about triangles.
_EVEN_TRIANGLE = (("rests-on", "a", "b"), ("from", "b", "c"), ("from", "a", "c"))

# Two segments that never meet: consistent, but their relative chirality is undetermined.
_TWO_SEGMENTS = (("rests-on", "a", "b"), ("rests-on", "x", "y"))

# Every edge kind free to take chirality 0 — the unpinned system.
_FREE = {"rests-on": 0, "from": 0, "enables": 0}


def free_chaining_never_contradicts(out: list[str]) -> int:
    """Check the UNPINNED system is satisfiable even on the graph that refutes the pinned one."""
    got = chirality.solve(_ODD_TRIANGLE, table=_FREE)
    if got.verdict != chirality.CONSISTENT:
        out.append(f"selftest: free chaining refuted a graph, verdict {got.verdict}")
        return 1
    if got.conflicts:
        out.append(f"selftest: free chaining found {len(got.conflicts)} conflict(s)")
        return 1
    return 0


def pinned_odd_cycle_contradicts(out: list[str]) -> int:
    """Check an odd pinned cycle IS refuted — the constructive bound on ⟡paradox-freedom."""
    got = chirality.solve(_ODD_TRIANGLE)
    if got.verdict != chirality.INCONSISTENT:
        out.append(f"selftest: the odd triangle read as {got.verdict}")
        return 1
    if not got.conflicts:
        out.append("selftest: the odd triangle was refuted with no witness edge")
        return 1
    if got.solutions != 0:
        out.append(f"selftest: a refuted graph reports {got.solutions} solution(s)")
        return 1
    return 0


def an_even_cycle_is_consistent(out: list[str]) -> int:
    """Check the discriminator is the bit-sum, not the presence of a cycle."""
    got = chirality.solve(_EVEN_TRIANGLE)
    if got.verdict != chirality.CONSISTENT:
        out.append(f"selftest: the even triangle read as {got.verdict}")
        return 1
    return 0


def a_consistent_graph_is_never_unique(out: list[str]) -> int:
    """Check the global sigma flip is always reported as free — `solutions` is never 1."""
    got = chirality.solve(_PATH)
    if got.solutions != 2:  # noqa: PLR2004 - one component means exactly the two sigma readings
        out.append(f"selftest: a connected consistent graph reports {got.solutions} solution(s)")
        return 1
    if not got.unique_up_to_flip:
        out.append("selftest: a connected consistent graph was not unique up to the flip")
        return 1
    return 0


def disjoint_segments_are_underconstrained(out: list[str]) -> int:
    """Check two unlinked segments are a FINDING, not an error — four assignments, reported."""
    got = chirality.solve(_TWO_SEGMENTS)
    if got.verdict != chirality.CONSISTENT:
        out.append(f"selftest: disjoint segments read as {got.verdict}")
        return 1
    if got.components != 2:  # noqa: PLR2004 - the fixture declares exactly two segments
        out.append(f"selftest: disjoint segments gave {got.components} component(s)")
        return 1
    if got.solutions != 4:  # noqa: PLR2004 - two free bits
        out.append(f"selftest: two components report {got.solutions} solution(s)")
        return 1
    if not any("does not tie its segments" in line for line in chirality.render(got)):
        out.append("selftest: the underconstrained finding did not reach the report")
        return 1
    return 0


def all_three_causes_are_rendered(out: list[str]) -> int:
    """Check a refutation prints all three readings — the operator's three-way ruling."""
    lines = chirality.render(chirality.solve(_ODD_TRIANGLE))
    text = "\n".join(lines)
    missing = [cause for cause in chirality.AMBIGUOUS_CAUSES if cause not in text]
    if missing:
        out.append(f"selftest: {len(missing)} of 3 causes were not rendered")
        return 1
    return 0


def an_empty_read_is_not_consistency(out: list[str]) -> int:
    """Check reading no edges is UNREAD — the dangerous arm, distinct from a clean graph."""
    got = chirality.solve(())
    if got.verdict != chirality.UNREAD:
        out.append(f"selftest: an empty read reported {got.verdict}")
        return 1
    if got.code == chirality.CODES[chirality.CONSISTENT]:
        out.append("selftest: an empty read shares an exit code with a clean one")
        return 1
    return 0


def the_three_verdicts_have_three_codes(out: list[str]) -> int:
    """Check no two verdicts share an exit code."""
    if len(set(chirality.CODES.values())) != len(chirality.CODES):
        out.append("selftest: two verdicts share an exit code")
        return 1
    return 0


def the_denominator_is_reported(out: list[str]) -> int:
    """Check every summary carries its population — a count with no denominator is unreadable."""
    got = chirality.solve(_PATH, nodes=("a", "b", "c", "lonely"))
    if got.nodes_read != 4:  # noqa: PLR2004 - three walked plus the isolated entry
        out.append(f"selftest: the population is {got.nodes_read}, not 4")
        return 1
    if got.components != 1:
        out.append(f"selftest: an isolated node inflated components to {got.components}")
        return 1
    if "of" not in got.summary() and "over" not in got.summary():
        out.append("selftest: the summary carries no denominator")
        return 1
    return 0


def an_unknown_kind_is_confessed(out: list[str]) -> int:
    """Check a kind absent from the table is named as a possible reader defect, not defaulted."""
    got = chirality.solve((("supersedes", "a", "b"),))
    if got.unknown_kinds != ("supersedes",):
        out.append(f"selftest: the unknown kind reads as {got.unknown_kinds!r}")
        return 1
    if not any("may be the defect" in line for line in chirality.render(got)):
        out.append("selftest: the unknown-kind confession did not reach the report")
        return 1
    return 0


def the_missing_mate_is_derived(out: list[str]) -> int:
    """Check the closure names the tau-mate of a lone completer dart."""
    got = chirality.solve(_PATH)
    dart = chirality.derive(got, "a", [("rests-on", "b")])
    if dart != ("from", "b"):
        out.append(f"selftest: the derived dart is {dart!r}, not ('from', 'b')")
        return 1
    return 0


def a_declared_mate_is_not_re_derived(out: list[str]) -> int:
    """Check an entry that already carries a predictor dart gets nothing derived."""
    got = chirality.solve(_PATH)
    if chirality.derive(got, "a", [("rests-on", "b"), ("from", "b")]) is not None:
        out.append("selftest: a dart was derived over an existing mate")
        return 1
    return 0


def an_ambiguous_target_derives_nothing(out: list[str]) -> int:
    """Check the closure DECLINES rather than picking when the darts name two targets."""
    got = chirality.solve(_PATH)
    if chirality.derive(got, "a", [("rests-on", "b"), ("rests-on", "c")]) is not None:
        out.append("selftest: a direction was hand-picked across two targets")
        return 1
    return 0


def the_mate_map_is_an_involution(out: list[str]) -> int:
    """Check tau is its own inverse, and that mated kinds carry OPPOSITE chirality bits."""
    for kind, mate in chirality.TAU_MATE.items():
        if chirality.TAU_MATE.get(mate) != kind:
            out.append(f"selftest: tau({kind}) = {mate} but tau({mate}) does not return")
            return 1
        if chirality.KIND_CHIRALITY[kind] == chirality.KIND_CHIRALITY[mate]:
            out.append(f"selftest: {kind} and its mate {mate} share a chirality bit")
            return 1
    return 0


def a_declared_tau_pair_is_one_dart(out: list[str]) -> int:
    """Check a pair carrying BOTH chiralities of one relation is a completed closure, not a clash.

    ⚑⚑⚑ THE SOLVER AND THE CLOSURE DISAGREED, AND THE CLOSURE WAS RIGHT. `derive`'s docstring calls
    the tau-mate *"the same relation to the same target, read from the opposite chirality"* and
    returns None when it is already declared — nothing to construct, because the closure is
    COMPLETE. `_adjacency` read those same two edges as two independent constraints with opposite
    bits and refuted every one. **One dart declared twice is one constraint, not a contradiction.**

    ⚑⚑ OPERATOR, SETTLING WHAT THIS READER WAS ABOUT TO DECIDE WRONGLY: *"All chain edges are. The
    DAG is a lattice of darts."* The proposed repair — filtering document-chain `from` edges out of
    the parity graph — would have removed real darts from the lattice and called the result
    consistent. **A false green bought by deleting evidence**, and the inverse of the mistake it was
    meant to fix.

    ⚑ SO THE PARITY CONSTRAINT IS PER RELATION, NOT PER DECLARED EDGE, and the tau-mate spelling is
    a second NAME for one dart. The negative control is that a pair carrying two UNRELATED kinds
    must still constrain twice — collapsing everything on a shared pair would be the filter again.
    """
    tau_pair = (("rests-on", "u", "v"), ("from", "v", "u"))
    got = chirality.solve(tau_pair)
    if got.verdict != chirality.CONSISTENT:
        out.append(f"selftest: a declared tau-mate pair read as {got.verdict}, want CONSISTENT")
        return 1
    # ⚑ THE CONTROL: the SAME two kinds on the SAME orientation are NOT tau-mates of each other —
    # tau reverses the reading, not the endpoints — so this pair still carries two constraints.
    same_way = (("rests-on", "u", "v"), ("from", "u", "v"))
    if chirality.solve(same_way).verdict != chirality.INCONSISTENT:
        out.append("selftest: two same-oriented kinds collapsed — the reader is dropping darts")
        return 1
    return 0


def a_two_node_cycle_means_a_doubled_pair(out: list[str]) -> int:
    """Check a length-2 cycle can ONLY come from one pair carrying two kinds.

    ⚑⚑⚑ THE READING THIS PINS WAS ABOUT TO BE ACTED ON UNVERIFIED. The live bib reported four
    two-node cycles and I read them as *one pair, two contradictory kinds* — true of all four, and
    read off the output of a helper I had written the same turn. **A cycle reader that emitted a
    spurious 2-cycle whenever the closing edge joined a parent to its child would produce exactly
    that appearance**, and the corroboration would be four instances of my own artifact. The
    property has to come from a case, not from the population agreeing with me.

    ⚑⚑ THE CONTROL IS THE ORDINARY TREE EDGE, WHICH IS THE THING THAT COULD HAVE FAKED IT. A path
    graph colours cleanly and closes no cycle at all, so a parent-child pair NEVER reports one — if
    it did, every edge in every refuted component would read as a doubled pair.

    ⚑ AND THE POSITIVE ARM USES TWO KINDS ON ONE PAIR, which is the corpus shape: `from` and
    `rests-on` between the same two claims, bits 1 and 0, unsatisfiable by construction.
    """
    doubled = (("rests-on", "p", "q"), ("from", "p", "q"))
    got = chirality.solve(doubled)
    if not got.conflicts:
        out.append("selftest: a pair carrying two contradictory kinds was not refuted")
        return 1
    if set(got.conflicts[0].cycle) != {"p", "q"}:
        out.append(f"selftest: a doubled pair read cycle {sorted(got.conflicts[0].cycle)}")
        return 1
    # ⚑ THE CONTROL: an ordinary tree edge closes nothing, so no 2-cycle can arise from adjacency.
    if chirality.solve(_PATH).conflicts:
        out.append("selftest: a plain path reported a conflict — 2-cycles are an artifact")
        return 1
    return 0


def a_conflict_carries_its_odd_cycle(out: list[str]) -> int:
    """Check the refuting CYCLE is reported, not only the edge that closed it.

    ⚑⚑⚑ THE COUNT CANNOT PARTITION THE THREE-WAY VERDICT AND THE CYCLE CAN. Two repairs to this
    reader moved the conflict population in OPPOSITE directions — a de-duplication took it down, a
    correct sigma-normalisation took it UP — so the number measures traversal order as much as the
    corpus. `Conflict`'s docstring said so from the start: *"the edge reported is the one that
    CLOSED an odd cycle during the walk, which depends on traversal order, and every edge on that
    cycle is equally implicated."* **The implicated set is the invariant; which member surfaced is
    not.**

    ⚑⚑ AND THE PARTITION IS A PROPERTY OF THE MEMBERS, WHICH IS WHY THIS IS THE DISCRIMINATOR AND
    NOT A NICER REPORT. A sigma-shift is a cycle whose nodes span two authorship segments and is
    repaired by flipping one; a genuine inconsistency stays odd under every flip. Neither question
    can be ASKED of an integer.

    ⚑ THE CONTROL IS THAT THE CYCLE IS NOT THE COMPONENT. A tail hanging off the triangle is in the
    same component and must NOT appear — otherwise the "partition" is the component again, which is
    the count's failure restated as a set.
    """
    got = chirality.solve(_ODD_TRIANGLE)
    if not got.conflicts:
        out.append("selftest: the odd triangle was refuted with no conflict")
        return 1
    if set(got.conflicts[0].cycle) != {"a", "b", "c"}:
        out.append(f"selftest: the cycle read {sorted(got.conflicts[0].cycle)}, want a/b/c")
        return 1
    tailed = (*_ODD_TRIANGLE, ("rests-on", "c", "d"))
    with_tail = chirality.solve(tailed)
    if not with_tail.conflicts:
        out.append("selftest: the tailed triangle stopped being refuted")
        return 1
    if "d" in set(with_tail.conflicts[0].cycle):
        out.append("selftest: the reported cycle swept in a node that is not on it")
        return 1
    return 0


def a_sigma_mate_normalises_to_its_partner(out: list[str]) -> int:
    """Check `enables` is read as the ENDPOINT SWAP the module declares it to be.

    ⚑⚑⚑ THE MODULE ALREADY NAMED THIS AND THE WALK DID NOT HONOUR IT. `TAU_MATE`'s comment states
    that *"`from` is the TAU-mate of `rests-on` (same endpoints, other chirality) while `enables`
    is its SIGMA-mate (other endpoints)"* — so `u enables v` denotes the same relation as
    `v rests-on u`. `_adjacency` added it at `(u, v)` carrying chirality 1, which is the constraint
    for the UNSWAPPED pair. **The declaration and the reader disagreed, in the module that exists
    to stop chirality being decided by ear.**

    ⚑⚑ THE CASE IS AN AGREEMENT, NOT A REFUTATION, WHICH IS WHY IT IS THE RIGHT WITNESS. The bib
    declares BOTH `A5-as rests-on A5-as-reach` and `A5-as-reach enables A5-as`. Under sigma those
    are ONE constraint stated twice and must agree; under the old reading they contradicted, and
    the pair was reported as a conflict. A fixture reproduces it minimally: a graph whose only two
    edges are sigma-mates of each other is CONSISTENT.

    ⚑ AND THE CONTROL MATTERS AS MUCH AS THE CASE. A reader that simply dropped `enables` would
    also pass the agreement arm, so the second half asserts a sigma-mate still CONSTRAINS: flipping
    it against a declared `from` on the same pair must still refute.
    """
    agreeing = (("rests-on", "goal", "detail"), ("enables", "detail", "goal"))
    got = chirality.solve(agreeing)
    if got.verdict != chirality.CONSISTENT:
        out.append(f"selftest: a sigma-mate pair read as {got.verdict}, want CONSISTENT")
        return 1
    # ⚑ THE CONTROL: `from` is the TAU-mate (endpoints unchanged, bit 1), so against the same
    # `enables` it must still contradict. A dropped kind would pass the arm above and fail here.
    clashing = (("from", "goal", "detail"), ("enables", "detail", "goal"))
    if chirality.solve(clashing).verdict != chirality.INCONSISTENT:
        out.append("selftest: a sigma-mate stopped constraining — it is being dropped, not swapped")
        return 1
    return 0


def a_conflict_is_reported_once(out: list[str]) -> int:
    """Check one violated constraint reports ONE row, not one per endpoint.

    ⚑⚑⚑ THE COUNT WAS A FACT ABOUT THE TRAVERSAL, NOT ABOUT THE GRAPH. The walk stores each edge
    in BOTH directions — correct, because `phi(u) XOR phi(v) == k` is symmetric — and then recorded
    a conflict on every re-encounter of an already-coloured node. So a single unsatisfiable edge
    surfaced twice, once from each end, and the live worklist read `58 conflict(s) over 125 edge(s)`
    where the undirected population cannot exceed the edge count in that way.

    ⚑⚑ AND IT MADE THE THREE-WAY VERDICT UNUSABLE, which is the cost. A red whose MEMBERS are
    duplicated cannot be partitioned into genuinely-inconsistent, sigma-shifted and reader-defect —
    every count is inflated by an unknown factor, so no arm can be sized. **A false RED banks as
    confidently as a false green**, and this one was banked: `gate-F60` reasoned about the kind
    table from a number the reader had manufactured.

    ⚑ THE MINIMAL WITNESS IS THE ODD TRIANGLE: three edges, exactly one of which cannot be
    satisfied once the other two have coloured the graph. Asserting the PROPERTY (no undirected
    pair appears twice) rather than the literal 1 keeps the case alive if the fixture grows.
    """
    got = chirality.solve(_ODD_TRIANGLE)
    seen = [frozenset((c.source, c.target)) for c in got.conflicts]
    if len(seen) != len(set(seen)):
        out.append(f"selftest: a conflict was reported from both endpoints: {seen}")
        return 1
    if len(got.conflicts) != 1:
        out.append(f"selftest: the odd triangle reported {len(got.conflicts)} conflict(s), want 1")
        return 1
    return 0


def conflicts_never_outnumber_edges(out: list[str]) -> int:
    """Check the conflict count cannot exceed the edges read.

    ⚑ THE BOUND THE LIVE READ VIOLATED WITHOUT ANYONE NOTICING. A conflict is a property OF an
    edge, so the population is bounded by `edges_read` by construction — a report claiming more
    is arithmetically impossible and says the instrument is counting something else.

    ⚑⚑⚑ AND THIS DOCSTRING OVER-CLAIMED UNTIL AN ADVERSARIAL AUDIT READ IT. It said the arm was
    *"cheap, total, and it would have caught the double-count on the first real corpus"* — and it
    is NOT total (it loops over two fixtures) and it would NOT have caught `gate-F61`: on the odd
    triangle the double-counting code produced 2 conflicts over 3 edges, comfortably under the
    bound. **A case whose docstring claims a counterfactual it cannot support is the same class as
    a green census read as a clean tree**, committed in the suite written to catch that class.
    What the arm actually does is assert an arithmetic invariant on two fixtures. That is worth
    having and it is not a safety net.
    """
    for label, fixture in (("the odd triangle", _ODD_TRIANGLE), ("a path", _PATH)):
        got = chirality.solve(fixture)
        if len(got.conflicts) > got.edges_read:
            out.append(
                f"selftest: {label} reported {len(got.conflicts)} conflict(s) "
                f"over {got.edges_read} edge(s)"
            )
            return 1
    return 0


def a_refuted_graph_derives_nothing(out: list[str]) -> int:
    """Check no dart is derived from a graph whose assignment does not exist."""
    got = chirality.solve(_ODD_TRIANGLE)
    if chirality.derive(got, "a", [("rests-on", "b")]) is not None:
        out.append("selftest: a dart was derived from a refuted graph")
        return 1
    return 0


_ARMS = (
    free_chaining_never_contradicts,
    pinned_odd_cycle_contradicts,
    an_even_cycle_is_consistent,
    a_consistent_graph_is_never_unique,
    disjoint_segments_are_underconstrained,
    all_three_causes_are_rendered,
    an_empty_read_is_not_consistency,
    the_three_verdicts_have_three_codes,
    the_denominator_is_reported,
    an_unknown_kind_is_confessed,
    the_missing_mate_is_derived,
    a_declared_mate_is_not_re_derived,
    an_ambiguous_target_derives_nothing,
    the_mate_map_is_an_involution,
    a_declared_tau_pair_is_one_dart,
    a_two_node_cycle_means_a_doubled_pair,
    a_conflict_carries_its_odd_cycle,
    a_sigma_mate_normalises_to_its_partner,
    a_conflict_is_reported_once,
    conflicts_never_outnumber_edges,
    a_refuted_graph_derives_nothing,
)

_CASE_COUNT = 2 + 3 + 1 + 2 + 4 + 1 + 2 + 1 + 3 + 2 + 1 + 1 + 1 + 2 + 2 + 3 + 4 + 2 + 2 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"chirality selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"chirality selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
