#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read every key the LEDGER BIBS define — through the tool that owns `.bib`, never a regex.

⚑⚑⚑ THE FOURTH DRAIN UNIT, AND ITS ONE RULE IS THAT IT DOES NOT PARSE. `bibstruct`'s own
header records that `paperkit/bib.py` consolidated THREE parsers which *"each re-derived the
format and disagreed on which fields survive"*, and that a regex inside `worklist_gate` made a
fourth. A fifth, written here, would be the same defect committed at the moment of registering
a witness — so this shells out to the owner and reads its rows.

⚑⚑⚑ UNREADABLE IS NOT EMPTY, AND THAT DISTINCTION IS THE WHOLE VALUE OF THE RETURN TYPE.
If `bibstruct` fails, this returns `None` rather than an empty set, because a caller handed
`set()` reports every witness as unpaired and prints a census claiming total drift. The
pairing census refuses to render on `None` for exactly that reason: a failed read looks
identical to a clean ledger once the distinction is collapsed, and the collapsed version is
the one that gets banked.

⚑ THE LEDGER DIRECTORY IS AN ARGUMENT, so the reader can be pointed at a fixture. The origin
closes over a module-global `HERE`, which is what makes its behaviour untestable without the
real ledger — the same coupling `finding_resolve` removed from the roster lookup.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import finding_kinds

if TYPE_CHECKING:
    from pathlib import Path

# ⚑ ROWS THE ENTRY LISTING EMITS THAT ARE NOT KEYS. A denominator line and a warning line both
#   lead the output; taking token zero blindly would intern them as findings.
_NOT_A_KEY = ("entries:", "⚑")


def ledger_bibs(where: Path) -> list[Path]:
    """Return every `.bib` under `where`, sorted, so the read order is stable.

    ⚑ SORTED BECAUSE A COLLISION IS DECIDED BY ORDER. Two ledgers can declare one key, and the
    later declaration silently wins; an unstable listing would make which one wins depend on
    the filesystem rather than on anything a reader can see.
    """
    if not where.is_dir():
        return []
    return sorted(p for p in where.iterdir() if p.suffix == ".bib")


def bib_keys(where: Path) -> tuple[set[str] | None, list[Path]]:
    """Return `(keys, bibs)`, or `(None, bibs)` when the ledgers could not be read.

    ⚑⚑ `None` IS A THIRD OUTCOME AND MUST NOT BE SMOOTHED INTO `set()`. A caller that treats an
    unreadable ledger as an empty one reports every witness as having no bib entry — a total
    drift census produced by a tool that failed to run, which reads exactly like a real finding.
    """
    bibs = ledger_bibs(where)
    if not bibs:
        # ⚑ NO BIBS AT ALL IS GENUINELY EMPTY, not unreadable: there was nothing to fail on.
        return set(), bibs
    code, out = finding_kinds.run(
        "python3", "scratch/bibstruct.py", "--entries", *[str(p) for p in bibs])
    if code != 0:
        return None, bibs
    keys: set[str] = set()
    for line in out.splitlines():
        head = line.strip().split(" ", 1)
        if head and head[0] and not head[0].startswith(_NOT_A_KEY):
            keys.add(head[0])
    return keys, bibs
