#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.concept_rows` — an empty population is not automatically closed.

⚑⚑⚑ THE UNMEASURED CASE IS THE ITEM. A reading with no findings means *nothing found* for a
reader that ran and *nothing looked at* for one that could not, and only the reader knows which.
A bare `if not findings: closed` collapses them — reintroducing the false green at the exact
layer built to carry the distinction through. The arms below drive both and assert they diverge.

⚑⚑ AND THE MARKER CONVENTION IS THE READERS' OWN. Every module in this family prefixes a finding
row with the flag and leaves summary lines unmarked, so the marked lines ARE the population —
stated by the reader rather than re-derived here. Verified against two live renderings: one
clean, one carrying five findings.

⚑ THE FIXTURES ARE RENDERINGS. Driving a real reader would measure today's tree, which moves
every time this arc lands a module; what is under test is the framing, not any reader's verdict.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_row

from substrate import concept_rows

# A clean rendering: a verdict line, no marked findings.
_CLEAN = "  all 3 write path(s) are gated and armed"

# A rendering carrying findings, in the shape every reader in this family emits.
_FINDINGS = (
    "  5 of 10 derivation(s) re-derive the catalogued DAG:\n"
    "    ⚑ a.py:46  _import_dag — query module_edges instead\n"
    "    ⚑ b.py:72  _blast_radius — query module_edges instead"
)

# ⚑ THE READER COULD NOT MEASURE. No findings, and closing over it would be the false green.
_UNMEASURED = "  no write path found — UNMEASURED, not clean"

# The other spellings the family uses for the same state.
_UNKNOWN = "  UNKNOWN — the store is unreachable, so depth is UNKNOWN — not zero"
_UNREAD = "  UNREAD — the census would not run"


def _verdict(key: str, reading: concept_rows.Reading) -> witness_row.Verdict | None:
    """Return the trailing verdict of a reading's rows."""
    found = [row for row in concept_rows.rows(key, reading) if isinstance(row, witness_row.Verdict)]
    return found[-1] if found else None


def a_clean_reading_closes(out: list[str]) -> int:
    """Check a reading with no findings and no unmeasured word closes."""
    reading = concept_rows.Reading(findings=(), summary=_CLEAN)
    got = _verdict("X", reading)
    if got is None or got.state != witness_row.CLOSED:
        out.append(f"selftest: a clean reading read as {got!r}")
        return 1
    return 0


def an_unmeasured_reading_opens(out: list[str]) -> int:
    """Check a reading that could not measure OPENS — THE WHOLE ITEM.

    ⚑⚑⚑ SAME EMPTY POPULATION, OPPOSITE VERDICT. The findings are identical to the clean case;
    only the reader's own summary separates them, which is why the adapter must read it rather
    than counting rows.
    """
    reading = concept_rows.Reading(findings=(), summary=_UNMEASURED)
    got = _verdict("X", reading)
    if got is None or got.state != witness_row.OPEN:
        out.append(f"selftest: an unmeasured reading read as {got!r}")
        return 1
    return 0


def every_unmeasured_spelling_opens(out: list[str]) -> int:
    """Check the family's other words for the same state also open.

    ⚑⚑ ONE SPELLING WOULD MISS THE OTHERS. This family says UNKNOWN for an unreachable store,
    UNREAD for a census that would not run, UNEXERCISED for a probe that could not load — and a
    reader knowing only one word banks a false green for the rest.
    """
    for summary in (_UNKNOWN, _UNREAD):
        reading = concept_rows.Reading(findings=(), summary=summary)
        got = _verdict("X", reading)
        if got is None or got.state != witness_row.OPEN:
            out.append(f"selftest: {summary!r} read as {got!r}")
            return 1
    return 0


def a_reading_with_findings_opens(out: list[str]) -> int:
    """Check findings open the item — the POSITIVE CONTROL."""
    reading = concept_rows.Reading(findings=("a.py:46", "b.py:72"), summary=_FINDINGS)
    got = _verdict("X", reading)
    if got is None or got.state != witness_row.OPEN:
        out.append(f"selftest: a reading with findings read as {got!r}")
        return 1
    return 0


def each_finding_becomes_a_part(out: list[str]) -> int:
    """Check the population crosses into the rows one-for-one.

    ⚑ THE PARTS ARE THE WORKLIST. A verdict naming a count without handing over the rows makes
    the reader re-run the tool to act on it.
    """
    reading = concept_rows.Reading(findings=("a.py:46", "b.py:72"), summary=_FINDINGS)
    parts = [row for row in concept_rows.rows("X", reading) if isinstance(row, witness_row.Part)]
    if len(parts) != len(reading.findings):
        out.append(f"selftest: {len(reading.findings)} finding(s) became {len(parts)} part(s)")
        return 1
    return 0


