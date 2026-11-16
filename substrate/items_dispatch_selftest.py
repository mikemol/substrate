#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `catalog/library/items.py` — the roster and its dispatch.

⚑⚑⚑ THE TRANSLATION IS THE ITEM. Consumers read dict rows across fourteen import sites; the
extracted readers emit `witness_row` records. One function converts at the boundary, and a
mistranslation would be invisible to both sides — the readers keep emitting valid records, the
consumers keep receiving valid-looking dicts, and only a case comparing them can say the fields
carried across.

⚑⚑ AND THE ROSTER IS THE LIBRARY'S. A key-to-function dict in the dispatch module would be two
authorities on what exists, disagreeing the first time either moved — the frozen-roster defect
this arc found at six separate sites. The arm below asserts the roster IS what the library
answers, never a count.

⚑ THE DRAIN CONTRACT IS `(rc, parts_forwarded)`, and the second half is what the collector
counted rather than what a witness declared. A size a witness declared alongside its rows would
be a second derivation whose disagreement nothing could detect.

⚑ ONE LIVE KEY IS EXERCISED. Running every item in one process is what the exhaustive sweep is
for, with a budget its caller chose.
"""

from __future__ import annotations

import sys
from typing import Protocol, cast

from mikemol.witness import witness_row

from substrate import library_module

# The dispatch module under test.
DISPATCH = "items"

# A key no library answers.
_ABSENT = "no-such-item-key-3b77"

# The key exercised live. ⚑ CHOSEN BY COST: it reads one stamp and compares it.
_LIVE = "CENSUS"


class Dispatch(Protocol):
    """The part of the dispatch module this suite consults."""

    ITEMS: dict[str, object]
    SIZES: dict[str, int]
    WHY: dict[str, str]
    PARTS: dict[str, list[str]]
    VERDICT: str
    PART: str

    def item_keys(self) -> tuple[str, ...]:
        """Return every registered key."""
        ...

    def as_row(self, got: witness_row.Part | witness_row.Verdict) -> dict[str, str]:
        """Translate a reader record into a dict row."""
        ...

    def part(self, key: str, name: str) -> dict[str, str]:
        """Build a part row."""
        ...

    def verdict(self, key: str, state: str, why: str) -> dict[str, str]:
        """Build a verdict row."""
        ...

    def main(self, argv: list[str]) -> int:
        """Run the named items."""
        ...


def dispatch() -> tuple[Dispatch | None, str | None]:
    """Load the dispatch module, narrowed to the surface this suite uses."""
    found, why = library_module.library_module(DISPATCH)
    if found is None:
        return None, why
    return cast("Dispatch", found), None


def the_dispatch_loads(out: list[str]) -> int:
    """Check the module is reachable at all.

    ⚑ EVERY OTHER ARM DEPENDS ON THIS, so asserting it first makes a packaging failure read as a
    packaging failure rather than as a dozen unrelated defects.
    """
    api, why = dispatch()
    if api is None:
        out.append(f"selftest: the dispatch did not load: {why!r}")
        return 1
    return 0


def a_verdict_record_translates_to_a_verdict_row(out: list[str]) -> int:
    """Check a reader's verdict becomes a consumer's verdict row — THE ITEM.

    ⚑⚑⚑ A MISTRANSLATION IS INVISIBLE TO BOTH SIDES. The reader keeps emitting valid records and
    the consumer keeps receiving valid-looking dicts; only comparing them says the fields carried
    across.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    got = api.as_row(witness_row.closed("K", "all clear"))
    if got.get("kind") != api.VERDICT:
        out.append(f"selftest: a verdict translated to {got!r}")
        return 1
    if got.get("key") != "K" or got.get("why") != "all clear":
        out.append(f"selftest: the verdict lost a field: {got!r}")
        return 1
    return 0


def a_part_record_translates_to_a_part_row(out: list[str]) -> int:
    """Check a reader's part becomes a consumer's part row."""
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    got = api.as_row(witness_row.part("K", "a-finding"))
    if got.get("kind") != api.PART or got.get("name") != "a-finding":
        out.append(f"selftest: a part translated to {got!r}")
        return 1
    return 0


