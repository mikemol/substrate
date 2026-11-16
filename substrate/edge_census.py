#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report which edge-shaped fields the corpus actually uses, and which each reader knows.

⚑⚑⚑ TWO READERS NAME ONE VOCABULARY, AND A FIELD IN ONE BUT NOT THE OTHER IS THE DEFECT. The
engine's `_LIST` fixes which bib fields parse as key LISTS; the local reader `raw_bib.EDGE_FIELDS`
names its own set. That is the `census-keyed-on-one-spelling` shape: a relation written in a field
the local reader does not scan is invisible to every witness built on that reader, and such a
witness reports ZERO rather than an error.

⚑⚑ THIS DOCSTRING PREVIOUSLY ASSERTED *"the engine has no such attribute"* AND THAT WAS FALSE.
`_LIST` is bound at `bib.py:48` and is live module-wide. The claim was reached by three plausible
readings in a row: `pydoc` does not list a `_`-prefixed name, so the attribute read as ABSENT; that
made the existing `T28_EDGES` witness citing `_LIST` look like it named something invented; and the
correction then came from the engine's module DOCSTRING rather than from the binding. The docstring
names three fields and the constant carries four — `consumes` was added and the prose did not
follow. **`pycodemod --binding _LIST` answers it in one call, and did.** Kept as residue because
the wrong claim was written into the artefact built to prevent wrong claims.

⚑ SO THIS REPORTS THREE POPULATIONS, NOT A VERDICT. What the corpus USES, what the local reader
SCANS, and what the engine CARRIES — because a single number cannot distinguish *"nobody writes
that field"* from *"nothing looks for it"*.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from mikemol.witness import raw_bib

from substrate import engine_edges, warrant_bib

if TYPE_CHECKING:
    from pathlib import Path


@dataclass(frozen=True, slots=True)
class Census:
    """The three populations, kept apart because one number cannot separate them."""

    used: tuple[str, ...]
    scanned: tuple[str, ...]
    carried: tuple[str, ...]

    @property
    def used_but_unscanned(self) -> tuple[str, ...]:
        """Return fields the corpus writes that the local reader does not look for.

        ⚑ THE DANGEROUS DIRECTION. A relation stated in one of these is invisible to every
        witness built on the local reader, and such a witness reports zero — a false green
        rather than a missing row.
        """
        return tuple(f for f in self.used if f not in self.scanned)

    @property
    def scanned_but_unused(self) -> tuple[str, ...]:
        """Return fields the local reader scans that no entry writes.

        ⚑ NOT A DEFECT BY ITSELF: a reader may legitimately anticipate a field. It becomes one
        when the field is also absent from the engine's roster, since then nothing can ever write
        it and the entry is dead vocabulary.
        """
        return tuple(f for f in self.scanned if f not in self.used)


def candidates() -> tuple[str, ...]:
    """Return every field either reader treats as an edge, in a stable order, deduplicated.

    ⚑ THE ENGINE'S HALF IS A CALL, NOT A MODULE CONSTANT. `engine_edges.edge_fields()` reads at
    CALL time; a constant would bind at import and freeze whatever the engine held when this
    module first loaded — the same staleness a local copy has, moved one layer in and made harder
    to see.
    """
    seen: list[str] = []
    for field in (*raw_bib.EDGE_FIELDS, *engine_edges.edge_fields()):
        if field not in seen:
            seen.append(field)
    return tuple(seen)


def edge_shaped(corpus: raw_bib.Corpus, names: tuple[str, ...]) -> tuple[str, ...]:
    """Return the candidate fields at least one entry in `corpus` actually carries."""
    present = {field for fields in corpus.entries.values() for field in fields}
    return tuple(name for name in names if name in present)


def census(path: Path | None = None) -> Census:
    """Read the corpus and report the three edge-field populations."""
    corpus = raw_bib.read(path if path is not None else warrant_bib.BIB)
    return Census(
        used=edge_shaped(corpus, candidates()),
        scanned=tuple(raw_bib.EDGE_FIELDS),
        carried=engine_edges.edge_fields(),
    )


def render(got: Census) -> str:
    """Return the census as text, naming each population's question."""
    lines = [
        f"  used by the corpus   : {', '.join(got.used) or 'none'}",
        f"  scanned by raw_bib   : {', '.join(got.scanned)}",
        f"  carried by the engine: {', '.join(got.carried)}",
    ]
    gap = got.used_but_unscanned
    if gap:
        lines.append(
            f"  ⚑ WRITTEN BUT NOT SCANNED: {', '.join(gap)} — "
            f"a witness over raw_bib cannot see these"
        )
    dead = got.scanned_but_unused
    if dead:
        lines.append(f"  scanned but unwritten: {', '.join(dead)}")
    return "\n".join(lines) + "\n"


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE, and it DELEGATES rather than
# exiting 0 — a no-op guard reports nothing, which the outcome classifier calls `silent`.
#
# ⚑⚑ THIS TRAILER WAS TEMPORARILY REMOVED TO BREAK A PER-FILE-GATE DEADLOCK, and the shape is
# worth recording. The gate checks an edited file's whole IMPORT CLOSURE, so a module and its
# suite that reference each other become MUTUALLY unwritable the moment one carries a stale name:
# each edit is judged against the other's current state, and neither can be the one that moves
# first. Deleting the suite did not help — a refused write leaves NO file, so the module then
# failed on a missing import instead. Cutting THIS edge made the suite independently writable,
# and the trailer went back afterwards.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import edge_census_selftest

        sys.exit(edge_census_selftest.selftest())
    sys.stdout.write(render(census()))
    sys.exit(0)
