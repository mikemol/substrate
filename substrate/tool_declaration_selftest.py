#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_declaration` — one arm per declaration shape.

⚑⚑⚑ FOUR OF THE FIVE SHAPES WERE FOUND BY REGRESSION, NOT BY DESIGN. Reading source instead of
launching tools broke each in turn, and every break looked the same from outside: a mode the tool
genuinely accepts, reported as undeclared. The sharpest was `--find promote-core` answering
*"named in sppf_db.py's own output, declared by NO tool"* — both clauses true and jointly absurd,
since `make` runs `--promote-core` on every module of a full build.

⚑⚑ SO AN ARM PER SHAPE IS THE MINIMUM, and dropping one would not fail any other. A reader that
handles the docstring, argparse and pair-roster shapes passes eleven of these cases while
silently losing an entire tool's mode list — which is exactly the state the origin shipped in
three times.

⚑ PARITY AGAINST THE ORIGIN WAS MEASURED FIRST — **434 tools, 0 disagreements** on the parsed
mode sets and signatures. These arms guard the PROPERTIES; that run guarded the TRANSCRIPTION,
and only one of the two survives the origin's retirement.
"""

from __future__ import annotations

import sys

from substrate import tool_declaration

# Shape 1 — the module docstring usage block, the assumed one.
_DOCSTRING = '"""probe.py --alpha <x>   the alpha mode\n"""\n'

# Shape 2 — argparse.
_ARGPARSE = (
    "import argparse\n"
    "p = argparse.ArgumentParser()\n"
    "p.add_argument('--beta', help='the beta mode')\n"
)

# Shape 3 — a module-level pair roster (`schema.py`; found when `--widest` went UNDOCUMENTED).
_PAIRS = '_MODES = (("--gamma", "the gamma mode"), ("--delta", "the delta mode"))\n'

# Shape 4 — a usage block that is a module constant rather than the docstring (`agda_defs.py`).
_CONSTANT = 'USAGE = """probe.py --epsilon <x>   the epsilon mode\n"""\n'

# Shape 4b — the SAME roster printed as single-line calls (`sppf_db.py`, ~40 of them). The
# multi-line filter that catches shape 4 excludes every one of these.
_PRINTED = 'print("  probe.py --zeta <x>   the zeta mode")\n'

# Shape 5 — a dict of flag → constructor (`pycodemod.MODES`), the richest declaration.
_CONSTRUCTORS = (
    'MODES = {"--eta": Mode(operand="name", why="the eta mode"),\n'
    '         "--theta": Mode(operand="path", why="the theta mode")}\n'
)

# A refusal, which is NOT a declaration — reading it promoted `--reap` to a top-level mode.
_REFUSAL = 'print("probe.py --coverage --reap: state --dry-run OR --apply first")\n'

# A complaint on stderr — a tool describes itself on stdout and complains on stderr.
_STDERR = 'print("probe.py --iota   not a declaration", file=sys.stderr)\n'

# The tool every fixture names.
_STEM = "probe.py"


def the_docstring_block_is_read(out: list[str]) -> int:
    """Check shape 1 — the assumed one."""
    got = tool_declaration.modes_of(_DOCSTRING, _STEM)
    if "--alpha" not in got:
        out.append(f"selftest: the docstring usage block yielded {sorted(got)!r}")
        return 1
    return 0


def argparse_arguments_are_read(out: list[str]) -> int:
    """Check shape 2 — reconstructed rather than rendered and re-parsed.

    ⚑ THE ROUND TRIP IS WHAT READING SOURCE DELETES. Rendering argparse's exact output in order
    to re-parse it would be re-implementing a formatter to feed a parser.
    """
    got = tool_declaration.modes_of(_ARGPARSE, _STEM)
    if "--beta" not in got:
        out.append(f"selftest: the argparse declaration yielded {sorted(got)!r}")
        return 1
    return 0


def a_pair_roster_is_read(out: list[str]) -> int:
    """Check shape 3 — the structured declaration that cannot drift.

    ⚑ FOUND WHEN `--widest` WENT UNDOCUMENTED on the first static run. `schema.py` builds its
    usage block from a pair tuple rather than from `__doc__`, so a docstring-only read lost it.
    """
    got = tool_declaration.modes_of(_PAIRS, _STEM)
    if {"--gamma", "--delta"} - set(got):
        out.append(f"selftest: the pair roster yielded {sorted(got)!r}")
        return 1
    return 0


def a_usage_constant_is_read(out: list[str]) -> int:
    """Check shape 4 — the block that is not the docstring.

    ⚑ `agda_defs.py` KEEPS A 9-LINE DOCSTRING and prints its real mode list from inside a
    1,057-line `__main__` guard. A docstring-only read lost two modes the tool accepts.
    """
    got = tool_declaration.modes_of(_CONSTANT, _STEM)
    if "--epsilon" not in got:
        out.append(f"selftest: the usage constant yielded {sorted(got)!r}")
        return 1
    return 0


def a_printed_roster_is_read(out: list[str]) -> int:
    """Check shape 4b — the roster printed one line at a time.

    ⚑⚑⚑ THE MULTI-LINE FILTER THAT FINDS SHAPE 4 HIDES THIS ONE, and that produced the sharpest
    misreading in the file's history: `--find promote-core` reporting a mode `make` runs on every
    module as *"declared by NO tool"*. A fact about the METHOD rendered as a fact about the
    SUBSTRATE.
    """
    got = tool_declaration.modes_of(_PRINTED, _STEM)
    if "--zeta" not in got:
        out.append(f"selftest: the printed roster yielded {sorted(got)!r}")
        return 1
    return 0


def a_constructor_roster_is_read(out: list[str]) -> int:
    """Check shape 5 — the richest, and the quietest to miss.

    ⚑ THE PAIR READER SKIPS IT ENTIRELY because it requires both halves to be string constants;
    here the values are `ast.Call` nodes. `Mode` declares the BEHAVIOUR a branch owes, so a
    census that reads glosses and skips this reads the least informative half of the
    best-declared tool.
    """
    got = tool_declaration.modes_of(_CONSTRUCTORS, _STEM)
    if {"--eta", "--theta"} - set(got):
        out.append(f"selftest: the constructor roster yielded {sorted(got)!r}")
        return 1
    return 0


def a_constructor_gloss_is_carried(out: list[str]) -> int:
    """Check the `why=` field becomes the gloss.

    ⚑ THE SAME FIELD `Arm`, `Convention` AND `Decline` CARRY. Reading the key and discarding the
    reason would record that a mode exists while losing what it is for.
    """
    got = tool_declaration.modes_of(_CONSTRUCTORS, _STEM)
    mode = got.get("--eta")
    if mode is None or "eta mode" not in mode.gloss:
        out.append(f"selftest: the constructor gloss read as {mode!r}")
        return 1
    return 0


def a_refusal_is_not_a_declaration(out: list[str]) -> int:
    """Check an error line does not promote its flags to modes — THE NEGATIVE CONTROL.

    ⚑⚑ READING A REFUSAL AS A USAGE LINE PROMOTED `--reap` TO A TOP-LEVEL MODE of `schema.py`,
    which is precisely the defect that file records having fixed once. A census that re-derives a
    retired misreading is worse than one that misses the mode, because the roster now ASSERTS a
    mode nothing dispatches.
    """
    got = tool_declaration.modes_of(_REFUSAL, _STEM)
    if "--reap" in got:
        out.append(f"selftest: a refusal was read as a declaration: {sorted(got)!r}")
        return 1
    return 0


def a_stderr_complaint_is_not_a_declaration(out: list[str]) -> int:
    """Check the stream is itself a signal.

    ⚑ A TOOL DESCRIBES ITSELF ON STDOUT AND COMPLAINS ON STDERR. The stream carries the
    declaration/refusal distinction without needing to parse the sentence.
    """
    got = tool_declaration.modes_of(_STDERR, _STEM)
    if "--iota" in got:
        out.append(f"selftest: a stderr complaint was read as a declaration: {sorted(got)!r}")
        return 1
    return 0


def every_roster_header_spelling_is_read(out: list[str]) -> int:
    """Check all three header spellings — THE ARM THE PARITY RUN HAD TO CATCH FOR ME.

    ⚑⚑⚑ MY FIRST CUT READ ONLY `options:` AND ALL TWELVE OTHER CASES PASSED, because every
    fixture I wrote spelled a header the parser already knew. The parity run against the origin
    found it: three tools, every disagreement `only-origin` — modes LOST, which is the dangerous
    direction. This is the same blind spot the origin records: `gate_census.py` publishes a
    textbook roster under `modes:` and all five of its modes read as UNDOCUMENTED until the
    alternation was widened.

    ⚑⚑ A CASE CANNOT FIND A SHAPE ITS AUTHOR DOES NOT KNOW ABOUT. That is what the origin was
    for, and why the comparison runs before the cases rather than after.
    """
    for header in ("options", "optional arguments", "modes"):
        got = tool_declaration.parse_options(f"{header}:\n  --kappa  the kappa mode\n")
        if "--kappa" not in got:
            out.append(f"selftest: the {header!r} header yielded {sorted(got)!r}")
            return 1
    return 0


def one_pair_is_not_a_roster(out: list[str]) -> int:
    """Check a lone flag-shaped pair does not become a roster.

    ⚑ ONE PAIR IS A COINCIDENCE. Any two-element tuple of strings whose first starts with `--`
    would otherwise declare a mode — including a test fixture or a substitution table.
    """
    got = tool_declaration.modes_of('X = (("--solo", "a lone pair"),)\n', _STEM)
    if "--solo" in got:
        out.append(f"selftest: a single pair was read as a roster: {sorted(got)!r}")
        return 1
    return 0


def an_unparseable_source_yields_what_it_can(out: list[str]) -> int:
    """Check a syntax error degrades rather than raising.

    ⚑ A TOOL MID-EDIT IS A STATE THIS READER WILL MEET. A census that died on one file would
    report nothing about the hundreds it could read.
    """
    if tool_declaration.self_description("def broken(\n") != "":
        out.append("selftest: an unparseable source did not degrade to empty")
        return 1
    return 0


def the_shapes_compose(out: list[str]) -> int:
    """Check a tool declaring several ways gets all of them.

    ⚑⚑ REAL TOOLS MIX SHAPES — a docstring block AND argparse AND a roster. A reader that
    returned at the first shape it recognised would silently drop the rest, which is the
    single-shape assumption every regression here came from.
    """
    got = tool_declaration.modes_of(_DOCSTRING + _ARGPARSE + _PAIRS, _STEM)
    missing = {"--alpha", "--beta", "--gamma", "--delta"} - set(got)
    if missing:
        out.append(f"selftest: mixing shapes lost {sorted(missing)!r}")
        return 1
    return 0


_ARMS = (
    the_docstring_block_is_read,
    argparse_arguments_are_read,
    a_pair_roster_is_read,
    a_usage_constant_is_read,
    a_printed_roster_is_read,
    a_constructor_roster_is_read,
    a_constructor_gloss_is_carried,
    a_refusal_is_not_a_declaration,
    a_stderr_complaint_is_not_a_declaration,
    every_roster_header_spelling_is_read,
    one_pair_is_not_a_roster,
    an_unparseable_source_yields_what_it_can,
    the_shapes_compose,
)

_CASE_COUNT = 1 + 1 + 2 + 1 + 1 + 2 + 1 + 1 + 1 + 3 + 1 + 1 + 4


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-declaration selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-declaration selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
