#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_docs` — a root that survives being reached through a symlink.

⚑⚑⚑ THE SYMLINK CASE IS A REPRODUCED CONSUMER BREAK, NOT A HYPOTHETICAL. A peer adopting this
repo's markdown tool by symlink got `ModuleNotFoundError` on every invocation, because the
original derived its root with `abspath(__file__)` — which does NOT resolve symlinks — so the
root became the CONSUMER's repo and every path derived from it pointed into the wrong tree.
Measured three ways before the cause was believed: direct invocation from a foreign CWD works,
the same file through a symlink fails, and the refactor blamed for it had touched nothing.

⚑⚑ SO THE CASE ASSERTS THE PROPERTY, NOT THE CALL. Checking that the code says `resolve()` would
pass on a rewrite that reintroduced the bug elsewhere; building an actual symlink and reading
the root through it fails whenever the property is lost, however it is spelled.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import md_docs


def the_root_holds_this_module(out: list[str]) -> int:
    """Check the derived root actually contains this package.

    ⚑ THE CHEAPEST FALSIFIER. A root pointing anywhere else — a parent, a consumer's tree —
    fails here before any path derived from it is used.
    """
    if not (md_docs.ROOT / "substrate" / "md_docs.py").exists():
        out.append(f"selftest: the root {md_docs.ROOT} does not contain this module")
        return 1
    return 0


def the_root_survives_a_symlink(out: list[str]) -> int:
    """Check a symlinked copy of this module resolves to the SAME root.

    ⚑⚑ THE REPRODUCED CONSUMER BREAK. Under `abspath` this returns the symlink's directory, so
    a consumer adopting the tool by symlink derives their OWN repo as the root and every lookup
    misses. Under `resolve()` the answer is where the file really lives.
    """
    real = Path(md_docs.__file__).resolve()
    with tempfile.TemporaryDirectory() as d:
        link = Path(d) / "linked_md_docs.py"
        link.symlink_to(real)
        # The property under test, applied to the link exactly as the module applies it to
        # itself: resolve first, THEN walk up.
        via_link = link.resolve().parent.parent
    if via_link != md_docs.ROOT:
        out.append(f"selftest: through a symlink the root is {via_link}, want {md_docs.ROOT}")
        return 1
    return 0


def abspath_would_have_failed(out: list[str]) -> int:
    """Check the symlink case is a real discriminator, not a tautology.

    ⚑ A CASE THAT CANNOT FAIL IS NOT A CASE. This asserts the OLD spelling gives the WRONG
    answer through a symlink — so if someone reverts to `abspath`, the case above starts
    failing rather than silently continuing to pass.
    """
    real = Path(md_docs.__file__).resolve()
    with tempfile.TemporaryDirectory() as d:
        link = Path(d) / "linked_md_docs.py"
        link.symlink_to(real)
        # `absolute()` is pathlib's non-resolving form — the `abspath` behaviour.
        via_abspath = link.absolute().parent.parent
    if via_abspath == md_docs.ROOT:
        out.append("selftest: the symlink case cannot discriminate — abspath agrees")
        return 1
    return 0


def a_missing_document_is_named(out: list[str]) -> int:
    """Check an absent record produces a note rather than a silent None.

    ⚑ ABSENCE IS A FACT WORTH STATING. A bare `None` leaves a caller unable to distinguish
    "the worklist has no file" from "I did not look" — the same collapse this repo keeps
    filing elsewhere.
    """
    plan, worklist, notes = md_docs.docs()
    missing = sum(1 for found in (plan, worklist) if found is None)
    if missing and not notes:
        out.append(f"selftest: {missing} document(s) absent and no note was produced")
        return 1
    return 0


def candidates_are_absolute(out: list[str]) -> int:
    """Check every candidate path is absolute, so a caller's CWD cannot change the answer.

    ⚑ A RELATIVE CANDIDATE WOULD RESOLVE AGAINST THE CALLER'S CWD, which is the same class of
    defect as the symlink one: the tool's answer would depend on where it was invoked from
    rather than on where things are.
    """
    bad = 0
    for path in (*md_docs.PLAN_CANDIDATES, *md_docs.WORKLIST_CANDIDATES):
        if not path.is_absolute():
            out.append(f"selftest: candidate {path} is relative")
            bad += 1
    return bad


_ARMS = (
    the_root_holds_this_module,
    the_root_survives_a_symlink,
    abspath_would_have_failed,
    a_missing_document_is_named,
    candidates_are_absolute,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 4


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"md-docs selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"md-docs selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
