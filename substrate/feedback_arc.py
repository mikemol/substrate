# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The minimal edge set whose removal breaks a cycle — an SCC's feedback arc set.

⚑⚑⚑ THE SIZE OF A CYCLE IS NOT THE SIZE OF THE PROBLEM, AND READING IT AS SUCH IS THE
RECURRING MISREAD. A ten-member knot reads as ten files to untangle; in a strongly-connected
component ONE wrong-direction edge can absorb an entire DAG, so the actionable number is the
FEEDBACK ARC SET, not the membership. Measured on this repo's blocker graph: two knots, one of
ten files and one of four, and the question is which handful of edges to cut.

⚑⚑ THIS IS A REUSE, NOT A NEW SOLVER, AND A SEARCH FOUND IT. `scratch/agda_defs.cycle_cuts`
already implements exact-then-greedy feedback arc set with the non-obvious parts solved: exact
search by increasing k so the first result found IS the minimum, a greedy fallback LABELLED as
greedy (a heuristic reported as a minimum is a false figure), and greedy scoring by actual
residual-cycle shrinkage rather than a static degree proxy — its own comments record a degree
proxy returning forty-two cuts for a component whose real answer was two.

⚑ WHAT THIS ADDS IS THE GRAPH BEING AN ARGUMENT. The origin calls `import_index()` inside its
body, so the algorithm is generic while its INPUT is bound to the Agda tree. Everything below
takes `{node: [node]}` and never asks where it came from — which is what lets one solver answer
for Python imports, bare-name edges, or a def-level graph.

⚑⚑ AND THE METHOD IS REPORTED WITH THE ANSWER. `exact` and `greedy` are different claims: the
first is a minimum, the second an upper bound. A caller that could not tell them apart would
plan a two-edge repair against a number that might be twenty.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

# ⚑ ABOVE THIS EDGE COUNT THE EXACT SEARCH IS NOT AFFORDABLE. The bound is on EDGES inside one
# component, not on members: a four-member knot with dense edges can exceed it while a
# twenty-member chain does not.
EXACT_LIMIT = 40

# ⚑ AND THE EXACT SEARCH STOPS AT THIS CUT SIZE. A component needing more than six cuts is not
# one an operator repairs edge by edge; reporting a greedy bound is more honest than an
# exhaustive search nobody will wait for.
MAX_CUTS = 6

Edge = tuple[str, str]


@dataclass(frozen=True, slots=True)
class Cuts:
    """One component's feedback arc set, and how it was found."""

    members: tuple[str, ...]
    cuts: tuple[Edge, ...]
    method: str
    edges_considered: int

    @property
    def is_minimal(self) -> bool:
        """Whether `cuts` is a proven minimum rather than a greedy upper bound.

        ⚑ THE DISTINCTION IS LOAD-BEARING. `exact` says no smaller set exists; `greedy` says
        this one works. Planning a repair against the second as if it were the first is how a
        two-edge fix gets budgeted as twenty.
        """
        return self.method.startswith("exact")


def acyclic(nodes: list[str], edges: list[Edge]) -> bool:
    """Report whether `edges` over `nodes` form a DAG, by Kahn peeling."""
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    indeg: dict[str, int] = dict.fromkeys(nodes, 0)
    for a, b in edges:
        if a in adj and b in indeg:
            adj[a].append(b)
            indeg[b] += 1
    queue = [n for n in nodes if indeg[n] == 0]
    seen = 0
    while queue:
        node = queue.pop()
        seen += 1
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                queue.append(nxt)
    return seen == len(nodes)


def internal_edges(members: list[str], graph: dict[str, set[str]]) -> list[Edge]:
    """Return the edges of `graph` with both ends inside `members`.

    ⚑ ONLY INTERNAL EDGES CAN BREAK THE CYCLE. An edge leaving the component is already on a
    DAG path out of it, so cutting one would be work that changes nothing — and including
    them would inflate the search space that decides whether an exact answer is affordable.
    """
    inside = set(members)
    return [(m, d) for m in members for d in sorted(graph.get(m, set())) if d in inside]


def _exact(members: list[str], edges: list[Edge]) -> tuple[list[Edge], str] | None:
    """Search removal sets by increasing size; the first that works IS the minimum."""
    for size in range(1, min(len(edges), MAX_CUTS) + 1):
        for pick in itertools.combinations(edges, size):
            if acyclic(members, [e for e in edges if e not in pick]):
                return list(pick), "exact"
    return None


def still_cyclic(edges: list[Edge]) -> list[Edge]:
    """Return the edges still lying on some cycle, by peeling the acyclic part away.

    ⚑ THIS IS THE GREEDY SCORER'S INPUT, AND SCORING BY A STATIC PROXY IS WHAT IT REPLACES.
    The origin records a degree-based heuristic returning forty-two cuts where two sufficed;
    re-deriving which edges remain cyclic at each step measures instead of guessing.
    """
    keep = list(edges)
    changed = True
    while changed:
        changed = False
        live = {n for e in keep for n in e}
        sources = {a for a, _b in keep}
        sinks = {b for _a, b in keep}
        dead = (live - sources) | (live - sinks)
        if dead:
            before = len(keep)
            keep = [e for e in keep if e[0] not in dead and e[1] not in dead]
            changed = len(keep) != before
    return keep


def _greedy(members: list[str], edges: list[Edge]) -> tuple[list[Edge], str]:
    """Remove the edge that shrinks the cyclic residue most, until acyclic."""
    remaining = list(edges)
    cuts: list[Edge] = []
    while not acyclic(members, remaining):
        candidates = still_cyclic(remaining) or remaining
        scored = [(len(still_cyclic([x for x in remaining if x != e])), e) for e in candidates]
        best = min(scored)[1]
        remaining.remove(best)
        cuts.append(best)
    return cuts, "greedy"


def cuts_for(members: list[str], graph: dict[str, set[str]]) -> Cuts:
    """Return the feedback arc set for one component of `graph`.

    ⚑ EXACT WHERE AFFORDABLE, GREEDY WHERE NOT, AND THE METHOD IS NAMED EITHER WAY. A caller
    receiving a bare edge list cannot tell a proven minimum from an upper bound, and the two
    justify different plans.
    """
    ordered = sorted(members)
    edges = internal_edges(ordered, graph)
    if not edges or acyclic(ordered, edges):
        return Cuts(tuple(ordered), (), "acyclic", len(edges))
    found = _exact(ordered, edges) if len(edges) <= EXACT_LIMIT else None
    if found is None:
        found = _greedy(ordered, edges)
    return Cuts(tuple(ordered), tuple(found[0]), found[1], len(edges))


def render(found: Cuts) -> str:
    """Render one component's cuts, with the method that produced them."""
    note = "MINIMUM" if found.is_minimal else "upper bound (greedy)"
    head = (
        f"{len(found.members)} member(s), {found.edges_considered} internal edge(s) "
        f"-> {len(found.cuts)} cut(s)  [{found.method}, {note}]"
    )
    out = [head]
    out.extend(f"    cut  {a}  ->  {b}" for a, b in found.cuts)
    return "\n".join(out) + "\n"
