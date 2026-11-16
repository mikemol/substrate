#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.mode_coverage` — a suite the reader cannot find is not an absent one.

⚑⚑⚑ THE SPLIT-SUITE CASE IS THE ONE THAT MOVED THE NUMBER. Reading a tool's own file alone called
80 of 92 modes uncovered; resolving sibling suite files brought it to 27. **The 53-row difference
was entirely the reader's blind spot** — a fact about the METHOD that, at that scale, reads as a
catastrophe in the tools rather than as a broken predicate.

⚑⚑ AND THE AST-EXTENT CASE IS WHY THE PREDICATE FIRES AT ALL. A regex slice from `def _selftest(`
to the next top-level `def` swallows whatever the function precedes — in the sharpest instance the
CLI dispatch itself, so every mode read as covered by its own declaration and the item reported
CLOSED on a tool whose newest modes had no case. A guard whose positive branch cannot fire is
decoration.

⚑ THE FIXTURES ARE SOURCE STRINGS AND TEMP FILES. A case reading the live tools measures today's
coverage — 27 gaps right now — and would go red the moment someone adds a case, reporting the
repair as a defect.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import mode_coverage

# A tool whose suite names the flag directly.
_NAMED = '''"""A tool with a covered mode."""


def _selftest() -> int:
    """Exercise the mode."""
    assert run(["--census"]) == 0
    return 0


def main() -> int:
    """Dispatch."""
    if "--census" in sys.argv:
        return census()
    return 0
'''

# A tool whose suite calls the function the flag dispatches to.
_CALLED = '''"""A tool covered through its function."""


def _selftest() -> int:
    """Exercise the mode by calling it."""
    assert check_indexes() == 0
    return 0


def main() -> int:
    """Dispatch."""
    if "--check-indexes" in sys.argv:
        return check_indexes()
    return 0
'''

# ⚑⚑⚑ THE SECOND DISPATCH IDIOM, AND IT READ AS ZERO MODES UNTIL THE READER LEARNED IT. A table
# routed by `MODES.get(flag)` carries its flags as dict KEYS, which the `in sys.argv` pattern
# cannot see — so every table-dispatched tool reported "no advertised mode read", an ABSENCE where
# the truth was a GAP. That direction hides work: a census says nothing to do exactly where the
# uncovered modes are. This fixture is the pin.
_TABLE = '''"""A tool dispatching through a table."""


def _selftest() -> int:
    """Exercise one of the two."""
    assert summary("") == ""
    return 0


MODES = {"--summary": summary, "--target": target}


def main() -> int:
    """Dispatch."""
    return MODES[sys.argv[1]]()
'''

# ⚑ THE DEFECT: advertised and unexercised.
_UNCOVERED = '''"""A tool with an uncovered mode."""


def _selftest() -> int:
    """Exercise something else."""
    assert run(["--census"]) == 0
    return 0


def main() -> int:
    """Dispatch."""
    if "--census" in sys.argv:
        return census()
    if "--spread" in sys.argv:
        return spread()
    return 0
'''

# ⚑ THE SLICE TRAP: the dispatch FOLLOWS the suite, so a regex slice swallows it.
_DISPATCH_AFTER = '''"""A tool whose dispatch follows its suite."""


def _selftest() -> int:
    """Exercise nothing relevant."""
    return 0


def main() -> int:
    """Dispatch."""
    if "--spread" in sys.argv:
        return spread()
    return 0
'''

# A tool with no suite at all.
_NO_SUITE = '''"""A tool with no cases."""


def main() -> int:
    """Dispatch."""
    if "--spread" in sys.argv:
        return spread()
    return 0
'''


def _modes(where: str, text: str, sibling: str | None = None) -> tuple[mode_coverage.Mode, ...]:
    """Write a fixture tool, optionally with a sibling suite, and read its modes."""
    path = Path(where) / "tool.py"
    path.write_text(text, encoding="utf-8")
    if sibling is not None:
        (Path(where) / "tool_selftest.py").write_text(sibling, encoding="utf-8")
    return mode_coverage.modes(path, "tool.py")


def a_named_flag_is_covered(out: list[str]) -> int:
    """Check a case naming the flag counts as coverage."""
    with tempfile.TemporaryDirectory() as where:
        got = _modes(where, _NAMED)
    if len(got) != 1 or not got[0].covered:
        out.append(f"selftest: a named flag read as {got!r}")
        return 1
    return 0


