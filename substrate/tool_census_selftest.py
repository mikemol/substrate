#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_census` — the population predicate, and the two silences.

⚑⚑⚑ THE ADMISSION TEST TOOK THREE WRONG ANSWERS TO PIN, AND EACH LOOKED RIGHT. First the census
filtered on "which files RUN" and admitted 436 rows against the origin's 98. Then it filtered on
what a tool DECLARES and lost four tools that are censused with zero modes — the sharpest paydown
rows there are, dropped for being exactly what the census exists to surface. Only then did the
predicate resolve: a tool is admitted when a usage line exists in its RAW SOURCE, or when the
routing table names it.

⚑⚑ THE ASYMMETRY BETWEEN ADMISSION AND DECLARATION IS DELIBERATE, and an arm below pins it.
`publishes` reads the whole source; the declaration readers read the docstring, constants, prints
and argparse. A tool whose usage line sits somewhere only the first can see is IN the census with
no modes — which is a finding, not an omission. MEASURED on four: `store.py`,
`check_indented_imports.py`, `sppf_node_index.py`, `sppf_query.py`.

⚑ AND `described == False` IS TWO OPPOSITE FACTS UNDER ONE NAME. A tool that publishes nothing
and a tool whose publication this parser could not read render identically, and only the first is
a fact about the substrate. The `unparsed` witness is what separates them, and it must stay
EVIDENCE — returned only when a header-shaped line has flag rows under it — because inventing an
excuse for a genuinely silent tool is the mirror defect.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — **110 tools, 0 disagreements** on modes,
accepted, literals, options, mentioned, described and unparsed across every shared row. These
arms guard the PROPERTIES; that run guarded the ASSEMBLY.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tool_census, tool_population

# A tool that publishes a mode in its docstring — admitted, and declares it.
#
# ⚑ THE `__main__` GUARD IS LOAD-BEARING IN THE FIXTURE, and leaving it out cost two arms. The
# census filters `executables` first, so a file with a usage line and no dispatch is not a tool at
# all — correctly. A fixture that skips the guard tests nothing about declarations.
_PUBLISHES = (
    '"""probe.py --alpha <x>   the alpha mode\n"""\n'
    'import sys\nif __name__ == "__main__":\n    main()\n'
)

# A tool whose only usage line sits in CODE — admitted by the raw-source test, declares nothing.
_BURIED = (
    "import sys\n"
    "def usage():\n"
    '    return "probe.py --beta <x>   the beta mode"\n'
    'if __name__ == "__main__":\n    print(usage())\n'
)

# A script that runs and publishes nothing at all.
_SILENT = 'import sys\nif __name__ == "__main__":\n    do_work()\n'

# A roster under a header the declaration reader does not know — the `unparsed` witness case.
_UNKNOWN_HEADER = (
    '"""probe.py\n\ncommands:\n  --gamma  the gamma mode\n  --delta  the delta mode\n"""\n'
)

# A tool whose silence is genuine: no header, no rows.
_NO_ROSTER = '"""probe.py does one thing and takes no flags.\n"""\nimport sys\nmain()\n'

# A tool the routing table is known to name.
_ROUTED = "pycodemod.py"


def _tree(where: str, files: dict[str, str]) -> Path:
    """Build a fixture tool tree and return its root."""
    root = Path(where)
    for name, body in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return root


def a_publishing_tool_is_censused(out: list[str]) -> int:
    """Check a tool with a usage line is admitted and declares its mode."""
    with tempfile.TemporaryDirectory() as where:
        rows = tool_census.census(_tree(where, {"scripts/probe.py": _PUBLISHES}))
    if len(rows) != 1 or "--alpha" not in rows[0].modes:
        out.append(f"selftest: a publishing tool censused as {rows!r}")
        return 1
    return 0


def a_buried_usage_line_is_still_admitted(out: list[str]) -> int:
    """Check the admission test reads the RAW SOURCE — THE ITEM.

    ⚑⚑⚑ THIS IS THE ARM THAT COST FOUR TOOLS. Filtering admission on what a tool DECLARES drops
    every tool whose usage line sits where the declaration readers do not look — and those rows
    are the sharpest form of the paydown census, not noise. Admitted with zero modes IS the
    finding.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = tool_census.census(_tree(where, {"scripts/probe.py": _BURIED}))
    if len(rows) != 1:
        out.append(f"selftest: a buried usage line was not admitted: {len(rows)} row(s)")
        return 1
    if rows[0].described:
        out.append("selftest: a buried usage line was read as a declaration")
        return 1
    return 0


def a_silent_script_is_not_a_tool(out: list[str]) -> int:
    """Check a script that publishes nothing is excluded — the negative control.

    ⚑ WITHOUT THIS, "admit everything that runs" passes every other arm here while inflating the
    population four-fold. A gate that runs and exits is not a tool.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = tool_census.census(_tree(where, {"scripts/probe.py": _SILENT}))
    if rows:
        out.append(f"selftest: a silent script was censused: {[r.relpath for r in rows]!r}")
        return 1
    return 0


