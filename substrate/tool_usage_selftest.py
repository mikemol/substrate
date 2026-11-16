#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_usage` — the fixtures are the shapes that broke the origin.

⚑⚑⚑ EVERY ARM HERE IS A MEASURED DEFECT, NOT AN INVENTED EDGE CASE. The origin module records
each one against a named tool: bracketed options read as modes, a `#`-only gloss split emptying
bibstruct, a gloss's own `<key>` counted as a second argument, a positional-only tool dropped.
Writing fixtures from imagination would test the parser this rewrite happens to be; these test
the parser the corpus demanded.

⚑⚑ AND PARITY AGAINST THE ORIGIN WAS MEASURED BEFORE THESE WERE WRITTEN — **432 tools compared,
0 disagreements** in modes, signatures and glosses. That is the check a suite over the new module
alone cannot make: cases pin whatever the rewrite does, so a faithful rewrite and a subtly
different one both go green. The origin is still on disk during the split, which is the only
window in which that comparison exists.

⚑ SO THESE ARMS GUARD THE PROPERTIES, and the parity run guarded the TRANSCRIPTION. Two different
questions, and only one of them stays answerable after the origin is retired.
"""

from __future__ import annotations

import sys

from substrate import tool_usage

# The measured case for bracket-awareness: three flags, one mode.
_BRACKETED = "mdstruct.py --rows <file> [--table N] [--where <substr>]   the rows of a table\n"

# A positional preceding the mode — the shape that is lost by reading the first token only.
_POSITIONAL_FIRST = "transcriptstruct.py <file> --messages   every message in a session\n"

# A tool whose whole interface is a path.
_POSITIONAL_ONLY = "agda_defs.py <name> ...   where a name is defined\n"

# The column-aligned gloss that a `#`-only split swallowed into the argument region.
_ALIGNED = "bibstruct.py --field <name> [bib]        which entries set <name>\n"

# The single-space separator that defeats column alignment too.
_ONE_SPACE = "bibstruct.py --mentions <key> [bib] whose PROSE names <key> — edge evidence\n"

# A mode documented twice with different arguments; both glosses are kept.
_TWICE = (
    "pycodemod.py --attr <name> [paths]   attribute reads\n"
    "pycodemod.py --attr <Recv>.* [paths]   the INVERSE reading\n"
)

# A wrapped rationale under a usage line — usually the half that says what the mode is FOR.
_WRAPPED = (
    "mdstruct.py --spans <file>   the spans\n"
    "                             # and what each one covers\n"
)

# Prose that names a tool without declaring anything.
_PROSE = "See pycodemod.py for the structural queries this replaces.\n"


def bracketed_flags_are_not_modes(out: list[str]) -> int:
    """Check `[--table N]` is an option, not a mode — THE MEASURED DEFECT.

    ⚑⚑ READING ALL THREE FLAGS AS MODES INVENTS TWO THAT NO DISPATCH HAS, and the invented ones
    then appear in the gap census as capabilities to build. Eight of thirteen entries in that
    census were this artefact.
    """
    got = tool_usage.parse_usage(_BRACKETED, "mdstruct.py")
    if set(got) != {"--rows"}:
        out.append(f"selftest: bracketed options leaked into the modes: {sorted(got)!r}")
        return 1
    return 0


def a_bracketed_option_is_still_reported(out: list[str]) -> int:
    """Check the options ARE readable, just not as modes.

    ⚑ DECLARED, JUST NOT AS MODES. Subtracting only the modes from a tool's prose mentions
    reported these as "named by a tool and declared by nothing" — filed gaps for flags that exist.
    """
    got = tool_usage.bracketed_options(_BRACKETED, "mdstruct.py")
    if got != {"--table", "--where"}:
        out.append(f"selftest: the bracketed options read as {got!r}")
        return 1
    return 0


def a_mode_after_a_positional_is_found(out: list[str]) -> int:
    """Check a mode is seen when a positional precedes it.

    ⚑ READING ONLY THE FIRST TOKEN AFTER THE BASENAME loses `--messages` entirely — the opposite
    error from the bracket one, and the reason the parse is a scan rather than a peek.
    """
    got = tool_usage.parse_usage(_POSITIONAL_FIRST, "transcriptstruct.py")
    if "--messages" not in got:
        out.append(f"selftest: a mode after a positional was lost: {sorted(got)!r}")
        return 1
    return 0


def a_positional_only_tool_is_recorded(out: list[str]) -> int:
    """Check a path-only interface publishes `(positional)` rather than nothing.

    ⚑⚑ DROPPING IT SHRANK THE POPULATION FROM 74 TOOLS TO 9 in the origin's own measurement, and
    the excluded entries were the paydown census. A tool whose whole interface is a path still
    SHARES that interface with sixteen others, which is the convergence finding.
    """
    got = tool_usage.parse_usage(_POSITIONAL_ONLY, "agda_defs.py")
    if tool_usage.POSITIONAL not in got:
        out.append(f"selftest: a positional-only tool published nothing: {sorted(got)!r}")
        return 1
    return 0


def a_column_aligned_gloss_is_not_an_argument(out: list[str]) -> int:
    """Check prose after a column break does not become part of the signature.

    ⚑⚑⚑ THIS IS THE DEFECT THAT FABRICATED A TOOL'S ENTIRE SIGNATURE SET. `--field <name> [bib]
    which entries set <name>` parsed as taking `<name> <name>` — the gloss's own placeholder
    counted as a second argument, and the signature is what the gap and sibling reports are
    computed from.
    """
    got = tool_usage.parse_usage(_ALIGNED, "bibstruct.py")
    mode = got.get("--field")
    if mode is None:
        out.append("selftest: the aligned usage line published no mode")
        return 1
    if len(mode.sig) != 1:
        out.append(f"selftest: the gloss leaked into the signature: {mode.sig!r}")
        return 1
    if not mode.gloss:
        out.append("selftest: the column-aligned gloss came back empty")
        return 1
    return 0


def a_single_space_gloss_is_still_cut(out: list[str]) -> int:
    """Check the grammatical cut catches what neither `#` nor alignment does.

    ⚑ THE TOOLS DO NOT HOLD TO ONE CONVENTION, which is why there are three cuts and the earliest
    wins. This line separates its gloss with ONE space.
    """
    got = tool_usage.parse_usage(_ONE_SPACE, "bibstruct.py")
    mode = got.get("--mentions")
    if mode is None:
        out.append("selftest: the single-space usage line published no mode")
        return 1
    if len(mode.sig) != 1:
        out.append(f"selftest: the single-space gloss leaked into the signature: {mode.sig!r}")
        return 1
    return 0


def both_glosses_survive_a_double_declaration(out: list[str]) -> int:
    """Check a mode documented twice keeps both readings.

    ⚑ THE SECOND IS WHERE THE INVERSE READING IS EXPLAINED, so keeping only one loses half the
    mode — and the half that is lost is the one a reader could not have guessed.
    """
    got = tool_usage.parse_usage(_TWICE, "pycodemod.py")
    mode = got.get("--attr")
    if mode is None:
        out.append("selftest: the twice-declared mode is absent")
        return 1
    if "INVERSE" not in mode.gloss or "attribute reads" not in mode.gloss:
        out.append(f"selftest: one of the two glosses was dropped: {mode.gloss!r}")
        return 1
    return 0


def a_wrapped_rationale_is_kept(out: list[str]) -> int:
    """Check continuation lines join the gloss.

    ⚑ THE WRAPPED HALF IS USUALLY THE PART THAT SAYS WHAT THE MODE IS FOR — reading only the
    first line keeps the label and drops the reason.
    """
    got = tool_usage.parse_usage(_WRAPPED, "mdstruct.py")
    mode = got.get("--spans")
    if mode is None or "what each one covers" not in mode.gloss:
        out.append(f"selftest: the wrapped rationale was dropped: {mode!r}")
        return 1
    return 0


def prose_is_not_a_usage_line(out: list[str]) -> int:
    """Check a sentence naming a tool declares nothing — the negative control.

    ⚑ WITHOUT THIS, a parser that admitted every line mentioning the tool would pass every arm
    above while inventing modes out of documentation.
    """
    got = tool_usage.parse_usage(_PROSE, "pycodemod.py")
    if got:
        out.append(f"selftest: prose was read as a usage line: {sorted(got)!r}")
        return 1
    return 0


def a_tool_is_named_as_a_word(out: list[str]) -> int:
    """Check a substring match does not attribute a helper's lines to the tool.

    ⚑ `scratch/pycodemod.py` NAMES THE TOOL; `_pycodemod_query.py` DOES NOT. Matching loosely
    would fold a private helper's usage into its public sibling's mode list.
    """
    if tool_usage.names_tool("pycodemod.py", "_pycodemod_query.py --x") is not None:
        out.append("selftest: a helper's name matched the tool as a substring")
        return 1
    if tool_usage.names_tool("pycodemod.py", "scratch/pycodemod.py --x") is None:
        out.append("selftest: the tool's own line did not match")
        return 1
    return 0


def nested_brackets_are_walked(out: list[str]) -> int:
    """Check the bracket walk handles nesting rather than counting pairs.

    ⚑ A NAIVE STRIP would reopen at the inner `]` and expose the tail of an outer group, which
    turns an option into a mode at exactly the lines that are hardest to read by eye.
    """
    got = tool_usage.outside_brackets("--mode <a> [[--inner] --outer] --after")
    if "--inner" in got or "--outer" in got:
        out.append(f"selftest: a nested bracket leaked: {got!r}")
        return 1
    if "--mode" not in got or "--after" not in got:
        out.append(f"selftest: unbracketed flags were swallowed: {got!r}")
        return 1
    return 0


_ARMS = (
    bracketed_flags_are_not_modes,
    a_bracketed_option_is_still_reported,
    a_mode_after_a_positional_is_found,
    a_positional_only_tool_is_recorded,
    a_column_aligned_gloss_is_not_an_argument,
    a_single_space_gloss_is_still_cut,
    both_glosses_survive_a_double_declaration,
    a_wrapped_rationale_is_kept,
    prose_is_not_a_usage_line,
    a_tool_is_named_as_a_word,
    nested_brackets_are_walked,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 3 + 2 + 2 + 1 + 1 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-usage selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-usage selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
