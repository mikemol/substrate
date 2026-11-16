#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""THE cone authority: reachability, and the part a set blocks EXCLUSIVELY.

⚑⚑ WHY THIS EXISTS — TWO `leverage` DEFINITIONS UNDER ONE NAME. One answered it over the Agda
import DAG; another over the warrant graph. Neither was a copy of the other and both were
correct, which is exactly the shape that hides: **a shared NAME is not a shared authority**, and
the same relation with two implementations grows two answers.

⚑⚑⚑ AND THE DEFECT THEY SHARED IS WHY IT HAD TO BE LIFTED, NOT MERELY DEDUPED. Both called their
result *"what clearing this would free"*. A cone is REACHABILITY: every node transitively
depending on the seeds. A node in it can sit behind several blocking sets at once, so clearing
one frees only the nodes whose remaining blockers are all inside it.

MEASURED on three ban-directive buckets: cones of 538 / 417 / 298, exclusive 205 / 97 / 82 —
**60-75% shared, so the naive reading was wrong by ~4x**, and the figures never summed
(538+417+298 over a ~3400-module tree is one subtree counted three times). Fixing that in one
consumer and leaving the other is how a correction becomes a divergence.

⚑⚑ `rests-on` AND `enables` ARE NOT TWO EDGE KINDS — THEY ARE ONE ARROW READ FROM BOTH ENDS. A
graph and its reverse. Both spellings are stored so an entry can state its own relations without
editing its neighbours; that is an AUTHORING convenience, not two relations. The substantive half
is which FOLD each reading wants:

    GROUNDING is many-to-one — an item rests on several premises and needs them all, a
    conjunction, so LAYERING follows this direction;
    SEQUENCING is one-to-many — clearing this makes several things cheaper, a fan-out, so
    WEIGHT follows this one.

Same arrows, different question. Two functions over one graph, not two graphs.

⚑ THE GRAPH IS SUPPLIED, NEVER DISCOVERED HERE. Callers own their edges — the import DAG from the
build generator, the warrant graph from the bib — and this module owns only the walk. Inventing
an edge source here would make it a second authority for whatever it guessed at.

⚑⚑ AND THE WALK ITSELF IS `networkx`. A first cut hand-wrote the BFS — which is exactly
`nx.descendants`, already in the environment. The reuse-search should have fired on the words
"reachability closure" before a line was written. What is NOT networkx, and is why this module
exists: **the exclusivity subtraction and the refusal to call a cone a liberation.**

⚑ PROMOTED FROM `scratch/` (⟡items-n-split): a witness in a promoted tree may not depend on
`scratch/` at runtime, and the sanctioned resolution is promotion rather than repathing. The
fallback BFS the scratch version carried is GONE — it existed so a bare environment degraded to
a slower answer, and a promoted module has a declared dependency instead of a hedge.

⚑⚑⚑ THE GRAPH NEVER ESCAPES THIS MODULE, and that is what made a STUB the right answer rather
than a typing waiver (operator: *"this is what type stubs are for"*). Every public function
returns a `set`, `list` or `dict` over the CALLER's own node type, so the library's shape is an
implementation detail. `types-networkx` was installed first and removed: its `DiGraph` is generic
over ATTRIBUTE DICTS, so every graph expression became `Any` under `disallow_any_expr` — the
repo's rule reads *stub an untyped dep (that ADDS types); ignore a typed dep whose types contain
`Any` at a boundary walled by a concrete return*, and node attributes are not a walled boundary,
they are the interface. `stubs/networkx/` declares the four names this repo calls, generic over
the node type alone.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import networkx as nx

if TYPE_CHECKING:
    from collections.abc import Iterable


class Successors[T](Protocol):
    """The caller's edge relation: importers for an import DAG, dependents for a claim graph.

    ⚑ A CALLABLE, NOT A GRAPH OBJECT. Callers hold their edges in dicts, adjacency lists and
    closures, so demanding a built graph at every call site would push graph construction into
    five modules to save it in one.
    """

    def __call__(self, node: T) -> Iterable[T]:
        """Return the nodes reachable in one step from `node`."""
        ...


def _by_count[T](row: tuple[int, T]) -> int:
    """Sort key: the reach count alone.

    ⚑ THE COUNT, NOT THE WHOLE TUPLE. Sorting the pair would demand that the caller's NODE type
    be orderable, for a tie-break nobody asked for — and the node type belongs to the caller.
    """
    return row[0]


