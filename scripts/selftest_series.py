#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Push one selftest run's sample to the TSDB, buffering it when the store is unreachable.

⚑ THE LEDGER IS A LEVEL BY CONSTRUCTION, AND THAT IS WHY THIS EXISTS. The run ledger is
written with truncate — exactly one run survives — so it answers "where am I", which is the
right question for staleness and the wrong one for MOVEMENT. A series is the missing axis,
not a replacement: the stamp stays, because "is this record current" and "what moved" are two
questions and the ledger only ever answered the first.

⚑ MEASURED ON THE AUTHOR, ONE ITEM AFTER FILING IT (2026-08-02). The suite went 875 → 873
when a witness took a different branch — POPULATION CHANGED — and that was reported as "a real
regression, not noise" on the strength of one integer and a memory of a previous one.

⚑ THE PRODUCER IS REUSED, NEVER RE-DERIVED. `membudget_otlp.emit_gauges` already owns the OTLP
wiring and two hard-won constraints — pin `service.instance.id`, and `Resource(attributes=)`
rather than `Resource.create()`, which injects a random per-process UUID and mints a fresh
series set every run (~4148 churn series bought that lesson). Verification goes through
`tsdbprobe`, which carries the read-your-write semantics. A second emitter here would be a
third place for those to drift.

⚑ BUFFERED IS NOT FAILED, AND NOT SILENT. Telemetry is an OBSERVATION of the run, never part
of it: a suite must not fail because a store is down. But "not emitted" alone would be a LOST
measurement — the exact gap that makes a series unreadable — so an unreachable store spools
the sample and the depth is REPORTED. The difference between deferred and lost is the whole
point of the buffer.

⚑ DRAIN BEFORE EMITTING, so a recovered store rebuilds the series IN ORDER. Emitting today's
point first and backfilling after would make the newest point land before the older ones it
explains.

⚑⚑ NOT CONFIRMED IS NOT FAILED. An empty read has three causes — not written, written but not
yet queryable, store down — and no predicate here distinguishes them, so the verdict says
which it means rather than collapsing "absent" into "failed".

⚑ THE COLLABORATORS ARE PROTOCOLS, NOT `Any`. `membudget_otlp`, `tsdbprobe` and `spool` are
resolved at call time (they live on paths this module extends). They are declared as CALLABLE
ATTRIBUTES rather than methods, because the collaborators are MODULES: a method declaration
would bind the module to `self` and shift every keyword by one — a mismatch no checker can
see, since a module satisfies either shape structurally.

⚑⚑ AND `verify` IS KEYWORD-ONLY, WHICH IS NOT A STYLE POINT HERE. The crash that motivated
this whole retirement was a positional `may_write(True)` against a keyword-only parameter: a
bare boolean at a call site says nothing about what the True decides, and this one decides
whether the run waits on a store. Named at every call site, or not passed.

⚑ THE SHAPE OF THE SAMPLE LIVES IN `substrate.suite_sample`, WHICH IS PURE. This module owns
only the transport; that one owns the projection, shared by the live path and the replay so a
field added there reaches both by construction.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner).
"""

from __future__ import annotations

import importlib
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

ROOT = Path(__file__).resolve().parent.parent
for _extra in (ROOT, ROOT / "scratch", ROOT / "scripts"):
    if str(_extra) not in sys.path:
        sys.path.insert(0, str(_extra))

from substrate import suite_sample  # noqa: E402

# Where this module's progress lines go — injected so a case can capture them.
Writer = Callable[[str], None]


@dataclass(frozen=True, slots=True)
class Shot:
    """One export: the gauges, the moment they describe, and where they go."""

    series: dict[str, suite_sample.Points]
    at: float
    endpoint: str


class Gauges(Protocol):
    """The producer's export entry point.

    ⚑ THE KEYWORDS ARE OPEN, NOT RESTATED. This module does not OWN `emit_gauges`' signature,
    and spelling all seven parameters here would make it a SECOND authority for them — the
    restated-constant drift this repo has measured across four files. What this module does
    own is that every argument goes by NAME, and that is what this shape pins.
    """

    def __call__(self, **fields: object) -> None:
        """Export one shot of gauges."""


class Verifier(Protocol):
    """The probe's read-your-write check."""

    def __call__(self, base: str, selector: str, expected: float, deadline_s: float) -> int:
        """Return 0 once the store reads back the value we wrote."""


class Producer(Protocol):
    """The shared OTLP producer — `membudget_otlp`."""

    OTLP_ENDPOINT: str
    emit_gauges: Gauges


class Probe(Protocol):
    """The read-your-write verifier — `tsdbprobe`."""

    DEFAULT_BASE: str
    DEFAULT_DEADLINE: float
    verify: Verifier


