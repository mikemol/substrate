# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The totality probe: every place the PARSE fails to ACCOUNT for the file.

⚑⚑⚑ THIS IS A COALGEBRA QUESTION AND A CENSUS CANNOT STAND IN FOR IT. `--entries` reporting `42 of
42` is an ALGEBRA statement — at THIS input, the parser agrees with a second reading of the same
bytes. What the parse DOES TO inputs it has not seen is the other direction, and it is where the
losses are. Measured on a live bib: 0 quoted fields, 0 bare-integer fields, 42 headers = 42 parsed
— **which says the kernel is UNWITNESSED, not empty.** An unwitnessed kernel is the dangerous case,
because nothing exercises it and its first firing is invisible.

⚑⚑⚑ AND THE PROBE MUST NOT RE-DERIVE THE GRAMMAR IT IS CHECKING. The origin's first cut scanned
with the PARSER'S OWN character class, so it could only ever see what the parser sees — a totality
check measuring its own reimplementation. Demonstrated on a two-entry fixture: `'rests-on' = {A}`,
quoted and well-formed BibTeX, read back as *"0 unaccounted-for constructs — this read is TOTAL"*
while the bytes held four fields and the parse listed three.

⚑⚑ THE LIVE COST WAS 60% OF A GRAPH. A peer found 56 quoted `rests-on` across their placed floor —
19 of 20 workarounds had their grounding edge INVISIBLE — and unquoting moved the edge count from 39
to 98. **Every surface was green throughout, including this one.** The framing that fixed it:
*a dropped-field report answers for the WHITELIST; nothing answered for the LEXER.* So the scan uses
a deliberately LOOSER pattern that never produces a value, only a discrepancy — a name form nobody
anticipated is LOUD rather than silent.

⚑⚑ MASK THE PARSED VALUES BEFORE SCANNING, OR PROSE READS AS AN ASSIGNMENT. Live false positive:
an entry whose claim discusses a Fano line says `p+q+r = 0 over F2`, and the scan reported `p+q+r`
as an unparsed field. That is use-versus-mention, committed by the instrument built to catch it.
What remains after masking is exactly the text the parser did not account for, which is the question
being asked.

⚑ THE FILE IS THE ORACLE AND THE PARSE IS WHAT MUST ACCOUNT FOR IT — never a re-emitter diff. There
is no lossless BibTeX writer here, and writing one would be a second grammar in the module whose own
banner records existing to stop being a fourth parser.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from substrate.bib_edit import mask_comments
from substrate.bib_parse import ENTRY, FIELD

# ⚑⚑⚑ DELIBERATELY LOOSER THAN THE FIELD GRAMMAR, AND THAT LOOSENESS IS THE WHOLE INSTRUMENT.
# `(\S+)\s*=\s*\{` accepts any non-space run before the assignment, so a quoted name, a dotted one,
# or a spelling nobody has met yet still registers as *something the bytes assign*. Matching the
# parser's own class here is what made the probe blind to 56 live edges.
ASSIGN = re.compile(r"(\S+)\s*=\s*\{")

# An `@header{key,` as the BYTES hold it — scanned independently of the entry grammar so a header
# the parse cannot reach is still counted.
HEADER = re.compile(r"(?m)^\s*@(\w+)\s*\{\s*([^,\s]+)\s*,")


@dataclass(frozen=True, slots=True)
class Loss:
    """One construct the file holds that the parse did not account for."""

    kind: str
    what: str
    detail: str


def _line_of(text: str, at: int) -> int:
    """Return the 1-based line number of an offset."""
    return text.count("\n", 0, at) + 1


def _vanished(text: str, parsed: dict[str, dict[str, str]]) -> list[Loss]:
    """Return headers the bytes hold that the parse produced no key for.

    ⚑ AND A DUPLICATE HEADER IS A SILENT LOSS, NOT A DUPLICATE. The parse keeps the last, so a
    repeated key discards an earlier declaration with no signal — reported here because the entry
    map cannot show what it overwrote.
    """
    out: list[Loss] = []
    seen: list[tuple[str, int]] = [
        (str(m.group(2)), _line_of(text, m.start())) for m in HEADER.finditer(text)
    ]

    out.extend(
        Loss("entry-vanished", key, f"line {line}: header present, not parsed")
        for key, line in seen
        if key not in parsed
    )

    counts: dict[str, int] = {}
    for key, _line in seen:
        counts[key] = counts.get(key, 0) + 1
    out.extend(
        Loss("duplicate-key", key, f"{n} headers, parse keeps 1")
        for key, n in sorted(counts.items())
        if n > 1
    )
    return out


def _mask_values(body: str) -> str:
    """Blank every parsed value in an entry body, preserving length.

    ⚑ LENGTH-PRESERVING SO THE REPORTED LINE NUMBER STAYS TRUE — the same rule the comment mask
    follows, and for the same reason: an offset computed on one text must be valid on the other.
    """
    out = body
    for found in FIELD.finditer(body):
        lo, hi = found.span(2)
        out = out[:lo] + (" " * (hi - lo)) + out[hi:]
    return out


def _unparsed(text: str, parsed: dict[str, dict[str, str]]) -> list[Loss]:
    """Return assignments inside a parsed entry that produced no field.

    ⚑ THE SPAN IS THE ENTRY'S, NOT THE FILE'S. Scanning the whole file would flag prose outside
    any entry; the question is what the parse missed in the region it actually read.
    """
    out: list[Loss] = []
    for entry in ENTRY.finditer(text):
        key = str(entry.group(2))
        body = str(entry.group(3))
        got = set(parsed.get(key, {}))
        for found in ASSIGN.finditer(_mask_values(body)):
            raw = str(found.group(1))
            if raw.strip("'\"") in got:
                continue
            line = _line_of(text, entry.start(3) + found.start())
            out.append(
                Loss(
                    "field-unparsed",
                    f"{key}.{raw}",
                    f"line {line}: `{raw} = {{` in the bytes, no field in the parse",
                )
            )
    return out


def probe(text: str, parsed: dict[str, dict[str, str]]) -> tuple[Loss, ...]:
    """Return every construct the file holds that `parsed` does not account for.

    ⚑⚑ COMMENTS ARE MASKED THE SAME WAY THE PARSE MASKS THEM, or the probe measures a DIFFERENT
    file and reports the difference as a defect. Routed through the one mask rather than
    re-testing for a comment marker here — the origin's first cut did the latter and, because
    masking was then missing from the parser itself, correctly reported a vanished entry for the
    RIGHT reason. **Two comment rules would have hidden the fabrication bug.**
    """
    masked = mask_comments(text)
    return (*_vanished(masked, parsed), *_unparsed(masked, parsed))


def total(losses: tuple[Loss, ...]) -> bool:
    """Whether this read accounted for the whole input.

    ⚑ AN ALGEBRA RESULT ABOUT THIS INPUT, AND NOTHING MORE. It does NOT say the parser's kernel is
    empty; it says nothing in THIS file fell into it. Reporting it as the former is the claim the
    module docstring exists to refuse.
    """
    return not losses
