#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Exercise the bib reader's totality probe against inputs it has not seen.

⚑⚑⚑ THE ALGEBRA / COALGEBRA DISTINCTION IS THE ITEM. *"`--entries` reporting 42 of 42"* is an
ALGEBRA statement: at THIS input, the parser agrees with a second reading of the same bytes. The
hazard is a COALGEBRA one — what the map does to inputs it has NOT seen. Measured on the live
bib: 0 quoted fields, 0 bare-integer fields. **That says the kernel is UNWITNESSED, not empty**,
and an unwitnessed kernel is the dangerous case, because nothing exercises it and its first
firing is invisible.

⚑⚑ SO PRESENCE IS NOT BEHAVIOUR, AND THIS ITEM EXISTS BECAUSE THAT WAS GOT WRONG ONCE. The
question is never *"is `--roundtrip` defined"*. Each silent-drop input is CONSTRUCTED and the
probe must REPORT it: a probe returning `[]` on a corrupted file is decoration, and it reads as a
clean census. `roundtrip(live) == []` is necessary and nowhere near sufficient — it is exactly
the algebra result that motivated the item.

⚑⚑ ONE CLASS FABRICATES RATHER THAN OMITS, WHICH MAKES IT THE WORST. A `%` comment mentioning
`@misc{K,` was read as a real header, and the entry regex then swallowed the following entry
whole: the reader reported `GHOST / 1 of 1 entry` — the real entry gone, a FICTIONAL one in its
place, and a clean `n of m` over a file it had misread. **A missing row can be caught by a
denominator; an invented row corroborates itself.** That case is asserted on the READER, not on
the probe: what must hold is that a comment is no longer read as a header.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from substrate import scratch_module

# The tool whose parser this probes.
READER = "bibstruct"

# The mode that answers totality. ⚑ ITS ABSENCE IS THE FIRST FINDING: without it every census
# over the bib is a count of what its parser can see.
PROBE_MODE = "roundtrip"

# Each fixture is a construct the parser is known to lose SILENTLY — it returns success with
# data gone. The probe must name every one.
SILENT_DROPS = {
    "indented closing brace loses the whole entry": "@misc{A,\n  claim = {a}\n}\n\n@misc{B,\n  claim = {b}\n  }\n",
    "a one-line entry is lost whole": "@misc{A,\n  claim = {a}\n}\n\n@misc{B, claim = {b}}\n",
    "a quoted value leaves a HOLE in a present entry": '@misc{A,\n  claim = {a},\n  from = "B"\n}\n',
    "a bare-integer value leaves a hole": "@misc{A,\n  claim = {a},\n  year = 2026\n}\n",
    "a duplicate key silently keeps the last": "@misc{A,\n  claim = {first}\n}\n\n@misc{A,\n  claim = {second}\n}\n",
}

# The fabrication fixture: a comment naming an @-key, plus one real entry.
FABRICATION = "% see @misc{GHOST, ...} for the shape\n@misc{A,\n  claim = {a}\n}\n"
GHOST_KEY = "GHOST"
REAL_KEY = "A"


class Reader(Protocol):
    """The part of the bib reader this witness exercises."""

    def roundtrip(self, path: str | None = ...) -> list[tuple[str, str, str]]:
        """Return every place the parse fails to account for the file."""
        ...

    def entries(self, path: str | None = ...) -> dict[str, dict[str, str]]:
        """Return the parsed entries, keyed."""
        ...


@dataclass(frozen=True, slots=True)
class Blindness:
    """What the probe fails to report, and what it could not be asked."""

    # Silent-drop classes the probe returned nothing for.
    blind: tuple[str, ...]
    # Unaccounted-for constructs in the live bib, when the probe discriminates.
    live: int
    why: str

    @property
    def known(self) -> bool:
        """Report whether the probe could be exercised at all."""
        return not self.why

    @property
    def discriminates(self) -> bool:
        """Report whether the probe caught every constructed corruption."""
        return self.known and not self.blind


def reader() -> tuple[Reader | None, str]:
    """Load the bib reader, narrowed to the two calls this witness makes."""
    found, why = scratch_module.scratch_module(READER)
    if found is None:
        return None, f"{READER} will not load: {why}"
    if not hasattr(found, PROBE_MODE):
        return None, (
            f"no --{PROBE_MODE}: the bib reader has no totality probe, so every "
            f"census over it is a count of what its parser can see"
        )
    return cast("Reader", found), ""


def blind_classes(api: Reader, where: Path) -> tuple[str, ...]:
    """Return the silent-drop classes the probe does not report.

    ⚑ A PROBE RETURNING `[]` ON A CORRUPTED FILE IS DECORATION. Each fixture is written and fed
    back; a class the probe stays silent about is one the live census cannot see either.
    """
    blind: list[str] = []
    for label, text in sorted(SILENT_DROPS.items()):
        path = where / "probe.bib"
        path.write_text(text, encoding="utf-8")
        if not api.roundtrip(str(path)):
            blind.append(label)
    return tuple(blind)


def fabricates(api: Reader, where: Path) -> bool:
    """Report whether a commented @-key is read as a real entry.

    ⚑⚑ ASSERTED ON THE READER, NOT THE PROBE. A probe that merely REPORTED a swallowed entry
    would still leave the census inventing a key; what must hold is that the comment never
    becomes a header in the first place.
    """
    path = where / "comment.bib"
    path.write_text(FABRICATION, encoding="utf-8")
    got = api.entries(str(path))
    return GHOST_KEY in got or REAL_KEY not in got


def kernel() -> Blindness:
    """Exercise the probe against every known silent-drop class."""
    api, missing = reader()
    if api is None:
        return Blindness(blind=(), live=0, why=missing)

    with tempfile.TemporaryDirectory() as tmp:
        where = Path(tmp)
        blind = list(blind_classes(api, where))
        if fabricates(api, where):
            blind.append(
                "a %-comment @-key is read as an entry (FABRICATION: the reader "
                "invents a key and loses the real one)"
            )

    if blind:
        return Blindness(blind=tuple(blind), live=0, why="")

    # ⚑ NECESSARY, NOT SUFFICIENT — the algebra result that motivated the item.
    return Blindness(blind=(), live=len(api.roundtrip()), why="")


def render(got: Blindness) -> str:
    """Render the verdict, keeping unexercised distinct from clean."""
    if not got.known:
        return f"  UNEXERCISED — {got.why}"
    if got.blind:
        head = f"  the probe is BLIND to {len(got.blind)} silent-drop class(es):"
        return "\n".join([head, *(f"    ⚑ {label}" for label in got.blind)])
    if got.live:
        return (
            f"  the probe discriminates, but the LIVE bib does not round-trip: "
            f"{got.live} unaccounted-for construct(s)"
        )
    return "  the probe reports every known silent-drop class, and the live bib round-trips"


if __name__ == "__main__":
    import sys

    sys.stdout.write(render(kernel()) + "\n")
    sys.exit(0)
