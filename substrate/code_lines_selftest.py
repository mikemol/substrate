#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Arms for `substrate.code_lines` — the tokenize-backed code/comment/docstring split."""

from __future__ import annotations

import sys
from pathlib import Path

from substrate.code_lines import code_count, code_lines, physical_count

_MIXED = '''"""A module docstring.

It spans several lines, and none of them are code.
"""
# a whole-line comment

x = 1  # code with a trailing comment
y = "# not a comment"
'''

#: The 1-based lines of `_MIXED` occupied by the module docstring.
_DOCSTRING_LINES = (1, 2, 3, 4)
#: The 1-based line of `_MIXED` holding nothing but a comment.
_COMMENT_ONLY = 5
#: The 1-based line of `_MIXED` holding code followed by a comment.
_CODE_WITH_COMMENT = 7
#: The 1-based line of `_MIXED` whose string literal contains a `#`.
_HASH_IN_STRING = 8


def a_docstring_is_not_code(out: list[str]) -> int:
    """⚑ THE DEFECT THE NAIVE COUNTER SHIPPED: docstring lines scored as bulk.

    Counting them makes the most carefully documented modules read as the worst offenders on
    the census built to find bulk, pushing a reader toward deleting the valuable half.
    """
    got = code_lines(_MIXED)
    for line in _DOCSTRING_LINES:
        if line in got:
            out.append(f"docstring line {line} counted as code: {sorted(got)}")
            return 1
    return 0


def a_whole_line_comment_is_not_code(out: list[str]) -> int:
    """⚑ A line holding only a comment is commentary, not the bulk a size cap measures."""
    if _COMMENT_ONLY in code_lines(_MIXED):
        out.append(f"the whole-line comment at {_COMMENT_ONLY} counted as code")
        return 1
    return 0


def a_trailing_comment_does_not_erase_its_line(out: list[str]) -> int:
    """⚑ Dropping it would hide a defect that happens to carry an explanation."""
    got = code_lines(_MIXED)
    if _CODE_WITH_COMMENT not in got:
        out.append(f"line {_CODE_WITH_COMMENT} is code and was dropped: {sorted(got)}")
        return 1
    return 0


def a_hash_inside_a_string_is_not_a_comment(out: list[str]) -> int:
    """⚑ THE EXACT CASE A REGEX STRIPPER GETS WRONG, and the reason this tokenizes."""
    if _HASH_IN_STRING not in code_lines(_MIXED):
        out.append(f"line {_HASH_IN_STRING} (a `#` inside a string) was read as a comment")
        return 1
    return 0


def an_untokenizable_source_is_permissive_not_empty(out: list[str]) -> int:
    """⚑ A ZERO WOULD READ AS A CLEAN SCAN — the absence-as-finding shape.

    A file that will not tokenize must report every line as code, so a caller sees an
    implausible number rather than a plausible pass.
    """
    broken = "def f(:\n    'unterminated\n"
    if code_count(broken) == 0:
        out.append("an untokenizable source reported 0 code lines rather than being permissive")
        return 1
    return 0


def physical_and_code_are_different_numbers_here(out: list[str]) -> int:
    """⚑ POSITIVE CONTROL: a counter returning the same value for both measures nothing.

    The whole `sppf_db.py` incident is that these two diverge; a fixture where they agree
    would let an implementation that aliases one to the other pass every arm above.
    """
    code = code_count(_MIXED)
    physical = physical_count(_MIXED)
    if code >= physical:
        out.append(f"code={code} physical={physical}; the fixture has non-code lines")
        return 1
    if code == 0:
        out.append("the fixture has code lines and none were counted")
        return 1
    return 0


def the_counter_reads_a_real_module(out: list[str]) -> int:
    """⚑ POSITIVE CONTROL against a reader that only works on the fixture string."""
    here = Path(__file__).with_name("code_lines.py")
    source = here.read_text(encoding="utf-8")
    code = code_count(source)
    physical = physical_count(source)
    if not 0 < code < physical:
        out.append(f"code_lines.py: code={code} physical={physical}; expected 0 < code < physical")
        return 1
    return 0


def a_single_line_string_beside_code_stays_code(out: list[str]) -> int:
    """⚑ THE OVER-CORRECTION GUARD for the fix to the first-docstring-line defect.

    Excluding any line a string token touches would drop `x = "value"` — so a single-line
    token counts as covering its line only when BOTH sides of it are empty.
    """
    got = code_lines('x = "value"\n')
    if got != {1}:
        out.append(f'`x = "value"` should be code; got {sorted(got)}')
        return 1
    if code_lines('"""standalone"""\n'):
        out.append("a bare single-line string statement was counted as code")
        return 1
    return 0


_ARMS = (
    a_single_line_string_beside_code_stays_code,
    a_docstring_is_not_code,
    a_whole_line_comment_is_not_code,
    a_trailing_comment_does_not_erase_its_line,
    a_hash_inside_a_string_is_not_a_comment,
    an_untokenizable_source_is_permissive_not_empty,
    physical_and_code_are_different_numbers_here,
    the_counter_reads_a_real_module,
)

_CASE_COUNT = 2 + 4 + 1 + 1 + 1 + 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"code-lines selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"code-lines selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
