#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.quiet_read` — suppression must not become swallowing.

⚑⚑⚑ THE FAILURE THIS SUITE GUARDS IS THE FIX'S OWN SHADOW. A capture that hides an authority's
routine chatter is useful; the same capture hiding its ERROR message trades a noisy report for a
silent one, which is strictly worse. So the captured text is asserted PRESENT, not merely absent
from stdout — and the wrapped value is asserted to come back unchanged, because a helper that
quietly altered results would corrupt every verdict downstream of it.
"""

from __future__ import annotations

import contextlib
import sys

from substrate import quiet_read


def the_value_comes_back_unchanged(out: list[str]) -> int:
    """Check wrapping a call does not disturb what it returns."""
    got, _noise = quiet_read.quietly(lambda: 41 + 1)
    want = 42
    if got != want:
        out.append(f"selftest: the wrapped value came back as {got!r}, want {want}")
        return 1
    return 0


def what_was_printed_is_captured_not_discarded(out: list[str]) -> int:
    """Check the printed text is RETURNED, so an error message cannot vanish.

    ⚑ THIS IS THE ARM THAT KEEPS SUPPRESSION FROM BECOMING SWALLOWING. Discarding the capture
    would pass any test asserting only that stdout stayed clean.
    """

    def noisy() -> int:
        sys.stdout.write("authority: something you needed to know\n")
        return 7

    got, noise = quiet_read.quietly(noisy)
    bad = 0
    want = 7
    if got != want:
        out.append(f"selftest: the noisy call returned {got!r}, want {want}")
        bad += 1
    if "something you needed to know" not in noise:
        out.append(f"selftest: the printed text was not captured — got {noise!r}")
        bad += 1
    return bad


def a_silent_call_captures_nothing(out: list[str]) -> int:
    """Check the POSITIVE CONTROL: a quiet call yields an empty capture.

    ⚑ WITHOUT THIS, A HELPER THAT ALWAYS REPORTED NOISE would satisfy the arm above. The
    capture has to DISCRIMINATE, not merely be non-empty sometimes.
    """
    _got, noise = quiet_read.quietly(lambda: None)
    if noise:
        out.append(f"selftest: a silent call captured {noise!r}")
        return 1
    return 0


def stdout_is_restored_afterwards(out: list[str]) -> int:
    """Check the redirect does not leak past the call.

    ⚑ A CAPTURE THAT NEVER RELEASES would silence the report itself — the tool would run,
    conclude, and print nothing at all.
    """
    before = sys.stdout
    quiet_read.quietly(lambda: None)
    if sys.stdout is not before:
        out.append("selftest: stdout was not restored after the capture")
        return 1
    return 0


def an_exception_still_restores_stdout(out: list[str]) -> int:
    """Check a raising call does not leave stdout redirected.

    ⚑ THE CONTEXT MANAGER GUARANTEES THIS, and the arm exists so a future rewrite to a manual
    save/restore cannot silently lose it — that variant fails exactly here and nowhere else.
    """
    before = sys.stdout

    def boom() -> None:
        msg = "fixture"
        raise RuntimeError(msg)

    with contextlib.suppress(RuntimeError):
        quiet_read.quietly(boom)
    if sys.stdout is not before:
        out.append("selftest: stdout stayed redirected after an exception")
        return 1
    return 0


_ARMS = (
    the_value_comes_back_unchanged,
    what_was_printed_is_captured_not_discarded,
    a_silent_call_captures_nothing,
    stdout_is_restored_afterwards,
    an_exception_still_restores_stdout,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"quiet-read selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"quiet-read selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
