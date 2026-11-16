#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Report whether a generated census may be synced, by running its deriving tool's suite.

⚑⚑⚑ THE CONTRACT. A census is an artifact DERIVED from a tool, and syncing it stamps that tool's
current output as authoritative. If the tool's own suite is failing, the sync launders output from
a broken derivation into an artifact that reads as authoritative — and the next reader trusts the
artifact rather than re-running the suite. Measured: `sql_lift --check-census` reports STALE and
`--sync-census` would regenerate it while that tool's own suite is red, its falsified cases pinned
on a walk an in-flight rewrite removed. None of the three sync sites has a precondition today.

⚑⚑ THE CHECK RUNS THE SUITE; IT DOES NOT READ A LEDGER. A recorded outcome answers *what the suite
did when it last ran*, which is a different question from *what it does now* — and the gap between
them is exactly the window a sync opens. Reading a recorded last-outcome in place of a run is the
defect this session already recorded once; encoding it here would be recording it twice.

⚑⚑ AND THE THIRD STATE IS THE ONE A BOOLEAN CANNOT HOLD. A suite that will not RUN — a missing
dependency, an absent database, a tool that is not there — has not FAILED. It is UNVERIFIABLE, and
reporting that as failure blames the tool for a defect in the environment, while reporting it as
success licenses the very sync this exists to refuse. Both collapses are wrong in a different
direction, so neither is available. `check_stub_authority` and `check_assign_types` reached this
same three-way split independently.

⚑ WHAT THIS CAN AND CANNOT SEE, stated because a green verdict here is a fact about the SUITE. It
sees whether the declared suite command exits zero. It does NOT see whether the suite COVERS the
derivation the census reads — a tool whose suite passes while testing something else entirely
reports PASSING, and this check cannot tell. It also cannot see a census whose drift comes from a
tool it does not name. A PASSING verdict licenses the sync; it does not certify the census.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from enum import Enum

from substrate import corpus

# How long a suite may run before the reader gives up. ⚑ A CEILING ON WAITING, NOT A PREDICTION:
# too generous costs nothing when the suite finishes early, too tight reports a slow suite as
# unverifiable.
TIMEOUT = 600

# The flag every suite in this repo answers to (⟡selftest-discovery).
SUITE_FLAG = "--selftest"

# How many characters of a suite's own output a verdict carries. ⚑ NAMED ONCE: the bound appears
# in the slice and nowhere else, so a report cannot claim elision over text it showed in full.
EXCERPT = 400


class State(Enum):
    """What a reader may conclude about a sync site's precondition.

    ⚑ THREE STATES, NOT A BOOLEAN. PASSING licenses the sync; FAILING refuses it; UNVERIFIABLE
    refuses it for a DIFFERENT reason and calls for a different repair — fix the environment, not
    the tool. Collapsing the last two makes a missing dependency look like a broken derivation.
    """

    PASSING = "passing"
    FAILING = "failing"
    UNVERIFIABLE = "unverifiable"


@dataclass(frozen=True, slots=True)
class Site:
    """A census-sync site: the tool, its sync mode, and the suite that must pass first."""

    # How this site is named in a report.
    label: str
    # The tool that derives the census, relative to the repo root.
    tool: tuple[str, ...]
    # The mode that would write the census.
    sync_mode: str
    # The mode that runs the tool's own suite.
    suite_mode: str = SUITE_FLAG
    # How long THIS site's suite may run. ⚑ PER-SITE because suites differ by orders of magnitude,
    # and one ceiling sized for the slowest reports every faster one as unverifiable far too late.
    timeout: int = TIMEOUT


# The three sites sharing this shape. ⚑ ENUMERATED, NOT DISCOVERED, and that is a LIMIT worth
# stating: a fourth sync site added tomorrow is invisible here until it is listed. The alternative
# — globbing for `--sync` flags — would silently pick up modes that write something other than a
# census, which is a worse failure than a known-incomplete roster.
SITES = (
    Site(label="sql-lift", tool=("jea", "metalanguage", "sql_lift.py"), sync_mode="--sync-census"),
    Site(label="gate-census", tool=("scripts", "gate_census.py"), sync_mode="--sync"),
    Site(
        label="build-makefiles",
        tool=("scripts", "gen_build_makefiles.py"),
        sync_mode="--sync-census",
    ),
)


