#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The full-build argv and the captured run - one spelling of `make -C agda -j<N>`.

THE THIRD CUT OF THE DRAIN'S FOURTH FILE (`scratch/split_pipeline.py:186-225`, W4 tick 41).
Three call sites once spelled `["make", "-C", AG, "-j"]` by hand - one capability in three
copies - and `make_cmd` collapsed them, reading the `-j` width from the ONE authority
(`gen_build_makefiles.AGDA_JOBS`, env `AGDA_JOBS` overriding). The width replaced a bare `-j`
whose rationale was sound and is kept: unlimited `-j` lets membudget's semaphore self-tune
parallelism to RAM, and what the semaphore does not bound is PROCESS COUNT, so the cap bounds
the queue, not the throttle.

THE JOBS FLAG IS A PARAMETER, NOT A LOAD. The origin loads `gen_build_makefiles.py` through
`importlib` by path inside the function, with a bare `except Exception` falling back to `-j` -
a second copy of what `gen_build_makefiles.jobs_flag()` already is. A `substrate/` module cannot
import `scripts/` bare (the `climode` lesson: a bare site resolves only under a `sys.path`
insert and fails for an installed wheel), so the caller supplies the fragment, and the shim's
fallback stays where the shim is. `BARE_JOBS` names the fallback so no caller re-spells it.

⚑ THE ORIGIN'S `DEFAULT_MB = 384` IS NOT CARRIED, AND THAT IS A FINDING. It restates the
membudget lease ceiling - a BUILD FIGURE whose authority is `scripts/membudget` - in a fifth
file, which is exactly the stale-copy shape the always-loaded instructions name ("do not quote
a cap, a lease default, or a build figure"). `enforce_ban` reads it through this module; when
the shim lands it reads the authority instead. A constant restated here would have shipped the
defect into the package.

`run` is the captured subprocess: it returns the command's OWN exit code and its interleaved
output, never a pipeline's, and prints the header line the origin printed so a log reads the
same.
"""

from __future__ import annotations

import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

# The agda tree, relative to the repo root, as `make -C` takes it.
AGDA_DIR = "agda"
# The pre-⟡agda-jobs fallback: unlimited, the semaphore still governs.
BARE_JOBS: tuple[str, ...] = ("-j",)


def make_cmd(jobs: Sequence[str] = BARE_JOBS, *extra: str, agda_dir: str = AGDA_DIR) -> list[str]:
    """Return the full-build argv: `make -C <agda_dir> <jobs...> <extra...>`."""
    return ["make", "-C", agda_dir, *jobs, *extra]


def run(cmd: Sequence[str], cwd: str | None = None, label: str | None = None) -> tuple[int, str]:
    """Run `cmd` capturing stdout+stderr; print the header; return (rc, out) - the command's own."""
    suffix = f"   [{label}]" if label else ""
    sys.stdout.write(f"$ {' '.join(cmd)}{suffix}\n")
    p = subprocess.run(
        list(cmd),
        cwd=cwd,
        stdout=subprocess.PIPE,  # noqa: S603 - the caller's argv, never a shell
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return p.returncode, p.stdout
