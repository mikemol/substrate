# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Census whether a paydown's remaining population can actually be paid.

⚑⚑⚑ A PAYDOWN WITHOUT THIS RUNS UNTIL IT HITS A WALL AND CALLS THAT A SURPRISE. The drain was
measured to have NO frontier — every one of its entry points is itself gate-refused, so a
queue that looked cheapest-first was a queue with no first. A header paydown over a different
population proceeded module by module on the assumption that the next file would be editable,
and that assumption was never checked against the set.

⚑⚑ THE READER ALREADY EXISTED AND HAD NO CONSUMER FOR THIS QUESTION. `editable.partition`
groups paths into CLEAN, DIRTY and UNKNOWN, running both checkers because the gate runs both —
a ruff-only census calls a file clean that mypy refuses, and the paydown then discovers it one
refused edit at a time. What was missing is a caller that asks it about an arbitrary file set
rather than about the drain's own candidates.

⚑ `UNKNOWN` IS THE ROW THAT MAKES THIS WORTH RUNNING, and it is not an error bucket. A file
whose checker could not run is not clean and not dirty: it is unmeasured, and counting it as
either turns a gap into a verdict. A payable count that silently absorbs its unknowns is the
census-green shape, so the three buckets are reported separately and never summed into a
pass rate.
"""

from __future__ import annotations

import sys

from substrate import editable, file_header, scan_root


def population(scope: str) -> list[str]:
    """Return the header-lacking files under `scope`, as repo-relative paths.

    ⚑ THE SUBJECT IS THE PAYDOWN'S OWN REMAINDER, not every file under the scope. Asking
    whether the whole tree is editable answers a different question than asking whether the
    work still queued can land, and the second is the one a paydown needs.
    """
    where = None if scope == "." else scope
    found = file_header.entries(file_header.population(None, *([] if where is None else [where])))
    return [e.label for e in file_header.missing(found)]


def _by_findings(verdict: editable.Verdict) -> int:
    """Return the sort key: fewest findings first, since those are the nearest to payable."""
    return verdict.findings


def _by_path(verdict: editable.Verdict) -> str:
    """Return the sort key for clean rows, which carry no count to rank by."""
    return verdict.path


def render(
    buckets: dict[str, list[editable.Verdict]], limit: int, *, names_clean: bool = False
) -> str:
    """Render the three buckets, with the dirty rows named and their own counts shown.

    ⚑ THE DIRTY ROWS ARE NAMED BECAUSE A COUNT CANNOT BE AUDITED AGAINST A CASE. `12 dirty`
    invites a plan; twelve paths with their finding counts let a reader see whether the wall
    is one monolith or a spread, which are different problems with different remedies.

    ⚑⚑ AND `names_clean` EXISTS BECAUSE THE ACTIONABLE HALF WAS THE UNNAMEABLE ONE. The rule
    above was applied to DIRTY only, so a tree reporting `1 of 140 payable` handed a reader
    the 139 files they cannot touch and withheld the one they can. A paydown acts on the CLEAN
    set, so the clean set is what it must be able to enumerate.

    ⚑ IT IS OPT-IN RATHER THAN ALWAYS-ON because the two halves are read at different scales:
    a refused tree is legible from its dirty rows, and a payable one would print its whole
    population every run. The flag names which question is being asked.
    """
    clean = buckets[editable.CLEAN]
    dirty = buckets[editable.DIRTY]
    unknown = buckets[editable.UNKNOWN]
    total = len(clean) + len(dirty) + len(unknown)

    out = [f"payable: {len(clean)} of {total} file(s) would accept an edit today"]
    if names_clean and clean:
        out.append(f"  {len(clean)} CLEAN — the paydown can take these today:")
        out.extend(f"      {v.path}" for v in sorted(clean, key=_by_path)[:limit])
    if dirty:
        out.append(f"  {len(dirty)} DIRTY — the gate refuses these, so the paydown stops here:")
        out.extend(
            f"      {v.path:<52} {v.findings:>6} finding(s)"
            for v in sorted(dirty, key=_by_findings)[:limit]
        )
    if unknown:
        out.append(
            f"  {len(unknown)} UNKNOWN — a checker could not run, so these are "
            f"UNMEASURED rather than clean:"
        )
        out.extend(f"      {v.path:<52} {v.why}" for v in unknown[:limit])
    out.append(
        "   ⚑ THE THREE COUNTS ARE NOT SUMMED INTO A RATE. An unknown absorbed into "
        "either side turns a gap into a verdict."
    )
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    """Census the payability of a scope's header-lacking files."""
    flags = [a for a in argv if a.startswith("-")]
    if any(f not in ("--top", "--clean") for f in flags):
        sys.stderr.write("usage: payable_census.py [<path>] [--top N] [--clean]\n")
        return 2

    operands = [a for a in argv if not a.startswith("-")]
    limit = 12
    if "--top" in argv:
        at = argv.index("--top") + 1
        if at >= len(argv) or not argv[at].isdigit():
            sys.stderr.write("payable_census: --top needs a number\n")
            return 2
        limit = int(argv[at])
        operands = [a for a in operands if a != argv[at]]

    scope = scan_root.resolve(operands)
    if isinstance(scope, scan_root.Refusal):
        sys.stderr.write(f"payable_census: {scope.message}\n")
        return 2

    paths = population(scope.root)
    if not paths:
        sys.stdout.write(
            "payable: nothing lacks a header under that scope — "
            "a fact about the SCOPE, not a finished paydown\n"
        )
        return 0
    sys.stdout.write(render(editable.partition(paths), limit, names_clean="--clean" in flags))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
