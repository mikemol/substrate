#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The intake manifest: which modules are ready to publish as a package, and which are not.

⚑⚑⚑ THE OPERATOR'S RULING IS THE REASON THIS EXISTS, AND THE RATIONALE PICKS THE CRITERION.
*"mtools publishes substrate's clean code AS PACKAGES, which lets everyone express proper
python dependencies instead of symlinks and copy vendoring."* So intake is not tidying — it
is the mechanism that retires vendoring, and the unit is therefore whatever forms a valid
DISTRIBUTION rather than whatever happens to be clean.

⚑⚑ AND THE THREE PROPERTIES ARE ALREADY COMPUTED BY THREE EXISTING READERS. Nothing here
re-derives them: `promote_frontier` owns *clean with every transitive callee clean*,
`file_header` owns *carries both licence lines*, and `adopter_import` owns *imports nothing
unpackaged at module scope*. This joins them, because the question a package boundary asks
is the CONJUNCTION and no single reader answers it.

⚑ THE CONJUNCTION IS NOT THE CHEAPEST OF THE THREE, WHICH IS WHY IT NEEDS ITS OWN NAME. A
module can be promotable and still reach back into `scratch/` at module scope — measured, and
that reach-back is invisible to promotability because a reach-back to a CLEAN unpackaged
module violates no cleanliness property. Publishing on the promotable count alone would ship
a distribution that cannot be imported.

⚑⚑⚑ AND CLOSURE IS THE PROPERTY INTAKE DEPENDS ON, NOT A FILE COUNT. A peer measured this by
hand for the ratchet island and found the subgraph landable only after computing the closure
— a tracked-file count could not see it. `promote_frontier`'s definition already IS the
closure, so this reads its verdict rather than walking the graph a second time: a second
walk would be a rival authority for one relation.

⚑ WHAT THIS DOES NOT MEASURE, AND WHY IT CANNOT BE A FOURTH COLUMN. The operator requires
ported tests to be BAZEL-ACTION-PER-TEST with the bib a bijection against them
(claim-per-test, test-per-claim). `substrate/arm_claims.py` measures that — so the axis is
no longer unmeasured, which this docstring claimed until it was corrected.

⚑⚑ BUT IT DOES NOT JOIN HERE, BECAUSE THE POPULATIONS DO NOT CORRESPOND. `arm_claims` reports
one row per ARM across the suites; this reports one row per MODULE across the corpus. There
are far more modules than suites, and most modules have no suite at all — so a module counted
ready below is ready on three axes and SILENT on the fourth, which is not the same as passing
it. Adding a fourth column would have to invent a verdict for every module with no arms, and
that invention is exactly the over-glue this repo keeps paying for.

⚑ THE ROLL-UP IS ALSO A DECISION NOBODY HAS MADE: whether one multi-claim arm blocks its whole
module. Until that is ruled on, the honest report is two censuses side by side rather than one
column that presumes the answer.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass

from substrate import corpus, file_header

# The readers this joins. ⚑ INVOKED AS PROGRAMS, not imported, because `promote_frontier`
# lives in `scripts/` and shells out to ruff over the whole corpus — importing it would make
# this module's import time a full lint run.
_FRONTIER = "scripts/promote_frontier.py"
_ADOPTER = "substrate/adopter_import.py"

# How long a corpus-wide reader may take before this refuses to wait.
_TIMEOUT_S = 900

# What `promote_frontier` prints above the list this reader wants, and what ends it.
_PROMOTABLE_HEADER = "-- PROMOTABLE"
_SECTION_END = ("--", "promote-frontier")


@dataclass(frozen=True, slots=True)
class Module:
    """One candidate, and the three properties a distribution needs of it."""

    label: str
    promotable: bool
    header: bool
    adoptable: bool

    @property
    def ready(self) -> bool:
        """Whether this module could ship in a distribution today."""
        return self.promotable and self.header and self.adoptable

    def blockers(self) -> tuple[str, ...]:
        """Name what stands between this module and a distribution.

        ⚑ NAMED, NEVER COUNTED. Three modules each missing a different property is a
        different intake plan from three missing the same one, and a deficit count cannot
        tell them apart.
        """
        out: list[str] = []
        if not self.promotable:
            out.append("not-promotable")
        if not self.header:
            out.append("no-header")
        if not self.adoptable:
            out.append("reaches-unpackaged")
        return tuple(out)


