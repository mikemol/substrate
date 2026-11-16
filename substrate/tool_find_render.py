#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Render a capability search — seven arms, one of which pages.

⚑⚑⚑ PAGING IS PER-ARM, AND THE ASYMMETRY IS THE DESIGN. Mode names, glosses, citations and
dispatches are a roster the census OWNS — a few dozen rows at most — so truncating them would hide
part of the answer to *which tool has this*. The function arm searches thousands of documented
defs and can return hundreds, which is why it alone is bounded.

⚑⚑ AND THE PAGE WAS A SILENT CAP BEFORE, WHICH IS THE DEFECT THE BOUND CLOSES. MEASURED:
`--find _sql` reported **54 hits** and printed **20**, with `… and 32 more` — a count that was
exact beside a list that was not. The notice was honest and unactionable in the same breath: it
said what was missing without offering any way to see it. A census that can name its own omission
but not remove it still reports a fact about the METHOD as if it were the whole substrate.

⚑ SO ONE `Page` DRIVES BOTH THE SLICE AND THE NOTICE. Two independent literals is exactly how a
truncation notice comes to disagree with the list above it, and `substrate.page` returns the
denominator with the rows so the footer cannot drift from what was shown.

⚑ THE UNSEARCHED FUNCTION CORPUS IS REPORTED AS UNSEARCHED, NEVER AS EMPTY. A caller that did not
pay for the docstring walk gets `(not searched)` rather than `(none)` — the same
absent-versus-unmeasured distinction the census draws one layer down, and the one that turns "no
tool does this" into a claim the search cannot support.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers). Rendering is separate from finding so
every arm is testable without capturing stdout.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import page, tool_find

if TYPE_CHECKING:
    from substrate.tool_find import Found

# How wide a gloss may be before it is elided.
GLOSS_WIDTH = 50
FUNCTION_GLOSS_WIDTH = 46
TOOL_GLOSS_WIDTH = 60

# Column widths, so the arms line up when read together.
MODE_COL = 18
PATH_COL = 28
NAME_COL = 22
FN_PATH_COL = 34
TOOL_COL = 40


@dataclass(frozen=True, slots=True)
class Scope:
    """What a search covered — the denominators a hit count needs to be readable.

    ⚑ A HIT COUNT WITH NO POPULATION IS A NUMBER A READER CANNOT WEIGH, and reporting "0 hits"
    without saying over what is the absence-as-fact shape this census exists to refuse.

    ⚑ `searched` IS SEPARATE FROM `functions == 0`. A corpus nobody walked and a corpus with
    nothing in it are different facts, and only the second is about the tree.

    ⚑⚑ A SLOTTED DATACLASS, NOT `NamedTuple` (⟡symbolic-reference-only). Four ints and a bool in a
    `tuple` subclass is the worst case for positional access: `tools, modes, functions = scope`
    type-checks, reads plausibly, and silently rebinds if a field is inserted. Without `tp_iter`
    or the sequence protocol that site is a static error instead.
    """

    tools: int
    modes: int
    functions: int
    searched: bool = True


def one_line(text: str, width: int) -> str:
    """Return `text` collapsed to one line, elided at `width`."""
    flat = " ".join(text.split())
    return flat if len(flat) <= width else flat[: width - 1] + "…"


def _mode_rows(found: Found) -> list[str]:
    """Render the by-name arm, and the tools that LACK the mode."""
    out = [f"── by MODE NAME containing {found.needle.lstrip('-').lower()!r}"]
    out.extend(
        f"   {hit.mode:<{MODE_COL}} on {hit.relpath:<{PATH_COL}} "
        f"[{'+'.join(sorted(hit.sources))}]  {one_line(hit.gloss, GLOSS_WIDTH)}"
        for hit in found.by_mode
    )
    if not found.by_mode:
        out.append("   (none)")
    elif found.lacking:
        # ⚑ THE ACTIONABLE HALF. "`--grep` exists" was never the question; "it is not on the tool
        # I just typed" was, in five recorded misses.
        out.append(f"   ⚑ NOT on: {', '.join(found.lacking)}")
    else:
        out.append("   ⚑ NOT on: (every tool has it)")
    return out


