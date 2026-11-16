#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""WHICH TOOL has this capability — seven arms, each added because a search missed something.

⚑⚑⚑ EVERY ARM IS A RECORDED MISS, NOT A DESIGN. The mode arm was the original; the other six
exist because a real search returned nothing while the capability sat in the tree:

  by MODE NAME    the original, and the `⚑ NOT on:` line beside it — *"`--grep` exists"* was
                  never the problem; *"it is not on the tool I just typed"* was
  by GLOSS        the mode you MEANT may be named differently
  CITED           ⚑ a tool NAMING another's mode is the REMEDY, not a gap; folding it into the
                  block below made a correct cross-reference read as debt
  NAMED-not-declared   prose mentions and undocumented dispatches, which are different kinds
  by FUNCTION     a capability implemented as a library function and never exposed as a mode was
                  invisible to all three arms above — `literal_flags` is the measured instance
  by TOOL         ⚑⚑ THE FAMILY-SCALE INSTANCE OF THIS MODE'S OWN DEFECT: every other arm
                  searches INSIDE a tool, so a file-level entry point was unreachable from the
                  census built to make capabilities reachable

⚑⚑ THE `by TOOL` MISS IS WORTH ITS OWN SENTENCE. `--find telescope` returned four LIBRARY
FUNCTIONS while `split_telescoped.py` — the tool that performs the operation — appeared nowhere;
`--find split_telescoped` returned **0 hits for the tool's own name**. A reader asking *"how do I
split a telescoped module"* was answered with a function list. That is a fact about the METHOD
reported as a fact about the toolkit.

⚑⚑ AND THE ATTRIBUTION SPLIT WAS A DISAGREEMENT INSIDE ONE RUN. The prose arm read mentions alone
and printed *"declared by NO tool"* while the mode arm, reading the same index, printed the
declarer — so one invocation said `agda_defs` declares `--telescope` AND that nothing declares it.
The fix was to SHARE the predicate, never to add a second copy.

⚑ PAGING IS PER-ARM AND ONLY THE FUNCTION ARM TAKES IT. Mode names, glosses and dispatches are a
roster the census OWNS — a few dozen at most — so truncating them hides part of the answer to
*which tool has this*. The function arm searches thousands of documented defs and can return
hundreds. `substrate.page` drives both the slice and the notice from ONE page, because two
independent literals is exactly how a truncation notice comes to disagree with the list above it.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by the
per-file gate. This module FINDS; rendering is the caller's, so every arm is testable without
capturing stdout.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from substrate import tool_decline, tool_similarity

if TYPE_CHECKING:
    from substrate.tool_census import Tool

# How many function rows a search shows before paging. ⚑ NOT UNBOUNDED: this arm alone can return
# hundreds, and a wall is what sent a reader to read the file by hand.
FUNCTION_PAGE = 20

# Shared content words needed to call two glosses related. ⚑ TWO, because one shared word pairs
# almost anything; the origin measured its own motivating case at exactly two under stemming.
SHARED = 2


class ModeHit(NamedTuple):
    """A declared mode matching the needle, and where it lives."""

    mode: str
    relpath: str
    gloss: str
    sources: frozenset[str]


class MentionHit(NamedTuple):
    """A flag a tool NAMES — either citing another's mode, or naming nothing declared."""

    relpath: str
    flag: str
    citation: tool_decline.Citation | None

    @property
    def cited(self) -> bool:
        """Report whether this mention resolves to a declaring tool."""
        return self.citation is not None


class FunctionHit(NamedTuple):
    """A library function whose name or gloss matches — a capability with no mode."""

    relpath: str
    name: str
    gloss: str
    why: str


class ToolHit(NamedTuple):
    """A tool matched as a WHOLE — by its own name, or by its self-description."""

    relpath: str
    stem: str
    gloss: str
    why: str


class Found(NamedTuple):
    """Everything a search returns, by arm."""

    needle: str
    by_mode: tuple[ModeHit, ...]
    lacking: tuple[str, ...]
    by_gloss: tuple[ModeHit, ...]
    cited: tuple[MentionHit, ...]
    prose: tuple[MentionHit, ...]
    dispatched: tuple[tuple[str, str], ...]
    functions: tuple[FunctionHit, ...]
    tools: tuple[ToolHit, ...]

    @property
    def hits(self) -> int:
        """Return how many rows this search produced, across every arm."""
        return (
            len(self.by_mode)
            + len(self.by_gloss)
            + len(self.cited)
            + len(self.prose)
            + len(self.dispatched)
            + len(self.functions)
            + len(self.tools)
        )


def _key(needle: str) -> str:
    """Return the comparison key — a needle with its leading dashes and case removed."""
    return needle.lstrip("-").lower()


def _by_mode(rows: tuple[Tool, ...], key: str) -> tuple[tuple[ModeHit, ...], tuple[str, ...]]:
    """Return matching modes and the tools that LACK them.

    ⚑ THE SECOND HALF IS THE ACTIONABLE ONE. Naming the tools without the mode is what turns
    *"`--grep` exists"* into *"…but not on the tool you just typed"*, which was the operator's
    actual question in five recorded misses.
    """
    hits = tuple(
        sorted(
            ModeHit(mode=mode, relpath=tool.relpath, gloss=rec.gloss, sources=rec.sources)
            for tool in rows
            for mode, rec in tool.modes.items()
            if key in mode.lstrip("-").lower()
        )
    )
    owners = {hit.relpath for hit in hits}
    lacking = tuple(tool.relpath for tool in rows if tool.relpath not in owners) if hits else ()
    return hits, lacking


