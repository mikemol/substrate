#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Locate a tool's dispatch branches, and hold its roster to them.

⚑⚑⚑ THE SECOND PROMOTION UNIT (gate-G80, after `selftest_decl`). `procstruct` imports
`contract_rows` and `check_mode_contracts` imports the origin whole, so neither can be
repointed at the package until these land. **The order is forced** — promote, then repoint.

⚑⚑ AND THIS IS THE GENERALISATION OF A ONE-FILE READER, WHICH IS WHY IT EXISTS AT ALL. The
predecessor parsed one tool's dispatch and read one module-global roster, so converting a
roster elsewhere produced a tool that was STANDARDISED but not CHECKED — and a
converted-unchecked roster contributes zero keys to its gate, rendering exactly like a clean
one. Standardising the shape without moving the enforcement buys consistency and nothing else.

⚑⚑⚑ THREE VERDICTS, AND THE THIRD IS THE HONEST ONE. `True` — the mode honours what its
roster claims. `False` — a real disagreement. `None` — **UNKNOWN: the branch could not be
located**, a fact about this READER and never banked as a pass. The predecessor's own history
is the argument: it reported UNKNOWN rather than PASS on a spelling it could not see, and that
UNKNOWN is what kept the disagreement visible instead of silently green.

⚑ EVERY MATCHING RULE BELOW IS A REPAIRED FALSE POSITIVE, and each is cased. A gate that
accuses a compliant tool is the one failure it must not make, because the fix it demands is to
break a working refusal.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Mapping

# The roster key a POSITIONAL operand is filed under — it has no flag to dispatch on.
POSITIONAL = "<positional>"

# The marker a scanning mode must call to report an incomplete read.
SKIP_MARKER = "_report_skipped("

# ⚑⚑ `[\w.]*argv` — THE DOT IS LOAD-BEARING AND ITS ABSENCE WAS MEASURED. `sys.argv` is the
#   commonest receiver of all, and a `\w*argv` pattern does not match it: a first cut located
#   only the `flagged_argv()` branches, so every ordinary mode read UNKNOWN. The breadth this
#   reader exists for, missed on the most ordinary spelling.
_OPENS = re.compile(r'(\s*)(?:el)?if "(--[a-z-]+)" in [\w.]*argv\w*\(?\)?')
_FLAGS_ON_LINE = re.compile(r'"(--[a-z-]+)" in [\w.]*argv\w*\(?\)?')
_TESTED = re.compile(r'"(--[a-z-]+)"\s+in\s+\w*argv\w*\(?\)?')

_UNDISPATCHED = (
    "DECLARED in the roster, never dispatched — a promise the CLI does not "
    "keep, and its arity still feeds the entry point"
)
_UNDECLARED = "DISPATCHED, absent from the roster — undeclared arity"
_ONLY_ON_FAILURE = (
    " (its usage exists only as a runtime print — reachable only by FAILING the mode)"
)


class Declared(Protocol):
    """What this reader needs from a roster entry, and nothing more.

    ⚑ NAMED AS A PROTOCOL SO THE READER STATES ITS OWN REACH. It consumes three fields; a
    roster carrying more is fine and a roster carrying fewer is a type error at the call
    site rather than an `AttributeError` mid-scan.
    """

    @property
    def scans(self) -> bool:
        """Whether the mode owes an incomplete-read report."""

    @property
    def writes(self) -> object:
        """What artifact kinds the mode mutates, or a falsy value for a pure reader."""

    @property
    def opts(self) -> tuple[str, ...]:
        """The modifier flags this mode OWNS — not modes in their own right."""


def _flags_in(text: str) -> list[str]:
    """Return every flag an argv test names, narrowed to `str` at the regex seam.

    ⚑ `finditer`, NOT `findall`, AND THE DIFFERENCE IS THE TYPE — the idiom `tool_usage`
    already settled, found by reuse-search rather than reinvented. `findall` returns
    `list[Any]`, which carries an untyped value into every downstream comparison;
    `finditer` yields `Match[str]`, so `.group(1)` is a `str` by construction.
    """
    return [found.group(1) for found in _FLAGS_ON_LINE.finditer(text)]


def _tested_in(src: str) -> set[str]:
    """Return every flag the source tests against argv anywhere, narrowed the same way."""
    return {found.group(1) for found in _TESTED.finditer(src)}


