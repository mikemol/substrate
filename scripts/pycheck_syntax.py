#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decide whether post-edit content PARSES, as a state of its own.

⚑⚑ UNPARSEABLE IS A FOURTH STATE, AND IT WAS LIVING IN THE FAIL-OPEN ONE. The pycheck
tristate is `True` clean / `False` findings / `None` could-not-run, and `None` fails
OPEN deliberately: *a gate cannot deny every edit because its own dependency is
missing, and could not be repaired from inside the session it broke.* That rationale
is not merely inapplicable to a syntax error — it INVERTS. The checkers ran fine; the
FILE is broken; and the author repairs it with their very next write, from inside the
session, without any dependency being restored.

⚑⚑⚑ THE MECHANISM IS AN ORDERING ACCIDENT, NOT AN EMPTY-FINDINGS READ, AND THAT
CORRECTION MATTERS BECAUSE IT NAMES A SECOND DEFECT. It is natural to assume neither
checker can parse the file, both report nothing, and emptiness reads as CLEAN.
MEASURED 2026-09-02, and that is not what happens:

    ruff  on `def broken(`  →  exit 1, `invalid-syntax: unexpected EOF while parsing`
    mypy  on `def broken(`  →  exit 2, `'(' was never closed  [syntax]`

**ruff DOES refuse it, as a finding.** mypy exits 2, which `run_checker` correctly
reads as UNKNOWN — and `analyze_python`'s loop returns on the FIRST `None` it sees,
DISCARDING the finding ruff already collected. So the fail-open is a real finding
overwritten by a later checker's UNKNOWN, and the hole would remain even if only one
checker were parse-blind.

⚑ WHICH IS WHY THE DETECTOR IS `ast.parse` AND NOT A SCAN OF EITHER CHECKER'S TEXT.
Keying on a message string (`invalid-syntax`, `was never closed`) would make the state
depend on two vendors' wording, in a gate whose whole subject is not confusing a fact
about the instrument for a fact about the substrate. `compile()` is the same parser
the interpreter will use on the file, so it answers the question actually being asked:
*will this content load at all?*

⚑⚑ THE AUTHOR-MID-REPAIR TRAP DOES NOT EXIST HERE, AND CHECKING FOR IT WOULD BE WORSE.
The obvious worry is a refusal that strands an author fixing a syntax error. It cannot
arise: this hook gates POST-EDIT content, so the only writes refused are ones whose
RESULT does not parse. A write that repairs the syntax parses, and is admitted no
matter how broken the file was before. An "improves parseability" allowance would be a
strictly weaker gate — it would admit a write that leaves the file broken, which is
precisely the state that gets banked as good under a truncating disk.
"""

from __future__ import annotations

import ast


def syntax_error(content: str, path: str) -> str:
    """Return a one-line description of `content`'s syntax error, or "" if it parses.

    ⚑ THE EMPTY STRING IS THE PARSES-FINE ANSWER, so the caller branches on truthiness
    without a second sentinel. A non-empty return is always a refusal reason.

    ⚑ `ValueError` IS CAUGHT ALONGSIDE `SyntaxError` BECAUSE `compile` RAISES IT for
    content the parser rejects before it can locate a position — a NUL byte is the
    reachable case, and a truncated write is exactly how one arrives.
    """
    try:
        ast.parse(content, filename=path or "<the edited file>")
    except SyntaxError as e:
        where = f"line {e.lineno}" if e.lineno is not None else "an unknown line"
        return f"{e.msg} ({where})"
    except ValueError as e:
        return f"source cannot be parsed: {e}"
    return ""
