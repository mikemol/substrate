#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Compare a promoted module against the implementation it replaced.

⚑⚑ THE ONE QUESTION EVERY CUT OUT OF THE `scratch/` CLUSTER ASKS, AND IT HAD NO PROGRAM.
⟡corpus-repoint promoted `py_files` and `type_errors` into `substrate/`; the strongest
evidence a promotion is sound is that the new form returns what the old one did over the same
input. Answering that by hand — run both, eyeball two counts — is the judgement happening in
the turn. It recurs once per cut, so it is a capability, so it gets a program.

⚑⚑⚑ IT COMPARES ACROSS A SUBPROCESS, NOT ACROSS AN IMPORT, AND THAT IS THE WHOLE DESIGN.
`scratch/` is not a package, so importing from it yields `Any` and that `Any` PROPAGATES into
whatever holds it. Six spellings were tried and every one was refused identically: a plain
`import` in the arm; a helper returning `Callable[[str], object]`; an `isinstance` narrowing
on the result; the reach confined to `__main__`; `importlib.import_module` plus a defaulted
`getattr` (the module object is typed, but `getattr` on a `ModuleType` returns `Any` by
declaration); `vars(mod).get` (a module's `__dict__` is `dict[str, Any]`).

⚑⚑ AND A SEVENTH ATTEMPT ESTABLISHED THAT LOCATION DOES NOT HELP EITHER. The obvious
route-around was to put this in `scratch/`, where the surrounding files are already dirty so
the `Any` would cost nothing. It was written that way and REFUSED at 78 findings: the gate
applies to every NEW file regardless of directory, and only files that already exist are
grandfathered. There is no location where the reach is free.

⚑⚑⚑ AND ALL EIGHT OF THOSE ASKED THE WRONG QUESTION — CORRECTED BY THE OPERATOR (*"isn't this
what typing stubs are for?"*). Every attempt asked *how do I hide this `Any`*; none asked
*what is its type*. A `.pyi` supplies signatures independently of packaging, so an unpackaged
module CAN be imported with types — `stubs/check_scratch_independence.pyi` plus `mypy_path`
now types `ROOTS` as `list[str]` under `--strict`, verified by a control where the wrong
annotation must ERROR rather than pass as `Any`. `pyproject.toml` already stated the rule
("stub an untyped dep") four paragraphs above the setting that was missing.

⚑ SO THE SUBPROCESS IS NOW A CHOICE, NOT A NECESSITY, AND IT IS KEPT FOR A DIFFERENT REASON:
stubbing `_pycodemod_core` would mean declaring the surface of the module being RETIRED, which
is maintenance owed to a corpse. Comparing across a process boundary needs no stub, no
declaration, and nothing to delete later. Where the authority SURVIVES the migration — `ROOTS`
does — the stub is right; where it is being deleted, the subprocess is.

⚑ A SUBPROCESS BOUNDARY IS A `str` BOUNDARY. The prior implementation is invoked as a
program, its stdout is text, and text has a type. This is slower and cannot compare in-memory
structures — but the things worth comparing here are printable, and printing them is what the
prior tools already do.

⚑ A COMPARISON, NEVER A GATE. It reports; it does not rule. The original is the thing being
RETIRED, so enshrining its output as the authority would invert the migration: a promoted
module that FIXES a bug in its ancestor should differ, and that difference is a result to
read rather than a failure to refuse. Nothing in pre-commit calls this.

    promote_agree.py             # every arm
    promote_agree.py --corpus    # the population: substrate.corpus vs _pycodemod_core
    promote_agree.py --mypy      # the type census: substrate.mypy_census vs the gate
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from mikemol.corpus import suite_discovery, tree_root

from substrate import corpus, mypy_census, promoted

# How many differing items to name before summarising. A diff longer than this is a design
# disagreement rather than a discrepancy, and 400 lines does not help anyone read it.
_SHOW = 8

# ⚑ THE PRE-SPLIT SUITE DISCOVERY. `run_selftests.discover()` returns `(label, path)` pairs;
# only the labels are compared, because the paths are the same files by construction and a
# path difference would be a fact about where the walk started rather than what it admits.
_DISCOVER = (
    "import sys; sys.path.insert(0, 'scripts'); sys.path.insert(0, 'scratch'); "
    "import run_selftests as r; "
    "print('\\n'.join(sorted(lbl for lbl, _p in r.discover())))"
)


def _prior_suites() -> set[str] | None:
    """Run the pre-split suite discovery as a program and read back its population."""
    try:
        p = subprocess.run(
            [sys.executable, "-c", _DISCOVER],
            cwd=str(corpus.ROOT),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    return {ln for ln in p.stdout.splitlines() if ln}


def discovery_arm() -> list[str]:
    """Compare `substrate.suite_discovery` against the predicate it replaced.

    ⚑⚑ THIS ARM CANNOT LIVE IN THE SUITE IT CHECKS. Running the prior implementation needs an
    `S603` exemption, and a per-file exemption over a file that also holds unit cases grants
    it to both responsibilities. This module owns that exemption because running prior
    implementations is its ONE job — so every extraction's comparison lands here rather than
    each suite acquiring a subprocess.

    ⚑ AND THE POPULATION IS EXACTLY WHAT MUST NOT DRIFT. This predicate's every recorded
    failure was a population that silently SHRANK: three suites erased by requiring a local
    `_selftest` body, one by anchoring on the `__main__` idiom, two directories missed by a
    frozen roster. None showed as a failure — each showed as a smaller green total.
    """
    got = {label for label, _path in suite_discovery.discover(corpus.ROOT)}
    return rows(f"suite discovery ({len(got)} suite(s))", _prior_suites(), got)


# The gate's population, DERIVED from its authority (`substrate.promoted`).
#
# ⚑⚑ THIS WAS A HARDCODED `("scripts/", "jea/", "el-atlas/")`, JUSTIFIED BY A COMMENT SAYING
# THE AUTHORITY "CANNOT BE IMPORTED" — and that was wrong (operator: *"isn't this what typing
# stubs are for?"*). The premise held of the IMPLEMENTATION: `check_scratch_independence` is
# not in a package, so importing it yields `Any`, which `disallow_any_expr` propagates. The
# CONCLUSION did not follow — a `.pyi` types an unpackaged import.
#
# ⚑ SEVEN SPELLINGS WERE TRIED TO LAUNDER THAT `Any` FIRST, each asking *how do I hide this*
# rather than *what is its type*. A copied roster is the second-spelling class this repo has
# recorded over and over, and a duplication accepted because the fix looked impossible is
# worse than one accepted knowingly: nothing prompts a recheck.
#
# ⚑⚑ AND THE STUB ROUTE WAS THE SECOND-BEST FIX, MEASURED: importing through it took this
# module's closure **0 → 4,955**, because a stub types the IMPORT while the RUNTIME still
# executes it and drags the authority's 23-callee chain. ⟡roots-authority-cut moved the roster
# itself into a clean module, so the import is now both typed AND cheap — and the stub stays
# for what has not moved yet.
_GATE_POPULATION = tuple(f"{r}/" for r in promoted.POPULATION)

# A tree walk over the whole corpus is seconds, not minutes; this bounds a hang, not the work.
_TIMEOUT_S = 300

# ⚑ A FULL TYPE CENSUS TAKES MINUTES, AND THIS MUST EXCEED THE GATE'S OWN 900s MYPY TIMEOUT —
# otherwise a healthy slow run reports UNRUN, which is a fact about this bound reported as a
# fact about the census.
_CENSUS_TIMEOUT_S = 1800

# The trees the population arm compares over. `scratch` is included deliberately: it is the
# largest and least regular tree, so a boundary the rewrite moved shows up there first.
_TREES = ("scripts", "substrate", "tests", "jea", "catalog", "scratch")

# ⚑ THE PRIOR IMPLEMENTATION, INVOKED AS A PROGRAM. `-c` is the only way to reach a
# non-package module's function without importing it here, and this code is a module
# constant — never assembled from input — which keeps it a fixed invocation.
_ENUMERATE = (
    "import sys; sys.path.insert(0, 'scratch'); "
    "import _pycodemod_core as c; "
    "print('\\n'.join(c.py_files(sys.argv[1])))"
)

# ⚑ THE PRE-SPLIT CENSUS, COMPUTED THE WAY THE OLD GATE COMPUTED IT — `pycodemod.type_errors`
# over a population passed in, which is exactly what `check_mypy_ratchet.census()` called. The
# population comes from the PROMOTED roster so both arms answer the same question; scoping them
# differently would report a difference that is entirely about scope.
_PRIOR_CENSUS = (
    "import sys; sys.path.insert(0, 'scratch'); "
    "import _pycodemod_core as c, _pycodemod_census as z; "
    "rows = z.type_errors(c.py_files(*sys.argv[1:])) or {}; "
    "print('\\n'.join(sorted(k for k in rows if '::' in k)))"
)


def _rel(path: str) -> str:
    """Return a corpus path as repo-relative text.

    ⚑⚑⚑ THE `is_absolute()` GUARD READ AS PROTECTION AND GAVE NONE (gate-G257). A path from a
    BORROWING checkout is absolute — that is exactly the case that raises — so the guard admitted
    the failing input and excluded only the one shape that could never fail. Confirmed by
    execution: run from a peer's tree this raised on `summit/scripts/__init__.py`.

    ⚑ `tree_root.label` is tolerant in the direction that matters instead: outside the tree, the
    path comes back whole, so a foreign row is a row rather than a dead census.
    """
    return tree_root.of(corpus.ROOT).label(Path(path))


def _prior_population(tree: str) -> set[str] | None:
    """Run the pre-split enumerator as a program and read back its population."""
    try:
        p = subprocess.run(
            [sys.executable, "-c", _ENUMERATE, tree],
            cwd=str(corpus.ROOT),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    return {ln for ln in p.stdout.splitlines() if ln}


def _prior_census() -> set[str] | None:
    """Read the census keys the ratchet BASELINE holds.

    ⚑⚑ THE BASELINE IS THE AUTHORITY, AND THE GATE WAS ONLY ITS READER — a distinction the
    first cut of this function stated and then failed to act on. It ran
    `check_mypy_ratchet --list --dry-run` and argued the gate was *"the honest authority
    anyway"* because it *"prints exactly the keys its BASELINE holds"*. That sentence names
    the real authority in its own subordinate clause. Reading the file directly is the same
    comparison with one fewer indirection — and it does not require the retiring gate to
    exist.

    ⚑ WHICH MADE A RETIREMENT LOOK BLOCKED THAT WAS NOT. `check_mypy_ratchet` has no gate
    consumer since ⟡hook-repoint, and this call site was cited as a reason it could not be
    deleted (operator: *"These are all fixable"*). A dependency on a tool that exists only to
    print a file is a dependency on the file.

    ⚑⚑ AND A SECOND REWRITE READ THE BASELINE FILE INSTEAD, ON THE STRENGTH OF THAT CLAIM. It
    reported `prior=0 promoted=1144` — because the baseline is genuinely EMPTY (zero bytes,
    the zero-tolerance setting) while `--list` prints the LIVE census. The gate's own docstring
    said "baseline" and meant "census"; trusting it produced a comparison against nothing that
    LOOKED like a total divergence.

    ⚑ SO THE ARM WAS RIGHT ABOUT WHAT IT READ AND WRONG ABOUT WHY — the more dangerous shape,
    because a correct result resting on a false model survives until someone acts on the model.
    That happened one edit later, in this session.

    ⚑ WHAT IT COMPARES, STATED HONESTLY: the pre-split census is `pycodemod.type_errors` over
    a population; the promoted one is `substrate.mypy_census.type_errors` over the same
    population. Two CENSUS IMPLEMENTATIONS, not a gate against a ledger — so this calls the
    prior implementation directly, and does not need the retiring gate to exist.
    """
    try:
        p = subprocess.run(
            [sys.executable, "-c", _PRIOR_CENSUS, *promoted.POPULATION],
            cwd=str(corpus.ROOT),
            capture_output=True,
            text=True,
            timeout=_CENSUS_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if p.returncode != 0:
        return None
    return {ln for ln in p.stdout.splitlines() if "::" in ln}


def rows(label: str, prior: set[str] | None, promoted: set[str]) -> list[str]:
    """Render one comparison.

    ⚑ AN UNRUNNABLE ARM IS REPORTED AS UNRUNNABLE, NEVER AS AGREEMENT. Two absences are not
    a match, and calling them one is how a comparison certifies its own blind spot — the
    same defect `check_mypy_ratchet`'s unrunnable sentinel exists to prevent one layer down.
    """
    if prior is None:
        return [f"  UNRUN {label}: the prior implementation did not run"]
    if prior == promoted:
        return [f"  ok    {label}: {len(prior)} item(s), identical"]
    out = [f"  DIFF  {label}: prior={len(prior)} promoted={len(promoted)}"]
    out.extend(f"          only-prior: {k}" for k in sorted(prior - promoted)[:_SHOW])
    out.extend(f"          only-promoted: {k}" for k in sorted(promoted - prior)[:_SHOW])
    return out


def corpus_arm() -> list[str]:
    """Compare `substrate.corpus.py_files` against the enumeration it replaced.

    ⚑ THE POPULATION IS THE HIGHEST-STAKES COMPARISON HERE. `--calls py_files` measures 143
    calls across 72 refs, three of them in other tools and one in a pre-commit gate. A
    population differing by one directory changes every census built on it, SILENTLY — a
    smaller corpus reports fewer findings, and fewer findings reads as progress.
    """
    out: list[str] = []
    for tree in _TREES:
        out.extend(rows(f"population {tree}", _prior_population(tree), set(corpus.py_files(tree))))
    return out


def mypy_arm() -> list[str]:
    """Compare `substrate.mypy_census` against the census the gate publishes.

    ⚑ SCOPED TO THE GATE'S OWN POPULATION, NOT THE WHOLE CORPUS. Both sides must be asked the
    same question: the gate censuses `ROOTS + scripts`, so a corpus-wide run would report a
    difference that is entirely about scope. `substrate/` is deliberately NOT in that
    population yet — worth knowing, and why the row prints the scope it used.

    ⚑ AND KEYS, NOT MESSAGES. A baseline holds keys; two mypy runs can word the same finding
    differently while keying identically, so comparing messages reports churn the gate cannot
    see.
    """
    prior = _prior_census()
    if prior is None:
        return ["  UNRUN mypy census: the gate did not publish a census"]
    files = [f for f in corpus.py_files() if _rel(f).startswith(_GATE_POPULATION)]
    got = mypy_census.type_errors([_rel(f) for f in files])
    if got is None or mypy_census.UNRUNNABLE in got:
        return ["  UNRUN mypy census: the promoted census could not run"]
    scope = "/".join(p.rstrip("/") for p in _GATE_POPULATION)
    return rows(f"mypy census ({len(files)} file(s) over {scope})", prior, set(got))


_ARMS = (("--corpus", corpus_arm), ("--mypy", mypy_arm), ("--discovery", discovery_arm))


def main(argv: list[str]) -> int:
    """Run the requested arms; 1 if any differs or could not run."""
    wanted = [fn for flag, fn in _ARMS if flag in argv] or [fn for _f, fn in _ARMS]
    out: list[str] = []
    for fn in wanted:
        out.extend(fn())
    bad = [r for r in out if r.lstrip().startswith(("DIFF", "UNRUN"))]
    out.append(f"promote-agree: {len(out)} row(s), {len(bad)} differing")
    sys.stdout.write("\n".join(out) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
