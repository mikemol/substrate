#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_tables_show` — the ONE `_show` module holding its own logic.

⚑⚑⚑ WHY THIS RENDERER GETS A SUITE WHEN ITS SIBLINGS DO NOT. `md_spans_show`, `kind_partition_show`
and `suite_gap_report` are argument-check-plus-print over a reader that is separately covered, and
each already DELEGATES `--selftest` to that reader's suite. This one is different: `flag` is a
hand-rolled two-spelling argument parser that no reader's suite exercises, and a filter silently
read as absent turns a targeted query into a full listing — the tool answering a question the
caller did not ask, with no error to say so.

⚑⚑ THE PARSER'S FAILURE MODE IS THE SUBJECT. `--where` missing its value, `--where=` with an empty
one, and a flag that is the LAST argument are the three inputs where a naive `argv[i + 1]` either
raises or silently consumes the wrong token. Each is an arm, because none of them announces
itself: the tool prints a plausible listing either way.

⚑⚑ AND A NON-NUMERIC `--table` FALLS BACK TO `None`, WHICH IS A REAL DECISION RATHER THAN A GAP.
`--table abc` means the position filter does not apply — so the tool lists tables instead of rows.
That is defensible and it is also how a typo becomes a wrong answer, so the behaviour is pinned
where a reader can see it rather than left to be rediscovered from a surprising listing.