def _graph_from[T](seeds: list[T], successors: Successors[T]) -> nx.DiGraph[T]:
    """Materialise ONLY the reachable part of the caller's graph.

    ⚑ LAZY BY CONSTRUCTION. The caller's relation may describe a graph far larger than the cone
    being asked about; walking it eagerly would make a question about six seeds cost the whole
    corpus.
    """
    graph: nx.DiGraph[T] = nx.DiGraph()
    graph.add_nodes_from(seeds)
    seen, stack = set(seeds), list(seeds)
    while stack:
        current = stack.pop()
        for nxt in successors(current):
            graph.add_edge(current, nxt)
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return graph


def reach[T](seeds: Iterable[T], successors: Successors[T]) -> set[T]:
    """Return every node transitively reachable from `seeds`, EXCLUDING the seeds.

    ⚑ NO DEPTH BOUND, and that is load-bearing rather than incidental: a bound here silently
    TRUNCATES. A recorded instance capped a walk at three levels and 1,506 of 2,964 modules
    reached past it — a capability bound wearing a termination bound's clothes. `descendants` is
    unbounded and cycle-safe by construction, which is one fewer invariant to re-establish.
    """
    seed_list = list(seeds)
    graph = _graph_from(seed_list, successors)
    out: set[T] = set()
    for seed in seed_list:
        out |= nx.descendants(graph, seed)
    return out - set(seed_list)


def rank[T](seeds: Iterable[T], successors: Successors[T]) -> list[tuple[int, T]]:
    """Return `[(n_reached, seed)]` descending — which seed reaches most, ALL of them.

    ⚑⚑ THE TRUNCATION THAT USED TO LIVE HERE WAS JUDGEMENT FROZEN INTO THE COMPUTATION. It
    returned `top[:5]`: a DISPLAY decision baked in where no caller could ask for more, silently
    dropping the sixth-largest seed from every consumer. **The cap belongs at the print**, so
    this returns the ranking WHOLE.

    ⚑ AND THE ROWS OVERLAP — the same caveat as a cone. Two seeds under one subtree both report
    it, so this ORDERS seeds and must never be SUMMED.
    """
    scored = [(len(reach([seed], successors)), seed) for seed in seeds]
    scored.sort(key=_by_count, reverse=True)
    return scored


def exclusive[T](
    seeds: Iterable[T], others: Iterable[Iterable[T]], successors: Successors[T]
) -> set[T]:
    """Return the part of `seeds`' cone that NO other blocking set also reaches.

    ⚑⚑⚑ THIS IS THE FUNCTION THE WHOLE MODULE EXISTS FOR, and it is what a bare cone gets wrong.
    Clearing a set frees only the nodes whose remaining blockers are all inside it — measured at
    60-75% overlap across three real buckets, so reporting a cone as "frees N" was wrong by ~4x.

    ⚑ THE SUBTRACTION IS OVER UNIONS, NEVER SUMS. Other blockers share descendants with each
    other too; summing their cones would over-subtract exactly where they overlap.
    """
    mine = reach(seeds, successors)
    blocked: set[T] = set()
    for other in others:
        blocked |= reach(other, successors)
    return mine - blocked


def weigh[T](nodes: Iterable[T], successors: Successors[T]) -> dict[T, int]:
    """Return `{node: n_descendants}` — every node's transitive weight, in ONE pass.

    ⚑⚑ THE COLLAPSE IS WHERE LEVERAGE WAS BEING LOST. An item is a FOLD of its population: one
    worklist row can stand for 216 census keys. Ranking by warrants-that-cite-me charges 215 of
    those keys nothing, so the fold that made the list readable also made it mis-ordered — a
    216-key item and a 1-key item sorting adjacently.

    ⚑ AND THE FIX IS NOT A FLOOR RULE, IT IS PUTTING THE CONTENT IN THE GRAPH. With each key a
    node under its item, the weight holds BY CONSTRUCTION — no rule to enforce, no size special
    case, no second grade to reconcile.

    ⚑⚑ UNION, NEVER SUM — this is the whole subtlety. Children's weights double-count shared
    descendants, so adding them counts one subtree several times. Cardinality of the UNION of
    descendant SETS is exact.
    """
    node_list = list(nodes)
    graph = _graph_from(node_list, successors)
    return {node: len(nx.descendants(graph, node)) for node in node_list if node in graph}
