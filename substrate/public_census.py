# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The re-export census — every `open … public` in the tree, as debt.

⚑ POLICY. A module re-exports ONLY what it DEFINES. Agda module application COPIES rather than
references, so a wholesale `open X public` re-materialises X's entire accumulated API into this
module's core and into every consumer's, transitively — which is the mechanism behind the
elaboration blowups the cap ratchet gates. The paydown is to bind at the owner and drop the
re-export, never to delete a keyword and leave the structure.

⚑⚑ THE PREDICATE MATCHES THE POLICY, NOT THE GATE'S CONVENIENCE, and that distinction has
already been paid for once here. An earlier census counted only WHOLESALE re-exports, so a
narrowed `open X using (…) public` was not exempt debt — it was INVISIBLE debt, absent from the
baseline entirely. Widening the predicate RAISES a baseline before it falls, which is the
ratchet working rather than a regression.

⚑⚑⚑ THE UNIT IS THE STATEMENT, NOT THE LINE. Agda accepts import directives in any order and
across continuation lines, so `public` may sit on the opening line with `using (…)` on the next,
or follow multi-line arguments. A line-anchored scan misses both shapes — the same
statement-vs-line blindness that once let a hundred and fifty-eight narrowed re-exports escape
this very census.

⚑ `Agda.Primitive` IS EXCLUDED, and it is the one exclusion the policy licenses. The catalog
does not index compiler builtins, so there is no owner to bind at; `Foundation/Level.agda`
re-exporting `Level` IS the insulation boundary working rather than a conduit.

⚑ EXTRACTED FROM `scripts/check_public_ratchet.py` SO IT CAN BE READ WITHOUT RUNNING THE GATE.
That file reaches its tree-walking helpers by bare sibling import — `from check_carrier_locality
import ROOT, strip_comments, agda_files` — which resolves only because gates run as scripts with
their directory on the path. The census is the half other tools need, and the half that can be
clean; the sibling reach is what kept it from being either.
"""

from __future__ import annotations

import re
from pathlib import Path

from substrate import census_call, corpus, scratch_module

# An `open` statement's head: the indent (which delimits its continuations) and what is opened.
OPEN = re.compile(r"^([ \t]*)open\s+(?:import\s+)?(\S+)")

# ⚑ BOUNDED SO IT CANNOT MATCH A NAME CONTAINING IT. `public` inside an identifier — or a module
# path segment — is not the keyword, and an unbounded search would census a module for being
# named after the thing the gate forbids.
PUBLIC = re.compile(r"(?<![\w.-])public(?![\w.-])")

# The one module whose re-export has no owner to bind at.
BUILTIN = "Agda.Primitive"

_LEX = "agda_lex"


def opened_by(line: str) -> str | None:
    """Return what `line` opens, or None when it opens nothing.

    ⚑ THE NARROWING HAPPENS HERE, ONCE. `Match.group` is untyped, so a caller comparing its
    result carries `Any` into every expression that touches it — the same boundary discipline
    the dynamic-call sites use, applied to the regex layer.
    """
    head = OPEN.match(line)
    if head is None:
        return None
    return str(head.group(2))


def statement(lines: list[str], i: int) -> tuple[list[str], int]:
    """Return the full `open` statement starting at `lines[i]`, and the index after it.

    ⚑ A CONTINUATION IS A MORE-INDENTED NON-BLANK LINE. Consuming the head alone would drop a
    `public` sitting on the following line, which is exactly the shape this census exists to
    catch — so the statement, not the line, is the unit throughout.
    """
    head = OPEN.match(lines[i])
    if head is None:
        return [], i + 1
    ind = len(head.group(1))
    out = [lines[i]]
    j = i + 1
    while j < len(lines) and lines[j].strip() and (len(lines[j]) - len(lines[j].lstrip())) > ind:
        out.append(lines[j])
        j += 1
    return out, j


def reexports_in(rel: str, lines: list[str]) -> set[str]:
    """Return `{rel::opened}` for every `open … public` in one comment-masked file."""
    out: set[str] = set()
    i = 0
    while i < len(lines):
        opened = opened_by(lines[i])
        if opened is None:
            i += 1
            continue
        stmt, nxt = statement(lines, i)
        if PUBLIC.search("\n".join(stmt)) and not opened.startswith(BUILTIN):
            out.add(f"{rel}::{opened}")
        i = nxt
    return out


def census() -> set[str]:
    """Return `{relpath::opened}` for every `open … public` in the tree.

    ⚑ AN UNLOADABLE LEXER RETURNS AN EMPTY SET, WHICH IS A KNOWN LIMIT AND NOT A CLEAN TREE.
    A gate must prefer `census_or_why`, which says which of the two happened.
    """
    keys, _why = census_or_why()
    return keys


def census_or_why() -> tuple[set[str], str | None]:
    """Return `(census, None)`, or `(empty, why)` when the lexer could not be loaded.

    ⚑⚑ AN EMPTY CENSUS AND AN UNMEASURABLE ONE RENDER IDENTICALLY AS A NUMBER, and the second
    banked into a paydown-only baseline would absolve every existing re-export permanently.
    The reason is carried so a caller can refuse rather than record.
    """
    lex, why = scratch_module.scratch_module(_LEX)
    if lex is None:
        return set(), why or f"could not load {_LEX}"

    root = corpus.ROOT
    files, why = census_call.str_set_call(lex, "agda_files", str(root / "agda"), _LEX)
    if why is not None:
        return set(), why

    out: set[str] = set()
    for path in sorted(files):
        text = Path(path).read_text(encoding="utf-8", errors="replace")
        masked, why = census_call.text_call(lex, "mask_comments", text, _LEX)
        if why is not None:
            return set(), why
        rel = str(Path(path).relative_to(root))
        out |= reexports_in(rel, masked.splitlines())
    return out, None
