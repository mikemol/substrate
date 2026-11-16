#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_cli` — a discarded operand is worse than a refused one.

⚑⚑⚑ THE OPERAND ARM IS THE ITEM, AND IT COST A REAL MISREADING. Every census mode accepted an
operand and silently dropped it, so `--divergence scratch/pipeflow.py` printed the whole-corpus
census — byte-identical to the bare call — while reading exactly like a scoped one. The caller
believed the census had been narrowed and reasoned from a corpus-wide answer.

⚑⚑ AND REFUSING IS THE FIX RATHER THAN SCOPING. These predicates are CORPUS-RELATIVE — a flag is
"universal" only against the full population — so a per-tool census would be a DIFFERENT statistic
under the same mode name, which is the two-spelling defect the census exists to prevent.

⚑ A MODIFIER ON THE WRONG MODE IS A TYPO, NOT A NO-OP. Each refusal names the mode that owns it,
so the caller is redirected rather than told only that something was wrong.

⚑ AND A NEGATIVE `--top` IS REFUSED RATHER THAN CLAMPED: `rows[:-3]` silently drops the LAST three
and prints a truncation notice about the wrong end of the list.
"""

from __future__ import annotations

import sys

from substrate import tool_cli

# A census mode, a standalone mode, and the search.
_CENSUS = "--divergence"
_STANDALONE = "--deps"
_FIND = "--find"

# A bound and an out-of-range one.
_TOP = 5
_NEGATIVE = "-3"


def _parsed(args: list[str]) -> tool_cli.Parsed | None:
    """Return the parse when it succeeded, else None."""
    got = tool_cli.parse(args)
    return got if isinstance(got, tool_cli.Parsed) else None


def _refusal(args: list[str]) -> tool_cli.Refusal | None:
    """Return the refusal when it refused, else None."""
    got = tool_cli.parse(args)
    return got if isinstance(got, tool_cli.Refusal) else None


def a_census_mode_parses(out: list[str]) -> int:
    """Check an ordinary invocation is accepted."""
    got = _parsed([_CENSUS])
    if got is None or got.mode != _CENSUS:
        out.append(f"selftest: a census mode parsed as {tool_cli.parse([_CENSUS])!r}")
        return 1
    return 0


def a_census_mode_refuses_an_operand(out: list[str]) -> int:
    """Check a path is refused rather than discarded — THE MISREADING ARM.

    ⚑⚑⚑ AN ACCEPTED-AND-IGNORED OPERAND RETURNS A PLAUSIBLE ANSWER TO A QUESTION NOBODY ASKED.
    A refused one sends the caller to look for the mode that scopes; a discarded one sends them
    away believing a corpus-wide answer was scoped.
    """
    got = _refusal([_CENSUS, "scratch/pipeflow.py"])
    if got is None:
        out.append("selftest: a census mode accepted an operand")
        return 1
    if "CORPUS-WIDE" not in got.message:
        out.append(f"selftest: the refusal does not say why: {got.message!r}")
        return 1
    return 0


def the_operand_refusal_names_what_it_saw(out: list[str]) -> int:
    """Check the message quotes the operand, so the caller sees what was rejected."""
    got = _refusal([_CENSUS, "scratch/pipeflow.py"])
    if got is None or "scratch/pipeflow.py" not in got.message:
        out.append(f"selftest: the refusal does not quote the operand: {got!r}")
        return 1
    return 0


def a_flag_is_not_an_operand(out: list[str]) -> int:
    """Check a modifier is not mistaken for a path.

    ⚑ THE OPERAND TEST IS "DOES NOT START WITH `-`", so a modifier belonging to this mode must
    pass through it untouched.
    """
    if _refusal(["--nearmiss", "--list"]) is not None:
        out.append("selftest: a modifier was refused as an operand")
        return 1
    return 0


def the_search_takes_its_needle(out: list[str]) -> int:
    """Check the one mode with an operand keeps it."""
    got = _parsed([_FIND, "telescope"])
    if got is None or got.operand != "telescope":
        out.append(f"selftest: the needle parsed as {got!r}")
        return 1
    return 0


def the_search_without_a_needle_refuses(out: list[str]) -> int:
    """Check a bare search names its usage."""
    got = _refusal([_FIND])
    if got is None or "usage" not in got.message:
        out.append(f"selftest: a bare search parsed as {tool_cli.parse([_FIND])!r}")
        return 1
    return 0


def top_is_parsed_before_the_needle(out: list[str]) -> int:
    """Check the bound is not searched for — THE ORDERING ARM.

    ⚑⚑ `--find --top` WOULD OTHERWISE SEARCH FOR THE LITERAL STRING `--top`, returning a
    confident answer about a needle the caller never typed.
    """
    got = _parsed([_FIND, "--top", str(_TOP), "telescope"])
    if got is None:
        out.append(f"selftest: the search refused: {tool_cli.parse([_FIND, '--top'])!r}")
        return 1
    if got.top != _TOP:
        out.append(f"selftest: the bound parsed as {got.top!r}")
        return 1
    if got.operand != "telescope":
        out.append(f"selftest: the needle parsed as {got.operand!r} — the bound leaked in")
        return 1
    return 0


def a_bound_with_no_count_refuses(out: list[str]) -> int:
    """Check an omitted count does not consume the needle."""
    got = _refusal([_FIND, "--top", "telescope"])
    if got is None or "COUNT" not in got.message:
        out.append(
            f"selftest: a countless bound parsed as "
            f"{tool_cli.parse([_FIND, '--top', 'telescope'])!r}"
        )
        return 1
    return 0


def a_negative_bound_is_refused_not_clamped(out: list[str]) -> int:
    """Check a negative is rejected — THE WRONG-END ARM.

    ⚑⚑ `rows[:-3]` SILENTLY DROPS THE LAST THREE and prints a truncation notice about the wrong
    end of the list. The caller meant something this cannot do, so they are told rather than
    quietly given the opposite.
    """
    got = _refusal([_FIND, "--top", _NEGATIVE, "telescope"])
    if got is None:
        out.append("selftest: a negative bound was accepted")
        return 1
    if ">= 0" not in got.message:
        out.append(f"selftest: the refusal does not state the range: {got.message!r}")
        return 1
    return 0


def zero_means_every_row(out: list[str]) -> int:
    """Check the unbounded spelling parses as a bound of zero, not as absent."""
    got = _parsed([_FIND, "--top", "0", "telescope"])
    if got is None or got.top != tool_cli.UNBOUNDED:
        out.append(f"selftest: --top 0 parsed as {got.top if got else None!r}")
        return 1
    return 0


def a_modifier_on_the_wrong_mode_names_its_owner(out: list[str]) -> int:
    """Check a misplaced modifier is a redirection, not just a rejection.

    ⚑ A MODIFIER CARRIES NO VERDICT OF ITS OWN, so on the wrong mode it is a typo — and naming
    the mode that owns it is what turns a refusal into an answer.
    """
    for modifier, owner in tool_cli.MODIFIERS.items():
        if modifier == "--top":
            continue  # `--top` needs a count; covered by its own arms
        got = _refusal([_CENSUS, modifier])
        if got is None:
            out.append(f"selftest: {modifier} was accepted on {_CENSUS}")
            return 1
        if owner not in got.message:
            out.append(f"selftest: the refusal for {modifier} does not name {owner}")
            return 1
    return 0


def a_modifier_on_its_own_mode_is_carried(out: list[str]) -> int:
    """Check each modifier reaches the mode that owns it."""
    if not (got := _parsed(["--check", "--autosync"])) or not got.autosync:
        out.append("selftest: --autosync did not reach --check")
        return 1
    if not (got := _parsed(["--declines", "--quick"])) or not got.quick:
        out.append("selftest: --quick did not reach --declines")
        return 1
    if not (got := _parsed(["--nearmiss", "--list"])) or not got.list_keys:
        out.append("selftest: --list did not reach --nearmiss")
        return 1
    return 0


def an_unknown_mode_refuses(out: list[str]) -> int:
    """Check a flag no mode declares is rejected by name."""
    got = _refusal(["--nonesuch"])
    if got is None or "--nonesuch" not in got.message:
        out.append(f"selftest: an unknown mode parsed as {tool_cli.parse(['--nonesuch'])!r}")
        return 1
    return 0


def no_arguments_refuses(out: list[str]) -> int:
    """Check a bare invocation asks for a mode rather than choosing one."""
    if _refusal([]) is None:
        out.append("selftest: an empty argv parsed as a mode")
        return 1
    return 0


def every_declared_flag_is_known(out: list[str]) -> int:
    """Check the known set covers every mode and modifier this parser dispatches.

    ⚑ THE KNOWN SET ARMS THE UNKNOWN-FLAG GUARD, so a mode missing from it would be refused by
    the guard while this parser accepts it — two readers of one roster, disagreeing.
    """
    known = tool_cli.known_flags()
    for flag in (
        *tool_cli.CENSUS_MODES,
        *tool_cli.STANDALONE_MODES,
        tool_cli.FIND,
        *tool_cli.MODIFIERS,
    ):
        if flag not in known:
            out.append(f"selftest: {flag} is dispatched but not in the known set")
            return 1
    return 0


_ARMS = (
    a_census_mode_parses,
    a_census_mode_refuses_an_operand,
    the_operand_refusal_names_what_it_saw,
    a_flag_is_not_an_operand,
    the_search_takes_its_needle,
    the_search_without_a_needle_refuses,
    top_is_parsed_before_the_needle,
    a_bound_with_no_count_refuses,
    a_negative_bound_is_refused_not_clamped,
    zero_means_every_row,
    a_modifier_on_the_wrong_mode_names_its_owner,
    a_modifier_on_its_own_mode_is_carried,
    an_unknown_mode_refuses,
    no_arguments_refuses,
    every_declared_flag_is_known,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 1 + 1 + 3 + 1 + 2 + 1 + 3 + 3 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-cli selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-cli selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
