#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The DECLARED intent of a suite — what discovery cannot say about it.

⚑⚑⚑ WHAT DISCOVERY CANNOT SAY, AND WHY IT MATTERS HERE SPECIFICALLY. `suite_discovery`
answers ONE question: is this file in the roster. So a tool with NO suite, a deliberate
failing FIXTURE, and a tool NOBODY HAS LOOKED AT are the same absence from a 96-row list — and
membership-by-convention is exactly what admitted a fork bomb, because there was nowhere for
`worklist_gate` to state that its suite RUNS THIS ROSTER. Six generations, load 54.93, 68
processes on 10 cores, and no source file said the edge existed.

⚑ THREE STATES RATHER THAN ONE SILENCE: has-none, has-one, IS-A-FIXTURE. A standing
instruction to "run the selftest after you change it" could otherwise be issued against a tool
where the flag refuses as unknown.

⚑⚑ THIS IS A SEED, NOT A CENSUS, AND THE DIFFERENCE IS DECLARED. Five entries against a
discovered population two orders larger. The undeclared remainder is REPORTED rather than
omitted, because a row-set of disagreements alone cannot distinguish "all consistent" from
"nothing declared yet" — a false ZERO gets banked while a false positive gets investigated.

⚑ AND A FROZEN ROSTER OF EVERY TOOL IS THE ARTIFACT THIS ARC ARGUES AGAINST. What is NOT
derivable is the INTENT, which is all that is declared here. Membership comes from discovery;
only the claim about a tool's relationship to the roster is written down.

