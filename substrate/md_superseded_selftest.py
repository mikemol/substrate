# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_superseded` — the three predicates that were each wrong.

⚑⚑⚑ THE TWO STRUCTURALLY IDENTICAL CASES ARE THE SUBJECT. `589 leaves` vs `1322 leaves` is a real
supersession and `2 files` vs `2941 files` is a coincidence, and they share a noun, carry two
values, and have no modifier either way. Each of the origin's first two predicates satisfied one by
breaking the other, so a suite holding only one of them would have passed both broken versions.

⚑⚑ AND THE BARE-NOUN ARM IS THE ONE THAT WENT SILENT. A filter dropping phrases with no space was
meant to discard unqualified nouns and instead discarded `leave` — the phrase the motivating
supersession produces — so the tool reported NOTHING for the case it was built for. That arm asserts
presence, which is the only assertion an empty census cannot satisfy.

⚑ THE FIXTURES ARE LINES, NOT A DOCUMENT, which is what makes the magnitude rule statable. The
origin opened a file, so separating a supersession from a coincidence required finding real text
containing both.
"""

from __future__ import annotations

import sys

from substrate import md_superseded as ms

#: ⚑ THE MOTIVATING SUPERSESSION, verbatim in the shape the corpus writes it. Same phrase, two
#: values, within an order of magnitude.
SUPERSEDED = ["the tree holds 589 leaves today", "re-measured: 1322 leaves"]

#: ⚑ THE COINCIDENCE THE FIRST PREDICATE COULD NOT REJECT. Same noun, two values, three orders
#: of magnitude apart — two populations, not one re-measured.
COINCIDENCE = ["a diff of 2 files", "the corpus holds 2941 files"]

#: One phrase measured once — nothing to disagree with.
SINGLE = ["the tree holds 589 leaves today"]

#: How many DISTINCT phrases the modifier fixture writes — `wired gate` and `unwired gate`.
PHRASES = 2

#: Float comparison tolerance for the spread ratio. Named because a bare literal here is a
#: judgement about precision that a reader cannot see the reason for.
TOLERANCE = 0.01


def _supersession_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the case the bare-noun filter silenced."""
    out: list[tuple[str, bool]] = []
    found = ms.collisions(SUPERSEDED)

    # ⚑ PRESENCE IS THE ASSERTION. An empty census satisfies every absence check ever written.
    out.append(
        (f"the motivating supersession is FOUND: {[c.why() for c in found]}", len(found) == 1)
    )
    out.append(
        (
            f"and it names both values: {found[0].why()}",
            [f.value for f in found[0].figures] == [589, 1322],
        )
    )
    out.append(
        (
            f"and each value carries its line: {found[0].figures}",
            [f.line for f in found[0].figures] == [1, 2],
        )
    )

    # ⚑⚑ THE BARE PHRASE IS WHAT THE FILTER DISCARDED. `leaves` carries no modifier here, so a
    # rule requiring one reports nothing — which is the recorded failure.
    out.append(
        (f"and the phrase is the bare noun: {found[0].phrase!r}", " " not in found[0].phrase)
    )
    return out


def _coincidence_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the case the second predicate could not reject.

    ⚑⚑ THIS AND THE ARM ABOVE MUST BOTH HOLD AT ONCE. They are the pair no phrasing rule
    separates, and satisfying either alone is what both failed predicates did.
    """
    out: list[tuple[str, bool]] = []

    out.append(
        (
            f"a three-order-of-magnitude gap is NOT reported: {ms.collisions(COINCIDENCE)}",
            ms.collisions(COINCIDENCE) == [],
        )
    )

    # ⚑ THE SENSITIVITY ARM. Widening the ratio must admit it, or the magnitude rule is not what
    # rejected it and this arm proves nothing about the rule.
    widened = ms.collisions(COINCIDENCE, ratio=10_000)
    out.append(
        (f"widening ONLY the ratio admits it: {[c.phrase for c in widened]}", len(widened) == 1)
    )
    return out


def _quiet_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for inputs that must report nothing."""
    out: list[tuple[str, bool]] = []

    out.append(
        (
            f"one measurement is not a disagreement: {ms.collisions(SINGLE)}",
            ms.collisions(SINGLE) == [],
        )
    )
    out.append((f"empty input yields nothing: {ms.collisions([])}", ms.collisions([]) == []))
    out.append(
        (
            f"prose with no figure yields nothing: {ms.collisions(['plain prose here'])}",
            ms.collisions(["plain prose here"]) == [],
        )
    )

    # ⚑ A ZERO HAS NO RATIO, so admitting it would make every phrase that counted nothing collide
    # with every other value it carries.
    zeroed = ms.collisions(["0 gates wired", "27 gates wired"])
    out.append((f"a zero value is excluded: {zeroed}", zeroed == []))
    return out


