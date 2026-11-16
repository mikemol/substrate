#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Splice a generated census into a marked region of a document — content only, never placement.

⚑⚑⚑ MISSING MARKERS ARE A REFUSAL, NOT AN INSERTION, AND THE CHOICE IS LOAD-BEARING. A sync owns
the block's CONTENT; it does not own its PLACEMENT. A tool that inserted would append dozens of
lines wherever it happened to reach — with none of the prose that introduces them — and, worse,
would silently restore a block a human had deliberately removed, so *"delete the block"* would be
an instruction nothing could carry out. Refusing names the remedy and leaves the editorial
decision with the editor.

⚑⚑ IT ALSO KEEPS THE DRIFT GATE HONEST. Absent markers are DRIFT, reported as absent rather than
repaired into a pass — which is the difference between a gate that measures a document and one
that edits it until it agrees.

⚑⚑⚑ AND NO RENDERED LINE MAY BEGIN WITH `|` — THAT IS CORRECTNESS, NOT STYLE. The population
reader parses every `|`-leading line of the routing document as an `artifact | tool` row, so a
markdown table inside the block would feed a sync's OUTPUT back into its INPUT: phantom tools in
the roster, a PreToolUse gate armed for artifacts nothing claims, and a sync that never reaches a
fixed point. A fenced code block is the shape that cannot do that, pinned by a case rather than by
anyone remembering.

⚑ EVERY BYTE OUTSIDE THE MARKERS IS PRESERVED, and the markers themselves are part of what is
preserved: only the region strictly between them is rewritten, so a sync cannot move, duplicate or
reformat them.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers). This module SPLICES; what goes in the
block is the caller's.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

# How wide a wrapped line may be before it is broken.
WIDTH = 96

# ⚑ THE CHARACTER A RENDERED LINE MAY NEVER LEAD WITH — see the module note. A table row here is
# read as a routing declaration by the very reader this census feeds.
FORBIDDEN_LEAD = "|"


class BlockError(Exception):
    """The markers are missing or malformed — a PLACEMENT question, not a content one."""


@dataclass(frozen=True, slots=True)
class Markers:
    """The pair that delimits a generated region, and the document they live in."""

    begin: str
    end: str
    where: str


def wrap(items: Iterable[str], indent: str, width: int = WIDTH) -> list[str]:
    """Return `items` packed onto as few lines as fit, each prefixed with `indent`."""
    lines: list[str] = []
    current = ""
    for item in items:
        if current and len(indent) + len(current) + 1 + len(item) > width:
            lines.append(indent + current)
            current = item
        else:
            current = (current + " " + item) if current else item
    if current:
        lines.append(indent + current)
    return lines


def leads_forbidden(body: str) -> tuple[str, ...]:
    """Return any rendered lines that would be read back as routing declarations.

    ⚑⚑ THE SELF-REFERENCE IS THE HAZARD. The population reader treats a `|`-leading line as an
    `artifact | tool` row, and it reads the same document this block is spliced into — so a
    markdown table in the body makes a sync's output its own input. Checking is cheap; noticing
    the loop after it has run is not.
    """
    return tuple(line for line in body.splitlines() if line.lstrip().startswith(FORBIDDEN_LEAD))


def span(src: str, markers: Markers) -> tuple[int, int]:
    """Return `(body_start, body_end)` for the marked region, or refuse with a named remedy.

    ⚑ EACH REFUSAL NAMES WHAT TO DO, because the three failures want different repairs: add the
    markers, remove the duplicates, or un-invert them. A single "malformed block" message would
    make the reader diff the file to find out which.
    """
    begin, end = src.find(markers.begin), src.find(markers.end)
    if begin < 0 or end < 0:
        msg = (
            f"no `{markers.begin}` … `{markers.end}` pair in {markers.where} — add the two "
            "marker lines where the block belongs; a sync fills between them but will not "
            "choose their place."
        )
        raise BlockError(msg)
    if src.count(markers.begin) != 1 or src.count(markers.end) != 1:
        msg = (
            f"{markers.where} carries {src.count(markers.begin)} `{markers.begin}` and "
            f"{src.count(markers.end)} `{markers.end}` marker(s); exactly one of each is "
            "required — a sync cannot know which pair it owns."
        )
        raise BlockError(msg)
    if end < begin + len(markers.begin):
        msg = (
            f"`{markers.end}` precedes `{markers.begin}` in {markers.where} — the markers "
            "are inverted."
        )
        raise BlockError(msg)
    return begin + len(markers.begin), end


def splice(src: str, body: str, markers: Markers) -> str:
    """Return `src` with the marked region's body replaced, every other byte preserved."""
    start, end = span(src, markers)
    return src[:start] + "\n" + body + "\n" + src[end:]


def current_body(src: str, markers: Markers) -> str:
    """Return the block's body exactly as it sits on disk, including its framing newlines."""
    start, end = span(src, markers)
    return src[start:end]


def is_current(src: str, body: str, markers: Markers) -> bool:
    """Report whether the document already carries exactly this body.

    ⚑ COMPARED THROUGH `splice`, NOT BY DIFFING THE BODIES. The framing newlines belong to the
    splice rather than to the body, so comparing bodies directly reports drift on a document that
    is byte-identical to what a sync would write — a gate failing over its own formatting.
    """
    return splice(src, body, markers) == src
