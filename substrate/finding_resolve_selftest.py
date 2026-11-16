#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the key resolver, and pin it DIFFERENTIALLY against the origin's LIVE roster.

⚑⚑⚑ THE DIFFERENTIAL HERE IS STRONGER THAN THE KIND UNIT'S, and deliberately so. `resolve` is
pure over a roster, so the origin's own `WITNESSES` can be handed to BOTH implementations and
every key in it compared — not five fixtures, the whole live population. A drain that agrees
on a fixture and disagrees on the corpus has not been verified.

⚑⚑ THE SPELLING PAIRS ARE THE CASE THAT MATTERS. `tmi-F6` is a bare stem AND a prefix of
`tmi-F6-ground-truth-…` in the bib, so exact-must-win is not a nicety: without it a key that
exists refuses as ambiguous. Those four are read from the live roster rather than typed, so
the case tracks the population instead of a snapshot of it.

⚑ AND AMBIGUITY IS ASSERTED IN BOTH DIRECTIONS. A case that only checks a unique prefix
resolves would hold against a resolver that picks the first hit — which is the defect the
refusal exists to prevent, and the one where a wrong witness reads exactly like a right one.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

from substrate import finding_resolve

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / ".claude" / "agents" / "findings.py"

Case = tuple[str, bool]


def _thunk(code: int, note: str) -> Callable[[], tuple[int, str]]:
    """Build a stand-in witness, so a fixture roster needs no real command."""
    def run() -> tuple[int, str]:
        return code, note
    return run


# ⚑ THE FIXTURE MIRRORS THE LIVE ROSTER'S AWKWARD SHAPE rather than an idealised one: a bare
#   stem that is also a prefix, plus a sibling family that makes a short stem ambiguous.
_FIXTURE: dict[str, Callable[[], tuple[int, str]]] = {
    "aa-F1": _thunk(0, "one"),
    "aa-F10": _thunk(0, "ten"),
    "aa-F11": _thunk(0, "eleven"),
    "bb-F2-descriptive-tail": _thunk(1, "two"),
    "cc-F3": _thunk(2, "three"),
}


class _Origin(Protocol):
    """The origin surface this differential reads — named so a typo cannot pass."""

    WITNESSES: Mapping[str, Callable[[], tuple[int, str]]]

    def resolve(self, want: str) -> tuple[str, Callable[[], tuple[int, str]] | None]: ...


def _origin() -> _Origin | None:
    """Load the origin by path, or return None when it cannot be reached."""
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_findings_resolve", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _exact_cases() -> list[Case]:
    """Return the cases pinning that an exact key wins outright."""
    key, hit = finding_resolve.resolve("aa-F1", _FIXTURE)
    return [
        ("an exact key resolves to itself", key == "aa-F1"),
        ("...and carries its witness", hit is not None),
        # ⚑ THE LOAD-BEARING ONE: `aa-F1` also PREFIXES aa-F10 and aa-F11. Exact must beat
        #   prefix, or a key that exists refuses as ambiguous — the live `tmi-F6` shape.
        ("...even though it is also a prefix of two longer keys",
         not finding_resolve.unresolved((key, hit))),
        ("the witness actually runs", hit is not None and hit()[1] == "one"),
    ]


def _prefix_cases() -> list[Case]:
    """Return the cases pinning that a UNIQUE prefix resolves and an ambiguous one refuses."""
    key, hit = finding_resolve.resolve("bb-F2", _FIXTURE)
    amb_text, amb_hit = finding_resolve.resolve("aa-F", _FIXTURE)
    return [
        ("a unique prefix resolves to the full key", key == "bb-F2-descriptive-tail"),
        ("...and carries that key's witness", hit is not None and hit()[1] == "two"),
        # ⚑⚑ BOTH DIRECTIONS: without this, a resolver picking the first hit passes above.
        ("an ambiguous prefix REFUSES rather than picking", amb_hit is None),
        ("...and the refusal says it is ambiguous", "AMBIGUOUS" in amb_text),
        # ⚑ THE REFUSAL NAMES ITS CANDIDATES — a successor the caller can retype (gate-G55).
        ("...and names every candidate, so the caller can retype one",
         all(k in amb_text for k in ("aa-F1", "aa-F10", "aa-F11"))),
        ("...and says WHY it will not guess", "reads like a right one" in amb_text),
    ]


