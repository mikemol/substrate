#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Parse a generic-walker LEAF constructor: `#Int:0` -> ("Int", "0").

⚑ THE ONE PLACE THE LEAF FORMAT IS PARSED. `AgdaiReflect.hs:399-403` emits every leaf as
`"#" ++ nameBase h ++ ":" ++ show v`, so `#Int:0`, `#Integer:1`, `#String:"V4"` and
`#Bool:False` are ONE rule, not four. Two consumers need it (`_insert_decoded` and
`project_sppf`'s head branch), and a second spelling is how `agda_files()` became four
bodies under one name.

⚑ `re.DOTALL`, NOT `re.S`. The alias saves four characters and costs the reader the
question "what is S" — and a `#String:` value can legitimately contain a newline, so the
flag is load-bearing rather than decorative. Spelling it out is what makes that visible.
"""

from __future__ import annotations

import re

_LEAF_RE = re.compile(r"^#(\w+):(.*)$", re.DOTALL)


def leaf_value(ctor: str | None) -> tuple[str, str] | None:
    """Return a leaf's (type, value), or None when the constructor is not a leaf."""
    m = _LEAF_RE.match(ctor or "")
    return (m.group(1), m.group(2)) if m else None


def leaf_int(ctor: str | None) -> int | None:
    """Return a leaf's value as an int when it is an `#Int:`, else None.

    ⚑ THE `isdigit` GUARD IS NOT REDUNDANT AND THE `lstrip("-")` IS WHY. A de Bruijn index
    is non-negative, but the leaf format is shared with every other `#Int:` the walker
    emits, so the parse must accept a sign to reject it honestly rather than crash on it.
    `recover_fields` spelled this inline as a condition on `clv[1]`; the type test belongs
    with the format it tests.
    """
    got = leaf_value(ctor)
    if got is None or got[0] != "Int":
        return None
    return int(got[1]) if got[1].lstrip("-").isdigit() else None
