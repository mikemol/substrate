# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""module_name_of — the module a source declares, read from its own header.

14 header-regex sites carry at least one of two defects: 6 anchor on a same-line
`where` (so every PARAMETERIZED header is missed), and 8 use a `[A-Za-z0-9_.\-]+`
character class (so every unicode name is rejected — most of this corpus).  None masks
comments first, so a commented-out header currently matches.

These tests are the acceptance criteria for Phase B1/B2 of the sweep: converting a site
to `module_name_of` CHANGES BEHAVIOUR, and these say what the new behaviour must be.

⚑⚑ CONVERTED FROM `unittest.TestCase` TO PLAIN pytest FUNCTIONS UNDER Ⓝ73″
⟡the-tests-seam, and the conversion is a PAYDOWN rather than a restyling: the file
carried 85 ruff findings on disk (18 `PT009`, 14 each `ANN201`/`D400`/`D415`, 7
`PLC0415`, five `PTH` path-API findings, and 2 `RUF001`), so any edit to it was refused
by the per-file gate.  `"tests/*" = ["S101"]` admits the bare `assert` these become.

⚑ THE DELTA ASSERTIONS ARE ALL KEPT — the ones showing what the OLD copy returns.  They
are why the file is readable by a reviewer who does not trust its author, and dropping
them in a mechanical conversion would have removed the evidence while keeping the claim.

⚑ THE SEVEN IN-FUNCTION IMPORTS WERE HOISTED, and that is a correctness change rather
than tidying: `PLC0415` is enforced tree-wide, so a lazy in-function import is debt.
Five cases re-imported names the module already had at the top of the file.

⚑ THE CORPUS WALK NOW USES `agda_files` AND `pathlib`, NOT `glob` + `os.path` + `open`.
That is the same authority the sibling suites use (the `_build` exclusion, the sort), and
it retires four `PTH` findings — `PTH207`/`PTH100`/`PTH120`/`PTH123` — that the old
hand-rolled walk carried.  The claim is unchanged: the walk covers the same files.

⚑⚑ THE DOUBLE-STRUCK CAPITAL N IS SPELLED AS A `\N{...}` ESCAPE, AND THAT IS NOT
COSMETIC EITHER.  `RUF001` refuses the literal because that codepoint is visually
confusable with a plain ASCII `N` — which is precisely the hazard this file is ABOUT: an
ASCII-only character class truncates such a name, and a truncated name is worse than a
failure because it is plausible.  A reader who cannot tell the two apart on screen is the
reader the rule protects, so naming the codepoint makes the test's own subject
unambiguous.  The RING OPERATOR in the other fixture is NOT flagged (no ASCII lookalike)
and stays literal — the rule fires on confusability, not on non-ASCII, and matching that
distinction is what keeps the escape meaningful rather than a blanket habit.

⚑ EVERY `.group(1)` IS BOUND TO A DECLARED `str` BEFORE IT IS COMPARED.  `re.Match.group`
is typed `str | Any` (a group CAN be None), and `disallow_any_expr` refuses the comparison
before the value is ever read.  The binding is a narrowing at the untyped boundary, which
is the same shape the sibling suites record at their own `re` seams — not a formality.

⚑ THE `Scenario:` LINES SIT BELOW EACH SUMMARY LINE.  `D400`/`D415` require a first
docstring line ending in a period, while `gherkin_scan` captures to the closing quotes —
so a period on the `Scenario:` line becomes part of the scenario NAME and breaks the
match against `features/`.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from agda_lex import HEADER, agda_files, module_name_of

from tests import corpus

# The two defective spellings, reproduced so the tests can demonstrate the delta rather
# than merely assert the fix. A test that shows what the OLD copy returns is the one a
# reviewer can check without trusting the author.
OLD_WHERE_ANCHORED = re.compile(r"^module\s+(\S+)\s+where", re.MULTILINE)
OLD_ASCII_ONLY = re.compile(r"^module\s+([A-Za-z0-9_.\-]+)\s+where", re.MULTILINE)

