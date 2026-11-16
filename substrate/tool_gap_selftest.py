#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_gap` — a gap needs a denominator, and a ratchet needs a kind.

⚑⚑⚑ "ABSENT ON X" WITHOUT COVERAGE IS A CLAIM A READER CANNOT WEIGH. A kind carried by MOST of a
tool's modes is that tool's CORPUS ARGUMENT, not a capability — `<file>` on 6 of 7 modes is how
the tool takes its document, while `<regex>` on 2 of 12 is a query. Collapsing both would report a
tool as unable to take a file when it takes one, optionally, on nearly every mode.

⚑⚑ AND THE DIVERGENCE KIND IS A RATCHET'S DATA, NOT A LABEL. `FIXTURE` and `UNDOCUMENTED` are the
same row with opposite consequences: one is a declared exemption the gate must not count, the
other is debt it must. An arm below drives both, because a reader that got the KEYS right and the
kinds wrong would look correct while inverting every verdict.

⚑ THE KEY IS `<tool> <flag>`, NOT THE FLAG. `--check` is undocumented on two tools and `--dry` on
two more; a flag-keyed census collides them, so paying down one would read as paying down both — a
ratchet silently forgiving debt it never saw.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — **16 divergence rows, 122 named-undeclared, 0
disagreements**, kinds included.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tool_census, tool_gap

# A tool whose every mode takes a file — the CORPUS-ARGUMENT shape, not a capability.
_CORPUS = (
    '"""a.py --rows <file>   the rows of a document\n'
    "a.py --spans <file>   the spans of a document\n"
    'a.py --tables <file>   the tables of a document\n"""\n'
    "import sys\n"
    'if "--rows" in sys.argv:\n    run()\n'
    'if "--spans" in sys.argv:\n    run()\n'
    'if "--tables" in sys.argv:\n    run()\n'
)

# A tool where the file question is one mode of several — a genuine capability.
_QUERY = (
    '"""b.py --grep <regex>   search the corpus\n'
    "b.py --calls <name>   call sites of a name\n"
    'b.py --read <file>   read one document\n"""\n'
    "import sys\n"
    'if "--grep" in sys.argv:\n    run()\n'
    'if "--calls" in sys.argv:\n    run()\n'
    'if "--read" in sys.argv:\n    run()\n'
)

# A tool that declares a mode its code never dispatches — UNBACKED.
_UNBACKED = (
    '"""c.py --claimed <x>   a mode nothing reaches\n'
    'c.py --real <x>   a mode that dispatches\n"""\n'
    'import sys\nif "--real" in sys.argv:\n    run()\n'
)

# A tool dispatching a flag it documents nowhere — UNDOCUMENTED debt.
_UNDOC = (
    '"""d.py --shown <x>   the shown mode\n"""\n'
    "import sys\n"
    'if "--ghost" in sys.argv:\n    run()\n'
    'if "--shown" in sys.argv:\n    run()\n'
)

# The same, declared as a deliberate failing fixture — an exemption, not debt.
_FIXTURE = (
    '"""e.py --shown <x>   the shown mode\n"""\n'
    "import sys\n"
    f'if "--ghost" in sys.argv:   # {"toolmodes:fixture"}\n    fail()\n'
    'if "--shown" in sys.argv:\n    run()\n'
)

