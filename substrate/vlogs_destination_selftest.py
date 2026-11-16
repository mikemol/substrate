#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.vlogs_destination` — the by-name refusal-log address (W38c).

⚑ LUTHEN'S RESOLVER IS REPLACED, NOT CALLED. Every case patches `vmagent_address.resolve`, so the
suite runs on a box with no luthen checkout and never depends on a live cluster name — whose host
reachability is itself unconfirmed. What is under test is this module's composition: the URL it
builds from an answer, and the `None` it hands the emitter when there is no answer.

⚑⚑ THE LOAD-BEARING CASE IS THE UNRESOLVED ONE. The property the retired `ratchet_log` guarded —
a logging failure never turns a refusal into a pass — now rests on `None` reaching mtools'
emitter, which then reports NOT emitted instead of raising. A case that only checked the
resolved URL would pass against a module that raised on an unresolvable port.
"""

from __future__ import annotations

import subprocess
import sys
from unittest import mock

from mikemol.hooks import refusal_log

from substrate import vlogs_destination, vmagent_address


def _answered(port: str, luthen: object) -> tuple[str, int]:
    """Stand in for luthen's resolver answering with a fixed host and port."""
    del port, luthen
    return "logs.example", 9428


def _refused(port: str, luthen: object) -> tuple[str, int]:
    """Stand in for luthen's resolver answering anything but `answered`."""
    del luthen
    msg = f"{port} unresolved: synthetic"
    raise vmagent_address.UnresolvedError(msg)


def _timed_out(port: str, luthen: object) -> tuple[str, int]:
    """Stand in for luthen's resolver hanging past its timeout."""
    del luthen
    raise subprocess.TimeoutExpired(cmd=port, timeout=0)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    with mock.patch.object(vmagent_address, "resolve", _answered):
        resolved = vlogs_destination.destination()
    with mock.patch.object(vmagent_address, "resolve", _refused):
        refused = vlogs_destination.destination()
    with mock.patch.object(vmagent_address, "resolve", _timed_out):
        timed_out = vlogs_destination.destination()
        emission = vlogs_destination.log_fallthrough("probe", "unknown-flag", "--nonesuch")
    return [
        (
            "an answered port builds the jsonline ingest URL",
            resolved == f"http://logs.example:9428{vlogs_destination.INGEST}",
        ),
        ("the port is asked for BY NAME", vlogs_destination.PORT == "victorialogs-http"),
        ("an unresolved port yields None, not an exception", refused is None),
        ("a resolver timeout yields None, not an exception", timed_out is None),
        (
            "an unresolvable destination reports NOT emitted rather than raising",
            not emission.emitted and emission.why == refusal_log.NO_DESTINATION,
        ),
    ]


def selftest() -> int:
    """Run every case, reporting failures by name, and return an EXIT CODE.

    ⚑ AN INT, NOT A BOOL: `ratchet_suites.run_all` reads the return as an exit code, so a `True`
    for "passed" counted as exit 1 — a green 5/5 reported as a failed suite (measured).
    """
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"vlogs-destination selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 1)