def _roster_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the noun roster is a parameter, not a secret.

    ⚑⚑⚑ THE ROSTER IS THE KNOWN WEAKNESS. A figure counted in a noun nobody listed is invisible,
    and the census would report its own vocabulary as the document's — so a case widens it and
    asserts the widening reaches, which is what makes the limit legible rather than silent.
    """
    out: list[tuple[str, bool]] = []
    unlisted = ["the run used 12 widgets", "the run used 19 widgets"]

    out.append(
        (
            f"an unlisted noun is INVISIBLE by default: {ms.collisions(unlisted)}",
            ms.collisions(unlisted) == [],
        )
    )

    widened = ms.collisions(unlisted, nouns=(*ms.NOUNS, "widgets"))
    out.append(
        (f"and widening the roster reaches it: {[c.why() for c in widened]}", len(widened) == 1)
    )
    return out


def _phrase_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the modifier-bearing phrase key.

    ⚑ THE MODIFIER IS WHAT SEPARATES TWO REAL POPULATIONS sharing a noun, which is why the key is
    the whole phrase rather than the noun alone.
    """
    out: list[tuple[str, bool]] = []
    modified = ["21 wired gates", "27 wired gates", "3 unwired gates"]
    found = ms.collisions(modified)

    out.append(
        (
            f"the modified phrase collides with itself: {[c.phrase for c in found]}",
            len(found) == 1 and "wired" in found[0].phrase,
        )
    )
    out.append(
        (
            f"and the differently-modified figure stays out: {found[0].figures}",
            [f.value for f in found[0].figures] == [21, 27],
        )
    )

    seen = ms.figures(modified)
    out.append((f"and both phrases are recorded separately: {sorted(seen)}", len(seen) == PHRASES))
    return out


def _account_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what a collision reports about itself."""
    out: list[tuple[str, bool]] = []
    got = ms.collisions(SUPERSEDED)[0]

    out.append(
        (f"the spread is the ratio: {got.spread:.2f}", abs(got.spread - 1322 / 589) < TOLERANCE)
    )
    out.append(
        (
            f"and the account names every value with its line: {got.why()}",
            "589" in got.why() and "1322" in got.why() and ":1" in got.why(),
        )
    )
    return out


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` running the census over the live plan document.

    ⚑ THE ARC'S OWN DOCUMENT IS THE SUBJECT THIS TOOL WAS BUILT FOR, so a fixture-only suite would
    leave the one population it exists to measure unmeasured.
    """
    out: list[tuple[str, bool]] = []

    from pathlib import Path  # noqa: PLC0415 - only this arm needs a real document

    doc = Path.home() / ".claude/plans/dispatch-a-research-agent-streamed-torvalds.md"
    if not doc.exists():
        out.append((f"the live plan is absent — a fact about the METHOD: {doc}", True))
        return out

    lines = doc.read_text(encoding="utf-8").split("\n")
    found = ms.collisions(lines)

    # ⚑ THE COUNT IS NOT ASSERTED — it moves with the document. What is asserted is that every
    # reported row satisfies the rule that admitted it, which cannot drift.
    out.append(
        (
            f"every live collision is within the ratio: {len(found)} row(s)",
            all(c.spread <= ms.RATIO for c in found),
        )
    )
    out.append(
        (
            f"and every one carries at least two values: {len(found)} row(s)",
            all(len(c.figures) >= ms.DISAGREEING for c in found),
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _supersession_cases()
        + _coincidence_cases()
        + _quiet_cases()
        + _roster_cases()
        + _phrase_cases()
        + _account_cases()
        + _live_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-superseded selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
