#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Emit one suite's result as a TYPED RECORD (Ⓝ73 ⟡selftest-contract), for `substrate/` suites.

⚑⚑⚑ THE READER EXISTED AND THE EMITTER DID NOT, WHICH IS A LARGE PART OF WHY THE DEBT SITS IN
THE HUNDREDS. `substrate.suite_record` is imported by four modules and every one of them PARSES.
So a suite in this package that wanted to report by record had nowhere to call: the only emitter
in the tree is `scratch/rungs.emit_record`, and `scratch/` is unimportable from `substrate/` by
gate (`check_scratch_independence`). A contract whose satisfying move has no implementation on
this side of a gated seam is one every suite here fails by default — and the ratchet correctly
reports every one as NEW against an EMPTY (zero-tolerance) baseline, which is an unpaid debt,
not a broken gate.

⚑⚑ SO THIS IS THE HALF THAT MAKES THE PAYDOWN CHEAP, AND IT IS BUILT BEFORE THE SECOND
CONVERSION RATHER THAN AFTER THE FIFTIETH. `rungs.Cases`' own header records what happens
otherwise: *"FIFTY SUITES REIMPLEMENTED THIS — 55 defs, 55 reimplementing, 0 delegating, and 40
of them the identical single statement."* One name, fifty bodies, no authority. Converting the
roster by copying five lines into each suite would mint that exact shape a second time, in the
machinery that verifies everything else.

⚑ IT EMITS ONLY; IT RUNS NOTHING AND COUNTS NOTHING. `rungs.Cases` is the richer form — it
collects cases, captures a failure's source location, and folds. This package's suites already
have their own counting convention (the `_ARMS` tuple plus a `witness_family` whose `count` is
derived), so what they lack is exactly one thing: the line that says the result in the machine's
spelling. Growing this into a second `Cases` would be reinventing a class that already exists
across the seam, which is the failure mode this module is here to prevent.

⚑⚑ THE PREFIX AND THE SCHEMA ARE CITED, NEVER RESPELLED. `suite_record.RECORD_PREFIX` is the
constant the runner actually reads, and it is itself a DOCUMENTED restatement of
`scratch/rungs.ROW_PREFIX` — the authority, named in `suite_record`'s own header as the one that
wins if they ever disagree. That header also records the cost of getting this wrong: the prefix
was once spelled `"#row "` with a space instead of a tab, so `startswith` was FALSE for every
real record, the structural arm never fired, and suites passing 15 of 15 were reported `unread
(0/0)`. Reading the constant rather than typing the string is the whole defence.

⚑ THE STATE FIELD IS EMITTED AND IS NOT THE VERDICT. `suite_record` derives the kind from the
NUMBERS (`verdict_kind`), so a producer bug writing `"state": "ok"` beside `0/0` still reads
VACUOUS. It is carried because the schema has it and a consumer may render it — never because a
suite is trusted to grade itself.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from substrate.suite_record import RECORD_PREFIX

# ⚑ THE SCHEMA VERSION THE READER EXPECTS. `rungs.RECORD_SCHEMA` is the authority; this is the
# same restatement-with-a-named-owner that `suite_record` makes for the prefix, and for the same
# reason — the seam is a gate, not a preference.
SCHEMA = 1

# The suffix `suite_discovery` uses to name a suite's module. Stripped to build the human label.
_SUFFIX = "_selftest"


def label_of(key: str) -> str:
    """Return the human name for a suite key — the module, without path or suffix.

    ⚑⚑ DERIVED, SO THE TWO CANNOT DISAGREE. A first cut took `key` and `label` as separate
    parameters and the per-file gate refused it at `PLR0913` — correctly, because they are two
    spellings of ONE identity, and a signature offering both invites a suite to report under a
    key the runner indexes by and a name a human reads, drifting apart with nothing to catch it.
    That is `census-keyed-on-one-spelling` at the emitter rather than the reader.
    """
    return Path(key).stem.removesuffix(_SUFFIX)


