#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the kind census, and pin that a DECLARED kind with no members still gets a row.

⚑⚑⚑ THE ZERO ROW IS THE PROPERTY UNDER TEST, and it is asserted by ABSENCE from the input. A
case that hands the reader every kind cannot tell a roster-driven census from one that
iterates its input — the two agree exactly when nothing is missing, which is the one condition
under which the distinction does not matter.

⚑⚑ THE MEASURED FAILURE WAS FIVE SIMULTANEOUS ZEROES from a classifier that missed a leading
underscore, caught only because five zeroes are absurd on their face. An UNDERCOUNT would have
banked silently, so the surplus row exists too: a kind the grouping produced that no
declaration names is reported, never dropped.

⚑ AND `BEHAVIOURAL` IS ASSERTED AS A DERIVATION, not as a list. Pinning its members would let
the two rosters drift apart exactly as `swarm-F3` records; pinning that it is a PREFIX of the
declared order keeps the derivation load-bearing.
"""

from __future__ import annotations

import sys

from substrate import finding_census

Case = tuple[str, bool]

# ⚑ DELIBERATELY PARTIAL: three declared kinds absent, one surplus kind present. A complete
#   fixture cannot exercise either property.
_SELFTESTS = ("a", "b", "c")
_STANDINGS = ("d", "e")
_UNWITNESSED = ("f",)
_SURPLUS = ("g",)
_SURPLUS_KIND = "a-kind-nobody-declared"

_PARTIAL: dict[str, tuple[str, ...]] = {
    "selftest": _SELFTESTS,
    "standing": _STANDINGS,
    "unwitnessed": _UNWITNESSED,
    _SURPLUS_KIND: _SURPLUS,
}


def _zero_row_cases() -> list[Case]:
    """Return the cases pinning that an unused DECLARED kind is still reported."""
    got = dict(finding_census.rows(_PARTIAL))
    ordered = [kind for kind, _ in finding_census.rows(_PARTIAL)]
    return [
        # ⚑ THE LOAD-BEARING ONE. `refuses` is absent from the input entirely; a census that
        #   iterated its input would omit the row and read as "this roster never had one".
        ("an absent declared kind gets a row", "refuses" in got),
        ("...reported as zero rather than missing", got.get("refuses") == 0),
        ("every declared kind appears",
         all(kind in got for kind in finding_census.KIND_ORDER)),
        ("a populated kind carries its count", got.get("selftest") == len(_SELFTESTS)),
        # ⚑ THE SURPLUS ROW: an unrecognised kind is a finding about the CLASSIFIER, so it is
        #   reported rather than dropped — the direction that would have caught the undercount.
        ("a kind no declaration names is still reported",
         got.get(_SURPLUS_KIND) == len(_SURPLUS)),
        # ⚑ AND THE DECLARED ROWS COME FIRST, so a reader scanning sees the contract before
        #   the anomalies.
        ("the declared rows lead, surplus trails",
         ordered[:len(finding_census.KIND_ORDER)] == list(finding_census.KIND_ORDER)),
    ]


def _derivation_cases() -> list[Case]:
    """Return the cases pinning that BEHAVIOURAL is derived, not a second roster."""
    order = finding_census.KIND_ORDER
    behavioural = finding_census.BEHAVIOURAL
    return [
        # ⚑ A PREFIX, ASSERTED AS ONE. Pinning the members would let two rosters drift apart,
        #   which is the defect the derivation exists to prevent.
        ("BEHAVIOURAL is a PREFIX of the declared order",
         order[:len(behavioural)] == behavioural),
        ("...cut at the first non-falsifiable kind",
         order[len(behavioural)] == "mode_undocumented"),
        # ⚑ THE THREE EXCLUSIONS, each for its own reason — see the module docstring.
        ("mode_undocumented is NOT behavioural", "mode_undocumented" not in behavioural),
        ("unwitnessed is NOT behavioural", "unwitnessed" not in behavioural),
        ("standing is NOT behavioural", "standing" not in behavioural),
        ("selftest IS behavioural", "selftest" in behavioural),
        ("refuses IS behavioural", "refuses" in behavioural),
    ]


def _total_cases() -> list[Case]:
    """Return the cases pinning the two totals and the distinction between them."""
    behavioural = finding_census.behavioural_total(_PARTIAL)
    vacuous = finding_census.vacuous_total(_PARTIAL)
    only_unwitnessed = {"unwitnessed": ("x", "y")}
    return [
        ("the behavioural total counts only flippable witnesses",
         behavioural == len(_SELFTESTS)),
        ("the vacuous total counts standing", vacuous == len(_STANDINGS)),
        # ⚑⚑ `unwitnessed` IS IN NEITHER, and that is the honest-gap distinction. Folding it
        #   into vacuous would report the kind that ADMITS a gap as debt.
        ("unwitnessed is absent from the vacuous total",
         finding_census.vacuous_total(only_unwitnessed) == 0),
        ("...and absent from the behavioural total",
         finding_census.behavioural_total(only_unwitnessed) == 0),
        # ⚑ AND THE SURPLUS KIND IS IN NEITHER TOTAL EITHER — reported as a row, never summed
        #   into a figure that claims to be about declared kinds.
        ("a surplus kind is reported but not totalled",
         behavioural + vacuous + len(_UNWITNESSED) + len(_SURPLUS)
         == sum(len(v) for v in _PARTIAL.values())),
    ]


def _empty_cases() -> list[Case]:
    """Return the cases pinning that an empty ledger reports every kind at zero."""
    got = dict(finding_census.rows({}))
    return [
        ("an empty ledger still reports every declared kind",
         len(got) == len(finding_census.KIND_ORDER)),
        ("...all at zero", all(count == 0 for count in got.values())),
        # ⚑ A ZERO CENSUS IS NOT A CLEAN ONE, and the totals must not imply otherwise by
        #   raising — the reader answers about an empty input rather than refusing it.
        ("the totals answer over an empty ledger",
         finding_census.behavioural_total({}) == 0
         and finding_census.vacuous_total({}) == 0),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _zero_row_cases() + _derivation_cases() + _total_cases() + _empty_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"finding_census: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
