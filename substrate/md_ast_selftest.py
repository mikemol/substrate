#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_ast` — headers that a line scan gets wrong, and anchor keys.

⚑⚑⚑ THE FENCED-HASH CASE IS WHY THIS TOOLKIT PARSES INSTEAD OF SCANNING. A `#` inside a code
fence is not a header, and this repo's own plan documents hold shell fences full of `#` comments
— so a `grep '^#'` reports sections that do not exist and, worse, gets the SPANS between them
wrong. One fixture with a fenced hash is what separates a parser from a regex.

⚑⚑ AND THE ANCHOR-KEY CASE HAS A MEASURED COST. A heading carrying backticks rendered without
them, so raw-line anchoring never matched — and because the scan is a forward cursor, that
heading and EVERY SECTION AFTER IT vanished from the span list. Measured on this repo's
CLAUDE.md: 3 of 9 headings carry backticks, so a third of the document was unwritable while the
header listing showed it fine.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from substrate import md_ast

# A document whose fenced block contains a line that LOOKS like a header.
_FIXTURE = """# Real heading

```sh
# not a heading — a shell comment inside a fence
echo hi
```

## Second real heading

Some prose.
"""

# The headers a parser must find, and a line scan must not.
_WANT = [(1, "Real heading"), (2, "Second real heading")]


def _have_pandoc() -> bool:
    """Report whether the converter is present on this machine."""
    return shutil.which("pandoc") is not None


def _doc(d: str) -> Path:
    """Write the fixture document and return its path."""
    path = Path(d) / "doc.md"
    path.write_text(_FIXTURE, encoding="utf-8")
    return path


def a_fenced_hash_is_not_a_header(out: list[str]) -> int:
    """Check the parser skips a `#` inside a code fence.

    ⚑ THE LINE SCAN THIS REPLACES WOULD REPORT THREE HEADERS, and the extra one would split a
    section in half — a correct-looking short span that a reader cannot see is wrong.
    """
    with tempfile.TemporaryDirectory() as d:
        got = md_ast.headers(_doc(d))
    if got != _WANT:
        out.append(f"selftest: headers read as {got!r}, want {_WANT!r}")
        return 1
    return 0


def anchor_key_strips_inline_markup(out: list[str]) -> int:
    """Check a backticked heading and its rendered form produce one key.

    ⚑ THE MEASURED DEFECT. Without this, a heading with inline markup never matched its own raw
    line, and every section after it disappeared from the span list.
    """
    raw = "Building the tree: `make -j` self-throttles"
    rendered = "Building the tree: make -j self-throttles"
    if md_ast.anchor_key(raw) != md_ast.anchor_key(rendered):
        out.append("selftest: a backticked heading does not match its rendered form")
        return 1
    return 0


def anchor_key_folds_case_and_space(out: list[str]) -> int:
    """Check the key is stable under casing and whitespace."""
    bad = 0
    if md_ast.anchor_key("A  Heading") != md_ast.anchor_key("a heading"):
        out.append("selftest: the anchor key is case- or space-sensitive")
        bad += 1
    if md_ast.anchor_key("  padded  ") != "padded":
        out.append("selftest: the anchor key keeps surrounding space")
        bad += 1
    return bad


def distinct_headings_keep_distinct_keys(out: list[str]) -> int:
    """Check normalizing does not collapse genuinely different headings.

    ⚑ OVER-MATCHING IS BOUNDED, NOT ABSENT: two headings differing only by markup DO collide,
    and the section finder refuses that ambiguity rather than picking one. Two headings
    differing by a word must not.
    """
    if md_ast.anchor_key("Section one") == md_ast.anchor_key("Section two"):
        out.append("selftest: two different headings share an anchor key")
        return 1
    return 0


_ARMS = (
    a_fenced_hash_is_not_a_header,
    anchor_key_strips_inline_markup,
    anchor_key_folds_case_and_space,
    distinct_headings_keep_distinct_keys,
)

_CASE_COUNT = 1 + 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    if not _have_pandoc():
        # ⚑ A DECLARED SKIP, NEVER A SILENT PASS. The parser needs the converter; reporting
        # these green without it would claim a measurement nobody took.
        sys.stdout.write("md-ast selftest: SKIP — pandoc is not on this machine\n")
        sys.stdout.write("md-ast selftest: 0/0\n")
        return 0

    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"md-ast selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"md-ast selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
