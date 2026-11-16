# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read the findings ledger's witnesses from the BIBS, as the same `Row`s the roster yielded (W40).

⚑⚑ THE COLLAPSE THAT RETIRES THE ROSTER READER. Every consumer of `witness_source.rows()` — the
census, the converger, the live differentials — reads `Row(key, kind, args)` parsed out of the
`WITNESSES` literal. Since the convergence each bib entry's `check` IS its witness, spelled by
`witness_check.emit`, which REFUSES any spelling that does not parse back to the same witness. So
the inverse is well defined for every row: parse the check, and the row comes back — from data,
not from code. A consumer switches by changing where its rows come from, nothing else.

⚑ THE NOTE IS THE ENTRY'S OWN `note`. It is the last argument, as in the roster; after the lossless
move it is the merged text (the bib's note plus the roster's under its provenance marker), so it
legitimately differs from the roster's and the differential compares `args[:-1]`.

⚑ AN ENTRY WHOSE CHECK DOES NOT PARSE RAISES, as `witness_source` does for an unrepresentable roster
row: a witness this reader cannot represent must stop the migration, never be dropped from it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.ledger import finding_kindspec

from substrate import bib_parse, ledger_cli, witness_check
from substrate.witness_source import RosterShapeError, Row

if TYPE_CHECKING:
    from pathlib import Path

# The kinds whose first argument is an argv.
_COMMAND = ("selftest", "refuses")


def row_of(key: str, check: str, note: str) -> Row:
    """Return the witness `check` spells, as a roster `Row` whose last argument is `note`."""
    local = witness_check.parse_local(check)
    if local is not None:
        return Row(key=key, kind=local[0], args=(*local[1], note))
    spec, refusal = finding_kindspec.parse(check)
    if spec is None:
        msg = f"{key}: check {check!r} does not parse ({refusal})"
        raise RosterShapeError(msg)
    kind = spec.builder.removeprefix("_")
    if kind in _COMMAND:
        return Row(key=key, kind=kind, args=(list(spec.cmd), note))
    if kind == "mode_undocumented":
        # ⚑ THE ONE KIND WITH NO NOTE: the roster helper takes (tool, flag) and nothing else, so its
        # last argument is the FLAG. A first cut appended the note here and 4 rows differed.
        return Row(key=key, kind=kind, args=(spec.tool, spec.flag))
    return Row(key=key, kind=kind, args=(note,))


def rows(project: Path) -> list[Row]:
    """Return every witness the project's warrant bibs declare, sorted by key.

    Raises on an entry whose check does not parse.
    """
    by_key: dict[str, Row] = {}
    for bib in ledger_cli.warrant_bibs(project):
        for key, fields in bib_parse.parse(bib.read_text(encoding="utf-8")).items():
            by_key[key] = row_of(key, fields.get("check", ""), fields.get("note", ""))
    return [by_key[key] for key in sorted(by_key)]
