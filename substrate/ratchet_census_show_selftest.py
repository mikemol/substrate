#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ratchet_census_show` — a small renderer holding one large distinction.

⚑⚑⚑ UNMEASURABLE IS NOT CLEAN, AND THAT IS THE WHOLE REASON THIS RENDERER EARNS CASES. A gate
nobody could read and a gate with nothing to report are opposite facts, and collapsing them banks
a false green over a population that was never measured — the exact defect this arc exists to
close. Three arms hold it: each state renders distinctly, an unmeasurable row carries its REASON,
and an unmeasurable gate is not silently absorbed into the clean one.

⚑⚑ AND THE EXIT CODE IS PART OF THE DISTINCTION, NOT A DETAIL. `main` returns 1 for `over` OR
`unmeasurable` and 2 for a usage refusal, so a renderer that dropped unmeasurable rows would exit
0 over a report nobody could act on, and a collapsed usage code would make a typo read as a
failing census.

⚑⚑ THE `render` ARMS TAKE HAND-BUILT `Census` VALUES rather than reading a live gate. Which gates
are over baseline changes with every commit; a case naming one would expire on the next paydown —
and a paydown is the work SUCCEEDING, which is the worst time for a case to go red. What does not
move is that the three states must stay distinguishable.

⚑ `main` IS EXERCISED ONLY ON ITS ARGUMENT CONTRACT, because every other path shells into
whichever gates the tree holds this hour. A case pinning a real gate's verdict would be measuring
the tree, not this module.
"""

from __future__ import annotations

import sys

from substrate import ratchet_census, ratchet_census_show

# A gate's census size, and the keys an over-baseline fixture adds.
_HELD = 12
_ADDED = ("scripts/one.py::E501", "scripts/two.py::E501")

# The usage refusal. ⚑ DISTINCT FROM 1, which means a gate is over baseline or unreadable —
# collapsing them makes a mistyped invocation read as a failing census.
_USAGE = 2


def _at_baseline() -> ratchet_census.Census:
    """Return a census holding keys with nothing added."""
    return ratchet_census.Census(held=_HELD, added=())


def _over_baseline() -> ratchet_census.Census:
    """Return a census with keys over baseline."""
    return ratchet_census.Census(held=_HELD, added=_ADDED)


def an_unmeasurable_gate_is_marked_and_carries_its_reason(out: list[str]) -> int:
    """Check a gate nobody could read renders UNMEASURABLE with the reason — THE ARM.

    ⚑⚑⚑ A REFUSAL THAT CANNOT SAY WHAT IT HIT is a guard degraded to measuring nothing. The
    reason is the whole actionable content of the row: `would not import` and `exposes no
    census` need different repairs, and a bare UNMEASURABLE sends a reader to neither.
    """
    why = "the gate would not import"
    row = ratchet_census_show.render("some_gate", None, why)
    if "UNMEASURABLE" not in row:
        out.append(f"selftest: an unreadable gate rendered {row!r}")
        return 1
    if why not in row:
        out.append(f"selftest: the unmeasurable row omits its reason: {row!r}")
        return 1
    if "at baseline" in row:
        out.append(f"selftest: an unmeasurable gate read as clean: {row!r}")
        return 1
    return 0


def a_gate_at_baseline_reports_what_it_holds(out: list[str]) -> int:
    """Check a clean gate names its census SIZE — a verdict with no population cannot be weighed.

    ⚑ `held` ALONE CANNOT SAY WHETHER ANYTHING IS NEW, and `added` alone hides whether the
    population is 3 keys or 3,000. The clean row is where the size has to appear, since there
    is no delta to carry it.
    """
    row = ratchet_census_show.render("some_gate", _at_baseline(), None)
    if "at baseline" not in row:
        out.append(f"selftest: a clean gate rendered {row!r}")
        return 1
    if f"{_HELD} held" not in row:
        out.append(f"selftest: the clean row omits its census size: {row!r}")
        return 1
    return 0


def a_gate_over_baseline_reports_both_numbers_and_an_example(out: list[str]) -> int:
    """Check an OVER row carries the delta, the population, and one offending key.

    ⚑⚑ THE EXAMPLE IS WHAT MAKES THE ROW ACTIONABLE. A count of added keys tells a reader that
    something is new; naming one tells them where to start, without printing a whole census.
    """
    row = ratchet_census_show.render("some_gate", _over_baseline(), None)
    if "OVER" not in row:
        out.append(f"selftest: a gate over baseline rendered {row!r}")
        return 1
    if f"{len(_ADDED)} added" not in row:
        out.append(f"selftest: the OVER row omits the delta: {row!r}")
        return 1
    if f"{_HELD} held" not in row:
        out.append(f"selftest: the OVER row omits the population: {row!r}")
        return 1
    if _ADDED[0] not in row:
        out.append(f"selftest: the OVER row names no offending key: {row!r}")
        return 1
    return 0


def the_three_states_render_distinctly(out: list[str]) -> int:
    """Check no two verdicts collapse — the guard against a constant renderer.

    ⚑⚑ EACH ARM ABOVE PASSES INDIVIDUALLY against a renderer that emitted one string containing
    every marker. What must hold is that the three states are mutually distinguishable, since
    the exit code cannot tell them apart and the rows are all a reader gets.
    """
    rows = (
        ratchet_census_show.render("g", None, "a reason"),
        ratchet_census_show.render("g", _at_baseline(), None),
        ratchet_census_show.render("g", _over_baseline(), None),
    )
    if len(set(rows)) != len(rows):
        out.append(f"selftest: the three verdicts do not render distinctly: {rows!r}")
        return 1
    return 0


def every_row_names_its_gate(out: list[str]) -> int:
    """Check the gate name survives all three branches — a row is unattributable without it."""
    name = "the_gate_under_test"
    for census, why in ((None, "a reason"), (_at_baseline(), None), (_over_baseline(), None)):
        row = ratchet_census_show.render(name, census, why)
        if name not in row:
            out.append(f"selftest: a row omits its gate name: {row!r}")
            return 1
    return 0


def a_census_holding_nothing_is_still_at_baseline(out: list[str]) -> int:
    """Check an EMPTY census renders as clean, never as unmeasurable.

    ⚑⚑ EMPTY AND ABSENT ARE OPPOSITE FACTS, one layer up from where this module draws them. A
    gate that ran and holds no keys is at baseline; a gate that could not run is not. Keying on
    falsiness rather than on `None` would merge them, and this is the input where they diverge.
    """
    row = ratchet_census_show.render("g", ratchet_census.Census(held=0, added=()), None)
    if "UNMEASURABLE" in row:
        out.append(f"selftest: an empty census read as unmeasurable: {row!r}")
        return 1
    if "at baseline" not in row:
        out.append(f"selftest: an empty census rendered {row!r}")
        return 1
    return 0


def main_refuses_with_no_gate_named(out: list[str]) -> int:
    """Check the usage refusal is its own exit code, distinct from a report that found problems."""
    code = ratchet_census_show.main(["ratchet_census_show.py"])
    if code != _USAGE:
        out.append(f"selftest: an argument-free invocation exited {code}, not {_USAGE}")
        return 1
    return 0


def flags_are_not_read_as_gate_names(out: list[str]) -> int:
    """Check a lone flag leaves no gate named, so it refuses rather than censusing `--verbose`."""
    code = ratchet_census_show.main(["ratchet_census_show.py", "--verbose"])
    if code != _USAGE:
        out.append(f"selftest: a lone flag was taken as a gate name (exit {code})")
        return 1
    return 0


_ARMS = (
    an_unmeasurable_gate_is_marked_and_carries_its_reason,
    a_gate_at_baseline_reports_what_it_holds,
    a_gate_over_baseline_reports_both_numbers_and_an_example,
    the_three_states_render_distinctly,
    every_row_names_its_gate,
    a_census_holding_nothing_is_still_at_baseline,
    main_refuses_with_no_gate_named,
    flags_are_not_read_as_gate_names,
)

_CASE_COUNT = 3 + 2 + 4 + 1 + 3 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"ratchet-census-show selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"ratchet-census-show selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
