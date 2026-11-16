#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_pandoc` — the re-attach rule, in both directions.

⚑⚑⚑ BOTH DIRECTIONS ARE THE POINT, because getting either one wrong was a real defect and they
fail oppositely. NOT re-attaching lost a memory's identity (`name:`, `type:`,
`originSessionId:`) through a markdown round-trip while two gates reported success. Re-attaching
UNCONDITIONALLY prepended a YAML head to JSON output, so the AST parser read a document opening
with `---` and died at char 0 — every structural mode blind to frontmatter'd markdown, which is
every governed doc and every SKILL.md.

⚑ SO THE PREDICATE IS THE WRITER, AND ONE CASE EACH WAY IS WHAT PINS IT. A single case in
either direction passes while the other defect is live.
"""

from __future__ import annotations

import shutil
import sys

from substrate import md_pandoc

# A document whose frontmatter must survive a markdown round-trip and must NOT reach a JSON one.
_HEAD = "---\nname: probe\n---\n"
_BODY = "# A heading\n\nSome prose.\n"


def _have_pandoc() -> bool:
    """Report whether the converter is present on this machine."""
    return shutil.which("pandoc") is not None


def markdown_keeps_the_frontmatter(out: list[str]) -> int:
    """Check a markdown writer gets the head back.

    ⚑ THE LOSS THIS PREVENTS WAS SILENT AND GRADED GREEN. A memory converted without this kept
    its prose and lost its identity, while the round-trip check called the drift expected.
    """
    got = md_pandoc.convert(_HEAD + _BODY, "markdown")
    if not got.startswith("---"):
        out.append(f"selftest: a markdown conversion dropped the frontmatter: {got[:40]!r}")
        return 1
    return 0


def json_does_not_get_the_frontmatter(out: list[str]) -> int:
    """Check a non-markdown writer's output is not prefixed with YAML.

    ⚑ THE OPPOSITE DEFECT, AND THE MORE DAMAGING ONE: a JSON document prefixed with `---` fails
    to parse at char 0, which took out every AST-backed mode on every frontmatter'd file.
    """
    got = md_pandoc.convert(_HEAD + _BODY, "json")
    if got.lstrip().startswith("---"):
        out.append("selftest: a JSON conversion was prefixed with frontmatter")
        return 1
    if not got.lstrip().startswith(("{", "[")):
        out.append(f"selftest: the JSON conversion does not look like JSON: {got[:40]!r}")
        return 1
    return 0


def a_dialect_still_counts_as_markdown(out: list[str]) -> int:
    """Check the writer predicate is a PREFIX test, not an equality test.

    ⚑ AN EQUALITY CHECK WOULD SILENTLY STOP PRESERVING the first time someone asked for
    `markdown_strict` or `gfm` — the failure would be a missing head, not an error.
    """
    got = md_pandoc.convert(_HEAD + _BODY, "gfm")
    if not got.startswith("---"):
        out.append("selftest: a gfm conversion dropped the frontmatter")
        return 1
    return 0


def a_failed_conversion_raises(out: list[str]) -> int:
    """Check a rejected format is an error, not an empty string.

    ⚑ AN EMPTY RETURN WOULD READ AS AN EMPTY DOCUMENT, and a caller writing that back would
    truncate the file it was converting.
    """
    try:
        md_pandoc.convert(_BODY, "not-a-real-format")
    except RuntimeError:
        return 0
    out.append("selftest: an invalid writer did not raise")
    return 1


_ARMS = (
    markdown_keeps_the_frontmatter,
    json_does_not_get_the_frontmatter,
    a_dialect_still_counts_as_markdown,
    a_failed_conversion_raises,
)

_CASE_COUNT = 1 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    if not _have_pandoc():
        # ⚑ A DECLARED SKIP, NEVER A SILENT PASS. Without the converter these cases cannot run,
        # and reporting them green would claim a measurement nobody took.
        sys.stdout.write("md-pandoc selftest: SKIP — pandoc is not on this machine\n")
        sys.stdout.write("md-pandoc selftest: 0/0\n")
        return 0

    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"md-pandoc selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"md-pandoc selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
