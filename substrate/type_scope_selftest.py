#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.type_scope`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321). A name the origin only
IMPORTED is taken from its own source instead (gate-G325).
"""

from __future__ import annotations

import sys

from substrate import suite_emit
from substrate.type_scope import (
    _AGREED_OWN,
    _FOLLOW_SKIP,
    _LIVE_WITH_INDUCED,
    _MODES,
    _ONE,
    _SEP,
    leads,
    refusal,
    render,
    rows_for,
    split_of,
    unresolved,
)


def _cases() -> tuple[int, int]:
    """Return `(passed, total)` over this module's cases."""
    checks: list[bool] = []
    tgt = "a/b.py"
    both = {f"misc{_SEP}{tgt}": ["x", "x"], f"arg-type{_SEP}{tgt}": ["q"]}
    # Two arms that agree: everything is OWN, and neither closure arm is populated.
    same = split_of(both, both, tgt)
    checks.append(len(same.own) == _AGREED_OWN)
    checks.append(same.induced == () and same.suppressed == ())
    # ⚑ THE DISCRIMINATOR FOR `induced`: a predicate that always answers OWN fails here. The
    # `normal` arm holds one MORE `misc` with IDENTICAL text, so only a multiset difference
    # sees it -- a set difference reports this file as entirely self-owned.
    more = {f"misc{_SEP}{tgt}": ["x", "x", "x"], f"arg-type{_SEP}{tgt}": ["q"]}
    ind = split_of(more, both, tgt)
    checks.append(len(ind.induced) == _ONE)
    checks.append(len(ind.own) == _AGREED_OWN)
    # ⚑ AND THE OPPOSITE DIRECTION, so a predicate that always answers INDUCED fails too.
    sup = split_of(both, more, tgt)
    checks.append(len(sup.suppressed) == _ONE and sup.induced == ())
    # ⚑ THE DISCRIMINATOR FOR THE PATH OPERAND ACTUALLY SCOPING THE READ: a census holding
    # only ANOTHER file's rows contributes nothing here. A `messages_for` that ignored its
    # target -- the `module_size` defect -- would report three own messages instead of none.
    other = {f"misc{_SEP}other/c.py": ["x", "x", "x"]}
    checks.append(split_of(other, other, tgt).own == ())
    # Messages are code-qualified, so one code's text cannot cancel another's.
    checks.append(all(m.startswith(("misc: ", "arg-type: ")) for m in same.own))
    # `normal_total` counts the live arms only; a suppressed message is not a live finding.
    checks.append(ind.normal_total == _LIVE_WITH_INDUCED)
    checks.append(sup.normal_total == _AGREED_OWN)
    # The blind roster is non-empty and every line names a mechanism, not a caveat.
    checks.append(bool(unresolved()) and all(" -- " in b for b in unresolved()))
    # ⚑ THE DISCRIMINATOR FOR THE HONESTY MARKING: a renderer that dropped either half still
    # prints a plausible report. Every mode must carry BOTH words and the blind roster.
    checks.append(
        all(
            "ESTABLISHED" in render(ind, m)
            and "INFERRED" in render(ind, m)
            and "CANNOT see" in render(ind, m)
            for m in ("", *_MODES)
        )
    )
    # A truncated arm names its own remainder rather than reading as the whole arm.
    checks.append("... 2 more" in "\n".join(rows_for("OWN", ("a", "b", "c"), _ONE)))
    # Leads come from the INDUCED arm only -- an all-own split offers none to follow.
    checks.append(leads(same) == () and leads(ind) != ())
    # The refusal names WHICH arm failed, so a reader is not left to guess between them.
    checks.append(_FOLLOW_SKIP in refusal(tgt, _FOLLOW_SKIP))
    return sum(checks), len(checks)


if "--selftest" in sys.argv:
    raise SystemExit(suite_emit.report("type_scope_selftest", *_cases()))
