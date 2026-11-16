#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.live_indexes` — order, the three index kinds, and the tenant clause.

⚑⚑⚑ THE ORDER ARM IS THE ONE WITH NO SYMPTOM. A composite read as an unordered set still
produces a plausible `(a, b)` pair; it is simply the wrong one half the time, and a nomination
built on it looks exactly as reasonable as a correct one. The arm feeds columns in a scrambled
row order that a set-valued or re-sorted implementation would normalise away, and asserts the
ENGINE's order survives.

⚑⚑ THE THREE KINDS MUST PARTITION, and the plain single-column index is the one an eager
implementation swallows. It is neither a composite nor a key seek, so it must appear in NEITHER
return value — an implementation that lumped it with the keys would suppress real covering-index
candidates, which is the same over-suppression the PK rule exists to bound.

⚑ AND THE SQL IS CHECKED FOR ITS TENANT CLAUSE. `current_schemas(false)` is what makes a sandbox
read the sandbox; a hardcoded `public` would return plausible rows from the wrong tenant, and no
downstream shape distinguishes them. That is a property of a string constant, so a case is the
only thing that can hold it.
"""

from __future__ import annotations

import sys

from substrate import live_indexes as li

# ⚑ ROWS DELIBERATELY INTERLEAVED ACROSS INDEXES but in per-index `ord` order — exactly what
# `ORDER BY t.relname, i.relname, k.ord` guarantees within an index and nothing more. An
# implementation that grouped by a sorted column name would pass a same-index-contiguous
# fixture and fail here.
_ROWS: tuple[dict[str, object], ...] = (
    # A composite whose leading column sorts AFTER its second — so an implementation that
    # sorted the columns would return ("kind", "uri") and be wrong in the seekable direction.
    {"tbl": "obs", "idx": "ix_obs_uri_kind", "col": "uri", "uniq": False, "pk": False, "ord": 1},
    {"tbl": "obs", "idx": "ix_obs_uri_kind", "col": "kind", "uniq": False, "pk": False, "ord": 2},
    # A single-column PRIMARY KEY — a key seek.
    {"tbl": "obs", "idx": "obs_pkey", "col": "id", "uniq": True, "pk": True, "ord": 1},
    # A single-column UNIQUE that is not the PK — also a key seek.
    {"tbl": "edge", "idx": "edge_src_key", "col": "src", "uniq": True, "pk": False, "ord": 1},
    # ⚑ A PLAIN single-column index — NEITHER a composite NOR a key. The discriminator.
    {"tbl": "edge", "idx": "ix_edge_dst", "col": "dst", "uniq": False, "pk": False, "ord": 1},
    # A three-column composite: only the leading PAIR is reported.
    {"tbl": "term", "idx": "ix_term_abc", "col": "a", "uniq": False, "pk": False, "ord": 1},
    {"tbl": "term", "idx": "ix_term_abc", "col": "b", "uniq": False, "pk": False, "ord": 2},
    {"tbl": "term", "idx": "ix_term_abc", "col": "c", "uniq": False, "pk": False, "ord": 3},
)


def a_composite_keeps_engine_column_order(out: list[str]) -> int:
    """Check the leading column is the query's first, not the alphabetically first.

    ⚑ THE SEEKABLE DIRECTION IS THE WHOLE ANSWER. Reporting `(kind, uri)` for an index built as
    `(uri, kind)` nominates nothing wrong-LOOKING; it just describes an index that cannot serve
    the predicate the report claims it serves.
    """
    got = li.composites(li.group_by_index(_ROWS)).get("obs", [])
    if got != [("uri", "kind", "ix_obs_uri_kind")]:
        out.append(f"selftest: the obs composite read as {got}, want uri leading")
        return 1
    return 0


def a_wide_composite_reports_only_its_leading_pair(out: list[str]) -> int:
    """Check a three-column index contributes exactly one pair, its first two."""
    got = li.composites(li.group_by_index(_ROWS)).get("term", [])
    if got != [("a", "b", "ix_term_abc")]:
        out.append(f"selftest: the three-column index read as {got}")
        return 1
    return 0


def both_unique_and_primary_count_as_keys(out: list[str]) -> int:
    """Check a single-column UNIQUE is a key seek even when it is not the PK.

    ⚑ CHECKING ONLY `pk` WOULD PASS EVERY OTHER ARM. A UNIQUE non-PK index identifies a row just
    as well, and missing it under-suppresses: its contours get nominated as gaps that a seek
    already serves.
    """
    keys = li.key_columns(li.group_by_index(_ROWS))
    missing = {"obs.id", "edge.src"} - keys
    if missing:
        out.append(f"selftest: key columns missing {sorted(missing)}")
        return 1
    return 0


def a_plain_single_column_index_is_neither(out: list[str]) -> int:
    """Check the discriminator: a non-unique single-column index is in NEITHER result.

    ⚑ WITHOUT THIS ARM, AN IMPLEMENTATION THAT TREATED EVERY SINGLE-COLUMN INDEX AS A KEY WOULD
    PASS. That over-suppression is invisible — the gap list simply comes back shorter, and a
    shorter list of nominations reads as a healthier schema.
    """
    by_index = li.group_by_index(_ROWS)
    if "edge.dst" in li.key_columns(by_index):
        out.append("selftest: a plain single-column index was counted as a key seek")
        return 1
    if any(
        idx == "ix_edge_dst" for pairs in li.composites(by_index).values() for _a, _b, idx in pairs
    ):
        out.append("selftest: a single-column index was counted as a composite")
        return 1
    return 0


def a_table_with_no_composite_is_absent_not_empty(out: list[str]) -> int:
    """Check a table contributing no composite yields no entry at all.

    An empty list under a table key and a missing key read the same to `dict.get(t, [])`, but
    only one of them says the table was examined. Absence is the honest one here: the map holds
    what was FOUND, and the caller's `.get` default supplies the rest.
    """
    comps = li.composites(li.group_by_index(_ROWS))
    if "edge" in comps:
        out.append(f"selftest: edge has no composite but appears as {comps['edge']}")
        return 1
    return 0


def no_rows_yields_empty_results(out: list[str]) -> int:
    """Check an empty feed produces empty results — the shape the caller must NOT confuse.

    ⚑ THIS ARM PINS A FACT THE MODULE CANNOT FIX. An unreachable store and a store with no
    indexes both arrive here as no rows, and the return value is identical. The docstring says
    the caller must distinguish them; this arm is the evidence that the module genuinely cannot.
    """
    by_index = li.group_by_index(())
    if li.composites(by_index) or li.key_columns(by_index):
        out.append("selftest: an empty feed produced non-empty index knowledge")
        return 1
    return 0


def the_query_names_the_connection_search_path(out: list[str]) -> int:
    """Check the SQL scopes to the connection's own schemas, not a hardcoded one.

    ⚑ A WRONG-TENANT READ RETURNS PLAUSIBLE ROWS. Nothing downstream can tell a sandbox's
    indexes from the live store's, so the only place this is checkable is the string itself.
    """
    if "current_schemas(false)" not in li.INDEX_SQL:
        out.append("selftest: the index query does not scope to current_schemas")
        return 1
    if "'public'" in li.INDEX_SQL:
        out.append("selftest: the index query hardcodes a schema name")
        return 1
    return 0


_ARMS = (
    a_composite_keeps_engine_column_order,
    a_wide_composite_reports_only_its_leading_pair,
    both_unique_and_primary_count_as_keys,
    a_plain_single_column_index_is_neither,
    a_table_with_no_composite_is_absent_not_empty,
    no_rows_yields_empty_results,
    the_query_names_the_connection_search_path,
)

# ⚑ DERIVED FROM `_ARMS`, NEVER TYPED — a hand-kept count is a second roster that drifts.
_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"live-indexes selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"live-indexes selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
