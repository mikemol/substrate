#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.collision_witness` — the T23 family, and how it could close falsely.

⚑⚑⚑ THE UNKNOWN-PARTITION CASE IS THE ONE WITH TEETH. A witness handed a kind the census does not
know finds an empty bucket, and an empty bucket reads as *no collisions of that kind* — a green
verdict about a partition that was never measured. The ban family recorded the same shape at the
aggregate level: three buckets summing to the census today is a MEASUREMENT, not a construction,
and the moment a fourth kind appears every sub-item still reads clean.

⚑⚑ AND THE SHAPE CASES OUTLIVE THE POPULATION. The corpus has 533 collisions today and the point
of the arc is to reduce that; a case asserting a count would fail on every paydown. So these
assert the verdict's SHAPE — a part per finding, each carrying its route, the verdict last — which
stays true as the number falls and goes green only when the work lands.

⚑ THE FAMILY CASES READ THE DECLARATION, not the corpus, so they are stable regardless.
"""

from __future__ import annotations

import sys

from mikemol.witness import witness_row

from substrate import collision_witness, name_collision

_THREE_MEMBERS = 3


def the_family_declares_one_member_per_partition(out: list[str]) -> int:
    """Check the roster matches the census's kinds.

    ⚑ THE ROSTER IS THE AGGREGATE. The origin spelled its parts as a list literal inside the
    aggregate's body, so nothing could read the members without running it.
    """
    got = collision_witness.FAMILY
    if len(got.members) != _THREE_MEMBERS:
        out.append(f"selftest: the family holds {len(got.members)} member(s)")
        return 1
    if len(collision_witness.KEYS) != len(name_collision.KINDS):
        out.append(
            f"selftest: {len(collision_witness.KEYS)} key(s) for "
            f"{len(name_collision.KINDS)} kind(s)"
        )
        return 1
    return 0


def every_census_kind_has_a_bib_key(out: list[str]) -> int:
    """Check no partition exists that no item answers for.

    ⚑⚑ A KIND WITH NO ITEM IS A POPULATION NOBODY IS ACCOUNTABLE FOR. It would accumulate
    silently while all three declared sub-items read clean — the aggregate-coverage defect, one
    level down from where the ban family found it.
    """
    missing = [k for k in name_collision.KINDS if k not in collision_witness.KEYS]
    if missing:
        out.append(f"selftest: kinds with no bib key: {missing!r}")
        return 1
    return 0


def the_crossing_route_rests_on_the_sibling_one(out: list[str]) -> int:
    """Check the premise edge is declared rather than left in prose.

    ⚑ THE WIDER READING DEPENDS ON THE NARROWER. `crossing` is defined by what `sibling` is not —
    a same-directory collision that got wider — so deleting the sibling route would leave the
    crossing route reading as protected while its boundary went undefined.
    """
    got = collision_witness.FAMILY.member("no_name_is_reimplemented_across_two_trees")
    if got.premises != ("no_name_is_reimplemented_twice_within_one_directory",):
        out.append(f"selftest: the premise edge reads {got.premises!r}")
        return 1
    return 0


def the_familys_premises_all_resolve(out: list[str]) -> int:
    """Check no declared premise names a member the family does not hold.

    ⚑ A DANGLING PREMISE READS AS PROTECTED AND IS NOT.
    """
    got = collision_witness.FAMILY.dangling_premises()
    if got != ():
        out.append(f"selftest: the family carries a dangling premise: {got!r}")
        return 1
    return 0


def an_unknown_partition_reports_unmeasured(out: list[str]) -> int:
    """Check a kind the census does not know OPENS rather than reading clean.

    ⚑⚑⚑ AN EMPTY BUCKET AND AN UNKNOWN BUCKET ARE THE SAME BYTES. A witness that looked up an
    unrecognised kind, found nothing, and closed would report a green verdict about a partition
    that was never measured — and the verdict would be indistinguishable from an honest one.
    """
    rows = list(collision_witness.witness("T23-local", "name-collisions-local", "no-such-kind"))
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    if not verdicts or verdicts[-1].state != witness_row.OPEN:
        out.append(f"selftest: an unknown partition did not open: {verdicts!r}")
        return 1
    if "UNMEASURED" not in verdicts[-1].why:
        out.append(f"selftest: the verdict does not say unmeasured: {verdicts[-1].why!r}")
        return 1
    return 0


def a_route_without_its_tag_opens_rather_than_raising(out: list[str]) -> int:
    """Check an unreadable figure tag opens the item instead of crashing.

    ⚑ A WITNESS THAT RAISES TAKES THE WHOLE ROSTER DOWN. An unanchored claim is a finding about
    the CLAIM — the item cannot be measured — and that is a verdict, not an exception.
    """
    rows = list(collision_witness.witness_local("T23-local", "no-such-figure"))
    verdicts = [r for r in rows if isinstance(r, witness_row.Verdict)]
    if not verdicts or verdicts[-1].state != witness_row.OPEN:
        out.append(f"selftest: a missing tag did not open the item: {verdicts!r}")
        return 1
    if "tag" not in verdicts[-1].why:
        out.append(f"selftest: the verdict does not name the missing tag: {verdicts[-1].why!r}")
        return 1
    return 0


def each_part_carries_a_site(out: list[str]) -> int:
    """Check a reported collision names where it is, not just that it exists.

    ⚑ A NAME WITHOUT A SITE IS NOT ACTIONABLE. The repair differs per kind, and a reader told
    only that `add` collides has to re-derive the census to find the files.
    """
    rows = list(collision_witness.witness_crossing("T23-crossing", "name-collisions-crossing"))
    parts = [r for r in rows if isinstance(r, witness_row.Part)]
    if not parts:
        out.append("selftest: the crossing route emitted no part")
        return 1
    if not all(p.route for p in parts):
        out.append("selftest: a part carries no route")
        return 1
    return 0


def the_verdict_trails_its_parts(out: list[str]) -> int:
    """Check the verdict is the LAST row, never the first.

    ⚑ A WITNESS KNOWS ITS VERDICT ONLY AFTER LOOKING. Emitting it first is the
    count-before-the-walk defect, and a reader taking rows in order would bank a verdict about a
    population it had not yet seen.
    """
    rows = list(collision_witness.witness_local("T23-local", "name-collisions-local"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the last row is not a verdict")
        return 1
    if any(isinstance(r, witness_row.Verdict) for r in rows[:-1]):
        out.append("selftest: a verdict was emitted before the parts")
        return 1
    return 0


def each_kind_answers_for_its_own_bucket(out: list[str]) -> int:
    """Check the three routes report disjoint populations.

    ⚑⚑ ONE BODY, THREE ITEMS — so a mis-wired `kind` argument would make two routes report the
    SAME bucket and both agree with themselves. The partition is disjoint by construction, and
    this asserts the wiring preserves that rather than trusting it.
    """
    seen = {kind: {c.name for c in rows} for kind, rows in collision_witness.buckets().items()}
    bad = 0
    for left in name_collision.KINDS:
        for right in name_collision.KINDS:
            if left < right and seen[left] & seen[right]:
                out.append(
                    f"selftest: {left} and {right} share {sorted(seen[left] & seen[right])[:3]!r}"
                )
                bad += 1
    return bad


def a_sample_of_an_empty_bucket_says_none(out: list[str]) -> int:
    """Check the sample renderer names emptiness rather than returning a bare blank.

    ⚑ AN EMPTY STRING IN A VERDICT READS AS A TRUNCATED MESSAGE, not as a measured zero — the
    reader cannot tell whether the sample was empty or the formatting broke.
    """
    if collision_witness.sample(()) != "none":
        out.append(f"selftest: an empty sample rendered {collision_witness.sample(())!r}")
        return 1
    return 0


def the_family_is_not_yet_split(out: list[str]) -> int:
    """Check every member is a leaf, so the count equals the roster.

    ⚑ AN HONEST STATEMENT OF WHERE THIS FAMILY IS. Its three members each assert one fact today;
    should one grow a second, `unsplit()` names it rather than letting the total drift.
    """
    got = collision_witness.FAMILY
    if got.count != len(got.members) or got.unsplit() != ():
        out.append(
            f"selftest: count {got.count} over {len(got.members)} member(s), "
            f"unsplit {got.unsplit()!r}"
        )
        return 1
    return 0


# ⚑⚑⚑ THE THREE ARMS BELOW BEAR THE FAMILY'S MEMBER NAMES, AND THAT CORRESPONDENCE IS THE POINT.
# `family_roster` reports a declared member no arm runs, because **a family naming a member
# nothing runs reads as MORE rigorous than an undeclared suite while being less.** This family
# declared three claims about the corpus and ran none of them by name: every other arm here tests
# the WIRING — that the routes are disjoint, that an unknown partition refuses — which is a
# different subject from the claims themselves.
#
# ⚑⚑ THEY ASSERT THE VERDICT IS RENDERED, NOT THAT IT IS CLOSED. The corpus holds 533+ collisions
# and reducing that is the arc's business, not this suite's — a case pinning "closed" would fail
# today and go green only on the arc's completion, reporting the corpus rather than the witness.
def no_name_is_reimplemented_twice_within_one_file(out: list[str]) -> int:
    """Check the local-collision route reaches a verdict on the live corpus."""
    rows = list(collision_witness.witness_local("T23-local", "name-collisions-local"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the local route rendered no verdict")
        return 1
    return 0


def no_name_is_reimplemented_twice_within_one_directory(out: list[str]) -> int:
    """Check the sibling-collision route reaches a verdict on the live corpus."""
    rows = list(collision_witness.witness_sibling("T23-sibling", "name-collisions-sibling"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the sibling route rendered no verdict")
        return 1
    return 0


def no_name_is_reimplemented_across_two_trees(out: list[str]) -> int:
    """Check the crossing-collision route reaches a verdict on the live corpus."""
    rows = list(collision_witness.witness_crossing("T23-crossing", "name-collisions-crossing"))
    if not rows or not isinstance(rows[-1], witness_row.Verdict):
        out.append("selftest: the crossing route rendered no verdict")
        return 1
    return 0


_ARMS = (
    no_name_is_reimplemented_twice_within_one_file,
    no_name_is_reimplemented_twice_within_one_directory,
    no_name_is_reimplemented_across_two_trees,
    the_family_declares_one_member_per_partition,
    every_census_kind_has_a_bib_key,
    the_crossing_route_rests_on_the_sibling_one,
    the_familys_premises_all_resolve,
    an_unknown_partition_reports_unmeasured,
    a_route_without_its_tag_opens_rather_than_raising,
    each_part_carries_a_site,
    the_verdict_trails_its_parts,
    each_kind_answers_for_its_own_bucket,
    a_sample_of_an_empty_bucket_says_none,
    the_family_is_not_yet_split,
)

# ⚑ THE THREE MEMBER ARMS CONTRIBUTE ONE CASE EACH, and the total MOVES by exactly three —
# growth, not a corrected sum. A total that HELD would have meant they were already counted under
# other names.
_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"collision-witness selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"collision-witness selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
