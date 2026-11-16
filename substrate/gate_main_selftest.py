#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `gate_main` — the authority that can say "I did not run".

⚑⚑⚑ THE `Unmeasurable` ARMS ARE THE ITEM, AND THE DEFECT THEY PIN WAS BANKED FOR REAL. A gate that
can only say 0 or 1 REPORTS ITS OWN BLIND SPOT AS A PASS: a `python3` without mypy produced no
error lines, the parse honestly found nothing, and **0 keys over 60 unannotated files was recorded
as a clean census**. Exit 2 is the branch that separates *"no type errors"* from *"the checker
never ran"*, and `--quiet` must never silence it — quiet suppresses a PASS, and this is not one.

⚑⚑ AND THE THREE EXIT CODES ARE THREE DIFFERENT NEXT ACTIONS. 0 passes; 1 is fixed AT THE
OFFENDING SITE; 2 is fixed IN THE ENVIRONMENT. Conflating 1 and 2 sends a reader hunting code that
is not wrong, which is why the constant is named rather than written as a literal.

⚑ THE CENSUS IS A CALLABLE AND IS NOT TAKEN WHEN ARGV IS REFUSED — pinned because a census that
walks a large tree costs seconds, and running it before discovering the operator typo'd a flag is
work nobody asked for. The arm counts invocations, since "it returned 2" cannot distinguish a
census that ran from one that did not.

⚑⚑ THIS SUITE EXISTS BECAUSE THE MODULE HAD NONE WHILE HOLDING THE LINE THAT CRASHED THE TYPE
GATE. `run_gate` called `report._replace(...)` — a `NamedTuple` method — after a 58-file
conversion turned `Report` into a frozen slotted dataclass. Nothing here ran until an unrelated
gate did, and the crash surfaced there. The `__replace__` arm below is that incident, pinned.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.ratchet import render

from substrate import gate_main

# What a fixture census reports, and the label a fixture gate carries.
_KEYS = ("one::a.py", "two::b.py")
_LABEL = "probe-gate"

# The exit codes the module distinguishes.
_PASS = 0
_DEBT_GREW = 1
_CANNOT_MEASURE = 2

# How many verdicts must be distinguishable, and how many flags the vocabulary declares.
_VERDICTS = 3

# What a blind census reports. ⚑ BOUND, NOT ASSEMBLED AT THE RAISE (EM101/TRY003) — the same
# discipline the module follows: a message built at the raise site is one nothing can reuse.
_BLIND_REASON = "synthetic: the checker did not run"

# How many times a census callable was invoked — the counter an arm reads.
_calls: list[int] = []


def _census() -> tuple[str, ...]:
    """Return a fixed census and record that it was taken."""
    _calls.append(1)
    return _KEYS


def _blind() -> tuple[str, ...]:
    """Refuse to take a census, the way a missing checker does."""
    raise gate_main.Unmeasurable(_BLIND_REASON)


def _gate(path: str, census: object = None) -> gate_main.Gate:
    """Build a gate over a baseline path, defaulting to the counting census."""
    taker = census if census is not None else _census
    return gate_main.Gate(
        label=_LABEL,
        census=taker,  # type: ignore[arg-type]
        baseline_path=path,
    )


def _baseline(directory: str, *keys: str) -> str:
    """Write a baseline holding `keys` and return its path."""
    path = Path(directory) / "baseline.txt"
    path.write_text("".join(f"{key}\n" for key in keys), encoding="utf-8")
    return str(path)


def a_census_at_baseline_passes(out: list[str]) -> int:
    """Check an unchanged census returns 0."""
    with tempfile.TemporaryDirectory() as raw:
        path = _baseline(raw, *_KEYS)
        rc = gate_main.run_gate(_gate(path), argv=["probe.py", "--quiet"])
        if rc != _PASS:
            out.append(f"selftest: a census at baseline returned {rc}, not {_PASS}")
            return 1
    return 0