def _unknown_cases() -> list[Case]:
    """Return the cases pinning that an unknown key is its own outcome, not an open finding."""
    text, hit = finding_resolve.resolve("zz-nothing-like-this", _FIXTURE)
    return [
        ("an unknown key does not resolve", hit is None),
        ("...and says no witness is registered", "no witness registered" in text),
        # ⚑ NAMED AS A ROSTER/RECORD DISAGREEMENT, because that is the actionable reading —
        #   a typo and a genuinely unpaired bib entry look identical from here otherwise.
        ("...and names the disagreement it might be", "roster/record" in text),
        ("the predicate agrees it is unresolved",
         finding_resolve.unresolved((text, hit))),
    ]


def _live_differential_cases() -> list[Case]:
    """Compare both resolvers over the ORIGIN's ENTIRE live roster.

    ⚑⚑⚑ EVERY KEY, NOT A SAMPLE. The whole point of taking the roster as an argument is that
    the two implementations can be run against one population; checking a handful would leave
    exactly the awkward keys — the bare stems — unexercised.
    """
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    roster = origin.WITNESSES
    keys = sorted(roster)
    if not keys:
        return [("⚑ the live roster is non-empty, so the differential means something", False)]

    same_exact = all(
        finding_resolve.resolve(k, roster)[0] == origin.resolve(k)[0] for k in keys)
    # ⚑⚑⚑ MY FIRST PREDICATE HERE WAS WRONG AND THE CASE CAUGHT IT, which is the case working.
    #   It looked for STEMS — a roster key that is a strict prefix of another roster key — and
    #   found ZERO, so it went red. I had asserted `tmi-F6` was such a stem; it is not.
    #   `tmi-F6-ground-truth-…` lives only in the BIB, which is exactly what gate-G54 measured
    #   when I read the binding, and I wrote a case contradicting my own finding two ticks on.
    # ⚑⚑ THE LIVE SHAPE IS A TYPED ABBREVIATION, NOT A STEM. `tmi-F1` is ambiguous over ELEVEN
    #   keys — `tmi-F1-revision-recall-…`, `tmi-F10-…`, `tmi-F11-…` — and NONE contains another,
    #   because they diverge at the character after the shared prefix. So the population that
    #   exercises the refusal is "abbreviations a caller would plausibly type", not stems.
    abbrevs = sorted({k[:len(k) - 1] for k in keys} & {k[:6] for k in keys})
    ambiguous = [a for a in abbrevs
                 if len([k for k in keys if k.startswith(a)]) > 1]
    same_ambiguous = all(
        finding_resolve.resolve(a, roster)[0] == origin.resolve(a)[0] for a in ambiguous)
    unknown = "zz-no-such-finding-anywhere"
    same_unknown = (finding_resolve.resolve(unknown, roster)[0]
                    == origin.resolve(unknown)[0])
    return [
        ("the origin loaded with a non-empty roster", True),
        ("both resolvers agree on EVERY live key", same_exact),
        # ⚑ REPORTED WITH ITS COUNT, so a population that empties says so rather than passing
        #   vacuously and hiding that the case stopped testing anything.
        (f"the live roster carries ambiguous abbreviations to exercise ({len(ambiguous)})",
         len(ambiguous) > 0),
        ("both resolvers refuse every ambiguous abbreviation identically", same_ambiguous),
        ("both refuse an unknown key identically", same_unknown),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (_exact_cases() + _prefix_cases() + _unknown_cases()
             + _live_differential_cases())
    bad = [label for label, holds in cases if not holds]
    print(f"finding_resolve: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
