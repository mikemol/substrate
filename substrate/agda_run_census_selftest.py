#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `agda_run_census` - the argv, the log, and the stamp guard in both directions.

THE LAUNCH IS FAKED, so no build runs: a recording launcher captures the argv it was handed and
returns make's `-k` exit (1, failures reported). The guard is driven both ways over a temporary
tree - one launcher leaves the tree alone and the run BANKS, another edits a source mid-build
and the run REFUSES with the origin's exit 2. `launch_to_log` itself is cased once against the
interpreter so the redirect-to-log contract is a case, not an assumption.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import agda_run_census as rc

if TYPE_CHECKING:
    from collections.abc import Sequence

_MAKE_K_RC = 1
_T0, _T1 = 1_000_000_000.0, 1_000_000_500.0

Cases = list[tuple[str, bool]]


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _mirror(root: Path) -> Path:
    """Lay one source under agda/ and return its path."""
    src = root / "agda" / "Substrate" / "A.agda"
    src.parent.mkdir(parents=True)
    src.write_text("module Substrate.A where\n", encoding="utf-8")
    os.utime(src, (_T0, _T0))
    return src


def _run_cases(cases: Cases, root: Path, src: Path) -> None:
    """Pin the argv, the log path, and a banked run."""
    seen: list[list[str]] = []

    def quiet(cmd: Sequence[str], _cwd: str, log: str) -> int:
        seen.append(list(cmd))
        Path(log).write_text("make: *** [x] Error 1\n", encoding="utf-8")
        return _MAKE_K_RC

    run = rc.run_census(str(root), ["-j", "4"], launch=quiet)
    _check(
        cases,
        "the argv is make -C agda -j 4 -k, spelled by agda_build_cmd",
        ok=seen == [["make", "-C", "agda", "-j", "4", "-k"]] and run.cmd == seen[0],
    )
    _check(
        cases,
        "the log lands at <repo>/.build.log and holds the build's output",
        ok=run.log == str(root / rc.LOG_NAME) and "Error 1" in Path(run.log).read_text(),
    )
    _check(
        cases,
        "a -k build's non-zero rc is carried, and the run still banks",
        ok=run.rc == _MAKE_K_RC and run.banked and run.exit == 0,
    )
    _check(cases, "the stamps agree when the tree held still", ok=run.before == run.after)
    _check(cases, "the source is unchanged by a quiet launch", ok=Path(src).stat().st_mtime == _T0)


def _straddle_cases(cases: Cases, root: Path, src: Path) -> None:
    """Pin the refusal: a launcher that edits the tree mid-build is not banked."""

    def noisy(_cmd: Sequence[str], _cwd: str, log: str) -> int:
        Path(log).write_text("", encoding="utf-8")
        os.utime(src, (_T1, _T1))
        return 0

    run = rc.run_census(str(root), ["-j"], launch=noisy)
    _check(
        cases,
        "a tree edited during the build is REFUSED: not banked, exit STRADDLED",
        ok=not run.banked and run.exit == rc.STRADDLED and run.before != run.after,
    )


def _launch_cases(cases: Cases, root: Path) -> None:
    """Pin the production launcher's redirect and exit against the interpreter."""
    log = str(root / "probe.log")
    code = rc.launch_to_log(
        [sys.executable, "-c", "import sys; print('hello'); sys.exit(3)"], str(root), log
    )
    _check(
        cases,
        "launch_to_log returns the command's exit and captures its output in the log",
        ok=code == 3 and Path(log).read_text(encoding="utf-8").strip() == "hello",
    )  # noqa: PLR2004 - the probe's exit


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        src = _mirror(root)
        _run_cases(cases, root, src)
        _straddle_cases(cases, root, src)
        _launch_cases(cases, root)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"agda_run_census_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
