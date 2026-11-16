#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The worklist roster and its dispatch — the witnesses live in `concepts.py`.

⚑⚑⚑ THIS FILE WAS 2,736 LINES CARRYING 1,804 FINDINGS, AND THAT MADE IT UNEDITABLE. The per-file
gate has no partial-credit path: an edit leaving findings is refused, so the unit of repair was
the whole file and every cheap correct change was abandoned at the door. **A module that cannot
be edited cannot be repaired** — the roster and its witnesses had become one artifact that could
only grow.

⚑⚑ SO THE SPLIT IS ROSTER HERE, CLAIMS THERE. This file says WHICH items exist and drives their
rows; `concepts.py` says WHICH READER answers each key, over two binding tables in `substrate/`.
Adding a witness is writing a module and binding it — never growing this file, which is what the
origin's shape made unavoidable.

⚑⚑ THE ROW PROTOCOL IS TRANSLATED, NOT REPLACED, BECAUSE THE CONSUMERS ARE NOT THIS FILE'S TO
CHANGE. `worklist_gate`, `wg_dispatch` and `wg_order` read `ITEMS`, `SIZES`, `WHY`, `PARTS` and
`_drain` across fourteen import sites, and they read dict rows. The readers emit `witness_row`
records. Translating at this boundary keeps both sides honest; making either conform to the other
would be a change to a file that did not ask for one.

⚑ `SIZES` AND `PARTS` SURVIVE AS THE LEGACY DEPOSIT. A witness that returns an int deposits into
them and `_drain` reads them back; a streaming witness never touches them and its size is the
count the collector made. Both paths are driven here so no consumer has to know which kind it
asked for.

⚑ EXTRACTED BY ⟡items-n-split. The witnesses are gone from this file, which is what `T25-library`
checks; what remains is the roster and the walk.
"""

from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING, Protocol, cast

from mikemol.witness import witness_row

from substrate import library_module

if TYPE_CHECKING:
    from collections.abc import Iterator

# The keyed library that answers each item.
LIBRARY = "concepts"

# The two row kinds a consumer reads.
VERDICT, PART = "verdict", "part"

# ⚑ THE LEGACY DEPOSIT, KEPT FOR THE WITNESSES THAT RETURN AN INT. A streaming witness never
# writes here; `_drain` reads these only on the legacy path, so the two cannot disagree.
SIZES: dict[str, int] = {}
WHY: dict[str, str] = {}
PARTS: dict[str, list[str]] = {}


class Concepts(Protocol):
    """The part of the keyed library this dispatch consults."""

    def keys(self) -> tuple[str, ...]:
        """Return every key the library answers."""
        ...

    def witness(self, key: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
        """Yield the rows for one key."""
        ...


def library() -> tuple[Concepts | None, str | None]:
    """Load the keyed library, narrowed to the surface this dispatch uses.

    ⚑ LOADED BY LOCATION, NOT IMPORTED BY NAME. `catalog` is unpackaged by decision — the same
    status `scratch` carries — so a named import raises. Naming it would make the checker follow
    the edge and land the followed module's findings here, which is the debt-surfacing this
    file's whole history is about.
    """
    found, why = library_module.library_module(LIBRARY)
    if found is None:
        return None, why
    return cast("Concepts", found), None


def part(key: str, name: str, **extra: str) -> dict[str, str]:
    """Build one emitted part of an item — yielded as it is FOUND, never collected."""
    row = {"kind": PART, "key": key, "name": name}
    row.update(extra)
    return row


def verdict(key: str, state: str, why: str, **extra: str) -> dict[str, str]:
    """Build the item's own row, which TRAILS its parts.

    ⚑ NO `size=` PARAMETER, DELIBERATELY. The collector counts what it forwarded; a witness that
    also declared a size would reintroduce the second derivation whose disagreement was the only
    thing the old reconciliation could detect.
    """
    row = {"kind": VERDICT, "key": key, "state": state, "why": why}
    row.update(extra)
    return row


def as_row(got: witness_row.Part | witness_row.Verdict) -> dict[str, str]:
    """Translate one reader record into the dict row consumers read.

    ⚑⚑ THE TRANSLATION IS THE SEAM, AND IT IS ONE FUNCTION. Consumers read dicts; readers emit
    records. Putting the conversion anywhere else would mean either the readers knowing the
    consumer's protocol or the consumers knowing the readers' — and the whole split exists so
    neither has to.
    """
    if isinstance(got, witness_row.Verdict):
        return verdict(got.key, got.state, got.why)
    return part(got.key, got.name, **({"route": got.route} if got.route else {}))


def item_keys() -> tuple[str, ...]:
    """Return every registered key, read from the library.

    ⚑⚑ THE ROSTER IS THE LIBRARY'S, NOT A SECOND LIST HERE. A dict of key-to-function in this
    file would be exactly the roster-beside-a-roster shape the split removes: two authorities on
    what exists, disagreeing the first time either moved. The library binds the readers; asking
    it what it answers IS the roster.
    """
    api, _why = library()
    if api is None:
        return ()
    return api.keys()


def _rows(key: str) -> Iterator[dict[str, str]]:
    """Yield one item's rows as dicts, or a single unmeasurable verdict."""
    api, why = library()
    if api is None:
        yield verdict(key, "OPEN", f"the keyed library will not load: {why}")
        return
    for got in api.witness(key):
        yield as_row(got)