def a_called_function_is_covered(out: list[str]) -> int:
    """Check a case calling the dispatched function counts as coverage.

    ⚑ TWO SPELLINGS. A reader knowing only the flag reports a genuinely covered mode as a gap,
    which is a false finding that generates work.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _modes(where, _CALLED)
    if len(got) != 1 or not got[0].covered:
        out.append(f"selftest: a called function read as {got!r}")
        return 1
    return 0


def a_table_dispatch_advertises_its_modes(out: list[str]) -> int:
    """Check a `MODES = {...}` table is read as advertising, not as no modes at all.

    ⚑⚑⚑ THE FAILURE THIS PINS WAS AN ABSENCE, NOT A GAP, which is the dangerous direction. Before
    the table pattern was added, every table-dispatched tool reported "no advertised mode read —
    UNMEASURED, not clean", so the census said NOTHING TO DO exactly where the uncovered modes
    were. MEASURED on `make_rules.py`: 0 modes read, then 5 — of which all 5 were genuinely
    uncovered and had been invisible.

    ⚑⚑ AND THE REPO PREFERS THIS IDIOM, which is what makes the blind spot expensive rather than
    academic: `PLR0911` pushes a branch chain into a table, so the tree converges on exactly the
    shape the detector could not see.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _modes(where, _TABLE)
    names = sorted(m.mode for m in got)
    if names != ["--summary", "--target"]:
        out.append(f"selftest: a dispatch table advertised {names!r}")
        return 1
    # ⚑ AND THE COVERAGE SPLIT IS REAL: the suite calls `summary(...)` and never mentions
    # `--target`, so one is covered and one is a gap. Reporting both alike would make the
    # widening a count rather than a measurement.
    missing = [m.mode for m in mode_coverage.uncovered(got)]
    if missing != ["--target"]:
        out.append(f"selftest: the table's uncovered set read as {missing!r}")
        return 1
    return 0


def prose_describing_a_mode_is_not_a_mode(out: list[str]) -> int:
    """Check a flag mentioned only in a docstring or comment is not read as advertised.

    ⚑⚑⚑ THE READER MATCHED ITS OWN DOCUMENTATION, which is the instrument-is-not-its-subject
    defect. MEASURED across the package: 35 uncovered modes, of which SIX were flags occurring
    only in prose — including `--x` inside this reader's own comment explaining the table
    pattern. A census that invents a row SPENDS work arguing with a file that already documented
    why the row is wrong, which is worse than one that misses a row.

    ⚑⚑ AND A COMMENT COUNTS, WHICH I FIRST GOT WRONG. I reasoned a `#` comment is dropped by the
    tokenizer before dispatch, so it could not carry a live flag — true of the PROGRAM, irrelevant
    to a reader that scans TEXT.
    """
    source = (
        '"""A tool whose docstring mentions --ghost and dispatches --real."""\n'
        "\n"
        '# a comment mentioning --phantom in a table: {"--phantom": fn}\n'
        "\n"
        "\n"
        "def _selftest() -> int:\n"
        '    """Exercise it."""\n'
        "    assert real() == 0\n"
        "    return 0\n"
        "\n"
        "\n"
        "def main() -> int:\n"
        '    """Dispatch --ghost is only named here."""\n'
        '    if "--real" in sys.argv:\n'
        "        return real()\n"
        "    return 0\n"
    )
    got = sorted(mode_coverage.advertised(source))
    if got != ["--real"]:
        out.append(f"selftest: prose-only flags read as advertised: {got!r}")
        return 1
    return 0


def an_unexercised_mode_is_a_gap(out: list[str]) -> int:
    """Check an advertised mode with no case is reported — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER CALLING EVERYTHING COVERED passes both cases above and reports the
    corpus clean forever — which is exactly what the slice bug did.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _modes(where, _UNCOVERED)
    missing = mode_coverage.uncovered(got)
    if len(missing) != 1 or missing[0].mode != "--spread":
        out.append(f"selftest: the uncovered set read as {missing!r}")
        return 1
    return 0


def a_dispatch_after_the_suite_is_not_covered(out: list[str]) -> int:
    """Check a mode declared AFTER the suite is still a gap.

    ⚑⚑⚑ THE SLICE BUG, PINNED. A regex extent running to the next top-level `def` swallows the
    dispatch, so the mode's own `"--spread" in sys.argv` literal lands inside the "body" and the
    mode reads as covering itself. The AST extent stops at the function.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _modes(where, _DISPATCH_AFTER)
    if not mode_coverage.uncovered(got):
        out.append("selftest: a mode declared after the suite read as covered")
        return 1
    return 0