@dataclass(frozen=True, slots=True)
class Verdict:
    """Whether one site's census may be synced, and the evidence for that."""

    site: Site
    state: State
    # The suite's exit code, when it ran at all.
    code: int | None
    # What the suite said, bounded. Kept for every state: the half that succeeded is still a fact.
    output: str
    why: str

    @property
    def may_sync(self) -> bool:
        """Report whether the sync is licensed.

        ⚑ ONLY PASSING LICENSES IT. Unverifiable is not a pass — an unrun suite is no more evidence
        of correctness than an unreached store is evidence of an empty one.
        """
        return self.state is State.PASSING


def _excerpt(done: subprocess.CompletedProcess[str]) -> str:
    """Return a bounded excerpt of what a suite emitted, either stream."""
    said = (done.stdout or "").strip() or (done.stderr or "").strip()
    return said[:EXCERPT]


def check(site: Site) -> Verdict:
    """Run one site's suite and report whether its census may be synced.

    ⚑ THE SUITE IS RUN, NOT LOOKED UP. Every other spelling of this check answers a question about
    the past, and a sync acts on the present.
    """
    where = corpus.ROOT.joinpath(*site.tool)
    if not where.exists():
        return Verdict(
            site=site,
            state=State.UNVERIFIABLE,
            code=None,
            output="",
            why=f"no tool at {'/'.join(site.tool)} — the suite did not run, "
            f"which is not the same as failing",
        )

    try:
        done = subprocess.run(
            [sys.executable, str(where), site.suite_mode],  # noqa: S603
            capture_output=True,
            text=True,
            timeout=site.timeout,
            check=False,
            cwd=str(corpus.ROOT),
        )
    except subprocess.TimeoutExpired:
        return Verdict(
            site=site,
            state=State.UNVERIFIABLE,
            code=None,
            output="",
            why=f"the suite did not finish within {site.timeout}s — UNVERIFIABLE, "
            f"a reader that waited longer might see either verdict",
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return Verdict(
            site=site,
            state=State.UNVERIFIABLE,
            code=None,
            output="",
            why=f"the suite would not run: {exc}",
        )

    said = _excerpt(done)
    if done.returncode == 0:
        return Verdict(
            site=site,
            state=State.PASSING,
            code=0,
            output=said,
            why=f"{'/'.join(site.tool)} {site.suite_mode} passes; {site.sync_mode} is licensed",
        )
    return Verdict(
        site=site,
        state=State.FAILING,
        code=done.returncode,
        output=said,
        why=f"{'/'.join(site.tool)} {site.suite_mode} exited {done.returncode} — "
        f"{site.sync_mode} would launder a census derived from a tool whose own "
        f"suite is red",
    )


def check_all(sites: tuple[Site, ...] = SITES) -> tuple[Verdict, ...]:
    """Report every declared sync site's precondition."""
    return tuple(check(site) for site in sites)


def render(got: Verdict) -> str:
    """Render one verdict, naming the state as well as the reason."""
    return f"  {got.site.label}: {got.state.value.upper()} — {got.why}"


def render_all(seen: tuple[Verdict, ...]) -> str:
    """Render every verdict plus the count that may sync.

    ⚑ THE DENOMINATOR IS SHOWN. *"1 licensed"* alone hides whether the other two were refused or
    merely unreadable, which is the distinction this module exists to keep.
    """
    lines = [render(one) for one in seen]
    licensed = sum(1 for one in seen if one.may_sync)
    blocked = sum(1 for one in seen if one.state is State.FAILING)
    unknown = sum(1 for one in seen if one.state is State.UNVERIFIABLE)
    lines.append(
        f"  {licensed} of {len(seen)} site(s) may sync ({blocked} refused, {unknown} unverifiable)"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    _seen = check_all()
    sys.stdout.write(render_all(_seen) + "\n")
    sys.exit(0)
