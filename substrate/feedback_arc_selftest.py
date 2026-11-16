# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.feedback_arc` — which edges to cut to break a cycle.

⚑⚑⚑ THE METHOD LABEL IS AS LOAD-BEARING AS THE ANSWER, so it is asserted alongside every
result. `exact` claims no smaller set exists; `greedy` claims only that this one works. A
caller shown a bare edge list plans a two-edge repair against a number that might be twenty,
and the origin this reuses records exactly that misread — a degree heuristic returning
forty-two cuts for a component whose real answer was two.

⚑⚑ AND MINIMALITY IS ASSERTED BY SIZE, NOT BY IDENTITY. Several distinct minimum cut sets can
exist for one component, so a case naming WHICH edge came back would be pinning an arbitrary
choice among equals and would fail on a tie-break change that broke nothing.

⚑ THE ACYCLIC CASE IS NOT A FORMALITY. A solver that returned a cut for a DAG would send an
operator to sever a working edge, and the failure is silent — the graph stays acyclic either
way, so nothing downstream notices.
"""

from __future__ import annotations

from substrate import feedback_arc

# A two-node mutual cycle: one edge is enough.
_PAIR: dict[str, set[str]] = {"a": {"b"}, "b": {"a"}}

# A three-node ring: still one edge.
_RING: dict[str, set[str]] = {"a": {"b"}, "b": {"c"}, "c": {"a"}}

# Two independent rings sharing no edge: needs one cut each.
_TWO_RINGS: dict[str, set[str]] = {
    "a": {"b"},
    "b": {"a"},
    "c": {"d"},
    "d": {"c"},
}

# A DAG — nothing to cut.
_CHAIN: dict[str, set[str]] = {"a": {"b"}, "b": {"c"}, "c": set()}


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the minimum is found, and named as a minimum ────────────────────────
    pair = feedback_arc.cuts_for(["a", "b"], _PAIR)
    check("a mutual pair needs one cut", passed=len(pair.cuts) == 1)
    check("and the answer is labelled exact", passed=pair.is_minimal)
    # ⚑ THE CUT MUST ACTUALLY WORK — a minimum that leaves a cycle is worse than none.
    check(
        "cutting it leaves the component acyclic",
        passed=feedback_arc.acyclic(
            ["a", "b"],
            [e for e in feedback_arc.internal_edges(["a", "b"], _PAIR) if e not in pair.cuts],
        ),
    )

    ring = feedback_arc.cuts_for(["a", "b", "c"], _RING)
    # ⚑ SIZE, NOT IDENTITY. Any one of the three edges breaks the ring, so naming one
    # would pin an arbitrary choice among equals.
    check("a three-node ring also needs only one cut", passed=len(ring.cuts) == 1)
    check(
        "and its cut breaks the ring",
        passed=feedback_arc.acyclic(
            ["a", "b", "c"],
            [e for e in feedback_arc.internal_edges(["a", "b", "c"], _RING) if e not in ring.cuts],
        ),
    )

    # ── two independent cycles need two cuts ────────────────────────────────
    # ⚑ ONE CUT CANNOT BREAK TWO DISJOINT RINGS, and a solver that returned one would be
    # reporting a set that does not do what it claims.
    both = feedback_arc.cuts_for(["a", "b", "c", "d"], _TWO_RINGS)
    check("two disjoint rings need two cuts", passed=len(both.cuts) == 2)  # noqa: PLR2004

    # ── a DAG yields no cuts ────────────────────────────────────────────────
    # ⚑ A CUT FOR AN ACYCLIC GRAPH SENDS AN OPERATOR TO SEVER A WORKING EDGE, and nothing
    # downstream would notice, because the graph stays acyclic either way.
    chain = feedback_arc.cuts_for(["a", "b", "c"], _CHAIN)
    check("a DAG needs no cuts", passed=chain.cuts == ())
    check("and is labelled acyclic rather than exact", passed=chain.method == "acyclic")
    # ⚑ AND `is_minimal` MUST NOT CLAIM MINIMALITY FOR A NON-SEARCH.
    check("an acyclic verdict is not a minimality claim", passed=not chain.is_minimal)

    # ── only internal edges are considered ──────────────────────────────────
    # ⚑ AN EDGE LEAVING THE COMPONENT IS ALREADY ON A DAG PATH OUT, so cutting it changes
    # nothing — and counting it would inflate the search space that decides affordability.
    with_exit: dict[str, set[str]] = {"a": {"b", "outside"}, "b": {"a"}}
    edges = feedback_arc.internal_edges(["a", "b"], with_exit)
    check("an edge leaving the component is excluded", passed=("a", "outside") not in edges)
    check("while the internal ones are kept", passed=len(edges) == 2)  # noqa: PLR2004

    # ── the cyclic residue peels correctly ──────────────────────────────────
    # ⚑ THIS IS THE GREEDY SCORER'S INPUT. A tail hanging off a ring is not on a cycle,
    # and scoring it as if it were is what a static degree proxy does.
    residue = feedback_arc.still_cyclic([("a", "b"), ("b", "a"), ("b", "tail")])
    check(
        "a dangling tail is peeled out of the cyclic residue", passed=("b", "tail") not in residue
    )
    check("and the ring itself survives the peel", passed=len(residue) == 2)  # noqa: PLR2004

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
