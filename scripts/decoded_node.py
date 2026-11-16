#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read one node out of a decoded generic-walk record map.

⚑⚑ THE INT/STR KEY TOLERANCE WAS WRITTEN TWICE, AND THAT DUPLICATION IS WHY THIS IS A
MODULE. `sppf_recover._child` carries the rule with a comment explaining it, and
`recover_fields`' de Bruijn branch carries the SAME rule inline with its own comment saying
the same thing — one fact about the producer's output, stated in two places, either of which
could be fixed without the other. It is a property of the FORMAT, so it belongs to the layer
that reads the format.

⚑ THE TRAP ITSELF: JSON object keys are STRINGS while a record's `children` holds INTEGERS.
Looking up the int alone silently missed every child — no error, no empty result, just a
`None` that every caller reads as "absent" rather than "asked wrong".

⚑⚑ AND THE DECODED SHAPE IS `object`, NOT `Any` — WHICH IS THE WHOLE POINT OF THE SEAM.
`Any` is refused outright here (no suppression path), and reaching for it was the reflex: a
`json.load` result FEELS untyped, so `dict[str, Any]` reads as the honest annotation. It is
the opposite. `Any` propagates — every read off a `Record` would silently become `Any` in the
caller, which is exactly how the 76-finding `namedtuple` cascade got in. `object` does not
propagate: it forces each read to narrow at the point it commits to a type, which is where
the producer's contract actually gets asserted. The verbosity is the type system asking for
the check that the inline `isinstance` dance was doing by hand anyway.
"""

from __future__ import annotations

# A decoded record: `{"id", "constructor", "children"}` plus whatever v1 fields survive.
Record = dict[str, object]

# local id -> record, keyed as the producer wrote it (see the trap above).
NodeMap = dict[object, Record]


def child(nodes: NodeMap, lid: object) -> Record | None:
    """Return one node by local id, tolerating int/str JSON keys. None if absent."""
    return nodes.get(lid) if lid in nodes else nodes.get(str(lid))


def ctor_of(node: Record | None) -> str | None:
    """Return a node's constructor, or None for an absent or unconstructed node.

    ⚑ ABSENT AND UNCONSTRUCTED COLLAPSE HERE DELIBERATELY. Every caller treats a missing
    node and a node with no constructor the same way — skip the branch — so `(c0 or {}).get(...)`
    was being spelled at each site. One spelling, and the callers stop carrying the `or {}`.
    """
    if node is None:
        return None
    got = node.get("constructor")
    return got if isinstance(got, str) else None


def kids_of(node: Record) -> list[object]:
    """Return a record's children, or an empty list when it has none.

    ⚑ `rec.get("children") or []` WAS THE SPELLING AT EVERY SITE, and the `or` was doing
    real work: the producer writes `null`, not an omitted key, for a childless node. A
    reader that only guarded the KeyError still got `None` back.
    """
    got = node.get("children")
    return got if isinstance(got, list) else []