def a_grown_census_refuses(out: list[str]) -> int:
    """Check a new key returns 1 — the ratchet's whole purpose."""
    with tempfile.TemporaryDirectory() as raw:
        path = _baseline(raw, _KEYS[0])
        rc = gate_main.run_gate(_gate(path), argv=["probe.py", "--quiet"])
        if rc != _DEBT_GREW:
            out.append(f"selftest: a grown census returned {rc}, not {_DEBT_GREW}")
            return 1
    return 0


def an_unmeasurable_census_refuses_rather_than_passing(out: list[str]) -> int:
    """Check a census that could not run returns 2 — THE BANKED-BLIND-SPOT ARM.

    ⚑⚑⚑ THE DEFECT THIS PREVENTS WAS RECORDED, NOT IMAGINED: a `python3` without mypy produced no
    error lines, the parse honestly found nothing, and 0 keys over 60 unannotated files was banked
    as a clean census. A gate that cannot say *"I did not run"* reports its blind spot as a pass.
    """
    with tempfile.TemporaryDirectory() as raw:
        path = _baseline(raw, *_KEYS)
        rc = gate_main.run_gate(_gate(path, _blind), argv=["probe.py"])
        if rc != _CANNOT_MEASURE:
            out.append(f"selftest: an unmeasurable census returned {rc}, not {_CANNOT_MEASURE}")
            return 1
    return 0


def quiet_does_not_silence_a_refusal_to_measure(out: list[str]) -> int:
    """Check `--quiet` suppresses a pass but never blindness.

    ⚑⚑ QUIET IS ABOUT SUCCESS. A gate that goes quiet about being blind is worse than a noisy one,
    because the silence is indistinguishable from success — the same defect the unmeasurable
    branch exists to prevent, one layer up.
    """
    with tempfile.TemporaryDirectory() as raw:
        path = _baseline(raw, *_KEYS)
        rc = gate_main.run_gate(_gate(path, _blind), argv=["probe.py", "--quiet"])
        if rc != _CANNOT_MEASURE:
            out.append("selftest: --quiet changed the unmeasurable verdict")
            return 1
    return 0


def the_three_verdicts_have_three_codes(out: list[str]) -> int:
    """Check no two outcomes share an exit code.

    ⚑ THREE CODES, THREE NEXT ACTIONS: 0 passes, 1 is fixed at the offending SITE, 2 is fixed in
    the ENVIRONMENT. Conflating 1 and 2 sends a reader hunting code that is not wrong.
    """
    if len({_PASS, _DEBT_GREW, _CANNOT_MEASURE}) != _VERDICTS:
        out.append("selftest: the three verdicts do not have three codes")
        return 1
    return 0


def an_unknown_flag_is_refused(out: list[str]) -> int:
    """Check argv validation happens before anything else."""
    with tempfile.TemporaryDirectory() as raw:
        path = _baseline(raw, *_KEYS)
        rc = gate_main.run_gate(_gate(path), argv=["probe.py", "--nonesuch"])
        if rc == _PASS:
            out.append("selftest: an unknown flag passed")
            return 1
    return 0


def a_refused_argv_does_not_take_the_census(out: list[str]) -> int:
    """Check the census is NOT run when argv is rejected — THE COST ARM.

    ⚑⚑ THE CENSUS IS A CALLABLE, NOT A SET, precisely so it is not taken on a refused invocation.
    A census that walks a large tree costs seconds, and running it before discovering the operator
    typo'd a flag is work nobody asked for. ⚑ The COUNT is what proves it: an exit code cannot
    distinguish a census that ran from one that did not.
    """
    with tempfile.TemporaryDirectory() as raw:
        path = _baseline(raw, *_KEYS)
        _calls.clear()
        gate_main.run_gate(_gate(path), argv=["probe.py", "--nonesuch"])
        if _calls:
            out.append(f"selftest: a refused argv still took the census {len(_calls)} time(s)")
            return 1
    return 0


