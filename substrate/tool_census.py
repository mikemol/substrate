#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The whole derived picture — one record per tool, assembled from the reading layers.

⚑⚑⚑ `described == False` IS TWO OPPOSITE FACTS UNDER ONE NAME, AND SEPARATING THEM IS THIS
LAYER'S REASON TO EXIST. A tool that PUBLISHES NOTHING and a tool whose publication THIS PARSER
COULD NOT READ render identically — and only the first is a fact about the substrate. The second
is a fact about the METHOD, and it is the one that must name its own successor.

⚑⚑ MEASURED, AND IT IS WHY THE `unparsed` FIELD EXISTS: `scripts/gate_census.py` published a
five-row `modes:` roster and read as UNDOCUMENTED on every one, because the header alternation
spelled only argparse's two. **The reader that noticed was a human agent comparing a new mode
against its four siblings** — nothing in the census could say *"I failed to parse this"*. Now it
can, and it names the alternation to widen rather than extracting the modes itself: a detector
that quietly succeeded where the parser failed would give the census two answers for one file.

⚑ THE COLLAPSE THIS TOOLKIT HAS NOW FIXED THREE TIMES — ABSENT-vs-EMPTY in `gate_census`,
*"no consumer found"* vs *"no consumer exists"* in the standing rule, and `--calls emit` missing
`_emit_one`. Each was one predicate answering two questions.

⚑ THERE IS NO FALLBACK ROSTER, DELIBERATELY. A tool whose source yields no usage line has NO
SELF-DESCRIPTION, reported as such. Falling back to a hand-written list is the defect this whole
census exists to prevent.

⚑ AND `sources` RECORDS WHICH LAYER FOUND EACH MODE, which is what makes a divergence readable:
a mode declared in a usage line carries a SIGNATURE, one found only in an option roster carries a
gloss, and one backed by dispatch but declared nowhere is the paydown census. Collapsing them
into a bare set would leave a reader unable to tell what kind of gap they are looking at.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by the
per-file gate. The cut continues until the dispatch moves out and the original is retired.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate import tool_declaration, tool_dispatch, tool_population, tool_usage

if TYPE_CHECKING:
    from pathlib import Path

# Where a mode was found. ⚑ A USAGE LINE CARRIES A SIGNATURE; AN OPTION ROW CARRIES ONLY A GLOSS.
USAGE = "usage"
OPTLIST = "optlist"

# A header that INTRODUCES a roster this parser declined. ⚑ READ AS EVIDENCE, NEVER AS A ROSTER:
# matching it says "there is a block here the parser could not read", which is exactly the claim
# `unparsed` makes and no more.
ROSTERISH = re.compile(r"^\s{0,4}([A-Za-z][A-Za-z ]{0,24}):\s*$")

# An indented row that leads with a flag — the shape a roster's body has.
ROSTER_ROW = re.compile(r"^\s+--[A-Za-z]")

# How many such rows make a roster rather than a stray line.
MIN_ROSTER_ROWS = 2


@dataclass(frozen=True, slots=True)
class Mode:
    """One mode a tool declares, and which reading layer found it."""

    gloss: str
    sig: tuple[str, ...]
    sources: frozenset[str]


@dataclass(frozen=True, slots=True)
class Tool:
    """Everything the census derives about one tool."""

    relpath: str
    modes: dict[str, Mode]
    options: frozenset[str]
    mentioned: frozenset[str]
    accepted: frozenset[str]
    literals: frozenset[str]
    unparsed: str
    source: str

    @property
    def described(self) -> bool:
        """Report whether this tool publishes any mode at all.

        ⚑ FALSE HERE IS NOT A VERDICT ON ITS OWN — read it beside `unparsed`, which says whether
        the silence is the tool's or this reader's.
        """
        return bool(self.modes)

    @property
    def undocumented(self) -> frozenset[str]:
        """Return flags the tool DISPATCHES but does not declare — the paydown census."""
        return self.accepted - set(self.modes) - self.options

    @property
    def unbacked(self) -> frozenset[str]:
        """Return flags the tool DECLARES but no dispatch reaches."""
        return frozenset(self.modes) - self.accepted