⚑ EXTRACTED FROM `scripts/run_selftests.py` (⟡declarations-census). The rendering already
delegated to `climode`, so what moves is the roster and the shape of the read.
"""

from __future__ import annotations

from dataclasses import dataclass

# The roster tool's own key — excluded from the self-inclusion check, since running the roster
# is what it IS. Named once rather than typed at each call site.
ROSTER_KEY = "scripts/run_selftests.py"


@dataclass(frozen=True, slots=True)
class Declared:
    """One tool's claim about its own suite.

    ⚑ `runs_roster` IS THE FIELD THE FORK BOMB NEEDED AND DID NOT HAVE. A suite that invokes
    the roster containing it is a legitimate want — `worklist_gate` genuinely wants to know the
    selftests pass — and the cycle is only refusable if the edge is WRITABLE. A ppid walk
    refuses it at runtime, after a generation has already forked; a declaration refuses it at
    commit time.

    ⚑ `key` OVERRIDES THE DISCOVERED LABEL for a tool whose entry is a FIXTURE rather than a
    member — a mode MEANT to fail is a positive control for the runner, and as a roster member
    it makes the gate red by design.
    """

    why: str
    runs_roster: bool = False
    key: str | None = None


# ⚑ INTENT, NOT MEMBERSHIP. Every entry states something no walk can derive from source.
DECLARED: dict[str, Declared] = {
    "scripts/run_selftests.py": Declared(
        runs_roster=True, why="the roster itself — running every suite is what it IS"
    ),
    # ⚑⚑⚑ A DECLARATION THAT OUTLIVED ITS CODE, CORRECTED 2026-09-03 — AND THE RETIRED
    # CLAIM IS KEPT, because a repaired incident is residue, not an erasure.
    #
    # ⚑ WHAT IT SAID: `runs_roster=True`, "its suite invokes run_selftests —
    # ⟡worklist-gate-recursion", above a comment reading THE EDGE THAT CLOSED THE CYCLE,
    # FINALLY WRITABLE. That was TRUE WHEN WRITTEN: the edge existed and this table is
    # where it first became sayable.
    #
    # ⚑⚑ WHAT THE CODE SAYS NOW: the edge was REMOVED and replaced by a guard.
    # `--literal run_selftests scripts/worklist_gate.py` reports two sites, NEITHER an
    # invocation — the module docstring, and a string ARGUMENT to
    # `ratchet.check_cycle("run_selftests.py", "worklist_gate")`, a ppid walk that
    # REFUSES re-entry. So the declaration was a fossil of the state BEFORE the fix,
    # and it recorded the edge being ADDED while the code had since deleted it.
    #
    # ⚑⚑⚑ AND BOTH READERS TRUSTED IT RATHER THAN THE CODE. `run_selftests
    # --declarations` and `selftest_mk` both key on this table, so both reported this
    # tool as the one non-leaf that runs the roster — a green gate over 352 suites,
    # resting on a claim nobody re-derived. That is the general hazard of this table's
    # own charter: an entry states what no walk can derive, which is exactly the
    # property that makes it unfalsifiable by any walk. The charter is still right; the
    # ENTRY was wrong, and only a reading of the code could say so.
    #
    # ⚑ THE ENTRY IS KEPT RATHER THAN DELETED, because the FIX is itself intent no walk
    # derives: a reader who finds no entry cannot tell "never assessed" from "assessed
    # and found not to fan out", and the second is a stronger statement than silence.
    "scripts/worklist_gate.py": Declared(
        why="does NOT run the roster: `ratchet.check_cycle` walks this process's ppid "
        "chain and refuses re-entry, so the edge cannot form. RETIRED 2026-09-03 — "
        "this entry read `runs_roster=True` ('its suite invokes run_selftests — "
        "⟡worklist-gate-recursion') after the invocation had been replaced by that "
        "guard, and two readers reported the stale claim as fact"
    ),
    # ⚑ THE FIXTURE PRECEDENT. A mode that is MEANT to fail is a positive control for the
    # runner, not a member of the roster.
    "scripts/sppf_db.py": Declared(
        key="scripts/sppf_db.py",
        why="carries --selftest-demo-failure, the canonical failing FIXTURE, which is "
        "invoked BY a suite as a positive control and never AS a roster member",
    ),
    # ⚑ BOTH TOOLS A BRIEF NAMED AS HAVING NO SUITE. One of them did.
    "scripts/check_mode_contracts.py": Declared(
        why="gained a suite 2026-08-24: its kind classifier was an inline chain inside "
        "census(), unreachable from any case"
    ),
    # ⚑⚑ THE COUNT WAS REMOVED FROM THIS ENTRY 2026-09-03 (Ⓝ133 ⟡no-counts-in-prose), AND THE
    # ENTRY IS THE WORKED EXAMPLE FOR THE RULE. It read "a 56-case suite" while
    # `--selftest` reported a larger total: the suite grew, the sentence did not, and a
    # declaration whose whole job is to state what no walk can derive had drifted on the one
    # part a walk CAN. The reason the entry exists is untouched and still true; only the
    # number is gone.
    #
    # ⚑ CITED, NOT RE-QUOTED WITH A FRESHER FIGURE. Retyping today's value rebuilds the
    # condition one edit later — the count is a snapshot the moment it is typed, and this
    # table is not re-derived by anything. Naming the command that answers is what makes the
    # claim checkable instead of merely current.
    "scratch/fix_notinscope.py": Declared(
        why="a suite existed all along and was RED by one case on a data-pinned index hash — "
        "corrected to derive the hash from the live index. For the case count, run "
        "`scratch/fix_notinscope.py --selftest`; it is not quoted here because a count "
        "in prose is a snapshot and this table is re-derived by nothing"
    ),
}


@dataclass(frozen=True, slots=True)
class Standing:
    """One row of DECLARED-against-DISCOVERED."""

    label: str
    state: str
    why: str


def standings(discovered: list[str], table: dict[str, Declared] | None = None) -> list[Standing]:
    """Return every discovered suite's declaration state, undeclared included.

    ⚑ THE UNDECLARED POPULATION IS RETURNED, NEVER FILTERED OUT. It is this reader's OWN
    BOUNDARY — rows nobody has assessed — and reporting only disagreements would make a green
    result indistinguishable from an empty one.

    ⚑⚑ `table` IS INJECTABLE BECAUSE THE CASES WERE PINNED TO LIVE ENTRIES, and that made
    the roster's own content load-bearing for the suite. Two arms named
    `scripts/worklist_gate.py` as their self-including exemplar; when that entry was
    corrected to match its code, arms testing the READER broke on a change to the DATA.
    A case that fails when a declaration is repaired is testing the wrong thing — so a
    fixture table is passed in, and `DECLARED` stays the default for every real caller.
    """
    declared = DECLARED if table is None else table
    found = set(discovered)
    # ⚑ A FIXTURE IS ITS OWN STATE, not a declared member. Collapsing it into "declared" would
    # put a mode MEANT to fail into the roster's population, where it makes the gate red by
    # design — which is the distinction the `key` field exists to carry.
    rows = [
        Standing(label, "fixture" if declared[label].key else "declared", declared[label].why)
        for label in sorted(found & set(declared))
    ]
    rows += [
        Standing(label, "undeclared", "never assessed") for label in sorted(found - set(declared))
    ]
    # ⚑ A DECLARATION FOR A TOOL NOBODY DISCOVERED IS A FINDING, not a row to drop. It means
    # the tool was renamed, deleted, or lost its dispatch — and a claim about a file that is
    # not there is exactly the stale-ruling shape a census must surface.
    rows += [
        Standing(label, "STRAY", f"declared but not discovered: {declared[label].why}")
        for label in sorted(set(declared) - found)
    ]
    return rows


def self_including(discovered: list[str], table: dict[str, Declared] | None = None) -> list[str]:
    """Return the discovered tools that declare they run the roster containing them.

    ⚑ THE STATIC HALF OF A CHECK THAT ALSO HAS A RUNTIME HALF, and neither subsumes the other.
    A ppid walk reads what ACTUALLY happened and refuses only after a generation has forked;
    this reads a claim in a source file and can refuse at commit time. An UNDECLARED tool whose
    suite grows a roster call tomorrow is invisible here and caught only by the walk.

    ⚑ AND THE POPULATION IS CURRENTLY EMPTY, WHICH IS A FINDING RATHER THAN A CLEAN BILL.
    The one entry that ever declared `runs_roster` besides the roster itself was
    `worklist_gate`, and it was retired 2026-09-03 as a fossil of a removed edge. So this
    returns nothing today — and "nothing declares it" is a fact about the five-entry
    SEED, not about the 350-odd suites nobody has assessed.

    ⚑ `table` IS INJECTABLE for the reason `standings` records: a case must be able to
    supply its own exemplar rather than depend on a live declaration staying wrong.
    """
    found = set(discovered)
    return sorted(
        label
        for label, d in (DECLARED if table is None else table).items()
        if d.runs_roster and label != ROSTER_KEY and label in found
    )
