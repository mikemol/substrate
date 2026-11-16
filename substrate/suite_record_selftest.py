#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.suite_record` — the reader must parse what the emitter emits.

⚑⚑⚑ THE SEPARATOR CASE IS THE ITEM, AND IT IS HERE BECAUSE THE TWO HALVES DISAGREED IN
PRODUCTION. `scratch/rungs.py` owns the row contract and spells it `"#row\t"`; this reader
spelled it `"#row "` with a space. Every `startswith` therefore failed on a real record, the
structural arm never fired, the prose arm found no `N/M` in `0 of 15 check(s) failed`, and
suites passing 15 of 15 were reported `unread (0/0)` and failed their make targets.

⚑⚑ AND NOTHING CAUGHT IT BECAUSE THIS MODULE HAD NO SUITE. `suite_outcome_selftest` covers the
CLASSIFIER thoroughly — it pins that a parsed count is never reported unread — but the
classifier was never reached: the failure was upstream of it, in the parse. A case over the
verdict logic cannot see a reader that hands it nothing.

⚑ THE FIXTURE IS BUILT FROM THE REAL PREFIX, NOT FROM A TYPED COPY. A case that spelled the
separator itself would pass against whatever this module happens to say and re-create the exact
defect one layer down — two spellings again, with a green suite over them.
"""

from __future__ import annotations

import sys

from substrate import corpus, suite_record

# The authority for the row contract. ⚑ READ AS TEXT, NOT IMPORTED: `scratch/` is unpackaged and
# `rungs.py` executes at import, so this case reads the constant out of the file that declares it
# rather than loading a CLI tool to compare one string.
_AUTHORITY = corpus.ROOT / "scratch" / "rungs.py"
_AUTHORITY_DECL = 'ROW_PREFIX = "#row\\t"'

# The separator the emitter writes, spelled once here for the assertion below.
_EXPECTED_PREFIX = "#row\t"

# A complete record line, in the emitter's own shape.
_RECORD = (
    '{"key": "probe.py", "kind": "verdict", "passed": 15, "schema": 1, '
    '"skipped": 0, "state": "ok", "total": 15}'
)

# What that record reports.
_PASSED = 15
_TOTAL = 15

# The counts the prose and malformed-record fixtures carry.
_PROSE_TOTAL = 12
_FALLBACK_TOTAL = 3

# A suite that passes every case and prints NO `N/M` anywhere — the shape that made the defect
# visible, since the prose fallback cannot rescue it.
_NO_PROSE = "  ok   a case\nselftest: 0 of 15 check(s) failed\n"


def the_reader_uses_the_emitters_separator(out: list[str]) -> int:
    """Check the prefix matches the contract's authority — THE ITEM.

    ⚑⚑⚑ A TAB, NOT A SPACE. This is the assertion that was missing, and its absence cost every
    correctly-emitting suite a false `unread`. It reads the declaration out of `scratch/rungs.py`
    so the two cannot drift without this failing.
    """
    try:
        text = _AUTHORITY.read_text(encoding="utf-8")
    except OSError as exc:
        out.append(f"selftest: cannot read the row-contract authority: {exc}")
        return 1
    if _AUTHORITY_DECL not in text:
        out.append(
            f"selftest: {_AUTHORITY.name} no longer declares {_AUTHORITY_DECL!r} — "
            "the authority moved and this reader must follow it"
        )
        return 1
    if suite_record.RECORD_PREFIX != _EXPECTED_PREFIX:
        out.append(
            f"selftest: the reader's prefix is {suite_record.RECORD_PREFIX!r}, "
            "which is not what the emitter writes"
        )
        return 1
    return 0


def a_real_record_is_read_structurally(out: list[str]) -> int:
    """Check a record line in the emitter's shape reaches the structural arm.

    ⚑ AND THE ARM IS IDENTIFIED, NOT JUST THE COUNTS. `by_prose` False is what says the typed
    record was used; the same numbers arriving via the regex would be the debt path passing
    itself off as the supported one.
    """
    got = suite_record.read_result(suite_record.RECORD_PREFIX + _RECORD + "\n", 0)
    if got.by_prose:
        out.append("selftest: a typed record was read by the PROSE fallback")
        return 1
    if (got.reported.ok, got.reported.all_) != (_PASSED, _TOTAL):
        out.append(f"selftest: the record read as {got.reported.ok}/{got.reported.all_}")
        return 1
    if got.kind != "ok":
        out.append(f"selftest: a passing record classified {got.kind!r}")
        return 1
    return 0


def a_passing_suite_without_prose_is_not_unread(out: list[str]) -> int:
    """Check the exact production shape — a record plus no `N/M` — reads as ok.

    ⚑⚑ THIS IS THE FAILURE AS IT HAPPENED. The suite passed, printed a complete record, and
    printed a human line carrying no parseable ratio. With the separator wrong, BOTH arms came
    back empty and the verdict was `unread` — a reader's parse failure reported as a fact about
    the suite, which sent every reader to the wrong code.
    """
    body = _NO_PROSE + suite_record.RECORD_PREFIX + _RECORD + "\n"
    got = suite_record.read_result(body, 0)
    if got.kind != "ok":
        out.append(f"selftest: a passing suite with no prose ratio classified {got.kind!r}")
        return 1
    return 0


def the_last_record_wins(out: list[str]) -> int:
    """Check a streaming suite's trailing verdict is what is read.

    ⚑ THE VERDICT TRAILS ITS PARTS. A member emits parts as it finds them and its verdict comes
    last, so a reader taking the FIRST row reads a part and truncates the run — the defect
    `rungs.py` records in its own header.
    """
    early = (
        '{"key": "probe.py", "kind": "part", "passed": 1, "schema": 1, '
        '"skipped": 0, "state": "ok", "total": 1}'
    )
    body = suite_record.RECORD_PREFIX + early + "\n" + suite_record.RECORD_PREFIX + _RECORD + "\n"
    got = suite_record.read_result(body, 0)
    if got.reported.all_ != _TOTAL:
        out.append(f"selftest: an early part won over the verdict ({got.reported.all_})")
        return 1
    return 0


def prose_remains_the_fallback(out: list[str]) -> int:
    """Check a suite emitting no record still reads, via the debt path.

    ⚑ RATCHETED DEBT, NOT A SUPPORTED SPELLING — but removing it would strand every unmigrated
    suite, so the case pins that it still works AND that it is labelled as prose.
    """
    got = suite_record.read_result(f"selftest: {_PROSE_TOTAL}/{_PROSE_TOTAL}\n", 0)
    if not got.by_prose:
        out.append("selftest: a prose-only suite was reported as structurally read")
        return 1
    if got.reported.all_ != _PROSE_TOTAL:
        out.append(f"selftest: the prose read as {got.reported.ok}/{got.reported.all_}")
        return 1
    return 0


def a_malformed_record_falls_through_rather_than_raising(out: list[str]) -> int:
    """Check a broken record line degrades to the next arm.

    ⚑ THE LINE IS PRODUCED BY THE SUITE UNDER TEST, so it is exactly the input that can be
    wrong. A reader that raised here would turn one broken suite into no results at all.
    """
    body = (
        suite_record.RECORD_PREFIX
        + "{not json\n"
        + f"selftest: {_FALLBACK_TOTAL}/{_FALLBACK_TOTAL}\n"
    )
    got = suite_record.read_result(body, 0)
    if got.reported.all_ != _FALLBACK_TOTAL:
        out.append(f"selftest: a malformed record yielded {got.reported!r}")
        return 1
    return 0


def a_record_missing_its_counts_is_not_trusted(out: list[str]) -> int:
    """Check a record without `passed`/`total` does not read as a pass.

    ⚑ A PARSED LINE IS NOT A COUNTED ONE. The record arm must decline when the numbers are
    absent, or a well-formed row carrying no counts would report 0/0 as a verdict.
    """
    partial = '{"key": "probe.py", "kind": "verdict", "state": "ok"}'
    got = suite_record.read_result(suite_record.RECORD_PREFIX + partial + "\n", 0)
    if got.kind == "ok":
        out.append("selftest: a record with no counts classified ok")
        return 1
    return 0


_ARMS = (
    the_reader_uses_the_emitters_separator,
    a_real_record_is_read_structurally,
    a_passing_suite_without_prose_is_not_unread,
    the_last_record_wins,
    prose_remains_the_fallback,
    a_malformed_record_falls_through_rather_than_raising,
    a_record_missing_its_counts_is_not_trusted,
)

_CASE_COUNT = 3 + 3 + 1 + 1 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-record selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-record selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
