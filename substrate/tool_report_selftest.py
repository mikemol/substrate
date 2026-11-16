#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_report` — the two silences must not render alike.

⚑⚑⚑ COLLAPSING THE TWO VERDICTS COST FIVE MODES FOR AS LONG AS THEY EXISTED. A tool publishing a
textbook roster under a header the parser did not know read as UNDOCUMENTED on every mode, and the
reader who noticed was a human comparing a new mode against its four siblings. `UNREADABLE BY THIS
CENSUS` is a fact about the PARSER; `NO SELF-DESCRIPTION` is a fact about the TOOL — and only the
second is about the tree.

⚑⚑ THE WARNING'S WORDING IS ASSERTED, NOT JUST ITS PRESENCE. A flag list under a tool's name reads
naturally as *"these are undocumented"*; here it means *"this reader could not tell"*. An arm
below pins that the text says so, because a header alone would not stop someone acting on the
list.

⚑ AND THE DENOMINATOR SURVIVES PAGING. A mode count over a slice is a number weighed against the
wrong total — the transport-truncation defect moved inside the tool.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import page, tool_census, tool_report

# A tool that declares a mode plainly.
_DESCRIBED = (
    '"""a.py --alpha <x>   the alpha mode\n"""\nimport sys\nif "--alpha" in sys.argv:\n    run()\n'
)

# A tool publishing a roster under a header the declaration reader does not know — the UNREADABLE
# shape.
#
# ⚑⚑ THE ADMISSION LINE IS IN CODE, NOT IN THE DOCSTRING, AND THAT IS THE WHOLE FIXTURE. A tool is
# CENSUSED when a usage line exists anywhere in its raw source, but DECLARES only what the
# declaration readers can see — so a roster under an unknown header leaves the tool admitted with
# no modes, which is exactly the state that must not render as "this tool documents nothing". A
# first cut put the usage line in the docstring, where the parser read it, and the tool came back
# described: the fixture tested the ordinary path while claiming to test this one.
_UNREADABLE = (
    '"""b.py\n\ncommands:\n'
    '  --beta   the beta mode\n  --gamma  the gamma mode\n"""\n'
    "import sys\n"
    "def usage():\n"
    '    return "b.py --beta <x>   the beta mode"\n'
    'if "--beta" in sys.argv:\n    run()\n'
)

# A tool admitted by a usage line in code, declaring nothing a reader can see — the SILENT shape.
_SILENT = (
    "import sys\n"
    "def usage():\n"
    '    return "c.py --delta <x>   the delta mode"\n'
    'if __name__ == "__main__":\n'
    '    if "--delta" in sys.argv:\n        run()\n'
    "    print(usage())\n"
)


def _census(files: dict[str, str]) -> tuple[tool_census.Tool, ...]:
    """Build a fixture tree and return its census."""
    with tempfile.TemporaryDirectory() as where:
        root = Path(where)
        for name, body in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        return tool_census.census(root)


def _one(source: str, name: str = "scripts/a.py") -> tool_census.Tool | None:
    """Return the single censused tool for a fixture, or None when it was not admitted."""
    rows = _census({name: source})
    return rows[0] if rows else None


def a_described_tool_renders_its_modes(out: list[str]) -> int:
    """Check the ordinary case shows the mode and its gloss."""
    tool = _one(_DESCRIBED)
    if tool is None:
        out.append("selftest: the described tool was not censused")
        return 1
    got = "\n".join(tool_report.tool_block(tool))
    if "--alpha" not in got or "alpha mode" not in got:
        out.append(f"selftest: the described tool rendered as {got!r}")
        return 1
    if tool_report.UNREADABLE in got or tool_report.SILENT in got:
        out.append("selftest: a described tool carries a silence verdict")
        return 1
    return 0


def an_unreadable_tool_is_marked_as_the_readers_failure(out: list[str]) -> int:
    """Check the parser's limit is not reported as the tool's gap — THE ITEM.

    ⚑⚑⚑ THIS IS THE COLLAPSE THAT COST FIVE MODES. Rendering an unreadable roster as
    NO SELF-DESCRIPTION sends a reader to write documentation the tool already carries.
    """
    tool = _one(_UNREADABLE, "scripts/b.py")
    if tool is None:
        out.append("selftest: the unreadable tool was not censused")
        return 1
    got = "\n".join(tool_report.tool_block(tool))
    if tool_report.SILENT in got:
        out.append("selftest: an unreadable tool was marked as having no self-description")
        return 1
    if tool_report.UNREADABLE not in got:
        out.append(f"selftest: the unreadable verdict is absent: {got!r}")
        return 1
    return 0


