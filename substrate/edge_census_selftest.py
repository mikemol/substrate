#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.edge_census` — the three populations, and the gap that matters.

⚑⚑⚑ THE `used_but_unscanned` CASE IS THE ONE THIS MODULE EXISTS FOR. A field the corpus writes
and the local reader does not scan makes every witness over that reader report ZERO — a false
green, not a missing row. The case asserts the census NAMES it rather than merely counting.

⚑⚑ AND THE POPULATIONS MUST NOT COLLAPSE. A census returning one merged list would satisfy a
count-based check while losing the only distinction it exists to draw: *nobody writes that field*
and *nothing looks for it* are different facts with different repairs.

⚑ THE FIXTURES ARE WRITTEN HERE, NOT READ FROM THE LIVE CORPUS. A case whose subject is the real
warrants bib passes or fails on today's content, so it would report the corpus rather than the
reader — and it would go green the moment someone edited a bib for unrelated reasons. MEASURED on
live at the time of writing: used and scanned agree exactly (`from, rests-on, enables`), so a
live-corpus case for the gap could not fail at all.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import raw_bib

from substrate import edge_census, engine_edges

# ⚑ THE ENGINE'S ROSTER, READ FROM THE AUTHORITY. Named so the identity case below compares
# against what the engine says rather than against a tuple typed into this file — which is the
# defect that case exists to catch.
_ENGINE_ROSTER = engine_edges.edge_fields()

# An entry carrying an edge field the local reader scans, and one it does not.
_BIB = """@misc{ALPHA,
  section  = {s},
  claim    = {a claim},
  rests-on = {BETA},
  check    = {item:ALPHA}
}

@misc{BETA,
  section = {s},
  claim   = {another claim},
  reads   = {ALPHA},
  check   = {item:BETA}
}
"""

# A bib whose entries carry no edge field at all.
_NO_EDGES = """@misc{GAMMA,
  section = {s},
  claim   = {a claim with no relation},
  check   = {item:GAMMA}
}
"""


def _bib(where: str, name: str, text: str) -> Path:
    """Write a fixture bib and return its path."""
    path = Path(where) / name
    path.write_text(text, encoding="utf-8")
    return path


def the_engines_roster_is_read_not_restated(out: list[str]) -> int:
    """Check the carried roster comes from the engine, and is non-empty.

    ⚑⚑⚑ THIS PINS THE MECHANISM, NOT THE MEMBERS, AND THE INVERSION IS THE POINT. An earlier cut
    asserted the exact tuple `("from", "rests-on", "reads")`, read off the engine's module
    DOCSTRING — which names three while the constant at `bib.py:48` carries FOUR (`consumes` was
    added and the prose did not follow). A case pinning members must be edited every time the
    roster grows, and until someone does, it reports a CORRECT roster as wrong.

    ⚑⚑ SO IT ASSERTS IDENTITY WITH THE AUTHORITY INSTEAD. If the census ever restates the roster
    locally, this diverges the moment upstream changes — the only failure worth catching here,
    since a local copy is exactly what produced the wrong claim.

    ⚑ AND NON-EMPTY IS A SEPARATE ASSERTION, because a `getattr(..., ())` fallback degrading to an
    empty roster would satisfy an identity check against itself while reporting every edge in the
    corpus as engine-dropped.
    """
    got = edge_census.census().carried
    bad = 0
    if got != _ENGINE_ROSTER:
        out.append(f"selftest: the carried roster {got!r} is not the engine's own")
        bad += 1
    if not got:
        out.append("selftest: the engine's roster read EMPTY — a degraded read, not a roster")
        bad += 1
    return bad


def a_used_edge_field_is_reported_as_used(out: list[str]) -> int:
    """Check a field an entry carries appears in the `used` population."""
    with tempfile.TemporaryDirectory() as where:
        got = edge_census.census(_bib(where, "one.bib", _BIB))
    if "rests-on" not in got.used:
        out.append(f"selftest: a written edge field is not reported used: {got.used!r}")
        return 1
    return 0


