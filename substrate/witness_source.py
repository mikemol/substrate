# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The findings ledger's witness as DATA: `Row(key, kind, args)`, and the error for one unreadable.

⚑⚑ THIS MODULE ONCE READ THE `WITNESSES` LITERAL, AND ITS READER RETIRED WITH IT (W40). It parsed
`.claude/agents/findings.py`'s roster by syntax tree — each entry a lambda calling one kind helper
with literal arguments — into these rows, so the roster could be moved into the bibs without
executing it. The move is done: every bib entry's `check` IS its witness, `witness_bibrows` reads
the same `Row`s back from the bibs, and `findings.py` is a shim with no literal left to parse.
The reader's last result is recorded in the paths-forward ledger: 850 rows, and the bib reading
agreed with every one.

⚑ WHAT STAYS IS THE SHAPE. `Row` is the one witness representation both sides spoke, and
`RosterShapeError` is how a reader refuses an entry it cannot represent — a witness that cannot be
read must stop a migration, never be dropped from it.
"""

from __future__ import annotations

from dataclasses import dataclass


class RosterShapeError(ValueError):
    """A witness entry cannot be represented as a `Row` — refuse it rather than drop it."""


@dataclass(frozen=True, slots=True)
class Row:
    """One witness as data: its key, its kind, and the literal arguments its helper takes."""

    key: str
    kind: str
    args: tuple[object, ...]
