# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""is_public_open — the predicate deciding whether a statement re-exports.

18 distinct predicates existed across ~41 files.  Only 2 used a lookaround; the other 16
spell it `\bpublic\b`, which matches `public` inside a COMMENT and as a RENAME TARGET.
One is weaker still: `"public" not in l`, a bare substring test that matches
`republication`.

These are the acceptance criteria for Phase B3 — the highest-risk conversions, because
four of the affected sites are on WRITE paths:
  * scope_fix.py:1706,:1960  — a re-export chain walker; a comment reads as live
  * split_lemmas.py:456      — it ATTACHES comment blocks to each leaf BY DESIGN, so
                               the false positive there is structural, not luck
  * split_upstream.py:32     — emits ` public` into generated source from the match

⚑⚑ CONVERTED FROM `unittest.TestCase` TO PLAIN pytest FUNCTIONS UNDER Ⓝ73″ ⟡the-tests-seam,
and the conversion resolves a LIVE REFUSAL rather than following a fashion.  `PT009`
refuses `self.assertEqual` in a new file; `"tests/*" = ["S101"]` admits bare `assert`
here and nowhere else.  The unittest idiom was the population actually being pushed.

⚑ THE ASSERTIONS ARE UNCHANGED IN CONTENT.  Each `assertTrue`/`assertFalse` became the
bare predicate it always was, and the DELTA assertions — the ones showing what the OLD
copy returns — are kept, because a test a reviewer can check without trusting its author
is the whole reason they were written.

⚑ THE `Scenario:` LINES SIT BELOW EACH SUMMARY LINE, and that placement is load-bearing
rather than stylistic.  `D400`/`D415` require a first docstring line ending in a period,
while `gherkin_scan`'s pattern captures to the closing quotes — so a period on the
`Scenario:` line becomes part of the scenario NAME and breaks the match against
`features/`.  The scan is `re.MULTILINE` and `D400` governs only the FIRST line.
"""

from __future__ import annotations

import re

from agda_lex import is_public_open

from tests import corpus

OLD_WORDBOUNDARY = re.compile(r"\bpublic\b")  # 16 of the 18 copies


def test_a_real_re_export() -> None:
    """An open whose tail is `public` re-exports.

    Scenario: an open with a public tail is a re-export
    """
    assert is_public_open("open import A using (x) public")


def test_public_after_a_using_clause() -> None:
    """A `public` trailing a using-clause is still a re-export.

    Scenario: public following a using clause is still a re-export

    Verbatim shape from S5/S5Fixpoint.agda:19 — the form where `public` trails the
    filter rather than the module name.
    """
    assert is_public_open(corpus.PUBLIC_AFTER_USING)


def test_public_in_a_comment_is_not_a_re_export() -> None:
    """The word `public` inside a comment does not re-export.

    Scenario: the word public in a comment is not a re-export
    """
    assert not is_public_open(corpus.PUBLIC_IN_COMMENT)
    # the delta: every \bpublic\b copy counts this as live
    assert OLD_WORDBOUNDARY.search(corpus.PUBLIC_IN_COMMENT)


def test_public_as_a_rename_target_is_not_a_re_export() -> None:
    """A `public` used as a renaming target does not re-export.

    Scenario: public as a renaming target is not a re-export
    """
    assert not is_public_open(corpus.PUBLIC_AS_RENAME_TARGET)


def test_substring_match_is_not_enough() -> None:
    """A word merely CONTAINING `public` does not re-export.

    Scenario: republication does not make an import a re-export

    `narrow_leaf_imports.py:35` uses `"public" not in l`, so this string disables
    the whole narrowing for that file.
    """
    assert not is_public_open(corpus.PUBLIC_SUBSTRING)
    assert "public" in corpus.PUBLIC_SUBSTRING  # the substring test fires


def test_a_plain_import_is_not_a_re_export() -> None:
    """An ordinary filtered import does not re-export.

    Scenario: an ordinary filtered import is not a re-export
    """
    assert not is_public_open(corpus.PLAIN_OPEN)


def test_a_non_open_statement_is_not_a_re_export() -> None:
    """A statement that is not an open never re-exports.

    Scenario: a statement that is not an open is never a re-export

    The two lookaround-correct sites are bare TOKEN matchers with no `open` guard,
    so folding them in requires this anchor — otherwise any line mentioning
    `public` would qualify.
    """
    assert not is_public_open(corpus.NOT_AN_OPEN)
    assert not is_public_open("-- public")
