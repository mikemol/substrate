#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_find` and its renderer — seven arms, each a recorded miss.

⚑⚑⚑ NO ARM HERE WAS DESIGNED; EACH WAS ADDED AFTER A REAL SEARCH RETURNED NOTHING while the
capability sat in the tree. The sharpest was the TOOL arm: `--find telescope` returned four
library functions while `split_telescoped.py` — the tool that performs the operation — appeared
nowhere, and `--find split_telescoped` returned **0 hits for the tool's own name**. A reader
asking *"how do I split a telescoped module"* was answered with a function list.

⚑⚑ THE MENTION SPLIT IS A PARTITION, AND ONE RUN ONCE CONTRADICTED ITSELF ON IT. The prose arm
read mentions alone and printed *"declared by NO tool"* while the mode arm, reading the same
index, printed the declarer — so a single invocation said `agda_defs` declares `--telescope` AND
that nothing declares it. The arms below assert the partition, not just the rows.

⚑ AND THE FUNCTION ARM'S BOUND CLOSES A SILENT CAP: `--find _sql` reported 54 hits and printed 20
with `… and 32 more` — a count that was exact beside a list that was not, and a notice that named
the omission without offering any way to remove it.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — **7 needles over 98 shared tools, 0
disagreements**, including the cited/prose partition.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import tool_census, tool_find, tool_find_render

# A tool declaring a mode, and a second that CITES it — the attribution fixture.
_OWNER = (
    '"""owner.py --telescope <mod>   repair a telescope a split dropped\n"""\n'
    'import sys\nif "--telescope" in sys.argv:\n    run()\n'
)
_CITER = (
    '"""citer.py --split <mod>   split a module\n\n'
    'Contract preserved — verified by `owner.py --telescope`.\n"""\n'
    'import sys\nif "--split" in sys.argv:\n    run()\n'
)

# A tool whose gloss names the capability under a different word.
_SYNONYM = (
    '"""other.py --widen <x>   grow the telescope past its header\n"""\n'
    'import sys\nif "--widen" in sys.argv:\n    run()\n'
)

# A tool that dispatches a flag it documents nowhere.
_UNDOC = (
    '"""quiet.py --shown <x>   the shown mode\n"""\n'
    'import sys\nif "--telescope" in sys.argv:\n    run()\n'
    'if "--shown" in sys.argv:\n    run()\n'
)

_OWNER_REL = "scripts/owner.py"
_CITER_REL = "scripts/citer.py"
_SYNONYM_REL = "scripts/other.py"
_UNDOC_REL = "scripts/quiet.py"

# Function glosses, in the shape the finder consumes.
_GLOSSES = (
    ("scratch/a.py", "literal_flags", "the flag string constants in a tool's AST"),
    ("scratch/b.py", "cli_flags", "every flag constant a tool's AST carries"),
    ("scratch/c.py", "unrelated", "compute a checksum over bytes"),
)

# How many function rows the paging fixture builds, and the bound applied to them.
_MANY = 50
_BOUND = 5


def _census(files: dict[str, str]) -> tuple[tool_census.Tool, ...]:
    """Build a fixture tree and return its census."""
    with tempfile.TemporaryDirectory() as where:
        root = Path(where)
        for name, body in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        return tool_census.census(root)


def _found(needle: str, glosses: tuple[tuple[str, str, str], ...] = ()) -> tool_find.Found:
    """Search the standard fixture corpus."""
    rows = _census(
        {_OWNER_REL: _OWNER, _CITER_REL: _CITER, _SYNONYM_REL: _SYNONYM, _UNDOC_REL: _UNDOC}
    )
    return tool_find.find(rows, needle, glosses)


def a_mode_is_found_by_name(out: list[str]) -> int:
    """Check the original arm still answers."""
    got = _found("telescope")
    if not any(hit.mode == "--telescope" for hit in got.by_mode):
        out.append(f"selftest: the declared mode was not found: {got.by_mode!r}")
        return 1
    return 0


