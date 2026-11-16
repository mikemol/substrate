# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""module_path / module_file / agda_root_from — the path<->module conversion.

69 inline conversions existed across ~24 files with NO canonical helper, which is why
"adopt the shared module" was never actionable for this class.  The suffix strip alone
was spelled three ways (`[:-5]` 22x, `[:-len(".agda")]` 23x, `with_suffix` 5x).

Each test docstring names the `Scenario:` in features/agda_text_invariant_0_helpers.feature
that it implements; `scripts/check_feature_coverage.py` fails on any scenario with no
implementing test.

⚑⚑ CONVERTED FROM `unittest.TestCase` TO PLAIN pytest FUNCTIONS UNDER Ⓝ73″
⟡the-tests-seam.  `PT009` refuses `self.assertEqual` in a new file while
`"tests/*" = ["S101"]` admits bare `assert` here, so the unittest idiom was the
population actually being pushed.

⚑ `subTest` BECAME `@pytest.mark.parametrize`, WHICH IS THE ONE PLACE THE CASE COUNT
MOVES.  The root-spelling case ran three sub-cases inside ONE test; parametrize makes
them three COLLECTED tests.  pytest reported the unittest form as "1 passed, 3 subtests
passed" — the subtests were always there and were never in the total.  Named here because
an unexplained count change is the denominator-loss shape this repo ratchets against: the
suite goes 52 → 54 cases with no case added and none lost, because two sub-cases were
promoted into the denominator that already ran them.

⚑ `self.skipTest` IS GONE ENTIRELY, NOT TRANSLATED.  The three tempdir cases skipped
nothing — they built their own fixture with `tempfile.TemporaryDirectory` and always ran.
`tmp_path` is that same fixture, supplied and cleaned by pytest.  ⚑ THE PATHS ARE STILL
PASSED AS `str`: `agda_files` and `agda_root_from` take `str` at their declared signature,
and widening a call site to satisfy a fixture's convenience would be the test dictating
the API.

⚑ `os.path` IS GONE TOO, AND THAT IS THE `PTH` FAMILY RATHER THAN TASTE.  `os.path.join`
and `os.path.basename` are both refused tree-wide in favour of `Path`; the one assertion
that compared against a joined path now builds the expected value with `Path`, which also
makes the platform separator the library's problem rather than the test's.

⚑ THE `Scenario:` LINES SIT BELOW EACH SUMMARY LINE.  `D400`/`D415` require a first
docstring line ending in a period, while `gherkin_scan` captures to the closing quotes —
so a period on the `Scenario:` line becomes part of the scenario NAME and breaks the
match against `features/`.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from agda_lex import agda_files, agda_root_from, module_file, module_path

from tests import corpus

# ⚑ THE THREE SPELLINGS A CALLER MIGHT USE FOR ONE ROOT.  Named as data so the claim —
# that the root is NORMALIZED, so a caller's spelling cannot change the answer — is
# readable without executing the loop.
_ROOT_SPELLINGS = ("agda", "./agda", "agda/")

_HEADER = "module M where\n"


