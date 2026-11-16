#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sync_precondition` — passing, failing and unverifiable.

⚑⚑⚑ THE THREE-WAY SPLIT IS THE ITEM. A sync site whose suite CANNOT RUN has not been shown to be
broken, and one whose suite FAILS has. They call for different repairs — fix the environment versus
fix the tool — and a boolean gives a caller neither. The arms below pin each state as its own
verdict, and pin that only one of the three licenses a sync.

⚑⚑ THE POSITIVE CONTROL IS LOAD-BEARING. A checker that returned FAILING for everything would pass
every refusal case here and block every sync forever, which reads as safety and is not. The passing
arm is what says the check discriminates rather than merely refuses.

⚑ THE FIXTURES ARE TEMP TOOLS, NEVER THE LIVE SITES. An arm running the real `sql_lift` suite would
pin today's red into this file: it goes green the moment someone repairs that tool, reporting a
FIXED tree as a broken reader. The live verdict belongs in the report, not in a case.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus, sync_precondition

# A fixture tool that exits zero and says so.
_GREEN = "import sys\nsys.stdout.write('fixture selftest: 3/3\\n')\nsys.exit(0)\n"

# A fixture tool that fails the way a real suite does — a nonzero code and a count on stderr.
_RED = "import sys\nsys.stderr.write('fixture selftest: 30/33\\n')\nsys.exit(1)\n"

# A fixture tool that outlives any ceiling the timeout arm gives it.
_SLOW = "import time\ntime.sleep(30)\n"

# What a fixture site is called in a verdict.
_LABEL = "fixture"

# The ceiling the timeout arm imposes. ⚑ ZERO SECONDS so the arm costs no wall time: the point is
# that the ceiling was EXCEEDED, and one second of real sleeping proves nothing extra.
_NO_WAIT = 0


def _site(
    where: str,
    body: str | None,
    wait: int = sync_precondition.TIMEOUT,
    name: str = "fixture_tool.py",
) -> sync_precondition.Site:
    """Write a fixture tool into a temp root and return the site naming it."""
    corpus.ROOT = Path(where)
    if body is not None:
        Path(where, name).write_text(body, encoding="utf-8")
    return sync_precondition.Site(
        label=_LABEL, tool=(name,), sync_mode="--sync-census", timeout=wait
    )


def _check_with(
    body: str | None, wait: int = sync_precondition.TIMEOUT
) -> sync_precondition.Verdict:
    """Run the reader against a fixture tool, restoring the corpus root after."""
    original = corpus.ROOT
    try:
        with tempfile.TemporaryDirectory() as where:
            return sync_precondition.check(_site(where, body, wait))
    finally:
        corpus.ROOT = original


def a_green_suite_is_passing(out: list[str]) -> int:
    """Check a suite exiting zero reports PASSING — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A CHECKER THAT REFUSED EVERYTHING passes every other arm here and blocks every
    sync permanently, which looks like caution and is a broken instrument.
    """
    got = _check_with(_GREEN)
    if got.state is not sync_precondition.State.PASSING:
        out.append(f"selftest: a green suite read as {got.state!r} ({got.why!r})")
        return 1
    if not got.may_sync:
        out.append("selftest: a green suite did not license the sync")
        return 1
    return 0


def a_red_suite_is_failing(out: list[str]) -> int:
    """Check a suite exiting nonzero reports FAILING and refuses the sync."""
    got = _check_with(_RED)
    if got.state is not sync_precondition.State.FAILING:
        out.append(f"selftest: a red suite read as {got.state!r}")
        return 1
    if got.may_sync:
        out.append("selftest: a red suite licensed the sync")
        return 1
    return 0