def the_unreadable_warning_says_whose_failure_it_is(out: list[str]) -> int:
    """Check the text stops a reader acting on the flag list.

    ⚑⚑ A HEADER ALONE WOULD NOT. The natural reading of a flag list under a tool's name is
    *"these are undocumented"*, so the warning has to say the opposite in words.
    """
    tool = _one(_UNREADABLE, "scripts/b.py")
    if tool is None:
        out.append("selftest: the unreadable tool was not censused")
        return 1
    got = "\n".join(tool_report.tool_block(tool))
    if "fact about THIS READER" not in got:
        out.append("selftest: the warning does not say whose failure it is")
        return 1
    if "UNKNOWN" not in got:
        out.append("selftest: the flags are not marked as status-unknown")
        return 1
    return 0


def a_silent_tool_is_reported_as_the_tools_own_gap(out: list[str]) -> int:
    """Check a tool that genuinely publishes nothing carries the other verdict."""
    tool = _one(_SILENT, "scripts/c.py")
    if tool is None:
        out.append("selftest: the silent tool was not censused")
        return 1
    got = "\n".join(tool_report.tool_block(tool))
    if tool_report.UNREADABLE in got:
        out.append("selftest: a silent tool was excused as a parser failure")
        return 1
    if tool_report.SILENT not in got:
        out.append(f"selftest: the silent verdict is absent: {got!r}")
        return 1
    return 0


def a_silent_tools_flags_are_still_listed(out: list[str]) -> int:
    """Check the only available signal is shown.

    ⚑ EVERY FLAG ITS AST CARRIES IS ONE NO READER CAN SEE, which is the sharpest form of the
    paydown census — and withholding them would leave nothing to act on.
    """
    tool = _one(_SILENT, "scripts/c.py")
    if tool is None:
        out.append("selftest: the silent tool was not censused")
        return 1
    got = "\n".join(tool_report.tool_block(tool))
    if "--delta" not in got:
        out.append(f"selftest: the dispatched flag was withheld: {got!r}")
        return 1
    return 0


def the_denominator_survives_paging(out: list[str]) -> int:
    """Check a page reports the whole population, not its slice — THE PAGING ARM.

    ⚑⚑ A MODE COUNT OVER A SLICE is a number a reader weighs against the wrong total. A bounded
    listing that reported its own page as the toolkit would be transport truncation moved inside
    the tool.
    """
    rows = _census(
        {"scripts/a.py": _DESCRIBED, "scripts/b.py": _UNREADABLE, "scripts/c.py": _SILENT}
    )
    if len(rows) < len(("a", "b", "c")):
        out.append(f"selftest: the fixture censused {len(rows)} tool(s)")
        return 1
    got = tool_report.render(rows, top=1)
    if f"{len(rows)} tool(s)" not in got:
        out.append(f"selftest: a paged render reported the wrong denominator: {got!r}")
        return 1
    return 0


def a_page_says_what_it_withheld(out: list[str]) -> int:
    """Check a bounded census names the rest."""
    rows = _census(
        {"scripts/a.py": _DESCRIBED, "scripts/b.py": _UNREADABLE, "scripts/c.py": _SILENT}
    )
    got = tool_report.render(rows, top=1)
    if page.SKIP not in got:
        out.append("selftest: a bounded census did not name the next page")
        return 1
    return 0


def an_unbounded_census_says_nothing_extra(out: list[str]) -> int:
    """Check a complete listing carries no truncation notice."""
    rows = _census({"scripts/a.py": _DESCRIBED})
    if "more —" in tool_report.render(rows):
        out.append("selftest: an unbounded census emitted a truncation notice")
        return 1
    return 0


def the_mode_source_is_shown(out: list[str]) -> int:
    """Check which reading layer found a mode travels into the report.

    ⚑ A USAGE LINE CARRIES A SIGNATURE AND AN OPTION ROW CARRIES ONLY A GLOSS, so a reader
    weighing a divergence needs to know which they are looking at.
    """
    tool = _one(_DESCRIBED)
    if tool is None:
        out.append("selftest: the described tool was not censused")
        return 1
    got = "\n".join(tool_report.tool_block(tool))
    if "[usage]" not in got:
        out.append(f"selftest: the mode's source is not shown: {got!r}")
        return 1
    return 0


_ARMS = (
    a_described_tool_renders_its_modes,
    an_unreadable_tool_is_marked_as_the_readers_failure,
    the_unreadable_warning_says_whose_failure_it_is,
    a_silent_tool_is_reported_as_the_tools_own_gap,
    a_silent_tools_flags_are_still_listed,
    the_denominator_survives_paging,
    a_page_says_what_it_withheld,
    an_unbounded_census_says_nothing_extra,
    the_mode_source_is_shown,
)

_CASE_COUNT = 2 + 2 + 2 + 2 + 1 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-report selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-report selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
