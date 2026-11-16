#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The worklist ordering's ROW — nine typed fields whose ORDER is the sort key.

⚑⚑⚑ THIS IS THE TYPED FORM OF `wg_order.Row`, EXTRACTED RATHER THAN FIXED IN PLACE,
AND THE GATE GAVE THAT INSTRUCTION DIRECTLY. `scripts/wg_order.py` carries hundreds of
findings and the per-file gate has no partial-credit path: an edit that leaves the file
dirty is refused and reverted, so typing the definition where it lives cannot land. The
refusal's own text says what to do instead — *extract the one concern you need into a
NEW module, written clean in one pass, and let the next consumer import that*.

⚑⚑ IT IS A `NamedTuple`, NOT THE HOUSE `@dataclass(frozen=True, slots=True)`, AND THE
CONSUMERS DECIDE THAT — this is a deliberate, argued deviation from the convention.
`wg_order.order()` builds a list of these and calls `rows.sort()` with no key: the sort
is the TUPLE comparison, field by field, and the field ORDER is therefore the ranking
policy. The original's own comment says so — *`graded` BEFORE `neg_lev` IS THE GRADING,
IN THE FIELD ORDER*, recording that an earlier order let the declared reading outrank
the evaluated one. A frozen dataclass would need `order=True` to compare at all, would
compare as a dataclass rather than as a tuple, and would drop tuple identity for a
`_Rows(list)` subclass built out of these. ruff agrees from the other side: `PYI024` on
the original says *use `typing.NamedTuple`*.

⚑ SO THE RULE IS NOT BEING WAIVED, IT IS BEING READ. The convention exists so a record
is immutable and cheap; a `NamedTuple` is both. What it adds — tuple ordering — is the
thing this particular record is FOR, and swapping it out would silently change the
ranking of the worklist while every field kept its name.

⚑ WHAT IS OWED, STATED RATHER THAN IMPLIED: nothing imports this yet. `Row`'s only
importer is `worklist_gate.py`, and its only construction site is inside `wg_order.py`
— so WIRING THIS IN IS AN EDIT TO `wg_order.py`, which the gate refuses for the same
reason the in-place fix was refused. This is the strand case the refusal names. The
rung is built and typed and carries its own cases; the binding lands when `wg_order.py`
is DRAINED, not before, and that is the remaining work rather than a defect here.
"""

from __future__ import annotations

from typing import NamedTuple


class Row(NamedTuple):
    """One ordered worklist item: its grading keys, its identity, and its edges.

    ⚑ THE FIELD ORDER IS THE SORT ORDER, so these declarations are policy rather than
    layout. `layer` is the only hard constraint (an item cannot precede what grounds
    it); `graded` and `neg_lev` are the same leverage relation at grades 1 and 0, in
    that precedence; `after` and `size` break ties within a grade-1 class.

    ⚑ `deps` IS A LIST, NOT A JOINED STRING, and the original records why: it was
    `", ".join(...)`, so the structure died at construction, every consumer re-split
    it, and a membership test `r.key in r.deps` silently became a SUBSTRING test —
    `"A5" in "A5-as, A5-using"` is True. Four false self-loops came from that.

    ⚑ `is_open` IS THREE-STATE. `None` means grade 1 was never EVALUATED, which is not
    the same as evaluated-and-blocked; it sorts WITH the actionable, because an
    unmeasured item is unported or trivial and both are cheap to look at. Collapsing it
    to `False` would bury exactly the items whose live reading is missing.
    """

    layer: int
    graded: int
    neg_lev: int
    after: int
    size: int
    key: str
    is_open: bool | None
    lev: int
    deps: list[str]


def _ordering_cases(out: list[str]) -> int:
    """Check the field order ranks as the ordering's policy says it must."""
    bad = 0
    # ⚑ EVERY FIXTURE IS BUILT BY KEYWORD. A nine-field positional call puts a bare
    # `True` in the seventh slot, which is the `FBT003` class — and here the rule is
    # exactly right rather than merely satisfied: the whole point of this record is
    # that its POSITIONS carry meaning, so a reader must not have to count to seven to
    # learn which field a boolean landed in.
    #
    # ⚑ LAYER OUTRANKS EVERYTHING: a grounded item never jumps its premise, however
    # much leverage it carries.
    deep_but_free = Row(
        layer=2, graded=0, neg_lev=-99, after=0, size=0, key="deep", is_open=True, lev=99, deps=[]
    )
    shallow_blocked = Row(
        layer=1, graded=1, neg_lev=0, after=0, size=0, key="shallow", is_open=True, lev=0, deps=[]
    )
    if min(deep_but_free, shallow_blocked) != shallow_blocked:
        out.append("row: layer did not outrank leverage")
        bad += 1

    # ⚑⚑ AND `graded` OUTRANKS `neg_lev` WITHIN A LAYER — the evaluated grade beating
    # the declared one. This is the case for the defect the original names: an earlier
    # field order had these reversed, letting a stale declared cone outrank a live
    # blocked reading.
    live_clear = Row(
        layer=1, graded=0, neg_lev=0, after=0, size=0, key="clear", is_open=True, lev=0, deps=[]
    )
    declared_big = Row(
        layer=1, graded=1, neg_lev=-99, after=0, size=0, key="big", is_open=True, lev=99, deps=[]
    )
    if min(declared_big, live_clear) != live_clear:
        out.append("row: the declared grade outranked the evaluated one")
        bad += 1
    return bad


def _shape_cases(out: list[str]) -> int:
    """Check the row stayed a TUPLE and its three-state field admits `None`."""
    bad = 0
    row = Row(
        layer=0, graded=0, neg_lev=0, after=0, size=0, key="k", is_open=None, lev=0, deps=["a", "b"]
    )
    # ⚑⚑⚑ TUPLE IDENTITY IS LOAD-BEARING — `rows.sort()` is a bare tuple comparison and
    # `_Rows` is a `list` subclass built out of these — BUT AN `isinstance(row, tuple)`
    # CASE FOR IT IS VACUOUS, AND MYPY SAID SO. The first draft wrote exactly that
    # check, and the checker reported the failure branch UNREACHABLE: a `NamedTuple` is
    # statically a tuple, so the case could never have gone red.
    #
    # ⚑ THAT IS THE ASSURANCE ARRIVING EARLIER, NOT A CASE BEING LOST. The property is
    # guaranteed by the declaration and checked at type-check time; a runtime arm
    # restating it would pass forever, including on the day someone swapped this for a
    # dataclass — because that edit changes what the checker proves, not what the
    # `isinstance` returns. So what is asserted here is the OPERATION that identity
    # exists for: that these UNPACK positionally, which a frozen dataclass would not.
    layer, graded, neg_lev, after, size, key, is_open, lev, deps = row
    if (layer, graded, neg_lev, after, size) != (0, 0, 0, 0, 0):
        out.append(f"row: the grading fields did not unpack in order: {row}")
        bad += 1
    if (key, is_open, lev, deps) != ("k", None, 0, ["a", "b"]):
        out.append(f"row: the identity and edge fields did not unpack in order: {row}")
        bad += 1
    # ⚑ `deps` IS A REAL LIST so a membership test is a membership test. The original
    # defect was a substring test wearing that spelling.
    substr = Row(
        layer=0,
        graded=0,
        neg_lev=0,
        after=0,
        size=0,
        key="k",
        is_open=True,
        lev=0,
        deps=["A5-as", "A5-using"],
    )
    if "A5" in substr.deps:
        out.append("row: a deps membership test read as a substring test")
        bad += 1
    return bad


_ARMS = (_ordering_cases, _shape_cases)

_CASE_COUNT = 2 + 3