⚑ THE RENDER ARMS ASSERT THE TRUNCATION AND ITS ABSENCE TOGETHER. `_CELL_WIDTH` exists so one wide
row cannot flood a terminal; a case checking only that long cells are cut would pass against a
renderer that cut everything, so the short-cell half sits beside it.
"""

from __future__ import annotations

import sys

from mikemol.mdstruct import tables as md_tables

from substrate import md_tables_show

# The usage refusal — distinct from a query that ran and matched nothing.
_USAGE = 2


def _table(position: int = 1) -> md_tables.Table:
    """Return one table summary."""
    return md_tables.Table(position=position, rows=2, cols=2, header=("name", "kind"))


def _row(cells: tuple[str, ...], table: int = 1) -> md_tables.Row:
    """Return one table row."""
    return md_tables.Row(table=table, cells=cells)


def a_separated_flag_value_is_read(out: list[str]) -> int:
    """Check `--where value` resolves — the spelling a caller types most often."""
    got = md_tables_show.flag(["tool", "doc.md", "--where", "thing"], "--where")
    if got != "thing":
        out.append(f"selftest: a separated flag value read as {got!r}")
        return 1
    return 0


def an_equals_flag_value_is_read(out: list[str]) -> int:
    """Check `--where=value` resolves — the second spelling, parsed by a different branch."""
    got = md_tables_show.flag(["tool", "doc.md", "--where=thing"], "--where")
    if got != "thing":
        out.append(f"selftest: an equals-form flag value read as {got!r}")
        return 1
    return 0


def an_absent_flag_reads_none(out: list[str]) -> int:
    """Check a flag nobody passed is None — THE DISCRIMINATOR.

    ⚑⚑ WITHOUT THIS A PARSER RETURNING A CONSTANT passes both arms above. `None` is what makes
    the caller's `where is None and position is None` branch fire, so a parser that always found
    something would turn every invocation into a filtered query.
    """
    if md_tables_show.flag(["tool", "doc.md"], "--where") is not None:
        out.append("selftest: an unpassed flag returned a value")
        return 1
    return 0


def a_trailing_flag_with_no_value_reads_none(out: list[str]) -> int:
    """Check a flag in final position does not run off the end of `argv`.

    ⚑⚑ THIS IS THE INPUT A NAIVE `argv[i + 1]` RAISES ON. `--where` typed with no value is an
    ordinary typo; the honest answer is that no filter was given, not an IndexError out of a
    print tool.
    """
    if md_tables_show.flag(["tool", "doc.md", "--where"], "--where") is not None:
        out.append("selftest: a valueless trailing flag returned a value")
        return 1
    return 0


def an_empty_equals_value_is_not_none(out: list[str]) -> int:
    """Check `--where=` yields the empty string, which is a VALUE the caller supplied.

    ⚑ EMPTY AND ABSENT ARE DIFFERENT FACTS here too. `--where=` is a filter matching everything;
    no `--where` at all is no filter. A parser collapsing them makes the two invocations
    indistinguishable, and only one of them was asked.
    """
    got = md_tables_show.flag(["tool", "doc.md", "--where="], "--where")
    if got != "":
        out.append(f"selftest: an empty equals-form value read as {got!r}")
        return 1
    return 0


def one_flag_does_not_answer_for_another(out: list[str]) -> int:
    """Check the two flags are read independently, so a prefix cannot cross-match."""
    argv = ["tool", "doc.md", "--where", "thing", "--table", "2"]
    if md_tables_show.flag(argv, "--where") != "thing":
        out.append("selftest: --where did not resolve alongside --table")
        return 1
    if md_tables_show.flag(argv, "--table") != "2":
        out.append("selftest: --table did not resolve alongside --where")
        return 1
    if md_tables_show.flag(argv, "--missing") is not None:
        out.append("selftest: an undeclared flag matched another flag's value")
        return 1
    return 0


def a_flag_value_that_looks_like_a_flag_is_still_taken(out: list[str]) -> int:
    """Check the parser does not second-guess a value beginning with a dash.

    ⚑ RECORDED AS BEHAVIOUR, NOT ENDORSED. `--where --table` reads `--table` as the search text,
    which is what a positional read does. Pinning it means the day someone wants the stricter
    parser, this case tells them what changes rather than the change being silent.
    """
    got = md_tables_show.flag(["tool", "doc.md", "--where", "--table"], "--where")
    if got != "--table":
        out.append(f"selftest: a dash-leading flag value read as {got!r}")
        return 1
    return 0


def tables_render_with_their_position_and_size(out: list[str]) -> int:
    """Check a table summary carries what a follow-up query needs.

    ⚑ THE POSITION IS THE ACTIONABLE FIELD — it is what `--table <n>` takes. A summary without
    it names a table the caller cannot then select.
    """
    line = md_tables_show.render_tables([_table(position=3)])[0]
    if "table 3" not in line:
        out.append(f"selftest: the table summary omits its position: {line!r}")
        return 1
    if "2 row(s)" not in line or "2 col(s)" not in line:
        out.append(f"selftest: the table summary omits its size: {line!r}")
        return 1
    if "name | kind" not in line:
        out.append(f"selftest: the table summary omits its header: {line!r}")
        return 1
    return 0


def a_row_is_prefixed_with_the_table_it_came_from(out: list[str]) -> int:
    """Check rows from a multi-table document stay attributable.

    ⚑⚑ A FILTERED QUERY CROSSES TABLES. Without the prefix, two rows with the same cells from
    different tables are indistinguishable in the output, and the reader cannot tell which
    table to go and edit.
    """
    lines = md_tables_show.render_rows([_row(("a", "b"), table=1), _row(("a", "b"), table=7)])
    if "table 1" not in lines[0] or "table 7" not in lines[1]:
        out.append(f"selftest: rows are not attributed to their tables: {lines!r}")
        return 1
    if lines[0] == lines[1]:
        out.append("selftest: identical cells from different tables render identically")
        return 1
    return 0


def a_wide_cell_is_truncated(out: list[str]) -> int:
    """Check one long cell cannot flood the terminal."""
    width = md_tables_show._CELL_WIDTH  # noqa: SLF001 — the bound under test
    line = md_tables_show.render_rows([_row(("x" * (width * 3),))])[0]
    if "x" * (width + 1) in line:
        out.append(f"selftest: a cell longer than {width} was rendered whole")
        return 1
    if "x" * width not in line:
        out.append(f"selftest: a wide cell was cut below the width: {line!r}")
        return 1
    return 0


def a_narrow_cell_is_left_alone(out: list[str]) -> int:
    """Check truncation is conditional — the other half, so a cutter is not a constant."""
    line = md_tables_show.render_rows([_row(("short", "also short"))])[0]
    if "short | also short" not in line:
        out.append(f"selftest: cells inside the width were altered: {line!r}")
        return 1
    return 0


def main_refuses_with_no_document_named(out: list[str]) -> int:
    """Check a usage refusal is its own exit code, not a report over nothing."""
    if md_tables_show.main(["md_tables_show.py"]) != _USAGE:
        out.append("selftest: an argument-free invocation did not refuse")
        return 1
    return 0


def main_refuses_an_absent_document(out: list[str]) -> int:
    """Check a missing file is named rather than read as a document with no tables.

    ⚑⚑ ABSENT AND EMPTY ARE OPPOSITE FACTS. `holds no tables` over a path that does not exist
    would send a reader to check their document instead of their spelling.
    """
    if md_tables_show.main(["md_tables_show.py", "/nonexistent/doc.md"]) != _USAGE:
        out.append("selftest: an absent document did not refuse")
        return 1
    return 0


_ARMS = (
    a_separated_flag_value_is_read,
    an_equals_flag_value_is_read,
    an_absent_flag_reads_none,
    a_trailing_flag_with_no_value_reads_none,
    an_empty_equals_value_is_not_none,
    one_flag_does_not_answer_for_another,
    a_flag_value_that_looks_like_a_flag_is_still_taken,
    tables_render_with_their_position_and_size,
    a_row_is_prefixed_with_the_table_it_came_from,
    a_wide_cell_is_truncated,
    a_narrow_cell_is_left_alone,
    main_refuses_with_no_document_named,
    main_refuses_an_absent_document,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 3 + 1 + 3 + 2 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"md-tables-show selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"md-tables-show selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
