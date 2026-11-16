#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The T25 family — where a witness lives, what it takes, and what it reaches for.

⚑⚑⚑ THE AGGREGATE IS A PREMISE EDGE, NOT A RE-RUN. The original `T25` invoked each of its three
routes, redirected stdout into a buffer to swallow their output, and read the return codes — an
aggregate that measures nothing itself but must EXECUTE everything to say so. Under the family
shape that relationship is DECLARED: `T25` rests on its three routes, and a reader asks the
roster rather than the interpreter. The original's own docstring already argued the principle —
*"an aggregate rests on its parts and measures nothing itself"* — while the code could only
express it by running them.

⚑⚑ AND THE THREE ROUTES ARE ONE QUESTION AT THREE GRAINS, which is what makes this a family. WHERE
a witness is defined (`T25-library`), whether it TAKES its inputs (`T25-parametric`), whether it
READS a sibling's state (`T25-globals`). `library_shape` answers all three from one walk, so the
bodies stop re-deriving the same parse three times.

⚑⚑ AND THE CLOSING FIGURE MEANT THE WRONG THING (⟡t25-figure-meaning). When the split landed,
`T25-library` closed at *"4 witness(es) in the keyed library"* — the four DISPATCH functions in
`concepts.py` — while that library binds ~50 readers across two tables. **A closed item whose
number describes something else is how a stale claim gets quoted onward.** The library is now
ASKED what it answers rather than counted; reading its definitions measures how it is
IMPLEMENTED, which is the distinction the split created and the counting reader predates.

⚑ MEASURED BEFORE WRITING, and the population is not what the original reports. On the live
dispatch module: 65 definitions, 1 non-parametric, and 6 reading shared state — where all six are
the RETIRED LEGACY ACCESSORS themselves (`sizes_of`, `rowsum`, `_open`, `_closed`, `_drain`,
`_selftest`), not witnesses reaching sideways. The original counted every definition whose SOURCE
TEXT contained the name, which is the false-population defect it records twice in its own
docstrings.

⚑⚑ THE FIGURE COMES FROM `warrant_records` AND THE EXCEPTION FROM `warrant_bib` (gate-G209). The
engine half — `records` / `claim_of` / `tag` — imports paperkit at module scope and lives in its
own module; `WarrantError` stays with the config half precisely so a caller catching it need not
import the engine to name the exception it is catching. ⚑ MYPY WAS ALREADY REPORTING
`Module has no attribute "tag"` on the old spelling, so this repoint pays a gate finding the file
was carrying independently of the AttributeError its suite died on.

⚑ EXTRACTED FROM `catalog/library/items.py` (⟡items-n-split), rewritten rather than moved.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from mikemol.witness import witness_family, witness_row
from mikemol.witness.warrant_bib import WarrantError

