#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the roster readers on fixtures.

⚑⚑⚑ THE FIXTURES ARE THE POINT OF THE PARAMETER. The readers take the roster as an argument, so a
case pinning `resolve`'s ambiguity refusal states its collision in three lines and a case pinning
the zero row names a kind nothing uses — neither has to be discovered in the live ledger.

⚑⚑ THE LIVE DIFFERENTIAL RETIRED WITH THE ROSTER IT READ. It loaded `.claude/agents/findings.py`'s
`WITNESSES` literal by path and asserted this module reproduced the ledger's own `--kinds` numbers;
it agreed. The roster then moved into the bibs (W40) and `findings.py` became a shim with no
literal to load, so that arm has nothing to difference. The kind vocabulary it certified,
`KIND_ORDER`, is now checked against the bibs by `witness_bibrows_selftest`.

⚑ THE FIVE-ZEROES LESSON STAYS IN THE FIXTURE. `group_by_kind` reads each witness's
`__code__.co_names` for a helper name with a LEADING UNDERSCORE; the origin once omitted it and
every witness landed in `?`. The fixture's witnesses call `_standing` / `_refuses`, so a broken
underscore match fails the grouping cases here.
"""

from __future__ import annotations

import sys

from substrate import witness_roster as wr

_PAIR_ROWS = 2

Case = tuple[str, bool]


def _standing(why: str) -> tuple[int, str]:
    """Mirror the origin's `_standing` helper closely enough for `co_names`."""
    return 0, why


def _refuses(why: str) -> tuple[int, str]:
    """Mirror the origin's `_refuses` helper closely enough for `co_names`."""
    return 0, why


def _standing_witness() -> tuple[int, str]:
    """Stand in for a `standing` witness: its code object must name `_standing`."""
    return _standing("a measured fact")


def _refuses_witness() -> tuple[int, str]:
    """Stand in for a `refuses` witness."""
    return _refuses("a refusal")


def _fixture() -> wr.Roster:
    """Return a small roster whose collisions are stated rather than discovered."""
    return {
        "aa-F1": _standing_witness,
        "aa-F10": _refuses_witness,
        "bb-F2": _standing_witness,
    }


def _resolve_cases() -> list[Case]:
    """Return the cases pinning exact / prefix / ambiguous / unknown lookup."""
    r = _fixture()
    exact = wr.resolve(r, "aa-F1")
    prefix = wr.resolve(r, "bb")
    ambig = wr.resolve(r, "aa")
    unknown = wr.resolve(r, "zz-F9")
    return [
        # ⚑ EXACT WINS OUTRIGHT even though "aa-F1" also prefixes "aa-F10". Without this the
        #   bare-stem keys minted early become unreachable the day a longer key lands.
        (
            "an exact key resolves even when it prefixes another",
            isinstance(exact, wr.Resolved) and exact.key == "aa-F1",
        ),
        ("a unique prefix resolves", isinstance(prefix, wr.Resolved) and prefix.key == "bb-F2"),
        ("an ambiguous prefix is REFUSED", isinstance(ambig, wr.Unresolved)),
        (
            "the ambiguity refusal lists its candidates",
            isinstance(ambig, wr.Unresolved) and "aa-F10" in ambig.reason,
        ),
        ("an unknown key is REFUSED", isinstance(unknown, wr.Unresolved)),
        # ⚑ UNKNOWN and OPEN are different facts; the refusal must not read as debt.
        (
            "the unknown refusal says no witness is registered",
            isinstance(unknown, wr.Unresolved) and "no witness registered" in unknown.reason,
        ),
    ]


def _kind_cases() -> list[Case]:
    """Return the cases pinning grouping, the zero row, and the derived falsifiable set."""
    by = wr.group_by_kind(_fixture())
    named = dict(wr.kind_rows(by))
    return [
        ("a standing witness groups as standing", "standing" in by),
        ("a refuses witness groups as refuses", "refuses" in by),
        ("the grouping is not all-unknown", "?" not in by),
        # ⚑ THE ZERO ROW IS THE CONTRACT: an unused kind must still be REPORTED.
        ("every declared kind appears in the rows", all(k in named for k in wr.KIND_ORDER)),
        ("an unused kind reports zero rather than vanishing", named.get("excludes") == 0),
        # ⚑ BEHAVIOURAL IS DERIVED, not spelled beside the order — the stale-tuple defect.
        (
            "behavioural excludes the non-falsifiable kinds",
            "standing" not in wr.BEHAVIOURAL and "unwitnessed" not in wr.BEHAVIOURAL,
        ),
        ("behavioural includes excludes:", "excludes" in wr.BEHAVIOURAL),
        ("the fixture counts one behavioural witness", wr.behavioural_count(by) == 1),
    ]


def _restem_cases() -> list[Case]:
    """Return the cases pinning de-duplication before counting."""
    one = wr.restem(["tmi-F6"], ["tmi-F6-ground-truth-reduced-to-count"])
    # ⚑ THE TRAILING HYPHEN: without it "tmi-F1" would pair with "tmi-F10-…".
    hyphen = wr.restem(["tmi-F1"], ["tmi-F10-a-different-finding"])
    many = wr.restem(["x-F1"], ["x-F1-one", "x-F1-two"])
    return [
        ("a stem and its descriptive key pair up", len(one.spelling_pairs) == 1),
        ("a pair is removed from BOTH unpaired lists", not one.witness_only and not one.bib_only),
        ("true drift counts a pair ONCE", one.true_drift == 1),
        ("the raw count is higher than the true drift", one.raw_unpaired == _PAIR_ROWS),
        ("a hyphen-less prefix does NOT pair", len(hyphen.spelling_pairs) == 0),
        (
            "the unpaired rows survive a non-pair",
            len(hyphen.witness_only) == 1 and len(hyphen.bib_only) == 1,
        ),
        # ⚑ AMBIGUITY IS REPORTED, NOT RESOLVED.
        (
            "an ambiguous stem stays witness-only rather than guessing",
            not many.spelling_pairs and many.witness_only == ["x-F1"],
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _resolve_cases() + _kind_cases() + _restem_cases()
    bad = [label for label, holds in cases if not holds]
    sys.stdout.write(f"witness_roster: {len(cases) - len(bad)}/{len(cases)}\n")
    for label in bad:
        sys.stdout.write(f"  FAIL {label}\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