def an_accepted_argv_does_take_the_census(out: list[str]) -> int:
    """Check the arm above is not vacuous — the census runs when argv is fine."""
    with tempfile.TemporaryDirectory() as raw:
        path = _baseline(raw, *_KEYS)
        _calls.clear()
        gate_main.run_gate(_gate(path), argv=["probe.py", "--quiet"])
        if not _calls:
            out.append("selftest: an accepted argv did not take the census")
            return 1
    return 0


def the_unmeasurable_reason_reaches_the_reader(out: list[str]) -> int:
    """Check the raise site's own message survives — THE GUESS-AS-FACT ARM.

    ⚑ *"NOT IMPORTABLE"* WAS ONCE A GUESS PRINTED AS A FACT. mypy exits non-census for a config
    error, a duplicate module name, or an unreadable path as readily as for an absent install,
    and each wants a different fix. Summarising the tool's own words into a plausible story is
    exactly what must not happen.
    """
    raised = gate_main.Unmeasurable(_BLIND_REASON)
    if raised.reason != _BLIND_REASON:
        out.append(f"selftest: the reason is {raised.reason!r}")
        return 1
    return 0


def a_remedy_is_the_classs_and_a_reason_is_the_sites(out: list[str]) -> int:
    """Check the two are separate fields.

    ⚑ A REMEDY IS CONSTANT FOR A WHOLE KIND OF FAILURE, so passing it at every raise is one string
    re-typed and free to drift; a reason is whatever the tool actually said.
    """

    class _WithRemedy(gate_main.Unmeasurable):
        """An unmeasurable state whose whole class shares one fix."""

        remedy = "install the checker"

    raised = _WithRemedy(_BLIND_REASON)
    if raised.remedy != "install the checker":
        out.append(f"selftest: the class remedy is {raised.remedy!r}")
        return 1
    if raised.reason != _BLIND_REASON:
        out.append(f"selftest: the raise reason is {raised.reason!r}")
        return 1
    return 0


def a_report_is_reshaped_by_the_dunder(out: list[str]) -> int:
    """Check the copy-with-changes spelling a dataclass provides — THE CRASH ARM.

    ⚑⚑⚑ THIS IS THE LINE THAT BROKE THE TYPE GATE. `run_gate` called `report._replace(...)` — a
    `NamedTuple` method — after a 58-file conversion turned `Report` into a frozen slotted
    dataclass. Nothing in this module ran until an unrelated gate did, and the crash surfaced
    there. The arm asserts the spelling directly so the next conversion cannot repeat it silently.
    """
    reshaped = render.DEFAULT.__replace__(quiet=True, list_keys=True)
    if not reshaped.quiet or not reshaped.list_keys:
        out.append(f"selftest: the reshaped report is {reshaped!r}")
        return 1
    if render.DEFAULT.quiet:
        out.append("selftest: the original report was mutated")
        return 1
    return 0


def the_flag_vocabulary_is_declared_once(out: list[str]) -> int:
    """Check the authority owns the flags rather than each gate re-listing them.

    ⚑ NINE GATES READ `--quiet` AND `--list` OUT OF `sys.argv` BY HAND and passed them down; a
    tenth would have had to remember. `--selftest` is in the set because it is the flag every gate
    accepts and six of eleven did not list, so the authority's own capability was unreachable
    through them.
    """
    for flag in ("--quiet", "--list", "--selftest"):
        if flag not in gate_main.GATE_FLAGS:
            out.append(f"selftest: {flag} is not in the declared vocabulary")
            return 1
    return 0


_ARMS = (
    a_census_at_baseline_passes,
    a_grown_census_refuses,
    an_unmeasurable_census_refuses_rather_than_passing,
    quiet_does_not_silence_a_refusal_to_measure,
    the_three_verdicts_have_three_codes,
    an_unknown_flag_is_refused,
    a_refused_argv_does_not_take_the_census,
    an_accepted_argv_does_take_the_census,
    the_unmeasurable_reason_reaches_the_reader,
    a_remedy_is_the_classs_and_a_reason_is_the_sites,
    a_report_is_reshaped_by_the_dunder,
    the_flag_vocabulary_is_declared_once,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 2 + 3


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"gate-main selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"gate-main selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
