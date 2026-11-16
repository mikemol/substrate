# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""statements / span_end / mask_comments — the statement-span authority.

The span rule is the one that has DESTROYED SOURCE, twice, from two different copies:
an import above a parameterized module header absorbed the header and its whole
telescope, so a caller deleting the span deleted the module.  33 files gutted;
Coxeter/Core.agda went 76 lines to 3; found only by the build.

15 copies of the naive rule existed.  They are now retired on write paths, with ONE
documented exception (`split_lemmas.py:52`, which pairs with a COLUMN-0 opener where the
canonical rule would release indented body lines — measured: 47 unplaced lines in
Coxeter/Core.agda, caught by the conservation guard).

⚑ These duplicate cases in `agda_lex._selftest`.  That is deliberate and temporary: the
selftest stays until `run_selftests.py` gates it, so neither layer is the single point of
failure while the other is being wired up.  Do not delete either half unilaterally.

⚑⚑ CONVERTED FROM `unittest.TestCase` TO PLAIN pytest FUNCTIONS UNDER Ⓝ73″
⟡the-tests-seam, and the conversion is a PAYDOWN rather than a restyling: the file
carried 57 ruff findings on disk (14 `PT009`, 11 `ANN201`, 10 each `D400`/`D415`, 2
`PLC0415`), so any edit to it was refused by the per-file gate.  `"tests/*" = ["S101"]`
admits the bare `assert` these become.

⚑⚑ `_continues` IS NO LONGER IMPORTED, AND THAT IS THE ONE BEHAVIOURAL CHANGE HERE.
Two cases reached `agda_lex._continues(line, depth)` directly — an underscore-named
helper imported across a module boundary, which is the exact shape `agda_lex.span_end`'s
own docstring names as a hazard ("public API wearing a private label", recorded there of
`agda_imports._span_end` and its seven importers).  It is absent from
`stubs/agda_lex.pyi`, whose stated scope is the PUBLIC surface, so a strict check reads
the import as `attr-defined` and every call as `Any`.

⚑ SO THE PREDICATE IS ASKED THROUGH `span_end`, WHICH IS THE PUBLIC WRAPPER OVER THE SAME
RULE, and the claims are unchanged in content: a declaration opener still must STOP a
span, and inside an open paren a keyword still must NOT.  What is lost is the ability to
pass a synthetic depth — the depth>0 arm is now exercised through the corpus fixture that
actually produces it, which is the stronger witness anyway (it is the ONE statement in the
whole corpus where the two rules disagree).  ⚑ Restoring the direct form is a matter for
whoever owns `stubs/agda_lex.pyi`; it is named here rather than worked around silently.

