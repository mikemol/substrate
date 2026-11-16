#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.suite_run` — that the stamp carries the kind, and green is earned.

⚑⚑⚑ THIS SUITE EXISTS BECAUSE THE WRAPPER CAUGHT ITS OWN AUTHOR. The first `make` run through
the new recipe classified `suite_run.py` itself as `silent` — it had no `--selftest` body, so
it printed nothing and exited 0. Under a bare `touch` that would have stamped the target and
gone green: a roster member asserting nothing, indistinguishable from a real pass. The
instrument found the gap on its first pass over the tree.

⚑⚑ NO STAMP ON FAILURE IS THE OTHER HALF, AND IT IS WHAT MAKES THE BUILD RE-RUN. `make` treats
a present, newer-than-source stamp as satisfied, so stamping a failed run would mark the target
done and the next build would skip the suite entirely — a failure that silences itself.

⚑ AND `vacuous` IS THE CASE A MARKER CANNOT HOLD. `verdict_kind` decides it from the reported
record alone (`returncode` is never read on that branch), so a suite can report 0/0 and exit
SUCCESS. Only the kind separates that from a pass.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import suite_run

# A suite that passes: prints a parseable count and exits 0.
_PASSES = "print('fixture selftest: 2/2')\n"

# A suite that asserts nothing but exits SUCCESS — the case a bare marker cannot see.
_VACUOUS = "print('fixture selftest: 0/0')\n"

# A suite whose assertions fail.
_FAILS = "import sys\nprint('fixture selftest: 1/2')\nsys.exit(1)\n"


def _fixture(d: str, name: str, src: str) -> tuple[str, str]:
    """Write a fixture suite; return its path and a stamp path beside it."""
    path = Path(d) / name
    path.write_text(src, encoding="utf-8")
    return str(path), str(Path(d) / (name + ".ran"))


def a_pass_is_recorded_ok(out: list[str]) -> int:
    """Check a passing suite earns `ok`, exits 0, and leaves a stamp."""
    with tempfile.TemporaryDirectory() as d:
        path, stamp = _fixture(d, "p.py", _PASSES)
        code, kind = suite_run.run(path, stamp, "fixture/p.py")
        stamped = Path(stamp).exists()
    bad = 0
    if kind != "ok":
        out.append(f"selftest: a passing suite was classified {kind!r}")
        bad += 1
    if code != 0:
        out.append(f"selftest: a passing suite exited {code}")
        bad += 1
    if not stamped:
        out.append("selftest: a passing suite left no stamp")
        bad += 1
    return bad


def the_stamp_carries_the_kind(out: list[str]) -> int:
    """Check the stamp is a readable record, not an empty marker.

    ⚑ THE STAMP IS OURS TO DEFINE, so it holds the outcome rather than a second file holding
    it beside. Two files carrying one fact can drift; one cannot.

    ⚑ COMPARED AGAINST THE MODULE'S OWN RENDERER, NOT A RE-PARSE. `json.loads` returns `Any`
    and would poison every field read; asserting the exact text the renderer produces is both
    concretely typed and a stronger claim — it pins the FORM a later reader must parse.
    """
    with tempfile.TemporaryDirectory() as d:
        path, stamp = _fixture(d, "s.py", _PASSES)
        suite_run.run(path, stamp, "fixture/s.py")
        body = Path(stamp).read_text(encoding="utf-8")
    want = suite_run.stamp_body("fixture/s.py", "ok", 2, 2)
    if body != want:
        out.append(f"selftest: the stamp reads {body!r}, want {want!r}")
        return 2
    return 0


def a_vacuous_pass_fails_and_leaves_no_stamp(out: list[str]) -> int:
    """Check a suite that asserts nothing and exits 0 is caught and not stamped.

    ⚑⚑ THE WHOLE POINT OF THE WRAPPER. A bare `touch` would mark this done; the kind is the
    only thing distinguishing it from a real pass, and the absent stamp is what re-runs it.
    """
    with tempfile.TemporaryDirectory() as d:
        path, stamp = _fixture(d, "v.py", _VACUOUS)
        code, kind = suite_run.run(path, stamp, "fixture/v.py")
        stamped = Path(stamp).exists()
    bad = 0
    if kind != "vacuous":
        out.append(f"selftest: a 0/0 suite was classified {kind!r}")
        bad += 1
    if code == 0:
        out.append("selftest: a vacuous suite left the target green")
        bad += 1
    if stamped:
        out.append("selftest: a vacuous suite was stamped, so the build would skip it")
        bad += 1
    return bad


