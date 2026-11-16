#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.probe_kernel` — a probe that reports nothing is decoration.

⚑⚑⚑ THE BLIND-PROBE CASE IS THE ITEM. A totality probe returning `[]` on a corrupted file looks
exactly like one returning `[]` on a clean one, and the second reading is the one that gets
banked. So the arms below drive a probe that stays silent and assert the reader calls it BLIND —
without that, every other case here passes against an instrument measuring nothing.

⚑⚑ AND THE FABRICATION CASE IS ASSERTED ON THE READER, NOT THE PROBE. A probe that merely
REPORTED a swallowed entry would still leave the census inventing a key. What must hold is that a
`%`-comment naming `@misc{GHOST,` never becomes a header — a missing row can be caught by a
denominator, an invented row corroborates itself.

⚑ THE FIXTURES ARE FAKE READERS. A case driving the live `bibstruct` measures today's parser: it
discriminates on all seven classes right now, so a case pinning that would go red the moment
someone widens a regex — reporting a repair as a defect. What is asserted is that this reader
reaches the right verdict about whatever probe it is handed.
"""

from __future__ import annotations

import sys

from substrate import probe_kernel

# How many unaccounted constructs the live-failure fixture reports. ⚑ NAMED so the assertion
# reads against a declaration rather than a number typed twice.
_LIVE_ROWS = 3


class _Reader:
    """A bib reader whose totality answer is chosen by the case."""

    def __init__(self, *, reports: bool = True, ghost: bool = False, live: int = 0) -> None:
        self._reports = reports
        self._ghost = ghost
        self._live = live
        self.asked: list[str | None] = []

    def roundtrip(self, path: str | None = None) -> list[tuple[str, str, str]]:
        """Report a finding per corrupted input, or nothing when blind."""
        self.asked.append(path)
        if path is None:
            return [("live", f"row{n}", "unaccounted") for n in range(self._live)]
        return [("drop", "K", "detail")] if self._reports else []

    def entries(self, path: str | None = None) -> dict[str, dict[str, str]]:
        """Return the parse, optionally fabricating a key from a comment."""
        del path
        if self._ghost:
            return {probe_kernel.GHOST_KEY: {"claim": "invented"}}
        return {probe_kernel.REAL_KEY: {"claim": "a"}}


def _kernel_with(api: _Reader) -> probe_kernel.Blindness:
    """Run the witness against a fixture reader."""

    def _load() -> tuple[probe_kernel.Reader | None, str]:
        return api, ""

    original = probe_kernel.reader
    probe_kernel.reader = _load
    try:
        return probe_kernel.kernel()
    finally:
        probe_kernel.reader = original


def a_discriminating_probe_reports_no_blindness(out: list[str]) -> int:
    """Check a probe catching every corruption is reported as discriminating."""
    got = _kernel_with(_Reader())
    if not got.discriminates or got.blind:
        out.append(f"selftest: a discriminating probe read as {got!r}")
        return 1
    return 0


def a_silent_probe_is_blind_to_every_class(out: list[str]) -> int:
    """Check a probe returning nothing is reported BLIND — THE WHOLE ITEM.

    ⚑⚑⚑ A PROBE THAT REPORTS NOTHING IS DECORATION, and it renders identically to a healthy one.
    Only feeding it a known-corrupt input separates the two, which is why presence is never
    behaviour.
    """
    got = _kernel_with(_Reader(reports=False))
    if got.discriminates:
        out.append("selftest: a silent probe was reported as discriminating")
        return 1
    if len(got.blind) != len(probe_kernel.SILENT_DROPS):
        out.append(
            f"selftest: a silent probe read as blind to {len(got.blind)} class(es), "
            f"expected {len(probe_kernel.SILENT_DROPS)}"
        )
        return 1
    return 0


def every_silent_drop_class_is_exercised(out: list[str]) -> int:
    """Check each declared fixture is actually fed to the probe.

    ⚑ A FIXTURE NOBODY RUNS is a class nobody checks, and the roster would still read as complete.
    """
    api = _Reader()
    _kernel_with(api)
    written = [asked for asked in api.asked if asked is not None]
    if len(written) < len(probe_kernel.SILENT_DROPS):
        out.append(
            f"selftest: {len(written)} fixture(s) fed, {len(probe_kernel.SILENT_DROPS)} declared"
        )
        return 1
    return 0


def a_fabricating_reader_is_reported(out: list[str]) -> int:
    """Check a comment read as a header is a finding.

    ⚑⚑ THE ONLY CLASS THAT FABRICATES. The reader invents a key and loses the real one, so the
    census reports a clean `n of m` over a file it misread — self-corroborating, unlike an
    omission a denominator would catch.
    """
    got = _kernel_with(_Reader(ghost=True))
    if got.discriminates:
        out.append("selftest: a fabricating reader was reported as discriminating")
        return 1
    fabrication = [label for label in got.blind if "FABRICATION" in label]
    if not fabrication:
        out.append(f"selftest: the fabrication was not named: {got.blind!r}")
        return 1
    return 0


def a_sound_reader_is_not_accused_of_fabricating(out: list[str]) -> int:
    """Check a reader keeping the real key raises no fabrication finding.

    ⚑ THE POSITIVE CONTROL FOR THE SHARPEST ARM. A reader flagging every parse would satisfy the
    case above while reporting a correct parser as broken.
    """
    got = _kernel_with(_Reader())
    fabrication = [label for label in got.blind if "FABRICATION" in label]
    if fabrication:
        out.append(f"selftest: a sound reader was accused: {fabrication!r}")
        return 1
    return 0


def a_live_failure_is_reported_separately(out: list[str]) -> int:
    """Check a discriminating probe over a non-round-tripping bib is its own verdict.

    ⚑ TWO DIFFERENT FINDINGS. *"The probe cannot see this class"* and *"the live file has an
    unaccounted construct"* call for different work — fix the probe, or fix the file.
    """
    got = _kernel_with(_Reader(live=_LIVE_ROWS))
    if got.blind:
        out.append(f"selftest: a live failure was reported as blindness: {got.blind!r}")
        return 1
    if got.live != _LIVE_ROWS:
        out.append(f"selftest: the live count read as {got.live!r}")
        return 1
    return 0


def the_live_bib_is_only_asked_when_the_probe_discriminates(out: list[str]) -> int:
    """Check a blind probe is not then asked about the live file.

    ⚑⚑ NECESSARY, NOWHERE NEAR SUFFICIENT. `roundtrip(live) == []` from a probe that reports
    nothing is the algebra result that motivated the item — reading it as a verdict is exactly
    the mistake, so it is not even collected.
    """
    api = _Reader(reports=False)
    _kernel_with(api)
    if None in api.asked:
        out.append("selftest: a blind probe was asked about the live bib")
        return 1
    return 0


def a_missing_probe_mode_is_unexercised(out: list[str]) -> int:
    """Check a reader with no totality mode reports UNEXERCISED, not clean.

    ⚑ THE FIRST FINDING. Without the probe, every census over the bib is a count of what its
    parser can see — which is a fact about the reader reported as a fact about the file.
    """
    original = probe_kernel.PROBE_MODE
    probe_kernel.PROBE_MODE = "no_such_mode_5a71"
    try:
        got = probe_kernel.kernel()
    finally:
        probe_kernel.PROBE_MODE = original
    if got.known:
        out.append(f"selftest: a missing probe mode read as measured: {got!r}")
        return 1
    if "totality probe" not in got.why:
        out.append(f"selftest: the missing-mode reason reads as {got.why!r}")
        return 1
    return 0


def an_unloadable_reader_is_unexercised(out: list[str]) -> int:
    """Check a reader that will not load reports its reason."""
    original = probe_kernel.READER
    probe_kernel.READER = "no-such-reader-3e88"
    try:
        got = probe_kernel.kernel()
    finally:
        probe_kernel.READER = original
    if got.known:
        out.append(f"selftest: an unloadable reader read as measured: {got!r}")
        return 1
    if "will not load" not in got.why:
        out.append(f"selftest: the unloadable reason reads as {got.why!r}")
        return 1
    return 0


def an_unexercised_verdict_renders_distinctly(out: list[str]) -> int:
    """Check unexercised cannot be mistaken for the clean reading."""
    text = probe_kernel.render(
        probe_kernel.Blindness(blind=(), live=0, why="bibstruct will not load")
    )
    if "UNEXERCISED" not in text:
        out.append(f"selftest: an unexercised verdict renders as {text!r}")
        return 1
    return 0


def a_blind_verdict_names_every_class(out: list[str]) -> int:
    """Check the render lists what the probe cannot see."""
    text = probe_kernel.render(
        probe_kernel.Blindness(blind=("class one", "class two"), live=0, why="")
    )
    if "class one" not in text or "class two" not in text:
        out.append(f"selftest: the blind render omits a class:\n{text}")
        return 1
    return 0


def the_clean_verdict_states_both_halves(out: list[str]) -> int:
    """Check the closed reading says the probe discriminates AND the bib round-trips.

    ⚑ ONE HALF ALONE IS THE ITEM'S OWN FAILURE MODE — a live round-trip proves nothing about a
    probe that cannot see, and a discriminating probe says nothing about today's file.
    """
    text = probe_kernel.render(probe_kernel.Blindness(blind=(), live=0, why=""))
    if "silent-drop" not in text or "round-trip" not in text:
        out.append(f"selftest: the clean verdict states one half: {text!r}")
        return 1
    return 0


_ARMS = (
    a_discriminating_probe_reports_no_blindness,
    a_silent_probe_is_blind_to_every_class,
    every_silent_drop_class_is_exercised,
    a_fabricating_reader_is_reported,
    a_sound_reader_is_not_accused_of_fabricating,
    a_live_failure_is_reported_separately,
    the_live_bib_is_only_asked_when_the_probe_discriminates,
    a_missing_probe_mode_is_unexercised,
    an_unloadable_reader_is_unexercised,
    an_unexercised_verdict_renders_distinctly,
    a_blind_verdict_names_every_class,
    the_clean_verdict_states_both_halves,
)

_CASE_COUNT = 1 + 2 + 1 + 2 + 1 + 2 + 1 + 2 + 2 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"probe-kernel selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"probe-kernel selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