def the_verdict_trails_the_parts(out: list[str]) -> int:
    """Check the verdict is the last row.

    ⚑ A WITNESS KNOWS ITS VERDICT ONLY AFTER LOOKING — emitting it first is the
    count-before-the-walk defect.
    """
    reading = concept_rows.Reading(findings=("a.py:46",), summary=_FINDINGS)
    got = list(concept_rows.rows("X", reading))
    if not got or not isinstance(got[-1], witness_row.Verdict):
        out.append("selftest: the last row is not a verdict")
        return 1
    if any(isinstance(row, witness_row.Verdict) for row in got[:-1]):
        out.append("selftest: a verdict was emitted before the parts")
        return 1
    return 0


def a_route_reaches_every_part(out: list[str]) -> int:
    """Check a declared route is carried onto the rows."""
    reading = concept_rows.Reading(
        findings=("a.py:46",), summary=_FINDINGS, route="query the store"
    )
    parts = [row for row in concept_rows.rows("X", reading) if isinstance(row, witness_row.Part)]
    if not parts or parts[0].route != "query the store":
        out.append(f"selftest: the route read as {parts!r}")
        return 1
    return 0


def a_partless_reading_still_verdicts(out: list[str]) -> int:
    """Check a reading with no findings still emits its verdict."""
    reading = concept_rows.Reading(findings=(), summary=_CLEAN)
    got = list(concept_rows.rows("X", reading))
    if len(got) != 1 or not isinstance(got[0], witness_row.Verdict):
        out.append(f"selftest: a partless reading emitted {got!r}")
        return 1
    return 0


def the_marker_reads_the_findings(out: list[str]) -> int:
    """Check marked lines are extracted as the population."""
    got = concept_rows.marked(_FINDINGS)
    if len(got) != len(_FINDINGS.splitlines()) - 1:
        out.append(f"selftest: the marked lines read as {got!r}")
        return 1
    return 0


def the_marker_drops_the_summary_line(out: list[str]) -> int:
    """Check an unmarked summary is not counted as a finding.

    ⚑⚑ THE SUMMARY SITS IN THE SAME STREAM as the rows, and counting it would make every reading
    one finding larger — a population inflated by the reader's own header.
    """
    got = concept_rows.marked(_FINDINGS)
    if any("re-derive the catalogued DAG" in line for line in got):
        out.append(f"selftest: the summary line was read as a finding: {got!r}")
        return 1
    return 0


def a_clean_rendering_marks_nothing(out: list[str]) -> int:
    """Check a clean rendering yields an empty population."""
    if concept_rows.marked(_CLEAN):
        out.append(f"selftest: a clean rendering marked {concept_rows.marked(_CLEAN)!r}")
        return 1
    return 0


def an_unmarked_unmeasured_rendering_is_still_open(out: list[str]) -> int:
    """Check the marker and the verdict are independent readings.

    ⚑⚑⚑ A RENDERING WITH NO MARKED LINE IS NOT THEREBY CLEAN. The unmeasured renderings carry no
    flag either — so a reader deriving the verdict from the marker alone would close every one of
    them, which is precisely the state that must never close.
    """
    reading = concept_rows.Reading(findings=concept_rows.marked(_UNMEASURED), summary=_UNMEASURED)
    got = _verdict("X", reading)
    if got is None or got.state != witness_row.OPEN:
        out.append(f"selftest: an unmarked unmeasured rendering read as {got!r}")
        return 1
    return 0


def the_convenience_form_agrees_with_the_record(out: list[str]) -> int:
    """Check both entry points produce the same rows.

    ⚑ TWO SPELLINGS OF ONE CALL must not diverge; the convenience form exists so a binding is one
    call, not so it can answer differently.
    """
    reading = concept_rows.Reading(findings=("a.py:46",), summary=_FINDINGS, route="fix it")
    direct = list(concept_rows.rows("X", reading))
    convenience = list(concept_rows.from_render("X", _FINDINGS, ("a.py:46",), "fix it"))
    if direct != convenience:
        out.append(f"selftest: the two forms disagree:\n{direct!r}\n{convenience!r}")
        return 1
    return 0


def the_verdict_carries_the_readers_prose(out: list[str]) -> int:
    """Check the reader's own summary reaches the verdict.

    ⚑ THE ADAPTER MUST NOT RE-WORD THE FINDING. A summary rewritten here is a second voice on one
    fact, and the two would drift the moment either was edited.
    """
    reading = concept_rows.Reading(findings=(), summary=_CLEAN)
    got = _verdict("X", reading)
    if got is None or got.why != _CLEAN.strip():
        out.append(f"selftest: the verdict prose reads as {got!r}")
        return 1
    return 0


_ARMS = (
    a_clean_reading_closes,
    an_unmeasured_reading_opens,
    every_unmeasured_spelling_opens,
    a_reading_with_findings_opens,
    each_finding_becomes_a_part,
    the_verdict_trails_the_parts,
    a_route_reaches_every_part,
    a_partless_reading_still_verdicts,
    the_marker_reads_the_findings,
    the_marker_drops_the_summary_line,
    a_clean_rendering_marks_nothing,
    an_unmarked_unmeasured_rendering_is_still_open,
    the_convenience_form_agrees_with_the_record,
    the_verdict_carries_the_readers_prose,
)

_CASE_COUNT = 1 + 1 + 2 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"concept-rows selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"concept-rows selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
