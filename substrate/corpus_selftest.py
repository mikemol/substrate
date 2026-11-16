#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.corpus`: refusal, component matching, root discovery, order.

⚑ THE ARMS ARE SEPARATE FUNCTIONS BECAUSE THE GATE SAID SO. One `_cases` holding all of them
came back `C901` at complexity 12; they test genuinely different properties, and reading them
as one function was the same too-much-in-one-place the module under test was split for.

⚑⚑ AND THE AGREEMENT CHECK IS A FUNCTION TAKING THE PRIOR IMPLEMENTATION, NOT A CASE.
Set-equality against what `substrate.corpus` replaces is the check that matters most: a
population differing by one directory changes every census built on it, SILENTLY, since a
smaller corpus reports fewer findings and that reads as progress. `agreement` performs it;
the CALLER supplies the enumerator to compare against.

⚑⚑⚑ NO CALLER CAN LIVE IN A CHECKED FILE, AND FIVE SPELLINGS ESTABLISHED IT RATHER THAN ONE
GUESS. `scratch/` is not a package, so reaching `_pycodemod_core.py_files` yields `Any` and
it propagates into whatever holds it. Tried, each refused: a plain `import` inside the arm; a
helper returning `Callable[[str], object]`; an `isinstance` narrowing on the result; the
reach confined to `__main__`; `importlib.import_module` plus a defaulted `getattr` (the
module object is typed, but `getattr` on a `ModuleType` returns `Any` by declaration, so the
`Any` returns with it).

⚑ THAT IS A PROPERTY OF THE PACKAGING, NOT OF THIS FILE — the ⟡package-jea seam, at the one
place where it costs a real check rather than an annotation. The comparison was run once by
hand against this module's landing and its result belongs to that commit; it is not asserted
here, because nothing here can re-run it. A coverage gap with a named cause and a known
repair, stated rather than quietly absent.

⚑⚑ THE POPULATION ARM WAS AN UNSPLIT WITNESS FAMILY, AND ITS OWN DOCSTRING SAID SO. It
asserted three facts under one name while arguing two of them as distinct claims in prose —
so the names and the arguments were already being written, with nowhere to put them. It is
now three arms; `FAMILY` below declares them, and the positive control is named as a PREMISE
of the two members it protects rather than as a paragraph hoping to be read.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from mikemol.witness import witness_family

from substrate import corpus

if TYPE_CHECKING:
    from collections.abc import Callable

# Paths that merely CONTAIN a skip word and must survive component matching.
_KEEP = ("rebuild", "buildtools", "prebuild/inner")

# Paths that are genuinely generated output or vendored code.
_DROP = (
    "build",
    "dist/wheel",
    "a/__pycache__/b",
    "bazel-bin",
    "bazel-substrate",
    ".venv/lib",
    "x/site-packages/y",
)

# The trees an agreement report compares over.
_SUBJECTS = ("scripts", "substrate", "tests", "jea", "catalog")


def refusal(out: list[str]) -> int:
    """Check that an unresolvable root raises, naming what was asked for.

    ⚑ SILENTLY RETURNING THE DEFAULT CORPUS IS THE WHOLE BUG `resolve_root` RECORDS — a peer
    nearly published substrate's census as their own repo's.
    """
    try:
        corpus.resolve_root("no-such-directory-anywhere")
    except corpus.PopulationError as e:
        if "no-such-directory-anywhere" in str(e):
            return 0
        out.append("selftest: the refusal does not name what was requested")
        return 1
    out.append("selftest: an unresolvable root did not raise")
    return 1


def component_match(out: list[str]) -> int:
    """Check that the exclusion rule matches whole components, never substrings.

    ⚑ `"build" in rel` would also eat `rebuild/` and `buildtools/` — the class of bug this
    repo already paid for with a hand-written regex whose `.` matched any character.
    """
    bad = 0
    for keep in _KEEP:
        if corpus.excluded(Path(keep)):
            out.append(f"selftest: {keep!r} was excluded by a substring match")
            bad += 1
    for drop in _DROP:
        if not corpus.excluded(Path(drop)):
            out.append(f"selftest: {drop!r} is outside the corpus and was admitted")
            bad += 1
    return bad


def root_vocabulary(out: list[str]) -> int:
    """Check that root discovery uses the same skip vocabulary as the walk.

    ⚑ IT ONCE DID NOT — a generated tree that is a TOP-LEVEL entry becomes its own root, so
    the relative check never sees its name and the whole tree is admitted. Measured on
    paperkit: `bazel-bin/` is a top-level symlink, and the filter was installed and doing
    nothing.
    """
    bad = 0
    discovered = corpus.roots()
    for name in discovered:
        if name in corpus.SKIP_DIRS or name in corpus.GENERATED_DIRS:
            out.append(f"selftest: {name!r} is skipped yet was discovered as a root")
            bad += 1
    if "scripts" not in discovered:
        out.append(f"selftest: the corpus does not contain scripts/: {discovered}")
        bad += 1
    return bad


def the_walk_of_its_own_package_is_not_empty(out: list[str]) -> int:
    """Check that walking this package returns at least one file.

    ⚑ THE POSITIVE CONTROL FOR EVERY OTHER CLAIM ABOUT THE POPULATION. Every exclusion in this
    module is a way to return FEWER files, and an over-eager one returns zero — which reads as
    a clean tree rather than as a broken walk. Sortedness and membership are both checks on a
    list's CONTENTS, and the empty list passes sortedness vacuously, so without this arm an
    exclusion that ate the whole package would leave one sibling green and only the other red.
    """
    if not corpus.py_files("substrate"):
        out.append("selftest: the walk found no files in its own package")
        return 1
    return 0


