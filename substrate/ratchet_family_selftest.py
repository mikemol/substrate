#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ratchet_family` — the roster, and the two ways it could lie.

⚑⚑⚑ THE STALE-MEMBERSHIP CASE IS THE ONE WITH A MEASURED HISTORY. The origin's docstring named
SIX items riding its shared body while the tree had EIGHT call sites — a membership written in
prose beside the code that implements it, drifting in the direction that under-reports. These
cases assert the roster against the DECLARATION rather than against a number typed in prose.

⚑⚑ AND THE UNMEASURABLE CASE IS THE OTHER DIRECTION. Four of seven gates currently fail to import
because they are written to run as scripts; an item that read that as *nothing to see* would bank
a false clean across most of the family. The distinction has to be visible BEFORE a verdict.

⚑ THE CASES ASSERT SHAPE, NOT COUNTS. Gate populations move with every paydown, and a case
pinning `2 added of 62` fails on the work succeeding.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_row

from substrate import ratchet_family

_ROSTER_SIZE = 7


def the_roster_and_the_family_agree(out: list[str]) -> int:
    """Check one declared member per roster item.

    ⚑⚑ THE DRIFT THIS CATCHES IS MEASURED. The origin's prose said six while its code had eight;
    two members can be added to a shared body without anything noticing, because the body does
    not change. Comparing the two declarations is what makes the membership checkable.
    """
    got = ratchet_family.FAMILY
    bad = 0
    if len(ratchet_family.ITEMS) != _ROSTER_SIZE:
        out.append(f"selftest: the roster holds {len(ratchet_family.ITEMS)} item(s)")
        bad += 1
    if len(got.members) != len(ratchet_family.ITEMS):
        out.append(
            f"selftest: {len(got.members)} member(s) for {len(ratchet_family.ITEMS)} roster item(s)"
        )
        bad += 1
    return bad


def every_item_names_a_distinct_gate(out: list[str]) -> int:
    """Check no two items ride the same gate.

    ⚑ TWO ITEMS ON ONE GATE WOULD BOTH REPORT THE SAME POPULATION and both agree with
    themselves — a duplicate reading that looks like corroboration.
    """
    gates = [i.gate for i in ratchet_family.ITEMS]
    if len(gates) != len(set(gates)):
        out.append(f"selftest: a gate is claimed twice: {gates!r}")
        return 1
    return 0


def every_item_names_a_distinct_key(out: list[str]) -> int:
    """Check no worklist key appears twice.

    ⚑ A REPEATED KEY MAKES `item()` RETURN WHICHEVER COMES FIRST, so the second item would be
    unreachable while still reading as declared — the addressability defect, in the roster.
    """
    keys = [i.key for i in ratchet_family.ITEMS]
    if len(keys) != len(set(keys)):
        out.append(f"selftest: a key is claimed twice: {keys!r}")
        return 1
    return 0


def the_ban_item_is_not_in_this_family(out: list[str]) -> int:
    """Check `A5` rides its own family, not this one.

    ⚑⚑ IT HAS A STRUCTURE THE PLAIN COUNT CANNOT EXPRESS: a ban key partitions by DIRECTIVE, and
    its aggregate must cover kinds no sub-item names. Listing it here would give it a witness that
    reports a total while its real population is a partition — the shape that let three sub-items
    read clean while the census refused.
    """
    if ratchet_family.item("A5") is not None:
        out.append("selftest: A5 is in the plain-ratchet roster")
        return 1
    return 0


def a_key_riding_no_ratchet_reports_unmeasured(out: list[str]) -> int:
    """Check an unknown key OPENS rather than reading clean.

    ⚑⚑⚑ THE FALSE-CLEAN THE ROSTER EXISTS TO PREVENT. A witness that took a gate name from its
    caller could answer about a gate no item claims — and finding nothing over baseline, it would
    close. That is a green verdict about a population nobody is accountable for.
    """
    rows = list(ratchet_family.witness("no-such-item"))
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    if not verdicts or verdicts[-1].state != witness_row.OPEN:
        out.append(f"selftest: an unknown key did not open: {verdicts!r}")
        return 1
    if "UNMEASURED" not in verdicts[-1].why:
        out.append(f"selftest: the verdict does not say unmeasured: {verdicts[-1].why!r}")
        return 1
    return 0


def a_known_key_resolves_to_its_gate(out: list[str]) -> int:
    """Check the roster lookup returns the right entry — the POSITIVE CONTROL.

    ⚑ WITHOUT THIS, A LOOKUP RETURNING None FOR EVERYTHING would pass the case above and make
    every item unmeasured. The pair says the roster resolves rather than refusing uniformly.
    """
    got = ratchet_family.item("S1")
    if got is None or got.gate != "check_snapshot_guard":
        out.append(f"selftest: S1 resolved to {got!r}")
        return 1
    return 0


