#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.spoken_text` — and for the banners it checks.

⚑⚑⚑ THE BANNERS ARE VERIFIED HERE, WHERE THE CONTRACT LIVES, RATHER THAN ONCE PER MODULE. Each
module owning a `speak()` gets one row in `_BANNERS` naming its text and the words it owes; adding
another refusing module is a row, not a copied arm. That is the difference between a contract and
a convention — a convention is what fifty suites each reimplement.

⚑⚑ AND EVERY ROW PAIRS THE REFUSAL WITH THE CAPABILITY. A module that refused everything, entry
point and functions alike, would satisfy every speaks-when-run arm and read as repaired. What the
refusal must remove is the SILENT ZERO, not the reading — so `the_libraries_still_answer` exercises
each module's real entry point beside the banner arms.

⚑ THE NEEDLES ARE THE MODULE'S OWN DISCLAIMER WORDS, not a generic roster. What `edge_split` must
disclaim ("does not read a bib") is not what `spoken_text` must ("does not run a module"), and a
shared needle list would check that banners contain the same sentence rather than that each names
its own missing capability.

⚑ `witness_row` AND `warrant_bib` LEFT THIS TABLE (2026-09-25): both moved to mtools'
`mikemol-witness`, which owns their contracts and suites now. A substrate suite checking a
banner substrate no longer ships would be a test of someone else's package — and `witness_row`
dropped `speak()` in the move, having no modes to describe.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from substrate import edge_split, spoken_text


@dataclass(frozen=True, slots=True)
class Banner:
    """One module's spoken text and the words that text owes a reader."""

    label: str
    text: str
    needs: tuple[str, ...]


# ⚑ EACH ROW NAMES ITS OWN DISCLAIMER. The third needle in every row is the capability the
# module's NAME suggests and it lacks — the part a copied arm drops.
_BANNERS = (
    Banner("edge_split", edge_split.speak(), ("LIBRARY", "targets(raw)", "DOES NOT READ A BIB")),
    Banner("spoken_text", spoken_text.usage(), ("LIBRARY", "audit(text", "DOES NOT RUN A MODULE")),
)


def every_banner_says_what_it_owes(out: list[str]) -> int:
    """Check each module's spoken text names itself, an entry point, and what it lacks."""
    bad = 0
    for banner in _BANNERS:
        missing = spoken_text.audit(banner.text, *banner.needs)
        if not missing.ok:
            out.append(f"selftest: {banner.label} — {missing.why()}")
            bad += 1
    return bad


def every_banner_check_asks_for_something(out: list[str]) -> int:
    """Check no row degrades into the predicate that cannot fail.

    ⚑⚑ THE VACUOUS ROW IS THE FAILURE MODE OF THIS WHOLE TABLE. A `Banner` with an empty `needs`
    passes `audit` on any non-empty string, so the row would report green while checking that the
    banner exists and nothing more — the census-green-is-a-fact-about-the-census shape, one layer
    inside the suite built to prevent it.
    """
    bad = 0
    for banner in _BANNERS:
        if spoken_text.demands(*banner.needs) < 1:
            out.append(f"selftest: {banner.label}'s row demands nothing of its banner")
            bad += 1
    return bad


def an_absent_word_is_reported(out: list[str]) -> int:
    """Check the audit FAILS when a banner omits what it owes — the discriminator.

    ⚑ WITHOUT THIS ARM the table above passes against an `audit` that returns ok unconditionally.
    A check on real banners cannot tell a working predicate from a permissive one; only a banner
    known to be deficient can.
    """
    bad = 0
    missing = spoken_text.audit("a banner saying almost nothing", "ABSENT-WORD")
    if missing.ok:
        out.append("selftest: an omitted word audited as ok")
        bad += 1
    if "ABSENT-WORD" not in missing.why():
        out.append(f"selftest: the reason does not name the omission: {missing.why()}")
        bad += 1
    return bad


def an_empty_banner_is_its_own_finding(out: list[str]) -> int:
    """Check emptiness reports as emptiness, not as omitting everything.

    ⚑ TWO DIFFERENT NEXT ACTIONS. `omits [a, b, c]` sends a reader to add three sentences; `is
    empty` tells them there is no banner at all. Collapsing them reports the second as the first.
    """
    bad = 0
    missing = spoken_text.audit("   \n  ", "anything")
    if missing.ok:
        out.append("selftest: a blank banner audited as ok")
        bad += 1
    if not missing.empty:
        out.append("selftest: a blank banner was not reported as empty")
        bad += 1
    if missing.absent:
        out.append(f"selftest: a blank banner also reported omissions {missing.absent!r}")
        bad += 1
    return bad


def the_libraries_still_answer(out: list[str]) -> int:
    """Check each refusing module's real capability still works — THE PAIR for the arms above.

    ⚑⚑ THE REFUSAL MUST REMOVE THE SILENCE, NOT THE READING. A module whose functions raised
    would pass every banner arm here, so each library is exercised on the one question it exists
    to answer.
    """
    bad = 0
    if edge_split.targets("A, B") != ("A", "B"):
        out.append("selftest: edge_split stopped splitting a declared field")
        bad += 1
    if spoken_text.REFUSAL_STATUS == 0:
        out.append("selftest: the refusal status collapsed to the silence it replaces")
        bad += 1
    return bad


_ARMS = (
    every_banner_says_what_it_owes,
    every_banner_check_asks_for_something,
    an_absent_word_is_reported,
    an_empty_banner_is_its_own_finding,
    the_libraries_still_answer,
)

_CASE_COUNT = len(_BANNERS) + len(_BANNERS) + 2 + 3 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"spoken-text selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"spoken-text selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
