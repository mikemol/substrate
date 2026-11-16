#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.walk_scope`: the three exclusion kinds, and the shadow it measures.

⚑⚑ EVERY ARM DRIVES A SYNTHETIC ROOT, NOT THE REAL TREE. A case asserting `.claude` is skipped
here would be a case about today's repo layout — it would pass for the wrong reason the day
somebody renames a directory, and FAIL for the wrong reason the day the corpus widens. The
property under test is the CLASSIFICATION, so the fixture is a root built to hold one of each
kind.

⚑⚑⚑ AND THE POSITIVE CONTROL IS THE ARM THAT MATTERS MOST, because every other arm here asserts
that something IS excluded — and a reader that excluded EVERYTHING would pass all of them while
reporting the entire tree as a blind spot. `a_walked_root_is_not_reported_as_skipped` is what
separates a scope reader from a broken one, and it is named as a premise of the three exclusion
arms rather than argued in a paragraph nobody can check.

⚑ THE ROOT-LEVEL FILE ARM IS A REGRESSION TEST FOR A HOLE THAT WAS NEVER NOTICED. `corpus.roots()`
yields directories, so a `.py` at the repo root is under no root; three such files are live in
this tree and in no census. If the corpus walk is ever fixed to reach them, this arm turns red —
which is correct: the scope reader must then stop reporting them as a shadow, and a silent
disagreement between the two is exactly what this whole item is about.