def _run(argv: list[str]) -> tuple[int, str]:
    """Run a reader and return its exit code and output. Never raises."""
    try:
        p = subprocess.run(  # noqa: S603
            [sys.executable, *argv],
            cwd=str(corpus.ROOT),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return 1, str(e)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def promotable_set() -> frozenset[str]:
    """Return the labels `promote_frontier` calls promotable.

    ⚑ ITS VERDICT IS READ, NOT RE-DERIVED. Promotable means *clean, and every transitive
    callee clean* — the closure property intake needs — and walking that graph again here
    would be a second authority for one relation.
    """
    rc, out = _run([_FRONTIER])
    if rc != 0:
        return frozenset()
    keep: list[str] = []
    seen_header = False
    for line in out.splitlines():
        if line.startswith(_PROMOTABLE_HEADER):
            seen_header = True
            continue
        if line.startswith(_SECTION_END):
            seen_header = False
            continue
        if seen_header and line.strip():
            keep.append(line.strip())
    return frozenset(keep)


def blocked_set() -> frozenset[str]:
    """Return the labels `adopter_import` reports as reaching something unpackaged."""
    rc, out = _run([_ADOPTER, "--reach-back"])
    if rc != 0:
        return frozenset()
    keep: list[str] = []
    for line in out.splitlines():
        stripped = line.strip()
        # The consumers are indented under each unpackaged name, as dotted module names.
        if line.startswith("    ") and stripped and "." in stripped and " " not in stripped:
            keep.append(stripped.replace(".", "/") + ".py")
    return frozenset(keep)


def manifest() -> tuple[Module, ...]:
    """Return every corpus module with its three properties resolved."""
    promotable = promotable_set()
    blocked = blocked_set()
    headers = {e.label: e for e in file_header.entries(file_header.population())}
    return tuple(
        Module(
            label=label,
            promotable=label in promotable,
            header=entry.complete,
            adoptable=label not in blocked,
        )
        for label, entry in sorted(headers.items())
    )


def ready(found: tuple[Module, ...]) -> tuple[Module, ...]:
    """Return only the modules a distribution could ship today."""
    return tuple(m for m in found if m.ready)


def by_blocker(found: tuple[Module, ...]) -> dict[str, int]:
    """Return `{blocker: how many modules it holds back}`, for the paydown order."""
    out: dict[str, int] = {}
    for m in found:
        for b in m.blockers():
            out[b] = out.get(b, 0) + 1
    return out


def by_tree(found: tuple[Module, ...]) -> dict[str, tuple[int, int]]:
    """Return `{top-level dir: (ready, total)}`."""
    out: dict[str, tuple[int, int]] = {}
    for m in found:
        tree = m.label.split("/")[0]
        done, total = out.get(tree, (0, 0))
        out[tree] = (done + (1 if m.ready else 0), total + 1)
    return out


def _count_desc(row: tuple[str, int]) -> tuple[int, str]:
    """Sort blockers by how many modules they hold, worst first."""
    return (-row[1], row[0])


def render(found: tuple[Module, ...]) -> str:
    """Render the manifest: per-tree readiness, then what holds the rest back.

    ⚑ A ZERO HERE IS TWO DIFFERENT FACTS AND THE READER MUST NOT COLLAPSE THEM. A tree with
    no ready modules because its readers returned nothing is not a tree with no ready
    modules — so an empty join says so rather than reporting an all-zero table.
    """
    if not found:
        return "intake: no modules read — a fact about the READERS, not the tree\n"

    ok = ready(found)
    if not ok and not any(m.promotable for m in found):
        return (
            "intake: NOTHING promotable in the whole corpus — the frontier reader "
            "returned nothing, which is a fact about the READER\n"
        )

    rows = [f"  {'TREE':<12} {'READY':>6} {'TOTAL':>6}"]
    rows.extend(
        f"  {tree:<12} {done:>6} {total:>6}"
        for tree, (done, total) in sorted(by_tree(found).items())
    )
    rows.append("")
    rows.append(
        f"intake: {len(ok)} of {len(found)} module(s) could ship today — "
        "promotable AND header-conforming AND reaching nothing unpackaged"
    )
    rows.append(
        "  ⚑ THREE AXES, AND THE FOURTH HAS A DIFFERENT POPULATION. Bazel-action-per-"
        "test and the claim/test bijection live at ARM grain — `arm_claims` measures "
        "them, and it reports over SUITES, not modules. Most modules have no suite, "
        "so a module counted ready here is not thereby bijection-ready."
    )
    rows.append("")
    rows.append("  what holds the rest back (a module may carry several):")
    rows.extend(
        f"    {blocker:<22} {count:>5}"
        for blocker, count in sorted(by_blocker(found).items(), key=_count_desc)
    )
    return "\n".join(rows) + "\n"


def sole_blocked(found: tuple[Module, ...], blocker: str) -> tuple[Module, ...]:
    """Return the modules `blocker` holds back ALONE — the ones paying it would release.

    ⚑⚑⚑ THE OVERLAPPING COUNT IS NOT A PAYDOWN ORDER, AND READING IT AS ONE COST SIX BATCHES
    OF MISDIRECTED WORK. `by_blocker` counts every blocker a module carries, so a module with
    three is counted three times and the largest class looks like the frontier. It is not:
    paying a blocker moves a module to READY only when it was that module's LAST one.

    ⚑⚑ MEASURED — the `tests` tree reached zero header-lacking files and stayed at zero READY,
    because every module there fails a different conjunct as well. The header work landed and
    bought nothing, which is what an overlapping count cannot predict and this can.
    """
    return tuple(m for m in found if m.blockers() == (blocker,))


def render_sole(found: tuple[Module, ...]) -> str:
    """Render, per blocker, how many modules it holds back alone versus in total.

    ⚑ BOTH NUMBERS OR NEITHER. The total alone invites the paydown this module's own docstring
    warns against, and the sole count alone hides how much work sits behind a shared blocker.
    The gap between them IS the finding: a blocker with a large total and a small sole count
    is one whose paydown is mostly blocked on something else.
    """
    totals = by_blocker(found)
    rows = ["  BLOCKER               SOLE   TOTAL"]
    rows.extend(
        f"  {blocker:<20} {len(sole_blocked(found, blocker)):>5} {count:>7}"
        for blocker, count in sorted(totals.items(), key=_count_desc)
    )
    rows.append("")
    rows.append(
        "   ⚑ SOLE is what paying that blocker would RELEASE. TOTAL is how many "
        "modules carry it at all."
    )
    rows.append(
        "   ⚑ A module with several blockers appears in every TOTAL and in no SOLE, "
        "so the columns do not sum to the same population."
    )
    return "\n".join(rows) + "\n"


def render_names(found: tuple[Module, ...], blocker: str) -> str:
    """Render the modules `blocker` holds back ALONE, by name.

    ⚑⚑⚑ `render_sole` COUNTS THEM AND I WROTE IT ONE TICK AFTER FILING A FINDING ABOUT
    EXACTLY THAT. A count says how many a paydown would release and cannot say WHICH, so a
    batch drawn from the header-lacking set is a guess about whether any given file moves
    READY — and the `tests` tree is the measured case where the guess was wrong for all
    fourteen of its files.

    ⚑ THE DENOMINATOR IS THE BLOCKER'S TOTAL, so a reader can see at once how much of that
    blocker's population is actually released by paying it. Naming the sole set without the
    total would hide the ratio that makes the sole set worth naming.
    """
    rows = [f"  {b.label}" for b in sorted(sole_blocked(found, blocker), key=_by_label)]
    total = by_blocker(found).get(blocker, 0)
    rows.append(
        f"sole-blocked: {len(rows)} of {total} module(s) carrying {blocker!r} "
        f"would be RELEASED by paying it"
    )
    return "\n".join(rows) + "\n"


def _by_label(module: Module) -> str:
    """Return a module's sort key — its repo-relative label."""
    return module.label


def main(argv: list[str]) -> int:
    """Print the intake manifest for the corpus."""
    known = {"--sole", "--names"}
    flags = [a for a in argv if a.startswith("-")]
    if any(f not in known for f in flags):
        sys.stderr.write("usage: intake_manifest.py [--sole | --names <blocker>]\n")
        return 2
    if "--names" in flags:
        operands = [a for a in argv if not a.startswith("-")]
        if len(operands) != 1:
            sys.stderr.write("intake_manifest: --names takes exactly one blocker name\n")
            return 2
        sys.stdout.write(render_names(manifest(), operands[0]))
        return 0
    found = manifest()
    sys.stdout.write(render_sole(found) if argv == ["--sole"] else render(found))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
