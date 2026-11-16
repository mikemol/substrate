#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decode a Haskell-shown string literal back to the text it represents.

Split out of `sppf_recover` because the escape grammar is its own concern — and because
it is the piece that kept faulting: a `re.sub` replacement callback is `Callable[[Any],
str]`, so the obvious lambda leaks `Any` into whatever holds it.

⚑ DECIMAL CODEPOINT ESCAPES ARE THE COMMON CASE HERE, NOT AN EDGE ONE. Agda names are
routinely non-ASCII, and Haskell's `show` renders each such character as a decimal escape.
A recovered qname left escaped joins against nothing while still LOOKING like a name —
the failure mode that reads as data rather than as a defect.
"""

from __future__ import annotations

import re

_ESC_RE = re.compile(r"\\(\d+)")

# A shown string literal is wrapped in quotes; anything shorter cannot be.
_QUOTED_MIN = 2


def _codepoint(m: re.Match[str]) -> str:
    """Return the character a decimal escape names.

    ⚑ A NAMED FUNCTION, NOT A LAMBDA, AND THAT IS WHAT THE CHECKER WAS ASKING FOR.
    `re.sub`'s replacement callback is typed `Callable[[Any], str]`, so
    `lambda m: chr(int(m.group(1)))` makes both the callable and its body `Any` — two
    findings from one expression. Declaring the parameter as `re.Match[str]` types the
    whole thing, and the fix reads better than the lambda did.
    """
    return chr(int(m.group(1)))


def unescape(s: str) -> str:
    """Strip the surrounding quotes and undo the escaping of a shown literal.

    ⚑ THE NUMERIC ESCAPE IS UNDONE BEFORE THE BACKSLASH PAIRS, and the order matters:
    collapsing doubled backslashes first would turn an escaped backslash followed by
    digits into a codepoint escape, silently producing a different character.
    """
    if len(s) >= _QUOTED_MIN and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return _ESC_RE.sub(_codepoint, s).replace('\\"', '"').replace("\\\\", "\\")
