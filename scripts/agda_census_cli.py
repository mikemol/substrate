#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run the Agda census and report it — the entry point, and the place intent belongs.

The last cut of ⟡drain-split-census. `scratch/split_census.py` held the DAG, the log index,
the classifier, the census read, the tree stamp and this dispatch in one file, which is why
the per-file gate refused every write to it — including the `edit_snapshot.guard()` the
snapshot-guard gate names as the repair. Each concern now has its own clean module; this is
the dispatch moving out, which is what keeps those modules from being built-then-orphaned.

⚑⚑ THE GUARD BELONGS HERE AND IS NOT YET ARMED, AND THE REASON IS A MEASUREMENT RATHER
THAN A JUDGEMENT. The snapshot-guard gate named `run_census` as the scope holding the first
write, and it was right about the WRITE — `.build.log` is opened for writing over a file
the tool also reads. What a line-scoped mitigation cannot name is the right HOME for the
guard: `guard` checks the INVOCATION's mutation intent, and an invocation is a property of
an entry point rather than of a library function. Arming it inside `run_census` would make
every importer's argv that function's business.

⚑⚑⚑ AND ARMING IT HERE IS BLOCKED BY ONE MISSING STUB, MEASURED NOT ASSUMED. `import
edit_snapshot` in this file yields exactly two findings — `import-not-found` and, following
from it, `Expression has type "Any"` on the `guard` call — because `scratch/` is not a
package and `stubs/edit_snapshot.pyi` does not exist. The per-file gate's own refusal text
names the remedy: *relief lives on the ENUMERABLE side — a STUB that ADDS types for an
untyped dependency*. So this is not a design question left open; it is one stub, and every
other module in the drain is already clean behind it.

⚑ WHAT THAT MEANS FOR A READER RIGHT NOW: this command rewrites `.build.log` unguarded,
exactly as its monolithic ancestor did. The status is unchanged rather than worsened, and
it is now a ONE-LINE change in a clean file instead of an unreachable edit inside a file
carrying a hundred findings. That is the whole point of the drain.

⚑⚑ THE INTENT CONTRACT IS STATED RATHER THAN DEFAULTED, AND THE FIRST CUT OF THIS FILE GOT
IT WRONG IN THE WAY THE CONTRACT EXISTS TO PREVENT. It treated any non-flag word as the
root and everything else as absent, so a plain `--help` fell through to `run_census` and
started a full `make -k` over the Agda tree. **A tool that runs a multi-minute build in
response to a request for its usage has default-apply behaviour**, which is precisely what
`split_pipeline` refuses at its own entry: *a mutating tool must not GUESS*. An unrecognised
word is now a refusal.
"""

from __future__ import annotations

import sys

from substrate.agda_census_run import STRADDLED, build_command, run_census

# ⚑ THE BUILD LOG IS THE SUBJECT OF THE PENDING SNAPSHOT, NOT THE AGDA TREE. `run_census`
# does not edit sources — that is exactly what the tree stamp verifies afterwards — so the
# one file this run rewrites is the log it is about to overwrite. Named here so the guard,
# when it can be armed, has nothing left to decide.
SNAPSHOT_LABEL = "agda_census_cli"
SNAPSHOT_PATHS = (".build.log",)

REFUSED = 2

_USAGE = (
    "usage: agda_census_cli.py --run [<root>]\n"
    "  --run   build <root> (default `agda`) under -k, then report the log path.\n"
    "\n"
    "  This RUNS A FULL BUILD and rewrites .build.log, so it will not start\n"
    "  without --run. State it."
)


def _say(line: str) -> None:
    """Write one reporting line to stdout."""
    sys.stdout.write(f"{line}\n")


def _report(result_code: int, before: str, after: str, log: str) -> int:
    """Render one run's outcome and return the process exit code."""
    _say(
        f"census: make exited {result_code} (with -k, non-zero means failures were "
        f"reported, not that the build did not run)"
    )
    if before != after:
        _say(
            f"census: REFUSING to bank — the tree changed during the build "
            f"({before} -> {after}). A census that straddles an edit measures "
            f"neither tree."
        )
        return STRADDLED
    _say(log)
    return 0


def main(argv: list[str]) -> int:
    """Build the tree under `-k`, then report where the log landed and whether it may bank."""
    if "--run" not in argv:
        sys.stderr.write(f"{_USAGE}\n")
        return REFUSED
    roots = [a for a in argv if not a.startswith("-")]
    if len(roots) > 1:
        sys.stderr.write("agda_census_cli: name at most one root\n")
        return REFUSED
    root = roots[0] if roots else "agda"

    _say(f"census: building — {' '.join(build_command(root))}")
    result = run_census(root)
    return _report(result.code, result.before, result.after, result.log)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
