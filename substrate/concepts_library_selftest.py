#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `catalog/library/concepts.py` — one dispatch over two reader shapes.

⚑⚑⚑ THE OVERLAP CASE IS THE ITEM. A key bound in BOTH tables would be answered twice, by two
readers that drift apart, with lookup order silently deciding which verdict a caller sees. The
dispatch cannot detect that from one lookup — only comparing the two rosters can — so the arm
below asserts the intersection is empty rather than trusting the order.

⚑⚑ THE LIBRARY IS LOADED BY LOCATION, NOT IMPORTED BY NAME, AND THE FAILURE TAUGHT THAT.
`from catalog.library import concepts` raised `ModuleNotFoundError` in a suite that type-checked
clean: `pyproject.toml` declares `packages = ["substrate", "scripts"]` and `catalog` is
deliberately absent, exactly as `scratch` is. Adding it would make mypy follow the edge and land
every finding in the followed module on the declarer — *type the callee, THEN name it*.

⚑ SO THE SURFACE IS DECLARED AS A PROTOCOL. A location-loaded module is `Any` at every reach, and
that `Any` propagates; declaring the four names this suite consults keeps the cases typed and
states the dependency as what it actually is.

⚑ ONE LIVE KEY IS EXERCISED, NOT ALL OF THEM. Running every reader in one process was killed at
exit 143 under the 192 MB lease — the exhaustive sweep is `concept_bindings.sweep()`, invoked
with a budget its caller chose.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Protocol, cast

from mikemol.witness import witness_row

from substrate import concept_bindings, concept_families, library_module

if TYPE_CHECKING:
    from collections.abc import Iterator

# The library module this suite drives.
LIBRARY = "concepts"

# A key no table answers.
_ABSENT = "no-such-concept-key-5f19"

# The key exercised live. ⚑ CHOSEN BY COST: it reads one stamp and compares it, where the
# corpus-walking readers are what put an exhaustive run over its lease.
_LIVE = "CENSUS"


