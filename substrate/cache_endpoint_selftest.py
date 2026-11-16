# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.cache_endpoint` — parsing, refusal, and the three-way verdict.

⚑⚑⚑ THE VERDICT CASES ARE THE LOAD-BEARING ONES, AND THEY RUN ON CONSTRUCTED PROBE SETS
RATHER THAN ON THE NETWORK. What must be pinned is the REASONING — that nothing answering
reads as UNREACHABLE and never as a wrong endpoint — and a live probe cannot exercise that
arm on demand. Driving `verdict` directly makes every branch reachable in every environment,
including the one where the store is up.

⚑⚑ AND THE NETWORK ARM IS DELIBERATELY SMALL. A case asserting that a particular port answers
would pin MUTABLE STATE (gate-G285): the store moves, and the arm would invert on a cutover
while claiming the module broke. So the live probe is asserted only for SHAPE — that it
returns a reading at all, and that a refused address reports refused.
"""

from __future__ import annotations

import sys

from substrate import cache_endpoint as ce

#: An address nothing listens on, for the refusal arm. Port 1 is privileged and unused here.
DEAD = ce.Endpoint("127.0.0.1", 1)


def _parse_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for endpoint parsing."""
    out: list[tuple[str, bool]] = []

    got = ce.parse("127.0.0.1:30637")
    out.append((f"a host:port parses: {got}", got == ce.Endpoint("127.0.0.1", 30637)))
    out.append((f"and round-trips through str: {got}", str(got) == "127.0.0.1:30637"))
    # ⚑ A HOSTNAME IS NOT ONLY AN IP — the store may move off loopback, and a parser that
    # accepted only dotted quads would refuse the working config at exactly that moment.
    named = ce.parse("cache.internal:6379")
    out.append((f"a hostname parses: {named}", named.host == "cache.internal"))
    return out


def _refusal_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for a malformed spec being REFUSED rather than defaulted.

    ⚑⚑ THE REFUSAL IS THE POINT. A silent fallback to the default reproduces the failure the
    override exists to remove — a client pointed somewhere nobody intended, degrading
    quietly, with the operator's setting discarded and nothing saying so.
    """
    out: list[tuple[str, bool]] = []

    for spec in ("no-port", "host:notaport", ":6379", ""):
        try:
            ce.parse(spec)
        except ValueError as exc:
            out.append((f"{spec!r} is refused: {str(exc)[:48]}", True))
        else:
            out.append((f"{spec!r} is refused", False))

    # ⚑ AND THE REFUSAL SAYS WHY, so a reader does not "fix" it by deleting the setting —
    # which would restore the silent default this module exists to remove.
    try:
        ce.parse("bad")
    except ValueError as exc:
        out.append(
            (
                f"and it names the reason: {'nobody intended' in str(exc)}",
                "nobody intended" in str(exc),
            )
        )
    else:
        out.append(("and it names the reason", False))
    return out


def _configured_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the override outranking the default."""
    out: list[tuple[str, bool]] = []

    fallback = ce.configured({})
    out.append((f"an unset environment uses the default: {fallback}", str(fallback) == ce.DEFAULT))

    override = ce.configured({ce.ENV_VAR: "10.0.0.5:6380"})
    out.append(
        (f"the env var OUTRANKS the default: {override}", override == ce.Endpoint("10.0.0.5", 6380))
    )

    # ⚑ A BAD OVERRIDE PROPAGATES ITS REFUSAL rather than being swallowed back to the
    # default — the whole asymmetry this module turns on.
    try:
        ce.configured({ce.ENV_VAR: "garbage"})
    except ValueError:
        out.append(("a malformed override refuses rather than falling back", True))
    else:
        out.append(("a malformed override refuses rather than falling back", False))
    return out


def _verdict_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the three-way verdict.

    ⚑⚑⚑ THE UNREACHABLE ARM IS THE ONE THAT MATTERS, and it is the arm a naive reader would
    omit. When nothing answers, the honest verdict is that this cannot tell a moved port from
    a host with no reach — and reporting STALE CONFIG there would send someone to change a
    setting that was correct. The origin's own probe comment asks for exactly this.
    """
    out: list[tuple[str, bool]] = []
    current = ce.Endpoint("127.0.0.1", 30637)
    retired = ce.Endpoint("127.0.0.1", 6379)

    live = ce.Probe(current, connected=True, answered=True, note="current")
    dead = ce.Probe(retired, connected=False, answered=False, note="retired")

    ok = ce.verdict([live, dead], current)
    out.append((f"the configured endpoint answering reads OK: {ok[:24]}", ok.startswith("OK")))

    stale = ce.verdict([ce.Probe(retired, connected=True, answered=True, note="x")], current)
    out.append(
        (
            f"a DIFFERENT address answering reads STALE: {stale[:28]}",
            stale.startswith("STALE CONFIG"),
        )
    )
    out.append((f"and it names the remedy: {ce.ENV_VAR in stale}", ce.ENV_VAR in stale))

    none = ce.verdict([dead, ce.Probe(current, connected=False, answered=False, note="y")], current)
    out.append(
        (f"NOTHING answering reads UNREACHABLE: {none[:28]}", none.startswith("UNREACHABLE"))
    )
    # ⚑ AND EXPLICITLY NOT "the endpoint is wrong" — the two look identical from here, and
    # sending someone to change a correct setting is the expensive direction.
    out.append((f"and does NOT claim a stale config: {'STALE' not in none}", "STALE" not in none))
    return out


def _probe_shape_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the probe's shape against a known-dead address.

    ⚑ ASSERTED FOR SHAPE, NEVER FOR WHICH PORT IS UP (gate-G285). A case pinning that a
    particular address answers reads mutable state and inverts at the next cutover, blaming
    the module for the move.
    """
    out: list[tuple[str, bool]] = []
    got = ce.probe(DEAD, note="nothing listens here", timeout=0.5)

    out.append((f"a dead address reports refused: {got.why()}", not got.connected))
    out.append((f"and not answering: {got.answered}", not got.answered))
    # ⚑ CONNECTED AND ANSWERED ARE SEPARATE FACTS — a port held by something that is not a
    # cache is a different problem from a refused one, and a boolean would merge them.
    held = ce.Probe(DEAD, connected=True, answered=False, note="something else has it")
    out.append(
        (f"connected-but-silent is its own outcome: {held.why()}", "NOT a cache" in held.why())
    )

    every = ce.candidates(timeout=0.5)
    out.append(
        (
            f"candidates probes every KNOWN address: {len(every)} of {len(ce.KNOWN)}",
            len(every) == len(ce.KNOWN),
        )
    )
    # ⚑ THE RETIRED ADDRESS IS STILL IN THE ROSTER — it is the discriminator, and dropping it
    # would make the next cutover undiagnosable in the same way this one was.
    probed = {str(p.endpoint) for p in every}
    out.append((f"including the retired one: {sorted(probed)}", "127.0.0.1:6379" in probed))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _parse_cases()
        + _refusal_cases()
        + _configured_cases()
        + _verdict_cases()
        + _probe_shape_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"cache-endpoint selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