def unparsed_roster(text: str) -> str:
    """Return a witness that this text carries mode rows the parser could not read, or "".

    ⚑⚑ THE WHOLE POINT IS THE DISTINCTION, NOT THE DETECTION. A false UNDOCUMENTED and a true one
    are indistinguishable to a reader, and the false one sends them to WRITE documentation that
    already exists.

    ⚑ EVIDENCE, NOT INFERENCE. A witness is returned only when the text contains BOTH a
    header-shaped line AND, under it, at least two indented flag rows — a two-column roster in
    every respect except the one word this parser happened to recognise. Absent that, "" is
    returned and the tool keeps its honest NO SELF-DESCRIPTION: a tool whose bare run prints a
    selftest genuinely publishes nothing, and inventing an excuse for it is the mirror defect.

    ⚑ AND IT IS DELIBERATELY NOT A SECOND PARSER. It does not extract the modes — it reports that
    extraction FAILED and names the header it choked on, so the fix lands in one alternation
    rather than accreting a parallel reader whose output could disagree with the real one.
    """
    lines = text.splitlines()
    for at, line in enumerate(lines):
        found = ROSTERISH.match(line)
        if not found or tool_declaration.OPTIONS_HEADS.match(line.strip()):
            continue
        rows = 0
        for nxt in lines[at + 1 :]:
            if not nxt.strip():
                break
            if tool_declaration.OPTION_ROW.match(nxt.rstrip()) or ROSTER_ROW.match(nxt):
                rows += 1
            elif not nxt.startswith(" "):
                break
        if rows >= MIN_ROSTER_ROWS:
            return (
                f"a `{found.group(1)}` block with {rows} `--flag` row(s) — a roster this "
                "parser does not recognise (widen the header alternation)"
            )
    return ""


def _modes_with_sources(text: str, stem: str) -> dict[str, Mode]:
    """Return every declared mode, tagged with the layer that found it.

    ⚑ A MODE FOUND BY BOTH CARRIES BOTH, and its glosses are joined. The usage line supplies the
    signature; the option row often supplies the wording a human wrote for `--help`, and keeping
    only one loses half of what the tool says about itself.
    """
    out: dict[str, Mode] = {}
    for name, mode in tool_usage.parse_usage(text, stem).items():
        out[name] = Mode(gloss=mode.gloss, sig=mode.sig, sources=frozenset({USAGE}))

    for flag, gloss in tool_declaration.parse_options(text).items():
        prev = out.get(flag)
        if prev is None:
            out[flag] = Mode(gloss=gloss, sig=(), sources=frozenset({OPTLIST}))
            continue
        merged = prev.gloss
        if gloss and gloss not in prev.gloss:
            merged = (prev.gloss + " | " + gloss).strip(" |")
        out[flag] = Mode(gloss=merged, sig=prev.sig, sources=prev.sources | {OPTLIST})
    return out


def read_tool(path: Path, source: str, peers: frozenset[str], root: Path | None = None) -> Tool:
    """Return the census record for one tool.

    ⚑ THE SOURCE IS PASSED IN, NOT RE-READ. The population already read it to decide this file is
    a tool, and a second read is where two readers start disagreeing about what one file contains.

    ⚑⚑ AND THE ROOT TRAVELS WITH IT, WHICH IT DID NOT ON THE FIRST CUT. `census(root)` accepts a
    root and this computed relpaths against the CORPUS root regardless, so a census over any other
    tree returned absolute paths — and every key derived from a relpath (the citation map, the
    inverted index) silently stopped matching. Caught by three fixture arms at once, which is the
    only reason it did not reach the live census as a subtle join failure: there, the two roots
    happen to be the same.
    """
    stem = path.name
    text = tool_declaration.self_description(source)
    modes = _modes_with_sources(text, stem)
    options = frozenset(tool_usage.bracketed_options(text, stem))
    flags = tool_dispatch.flags_of(path, peers)

    return Tool(
        relpath=tool_population.relative(path, root),
        modes=modes,
        options=options,
        # ⚑ NAMED IN THE TEXT BUT DECLARED BY NEITHER READER — a prose mention, not a mode.
        mentioned=frozenset(tool_usage.flags_in(text)) - set(modes) - options,
        accepted=flags.accepted,
        literals=flags.literals,
        unparsed=unparsed_roster(text) if not modes else "",
        source=source,
    )


