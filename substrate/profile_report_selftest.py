#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.profile_report`: the denominator, the truncation, and the absent RSS.

⚑⚑ THESE ARMS EXIST BECAUSE THE REPORT RETURNS LINES RATHER THAN PRINTING. None of what is asserted
here — that the target is named, that a cut table says it was cut, that an unreadable procfs does
not render as a zero — is reachable through a function whose only output is stdout. The split is
what turned three prose caveats into three checkable claims.

⚑⚑ THE DENOMINATOR ARM IS THE ONE WITH HISTORY. A profile hardcoded to one target, reported without
naming it, gave a reader chasing one suite a measurement of a DIFFERENT PROGRAM — and nothing in the
output said so. An arm that only checked "some lines came back" would pass on exactly that report.

⚑ NO ARM ASSERTS AN EXACT LAYOUT. Column widths are presentation and will move; what must hold is
that a named figure APPEARS and that a suppressed one does NOT. Pinning the spacing would make this
suite fire on every cosmetic edit while still missing a dropped figure.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mikemol.witness import witness_family

from substrate import profile_report, suite_emit
from substrate.process_memory import UNKNOWN, Reading
from substrate.profile_join import Allocation, Joined, Orphan, Row, Site, Timing

_READING = Reading(
    rss_before=100_000_000,
    rss_after=180_000_000,
    rss_collected=170_000_000,
    traced_base=5_000_000,
    traced_current=35_000_000,
    traced_peak=95_000_000,
    collected_objects=4_242,
)

_BLIND = Reading(
    rss_before=UNKNOWN,
    rss_after=UNKNOWN,
    rss_collected=UNKNOWN,
    traced_base=0,
    traced_current=10_000_000,
    traced_peak=10_000_000,
    collected_objects=0,
)


def _row(name: str, line: int, seconds: float, size: int) -> Row:
    """Build one joined row for a case, keeping the arms free of constructor noise."""
    return Row(Site(f"/tree/{name}.py", line, name), Timing(1, seconds), Allocation(size, 1))


def the_report_names_the_target_it_measured(out: list[str]) -> int:
    """Check that the rendered summary states which program was run.

    ⚑⚑ THIS IS THE DENOMINATOR ARM. Without the target in the output, a table is read as covering
    whatever the reader had in mind — which is how a measurement of one function was acted on as a
    measurement of another, with the limitation surviving only in prose that then evaporated.
    """
    lines = profile_report.memory_lines("order", _READING)
    if not any("order()" in line for line in lines):
        out.append(f"selftest: the report never names its target: {lines[:1]}")
        return 1
    return 0


def an_unreadable_procfs_is_absent_rather_than_zero(out: list[str]) -> int:
    """Check that a failed RSS read suppresses the subtraction instead of rendering it.

    ⚑⚑ THE SUPPRESSED FIGURE IS THE POINT. With RSS at the sentinel, `unattributed` computes to the
    negated traced figure — a plausible-looking number describing nothing. The arm asserts BOTH
    that the absence is announced and that the derived figure is withheld; checking only the first
    would accept a report that said "unknown" and then printed the fiction anyway.
    """
    bad = 0
    lines = profile_report.memory_lines("order", _BLIND)
    text = "\n".join(lines)
    if profile_report.NO_RSS not in text:
        out.append("selftest: an unreadable procfs was not announced as unknown")
        bad += 1
    if "UNATTRIBUTED" in text:
        out.append("selftest: the unattributed subtraction was rendered against a sentinel")
        bad += 1
    if "ABSENT, not zero" not in text:
        out.append("selftest: the absence was not distinguished from a zero measurement")
        bad += 1
    return bad


def a_readable_procfs_reports_the_unattributed_remainder(out: list[str]) -> int:
    """Check the positive control for the arm above: with real RSS, the figure appears.

    ⚑ WITHOUT THIS, A REPORT THAT NEVER RENDERED THE REMAINDER would pass the suppression arm by
    vacuity — and the remainder is the single figure that tells a reader to stop looking for
    allocation detail.
    """
    text = "\n".join(profile_report.memory_lines("order", _READING))
    if "UNATTRIBUTED" not in text:
        out.append("selftest: a readable reading did not report the unattributed remainder")
        return 1
    return 0


def a_truncated_table_says_that_it_truncated(out: list[str]) -> int:
    """Check that cutting the table to its limit is announced with the full total.

    ⚑⚑ A SILENT CUT IS THE IMPLICIT-POPULATION DEFECT THE INSTRUMENT EXISTS TO AVOID. The reader
    cannot tell "these are all the rows" from "these are the rows that fit", and both look like a
    complete answer. The total must appear, not merely the word "more".
    """
    bad = 0
    over = profile_report.JOINED_ROWS + 5
    rows = tuple(_row("f", i, 10.0 - i * 0.01, 0) for i in range(over))
    text = "\n".join(profile_report.joined_lines(Joined(rows, ())))
    if "not shown" not in text:
        out.append("selftest: a truncated table did not announce the truncation")
        bad += 1
    if str(over) not in text:
        out.append(f"selftest: the truncation note omits the total of {over}")
        bad += 1
    return bad


