#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `agda_build_cmd` - the argv shape, the fallback, and the captured run.

THE DIFFERENTIAL IS AGAINST THE ORIGIN'S ARGV WITH ITS OWN JOBS READING. `split_pipeline` is
loaded by path and its `make_cmd()` called; whatever `-j` fragment it read from the authority
is the fragment this module is handed, so the two argvs must be byte-equal. If the origin will
not import here the arms are skipped, not failed.

THE RUN ARM USES THE INTERPRETER ITSELF as the command, so the case is hermetic: a script that
writes to both streams and exits 3 must come back as (3, both streams interleaved).
"""

from __future__ import annotations

import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Protocol, cast

from substrate import agda_build_cmd as bc

_ORIGIN = Path(__file__).resolve().parent.parent / "scratch" / "split_pipeline.py"
_EXIT = 3
_SCRIPT = "import sys; sys.stdout.write('out\\n'); sys.stderr.write('err\\n'); sys.exit(3)"

Cases = list[tuple[str, bool]]


class _Origin(Protocol):
    AG: str

    def make_cmd(self, *extra: str) -> list[str]: ...


def _origin() -> _Origin | None:
    """Load `split_pipeline.py` by PATH, or None when it is gone or will not import here."""
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_split_pipeline_origin_bc", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImportError:
        return None
    return cast("_Origin", module)


def _check(cases: Cases, name: str, *, ok: bool) -> None:
    """Append one verdict to the run."""
    cases.append((name, ok))


def _argv_cases(cases: Cases) -> None:
    """Pin the argv shape and the bare fallback."""
    _check(
        cases,
        "the default is the bare -j fallback over the agda tree",
        ok=bc.make_cmd() == ["make", "-C", "agda", "-j"],
    )
    _check(
        cases,
        "a jobs fragment is spliced after -C and before the extras",
        ok=bc.make_cmd(["-j", "20"], "all", "-k")
        == ["make", "-C", "agda", "-j", "20", "all", "-k"],
    )
    _check(cases, "the agda dir is a keyword parameter", ok=bc.make_cmd(agda_dir="x")[2] == "x")


def _run_cases(cases: Cases) -> None:
    """Pin the captured run: the command's own rc, both streams, the header line."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc, out = bc.run([sys.executable, "-c", _SCRIPT], label="probe")
    _check(cases, "run returns the command's own exit code", ok=rc == _EXIT)
    _check(
        cases, "run captures stdout and stderr interleaved", ok="out\n" in out and "err\n" in out
    )
    _check(
        cases,
        "run prints the command header with its label",
        ok=buf.getvalue().startswith("$ ") and "[probe]" in buf.getvalue(),
    )


def _differential_cases(cases: Cases) -> None:
    """Assert the argv equals the origin's, handed the origin's own jobs reading, or skip."""
    o = _origin()
    if o is None:
        _check(cases, "differential: origin unavailable, skipped", ok=True)
        return
    theirs = o.make_cmd("all")
    jobs = theirs[3 : theirs.index("all")]
    _check(
        cases,
        "differential: make_cmd agrees with the origin given its jobs fragment",
        ok=bc.make_cmd(jobs, "all", agda_dir=o.AG) == theirs,
    )
    _check(
        cases,
        "differential: the origin's fragment is -j or -j <n>",
        ok=jobs[0] == "-j" and len(jobs) in (1, 2),
    )


def main() -> int:
    """Run every case; exit 1 if any failed."""
    cases: Cases = []
    _argv_cases(cases)
    _run_cases(cases)
    _differential_cases(cases)
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"agda_build_cmd_selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