def publishes(source: str, stem: str) -> bool:
    """Report whether a module publishes at least one usage line — the admission test.

    ⚑⚑⚑ THE TEST READS THE RAW SOURCE, NOT THE SELF-DESCRIPTION, AND THE ASYMMETRY IS THE WHOLE
    POINT. A module is ADMITTED when a usage line exists anywhere in its text; what it then
    DECLARES is read from its docstring, constants, prints and argparse. Those are different
    questions and the gap between them is a finding: MEASURED on four tools — `store.py`,
    `check_indented_imports.py`, `sppf_node_index.py`, `sppf_query.py` — all four are censused
    and all four declare nothing, because their usage line sits somewhere the declaration reader
    does not look.

    ⚑⚑ AND CONFLATING THEM COSTS IN THE DANGEROUS DIRECTION. Admitting on the narrow read drops
    those four from the census entirely, which turns "this tool declares nothing — that is the
    paydown" into "this tool does not exist". A census that excludes what it cannot yet see well
    reports the boundary of its own coverage as the boundary of the toolkit.

    ⚑ ONE PUBLISHED MODE IS THE BAR, INCLUDING `(positional)`. The origin records setting it at
    two and watching the population fall 74 → 9, then calling the excluded 40 *"noise"* — they
    were the paydown census. A script whose whole interface is "give me a path" still SHARES that
    interface with sixteen others, and reporting so is the convergence finding.
    """
    return bool(tool_usage.parse_usage(source, stem))


def census(root: Path | None = None, *, publishing_only: bool = True) -> tuple[Tool, ...]:
    """Return the record for every tool, in a stable order.

    ⚑⚑⚑ THE POPULATION IS "RUNS **AND** PUBLISHES", AND I DROPPED THE SECOND HALF ON THE FIRST
    CUT. `tool_population.executables` answers *which files RUN*; the census asks *which files
    are TOOLS*. Integration parity caught it: 436 rows against the origin's 98.

    ⚑⚑ THE ORIGIN ARGUES BOTH SIDES, WHICH IS WHY THE FIRST CUT LOOKED RIGHT. It records the bar
    at TWO modes shrinking the population 74 → 9 and concludes under-admitting is dangerous —
    an argument about the bar's HEIGHT, not about dropping the predicate. Widening a population
    and deleting its condition are different moves, and only the first was intended.

    ⚑⚑ AND THE SECOND CUT FAILED IN THE OPPOSITE DIRECTION, which is what `publishes` fixes.
    Filtering on what a tool DECLARES rather than on what it PUBLISHES lost four tools that are
    censused with zero modes — the sharpest paydown rows in the census, dropped for being what
    the census exists to surface.

    ⚑ `publishing_only=False` KEEPS THE WIDER READING, because "runs but publishes nothing" is a
    real question. It is simply not the one `--find` asks.
    """
    routed = tool_population.routed_names()
    tools = tool_population.executables(root)
    peers = frozenset(path.name for path, _source in tools)
    return tuple(
        read_tool(path, source, peers, root)
        for path, source in tools
        if not publishing_only or publishes(source, path.name) or path.name in routed
    )


def by_mode(rows: tuple[Tool, ...]) -> dict[str, list[Tool]]:
    """Return `{mode: [tool, …]}` — the inverted census, which is what `--find` reads."""
    out: dict[str, list[Tool]] = {}
    for tool in rows:
        for mode in tool.modes:
            out.setdefault(mode, []).append(tool)
    return out