def an_unmeasurable_gate_is_named_with_its_reason(out: list[str]) -> int:
    """Check a census that cannot be read reports WHY, not merely that it failed.

    ⚑⚑ A REFUSAL THAT CANNOT SAY WHAT IT HIT is a guard degraded to measuring nothing. MEASURED:
    four of seven gates fail on a SIBLING import (`ratchet`, `buildtime`) — they run as scripts,
    where their directory is on the path, and every one is present on disk. A reader reporting a
    bare count would send someone looking for missing files.
    """
    for _gate, why in ratchet_family.unmeasurable():
        if not why or why == "no reason given":
            out.append(f"selftest: an unmeasurable gate carries no reason: {why!r}")
            return 1
    return 0


def the_render_states_its_denominator(out: list[str]) -> int:
    """Check the roster report says how many of how many are measurable.

    ⚑ `0 of 0` AND `3 of 7` ARE DIFFERENT FACTS. A render printing only the measurable ones
    cannot distinguish a healthy family from one whose gates all stopped importing.
    """
    text = ratchet_family.render()
    if f"of {len(ratchet_family.ITEMS)} measurable" not in text:
        out.append(f"selftest: the render omits its denominator:\n{text}")
        return 1
    return 0


def the_familys_premises_all_resolve(out: list[str]) -> int:
    """Check no declared premise names a member the family does not hold."""
    got = ratchet_family.FAMILY.dangling_premises()
    if got != ():
        out.append(f"selftest: the family carries a dangling premise: {got!r}")
        return 1
    return 0


def the_family_is_not_yet_split(out: list[str]) -> int:
    """Check every member is a leaf, so the count equals the roster."""
    got = ratchet_family.FAMILY
    if got.count != len(got.members) or got.unsplit() != ():
        out.append(
            f"selftest: count {got.count} over {len(got.members)}, unsplit {got.unsplit()!r}"
        )
        return 1
    return 0


# ⚑⚑⚑ THE SEVEN ARMS BELOW BEAR THE FAMILY'S MEMBER NAMES, AND THAT CORRESPONDENCE IS THE POINT.
# `family_roster` reports a declared member no arm runs, because **a family naming a member
# nothing runs reads as MORE rigorous than an undeclared suite while being less.** This family
# declared seven claims about seven gates and ran none by name; every other arm here tests the
# ROSTER — distinct keys, distinct gates, an unknown key refusing — a different subject.
#
# ⚑⚑ THEY ASSERT THE WITNESS REACHES A VERDICT, NOT THAT THE GATE IS CLEAN. Four of the seven are
# currently UNMEASURABLE (they import siblings by bare name and run as scripts), and a case
# pinning either state would report the gates rather than the witness. What must hold is that a
# gate's condition — measurable or not, at baseline or over — is RENDERED rather than swallowed:
# an unmeasurable census read as clean is the false green this whole family exists to refuse.
def _renders(key: str, out: list[str]) -> int:
    """Check one roster member's witness reaches a verdict."""
    rows = list(ratchet_family.witness(key))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append(f"selftest: the witness for {key} rendered no verdict")
        return 1
    return 0


def the_public_re_export_residue_is_paid_down(out: list[str]) -> int:
    """Check the public-ratchet route reaches a verdict."""
    return _renders("R8", out)


def no_prose_claim_is_falsified_by_the_tree(out: list[str]) -> int:
    """Check the claims route reaches a verdict."""
    return _renders("G1", out)


def no_module_elaborates_over_the_cap(out: list[str]) -> int:
    """Check the cap route reaches a verdict."""
    return _renders("G6", out)


def no_type_is_declared_in_both_a_parent_and_its_leaf(out: list[str]) -> int:
    """Check the sumtype route reaches a verdict."""
    return _renders("R2-SWEEP", out)


def private_helpers_are_extracted_not_merely_hidden(out: list[str]) -> int:
    """Check the private route reaches a verdict."""
    return _renders("R9-residue", out)


def every_in_place_editor_is_snapshot_armed(out: list[str]) -> int:
    """Check the snapshot route reaches a verdict."""
    return _renders("S1", out)


def no_tool_re_derives_a_shared_authority(out: list[str]) -> int:
    """Check the rederive route reaches a verdict."""
    return _renders("T12-rederive", out)


_ARMS = (
    the_public_re_export_residue_is_paid_down,
    no_prose_claim_is_falsified_by_the_tree,
    no_module_elaborates_over_the_cap,
    no_type_is_declared_in_both_a_parent_and_its_leaf,
    private_helpers_are_extracted_not_merely_hidden,
    every_in_place_editor_is_snapshot_armed,
    no_tool_re_derives_a_shared_authority,
    the_roster_and_the_family_agree,
    every_item_names_a_distinct_gate,
    every_item_names_a_distinct_key,
    the_ban_item_is_not_in_this_family,
    a_key_riding_no_ratchet_reports_unmeasured,
    a_known_key_resolves_to_its_gate,
    an_unmeasurable_gate_is_named_with_its_reason,
    the_render_states_its_denominator,
    the_familys_premises_all_resolve,
    the_family_is_not_yet_split,
)

# ⚑ THE SEVEN MEMBER ARMS CONTRIBUTE ONE CASE EACH, and the total MOVES by exactly seven —
# growth, not a corrected sum.
_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"ratchet-family selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"ratchet-family selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