from substrate import (
    library_module,
    library_shape,
    warrant_records,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

# The keyed library, by the name its loader resolves.
LIBRARY = "concepts"


class Keyed(Protocol):
    """The part of the keyed library this witness asks.

    ⚑ A PROTOCOL RATHER THAN `getattr`. A defaulted attribute read returns `Any` and carries it
    into every branch below — the boundary this repo narrows at the seam. Declaring the one
    method consulted keeps the reader typed and states the dependency as one call.
    """

    def keys(self) -> tuple[str, ...]:
        """Return every key the library answers."""
        ...


# ⚑ THE FAMILY, DECLARED. The apex states what having all three routes establishes — which no one
# route says alone — and `subject` names what the family is parameterized over, so a dispatch
# module gaining a witness gains a subject without an edit here.
FAMILY = witness_family.of(
    key="T25",
    apex="a witness takes what it needs as arguments rather than reading another witness's "
    "globals, and lives in a keyed library the dispatch reads",
    subject="the top-level definitions in the witness library",
    members=[
        witness_family.Member(
            name="the_witnesses_live_in_a_keyed_library",
            claim="the structure IS the claim, so the predicate is structural: does the library "
            "exist, does it hold the witnesses, is the dispatch reduced to the roster. "
            "Counting witnesses in the right file would pass a library that exists and is "
            "empty",
        ),
        witness_family.Member(
            name="every_witness_takes_what_it_needs",
            claim="zero-argument is not the defect — a witness with its data INLINE reaches for "
            "nothing and is parametric in the sense that matters. What disqualifies is the "
            "REACH, so a witness that neither takes its inputs nor carries them is counted",
        ),
        witness_family.Member(
            name="no_witness_reads_another_witnesss_globals",
            claim="the defect is the READ, not the signature: a census asking only whether a "
            "witness takes arguments passes one that takes them AND still reads the shared "
            "state a sibling wrote",
            premises=("every_witness_takes_what_it_needs",),
        ),
    ],
)


def library_defs() -> tuple[str, ...]:
    """Return the names the keyed library defines — empty when it does not exist.

    ⚑ THIS IS THE LIBRARY'S OWN SURFACE, NOT ITS POPULATION. It counts functions in the file; a
    dispatch that BINDS readers defines only its dispatch. `library_answers` is the population.
    """
    return tuple(w.name for w in library_shape.witnesses(library_shape.library()))


def library_answers() -> tuple[str, ...]:
    """Return the keys the library answers, or empty when it cannot be asked.

    ⚑⚑ THE LIBRARY IS ASKED, NOT COUNTED. A keyed dispatch knows what it answers; reading its
    definitions measures how it is IMPLEMENTED — the distinction the split created, and the one
    the closing figure got wrong at the moment the item closed.

    ⚑ AN UNASKABLE LIBRARY YIELDS EMPTY, and the caller reports that as unmeasured rather than as
    a library holding nothing — the two states have different repairs.
    """
    found, _why = library_module.library_module(LIBRARY)
    if found is None:
        return ()
    return cast("Keyed", found).keys()


def dispatch_defs() -> tuple[str, ...]:
    """Return the names the dispatch module still defines."""
    return tuple(w.name for w in library_shape.witnesses(library_shape.dispatch()))


def reaching() -> tuple[library_shape.Witness, ...]:
    """Return the definitions that read another witness's module state."""
    return tuple(w for w in library_shape.witnesses(library_shape.dispatch()) if w.reads_state)


def nonparametric() -> tuple[library_shape.Witness, ...]:
    """Return the definitions that neither take their inputs nor carry them."""
    return tuple(w for w in library_shape.witnesses(library_shape.dispatch()) if not w.parametric)


def _figure(key: str, name: str) -> tuple[int | None, str | None]:
    """Return the figure a claim declares, or why it could not be read."""
    try:
        return warrant_records.tag(key, name), None
    except WarrantError as exc:
        return None, str(exc)


def witness_library(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield the verdict for where the witnesses are defined."""
    want, why = _figure(key, figure)
    if want is None:
        yield witness_row.opened(key, f"the claim carries no [{figure}=N] tag: {why}")
        return

    lib = library_shape.library()
    if not lib.exists():
        yield witness_row.part(key, str(lib), route="create the keyed library")
        yield witness_row.opened(
            key,
            "no keyed library — the witnesses are defined in the dispatch module itself, "
            "so the roster and the claims share a home",
        )
        return

    here = dispatch_defs()
    for name in here:
        yield witness_row.part(key, name, route="move to the keyed library")
    if here:
        yield witness_row.opened(
            key,
            f"{len(here)} witness(es) still defined in the dispatch module rather than the "
            f"library: {', '.join(sorted(here)[:6])}",
        )
        return

    answered = library_answers()
    if not answered:
        # ⚑ AN EMPTY LIBRARY IS NOT A CLOSED ITEM. The original's own docstring says counting
        # "witnesses in the right file" would pass a library that exists and is empty; moving
        # every definition OUT of the dispatch achieves that state exactly.
        #
        # ⚑⚑ AND THE ANSWER-COUNT IS WHAT MAKES THAT CHECK REAL. Counting DEFINITIONS could not
        # distinguish a library that binds fifty readers from one that binds none — both hold a
        # handful of dispatch functions — so the emptiness this branch guards against was
        # unreachable by the reader that guarded it.
        yield witness_row.opened(
            key,
            "the library exists and answers no key — the dispatch is empty because the "
            "witnesses were removed, not because they were bound",
        )
        return
    yield witness_row.closed(key, f"the keyed library answers {len(answered)} item(s)")


def witness_parametric(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield one part per witness that neither takes its inputs nor carries them."""
    want, why = _figure(key, figure)
    if want is None:
        yield witness_row.opened(key, f"the claim carries no [{figure}=N] tag: {why}")
        return

    found = nonparametric()
    for got in found:
        yield witness_row.part(key, got.name, route="take inputs as arguments")

    if len(found) != want:
        yield witness_row.opened(
            key,
            f"claim says {want}; {len(found)} witness(es) neither take their inputs nor "
            f"carry them: {', '.join(w.name for w in found[:6]) or 'none'}",
        )
        return
    if found:
        yield witness_row.opened(key, f"{len(found)} witness(es) still reach")
        return
    yield witness_row.closed(key, "every witness takes what it needs")


def witness_globals(key: str, figure: str) -> Iterator[witness_row.Part | witness_row.Verdict]:
    """Yield one part per witness reading another witness's module state."""
    want, why = _figure(key, figure)
    if want is None:
        yield witness_row.opened(key, f"the claim carries no [{figure}=N] tag: {why}")
        return

    found = reaching()
    for got in found:
        yield witness_row.part(key, got.name, route=f"pass in {', '.join(got.reads_state)}")

    if len(found) != want:
        yield witness_row.opened(
            key,
            f"claim says {want}; {len(found)} definition(s) read shared state: "
            f"{', '.join(w.name for w in found) or 'none'}",
        )
        return
    if found:
        yield witness_row.opened(key, f"{len(found)} definition(s) still read shared state")
        return
    yield witness_row.closed(key, "no witness reads another witness's globals")
