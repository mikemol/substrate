# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run one converged bib `check` and exit with its verdict (W40, the roster cleanroom).

⚑⚑ THE ONE ENTRY POINT THE `[checks.<kind>]` VERBS CALL. Once every ledger bib `check` is the
spelling `witness_check.emit` produced, paperkit needs a command per kind; each verb calls this
module with the whole check, so the kind semantics live in ONE program rather than in eight
`paper.toml` strings.

    python -m substrate.witness_run --root <tree> '<kind>:<target>'

⚑ THE VERDICT IS `mikemol.ledger.finding_kinds`' — CLOSED 0, OPEN 1, UNRUNNABLE 2 — and the kinds
mtools owns (`selftest`, `refuses`, `standing`, `unwitnessed`) are run by it, never re-implemented.

`mode` runs through `witness_mode`, `excludes` through `witness_excludes`, and `agda-field` /
`agda-grep` through `witness_agda` — each cleanroomed from the ledger's own witness and
differenced against it on the live roster. ⚑ EVERY KIND THE ROSTER USES IS NOW BOUND; an
unparseable check is UNRUNNABLE, never guessed.

⚑ THE TREE IS A PARAMETER (`--root`), resolved at this CLI entry and nowhere else.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mikemol.ledger import finding_kinds, finding_kindspec

from substrate import witness_agda, witness_check, witness_excludes, witness_mode

# The argv shape: the flag, the tree, and the check.
_ARGC = 3


def _run_local(kind: str, args: tuple[object, ...], root: Path) -> finding_kinds.Verdict:
    """Run one of the three substrate-local kinds, as `witness_check.parse_local` returned it."""
    if kind == "excludes":
        mod_path, func, needle = (str(arg) for arg in args)
        return witness_excludes.verdict(mod_path, func, needle, root)
    run = finding_kinds.runner_in(root)
    if kind == "agda_lacks_field":
        module, record, field = (str(arg) for arg in args)
        return witness_agda.lacks_field(module, record, field, run)
    pattern, expected = args
    return witness_agda.grep_holds(str(pattern), int(str(expected)), run)


def verdict(check: str, root: Path) -> finding_kinds.Verdict:
    """Return the verdict for one converged `check`, run in `root`."""
    local = witness_check.parse_local(check)
    if local is not None:
        return _run_local(local[0], local[1], root)
    spec, refusal = finding_kindspec.parse(check)
    if spec is None:
        return finding_kinds.UNRUNNABLE, f"{check}: does not parse: {refusal}"
    return _run_spec(spec, check, root)


def _run_spec(spec: finding_kindspec.Spec, check: str, root: Path) -> finding_kinds.Verdict:
    """Run a parsed kind: the four mtools owns through `finding_kinds`, `mode` locally."""
    if spec.builder == "_selftest":
        return finding_kinds.selftest(list(spec.cmd), check, cwd=root)
    if spec.builder == "_refuses":
        return finding_kinds.refuses(list(spec.cmd), check, cwd=root)
    if spec.builder == "_mode_undocumented":
        return witness_mode.verdict(spec.tool, spec.flag, finding_kinds.runner_in(root))
    if spec.builder == "_standing":
        return finding_kinds.standing(check)
    return finding_kinds.unwitnessed(check)


def main(argv: list[str]) -> int:
    """Run the check named on the command line and exit with its verdict code."""
    args = argv[1:]
    if len(args) != _ARGC or args[0] != "--root":
        sys.stderr.write(__doc__ or "")
        return finding_kinds.UNRUNNABLE
    code, note = verdict(args[2], Path(args[1]))
    sys.stdout.write(f"{note}\n")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
