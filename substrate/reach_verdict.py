#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Classify one suite's reach reading — were the missing cases DELETED, or merely LOST.

⚑⚑⚑ THE RATCHET IS THIS PREDICATE, NOT AN INEQUALITY AGAINST A STORED MAXIMUM. What refuses a
regression is `shrank`/`unknown` over the PAIR `(reached, call-sites)`; the recorded row is the
last ACCEPTED reading that predicate reads next time, deliberately NOT a high-water mark.

A high-water mark is a SCALAR COLLAPSE OF A PREDICATE OVER A SET, expressible only when the
done-set is a PREFIX — it buys that expressibility by ASSERTING prefix-closure rather than
carrying it. Suite reach is not a prefix, and the record proves it four times: `tmi_subject` runs
11 of a hardcoded 15 (four need a corpus that may be absent), `jea_circuit`'s 300 is a keyword
DEFAULT that `trials=50` moves with the source byte-identical, five suites read a static 0 purely
because the case-call vocabulary had not learned `ok`/`chk`, and three reported SILENT while
passing. A max over readings like those banks whichever configuration was richest, then refuses
every honest run forever.

⚑⚑ THE SIX KINDS, AND THE TWO THAT REFUSE:

    new       no baseline row. Recorded, never refused: a first sighting is not a loss.
    grew      reached MORE than ever before.
    held      unchanged.
    deleted   reached fewer AND the source shed at least as many call sites. Honest paydown.
    shrank    reached fewer while the source STILL HOLDS the cases. ⚑ THE DEFECT. REFUSES.
    unknown   reached fewer and the source could not be parsed, so the two are
              indistinguishable. ⚑ REFUSES — a drop nobody can classify is the case this gate
              exists for, and naming it is what stops `census-green-is-a-fact-about-the-census`
              from applying to the gate itself.

⚑⚑⚑ THE COMPARISON IS SCALED, NOT RAW, AND A STARVE HARNESS FOUND THAT. The two lenses do not
count the same unit: a case registered inside a loop is ONE call site and MANY cases. `bibstruct`
records (97 reached, 96 sites); deleting 56 of its 96 sites genuinely removes 57 cases, so a raw
`shed >= lost` compare REFUSED AN HONEST DELETION by exactly the loop inflation.

⚑⚑ SO THE RECORDED PAIR IS ITSELF THE CALIBRATION. The slack is the MEASURED inflation —
`prev - prev_static`, how many cases the suite reports over its own call sites — which is exactly
how many extra cases its loops can contribute, and therefore the largest discrepancy
loop-registration can explain. A suite with no loops records (N, N), slack 0, and gets nothing.

⚑ A RATIO WAS THE FIRST CUT AND WAS NOT ENOUGH: scaling 56 by 97/96 gives 56.58, still short of
57, so the honest deletion refused anyway. The loss is not LINEAR in sites removed — deleting the
one looping site removes two cases, any other removes one — so no per-site scaling is correct. A
BOUND on total unexplained-ness is, and it is the only quantity the two recorded numbers pin down.

⚑ AND IT ROUNDS IN THE FORGIVING DIRECTION, DELIBERATELY. The failure modes are asymmetric: a
false REFUSAL on honest paydown teaches people to route around the gate — and its own refusal text
forbids lowering the baseline, so they would have no legitimate move — while a false PASS loses
one regression, and the baseline only lowers on an already-accepted run, so the next run still
measures against the old mark.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (1,832 findings, refused whole by the per-file gate).
The extraction was FORCED: `reach_ratchet` calls `ratchet.may_write(write)` positionally against a
now keyword-only signature, and that one-keyword repair could not land inside the monolith.
"""

from __future__ import annotations

from typing import NamedTuple

# The classifications a reading can carry. The first four pass; the last two refuse.
NEW = "new"
GREW = "grew"
HELD = "held"
DELETED = "deleted"
SHRANK = "shrank"
UNKNOWN = "unknown"

# Which kinds refuse a run.
REFUSING = (SHRANK, UNKNOWN)


class Reading(NamedTuple):
    """One suite's two-lens reading: how many cases RAN, and how many the source declares."""

    reached: int | None
    static: int | None


class Verdict(NamedTuple):
    """What a reading means against the baseline, and the detail a reader acts on."""

    kind: str
    detail: str

    @property
    def refuses(self) -> bool:
        """Report whether this verdict fails the run."""
        return self.kind in REFUSING


class Regression(NamedTuple):
    """One suite whose verdict refuses the run.

    ⚑ A RECORD RATHER THAN A PAIR, so the caller reads `row.label` instead of `row[0]` — the
    ⟡symbolic-reference-only rule applied to this module's own output. Sorting by a named method
    also avoids the untyped lambda that makes every element it touches `Any`.
    """

    label: str
    verdict: Verdict

    def rank(self) -> str:
        """Return the sort key: alphabetical by suite."""
        return self.label


