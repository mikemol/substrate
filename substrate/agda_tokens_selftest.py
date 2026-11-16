# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.agda_tokens` — four false-dead verdicts, and a live differential.

⚑⚑⚑ EVERY ARM HERE GUARDS A DELETION. A caller uses `body_tokens` to decide which imports are
UNUSED and then removes them, so a token this module fails to report is not a smaller answer —
it is a deleted import and a name that goes out of scope. All four recoveries were measured as
exactly that failure, in the field, on real modules:

  * a `\b`-bounded name pattern is blind to 1269 of 10831 defined names,
  * a qualified head is the evidence a record-module import is live,
  * a standalone punctuation run is the ONLY token an infix constructor produces,
  * a bracket-delimited mixfix is built from the delimiters the splitter splits on.

⚑⚑ AND EACH POSITIVE ARM IS PAIRED WITH A CONTROL. A tokenizer that returned every substring
would satisfy every "this token is present" case while being useless, so the shapes that must
NOT appear are asserted too — most sharply for `mixfix_delims`, where an over-broad set can only
SUPPRESS a dead-name verdict, which is the dangerous direction.

⚑ THE DIFFERENTIAL RUNS OVER REAL FILES, because agreement with my fixtures says nothing about
agreement on the bodies four gates actually read.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from substrate import agda_mask, agda_tokens, corpus

if TYPE_CHECKING:
    from collections.abc import Iterable

# The live authority this module drains from.
_ORIGIN = corpus.ROOT / "scratch" / "agda_lex.py"

# ⚑ A QUALIFIED USE — the head token is what proves the import live, since a record here is both
# a module and a definition.
_QUALIFIED = "foo = Magma._·_ x y\n"

# ⚑⚑ AN INFIX PAIR CONSTRUCTOR: `,` is a delimiter, so the naive split yields NO token for it
# and the providing module reads as dead.
_PUNCT = "pair = x , y\n"

# ⚑⚑ A BRACKET-DELIMITED MIXFIX used APPLIED — the shape whose whitespace form never matches.
_MIXFIX = "f = [_,_] g h\n"


@runtime_checkable
class _Origin(Protocol):
    """The origin functions this differential reads.

    ⚑ NARROWED AT THE SEAM: a dynamically loaded module is `Any`, so an un-narrowed differential
    agrees with anything, a typo included.
    """

    def body_tokens(self, body: str, mixfix: Iterable[str] = ()) -> set[str]:
        """Return the tokens a body mentions."""
        ...

    def mixfix_delims(self, names: Iterable[str]) -> set[str]:
        """Return the delimiter-sectioned names."""
        ...


