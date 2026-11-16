#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""Pin the heading normaliser against the exact spellings that cost a census leg.

⚑⚑⚑ THE LOAD-BEARING CASE IS THE APOSTROPHE, and it is stated as the origin's own failure: an
ASCII apostrophe against its typographic rendering must compare EQUAL. The origin returns
unequal for that pair, which is the whole of gate-F78 and the reason a section vanished from a
filed census leg.

⚑⚑ AND THE ORIGIN'S BEHAVIOUR IS PRESERVED WHERE IT WAS RIGHT. It folded backticks, asterisks
and underscores, and those cases are asserted here unchanged — a widening that quietly dropped
a working case would be a rewrite wearing a fix's clothes. The markup cases exist to prove the
widening is additive.

⚑ THE NEGATIVE CONTROL IS THE ONE MOST LIKELY TO BE MISSING. A normaliser that folded
everything would pass every equality case above and be useless: two genuinely different
headings must still compare UNEQUAL. Without that arm, `hkey` returning a constant passes the
whole suite.

⚑⚑⚑ EVERY CONTROL HERE NAMES THE PREDICATE IT VALIDATES, because a control validates ONE
property and a changed predicate ORPHANS IT IN PLACE (gate-G21). This suite carried an
instance: a case asserting a filed census leg still existed on disk. It was chosen when that
leg was the live artifact, it kept printing, and under the predicate this suite actually tests
— *does the normaliser fold pandoc's rewrites* — it discriminated NOTHING. It would have
passed with this module deleted. It is replaced below by a differential against the origin's
own rule, which fails exactly where this module must succeed.
"""

from __future__ import annotations

import sys

from substrate import md_hkey

Case = tuple[str, bool]

# ⚑ THE ORIGIN'S RULE, TRANSCRIBED RATHER THAN IMPORTED. `scratch/mdstruct._hkey` cannot be
# imported here: that module carries mypy findings behind an all-or-nothing gate, and reaching
# it would make this suite's own admission depend on a file nobody can repair. Transcribed, it
# is a fixture that must be kept honest by hand — and the honesty check is that it FAILS the
# pair the replacement passes, which no transcription error could fake in that direction.
_ORIGIN_MARKUP = ("`", "*", "_")


def _origin_hkey(text: str) -> str:
    """Return what the ORIGIN's normaliser computes — markup only, no punctuation."""
    out = text
    for mark in _ORIGIN_MARKUP:
        out = out.replace(mark, "")
    return " ".join(out.split()).strip().casefold()


def _smart_cases() -> list[Case]:
    """Return the cases pinning that pandoc's rewrites fold to their ASCII source."""
    return [
        # ⚑ THE MEASURED ONE. gate-F78, gate-F82, gate-G8 all reduce to this pair.
        (
            "an apostrophe agrees with its typographic rendering",
            md_hkey.agree("the census's item", "the census\N{RIGHT SINGLE QUOTATION MARK}s item"),
        ),
        (
            "an opening single quote folds",
            md_hkey.agree("'quoted'", "\N{LEFT SINGLE QUOTATION MARK}quoted'"),
        ),
        (
            "a double quote pair folds",
            md_hkey.agree(
                'say "this"',
                "say \N{LEFT DOUBLE QUOTATION MARK}this\N{RIGHT DOUBLE QUOTATION MARK}",
            ),
        ),
        ("an em dash folds to two hyphens", md_hkey.agree("a -- b", "a \N{EM DASH} b")),
        ("an en dash folds to one hyphen", md_hkey.agree("a - b", "a \N{EN DASH} b")),
        (
            "an ellipsis folds to three dots",
            md_hkey.agree("wait...", "wait\N{HORIZONTAL ELLIPSIS}"),
        ),
    ]


def _markup_cases() -> list[Case]:
    """Return the cases pinning the ORIGIN's behaviour, unchanged.

    ⚑ THE WIDENING MUST BE ADDITIVE. The origin folded these three and nothing else, and a
    replacement that dropped one would be a rewrite rather than a repair.
    """
    return [
        ("a code span folds", md_hkey.agree("run `make -j` now", "run make -j now")),
        ("emphasis folds", md_hkey.agree("*emphatic* title", "emphatic title")),
        ("an underscore folds", md_hkey.agree("_under_ title", "under title")),
        ("whitespace collapses", md_hkey.agree("a   spaced   title", "a spaced title")),
        ("case folds", md_hkey.agree("A TITLE", "a title")),
    ]


def _negative_cases() -> list[Case]:
    """Return the arm without which a constant-returning normaliser would pass.

    ⚑ A NORMALISER THAT FOLDS EVERYTHING SATISFIES EVERY EQUALITY CASE ABOVE. These assert it
    still DISCRIMINATES, which is the property the anchoring loop actually depends on — a
    forward cursor that matched any heading to any line would mis-anchor rather than skip.
    """
    return [
        (
            "two different headings do NOT agree",
            not md_hkey.agree("the first section", "the second section"),
        ),
        (
            "a substring does NOT agree with its container",
            not md_hkey.agree("intro", "intro and more"),
        ),
        ("an empty key is not equal to a real one", not md_hkey.agree("", "a title")),
        # ⚑ THE FOLD MUST NOT MERGE DISTINCT PUNCTUATION INTO ONE KEY.
        (
            "an em dash and an en dash do NOT fold together",
            not md_hkey.agree("a \N{EM DASH} b", "a \N{EN DASH} b"),
        ),
    ]


def _differential_cases() -> list[Case]:
    """Assert this module SUCCEEDS exactly where the origin FAILS.

    ⚑⚑ THIS REPLACED A CONTROL THAT HAD STOPPED CONTROLLING (gate-G21). The prior case asserted
    a filed census leg still existed on disk — chosen when that leg was the live artifact, and
    true whether this module works or is deleted. Under this suite's actual predicate it
    discriminated nothing.

    ⚑ A DIFFERENTIAL IS THE RIGHT SHAPE HERE because the claim is not *the normaliser folds*
    but *the normaliser folds WHERE THE ORIGIN DID NOT*. Only a comparison carries that, and it
    fails loudly if the transcribed origin rule ever drifts into agreeing.
    """
    original = "SB-08 - What I re-derived (Q-8) the census's own highest-value item"
    rendered = original.replace("'", "\N{RIGHT SINGLE QUOTATION MARK}")
    return [
        (
            "the heading that vanished from a census leg now agrees",
            md_hkey.agree(original, rendered),
        ),
        ("the two spellings are genuinely different strings", original != rendered),
        # ⚑ THE DIFFERENCE IS THE REPAIR. If this ever passes, the origin folds punctuation too
        #   and this whole module is redundant — which is a finding, not a green.
        (
            "the ORIGIN's rule genuinely FAILS this pair",
            _origin_hkey(original) != _origin_hkey(rendered),
        ),
        # And the origin is not simply broken: it still folds what it was written to fold.
        (
            "the ORIGIN's rule still folds markup, so the fixture is faithful",
            _origin_hkey("run `make -j` now") == _origin_hkey("run make -j now"),
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _smart_cases() + _markup_cases() + _negative_cases() + _differential_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"md_hkey: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
