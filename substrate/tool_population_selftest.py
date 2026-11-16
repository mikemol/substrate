#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_population` — a directory absent from the roster is silent.

⚑⚑⚑ THE `substrate/` CASE IS THE ITEM, AND ITS ABSENCE COST A REAL SEARCH. `toolmodes` scanned
three directories and not this package, so `--find outline` reported **0 hits over 98 tools**
while `substrate/module_outline.py` did precisely that. An unsearched directory and an absent
capability produce byte-identical output — every hit the index returns is real, so it never looks
broken.

⚑⚑ SO THE ARMS BELOW PIN THE POPULATION, NOT THE PARSER. Whether a usage line is read correctly
is a different module's question; what is asserted here is which FILES are offered to it, because
that is the layer where a miss is invisible.

⚑ AND THE ADMISSION BAR STAYS LOW ON PURPOSE. The origin module measured a bar of two published
modes shrinking the population from 74 tools to 9 and called the excluded 40 *"noise"* — they
were the paydown census. Under-admitting is the dangerous direction, so an arm here asserts that
a library module is excluded while every real dispatch idiom is admitted.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tool_population

# The directory whose absence was the defect.
_ADDED = "substrate"

# A module that dispatches on the `__main__` guard.
_GUARD = "if __name__ == '__main__':\n    main()\n"

# A module that dispatches on a bare argv test — the second live spelling.
_BARE_ARGV = "if '--selftest' in sys.argv:\n    selftest()\n"

# A module that runs nothing: imported, never executed.
_LIBRARY = "def helper():\n    return 1\n"

# How many tools the two-file fixtures expect to admit.
_ONE = 1


def _tree(where: str, files: dict[str, str]) -> Path:
    """Build a fixture tool tree and return its root."""
    root = Path(where)
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


def the_package_directory_is_in_the_roster(out: list[str]) -> int:
    """Check `substrate/` is a tool directory — THE ITEM.

    ⚑⚑⚑ THIS IS THE ARM THAT WOULD HAVE PREVENTED THE WRONG-TOOL SEARCH. The roster is a list of
    PLACES, so a missing place silently removes every tool in it from every capability query.
    """
    if _ADDED not in tool_population.TOOL_DIRS:
        out.append(f"selftest: {_ADDED!r} is not in the tool roster: {tool_population.TOOL_DIRS!r}")
        return 1
    return 0


def the_historical_directories_are_kept(out: list[str]) -> int:
    """Check widening the roster did not narrow it.

    ⚑ A ROSTER EDIT CAN LOSE AN ENTRY AS EASILY AS GAIN ONE, and the loss is the invisible
    direction — the census would simply report fewer tools, which reads as a smaller toolkit.
    """
    for name in ("scratch", "scripts"):
        if name not in tool_population.TOOL_DIRS:
            out.append(f"selftest: {name!r} fell out of the roster")
            return 1
    return 0


def both_entry_spellings_are_seen(out: list[str]) -> int:
    """Check a CLI is recognised by either dispatch idiom.

    ⚑⚑ ANCHORING ON THE `__main__` GUARD ALONE DROPS REAL TOOLS. `suite_discovery` records the
    same union for the same reason: a module dispatching on a bare `if "--flag" in sys.argv` is a
    CLI, and testing only the common idiom loses it into a smaller count.
    """
    if not tool_population.has_entry_point(_GUARD):
        out.append("selftest: the __main__ guard was not read as an entry point")
        return 1
    if not tool_population.has_entry_point(_BARE_ARGV):
        out.append("selftest: a bare argv dispatch was not read as an entry point")
        return 1
    return 0


def a_library_is_not_a_tool(out: list[str]) -> int:
    """Check a module that never runs is excluded — the negative control.

    ⚑ WITHOUT THIS, `has_entry_point` RETURNING TRUE ALWAYS would pass every arm above while
    admitting the whole package.
    """
    if tool_population.has_entry_point(_LIBRARY):
        out.append("selftest: a library module was read as a CLI")
        return 1
    return 0


def private_modules_are_excluded(out: list[str]) -> int:
    """Check an underscore-prefixed helper is not offered as a tool."""
    with tempfile.TemporaryDirectory() as where:
        root = _tree(where, {"scripts/_helper.py": _GUARD, "scripts/real.py": _GUARD})
        names = [p.name for p in tool_population.candidates(root)]
    if "_helper.py" in names:
        out.append(f"selftest: a private module was admitted: {names!r}")
        return 1
    if "real.py" not in names:
        out.append(f"selftest: a real tool was dropped: {names!r}")
        return 1
    return 0


def an_absent_directory_is_skipped(out: list[str]) -> int:
    """Check a missing tool directory degrades rather than raising.

    ⚑ A BORROWING CHECKOUT may hold `scripts` and not `jea/`. A census that refused there would
    report a fact about the checkout as a fact about the toolkit.
    """
    with tempfile.TemporaryDirectory() as where:
        root = _tree(where, {"scripts/real.py": _GUARD})
        got = tool_population.directories(root)
    if len(got) != _ONE:
        out.append(f"selftest: absent directories were not skipped: {got!r}")
        return 1
    return 0


def executables_carry_their_source(out: list[str]) -> int:
    """Check the reader hands back text with each path.

    ⚑ EVERY CONSUMER NEEDS THE SOURCE NEXT — to parse usage lines, read literal flags, take the
    docstring. Returning paths alone makes each re-read the file, which is how two censuses came
    to disagree about what one tool contains.
    """
    with tempfile.TemporaryDirectory() as where:
        root = _tree(where, {"scripts/real.py": _GUARD, "scripts/lib.py": _LIBRARY})
        got = tool_population.executables(root)
    if len(got) != _ONE:
        out.append(f"selftest: {len(got)} executable(s) found, expected {_ONE}")
        return 1
    if "main()" not in got[0][1]:
        out.append("selftest: the source did not come back with the path")
        return 1
    return 0