def _drain(key: str, fn: object = None) -> tuple[int, int]:
    """Consume a witness's ROW STREAM, emitting each row as it arrives.

    Returns `(rc, parts_forwarded)` — the count is what this walk produced, so it cannot disagree
    with the rows the way a separately-declared `size` could.

    ⚑ THE `fn` PARAMETER IS ACCEPTED AND IGNORED, WHICH IS A MIGRATION FACT RATHER THAN A DESIGN.
    Three consumers call `_drain(key, ITEMS[key])`; the reader now comes from the library, so the
    function they pass is redundant. Accepting it keeps those call sites working unchanged — and
    changing them is a separate edit to files this split did not set out to touch.
    """
    del fn
    rc, seen = 1, 0
    for row in _rows(key):
        if row.get("kind") == PART:
            seen += 1
            sys.stdout.write(f"#row\t{json.dumps(row, sort_keys=True)}\n")
            continue
        # ⚑ THE VERDICT CARRIES THE COUNT THE COLLECTOR JUST MADE, not one the witness declared.
        # `size` is therefore a fact about what crossed the boundary rather than a second opinion
        # about the population.
        rc = 0 if row.get("state") == "closed" else 1
        # ⚑ KEPT, NOT DISCARDED. The ordering cannot rank an item without its openness, and cannot
        # know that without running the witness — so the verdict is in hand at this instant, and
        # dropping it made `--next` print a key whose sentence an operator recovered by running
        # the SAME witness again.
        WHY[key] = row.get("why", "")
        sys.stdout.write(f"item {key}: {row.get('state')} -- {row.get('why')}\n")
        # ⚑ THE SUMMARY IS BUILT AS ITS OWN DICT, not by splatting the row. `dict(row, rc=…)`
        # widens to `dict[str, Any]` under the strict bar — the int values poison the row's own
        # `str` typing — and carrying that `Any` outward is exactly what the bar exists to stop.
        summary = {**row, "rc": str(rc), "size": str(seen)}
        sys.stdout.write(f"#row\t{json.dumps(summary, sort_keys=True)}\n")
    return rc, seen


def _run(key: str) -> int:
    """Run one item and return its exit code."""
    rc, _seen = _drain(key)
    return rc


def roster() -> dict[str, object]:
    """Return the registered items, keyed.

    ⚑⚑ BUILT FROM THE LIBRARY, NOT TYPED. Consumers index this by key and call the value; building
    it from what the library answers means a reader added there is registered here with no edit —
    the frozen-roster defect this arc found at six separate sites, refused at the one place it
    would be most natural to reintroduce.
    """
    return dict.fromkeys(item_keys(), _run)


# The registered items, as consumers read them.
ITEMS: dict[str, object] = roster()


def main(argv: list[str]) -> int:
    """Run every registered item, or the ones named."""
    wanted = [got for got in argv[1:] if not got.startswith("-")]
    known = item_keys()
    keys = tuple(wanted) if wanted else known

    unknown = [key for key in keys if key not in known]
    if unknown:
        sys.stderr.write(f"unknown item key(s): {', '.join(unknown)}\n")
        return 2

    bad = 0
    for key in keys:
        bad += _run(key) != 0
    sys.stdout.write(f"  {len(keys)} item(s), {bad} open\n")
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        # ⚑ A PLAIN IMPORT, BECAUSE THE SUITE LIVES IN A PACKAGED DIRECTORY. `substrate` is in
        # `packages`; only THIS file's own directory is not, which is why the library above needs
        # a loader and the suite does not. A first cut routed the suite through the loader too and
        # produced a no-op branch the linter correctly called useless.
        from substrate import items_dispatch_selftest

        sys.exit(items_dispatch_selftest.selftest())
    sys.exit(main(sys.argv))
