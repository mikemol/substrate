#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.kind_partition` — a shape, not a count, and a truncation that says so.

⚑⚑⚑ THE ORDERING CASE IS WHAT MAKES THE PARTITION ACTIONABLE. Buckets are read to decide SWEEP
versus GRIND, so the largest must lead — and the tie-break must be deterministic, or two runs
over one census produce different reports and the population reads as moving.

⚑⚑ THE TRUNCATION CASE PROTECTS A CLASS OF SILENT LIE. A rendered summary sliced to four entries
is indistinguishable from a population that has four; stating `+N more` is what lets a reader
tell a short list from a cut one. The recorded instance is a render sliced to twelve while the
scalar reported the full count — the scalar was the honest half.

⚑ AND `n` RATHER THAN `count` IS PINNED BY THE TYPE CHECKER, not by a case here: a `NamedTuple`
field named `count` shadows `tuple.count`, which mypy refuses. A runtime case for a statically
enforced property would be unreachable code.
"""

from __future__ import annotations

import sys

from substrate import kind_partition


def _buckets(*pairs: tuple[str, int]) -> list[kind_partition.Bucket]:
    """Build buckets from `(label, n)` pairs."""
    return [kind_partition.Bucket(label=label, n=n, sample=f"{label}-key") for label, n in pairs]


def buckets_lead_with_the_largest(out: list[str]) -> int:
    """Check ordering is by size descending.

    ⚑ THE ORDER IS THE READING. A partition read to choose a tool must put the population that
    decides the choice first.
    """
    rows = {"small": ["a"], "big": ["b", "c", "d"], "mid": ["e", "f"]}
    got = [b.label for b in kind_partition.bucketed(rows)]
    if got != ["big", "mid", "small"]:
        out.append(f"selftest: buckets ordered {got}")
        return 1
    return 0


def equal_buckets_tie_break_by_label(out: list[str]) -> int:
    """Check two buckets of equal size order deterministically.

    ⚑ INSERTION ORDER WOULD MAKE THE REPORT MOVE between runs over one census, which reads as a
    changing population rather than as an unstable sort.
    """
    rows = {"zebra": ["a"], "alpha": ["b"]}
    got = [b.label for b in kind_partition.bucketed(rows)]
    if got != ["alpha", "zebra"]:
        out.append(f"selftest: equal buckets ordered {got}")
        return 1
    return 0


def the_sample_is_deterministic(out: list[str]) -> int:
    """Check the sample key is the least, not an arbitrary member."""
    rows = {"k": ["m", "a", "z"]}
    if kind_partition.bucketed(rows)[0].sample != "a":
        out.append("selftest: the sample is not the least key")
        return 1
    return 0


def a_truncated_render_says_so(out: list[str]) -> int:
    """Check a render beyond the limit states how many it omitted.

    ⚑ THE SILENT-SLICE CLASS. A summary cut to N looks exactly like a population of N, and the
    recorded instance had a render sliced to twelve while the scalar reported the full count.
    """
    got = kind_partition.render(_buckets(("a", 5), ("b", 4), ("c", 3), ("d", 2), ("e", 1)), limit=4)
    if "+1 more" not in got:
        out.append(f"selftest: a truncated render did not say so: {got!r}")
        return 1
    if "5 kind(s)" not in got:
        out.append(f"selftest: the render lost the true bucket count: {got!r}")
        return 1
    return 0


def an_untruncated_render_claims_nothing_extra(out: list[str]) -> int:
    """Check a short population renders without a `+N more`."""
    got = kind_partition.render(_buckets(("a", 2), ("b", 1)), limit=4)
    if "more" in got:
        out.append(f"selftest: a short render claimed omissions: {got!r}")
        return 1
    return 0


def an_empty_partition_is_named(out: list[str]) -> int:
    """Check no added keys renders as a fact rather than an empty string."""
    if kind_partition.render([]) != "no added keys":
        out.append("selftest: an empty partition rendered as nothing")
        return 1
    return 0


def an_unmeasurable_gate_returns_a_reason(out: list[str]) -> int:
    """Check a gate that cannot be censused gives None plus text, never an empty partition.

    ⚑ AN UNKNOWN SHAPE IS NOT A UNIFORM ONE. Returning `[]` here would let a caller print
    "0 kinds" for a gate nobody could read — a false green about a population never measured.
    """
    got, why = kind_partition.kinds("no_such_gate_module_anywhere")
    bad = 0
    if got is not None:
        out.append("selftest: an unmeasurable gate produced a partition")
        bad += 1
    if not why:
        out.append("selftest: an unmeasurable gate gave no reason")
        bad += 1
    return bad


def a_gate_without_a_schema_says_so(out: list[str]) -> int:
    """Check a gate with no key schema is reported as undeclared."""
    got, why = kind_partition.concentration("json", "using")
    bad = 0
    if got is not None:
        out.append("selftest: a schema-less gate produced a concentration")
        bad += 1
    if not why:
        out.append("selftest: a schema-less gate gave no reason")
        bad += 1
    return bad


_ARMS = (
    buckets_lead_with_the_largest,
    equal_buckets_tie_break_by_label,
    the_sample_is_deterministic,
    a_truncated_render_says_so,
    an_untruncated_render_claims_nothing_extra,
    an_empty_partition_is_named,
    an_unmeasurable_gate_returns_a_reason,
    a_gate_without_a_schema_says_so,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 1 + 1 + 2 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"kind-partition selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"kind-partition selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
