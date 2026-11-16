#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read one suite's result from its output: the typed record first, prose only as debt.

⚑⚑ THE RECORD WINS OVER THE PROSE, UNCONDITIONALLY. A migrated suite that still prints
`selftest: N/M` for a human must not have that line re-read as its result — two readings of
one run is how they come apart silently, and the prose is the one that drifts.

⚑ AND THE OUTPUT REACHES THE CLASSIFIER ON ONE ARM ONLY, deliberately. Both readers have
failed there and nowhere else, so the unreadable-output conjunction is consulted exactly where
it can hold. Passing the text on a matched arm would let a parsed suite's incidental banner
line change its verdict.

⚑⚑ IT IS A MODULE SO A CASE CAN REACH IT. This decision — record first, prose as ratcheted
debt, kind derived from the NUMBERS — was the thing that broke, and while it lived inline in a
run loop no case could drive it: a suite could test the pieces and only hope the loop wired
them the way it described.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass

from substrate.suite_outcome import Reported, verdict_kind

# ⚑ THE TYPED RECORD, EMITTED AS ONE LINE OF JSON PREFIXED SO IT IS UNAMBIGUOUS. A suite that
# prints it is read structurally; one that does not falls to the prose reader, which is debt.
#
# ⚑⚑⚑ THE SEPARATOR IS A TAB, AND SPELLING IT AS A SPACE HERE SILENTLY UNREAD EVERY SUITE THAT
# EMITTED CORRECTLY. `scratch/rungs.py` OWNS this contract — it defines `ROW_PREFIX = "#row\t"`
# with `parse_rows`/`fold` beside it, is selftested, and its own header argues at length against
# a second encoding of the row line. This module minted one anyway: `"#row "`, with a space. So
# `line.startswith(RECORD_PREFIX)` was FALSE for every real record, the structural arm never
# fired, the prose arm found no `N/M` in `0 of 15 check(s) failed`, and the suite was reported
# `unread (0/0)` — WHILE PASSING 15 OF 15. MEASURED on the roster run: suites printing
# `state: "ok"` and a complete `#row` line failed their make targets with Error 1.
#
# ⚑⚑ IT IS THE `census-keyed-on-one-spelling` SHAPE AT ITS MOST EXPENSIVE, because the two halves
# DISAGREE SILENTLY AND THE FAILURE LOOKS LIKE THE SUITE'S FAULT. A reader seeing `unread` goes
# to the suite's code — which is correct — rather than to the reader that cannot parse it. The
# emitter was right the whole time.
#
# ⚑ AND IT IS STILL RESTATED RATHER THAN IMPORTED, WHICH IS DEBT WITH A REASON. `scratch/` is
# unpackaged (`pyproject.toml` declares `substrate` and `scripts` only), `rungs.py` is a CLI tool
# that executes at import, and `check_scratch_independence` gates `substrate/` against depending
# on `scratch/`. Loading a whole tool through `scratch_module` to read one constant, on the path
# every suite takes, is the wrong weight. So the duplication stays and the AUTHORITY is named:
# if these two ever disagree again, `scratch/rungs.py:ROW_PREFIX` is right and this is wrong.
RECORD_PREFIX = "#row\t"

# The prose fallback: `N/M` anywhere in a line. Ratcheted debt, not a supported spelling.
RESULT = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")


@dataclass(frozen=True, slots=True)
class Result:
    """What one suite reported, how it was read, and what kind of outcome it is."""

    reported: Reported
    kind: str
    by_prose: bool
    skipped: int = 0
    reason: str | None = None


def _fields(line: str) -> dict[str, object] | None:
    """Parse one record line into a field map, or None when it is not one.

    ⚑ THE NARROWING IS AT THE SEAM. `json.loads` returns `Any`, and a raw return would carry
    that into every field read downstream — the recorded boundary. Asserting `dict` once, here,
    is what keeps the readers below concretely typed.

    ⚑ AND A MALFORMED RECORD READS AS ABSENT, NEVER AS A CRASH. The line is produced by the
    suite UNDER TEST, so it is exactly the input that can be wrong — a runner that raised on it
    would turn one broken suite into no results at all.
    """
    try:
        parsed: object = json.loads(line[len(RECORD_PREFIX) :])
    except ValueError:
        return None
    if not isinstance(parsed, dict):
        return None
    return {str(k): v for k, v in parsed.items()}


def _record(out: str) -> dict[str, object] | None:
    """Return the typed record a suite emitted, or None.

    ⚑ THE LAST ONE WINS. A suite that emits a record per phase reports its final state, and
    reading the first would freeze an intermediate — the same reason a ratchet records the last
    accepted reading rather than the first.
    """
    for line in reversed(out.splitlines()):
        if line.startswith(RECORD_PREFIX):
            return _fields(line)
    return None


def _ints(rec: dict[str, object], *keys: str) -> tuple[int, ...] | None:
    """Narrow a record's numeric fields, or None when any is missing or not an int."""
    out: list[int] = []
    for key in keys:
        got = rec.get(key)
        if not isinstance(got, int):
            return None
        out.append(got)
    return tuple(out)


def _from_record(rec: dict[str, object], returncode: int) -> Result | None:
    """Build a result from a typed record, or None when its counts are unreadable."""
    counts = _ints(rec, "passed", "total")
    if counts is None:
        return None
    passed, total = counts
    reported = Reported(matched=True, ok=passed, all_=total)
    skipped = rec.get("skipped")
    reason = rec.get("reason")
    return Result(
        reported=reported,
        kind=verdict_kind(reported, returncode),
        by_prose=False,
        skipped=skipped if isinstance(skipped, int) else 0,
        reason=reason if isinstance(reason, str) else None,
    )


def read_result(out: str, returncode: int) -> Result:
    """Read one suite's captured output into a result.

    ⚑ THE THREE ARMS ARE ORDERED BY TRUST: a typed record, then prose, then nothing. Only the
    last passes the output to the classifier, so `unread` can be distinguished from `silent`
    without a parsed suite's banner affecting its verdict.
    """
    rec = _record(out)
    if rec is not None:
        from_rec = _from_record(rec, returncode)
        if from_rec is not None:
            return from_rec

    m = RESULT.search(out)
    if m:
        reported = Reported(matched=True, ok=int(m.group(1)), all_=int(m.group(2)))
        return Result(reported=reported, kind=verdict_kind(reported, returncode), by_prose=True)

    none = Reported.none()
    return Result(
        reported=none, kind=verdict_kind(none, returncode, out=out, result=RESULT), by_prose=False
    )
