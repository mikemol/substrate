#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.grade_witness` — unmeasured is not satisfied, and not a count.

⚑⚑⚑ THE UNMEASURED CASE IS THE WHOLE ITEM. The origin read `getattr(fn, "_graded", False)` against
an attribute NOTHING in the tree sets, so it emitted a population — *"N witnesses report a bit"* —
derived from a value nobody writes. A number with no source reads exactly like a measurement, and
that is worse than silence: a reader acts on it.

⚑⚑ AND THE TWO ABSENCES MUST NOT COLLAPSE. *"the sweep has not run"* and *"the sweep ran and every
witness is ungraded"* call for entirely different work — one is a build to perform, the other a
population to fix — and a bare boolean makes them one row.

⚑ THE FIXTURES POINT THE READER AT A TEMP ROOT. A case reading the live tree measures today's
absence, so it would report the project rather than the reader — and would go green the day the
sweep runs, which is exactly when the OTHER arms need to start working.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from mikemol.witness import witness_row

from substrate import corpus, engine_grades, grade_witness


def _at(root: str) -> tuple[bool, str]:
    """Read availability with the records path pointed at a temp root.

    ⚑ THE ROOT IS REBOUND ON ITS OWNING MODULE, never through the reader's import. A module
    attribute reached through a second module is the same object at runtime and a DIFFERENT NAME
    to a type checker — `grade_witness.corpus` is not an explicit re-export, and asking for it is
    refused. Rebinding where the name is defined is both typed and the spelling that survives an
    import moving.
    """
    original = corpus.ROOT
    corpus.ROOT = Path(root)
    try:
        return grade_witness.graded()
    finally:
        corpus.ROOT = original


def _rows_at(root: str) -> list[witness_row.Part | witness_row.Verdict]:
    """Run the witness with the records path pointed at a temp root.

    ⚑⚑ THE ROWS ARE MATERIALISED INSIDE THE REBIND. `witness` is a GENERATOR, so a `list()` taken
    after the `finally` restores the root would read the LIVE tree while the case believed it had
    controlled one — a fixture that silently stops being a fixture, which is the defect class this
    suite's own arms were repaired for.
    """
    original = corpus.ROOT
    corpus.ROOT = Path(root)
    try:
        return list(grade_witness.witness("T28-grade", "ungraded-witnesses"))
    finally:
        corpus.ROOT = original


def _with_records(root: str) -> None:
    """Deposit an empty record set at the path the witness names."""
    path = grade_witness.records_path(Path(root))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("[]\n", encoding="utf-8")


def an_absent_record_set_is_unavailable(out: list[str]) -> int:
    """Check a project with no sweep output reports unavailable."""
    with tempfile.TemporaryDirectory() as where:
        available, why = _at(where)
    if available or not why:
        out.append(f"selftest: an absent record set read as {available!r}, {why!r}")
        return 1
    return 0


def the_absence_names_what_is_missing(out: list[str]) -> int:
    """Check the reason names the artifact and the sweep, not just 'no grades'.

    ⚑ A REASON THAT DOES NOT NAME THE MISSING THING is one a reader must re-derive. The repair
    here is running a specific tool that writes a specific file, and both belong in the message.
    """
    with tempfile.TemporaryDirectory() as where:
        _available, why = _at(where)
    if "sweep" not in why or "/".join(grade_witness.RECORDS) not in why:
        out.append(f"selftest: the reason omits the artifact or the sweep: {why!r}")
        return 1
    return 0


def a_present_record_set_is_available(out: list[str]) -> int:
    """Check the availability predicate discriminates — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A PREDICATE RETURNING FALSE UNCONDITIONALLY would satisfy both cases above
    and report the item unmeasured forever — which is precisely the failure the origin had, in the
    other direction. The pair says the reader can tell the two states apart.
    """
    with tempfile.TemporaryDirectory() as where:
        _with_records(where)
        available, why = _at(where)
    if not available or why:
        out.append(f"selftest: a present record set read as {available!r}, {why!r}")
        return 1
    return 0