def _write(path: Path) -> None:
    """Create one minimal Agda source at `path`, parents included."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_HEADER, encoding="utf-8")


def test_strips_root_and_suffix() -> None:
    """A path under the agda root becomes its dotted module name.

    Scenario: a path under the agda root becomes its dotted module name
    """
    assert module_path(corpus.PATH_UNDER_ROOT, "agda") == corpus.MODULE_UNDER_ROOT


def test_pure_root_is_an_argument() -> None:
    """The root is supplied by the caller, never discovered.

    Scenario: the root is an argument, never a global or a cwd

    ⚑ A `root=` DEFAULT was rejected: it relocates the disagreement into 69 call
    sites, each still deciding.  Computing the root from `__file__` was also
    rejected: installed from a package index the library lands in site-packages,
    nowhere near the tree, and every path silently comes out wrong.
    """
    assert module_path(corpus.PATH_ABSOLUTE, corpus.ROOT_ABSOLUTE) == corpus.MODULE_UNDER_ROOT


@pytest.mark.parametrize("root", _ROOT_SPELLINGS)
def test_root_spelling_does_not_change_the_answer(root: str) -> None:
    """A caller's spelling of the root is normalized away.

    Scenario: the root is normalized so a caller's spelling is irrelevant
    """
    assert module_path("agda/A/B.agda", root) == "A.B"


def test_empty_root_preserves_the_cwd_agda_contract() -> None:
    """The empty root leaves a module-relative path untouched.

    Scenario: a tool whose contract is cwd=agda/ passes the empty root

    `scope_fix.py` is documented "Run from agda/." and 20 of its conversions
    depend on this: with root="" the path is already module-relative.
    """
    assert module_path(corpus.PATH_ROOTLESS, "") == corpus.MODULE_UNDER_ROOT


def test_suffix_strip_is_by_name_not_a_magic_five() -> None:
    """The `.agda` suffix is stripped by name rather than by length.

    Scenario: the .agda suffix is stripped by name, not by a magic constant

    `[:-5]` is a magic constant that silently truncates the NAME if the extension
    ever changes; 22 sites spelled it that way.
    """
    assert module_path("agda/A/B.agda", "agda") == "A.B"


def test_non_agda_path_is_not_truncated() -> None:
    """A path that is not `.agda` keeps its whole final segment.

    Scenario: a path that is not .agda keeps its full final segment

    The `[:-5]` copies would silently eat five characters of a real name here.
    """
    assert module_path("agda/A/Bcdef", "agda") == "A.Bcdef"


def test_module_file_is_the_inverse() -> None:
    """`module_file` and `module_path` round-trip.

    Scenario: module_file and module_path round-trip
    """
    assert (
        module_path(module_file(corpus.MODULE_UNDER_ROOT, "agda"), "agda")
        == corpus.MODULE_UNDER_ROOT
    )


def test_module_file_uses_the_declared_suffix() -> None:
    """`module_file` appends `.agda` under the given root.

    Scenario: module_file appends the .agda suffix under the given root
    """
    assert module_file("A.B", "agda") == str(Path("agda") / "A" / "B.agda")


def test_excludes_build_by_default(tmp_path: Path) -> None:
    """The enumeration authority skips `_build` unless asked for it.

    Scenario: the enumerator excludes _build by default

    ⚑ THE ARMED HAZARD.  41 of 59 enumeration sites have no `_build` filter, which
    is harmless only because `agda/_build/` holds 2762 `.agdai` and zero `.agda`
    TODAY.  The agreement at 2764 is luck.  This test fails the moment a `.agda`
    appears under `_build` AND a caller has not adopted the authority — which is the
    signal that was missing when the gates and the analyses silently diverged.
    """
    real = tmp_path / "Substrate" / "Real.agda"
    stray = tmp_path / "_build" / "2.8.0" / "Generated.agda"
    for p in (real, stray):
        _write(p)
    assert agda_files(str(tmp_path)) == [str(real)]
    assert str(stray) in agda_files(str(tmp_path), include_build=True)


def test_root_is_a_parameter_not_a_global(tmp_path: Path) -> None:
    """A subdirectory-scoped caller narrows the enumeration by its root.

    Scenario: a subdirectory-scoped caller passes a narrower root

    Scoping is a PARAMETER of the canonical derivation, not a reason to hand-roll a
    walk — that is what keeps a rederivation census honest instead of exemption-ridden.
    """
    sub = tmp_path / "Sub"
    top = tmp_path / "Top.agda"
    deep = sub / "Deep.agda"
    for p in (top, deep):
        _write(p)
    # sorted, so `Sub/Deep.agda` precedes `Top.agda` — do not assert walk order
    assert agda_files(str(tmp_path)) == sorted([str(top), str(deep)])
    assert agda_files(str(sub)) == [str(deep)]


def test_sorted_so_two_callers_agree_on_order(tmp_path: Path) -> None:
    """The enumeration authority returns a sorted list.

    Scenario: the enumerator returns a sorted list

    One of the four same-named `agda_files()` sorted and another did not, so two
    "reuses" of the same name produced different orderings.
    """
    for n in ("c.agda", "a.agda", "b.agda"):
        _write(tmp_path / n)
    got = [Path(p).name for p in agda_files(str(tmp_path))]
    assert got == ["a.agda", "b.agda", "c.agda"]


def test_finds_the_root_by_walking_up(tmp_path: Path) -> None:
    """The agda root is discovered by walking up from a start path.

    Scenario: the agda root is discovered by walking up from a start path
    """
    start = tmp_path / "agda" / "Substrate" / "Deep" / "Deeper"
    start.mkdir(parents=True)
    assert agda_root_from(str(start)) == str(tmp_path / "agda")


def test_returns_none_rather_than_guessing(tmp_path: Path) -> None:
    """With no agda tree above it, the root search returns None.

    Scenario: with no agda tree above it, the root search returns None

    Returning a plausible-but-wrong root is the failure mode this avoids: 8 sites
    had `except OSError: return False`, so a wrong cwd yielded a WRONG ANSWER
    silently rather than raising.
    """
    assert agda_root_from(str(tmp_path)) is None
