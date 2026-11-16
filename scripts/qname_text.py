#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Walk a `QName` subtree in a decoded record to its dotted text.

⚑ THIS IS THE FIELD THE RESOLVER GATES ON, AND IT WAS NULL ON EVERY ROW.
`scope_fix._event_refs` reads `if not qname or ctor not in _FREE_CTORS: continue` — so with
`qname` NULL for all 2,124,390 events that loop skipped every node and the resolver returned
`[]` for every module. The v1 emitter wrote `"qname"` as a FIELD; the generic walker emits
the QName as a SUBTREE (`AgdaiReflect.hs`: *"A `QName` is a subtree"*), and `_insert_decoded`
kept reading the field.

⚑ MEASURED STRUCTURE (sandbox, `Algebra/F2/F2.agdai`, 2026-08-07):

    QName → [MName, Name]           child[0] the module path, child[1] the base name
    Name  → … → [] → Id → #String:"F\8322"

A `Name`'s name-part is a LIST of `Id`s (Agda's `nameParts`, so an operator like `_+_` is
several pieces), each `Id` wrapping a `#String:` leaf. Two `Name` arities occur — a 6-child
form and a 3-child form — so `name_text` SEARCHES the children for the list rather than
indexing a fixed position, which is what makes it work for both.

⚑ THE DOCSTRING IS RAW BECAUSE THE MEASURED SHAPE CONTAINS A BACKSLASH. Written cooked,
`\8322` becomes an escape python interprets, so the documented format silently stops matching
the format — a comment about an escaping bug, broken by escaping.

⚑⚑ AND NAMING THE PREFIX IN THE PROSE ENDED THE DOCSTRING EARLY. Spelling the three-quote
form inline closed the literal mid-sentence; the file still PARSED, as a different module
than the one intended, and both checkers passed it. A syntactic accident that survives every
gate is caught only by importing the module — which is why the equivalence check runs.
"""

from __future__ import annotations

from scripts import haskell_escape
from scripts.decoded_node import NodeMap, Record, child, ctor_of, kids_of
from scripts.leaf_format import leaf_value

# ⚑ A TERMINATION GUARD, NOT A CAPABILITY BOUND. `nodes` is a DAG with sharing; an unbounded
# walk over a malformed record would not terminate. The real structure is 3 levels, so this
# is slack rather than a limit that could silently truncate a real name.
_MAX_DEPTH = 8

# A QName is `[MName, Name]` — a record with fewer children is not one.
_QNAME_ARITY = 2


def name_text(nodes: NodeMap, lid: object, depth: int = 0) -> str | None:
    """Return the string a `Name` node carries, or None."""
    if depth > _MAX_DEPTH:
        return None
    rec = child(nodes, lid)
    if rec is None:
        return None
    lv = leaf_value(ctor_of(rec))
    if lv and lv[0] == "String":
        # ⚑ `show` ON A String YIELDS A QUOTED, ESCAPED LITERAL, and left raw the recovered
        # qname is `Substrate.Algebra.F2.F2.F\8322` — which joins against nothing while still
        # READING like a name. Agda names are routinely non-ASCII, so this is the common case.
        return haskell_escape.unescape(lv[1])
    for k in kids_of(rec):
        got = name_text(nodes, k, depth + 1)
        if got is not None:
            return got
    return None


def _path_parts(nodes: NodeMap, mname: Record) -> list[str]:
    """Return the module-path segments an `MName` node carries.

    ⚑ SPLIT OUT BECAUSE THE NESTING WAS THE COMPLEXITY, NOT THE JOIN. `MName → [] → [Name,
    Name, …]` is two levels of list before a segment, so inlining it put a doubly-nested loop
    inside the function whose job is to join with dots.
    """
    parts: list[str] = []
    for k in kids_of(mname):
        lst = child(nodes, k)
        for seg in kids_of(lst) if lst is not None else []:
            t = name_text(nodes, seg)
            if t:
                parts.append(t)
    return parts


def qname_text(rec: Record, nodes: NodeMap) -> str | None:
    """Return a `QName` node's dotted qualified name, or None.

    Dotted-joining the module path and appending the base is what `path_text` stores for
    the v1 records.
    """
    kids = kids_of(rec)
    if len(kids) < _QNAME_ARITY:
        return None
    mname = child(nodes, kids[0])
    parts = _path_parts(nodes, mname) if mname is not None else []
    base = name_text(nodes, kids[1])
    if base:
        parts.append(base)
    return ".".join(parts) if parts else None
