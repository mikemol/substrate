# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sandbox_watch` — the alarm's judgement, with no store."""

from __future__ import annotations

import sys

from substrate import sandbox_watch as sw

_USAGE = 2


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    base = {"edge": 10, "obs": 5, "schema_version": 1}
    return [
        ("growth is not a fall", sw.falls(base, {"edge": 12, "obs": 5, "schema_version": 1}) == []),
        (
            "a falling count is named with before and after",
            sw.falls(base, {"edge": 9, "obs": 5, "schema_version": 1}) == ["edge 10→9"],
        ),
        (
            "a vanished table is a fall",
            sw.falls(base, {"obs": 5, "schema_version": 1}) == ["edge 10→(gone)"],
        ),
        (
            "a new table is not a fall",
            sw.falls(base, {"edge": 10, "obs": 5, "schema_version": 1, "obs_node": 0}) == [],
        ),
        (
            "schema_version is exempt, as luthen's witness exempts it",
            sw.falls(base, {"edge": 10, "obs": 5, "schema_version": 0}) == [],
        ),
        ("a malformed --every is refused", sw.main(["--every", "x"]) == _USAGE),
        ("a zero --idle is refused", sw.main(["--idle", "0"]) == _USAGE),
        ("an unknown flag is refused", sw.main(["--forever"]) == _USAGE),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"sandbox-watch selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
