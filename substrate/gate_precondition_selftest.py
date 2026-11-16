#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.gate_precondition` — the omission a frozen roster cannot report.

⚑⚑⚑ THE UNMONITORED DIRECTION IS THE ITEM. A hand-typed list is never wrong about the entries it
HOLDS; it goes wrong by OMITTING, which is why the origin's bar was wrong twice while every
entry in it stayed correct. Only `declared - tracked` can see that, so it is the arm that would
have caught both incidents — and a reader computing only the other difference would pass every
other case in this file.

⚑⚑ AND UNREAD MUST NOT READ AS AN EMPTY ROSTER. A census that will not run, exits non-zero, or
prints nothing parseable has not told us there are zero gates — it has told us nothing. Reporting
that as a clean precondition is the false green the whole family refuses.

⚑ THE FIXTURES ARE CENSUS OUTPUT STRINGS. A case reading the live roster measures today's hook:
it is 35 gates now, and a case pinning that would go red the moment a gate is added — reporting
correct work as a defect. What is asserted is that the roster is READ, not what it contains.
"""

from __future__ import annotations

import sys

from substrate import gate_precondition

# What the census prints: two phase headers and their gates.
_OUTPUT = """== Phase A — cheap gates (BEFORE the build)
   · tool unit tests
   · ban ratchet
   · claims
== Phase C — core-reading gates (AFTER the build)
   · Set₁ ratchet (elaborated)
   · cap ratchet (128MB)

