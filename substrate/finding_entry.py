#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render one roster entry as SOURCE TEXT, and locate where it goes.

⚑⚑⚑ THE EIGHTH DRAIN UNIT, AND IT IS A RENDERER RATHER THAN A SECOND WRITER. The reuse-search
fires here: `bib_write` already owns the write protocol — render, diff, arm the snapshot,
write, re-parse, verify — and a roster splice is an `Edit` in that protocol's sense. Building
a parallel writer would be the rival-authority defect, so this produces the two strings the
protocol needs and decides nothing about how they land.

⚑⚑⚑ A SOURCE SPLICE, NOT AN AST REWRITE, AND THE REASON IS THE READER. A four-line addition
must be a four-line diff so a reviewer reads the CHANGE rather than a reformat of the file
around it. An AST round-trip would renormalise quoting, comment placement and line breaks
across a roster whose inter-entry comments carry the provenance for every finding.

⚑⚑ DOUBLE QUOTES ON THE KEY, AND `repr` GETS THIS WRONG. `bibstruct --add` resolves a
`check=item:<key>` against the roster with a regex requiring DOUBLE quotes, because every
hand-written entry uses them. `%r` emits single quotes — so the first machine-registered
witness was the first one that regex could not see: `--register` succeeded, the key resolved
at runtime, and `--add` still refused with *"the witness must exist FIRST"*. A witness that
exists, works, and is invisible to the one reader whose refusal it has to clear.

⚑ THE NOTE STILL GOES THROUGH `repr`, PER LINE. It is agent-supplied text emitted as source,
so a quote or a backslash in it would write a file that does not parse — and that failure
lands on the NEXT reader of the roster rather than on whoever caused it.

⚑⚑ AND THE ANCHOR IS COUNTED, NEVER SEARCHED-AND-HOPED. If the terminator does not appear
exactly once the module REFUSES rather than guessing an insertion point: a splice at the wrong
offset produces a file that may still parse, which is the failure mode a diff review is least
likely to catch.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from substrate.finding_kindspec import Spec

# The line the roster's closing brace is followed by. A splice lands immediately BEFORE it.
ANCHOR = "}\n\n\ndef _bib_keys():"

# How wide a wrapped note line may run before it is broken.
WIDTH = 94

# The indent a continued note literal carries inside the roster.
CONT = "\n        "


def wrap_note(note: str, width: int = WIDTH) -> str:
    """Return the note as one or more Python string literals, `repr`-quoted per line.

    ⚑ EVERY LINE BUT THE LAST KEEPS A TRAILING SPACE, so the concatenated literals rejoin into
    the original sentence. Dropping it silently welds the last word of one line to the first of
    the next, which reads as a typo in the ledger rather than as a rendering defect.
    """
    words = note.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + len(word) + 1 > width:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    if not lines:
        return "''"
    last = len(lines) - 1
    return CONT.join(repr(line if i == last else line + " ") for i, line in enumerate(lines))


def render(key: str, spec: Spec, note: str) -> str:
    """Return the roster entry for one witness, as the source line(s) to splice.

    ⚑ THE KEY IS INTERPOLATED WITH DOUBLE QUOTES DIRECTLY rather than through `repr` — see the
    module docstring. That is safe only because the caller has already refused any key outside
    the slug alphabet, which `finding_kindspec.bad_key` owns.
    """
    if spec.builder == "_mode_undocumented":
        body = f"lambda: _mode_undocumented({CONT}{spec.tool!r}, {spec.flag!r})"
    elif spec.cmd:
        body = f"lambda: {spec.builder}({CONT}{list(spec.cmd)!r}, {wrap_note(note)})"
    else:
        body = f"lambda: {spec.builder}({CONT}{wrap_note(note)})"
    return f'    "{key}": {body},\n'


def splice(source: str, entry: str) -> tuple[str, str]:
    """Return `(new_source, "")`, or `("", refusal)` when the anchor is not unique.

    ⚑⚑ COUNTED, NOT SEARCHED. Zero anchors means the roster's shape changed under this module
    and the insertion point is unknown; several means the choice is ambiguous. Both are refusals
    rather than a guess, because a splice at the wrong offset can still PARSE — so neither the
    write protocol's round-trip nor a diff review would necessarily catch it.
    """
    found = source.count(ANCHOR)
    if found != 1:
        return "", (f"cannot locate the roster terminator ({found} occurrence(s), expected 1) — "
                    "refusing to guess an insertion point, since a splice at the wrong offset "
                    "can still parse")
    return source.replace(ANCHOR, entry + ANCHOR, 1), ""
