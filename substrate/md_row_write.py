# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Append one row to a markdown table from the command line.

The CLI over `substrate.md_table_row`, which owns the splice and its refusals. Split for
the reason its sibling `md_write` is split from `md_sections`: the library is importable
by a caller that has already decided what to write, and the dispatch is a separate job
with its own failure modes.

⚑ NEITHER `--apply` NOR `--dry-run` DEFAULTS, matching this toolkit's converged contract.
A default-dry silently does nothing when you meant to write; a default-apply silently
writes when you meant to look. Intent must be stated.

⚑⚑ AND A FLAG'S VALUE IS NOT AN OPERAND. Reading argv as "everything without a leading
dash" counts `--table`'s value as a cell, so a correct invocation is refused for having
one cell too many — the defect `md_write` records and fixes the same way.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import md_table_row

_USAGE = """\
usage: md_row_write.py <file> <cell> [<cell> ...] [--table SUBSTR] (--apply | --dry-run)

Append one row to a markdown table, as a line splice.

  --table SUBSTR   name the table by a substring of its header row; required when the
                   document holds more than one table
  --apply          write the file
  --dry-run        report the row that would be written, and write nothing

⚑ REFUSES an ambiguous table (naming its candidates), a header substring matching none,
  and a row whose cell count disagrees with the header. A row padded or truncated to fit
  is a table that still parses and no longer means what its header says.
"""

_FLAGS_WITH_VALUE = ("--table",)


def _operands(argv: list[str]) -> list[str]:
    """Return argv's operands, excluding flags and the values they consume."""
    out: list[str] = []
    for i, arg in enumerate(argv):
        if arg.startswith("--"):
            continue
        if i and argv[i - 1] in _FLAGS_WITH_VALUE:
            continue
        out.append(arg)
    return out


def _value_after(argv: list[str], flag: str) -> str | None:
    """Return the value following `flag`, or None when it is absent or last."""
    if flag not in argv:
        return None
    at = argv.index(flag)
    return argv[at + 1] if at + 1 < len(argv) else None


def main(argv: list[str]) -> int:
    """Read argv, perform or preview one row append, and return an exit code."""
    if not argv or "--help" in argv or "-h" in argv:
        sys.stdout.write(_USAGE)
        return 0

    apply_it = "--apply" in argv
    if apply_it == ("--dry-run" in argv):
        sys.stderr.write("md_row_write: state exactly one of --apply / --dry-run\n")
        return 2

    operands = _operands(argv)
    if len(operands) < 2:  # noqa: PLR2004 — a file and at least one cell
        sys.stderr.write("md_row_write: need <file> and at least one cell\n")
        sys.stderr.write(_USAGE)
        return 2

    path = Path(operands[0])
    cells = operands[1:]
    try:
        row = md_table_row.append_row(
            path,
            cells,
            _value_after(argv, "--table"),
            apply=apply_it,
        )
    except md_table_row.TableError as exc:
        sys.stderr.write(f"md_row_write: {exc}\n")
        return 2
    except OSError as exc:
        sys.stderr.write(f"md_row_write: {exc}\n")
        return 2

    verb = "wrote" if apply_it else "would write"
    sys.stdout.write(f"md_row_write: {verb} {row}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
