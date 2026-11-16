#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The `check_scratch_independence` entry point — a roster, a dispatch, and nothing that decides.

⚑⚑⚑ THE SWAP OF THE ⟡drain-arc's FIRST FILE. Four modules now hold everything the origin did:
`scratch_refs` (what a reference IS), `scratch_scope` (the read-only `--scope` census),
`scratch_promotion` (`--promotable`), `scratch_gate` (the verdict). This module is the wiring
— it declares the modes as `climode.Mode`s, resolves argv against them in the origin's order,
and returns `(stdout, stderr, code)` so a refusal is a RESULT the suite can assert (the
`bib_cli` rule: the origin's `main` raised `SystemExit` from inside a branch, and its own suite
aborted at the first refusal while still printing a full-coverage N/N).

⚑⚑ THE DISPATCH ORDER IS THE ORIGIN'S, AND IT IS A PRECEDENCE. `--promotable` is checked first,
then `--scope`, then the gate; `--check` and `--quiet` are modifiers of the gate. The origin
strips every `-`-prefixed token from the operand list rather than binding operands to flags, so
`--scope jea --quiet` and `--quiet --scope jea` read the same — kept, because the pre-commit hook
spells the gate `--quiet` and every caller's spelling must keep resolving.

⚑ EXIT CODES, VERBATIM: the gate is 1 on any hit; `--promotable` is 1 on BLOCK and 2 with no
operand; `--scope` is ALWAYS 0 (a read, never a gate) and 2 with no operand.

⚑ THE ROSTER IS THE AUTHORITY'S (`substrate.promoted.ROOTS`), so the gate now sees `substrate/`
where the origin's frozen list did not. That is the direction `promoted.py` records as the only
acceptable one — consumers move to the authority; entries are never removed to make copies agree.

⚑⚑ THE TREE IS CHOSEN HERE, AT THE ENTRY POINT, AND NOWHERE BELOW (2026-09-24, operator: "We
should not have things [like] corpus.ROOT"). `run` takes the tree as a REQUIRED argument; `main`
reads it from a required `--root <dir>` through `mikemol.corpus.tree_root.from_argv`, which
refuses rather than falling back — a default would answer about wherever the process happened to
be. The pre-commit hook passes `--root "$ROOT"`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.corpus import tree_root

from substrate import climode, scratch_gate, scratch_promotion, scratch_scope

if TYPE_CHECKING:
    from pathlib import Path

# The exit codes, as the origin returns them.
OK = 0
FAILED = 1
USAGE = 2

# The modes, declared. ⚑ `--mentions` and `--quiet` are MODIFIERS owned by the modes that accept
# them, so neither reads as a mode of its own — the origin's docstring makes the same point.
MODES: dict[str, climode.Mode] = {
    "--check": climode.Mode(scans=True, why="the gate, quiet — the alias hook callers spell"),
    "--quiet": climode.Mode(scans=True, why="the gate, silent on success"),
    "--promotable": climode.Mode(
        operand="<dir>", scans=True, why="would promoting <dir> out of scratch/ hold?"
    ),
    "--scope": climode.Mode(
        operand="<dir>…",
        paths=True,
        opts=("--quiet", "--mentions"),
        scans=True,
        why="READ-ONLY: live scratch/ refs in dirs the GATE does not cover",
    ),
    climode.POSITIONAL: climode.Mode(scans=True, why="the gate over ROOTS; exit 1 on any ref"),
}

_PROMOTABLE_USAGE = (
    "usage: check_scratch_independence.py --promotable <dir>",
    "  e.g. --promotable scratch/cotype-ebnf-strictness",
)
_SCOPE_USAGE = (
    "usage: check_scratch_independence.py --scope <dir>… [--quiet]",
    "  e.g. --scope scripts        # the commit-path tooling",
    "       --scope scripts jea    # several at once",
    "       --scope scripts --mentions   # the residue: non-path 'scratch' strings",
    "  READ-ONLY: reports live scratch/ refs in dirs the GATE does not cover.",
)


def _operands(argv: list[str]) -> list[str]:
    """Return every token that is not a flag — the origin's operand rule."""
    return [a for a in argv if not a.startswith("-")]


def _promotable(argv: list[str], root: Path) -> tuple[list[str], list[str], int]:
    """Run `--promotable <dir>`: the verdict lines on stdout, exit 1 on BLOCK."""
    args = _operands(argv)
    if not args:
        return list(_PROMOTABLE_USAGE), [], USAGE
    verdict = scratch_promotion.report(args[0], root)
    return scratch_promotion.render(args[0], verdict), [], OK if verdict.ok else FAILED


def _scope(argv: list[str], root: Path) -> tuple[list[str], list[str], int]:
    """Run `--scope <dir>… [--quiet] [--mentions]`: always exit 0 once it has operands."""
    scope = _operands(argv[argv.index("--scope") + 1 :])
    if not scope:
        return [], list(_SCOPE_USAGE), USAGE
    found = scratch_scope.census(scope, root)
    err = scratch_scope.diagnostics(found)
    if "--mentions" in argv:
        return scratch_scope.render_mentions(found, scope), err, OK
    return scratch_scope.render(found, scope, quiet="--quiet" in argv), err, OK


def _gate(argv: list[str], root: Path) -> tuple[list[str], list[str], int]:
    """Run the gate: FAILED report on stderr and exit 1 on any hit, else the OK line."""
    quiet = "--quiet" in argv or "--check" in argv
    result = scratch_gate.run(root)
    out, err = scratch_gate.render(result)
    return ([] if quiet else out), err, (OK if result.ok else FAILED)


def run(argv: list[str], root: Path) -> tuple[list[str], list[str], int]:
    """Dispatch argv over the tree `root`, in the origin's precedence: `(stdout, stderr, code)`."""
    if "--promotable" in argv:
        return _promotable(argv, root)
    if "--scope" in argv:
        return _scope(argv, root)
    return _gate(argv, root)


def main(argv: list[str]) -> int:
    """Read `--root <dir>` (required), run, print, and hand back the exit code."""
    import sys  # noqa: PLC0415 - the only place output happens

    try:
        tree, rest = tree_root.from_argv(argv)
    except tree_root.RootError as exc:
        sys.stderr.write(f"check_scratch_independence: {exc}\n")
        return USAGE
    out, err, code = run(rest, tree.path)
    if out:
        sys.stdout.write("\n".join(out) + "\n")
    if err:
        sys.stderr.write("\n".join(err) + "\n")
    return code


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv[1:]))