⚑⚑ THIS SUITE REPORTS BY TYPED RECORD (Ⓝ73 ⟡selftest-contract), THROUGH `suite_emit`. It is the
worked example for that item's cost question, and the answer it measured is that the conversion
is two lines ONCE THE EMITTER EXISTS — an import and a `return suite_emit.report(...)` — because
this package's suites already derive their own totals from a `witness_family`. What it cost
BEFORE the emitter existed was a whole module: `substrate/` had the record READER and no writer,
so every suite here failed the contract by default with nowhere to call.
"""

from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from mikemol.witness import witness_family

from substrate import corpus, suite_emit, walk_scope

# The fixture's shape: one taken root, one dotfile tree, one declared skip, one loose `.py`, and
# one loose non-Python file. ⚑ ONE OF EACH KIND PLUS ITS NEGATIVE CONTROL, so classification and
# the shadow are driven by a single tree.
_TREE = ("scripts/real.py", ".hidden/tool.py", "docs/page.py", "loose.py", "README.md")

# What the shadow must be over `_TREE` — every `.py` outside a taken root.
_SHADOW = frozenset({".hidden/tool.py", "docs/page.py", "loose.py"})

# The key this suite reports under. ⚑ THE REPO-RELATIVE PATH, which is what `suite_discovery`
# labels a suite with and therefore what the runner's per-suite ledger and reach baseline are
# keyed on — a record carrying a different spelling reads as a suite nobody discovered.
_KEY = "substrate/walk_scope_selftest.py"


def _build(root: Path) -> None:
    """Materialise the fixture tree under `root`."""
    for rel in _TREE:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("x = 1\n", encoding="utf-8")


def _kinds(root: Path) -> dict[str, str]:
    """Return `{name: kind}` for everything the scope reader excludes under `root`."""
    return {item.name: item.kind for item in walk_scope.skipped(root)}


def a_walked_root_is_not_reported_as_skipped(out: list[str]) -> int:
    """Check that a directory the corpus DOES walk is absent from the skipped set.

    ⚑⚑ THE POSITIVE CONTROL FOR EVERY OTHER ARM. Each sibling asserts that something IS
    excluded, and a reader that reported the whole root as excluded would satisfy all of them —
    while telling a census that its denominator bounds nothing. This is the arm that fails on
    that reader, and it is why the others can be read as claims about classification rather than
    as claims that the reader emits output at all.
    """
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _build(root)
        if "scripts" in _kinds(root):
            out.append("selftest: a walked root was reported as skipped")
            return 1
    return 0


def a_dotfile_directory_is_reported_with_its_own_kind(out: list[str]) -> int:
    """Check that a `.`-prefixed directory is `dotfile-dir`, not folded into a declared skip.

    ⚑ THE TWO ARE DIFFERENT NEXT ACTIONS, WHICH IS THE WHOLE REASON FOR THE SPLIT. A declared
    skip is a decision somebody made; a dotfile directory is swallowed by a blanket
    `startswith(".")` that nobody aimed at it — and one of them held a live EXE001 this walk
    could not see.
    """
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _build(root)
        got = _kinds(root).get(".hidden")
        if got != walk_scope.DOTFILE:
            out.append(f"selftest: .hidden classified {got!r}, want {walk_scope.DOTFILE!r}")
            return 1
    return 0


def a_declared_skip_is_reported_as_policy(out: list[str]) -> int:
    """Check that a directory in `corpus.SKIP_DIRS` is reported as a declared exclusion.

    ⚑ IT ASSERTS THE CLASSIFICATION AGAINST THE AUTHORITY, NOT AGAINST A LITERAL. The fixture
    uses `docs`, which this suite reads out of `corpus.SKIP_DIRS` rather than trusting — if that
    set ever drops it, this arm reports a fixture that no longer tests what it names.
    """
    bad = 0
    if "docs" not in corpus.SKIP_DIRS:
        out.append("selftest: the fixture's declared-skip directory is no longer declared")
        bad += 1
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _build(root)
        got = _kinds(root).get("docs")
        if got != walk_scope.DECLARED:
            out.append(f"selftest: docs classified {got!r}, want {walk_scope.DECLARED!r}")
            bad += 1
    return bad


def a_root_level_python_file_is_reported_as_a_hole(out: list[str]) -> int:
    """Check that a `.py` file at the root is reported, and a non-Python file is not.

    ⚑⚑ BOTH HALVES, BECAUSE THE INTERESTING CASE IS THE ONE WITH NO NAME. `corpus.roots()`
    yields directories only, so a loose `.py` is in no root at all — a hole rather than a
    policy. Reporting every loose file would bury it under `README.md` and every other root
    artefact, so the reader is scoped to Python and this arm pins both directions.
    """
    bad = 0
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _build(root)
        kinds = _kinds(root)
        if kinds.get("loose.py") != walk_scope.LOOSE_FILE:
            out.append(f"selftest: loose.py classified {kinds.get('loose.py')!r}")
            bad += 1
        if "README.md" in kinds:
            out.append("selftest: a non-Python root file was reported as a shadow")
            bad += 1
    return bad


def the_shadow_counts_files_not_directories(out: list[str]) -> int:
    """Check that `unwalked_python` returns the `.py` files, not the excluded entries.

    ⚑ A COUNT OF SKIPPED DIRECTORIES IS NOT A COUNT OF UNSEEN CODE. `docs/` excluded is
    unremarkable at zero modules and a real gap at forty, and the directory name cannot say
    which — so the reader must walk them, and this arm is what holds it to that.
    """
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _build(root)
        got = frozenset(walk_scope.unwalked_python(root))
        if got != _SHADOW:
            out.append(f"selftest: the shadow is {sorted(got)}, want {sorted(_SHADOW)}")
            return 1
    return 0


def the_render_names_every_excluded_entry(out: list[str]) -> int:
    """Check that the rendered statement names each entry AND why it was excluded.

    ⚑⚑ THIS IS THE ITEM'S ACCEPTANCE, MADE INTO A CASE. Ⓝ72c asks that *a reader can tell what
    was NOT looked at, from the output, without reading the source* — so a render carrying only
    counts, or only names, would satisfy every other arm here and fail the requirement. Asserting
    that the prose reason travels with the name is what makes the acceptance checkable rather
    than a sentence in a commit message.
    """
    bad = 0
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _build(root)
        body = walk_scope.render(root)
        for name in (".hidden", "docs", "loose.py"):
            if name not in body:
                out.append(f"selftest: the render does not name {name!r}")
                bad += 1
        if "corpus.roots()" not in body:
            out.append("selftest: the render does not say WHY an entry was excluded")
            bad += 1
    return bad


def an_empty_root_renders_nothing(out: list[str]) -> int:
    """Check that a root with nothing excluded renders an empty statement, not a header.

    ⚑ A DISCLOSURE THAT FIRES WHEN THERE IS NOTHING TO DISCLOSE TEACHES A READER TO SKIP IT.
    The boundary line is only load-bearing if its presence means something; a `0 entr(ies)`
    header printed under every census is noise that the next reader learns to filter, taking the
    real ones with it.
    """
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir()
        (root / "scripts" / "a.py").write_text("x = 1\n", encoding="utf-8")
        if walk_scope.render(root):
            out.append("selftest: a root with nothing excluded still rendered a statement")
            return 1
    return 0


FAMILY = witness_family.of(
    key="walk_scope",
    apex="the corpus walk states its own boundary: which root entries it never visited, why "
    "each is outside the population, and how much Python that leaves unread",
    subject="the entries `substrate.walk_scope` reports as outside `corpus.roots()`",
    members=(
        witness_family.Member(
            name="a_walked_root_is_not_reported_as_skipped",
            claim="a directory the corpus does walk is absent from the skipped set",
        ),
        witness_family.Member(
            name="a_dotfile_directory_is_reported_with_its_own_kind",
            claim="a `.`-prefixed directory is dotfile-dir, not folded into a declared skip",
            premises=("a_walked_root_is_not_reported_as_skipped",),
        ),
        witness_family.Member(
            name="a_declared_skip_is_reported_as_policy",
            claim="a directory in corpus.SKIP_DIRS is reported as a deliberate exclusion",
            cases=2,
            premises=("a_walked_root_is_not_reported_as_skipped",),
        ),
        witness_family.Member(
            name="a_root_level_python_file_is_reported_as_a_hole",
            claim="a .py file at the root is reported and a non-Python root file is not",
            cases=2,
            premises=("a_walked_root_is_not_reported_as_skipped",),
        ),
        witness_family.Member(
            name="the_shadow_counts_files_not_directories",
            claim="unwalked_python returns the .py files, not the excluded entries",
        ),
        witness_family.Member(
            name="the_render_names_every_excluded_entry",
            claim="the rendered statement names each entry and why it was excluded",
            cases=4,
        ),
        witness_family.Member(
            name="an_empty_root_renders_nothing",
            claim="a root with nothing excluded renders an empty statement, not a header",
        ),
    ),
)

_ARMS = (
    a_walked_root_is_not_reported_as_skipped,
    a_dotfile_directory_is_reported_with_its_own_kind,
    a_declared_skip_is_reported_as_policy,
    a_root_level_python_file_is_reported_as_a_hole,
    the_shadow_counts_files_not_directories,
    the_render_names_every_excluded_entry,
    an_empty_root_renders_nothing,
)

# ⚑ DERIVED FROM THE FAMILY, NOT HAND-SUMMED — a total that moved while only names changed is a
# dropped or invented assertion.
_CASE_COUNT = FAMILY.count


def selftest() -> int:
    """Run every arm, report by TYPED RECORD, and return an exit code.

    ⚑⚑ THE VERDICT AND THE EXIT CODE COME FROM ONE PLACE (Ⓝ73 ⟡selftest-contract).
    `suite_emit.report` emits the record, prints the human line, and returns the code — so the
    numbers a consumer reads and the code `make` reads cannot disagree. The prose form this
    replaces computed the code in one branch and printed the counts in another, which is exactly
    where a suite can pass while reporting nothing readable.

    ⚑ FAILURE DETAIL STILL GOES TO STDERR, ahead of the record. The record says WHAT the result
    was; the arm messages say WHICH case, and mixing them into the machine-readable stream would
    put prose between a reader and the line it is scanning for.
    """
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
    return suite_emit.report(_KEY, _CASE_COUNT - failures, _CASE_COUNT)


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
