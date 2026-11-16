#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ratchet_witness` — the anchor, and what an unreadable gate means.

⚑⚑⚑ THE UNMEASURABLE CASE IS THE ONE THAT MUST NOT GO GREEN. A gate that will not import has an
UNKNOWN state, and reporting it as at-baseline banks a verdict nothing measured. That is the same
collapse a ratchet made when it exited 0 while reporting 116 unrecorded errors — an absent
measurement spelled as a passing one.

⚑⚑ AND THE ANCHOR IS WHY THIS BODY READS THE CLAIM AT ALL. A witness reporting only the gate's
number cannot be wrong about the claim, because it never consults it — so an item sized against
66 while the tree held 216 would report cleanly forever. Reading the claim is what makes the
disagreement expressible.

⚑⚑⚑ AND THIS SUITE'S OWN FIRST VERSION GOT ITS DIAGNOSIS BACKWARDS, WHICH IS WORTH KEEPING. A
case asked item `A5` for an `[as=N]` tag; `A5`'s claim carries no tag at all — the anchored items
spell theirs `[public-added=N]`, `[claims-added=N]` — so the witness correctly opened and
returned early, and the case reported *"no parts from a gate measured as over baseline"*, naming
the CENSUS as the problem when the CLAIM was. **A test's failure message is a hypothesis too**,
and this one pointed at the wrong half of the system.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_row

from substrate import ratchet_witness


def an_unmeasurable_gate_opens(out: list[str]) -> int:
    """Check a gate that cannot be read yields an OPEN verdict naming why.

    ⚑ NOT CLEAN, AND NOT SILENT. The reason travels with the verdict so a reader knows to fix an
    import rather than to look for debt that was never measured.
    """
    rows = list(ratchet_witness.witness("PROBE", "no_such_gate_anywhere", "probe"))
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    bad = 0
    if len(verdicts) != 1:
        out.append(f"selftest: {len(verdicts)} verdict(s) for an unmeasurable gate")
        bad += 1
    elif not verdicts[0].is_open:
        out.append("selftest: an unmeasurable gate closed")
        bad += 1
    elif "CANNOT MEASURE" not in verdicts[0].why:
        out.append(f"selftest: the verdict does not name the failure: {verdicts[0].why!r}")
        bad += 1
    return bad


def an_unmeasurable_gate_emits_no_parts(out: list[str]) -> int:
    """Check no rows are claimed for a census that never ran.

    ⚑ PARTS ARE MEASURED KEYS. Emitting any for a gate that could not be read would put rows in
    the ordering that correspond to nothing.
    """
    rows = list(ratchet_witness.witness("PROBE", "no_such_gate_anywhere", "probe"))
    parts = [r for r in rows if isinstance(r, witness_row.Part)]
    if parts:
        out.append(f"selftest: {len(parts)} part(s) emitted for an unmeasurable gate")
        return 1
    return 0


def the_verdict_trails_its_parts(out: list[str]) -> int:
    """Check the verdict is the LAST row, never the first.

    ⚑ FORCED, NOT CHOSEN. A witness knows open-or-closed only after it has finished looking;
    emitting a verdict first would be the count-before-the-walk defect.
    """
    rows = list(ratchet_witness.witness("PROBE", "no_such_gate_anywhere", "probe"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the last row is not a verdict")
        return 1
    return 0


def the_route_names_the_gates_listing(out: list[str]) -> int:
    """Check each row's route is an enumerating command, not prose.

    ⚑ EVERY RATCHET GATE GREW A `--list` MODE so a census could be enumerated; naming it is what
    makes a row actionable rather than descriptive.
    """
    got = ratchet_witness.route("check_ban_ratchet")
    if "--list" not in got or "check_ban_ratchet" not in got:
        out.append(f"selftest: the route reads {got!r}")
        return 1
    return 0


def an_unanchored_claim_opens_without_parts(out: list[str]) -> int:
    """Check an item whose claim carries no figure tag opens, and emits no rows.

    ⚑ EMITTING NO PARTS IS RIGHT HERE. Without a figure to reconcile against there is nothing to
    check the census's keys AGAINST, so rows would be an enumeration nobody asked for — the
    verdict is about the claim, not about the tree.
    """
    rows = list(ratchet_witness.witness("A5", "check_ban_ratchet", "as"))
    parts = [r for r in rows if isinstance(r, witness_row.Part)]
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    bad = 0
    if parts:
        out.append(f"selftest: {len(parts)} part(s) for an unanchored claim")
        bad += 1
    if len(verdicts) != 1 or not verdicts[0].is_open:
        out.append("selftest: an unanchored claim did not open")
        bad += 1
    return bad


def a_live_anchored_gate_yields_parts_and_one_verdict(out: list[str]) -> int:
    """Check a real anchored item produces one part per added key and exactly one verdict.

    ⚑ THE FIXTURES ABOVE PIN THE FAILURE SHAPES; this pins the success path against the tree as
    it is. A suite of failure cases alone can pass while nothing works.

    ⚑ `R8`/`public-added` IS USED BECAUSE ITS CLAIM IS ANCHORED and its gate is measurably over
    baseline today, so both halves — parts and a verdict — are exercised rather than trivially
    satisfied by a clean census.
    """
    rows = list(ratchet_witness.witness("R8", "check_public_ratchet", "public-added"))
    parts = [r for r in rows if isinstance(r, witness_row.Part)]
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    bad = 0
    if len(verdicts) != 1:
        out.append(f"selftest: {len(verdicts)} verdict(s) from a live gate")
        bad += 1
    if not parts:
        out.append("selftest: no parts from a gate measured as over baseline")
        bad += 1
    if parts and not all(p.route for p in parts):
        out.append("selftest: a part carries no route")
        bad += 1
    return bad


_ARMS = (
    an_unmeasurable_gate_opens,
    an_unmeasurable_gate_emits_no_parts,
    the_verdict_trails_its_parts,
    the_route_names_the_gates_listing,
    an_unanchored_claim_opens_without_parts,
    a_live_anchored_gate_yields_parts_and_one_verdict,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 2 + 3


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"ratchet-witness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"ratchet-witness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
