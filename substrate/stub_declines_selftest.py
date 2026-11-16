#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.stub_declines`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321).
"""

from __future__ import annotations

import sys

from substrate.stub_declines import (
    _BLANK_STOP,
    _BROKEN,
    _IN_COMMENT,
    _IN_METHOD,
    _IN_STRING,
    _MULTI,
    _SIG_MULTI,
    _SURFACE_IN_METHOD,
    PARSED,
    UNREADABLE,
    declines_signature_text,
    declines_text,
    read_source,
)


def _selftest() -> int:
    """Cases pinning that a declaration is read, and that a NON-declaration is not."""
    cases: list[tuple[str, object, object]] = []

    def check(name: str, got: object, want: object) -> None:
        cases.append((name, got, want))

    check(
        "a marker declares its prose",
        declines_text('"""Doc.\n\n⟡declines: the async surface.\n"""'),
        "the async surface.",
    )
    check(
        "a multi-line declaration is collapsed to one line",
        declines_text(_MULTI),
        "element constructors, and `walk`'s stop_if.",
    )
    check(
        "a declaration ending at a blank line stops there",
        declines_text(_BLANK_STOP),
        "the adapter layer.",
    )

    # ⚑ THE DISCRIMINATORS. Without these the predicate could answer "yes, something was
    # declined" to every stub in the tree and every case above would still pass.
    check(
        "a stub with NO marker declares nothing",
        declines_text('"""Doc.\n\nOnly what is called is declared.\n"""'),
        None,
    )
    check(
        "a MISSPELLED marker declares nothing (fail-closed)",
        declines_text('"""Doc.\n\n⟡dclines: the async surface.\n"""'),
        None,
    )
    check(
        "a marker with empty prose declares nothing",
        declines_text('"""Doc.\n\n⟡declines:\n\n"""'),
        None,
    )
    check(
        "the word 'declines' in ordinary prose is not a marker",
        declines_text('"""Doc.\n\nThis stub declines: nothing at all.\n"""'),
        None,
    )

    # ⚑⚑ THE `ast` NARROWING'S OWN DISCRIMINATORS. Both fixtures matched the OLD whole-file
    # regex and declared relief from a place that is not a declaration.
    check("a marker in a COMMENT is not a declaration", declines_text(_IN_COMMENT), None)
    check("a marker in a string literal is not a declaration", declines_text(_IN_STRING), None)

    check(
        "signature entries are split and stripped",
        declines_signature_text('"""D.\n\n⟡declines-signature: a.b, c.d\n"""'),
        ("a.b", "c.d"),
    )
    check(
        "signature entries span lines",
        declines_signature_text(_SIG_MULTI),
        ("nx.DiGraph.__init__", "nx.descendants"),
    )
    # ⚑ DISCRIMINATORS for the second marker: prose is NOT an entry, and the two markers are
    # read independently — declaring a surface must not conjure a signature allowlist.
    check(
        "prose in a signature marker is dropped, not passed to the allowlist",
        declines_signature_text('"""D.\n\n⟡declines-signature: every method really\n"""'),
        (),
    )
    check(
        "a surface declaration alone yields NO signature entries",
        declines_signature_text('"""D.\n\n⟡declines: the async surface.\n"""'),
        (),
    )
    check(
        "a signature declaration alone yields NO surface prose",
        declines_text('"""D.\n\n⟡declines-signature: a.b\n"""'),
        None,
    )

    # ⚑⚑ THE MEMBER-DOCSTRING ASYMMETRY, both halves. A class may name its OWN exemption; it may
    # not grant the package-wide surface flag.
    check(
        "a member docstring may declare its own signature exemption",
        declines_signature_text(_IN_METHOD),
        ("psycopg.rows.RowMaker.__call__",),
    )
    check(
        "a member docstring may NOT declare the package surface",
        declines_text(_SURFACE_IN_METHOD),
        None,
    )

    # ⚑⚑⚑ THE FALSE ZERO, PINNED. A broken stub must be UNREADABLE, never "declines nothing" —
    # and the discriminator is the healthy file beside it, which must NOT be flagged.
    broken = read_source(_BROKEN)
    healthy = read_source('"""Doc.\n\n⟡declines: the async surface.\n"""')
    check("a syntactically invalid stub is UNREADABLE", broken.state, UNREADABLE)
    check("an unreadable stub names its parse error", broken.reason.split(":")[0], "SyntaxError")
    check("an unreadable stub declares no surface", broken.surface, None)
    check("a VALID stub is not flagged unreadable", healthy.state, PARSED)
    check("a valid stub carries no parse-error reason", healthy.reason, "")

    ok = sum(1 for _n, g, w in cases if g == w)
    for n, g, w in cases:
        if g != w:
            sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"stub_declines selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.stdout.write(__doc__ or "")
    sys.exit(2)
