#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print a document's tables, or the rows matching a name — the CLI over `substrate.md_tables`.

⚑ THE CLI IS ITS OWN MODULE, the same split the rest of this toolkit uses: the reader returns
data, this decides how to render it.

    md_tables_show.py FILE.md                  # every table: position, size, header
    md_tables_show.py FILE.md --where <text>   # the rows mentioning <text>
    md_tables_show.py FILE.md --table <n>      # one table's rows

⚑⚑ THE `--where` FORM IS THE ONE THAT WAS MISSING FOR A YEAR OF READERS. This repo's name→home
index is a 963-row table, and its designated use is *"before writing a new record, name the
existing structure it specialises"* — a lookup by NAME. Nothing could perform it: the tool that
owns markdown could report the table's SIZE and not read a row. A read-only agent named the gap
correctly and could do nothing else about it.

⚑ EVERY ROW REPORTS ITS TABLE, so a hit in a document with several tables is actionable without
a second query.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mikemol.mdstruct import tables as md_tables

# How many cells of a row to render before truncating, so one wide row cannot flood a terminal.
_CELL_WIDTH = 40


def flag(argv: list[str], name: str) -> str | None:
    """Return a `--name value` or `--name=value` argument, or None."""
    for i, arg in enumerate(argv):
        if arg == name and i + 1 < len(argv):
            return argv[i + 1]
        if arg.startswith(name + "="):
            return arg.split("=", 1)[1]
    return None


def render_tables(tables: list[md_tables.Table]) -> list[str]:
    """Render one line per table: position, size, header."""
    return [
        f"  table {t.position}  {t.rows} row(s) x {t.cols} col(s)  {' | '.join(t.header)}"
        for t in tables
    ]


def render_rows(rows: list[md_tables.Row]) -> list[str]:
    """Render one line per row, prefixed with the table it came from."""
    return [
        f"  table {r.table}  " + " | ".join(cell[:_CELL_WIDTH] for cell in r.cells) for r in rows
    ]


def main(argv: list[str]) -> int:
    """Print the document's tables, or the rows a filter selects."""
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        sys.stderr.write("usage: md_tables_show.py FILE.md [--where <text>] [--table <n>]\n")
        return 2

    path = Path(args[0])
    if not path.exists():
        sys.stderr.write(f"md-tables: no such file: {path}\n")
        return 2

    where = flag(argv, "--where")
    at = flag(argv, "--table")
    position = int(at) if at is not None and at.isdigit() else None

    if where is None and position is None:
        found = md_tables.tables(path)
        if not found:
            sys.stdout.write(f"md-tables: {path} holds no tables\n")
            return 0
        sys.stdout.write("\n".join(render_tables(found)) + "\n")
        sys.stdout.write(f"  {len(found)} table(s) in {path}\n")
        return 0

    rows = md_tables.table_rows(path, position=position, where=where)
    if not rows:
        # ⚑ AN EMPTY RESULT IS A FACT ABOUT THE QUERY, and it says which query. A bare silence
        # cannot distinguish "no such name" from "the tool read nothing".
        sys.stdout.write(
            f"md-tables: no row in {path} matches "
            f"{where!r} (table {position if position is not None else 'any'})\n"
        )
        return 1

    sys.stdout.write("\n".join(render_rows(rows)) + "\n")
    sys.stdout.write(f"  {len(rows)} row(s) in {path}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE, and it DELEGATES rather than
# exiting 0 — a no-op guard reports nothing, which the outcome classifier calls `silent`.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import md_tables_show_selftest

        sys.exit(md_tables_show_selftest.selftest())
    sys.exit(main(sys.argv))
