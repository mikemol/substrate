#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_outcome` — every kind, and the order they are tested in.

⚑⚑ THE ORDERING ARMS ARE THE ONES THAT MATTER. Each kind is easy to produce in isolation;
what the classifier actually guarantees is that a cause which already explains the silence
OUTRANKS one that does not. A suite killed by its lease is `unfit` even if it also printed
something unparseable — because the kill explains the missing record and the spelling does
not.

⚑ AND `vacuous` VERSUS `silent` IS THE PAIR THAT LOOKS IDENTICAL IN THE NUMBERS. Both present
as zeros; only the `matched` flag separates "reported 0/0" from "reported nothing". A
classifier that derived `matched` from the counts would collapse them, and the collapse is
invisible — `vacuous` means 8 assertions never ran while the gate said green.
"""

from __future__ import annotations

import re
import sys

from substrate.suite_outcome import Reported, unreadable_output, verdict_kind

# The reader a live run uses: `N/M` somewhere in a line.
_RESULT = re.compile(r"\b(\d+)\s*/\s*(\d+)\b")

# (label, reported, returncode, out, expected kind)
_CASES: tuple[tuple[str, Reported, int, str, str], ...] = (
    ("a full pass is ok", Reported(matched=True, ok=9, all_=9), 0, "", "ok"),
    ("a partial pass names its cases", Reported(matched=True, ok=7, all_=9), 1, "", "cases"),
    # ⚑ ASSERTED NOTHING WHILE THE GATE SAID GREEN — the defect `vacuous` exists to name.
    ("0/0 is vacuous, not ok", Reported(matched=True, ok=0, all_=0), 0, "", "vacuous"),
    # ⚑ A LEASE FINDING, NOT A DEFECT. A session was spent treating one as the other.
    ("a SIGKILL is unfit", Reported.none(), -9, "", "unfit"),
    ("a shell-reported SIGKILL is unfit too", Reported.none(), 137, "", "unfit"),
    ("a timeout is unfit", Reported.none(), -15, "", "unfit"),
    # ⚑ THE SUITE DIED ON ITS OWN HARNESS; it did not assess anything.
    ("exit 2 with no record is refused", Reported.none(), 2, "", "refused"),
    ("printing nothing is silent", Reported.none(), 0, "", "silent"),
    ("a banner alone is silent", Reported.none(), 0, "starting up\n", "silent"),
    # ⚑ THE EMITTER EXISTS AND ITS SPELLING IS UNREADABLE — a different next action.
    ("an unparseable count is unread", Reported.none(), 0, "selftest: 15 of 15\n", "unread"),
    ("the count may lead the word", Reported.none(), 0, "18 cases ok of 20 run\n", "unread"),
)


def kinds(out: list[str]) -> int:
    """Check every kind the classifier can return."""
    bad = 0
    for label, reported, rc, text, want in _CASES:
        got = verdict_kind(reported, rc, out=text, result=_RESULT)
        if got != want:
            out.append(f"selftest: {label}: expected {want!r}, got {got!r}")
            bad += 1
    return bad


def cause_outranks_spelling(out: list[str]) -> int:
    """Check a kill or a refusal outranks an unparseable line.

    ⚑ AN ABORT EXPLAINS THE MISSING RECORD ON ITS OWN. Reporting `unread` there would send a
    reader to fix an emitter when the process never got to use it.
    """
    bad = 0
    noise = "selftest: 15 of 15\n"
    if verdict_kind(Reported.none(), -9, out=noise, result=_RESULT) != "unfit":
        out.append("selftest: an unparseable line outranked a lease kill")
        bad += 1
    if verdict_kind(Reported.none(), 2, out=noise, result=_RESULT) != "refused":
        out.append("selftest: an unparseable line outranked a refusal")
        bad += 1
    return bad


def record_outranks_exit(out: list[str]) -> int:
    """Check a suite that REPORTED is judged on its numbers, whatever it exited with.

    ⚑ A REFUSAL AFTER A COMPLETE REPORT IS NOT `refused`. The suite reported its cases, so the
    numbers are the verdict — exit 2 arriving afterwards does not retract them.
    """
    got = verdict_kind(Reported(matched=True, ok=9, all_=9), 2, result=_RESULT)
    if got != "ok":
        out.append(f"selftest: a complete report was overridden by an exit code: {got!r}")
        return 1
    return 0


def uncountable_is_not_unread(out: list[str]) -> int:
    """Check output with no two-integer count is silent, not unread.

    ⚑ LEGITIMATELY-UNCOUNTABLE IS NOT A DEFECT, and conflating them fires on correct tools. A
    declared SKIP carries no count, so it cannot satisfy the evidence half — the separation
    falls out of the predicate rather than from an exemption list.
    """
    bad = 0
    if verdict_kind(Reported.none(), 0, out="SKIP: numpy absent\n", result=_RESULT) != "silent":
        out.append("selftest: a declared SKIP was classified unread")
        bad += 1
    if unreadable_output("all done, 7 items\n", _RESULT) is not None:
        out.append("selftest: a line with one integer satisfied the arity half")
        bad += 1
    return bad


def evidence_is_the_line(out: list[str]) -> int:
    """Check the detector returns the offending LINE, never a bare boolean.

    ⚑ A BARE True CANNOT BE ACTED ON, and the next question is always *what did it print*.
    """
    got = unreadable_output("noise\nselftest: 15 of 15\nmore\n", _RESULT)
    if got != "selftest: 15 of 15":
        out.append(f"selftest: the detector did not return the line: {got!r}")
        return 1
    return 0


def parsed_line_is_not_evidence(out: list[str]) -> int:
    """Check a line the reader CAN parse is never reported as unreadable."""
    if unreadable_output("selftest: 15/15\n", _RESULT) is not None:
        out.append("selftest: a parseable count was reported as unreadable")
        return 1
    return 0


_ARMS = (
    kinds,
    cause_outranks_spelling,
    record_outranks_exit,
    uncountable_is_not_unread,
    evidence_is_the_line,
    parsed_line_is_not_evidence,
)

_CASE_COUNT = len(_CASES) + 2 + 1 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-outcome selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-outcome selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