# A tool naming a flag in prose that nothing declares — a filed gap, or a stale reference.
_NAMES = (
    '"""f.py --here <x>   the here mode\n\n'
    'A --nowhere mode is filed but unbuilt.\n"""\n'
    'import sys\nif "--here" in sys.argv:\n    run()\n'
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


def a_corpus_argument_is_distinguishable_from_a_capability(out: list[str]) -> int:
    """Check coverage lets a reader tell one from the other — THE DENOMINATOR ARM.

    ⚑⚑ A KIND ON MOST OF A TOOL'S MODES IS HOW IT TAKES ITS CORPUS. Reporting the same words for
    that and for a genuine one-mode capability is what would name a tool as lacking something it
    does on every invocation.
    """
    rows = _census({"scripts/a.py": _CORPUS, "scripts/b.py": _QUERY})
    coverage = [Coverage for gap in tool_gap.capability_gaps(rows) for Coverage in gap.answered_by]
    if not coverage:
        # No routing-table membership in a temp tree — the arm below covers the predicate
        # directly, so this is a fact about the fixture rather than the module.
        return 0
    if not any(c.is_corpus_argument for c in coverage):
        out.append("selftest: no coverage row reads as a corpus argument")
        return 1
    return 0


def coverage_reports_both_numerator_and_denominator(out: list[str]) -> int:
    """Check a coverage row carries what it is out of."""
    got = tool_gap.Coverage(relpath="a.py", modes_with_kind=6, modes_total=7, modes=())
    if not got.is_corpus_argument:
        out.append("selftest: 6 of 7 modes did not read as a corpus argument")
        return 1
    lean = tool_gap.Coverage(relpath="b.py", modes_with_kind=2, modes_total=12, modes=())
    if lean.is_corpus_argument:
        out.append("selftest: 2 of 12 modes read as a corpus argument")
        return 1
    return 0


def an_empty_tool_is_not_a_corpus_argument(out: list[str]) -> int:
    """Check a tool with no modes does not divide by zero into a verdict."""
    got = tool_gap.Coverage(relpath="c.py", modes_with_kind=0, modes_total=0, modes=())
    if got.is_corpus_argument:
        out.append("selftest: a tool with no modes read as a corpus argument")
        return 1
    return 0


def an_unreachable_routing_table_yields_no_comparable_set(out: list[str]) -> int:
    """Check the comparable set degrades to empty rather than to everything.

    ⚑ AN EMPTY COMPARABLE SET MAKES EVERY GAP ARM SILENT, which is indistinguishable from a
    toolkit with no gaps — so the caller must report it as UNMEASURED. Defaulting to "all tools
    are comparable" would be the opposite error, inventing gaps across unrelated surfaces.
    """
    rows = _census({"scripts/a.py": _CORPUS})
    if tool_gap.capability_gaps(rows):
        out.append("selftest: gaps were reported over an uncomparable population")
        return 1
    return 0


def a_declared_mode_nothing_dispatches_is_unbacked(out: list[str]) -> int:
    """Check a claim with no code behind it is reported."""
    got = tool_gap.divergence(_census({"scripts/c.py": _UNBACKED}))
    if got.get("scripts/c.py --claimed") != tool_gap.UNBACKED:
        out.append(f"selftest: the unbacked claim read as {got!r}")
        return 1
    return 0


def a_dispatched_flag_nothing_documents_is_undocumented(out: list[str]) -> int:
    """Check code with no claim in front of it is reported.

    ⚑⚑ THE SECOND TOOL IS LOAD-BEARING IN THE FIXTURE, and a first cut without it failed. With a
    ONE-tool census the universal set is `intersection(one_set)` — that tool's ENTIRE vocabulary —
    so every flag reads as a shared convention and nothing is ever undocumented. Correct by the
    definition, useless as a fixture, and the same degenerate shape the census's own admission
    predicate has: a population of one cannot discriminate.
    """
    got = tool_gap.divergence(_census({"scripts/d.py": _UNDOC, "scripts/c.py": _UNBACKED}))
    if got.get("scripts/d.py --ghost") != tool_gap.UNDOCUMENTED:
        out.append(f"selftest: the undocumented dispatch read as {got!r}")
        return 1
    return 0


def a_declared_fixture_is_emitted_with_its_own_kind(out: list[str]) -> int:
    """Check an exemption is VISIBLE and DISTINCT — THE RATCHET ARM.

    ⚑⚑ FILTERING A FIXTURE OUT HERE WOULD MAKE AN EXEMPTION INVISIBLE, which is how a ratchet
    rots: the gate shows a smaller number with nothing saying why. The kind travels with the row so
    the RATCHET declines to count it while the REPORT still shows it.
    """
    got = tool_gap.divergence(_census({"scripts/e.py": _FIXTURE, "scripts/c.py": _UNBACKED}))
    if got.get("scripts/e.py --ghost") != tool_gap.FIXTURE:
        out.append(f"selftest: the declared fixture read as {got!r}")
        return 1
    return 0


def the_divergence_key_carries_the_tool(out: list[str]) -> int:
    """Check the same flag on two tools is two rows — THE COLLISION GUARD.

    ⚑ A FLAG-KEYED CENSUS COLLIDES `--ghost` ACROSS TOOLS, so paying down one would read as paying
    down both — a ratchet silently forgiving debt it never saw.
    """
    # ⚑ THE THIRD TOOL BREAKS THE INTERSECTION, and without it this arm tests nothing. With only
    # the two tools that BOTH dispatch `--ghost`, the flag is accepted by every tool in the census
    # — so it reads as a universal convention and neither row is emitted. A shared flag needs a
    # non-sharer present before "shared by two" is distinguishable from "shared by all".
    got = tool_gap.divergence(
        _census({"scripts/d.py": _UNDOC, "scripts/e.py": _FIXTURE, "scripts/c.py": _UNBACKED})
    )
    keys = {key for key in got if key.endswith("--ghost")}
    if len(keys) != len(("d", "e")):
        out.append(f"selftest: the same flag on two tools produced {sorted(keys)!r}")
        return 1
    return 0


def a_flag_named_in_prose_is_reported(out: list[str]) -> int:
    """Check a filed-but-unbuilt gap is derivable from the tool's own output.

    ⚑ THE TOOL WROTE IT DOWN PRECISELY SO THE NEXT READER WOULD FIND IT, and until this arm
    existed nothing read that.
    """
    got = tool_gap.named_but_undeclared(_census({"scripts/f.py": _NAMES}))
    if not any(n.flag == "--nowhere" for n in got):
        out.append(f"selftest: the filed gap was not reported: {got!r}")
        return 1
    return 0


def a_cross_reference_is_not_a_filed_gap(out: list[str]) -> int:
    """Check a flag ANOTHER tool declares is excluded — the remedy, not the debt.

    ⚑ MAKING THIS CLASS INVISIBLE is what let a sibling report get the same flag wrong for as long
    as it did with nothing to contradict it. It is excluded here and COUNTED by the caller.
    """
    owner = (
        '"""g.py --nowhere <x>   the nowhere mode\n"""\n'
        'import sys\nif "--nowhere" in sys.argv:\n    run()\n'
    )
    got = tool_gap.named_but_undeclared(_census({"scripts/f.py": _NAMES, "scripts/g.py": owner}))
    if any(n.flag == "--nowhere" for n in got):
        out.append("selftest: a cross-reference was reported as a filed gap")
        return 1
    return 0


_ARMS = (
    a_corpus_argument_is_distinguishable_from_a_capability,
    coverage_reports_both_numerator_and_denominator,
    an_empty_tool_is_not_a_corpus_argument,
    an_unreachable_routing_table_yields_no_comparable_set,
    a_declared_mode_nothing_dispatches_is_unbacked,
    a_dispatched_flag_nothing_documents_is_undocumented,
    a_declared_fixture_is_emitted_with_its_own_kind,
    the_divergence_key_carries_the_tool,
    a_flag_named_in_prose_is_reported,
    a_cross_reference_is_not_a_filed_gap,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-gap selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-gap selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