def _by_gloss(rows: tuple[Tool, ...], key: str) -> tuple[ModeHit, ...]:
    """Return modes whose GLOSS matches while their name does not."""
    return tuple(
        sorted(
            ModeHit(mode=mode, relpath=tool.relpath, gloss=rec.gloss, sources=rec.sources)
            for tool in rows
            for mode, rec in tool.modes.items()
            if key in rec.gloss.lower() and key not in mode.lower()
        )
    )


def _mentions(
    rows: tuple[Tool, ...],
    key: str,
    cites: dict[tuple[str, str], tool_decline.Citation],
) -> tuple[tuple[MentionHit, ...], tuple[MentionHit, ...]]:
    """Return `(cited, prose)` — mentions that resolve to a declarer, and those that do not.

    ⚑⚑ THE SPLIT IS THE WHOLE POINT. A tool naming a sibling's mode is cross-discoverability, and
    reporting it under *"declared by NO tool"* drives a paydown that DELETES the reference.
    """
    cited: list[MentionHit] = []
    prose: list[MentionHit] = []
    for tool in rows:
        for flag in sorted(tool.mentioned):
            if key not in flag.lstrip("-").lower():
                continue
            hit = MentionHit(
                relpath=tool.relpath, flag=flag, citation=cites.get((tool.relpath, flag))
            )
            (cited if hit.cited else prose).append(hit)
    return tuple(sorted(cited)), tuple(sorted(prose))


def _dispatched(rows: tuple[Tool, ...], key: str) -> tuple[tuple[str, str], ...]:
    """Return flags a tool ACCEPTS but declares in no usage line — undocumented capability."""
    return tuple(
        sorted(
            (tool.relpath, flag)
            for tool in rows
            for flag in tool.accepted
            if key in flag.lstrip("-").lower() and flag not in tool.modes
        )
    )


def _by_function(
    glosses: tuple[tuple[str, str, str], ...],
    key: str,
    want: frozenset[str],
    stems: tuple[str, ...],
) -> tuple[FunctionHit, ...]:
    """Return functions matching by NAME substring, then by stemmed gloss overlap.

    ⚑ NAME FIRST, THEN MEANING, AND NEITHER ALONE. A searcher who knows what the thing is CALLED
    and one who knows what it DOES are different readers; the second is why `literal_flags` got
    reinvented as `cli_flags` while a name-only search reported nothing.
    """
    out: list[FunctionHit] = []
    seen: set[tuple[str, str]] = set()
    for relpath, name, gloss in glosses:
        if key in name.lstrip("_").lower():
            out.append(FunctionHit(relpath=relpath, name=name, gloss=gloss, why="name"))
            seen.add((relpath, name))

    for relpath, name, gloss in glosses:
        if (relpath, name) in seen:
            continue
        shared = want & tool_similarity.tokens(gloss, stems)
        if len(shared) >= SHARED or (len(want) == 1 and shared):
            out.append(
                FunctionHit(relpath=relpath, name=name, gloss=gloss, why="+".join(sorted(shared)))
            )
    return tuple(out)


def _by_tool(
    rows: tuple[Tool, ...], key: str, want: frozenset[str], stems: tuple[str, ...]
) -> tuple[ToolHit, ...]:
    """Return tools matched as a WHOLE — by their own name, or by their self-description.

    ⚑⚑ THE MATCH READS THE WHOLE DOCSTRING; A DISPLAY SHOWS ITS FIRST LINE. Matching line one
    only reproduced the defect one notch in: a tool whose opening sentence states its MECHANISM
    rather than its OCCASION stayed unreachable. A one-line window is a curated summary the tool
    never agreed to write.

    ⚑ AND THE WINDOW STOPS AT THE DOCSTRING. A raw source slice reaches into CODE, where
    identifiers match incidentally and a tool's imports read as its subject.
    """
    out: list[ToolHit] = []
    for tool in rows:
        stem = tool.relpath.rsplit("/", 1)[-1].removesuffix(".py")
        body = _docstring(tool.source)
        why = None
        if key in stem.lower():
            why = "name"
        else:
            shared = want & tool_similarity.tokens(body, stems)
            if len(shared) >= SHARED or (len(want) == 1 and shared):
                why = "+".join(sorted(shared))
        if why:
            out.append(ToolHit(relpath=tool.relpath, stem=stem, gloss=body, why=why))
    return tuple(sorted(out))


def _docstring(source: str) -> str:
    """Return a module's docstring text, or "" — the tool's own curated self-description."""
    body = source.lstrip()
    for opener in ('"""', "'''"):
        if body.startswith(("r" + opener, opener)):
            start = body.index(opener) + len(opener)
            end = body.find(opener, start)
            return body[start:end] if end > 0 else body[start:]
    return ""


def find(
    rows: tuple[Tool, ...], needle: str, glosses: tuple[tuple[str, str, str], ...] = ()
) -> Found:
    """Return every arm's answer for one needle.

    ⚑ THE FUNCTION CORPUS IS AN ARGUMENT because reading every top-level docstring in the tree is
    the expensive half, and a caller asking only about modes should not pay for it. Passing
    nothing yields no function hits — which the renderer must report as UNSEARCHED rather than as
    an absence.
    """
    key = _key(needle)
    stems = tuple(tool.relpath.rsplit("/", 1)[-1] for tool in rows)
    want = tool_similarity.tokens(needle, stems) or frozenset({tool_similarity.stem(key)})

    by_mode, lacking = _by_mode(rows, key)
    cited, prose = _mentions(rows, key, tool_decline.citations(rows))

    return Found(
        needle=needle,
        by_mode=by_mode,
        lacking=lacking,
        by_gloss=_by_gloss(rows, key),
        cited=cited,
        prose=prose,
        dispatched=_dispatched(rows, key),
        functions=_by_function(glosses, key, want, stems),
        tools=_by_tool(rows, key, want, stems),
    )
