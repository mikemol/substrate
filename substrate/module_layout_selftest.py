#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `substrate.module_layout` — the top-level-cut reader.

⚑⚑ EVERY CASE PINS A PROPERTY, NOT A VICTIM FILE. The origin's incidents were all discovered on
one file that has since moved; a case asserting *`pycodemod.py` has 17 defs* expires the moment
the drain it exists to serve makes progress, and then reads as a regression in the reader. Each
arm below states a rule about the GRAMMAR — an `AnnAssign` gets a name, a decorated def spans its
decorators — over a fixture written in the case itself.

⚑⚑ THE `AnnAssign` ARM IS THE INCIDENT ARM AND IT IS THE REASON THIS SUITE EXISTS. The origin
shipped a labeller that knew `Assign` and not `AnnAssign`, so a module-level memo rendered as an
unnamed group, a split plan made from that census left the cache behind, and the tool died with
`NameError`. A reader that silently cannot NAME a thing excludes it from every decision made by
reading it — so the case asserts the name is PRESENT, not merely that the row exists.

⚑ THE DECORATOR ARM IS THE ONE A PASSING READER STILL GETS WRONG. `node.lineno` on a decorated
def points at `def`, not at the first `@`, and every row still looks plausible — the span is
merely short by the decorator count. Nothing downstream complains until a cut made on that line
produces a syntax error in both halves, which is why the property is pinned here rather than
trusted to review.

⚑ THE CASES LIVE HERE, NOT IN THE MODULE'S TAIL (⟡n-split-the-tails). Inline cases cannot run
without importing the module under test, so a module that becomes too dirty to edit takes its own
suite hostage.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import module_layout, suite_emit

# One fixture exercising every recognised top-level shape at once. ⚑ ONE SOURCE, MANY ARMS: a
# per-arm fixture lets two arms disagree about what the grammar looks like, and the reader's job
# is precisely to report a WHOLE file's groups in order.
FIXTURE = '''"""Doc."""

import os

CONST = 1

MEMO: dict = {}


@staticmethod
def decorated():
    """Body."""
    return 1


class Thing:
    """A class."""


if __name__ == "__main__":
    decorated()
'''

# The `(kind, name)` rows FIXTURE must produce, in order. ⚑ THE WHOLE SEQUENCE IS THE ASSERTION,
# because the reader's contract is source ORDER: a set comparison passes on a reader that emits
# every group in the wrong place, which is exactly the fact a split plan reads.
EXPECTED: tuple[tuple[str, str], ...] = (
    (module_layout.STMT, "docstring"),
    (module_layout.STMT, "import"),
    (module_layout.STMT, "CONST"),
    (module_layout.STMT, "MEMO"),
    (module_layout.DEF, "decorated"),
    (module_layout.CLASS, "Thing"),
    (module_layout.GUARD, module_layout.GUARD_NAME),
)

# A path no walk can read, for the arms that pin honest behaviour on an unreadable file.
MISSING = Path("/nonexistent/not-a-file.py")

# The one-def fixture `case_code_lines_skip_comments` reads, and the two numbers it must produce.
# ⚑ NAMED RATHER THAN INLINE: the arm's whole claim is that these two differ — 4 source lines, 2 of
# them code — and a bare `== 2 and == 4` in the return hides which number is which.
_COUNTED = "def f():\n    # note\n\n    return 1\n"
_COUNTED_CODE = 2
_COUNTED_SPAN = 4


def _rows() -> tuple[module_layout.Group, ...]:
    """Return the fixture's groups, parsed once for the arms that share them."""
    return module_layout.groups(FIXTURE)


def case_order() -> bool:
    """Report every recognised shape, once, in source order."""
    return tuple((g.kind, g.name) for g in _rows()) == EXPECTED


def case_annassign_is_named() -> bool:
    """Name an annotated assignment rather than leaving it unnamed — the `_BARE_CACHE` arm.

    ⚑ ASSERTS THE NAME, NOT THE ROW. The origin emitted a row for `MEMO` too; what it could not do
    was say what the row was called, and an unnameable group is one a split plan cannot move.
    """
    memo = [g for g in _rows() if g.name == "MEMO"]
    return len(memo) == 1 and memo[0].name != module_layout.UNNAMED


def case_decorator_in_span() -> bool:
    """Start a decorated def's span at the `@`, not at the `def` — the both-halves-broken arm."""
    row = next(g for g in _rows() if g.name == "decorated")
    return FIXTURE.splitlines()[row.first_line - 1].lstrip().startswith("@")


def case_guard_needs_the_dunder() -> bool:
    """Refuse to name a non-entry top-level `if` as the guard.

    ⚑ THE NEGATIVE ARM. Without it, a classifier that calls EVERY top-level `if` the entry guard
    passes `case_order` — a constant function satisfying a case that only ever feeds it guards.
    """
    rows = module_layout.groups("import sys\nif sys.version_info:\n    pass\n")
    guards = [g for g in rows if g.kind == module_layout.GUARD]
    return not guards and rows[-1].name == module_layout.UNNAMED


def case_code_lines_skip_comments() -> bool:
    """Exclude blanks and whole-line comments from the count, and include the `def` line."""
    row = module_layout.groups(_COUNTED)[0]
    return row.code_lines == _COUNTED_CODE and row.span == _COUNTED_SPAN


def case_unparseable_file_is_empty_not_raised() -> bool:
    """Yield no rows for a file that does not parse, rather than taking the walk down."""
    return module_layout.of_file(MISSING) == ()


def case_report_prints_the_denominator() -> bool:
    """State the population even when a file contributed nothing — absent is not unread."""
    return "0 of 1 file(s)" in module_layout.report((MISSING,))


def case_reads_a_real_module() -> bool:
    """Answer on this package's own source, not only on the hand-written fixture.

    ⚑ THE FIXTURE ARMS ALL SHARE ONE INPUT, so they cannot catch a reader that works on 20 lines
    and fails on a real file. This arm pins only what cannot expire: the module under test defines
    the function this suite calls.
    """
    here = Path(module_layout.__file__)
    return any(
        g.kind == module_layout.DEF and g.name == "groups" for g in module_layout.of_file(here)
    )


_ARMS = (
    case_order,
    case_annassign_is_named,
    case_decorator_in_span,
    case_guard_needs_the_dunder,
    case_code_lines_skip_comments,
    case_unparseable_file_is_empty_not_raised,
    case_report_prints_the_denominator,
    case_reads_a_real_module,
)


def selftest() -> int:
    """Run every arm and report the verdict as a typed record."""
    passed = 0
    for arm in _ARMS:
        if arm():
            passed += 1
        else:
            sys.stdout.write(f"  FAIL {arm.__name__}\n")
    return suite_emit.report(__file__, passed, len(_ARMS))


if __name__ == "__main__":
    raise SystemExit(selftest())
