#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read a tool's SELF-DESCRIPTION: which modes it publishes, with what arguments and gloss.

⚑⚑⚑ THIS IS THE PARSE, AND THE NAIVE VERSION IS WRONG IN BOTH DIRECTIONS AT ONCE.
`mdstruct.py --rows <file> [--table N] [--where <substr>]` carries THREE `--flag` tokens and
declares ONE mode — the bracketed two are options OF `--rows`. Reading all three as modes
invents two that no dispatch has; reading only the first token after the basename loses
`--messages` in `transcriptstruct.py <file> --messages`, where a positional precedes the mode.
So the bracket walk is nesting-aware and the flag scan runs over what is left outside it.

⚑⚑ THE GLOSS SEPARATOR IS THREE CUTS, EARLIEST WINS, AND ASSUMING ONE EMPTIED A WHOLE TOOL.
`pycodemod`/`mdstruct`/`agda_defs` comment their glosses with `#`; `bibstruct` column-aligns
instead. Partitioning on `#` alone gave bibstruct six modes with EMPTY glosses and — worse —
swallowed the prose into the argument region, so `--field <name> [bib]   which entries set
<name>` parsed as taking `<name> <name>`. Its SIGNATURE, the thing the gap and sibling reports
are computed from, was fabricated from prose. The three cuts are `#`, a run of three or more
spaces, and a GRAMMATICAL boundary — the first token that is not a placeholder, bracket group,
flag or ellipsis.

⚑ A POSITIONAL-ONLY TOOL IS RECORDED, NEVER DROPPED. `agda_defs.py <name> ...` publishes
`(positional)`, which is a real mode and the one an operator reaches for first. Seventeen tools
colliding on it is a finding about naming convergence, not noise to filter — the origin module
measured a stricter bar shrinking the population from 74 tools to 9 and concluded that
***"a census that excludes what it cannot yet see well reports the boundary of its own coverage
as the boundary of the toolkit."***

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), which carries 2,196 pycheck
findings and is refused whole by the per-file gate. The extraction continues until the dispatch
moves out too and the original is retired — one carve-off strands, because the only consumer is
inside the file being drained.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# A long flag as it is WRITTEN. ⚑ SINGLE-DASH FLAGS ARE DELIBERATELY OUT OF SCOPE: `-h`/`-j`/`-u`
# are argparse and make idioms, not this toolkit's mode vocabulary.
FLAG = re.compile(r"--[A-Za-z][A-Za-z0-9-]*")

# A `<placeholder>` — the argument-shape vocabulary a signature is built from.
PLACE = re.compile(r"<[^>]*>")

# What a mode is called when a tool's whole interface is "give me a path".
POSITIONAL = "(positional)"

# The column break that separates arguments from prose, when a tool aligns rather than comments.
COLUMN = re.compile(r"\s{3,}")

# One whitespace-separated token, for the grammatical cut.
TOKEN = re.compile(r"\S+")

# The characters that mark a token as argument SYNTAX rather than prose.
SYNTAX = "<>[]"

# Trailing punctuation a bare separator token may be made of (`/`, `...`, `,`).
SEPARATOR_CHARS = "./,"


@dataclass(frozen=True, slots=True)
class Mode:
    """One published mode: what it is called, what it takes, and what it says it does."""

    gloss: str
    sig: tuple[str, ...]


def flags_in(text: str) -> list[str]:
    """Return every long flag written in `text`.

    ⚑ `finditer`, NOT `findall`, AND THE DIFFERENCE IS THE TYPE. `re.findall` returns
    `list[Any]`, which carries an untyped value into every downstream read; `finditer` yields
    `Match[str]`, so `.group(0)` is a `str` by construction. Same result, narrowed at the seam
    rather than asserted after it.
    """
    return [found.group(0) for found in FLAG.finditer(text)]


def placeholders_in(text: str) -> tuple[str, ...]:
    """Return the argument-shape signature `text` declares, lowercased."""
    return tuple(found.group(0).lower() for found in PLACE.finditer(text))


def outside_brackets(text: str) -> str:
    """Return the part of a usage line NOT inside `[...]`, nesting-aware.

    ⚑ THIS IS WHAT SEPARATES A MODE FROM AN OPTION OF A MODE, and getting it wrong manufactures
    capabilities. A bracketed `[--table N]` is an option; an unbracketed `--rows` is the mode.
    """
    out: list[str] = []
    depth = 0
    for ch in text:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _grammatical_cut(segment: str, limit: int) -> int:
    """Return where prose starts, by grammar: the first token that is not argument syntax."""
    for found in TOKEN.finditer(segment[:limit]):
        token = found.group(0)
        if (
            any(ch in token for ch in SYNTAX)
            or token.startswith("--")
            or token.strip(SEPARATOR_CHARS) == ""
        ):
            continue
        return found.start()
    return limit