5 declared gate(s) across 2 phase(s).
⚑ DECLARED, from the hook's own `run` call sites.
"""

# ⚑ DERIVED FROM THE FIXTURE, NEVER TYPED. A literal would make an assertion about the fixture
# wear the clothes of one about the reader, and would break when a row is added for another arm.
_GATES = sum(
    1 for line in _OUTPUT.splitlines() if line.strip().startswith(gate_precondition.GATE_PREFIX)
)
_PHASES = sum(
    1 for line in _OUTPUT.splitlines() if line.strip().startswith(gate_precondition.PHASE_PREFIX)
)

# A declared roster of two, used where the comparison needs both populations.
_DECLARED = ("claims", "ban ratchet")


def the_gate_names_are_read(out: list[str]) -> int:
    """Check every gate row becomes a name."""
    gates, _phases = gate_precondition._parse(_OUTPUT)  # noqa: SLF001
    if len(gates) != _GATES:
        out.append(f"selftest: parsed {len(gates)} gate(s), expected {_GATES}")
        return 1
    if "ban ratchet" not in gates:
        out.append(f"selftest: a known gate is missing from {gates!r}")
        return 1
    return 0


def the_phase_headers_are_read(out: list[str]) -> int:
    """Check both phases are counted."""
    _gates, phases = gate_precondition._parse(_OUTPUT)  # noqa: SLF001
    if len(phases) != _PHASES:
        out.append(f"selftest: parsed {len(phases)} phase(s), expected {_PHASES}")
        return 1
    return 0


def the_summary_line_is_not_a_gate(out: list[str]) -> int:
    """Check the trailing count line does not become an extra gate.

    ⚑ THE TOOL'S OWN SUMMARY SITS IN THE SAME STREAM as its rows, and a looser parse would count
    it — making the roster one larger than the tool declared, in the reader whose whole purpose
    is agreeing with that tool.
    """
    gates, _phases = gate_precondition._parse(_OUTPUT)  # noqa: SLF001
    stray = [name for name in gates if "declared gate(s)" in name or name.startswith("⚑")]
    if stray:
        out.append(f"selftest: non-gate line(s) parsed as gates: {stray!r}")
        return 1
    return 0


def an_unmonitored_gate_is_reported(out: list[str]) -> int:
    """Check a declared gate no item tracks is surfaced — THE WHOLE ITEM.

    ⚑⚑⚑ THE DIRECTION THAT CAUGHT NOTHING TWICE. *"All 21"* was true of the list and false of the
    hook; only declared-minus-tracked can express that, and without this arm a reader would
    report a frozen roster as complete forever.
    """
    seen = gate_precondition.coverage(tracked=("claims",), declared=_DECLARED)
    if seen.unmonitored != ("ban ratchet",):
        out.append(f"selftest: the unmonitored set read as {seen.unmonitored!r}")
        return 1
    return 0


def an_unenforced_item_is_reported(out: list[str]) -> int:
    """Check a tracked item naming no declared gate is surfaced.

    ⚑ THE OTHER DIRECTION CATCHES AN ITEM THAT OUTLIVED ITS GATE — measuring something the commit
    path will not enforce, which reads as coverage and is not.
    """
    seen = gate_precondition.coverage(tracked=("claims", "retired gate"), declared=("claims",))
    if seen.unenforced != ("retired gate",):
        out.append(f"selftest: the unenforced set read as {seen.unenforced!r}")
        return 1
    return 0


def full_coverage_reports_neither_difference(out: list[str]) -> int:
    """Check an exactly-matching pair yields no findings — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER REPORTING EVERYTHING AS A DIFFERENCE passes both cases above while
    being useless. The three arms together say the comparison is a real set difference.
    """
    seen = gate_precondition.coverage(
        tracked=("claims", "ban ratchet"), declared=("ban ratchet", "claims")
    )
    if seen.unmonitored or seen.unenforced:
        out.append(f"selftest: a matching pair reported {seen!r}")
        return 1
    return 0


def the_coverage_keeps_both_populations(out: list[str]) -> int:
    """Check the report carries what it compared, not only the differences.

    ⚑ A DIFFERENCE WITHOUT ITS DENOMINATORS cannot be checked by the next reader — *"2
    unmonitored"* means something different against 5 gates than against 35.
    """
    seen = gate_precondition.coverage(tracked=("claims",), declared=_DECLARED)
    if seen.tracked != ("claims",) or len(seen.declared) != len(_DECLARED):
        out.append(f"selftest: the coverage lost a population: {seen!r}")
        return 1
    return 0


def a_missing_census_is_unread(out: list[str]) -> int:
    """Check an absent tool reports UNREAD rather than an empty roster."""
    original = gate_precondition.CENSUS
    gate_precondition.CENSUS = ("scripts", "no_such_census_8f21.py")
    try:
        got = gate_precondition.roster()
    finally:
        gate_precondition.CENSUS = original
    if got.known:
        out.append(f"selftest: a missing census read as a roster: {got!r}")
        return 1
    if "UNREAD" not in got.why:
        out.append(f"selftest: the missing-census reason reads as {got.why!r}")
        return 1
    return 0


def an_empty_parse_is_unread_not_zero(out: list[str]) -> int:
    """Check output with no gate rows yields no names.

    ⚑⚑ ZERO DECLARED GATES WOULD BE AN EXTRAORDINARY CLAIM about a repo with a 35-gate hook, and
    a parse that stopped matching would make it silently. The reader turns that into UNREAD, so a
    reader-side failure cannot read as a substrate-side fact.
    """
    gates, _phases = gate_precondition._parse("nothing parseable here\n")  # noqa: SLF001
    if gates:
        out.append(f"selftest: unparseable output yielded gates: {gates!r}")
        return 1
    return 0


def an_unread_roster_renders_as_unread(out: list[str]) -> int:
    """Check the rendered failure cannot be mistaken for a clean precondition."""
    text = gate_precondition.render(
        gate_precondition.Roster(gates=(), phases=(), why="the census would not run")
    )
    if "UNREAD" not in text:
        out.append(f"selftest: an unread roster renders as {text!r}")
        return 1
    return 0


def the_render_names_its_authority(out: list[str]) -> int:
    """Check the report says where the roster came from.

    ⚑ A COUNT WITH NO SOURCE is the shape this item exists to replace. Naming the tool and mode
    is what lets the next reader re-derive it instead of trusting it.
    """
    text = gate_precondition.render(
        gate_precondition.Roster(gates=("claims",), phases=("A",), why="")
    )
    if gate_precondition.ROSTER_MODE not in text:
        out.append(f"selftest: the render omits its authority: {text!r}")
        return 1
    return 0


def a_long_difference_is_elided_once(out: list[str]) -> int:
    """Check the shown bound governs both the slice and the ellipsis.

    ⚑ TWO SPELLINGS OF ONE BOUND is how a report claims *"…"* over a list it showed in full, or
    truncates without saying so.
    """
    many = tuple(f"gate-{n}" for n in range(gate_precondition.SHOWN + 3))
    seen = gate_precondition.coverage(tracked=(), declared=many)
    text = gate_precondition.render(
        gate_precondition.Roster(gates=many, phases=("A",), why=""), seen
    )
    if "…" not in text:
        out.append(f"selftest: a long difference was not elided:\n{text}")
        return 1
    if f"gate-{gate_precondition.SHOWN}" in text:
        out.append(f"selftest: the elision showed past the bound:\n{text}")
        return 1
    return 0


def a_short_difference_is_not_elided(out: list[str]) -> int:
    """Check a list within the bound is shown whole."""
    seen = gate_precondition.coverage(tracked=(), declared=_DECLARED)
    text = gate_precondition.render(
        gate_precondition.Roster(gates=_DECLARED, phases=("A",), why=""), seen
    )
    if "…" in text:
        out.append(f"selftest: a short difference was elided:\n{text}")
        return 1
    return 0


_ARMS = (
    the_gate_names_are_read,
    the_phase_headers_are_read,
    the_summary_line_is_not_a_gate,
    an_unmonitored_gate_is_reported,
    an_unenforced_item_is_reported,
    full_coverage_reports_neither_difference,
    the_coverage_keeps_both_populations,
    a_missing_census_is_unread,
    an_empty_parse_is_unread_not_zero,
    an_unread_roster_renders_as_unread,
    the_render_names_its_authority,
    a_long_difference_is_elided_once,
    a_short_difference_is_not_elided,
)

_CASE_COUNT = 2 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"gate-precondition selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"gate-precondition selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