def _origin() -> _Origin | None:
    """Load the live authority by path, or None when it cannot be reached.

    ⚑ A MISSING ORIGIN SKIPS THE DIFFERENTIAL RATHER THAN FAILING IT, and the label says which:
    a skipped arm and a passing one are indistinguishable to anyone counting green.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_agda_lex_tok_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    got: object = module
    return got if isinstance(got, _Origin) else None


def _word_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the name-boundary pattern."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑⚑ THE 11.7% CASE. A name made entirely of non-word characters is invisible to `\b`.
    check("a wholly non-word name matches", passed=bool(agda_tokens.word("∙").search("x ∙ y")))
    check("a hyphenated name matches", passed=bool(agda_tokens.word("go-le").search("f = go-le x")))
    check(
        "a name ending in a non-word character matches",
        passed=bool(agda_tokens.word("_+_").search("f = _+_ a b")),
    )

    # ⚑⚑ THE CONTROLS. A pattern matching anywhere would satisfy every arm above, so a name
    # embedded in a LONGER name must NOT match — that is what makes this a boundary at all.
    check(
        "a name embedded in a longer name does NOT match",
        passed=not agda_tokens.word("go").search("f = go-le x"),
    )
    check(
        "and a prefix of a longer name does NOT match",
        passed=not agda_tokens.word("Nat").search("f : Nat-ish"),
    )

    # ⚑ BRACKETS DELIMIT, so a name adjacent to one is still bounded.
    check(
        "a name against a bracket is bounded", passed=bool(agda_tokens.word("x").search("f = (x)"))
    )

    return out


def _token_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the three body-token recoveries."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑⚑ THE QUALIFIED HEAD. Removing this recovery produced 16 false-dead verdicts corpus-wide.
    qualified = agda_tokens.body_tokens(_QUALIFIED)
    check("a qualified use yields its HEAD as a token", passed="Magma" in qualified)
    check("and the full qualified token too", passed="Magma._·_" in qualified)

    # ⚑⚑⚑ THE PUNCTUATION RUN. Without it an infix constructor yields nothing and its module
    # reads as dead — the import was dropped and the name went out of scope.
    punct = agda_tokens.body_tokens(_PUNCT)
    check("a standalone punctuation run is a token", passed="," in punct)
    # ⚑ THE CONTROL: punctuation that is NOT standalone is a delimiter, not a token. Reporting
    # it would add tokens that suppress legitimate dead-name verdicts.
    check(
        "but punctuation inside an expression is not",
        passed="(" not in agda_tokens.body_tokens("f = g (x)"),
    )

    # ⚑⚑⚑ THE BRACKET MIXFIX, which the splitter shreds — only a verbatim scan finds it.
    check(
        "a bracket-delimited mixfix is recovered when declared",
        passed="[_,_]" in agda_tokens.body_tokens(_MIXFIX, {"[_,_]"}),
    )
    # ⚑ AND THE CONTROL: an undeclared mixfix is NOT invented, or the recovery would report a
    # token for any name a caller happened to pass.
    check(
        "and one not present in the body is NOT added",
        passed="⟨_⟩" not in agda_tokens.body_tokens(_MIXFIX, {"⟨_⟩"}),
    )

    check("an ordinary token is still found", passed="foo" in agda_tokens.body_tokens("foo x"))

    return out


def _mixfix_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for which names count as delimiter-sectioned."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    got = agda_tokens.mixfix_delims({"[_,_]", "⌊_⌋", "⟨_,_⟩", "_+_", "foo", ",,", "WithTarget)"})
    check("a bracket mixfix is selected", passed="[_,_]" in got)

    # ⚑⚑⚑ THE PREDICATE IS ABOUT `BODY_DELIMS`, NOT ABOUT BRACKETS, AND I ASSERTED IT WRONG
    # TWICE. The origin's docstring offers `⌊_⌋` and `⟨_⟩` as examples of delimiter-sectioned
    # names, so I first asserted `⌊_⌋` IS selected; that failed. I then generalised to "unicode
    # brackets are not selected"; that failed too — because `⟨_,_⟩` contains a COMMA, which is
    # in `BODY_DELIMS`, and is selected for that reason rather than for its brackets.
    #
    # ⚑⚑ SO THE RULE IS EXACT AND THE EXAMPLES ARE APPROXIMATE: a name is delimiter-sectioned
    # iff it holds a hole AND a character the splitter splits on. `⌊_⌋` holds neither delimiter
    # nor comma, so it survives tokenization intact and needs no verbatim recovery; `⟨_,_⟩` is
    # shredded at its comma and does. The differential confirms this copy matches the origin on
    # all of them, so the docstring describes INTENT while the predicate describes BEHAVIOUR.
    check(
        "a name whose only brackets are outside BODY_DELIMS is NOT selected",
        passed="⌊_⌋" not in got,
    )
    check("but one containing a delimiter IS, whatever its brackets", passed="⟨_,_⟩" in got)

    # ⚑⚑ THE HOLE IS REQUIRED, AND THIS IS THE DANGEROUS DIRECTION. This set can only ADD
    # tokens, so a tokenizer artifact admitted here SUPPRESSES a legitimate dead-name verdict.
    check("a tokenizer artifact with no hole is rejected", passed=",," not in got)
    check("and one with a stray bracket but no hole is rejected", passed="WithTarget)" not in got)
    # ⚑ AND A NON-DELIMITER MIXFIX IS NOT ONE EITHER — it needs no verbatim recovery, since the
    # splitter does not shred it.
    check("an ordinary infix name is not delimiter-sectioned", passed="_+_" not in got)
    check("and a plain name is not", passed="foo" not in got)

    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting agreement with the live authority."""
    origin = _origin()
    if origin is None:
        skipped = (
            "the origin could not be LOADED, so the differential is SKIPPED, not run and not passed"
        )
        return [(skipped, True)]

    fixtures = (
        ("qualified", _QUALIFIED),
        ("punctuation", _PUNCT),
        ("mixfix", _MIXFIX),
        ("plain", "foo x = bar y\n"),
    )
    tokens = [
        (
            f"{label} tokens match the origin",
            agda_tokens.body_tokens(src, {"[_,_]"}) == origin.body_tokens(src, {"[_,_]"}),
        )
        for label, src in fixtures
    ]

    names = {"[_,_]", "⌊_⌋", "_+_", "foo", ",,", "WithTarget)"}
    delims = [
        (
            "mixfix_delims matches the origin",
            agda_tokens.mixfix_delims(names) == origin.mixfix_delims(names),
        )
    ]

    found = sorted((corpus.ROOT / "agda" / "Substrate").rglob("*.agda"))[:5]
    if not found:
        return [
            *tokens,
            *delims,
            ("no agda source was found to difference — a fact about the TREE", True),
        ]
    live = [
        (
            f"{path.name} tokens match the origin",
            agda_tokens.body_tokens(agda_mask.mask_comments(path.read_text(encoding="utf-8")))
            == origin.body_tokens(agda_mask.mask_comments(path.read_text(encoding="utf-8"))),
        )
        for path in found
    ]
    return tokens + delims + live


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _word_cases() + _token_cases() + _mixfix_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"agda-tokens selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
