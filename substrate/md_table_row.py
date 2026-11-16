# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Append one row to a markdown table, as a line splice.

⚑⚑⚑ THE READER EXISTS AND THE WRITER DID NOT, WHICH IS HOW A SHARD GOES UNROUTED.
`mdstruct` owns markdown structurally: `--tables` reports each table's header and size,
`--rows` reports the cells. Both READ. Its write modes operate on SECTIONS and are
explicitly a line splice rather than an AST render, so neither can add a row — and a
worklist shard whose concern the routing table cannot name is one nobody can decide is
too large, the defect recorded when an earlier arc sat buried in a shard whose title did
not name it.

⚑⚑ AND THE READER'S OWN DOCSTRING RECORDS THIS CLASS ONE LEVEL DOWN. `table_rows` was
specified in prose inside the file that owns tables, named correctly by a read-only agent
who could not build it, and left unbuilt through every later dispatch — *"a capability
named in a docstring is not a capability."* The write side was the same shape until this
module.

⚑ A LINE SPLICE, NOT AN AST RENDER, for the reason the section writers give: pandoc is a
NORMALIZER, so a markdown→AST→markdown round-trip reflows text and re-wraps tables. A
one-row edit must be a one-line diff, or every routing change carries an unreviewable
reformat of the whole document.

⚑ REFUSALS ARE THE POINT, and they mirror the section writers': an ambiguous table
refuses naming its candidates, a missing one refuses, and a row whose cell count
disagrees with the header refuses. A row silently padded or truncated to fit is a
malformed table that still parses — the shape that survives review.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# A markdown table row opens and closes with a pipe once stripped.
_PIPE = "|"

# The delimiter row: pipes, colons, dashes and spaces only.
_DELIM_CHARS = set("|:- ")


class TableError(ValueError):
    """Raised when the target table cannot be identified, or the row does not fit."""


@dataclass(frozen=True, slots=True)
class Table:
    """One pipe table's extent and shape, in source lines."""

    header_line: int
    delim_line: int
    last_line: int
    columns: int
    header: tuple[str, ...]


def _cells(line: str) -> list[str]:
    """Split one pipe-table line into its cells, without the bounding pipes."""
    body = line.strip()
    if body.startswith(_PIPE):
        body = body[1:]
    if body.endswith(_PIPE):
        body = body[:-1]
    return [c.strip() for c in body.split(_PIPE)]


def _is_delim(line: str) -> bool:
    """Report whether this line is a table's header/body delimiter."""
    body = line.strip()
    return bool(body) and _PIPE in body and set(body) <= _DELIM_CHARS


def tables(lines: list[str]) -> list[Table]:
    """Return every pipe table in `lines`, in document order.

    ⚑ A TABLE IS FOUND BY ITS DELIMITER, NOT BY ITS PIPES. A prose line may contain a
    pipe, and a fenced code block may contain many; the delimiter row is the only line
    whose whole content is table syntax, so anchoring on it is what keeps this from
    reporting arbitrary text as a table.
    """
    found: list[Table] = []
    for i, line in enumerate(lines):
        if i == 0 or not _is_delim(line):
            continue
        header = lines[i - 1]
        if _PIPE not in header:
            continue
        cols = _cells(header)
        last = i
        for j in range(i + 1, len(lines)):
            if _PIPE not in lines[j] or not lines[j].strip():
                break
            last = j
        found.append(Table(i - 1, i, last, len(cols), tuple(cols)))
    return found


def _select(found: list[Table], where: str | None) -> Table:
    """Return the one table `where` names, refusing ambiguity and absence."""
    if not found:
        msg = "no pipe table in this document"
        raise TableError(msg)
    if where is None:
        if len(found) > 1:
            heads = " / ".join(" ".join(t.header) for t in found)
            msg = f"{len(found)} tables — name one by a header substring: {heads}"
            raise TableError(msg)
        return found[0]
    hits = [t for t in found if where.casefold() in " ".join(t.header).casefold()]
    if not hits:
        heads = " / ".join(" ".join(t.header) for t in found)
        msg = f"no table header matches {where!r}; candidates: {heads}"
        raise TableError(msg)
    if len(hits) > 1:
        heads = " / ".join(" ".join(t.header) for t in hits)
        msg = f"{where!r} matches {len(hits)} tables: {heads}"
        raise TableError(msg)
    return hits[0]


def render_row(cells: list[str]) -> str:
    """Render cells as one pipe-table line."""
    return _PIPE + _PIPE.join(f" {c.strip()} " for c in cells) + _PIPE


def append_row(
    path: Path,
    cells: list[str],
    where: str | None = None,
    *,
    apply: bool = False,
) -> str:
    """Append `cells` as a row to the named table, returning the new line.

    ⚑ THE CELL COUNT MUST MATCH THE HEADER EXACTLY. Padding a short row or dropping a
    long one produces a table that still parses and no longer means what its header
    says — a malformed artefact that survives every reader downstream.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    table = _select(tables(lines), where)
    if len(cells) != table.columns:
        msg = (
            f"row has {len(cells)} cell(s), table has {table.columns} ({' | '.join(table.header)})"
        )
        raise TableError(msg)
    row = render_row(cells)
    if apply:
        cut = table.last_line + 1
        out = [*lines[:cut], row, *lines[cut:]]
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return row