class Concepts(Protocol):
    """The part of the keyed library this suite consults."""

    def keys(self) -> tuple[str, ...]:
        """Return every key the library answers."""
        ...

    def overlapping(self) -> tuple[str, ...]:
        """Return keys both tables claim."""
        ...

    def witness(self, key: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
        """Yield the rows for one key."""
        ...

    def unbound(self, registered: tuple[str, ...]) -> tuple[str, ...]:
        """Return the registered keys the library cannot answer."""
        ...


def library() -> tuple[Concepts | None, str | None]:
    """Load the keyed library, narrowed to the surface this suite uses."""
    found, why = library_module.library_module(LIBRARY)
    if found is None:
        return None, why
    return cast("Concepts", found), None


def the_library_loads(out: list[str]) -> int:
    """Check the library is reachable at all.

    ⚑⚑ EVERY OTHER ARM DEPENDS ON THIS, and without it they would all fail with the same opaque
    error. Asserting reachability first makes a packaging failure read as a packaging failure
    rather than as eleven unrelated defects.
    """
    api, why = library()
    if api is None:
        out.append(f"selftest: the library did not load: {why!r}")
        return 1
    return 0


def the_two_tables_do_not_overlap(out: list[str]) -> int:
    """Check no key is bound in both tables — THE WHOLE ITEM.

    ⚑⚑⚑ TWO READERS FOR ONE KEY answer the same question twice and drift, and the dispatch would
    report whichever the lookup order reached. A single lookup cannot see that; only comparing
    the rosters can.
    """
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    got = api.overlapping()
    if got:
        out.append(f"selftest: key(s) bound in both tables: {got!r}")
        return 1
    return 0


def the_keys_are_the_union_of_both_tables(out: list[str]) -> int:
    """Check the library answers every key either table binds.

    ⚑ A DISPATCH NARROWER THAN ITS TABLES would silently drop readers that exist — the binding
    would be live and unreachable, which reads as an absent witness.
    """
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    owed = {*concept_bindings.bound_keys(), *concept_families.bound_keys()}
    if set(api.keys()) != owed:
        out.append(f"selftest: the library omits bound key(s): {sorted(owed - set(api.keys()))!r}")
        return 1
    return 0


def the_keys_are_sorted(out: list[str]) -> int:
    """Check the enumeration is ordered, so two runs read the same."""
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    got = api.keys()
    if list(got) != sorted(got):
        out.append(f"selftest: the keys are unsorted: {got!r}")
        return 1
    return 0


def the_library_is_not_empty(out: list[str]) -> int:
    """Check the dispatch holds keys.

    ⚑ AN EMPTY LIBRARY PASSES EVERY SET-COMPARING ARM ABOVE, vacuously — the
    collection-destruction shape only a non-empty claim can catch.
    """
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    if not api.keys():
        out.append("selftest: the library answers no key")
        return 1
    return 0


def an_unbound_key_opens(out: list[str]) -> int:
    """Check a key no table answers yields an UNMEASURED verdict."""
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    rows = list(api.witness(_ABSENT))
    if len(rows) != 1 or not isinstance(rows[0], witness_row.Verdict):
        out.append(f"selftest: an unbound key emitted {rows!r}")
        return 1
    if rows[0].state != witness_row.OPEN:
        out.append(f"selftest: an unbound key read as {rows[0].state!r}")
        return 1
    return 0


def an_unbound_verdict_says_unmeasured(out: list[str]) -> int:
    """Check the unbound verdict names its own limit.

    ⚑ *"NO WITNESS IS BOUND"* IS A FACT ABOUT THIS LIBRARY, not about the tree — and a verdict
    that did not say so would read as a finding about the subject.
    """
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    verdicts = [row for row in api.witness(_ABSENT) if isinstance(row, witness_row.Verdict)]
    if not verdicts or "UNMEASURED" not in verdicts[-1].why:
        out.append(f"selftest: the unbound verdict reads as {verdicts!r}")
        return 1
    return 0


def a_family_key_dispatches_to_its_rows(out: list[str]) -> int:
    """Check a row-emitting key is answered by the family table."""
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    key = concept_families.bound_keys()[0]
    rows = list(api.witness(key))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append(f"selftest: {key} emitted no trailing verdict")
        return 1
    return 0


def a_render_key_dispatches_through_the_adapter(out: list[str]) -> int:
    """Check a rendering-shaped key is framed into rows.

    ⚑⚑ THE ADAPTER IS WHAT MAKES A RENDERING A VERDICT. Dispatching a render-shaped reader
    directly would yield a string where the caller expects rows, and the first consumer would be
    where that surfaced.
    """
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    rows = list(api.witness(_LIVE))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append(f"selftest: {_LIVE} emitted no trailing verdict: {rows!r}")
        return 1
    return 0


def the_verdict_trails_the_parts(out: list[str]) -> int:
    """Check no verdict precedes a part for an answered key.

    ⚑ A WITNESS KNOWS ITS VERDICT ONLY AFTER LOOKING — emitting it first is the
    count-before-the-walk defect, and the dispatch must not reorder what a reader emitted.
    """
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    rows = list(api.witness(_LIVE))
    if any(isinstance(row, witness_row.Verdict) for row in rows[:-1]):
        out.append(f"selftest: a verdict preceded a part: {rows!r}")
        return 1
    return 0


def a_fully_bound_roster_reports_nothing_unbound(out: list[str]) -> int:
    """Check a roster the library fully answers yields nothing owed."""
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    if api.unbound(api.keys()):
        out.append("selftest: the library reports its own keys as unbound")
        return 1
    return 0


def an_unknown_roster_key_is_reported_unbound(out: list[str]) -> int:
    """Check a registered key with no binding is named.

    ⚑ THE ROSTER IS THE CALLER'S. Holding a second copy of what exists would be the
    roster-beside-a-roster shape the split removes, so the dispatch answers about what it is
    asked about — and must actually report the gap.
    """
    api, _why = library()
    if api is None:
        out.append("selftest: the library did not load")
        return 1
    got = api.unbound((*api.keys(), _ABSENT))
    if got != (_ABSENT,):
        out.append(f"selftest: the unbound set read as {got!r}")
        return 1
    return 0


_ARMS = (
    the_library_loads,
    the_two_tables_do_not_overlap,
    the_keys_are_the_union_of_both_tables,
    the_keys_are_sorted,
    the_library_is_not_empty,
    an_unbound_key_opens,
    an_unbound_verdict_says_unmeasured,
    a_family_key_dispatches_to_its_rows,
    a_render_key_dispatches_through_the_adapter,
    the_verdict_trails_the_parts,
    a_fully_bound_roster_reports_nothing_unbound,
    an_unknown_roster_key_is_reported_unbound,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 2 + 1 + 2 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"concepts-library selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"concepts-library selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