REPO = Path(__file__).absolute().parent.parent
SRC = REPO / "agda" / "Substrate"

# The two unicode module names the corpus fixtures declare, spelled once each.
_UNICODE_NAME = "Substrate.\N{DOUBLE-STRUCK CAPITAL N}-elim"
_OPERATOR_NAME = "Substrate.Algebra.∘-assoc"

# ⚑ THE FLOOR THE CORPUS-SCALE CASE ASSERTS, named rather than typed at the comparison.
# MEASURED at Phase B1: the old regex misses 151 of 2764 files (5.5%).  The assertion is
# a FLOOR rather than the exact number so a corpus that grows does not fail a test about
# the regex — but a floor of 100 still catches a regression toward the anchored form,
# which would send it to zero.
_MISSED_FLOOR = 100


def _first_group(m: re.Match[str] | None) -> str | None:
    """Return a match's first group as a declared `str`, or None if there was no match.

    ⚑ THE NARROWING LIVES HERE RATHER THAN AT SIX CALL SITES.  `re.Match.group` is typed
    `str | Any` because a group can legitimately be None, so `disallow_any_expr` refuses
    every comparison against it.  One helper with a real `isinstance` is a CHECK; six
    inline casts would each be an assertion nothing verified.
    """
    if m is None:
        return None
    got: object = m.group(1)
    return got if isinstance(got, str) else None


def test_header_spanning_lines_is_found() -> None:
    """A parameterized header is found despite having no same-line `where`.

    Scenario: a parameterized header has no same-line `where`
    """
    src = "\n".join(corpus.PARAM_HEADER_AFTER_IMPORT)
    assert module_name_of(src) == "Substrate.Groups.Coxeter.Core"


def test_the_old_spelling_misses_it() -> None:
    """The where-anchored copies find no header at all here.

    Scenario: the where-anchored copies miss a parameterized header entirely

    Not a redundant assertion: it pins the DELTA, so if someone "simplifies"
    module_name_of back to the anchored form this test fails loudly instead of the
    change looking harmless.
    """
    src = "\n".join(corpus.PARAM_HEADER_AFTER_IMPORT)
    assert OLD_WHERE_ANCHORED.search(src) is None


def test_real_corpus_header_four_line_telescope() -> None:
    """A real four-line telescope resolves to its module name.

    Scenario: a real four-line telescope resolves (Discipline.agda:82)
    """
    assert module_name_of(corpus.PARAM_HEADER_REAL) == "Rule1"
    assert OLD_WHERE_ANCHORED.search(corpus.PARAM_HEADER_REAL) is None


def test_unicode_module_name() -> None:
    """A unicode module name resolves.

    Scenario: a unicode module name resolves
    """
    assert module_name_of(corpus.UNICODE_HEADER) == _UNICODE_NAME


def test_unicode_operator_name() -> None:
    """An operator-bearing module name resolves.

    Scenario: an operator-bearing module name resolves
    """
    assert module_name_of(corpus.UNICODE_OPERATOR_HEADER) == _OPERATOR_NAME


def test_the_ascii_only_copies_reject_it() -> None:
    """The ASCII character-class copies cannot return a unicode name.

    Scenario: the ASCII character-class copies reject a unicode name

    `[A-Za-z0-9_.-]+` stops at the first non-ASCII char, so it either fails or
    returns a TRUNCATED name — the second is worse, being plausible.
    """
    assert _first_group(OLD_ASCII_ONLY.search(corpus.UNICODE_HEADER)) != _UNICODE_NAME