⚑ THE `Scenario:` LINES SIT BELOW EACH SUMMARY LINE.  `D400`/`D415` require a first
docstring line ending in a period, while `gherkin_scan` captures to the closing quotes —
so a period on the `Scenario:` line becomes part of the scenario NAME and breaks the
match against `features/`.
"""

from __future__ import annotations

import re

from agda_lex import mask_comments, span_end, statements

from tests import corpus

# ⚑ THE NAIVE RULE, SPELLED HERE RATHER THAN IMPORTED.  The claim under test is that the
# canonical rule DIFFERS from this one, so the naive form is the reference arm and must be
# stated independently.  `\s` matches the newline, which is what lets it run from the
# import through the whole telescope.
_NAIVE_SPAN = re.compile(r"^open import \S+[^\n]*(\n\s+[^\n]*)*")

# ⚑ THE NON-GREEDY STRIPPER, the copy 19 importers inherited — three of them PRE-COMMIT
# GATES.  It stops at the FIRST `-}`, so a nested comment leaks live text.
_WEAK_MASK = re.compile(r"\{-.*?-\}", re.DOTALL)

# ⚑ THE WRAPPED USING-LIST'S EXTENT, NAMED RATHER THAN TYPED AT THE COMPARISON.  The
# fixture is three lines of one statement (`corpus.WRAPPED_USING_WITH_MODULE`, verbatim
# from TokiPona/LinearAlgebra.agda:49-51), so the span must reach index 3 — the exclusive
# end.  A bare literal here reads as arbitrary; it is the fixture's own shape.
_WRAPPED_USING_END = 3


def spans(lines: list[str], kind: str = "import") -> list[tuple[int, int]]:
    """Return the (start, end) spans the authority finds for one statement kind."""
    return [(s.start, s.end) for s in statements(lines) if s.kind == kind]


def test_parameterized_header_is_not_absorbed() -> None:
    """An import above a parameterized header keeps its own span.

    Scenario: an import above a parameterized header keeps its own span
    """
    assert spans(corpus.PARAM_HEADER_AFTER_IMPORT) == [(0, 1)]


def test_the_naive_rule_absorbs_it() -> None:
    """The naive indentation rule swallows the header and its telescope.

    Scenario: the naive indentation rule absorbs the header and telescope

    Pins the DELTA. The naive rule is `startswith(" ") and strip()`; it runs from
    the import to the end of the telescope, so the caller's delete takes the module.
    """
    lines = corpus.PARAM_HEADER_AFTER_IMPORT
    j = 1
    while j < len(lines) and lines[j].startswith(" ") and lines[j].strip():
        j += 1
    # blank line at index 1 stops it here, but the header's telescope at 3-5 is what
    # the regex form `(\n\s+[^\n]*)*` consumes — \s matches the newline too.
    m = _NAIVE_SPAN.match("\n".join(lines))
    assert m is not None
    assert "(Word : Set)" in m.group(0)  # the telescope was swallowed
    assert "module Substrate" in m.group(0)  # and so was the header


def test_indented_definitions_are_not_absorbed() -> None:
    """An indented definition after an import is not part of that import.

    Scenario: an indented definition after an import is not a continuation
    """
    assert spans(corpus.INDENTED_DEFS_AFTER_IMPORT) == [(1, 2)]


def test_a_declaration_opener_stops_the_span() -> None:
    """A line opening a declaration ends the preceding statement.

    Scenario: a line opening a declaration ends the statement

    ⚑ ASKED THROUGH `span_end` RATHER THAN THE PRIVATE PREDICATE. The import at index 0
    is followed by an INDENTED type signature, which the naive rule reads as a
    continuation; the authority must end the span at 1, meaning it did not consume the
    declaration.
    """
    assert span_end(["  open import A", "  x : Nat"], 0) == 1


def test_module_keyword_inside_parens_continues() -> None:
    """A wrapped using-list containing a module re-export stays whole.

    Scenario: a wrapped using-list containing a module re-export stays whole

    The ONE statement in the whole corpus where the depth-aware and depth-blind
    rules disagree (TokiPona/LinearAlgebra.agda:49-51). A depth-blind keyword guard
    truncates the list at `module WithTarget` and silently drops the re-export.
    """
    assert spans(corpus.WRAPPED_USING_WITH_MODULE) == [(0, _WRAPPED_USING_END)]


def test_inside_parens_nothing_opens_a_statement() -> None:
    """Inside an open paren a keyword does not begin a new statement.

    Scenario: inside an open paren, a keyword does not start a new statement

    ⚑ THE TWO ARMS ARE NOW BOTH CORPUS-DRIVEN. The `module` at depth>0 is the wrapped
    using-list's third line, which `span_end` must reach; the same keyword at depth 0
    opens a statement of its own, so a span starting there ends immediately.
    """
    assert span_end(corpus.WRAPPED_USING_WITH_MODULE, 0) == _WRAPPED_USING_END
    assert span_end(["module WithTarget", "next : Set"], 0) == 1


def test_nested_block_comments_fully_masked() -> None:
    """Nested block comments are masked to their true extent.

    Scenario: nested block comments are masked to their true extent
    """
    assert mask_comments(corpus.NESTED_BLOCK_COMMENT).replace(" ", "") == "ab"


def test_the_non_greedy_copy_leaks_live_text() -> None:
    """The non-greedy stripper leaves live text after the first close.

    Scenario: the non-greedy stripper leaves live text after the first close

    19 importers inherited this, three of them PRE-COMMIT GATES, so commented-out
    code was censused as real declarations.
    """
    weak = _WEAK_MASK.sub(" ", corpus.NESTED_BLOCK_COMMENT)
    assert "z" in weak  # leaked
    assert "z" not in mask_comments(corpus.NESTED_BLOCK_COMMENT)


def test_arrow_is_a_name_not_a_comment() -> None:
    """The token `-->` is an Agda name, not a comment opener.

    Scenario: --> is an Agda name, not a comment opener
    """
    assert "-->" in mask_comments(corpus.ARROW_NOT_A_COMMENT)


def test_length_and_line_structure_preserved() -> None:
    """Masking preserves the source's length and line structure.

    Scenario: masking preserves length and line structure

    Load-bearing: callers index by line and some by column, so the mask must be a
    drop-in for the source everywhere.
    """
    src = "a -- c\nb {- d -} e\n"
    out = mask_comments(src)
    assert len(out) == len(src)
    assert out.count("\n") == src.count("\n")
