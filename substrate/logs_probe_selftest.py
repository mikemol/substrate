# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.logs_probe` — and the four-way split it learned the hard way.

⚑⚑⚑ THE SLOW-VS-UNCONFIRMED ARMS ARE THE REASON THIS SUITE EXISTS. The module shipped with a
three-way split and reported UNCONFIRMED against an endpoint that ingests perfectly: the
read-back query was unbounded, so it scanned the whole retention and the deadline expired
INSIDE THE SCAN rather than on a missing row. From the caller's side those are identical — a
timeout with nothing returned — so nothing in the output could distinguish them. The arms
below force each state separately, because a probe run against the live store exercises
whichever one the store happens to be in.

⚑⚑ THE CASES DRIVE `probe` THROUGH A SUBSTITUTED READER, not the network. What is being
tested is the REASONING — which observation maps to which verdict — and that must be
exercisable when the store is up, when it is down, and in CI where there is no store at all.
A case that needed a live VictoriaLogs would be untestable in exactly the conditions where a
regression matters most.
"""

from __future__ import annotations

import sys

from substrate import logs_probe as lp

#: A base no case actually contacts — every reader here is substituted.
BASE = "http://127.0.0.1:1/fixture"

#: A deadline short enough that the exhausting arms finish quickly. It is a CEILING ON
#: WAITING, so shortening it for a fixture changes nothing about what is being asserted.
QUICK = 0.3

#: A poll interval below the deadline, so an exhausting arm gets at least one read.
TICK = 0.05


def _reader(answers: list[tuple[bool, bool]]) -> object:
    """Return a stand-in `read_back` yielding `answers` in order, then repeating the last.

    ⚑ A SEQUENCE, NOT A CONSTANT, because the interesting cases are about what happens ACROSS
    reads — a store that answers late is a different fact from one that never answers, and a
    single fixed reply cannot express either.
    """
    state = {"i": 0}

    def read(_base: str, _token: str, _timeout: float = 0.0) -> tuple[bool, bool]:
        i = min(state["i"], len(answers) - 1)
        state["i"] += 1
        return answers[i]

    return read


def _probe_with(
    answers: list[tuple[bool, bool]], sent: tuple[bool, str] = (True, "ok")
) -> lp.Result:
    """Run `probe` with the reader and writer substituted, restoring both afterwards.

    ⚑ THE ORIGINALS ARE RESTORED IN A `finally`, so one case's substitution cannot leak into
    the next and make a later failure read as a defect in the module.
    """
    real_read, real_post = lp.read_back, lp.post
    lp.read_back = _reader(answers)  # type: ignore[assignment]
    lp.post = lambda _b, _l, _t=0.0: sent  # type: ignore[assignment]
    try:
        return lp.probe(BASE, deadline=QUICK, poll=TICK)
    finally:
        lp.read_back, lp.post = real_read, real_post


def _outcome_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for each of the four outcomes."""
    out: list[tuple[str, bool]] = []

    found = _probe_with([(True, True)])
    out.append(
        (
            f"a read that finds the token is CONFIRMED: {found.ingest}",
            found.ingest is lp.Ingest.CONFIRMED,
        )
    )
    out.append((f"and it is truthy: {bool(found)}", bool(found)))

    refused = _probe_with([(True, True)], sent=(False, "connection refused"))
    out.append(
        (
            f"a write the store will not take is REFUSED: {refused.ingest}",
            refused.ingest is lp.Ingest.REFUSED,
        )
    )

    # ⚑⚑⚑ THE PAIR THAT COST A TICK. Both exhaust the deadline with no token found; they
    # differ ONLY in whether any read ANSWERED. A three-way split reported both as
    # UNCONFIRMED, so an expensive query read as a missing row.
    slow = _probe_with([(False, False)])
    out.append((f"reads that never answer are SLOW: {slow.ingest}", slow.ingest is lp.Ingest.SLOW))

    absent = _probe_with([(True, False)])
    out.append(
        (
            f"reads that ANSWER without the token are UNCONFIRMED: {absent.ingest}",
            absent.ingest is lp.Ingest.UNCONFIRMED,
        )
    )

    out.append(
        (
            f"and the two are distinct: {slow.ingest} vs {absent.ingest}",
            slow.ingest is not absent.ingest,
        )
    )
    # ⚑ AND THE SLOW REASON POINTS AT THE QUERY, not at the store — the actionable half.
    out.append(
        (
            f"and SLOW names the query as the suspect: {slow.detail[:40]}",
            "retention" in slow.detail or "_time" in slow.detail,
        )
    )
    return out