def the_population_is_returned_sorted(out: list[str]) -> int:
    """Check that `py_files` hands its population back in sorted order.

    ⚑ THE ORDER IS PAID FOR. A caller that re-sorts defensively is one that was not told; a
    caller that does not is one depending on luck. Standing as its own arm is what makes the
    guarantee something a caller can CITE rather than observe and hope.
    """
    got = corpus.py_files("substrate")
    if got != sorted(got):
        out.append("selftest: py_files returned an unsorted population")
        return 1
    return 0


def the_walk_finds_the_module_under_test(out: list[str]) -> int:
    """Check that the population of `substrate/` contains `corpus.py` itself.

    ⚑ A NAMED MEMBER IS WHAT SEPARATES A WALK FROM A LIST. Non-emptiness says the walk returned
    something; naming a file this suite KNOWS is in the tree says it returned the right
    something. `corpus.py` is the module under test, so its presence is the one membership fact
    this suite cannot be wrong about — which is what makes it usable as an assertion rather
    than a fixture that drifts with the tree.
    """
    got = corpus.py_files("substrate")
    if not any(p.endswith("corpus.py") for p in got):
        out.append("selftest: the walk did not find the module under test")
        return 1
    return 0


def agreement(prior: Callable[[str], list[str]]) -> list[str]:
    """Compare this population against a prior enumerator's, tree by tree.

    ⚑⚑ THE CHECK THAT CANNOT BE A CASE, MADE RUNNABLE ANYWAY. `substrate.corpus`
    reimplements a walk 71 call sites depend on, three of them in other tools and one in a
    pre-commit gate. Set-equality against what it replaces is the strongest available
    evidence the rewrite preserved the population.

    ⚑ IT CANNOT BE A SELFTEST CASE, AND THE REASON IS ⟡package-jea AT ITS SHARPEST.
    `scratch/` is not a package, so `_pycodemod_core.py_files` is `Any` at the ATTRIBUTE
    ACCESS — before any narrowing can run. Three successive attempts to wall it (a
    `Callable` return from a helper, an `isinstance` narrowing on the result, a `callable()`
    guard) each still tripped `Expression has type "Any"` on the access itself.

    ⚑ SO THE CALLER SUPPLIES THE PRIOR IMPLEMENTATION AND WEARS THAT COST. Declaring the
    parameter as the callable it must be types everything downstream of it; reaching into
    `scratch/` stays something this module refuses to make routine. When `scratch/` is
    retired, this grows a default and becomes a case.

    ⚑ AND IT IS A CAPABILITY, NOT A ONE-OFF. Every module cut out of the `scratch/` cluster
    faces this same question, and answering it with a throwaway script is the judgement
    happening in the turn — which is what the standing rule forbids.
    """
    lines: list[str] = []
    for label in _SUBJECTS:
        got = set(corpus.py_files(label))
        want = set(prior(label))
        mark = "ok  " if want == got else "DIFF"
        lines.append(f"  {mark} {label:12} prior={len(want):5}  corpus={len(got):5}")
        lines.extend(f"       only-prior: {p}" for p in sorted(want - got)[:5])
        lines.extend(f"       only-corpus: {p}" for p in sorted(got - want)[:5])
    return lines


# ⚑⚑ THE FAMILY IS THE ROSTER MADE READABLE, AND THE PREMISE EDGES ARE WHY IT IS HERE RATHER
# THAN IN A COMMENT. `the_walk_of_its_own_package_is_not_empty` exists to keep its two siblings
# honest; stated in prose, deleting it would leave them green and say nothing. Named as a
# premise, the edge is something `dangling_premises()` can check.
FAMILY = witness_family.of(
    key="corpus",
    apex="the corpus walk names its own population: what it refuses, what it excludes, "
    "what it discovers, and in what order",
    subject="the trees `substrate.corpus` enumerates",
    members=(
        witness_family.Member(
            name="refusal",
            claim="an unresolvable root raises, naming what was asked for",
        ),
        witness_family.Member(
            name="component_match",
            claim="the exclusion rule matches whole path components, never substrings",
            cases=len(_KEEP) + len(_DROP),
        ),
        witness_family.Member(
            name="root_vocabulary",
            claim="root discovery uses the same skip vocabulary as the walk",
            cases=2,
        ),
        witness_family.Member(
            name="the_walk_of_its_own_package_is_not_empty",
            claim="walking this package returns at least one file",
        ),
        witness_family.Member(
            name="the_population_is_returned_sorted",
            claim="py_files hands its population back in sorted order",
            premises=("the_walk_of_its_own_package_is_not_empty",),
        ),
        witness_family.Member(
            name="the_walk_finds_the_module_under_test",
            claim="the population of substrate/ contains corpus.py itself",
            premises=("the_walk_of_its_own_package_is_not_empty",),
        ),
    ),
)

_ARMS = (
    refusal,
    component_match,
    root_vocabulary,
    the_walk_of_its_own_package_is_not_empty,
    the_population_is_returned_sorted,
    the_walk_finds_the_module_under_test,
)

# ⚑ DERIVED FROM THE FAMILY, NOT HAND-SUMMED. The total is the invariant that makes the split
# auditable: a count that moved while only names changed is a dropped or invented assertion.
_CASE_COUNT = FAMILY.count


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"corpus selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"corpus selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE — see `baseline_io`'s
# note (⟡selftest-discovery). Every suite written into this package during the migration had
# the same gap: it ran correctly and the runner never looked at it.
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
