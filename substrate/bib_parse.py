# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The ONE bib parser: a full-fidelity read of what the file SAYS, not what an engine keeps.

⚑⚑⚑ A COMMENT IS NOT INPUT TO THE ENTRY GRAMMAR, AND OMITTING THAT FABRICATED A KEY. Measured on
the origin's first round-trip run: the live bib is two-thirds comment lines, and a comment that
MENTIONS an entry shape — `% see @misc{GHOST, …} for the shape` — was read as a real header. The
entry pattern then ran forward from inside the comment and swallowed the following entry whole. On
a two-entry fixture the reader reported `GHOST` present, the REAL entry absent, and a clean `1 of
1`.

⚑⚑ THAT IS THE ONLY ONE OF THE PARSE'S FAILURE CLASSES THAT FABRICATES RATHER THAN OMITS, WHICH
MAKES IT THE WORST. A missing row can be caught by a denominator; **an invented row corroborates
itself.** And it is the very failure this tool exists to expose — a reader silently dropping what it
cannot see — reproduced inside the reader.

⚑ DELIBERATELY NOT FILTERED TO THE ENGINE'S WHITELIST. The point is to see what the FILE says,
including fields the engine will silently ignore — which is what makes a *"this field was dropped"*
report possible at all.

⚑ ONE PARSER, AND THAT IS THE WHOLE REASON THIS IS A MODULE. Every call site routes through it, so
no two modes can disagree about what an entry IS. The origin's docstring records the alternative:
fixing composition in the CLI alone left the entry map merged while a reader re-read a single file,
reporting 154 edges against 971 entries.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from substrate.bib_edit import Grammar, mask_comments

if TYPE_CHECKING:
    from pathlib import Path

# ⚑ THE ENTRY GRAMMAR. Group 1 is the type, 2 the key, 3 the body. The closing brace must sit at
# column 0 on its own line — a KNOWN NARROWING the origin records: an indented `}` or a one-line
# entry makes the whole entry vanish, and widening the pattern is a second grammar rather than a
# fix. The round-trip probe is what reports the loss.
ENTRY = re.compile(r"(@\w+)\{([^,]+),(.*?)\n\}", re.DOTALL)

# ⚑ THE FIELD GRAMMAR. Group 1 is the name, group 2 the value span. Braces nest ONE level, which
# is why every writer refuses an unbalanced value: a deeper one truncates here at read-back.
FIELD = re.compile(r"(\w[\w-]*)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}")

# The grammar as the editor consumes it, so a locate cannot disagree with a read.
GRAMMAR = Grammar(entry_re=ENTRY, field_re=FIELD)

# The field carrying the entry's `@type`, kept under a private name so it cannot collide with a
# real field. ⚑ UNDERSCORED BECAUSE EVERY REPORT FILTERS ON THAT PREFIX — a bare `type` would be
# listed as a field the author wrote.
TYPE_FIELD = "_type"


def parse(text: str) -> dict[str, dict[str, str]]:
    """Return `{key: {field: value}}` for every entry the text declares.

    ⚑ COMMENTS ARE MASKED FIRST, AND THAT ORDER IS THE FABRICATION GUARD. Parsing before masking
    lets a commented-out entry header become a real key.

    ⚑ WHITESPACE INSIDE A VALUE IS COLLAPSED, so a field wrapped across lines reads back as one
    string. The raw spans stay available to the editor, which slices the ORIGINAL text.
    """
    masked = mask_comments(text)
    out: dict[str, dict[str, str]] = {}
    for entry in ENTRY.finditer(masked):
        fields = {
            str(found.group(1)): " ".join(str(found.group(2)).split())
            for found in FIELD.finditer(str(entry.group(3)))
        }
        fields[TYPE_FIELD] = str(entry.group(1))
        out[str(entry.group(2))] = fields
    return out


def read(path: Path) -> dict[str, dict[str, str]]:
    """Parse one bib from disk, REFUSING a path that is not there.

    ⚑⚑ ABSENT IS NOT EMPTY AND NOT A CRASH, AND THE CALLER DECIDES WHICH MATTERS. The origin
    collapsed three distinct facts — the bib is not there, the path is a directory, the read
    failed — into one exit. Only the last is a legitimate answer to *"what does this file say"*,
    and a caller pointed at a typo'd path deserves a different report from one whose bib was
    deleted.

    ⚑⚑⚑ AND THIS DOCSTRING ARGUED FOR THAT DISTINCTION WHILE THE CODE COLLAPSED IT (gate-G242).
    It returned an empty map for a missing file, so `--entries` on a nonexistent path printed
    `0 of 0 entries` and exited 0 — the reader answering *"this bib is empty"* about a bib that
    does not exist. A caller who mistyped a path was told the file had nothing in it, and a
    capability check pointed at this verb would have certified anything. The prose was right and
    unimplemented, which is the harder half to notice: nothing contradicted it.

    ⚑ A MISSING PATH NOW RAISES, and that is what makes a read verb usable as a behavioural
    check: the negative control — a bad operand must fail — is exactly the property an empty
    return destroys.
    """
    if not path.exists():
        message = (
            f"no such bib: {path} — ABSENT, not empty. A missing file is a fact about "
            "the PATH, and reporting it as zero entries would be indistinguishable "
            "from a bib that genuinely declares none."
        )
        raise FileNotFoundError(message)
    return parse(path.read_text(encoding="utf-8"))