def _unknown_source(reading: Reading, previous: Reading, lost: int) -> Verdict:
    """Return the verdict for a drop whose source could not be counted."""
    return Verdict(
        UNKNOWN,
        f"reached {reading.reached}, was {previous.reached} ({lost} fewer) — the "
        f"source could not be counted, so fewer-RAN and fewer-EXIST are "
        f"indistinguishable",
    )


def _classify_drop(reading: Reading, previous: Reading) -> Verdict:
    """Return `deleted` or `shrank` for a reading below its baseline."""
    lost = (previous.reached or 0) - (reading.reached or 0)
    if reading.static is None or previous.static is None:
        return _unknown_source(reading, previous, lost)
    shed = previous.static - reading.static
    slack = max(0, (previous.reached or 0) - previous.static)
    explained = shed + slack
    if explained >= lost:
        return Verdict(
            DELETED,
            f"reached {reading.reached}, was {previous.reached} ({lost} fewer); the "
            f"source shed {shed} case call-site(s) (+{slack} recorded loop slack = "
            f"{explained} explained) — cases were DELETED, not lost",
        )
    return Verdict(
        SHRANK,
        f"reached {reading.reached}, was {previous.reached} ({lost} fewer) while the "
        f"source still holds {reading.static} case call-site(s) (was "
        f"{previous.static}; {shed} shed +{slack} slack explains only {explained} of "
        f"the loss) — the cases EXIST and the run stopped reaching them",
    )


def classify(label: str, reading: Reading, baseline: dict[str, Reading]) -> Verdict:
    """Return this suite's verdict against its recorded reading.

    ⚑⚑ A MISSING REACH IS `unknown`, NOT AN EXCEPTION — found by the starve harness, which is the
    point of starving it. The live path only inserts rows with a positive total, so this is
    unreachable there today; a caller handing `None` was previously a TypeError deep inside the
    compare. **A gate that CRASHES is strictly worse than one that refuses**: a traceback is not a
    verdict, and nothing downstream can read it as one.
    """
    if reading.reached is None:
        return Verdict(UNKNOWN, "the suite reported no countable total")
    if label not in baseline:
        return Verdict(NEW, "first sighting — recorded, not refused")
    previous = baseline[label]
    if previous.reached is None:
        return Verdict(UNKNOWN, "the recorded reading holds no countable total")
    if reading.reached > previous.reached:
        return Verdict(GREW, f"{previous.reached} -> {reading.reached}")
    if reading.reached == previous.reached:
        return Verdict(HELD, f"{reading.reached}")
    return _classify_drop(reading, previous)


def regressions(verdicts: dict[str, Verdict]) -> tuple[Regression, ...]:
    """Return the suites whose verdict refuses the run, in a stable order."""
    refusing = [
        Regression(label=label, verdict=verdict)
        for label, verdict in verdicts.items()
        if verdict.refuses
    ]
    return tuple(sorted(refusing, key=Regression.rank))


def may_advance(verdicts: dict[str, Verdict]) -> bool:
    """Report whether the census may record this run's readings.

    ⚑ THE CENSUS ADVANCES ONLY WHEN NOTHING REGRESSED, mirroring the rule that paydown cannot
    record while a new key is present. Recording a mixed run would bank the growth and leave the
    regression un-refusable on the next run.
    """
    return not regressions(verdicts)


def advanced(baseline: dict[str, Reading], observed: dict[str, Reading]) -> dict[str, Reading]:
    """Return the baseline with this run's readings recorded over it.

    ⚑⚑⚑ A SUITE THAT DID NOT REPORT IS ABSENT FROM `observed`, AND ITS ROW SURVIVES. This is the
    single most important property here and the opposite of what a naive implementation does. A
    refused/silent/unfit suite reached NO countable cases, and recording that as `reached = 0`
    would BANK the abort as the new mark — the ratchet laundering exactly the defect it was built
    to catch, permanently, on the first run after the incident. A transient dip banked into a
    baseline is debt that can never legitimately be paid.

    ⚑⚑ AND WHAT LANDS IS THE LAST ACCEPTED READING, NOT A MAXIMUM. The predicate in `classify` is
    what refuses; this row is the residue it reads next time. So a low first reading self-corrects
    on the following run and a `deleted` row lowers without ceremony — which is why the ORDER two
    unrelated events happen in cannot fix a permanent floor, the observable proof that the scalar
    collapse is gone.
    """
    return {**baseline, **observed}
