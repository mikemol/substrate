#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.pycodemod_retired` — a refusal, never a zero.

⚑⚑⚑ THE ARM THAT MATTERS IS THE NON-ZERO EXIT. Both retired modes RAN and returned a
confident `0`, and this repo DELETES on a zero (`--dead`). So the property under test is
not "does it print something" but "does it refuse in a way a caller cannot mistake for an
answer" — which is an EXIT STATUS, not a string.

⚑⚑ AND THE SECOND ARM IS THE ONE THAT COULD SILENTLY OVER-REFUSE. A guard that scanned the
whole argv would refuse `--literal -- --attr`, which asks about the STRING `--attr` and is
a correct invocation of a WORKING mode. The tool's own history has this exact defect
recorded twice (`--literal -- --selftest` ran the suite; a flag-shaped operand was rebound
and produced a confident zero), so the end-of-flags case is a case rather than a comment.

⚑ THE SUCCESSOR MUST EXIST ON DISK, not merely be named. A redirect to a path that is not
there converts one dead end into another, and the refusal would still read as helpful —
the failure mode a reader cannot detect from the message alone.
"""

from __future__ import annotations

import sys

from substrate import pycodemod_retired


def every_retired_mode_exits_non_zero(out: list[str]) -> int:
    """Check each retired mode refuses with a non-zero status.

    ⚑ THE POINT OF THE WHOLE MODULE. A zero exit from a mode that never worked is
    indistinguishable from a successful empty result.
    """
    failures = 0
    for flag, mode in pycodemod_retired.SUPERSEDED.items():
        if pycodemod_retired.refuse(mode) == 0:
            out.append(f"selftest: {flag} refused with a zero exit")
            failures += 1
    return failures


def every_refusal_names_its_successor(out: list[str]) -> int:
    """Check the refusal text names the reader that replaced the mode."""
    failures = 0
    for flag, mode in pycodemod_retired.SUPERSEDED.items():
        if mode.successor not in pycodemod_retired.refusal(mode):
            out.append(f"selftest: {flag}'s refusal does not name {mode.successor}")
            failures += 1
    return failures


def every_successor_exists(out: list[str]) -> int:
    """Check each named successor is a real file — a redirect to nothing is a dead end."""
    failures = 0
    for flag, mode in pycodemod_retired.SUPERSEDED.items():
        if not (pycodemod_retired.ROOT / mode.successor).exists():
            out.append(f"selftest: {flag} redirects to missing {mode.successor}")
            failures += 1
    return failures


def a_retired_mode_is_recognised(out: list[str]) -> int:
    """Check a retired mode in the argv is found — the POSITIVE CONTROL."""
    found = pycodemod_retired.superseded_in(["--attr", "corpus.ROOT"])
    if found is None or found.flag != "--attr":
        out.append("selftest: --attr was not recognised as retired")
        return 1
    return 0


def an_operand_after_end_of_flags_is_not_a_mode(out: list[str]) -> int:
    """Check a flag-shaped OPERAND after `--` is not read as an invocation.

    ⚑ `--literal -- --attr` asks about the STRING. Refusing it would break a WORKING
    mode in the name of retiring a broken one.
    """
    argv = ["--literal", pycodemod_retired.END_OF_FLAGS, "--attr"]
    if pycodemod_retired.superseded_in(argv) is not None:
        out.append("selftest: an operand after `--` was read as a retired mode")
        return 1
    return 0


def a_working_mode_is_not_refused(out: list[str]) -> int:
    """Check an invocation naming no retired mode passes through untouched."""
    failures = 0
    if pycodemod_retired.superseded_in(["--calls", "modes"]) is not None:
        out.append("selftest: a working mode was refused")
        failures += 1
    if pycodemod_retired.superseded_in([]) is not None:
        out.append("selftest: a bare invocation was refused")
        failures += 1
    return failures


def the_table_is_keyed_on_its_own_flag(out: list[str]) -> int:
    """Check no row is filed under a key its record does not name.

    ⚑ A ROW REACHED BY ONE SPELLING AND REPORTING ANOTHER would print a refusal for a
    mode the caller did not invoke — the two-spelling drift this repo keeps paying for.
    """
    failures = 0
    for flag, mode in pycodemod_retired.SUPERSEDED.items():
        if flag != mode.flag:
            out.append(f"selftest: {flag} is keyed against {mode.flag}")
            failures += 1
    return failures


def the_origin_is_recognised_by_stem(out: list[str]) -> int:
    """Check every spelling of the origin tool's path is recognised.

    ⚑ KEYING ON ONE SPELLING is how a census reports its METHOD as the SUBSTRATE. The
    origin is reached as a bare relative path, through `python3`, and by absolute path
    from a borrowing checkout; all three must read as the same tool.
    """
    failures = 0
    spellings = (
        ["python3", "scratch/pycodemod.py"],
        ["./scratch/pycodemod.py"],
        ["python3", "/home/x/github/substrate/scratch/pycodemod.py"],
    )
    for words in spellings:
        if not pycodemod_retired.names_origin(words):
            out.append(f"selftest: {words} was not read as the origin tool")
            failures += 1
    if pycodemod_retired.names_origin(["python3", "substrate/attr_reads.py"]):
        out.append("selftest: the SUCCESSOR was misread as the origin tool")
        failures += 1
    return failures


def a_retired_mode_on_the_origin_is_refused(out: list[str]) -> int:
    """Check the command-level verdict fires on each retired mode — the POSITIVE CONTROL."""
    failures = 0
    for flag in pycodemod_retired.SUPERSEDED:
        words = ["python3", "scratch/pycodemod.py", flag, "corpus.ROOT"]
        found = pycodemod_retired.retired_in_command(words)
        if found is None or found.flag != flag:
            out.append(f"selftest: {flag} on the origin was not refused")
            failures += 1
    return failures


def the_conjunction_holds_both_ways(out: list[str]) -> int:
    """Check neither half of the verdict fires alone.

    ⚑⚑ THE SHARPEST HAZARD IN THIS WHOLE WIRING. The gate that refuses textual queries
    RECOMMENDS this tool by name. A verdict keyed on the TOOL would refuse the tool it
    recommends, and every refusal it issues would become a dead end. A verdict keyed on
    the FLAG would refuse the SUCCESSOR, which takes the same flag and works.
    """
    failures = 0
    working = ["python3", "scratch/pycodemod.py", "--calls", "reach_ratchet"]
    if pycodemod_retired.retired_in_command(working) is not None:
        out.append("selftest: a WORKING mode of the origin was refused")
        failures += 1
    successor = ["python3", "substrate/attr_reads.py", "--attr", "corpus.ROOT"]
    if pycodemod_retired.retired_in_command(successor) is not None:
        out.append("selftest: the SUCCESSOR was refused for taking the retired flag")
        failures += 1
    unrelated = ["grep", "--attr", "notes.txt"]
    if pycodemod_retired.retired_in_command(unrelated) is not None:
        out.append("selftest: an unrelated command carrying the flag was refused")
        failures += 1
    return failures


def end_of_flags_is_honoured_at_command_level(out: list[str]) -> int:
    """Check `--literal -- --attr` on the origin is NOT refused.

    ⚑ THE OPERAND IS A STRING, NOT AN INVOCATION. `superseded_in` already stops at `--`;
    this arm pins that the command-level reader inherits that stop rather than
    re-scanning the argv with a private loop that forgets it.
    """
    words = [
        "python3",
        "scratch/pycodemod.py",
        "--literal",
        pycodemod_retired.END_OF_FLAGS,
        "--attr",
    ]
    if pycodemod_retired.retired_in_command(words) is not None:
        out.append("selftest: `--literal -- --attr` was refused as an invocation")
        return 1
    return 0


def every_refusal_names_the_directory_its_route_assumes(out: list[str]) -> int:
    """Check the redirect states the CWD it is relative to — the route's own precondition.

    ⚑⚑⚑ THE ARM THAT WOULD HAVE SAVED A PEER A WRONG REPORT (gate-G381). A reader took this
    redirect from `~/github`, where the first path component is itself the repo directory, and
    reported both successors as one component short. Measured from the repo root the spelling
    resolves and runs — NEITHER IS WRONG, they differ only in the reader's position.

    ⚑⚑ AND `every_successor_exists` CANNOT CATCH THIS, which is why a second arm is needed
    rather than a stronger one. That arm resolves each successor against `ROOT` and so tests the
    path from the ONE position it already assumes: it and the route vary together, so it is
    green for a reader standing anywhere. This arm asserts the refusal SAYS which position.
    """
    failures = 0
    for mode in pycodemod_retired.SUPERSEDED.values():
        text = pycodemod_retired.refusal(mode)
        if str(pycodemod_retired.ROOT) not in text:
            out.append(f"selftest: {mode.flag}'s refusal names a route with no directory")
            failures += 1
    return failures


_ARMS = (
    every_retired_mode_exits_non_zero,
    every_refusal_names_its_successor,
    every_successor_exists,
    a_retired_mode_is_recognised,
    an_operand_after_end_of_flags_is_not_a_mode,
    a_working_mode_is_not_refused,
    the_table_is_keyed_on_its_own_flag,
    the_origin_is_recognised_by_stem,
    a_retired_mode_on_the_origin_is_refused,
    the_conjunction_holds_both_ways,
    end_of_flags_is_honoured_at_command_level,
    every_refusal_names_the_directory_its_route_assumes,
)

_CASE_COUNT = 2 + 2 + 2 + 1 + 1 + 2 + 2 + 4 + 2 + 3 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"pycodemod-retired selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"pycodemod-retired selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