def branch_bounds(src: str) -> dict[str, tuple[int, int]]:
    """Return `{flag: (start_line, end_line)}` — where each mode's dispatch branch sits.

    ⚑⚑ A BRANCH ENDS WHERE ITS INDENTATION DOES, NOT WHERE THE NEXT MATCH BEGINS, and the
    naive rule was a measured false positive on a real file. A tool opened `--coverage` and
    NESTED `--emit` and `--reap` inside it; under next-match bounding, `--coverage`'s body
    ended at the nested flag, so the `--apply` test its sub-branch performs fell OUTSIDE and
    the gate reported a correctly-guarded mutator as a silent-default writer.

    ⚑ SO A MATCH INDENTED DEEPER THAN AN OPEN BRANCH BELONGS TO IT. Two consequences worth
    stating: a nested flag is still recorded, so a reader asking where it lives gets an
    answer; and a mode's body now includes its own sub-dispatch, which is where the guard
    usually sits.

    ⚑⚑ AND ONE BRANCH CAN OPEN SEVERAL MODES. `if "--a" in argv or "--b" in argv:` is one
    line serving two modes that share a body; matching only the first made the second read
    DECLARED-never-dispatched — a PHANTOM verdict against a mode that dispatches fine, whose
    demanded fix is deleting a correct declaration.
    """
    lines = src.splitlines()
    seen: set[str] = set()
    order: list[tuple[str, int, int]] = []
    for i, line in enumerate(lines):
        opened = _OPENS.match(line)
        if not opened:
            continue
        indent = len(opened.group(1))
        for flag in _flags_in(line):
            if flag not in seen:
                seen.add(flag)
                order.append((flag, i, indent))
    out: dict[str, tuple[int, int]] = {}
    for n, (flag, i, indent) in enumerate(order):
        end = len(lines)
        for _later, j, ind2 in order[n + 1 :]:
            # ⚑ `j > i` — co-located flags share one `if` line and one body, so a sibling
            #   from the SAME line must not close this branch at zero length.
            if j > i and ind2 <= indent:
                end = j
                break
        out[flag] = (i, end)
    return out


def _scan_row(
    flag: str, lines: list[str], bounds: dict[str, tuple[int, int]]
) -> tuple[str, bool | None, str]:
    """Return the row for a mode declaring `scans`."""
    if flag not in bounds:
        return flag, None, "branch not located in the dispatch"
    start, end = bounds[flag]
    ok = SKIP_MARKER in "\n".join(lines[start:end])
    return (
        flag,
        ok,
        ("reports skips" if ok else f"declares scans=True but never calls {SKIP_MARKER}"),
    )


def _writes_row(
    flag: str, mode: Declared, lines: list[str], bounds: dict[str, tuple[int, int]]
) -> tuple[str, bool | None, str] | None:
    """Return a row when a mutating mode guards on neither `--apply` nor `--dry-run`.

    ⚑ THE CORPUS'S `--apply` CONVENTION, BOUND TO SOMETHING CHECKABLE: a mutating tool
    invoked with neither flag must REFUSE, never guess. That is this field's whole purpose.
    """
    writes = mode.writes
    if not writes or flag not in bounds:
        return None
    start, end = bounds[flag]
    body = "\n".join(lines[start:end])
    if "--apply" in body or "--dry-run" in body:
        return None
    detail = (
        f"declares writes={writes!r} but its branch tests neither --apply nor "
        "--dry-run — a mutating mode with a silent default"
    )
    return flag, False, detail


def contract_rows(
    src: str,
    roster: Mapping[str, Declared],
) -> list[tuple[str, bool | None, str]]:
    """Return `[(flag, ok, why)]` — hold ANY tool's roster to its own dispatch.

    ⚑⚑ BOTH DIRECTIONS ARE DEFECTS. A flag DISPATCHED but undeclared runs with arity nobody
    stated; a flag DECLARED but undispatched is a promise the CLI does not keep while still
    feeding arity resolution.

    ⚑ A FLAG DECLARED AS SOME MODE'S `opts` IS A MODIFIER, NOT AN UNDECLARED MODE. Without
    that, a tool's owned sub-flags read as top-level modes nobody declared, and the gate
    demanded they be promoted — the opposite of what the roster says.
    """
    lines = src.splitlines()
    bounds = branch_bounds(src)
    out: list[tuple[str, bool | None, str]] = []
    for flag, mode in sorted(roster.items()):
        if mode.scans:
            out.append(_scan_row(flag, lines, bounds))
        row = _writes_row(flag, mode, lines, bounds)
        if row is not None:
            out.append(row)
    tested = _tested_in(src)
    owned = {opt for mode in roster.values() for opt in mode.opts}
    for flag in sorted(set(roster) | set(bounds)):
        if flag in owned and flag not in roster:
            continue
        # ⚑ THE POSITIONAL HAS NO FLAG TO DISPATCH ON, so comparing it against argv would
        #   manufacture a phantom-declaration finding out of a correct declaration.
        if flag == POSITIONAL:
            continue
        if flag in roster and flag not in bounds and flag not in tested:
            out.append((flag, False, _UNDISPATCHED))
        elif flag in bounds and flag not in roster:
            start, end = bounds[flag]
            body = "\n".join(lines[start:end])
            hint = _ONLY_ON_FAILURE if "usage:" in body else ""
            out.append((flag, False, _UNDECLARED + hint))
    return out


def unknown(rows: list[tuple[str, bool | None, str]]) -> tuple[str, ...]:
    """Return the flags whose branch this reader could not locate.

    ⚑ REPORTED SEPARATELY FROM THE FAILURES, because an unlocatable branch is a gap in the
    READER and a disagreement is a gap in the TOOL. Summing them would let the reader's own
    blind spots inflate a tool's defect count.
    """
    return tuple(flag for flag, ok, _why in rows if ok is None)