def a_red_verdict_names_the_laundering(out: list[str]) -> int:
    """Check the refusal states the CONSEQUENCE, not just the exit code.

    ⚑ A BARE *"EXITED 1"* IS NOT THE CONTRACT. What makes this a refusal rather than a warning is
    that syncing would stamp a broken derivation as authoritative, and the verdict has to say so.
    """
    got = _check_with(_RED)
    if "launder" not in got.why:
        out.append(f"selftest: the red reason does not name the consequence: {got.why!r}")
        return 1
    return 0


def a_red_verdict_carries_the_exit_code(out: list[str]) -> int:
    """Check the suite's own exit code survives into the verdict."""
    got = _check_with(_RED)
    if got.code != 1:
        out.append(f"selftest: the red verdict carries code {got.code!r}")
        return 1
    return 0


def a_red_verdict_keeps_the_suite_output(out: list[str]) -> int:
    """Check what the suite SAID is reported, including on stderr.

    ⚑ THE COUNT IS THE ACTIONABLE PART. *"30/33"* tells a reader how far the tool is from green;
    an exit code alone tells them only that it is not.
    """
    got = _check_with(_RED)
    if "30/33" not in got.output:
        out.append(f"selftest: the red verdict lost the suite output: {got.output!r}")
        return 1
    return 0


def a_missing_tool_is_unverifiable(out: list[str]) -> int:
    """Check an absent tool reports UNVERIFIABLE, not FAILING.

    ⚑⚑⚑ THE STATE A BOOLEAN CANNOT HOLD. A suite that did not run has not failed, and blaming the
    tool for the environment is the same shape as reading an unreachable store as an empty one.
    """
    got = _check_with(None)
    if got.state is not sync_precondition.State.UNVERIFIABLE:
        out.append(f"selftest: a missing tool read as {got.state!r}")
        return 1
    return 0


def an_unverifiable_verdict_still_refuses(out: list[str]) -> int:
    """Check UNVERIFIABLE does not license the sync either.

    ⚑ UNVERIFIABLE IS NOT A PASS. It refuses for a different reason than FAILING does, but it
    refuses — an unrun suite is not evidence of correctness.
    """
    got = _check_with(None)
    if got.may_sync:
        out.append("selftest: an unverifiable site licensed the sync")
        return 1
    return 0


def an_unverifiable_verdict_says_it_did_not_run(out: list[str]) -> int:
    """Check the unverifiable reason distinguishes itself from a failure in prose too."""
    got = _check_with(None)
    if "not the same as failing" not in got.why:
        out.append(f"selftest: the unverifiable reason reads as {got.why!r}")
        return 1
    return 0


def an_unverifiable_verdict_invents_no_exit_code(out: list[str]) -> int:
    """Check a suite that never ran reports no code rather than a fabricated zero.

    ⚑ A ZERO HERE WOULD READ AS SUCCESS at any call site checking the code instead of the state.
    """
    got = _check_with(None)
    if got.code is not None:
        out.append(f"selftest: an unverifiable verdict invented code {got.code!r}")
        return 1
    return 0


def a_timeout_is_unverifiable(out: list[str]) -> int:
    """Check a suite that outruns its ceiling reports UNVERIFIABLE, not FAILING.

    ⚑ THE CEILING IS ON WAITING, NOT A PREDICTION. A slow suite has not been shown to be broken, so
    a timeout may not be banked as a failure — the same reasoning that makes an absent tool
    unverifiable rather than red.
    """
    got = _check_with(_SLOW, _NO_WAIT)
    if got.state is not sync_precondition.State.UNVERIFIABLE:
        out.append(f"selftest: a timeout read as {got.state!r} ({got.why!r})")
        return 1
    if got.may_sync:
        out.append("selftest: a timed-out suite licensed the sync")
        return 1
    return 0


def a_timeout_names_the_ceiling_it_hit(out: list[str]) -> int:
    """Check the timeout reason reports THIS site's ceiling, not the module default.

    ⚑ A VERDICT QUOTING THE DEFAULT while a site ran under its own ceiling tells the reader to
    lengthen a bound that was never in play.
    """
    got = _check_with(_SLOW, _NO_WAIT)
    if f"{_NO_WAIT}s" not in got.why:
        out.append(f"selftest: the timeout reason names the wrong ceiling: {got.why!r}")
        return 1
    return 0