def the_tools_lacking_a_mode_are_named(out: list[str]) -> int:
    """Check the actionable half is present — THE FIVE-MISS ARM.

    ⚑ "`--grep` EXISTS" WAS NEVER THE OPERATOR'S PROBLEM; "it is not on the tool I just typed"
    was. Naming the tools that LACK it is what makes the census actionable rather than correct.
    """
    got = _found("telescope")
    if _CITER_REL not in got.lacking:
        out.append(f"selftest: the tools lacking the mode read as {got.lacking!r}")
        return 1
    if _OWNER_REL in got.lacking:
        out.append("selftest: the declaring tool was listed as lacking its own mode")
        return 1
    return 0


def a_mode_is_found_by_gloss(out: list[str]) -> int:
    """Check a differently-named mode is reachable through its description."""
    got = _found("telescope")
    if not any(hit.mode == "--widen" for hit in got.by_gloss):
        out.append(f"selftest: the gloss arm found {got.by_gloss!r}")
        return 1
    return 0


def a_name_match_is_not_repeated_in_the_gloss_arm(out: list[str]) -> int:
    """Check the two mode arms partition rather than overlap."""
    got = _found("telescope")
    names = {hit.mode for hit in got.by_mode}
    if names & {hit.mode for hit in got.by_gloss}:
        out.append("selftest: a mode appears in both mode arms")
        return 1
    return 0


def a_citation_is_separated_from_a_gap(out: list[str]) -> int:
    """Check a tool naming another's mode lands in CITED — THE ATTRIBUTION ARM.

    ⚑⚑ ONE RUN ONCE SAID A TOOL DECLARES `--telescope` AND THAT NOTHING DECLARES IT, because two
    arms read different predicates. Reporting a cross-reference as debt drives a paydown that
    deletes the cross-discoverability the standing rule requires.
    """
    got = _found("telescope")
    cited = {(hit.relpath, hit.flag) for hit in got.cited}
    prose = {(hit.relpath, hit.flag) for hit in got.prose}
    if (_CITER_REL, "--telescope") not in cited:
        out.append(f"selftest: the cross-reference was not cited: {sorted(cited)!r}")
        return 1
    if cited & prose:
        out.append("selftest: a mention appears in both the cited and prose arms")
        return 1
    return 0


def an_undocumented_dispatch_is_reported(out: list[str]) -> int:
    """Check a flag a tool accepts but never declares is surfaced."""
    got = _found("telescope")
    if (_UNDOC_REL, "--telescope") not in got.dispatched:
        out.append(f"selftest: the undocumented dispatch read as {got.dispatched!r}")
        return 1
    return 0


def a_function_is_found_by_name_and_by_meaning(out: list[str]) -> int:
    """Check both function arms — THE REINVENTION CASE.

    ⚑⚑ `cli_flags` WAS WRITTEN AS A REINVENTION OF `literal_flags`, and a name-only search reports
    nothing: a searcher who knows what the thing DOES but not what it is CALLED is a different
    reader from one who knows the name.
    """
    got = _found("literal", _GLOSSES)
    names = {hit.name for hit in got.functions}
    if "literal_flags" not in names:
        out.append(f"selftest: the name arm missed its own case: {sorted(names)!r}")
        return 1
    if "unrelated" in names:
        out.append("selftest: an unrelated function matched")
        return 1
    return 0


def a_tool_is_found_as_a_whole(out: list[str]) -> int:
    """Check the tool arm answers "which tool does this" — THE FAMILY-SCALE MISS.

    ⚑⚑⚑ EVERY OTHER ARM SEARCHES INSIDE A TOOL. `--find split_telescoped` once returned 0 hits
    for the tool's own name, because nothing searched for a TOOL.
    """
    got = _found("owner")
    if not any(hit.relpath == _OWNER_REL for hit in got.tools):
        out.append(f"selftest: the tool arm found {got.tools!r}")
        return 1
    return 0


def a_tool_is_found_by_its_whole_docstring(out: list[str]) -> int:
    """Check the match reads past line one.

    ⚑ A TOOL WHOSE OPENING SENTENCE IS ITS MECHANISM rather than its occasion stayed unreachable
    when only the first line was matched. A one-line window is a curated summary the tool never
    agreed to write.
    """
    got = _found("split dropped")
    if not any(hit.relpath == _OWNER_REL for hit in got.tools):
        out.append(f"selftest: a phrase below line one did not match: {got.tools!r}")
        return 1
    return 0


