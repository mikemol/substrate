# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.build_settings` — first, that every value equals the origin's.

⚑⚑⚑ THE DIFFERENTIAL IS WHAT MAKES A SECOND COPY OF A BUILD FIGURE ACCEPTABLE, BRIEFLY. Until the
shim replaces `gen_build_makefiles`, both files hold `MEM_CAP`, `AGDA_JOBS`, the marker and the
paths; this suite fails the moment one changes without the other. CLAUDE.md records a cap restated
in four files while its authority said otherwise — the defect this differential exists to stop.
"""

from __future__ import annotations

import os
import sys

from substrate import build_settings as bs
from substrate import flat_origin

_JOBS_VAR = "AGDA_JOBS"


def _differential(origin: flat_origin.Origin) -> list[tuple[str, bool]]:
    """Return one case per value the origin also holds."""
    return [
        ("MEM_CAP equals the origin's", bs.MEM_CAP == origin.MEM_CAP),
        ("AGDA_JOBS equals the origin's", bs.AGDA_JOBS == origin.AGDA_JOBS),
        ("MARKER equals the origin's", bs.MARKER == origin.MARKER),
        ("SHIM_DIR equals the origin's", str(bs.SHIM_DIR) == origin.SHIM_DIR),
        ("ROOT equals the origin's", str(bs.ROOT) == origin.ROOT),
        ("AGDA_DIR equals the origin's", str(bs.AGDA_DIR) == origin.AGDA_DIR),
        ("SRC equals the origin's", str(bs.SRC) == origin.SRC),
        ("build_ver agrees with the origin", bs.build_ver() == origin.build_ver()),
        ("jobs agrees with the origin", bs.jobs() == origin.jobs()),
        ("jobs_flag agrees with the origin", bs.jobs_flag() == origin.jobs_flag()),
        (
            "MEMBUDGET is the origin's scripts/membudget",
            str(bs.MEMBUDGET) == str(flat_origin.ORIGIN.parent / "membudget"),
        ),
    ]


def _jobs_cases() -> list[tuple[str, bool]]:
    """Return the override cases, restoring the environment whatever happens."""
    saved = os.environ.get(_JOBS_VAR)
    out: list[tuple[str, bool]] = []
    try:
        os.environ[_JOBS_VAR] = "7"
        seven = 7
        out.append(("an AGDA_JOBS override is honoured", bs.jobs() == seven))
        for bad in ("abc", "0", "-3", ""):
            os.environ[_JOBS_VAR] = bad
            refused = False
            try:
                bs.jobs()
            except bs.JobsError:
                refused = True
            out.append((f"AGDA_JOBS={bad!r} refuses rather than falling back", refused))
    finally:
        if saved is None:
            os.environ.pop(_JOBS_VAR, None)
        else:
            os.environ[_JOBS_VAR] = saved
    return out


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out = _differential(flat_origin.load())
    out.extend(_jobs_cases())
    block = bs.shim_block()
    out.append(
        (
            "the shim block names SHIM_DIR and MEMBUDGET",
            f"SHIM_DIR := {bs.SHIM_DIR}" in block and f"MEMBUDGET := {bs.MEMBUDGET}" in block,
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"build-settings selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