def an_untruncated_table_makes_no_such_claim(out: list[str]) -> int:
    """Check the negative control: a table that fits does not claim rows were withheld.

    ⚑ AN UNCONDITIONAL NOTE WOULD PASS THE TRUNCATION ARM while telling every reader of every
    complete table that they were seeing a fragment — which is the same defect pointed the other
    way, and strictly harder to notice.
    """
    rows = tuple(_row("f", i, 1.0, 0) for i in range(3))
    text = "\n".join(profile_report.joined_lines(Joined(rows, ())))
    if "not shown" in text:
        out.append("selftest: a complete table claimed rows were withheld")
        return 1
    return 0


def the_orphan_arm_is_rendered_and_explained(out: list[str]) -> int:
    """Check that allocating sites with no call row appear, labelled as what they are.

    ⚑⚑ PRESENTED WITHOUT EXPLANATION, an allocation with no time column reads as a measurement
    failure rather than as a comprehension or a module-level table. This arm pins that the second
    arm of the join both SURVIVES rendering and arrives with its explanation attached.
    """
    bad = 0
    orphans = (Orphan(Site("/tree/big.py", 3), Allocation(9_000_000, 2)),)
    text = "\n".join(profile_report.joined_lines(Joined((), orphans)))
    if "big.py:3" not in text:
        out.append("selftest: the orphan allocation site was not rendered")
        bad += 1
    if "NO CALL ROW" not in text:
        out.append("selftest: the orphan arm was rendered without its explanation")
        bad += 1
    return bad


def the_repeated_work_table_carries_its_fix(out: list[str]) -> int:
    """Check that the repeated-work table arrives with the memoise-at-the-owner note.

    ⚑ THE TABLE ALONE INVITES PARALLELISING THE REPETITION, which speeds up doing the same thing
    many times instead of stopping it. The advice is part of the report for that reason, so its
    absence is a defect rather than a cosmetic loss.
    """
    bad = 0
    text = "\n".join(profile_report.repeated_lines((_row("mask", 12, 27.0, 0),)))
    if "mask" not in text:
        out.append("selftest: the repeated-work candidate was not rendered")
        bad += 1
    if "memoise at" not in text:
        out.append("selftest: the repeated-work table arrived without its fix")
        bad += 1
    if profile_report.repeated_lines(()):
        out.append("selftest: an empty candidate list still produced a table")
        bad += 1
    return bad


def a_site_is_rendered_relative_to_a_given_root(out: list[str]) -> int:
    """Check that the root argument reaches the rendered site.

    ⚑ A REPORT THAT ACCEPTED A ROOT AND IGNORED IT would print absolute paths everywhere and pass
    every other arm here, since none of them supply one.
    """
    rows = (_row("f", 7, 1.0, 0),)
    text = "\n".join(profile_report.joined_lines(Joined(rows, ()), Path("/tree")))
    if "/tree/f.py" in text:
        out.append("selftest: the root was accepted but not applied to the rendered site")
        return 1
    if "f.py:7" not in text:
        out.append("selftest: the site was not rendered at all")
        return 1
    return 0


FAMILY = witness_family.of(
    key="profile_report",
    apex="the rendered profile names the target it measured, announces a truncation with the full "
    "total rather than cutting silently, keeps the allocating-sites arm with its "
    "explanation, and reports an unreadable procfs as absent — withholding the subtraction "
    "that would otherwise render a sentinel as a confident measurement",
    subject="the lines `substrate.profile_report` returns for a constructed reading and join",
    members=(
        witness_family.Member(
            name="the_report_names_the_target_it_measured",
            claim="the rendered summary states which program was run",
        ),
        witness_family.Member(
            name="an_unreadable_procfs_is_absent_rather_than_zero",
            claim="a failed RSS read is announced and its subtraction withheld",
            cases=3,
        ),
        witness_family.Member(
            name="a_readable_procfs_reports_the_unattributed_remainder",
            claim="with real resident figures the remainder is rendered",
            premises=("an_unreadable_procfs_is_absent_rather_than_zero",),
        ),
        witness_family.Member(
            name="a_truncated_table_says_that_it_truncated",
            claim="a cut table announces the cut and the full total",
            cases=2,
        ),
        witness_family.Member(
            name="an_untruncated_table_makes_no_such_claim",
            claim="a table that fits does not claim rows were withheld",
            premises=("a_truncated_table_says_that_it_truncated",),
        ),
        witness_family.Member(
            name="the_orphan_arm_is_rendered_and_explained",
            claim="allocating sites with no call row appear, labelled as what they are",
            cases=2,
        ),
        witness_family.Member(
            name="the_repeated_work_table_carries_its_fix",
            claim="the repeated-work table arrives with its note, and is absent when empty",
            cases=3,
        ),
        witness_family.Member(
            name="a_site_is_rendered_relative_to_a_given_root",
            claim="the root argument reaches the rendered site",
        ),
    ),
)

_ARMS = (
    the_report_names_the_target_it_measured,
    an_unreadable_procfs_is_absent_rather_than_zero,
    a_readable_procfs_reports_the_unattributed_remainder,
    a_truncated_table_says_that_it_truncated,
    an_untruncated_table_makes_no_such_claim,
    the_orphan_arm_is_rendered_and_explained,
    the_repeated_work_table_carries_its_fix,
    a_site_is_rendered_relative_to_a_given_root,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/profile_report_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
