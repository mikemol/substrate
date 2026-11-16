#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Recover (qname, idx, lit) from a v2 generic-walk record — the v1 field semantics.

⚑ THE PRODUCER MOVED THESE FROM FIELDS TO CHILDREN AND THE CONSUMERS NEVER FOLLOWED.
`agdai_shim.hs`'s old `emit` printed `"qname":q,"index":ix,"lit":…`; the generic `emitG`
prints only `{"id","constructor","children"}`, and its own comment says why — *"under a
generic walk those are CHILDREN. A `QName` is a subtree, a de Bruijn index is a `#Int:7`
leaf, a literal is `#Integer:61`."* `_insert_decoded` still read `rec.get("index")`, so
every one of 2,124,390 event rows got NULL.

⚑ MEASURED CONSEQUENCE, VISIBLE IN THE STORE: `project_sppf` builds `role = f"db{idx}"`, so
with `idx` None every `Var` interns with role **`"dbNone"`** — one shared role for the whole
corpus (`_node.role_id` had exactly 2 distinct values over 4,775 nodes, and `dbNone` was one).

⚑ BUT THE INDEX WAS NEVER LOST, WHICH IS WHY THIS IS RECOVERY AND NOT RE-INGEST. The
`dbNone` node's own key carries `#Int:0` as child[0] — verified in the live store. So `Var 0`
and `Var 7` DO still differ (by child), and the alpha-equivalence collapse
`AgdaiReflect.hs:393-396` warns about did NOT happen at the node level. What broke is the
FIELD, and every consumer reading the field rather than the child.

⚑⚑ THE THREE RECOVERIES ARE INDEPENDENT AND ARE NOW THREE FUNCTIONS. One body did all of
them against one shared `kids`, so the qname branch's early `return` and the literal branch's
`if not lit` guard read as one algorithm with interacting state when they are three separate
reads of the same record. Splitting them is what let each one's return type be stated.
"""

from __future__ import annotations

from scripts.decoded_node import NodeMap, Record, child, ctor_of, kids_of
from scripts.leaf_format import leaf_int, leaf_value
from scripts.qname_text import qname_text

# jea_agdai.go referential set — the constructors whose child[0] carries a QName SUBTREE.
#
# ⚑ THIS SET IS THIS LAYER'S VOCABULARY, NOT THE WRITER'S. It is a fact about the generic
# walker's OUTPUT FORMAT, which is what this module reads; leaving it with the module that
# merely writes rows would put the format's vocabulary one layer above the only code that
# interprets it.
#
# ⚑⚑ AND IT IS COPIED FROM THE SOURCE, NOT FROM THE PROSE ABOUT IT. The first draft of this
# line was typed from a docstring's description of the set and got FIVE of eight members
# wrong in both directions — inventing `MetaV`/`PatternSyn`, dropping the whole pattern side
# (`PCon`/`PDef`/`PProj`) and both `Prim` forms. Every dropped member is a constructor whose
# qname would silently stop being recovered, which is the exact defect this module exists to
# repair. A membership set is DATA; re-deriving it from a summary is how it drifts.
FREE = frozenset({"Def", "Con", "Prim", "PrimSort", "Proj", "PCon", "PDef", "PProj"})

# A de Bruijn index lives at child[0], per the generator's declaration order:
# *"`Var/2 [Int, Elims]` emits `Var [0,1]`"* (`AgdaiReflect.hs:228-229`). Reading position 0
# is a documented contract, not an inference from one sample.
_VAR_CTORS = frozenset({"Var", "PVar"})


def recover_lit(rec: Record) -> str:
    """Return the literal this record carries as a leaf, or "" when it is not one."""
    lv = leaf_value(ctor_of(rec))
    return lv[1] if lv else ""


def recover_qname(rec: Record, nodes: NodeMap) -> str | None:
    """Return the qualified name this record references, or None.

    ⚑ MEASURED: `Def [137, 138]` where 137 is a `QName [MName, Name]` (sandbox,
    `Algebra/F2/F2.agdai`). A reference carries its QName as a SUBTREE at child[0]; a `QName`
    node is its own answer.
    """
    ctor = ctor_of(rec)
    if ctor == "QName":
        return qname_text(rec, nodes)
    kids = kids_of(rec)
    if ctor not in FREE or not kids:
        return None
    head = child(nodes, kids[0])
    if head is None or ctor_of(head) != "QName":
        return None
    return qname_text(head, nodes)


def recover_idx(rec: Record, nodes: NodeMap) -> int | None:
    """Return a Var/PVar's de Bruijn index from child[0], or None."""
    kids = kids_of(rec)
    if ctor_of(rec) not in _VAR_CTORS or not kids:
        return None
    return leaf_int(ctor_of(child(nodes, kids[0])))


def recover_fields(rec: Record, nodes: NodeMap) -> tuple[str | None, int | None, str]:
    """Return (qname, idx, lit) for one record, preferring explicit v1 fields.

    ⚑ A v1 RECORD MUST STILL WIN. If the explicit fields are present the record came from
    the old emitter and is authoritative; recovery only fills what v2 omits. There is no
    version tag on the JSON (checked: neither `emit` nor `emitG` writes one), so
    field-presence IS the discriminator.
    """
    qname, idx = rec.get("qname"), rec.get("index")
    lit = rec.get("lit", "")
    have_q = qname if isinstance(qname, str) else None
    have_i = idx if isinstance(idx, int) else None
    have_l = lit if isinstance(lit, str) else ""
    if have_q is not None and have_i is not None and have_l:
        return (have_q, have_i, have_l)

    return (
        have_q if have_q is not None else recover_qname(rec, nodes),
        have_i if have_i is not None else recover_idx(rec, nodes),
        have_l or recover_lit(rec),
    )
