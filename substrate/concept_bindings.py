#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Bind each worklist key to the reading that answers it.

⚑⚑⚑ EVERY CENSUS READER REDUCES TO A THUNK, AND MEASURING THAT IS WHAT MADE ONE BINDING TABLE
POSSIBLE. The extracted modules do not share a signature — `render(Currency)`, `render(rows)`,
`render(Depth)`, `render(rows, why)`, `read() -> (record, why)`, and one with no rendering at all
— so a table of bare callables cannot type. What they DO share is that each composes to a
zero-argument call producing a rendering, and that composition is the binding. **The differences
are real and stay at the binding site**, where a reader can see which population each key
measures.

⚑⚑ THIS TABLE COVERS THE READERS THAT DO NOT EMIT ROWS, AND THE CHECKER DREW THAT LINE. A binding
for `claim_legibility` was refused with *"module has no attribute render"* — it emits rows under
`witness_decision`, so it belongs in the family table. **Two reader shapes exist and conflating
them fails at the type level**, which is the cheapest place to find out.

⚑⚑ AND A `--calls render` CENSUS SCOPED TO THE WRONG FILES MADE ME GENERALISE PAST FOUR OF THEM.
Reporting that the remaining modules had no rendering, I had asked about five files that do not
and none of the four that do. Asking the right population found them.

⚑⚑ THE POPULATION READER IS NOT ONE NAME EITHER. Most spell it `population`; `closure_delegation`
spells it `corpus_calls`, and binding the guess was refused. **A convention assumed across a
family is a second roster** — the composition is written per module because the modules are not
uniform, and the checker is what proves each one right.

⚑ A KEY WITH NO READER IS ABSENT, NOT STUBBED. An entry returning a plausible verdict would
report a measurement nobody took; an absent one reports UNBOUND, which is a fact about this table
and actionable as one. `T24` stays absent for exactly this reason: its reader needs two
populations it does not own, and inventing them would report a measurement of nothing.

⚑ EXTRACTED FOR ⟡roster-reduce: `catalog/library/concepts.py` binds keys to readers, and this is
the half that knows how each render-shaped reader is called.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.witness import warrant_integrity

from substrate import (
    argument_consumed,
    census_currency,
    closure_delegation,
    concept_rows,
    dag_source,
    deadline_floor,
    flag_routing,
    gate_precondition,
    import_manifest,
    mode_coverage,
    premise_edge,
    probe_kernel,
    series_depth,
    sole_authority,
    suite_witness,
    tree_serialization,
    universal_flags,
    warrant_bib,
    warrant_records,
    write_path,
)

if TYPE_CHECKING:
    from collections.abc import Callable

# The capability whose sole home this repo asserts, and where that home is.
_AGDA_FILES = "agda_files"
_AGDA_LEX = "scratch/agda_lex.py"

# The tools whose advertised modes must each carry a case.
_MODE_TOOLS = (
    "scratch/pycodemod.py",
    "scratch/mdstruct.py",
    "scratch/bibstruct.py",
    "scratch/tsdbprobe.py",
)

# The files whose write paths must be gated and armed.
_WRITE_TOOLS = ("scratch/bibstruct.py",)

# The files whose import-graph derivations are censused.
_DAG_TOOLS = ("scripts/gen_build_makefiles.py", "scratch/split_census.py")

# The caches whose serialisation is censused.
_CACHE_TOOLS = ("scratch/_pycodemod_query.py", "scratch/cache_probe.py")

# The claim whose declared premises the grounding item reports on.
_GROUNDED_CLAIM = "R12b"

# How many not-ok suites a rendering names before eliding.
_SUITES_SHOWN = 6


def _census_reading() -> str:
    """Render whether the leaf-verify ledger describes the tree it claims to."""
    return census_currency.render(census_currency.currency())


def _flag_reading() -> str:
    """Render which gates route their flags through the shared authority."""
    return flag_routing.render(flag_routing.population(flag_routing.gates()))


def _universal_reading() -> str:
    """Render which gates accept the universal flags."""
    return universal_flags.render(universal_flags.population(flag_routing.gates()))


