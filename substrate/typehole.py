#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Align K interned nodes into a shared skeleton with typed holes — by position, or by key.

⚑⚑⚑ EXTRACTED FROM `jea_pysim.Corpus.typehole` (665 findings behind the per-file gate) so it
can grow one thing the origin could not: a KIND-DEPENDENT child alignment. The origin aligns
children POSITIONALLY and, on `same head, different arity`, returns one `:variadic` hole
without recursing — which is right for a python AST node, where position IS a child's
identity (`Call` with three args and `Call` with four have no corresponding third child), and
wrong for a node whose children carry their identity in a KEY. AMR nodes do: each child's
`role` (`:ARG0`, `:mod`) names it, and `jea_pyalg.IR.key()` already puts `role` in the
canonical identity — so aligning by role is not a new congruence, it is the intern's own,
applied to the recursion. MEASURED (amr-skills @e87d111, 64 sentences, K=5): with positional
alignment every divergence stopped at the first arity mismatch and L_OR support scored 0 votes
in 64 of 64; the planes had support to give and the reader never compared the children.

⚑⚑ THE RULE: a node's children are KEYED iff every child carries a non-empty key and the keys
are distinct within that node; otherwise they are POSITIONAL and the origin's behaviour is
reproduced exactly — including the variadic hole. Keyed children align by key: keys present in
EVERY candidate recurse (that is where shared fillers live); keys present in only some become
one `:variadic` hole beside them carrying the fillers, so the arity distinction is still
reported, just not in the way that hides everything under it.

⚑ THE OUTPUT IS THE ORIGIN'S DICT SHAPE, unchanged, so a consumer that reads `kind`, `head`,
`children`, `type`, `fillers` from the origin reads this without adaptation. `head` is
`(kind, op, lit)` — `role` is deliberately NOT part of a head, because role is a CHILD's identity
under its parent, not a property of the node's own shape. The origin compares heads the same
way; only its `shared` leaf reports a four-tuple, which is kept.

⚑ THE INTERN IS A PROTOCOL, NOT AN IMPORT. `jea_pyalg` is a bare-import module this package
must not reach for; the two things this reader needs — an indexable node table and five
attributes per node — are declared here and satisfied by `Intern` without change.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# The origin's default recursion cap.
MAX_DEPTH = 24

Head = tuple[str, str, str]
Report = dict[str, object]


class Node(Protocol):
    """What one interned node exposes — the five fields `jea_pyalg.IR` declares.

    ⚑ READ-ONLY PROPERTIES, NOT ATTRIBUTES: a Protocol attribute is settable and therefore
    INVARIANT, so a `list[FixtureNode]` could never satisfy `Sequence[Node]`. This reader only
    reads, so declaring what it reads as properties is both honest and what lets any node
    class — the origin's `IR`, a frozen fixture — satisfy it structurally.
    """

    @property
    def kind(self) -> str:
        """Return the node's kind — the AST class name, or the AMR node type."""
        ...

    @property
    def role(self) -> str:
        """Return the node's role under its parent, or `` when it carries none."""
        ...

    @property
    def op(self) -> str:
        """Return the operator token, or ``."""
        ...

    @property
    def lit(self) -> str:
        """Return the literal KIND (never the value), or ``."""
        ...

    @property
    def children(self) -> tuple[int, ...]:
        """Return the child ids, in the order the intern recorded them."""
        ...

    @property
    def payload(self) -> tuple[object, ...]:
        """Return the residue — the values the canonical identity does not carry."""
        ...


class Table(Protocol):
    """What an intern table exposes: its nodes, by id."""

    @property
    def nodes(self) -> Sequence[Node]:
        """Return the node table, indexable by id."""
        ...


def role_key(node: Node) -> str | None:
    """Return the default child key — a node's `role`, or None when it carries none."""
    return node.role or None


def _head(n: Node) -> Head:
    """Return the head the origin compares: `(kind, op, lit)`, never the role."""
    return (n.kind, n.op, n.lit)


def _filler(nodes: Sequence[Node], nid: int) -> Report:
    """Render one filler the way the origin's `_filler_repr` does."""
    nn = nodes[nid]
    return {"head": (nn.kind, nn.op, nn.lit), "payload": nn.payload, "node": nid}


def _keyed(
    nodes: Sequence[Node], children: tuple[int, ...], key: Callable[[Node], str | None]
) -> dict[str, int] | None:
    """Return `{key: child}` when every child has a distinct key, else None (positional)."""
    if not children:
        return None
    keyed: dict[str, int] = {}
    for c in children:
        k = key(nodes[c])
        if k is None or k in keyed:
            return None
        keyed[k] = c
    return keyed


