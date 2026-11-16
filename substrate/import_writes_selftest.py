#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.import_writes` — a guard that excuses everything is not a guard.

⚑⚑⚑ THE POSITIVE CONTROL IS THE WHOLE POINT HERE, because this predicate fails SAFE and a
fail-safe predicate is exactly the kind that passes a suite while doing nothing. If the detector
cannot be reached, `why_not_import` returns a reason for EVERY script — which is safe, and turns
the consumer's entire roster into UNMEASURABLE. That is not a hypothetical: it is what the first
cut did, because the authority lives in `scratch/` and was looked up against `scripts/`.

⚑⚑ SO EVERY ARM IS PAIRED. One specimen that genuinely writes at import, one that genuinely does
not, and an explicit check that the two answers DIFFER. A suite asserting only "the writer is
detected" would pass with a predicate hard-wired to "everything writes".
"""

from __future__ import annotations

import sys

from substrate import import_writes

# A tool whose whole body is top-level and whose final `else:` writes — importing it RUNS it.
_WRITER = "scripts/sppf_node_index.py"

# A gate whose every statement sits under a `def`, so importing it runs nothing.
_READER = "scripts/check_baseline_health.py"


def the_detector_is_reachable(out: list[str]) -> int:
    """Check the authority loads at all.

    ⚑ THIS ARM EXISTS BECAUSE ITS ABSENCE WAS THE BUG. With the detector unreachable every other
    behaviour here is still "correct" — it just answers "do not import" to everything. Pinning
    reachability separately is what stops a silent degradation from reading as caution.
    """
    if import_writes.detector() is None:
        out.append("selftest: the write-polarity authority could not be loaded")
        return 1
    return 0


def a_tool_that_writes_at_import_is_named(out: list[str]) -> int:
    """Check a write-default tool is reported, with a reason rather than a bare flag."""
    got = import_writes.why_not_import(_WRITER)
    bad = 0
    if not got:
        out.append(f"selftest: {_WRITER} was not detected as write-default")
        bad += 1
    elif got == import_writes.UNAVAILABLE:
        out.append("selftest: the writer was excused by the unavailable-detector branch")
        bad += 1
    return bad


def a_pure_reader_is_not_excused(out: list[str]) -> int:
    """Check the POSITIVE CONTROL: a tool that writes nothing is reported as safe to import.

    ⚑ WITHOUT THIS ARM THE GUARD COULD RETURN A REASON FOR EVERYTHING and still look correct.
    A predicate that refuses the whole population is indistinguishable from one that works,
    unless something asserts a member it must NOT refuse.
    """
    if import_writes.why_not_import(_READER):
        out.append(f"selftest: the pure reader {_READER} was wrongly held back")
        return 1
    return 0


def the_two_specimens_disagree(out: list[str]) -> int:
    """Check the predicate DISCRIMINATES rather than answering uniformly.

    ⚑ THE ARMS ABOVE PIN TWO VALUES; this pins that they are DIFFERENT values produced by the
    same call. A constant predicate satisfies each arm read alone only if one of them is wrong,
    so this states the discrimination directly rather than leaving it as an inference.
    """
    if bool(import_writes.why_not_import(_WRITER)) == bool(import_writes.why_not_import(_READER)):
        out.append("selftest: the writer and the reader got the same verdict")
        return 1
    return 0


def a_missing_file_is_not_called_safe(out: list[str]) -> int:
    """Check a path that does not exist is not reported as safe to import.

    ⚑ THE CONSERVATIVE DIRECTION. A false "writes" costs one skipped census; a false "safe"
    costs an unintended write, so an unreadable specimen must never come back clean.
    """
    if not import_writes.why_not_import("scripts/no_such_tool_anywhere.py"):
        out.append("selftest: a nonexistent script was reported as safe to import")
        return 1
    return 0


_ARMS = (
    the_detector_is_reachable,
    a_tool_that_writes_at_import_is_named,
    a_pure_reader_is_not_excused,
    the_two_specimens_disagree,
    a_missing_file_is_not_called_safe,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"import-writes selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"import-writes selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