def a_sibling_suite_provides_coverage(out: list[str]) -> int:
    """Check cases in a sibling file count — THE ROW THAT MOVED THE NUMBER.

    ⚑⚑⚑ 80 OF 92 BECAME 27 OF 92 when this resolved. Reading one file reports a split suite as a
    total absence of cases, and at that scale the false finding reads as a catastrophe in the
    tools rather than as a defect in the reader.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _modes(
            where,
            _DISPATCH_AFTER,
            sibling='def _selftest() -> int:\n    run(["--spread"])\n    return 0\n',
        )
    if mode_coverage.uncovered(got):
        out.append(f"selftest: a sibling suite did not cover: {got!r}")
        return 1
    return 0


def a_tool_with_no_suite_covers_nothing(out: list[str]) -> int:
    """Check a tool with no selftest reports every mode as a gap."""
    with tempfile.TemporaryDirectory() as where:
        got = _modes(where, _NO_SUITE)
    if not got or got[0].covered:
        out.append(f"selftest: a tool with no suite read as {got!r}")
        return 1
    return 0


def the_selftest_flag_is_exempt(out: list[str]) -> int:
    """Check the runner is not asked to cover itself.

    ⚑ A TAUTOLOGY WOULD REPORT EVERY TOOL ONE SHORT — the runner IS the case, so requiring a case
    for it manufactures a gap nothing can close.
    """
    source = 'if "--selftest" in sys.argv:\n    pass\n'
    if mode_coverage.advertised(source):
        out.append("selftest: --selftest was read as an advertised mode")
        return 1
    return 0


def the_modes_come_from_the_dispatch(out: list[str]) -> int:
    """Check a flag mentioned in prose is not read as advertised.

    ⚑ THE DISPATCH IS THE AUTHORITY. A docstring naming `--census` is not a mode a caller can
    invoke, and counting it would demand a case for something that does not exist.
    """
    got = mode_coverage.advertised('"""See --census for the shape."""\n')
    if got:
        out.append(f"selftest: prose yielded advertised modes: {got!r}")
        return 1
    return 0


def an_unparseable_tool_has_no_suite_body(out: list[str]) -> int:
    """Check a syntax error yields an empty body rather than raising."""
    if mode_coverage.suite_body("def _selftest(:\n"):
        out.append("selftest: an unparseable tool yielded a suite body")
        return 1
    return 0


def an_absent_tool_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = mode_coverage.modes(Path(where) / "gone.py", "gone.py")
    if got != ():
        out.append(f"selftest: an absent tool yielded {got!r}")
        return 1
    return 0


def the_rows_are_one_per_mode(out: list[str]) -> int:
    """Check the population counts modes, not tools.

    ⚑⚑ TWO QUANTITIES IN ONE ITEM. A per-tool row made the size count modes while the rows
    counted tools — the grouping is a READING of the population, never the population.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _modes(where, _UNCOVERED)
    if len(got) != len(mode_coverage.advertised(_UNCOVERED)):
        out.append(
            f"selftest: {len(got)} row(s) for {len(mode_coverage.advertised(_UNCOVERED))} mode(s)"
        )
        return 1
    return 0


def the_grouping_loses_no_mode(out: list[str]) -> int:
    """Check every row lands in exactly one tool group."""
    rows = (
        mode_coverage.Mode(tool="a.py", mode="--x", covered=False),
        mode_coverage.Mode(tool="a.py", mode="--y", covered=False),
        mode_coverage.Mode(tool="b.py", mode="--z", covered=False),
    )
    grouped = mode_coverage.by_tool(rows)
    if sum(len(found) for found in grouped.values()) != len(rows):
        out.append(f"selftest: grouping lost a row: {grouped!r}")
        return 1
    return 0


def a_finding_carries_its_route(out: list[str]) -> int:
    """Check each gap says what would close it."""
    row = mode_coverage.Mode(tool="a.py", mode="--x", covered=False)
    if "--x" not in row.route:
        out.append(f"selftest: the route reads as {row.route!r}")
        return 1
    return 0


def an_empty_population_is_unmeasured(out: list[str]) -> int:
    """Check no modes read renders as unmeasured, not as clean."""
    text = mode_coverage.render(())
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty population renders as {text!r}")
        return 1
    return 0


def the_render_states_its_denominator(out: list[str]) -> int:
    """Check the finding says how many modes were examined."""
    rows = (
        mode_coverage.Mode(tool="a.py", mode="--x", covered=False),
        mode_coverage.Mode(tool="a.py", mode="--y", covered=True),
    )
    text = mode_coverage.render(rows)
    if " of " not in text:
        out.append(f"selftest: the render states no denominator: {text!r}")
        return 1
    return 0


_ARMS = (
    a_named_flag_is_covered,
    a_called_function_is_covered,
    a_table_dispatch_advertises_its_modes,
    prose_describing_a_mode_is_not_a_mode,
    an_unexercised_mode_is_a_gap,
    a_dispatch_after_the_suite_is_not_covered,
    a_sibling_suite_provides_coverage,
    a_tool_with_no_suite_covers_nothing,
    the_selftest_flag_is_exempt,
    the_modes_come_from_the_dispatch,
    an_unparseable_tool_has_no_suite_body,
    an_absent_tool_yields_nothing,
    the_rows_are_one_per_mode,
    the_grouping_loses_no_mode,
    a_finding_carries_its_route,
    an_empty_population_is_unmeasured,
    the_render_states_its_denominator,
)

# ⚑⚑⚑ DERIVED FROM THE ROSTER, NEVER TYPED. This was a hand-maintained `1 + 1 + …` sum, so adding
# an arm to `_ARMS` left the printed denominator behind and the suite reported the OLD total while
# running the NEW set. MEASURED: a case was added, the arm ran, and the line still read 15/15 —
# a green that was a fact about the literal rather than about the cases.
#
# ⚑⚑ AND THE DIRECTION IS THE BAD ONE: the count can only UNDER-report, so a suite that grew looks
# unchanged and nobody learns the new case is live. The roster is the population; the size of the
# population is not a second thing to maintain.
_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"mode-coverage selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"mode-coverage selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
