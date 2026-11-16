# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Narrow a decoded JSON document to typed accessors, once, at the boundary.

⚑ `json.loads` RETURNS `Any` IN TYPESHED, AND `Any` SPREADS. Under
`disallow_any_expr` every expression touching a decoded document is a finding, so a
caller reading `reply["info"]["kind"]` inline earns one finding per access — seven,
in the module that motivated this. `stubs/json/__init__.pyi` re-declares the decode
functions as returning `object`, which is STRICTER than typeshed rather than looser:
`object` admits no subscript or attribute access at all, so a reader must narrow
before it can read. This module is where that narrowing lives, once, instead of at
every call site.

⚑⚑ AND EVERY READER RETURNS A DEFAULT RATHER THAN RAISING, DELIBERATELY. These
parse output from an external program, where a missing or wrong-typed field is a
fact about that program's version — not a bug in the caller. A reader that raises
turns "this reply had no `contents`" into a crash mid-batch and discards the replies
already parsed; one that returns a default lets the caller see a partial result AS
partial. The default is always explicit, so a caller that needs to tell "absent"
from "present and empty" can compare against the one it passed.
"""

from __future__ import annotations

import json


def decode(text: str) -> object | None:
    """Decode one JSON document, or None when it is not valid JSON.

    Handing back `object` rather than a union of JSON shapes is the point: the
    caller states what it expects by which reader it reaches for, and an unexpected
    shape becomes that reader's default instead of an error at the decode site.
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def field(doc: object, key: str) -> object | None:
    """Return `doc[key]` when `doc` is a mapping carrying it, else None."""
    if isinstance(doc, dict):
        return doc.get(key)
    return None


def text_field(doc: object, key: str, default: str = "") -> str:
    """Return `doc[key]` when it is a string, else `default`."""
    value = field(doc, key)
    return value if isinstance(value, str) else default


def list_field(doc: object, key: str) -> list[object]:
    """Return `doc[key]` when it is a list, else an empty list."""
    value = field(doc, key)
    return value if isinstance(value, list) else []


def str_map(doc: object) -> dict[str, str]:
    """Return `doc` as a str→str mapping, keeping only the pairs that already are.

    ⚑ NON-CONFORMING PAIRS ARE DROPPED, NOT COERCED. `str(value)` would manufacture
    a plausible string for a number or a nested object, and a caller comparing that
    against real output would find a difference it could not explain.
    """
    if not isinstance(doc, dict):
        return {}
    return {k: v for k, v in doc.items() if isinstance(k, str) and isinstance(v, str)}


def dumps_stable(doc: object) -> str:
    """Serialise `doc` so that equal content yields equal bytes.

    ⚑ SORTED KEYS ARE THE POINT, NOT THE INDENT. A cache written twice from the same
    inputs must compare equal, or every reader that diffs it — or keys a staleness
    check on its mtime — sees churn that means nothing. Python preserves insertion
    order, so an unsorted dump encodes the order the producer happened to iterate in,
    which is a fact about the producer rather than about the content.
    """
    return json.dumps(doc, indent=1, sort_keys=True)
