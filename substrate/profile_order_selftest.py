#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.profile_order`: the composition, and the probe that must not vanish.

⚑⚑ THE PROBE ARMS CARRY THE WEIGHT HERE. The composition itself is three calls in a row, and its
correctness is already asserted by the four suites underneath it. What is NOT asserted anywhere
else is the failure handling: a counter that cannot be read must be reported as unavailable, not
silently skipped, because a missing section reads exactly like a section with nothing to say.

⚑⚑ THE INJECTION IS WHAT KEEPS THIS MODULE IN `substrate/`, so an arm pins that a probe's lines
actually reach the report. Were they dropped, the package would still import cleanly, every other
case would pass, and the counters that exist precisely to attribute per-consumer cost would go
unread — which is the state this instrument was rebuilt to end.

⚑ THE TARGET IS A TRIVIAL CALLABLE. This suite is not re-testing the profiler; it is testing that
the pieces are wired together and that the writing happens exactly once, to the stream given.
"""

from __future__ import annotations

import io
import sys

from mikemol.witness import witness_family

from substrate import profile_order, suite_emit
from substrate.profile_order import Probe

#: What the failing probe raises — the shape a renamed or removed counter actually produces.
_MISSING_ATTR = "module has no attribute 'mask_stats'"


def _target() -> int:
    """Do a trivial amount of work — enough to profile, not enough to be slow."""
    return sum(range(100))


def _raising_lines() -> list[str]:
    """Fail the way a renamed or removed counter fails."""
    raise AttributeError(_MISSING_ATTR)


def the_report_names_the_target_and_carries_the_memory_summary(out: list[str]) -> int:
    """Check that the composed report opens with the denominator and the traced figures.

    ⚑ THE COMPOSITION'S ONE JOB IS THAT NOTHING IS LOST BETWEEN THE FOUR PIECES. If the memory
    summary were dropped, the table below it would still render and still look complete.
    """
    bad = 0
    text = "\n".join(profile_order.report_lines("tiny", _target))
    if "tiny()" not in text:
        out.append("selftest: the composed report does not name its target")
        bad += 1
    if "TRACED" not in text:
        out.append("selftest: the memory summary did not reach the composed report")
        bad += 1
    return bad


def a_probe_that_works_reaches_the_report(out: list[str]) -> int:
    """Check that injected counter lines are appended to the report.

    ⚑⚑ THIS IS THE INJECTION ARM. Dropping the probe's output leaves a package that imports, a
    suite that passes, and a set of per-consumer counters that nobody reads — which is exactly the
    condition that let "which consumer is paying for the round trips" stay a guess for four runs.
    """
    probe = Probe(name="MASK CACHE", lines=lambda: ["MASK CACHE: 10 calls, 9 hits"])
    text = "\n".join(profile_order.report_lines("tiny", _target, (probe,)))
    if "MASK CACHE: 10 calls" not in text:
        out.append("selftest: an injected probe's lines never reached the report")
        return 1
    return 0


def a_probe_that_fails_is_reported_as_unavailable(out: list[str]) -> int:
    """Check that a raising probe becomes a named finding rather than a silence.

    ⚑⚑ THE SUPERSEDED BODY WRAPPED THIS IN `except Exception: pass`. A renamed function then
    produced a report with the section simply absent — indistinguishable from a cache with nothing
    to say and from one never consulted. All three look like a complete report, and only one of
    them is. The arm checks that the probe is NAMED and that the absence is called absence.
    """
    bad = 0
    probe = Probe(name="MASK CACHE", lines=_raising_lines)
    text = "\n".join(profile_order.report_lines("tiny", _target, (probe,)))
    if "MASK CACHE" not in text:
        out.append("selftest: a failing probe vanished from the report entirely")
        bad += 1
    if "UNAVAILABLE" not in text:
        out.append("selftest: a failing probe was not reported as unavailable")
        bad += 1
    if "ABSENT, not empty" not in text:
        out.append("selftest: the unread counter was not distinguished from an empty one")
        bad += 1
    return bad


def one_failing_probe_does_not_suppress_another(out: list[str]) -> int:
    """Check that probes are independent, so an early failure does not hide a later result.

    ⚑ A LOOP THAT RETURNED ON THE FIRST FAILURE would pass the arm above while silently truncating
    every report whose first counter happens to be missing — and the reader would see a report
    that ends early rather than one that says why.
    """
    probes = (
        Probe(name="FIRST", lines=_raising_lines),
        Probe(name="SECOND", lines=lambda: ["SECOND: 3 rows"]),
    )
    text = "\n".join(profile_order.report_lines("tiny", _target, probes))
    if "SECOND: 3 rows" not in text:
        out.append("selftest: a failing probe suppressed the one after it")
        return 1
    return 0


def an_empty_probe_adds_nothing(out: list[str]) -> int:
    """Check that a probe with no lines contributes no blank section.

    ⚑ THE DISTINCTION THIS PRESERVES is between a counter that FAILED (named, above) and one that
    simply had nothing to report. Emitting a bare header for the latter would make an idle cache
    look like a defect.
    """
    quiet = Probe(name="QUIET", lines=list)
    text = "\n".join(profile_order.report_lines("tiny", _target, (quiet,)))
    if "QUIET" in text:
        out.append("selftest: a probe with no lines still produced a section")
        return 1
    return 0


def the_writer_puts_the_report_on_the_given_stream(out: list[str]) -> int:
    """Check that `profile` writes to the stream it was handed and returns success.

    ⚑ PROFILING IS A MEASUREMENT, NOT A VERDICT, so a non-zero return would turn this instrument
    into a gate whose threshold nobody chose. The stream argument is what makes the writing
    testable at all — without it this arm could only inspect stdout.
    """
    bad = 0
    buffer = io.StringIO()
    code = profile_order.profile("tiny", _target, (), buffer)
    if code != 0:
        out.append(f"selftest: profiling returned {code}, not success")
        bad += 1
    if "tiny()" not in buffer.getvalue():
        out.append("selftest: the report did not reach the given stream")
        bad += 1
    return bad


FAMILY = witness_family.of(
    key="profile_order",
    apex="composing the measurement, the join and the rendering keeps the target's name and the "
    "memory summary intact, appends each injected counter probe, reports a probe that "
    "cannot be read as explicitly unavailable rather than omitting its section, keeps "
    "probes independent of one another, and writes once to the stream it was given",
    subject="the lines and exit code `substrate.profile_order` produces for a trivial target",
    members=(
        witness_family.Member(
            name="the_report_names_the_target_and_carries_the_memory_summary",
            claim="the composed report opens with the denominator and the traced figures",
            cases=2,
        ),
        witness_family.Member(
            name="a_probe_that_works_reaches_the_report",
            claim="injected counter lines are appended to the report",
        ),
        witness_family.Member(
            name="a_probe_that_fails_is_reported_as_unavailable",
            claim="a raising probe becomes a named finding rather than a silence",
            cases=3,
        ),
        witness_family.Member(
            name="one_failing_probe_does_not_suppress_another",
            claim="probes are independent, so an early failure hides no later result",
            premises=("a_probe_that_fails_is_reported_as_unavailable",),
        ),
        witness_family.Member(
            name="an_empty_probe_adds_nothing",
            claim="a probe with no lines contributes no blank section",
            premises=("a_probe_that_works_reaches_the_report",),
        ),
        witness_family.Member(
            name="the_writer_puts_the_report_on_the_given_stream",
            claim="profile writes to the stream it was handed and returns success",
            cases=2,
        ),
    ),
)

_ARMS = (
    the_report_names_the_target_and_carries_the_memory_summary,
    a_probe_that_works_reaches_the_report,
    a_probe_that_fails_is_reported_as_unavailable,
    one_failing_probe_does_not_suppress_another,
    an_empty_probe_adds_nothing,
    the_writer_puts_the_report_on_the_given_stream,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/profile_order_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