def an_unsearched_function_corpus_says_so(out: list[str]) -> int:
    """Check the renderer distinguishes unsearched from empty — THE UNMEASURED ARM.

    ⚑⚑ A CALLER THAT DID NOT PAY FOR THE DOCSTRING WALK must not be told the capability is
    absent. "No tool does this" is a claim the search cannot support.
    """
    got = tool_find_render.render(
        _found("telescope"), tool_find_render.Scope(tools=4, modes=4, functions=0, searched=False)
    )
    if "not searched" not in got:
        out.append("selftest: an unsearched function corpus rendered as empty")
        return 1
    return 0


def the_function_arm_pages_and_names_its_remedy(out: list[str]) -> int:
    """Check the bound reports what it withheld AND how to see it.

    ⚑⚑ THE SILENT CAP SAID "… and 32 more" WITHOUT OFFERING A WAY TO REMOVE IT — honest and
    unactionable in the same breath, which sent a caller to a flag that did not exist.
    """
    # ⚑ THE NAME CARRIES THE NEEDLE, because the fixture must actually MATCH before it can page.
    # A first cut named them `fn_0…` with a gloss that shared no stemmed token with `literal`, so
    # nothing matched, the arm was empty, and the case failed reporting a missing notice — a
    # fixture testing its own construction rather than the bound.
    many = tuple(
        (f"scratch/{n}.py", f"literal_probe_{n}", "the flag constants a tool carries")
        for n in range(_MANY)
    )
    found = _found("literal", many)
    got = tool_find_render.render(
        found, tool_find_render.Scope(tools=4, modes=4, functions=_MANY), _BOUND
    )
    if "more" not in got:
        out.append("selftest: a bounded function arm did not say what it withheld")
        return 1
    if "--top 0" not in got:
        out.append("selftest: the truncation notice does not name its remedy")
        return 1
    return 0


def an_unbounded_function_arm_says_nothing(out: list[str]) -> int:
    """Check a complete list carries no notice.

    ⚑ A FOOTER ON EVERY CALL trains a reader to ignore the channel, which is what makes the one
    that matters invisible.
    """
    got = tool_find_render.render(
        _found("literal", _GLOSSES),
        tool_find_render.Scope(tools=4, modes=4, functions=len(_GLOSSES)),
        0,
    )
    if "more —" in got:
        out.append("selftest: an unbounded function arm emitted a truncation notice")
        return 1
    return 0


def the_footer_carries_the_denominators(out: list[str]) -> int:
    """Check a hit count is reported against a population.

    ⚑ A COUNT WITH NO DENOMINATOR is a number a reader cannot weigh, and "0 hits" without saying
    over what is the absence-as-fact shape this census refuses.
    """
    got = tool_find_render.render(
        _found("telescope"), tool_find_render.Scope(tools=4, modes=7, functions=99)
    )
    for figure in ("4 tool(s)", "7 declared mode(s)", "99 documented function(s)"):
        if figure not in got:
            out.append(f"selftest: the footer omits {figure!r}")
            return 1
    return 0


_ARMS = (
    a_mode_is_found_by_name,
    the_tools_lacking_a_mode_are_named,
    a_mode_is_found_by_gloss,
    a_name_match_is_not_repeated_in_the_gloss_arm,
    a_citation_is_separated_from_a_gap,
    an_undocumented_dispatch_is_reported,
    a_function_is_found_by_name_and_by_meaning,
    a_tool_is_found_as_a_whole,
    a_tool_is_found_by_its_whole_docstring,
    an_unsearched_function_corpus_says_so,
    the_function_arm_pages_and_names_its_remedy,
    an_unbounded_function_arm_says_nothing,
    the_footer_carries_the_denominators,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 2 + 1 + 2 + 1 + 1 + 1 + 2 + 1 + 3


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-find selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-find selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
