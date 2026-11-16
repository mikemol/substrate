#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.series_depth` — unknown, empty and shallow are three verdicts.

⚑⚑⚑ THE UNREACHABLE CASE IS THE ITEM. *"The store is down"* and *"no sample was ever recorded"*
are different facts with different remedies, and a predicate returning a bare count collapses
them into the smaller one — reporting a working emitter as a missing one. The arms below pin all
three readings apart, because only a case can prove a reader distinguishes them.

⚑⚑ AND THE FIXTURES ARE FAKE PROBES, NOT THE LIVE STORE. A case reading the real TSDB measures
today's connectivity: it would pass here (the store is unreachable from this host, MEASURED) and
fail on a machine where it is up, reporting the network as a defect in the reader. Every arm
drives a stub probe whose behaviour is chosen by the case.

⚑⚑ THE FAKE SATISFIES THE PROTOCOL STRUCTURALLY, AND MAKING IT DO SO CAUGHT A REAL MISMATCH. A
first cut declared its own exception class and reached for a `type: ignore` when mypy refused the
substitution — a suppression this gate has no path for, and the wrong instinct: the checker was
reporting that the fake did not implement the surface the reader consults. Raising the module's
own signal is both what the protocol asks for and what the live probe actually does.

⚑ THE FLOOR IS ASSERTED AS A RELATION, NOT AS THE NUMBER 2. Pinning the literal would restate
the module's own constant, and the property that matters is that the floor is where the verdict
flips.
"""

from __future__ import annotations

import sys

from substrate import series_depth


class _Probe:
    """A probe whose read is chosen by the case.

    ⚑ IT DECLARES THE THREE NAMES THE READER CONSULTS and nothing else, which is the point of the
    reader declaring a protocol: a fake cannot accidentally depend on the real module's wider
    surface, and a fourth attribute would fail to type-check here first.
    """

    DEFAULT_BASE = "http://fixture.invalid"
    Unreachable: type[Exception] = ConnectionError

    def __init__(self, values: list[float] | None = None, raises: Exception | None = None) -> None:
        self._values = values if values is not None else []
        self._raises = raises
        self.asked: list[tuple[str, str]] = []

    def query(self, base: str, promql: str) -> object:
        """Record the question and either raise or return an opaque body."""
        self.asked.append((base, promql))
        if self._raises is not None:
            raise self._raises
        return {"data": {"result": []}}

    def extract_values(self, body: object) -> list[float]:
        """Return the values the case chose."""
        del body
        return self._values


def _depth_with(probe: _Probe) -> series_depth.Depth:
    """Run the reader against a fixture probe.

    ⚑ THE SEAM IS THE LOADER, WHICH IS WHY IT IS WHAT GETS REPLACED. Patching the read itself
    would leave the load path untested; patching the loader exercises everything below it.
    """

    def _load() -> tuple[series_depth.Probe | None, str]:
        return probe, ""

    original = series_depth.probe
    series_depth.probe = _load
    try:
        return series_depth.depth()
    finally:
        series_depth.probe = original


def two_samples_read_as_a_series(out: list[str]) -> int:
    """Check a depth at the floor answers a delta question."""
    got = _depth_with(_Probe(values=[float(series_depth.SERIES_FLOOR)]))
    if not got.is_series or got.samples != series_depth.SERIES_FLOOR:
        out.append(f"selftest: a depth at the floor read as {got!r}")
        return 1
    return 0


def one_sample_reads_as_a_level(out: list[str]) -> int:
    """Check a depth below the floor is reported as a level — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER CALLING EVERYTHING A SERIES passes the case above and reports the
    question answerable forever. The pair says the floor is where the verdict actually flips.
    """
    got = _depth_with(_Probe(values=[float(series_depth.SERIES_FLOOR - 1)]))
    if got.is_series:
        out.append(f"selftest: a depth below the floor read as a series: {got!r}")
        return 1
    if not got.known:
        out.append(f"selftest: a read depth reported as unknown: {got!r}")
        return 1
    return 0


def an_empty_read_is_zero_and_known(out: list[str]) -> int:
    """Check no samples is a KNOWN zero, not an unknown.

    ⚑ THE STORE ANSWERED. An empty result read from a reachable store is a measurement — zero
    samples — and reporting it as unknown would discard a fact the reader actually has.
    """
    got = _depth_with(_Probe(values=[]))
    if not got.known or got.samples != 0:
        out.append(f"selftest: an empty read reported as {got!r}")
        return 1
    return 0


def an_unreachable_store_is_unknown_not_zero(out: list[str]) -> int:
    """Check the store being down does not read as an absent measurement.

    ⚑⚑⚑ THE WHOLE ITEM. Collapsing unreachable into zero reports a working emitter as a missing
    one, and sends an operator to fix the thing that is not broken.
    """
    got = _depth_with(_Probe(raises=ConnectionError("connection refused")))
    if got.known:
        out.append(f"selftest: an unreachable store read as a depth: {got!r}")
        return 1
    if "UNKNOWN" not in got.why:
        out.append(f"selftest: the unreachable verdict does not say unknown: {got.why!r}")
        return 1
    return 0


def an_unreachable_store_names_its_diagnosis(out: list[str]) -> int:
    """Check the unknown verdict says how to tell which cause it is.

    ⚑ THREE CAUSES, NO PREDICATE. Not-written, not-yet-queryable and store-down are
    indistinguishable here, so the verdict must hand the reader the tool that separates them.
    """
    got = _depth_with(_Probe(raises=ConnectionError("connection refused")))
    if "--reachable" not in got.why:
        out.append(f"selftest: the unknown verdict carries no diagnosis: {got.why!r}")
        return 1
    return 0


def a_malformed_read_is_unknown_not_zero(out: list[str]) -> int:
    """Check an unexpected failure is also a reason rather than a count.

    ⚑ A READ THAT BROKE IS NOT A READ THAT FOUND NOTHING, and the two arrive at this reader
    through different exceptions — so both are pinned rather than one.
    """
    got = _depth_with(_Probe(raises=ValueError("malformed body")))
    if got.known:
        out.append(f"selftest: a malformed read reported a depth: {got!r}")
        return 1
    if "could not be read" not in got.why:
        out.append(f"selftest: the malformed verdict does not name the failure: {got.why!r}")
        return 1
    return 0


def a_missing_probe_is_unknown(out: list[str]) -> int:
    """Check a probe that will not load reports unknown with its reason.

    ⚑ THE THIRD FAILURE. The tool being absent is neither a store problem nor an empty series,
    and a reader that could not consult its instrument must not report a measurement.
    """
    original = series_depth.PROBE
    series_depth.PROBE = "no-such-probe-7b32"
    try:
        got = series_depth.depth()
    finally:
        series_depth.PROBE = original
    if got.known:
        out.append(f"selftest: a missing probe reported a depth: {got!r}")
        return 1
    if "will not load" not in got.why:
        out.append(f"selftest: the missing-probe verdict does not say so: {got.why!r}")
        return 1
    return 0


def the_reader_asks_the_declared_selector(out: list[str]) -> int:
    """Check the query sent is the module's declared one.

    ⚑ A SELECTOR TYPED AT THE CALL SITE is how a reader starts measuring a series its own
    constant does not name — the census reports on one metric and labels it another.
    """
    probe = _Probe(values=[3.0])
    _depth_with(probe)
    if not probe.asked or probe.asked[0][1] != series_depth.SELECTOR:
        out.append(f"selftest: the reader asked {probe.asked!r}")
        return 1
    return 0


def the_window_appears_in_the_selector(out: list[str]) -> int:
    """Check the declared window is what the selector reads over.

    ⚑ TWO SPELLINGS OF ONE WINDOW would let the render claim a period the query never covered.
    """
    if series_depth.WINDOW not in series_depth.SELECTOR:
        out.append(f"selftest: the selector does not read over {series_depth.WINDOW}")
        return 1
    return 0


def an_unknown_render_says_unknown(out: list[str]) -> int:
    """Check the rendered unknown row cannot be mistaken for a count."""
    text = series_depth.render(series_depth.Depth(samples=None, why="store down"))
    if "UNKNOWN" not in text:
        out.append(f"selftest: the unknown render reads as {text!r}")
        return 1
    return 0


def a_level_render_names_what_is_missing(out: list[str]) -> int:
    """Check a shallow depth renders as the reason a delta is unanswerable."""
    text = series_depth.render(series_depth.Depth(samples=1, why=""))
    if "not a series" not in text:
        out.append(f"selftest: the level render does not say what is missing: {text!r}")
        return 1
    return 0


def a_series_render_says_a_delta_is_answerable(out: list[str]) -> int:
    """Check a sufficient depth renders as the closed reading."""
    text = series_depth.render(series_depth.Depth(samples=series_depth.SERIES_FLOOR, why=""))
    if "delta is answerable" not in text:
        out.append(f"selftest: the series render reads as {text!r}")
        return 1
    return 0


_ARMS = (
    two_samples_read_as_a_series,
    one_sample_reads_as_a_level,
    an_empty_read_is_zero_and_known,
    an_unreachable_store_is_unknown_not_zero,
    an_unreachable_store_names_its_diagnosis,
    a_malformed_read_is_unknown_not_zero,
    a_missing_probe_is_unknown,
    the_reader_asks_the_declared_selector,
    the_window_appears_in_the_selector,
    an_unknown_render_says_unknown,
    a_level_render_names_what_is_missing,
    a_series_render_says_a_delta_is_answerable,
)

_CASE_COUNT = 1 + 2 + 1 + 2 + 1 + 2 + 2 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"series-depth selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"series-depth selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