def _authority_reading() -> str:
    """Render whether the enumeration authority is sole."""
    return sole_authority.render(sole_authority.authority(_AGDA_FILES, _AGDA_LEX))


def _mode_reading() -> str:
    """Render which advertised modes no selftest case exercises."""
    return mode_coverage.render(mode_coverage.population(_MODE_TOOLS))


def _argument_reading() -> str:
    """Render whether a filtering mode consumes its argument."""
    return argument_consumed.render(argument_consumed.narrowing())


def _write_reading() -> str:
    """Render whether every write path is gated and armed."""
    return write_path.render(write_path.population(_WRITE_TOOLS))


def _dag_reading() -> str:
    """Render which consumers re-derive the catalogued import DAG."""
    return dag_source.render(dag_source.population(_DAG_TOOLS))


def _cache_reading() -> str:
    """Render which caches store a parse tree whole."""
    return tree_serialization.render(tree_serialization.population(_CACHE_TOOLS))


def _series_reading() -> str:
    """Render whether the recorded measurements are a series or a level."""
    return series_depth.render(series_depth.depth())


def _deadline_reading() -> str:
    """Render whether each verify deadline resolves through an authority."""
    return deadline_floor.render(deadline_floor.population())


def _manifest_reading() -> str:
    """Render which imports no manifest accounts for."""
    rows_found, why = import_manifest.population()
    return import_manifest.render(rows_found, why)


def _probe_reading() -> str:
    """Render whether the bib reader's totality probe discriminates."""
    return probe_kernel.render(probe_kernel.kernel())


def _gate_reading() -> str:
    """Render the gated-commit precondition against the declared roster."""
    return gate_precondition.render(gate_precondition.roster())


def _integrity_reading() -> str:
    """Render what the two warrant readers say about the bib.

    ⚑ THE UNREADABLE CASE IS THE BINDING'S TO STATE. This reader returns a record OR a reason, so
    the composition must turn the reason into an unmeasurable rendering — returning an empty
    string would let an unreadable bib close the item.

    ⚑ mtools' reader takes the bib and the engine's parser as ARGUMENTS (it owns neither); this
    binding supplies substrate's. `warrant_bib.BIB` is itself a root constant, owed under W36.
    """
    got, why = warrant_integrity.read(warrant_bib.BIB, parse=warrant_records.records)
    if got is None:
        return f"  UNMEASURED — the warrant set could not be read: {why}"
    return warrant_integrity.render(got)


def _closure_reading() -> str:
    """Render which closure call sites keep both returns."""
    return closure_delegation.render(closure_delegation.corpus_calls())


def _grounding_reading() -> str:
    """Render one claim's declared premises and whether they hold.

    ⚑ THE DECIDER IS EMPTY HERE, DELIBERATELY. Supplying verdicts would mean running the premise
    items to answer this one — the subgraph the aggregate refuses — so every premise reads
    UNCHECKABLE, which is the honest state for a reader that consulted nothing.
    """
    rows_found, why = premise_edge.grounding(_GROUNDED_CLAIM)
    return premise_edge.render(_GROUNDED_CLAIM, rows_found, why)


def _suite_reading() -> str:
    """Render which suites carry no ok reading.

    ⚑⚑ THE RENDERING IS WRITTEN HERE BECAUSE THE READER HAS NONE. `suite_witness` is a CLI that
    prints as it walks; it exposes `rows()` and `not_ok()` and no `render`. Writing the rendering
    at the binding keeps the reader unchanged and gives the marker convention one home — the
    alternative was adding a `render` to a clean module for this caller's benefit, which is the
    consumer dictating the producer's shape.

    ⚑ AN EMPTY ROSTER IS UNMEASURED, NOT CLEAN. Zero discovered suites means discovery found
    nothing, which is a fact about the walk rather than about the tree.
    """
    rows_found = suite_witness.rows()
    if not rows_found:
        return "  no suite discovered — UNMEASURED, not clean"

    bad = suite_witness.not_ok(rows_found)
    if not bad:
        return f"  all {len(rows_found)} suite(s) carry an ok reading"

    out = [f"  {len(bad)} of {len(rows_found)} suite(s) are not ok:"]
    out.extend(f"    ⚑ {row.kind:<8} {row.label}" for row in bad[:_SUITES_SHOWN])
    if len(bad) > _SUITES_SHOWN:
        out.append(f"    … {len(bad) - _SUITES_SHOWN} more")
    return "\n".join(out)


