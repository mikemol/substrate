#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.column_contours` — the two ways a nomination lies.

⚑⚑⚑ THE EMPTY-INDEX-MAP CASE IS THE MEASURED DEFECT, and it is why one arm here asserts a
NON-empty result is WRONG. When the live-index read returned an empty map, every pair became a
gap and the tool's whole output was a list of gaps that are not gaps — a failure that reads as
a productive report. The arm pins the shape by contrast: the SAME pairs against a populated map
must yield strictly fewer gaps. An arm checking only the populated case would pass while the
empty case still lied.

⚑⚑ THE PARTITION ARM IS THE ONE WITHOUT AN OBSERVABLE SYMPTOM. A pair dropped by two suppression
conditions at once simply is not in any output list, and a ranked report of the survivors looks
exactly the same either way. Only a conservation check — every input pair lands in exactly one
bucket — can see it.

⚑ AND THE SYMMETRY ARMS DISCRIMINATE THE TWO PAIR NOTIONS. `contours` is symmetric (a composite
index is one object) and `covering_pairs` is NOT (the predicate must lead, or the index cannot be
seeked). Getting this backwards halves one census or doubles the other, and both wrong answers
are plausible-looking integers.
"""

from __future__ import annotations

import sys

from substrate import column_contours as cc

# Two queries over one table. `obs.uri` is a predicate in both; `obs.kind` is a predicate in
# one and merely projected in the other, which is what makes the two pair notions differ.
_QUERIES = (
    cc.QueryColumns(
        "q_by_uri", frozenset({"obs.uri", "obs.kind", "obs.ts"}), frozenset({"obs.uri"})
    ),
    cc.QueryColumns(
        "q_by_kind", frozenset({"obs.uri", "obs.kind"}), frozenset({"obs.uri", "obs.kind"})
    ),
    # ⚑ A SECOND TABLE, so a cross-table pair would be visible if the grouping ever broke.
    cc.QueryColumns("q_edge", frozenset({"edge.src", "edge.dst"}), frozenset({"edge.src"})),
)

# A populated live-index map: `obs` has a composite leading with (uri, kind).
_LIVE: dict[str, list[tuple[str, str, str]]] = {
    "obs": [("uri", "kind", "ix_obs_uri_kind")],
}

# `edge.src` is a declared key, so its contours are already served.
_KEYS = frozenset({"edge.src"})

_EMPTY_LIVE: dict[str, list[tuple[str, str, str]]] = {}


def elevation_is_totally_ordered(out: list[str]) -> int:
    """Check breadth ranks correctly and ties break by name.

    `obs.uri` is touched by two queries, `obs.kind` by two, `obs.ts` by one — so the tie
    between uri and kind must resolve alphabetically rather than by dict order.
    """
    got = [(e.column, e.touched, e.predicated) for e in cc.elevations(_QUERIES)]
    want = [
        ("obs.kind", 2, 1),
        ("obs.uri", 2, 2),
        ("edge.dst", 1, 0),
        ("edge.src", 1, 1),
        ("obs.ts", 1, 0),
    ]
    if got != want:
        out.append(f"selftest: elevations read as {got}, want {want}")
        return 1
    return 0


def a_contour_never_crosses_tables(out: list[str]) -> int:
    """Check no pair joins columns of different tables.

    ⚑ A CROSS-TABLE PAIR IS NOT MERELY WRONG, IT IS UNBUILDABLE — no composite index spans two
    tables, so nominating one wastes the reader's whole judgement on the report.
    """
    crossing = [c for c in cc.contours(_QUERIES) if cc.table_of(c.left) != cc.table_of(c.right)]
    if crossing:
        out.append(f"selftest: {len(crossing)} contour(s) cross a table boundary")
        return 1
    return 0


def a_contour_is_symmetric(out: list[str]) -> int:
    """Check each unordered pair appears exactly once, sorted within itself."""
    seen = [(c.left, c.right) for c in cc.contours(_QUERIES)]
    if any(a > b for a, b in seen):
        out.append(f"selftest: a contour is not internally sorted: {seen}")
        return 1
    if len(seen) != len(set(seen)):
        out.append(f"selftest: a contour pair is double-counted: {seen}")
        return 1
    return 0


def a_covering_pair_is_directed(out: list[str]) -> int:
    """Check BOTH orderings appear when both columns are predicates — the discriminator.

    ⚑ WITHOUT THIS ARM THE SYMMETRY ARM ABOVE WOULD BE SATISFIED BY A WRONGLY-SYMMETRIC
    `covering_pairs` TOO. `obs.uri` and `obs.kind` are both predicates in `q_by_kind`, so a
    correct directed census holds both orderings; a symmetric one holds one and silently
    under-nominates the covering index that leads with the other.
    """
    pairs = {(g.predicate, g.covered) for g in cc.covering_pairs(_QUERIES)}
    if ("obs.uri", "obs.kind") not in pairs or ("obs.kind", "obs.uri") not in pairs:
        out.append(f"selftest: covering pairs are not directed: {sorted(pairs)}")
        return 1
    # A non-predicate column must never LEAD a covering candidate.
    if any(g.predicate == "obs.ts" for g in cc.covering_pairs(_QUERIES)):
        out.append("selftest: a projected-only column leads a covering candidate")
        return 1
    return 0


def nomination_partitions_every_pair(out: list[str]) -> int:
    """Check every candidate lands in exactly one bucket — the invisible failure.

    ⚑ NO OUTPUT SHAPE REVEALS A DROPPED PAIR. It is simply absent from three lists at once, and
    a ranked report of what survived looks identical. Conservation is the only observer.
    """
    pairs = cc.covering_pairs(_QUERIES)
    n = cc.nominate(pairs, _LIVE, _KEYS)
    total = len(n.gaps) + len(n.key_served) + len(n.indexed)
    if total != len(pairs):
        out.append(f"selftest: {len(pairs)} candidates partitioned into {total}")
        return 1
    rebuilt = {(g.predicate, g.covered) for g in n.gaps + n.key_served + n.indexed}
    if rebuilt != {(g.predicate, g.covered) for g in pairs}:
        out.append("selftest: the partition's union is not the input")
        return 1
    return 0


def a_key_predicate_is_suppressed_not_dropped(out: list[str]) -> int:
    """Check a PK/UNIQUE predicate leaves the gap list but stays reportable."""
    n = cc.nominate(cc.covering_pairs(_QUERIES), _LIVE, _KEYS)
    if any(g.predicate in _KEYS for g in n.gaps):
        out.append("selftest: a key predicate was nominated as a gap")
        return 1
    if not n.key_served:
        out.append("selftest: the key-served bucket is empty — the suppression vanished")
        return 1
    return 0


def an_existing_composite_suppresses_its_pair(out: list[str]) -> int:
    """Check a pair the engine already indexes is not nominated."""
    n = cc.nominate(cc.covering_pairs(_QUERIES), _LIVE, _KEYS)
    if any({g.predicate, g.covered} == {"obs.uri", "obs.kind"} for g in n.gaps):
        out.append("selftest: an already-indexed pair was nominated as a gap")
        return 1
    if not n.indexed:
        out.append("selftest: the indexed bucket is empty — the live map was not consulted")
        return 1
    return 0


def an_empty_index_map_over_nominates(out: list[str]) -> int:
    """Check the MEASURED defect's shape: an empty live map turns every pair into a gap.

    ⚑ THIS ARM ASSERTS THE BUG EXISTS, and that is deliberate. `column_contours` cannot tell an
    empty map from an unread one — no pure function can — so the arm pins the CONSEQUENCE, and
    the contrast with a populated map is what makes the caller's obligation to distinguish them
    legible rather than a sentence in a docstring. If someone ever gives the map a default, this
    arm still passes; what it protects is the reader's knowledge of the failure mode, and the
    strict inequality below is the evidence the map is load-bearing at all.
    """
    pairs = cc.covering_pairs(_QUERIES)
    blind = cc.nominate(pairs, _EMPTY_LIVE, _KEYS)
    seeing = cc.nominate(pairs, _LIVE, _KEYS)
    if len(blind.gaps) <= len(seeing.gaps):
        out.append(
            f"selftest: an empty live map nominated {len(blind.gaps)} gaps, "
            f"not more than the {len(seeing.gaps)} a populated one did — "
            "the map is not load-bearing and the over-nomination is untested"
        )
        return 1
    if blind.indexed:
        out.append("selftest: an empty live map reported an indexed pair")
        return 1
    return 0


def has_composite_matches_the_leading_pair_only(out: list[str]) -> int:
    """Check the pair is compared as a SET against the index's first two columns."""
    if not cc.has_composite(_LIVE, "obs.kind", "obs.uri"):
        out.append("selftest: the leading pair did not match in reversed order")
        return 1
    if cc.has_composite(_LIVE, "obs.uri", "obs.ts"):
        out.append("selftest: a pair absent from the index's prefix matched anyway")
        return 1
    if cc.has_composite(_LIVE, "edge.src", "edge.dst"):
        out.append("selftest: a table with no indexes reported a composite")
        return 1
    return 0


_ARMS = (
    elevation_is_totally_ordered,
    a_contour_never_crosses_tables,
    a_contour_is_symmetric,
    a_covering_pair_is_directed,
    nomination_partitions_every_pair,
    a_key_predicate_is_suppressed_not_dropped,
    an_existing_composite_suppresses_its_pair,
    an_empty_index_map_over_nominates,
    has_composite_matches_the_leading_pair_only,
)

# ⚑ DERIVED FROM `_ARMS`, NEVER TYPED — a hand-kept count is a second roster that drifts.
_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"column-contours selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"column-contours selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
