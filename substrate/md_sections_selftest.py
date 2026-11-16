#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_sections` — what a rewrite must not touch.

⚑⚑⚑ THE HEADING-SURVIVES CASE IS THE LOAD-BEARING ONE. The heading is the anchor every other
reader resolves against — spans, coherence, the item census, and this module's own finder — so a
rewrite that altered it would silently orphan every reference pointing at that section. The
failure would surface far away, as a lookup that stopped matching.

⚑⚑ AND THE NEIGHBOURS-SURVIVE CASE IS WHY A SPLICE WAS CHOSEN OVER AN AST RENDER. A render is
admissible and rewrites the WHOLE document, so a five-line edit arrives as a whole-file diff. A
case that pins the untouched sections is what keeps a future "just re-render it" from passing
review.

⚑ THE BLANK-LINE CASE LOOKS COSMETIC AND IS NOT. Markdown block separation is load-bearing: an
append that swallows the blank line before the next heading produces a document that RENDERS
differently from the one the author reviewed.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from substrate import md_sections

# A document with three sections, blank-line separation, and distinct bodies.
_FIXTURE = """# Top

## First

first body line

## Second

second body line

## Third

third body line
"""


def _have_pandoc() -> bool:
    """Report whether the converter is present on this machine."""
    return shutil.which("pandoc") is not None


def _doc(d: str) -> Path:
    """Write the fixture document and return its path."""
    path = Path(d) / "doc.md"
    path.write_text(_FIXTURE, encoding="utf-8")
    return path


def a_replace_keeps_the_heading(out: list[str]) -> int:
    """Check the heading line survives a body replacement.

    ⚑ THE ANCHOR. Every other reader resolves sections by heading text; moving it would orphan
    the references silently, and the breakage would appear somewhere else entirely.
    """
    with tempfile.TemporaryDirectory() as d:
        got, _span = md_sections.replace_section(_doc(d), "Second", "REPLACED\n")
    bad = 0
    if "## Second" not in got:
        out.append("selftest: the heading was lost in a replace")
        bad += 1
    if "REPLACED" not in got:
        out.append("selftest: the new body did not land")
        bad += 1
    return bad


def a_replace_leaves_neighbours_alone(out: list[str]) -> int:
    """Check the sections either side are byte-identical after a replace.

    ⚑ THE ARGUMENT FOR A SPLICE OVER A RENDER, as a case rather than a comment.
    """
    with tempfile.TemporaryDirectory() as d:
        got, _span = md_sections.replace_section(_doc(d), "Second", "REPLACED\n")
    bad = 0
    if "first body line" not in got:
        out.append("selftest: the preceding section was altered")
        bad += 1
    if "third body line" not in got:
        out.append("selftest: the following section was altered")
        bad += 1
    if "second body line" in got:
        out.append("selftest: the replaced body survived")
        bad += 1
    return bad


def an_append_lands_inside_the_section(out: list[str]) -> int:
    """Check appended text lands before the NEXT heading, not at end-of-file.

    ⚑ THE BOUNDED FORM OF `>>`. A shell append puts content under whatever heading happens to
    be last, which for a sectioned document is almost never where it belongs.
    """
    with tempfile.TemporaryDirectory() as d:
        got, _span = md_sections.append_to_section(_doc(d), "First", "ADDED\n")
    lines = got.split("\n")
    try:
        added = lines.index("ADDED")
        second = lines.index("## Second")
    except ValueError:
        out.append("selftest: the appended line or the next heading is missing")
        return 1
    if added > second:
        out.append("selftest: the append landed after the next heading")
        return 1
    return 0


def an_append_keeps_the_blank_line(out: list[str]) -> int:
    """Check the blank line before the next heading survives.

    ⚑ NOT COSMETIC. Block separation decides how the document renders, so swallowing it
    produces output unlike what the author reviewed — a silent formatting change riding along
    with a content edit.
    """
    with tempfile.TemporaryDirectory() as d:
        got, _span = md_sections.append_to_section(_doc(d), "First", "ADDED\n")
    lines = got.split("\n")
    second = lines.index("## Second")
    if second == 0 or lines[second - 1].strip():
        out.append("selftest: the blank line before the next heading was swallowed")
        return 1
    return 0


def a_write_returns_the_span_it_hit(out: list[str]) -> int:
    """Check the caller is told which section was targeted.

    ⚑ A WRITE THAT SAYS ONLY "done" leaves a reader to re-derive what moved.
    """
    with tempfile.TemporaryDirectory() as d:
        _got, span = md_sections.replace_section(_doc(d), "Second", "X\n")
    if span.text != "Second":
        out.append(f"selftest: the reported span is {span.text!r}")
        return 1
    return 0


def an_ambiguous_target_refuses(out: list[str]) -> int:
    """Check a needle matching two headings raises before writing anything.

    ⚑ THE TARGET IS A WRITE, so picking the earlier match is the silent-wrong-target class and
    a rewrite is not recoverable by re-running.
    """
    with tempfile.TemporaryDirectory() as d:
        try:
            md_sections.replace_section(_doc(d), "ir", "X\n")  # First AND Third
        except LookupError:
            return 0
    out.append("selftest: an ambiguous target was written")
    return 1


_ARMS = (
    a_replace_keeps_the_heading,
    a_replace_leaves_neighbours_alone,
    an_append_lands_inside_the_section,
    an_append_keeps_the_blank_line,
    a_write_returns_the_span_it_hit,
    an_ambiguous_target_refuses,
)

_CASE_COUNT = 2 + 3 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    if not _have_pandoc():
        # ⚑ A DECLARED SKIP, NEVER A SILENT PASS. Section bounds come from the parser, and
        # reporting these green without it would claim a measurement nobody took.
        sys.stdout.write("md-sections selftest: SKIP — pandoc is not on this machine\n")
        sys.stdout.write("md-sections selftest: 0/0\n")
        return 0

    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"md-sections selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"md-sections selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