# Each key, and the reading that answers it. ⚑ ONE ENTRY PER KEY, and a key naming no reading is
# absent rather than stubbed — an absent binding reports UNBOUND, a stub reports a measurement.
READINGS: dict[str, Callable[[], str]] = {
    "CENSUS": _census_reading,
    "R12b": _grounding_reading,
    "SUITE": _suite_reading,
    "keys-unique": _integrity_reading,
    "T11": _flag_reading,
    "T12": _authority_reading,
    "T17": _universal_reading,
    "T21": _mode_reading,
    "T22": _argument_reading,
    "T26": _mode_reading,
    "T27": _write_reading,
    "T28-closure": _closure_reading,
    "T29": _dag_reading,
    "T30": _cache_reading,
    "OBS": _series_reading,
    "OBS-DEADLINE": _deadline_reading,
    "DEPS": _manifest_reading,
    "D0-kernel": _probe_reading,
    "B3": _gate_reading,
}


def reading(key: str) -> Callable[[], str] | None:
    """Return the reading bound to one key, or None when nothing answers it."""
    return READINGS.get(key)


def bound_keys() -> tuple[str, ...]:
    """Return every key this table answers, sorted.

    ⚑ NOT SPELLED `keys`, AND THE LINTER IS RIGHT ABOUT WHY. A module-level `keys()` reads as the
    dict method at every call site — `for k in mod.keys()` is flagged as the redundant-`.keys()`
    idiom, which is a true observation about how the line READS even though the call is a
    function. A name that makes a correct line look like a mistake costs every future reader.
    """
    return tuple(sorted(READINGS))


def findings(key: str) -> tuple[str, ...]:
    """Return the marked finding lines for one key.

    ⚑ THE ROWS COME FROM THE ADAPTER, never re-derived here. This module knows how each reader is
    CALLED; `concept_rows` knows how a rendering becomes parts and a verdict, and keeping the two
    separate is what stops a second verdict path appearing.
    """
    found = reading(key)
    if found is None:
        return ()
    return concept_rows.marked(found())


def sweep() -> tuple[tuple[str, str], ...]:
    """Run every binding, returning `(key, outcome)` per row.

    ⚑⚑⚑ THE EXHAUSTIVE RUN IS A MODE, NOT A SUITE CASE, AND THE BUDGET DECIDED THAT. Running all
    of these in one process was killed at exit 143 under the 192 MB suite lease: several parse
    the whole corpus. A caller invoking this chooses its own budget — which is the difference
    between a check that cannot run and one that runs when asked.

    ⚑ A RAISING BINDING IS A ROW, NOT AN ABORT. One reader failing must not hide the state of the
    rest, which is what an uncaught exception here would do.
    """
    out: list[tuple[str, str]] = []
    for key in bound_keys():
        found = READINGS[key]
        try:
            text = found()
        except Exception as exc:  # noqa: BLE001 — a failing reader is this sweep's datum
            out.append((key, f"RAISED {type(exc).__name__}: {exc}"))
            continue
        marks = concept_rows.marked(text)
        out.append((key, f"{len(marks)} finding(s)" if marks else "no finding"))
    return tuple(out)


if __name__ == "__main__":
    import sys

    _bad = 0
    for _key, _outcome in sweep():
        sys.stdout.write(f"  {_key:<14} {_outcome}\n")
        _bad += _outcome.startswith("RAISED")
    sys.stdout.write(f"  {_bad} of {len(READINGS)} binding(s) raised\n")
    sys.exit(1 if _bad else 0)
