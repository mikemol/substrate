# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Types for the `networkx` surface this repo's cone authority uses.

⚑⚑⚑ THE PUBLISHED `types-networkx` WAS TRIED FIRST AND IS THE WRONG TOOL HERE. Its `DiGraph` is
generic over its ATTRIBUTE DICTS — `DiGraph[T, dict[str, Any], dict[str, Any]]` — so under
`disallow_any_expr` every expression touching a graph is flagged, and `cast()` cannot rescue it
because the `Any` is flagged before the cast concretises. The repo's rule distinguishes these
precisely: *stub an untyped dep (that ADDS types); ignore a typed dep whose types contain `Any`
at a boundary walled by a concrete return.* Node and edge attributes are not a walled boundary —
they are the interface — and this repo never uses them.

⚑⚑ SO THE PARAMETER THAT MATTERS IS DROPPED, NOT THE SURFACE. `DiGraph` here is generic over the
NODE type ALONE; the attribute-dict parameters are simply absent, because this repo's graphs carry
no attributes. That single omission is the whole fix, and it is not a consequence of declaring
fewer methods.

⚑⚑⚑ AND THE SIGNATURES ARE READ FROM THE LIBRARY, NOT FROM THE CALL SITES. Typing only what this
repo happens to pass would encode the CALLER's habits as the library's contract — so a later
caller using a documented form would be refused by a stub that was never wrong, only narrow.
Read from `classes/digraph.py` and `algorithms/dag.py`:

    add_nodes_from(nodes_for_adding, **attr)   nodes OR (node, attrdict) pairs
    add_edge(u_of_edge, v_of_edge, **attr)     positional endpoints
    descendants(G, source) -> set             RAISES NetworkXError if source not in G

⚑⚑ THAT LAST ONE IS A CONTRACT THIS REPO SILENTLY DEPENDS ON, and typing it is what makes the
dependence visible: `weigh` guards with `node in graph` and `reach` relies on its seeds having
been added first. Both are correct BECAUSE of the raise, and neither says so — the exception in
the stub is where a reader learns the guard is load-bearing rather than defensive.

⚑ THE `**attr` KEYWORDS ARE DELIBERATELY NOT DECLARED. Accepting them would re-admit the
attribute dicts this stub exists to drop, and a caller who wants graph attributes wants the
published stubs and a different typing bar — not this narrow one.

⚑ A STUB IS A CLAIM THIS REPO MUST KEEP TRUE. Every name here is a signature `stubtest` checks
against the installed library, and each drifts on their release schedule — so the surface is the
four names actually called, not a mirror of the library.

⚑⚑ AND THAT LAST SENTENCE IS A DECLARATION OF PARTIALITY, SO IT IS NOW SPELLED AS ONE. Checked
without relief, this stub produces thousands of findings across networkx's ~579 modules, of
which every single one is a name this file deliberately never claimed — a gate reporting the
CHECKER'S DEFAULT as though it were drift. With the marker below, what remains is six findings,
all of them declined OPTIONAL parameters (`**attr` attribute dicts and the `backend=` dispatch
kwargs), none of which any caller here passes.

⚑ WHAT THE MARKER DOES NOT BUY, said plainly because the neighbouring `panflute` stub proved it
matters: a wrong parameter NAME or type in a signature this file DOES declare is a contradiction,
not an omission, and survives the relief to fail the gate. Declining a surface is not declining
scrutiny of what is kept.

⟡declines: every networkx module beyond the package root (the `algorithms` tree and all its
    siblings), `DiGraph`'s attribute-dict `**attr` keywords on every method, the `backend=` /
    `**backend_kwargs` dispatch parameters, and every `DiGraph` method beyond the four this
    repo calls — the attribute dicts are the parameter this stub exists to drop.

⚑ THE THREE NAMED ENTRIES BELOW are the signatures the prose declines, handed to
`stubtest --allowlist` one finding at a time. `DiGraph.__init__` declines `incoming_graph_data`
and `**attr`; `DiGraph.__new__` and `descendants` decline the `backend=` dispatch machinery
networkx's decorators add. None is reachable from this repo, and none is a contradiction — the
stub's own parameters still match the library's.

⟡declines-signature: networkx.DiGraph.__init__, networkx.DiGraph.__new__, networkx.descendants
"""

from collections.abc import Iterable

class NetworkXError(Exception):
    """Raised for a request the graph cannot answer — including an absent source node."""

class DiGraph[T]:
    """A directed graph over nodes of type `T`, carrying no attributes.

    ⚑ NO ATTRIBUTE PARAMETERS, which is the entire reason this stub exists rather than the
    published one. A graph in this repo is a shape: edges come from the caller's own relation
    and answers come back as sets of the caller's nodes.
    """

    def __init__(self) -> None: ...
    def __contains__(self, node: T) -> bool: ...
    def __len__(self) -> int: ...
    def add_nodes_from(self, nodes_for_adding: Iterable[T]) -> None: ...
    def add_edge(self, u_of_edge: T, v_of_edge: T) -> None: ...

def descendants[T](G: DiGraph[T], source: T) -> set[T]:
    """Every node reachable from `source`, excluding `source` itself.

    ⚑ RAISES `NetworkXError` WHEN `source` IS NOT IN `G` — not an empty set. A caller must add
    its seeds before asking, and a membership guard before this call is load-bearing rather than
    defensive.
    """
    ...
