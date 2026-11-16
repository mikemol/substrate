#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.argument_consumed` — an accepted argument is not a consumed one.

⚑⚑⚑ THE UNCONSUMED CASE IS THE ITEM. `--items T12` returned all nineteen rows: the key was
accepted and never read, and the output still looked like an answer. Nothing in a run says the
filter did not apply, so only driving a mode with a key and checking what came back separates a
wired filter from an ignored argument.

⚑⚑ AND THE TWO FAILURES ARE OPPOSITE. A mode returning EVERYTHING answers and narrows nothing; a
mode returning NOTHING narrows perfectly and answers nothing. Collapsing them would report a
broken mode as a working filter, so `consumed` is the conjunction and both halves are pinned.

⚑ THE ROW GRAMMAR IS THE SUBTLE PART. One item emits a declaration row AND a verdict row, so a
line count doubles — and the doubling is indistinguishable from an unconsumed filter. Keys are
parsed and deduplicated rather than lines counted.

⚑ THE FIXTURES ARE FAKE GATES. A case driving the live worklist gate measures today's wiring: it
consumes the key right now, so a case pinning that would go red the moment the mode regresses in
either direction rather than reporting WHICH direction.
"""

from __future__ import annotations

import sys

from substrate import argument_consumed

_PROBE = argument_consumed.PROBE

# What a correctly-filtered run prints: two rows, one key.
_NARROW = (
    f"item {_PROBE}: DECLARED\n"
    f"    claim      the flags are reachable\n"
    f"item {_PROBE}: closed -- every gate implements them\n"
)

# ⚑ THE DEFECT: the key was accepted and the mode reported everything.
_WIDE = (
    f"item {_PROBE}: DECLARED\n"
    f"item {_PROBE}: closed -- fine\n"
    "item T12: DECLARED\n"
    "item T12: OPEN -- still open\n"
    "item B3: OPEN -- blocked\n"
)

# The other failure: the asked-for key is absent.
_ABSENT = "item T12: DECLARED\nitem T12: OPEN -- still open\n"


class _Gate:
    """A gate printing the output the case chose."""

    def __init__(self, text: str, *, exits: bool = False) -> None:
        self._text = text
        self._exits = exits
        self.asked: list[list[str]] = []

    def items(self, keys: list[str]) -> object:
        """Print the fixture output, optionally exiting afterwards."""
        self.asked.append(list(keys))
        sys.stdout.write(self._text)
        if self._exits:
            raise SystemExit(1)
        return 0


def _narrowing_with(api: _Gate) -> argument_consumed.Narrowing:
    """Run the witness against a fixture gate."""

    def _load() -> tuple[argument_consumed.Gate | None, str]:
        return api, ""

    original = argument_consumed.gate
    argument_consumed.gate = _load
    try:
        return argument_consumed.narrowing()
    finally:
        argument_consumed.gate = original


def a_narrowed_run_is_consumed(out: list[str]) -> int:
    """Check a run reporting only the asked-for key is consumed."""
    got = _narrowing_with(_Gate(_NARROW))
    if not got.consumed:
        out.append(f"selftest: a narrowed run read as {got!r}")
        return 1
    return 0


def a_wide_run_is_not_consumed(out: list[str]) -> int:
    """Check a run reporting everything is the finding — THE WHOLE ITEM.

    ⚑⚑⚑ THE OUTPUT STILL LOOKS LIKE AN ANSWER. Every row is real and correct; the only thing
    wrong is that the reader asked about one key and received nineteen.
    """
    got = _narrowing_with(_Gate(_WIDE))
    if got.consumed:
        out.append("selftest: a wide run read as consumed")
        return 1
    if not got.unasked:
        out.append(f"selftest: a wide run reported no unasked keys: {got!r}")
        return 1
    return 0


def an_absent_key_is_its_own_failure(out: list[str]) -> int:
    """Check a run omitting the asked-for key is distinguished from a wide one.

    ⚑⚑ THE OPPOSITE FAILURE. Zero rows narrows perfectly and answers nothing; reading it as a
    working filter would report a broken mode as the healthy case.
    """
    got = _narrowing_with(_Gate(_ABSENT))
    if got.answered:
        out.append(f"selftest: an absent key read as answered: {got!r}")
        return 1
    if got.consumed:
        out.append("selftest: an absent key read as consumed")
        return 1
    return 0


def an_empty_run_is_not_consumed(out: list[str]) -> int:
    """Check a mode printing nothing does not satisfy the property.

    ⚑ NOTHING IS THE PERFECT NARROWING and the worst answer — the conjunction is what stops a
    silent mode reading as a precise one.
    """
    got = _narrowing_with(_Gate(""))
    if got.consumed:
        out.append("selftest: an empty run read as consumed")
        return 1
    return 0


def two_rows_for_one_key_are_one_key(out: list[str]) -> int:
    """Check the declaration and verdict rows do not read as two answers.

    ⚑⚑⚑ THE DOUBLING LOOKS EXACTLY LIKE AN UNCONSUMED FILTER. Counting lines reports two answers
    where one key was asked about, so a correctly-narrowed mode would be called unconsumed — a
    false finding produced by the reader's own grammar.
    """
    got = argument_consumed.keys_in(_NARROW)
    if got != (_PROBE,):
        out.append(f"selftest: two rows for one key read as {got!r}")
        return 1
    return 0


def the_keys_are_read_in_order(out: list[str]) -> int:
    """Check every distinct key is reported once, in the order seen."""
    got = argument_consumed.keys_in(_WIDE)
    if got != (_PROBE, "T12", "B3"):
        out.append(f"selftest: the keys read as {got!r}")
        return 1
    return 0


def a_non_row_line_is_not_a_key(out: list[str]) -> int:
    """Check indented detail lines are not parsed as rows.

    ⚑ A `startswith` TEST WOULD TAKE THE CLAIM LINE TOO. The row grammar is anchored on the item
    key, which answers *whose row is this* rather than *does this look like a row*.
    """
    got = argument_consumed.keys_in("    claim      some prose about item X: here\n")
    if got:
        out.append(f"selftest: a detail line yielded keys: {got!r}")
        return 1
    return 0


def engine_noise_is_not_a_key(out: list[str]) -> int:
    """Check unrelated tool output does not become a reported key.

    ⚑ THE LIVE RUN EMITS ENGINE WARNINGS alongside its rows, and a looser parse would count each
    one as an unasked key — reporting a consumed filter as unconsumed, loudly.
    """
    noise = (
        "paperkit-bib: warrants.bib @T17: field 'enables' is not a paperkit field\n"
        f"item {_PROBE}: closed -- fine\n"
    )
    got = argument_consumed.keys_in(noise)
    if got != (_PROBE,):
        out.append(f"selftest: engine noise read as {got!r}")
        return 1
    return 0


def the_asked_key_is_the_one_passed(out: list[str]) -> int:
    """Check the probe key reaches the mode."""
    api = _Gate(_NARROW)
    _narrowing_with(api)
    if api.asked != [[_PROBE]]:
        out.append(f"selftest: the mode was asked {api.asked!r}")
        return 1
    return 0


def an_exiting_mode_still_reports(out: list[str]) -> int:
    """Check output printed before an exit is still read.

    ⚑ A GATE REFUSING AFTER PRINTING has still answered the question this reader asks. Letting the
    exit propagate would report an exercised mode as unexercised.
    """
    got = _narrowing_with(_Gate(_NARROW, exits=True))
    if not got.consumed:
        out.append(f"selftest: an exiting mode read as {got!r}")
        return 1
    return 0


def an_unloadable_gate_is_unexercised(out: list[str]) -> int:
    """Check a gate that will not load reports its reason, not a verdict."""
    original = argument_consumed.GATE
    argument_consumed.GATE = "no-such-gate-9c14"
    try:
        got = argument_consumed.narrowing()
    finally:
        argument_consumed.GATE = original
    if got.known:
        out.append(f"selftest: an unloadable gate read as exercised: {got!r}")
        return 1
    if "will not load" not in got.why:
        out.append(f"selftest: the unloadable reason reads as {got.why!r}")
        return 1
    return 0


def the_verdicts_render_distinctly(out: list[str]) -> int:
    """Check unexercised, unanswered, unconsumed and clean do not render alike.

    ⚑ THE EXPECTED COUNT IS DERIVED FROM THE CASES BUILT, never typed — a literal would break
    when a fifth verdict is added, as an assertion about this list wearing the clothes of one
    about the render.
    """
    verdicts = (
        _narrowing_with(_Gate(_NARROW)),
        _narrowing_with(_Gate(_WIDE)),
        _narrowing_with(_Gate(_ABSENT)),
        argument_consumed.Narrowing(asked=_PROBE, reported=(), why="no tool"),
    )
    seen = {argument_consumed.render(got) for got in verdicts}
    if len(seen) != len(verdicts):
        out.append(f"selftest: {len(verdicts)} verdict(s) render to {len(seen)} line(s)")
        return 1
    return 0


def an_unconsumed_verdict_counts_the_unasked(out: list[str]) -> int:
    """Check the finding says how many keys came back unasked.

    ⚑ A BARE *"NOT CONSUMED"* leaves the reader to re-run the mode to see the scale — and the
    scale is what says whether the filter is ignored or merely leaky.
    """
    text = argument_consumed.render(_narrowing_with(_Gate(_WIDE)))
    if "unasked" not in text:
        out.append(f"selftest: the unconsumed verdict omits the count: {text!r}")
        return 1
    return 0


_ARMS = (
    a_narrowed_run_is_consumed,
    a_wide_run_is_not_consumed,
    an_absent_key_is_its_own_failure,
    an_empty_run_is_not_consumed,
    two_rows_for_one_key_are_one_key,
    the_keys_are_read_in_order,
    a_non_row_line_is_not_a_key,
    engine_noise_is_not_a_key,
    the_asked_key_is_the_one_passed,
    an_exiting_mode_still_reports,
    an_unloadable_gate_is_unexercised,
    the_verdicts_render_distinctly,
    an_unconsumed_verdict_counts_the_unasked,
)

_CASE_COUNT = 1 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"argument-consumed selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"argument-consumed selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