def the_verdict_says_unmeasured_not_satisfied(out: list[str]) -> int:
    """Check an absent record set OPENS and names its own limit.

    ⚑⚑⚑ THE FALSE GREEN THIS REPLACES. An item whose evidence does not exist must not close, and
    must not emit a count either — the origin did the latter, from an attribute nothing writes.

    ⚑⚑ AND IT READS A CONTROLLED ROOT, NOT THE LIVE TREE (⟡witness-not-victim). It used to assert
    UNMEASURED against the real project, which is TRUE ONLY UNTIL THE SWEEP RUNS: the arm would go
    red the day the work it exists to demand succeeds, and the next reader would edit the case to
    make it pass. That is the same expiry `suite_gap`'s live-tree arm suffered TWICE in two turns
    — a witness pinned to a victim rather than to a property. The property is that the ABSENT
    branch opens; the fixture supplies the absence, so it survives the project improving, and the
    suite header already gave this exact reason for the other arms' fixtures.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = _rows_at(where)
    verdicts = [row for row in rows if isinstance(row, witness_row.Verdict)]
    if not verdicts:
        out.append("selftest: the grade witness emitted no verdict")
        return 1
    if "UNMEASURED" not in verdicts[-1].why:
        out.append(f"selftest: the verdict does not say unmeasured: {verdicts[-1].why!r}")
        return 1
    return 0


def a_present_record_set_does_not_open_unmeasured(out: list[str]) -> int:
    """Check the witness stops saying UNMEASURED once the evidence exists — THE DISCRIMINATOR.

    ⚑⚑⚑ WITHOUT THIS, A WITNESS HARDCODED TO OPEN UNMEASURED passes every arm above. A
    positive-only assertion over one branch cannot distinguish a working reader from a constant
    one, and this item's origin failure was exactly a constant — an inert predicate whose output
    no state of the tree could move. So the pair is what makes the unmeasured arm mean anything:
    absence opens it, presence does not.

    ⚑ AND THIS IS ALSO WHAT THE OLD LIVE-TREE ARM WAS REACHING FOR and got backwards. It would
    have detected the sweep landing — by going RED. Here the same event is what the case DEMANDS,
    so the suite records progress instead of obstructing it.
    """
    with tempfile.TemporaryDirectory() as where:
        _with_records(where)
        rows = _rows_at(where)
    verdicts = [row for row in rows if isinstance(row, witness_row.Verdict)]
    if not verdicts:
        out.append("selftest: a present record set emitted no verdict at all")
        return 1
    if "UNMEASURED" in verdicts[-1].why:
        out.append(
            "selftest: a present record set STILL reads UNMEASURED — the witness is a "
            f"constant, not a read: {verdicts[-1].why!r}"
        )
        return 1
    return 0


def the_unmeasured_verdict_carries_a_route(out: list[str]) -> int:
    """Check the finding says what would close it.

    ⚑⚑ UNMEASURED IS WORK, NOT A WALL, and the route is what carries that. A verdict reporting an
    absent artifact without naming the step that produces it reads as a permanent condition.

    ⚑ THE ROUTE IS OPTIONAL ON A `Part`, so its PRESENCE is half of what this asserts. Reading it
    as a bare string would have been a type error here and a silently missing repair in the
    report — the same shape twice, caught once.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = _rows_at(where)
    parts = [row for row in rows if isinstance(row, witness_row.Part)]
    if not parts:
        out.append("selftest: the unmeasured verdict emitted no part to carry a route")
        return 1
    route = parts[0].route
    if route is None or "sweep" not in route:
        out.append(f"selftest: the unmeasured verdict carries no route: {route!r}")
        return 1
    return 0


def the_verdict_trails_its_parts(out: list[str]) -> int:
    """Check the verdict is the LAST row.

    ⚑ A WITNESS KNOWS ITS VERDICT ONLY AFTER LOOKING — emitting it first is the
    count-before-the-walk defect.
    """
    with tempfile.TemporaryDirectory() as where:
        rows = _rows_at(where)
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the last row is not a verdict")
        return 1
    if any(isinstance(row, witness_row.Verdict) for row in rows[:-1]):
        out.append("selftest: a verdict was emitted before the parts")
        return 1
    return 0


def the_failing_rungs_come_from_the_engine(out: list[str]) -> int:
    """Check the module derives failing grades rather than listing them.

    ⚑⚑ A LOCAL BLACKLIST ADMITS EVERY FUTURE RUNG BY DEFAULT — the engine's own argument for
    deriving `below` from a rank comparison. Asserting identity with the engine's derivation is
    what keeps a copy from appearing here later.
    """
    if engine_grades.below() != engine_grades.below(engine_grades.FLOOR):
        out.append("selftest: the default floor is not the declared one")
        return 1
    if not engine_grades.below():
        out.append("selftest: no rung falls below the floor — the ladder read empty")
        return 1
    return 0


def the_records_path_is_named_once(out: list[str]) -> int:
    """Check the artifact location is a declared constant, not a literal at each site.

    ⚑ A PATH TYPED TWICE IS HOW A WITNESS STARTS LOOKING SOMEWHERE ITS MESSAGE DOES NOT NAME —
    the reader checks one file and tells a reader to create another.
    """
    where = grade_witness.records_path()
    if not str(where).endswith("/".join(grade_witness.RECORDS)):
        out.append(f"selftest: the records path {where} does not match RECORDS")
        return 1
    return 0


_ARMS = (
    an_absent_record_set_is_unavailable,
    the_absence_names_what_is_missing,
    a_present_record_set_is_available,
    the_verdict_says_unmeasured_not_satisfied,
    a_present_record_set_does_not_open_unmeasured,
    the_unmeasured_verdict_carries_a_route,
    the_verdict_trails_its_parts,
    the_failing_rungs_come_from_the_engine,
    the_records_path_is_named_once,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"grade-witness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"grade-witness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
