#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The DECODED-RECORD reader: raw generic-walk JSON -> v1 field semantics.

⚑⚑ SPLIT OUT OF `sppf_db.py` 2026-08-11 (⟡split-1200), AND THE SEAM WAS THE ARROW, NOT THE
SIZE. This module is the one layer in `sppf_db` that consumes NOTHING from it — every
function takes a decoded record and the core's node map and returns text or fields, with no
connection, interner, schema or store. The dependency runs one way, `sppf_db ->
sppf_recover`, so moving the SUPPLIER made a leaf where moving a consumer would have made a
cycle.

⚑⚑ AND IT IS NOW FOUR MODULES, BECAUSE ONE FILE HELD FOUR CONCERNS (⟡sppf-recover-reader).
The per-file gate refused it at 30 ruff findings plus mypy's — which is the gate saying the
UNIT is wrong, not that the annotations are missing:

    decoded_node    reading a node out of the record map (the int/str key trap)
    leaf_format     the `#Int:0` leaf grammar
    haskell_escape  undoing `show`'s decimal codepoint escapes
    qname_text      walking a QName subtree to dotted text
    recover_fields  the three independent field recoveries

⚑ THE INT/STR KEY RULE WAS WRITTEN TWICE IN THIS FILE — once in `_child` and once inline in
`recover_fields`' de Bruijn branch, each with its own comment saying the same thing. One fact
about the producer's output, in two places, either fixable without the other. That
duplication is what identified `decoded_node` as a module rather than a helper.

⚑ THIS FILE REMAINS AS THE DELEGATING FACE, and the delegation is the point rather than an
artifact: `sppf_db` and `sppf_decode` import these names from here, and `agda_files()` became
four bodies under one name exactly because a second spelling was allowed to appear. Each name
below resolves to ONE body — verified 14/14 against the pre-split implementation on the shapes
`sppf_db`'s suite drives, including the `F₂` escape recovery and the FREE set's membership.
"""

from __future__ import annotations

from scripts.decoded_node import NodeMap, Record, child, ctor_of
from scripts.haskell_escape import unescape
from scripts.leaf_format import leaf_value
from scripts.qname_text import name_text, qname_text
from scripts.recover_fields import FREE, recover_fields

__all__ = [
    "FREE",
    "leaf_value",
    "recover_fields",
]


def _unescape_haskell(s: str) -> str:
    """Delegate to `haskell_escape.unescape` — kept for the pre-split spelling."""
    return unescape(s)


def _child(nodes: NodeMap, lid: object) -> Record | None:
    """Delegate to `decoded_node.child` — kept for the pre-split spelling."""
    return child(nodes, lid)


def _name_text(nodes: NodeMap, lid: object, depth: int = 0) -> str | None:
    """Delegate to `qname_text.name_text` — kept for the pre-split spelling."""
    return name_text(nodes, lid, depth)


def _qname_text(rec: Record, nodes: NodeMap) -> str | None:
    """Delegate to `qname_text.qname_text` — kept for the pre-split spelling."""
    return qname_text(rec, nodes)


def _ctor_of(node: Record | None) -> str | None:
    """Delegate to `decoded_node.ctor_of`."""
    return ctor_of(node)