def a_written_but_unscanned_field_is_named(out: list[str]) -> int:
    """Check a field the corpus writes and the reader does not scan is NAMED.

    ⚑⚑ THE FALSE-GREEN CASE. `reads` is in the engine's roster and absent from
    `raw_bib.EDGE_FIELDS`, so an entry stating a relation through it is invisible to every
    witness over that reader — and the witness reports zero rather than an error.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_census.census(_bib(where, "one.bib", _BIB))
    if "reads" not in got.used_but_unscanned:
        out.append(
            f"selftest: a written-but-unscanned field was not named: "
            f"used={got.used!r} scanned={got.scanned!r}"
        )
        return 1
    return 0


def a_scanned_field_is_not_reported_as_a_gap(out: list[str]) -> int:
    """Check a field the reader DOES scan is not reported as unscanned.

    ⚑ THE POSITIVE CONTROL. Without it, a property reporting every used field would satisfy the
    case above — the pair says the predicate discriminates rather than flagging whatever it sees.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_census.census(_bib(where, "one.bib", _BIB))
    if "rests-on" in got.used_but_unscanned:
        out.append("selftest: a scanned field was reported as a gap")
        return 1
    return 0


def a_bib_with_no_edges_reports_none_used(out: list[str]) -> int:
    """Check an edgeless corpus reports an empty `used` and no gap."""
    with tempfile.TemporaryDirectory() as where:
        got = edge_census.census(_bib(where, "none.bib", _NO_EDGES))
    bad = 0
    if got.used != ():
        out.append(f"selftest: an edgeless bib reported used={got.used!r}")
        bad += 1
    if got.used_but_unscanned != ():
        out.append("selftest: an edgeless bib reported a gap")
        bad += 1
    return bad


def the_scanned_population_is_the_readers_own(out: list[str]) -> int:
    """Check `scanned` is read from the reader, never restated here.

    ⚑ A SECOND COPY OF THE VOCABULARY IS THE DEFECT THIS WHOLE MODULE IS ABOUT. If the census
    spelled its own list, it would compare the corpus against itself and agree by construction.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_census.census(_bib(where, "one.bib", _BIB))
    if got.scanned != tuple(raw_bib.EDGE_FIELDS):
        out.append(f"selftest: scanned={got.scanned!r} is not the reader's own set")
        return 1
    return 0


def the_three_populations_stay_separate(out: list[str]) -> int:
    """Check the census reports three distinct lists rather than one merged one.

    ⚑ COLLAPSING THEM LOSES THE ONLY DISTINCTION THE CENSUS DRAWS. *Nobody writes that field* and
    *nothing looks for it* are different facts needing different repairs, and a merged list
    cannot express either.
    """
    with tempfile.TemporaryDirectory() as where:
        got = edge_census.census(_bib(where, "one.bib", _BIB))
    if got.used == got.scanned == got.carried:
        out.append("selftest: the three populations are indistinguishable")
        return 1
    return 0


def the_candidate_list_holds_no_duplicates(out: list[str]) -> int:
    """Check a field named by BOTH readers is offered once.

    ⚑ `rests-on` IS IN BOTH LISTS, so a naive concatenation would report it twice and inflate
    every count derived from the census.
    """
    got = edge_census.candidates()
    if len(got) != len(set(got)):
        out.append(f"selftest: the candidate list repeats a field: {got!r}")
        return 1
    return 0


def the_gap_is_rendered_loudly(out: list[str]) -> int:
    """Check the rendered census surfaces a gap rather than burying it in a list.

    ⚑ A GAP PRINTED AS ONE MORE ROW READS AS INVENTORY. It is the one line a reader must act on,
    so the renderer marks it.
    """
    with tempfile.TemporaryDirectory() as where:
        text = edge_census.render(edge_census.census(_bib(where, "one.bib", _BIB)))
    if "WRITTEN BUT NOT SCANNED" not in text:
        out.append(f"selftest: the rendered census does not surface the gap:\n{text}")
        return 1
    return 0


_ARMS = (
    the_engines_roster_is_read_not_restated,
    a_used_edge_field_is_reported_as_used,
    a_written_but_unscanned_field_is_named,
    a_scanned_field_is_not_reported_as_a_gap,
    a_bib_with_no_edges_reports_none_used,
    the_scanned_population_is_the_readers_own,
    the_three_populations_stay_separate,
    the_candidate_list_holds_no_duplicates,
    the_gap_is_rendered_loudly,
)

_CASE_COUNT = 2 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"edge-census selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"edge-census selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