def _one_answer_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a store that answers once and then goes quiet.

    ⚑⚑ ONE ANSWER IS ENOUGH TO RULE OUT SLOW, and that asymmetry is deliberate. SLOW claims
    the query never completed; a single completed query falsifies it, however many later ones
    time out. The verdict must therefore be UNCONFIRMED — the row is genuinely not there.
    """
    got = _probe_with([(True, False), (False, False)])
    return [
        (f"one answered read rules out SLOW: {got.ingest}", got.ingest is lp.Ingest.UNCONFIRMED)
    ]


def _late_arrival_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a row that becomes queryable after a few polls.

    ⚑ A STORE SETTLING UNDER THE WRITE IS THE ORDINARY CASE, not an exotic one — which is why
    the probe polls at all rather than reading once. An implementation that decided on the
    first read would report UNCONFIRMED for every healthy store under load.
    """
    got = _probe_with([(True, False), (True, False), (True, True)])
    return [
        (
            f"a token that arrives late is still CONFIRMED: {got.ingest}",
            got.ingest is lp.Ingest.CONFIRMED,
        )
    ]


def _query_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the time bound on the read-back query.

    ⚑⚑⚑ THE BOUND IS THE FIX, AND ITS ABSENCE IS THE DEFECT. An unbounded LogsQL filter scans
    the whole retention: measured on the live store, `unit:"kernel"` returned nothing inside
    120s while the same filter with a 5m prefix returned rows in under a second. Asserting the
    prefix is present is what keeps someone from "simplifying" it away.
    """
    out: list[tuple[str, bool]] = []
    url = lp.query_url(BASE, f'{lp.READ_WINDOW} token:"abc"')

    out.append(
        (
            f"the read-back query carries a time bound: {lp.READ_WINDOW}",
            lp.READ_WINDOW.startswith("_time:"),
        )
    )
    out.append((f"and it reaches the URL: {url}", "_time" in url))
    # ⚑ THE INGEST URL DECLARES THE STREAM FIELDS the emitter uses, so the path verified is
    # the path taken. A probe writing to a different stream would verify a route nothing else
    # travels.
    out.append(
        (
            f"the ingest URL declares the emitter's stream: {lp.insert_url(BASE)}",
            lp.STREAM_FIELDS in lp.insert_url(BASE),
        )
    )
    return out


def _record_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the record shape.

    ⚑⚑ RFC3339 MICROSECONDS, NEVER AN INTEGER. VictoriaLogs answers HTTP 200 to an integer
    timestamp and ingests nothing — so a probe using the wrong format would report a healthy
    endpoint dead, which is the failure mode opposite to the one that motivated this module.
    """
    out: list[tuple[str, bool]] = []
    line = lp.record("tok123")

    out.append((f"the record carries the token: {'tok123' in line}", "tok123" in line))
    out.append(
        (
            f"and an RFC3339 timestamp, not an integer: {'_time' in line}",
            '"_time": "' in line and "T" in line and "Z" in line,
        )
    )
    out.append((f"and names itself a probe: {lp.PROBE_TOOL in line}", lp.PROBE_TOOL in line))
    return out


def _exit_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for one exit code per outcome.

    ⚑ FOUR OUTCOMES NEED FOUR CODES. A caller scripting this must tell "repoint it" from "read
    your query" without parsing prose, and the SLOW code exists precisely because that
    distinction was invisible for a tick.
    """
    out: list[tuple[str, bool]] = []
    out.append((f"a bare run prints usage and exits {lp.USAGE_EXIT}", lp.run([]) == lp.USAGE_EXIT))
    out.append(
        (f"an unknown mode also exits {lp.USAGE_EXIT}", lp.run(["--nope", BASE]) == lp.USAGE_EXIT)
    )
    # ⚑ THE CODES ARE ASSERTED DISTINCT rather than each pinned to a literal — a roster of
    # numbers beside the enum is a second roster, and it drifts when a fifth outcome is added.
    codes = {0, 1, lp.USAGE_EXIT, lp.UNCONFIRMED_EXIT, lp.SLOW_EXIT}
    out.append(
        (f"every outcome has its own exit code: {sorted(codes)}", len(codes) == len(lp.Ingest) + 1)
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _outcome_cases()
        + _one_answer_cases()
        + _late_arrival_cases()
        + _query_cases()
        + _record_cases()
        + _exit_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"logs-probe selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
