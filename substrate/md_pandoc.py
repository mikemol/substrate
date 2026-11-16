#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run pandoc — the ONE conversion point, and the only subprocess in the markdown toolkit.

⚑⚑ THIS IS ITS OWN MODULE BECAUSE RUNNING PANDOC IS ONE RESPONSIBILITY (⟡mdstruct-n-split).
The `S603` exemption a subprocess needs is granted per FILE, so a module that also parsed, or
read sections, or rendered results would extend that exemption over every one of them. The argv
here is `pandoc` plus format names from a fixed vocabulary — the document travels on stdin as
data and never becomes a word in the command.

⚑⚑ RE-ATTACHING FRONTMATTER IS CORRECT ONLY FOR A MARKDOWN WRITER, and doing it unconditionally
broke EVERY AST mode on any `---`-fenced document for the life of the original module: `-t json`
got the YAML head prepended, so the parser read a document opening with `---` and died at char
0 — the header, table, row, item and coherence modes were all blind to frontmatter'd markdown,
which in practice is every governed doc and every SKILL.md. For a non-markdown writer the head
is not preservation, it is corruption of a different language.

⚑ DIAGNOSED BY A PEER, NOT HERE — gabion reported it through summit and deliberately did NOT
patch their own copy, because it is a symlink and a local fix would fork the body silently. The
owner is the party who can fix it, and the owner could not see it from inside.

⚑⚑⚑ THE READER DISABLES PANDOC'S `smart` EXTENSION (summit ask-mdstruct-heading-contract, open
2026-09-06 to 2026-09-20). `smart` is ON by default for the `markdown` reader and it REWRITES
punctuation in the parsed text: an ASCII apostrophe becomes RIGHT SINGLE QUOTATION MARK, `--`
an EN DASH, `...` an ELLIPSIS. A heading spelled `The rule's layer` in the file parsed with the
curly mark, so every raw-vs-rendered anchoring — the span finder, mdstruct's header-to-line
match — failed on it and the section was ABSORBED INTO ITS PARENT with no error. Summit's
CLAUDE.md read 20 of 21 headings; this repo's own read 8 of 9 (`someone else's`). It was never
a dropped heading: it was a reader that changed the text it was asked to read.
`md_heading_contract` is the arm that catches the class, and it found the mechanism in one run.
"""

from __future__ import annotations

import subprocess

from mikemol.mdstruct import frontmatter as md_frontmatter

# ⚑ THE WRITERS THAT READ BACK AS MARKDOWN — the predicate this re-attaches on. A PREFIX tuple,
# not an equality set: callers pass a bare family name, but pandoc accepts `markdown_strict`,
# `commonmark_x`, and `+ext`/`-ext` suffixes on any of them. An equality check would silently
# stop preserving frontmatter the first time someone asked for a dialect.
MD_WRITERS = ("markdown", "commonmark", "gfm")

# The reader extensions this toolkit fixes, appended to whatever reader a caller names. A caller
# that already spells `smart` either way keeps its spelling: the suffix is added only when the
# reader string does not mention the extension, so an explicit choice is never overridden.
READER_EXTS = "-smart"

# How much of pandoc's stderr to carry into a raised error: enough to name the failure, bounded
# so a malformed document cannot flood a caller's context.
_ERR_CHARS = 400


def reader(frm: str) -> str:
    """Return the reader spec with this toolkit's fixed extensions applied."""
    return frm if "smart" in frm else frm + READER_EXTS


def convert(src: str, to: str, frm: str = "markdown") -> str:
    """Convert `src` with pandoc; `to` may carry writer FLAGS after the format name.

    ⚑ THE WRAPPING FLAGS DECIDE IDEMPOTENCE for a table-dense document, so they must be
    reachable from the caller. Passing the whole string as one `-t` argument makes pandoc read
    `--columns=999` as an extension name and refuse.
    """
    head, body = md_frontmatter.split(src)
    parts = (to or "markdown").split()
    cmd = ["pandoc", "-f", reader(frm), "-t", parts[0], *parts[1:]]
    proc = subprocess.run(cmd, input=body, capture_output=True, text=True, check=False)
    if proc.returncode:
        raise RuntimeError(proc.stderr.strip()[:_ERR_CHARS])
    stdout: str = proc.stdout
    return (head + stdout) if parts[0].startswith(MD_WRITERS) else stdout
