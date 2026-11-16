# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.md_table_row` — the bounded table-row writer.

⚑ THE REFUSALS ARE THE LOAD-BEARING HALF. A writer that pads a short row or drops a long
one produces a table that still parses and no longer means what its header says, and
nothing downstream reports it. Those cases are asserted as firmly as the successful write.

⚑⚑ AND THE SPLICE MUST BE A ONE-LINE DIFF. `mdstruct`'s section writers are line splices
for a stated reason — pandoc normalises, so an AST round-trip reflows prose and re-wraps
tables — so a case pins that every line outside the insertion point is byte-identical
after a write. Without it, a future AST-based rewrite would pass every other case here.

⚑ SELECTION IS EXERCISED THROUGH THE PUBLIC WRITE PATH, not by calling the private
chooser. A case that reaches past the surface it is testing stops being evidence about
what a caller can do — the first cut here did exactly that and the gate refused it.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from substrate import md_table_row

TABLES_IN_DOC = 2

_DOC = """\
# a document

Some prose with a | pipe in it, which is not a table.

| concern | threads |
|---|---|
| draining toolmodes | Ⓝ31h |
| false zeros | Ⓝ68b |

Trailing prose.

| tool | state |
|---|---|
| md_write | shipped |
"""


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    lines = _DOC.splitlines()
    found = md_table_row.tables(lines)

    # ── finding tables ───────────────────────────────────────────────────────
    check("both tables are found", passed=len(found) == TABLES_IN_DOC)
    # ⚑ The prose line carries a pipe and must NOT be read as a table.
    check(
        "a prose line with a pipe is not a table",
        passed=all("prose" not in " ".join(t.header) for t in found),
    )
    check("the header is read", passed=found[0].header == ("concern", "threads"))
    check(
        "the extent stops at the blank line",
        passed=found[0].last_line == lines.index("| false zeros | Ⓝ68b |"),
    )

    def write(where: str | None, cells: list[str]) -> tuple[bool, list[str]]:
        """Attempt a write in a throwaway copy; report (refused, resulting lines)."""
        with tempfile.TemporaryDirectory() as tmp:
            doc = Path(tmp) / "d.md"
            doc.write_text(_DOC, encoding="utf-8")
            try:
                md_table_row.append_row(doc, cells, where, apply=True)
            except md_table_row.TableError:
                return True, []
            return False, doc.read_text(encoding="utf-8").splitlines()

    # ── THE REFUSALS ─────────────────────────────────────────────────────────
    refused, _ = write(None, ["a", "b"])
    check("an unnamed table refuses when the document holds several", passed=refused)
    refused, _ = write("no-such-header", ["a", "b"])
    check("a header substring matching nothing refuses", passed=refused)
    refused, _ = write("concern", ["only-one"])
    check("a short row refuses rather than being padded", passed=refused)
    refused, _ = write("concern", ["a", "b", "c"])
    check("a long row refuses rather than being truncated", passed=refused)

    # ── selection, through the public path ───────────────────────────────────
    refused, second = write("tool", ["md_table_row", "shipped"])
    check("a header substring selects the second table", passed=not refused)
    check(
        "and the row lands in THAT table, not the first",
        passed=bool(second) and second[-1] == "| md_table_row | shipped |",
    )

    # ── the write, and its diff ──────────────────────────────────────────────
    with tempfile.TemporaryDirectory() as tmp:
        doc = Path(tmp) / "d.md"
        doc.write_text(_DOC, encoding="utf-8")
        # ⚑ Without apply nothing is written: the preview is not the write.
        preview = md_table_row.append_row(doc, ["bazel", "Ⓝ133h"], "concern")
        check("a dry run returns the row", passed=preview == "| bazel | Ⓝ133h |")
        check("a dry run writes nothing", passed=doc.read_text(encoding="utf-8") == _DOC)

    _, after = write("concern", ["bazel", "Ⓝ133h"])
    cut = found[0].last_line + 1
    check(
        "the row lands in the named table", passed=bool(after) and after[cut] == "| bazel | Ⓝ133h |"
    )
    check("exactly one line is added", passed=len(after) == len(lines) + 1)
    # ⚑ EVERY OTHER LINE IS BYTE-IDENTICAL — the property an AST render would break.
    check(
        "no other line changes",
        passed=after[:cut] == lines[:cut] and after[cut + 1 :] == lines[cut:],
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