def _gloss_rows(found: Found) -> list[str]:
    """Render the by-gloss arm — the mode you MEANT may be named differently."""
    key = found.needle.lstrip("-").lower()
    out = [f"\n── by GLOSS mentioning {key!r}  (the mode you MEANT may be named differently)"]
    out.extend(
        f"   {hit.mode:<{MODE_COL}} on {hit.relpath:<{PATH_COL}} {one_line(hit.gloss, GLOSS_WIDTH)}"
        for hit in found.by_gloss
    )
    if not found.by_gloss:
        out.append("   (none)")
    return out


def _mention_rows(found: Found) -> list[str]:
    """Render the citation and prose arms — a third verdict, in its own section.

    ⚑⚑ FOLDING CITATIONS INTO THE BLOCK BELOW made a correct cross-reference read as debt, and the
    paydown that follows deletes the cross-discoverability the standing rule requires.
    """
    out: list[str] = []
    if found.cited:
        out.append("\n── CITED  (this tool NAMES a mode another tool DECLARES — not a gap)")
        for hit in found.cited:
            cite = hit.citation
            owners = ", ".join(cite.owners) if cite else ""
            mark = "" if cite and cite.witnessed else "   ⚑ owner not named on the citing line"
            out.append(
                f"   {hit.flag:<{MODE_COL}} named in {hit.relpath}, declared by {owners}{mark}"
            )

    out.append("\n── NAMED but not declared  (prose mention / undocumented dispatch)")
    out.extend(
        f"   {hit.flag:<{MODE_COL}} named in {hit.relpath}'s own output, declared by NO tool"
        for hit in found.prose
    )
    out.extend(
        f"   {flag:<{MODE_COL}} dispatched by {relpath}, in no usage line — UNDOCUMENTED"
        for relpath, flag in found.dispatched
    )
    if not found.prose and not found.dispatched:
        out.append("   (none)")
    return out


def _function_rows(found: Found, top: int | None, scope: Scope) -> list[str]:
    """Render the function arm — the only paged one.

    ⚑ THE NOTICE NAMES ITS OWN REMEDY. A truncation saying only "N more" tells a reader the list
    is incomplete and leaves them to guess how to complete it — which sent one caller to a flag
    that did not exist and then to reading the file by hand.
    """
    out = ["\n── by FUNCTION  (a capability may be a library function, not a mode)"]
    if not scope.searched:
        # ⚑ UNSEARCHED IS NOT EMPTY. A caller that did not pay for the docstring walk must not be
        # told the capability is absent.
        out.append("   (not searched — no function corpus was supplied)")
        return out

    bound = tool_find.FUNCTION_PAGE if top is None else top
    slice_ = page.take(found.functions, bound)
    out.extend(
        f"   {hit.name:<{NAME_COL}} in {hit.relpath:<{FN_PATH_COL}} "
        f"[{hit.why}]  {one_line(hit.gloss, FUNCTION_GLOSS_WIDTH)}"
        for hit in slice_.rows
    )
    if not found.functions:
        out.append("   (none)")
    elif slice_.remaining:
        out.append(f"   … and {slice_.remaining} more — `--find {found.needle} --top 0` for all")
    return out


def _tool_rows(found: Found) -> list[str]:
    """Render the by-tool arm — the tool ITSELF, not a mode or function inside it."""
    out = ["\n── by TOOL  (the tool ITSELF, not a mode or function inside one)"]
    out.extend(
        f"   {hit.relpath:<{TOOL_COL}} [{hit.why}]  {one_line(hit.gloss, TOOL_GLOSS_WIDTH)}"
        for hit in found.tools
    )
    if not found.tools:
        out.append("   (none)")
    return out


def render(found: Found, scope: Scope, top: int | None = None) -> str:
    """Return the whole search, rendered."""
    lines = [
        *_mode_rows(found),
        *_gloss_rows(found),
        *_mention_rows(found),
        *_function_rows(found, top, scope),
        *_tool_rows(found),
    ]
    lines.append(
        f"\n{found.hits} hit(s) for {found.needle!r}; {scope.modes} declared mode(s) + "
        f"{scope.functions} documented function(s) over {scope.tools} tool(s)"
    )
    return "\n".join(lines) + "\n"
