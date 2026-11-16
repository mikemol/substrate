#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Resolve a finding KEY against a roster — exact, unique prefix, or a refusal.

⚑⚑⚑ THE SECOND DRAIN UNIT (gate-G57, gate-G59), AND IT IS THE ONE THAT LETS THE ROSTER MOVE.
The origin's `resolve` reads a module-global `WITNESSES`, so the lookup and the roster cannot
be separated: any relocation of the roster is also an edit to the resolver, inside a file the
per-file gate refuses. Taking the roster as an ARGUMENT is the whole unlock — the resolver
stops caring where the roster lives, which is the precondition for moving it into a keyed
library the way `catalog/library/items.py` moved its witnesses into `concepts`.

⚑⚑ AND THE ROSTER IS NOT DATA, WHICH gate-G59 CORRECTED. Every value is a callable closing
over a kind builder, so this module types the roster as a mapping to thunks rather than to
strings. A design that assumed rows would have moved executable dispatch into a citation
format and lost the inter-entry provenance comments with it.

⚑⚑⚑ THREE OUTCOMES, AND THE PREFIX ONE EXISTS BECAUSE AN EXACT-ONLY LOOKUP LIED. The roster
mixes two key spellings — bare stems minted early (`tmi-F6`) and descriptive full keys minted
since (`tmi-F13-census-reads-test-data-as-dispatch`) — and nothing records which spelling a
finding got, so a caller cannot know which to type. Exact-only answered a stem with *"no
witness registered"*: a CONFIDENT FALSE ABSENCE about a finding that is right there, phrased
in the vocabulary of a roster/record disagreement, which a reader takes as never-filed.

⚑ AMBIGUITY IS REFUSED, NEVER RESOLVED BY A RULE. `tmi-F1` prefixes `tmi-F10` and `tmi-F11`;
picking shortest or first would silently answer about a DIFFERENT finding, and a wrong witness
reads exactly like a right one. So the refusal NAMES ITS CANDIDATES rather than guessing —
and per gate-G55 it names ones the caller can actually retype, which is what a successor is
for.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    Witness = Callable[[], tuple[int, str]]
    Answer = tuple[str, Witness | None]


def resolve(
    want: str,
    roster: Mapping[str, Callable[[], tuple[int, str]]],
) -> tuple[str, Callable[[], tuple[int, str]] | None]:
    """Return `(key, witness)` for `want`, or `(refusal_text, None)`.

    ⚑ EXACT MATCH ALWAYS WINS OUTRIGHT, so a bare-stem key that is also a prefix of longer keys
    still resolves to itself. Without that, `tmi-F6` would read as ambiguous against
    `tmi-F6-ground-truth-…` and a key that exists would refuse.
    """
    if want in roster:
        return want, roster[want]
    hits = sorted(key for key in roster if key.startswith(want))
    if len(hits) == 1:
        return hits[0], roster[hits[0]]
    if hits:
        listed = "\n".join("    " + key for key in hits)
        return (f"findings.py: {want!r} is an AMBIGUOUS prefix over {len(hits)} key(s) — "
                "refusing rather than picking one, since a wrong witness reads like a right "
                f"one:\n{listed}"), None
    # ⚑ AN UNKNOWN KEY IS ITS OWN OUTCOME. "This finding is open" and "I have never heard of
    #   this finding" are different facts, and collapsing them lets a typo read as debt.
    return (f"findings.py: no witness registered for {want!r}, and no key begins with it — "
            "a bib entry with no witness is a roster/record disagreement "
            "(see --list)"), None


def unresolved(answer: tuple[str, Callable[[], tuple[int, str]] | None]) -> bool:
    """Report whether a `resolve` answer is a refusal rather than a hit.

    ⚑ THE PREDICATE EXISTS SO A CALLER NEVER TESTS THE TUPLE SHAPE BY HAND. Reading `[1] is
    None` at each call site is the judgement-in-the-caller shape: four sites spelling one rule
    is four chances to spell it as `not answer[1]`, which is the same for None and for a
    falsy-but-present witness.
    """
    return answer[1] is None
