#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render the census — three verdicts per tool, because two of them are about the READER.

⚑⚑⚑ THREE VERDICTS, NOT TWO, AND COLLAPSING THEM COST FIVE MODES FOR AS LONG AS THEY EXISTED.
`UNREADABLE BY THIS CENSUS` is a fact about the PARSER; `NO SELF-DESCRIPTION` is a fact about the
TOOL. Rendering the first as the second is what made every mode of a tool that publishes a
textbook roster read as undocumented — and it sends a reader to WRITE documentation that already
exists.

⚑⚑ SO AN UNREADABLE TOOL'S FLAGS ARE PRINTED WITH THEIR STATUS MARKED UNKNOWN, not as a gap. The
warning says so twice, because the natural reading of a flag list under a tool's name is *"these
are undocumented"* — and here it is *"this reader could not tell"*.

⚑ AND A GENUINELY SILENT TOOL IS REPORTED, NOT PATCHED. Its bare run prints something other than
a mode list, so every flag its AST carries is one no reader can see. That is the sharpest form of
the paydown census, and inventing a summary for it would be the mirror defect.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers). Rendering is separate from the census
so each verdict is assertable without capturing stdout.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import page

if TYPE_CHECKING:
    from substrate.tool_census import Tool

# What a tool's header says when the census could not read it, versus when it says nothing.
UNREADABLE = "   ⚑ UNREADABLE BY THIS CENSUS"
SILENT = "   ⚑ NO SELF-DESCRIPTION"

# Column widths.
MODE_COL = 18
SIG_COL = 22
FLAG_COL = 22
GLOSS_WIDTH = 60


def one_line(text: str, width: int) -> str:
    """Return `text` collapsed to one line, elided at `width`."""
    flat = " ".join(text.split())
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def _unreadable_rows(tool: Tool) -> list[str]:
    """Render a tool whose usage block this parser could not read.

    ⚑⚑ THE WARNING IS EXPLICIT AND REPEATED because the natural reading of a flag list under a
    tool's name is *"these are undocumented"*. Here it means *"this reader could not tell"*, and
    a reader who acts on the first will document what the tool already documents.
    """
    out = [
        f"   ⚑ COULD NOT PARSE this file's usage block: {tool.unparsed}.",
        "   This is a fact about THIS READER, not about the tool — its modes",
        "   may be fully documented. Do NOT read the flags below as a",
        "   documentation gap, and do not 'fix' the tool.",
    ]
    out.extend(
        f"     {flag:<{FLAG_COL}} (argv-anchored; documentation status UNKNOWN)"
        for flag in sorted(tool.accepted)
    )
    return out


def _silent_rows(tool: Tool) -> list[str]:
    """Render a tool that publishes no usage line at all — the sharpest paydown row."""
    out = [
        "   bare output yields NO usage line; its modes cannot be derived from it.",
        f"   {len(tool.accepted)} flag(s) its code dispatches on (argv-anchored) — the",
        "   only signal available, and no reader is told about any of them:",
    ]
    out.extend(
        f"     {flag:<{FLAG_COL}} (argv-anchored, undocumented)" for flag in sorted(tool.accepted)
    )
    return out


def _mode_rows(tool: Tool) -> list[str]:
    """Render a described tool's modes, with the layer each was found by."""
    out: list[str] = []
    for mode in sorted(tool.modes):
        rec = tool.modes[mode]
        sources = "+".join(sorted(rec.sources))
        out.append(
            f"   {mode:<{MODE_COL}} {' '.join(rec.sig):<{SIG_COL}} "
            f"[{sources}]  {one_line(rec.gloss, GLOSS_WIDTH)}"
        )
    return out


def tool_block(tool: Tool) -> list[str]:
    """Render one tool: its header, its verdict, and whatever the census could establish."""
    if tool.described:
        mark = ""
    elif tool.unparsed:
        mark = UNREADABLE
    else:
        mark = SILENT

    out = [f"\n── {tool.relpath}{mark}"]
    if tool.unparsed:
        out.extend(_unreadable_rows(tool))
    elif not tool.described:
        out.extend(_silent_rows(tool))
    else:
        out.extend(_mode_rows(tool))
    return out


def render(rows: tuple[Tool, ...], top: int = page.UNBOUNDED, skip: int = 0) -> str:
    """Return the whole census, rendered and pageable.

    ⚑ THE DENOMINATOR IS THE FULL POPULATION EVEN WHEN A PAGE IS SHOWN, because a mode count over
    a slice is a number a reader would weigh against the wrong total — and a bounded listing that
    reported its own page as the toolkit is the transport-truncation defect moved inside the tool.
    """
    slice_ = page.take(rows, top, skip)
    lines: list[str] = []
    for tool in slice_.rows:
        lines.extend(tool_block(tool))

    modes = sum(len(tool.modes) for tool in rows)
    lines.append(f"\n{modes} mode(s) across {len(rows)} tool(s).")
    tail = page.tail(slice_)
    if tail:
        lines.append(tail)
    return "\n".join(lines) + "\n"