class Aligner:
    """The recursion, parameterised on the intern and the child-key rule."""

    def __init__(
        self, table: Table, key: Callable[[Node], str | None] = role_key, max_depth: int = MAX_DEPTH
    ) -> None:
        """Bind the intern's node table, the child-key rule and the recursion cap."""
        self.nodes = table.nodes
        self.key = key
        self.max_depth = max_depth

    def typehole(self, node_ids: Sequence[int], depth: int = 0) -> Report:
        """Align `node_ids`; return the origin's `{kind, head, children | fillers, …}` shape."""
        ids = list(node_ids)
        if len(set(ids)) == 1:
            nn = self.nodes[ids[0]]
            return {
                "kind": "shared",
                "head": (nn.kind, nn.role, nn.op, nn.lit),
                "node": ids[0],
                "children": [],
            }
        heads = [_head(self.nodes[i]) for i in ids]
        if len(set(heads)) > 1 or depth >= self.max_depth:
            return self._diverged(ids, heads, depth)
        return self._agreed(ids, heads[0], depth)

    def _diverged(self, ids: list[int], heads: list[Head], depth: int) -> Report:
        """Return a skeleton if diverging heads still share child structure, else a hole."""
        kinds = sorted({h[0] for h in heads})
        if depth < self.max_depth and len(set(heads)) > 1:
            childsets = [self.nodes[i].children for i in ids]
            arities = {len(c) for c in childsets}
            if len(arities) == 1 and arities != {0}:
                sub = [
                    self.typehole([cs[pos] for cs in childsets], depth + 1)
                    for pos in range(arities.pop())
                ]
                if any(s["kind"] in ("shared", "skeleton") for s in sub):
                    return {
                        "kind": "skeleton",
                        "head": ("|".join(kinds), "", ""),
                        "diverged": True,
                        "children": sub,
                    }
        return {
            "kind": "hole",
            "type": kinds[0] if len(kinds) == 1 else "?",
            "head_kinds": kinds,
            "fillers": [_filler(self.nodes, i) for i in ids],
            "depth": depth,
        }

    def _agreed(self, ids: list[int], head: Head, depth: int) -> Report:
        """Recurse into agreeing heads' children — by key when every candidate is keyed."""
        childsets = [self.nodes[i].children for i in ids]
        keyed = [_keyed(self.nodes, cs, self.key) for cs in childsets]
        if all(k is not None for k in keyed):
            return self._agreed_keyed(ids, head, depth, [k for k in keyed if k is not None])
        arities = {len(c) for c in childsets}
        if len(arities) > 1:
            # ⚑ THE ORIGIN'S VARIADIC HOLE, UNCHANGED FOR POSITIONAL CHILDREN: position is the
            # child's identity here, so different arities have no corresponding children.
            return {
                "kind": "skeleton",
                "head": head,
                "children": [self._variadic(ids, head, depth)],
            }
        kids = [
            self.typehole([cs[pos] for cs in childsets], depth + 1) for pos in range(arities.pop())
        ]
        return {"kind": "skeleton", "head": head, "children": kids}

    def _agreed_keyed(
        self, ids: list[int], head: Head, depth: int, keyed: list[dict[str, int]]
    ) -> Report:
        """Recurse on the keys every candidate has; the rest becomes one variadic hole."""
        common = sorted(set.intersection(*(set(k) for k in keyed)))
        every = sorted(set.union(*(set(k) for k in keyed)))
        kids: list[Report] = [self.typehole([k[c] for k in keyed], depth + 1) for c in common]
        if len(every) != len(common):
            hole = self._variadic(ids, head, depth)
            hole["keys"] = [k for k in every if k not in common]
            kids.append(hole)
        return {"kind": "skeleton", "head": head, "keyed": True, "children": kids}

    def _variadic(self, ids: list[int], head: Head, depth: int) -> Report:
        """Render the origin's variadic hole: same head, children that do not correspond."""
        return {
            "kind": "hole",
            "type": head[0] + ":variadic",
            "fillers": [_filler(self.nodes, i) for i in ids],
            "depth": depth,
        }


def typehole(
    table: Table,
    node_ids: Sequence[int],
    *,
    key: Callable[[Node], str | None] = role_key,
    max_depth: int = MAX_DEPTH,
) -> Report:
    """Align `node_ids` over `table` — the one-call form of `Aligner`."""
    return Aligner(table, key, max_depth).typehole(node_ids)
