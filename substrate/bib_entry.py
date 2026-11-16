# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Validate and render one new bib entry — the checks that must pass BEFORE any write.

⚑⚑⚑ EVERY REFUSAL HERE PREVENTS AN ENTRY THAT CANNOT BE DISCHARGED, WHICH IS WORSE THAN AN ABSENT
ONE. An entry whose witness does not resolve files as ORDERED BUT NEVER CLOSABLE — permanently open,
permanently counted, indistinguishable from real work, and surfaced by the ordering forever. An edge
into a non-existent key breaks an invariant the corpus currently holds. Both are cheaper to refuse
than to detect later, and neither is visible in a diff.

⚑⚑ THE EDGE IS VALIDATED AGAINST THE CORPUS, NOT THE WRITE TARGET, AND THE OTHER WAY ROUND WAS A
FALSE REFUSAL — the dangerous direction. Measured by a peer on the first two writes after they split
a 242-entry monolith into five per-genre bibs: a corroboration resting on a use-case in a SIBLING
file was refused as dangling when it is not, and the entry had to be placed with its edge demoted to
prose. ⚑ The refusal's own justification named the bug: it said a bad edge *"would make `--orphans`
non-empty"* — and `--orphans` reads MANY bibs by design. **The writer was enforcing a corpus-wide
invariant against a single-file population.**

⚑ AND THE DUPLICATE CHECK STAYS TARGET-LOCAL, DELIBERATELY — the asymmetry is the point. *"Does
this key already exist HERE"* is a question about the file being written; *"does this edge resolve"*
is a question about the corpus. Widening both would refuse a key that legitimately appears in
another genre's bib.

⚑ CREATE AND EDIT ARE DIFFERENT ACTS WITH DIFFERENT BLAST RADII, so this refuses to edit exactly as
`--set` refuses to create. A wrong edit changes one value; a wrong CREATE puts a claim into the DAG
that the ordering will surface as work. An upsert would make *"did I mean to create this?"*
unanswerable at the call site.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from substrate.bib_corpus import EDGE_FIELDS

# An entry cannot be filed without these. ⚑ `claim` IS WHAT IS ASSERTED and `check` IS WHAT COULD
# FALSIFY IT; an entry missing either is a sentence with no way to go red.
REQUIRED = ("claim", "check")

# ⚑ FIELD ORDER IS THE FILE'S, NOT A DICT'S. The bib writes section and its edges before the
# claim and check, so matching it keeps the projection's render order stable and the diff readable.
FIELD_ORDER = ("section", "from", "rests-on", "enables", "join", "claim", "check")

# How a `check` names an item witness.
ITEM_CHECK = re.compile(r"item:(\S+)")

# What separates edge targets within one field.
_TARGETS = re.compile(r"[,\s]+")


@dataclass(frozen=True, slots=True)
class Refusal:
    """A write that will not proceed, and what the caller should do instead."""

    message: str
    code: int = 2


def witness_key(check: str) -> str | None:
    """Return the item key a `check` names, or None when it names no item witness."""
    found = ITEM_CHECK.match(check.strip())
    return found.group(1) if found else None


def edge_targets(fields: dict[str, str]) -> tuple[tuple[str, str], ...]:
    """Return `(field, target)` for every edge the entry declares."""
    return tuple(
        (name, target)
        for name in EDGE_FIELDS
        for target in _TARGETS.split(fields.get(name, "").strip())
        if target
    )


def validate(
    key: str,
    fields: dict[str, str],
    *,
    target_keys: frozenset[str],
    corpus_keys: frozenset[str],
) -> Refusal | None:
    """Return why this entry must not be written, or None when it may be.

    ⚑⚑ `target_keys` AND `corpus_keys` ARE TWO POPULATIONS AND MUST NOT BE COLLAPSED. The duplicate
    test reads the first (a question about the file being written); the edge test reads the second
    (a question about the corpus). One set for both is the defect this whole module records — wrong
    in whichever direction the gap points.
    """
    if key in target_keys:
        return Refusal(
            f"bibstruct --add: {key!r} already exists. Editing a field is `--set`; "
            f"this only creates."
        )

    missing = [name for name in REQUIRED if name not in fields]
    if missing:
        got = ", ".join(sorted(fields)) or "none"
        return Refusal(
            f"bibstruct --add: an entry needs at least "
            f"{' and '.join(f'`{n}`' for n in REQUIRED)} (got: {got})"
        )

    # ⚑ UNBALANCED BRACES BREAK THE NEXT PARSE, NOT THIS ONE. A field whose braces do not close
    # swallows the entries after it, so the file still parses and reports FEWER entries — a silent
    # loss the round-trip probe was built to catch and this refusal prevents outright.
    for name, value in sorted(fields.items()):
        if value.count("{") != value.count("}"):
            return Refusal(f"bibstruct --add: unbalanced braces in {name!r}")

    for name, dest in edge_targets(fields):
        if dest not in corpus_keys and dest != key:
            return Refusal(
                f"bibstruct --add: {name} names {dest!r}, which is not an entry in the file(s) "
                f"read. An edge into a non-existent key would make --orphans non-empty.\n"
                f"  ⚑ IF THE TARGET LIVES IN A SIBLING BIB, name it: `--corpus <bib> [<bib> …]`. "
                f"A split corpus makes an edge cross files, and this check reads only what it is "
                f"given — 'not in the population' is NOT 'does not exist'."
            )

    return None


def render(key: str, fields: dict[str, str]) -> str:
    """Return the entry's text, fields in the file's own order.

    ⚑ THE ORDER IS DECLARED RATHER THAN SORTED, and unknown fields follow in sorted order so a new
    field name cannot silently reshuffle every existing entry's rendering.
    """
    ordered = [name for name in FIELD_ORDER if name in fields]
    ordered += [name for name in sorted(fields) if name not in FIELD_ORDER]
    body = "".join(f"  {name:<8} = {{{fields[name]}}},\n" for name in ordered)
    trimmed = body.rstrip(",\n")
    return f"\n@misc{{{key},\n{trimmed}\n}}\n"


def append(text: str, key: str, fields: dict[str, str]) -> str:
    """Return `text` with the rendered entry appended. PURE — no write."""
    return text.rstrip("\n") + "\n" + render(key, fields)