def a_failure_is_recorded_as_cases(out: list[str]) -> int:
    """Check failed assertions are classified as `cases`, not merely as failure."""
    with tempfile.TemporaryDirectory() as d:
        path, stamp = _fixture(d, "f.py", _FAILS)
        code, kind = suite_run.run(path, stamp, "fixture/f.py")
        stamped = Path(stamp).exists()
    bad = 0
    if kind != "cases":
        out.append(f"selftest: a 1/2 suite was classified {kind!r}")
        bad += 1
    if code == 0:
        out.append("selftest: a failing suite left the target green")
        bad += 1
    if stamped:
        out.append("selftest: a failing suite was stamped")
        bad += 1
    return bad


# A suite that never returns — the hang the deadline exists to name (W3, ruled 2026-09-20).
_HANGS = "import time\nprint('fixture selftest: starting')\ntime.sleep(60)\n"


def a_hang_is_reported_as_timeout_and_leaves_no_stamp(out: list[str]) -> int:
    """Check a suite past its deadline is `timeout`, exits 1, and is NOT stamped done.

    ⚑ THE DEADLINE IS NAMED EXPLICITLY, so the arm does not depend on the label ledger: the
    explicit variable wins over history exactly as `SELFTEST_MB` does for memory. One second is
    enough to distinguish a hang from a run; the fixture would sleep sixty.
    """
    import os  # noqa: PLC0415 - the one arm that sets the override

    prior = os.environ.get(suite_run.TIMEOUT_ENV)
    os.environ[suite_run.TIMEOUT_ENV] = "1"
    try:
        with tempfile.TemporaryDirectory() as d:
            path, stamp = _fixture(d, "h.py", _HANGS)
            code, kind = suite_run.run(path, stamp, "fixture/h.py")
            stamped = Path(stamp).exists()
    finally:
        if prior is None:
            del os.environ[suite_run.TIMEOUT_ENV]
        else:
            os.environ[suite_run.TIMEOUT_ENV] = prior
    bad = 0
    if kind != suite_run.TIMED_OUT:
        out.append(f"selftest: a hung suite was classified {kind!r}, not timeout")
        bad += 1
    if code != 1:
        out.append(f"selftest: a hung suite exited {code}, not 1")
        bad += 1
    if stamped:
        out.append("selftest: a hung suite was stamped done — make would skip it forever")
        bad += 1
    return bad


def the_explicit_deadline_wins_over_history(out: list[str]) -> int:
    """Check `SELFTEST_TIMEOUT_S` is an instruction, not a default."""
    import os  # noqa: PLC0415 - the one other arm that sets the override

    prior = os.environ.get(suite_run.TIMEOUT_ENV)
    os.environ[suite_run.TIMEOUT_ENV] = "7"
    try:
        got = suite_run.timeout_for("selftest:worklist_gate.py")
    finally:
        if prior is None:
            del os.environ[suite_run.TIMEOUT_ENV]
        else:
            os.environ[suite_run.TIMEOUT_ENV] = prior
    if got.timeout_s != 7 or got.clamped:  # noqa: PLR2004 - the value just named
        out.append(f"selftest: the explicit deadline read back as {got.timeout_s}")
        return 1
    return 0


_ARMS = (
    a_pass_is_recorded_ok,
    the_stamp_carries_the_kind,
    a_vacuous_pass_fails_and_leaves_no_stamp,
    a_failure_is_recorded_as_cases,
    a_hang_is_reported_as_timeout_and_leaves_no_stamp,
    the_explicit_deadline_wins_over_history,
)

_CASE_COUNT = 3 + 2 + 3 + 3 + 3 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"suite-run selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"suite-run selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
