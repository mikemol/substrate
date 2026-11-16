#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Argument parsing for the mode census — where a modifier is refused rather than ignored.

⚑⚑⚑ AN ACCEPTED-AND-DISCARDED OPERAND RETURNS A PLAUSIBLE ANSWER TO A QUESTION NOBODY ASKED, and
that is the worse half of the defect. MEASURED: every census mode took an operand and silently
dropped it, so `--divergence scratch/pipeflow.py` printed the whole-corpus census — byte-identical
to the bare call — while reading exactly like a scoped one. The caller believed the census had
been narrowed to one tool and reasoned from a corpus-wide answer.

⚑⚑ SO IT REFUSES RATHER THAN IMPLEMENTING SCOPING. The census predicates are CORPUS-RELATIVE — a
flag is "universal" only against the full population — so a per-tool census would be a DIFFERENT
STATISTIC WEARING THE SAME MODE NAME, which is the two-spelling defect this whole census exists to
prevent. Scoping is WORK, and it needs its own mode name.

⚑ A MODIFIER CARRIES NO VERDICT OF ITS OWN, so on the wrong mode it is a TYPO the caller should
hear about rather than a flag silently ignored. `--top` belongs to the search, `--autosync` to the
drift check, `--quick` to the declines; each is refused elsewhere by name.

⚑⚑ AND `--top` IS PARSED BEFORE THE NEEDLE, deliberately: `--find --top` would otherwise search
for the literal string `--top`. A NEGATIVE COUNT IS REFUSED RATHER THAN CLAMPED — `rows[:-3]`
silently drops the LAST three and prints a truncation notice about the wrong end of the list, so
the caller meant something this cannot do and should be told.

⚑ THE UNKNOWN-FLAG GUARD COVERS THE FLAG HALF ONLY. It refuses an unrecognised `--flag` by set
membership; a bare PATH does not start with `-` and passes straight through. Both halves are
needed, which is why the operand check lives here rather than being delegated.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers). This module PARSES; the modes
themselves are the layers below it.
"""

from __future__ import annotations

from dataclasses import dataclass

# The modes that read the whole census and take no operand.
CENSUS_MODES = (
    "--all",
    "--collisions",
    "--siblings",
    "--gaps",
    "--divergence",
    "--conventions",
    "--nearmiss",
    "--sync",
    "--check",
)

# The modes that answer without building a census.
STANDALONE_MODES = ("--deps", "--declines")

# Modifiers, each with the single mode it belongs to. ⚑ A MODIFIER ON THE WRONG MODE IS A TYPO,
# and naming its owner is what turns a refusal into a redirection.
MODIFIERS = {
    "--top": "--find",
    "--autosync": "--check",
    "--quick": "--declines",
    "--list": "--nearmiss",
}

# The search mode, which alone takes an operand.
FIND = "--find"

# What `--top 0` means. ⚑ ZERO IS ALL, matching `substrate.page`.
UNBOUNDED = 0


@dataclass(frozen=True, slots=True)
class Refusal:
    """A parse that will not proceed, and what the caller should do instead."""

    message: str
    code: int = 2


@dataclass(frozen=True, slots=True)
class Parsed:
    """A parse that will proceed: the mode, its operand, and any modifier values."""

    mode: str
    operand: str | None = None
    top: int | None = None
    autosync: bool = False
    quick: bool = False
    list_keys: bool = False


def known_flags() -> frozenset[str]:
    """Return every flag this CLI accepts — modes, standalone modes, and modifiers."""
    return frozenset({*CENSUS_MODES, *STANDALONE_MODES, FIND, *MODIFIERS, "--selftest"})


def _top_of(args: list[str]) -> int | Refusal | None:
    """Return the `--top` count, a refusal, or None when it was not given.

    ⚑ A COUNT IS REQUIRED AND MUST BE NON-NEGATIVE. Omitting it would take the next token — often
    the needle — as the bound; a negative would slice from the END and print a truncation notice
    about the wrong part of the list.
    """
    if "--top" not in args:
        return None
    at = args.index("--top") + 1
    if at >= len(args) or not args[at].lstrip("-").isdigit():
        return Refusal("--top takes a COUNT (--top 0 = every row)")
    value = int(args[at])
    if value < UNBOUNDED:
        return Refusal("--top must be >= 0 (0 = every row)")
    return value


def _misplaced(args: list[str], mode: str) -> Refusal | None:
    """Return a refusal when a modifier appears on a mode that does not own it."""
    for modifier, owner in MODIFIERS.items():
        if modifier in args and mode != owner:
            return Refusal(f"{modifier} is a modifier on {owner}, not a mode (got {mode})")
    return None


def _find(args: list[str]) -> Parsed | Refusal:
    """Parse the search mode, whose operand is a needle rather than a path."""
    top = _top_of(args)
    if isinstance(top, Refusal):
        return top

    rest = [a for a in args[1:] if a != "--top"]
    if "--top" in args:
        at = args.index("--top") + 1
        if at < len(args):
            rest = [a for a in rest if a != args[at]]
    if not rest:
        return Refusal("usage: --find <name> [--top N]  (--top 0 = every row)")
    return Parsed(mode=FIND, operand=rest[0], top=top)


def parse(args: list[str]) -> Parsed | Refusal:
    """Return what to run, or a refusal naming the remedy.

    ⚑ THE ORDER MATTERS. `--find` is parsed first because its operand may look like anything; a
    misplaced modifier is caught next, so `--top` on the wrong mode is a named typo rather than a
    silently ignored flag; and the operand refusal comes last, where it only sees census modes.
    """
    if not args:
        return Refusal("a mode is required")

    mode = args[0]
    if mode == FIND:
        return _find(args)

    misplaced = _misplaced(args, mode)
    if misplaced is not None:
        return misplaced

    if mode in CENSUS_MODES:
        operands = [a for a in args[1:] if not a.startswith("-")]
        if operands:
            # ⚑⚑ REFUSED, NOT SCOPED. A silently-ignored operand returns a whole-corpus answer
            # that reads as a scoped one — and scoping would be a different statistic under the
            # same mode name, since these predicates are corpus-relative.
            return Refusal(
                f"{mode} takes no operand (got {' '.join(operands)}) — this census is "
                "CORPUS-WIDE; it is not scoped by a path. Refusing rather than discarding it: "
                "a silently-ignored operand returns a whole-corpus answer that reads as a "
                "scoped one."
            )

    if mode not in {*CENSUS_MODES, *STANDALONE_MODES}:
        return Refusal(f"unknown mode {mode}")

    return Parsed(
        mode=mode,
        autosync="--autosync" in args,
        quick="--quick" in args,
        list_keys="--list" in args,
    )
