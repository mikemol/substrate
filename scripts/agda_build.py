#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run the repo's ONE Agda build path, and report whether the tree is green.

⚑⚑ THIS EXISTS SO THAT "VERIFY THE AGDA TREE" HAS ONE IMPLEMENTATION AND ONE
SUBPROCESS BOUNDARY. It was extracted from `agda_stdlib_migrator`, which had grown a
per-file `agda --safe` invocation - a second build system, worse than `make` on four
axes at once: no parallelism (one file, then the next), no dependency order (each
invocation re-elaborates shared upstreams in-process rather than once), no
incrementality (no `.agdai` mtime check), and no memory discipline (a bare `agda` on
PATH, outside `membudget`, which is the OOM-the-box path the repo's standing rule
exists to prevent).

⚑ `make -C agda -j` HAS ALL FOUR FOR FREE, and that is not a coincidence - the
generated makefiles inject the agda shim onto PATH by construction, so every compile
routes through `membudget run` and self-throttles by RAM in dependency order. Routing
the old per-file call through `membudget` would have fixed ONE of the four defects and
left a second build system standing next to a correct one. Conform to the tool; do not
rebuild its core.

⚑⚑ AND THE S603 EXEMPTION IS WHY THIS IS ITS OWN FILE RATHER THAN A FIFTH
`per-file-ignores` ENTRY. Four entries naming one rule was already a pattern asking to
become a rule; the operator's framing is that a per-file override is a
per-RESPONSIBILITY override, so the honest question at the fifth is "do these share a
responsibility that wants extracting?" - not "has the glob become convenient?" Running
the repo's build IS a responsibility, distinct from rewriting import lines, so it gets
a module and the migrator gets none.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).absolute().parent.parent
_AGDA_DIR = _ROOT / "agda"
_GEN = _ROOT / "scripts" / "gen_build_makefiles.py"

# How much build output a failure carries back. A build log is unbounded and a caller
# reporting it into a session pays for every line, so the tail is where the errors are.
_TAIL = 2000


def jobs() -> str:
    """Return the build's `-j` width, or `""` when it cannot be read.

    ⚑ ONE AUTHORITY, READ RATHER THAN TYPED. `gen_build_makefiles.AGDA_JOBS` owns this
    number; six call sites once spelled it by hand, which is how conventions drift. An
    unreadable width degrades to a bare `-j`, which is still SAFE - the membudget
    semaphore governs either way, and the cap bounds the process QUEUE rather than the
    throttle.
    """
    p = subprocess.run(
        [sys.executable, str(_GEN), "--jobs"], capture_output=True, text=True, check=False
    )
    width = p.stdout.strip()
    return width if width.isdigit() else ""


def build() -> tuple[bool, str]:
    """Run `make -C agda -j<width>` once and return (green, failure tail).

    ⚑ THE VERDICT IS THE EXIT CODE OF THE PROCESS, never of a pipeline, and `check=False`
    is explicit because a nonzero exit is the ANSWER this function returns rather than an
    error to raise on.
    """
    width = jobs()
    argv = ["make", "-C", str(_AGDA_DIR), f"-j{width}" if width else "-j"]
    p = subprocess.run(argv, capture_output=True, text=True, check=False)
    if p.returncode == 0:
        return True, ""
    return False, (p.stdout + p.stderr)[-_TAIL:]


def main(argv: list[str]) -> int:
    """CLI: run the build and report the verdict."""
    if "--jobs" in argv:
        sys.stdout.write(f"{jobs() or '(unset)'}\n")
        return 0
    ok, tail = build()
    sys.stdout.write(f"agda build: {'green' if ok else 'FAILED'}\n")
    if tail:
        sys.stdout.write(f"{tail}\n")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