def the_wider_reading_stays_available(out: list[str]) -> int:
    """Check `publishing_only=False` admits the silent script.

    ⚑ "RUNS BUT PUBLISHES NOTHING" IS A REAL QUESTION — it is simply not the one `--find` asks,
    and conflating them made every non-publishing script look like a tool with no modes.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = tool_census.census(
            _tree(where, {"scripts/probe.py": _SILENT}), publishing_only=False
        )
    if not rows:
        out.append("selftest: the wider reading excluded a running script")
        return 1
    return 0


def an_unreadable_roster_names_itself(out: list[str]) -> int:
    """Check a roster under an unknown header produces a witness — THE THIRD-STATE ARM.

    ⚑⚑ A FALSE UNDOCUMENTED AND A TRUE ONE ARE INDISTINGUISHABLE TO A READER, and the false one
    sends them to WRITE documentation that already exists. MEASURED: `gate_census.py` published a
    five-row roster and read as UNDOCUMENTED on every mode; the reader who noticed was a human
    comparing a new mode against its four siblings, because nothing in the census could say
    *"I failed to parse this"*.
    """
    got = tool_census.unparsed_roster(_UNKNOWN_HEADER)
    if not got:
        out.append("selftest: an unreadable roster produced no witness")
        return 1
    if "commands" not in got:
        out.append(f"selftest: the witness does not name the header it choked on: {got!r}")
        return 1
    return 0


def a_genuinely_silent_tool_gets_no_excuse(out: list[str]) -> int:
    """Check the witness is EVIDENCE, not inference — the mirror control.

    ⚑ INVENTING AN EXCUSE FOR A TOOL THAT GENUINELY PUBLISHES NOTHING is the opposite defect, and
    it would make every silent tool look like a parser gap. A witness needs a header-shaped line
    AND flag rows beneath it.
    """
    if tool_census.unparsed_roster(_NO_ROSTER):
        out.append("selftest: a genuinely silent tool was handed a parser excuse")
        return 1
    return 0


def the_sources_tag_records_which_layer_found_a_mode(out: list[str]) -> int:
    """Check a mode carries where it came from.

    ⚑ A USAGE LINE CARRIES A SIGNATURE; AN OPTION ROW CARRIES ONLY A GLOSS. Collapsing the two
    would leave a reader unable to tell what kind of gap a divergence is.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = tool_census.census(_tree(where, {"scripts/probe.py": _PUBLISHES}))
    if not rows or tool_census.USAGE not in rows[0].modes["--alpha"].sources:
        out.append("selftest: the mode does not record the layer that found it")
        return 1
    return 0


def the_routing_table_admits_a_named_tool(out: list[str]) -> int:
    """Check the second admission arm reads the live table.

    ⚑⚑ MEASURED BY ELIMINATION: with only the publishing arm, `sql_lift.py` was the single tool
    the origin censuses and this did not. A tool can OWN an artifact kind — and so be the answer
    to a routing question — while declaring its modes where no reader looks.
    """
    got = tool_population.routed_names()
    if not got:
        out.append("selftest: the routing table yielded no tool names — UNMEASURED, not empty")
        return 1
    if _ROUTED not in got:
        out.append(f"selftest: the routing arm read as {sorted(got)!r}")
        return 1
    return 0


def the_live_census_is_not_empty(out: list[str]) -> int:
    """Check the whole pipeline runs against the real tree.

    ⚑ THE FIXTURE ARMS PROVE THE MECHANISM; THIS PROVES IT REACHES. A predicate that admitted
    nothing in the live corpus would pass every arm above.
    """
    rows = tool_census.census()
    if not rows:
        out.append("selftest: the live census is empty")
        return 1
    if not any(row.relpath.startswith("substrate/") for row in rows):
        out.append("selftest: no substrate/ tool reached the live census")
        return 1
    return 0


_ARMS = (
    a_publishing_tool_is_censused,
    a_buried_usage_line_is_still_admitted,
    a_silent_script_is_not_a_tool,
    the_wider_reading_stays_available,
    an_unreadable_roster_names_itself,
    a_genuinely_silent_tool_gets_no_excuse,
    the_sources_tag_records_which_layer_found_a_mode,
    the_routing_table_admits_a_named_tool,
    the_live_census_is_not_empty,
)

_CASE_COUNT = 2 + 2 + 1 + 1 + 2 + 1 + 1 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-census selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-census selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
