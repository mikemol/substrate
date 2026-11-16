#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Locate a module-level dict literal's closing brace by PARSING, never by its neighbour.

⚑⚑⚑ WHY THIS EXISTS (Ⓝ137-prime ⟡findings-drain, step 2). The findings ledger appends to its
own `WITNESSES` roster by splicing source text, and it finds the insertion point with a
literal anchor made of a closing brace, two blank lines, and the NEXT DEFINITION'S `def`
line. That anchor is a source-text dependency between a writer and whatever happens to
follow it, invisible to every import-graph and call-graph reader — `pycodemod --literal`
finds exactly one site for that def line, and it is the anchor string itself.

⚑⚑ THE CONSEQUENCE IS AN ORDERING CONSTRAINT NOBODY DECLARED. Reordering the module, renaming
the following function, or moving the roster to its own file all break the write path — and
two of those are exactly what a drain does. So the roster cannot move until the writer stops
naming its neighbour, which inverts the usual drain order (extract units, then swap).

⚑ WHAT THIS REPLACES IT WITH IS A PARSE, AND THE PARSE ANSWERS A QUESTION THE ANCHOR ONLY
APPROXIMATED. `ast` gives a module-level assignment's end position directly, so the closing
brace is located by the grammar rather than by a guess about what follows. A roster that
moves, gets renamed around, or ends the file entirely is still found.

⚑⚑⚑ AND IT KEEPS THE ORIGIN'S MOST IMPORTANT PROPERTY: REFUSE RATHER THAN GUESS. The origin
checks that its anchor occurs exactly once and refuses on zero or many, because a
half-written roster is unimportable and a misplaced entry still PARSES — a wrong insertion
point produces a valid file with an entry in the wrong dict, which no syntax check catches.
Every failure here returns a REASON, never a fallback offset.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass


@dataclass(frozen=True)
class Extent:
    """Byte offsets of a dict literal's braces within the source it was parsed from."""

    open_at: int
    close_at: int


@dataclass(frozen=True)
class NotFound:
    """Why the extent could not be established. Never a fallback — always a reason."""

    reason: str


def _offsets(src: str) -> list[int]:
    """Return the byte offset at which each 1-indexed line starts."""
    starts, at = [0], 0
    for line in src.splitlines(keepends=True):
        at += len(line)
        starts.append(at)
    return starts


def _assignments(tree: ast.Module, name: str) -> list[ast.Assign]:
    """Return every MODULE-LEVEL assignment binding `name` to a dict literal.

    ⚑ MODULE LEVEL ONLY, DELIBERATELY. A same-named dict inside a function is a different
    object, and splicing into it would put an entry somewhere no reader looks. Walking the
    whole tree would find it and report an ambiguity that does not exist at this level.
    """
    out: list[ast.Assign] = []
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.Dict):
            continue
        for tgt in node.targets:
            if isinstance(tgt, ast.Name) and tgt.id == name:
                out.append(node)
                break
    return out


def find(src: str, name: str) -> Extent | NotFound:
    """Return the braces of the module-level dict bound to `name`, or why not.

    ⚑ AMBIGUITY IS REFUSED, NOT RESOLVED. Two module-level bindings of one name means the
    later one wins at runtime, but picking it here would silently choose which roster a
    write lands in — the origin's exactly-once guard, kept.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return NotFound(f"the source does not parse, so no extent is knowable: {e}")

    found = _assignments(tree, name)
    if not found:
        return NotFound(
            f"no MODULE-LEVEL assignment binds {name!r} to a dict literal — refusing to "
            "guess an insertion point",
        )
    if len(found) > 1:
        lines = ", ".join(str(n.lineno) for n in found)
        return NotFound(
            f"{len(found)} module-level assignments bind {name!r} to a dict (lines {lines}) "
            "— refusing to choose which roster a write lands in",
        )

    node = found[0].value
    if node.end_lineno is None or node.end_col_offset is None:
        return NotFound(f"the parser gave {name!r} no end position")

    starts = _offsets(src)
    open_at = starts[node.lineno - 1] + node.col_offset
    close_at = starts[node.end_lineno - 1] + node.end_col_offset - 1
    if src[open_at] != "{" or src[close_at] != "}":
        return NotFound(
            f"the computed extent for {name!r} does not land on braces "
            f"({src[open_at]!r}..{src[close_at]!r}) — refusing a guessed offset",
        )
    return Extent(open_at, close_at)


def splice(src: str, name: str, entry: str) -> tuple[str, str | None]:
    """Return (new_source, None) with `entry` inserted before the dict's closing brace.

    On failure returns (src, reason) — the source UNCHANGED, so a caller that ignores the
    reason writes nothing rather than writing something wrong.

    ⚑ THE ENTRY LANDS BEFORE THE BRACE, WHICH IS WHERE THE ORIGIN PUTS IT. Appending after
    the last existing entry would require knowing where that is, and a dict whose final
    entry is followed by a comment would then take the insertion in the wrong place.
    """
    got = find(src, name)
    if isinstance(got, NotFound):
        return src, got.reason
    return src[: got.close_at] + entry + src[got.close_at :], None
