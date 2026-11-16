#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.worklist_paths`: one derived root, with the parameterised form agreeing.

⚑⚑ THE DERIVATION ARM IS THE WHOLE POINT, AND IT IS AN IDENTITY CHECK RATHER THAN AN EQUALITY ONE.
Asserting that `ROOT` merely EQUALS `corpus.ROOT` would pass on a module that re-derived the root
from its own `__file__` — which is exactly the superseded spelling, and which agrees today by
coincidence because both files sit one level under the same tree. The two disagree the moment
either file moves, and the disagreement surfaces as a path that does not exist rather than as a
conflict anyone can see. So the case pins that it is the SAME OBJECT.

⚑⚑ THE PARAMETERISED FORM IS CHECKED AGAINST THE CONSTANTS, NOT AGAINST A SECOND HAND-WRITTEN
PATH. A case that spelled `root / "catalog" / "worklist"` itself would agree with a stale copy of
the layout and report the copy rather than the module — the same duplication the module avoids by
deriving one from the other.

⚑ NO CASE TOUCHES THE FILESYSTEM, AND THAT IS AN ASSERTION THIS SUITE MAKES RATHER THAN A HABIT IT
KEEPS. The claim of the module is that locating the worklist is a PURE fact about the tree, so the
foreign-root arm drives a directory that does not exist and expects an answer anyway; a module that
had quietly acquired an `is_dir()` check would fail there and nowhere else.
"""

from __future__ import annotations

import sys
from pathlib import Path

from mikemol.witness import witness_family

from substrate import corpus, suite_emit, worklist_paths


def the_root_is_the_corpus_root_itself(out: list[str]) -> int:
    """Check that `ROOT` IS `corpus.ROOT`, not a value that happens to match it.

    ⚑ IDENTITY, NOT EQUALITY — see the module note. This is the arm the superseded hand-rolled
    `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` fails while still producing the
    right string.
    """
    if worklist_paths.ROOT is not corpus.ROOT:
        out.append(f"selftest: ROOT is {worklist_paths.ROOT!r}, not corpus.ROOT")
        return 1
    return 0


def the_project_and_library_sit_under_the_root(out: list[str]) -> int:
    """Check that both constants are built from `ROOT` rather than anchored anywhere else.

    ⚑ A CONSTANT ANCHORED TO AN ABSOLUTE PATH would satisfy every other arm here while pointing
    outside the checkout entirely, which is the failure a hardcoded `/home/...` introduces.
    """
    bad = 0
    for name, value in (("PROJECT", worklist_paths.PROJECT), ("LIBRARY", worklist_paths.LIBRARY)):
        if worklist_paths.ROOT not in value.parents:
            out.append(f"selftest: {name} is {value!r}, not under ROOT")
            bad += 1
    return bad


def the_project_and_library_are_distinct_siblings(out: list[str]) -> int:
    """Check that the two catalogs are different directories sharing one parent.

    ⚑ WITHOUT THIS, A MODULE THAT BOUND BOTH NAMES TO THE SAME PATH would pass the containment arm
    above. The library and the project are separate inputs to the gate — the warrants resolve
    against one and the items live in the other — so collapsing them would make every warrant
    lookup silently search the wrong tree.
    """
    bad = 0
    if worklist_paths.PROJECT == worklist_paths.LIBRARY:
        out.append("selftest: PROJECT and LIBRARY name the same directory")
        bad += 1
    if worklist_paths.PROJECT.parent != worklist_paths.LIBRARY.parent:
        out.append("selftest: PROJECT and LIBRARY are not siblings")
        bad += 1
    return bad


def the_parameterised_form_reproduces_the_constants(out: list[str]) -> int:
    """Check that `project_for(ROOT)` and `library_for(ROOT)` return the module constants.

    ⚑ THIS IS WHAT TIES THE TWO SPELLINGS TOGETHER. The constants exist for the common case and the
    functions for a foreign checkout; if they could disagree, a caller measuring a worktree would
    get a different layout from a caller measuring the live tree, and neither would say so.
    """
    bad = 0
    if worklist_paths.project_for(worklist_paths.ROOT) != worklist_paths.PROJECT:
        out.append("selftest: project_for(ROOT) does not reproduce PROJECT")
        bad += 1
    if worklist_paths.library_for(worklist_paths.ROOT) != worklist_paths.LIBRARY:
        out.append("selftest: library_for(ROOT) does not reproduce LIBRARY")
        bad += 1
    return bad


def a_foreign_root_is_answered_without_touching_the_disk(out: list[str]) -> int:
    """Check that a root which does not exist still resolves, and relative to ITSELF.

    ⚑⚑ THIS IS THE PURITY ARM, AND IT IS DRIVEN WITH A DIRECTORY THAT IS NOT THERE ON PURPOSE. A
    module that had acquired an existence check — or that ignored its argument and returned the
    live constant — fails here and passes everything else. The second half matters as much as the
    first: returning `PROJECT` for a foreign root is the "ignores its argument" defect, which a
    case asserting only "it did not raise" would miss.
    """
    foreign = Path("/nonexistent-checkout-for-a-case")
    bad = 0
    got = worklist_paths.project_for(foreign)
    if foreign not in got.parents:
        out.append(f"selftest: project_for(foreign) returned {got!r}, not under the foreign root")
        bad += 1
    if got == worklist_paths.PROJECT:
        out.append("selftest: project_for ignored its argument and returned the live PROJECT")
        bad += 1
    return bad


def the_two_layouts_differ_only_in_their_leaf(out: list[str]) -> int:
    """Check that project and library are reached the same way under any root.

    ⚑ THE POSITIVE CONTROL FOR THE FOREIGN-ROOT ARM. Without it, a `library_for` that returned its
    argument unchanged would satisfy the containment check above by vacuity, since a path is not
    among its own parents.
    """
    foreign = Path("/nonexistent-checkout-for-a-case")
    project = worklist_paths.project_for(foreign)
    library = worklist_paths.library_for(foreign)
    if project.parent != library.parent or project == library:
        out.append(f"selftest: the foreign layout is {project!r} beside {library!r}")
        return 1
    return 0


FAMILY = witness_family.of(
    key="worklist_paths",
    apex="the worklist path vocabulary derives every constant from the one corpus root rather "
    "than re-computing it, keeps project and library as distinct siblings, and answers a "
    "foreign root purely — relative to that root and without consulting the filesystem",
    subject="the path vocabulary `substrate.worklist_paths` declares, resolved offline",
    members=(
        witness_family.Member(
            name="the_root_is_the_corpus_root_itself",
            claim="ROOT is corpus.ROOT, not a value that happens to match it",
        ),
        witness_family.Member(
            name="the_project_and_library_sit_under_the_root",
            claim="both constants are built from ROOT rather than anchored elsewhere",
            cases=2,
        ),
        witness_family.Member(
            name="the_project_and_library_are_distinct_siblings",
            claim="the two catalogs are different directories sharing one parent",
            cases=2,
        ),
        witness_family.Member(
            name="the_parameterised_form_reproduces_the_constants",
            claim="project_for and library_for at ROOT return the module constants",
            cases=2,
        ),
        witness_family.Member(
            name="a_foreign_root_is_answered_without_touching_the_disk",
            claim="a root that does not exist resolves, and relative to itself",
            cases=2,
        ),
        witness_family.Member(
            name="the_two_layouts_differ_only_in_their_leaf",
            claim="project and library are reached the same way under any root",
            premises=("a_foreign_root_is_answered_without_touching_the_disk",),
        ),
    ),
)

_ARMS = (
    the_root_is_the_corpus_root_itself,
    the_project_and_library_sit_under_the_root,
    the_project_and_library_are_distinct_siblings,
    the_parameterised_form_reproduces_the_constants,
    a_foreign_root_is_answered_without_touching_the_disk,
    the_two_layouts_differ_only_in_their_leaf,
)

_CASE_COUNT = FAMILY.count

_SELF_KEY = "substrate/worklist_paths_selftest.py"


def selftest() -> int:
    """Run every arm, report by typed record, and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_SELF_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
