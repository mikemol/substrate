#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The `writers` half of `--touching <table>`: verb-scanned write sites in the SQL-writing modules.

⚑⚑⚑ THE SECOND CUT OF THE DRAIN'S SECOND FILE, AND IT IS HALF OF ITS ORIGIN BY DESIGN.
`query_defs.touching` returns three provenances for one relation: `readers` and
`builder_writes`, EXACT from the declared SQLAlchemy builders' statement trees, and `writers`, a
VERB SCAN over source text. The exact half needs the compiled builders (`query_decl`, a
bare-import module with SQLAlchemy under it) and cannot be reached cleanly from the package
today; the scanned half is the same text-census family as `sql_drops` and moves here whole.
⚑ THE SPLIT IS THE ORIGIN'S OWN: its docstring says *"the two halves are asymmetric by
construction, and saying so is the point"*, returned under different keys with different
provenance. This module carries the text-provenance key alone, and says so.

⚑ WRITE VERBS, NOT "MENTIONS". `INSERT`/`UPDATE`/`DELETE`/`DROP` are what a schema change must
move together; a SELECT naming the same table is a reader and belongs to the other half. A hit
is a quoted literal on one line that names the table AFTER one of the verbs — the origin's
`frag.index(verb) < frag.index(table)` test, kept verbatim.

⚑ VERB-SCANNED, SO IT REPORTS PRESENCE AND NEVER ABSENCE. A write through a variable, an
f-string, or a helper is invisible here. The origin prints exactly this caveat beside the list,
and the count is a count of what was FOUND under these spellings.

⚑ THE TREE IS A REQUIRED ARGUMENT (2026-09-24, operator: "We should not have things [like]
corpus.ROOT"). `writers` used to default `root` to `corpus.ROOT`, which let every caller skip
choosing a tree; now the caller that knows which tree it means — an entry point, or the suite's
differential against the live origin — passes it. `scan_text` is the pure core and never needed one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

from substrate.sql_drops import TREES

if TYPE_CHECKING:
    from pathlib import Path

# The write verbs, in the origin's order — the first one found before the table name wins.
VERBS = (
    "insert into",
    "insert or replace into",
    "insert or ignore into",
    "update",
    "delete from",
    "drop table",
)


@dataclass(frozen=True, slots=True, order=True)
class Writer:
    """One verb-scanned write site: where, and which verb precedes the table name."""

    path: str
    line: int
    verb: str


def _literal(table: str) -> re.Pattern[str]:
    """Return the pattern for a one-line quoted literal that names `table` as a word."""
    return re.compile(r"[\"'][^\"'\n]*\b" + re.escape(table) + r"\b[^\"'\n]*[\"']")


def _verb_before(fragment: str, table: str) -> str | None:
    """Return the first verb that appears BEFORE the table name in a lowercased literal."""
    at = fragment.index(table.lower())
    return next((v for v in VERBS if v in fragment and fragment.index(v) < at), None)


def scan_text(src: str, relpath: str, table: str) -> list[Writer]:
    """Return every verb-preceded literal naming `table` in one file's text."""
    out: list[Writer] = []
    for m in _literal(table).finditer(src):
        verb = _verb_before(str(m.group(0)).lower(), table)
        if verb is not None:
            out.append(Writer(relpath, src[: m.start()].count("\n") + 1, verb))
    return out


def _files(root: Path) -> list[Path]:
    """Return every `.py` directly under each SQL-writing tree, sorted — the origin's glob."""
    return sorted(p for tree in TREES for p in (root / tree).glob("*.py"))


def writers(table: str, root: Path) -> tuple[Writer, ...]:
    """Return every distinct verb-scanned write site for `table` under `root`, sorted."""
    found: set[Writer] = set()
    for path in _files(root):
        try:
            src = path.read_text(encoding="utf-8")
        except OSError:
            continue
        found.update(scan_text(src, str(path.relative_to(root)), table))
    return tuple(sorted(found))


def render(found: tuple[Writer, ...]) -> list[str]:
    """Render the `writers` block of `--touching` in the origin's words."""
    lines = [f"  writers ({len(found)}) — verb-scanned, file:line:"]
    lines += [f"      {w.path}:{w.line}  {w.verb}" for w in found]
    return lines