class Spool(Protocol):
    """The store-and-forward buffer — `spool`."""

    def depth(self, key: str) -> int:
        """How many samples are waiting."""

    def drain(self, key: str, deliver: Callable[[dict[str, object]], bool]) -> dict[str, int]:
        """Attempt delivery of every waiting sample."""

    def enqueue(self, key: str, values: dict[str, object]) -> tuple[int, int]:
        """Buffer one sample, returning the new depth and how many were dropped."""


def _producer() -> Producer:
    """Return the shared OTLP producer."""
    return cast("Producer", importlib.import_module("membudget_otlp"))


def _probe() -> Probe:
    """Return the read-your-write verifier."""
    return cast("Probe", importlib.import_module("tsdbprobe"))


def _buffer() -> Spool:
    """Return the store-and-forward spool."""
    return cast("Spool", importlib.import_module("spool"))


def _export(producer: Producer, shot: Shot) -> None:
    """Hand one shot to the producer under this service's names."""
    producer.emit_gauges(
        service=suite_sample.SERVICE,
        prefix=suite_sample.PREFIX,
        series=shot.series,
        at=shot.at,
        endpoint=shot.endpoint,
        meter_name=suite_sample.METER,
        units=suite_sample.UNITS,
    )


def emit_sample(values: dict[str, object], endpoint: str) -> int:
    """Push ONE persisted sample through the shared producer. 0 on success, 1 otherwise.

    ⚑ THE SAMPLE'S OWN MOMENT, NEVER NOW. A replayed sample carries its timestamp verbatim:
    emitting a week-old measurement under today's stamp makes the backfilled series a fiction.
    """
    try:
        producer = _producer()
    except ImportError:
        return 1
    sample = suite_sample.Sample.of(values)
    try:
        _export(
            producer, Shot(series=suite_sample.series_of(sample), at=sample.at, endpoint=endpoint)
        )
    except Exception:  # noqa: BLE001 — telemetry must never fail the run it observes
        return 1
    return 0


def _drain(endpoint: str, say: Writer) -> None:
    """Deliver buffered samples BEFORE this run's, so the series rebuilds in order."""
    buffer = _buffer()
    pending = buffer.depth(suite_sample.SPOOL_KEY)
    if not pending:
        return
    report = buffer.drain(suite_sample.SPOOL_KEY, lambda values: emit_sample(values, endpoint) == 0)
    say(
        f"  selftest-series: {pending} deferred — {report['delivered']} delivered, "
        f"{report['kept']} still waiting"
    )


def _buffer_or_lose(values: dict[str, object], say: Writer) -> None:
    """Spool an undelivered sample, and SAY so — deferred and lost are different."""
    try:
        depth, dropped = _buffer().enqueue(suite_sample.SPOOL_KEY, values)
    except Exception:  # noqa: BLE001 — a spool fault must not fail the run it observes
        say("  selftest-series: not emitted, and NOT buffered — this sample is lost")
        return
    say(
        f"  selftest-series: not emitted — BUFFERED, {depth} waiting"
        + (f"; {dropped} dropped at the cap" if dropped else "")
    )


def emit(
    sample: suite_sample.Sample,
    say: Writer,
    endpoint: str | None = None,
    deadline: float | None = None,
    *,
    verify: bool = True,
) -> int:
    """Emit this run's series. 0 unless the write could not be confirmed."""
    probe = _probe()
    endpoint = endpoint or _producer().OTLP_ENDPOINT
    deadline = probe.DEFAULT_DEADLINE if deadline is None else deadline
    values = sample.as_dict()

    try:
        _drain(endpoint, say)
    except Exception:  # noqa: BLE001 — a spool fault must not fail the run it observes
        say("  selftest-series: the deferred buffer could not be read")

    if emit_sample(values, endpoint) != 0:
        _buffer_or_lose(values, say)
        return 0

    if not verify:
        say(f"  selftest-series: {len(sample.per_suite)} suite(s) emitted (unverified).")
        return 0

    # ⚑ READ-YOUR-WRITE ON A VALUE WE CONTROL — never the transport 200, never a shared row
    # counter that lives only on an exposition page. ⚑ `verify` returns an EXIT CODE
    # (0 = confirmed), not a bool: reading it as truthy inverts the verdict, which is how a
    # NOT-CONFIRMED reads as success.
    if (
        probe.verify(probe.DEFAULT_BASE, suite_sample.HEARTBEAT, sample.at, deadline_s=deadline)
        == 0
    ):
        say(
            f"  selftest-series: recorded — {len(sample.per_suite)} suite(s), "
            f"{sample.cases}/{sample.declared} cases, queryable back."
        )
        return 0
    say(
        f"  selftest-series: NOT CONFIRMED within {deadline:.0f}s. The write may have "
        f"ingested and not yet be queryable, or been dropped, or the store may be down — "
        f"this check cannot tell which. Diagnose with: "
        f"python3 scratch/tsdbprobe.py --reachable"
    )
    return 1
