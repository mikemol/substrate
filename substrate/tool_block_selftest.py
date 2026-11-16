#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_block` — content is owned, placement is not.

⚑⚑⚑ THE REFUSAL ARMS ARE THE ITEM. A sync that INSERTED missing markers would append dozens of
lines wherever it reached, and would silently restore a block a human deliberately removed — so
*"delete the block"* becomes an instruction nothing can carry out. Refusing keeps the editorial
decision with the editor and keeps a drift gate honest: absent markers are DRIFT, not something to
repair into a pass.

⚑⚑ AND THE `|` GUARD IS CORRECTNESS, NOT STYLE. The population reader parses every `|`-leading
line of the routing document as an `artifact | tool` row, and it reads the same document this
block is spliced into. A markdown table in the body makes a sync's OUTPUT its own INPUT: phantom
tools in the roster, a PreToolUse gate armed for artifacts nothing claims, and a sync that never
reaches a fixed point. An arm pins it, because nobody remembers a constraint this indirect.

⚑ THE THREE MARKER FAILURES WANT THREE DIFFERENT REPAIRS — add, de-duplicate, un-invert — so each
refusal is asserted to name its own, rather than a single "malformed" message that sends a reader
to diff the file.
"""

from __future__ import annotations

import sys

from substrate import tool_block

# The markers a fixture document carries.
_MARKERS = tool_block.Markers(begin="<!-- BEGIN -->", end="<!-- END -->", where="fixture.md")

# A document with exactly one well-formed pair.
_DOC = f"before\n{_MARKERS.begin}\nold body\n{_MARKERS.end}\nafter\n"

# The body a sync would write.
_BODY = "new body"

# How many lines the wrap fixture should produce at a narrow width.
_WRAPPED = 2


def a_body_is_spliced_between_the_markers(out: list[str]) -> int:
    """Check the region between the markers is replaced."""
    got = tool_block.splice(_DOC, _BODY, _MARKERS)
    if _BODY not in got or "old body" in got:
        out.append(f"selftest: the splice produced {got!r}")
        return 1
    return 0


def every_byte_outside_the_markers_survives(out: list[str]) -> int:
    """Check the splice touches nothing else — INCLUDING the markers themselves.

    ⚑ A SYNC CANNOT MOVE, DUPLICATE OR REFORMAT ITS OWN MARKERS. They are part of the preserved
    text, so only the region strictly between them is rewritten.
    """
    got = tool_block.splice(_DOC, _BODY, _MARKERS)
    if not got.startswith("before\n") or not got.endswith("after\n"):
        out.append(f"selftest: text outside the markers changed: {got!r}")
        return 1
    if got.count(_MARKERS.begin) != 1 or got.count(_MARKERS.end) != 1:
        out.append("selftest: the markers were duplicated or dropped")
        return 1
    return 0


def absent_markers_refuse_rather_than_insert(out: list[str]) -> int:
    """Check a document with no markers is refused — THE PLACEMENT ARM.

    ⚑⚑ INSERTING WOULD SILENTLY RESTORE A BLOCK SOMEONE DELETED, making removal an instruction
    nothing can carry out. It would also append dozens of lines with none of the prose that
    introduces them.
    """
    try:
        tool_block.splice("no markers here\n", _BODY, _MARKERS)
    except tool_block.BlockError as exc:
        if "add the two marker lines" not in str(exc):
            out.append(f"selftest: the refusal does not name the remedy: {exc}")
            return 1
        return 0
    out.append("selftest: a markerless document was spliced rather than refused")
    return 1


def duplicate_markers_refuse(out: list[str]) -> int:
    """Check an ambiguous document is refused — a sync cannot know which pair it owns."""
    doubled = _DOC + _DOC
    try:
        tool_block.splice(doubled, _BODY, _MARKERS)
    except tool_block.BlockError as exc:
        if "exactly one of each" not in str(exc):
            out.append(f"selftest: the duplicate refusal reads as {exc}")
            return 1
        return 0
    out.append("selftest: a document with two marker pairs was spliced")
    return 1


def inverted_markers_refuse(out: list[str]) -> int:
    """Check a reversed pair is refused and NAMED as inverted.

    ⚑ THE THREE FAILURES WANT THREE REPAIRS. Reporting this as "malformed" would send a reader to
    diff a document whose problem is one word long.
    """
    inverted = f"{_MARKERS.end}\nbody\n{_MARKERS.begin}\n"
    try:
        tool_block.splice(inverted, _BODY, _MARKERS)
    except tool_block.BlockError as exc:
        if "inverted" not in str(exc):
            out.append(f"selftest: the inversion refusal reads as {exc}")
            return 1
        return 0
    out.append("selftest: inverted markers were spliced")
    return 1


def a_table_row_in_the_body_is_reported(out: list[str]) -> int:
    """Check a `|`-leading line is caught — THE SELF-REFERENCE GUARD.

    ⚑⚑⚑ THE POPULATION READER PARSES `|`-LEADING LINES OF THIS SAME DOCUMENT as routing rows, so
    a markdown table in the body makes a sync's output its own input — phantom tools, a gate armed
    for artifacts nothing claims, and no fixed point. Nobody remembers a constraint this indirect,
    which is why it is a check rather than a convention.
    """
    got = tool_block.leads_forbidden("fine\n| artifact | tool |\nalso fine\n")
    if len(got) != 1:
        out.append(f"selftest: the table row was not caught: {got!r}")
        return 1
    return 0


def an_indented_table_row_is_still_caught(out: list[str]) -> int:
    """Check leading whitespace does not hide the hazard.

    ⚑ THE READER STRIPS BEFORE MATCHING, so an indented row is read as a routing declaration just
    the same — and a guard that only saw column zero would pass the body that breaks it.
    """
    if not tool_block.leads_forbidden("    | artifact | tool |\n"):
        out.append("selftest: an indented table row was not caught")
        return 1
    return 0


def an_ordinary_body_is_clean(out: list[str]) -> int:
    """Check the guard does not fire on text that merely contains a pipe."""
    if tool_block.leads_forbidden("a | b inline is fine\n```\ncode | here\n```\n"):
        out.append("selftest: an inline pipe was reported as a table row")
        return 1
    return 0


def a_current_document_reports_as_current(out: list[str]) -> int:
    """Check currency is decided through the splice, not by diffing bodies.

    ⚑⚑ THE FRAMING NEWLINES BELONG TO THE SPLICE, NOT THE BODY. Comparing bodies directly reports
    drift on a document byte-identical to what a sync would write — a gate failing over its own
    formatting.
    """
    synced = tool_block.splice(_DOC, _BODY, _MARKERS)
    if not tool_block.is_current(synced, _BODY, _MARKERS):
        out.append("selftest: a freshly synced document reads as drifted")
        return 1
    if tool_block.is_current(_DOC, _BODY, _MARKERS):
        out.append("selftest: a stale document reads as current")
        return 1
    return 0


def the_body_is_readable_without_splicing(out: list[str]) -> int:
    """Check what is on disk can be read back for comparison."""
    if "old body" not in tool_block.current_body(_DOC, _MARKERS):
        out.append("selftest: the current body was not readable")
        return 1
    return 0


def wrapping_packs_items_onto_few_lines(out: list[str]) -> int:
    """Check the wrapper fills to the width rather than one item per line."""
    got = tool_block.wrap(("alpha", "beta", "gamma", "delta"), "  ", width=20)
    if len(got) != _WRAPPED:
        out.append(f"selftest: the wrap produced {len(got)} line(s): {got!r}")
        return 1
    if not all(line.startswith("  ") for line in got):
        out.append(f"selftest: the indent was not applied: {got!r}")
        return 1
    return 0


_ARMS = (
    a_body_is_spliced_between_the_markers,
    every_byte_outside_the_markers_survives,
    absent_markers_refuse_rather_than_insert,
    duplicate_markers_refuse,
    inverted_markers_refuse,
    a_table_row_in_the_body_is_reported,
    an_indented_table_row_is_still_caught,
    an_ordinary_body_is_clean,
    a_current_document_reports_as_current,
    the_body_is_readable_without_splicing,
    wrapping_packs_items_onto_few_lines,
)

_CASE_COUNT = 1 + 2 + 2 + 2 + 2 + 1 + 1 + 1 + 2 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-block selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-block selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