def split_gloss(segment: str) -> tuple[str, str]:
    """Return `(arguments, gloss)` for the text following a tool's name on a usage line.

    ⚑⚑ THREE CUTS, EARLIEST WINS, because the tools do not hold to one convention and each cut
    covers a shape the others miss. `#` catches the commenting tools; a three-space run catches
    the column-aligning ones; the grammatical boundary catches `bibstruct.py --mentions <key>
    [bib] whose PROSE names <key>`, which separates its gloss with a SINGLE space.

    ⚑ THE UNION IS WHAT STOPS A GLOSS'S OWN `<key>` BEING COUNTED AS A SECOND ARGUMENT — the
    defect that fabricated one tool's entire signature set out of its prose.
    """
    body = segment.lstrip()
    lead = len(segment) - len(body)
    cut = len(segment)

    hash_at = segment.find("#", lead)
    if hash_at != -1:
        cut = hash_at

    column = COLUMN.search(segment[lead:])
    if column and lead + column.start() < cut:
        cut = lead + column.start()

    cut = _grammatical_cut(segment, cut)
    return segment[:cut], segment[cut:].lstrip().lstrip("#").strip()


def names_tool(stem: str, line: str) -> int | None:
    """Return where `stem` ends on this line when it is named as a WORD, else None.

    ⚑ AS A WORD, NOT A SUBSTRING. `scratch/pycodemod.py` names the tool; `_pycodemod_query.py`
    does not, and matching loosely would attribute a helper's usage lines to the tool.
    """
    found = re.search(r"(?<![A-Za-z0-9_])" + re.escape(stem), line)
    return found.end() if found else None


def _continuation(lines: list[str], start: int, stem: str) -> tuple[str, int]:
    """Return the wrapped `#` gloss under a usage line, and where it ends.

    ⚑ THE WRAPPED HALF IS USUALLY THE PART THAT SAYS WHAT THE MODE IS FOR. Every tool here wraps
    its rationale over several comment lines, so reading only the first would keep the label and
    drop the reason.
    """
    parts: list[str] = []
    at = start
    while at < len(lines):
        text = lines[at].strip()
        if not text.startswith("#") or names_tool(stem, lines[at]) is not None:
            break
        parts.append(text.lstrip("#").strip())
        at += 1
    return " ".join(p for p in parts if p), at


def _merge(found: dict[str, Mode], mode: str, gloss: str, sig: tuple[str, ...]) -> None:
    """Record one mode, keeping BOTH glosses when it is documented twice.

    ⚑ A MODE MAY BE DOCUMENTED TWICE WITH DIFFERENT ARGUMENTS — `pycodemod --attr <name>` and
    `--attr <Recv>.*`. The second is where the INVERSE reading is explained, so keeping only one
    loses half the mode.
    """
    prev = found.get(mode)
    if prev is None:
        found[mode] = Mode(gloss=gloss, sig=sig)
        return
    merged = prev.gloss
    if gloss and gloss not in prev.gloss:
        merged = (prev.gloss + " | " + gloss).strip(" |")
    found[mode] = Mode(gloss=merged, sig=prev.sig or sig)


def parse_usage(text: str, stem: str) -> dict[str, Mode]:
    """Return `{mode: Mode}` from the tool's OWN usage lines.

    A usage line names the tool and is followed by its arguments; the gloss is that line's `#`
    comment plus the continuation lines beneath it.
    """
    lines = text.splitlines()
    found: dict[str, Mode] = {}
    at = 0
    while at < len(lines):
        end = names_tool(stem, lines[at])
        if end is None:
            at += 1
            continue

        code, gloss = split_gloss(lines[at][end:])
        outside = outside_brackets(code)
        modes = flags_in(outside)
        sig = placeholders_in(outside)

        if not modes:
            if not sig:
                at += 1  # a prose mention of the tool, not a usage line
                continue
            modes = [POSITIONAL]

        wrapped, at = _continuation(lines, at + 1, stem)
        whole = " ".join(p for p in (gloss.strip(), wrapped) if p)
        for mode in modes:
            _merge(found, mode, whole, sig)
    return found


def bracketed_options(text: str, stem: str) -> set[str]:
    """Return the flags a usage line declares INSIDE `[...]` — options of a mode, not modes.

    ⚑⚑ DECLARED, JUST NOT AS MODES, AND CONFLATING THE TWO MANUFACTURES GAPS. `mdstruct --rows
    <file> [--table N] [--where <substr>]` declares `--table` and `--where`; they are correctly
    kept out of the mode list, but subtracting only the MODES from a tool's prose mentions then
    reported both as *"named by a tool and declared by nothing"* — as filed gaps. Eight of
    thirteen entries in that census were this artefact, which would have sent a reader building
    modes that already exist.
    """
    out: set[str] = set()
    for line in text.splitlines():
        end = names_tool(stem, line)
        if end is None:
            continue
        code, _gloss = split_gloss(line[end:])
        inside = code
        for token in outside_brackets(code).split():
            inside = inside.replace(token, " ")
        out.update(flags_in(inside))
    return out
