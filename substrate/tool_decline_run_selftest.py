#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.tool_decline_run` — four verdicts, and none may collapse.

⚑⚑⚑ EVERY ARM HERE DRIVES A REAL SUBPROCESS, because the whole claim of this module is that the
check RUNS. A suite that stubbed execution would pass while the module quoted commands nobody
executes — which is the inert-guard shape the record type exists to refuse, reproduced in the
thing built to prevent it.

⚑⚑ UNCHECKED IS NOT LAPSED, AND THE DISTINCTION IS THE SHARPEST ONE HERE. A check that could not
RUN says something about this machine; a check that ran and FAILED says something about the
refusal. Collapsing them reports an environment as a claim — and a slow host would turn a tree of
sound refusals into a tree of apparent lapses.

⚑ AND A LAPSED CHECK DOES NOT MEAN THE REJECTED READING IS NOW TRUE. It means the record stopped
being load-bearing: either the world moved or the check drifted off its subject, and a reader must
open the check before the claim.
"""

from __future__ import annotations

import sys

from substrate import tool_decline, tool_decline_run

# A check that passes, one that fails, and one that cannot run at all.
_PASSES = "true"
_FAILS = "false"
_ABSENT = "this-command-does-not-exist-anywhere-on-this-machine"


def _decline(check: str | None) -> tool_decline.Decline:
    """Build a decline carrying one check."""
    return tool_decline.Decline(
        claim="a tempting reading", instead="what is true instead", check=check, why="the argument"
    )


def a_passing_check_is_guarded(out: list[str]) -> int:
    """Check a refusal backed by a passing command reads as held."""
    got = tool_decline_run.verify((_decline(_PASSES),))
    if got.verdicts[0].verdict != tool_decline_run.GUARDED:
        out.append(f"selftest: a passing check read as {got.verdicts[0].verdict}")
        return 1
    if not got.verdicts[0].holds:
        out.append("selftest: a guarded verdict does not report as holding")
        return 1
    return 0


def a_failing_check_is_lapsed(out: list[str]) -> int:
    """Check a refusal whose check now fails is flagged — THE MODE'S REASON TO EXIST.

    ⚑⚑ A LAPSE IS NOT A PROOF THAT THE REJECTED READING IS TRUE. It says the record stopped being
    load-bearing, which is why the verdict sends a reader to the CHECK rather than to the claim.
    """
    got = tool_decline_run.verify((_decline(_FAILS),))
    if got.verdicts[0].verdict != tool_decline_run.LAPSED:
        out.append(f"selftest: a failing check read as {got.verdicts[0].verdict}")
        return 1
    if got.lapsed != 1:
        out.append(f"selftest: the lapse was not counted: {got.lapsed}")
        return 1
    return 0


def an_unrunnable_check_is_unchecked(out: list[str]) -> int:
    """Check a command that cannot run is distinguished from one that failed — THE ITEM.

    ⚑⚑⚑ COLLAPSING THIS INTO LAPSED REPORTS A FACT ABOUT THIS MACHINE AS A FACT ABOUT THE
    REFUSAL. MEASURED once already: a corpus walk exceeded its budget on a host in POWERSAVE and
    reported UNCHECKED — correct, and the reason the two verdicts are separate.
    """
    got = tool_decline_run.verify((_decline(_ABSENT),))
    verdict = got.verdicts[0].verdict
    if verdict == tool_decline_run.LAPSED:
        out.append("selftest: an unrunnable check was reported as a lapse")
        return 1
    if verdict != tool_decline_run.UNCHECKED:
        out.append(f"selftest: an unrunnable check read as {verdict}")
        return 1
    return 0


def a_declineless_check_is_unguarded(out: list[str]) -> int:
    """Check a refusal with no command says so.

    ⚑ AN UNGUARDED DECLINE IS THIS MODULE'S OWN DEFECT CLASS IN ITS OWN OUTPUT — a refusal nothing
    would notice lapsing. Reported, never hidden.
    """
    got = tool_decline_run.verify((_decline(None),))
    if got.verdicts[0].verdict != tool_decline_run.UNGUARDED:
        out.append(f"selftest: a checkless decline read as {got.verdicts[0].verdict}")
        return 1
    if got.unguarded != 1:
        out.append(f"selftest: the unguarded decline was not counted: {got.unguarded}")
        return 1
    return 0


def unguarded_does_not_demand_attention(out: list[str]) -> int:
    """Check a standing property is not reported as a change.

    ⚑ AN UNGUARDED DECLINE IS TRUE EVERY RUN. Folding it into "someone must look" would drown the
    two verdicts that mean something HAPPENED, which is how a signal channel stops being read.
    """
    got = tool_decline_run.verify((_decline(None),))
    if got.verdicts[0].needs_attention:
        out.append("selftest: an unguarded decline demands attention every run")
        return 1
    return 0


def a_lapse_and_an_unchecked_both_demand_attention(out: list[str]) -> int:
    """Check both actionable verdicts are surfaced, for different reasons."""
    got = tool_decline_run.verify((_decline(_FAILS), _decline(_ABSENT)))
    if not all(v.needs_attention for v in got.verdicts):
        out.append(f"selftest: an actionable verdict was not surfaced: {got.verdicts!r}")
        return 1
    return 0


def an_unchecked_run_does_not_report_success(out: list[str]) -> int:
    """Check a run that could not verify does not exit 0 — THE HONEST DIRECTION.

    ⚑⚑ A RUN THAT COULD NOT VERIFY ITS REFUSALS HAS NOT ESTABLISHED THAT THEY HOLD, and reporting
    success would bank an unmeasured claim — the census-green-is-a-fact-about-the-census shape,
    one layer over.
    """
    if tool_decline_run.verify((_decline(_ABSENT),)).exit_code == 0:
        out.append("selftest: a run that could not check anything reported success")
        return 1
    if tool_decline_run.verify((_decline(_PASSES),)).exit_code != 0:
        out.append("selftest: a fully guarded run did not report success")
        return 1
    return 0


def an_identical_check_runs_once(out: list[str]) -> int:
    """Check two declines sharing a discriminator do not run it twice.

    ⚑ SHARING A CHECK IS LEGITIMATE — two different REFUSALS can be guarded by one command, and
    that is not a duplicate record. Running it twice is repeated work on a corpus walk.
    """
    seen: list[str] = []
    tool_decline_run.verify((_decline(_PASSES), _decline(_PASSES)), announce=seen.append)
    if len(seen) != 1:
        out.append(f"selftest: a shared check announced {len(seen)} time(s)")
        return 1
    return 0


def quick_skips_execution_and_says_so(out: list[str]) -> int:
    """Check the cheap path is distinguishable from a verified one.

    ⚑⚑ `quick` IS NEVER THE DEFAULT, because a listing that skips execution makes UNGUARDED and
    GUARDED indistinguishable — the exact failure the record type prevents. An arm here pins that
    it produces neither verdict.
    """
    got = tool_decline_run.verify((_decline(_FAILS),), quick=True)
    if got.verdicts[0].verdict != tool_decline_run.DECLARED:
        out.append(f"selftest: --quick produced {got.verdicts[0].verdict}")
        return 1
    if got.lapsed or got.guarded:
        out.append("selftest: --quick produced a verified verdict")
        return 1
    return 0


def quick_still_reports_an_unguarded_decline(out: list[str]) -> int:
    """Check the one verdict that needs no execution survives the cheap path.

    ⚑ NO COMMAND HAS TO RUN to know a decline declares no check, so `--quick` withholding that
    would hide the one thing it can still honestly report.
    """
    got = tool_decline_run.verify((_decline(None),), quick=True)
    if got.unguarded != 1:
        out.append("selftest: --quick lost the unguarded decline")
        return 1
    return 0


def the_timeout_is_its_own_budget(out: list[str]) -> int:
    """Check the decline budget is separate from any other timeout in the toolkit.

    ⚑ RAISING THIS MUST NOT LOOSEN AN UNRELATED ONE. A timeout tuned on a fast machine turns a
    slow host into a tree of unverifiable refusals — a fact about the box read as a fact about
    the claims — so it is overridable, and separately.
    """
    if tool_decline_run.TIMEOUT_S <= 0:
        out.append(f"selftest: the decline budget is {tool_decline_run.TIMEOUT_S}")
        return 1
    return 0


_ARMS = (
    a_passing_check_is_guarded,
    a_failing_check_is_lapsed,
    an_unrunnable_check_is_unchecked,
    a_declineless_check_is_unguarded,
    unguarded_does_not_demand_attention,
    a_lapse_and_an_unchecked_both_demand_attention,
    an_unchecked_run_does_not_report_success,
    an_identical_check_runs_once,
    quick_skips_execution_and_says_so,
    quick_still_reports_an_unguarded_decline,
    the_timeout_is_its_own_budget,
)

_CASE_COUNT = 2 + 2 + 2 + 2 + 1 + 1 + 2 + 1 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"tool-decline-run selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"tool-decline-run selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
