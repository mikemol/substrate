# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""`bibstruct`'s modes, DECLARED — and a dispatch that is a lookup rather than a chain.

⚑⚑⚑ THE MONOLITHIC FAILURE MODE IS WHAT `climode.Mode` EXISTS TO REMOVE, AND PORTING A DISPATCH
LIFT-AND-CARRY REINSTATES IT. The origin's `main` is a 377-line `if mode == …` chain in which the
argv shape, the contract and the body are the same lines — so nothing can read a mode's arity
without reading its implementation, and the roster exists only as prose in a usage string. That is
the shape this table replaces: **the declaration is data, the bodies live in the extracted modules,
and the dispatch is a lookup.**

⚑⚑ THE DECLARED FIELDS ARE ONES A DISCRIMINATOR CAN CHECK, WHICH IS WHY THIS IS NOT A CONFIG FILE.
`scans` says a branch owes an incomplete-read report. `writes` names WHICH artifact kinds a mode
mutates — a tuple, never a boolean, because *"it matters WHAT you're mutating; a tool might read two
things and only mutate one of them."* `check_mode_contracts.py` (pre-commit, Phase A) runs the
discriminator, so a mode claiming a contract it does not honour is a GATE FAILURE. An inert TOML
table could carry the same words and nothing would ever test them.

⚑ AND THE ARITY IS THE MEASURED COST OF NOT DECLARING. An undeclared mode makes the arg-stripper
GUESS: `--key --archive f.py` crashed because `--key`'s operand bound a tarball path. That is the
operand-ownership class `bib_argv` already carries four instances of, arriving through the roster
instead of through the parser.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

from substrate.climode import Mode

# ⚑⚑⚑ THE ROSTER, AND IT IS THE ONLY ONE. The origin spelled its write verbs in two places — a
# `WRITE_MODES` tuple and a `known` set built inline — so `--addfield` reached the `--bib` guard
# and never the recogniser, and its refusal named only the other two verbs. Here membership,
# arity, contracts and the write set are all read off ONE table, so a fourth verb cannot reach
# one reader and miss another.
MODES: dict[str, Mode] = {
    # ── the reads ────────────────────────────────────────────────────────────
    # ⚑ EVERY READ TAKES `paths=True` AND NO `--bib`, WHICH IS THE FIX FOR A MEASURED DEFECT.
    # `--bib` is the WRITE target and takes exactly one path, so accepting it on a read DROPPED
    # the named file from the read set — a peer measured false dangling edges for every premise
    # defined there and reasonably read a clean corpus as broken. The refusal lives in
    # `bib_argv`; the roster is what makes it expressible.
    "--entries": Mode(paths=True, writes=(), why="every key and the field names it carries"),
    "--field": Mode(
        operand="name",
        paths=True,
        writes=(),
        why="one field's value across every entry that has it",
    ),
    "--mentions": Mode(
        operand="name",
        paths=True,
        writes=(),
        why="entries whose PROSE names this key (evidence, not a verdict)",
    ),
    "--dropped": Mode(paths=True, writes=(), why="fields the engine silently ignores"),
    "--edges": Mode(paths=True, writes=(), why="every declared edge across the composed corpus"),
    "--orphans": Mode(
        paths=True, writes=(), why="edges whose target is no entry in the corpus READ"
    ),
    # ⚑⚑ `--roundtrip` IS THE TOTALITY PROBE AND IT EXITS NON-ZERO ON A FINDING, unlike every
    # other read here. It asks whether the parse ACCOUNTS for the file — the coalgebra question a
    # census cannot answer — so its rows are failures rather than results.
    "--roundtrip": Mode(
        paths=True, writes=(), why="every place the PARSE fails to account for the file"
    ),
    # ── the writes ───────────────────────────────────────────────────────────
    # ⚑⚑⚑ `writes=(".bib",)` IS A CHECKABLE CLAIM, NOT A LABEL. The kinds are keys of the
    # struct-tools artifact table, so a mode declaring it writes a kind its tool does not claim
    # is a DETECTABLE LIE. And it is what binds these three to the `--apply`/`--dry-run` refusal
    # convention: a mutating mode invoked with neither must refuse rather than guess.
    "--add": Mode(
        paths=True,
        opts=("--bib", "--corpus", "--apply"),
        writes=(".bib",),
        why="create a NEW entry from name=value operands",
    ),
    "--set": Mode(
        paths=True,
        opts=("--bib", "--corpus", "--apply"),
        writes=(".bib",),
        why="edit ONE field of ONE existing entry",
    ),
    "--addfield": Mode(
        paths=True,
        opts=("--bib", "--corpus", "--apply"),
        writes=(".bib",),
        why="add a field an existing entry does not carry",
    ),
    "--delete": Mode(
        paths=True,
        opts=("--bib", "--corpus", "--apply"),
        writes=(".bib",),
        why="remove ONE whole entry, refused while it would leave an edge dangling",
    ),
    "--rename": Mode(
        paths=True,
        opts=("--bib", "--corpus", "--apply"),
        writes=(".bib",),
        why="rename ONE entry's key and repoint every inbound edge across the corpus",
    ),
    # ── the suite ────────────────────────────────────────────────────────────
    # ⚑ THE SHARED CONVENTION, DECLARED LIKE ANY OTHER MODE. `--selftest` is one of six flags
    # `toolmodes --conventions` reports as cross-tool contracts, and the roster is where this
    # tool states that it honours it.
    "--selftest": Mode(writes=(), why="run this tool's guarded cases"),
}

