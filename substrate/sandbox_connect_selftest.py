#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sandbox_connect`, split out of its tail.

⚑ SPLIT BY `module_trim`, NOT HAND-RETYPED. The cases below are the origin's own,
moved verbatim — the conservation guard checked that every line landed in exactly
one of the two halves, which is the property a retype cannot offer.

⚑ THE BACK-IMPORT NAMES EVERY SYMBOL EXPLICITLY because a star import drops the
origin's private helpers, which the cases reach (gate-G321). A name the origin only
IMPORTED is taken from its own source instead (gate-G325).
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import psycopg

from substrate import suite_emit
from substrate.sandbox_target import reset_statements

if TYPE_CHECKING:
    from psycopg.rows import DictRow

from substrate.sandbox_connect import (
    RowShapeError,
    UnreachableError,
    _raises,
    descriptor,
    probe_report,
)


def _selftest() -> int:
    """Check what is checkable with no server: the seam, not the connection.

    ⚑⚑ THE CASES DO NOT OPEN A CONNECTION, AND THAT IS THE POINT RATHER THAN A LIMITATION. What
    this module adds over the driver is the narrowing in `descriptor` and the transport/query
    split — both are decidable against a stand-in, and a suite that needed a live store would be
    asserting the store's availability instead of this module's rules. The connection itself is
    exercised against a real sandbox, where a failure is an operator's to read.

    ⚑ THE CASES CALL `descriptor` ITSELF, never a copy of its checks. A suite that reimplements
    the rule it is testing passes while the shipped rule rots — `census-keyed-on-one-spelling`
    moved into a test.
    """
    ok_row: DictRow = {"table_name": "t", "table_type": "BASE TABLE"}
    cases: list[tuple[str, bool]] = [
        (
            "descriptor reads text columns",
            descriptor(ok_row, "table_name", "table_type") == ("t", "BASE TABLE"),
        ),
        ("descriptor refuses a non-text value", _raises({"table_name": 17, "table_type": "VIEW"})),
        ("descriptor refuses an absent column", _raises({"table_type": "VIEW"})),
        ("descriptor refuses a None value", _raises({"table_name": None, "table_type": "VIEW"})),
        ("unreachable is not a psycopg error", not issubclass(UnreachableError, psycopg.Error)),
        ("row-shape fault is a TypeError", issubclass(RowShapeError, TypeError)),
        (
            "views drop before tables",
            reset_statements([("t", "BASE TABLE"), ("v", "VIEW")])[0].startswith("DROP VIEW"),
        ),
        # ⚑ The probe reports the SERVER's identity and a denominator even when empty — a
        # freshly provisioned tenant IS empty, and silence would read as a failed probe.
        (
            "the probe names the role and database the server accepted",
            probe_report("r", "d", []).startswith("connected as r to d\n"),
        ),
        (
            "an empty database prints its denominator",
            "0 relation(s) — empty" in probe_report("r", "d", []),
        ),
        (
            "relations are counted by kind",
            "3 relation(s) — 2 BASE TABLE, 1 VIEW"
            in probe_report("r", "d", [("a", "BASE TABLE"), ("b", "BASE TABLE"), ("v", "VIEW")]),
        ),
    ]
    for name, ok in cases:
        if not ok:
            sys.stdout.write(f"  FAIL {name}\n")
    return suite_emit.report(__file__, sum(1 for _, ok in cases if ok), len(cases))


if "--selftest" in sys.argv:
    raise SystemExit(_selftest())


if __name__ == "__main__":
    sys.exit(_selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
