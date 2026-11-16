#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.concept_bindings` — a binding that type-checks may still not run.

⚑⚑⚑ A BINDING MUST BE INVOKED, AND THAT IS THE ITEM. A table of callables type-checks whether or
not the composition inside each one works: a wrong argument count, a renamed field, a reader that
raises on a missing artifact — all pass the checker and fail at the first real call. **A binding
nobody exercises is the inert guard this arc has paid for repeatedly.**

⚑⚑ BUT RUNNING ALL FIFTEEN IN ONE SUITE WAS KILLED AT EXIT 143, and the budget is the finding.
Several readers parse the whole corpus; together they exceed the 192 MB suite lease. **That is
the per-file gate's lesson at runtime** — the unit was doing too much — so this suite exercises
ONE representative binding and the exhaustive sweep is a mode a caller invokes with a budget it
chose. A suite that cannot run is not a stricter suite.

⚑⚑ AND THE CHECKER ALREADY CAUGHT ONE BINDING WITHOUT RUNNING ANYTHING. `claim_legibility` was
bound as a render reader and refused with *"module has no attribute render"* — it is a
`witness_family` module, a different shape entirely. Static checking covers the wiring; these
arms cover what it cannot see.

⚑ TWO ARMS WERE CUT RATHER THAN WRITTEN, BOTH BECAUSE THE TYPE SYSTEM PROVES THEM. A check that
every entry is callable is UNREACHABLE against a `dict[str, Callable[[], str]]`, and mypy says
so. A case that cannot fail measures nothing.
"""

from __future__ import annotations

import sys

from substrate import concept_bindings, concept_rows

# A key no binding answers.
_ABSENT = "no-such-key-4a71"

# The binding this suite exercises. ⚑ CHOSEN BY COST, MEASURED: it reads one stamp and compares
# it, where the corpus-parsing readers are what put the exhaustive run over its lease.
_CHEAP = "CENSUS"


def a_binding_runs(out: list[str]) -> int:
    """Check a representative binding produces a rendering without raising.

    ⚑⚑⚑ TYPE-CHECKING A COMPOSITION IS NOT RUNNING IT. A binding whose reader raises on a missing
    artifact, or whose argument shape drifted, passes every static check and fails at the first
    real call — and a table of such bindings looks complete right up until the dispatch uses it.
    """
    found = concept_bindings.reading(_CHEAP)
    if found is None:
        out.append(f"selftest: {_CHEAP} is unbound — the fixture assumption changed")
        return 1
    try:
        text = found()
    except Exception as exc:  # noqa: BLE001 — any failure is this case's finding
        out.append(f"selftest: {_CHEAP} raised {type(exc).__name__}: {exc}")
        return 1
    if not text.strip():
        out.append(f"selftest: {_CHEAP} produced an empty rendering")
        return 1
    return 0


def a_rendering_is_indented(out: list[str]) -> int:
    """Check a reading follows the family's row convention.

    ⚑ THE ADAPTER READS INDENTED, MARKED LINES as its population, so a reading that renders flush
    left would contribute no findings however many it holds — a false clean produced by a
    formatting difference.
    """
    found = concept_bindings.reading(_CHEAP)
    if found is None:
        out.append(f"selftest: {_CHEAP} is unbound")
        return 1
    first = found().splitlines()[0]
    if first and not first.startswith(" "):
        out.append(f"selftest: {_CHEAP} renders flush left: {first!r}")
        return 1
    return 0


def an_absent_key_binds_to_nothing(out: list[str]) -> int:
    """Check an unlisted key returns None rather than a plausible reader."""
    if concept_bindings.reading(_ABSENT) is not None:
        out.append("selftest: an absent key resolved to a reader")
        return 1
    return 0


def an_absent_key_yields_no_findings(out: list[str]) -> int:
    """Check an unbound key produces no findings rather than raising.

    ⚑ THE CALLER DECIDES WHAT UNBOUND MEANS. This table reports that it has nothing; the library
    above it turns that into an UNMEASURED verdict, and collapsing the two here would put the
    verdict in two places.
    """
    if concept_bindings.findings(_ABSENT) != ():
        out.append("selftest: an absent key yielded findings")
        return 1
    return 0


def the_key_list_matches_the_table(out: list[str]) -> int:
    """Check the enumerated keys are exactly the bound ones."""
    if set(concept_bindings.bound_keys()) != set(concept_bindings.READINGS):
        out.append("selftest: the key list disagrees with the table")
        return 1
    return 0


def the_key_list_is_sorted(out: list[str]) -> int:
    """Check the enumeration is ordered, so two runs read the same."""
    got = concept_bindings.bound_keys()
    if list(got) != sorted(got):
        out.append(f"selftest: the keys are unsorted: {got!r}")
        return 1
    return 0


def findings_come_from_the_adapter(out: list[str]) -> int:
    """Check the marked-line extraction is the adapter's, not a second copy.

    ⚑⚑ A SECOND EXTRACTOR WOULD DISAGREE THE FIRST TIME EITHER WAS FIXED — the derived-view
    defect. Asserting identity with the adapter's reading is what keeps one authority.
    """
    found = concept_bindings.reading(_CHEAP)
    if found is None:
        out.append(f"selftest: {_CHEAP} is unbound")
        return 1
    if concept_bindings.findings(_CHEAP) != concept_rows.marked(found()):
        out.append(f"selftest: {_CHEAP} findings disagree with the adapter")
        return 1
    return 0


def a_shared_reader_binds_more_than_one_key(out: list[str]) -> int:
    """Check two keys may name one reading.

    ⚑ ONE READER, TWO ITEMS is a real shape here — mode coverage answers both the roster item and
    the per-tool one — and a table refusing it would force a copy per key.
    """
    seen = list(concept_bindings.READINGS.values())
    if len({id(found) for found in seen}) == len(seen):
        out.append("selftest: no reading is shared — the fixture assumption changed")
        return 1
    return 0


def no_binding_is_a_bare_module(out: list[str]) -> int:
    """Check every entry is a function, not a module.

    ⚑⚑ THE FIRST LIBRARY CUT BOUND MODULES and the checker refused every row: a module does not
    satisfy a callable protocol. Pinning it here keeps the repair from being undone by someone
    reaching for the shorter-looking spelling.
    """
    bad = [key for key, found in concept_bindings.READINGS.items() if hasattr(found, "__file__")]
    if bad:
        out.append(f"selftest: module-valued binding(s): {bad!r}")
        return 1
    return 0


def an_elided_reading_says_it_elided(out: list[str]) -> int:
    """Check a capped rendering states the rows it did not show.

    ⚑⚑⚑ A DISPLAY CAP IS WHERE AN UNDER-REPORT HIDES. The suite reading names six of its not-ok
    rows and the live population is far larger; a cap that showed six and said nothing would let
    a reader take six for the total — the same shape as a count with no denominator, one layer
    down in the rendering.

    ⚑ THE HEAD IS ASSERTED AGAINST THE READER'S OWN TOTAL, never a number typed here: what must
    hold is that showing fewer than all of them SAYS SO.
    """
    found = concept_bindings.reading("SUITE")
    if found is None:
        out.append("selftest: SUITE is unbound")
        return 1
    text = found()
    shown = len(concept_rows.marked(text))
    total = text.splitlines()[0]
    if "of" in total and "more" not in text and str(shown) not in total:
        out.append(f"selftest: a capped reading names no elision:\n{text}")
        return 1
    return 0


def the_table_is_not_empty(out: list[str]) -> int:
    """Check the binding table holds entries.

    ⚑ AN EMPTY TABLE PASSES EVERY SET-COMPARING ARM ABOVE, vacuously — the collection-destruction
    shape only a non-empty claim can catch.
    """
    if not concept_bindings.READINGS:
        out.append("selftest: the binding table is empty")
        return 1
    return 0


_ARMS = (
    a_binding_runs,
    a_rendering_is_indented,
    an_absent_key_binds_to_nothing,
    an_absent_key_yields_no_findings,
    the_key_list_matches_the_table,
    the_key_list_is_sorted,
    findings_come_from_the_adapter,
    a_shared_reader_binds_more_than_one_key,
    no_binding_is_a_bare_module,
    an_elided_reading_says_it_elided,
    the_table_is_not_empty,
)

_CASE_COUNT = 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"concept-bindings selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"concept-bindings selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
