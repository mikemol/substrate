#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_emit`: the record round-trips through the runner's own reader.

⚑⚑⚑ THE ARMS DRIVE `suite_record.read_result`, NOT A STRING COMPARISON — AND THAT IS THE WHOLE
DESIGN OF THIS SUITE. An emitter checked against a hand-written expected string is checked
against a SECOND definition of the format, which is precisely the defect `suite_record`'s header
records: the prefix was once spelled with a SPACE beside an authority spelling it with a TAB,
both sides were self-consistent, and every real record went unread while the suites were correct
the whole time. A case comparing the emitted line to a literal would have passed on the wrong
spelling. Asserting that THE CONSUMER reads back what was emitted cannot.

⚑⚑ SO THIS IS A ROUND-TRIP SUITE, AND THE TWO ENDS ARE DELIBERATELY DECORRELATED. `suite_emit`
writes; `suite_record` (already in the tree, already the runner's reader) parses. Two instruments
agreeing is not coverage in general — but here the reader is the ACTUAL consumer, so agreement
with it is the property under test rather than a proxy for it.

⚑ AND `by_prose` IS THE FIELD THAT MATTERS MOST. `read_result` has three arms ordered by trust —
record, prose, nothing — and the prose arm would ALSO yield the right counts from the human line
this emitter prints beside the record. A case checking only the counts would pass with the record
entirely unread, which is the exact false green this contract exists to remove. Checking that the
result was NOT read by prose is what proves the structural arm fired.
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stdout

from mikemol.witness import witness_family

from substrate import suite_emit, suite_record

# A key with the full repo-relative shape a real suite reports under.
_KEY = "substrate/example_selftest.py"

# A passing fixture, and a short one. ⚑ NAMED, BECAUSE THE GATE REFUSED THEM AS MAGIC VALUES —
# and it was right: a bare `12` appearing in both the call and the assertion says nothing about
# whether the two are the same fact or two facts that happen to agree.
_ALL, _SOME = 12, 9

# The skip fixture: a suite that RAN this many and deliberately skipped that many, for the named
# reason. ⚑ `_RAN` IS THE DENOMINATOR AND `_SKIPPED` IS NOT IN IT — the property under test.
_RAN, _SKIPPED, _REASON = 8, 4, "store unreachable"


def _read(
    passed: int, total: int, *, skipped: int = 0, reason: str | None = None
) -> suite_record.Result:
    """Emit a record into a captured stream and read it back with the runner's reader."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        suite_emit.report(_KEY, passed, total, skipped=skipped, reason=reason)
    return suite_record.read_result(buf.getvalue(), 0 if passed == total else 1)


def the_record_is_read_structurally_not_by_prose(out: list[str]) -> int:
    """Check that the runner's reader takes the RECORD arm, not the prose fallback.

    ⚑⚑ THIS IS THE ARM THE WHOLE CONTRACT IS ABOUT. The human line beside the record also
    matches the prose regex, so counts alone cannot distinguish a suite that emitted a record
    from one that merely printed its totals. `by_prose` being False is the only observable that
    says the structural arm fired — and it is exactly what the ratchet censuses.
    """
    if _read(_ALL, _ALL).by_prose:
        out.append("selftest: the emitted record was read by PROSE, not structurally")
        return 1
    return 0


def the_counts_survive_the_round_trip(out: list[str]) -> int:
    """Check that passed and total read back as emitted.

    ⚑ A RECORD THAT PARSES BUT CARRIES THE WRONG NUMBERS IS WORSE THAN ONE THAT DOES NOT PARSE.
    The unread case is reported as `unread` and someone looks; a mis-keyed count is banked.
    """
    got = _read(_SOME, _ALL).reported
    if (got.ok, got.all_) != (_SOME, _ALL):
        out.append(f"selftest: counts read back as {(got.ok, got.all_)}, want {(_SOME, _ALL)}")
        return 1
    return 0


def a_failing_suite_reads_as_cases_not_ok(out: list[str]) -> int:
    """Check that the verdict kind is derived from the NUMBERS, not from the state field.

    ⚑ A SUITE MUST NOT BE ABLE TO GRADE ITSELF GREEN. `suite_record` derives the kind via
    `verdict_kind`, so this arm pins the property that a short count is a `cases` verdict
    regardless of what the emitter wrote into `state`.
    """
    if _read(_SOME, _ALL).kind == "ok":
        out.append("selftest: a short count reported kind 'ok'")
        return 1
    return 0


def a_zero_denominator_refuses(out: list[str]) -> int:
    """Check that a suite with no cases returns non-zero and does not read as ok.

    ⚑⚑ A ZERO DENOMINATOR SATISFIES THE OLD PROSE REGEX WHILE ASSERTING NOTHING — measured on
    `spool`, whose 8 assertions never ran while the gate read green. Both halves are checked:
    the exit code the suite returns, and the kind the reader derives.
    """
    bad = 0
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = suite_emit.report(_KEY, 0, 0)
    if code == 0:
        out.append("selftest: a zero-case suite returned 0")
        bad += 1
    if _read(0, 0).kind == "ok":
        out.append("selftest: a zero-denominator result read as 'ok'")
        bad += 1
    return bad


def skipped_cases_are_carried_and_not_in_the_total(out: list[str]) -> int:
    """Check that `skipped` round-trips and does not inflate the denominator.

    ⚑ A SUITE THAT RAN EIGHT AND SKIPPED FOUR REPORTS EIGHT OF EIGHT. Folding the skipped into
    `total` would render eight of twelve, which reads as four FAILING assertions and sends a
    reader hunting for them.
    """
    bad = 0
    result = _read(_RAN, _RAN, skipped=_SKIPPED, reason=_REASON)
    if result.skipped != _SKIPPED:
        out.append(f"selftest: skipped read back as {result.skipped}, want {_SKIPPED}")
        bad += 1
    if result.reported.all_ != _RAN:
        out.append(
            f"selftest: total is {result.reported.all_}, want {_RAN} — the skipped "
            f"cases must not be in the denominator"
        )
        bad += 1
    if result.reason != _REASON:
        out.append(f"selftest: reason read back as {result.reason!r}")
        bad += 1
    return bad


def the_label_is_derived_from_the_key(out: list[str]) -> int:
    """Check that a suite's human label comes from its key, with the suffix stripped.

    ⚑ ONE IDENTITY, NOT TWO. The per-file gate refused a signature taking `key` and `label`
    separately, which was the right call — two spellings of one name drift, and nothing catches
    it. This arm pins the derivation so the refusal's lesson stays enforced.
    """
    bad = 0
    for key, want in (
        (_KEY, "example"),
        ("substrate/walk_scope_selftest.py", "walk_scope"),
        ("scripts/tool.py", "tool"),
    ):
        got = suite_emit.label_of(key)
        if got != want:
            out.append(f"selftest: label_of({key!r}) is {got!r}, want {want!r}")
            bad += 1
    return bad


FAMILY = witness_family.of(
    key="suite_emit",
    apex="a suite's typed record round-trips through the runner's own reader: read "
    "structurally rather than by prose, with its counts, its skips and its kind intact",
    subject="the records `substrate.suite_emit` writes and `substrate.suite_record` reads",
    members=(
        witness_family.Member(
            name="the_record_is_read_structurally_not_by_prose",
            claim="the runner's reader takes the record arm, not the prose fallback",
        ),
        witness_family.Member(
            name="the_counts_survive_the_round_trip",
            claim="passed and total read back as emitted",
            premises=("the_record_is_read_structurally_not_by_prose",),
        ),
        witness_family.Member(
            name="a_failing_suite_reads_as_cases_not_ok",
            claim="the verdict kind is derived from the numbers, not the state field",
        ),
        witness_family.Member(
            name="a_zero_denominator_refuses",
            claim="a suite with no cases returns non-zero and does not read as ok",
            cases=2,
        ),
        witness_family.Member(
            name="skipped_cases_are_carried_and_not_in_the_total",
            claim="skipped round-trips and does not inflate the denominator",
            cases=3,
        ),
        witness_family.Member(
            name="the_label_is_derived_from_the_key",
            claim="a suite's human label comes from its key, with the suffix stripped",
            cases=3,
        ),
    ),
)

_ARMS = (
    the_record_is_read_structurally_not_by_prose,
    the_counts_survive_the_round_trip,
    a_failing_suite_reads_as_cases_not_ok,
    a_zero_denominator_refuses,
    skipped_cases_are_carried_and_not_in_the_total,
    the_label_is_derived_from_the_key,
)

_CASE_COUNT = FAMILY.count

# ⚑ THIS SUITE REPORTS THROUGH THE MODULE IT TESTS, which is a positive control nobody had to
# write: if `suite_emit.report` breaks, this suite's own result becomes unreadable to the runner.
_SELF_KEY = "substrate/suite_emit_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
