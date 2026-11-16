# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""`bibstruct`'s entry point: resolve a mode from the roster, run it, return what it printed.

⚑⚑⚑ THIS IS WIRING, AND ITS SIZE IS THE POINT. The origin's `main` is 377 lines because argv
parsing, the mode roster, the per-mode contracts and every branch body live in one function — so
nothing can read a mode's arity without reading its implementation. Here each of those is a module
that already exists: `bib_argv` owns which token belongs to which flag, `bib_modes` owns the roster,
`bib_pairs` owns the field split, `bib_write` owns the write protocol, `bib_report` owns the
denominator, and `bib_corpus` owns composition. **What is left is lookup and plumbing, which is what
an entry point should be.**

⚑⚑ THE ROSTER IS THE AUTHORITY ON BOTH SIDES OF THE DISPATCH, WHICH IS WHAT KEEPS THIS SMALL. A
handler for a flag no `Mode` declares is a branch the CLI can reach and no reader can see; a `Mode`
with no handler is a promise the CLI does not keep that still feeds arity resolution. Both are
reported by `bib_modes.unbound`, so neither is discovered by a user hitting it.

⚑ NOTHING HERE DECIDES ANYTHING. Every refusal comes from `bib_argv`, every verdict from a reader,
every write from `bib_write`. A branch that made a judgement would be a second authority over a
question one of those modules already answers, which is exactly how the origin grew.

⚑ EXTRACTED, NOT EDITED IN PLACE. `scratch/bibstruct.py` carries enough findings that the per-file
gate refuses every write to it, so this is rebuilt whole and the origin is left alone until it can
be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import bib_argv, bib_modes

if TYPE_CHECKING:
    from collections.abc import Callable

    from substrate import bib_report
    from substrate.climode import Mode

# What a mode's handler returns: the lines to print, and the exit code.
Result = tuple[tuple[str, ...], int]

# The code a refusal exits with. ⚑ READ FROM THE PARSER'S OWN DEFAULT rather than typed here, so
# the entry point cannot disagree with the module that produces the refusals.
REFUSED = bib_argv.Refusal("").code

# ⚑⚑⚑ AN UNREADABLE OPERAND EXITS ON ITS OWN CODE (gate-G244), because the two refusals it would
# otherwise share are two different repairs. `REFUSED` means *I do not know that verb* — a fact
# about the ARGV — and a caller's fix is to spell the mode differently. This means *the file you
# named is not there*, a fact about the OPERAND, and the fix is to correct the path or restore the
# file. Collapsing them tells a script that something went wrong and not which thing.
#
# ⚑⚑ AND IT DIVERGES FROM BOTH FORKS DELIBERATELY. paperkit's copy of this tool exits 1 for an
# absent path, arguing from its own `routes.py` that 2 must mean *not mine* or a gate can skip a
# missing tool silently. That argument is right about 2 and does not reach 3: exiting 1 would put
# an absent operand in the same class as an ordinary failure, which is the collapse one step over.
# The record says the transfer to paperkit is accepted and NOT YET EFFECTIVE, so this is settled
# before the file moves rather than after it becomes an external contract.
UNREADABLE = 3

# ⚑ THE REFUSAL FOR A DECLARED-BUT-UNWIRED MODE, held as a template rather than built inline. A
# reader who invoked a documented mode needs to know the mode is REAL and the wiring is missing,
# not that they mistyped — which is a different message from usage.
UNWIRED = (
    "bibstruct.py: {mode} is declared but not wired — the roster names it and no handler runs it."
)


def usage(modes: dict[str, Mode] | None = None) -> tuple[str, ...]:
    """Render the mode list from the ROSTER, so it cannot drift from what dispatches.

    ⚑⚑ THE ORIGIN PRINTED ITS MODULE DOCSTRING, AND THAT IS THE DRIFT THE ROSTER REMOVES. A usage
    block maintained by hand is a second roster: `toolmodes --divergence` measures modes across the
    corpus that dispatch and appear in no self-description. Rendering from `MODES` makes an
    undocumented mode unrepresentable — if it dispatches it is declared, because the declaration is
    what makes it dispatch.
    """
    table = bib_modes.MODES if modes is None else modes
    rows: list[str] = ["bibstruct.py — the bib reader and writer.", ""]
    for flag, mode in table.items():
        operand = f" <{mode.operand}>" if mode.operand else ""
        paths = " [bib …]" if mode.paths else ""
        marker = " ⚑ writes" if mode.mutates else ""
        rows.append(f"  {flag}{operand}{paths:<12}{mode.why}{marker}")
    return tuple(rows)


def resolve(argv: list[str]) -> bib_argv.Parsed | bib_argv.Refusal:
    """Parse argv against the roster, or return the refusal that says why not.

    ⚑ THE ROSTER AND THE PARSER AGREE BY CONSTRUCTION because the parser's mode rosters are
    derived from it. The origin kept two hand-maintained sets and they disagreed — a third write
    verb reached the guard and never the recogniser.
    """
    return bib_argv.parse(argv)


def render(rows: tuple[str, ...], census: bib_report.Census) -> tuple[str, ...]:
    """Return a read's rows followed by its `n of m` line.

    ⚑ THE DENOMINATOR IS NOT OPTIONAL AND NOT COSMETIC. A bare count cannot distinguish a TOTAL
    read from a probe that examined nothing, so every read mode ends with a census line — which is
    why this is one function rather than a convention each branch remembers.
    """
    return (*rows, census.line())


def run(
    argv: list[str],
    handlers: dict[str, Callable[[bib_argv.Parsed], Result]],
) -> Result:
    """Resolve, dispatch, and return `(lines, code)` — the whole entry point.

    ⚑⚑ A REFUSAL IS A RESULT, NOT AN EXCEPTION. The origin raised `SystemExit` from inside `main`,
    so its own suite ABORTED at the first refusal and twenty-four cases below it were dead text
    while the suite still printed an N/N that read as full coverage. Returning the code makes a
    refusal assertable — and refusing is most of what this tool does.

    ⚑ AN UNKNOWN MODE PRINTS USAGE AND REFUSES. That is not a default: a tool that guesses which
    mode was meant is the operand-ownership defect one level up.
    """
    parsed = resolve(argv)
    if isinstance(parsed, bib_argv.Refusal):
        return (parsed.message,), parsed.code

    if parsed.mode is None:
        return usage(), REFUSED

    handler = bib_modes.dispatch(parsed.mode, handlers)
    if handler is None:
        return (UNWIRED.format(mode=parsed.mode),), REFUSED

    # ⚑⚑⚑ AN UNREADABLE OPERAND IS A REFUSAL, NOT A TRACEBACK (gate-G242). `bib_parse.read` now
    # raises on a path that does not exist, because reporting a missing bib as zero entries let
    # `--entries` certify anything. That refusal has to arrive HERE as a result — this module's
    # own rule is that a refusal is a result and not an exception, and a stack trace escaping
    # through the one function that states that rule would be the defect it was written against.
    try:
        return handler(parsed)
    except OSError as exc:
        return (str(exc),), UNREADABLE
