#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for the ledger's `[checks.<kind>]` verbs — each run exactly as paperkit runs it.

⚑⚑ A VERB IS A SHELL STRING, AND NOTHING ELSE TESTS ONE. paperkit splits a check on its first
`:`, substitutes the rest into `[checks.<kind>].cmd` with `str.replace("{target}", …)` UNQUOTED,
and runs the result through a shell from the project directory. So a verb can be wrong in ways
no Python test of `witness_run` sees: a bad `cd`, a missing interpreter, broken quoting. Each
case here does exactly what paperkit does and requires the exit to EQUAL `witness_run.verdict`
on the same check.

⚑ THE HAZARDOUS TARGET IS CASED ON PURPOSE: the live `agda-grep` witness carries a `$`, the one
shell metacharacter the census found, and a verb that let the shell expand it would count a
different pattern.

⚑ `selftest`/`refuses` use `true`/`false` rather than live rows — both polarities, and without
running hundreds of real suites. The tree is the working directory, resolved at this CLI entry.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

from mikemol.ledger import finding_kinds

from substrate import ledger_cli, witness_run

# The ledger project, relative to the tree.
_PROJECT = ledger_cli.PROJECT

# One live check is sampled per kind; `selftest`/`refuses` get synthetic checks instead.
_SYNTHETIC = ("selftest:true", "selftest:false", "refuses:true", "refuses:false")
_LIVE_KINDS = ("standing", "unwitnessed", "mode", "excludes", "agda-field", "agda-grep")


def _verbs(project: Path) -> dict[str, str]:
    """Return `{kind: cmd}` for every `[checks.<kind>]` the project's paper.toml declares.

    ⚑ THE `Any` FROM `tomllib` IS NARROWED HERE, AT THE SEAM (the `dep_addressing.declared`
    shape), so every expression downstream is concrete.
    """
    parsed: object = tomllib.loads(project.joinpath("paper.toml").read_text(encoding="utf-8"))
    checks: object = parsed.get("checks") if isinstance(parsed, dict) else None
    if not isinstance(checks, dict):
        return {}
    verbs: dict[str, str] = {}
    for kind, table in checks.items():
        cmd: object = table.get("cmd") if isinstance(table, dict) else None
        if isinstance(kind, str) and isinstance(cmd, str):
            verbs[kind] = cmd
    return verbs


def _samples(project: Path) -> list[str]:
    """Return the checks to run: the synthetic ones, then one live spelling per kind.

    ⚑ THE LIVE SPELLINGS ARE READ FROM THE BIBS, not re-emitted from the roster: since the
    convergence each entry's `check` IS the witness paperkit runs, so sampling the roster would
    test a spelling one step removed from the thing the verb receives.
    """
    picked: dict[str, str] = {}
    for check in ledger_cli.checks(project).values():
        kind = ledger_cli.kind_of(check)
        if kind in _LIVE_KINDS and kind not in picked:
            picked[kind] = check
    return [*_SYNTHETIC, *picked.values()]


def _as_paperkit(verbs: dict[str, str], check: str, project: Path) -> int | None:
    """Run `check` as paperkit does: split, substitute unquoted, shell, from `project`."""
    kind, _, target = check.partition(":")
    code, _ = finding_kinds.run("sh", "-c", verbs[kind].replace("{target}", target), cwd=project)
    return code


def _cases(root: Path) -> list[tuple[str, bool]]:
    """Return one case per sampled check, plus the roster-coverage case."""
    project = root.joinpath(*_PROJECT)
    verbs = _verbs(project)
    samples = _samples(project)
    kinds = {check.partition(":")[0] for check in samples}
    cases = [("every sampled kind has a declared verb", kinds <= verbs.keys())]
    for check in samples:
        if check.partition(":")[0] not in verbs:
            continue
        got = _as_paperkit(verbs, check, project)
        want = witness_run.verdict(check, root)[0]
        sys.stdout.write(f"  {check[:60]}: verb={got} runner={want}\n")
        cases.append((f"the verb for {check[:50]!r} exits as the runner does", got == want))
    return cases


def selftest(root: Path) -> int:
    """Run every case, reporting failures by name, and return an exit code."""
    cases = _cases(root)
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"witness-verbs selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


def main(argv: list[str]) -> int:
    """Resolve the tree from the working directory, refusing when it holds no ledger project."""
    if len(argv) > 1 and "--selftest" not in argv:
        return 1
    root = Path.cwd()
    if not root.joinpath(*_PROJECT, "paper.toml").is_file():
        sys.stderr.write(f"witness-verbs selftest: no ledger project under {root}\n")
        return 2
    return selftest(root)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main(sys.argv))
