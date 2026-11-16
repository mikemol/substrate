#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The runner's READ modes: what each suite DECLARES, against what discovery found.

⚑⚑⚑ THE DISTINCTION THESE MODES EXIST TO MAKE IS has-none / has-one / IS-A-FIXTURE AS THREE
STATES RATHER THAN ONE SILENCE. A bare listing prints the files discovery reached and cannot
distinguish a tool that HAS no suite from one nobody has looked at — which is how a standing
instruction to "run the selftest after you change it" could be issued against a tool where the
flag refuses as unknown.

⚑ THE UNDECLARED POPULATION IS REPORTED, NEVER OMITTED. A mode listing only disagreements
cannot distinguish "everything is consistent" from "nothing is declared": a false ZERO gets
banked while a false positive gets investigated. The declared set is a SEED, not a census, and
these modes say so in the output rather than in a docstring nobody reads at the terminal.

⚑⚑ AND MASS-DECLARING WOULD BE CEREMONY, WHICH IS WHY THE GAP STAYS OPEN. Every discovered
suite is a file where the dispatch already works — discovery established that. So adding a bare
declaration for each would add rows that CANNOT FAIL, turning an honest boundary into a green
census that assessed nothing. That is a manufactured false green, and the count is worth more
than the ceremony.

⚑ A STRAY IS THE FINDING, AND IT IS A ROW RATHER THAN A DROP. A declaration naming a tool
nobody discovered means the tool was renamed, deleted, or lost its dispatch — a claim about a
file that is not there, which is exactly the stale-ruling shape a census must surface.

⚑ THESE ARE READS, NOT GATES, DELIBERATELY. A ratchet minted over an unassessed census is the
ABSENT-baseline free pass this repo has measured — a gate exiting 0 while reporting unrecorded
errors. The gate is owed once the declared population MEANS something, and naming that here is
what keeps this from reading as done.

⚑ WHAT IS ACTUALLY UNREAD IS THE PRAGMA LAYER. The invocation builder ACTS on
`# selftest-requires:` and `# selftest-tenant:` — supplying dependencies, appending a tenant
flag — and nothing ever reported them. So a suite that needs a package and does not say so
degrades to a pass-shaped SKIP, and a suite that reaches a store without declaring a tenant
resolves LIVE. Both are SOURCE facts, and both were invisible to every other mode.

⚑ THE LINES ARE RETURNED, NOT PRINTED, so a case can drive them. Inline, this reasoning was
unreachable from any suite.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡retire-the-runner).
"""

from __future__ import annotations

from mikemol.corpus import suite_pragmas

from substrate import suite_declared, tenant_pragma

# The state a row carries when nobody has assessed the tool.
UNDECLARED = "undeclared"

# The state a row carries when a declaration names a tool discovery did not find.
STRAY = "STRAY"

# How wide the label column is, so the readings line up under each other.
_LABEL_WIDTH = 42

# How wide the label column is in the declarations mode, which prints a state beside it.
_TOOL_WIDTH = 38


def _labels(suites: list[tuple[str, str]]) -> list[str]:
    """Return just the labels of a `(label, path)` roster."""
    return [label for label, _path in suites]


def declaration_lines(
    suites: list[tuple[str, str]],
    table: dict[str, suite_declared.Declared] | None = None,
) -> list[str]:
    """Render DECLARED intent against DISCOVERED membership, and the self-including edge.

    ⚑ `table` IS PASSED THROUGH so a case can supply its own exemplars. Without it the
    self-inclusion arm could only exercise the branch while some LIVE entry happened to
    declare a roster edge — so repairing a stale declaration turned that arm VACUOUS
    rather than red, and a case that quietly stops asserting is worse than one that
    fails.
    """
    standings = suite_declared.standings(_labels(suites), table)
    findings = [row for row in standings if row.state == STRAY]
    settled = [row for row in standings if row.state not in (STRAY, UNDECLARED)]
    undeclared = [row for row in standings if row.state == UNDECLARED]

    lines = [f"  FINDING    {row.label:<{_TOOL_WIDTH}} [{row.state}] {row.why}" for row in findings]
    lines += [f"  ok         {row.label:<{_TOOL_WIDTH}} [{row.state}]" for row in settled]

    # ⚑ THE STATIC CYCLE CHECK, and it is the half a process-tree walk CANNOT be. The walk
    # reads what ACTUALLY happened and refuses only after a generation has forked; this reads
    # a claim in a source file and can refuse at commit time. Neither subsumes the other — an
    # UNDECLARED tool whose suite grows a roster call tomorrow is invisible here and caught
    # only by the walk, which is why both ship.
    cycle = suite_declared.self_including(_labels(suites), table)
    if cycle:
        lines.append("  ⚑ SELF-INCLUDING — declared to run the roster that contains them:")
        lines += [f"      {tool}" for tool in cycle]
        lines.append(
            "    A process-tree walk refuses this at RUNTIME, after a generation "
            "has already forked.\n    This is the same edge, readable from source "
            "at commit time."
        )

    lines.append(
        f"  {len(settled) + len(findings)} declared, {len(suites)} discovered, "
        f"{len(findings)} finding(s), {len(undeclared)} UNDECLARED"
    )
    # ⚑ THE UNDECLARED COUNT IS THE PAYDOWN POPULATION, NAMED AS SUCH — and COUNTED, never
    # typed. A figure restated beside the code that derives it is the drift this repo has
    # measured across four files, one of them the gate that enforced the value it misquoted.
    lines.append(
        f"    ⚑ UNDECLARED is this mode's OWN BOUNDARY, not a clean tree: "
        f"{len(undeclared)} of these\n      have never been assessed. A gate here "
        f"is owed once that number means something."
    )
    return lines


def pragma_lines(suites: list[tuple[str, str]]) -> list[str]:
    """Render what each suite DECLARES TO THE RUNNER — the assessable half of UNDECLARED."""
    rows = [
        (label, suite_pragmas.requires(path), tenant_pragma.tenant(path)) for label, path in suites
    ]
    with_deps = sorted(row for row in rows if row[1])
    with_tenant = sorted(row for row in rows if row[2])
    silent = [row for row in rows if not row[1] and not row[2]]

    lines = [
        f"  requires   {label:<{_LABEL_WIDTH}} {', '.join(deps)}"
        for label, deps, _tenant in with_deps
    ]
    lines += [
        f"  tenant     {label:<{_LABEL_WIDTH}} {tenant}" for label, _deps, tenant in with_tenant
    ]
    lines.append(
        f"  {len(rows)} discovered, {len(with_deps)} declare a dependency, "
        f"{len(with_tenant)} declare a tenant"
    )
    # ⚑ THE SILENT MAJORITY IS NAMED AS UNREAD, NEVER AS CLEAN. A suite declaring neither
    # pragma is not thereby known to need neither — nobody has asked.
    lines.append(
        f"    ⚑ {len(silent)} suite(s) declare NEITHER. That is not a clean tree: "
        f"this mode reports\n      what a suite SAYS, and cannot tell 'needs "
        f"nothing' from 'never asked'."
    )
    return lines
