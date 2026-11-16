# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_cells` — the AST half that `table_fit` was waiting for.

⚑⚑⚑ THE FIXTURES ARE MARKDOWN DRIVEN THROUGH PANDOC, BY OPERATOR RULING, and the alternative is
why. Constructing panflute ASTs directly would need `stubs/panflute/__init__.pyi` widened — it is a
hand-written narrowing declaring exactly what substrate's readers consume, with no `Str` and
different constructor arities — and widening shared type machinery on behalf of a test is a larger
act than the case is worth. So each fixture is the markdown that PRODUCES the shape, which also
means the cases exercise the real parser rather than my model of it.

⚑⚑ THE THREE-OUTCOME HEADER ARM IS THE ONE THE ORIGIN COLLAPSED. It caught every exception and fell
through to an empty header, so *could not read the head* and *there is no head* produced the same
verdict on tables that need different responses. `table_read.Table` records the identical repair on
the text side, which is why the two agree on `None` versus `()`.

⚑ AND THE COMPOSITION ARM IS WHY THIS MODULE EXISTS. `table_fit` holds the precedence and had ONE
importer — its own suite — so the verdict half was reachable by nothing. A case drives both
together, which is the only assertion that shows the seam is closed.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import md_ast, md_cells, table_fit, table_read

if TYPE_CHECKING:
    import panflute

#: A table nothing blocks — single-line inline cells under a header.
PLAIN = """| h | i |
|---|---|
| a | b |
"""

#: ⚑ A CELL HOLDING A LIST — a block pipe syntax cannot express at any width. Written as a grid
#: table because that is the only markdown syntax that can carry one.
LISTED = """+-------+
| h     |
+=======+
| - one |
| - two |
+-------+
"""

#: ⚑ A CELL HOLDING TWO PARAGRAPHS — two blocks even though each alone would fit.
TWO_BLOCKS = """+-------+
| h     |
+=======+
| one   |
|       |
| two   |
+-------+
"""

#: A table with no header row at all.
HEADLESS = """+-----+-----+
| a   | b   |
+-----+-----+
"""


def _doc(src: str) -> panflute.Doc:
    """Return the parsed document for `src`, via a temporary file the reader can open."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "fixture.md"
        path.write_text(src, encoding="utf-8")
        return md_ast.ast(path)


def _only_table(src: str) -> panflute.Table:
    """Return the single table `src` produces, or raise when it produced none."""
    found = md_cells.tables(_doc(src))
    if not found:
        msg = f"fixture produced no table: {src!r}"
        raise AssertionError(msg)
    return found[0]


def _verdict_for(src: str) -> table_fit.Reason | None:
    """Return the pipe-table verdict for `src`, reading the cells and applying the precedence."""
    table = _only_table(src)
    cells = md_cells.read(table)
    return table_fit.blocked(
        table_read.Table(0, md_cells.header_cells(table), ()),
        cell_blocks=cells.blocks,
        cell_breaks=cells.breaks,
    )


def _plain_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a table nothing blocks."""
    out: list[tuple[str, bool]] = []
    got = md_cells.read(_only_table(PLAIN))

    out.append((f"an inline table is readable: {got.why()}", got.readable))
    out.append((f"and holds no block: {got.blocks}", not got.blocks))
    out.append((f"and holds no break: {got.breaks}", not got.breaks))
    return out


def _block_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for cells pipe syntax cannot express."""
    out: list[tuple[str, bool]] = []

    listed = md_cells.read(_only_table(LISTED))
    out.append((f"a list cell is a block: {listed.why()}", listed.blocks))

    # ⚑⚑ THE CONDITION EASY TO MISS. Two paragraphs are two blocks even though each alone fits.
    twice = md_cells.read(_only_table(TWO_BLOCKS))
    out.append((f"two inline blocks are still blocked: {twice.why()}", twice.blocks))

    # ⚑ THE SENSITIVITY ARM. The same grid shape with ONE paragraph must clear it, or the block
    # count is not what decided and this arm proves nothing.
    once = md_cells.read(_only_table(TWO_BLOCKS.replace("|       |\n| two   |\n", "")))
    out.append((f"dropping ONLY the second block clears it: {once.why()}", not once.blocks))
    return out


def _header_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the header outcomes.

    ⚑⚑⚑ `None` AND `()` ARE DIFFERENT ANSWERS. The origin returned the same verdict for both, so
    a table it could not read was reported as a table with no header — a confident claim built on
    a failed read.
    """
    out: list[tuple[str, bool]] = []

    named = md_cells.header_cells(_only_table(PLAIN))
    out.append((f"a header row is read: {named}", named == ("h", "i")))

    absent = md_cells.header_cells(_only_table(HEADLESS))
    out.append((f"a headerless table reports (): {absent}", absent == ()))
    out.append((f"and () is not None: {absent!r}", absent is not None))
    return out


def _composition_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` driving `md_cells` into `table_fit` — the closed seam.

    ⚑⚑⚑ `table_fit` HELD THE PRECEDENCE AND HAD ONE IMPORTER, ITS OWN SUITE. Every arm above tests
    this module alone and would pass with the verdict half still unreachable; these drive both, so
    the assertion is that the capability is whole.
    """
    out: list[tuple[str, bool]] = []

    out.append(
        (
            f"a block cell reaches the BLOCK reason: {_verdict_for(LISTED)}",
            _verdict_for(LISTED) == table_fit.Reason.BLOCK,
        )
    )
    out.append(
        (f"and an inline table is not blocked: {_verdict_for(PLAIN)}", _verdict_for(PLAIN) is None)
    )

    # ⚑ THE PRECEDENCE IS `table_fit`'s AND THIS PROVES IT REACHES: a headerless table reports
    # NO_HEADER even though its cells are clean.
    out.append(
        (
            f"a headerless table reports NO_HEADER: {_verdict_for(HEADLESS)}",
            _verdict_for(HEADLESS) == table_fit.Reason.NO_HEADER,
        )
    )
    return out


def _walk_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for finding tables in a document."""
    out: list[tuple[str, bool]] = []

    found = md_cells.tables(_doc("prose\n\n" + PLAIN + "\nmore prose\n"))
    out.append((f"a table among prose is found: {len(found)}", len(found) == 1))

    none = md_cells.tables(_doc("just prose, no table\n"))
    out.append((f"a document with no table yields none: {none}", none == []))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _plain_cases() + _block_cases() + _header_cases() + _composition_cases() + _walk_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-cells selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