def the_relative_spelling_is_posix(out: list[str]) -> int:
    """Check the join key is stable across platforms.

    ⚑ THE RELATIVE PATH IS THE JOIN KEY between this population and every table citing a tool.
    Two spellings of one path is how a roster starts disagreeing with a census about what exists.
    """
    with tempfile.TemporaryDirectory() as where:
        root = _tree(where, {"scripts/real.py": _GUARD})
        got = tool_population.relative(root / "scripts" / "real.py", root)
    if got != "scripts/real.py":
        out.append(f"selftest: the relative spelling read as {got!r}")
        return 1
    return 0


def the_order_is_stable(out: list[str]) -> int:
    """Check the population comes back sorted.

    ⚑ THIS CENSUS IS SPLICED INTO A GATED BLOCK, so a row order that follows `iterdir` renders
    differently per machine and reads as drift on someone else's checkout.
    """
    with tempfile.TemporaryDirectory() as where:
        root = _tree(
            where, {"scripts/b.py": _GUARD, "scripts/a.py": _GUARD, "scripts/c.py": _GUARD}
        )
        names = [p.name for p in tool_population.candidates(root)]
    if names != sorted(names):
        out.append(f"selftest: the population is unsorted: {names!r}")
        return 1
    return 0


def the_live_tree_admits_the_package(out: list[str]) -> int:
    """Check the real repo now offers `substrate/` tools — the end-to-end reading.

    ⚑⚑ THE FIXTURE ARMS PROVE THE MECHANISM; THIS PROVES IT REACHES THE TREE. A roster entry
    naming a directory the code never scanned would pass every arm above.
    """
    found = [tool_population.relative(path) for path, _source in tool_population.executables()]
    if not any(rel.startswith(f"{_ADDED}/") for rel in found):
        out.append(
            f"selftest: no {_ADDED}/ tool was admitted from the live tree "
            f"({len(found)} tool(s) found)"
        )
        return 1
    return 0


def the_needle_is_read_off_the_command_line(out: list[str]) -> int:
    """Check `--find <x>` yields its operand and an absent flag yields nothing.

    ⚑⚑⚑ THE ABSENT CASE IS THE LOAD-BEARING HALF. Before this mode existed, an unrecognised flag
    was silently dropped and the census printed ALL rows — byte-identical to a bare run — so the
    caller read a full listing as an answer to a narrow question (gate-G370).
    """
    if tool_population.needle(("tool_population.py", "--find", "run_selftests")) != "run_selftests":
        out.append("selftest: --find did not yield its operand")
        return 1
    if tool_population.needle(("tool_population.py",)) != "":
        out.append("selftest: an absent --find yielded a needle")
        return 1
    return 0


def a_bare_find_does_not_widen_to_everything(out: list[str]) -> int:
    """Check a trailing `--find` with no operand is not read as match-all.

    ⚑ THE FAILURE THIS MODE EXISTS TO REMOVE, ONE LEVEL DOWN. A flag that silently widens to the
    whole census is exactly the shape that made the original miss invisible, so a bare `--find`
    must come back empty rather than matching every row.
    """
    if tool_population.needle(("tool_population.py", "--find")) != "":
        out.append("selftest: a bare --find produced a needle")
        return 1
    return 0


def matching_narrows_and_an_empty_needle_keeps_all(out: list[str]) -> int:
    """Check the filter selects, and that no needle means no filtering — both directions.

    ⚑ A FILTER ONLY EVER CHECKED ON ITS HIT PATH has a false branch nothing has run. Asserting
    the empty-needle case is what stops `matching` quietly becoming a no-op.
    """
    rows = ("scripts/run_selftests.py", "substrate/module_trim.py", "scratch/mdstruct.py")
    got = tool_population.matching(rows, "run_selftests")
    if got != ("scripts/run_selftests.py",):
        out.append(f"selftest: the filter did not narrow: {got!r}")
        return 1
    if tool_population.matching(rows, "") != rows:
        out.append("selftest: an empty needle dropped rows")
        return 1
    return 0


def a_miss_names_the_denominator(out: list[str]) -> int:
    """Check the miss line carries the population it was taken over.

    ⚑⚑ A BARE `no tool matches 'x'` IS INDISTINGUISHABLE FROM A CENSUS THAT READ NOTHING, which
    this repo banks as a clean bill routinely. The denominator makes the claim falsifiable: it is
    a fact about THESE rows, never about the tree.
    """
    got = tool_population.render_miss("nope", 755)
    if "755" not in got:
        out.append(f"selftest: the miss line dropped its denominator: {got!r}")
        return 1
    if "nope" not in got:
        out.append(f"selftest: the miss line dropped the needle: {got!r}")
        return 1
    return 0


_ARMS = (
    the_package_directory_is_in_the_roster,
    the_historical_directories_are_kept,
    both_entry_spellings_are_seen,
    a_library_is_not_a_tool,
    private_modules_are_excluded,
    an_absent_directory_is_skipped,
    executables_carry_their_source,
    the_relative_spelling_is_posix,
    the_order_is_stable,
    the_live_tree_admits_the_package,
    the_needle_is_read_off_the_command_line,
    a_bare_find_does_not_widen_to_everything,
    matching_narrows_and_an_empty_needle_keeps_all,
    a_miss_names_the_denominator,
)

_CASE_COUNT = 1 + 2 + 2 + 1 + 2 + 1 + 2 + 1 + 1 + 1 + 2 + 1 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-population selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-population selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