def test_the_old_regex_misses_a_large_slice_of_the_corpus() -> None:
    """The old header regex silently drops a large slice of the live corpus.

    Scenario: the old header regex silently drops 5% of the corpus

    ⚑ MEASURED at Phase B1: over the 2764-module corpus the old ASCII+anchored regex
    MISSES 151 files entirely (5.5%), returning None so every analysis silently drops
    them.  151 = 149 parameterized headers (no same-line `where`) + 2 unicode names.
    Zero files differ in the OTHER direction, so the canonical is a strict improvement,
    never a regression.

    This test is corpus-dependent by design: if someone re-introduces the anchored form,
    the count moves and the test says by how much.
    """
    files = agda_files(str(SRC))
    if not files:
        pytest.skip("no Agda corpus present")

    missed = disagreed = 0
    for p in files:
        src = Path(p).read_text(encoding="utf-8", errors="replace")
        new = module_name_of(src)
        if new is None:
            continue
        old = _first_group(OLD_ASCII_ONLY.search(src))
        if old is None:
            missed += 1
        elif old != new:
            disagreed += 1
    # The canonical must never disagree on a name the old form DID find —
    # that would be a regression, not an improvement.
    assert disagreed == 0
    # And it must still be finding the ones the old form drops.
    assert missed > _MISSED_FLOOR, (
        "the old regex should miss ~151 corpus files; if this fell, either the corpus "
        "changed shape or the canonical regressed toward the anchored form"
    )


def test_search_returns_a_group_1_like_a_pattern() -> None:
    """The header shim answers `.search().group(1)` like a compiled pattern.

    Scenario: the header shim answers .search().group(1) like a compiled pattern

    Six tools held the header regex as a compiled PATTERN OBJECT and used it as
    `modre.search(text).group(1)`.  Rewriting six call sites would have touched more
    code than the defect warranted and could diverge six ways again; exposing the
    canonical with the SAME interface converts each by one line.
    """
    m = HEADER.search("module M where\n")
    assert m is not None
    assert m.group(1) == "M"


def test_search_returns_none_when_absent() -> None:
    """The header shim returns None when there is no header.

    Scenario: the header shim returns None when there is no header
    """
    assert HEADER.search("x : Set\n") is None


def test_shim_sees_a_parameterized_header() -> None:
    """The header shim resolves what the compiled pattern missed.

    Scenario: the header shim resolves what the compiled pattern missed
    """
    src = "\n".join(corpus.PARAM_HEADER_AFTER_IMPORT)
    m = HEADER.search(src)
    assert m is not None
    assert m.group(1) == "Substrate.Groups.Coxeter.Core"
    assert OLD_WHERE_ANCHORED.search(src) is None


def test_unsupported_group_fails_loudly() -> None:
    """A caller wanting a group the shim cannot supply fails loudly.

    Scenario: a caller wanting a group the shim cannot supply fails loudly

    ⚑ The shim deliberately does NOT implement .span()/.groups(): a caller relying
    on a byte offset must break at conversion time, not silently receive a wrong
    one.  Failing loudly is the whole reason this is a narrow shim and not a
    general match-object impersonation.
    """
    m = HEADER.search("module M where\n")
    assert m is not None
    with pytest.raises(IndexError):
        m.group(2)
    assert not hasattr(m, "span")


def test_commented_header_is_not_a_header() -> None:
    """A commented-out module header is not the module.

    Scenario: a commented-out module header is not the module
    """
    assert module_name_of(corpus.COMMENTED_HEADER) == "Real"


def test_a_block_commented_header_is_not_a_header() -> None:
    """A header inside a block comment is not the module.

    Scenario: a header inside a block comment is not the module

    ⚑ The `--`-at-column-0 case is ALREADY safe in the old copies, because their
    `^` anchor rejects a leading `--`.  The case that is NOT safe is a BLOCK
    comment: `{- module Ghost where -}` puts `module` at column 0 on its own line,
    so an unmasked `^module` matches it.  Pinning the easy case and calling comment
    masking tested would have been theatre — this is the one that bites.
    """
    src = "{-\nmodule Ghost where\n-}\nmodule Real where\n"
    assert module_name_of(src) == "Real"
    # and the delta: the unmasked copy binds the ghost
    assert _first_group(OLD_WHERE_ANCHORED.search(src)) == "Ghost"


def test_absent_header_returns_none() -> None:
    """Source with no module header yields None.

    Scenario: source with no module header yields None
    """
    assert module_name_of(corpus.NOT_AN_OPEN) is None