# The verbs that MUTATE, derived from the roster rather than restated beside it.
# ⚑⚑ `Mode.mutates` IS ITSELF A PROJECTION OF `writes`, never a stored peer field — *"two
# spellings of one fact that can disagree"*. So this is one derivation over another, and there is
# no third place a write verb can be named.
WRITE_MODES: tuple[str, ...] = tuple(flag for flag, mode in MODES.items() if mode.mutates)

# The verbs that only READ.
READ_MODES: tuple[str, ...] = tuple(
    flag for flag, mode in MODES.items() if not mode.mutates and flag != "--selftest"
)


def known(flag: str) -> bool:
    """Whether this tool dispatches `flag`."""
    return flag in MODES


def operand_of(flag: str) -> str | None:
    """Return what token `flag` itself consumes, or None when it is nullary.

    ⚑ THE QUESTION THE ARG-STRIPPER MUST NOT GUESS. Arity read from a declaration cannot be
    wrong about a mode nobody remembered to handle — it is absent VISIBLY, and the contract gate
    says so, where a guess silently binds the next token.
    """
    mode = MODES.get(flag)
    return mode.operand if mode is not None else None


def accepts(flag: str, opt: str) -> bool:
    """Whether `flag` accepts the modifier `opt`.

    ⚑ A MODIFIER IS OWNED BY A MODE, NOT GLOBALLY TRUE. `--bib` means the write target and is a
    refusal on a read; declaring it per-mode is what lets that refusal be derived rather than
    hand-written at each guard.
    """
    mode = MODES.get(flag)
    return mode is not None and opt in mode.opts


def dispatch[H](flag: str, table: dict[str, H]) -> H | None:
    """Return the handler declared for `flag`, or None when the roster does not name it.

    ⚑⚑⚑ THE LOOKUP IS THE WHOLE DISPATCH, AND THE ROSTER IS THE AUTHORITY ON BOTH SIDES. A
    handler for a flag no `Mode` declares is a branch the CLI can reach and no reader can see —
    which is how a mode ships without documentation. A `Mode` with no handler is the opposite
    defect: *"a promise the CLI does not keep, that still feeds arity resolution."* `unbound()`
    reports both, so neither can be discovered by a user hitting it.

    ⚑⚑ GENERIC IN THE HANDLER, AND THE FIRST CUT WAS NOT — IT PINNED `Callable[[], int]`, A SHAPE
    GUESSED BEFORE ANY CALLER EXISTED. The real handler takes the parse and returns lines with a
    code, so the entry point failed to type-check against the very roster written to serve it.
    **This module knows WHICH flags dispatch and must not claim to know what a handler looks
    like** — that is the caller's contract, and inventing one here made the roster wrong about the
    only consumer it has.
    """
    if flag not in MODES:
        return None
    return table.get(flag)


def unbound[H](table: dict[str, H]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return `(declared_without_handler, handled_without_declaration)`.

    ⚑ BOTH DIRECTIONS, BECAUSE THEY ARE DIFFERENT DEFECTS. The first is a documented mode that
    does not run; the second is a running mode nothing documents. The origin had the second —
    eight flags dispatching with no self-description — and no reader could see either.
    """
    declared = set(MODES)
    handled = set(table)
    return tuple(sorted(declared - handled)), tuple(sorted(handled - declared))