def a_route_survives_translation(out: list[str]) -> int:
    """Check a part's repair reaches the row.

    ⚑ A ROUTE IS WHAT MAKES A FINDING ACTIONABLE, and dropping it at the seam would leave every
    consumer re-deriving the repair the reader already named.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    got = api.as_row(witness_row.part("K", "a-finding", route="fix it"))
    if got.get("route") != "fix it":
        out.append(f"selftest: the route did not survive: {got!r}")
        return 1
    return 0


def a_routeless_part_carries_no_route(out: list[str]) -> int:
    """Check a part with no repair does not invent one.

    ⚑ AN EMPTY ROUTE ON A ROW READS AS A FINDING WITH NO FIX, which is worse than no column: it
    trains a reader to ignore the field.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    got = api.as_row(witness_row.part("K", "a-finding"))
    if "route" in got:
        out.append(f"selftest: a routeless part carries a route: {got!r}")
        return 1
    return 0


def the_roster_is_the_librarys(out: list[str]) -> int:
    """Check the registered keys are exactly what the library answers.

    ⚑⚑ TWO AUTHORITIES ON WHAT EXISTS disagree the first time either moves. Asserting identity
    rather than a count is what keeps the library free to gain a reader without an edit here.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    if set(api.ITEMS) != set(api.item_keys()):
        out.append("selftest: the roster disagrees with the library")
        return 1
    return 0


def the_roster_is_not_empty(out: list[str]) -> int:
    """Check the dispatch registers items.

    ⚑ AN EMPTY ROSTER PASSES THE IDENTITY ARM ABOVE, vacuously — the collection-destruction shape
    only a non-empty claim can catch.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    if not api.ITEMS:
        out.append("selftest: the roster is empty")
        return 1
    return 0


def the_legacy_deposits_exist(out: list[str]) -> int:
    """Check the four names consumers read are present.

    ⚑ MEASURED FROM THE CONSUMERS, NOT CHOSEN. Fourteen import sites across three modules reach
    for `ITEMS`, `SIZES`, `WHY` and `PARTS`; dropping any one is a break this suite must catch
    rather than a simplification.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    missing = [name for name in ("ITEMS", "SIZES", "WHY", "PARTS") if not hasattr(api, name)]
    if missing:
        out.append(f"selftest: the dispatch omits consumer name(s): {missing!r}")
        return 1
    return 0


def a_live_item_returns_a_code(out: list[str]) -> int:
    """Check running one item yields an exit code.

    ⚑⚑ A WELL-TYPED DISPATCH CAN STILL FAIL AT THE FIRST CALL. Wiring is what the checker proves;
    that the walk survives contact with a real reader is what only running it shows.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    try:
        rc = api.main(["items", _LIVE])
    except Exception as exc:  # noqa: BLE001 — any failure is this case's finding
        out.append(f"selftest: running {_LIVE} raised {type(exc).__name__}: {exc}")
        return 1
    if rc not in (0, 1):
        out.append(f"selftest: running {_LIVE} returned {rc!r}")
        return 1
    return 0


def an_unknown_key_is_refused(out: list[str]) -> int:
    """Check an unregistered key is refused rather than run.

    ⚑ THE ARGUMENT MUST BE CONSUMED. A dispatch that accepted any key and reported nothing is the
    accepted-and-ignored defect this worklist already found in its own filtering mode.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    if api.main(["items", _ABSENT]) == 0:
        out.append("selftest: an unknown key ran clean")
        return 1
    return 0


def the_verdict_carries_the_collectors_count(out: list[str]) -> int:
    """Check a verdict row is built without a declared size.

    ⚑⚑ A SIZE A WITNESS DECLARED beside its rows is a second derivation, and the disagreement
    between it and the collector's count was the only thing the old reconciliation could detect.
    The builder takes no size at all.
    """
    api, _why = dispatch()
    if api is None:
        out.append("selftest: the dispatch did not load")
        return 1
    got = api.verdict("K", "closed", "fine")
    if "size" in got:
        out.append(f"selftest: a fresh verdict carries a size: {got!r}")
        return 1
    return 0


_ARMS = (
    the_dispatch_loads,
    a_verdict_record_translates_to_a_verdict_row,
    a_part_record_translates_to_a_part_row,
    a_route_survives_translation,
    a_routeless_part_carries_no_route,
    the_roster_is_the_librarys,
    the_roster_is_not_empty,
    the_legacy_deposits_exist,
    a_live_item_returns_a_code,
    an_unknown_key_is_refused,
    the_verdict_carries_the_collectors_count,
)

_CASE_COUNT = 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"items-dispatch selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"items-dispatch selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
