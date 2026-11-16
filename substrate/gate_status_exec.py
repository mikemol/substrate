# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The process boundary of `gate_status`: run one command, report how it ended.

⚑ THIS IS THE ONLY MODULE OF THE FAMILY THAT STARTS A PROCESS, AND EVERYTHING ELSE TAKES A
`Runner`. That is what lets `gate_status_selftest` substitute a fake and never start a gate, a
lease or a build: the suite proves the parse, the sweep and the report against canned outcomes,
and only this module touches the operating system.

⚑ THE ARGV IS NEVER OPERATOR INPUT: a shell fragment parsed from the hook (run as
`/bin/sh -c <fragment>`, which is what the origin's `shell=True` did) or a vector the caller built
from a declared roster. The `S603` relief for that is a per-file entry in `pyproject.toml`
(substrate:W334), the same shape as the other per-responsibility entries.

⚑ A TIMEOUT IS AN OUTCOME, NOT AN EXCEPTION: `Outcome.timed_out` with `TIMEOUT_RC` (124, the
`timeout(1)` convention) so a sweep records it as a row instead of dying mid-fleet.
"""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, NamedTuple, Protocol

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from pathlib import Path

#: Exit status a timed-out command reports (the `timeout(1)` convention).
TIMEOUT_RC = 124

_SHELL = "/bin/sh"


class Outcome(NamedTuple):
    """What a runner reports: exit status, both streams, and whether the clock ended it."""

    rc: int
    stdout: str
    stderr: str
    timed_out: bool


class Runner(Protocol):
    """A command runner; a `str` is a shell fragment, a sequence is an argv vector."""

    def __call__(
        self,
        cmd: str | Sequence[str],
        cwd: Path,
        env: Mapping[str, str],
        timeout: int,
    ) -> Outcome:
        """Run `cmd` in `cwd` under `env` for at most `timeout` seconds."""
        ...


def run_process(
    cmd: str | Sequence[str],
    cwd: Path,
    env: Mapping[str, str],
    timeout: int,
) -> Outcome:
    """Run `cmd` for real; a `str` goes through `/bin/sh -c`, as the origin's `shell=True` did."""
    argv = [_SHELL, "-c", cmd] if isinstance(cmd, str) else list(cmd)
    try:
        done = subprocess.run(  # decoding is the locale's, strict, as the origin's text=True was
            argv,
            cwd=cwd,
            env=dict(env),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return Outcome(TIMEOUT_RC, "", "", timed_out=True)
    return Outcome(done.returncode, done.stdout, done.stderr, timed_out=False)