def record(
    key: str, passed: int, total: int, *, skipped: int = 0, reason: str | None = None
) -> dict[str, object]:
    """Build the typed result row for one suite.

    ⚑ SKIPPED CASES ARE NOT IN `total`, which `rungs.record` argues and this must match. A suite
    that ran 8 of 12 reports `8/8 (4 skipped)`, because `8/12` reads as four FAILING assertions
    and sends a reader hunting for them.

    ⚑ `passed`/`total` ARE THE VERDICT AND ARE REQUIRED. They are also what distinguishes a
    suite's result from any other row a suite might print — a witness verdict row carries `state`
    and no counts, so the numbers are what make this unambiguously THE result line.
    """
    row: dict[str, object] = {
        "kind": "verdict",
        "schema": SCHEMA,
        "key": key,
        "passed": int(passed),
        "total": int(total),
        "skipped": int(skipped),
        "state": "vacuous" if not total else ("ok" if passed == total else "cases"),
    }
    if reason:
        row["reason"] = str(reason)
    return row


def emit(key: str, passed: int, total: int, *, skipped: int = 0, reason: str | None = None) -> None:
    """Print the typed result on its own line. ONE per suite, the last word.

    ⚑ `sort_keys` IS NOT COSMETIC. The record lands in stamps and logs that get diffed across
    runs; an unstable key order makes every run differ from the last and buries a real change.

    ⚑⚑ IT IS EMITTED ON EVERY PATH, INCLUDING THE ZERO ONE. A suite that ran nothing must still
    SAY so in the machine-readable form — omitting the record there makes a vacuous suite
    indistinguishable from a killed one, collapsing `vacuous` into `unfit`/`silent`, which are
    three different next actions.
    """
    sys.stdout.write(
        RECORD_PREFIX
        + json.dumps(record(key, passed, total, skipped=skipped, reason=reason), sort_keys=True)
        + "\n"
    )


def report(
    key: str, passed: int, total: int, *, skipped: int = 0, reason: str | None = None
) -> int:
    """Emit the record, then the human line, and return the suite's exit code.

    ⚑⚑ THE PROSE LINE STAYS AND THAT IS NOT A REGEX FALLBACK. `suite_record.read_result` tries
    the record FIRST and unconditionally, so a suite emitting one is migrated by construction and
    its banner can never be re-read as its verdict — the two readings that came apart silently
    can no longer both be consulted. Keeping the human line costs nothing and removes the only
    reason a converter would hesitate.

    ⚑ AND A ZERO DENOMINATOR IS NOT A PASS. `0/0` satisfies the old prose regex while asserting
    nothing — measured on `spool`, whose 8 assertions never ran while the gate read green. A
    suite with no cases reports and REFUSES.
    """
    emit(key, passed, total, skipped=skipped, reason=reason)
    tail = f" ({skipped} skipped: {reason or 'no reason given'})" if skipped else ""
    label = label_of(key)
    if not total:
        sys.stdout.write(
            f"{label} selftest: 0/0 — NO CASES RAN; a zero denominator is not a pass{tail}\n"
        )
        return 1
    sys.stdout.write(f"{label} selftest: {passed}/{total}{tail}\n")
    return 0 if passed == total else 1


# ⚑ `--selftest` DELEGATES TO THE SIBLING SUITE (⟡selftest-discovery, ⟡silent-nine); anything
# else refuses rather than exiting 0, for the same reason `gen_selftest_mk` now does — a module
# with no command line that accepts every flag is indistinguishable from one that satisfied it.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import suite_emit_selftest

        sys.exit(suite_emit_selftest.selftest())
    sys.stderr.write(
        "suite_emit is a library — it emits a record for a suite that calls it.\n"
        "usage: suite_emit.py --selftest\n"
    )
    sys.exit(2)