def every_declared_site_names_a_sync_mode(out: list[str]) -> int:
    """Check each declared site carries the mode it is gating.

    ⚑ A SITE WITHOUT ITS SYNC MODE cannot say what it is refusing, so the verdict degrades into a
    bare tool name and the reader has to guess which write was blocked.
    """
    for site in sync_precondition.SITES:
        if not site.sync_mode.startswith("--"):
            out.append(f"selftest: {site.label} declares sync mode {site.sync_mode!r}")
            return 1
        if not site.tool:
            out.append(f"selftest: {site.label} names no tool")
            return 1
    return 0


def the_declared_sites_are_distinct(out: list[str]) -> int:
    """Check no two sites share a label or a tool path.

    ⚑ A DUPLICATE LABEL makes two verdicts indistinguishable in the report, which is how a refusal
    gets attributed to the wrong tool.
    """
    labels = {site.label for site in sync_precondition.SITES}
    tools = {site.tool for site in sync_precondition.SITES}
    if len(labels) != len(sync_precondition.SITES):
        out.append(f"selftest: {len(sync_precondition.SITES)} site(s) share {len(labels)} label(s)")
        return 1
    if len(tools) != len(sync_precondition.SITES):
        out.append(f"selftest: {len(sync_precondition.SITES)} site(s) share {len(tools)} tool(s)")
        return 1
    return 0


def every_state_renders_distinguishably(out: list[str]) -> int:
    """Check the three verdicts do not render as the same line.

    ⚑ A RENDER THAT COLLAPSES TWO STATES undoes the split at the last step, where the reader looks.
    """
    site = sync_precondition.SITES[0]
    seen = {
        sync_precondition.render(
            sync_precondition.Verdict(site=site, state=state, code=None, output="", why="x")
        )
        for state in sync_precondition.State
    }
    if len(seen) != len(sync_precondition.State):
        out.append(f"selftest: the states render to {len(seen)} distinct line(s)")
        return 1
    return 0


def the_summary_shows_the_denominator(out: list[str]) -> int:
    """Check the roll-up reports refused and unverifiable separately.

    ⚑⚑ *"1 OF 3 MAY SYNC"* ALONE HIDES THE SPLIT that the whole module exists to keep — whether the
    other two were refused on evidence or merely could not be read.
    """
    site = sync_precondition.SITES[0]
    seen = tuple(
        sync_precondition.Verdict(site=site, state=state, code=None, output="", why="x")
        for state in sync_precondition.State
    )
    said = sync_precondition.render_all(seen)
    if "1 of 3 site(s) may sync" not in said:
        out.append(f"selftest: the summary reads as {said!r}")
        return 1
    if "1 refused" not in said or "1 unverifiable" not in said:
        out.append(f"selftest: the summary collapses the refusal kinds: {said!r}")
        return 1
    return 0


_ARMS = (
    a_green_suite_is_passing,
    a_red_suite_is_failing,
    a_red_verdict_names_the_laundering,
    a_red_verdict_carries_the_exit_code,
    a_red_verdict_keeps_the_suite_output,
    a_missing_tool_is_unverifiable,
    an_unverifiable_verdict_still_refuses,
    an_unverifiable_verdict_says_it_did_not_run,
    an_unverifiable_verdict_invents_no_exit_code,
    a_timeout_is_unverifiable,
    a_timeout_names_the_ceiling_it_hit,
    every_declared_site_names_a_sync_mode,
    the_declared_sites_are_distinct,
    every_state_renders_distinguishably,
    the_summary_shows_the_denominator,
)

_CASE_COUNT = 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1 + 2 + 2 + 1 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"sync-precondition selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"sync-precondition selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
