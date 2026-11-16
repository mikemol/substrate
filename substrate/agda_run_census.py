#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""BUILD then READ - the whole census as one command, with the stamp guard around the build.

THE NINTH CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_census.py:710-783`, W4 tick 48). Built
because the sequence kept being reassembled by hand ("you're still running two different
commands"): a build must precede the read; `-k`, so one run yields the FULL error census - the
error list IS the worklist, and `-k` is what makes it a list instead of a single item; the `-j`
width from the ONE authority; where the log goes, so the build's own failed targets can be
folded in; and that the tree must not be EDITED while it runs. Five facts in a shell line is
exactly the shape this repo keeps retiring.

THE STAMP GUARD IS WHAT MAKES ONE COMMAND SAFE. `tree_stamp` is taken before the build and
re-checked after, so a concurrent edit REFUSES to bank rather than producing a blend with no
referent. Automating the sequence does not weaken the guard; it removes the step where a human
forgets it. A non-zero `make` is EXPECTED, not an abort: with `-k` the build reports every
failure and exits 1, and treating that as fatal would refuse to census exactly the tree that
most needs censusing.

THIS IS A COMPOSITION OF THE CUTS ALREADY LANDED: `agda_build_cmd.make_cmd` spells the argv
(the origin carried a SECOND `importlib` load of `gen_build_makefiles.jobs_flag` here, beside
the one `make_cmd` had - two copies of a reader that already existed), `agda_tree_state.tree_stamp`
is the guard, and the launch itself is a parameter so a suite can fake the build and drive the
straddle branch without compiling anything. The result is a dataclass: the origin returned the
log PATH on success and the integer 2 on refusal - a return SHAPE that forked on the outcome,
so a caller had to test the type to learn which it held.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import agda_build_cmd, agda_tree_state

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

# The build's own output, folded in by `--build-log`: make's failed targets outrank a rederivation.
LOG_NAME = ".build.log"
# The exit the origin returned when it refused to bank a straddled census.
STRADDLED = 2


def launch_to_log(cmd: Sequence[str], cwd: str, log: str) -> int:
    """Run the build with stdout+stderr into `log`; return make's own exit code."""
    with Path(log).open("w", encoding="utf-8") as fh:
        return subprocess.run(
            list(cmd),
            cwd=cwd,
            stdout=fh,  # noqa: S603 - the caller's argv, never a shell
            stderr=subprocess.STDOUT,
            check=False,
        ).returncode


@dataclass(frozen=True)
class CensusRun:
    """One BUILD-then-READ: the argv, the log, make's exit, and whether the tree held still."""

    cmd: list[str]
    log: str
    rc: int
    before: str
    after: str

    @property
    def banked(self) -> bool:
        """Return whether the build's logs may be read as a census of ONE tree."""
        return self.before == self.after

    @property
    def exit(self) -> int:
        """Return the origin's exit: STRADDLED when refused, else 0 (a -k rc is expected)."""
        return 0 if self.banked else STRADDLED


def run_census(
    repo_root: str,
    jobs: Sequence[str],
    agda_dir: str = agda_build_cmd.AGDA_DIR,
    launch: Callable[[Sequence[str], str, str], int] = launch_to_log,
) -> CensusRun:
    """Stamp, build with `-k` into the log, stamp again; the result says whether to bank."""
    sources = str(Path(repo_root) / agda_dir)
    before = agda_tree_state.tree_stamp(sources)
    cmd = agda_build_cmd.make_cmd(jobs, "-k", agda_dir=agda_dir)
    log = str(Path(repo_root) / LOG_NAME)
    rc = launch(cmd, repo_root, log)
    after = agda_tree_state.tree_stamp(sources)
    return CensusRun(cmd=cmd, log=log, rc=rc, before=before, after=after)
