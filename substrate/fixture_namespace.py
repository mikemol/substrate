#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Compute the private SCHEMA NAME a suite fixture owns — one computation, no connection.

⚑⚑⚑ EXPOSED BECAUSE THE CREATOR WAS THE ONLY THING THAT KNEW THE TARGET, AND IT KEPT IT. The
fixture builder created the namespace, pointed `search_path` at it, and returned only the
connection — so a caller wanting to SCHEMA-QUALIFY a statement (a teardown whose whole thesis is
derived destruction) had no way to name the schema its objects live in. Every DROP therefore
went out unqualified and resolved through `search_path`: right by luck, not by mechanism. The
measured cost of that luck is one table name existing in SIXTEEN schemas of the sandbox tenant.

⚑⚑ AND IT IS A FUNCTION, NOT A DOCUMENTED CONVENTION. A caller re-spelling the prefix and the
sanitiser for itself would be computing a target that agrees with the creator by COINCIDENCE —
the two drift the first time either changes, and the drift's symptom is a DROP against the wrong
namespace, which is silent until something that should have been deleted is still there. The
fixture builder resolves through this, so there is exactly one computation of the name.

⚑⚑ NOT `current_schema()`, WHICH WOULD BE THE SAME AMBIGUITY ONE LAYER DOWN. That reads
`search_path` as well — merely later, and from inside the server. The qualification has to come
from where the object was CREATED, not from wherever the reader's path happens to point.

⚑⚑ THE NAME IS DETERMINISTIC, NOT RANDOMISED, AND THAT IS WHAT MAKES IT SELF-CLEANING. A random
name leaks a schema per run forever; a deterministic one is dropped and recreated, so the tenant
holds at most one namespace per fixture no matter how often the suite runs. ⚑ The cost is that
two fixtures passing the same identifier SHARE a namespace, which is why the identifier is
passed in by the caller rather than inferred: inferring it from the calling frame collapsed
several fixtures onto one fallback name, and the second one's teardown deleted the first's
search_path out from under it — a failure surfacing several frames later, naming a table.

⚑ PURE — IT OPENS NO CONNECTION. That is what lets a caller qualify its statements, and a case
assert the qualification, with postgres unreachable. A name computation that had to connect in
order to say what it would create could not be checked at the moment it most needs checking.
"""

from __future__ import annotations

#: The prefix every fixture namespace carries. ⚑ IT MARKS THESE SCHEMAS AS DISPOSABLE: an
#: operator listing the tenant's schemas can tell a fixture's namespace from a real one without
#: consulting any code, which is what makes a stale one safe to remove.
PREFIX = "fx_"

#: The character introducing an escaped one.
REPLACEMENT = "_"

#: How many hex digits encode one replaced character. ⚑⚑ THE PREDECESSOR REPLACED EVERY UNSAFE
#: CHARACTER WITH A BARE `_`, WHICH COLLAPSES DISTINCT IDENTIFIERS — measured here, not predicted:
#: `suite.alpha` and `suite-alpha` both rendered `fx_suite_alpha`, so two fixtures would have
#: shared one namespace and one teardown would have dropped the other's schema. That is exactly
#: the collision the deterministic name exists to prevent, reintroduced by its own sanitiser.
#: Encoding the character's code point instead keeps distinct inputs distinct.
ESCAPE_WIDTH = 2

#: The largest code point the escape can represent. ⚑ ABOVE IT THE ENCODING WOULD BE WIDER THAN
#: its width and two different characters could render alike — the collapse this escape removes.
ESCAPE_MAX = 0xFF

#: How much of the sanitised identifier survives. ⚑ POSTGRES TRUNCATES AN OVER-LONG IDENTIFIER
#: SILENTLY at 63 bytes, so two long fixture names could collide inside the server while looking
#: distinct in the source. Truncating here — shorter than the server's limit, with the prefix
#: accounted for — makes the collision happen where a case can see it rather than in the catalogue.
LIMIT = 48


def schema_for(name: str) -> str:
    """Return the schema name the fixture identified by `name` owns.

    ⚑⚑ EVERY NON-ALPHANUMERIC CHARACTER IS ESCAPED TO ITS CODE POINT, NOT COLLAPSED TO A BARE
    `_`. A schema name reaching a statement is an identifier, and one assembled from an arbitrary
    string is where an injection lives — but a sanitiser that maps every unsafe character to the
    SAME replacement is INJECTIVE ON NOTHING: measured here, `suite.alpha` and `suite-alpha` both
    rendered `fx_suite_alpha`. That is two fixtures sharing one namespace, which is precisely the
    collision a deterministic name exists to prevent, reintroduced by the sanitiser meant to make
    the name safe. Escaping keeps distinct identifiers distinct AND keeps the result safe.

    ⚑ A CODE POINT WIDER THAN THE ESCAPE REFUSES rather than rendering a truncated hex digit that
    a different character could also produce — the same collapse one layer down.

    ⚑ AN EMPTY IDENTIFIER REFUSES. It would render as the bare prefix — a namespace every
    unnamed fixture would share, which is exactly the collapse that made a teardown delete
    another fixture's schema.
    """
    if not name:
        msg = (
            "schema_for(''): a fixture needs an identifier. An empty one renders as the bare "
            "prefix, so every unnamed fixture would share one namespace — the collapse whose "
            "symptom is one fixture's teardown dropping another's schema."
        )
        raise ValueError(msg)
    parts: list[str] = []
    for char in name:
        if char.isalnum():
            parts.append(char)
            continue
        point = ord(char)
        if point > ESCAPE_MAX:
            msg = (
                f"schema_for({name!r}): {char!r} is outside the escape's range, so it would "
                f"render alike to a different character. Use an identifier a fixture can own "
                f"unambiguously."
            )
            raise ValueError(msg)
        parts.append(f"{REPLACEMENT}{point:0{ESCAPE_WIDTH}x}")
    return PREFIX + "".join(parts)[:LIMIT]
