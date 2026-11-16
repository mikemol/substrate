# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Run the Agda build under `-k`, refusing to bank a result that straddles an edit.

Extracted from `scratch/split_census.py` as part of ⟡drain-split-census. One
responsibility: sequence the build that PRODUCES the census artifacts and decide whether
the tree held still while it ran. Reading those artifacts is `substrate.agda_census`;
reporting the outcome to an operator is the CLI's.

⚑ BUILT BECAUSE THE SEQUENCE KEPT BEING REASSEMBLED BY HAND (operator: *"you're still
running two different commands"*). `--from-build` READS the build's logs, but nothing
PRODUCED them, so every invocation of *"do the census"* meant re-deriving five separate
pieces of knowledge: that a build must precede the read at all; `-k`, so one run yields the
FULL error census rather than the first failure — the error list IS the worklist, and `-k`
is what makes it a list instead of a single item; the `-j` width, from the ONE authority
(⟡agda-jobs); where the log goes, so make's own failed targets can be folded in; and that
the tree must not be EDITED while it runs. **Five facts in a shell line is exactly the
shape this repo keeps retiring.**

⚑ THE ORIGIN PRINTED ITS OWN PROGRESS AND VERDICT, AND THAT IS WHY IT COULD NOT BE A
LIBRARY. `T201` refuses `print` here, which reads as a lint rule and is a design finding:
a function that both performs the build and narrates it has two reasons to change, and its
caller cannot obtain the verdict without also obtaining the narration. The result is
returned as data; `scripts/agda_census_cli.py` renders it.

⚑⚑⚑ THE ⟡agda-jobs AUTHORITY IS REACHED AS A SUBPROCESS, NOT AS AN IMPORT, AND THAT IS A
PACKAGING FACT RATHER THAN A STYLE ONE. This module held `from gen_build_makefiles import
jobs_flag` — a BARE name resolving only under a `sys.path` insert into `scripts/`, which is
not a package. `substrate/adopter_import.py` measured the consequence: this module was one
of exactly two in the whole tree that `reaches-unpackaged` blocks SOLELY, so an adopter
installing the wheel got `ModuleNotFoundError: No module named 'gen_build_makefiles'`.
`--reach-back` further reported this module as that name's ONLY consumer, so the edge
drains to zero here rather than being narrowed.

⚑⚑ AND THE STUB IS WHY THIS WAS INVISIBLE. `stubs/gen_build_makefiles.pyi` makes the bare
import TYPE-CHECK, so every gate reading types was green while the runtime import could not
resolve for anyone outside this checkout. **A stub is a claim about SIGNATURES, never about
IMPORTABILITY** — the two are different properties, and a green type check on the first
reads as evidence for the second to anyone not looking for the distinction.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from scripts.agda_build import jobs
from substrate import corpus
from substrate.agda_tree_state import tree_stamp

# The exit code that says the tree moved under the build, so nothing may be banked.
STRADDLED = 2


@dataclass(frozen=True, slots=True)
class CensusRun:
    """The outcome of one build-then-read cycle.

    `log` is where make's combined output landed. `code` is make's own exit status, which is
    routinely non-zero and is NOT a failure signal here. `before` and `after` are the tree
    stamps bracketing the run; when they differ the result must not be banked, and
    `straddled` says so without the caller re-deriving the comparison.
    """

    log: str
    code: int
    before: str
    after: str

    @property
    def straddled(self) -> bool:
        """Report whether the tree changed while the build ran."""
        return self.before != self.after


def census_jobs_flag(width: int | None = None) -> list[str]:
    """Return make's job flag — ⟡agda-jobs, from the ONE authority.

    An explicit `width` argument still wins: a caller who names a width gets it. The default
    comes from `scripts.agda_build.jobs`, which shells out to
    `gen_build_makefiles.py --jobs` — never a bare `-j` typed here and never a number.

    ⚑⚑ THE AUTHORITY IS THE SAME; THE ROUTE TO IT IS NOT. An earlier form imported
    `jobs_flag` at module scope by BARE name, and argued that this was the safer shape
    because failing to reach the authority became an ImportError at load rather than a
    silent per-call substitution. **That argument was sound about an IMPORT and does not
    transfer to a SUBPROCESS**: a subprocess boundary has no load-time moment to fail at, so
    the choice is between reporting an unreadable width and degrading. The degrade is taken
    deliberately here, on the reasoning `scripts/agda_build.jobs` already records — a bare
    `-j` is SAFE because membudget's semaphore still governs admission by RAM, so the
    degradation costs more PROCESSES and never more MEMORY.

    ⚑ SO THE PREMISE CHANGED RATHER THAN THE EARLIER READING BEING WRONG. An inert guard is
    worse than none, which is why the old fallback was deleted when the import was
    module-scope; under a subprocess the same fallback is REACHABLE, which is the property
    that made it worth deleting and now makes it worth keeping.
    """
    if width:
        return [f"-j{width}"]
    found = jobs()
    return ["-j", found] if found else ["-j"]


def build_command(root: str = "agda", width: int | None = None) -> list[str]:
    """Return the census build's argv. Named separately so a caller can SHOW it."""
    return ["make", "-C", root, "-k", *census_jobs_flag(width)]


def run_census(root: str = "agda", width: int | None = None) -> CensusRun:
    """Build with `-k` and return the run's outcome, stamped on both sides.

    ⚑ THE STAMP GUARD IS WHAT MAKES THIS SAFE AS ONE COMMAND: `tree_stamp()` is taken before
    the build and re-checked after, so a concurrent edit is REPORTED rather than producing a
    blend with no referent. Automating the sequence does not weaken the guard; it removes
    the step where a human forgets it.

    ⚑ A NON-ZERO `make` IS EXPECTED, NOT AN ABORT. With `-k` the build reports every failure
    and exits 1; treating that as fatal would refuse to census exactly the tree that most
    needs censusing. The code is returned for the caller to render, never raised on.

    ⚑ THE SNAPSHOT GUARD IS ARMED BY THE CLI, NOT HERE, and that placement is the finding
    the snapshot-guard gate was naming. This function opens `.build.log` for writing — a
    read-then-rewrite of a repo file, the shape that made 33 files unrecoverable — but it is
    a LIBRARY function, and `edit_snapshot.guard` refuses when the process's mutation intent
    is unstated. Arming it here would make every importer's intent this function's business;
    arming it at the entry point is where the invocation's intent actually lives.
    """
    before = tree_stamp(root)
    log = corpus.ROOT / ".build.log"
    with log.open("w", encoding="utf-8") as handle:
        code = subprocess.call(
            build_command(root, width), cwd=corpus.ROOT, stdout=handle, stderr=subprocess.STDOUT
        )
    return CensusRun(str(log), code, before, tree_stamp(root))
