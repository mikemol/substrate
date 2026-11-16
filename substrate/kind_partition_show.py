#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Print a gate's added keys as a SHAPE — the CLI over `substrate.kind_partition`.

    kind_partition_show.py <gate-module>            # the kind partition
    kind_partition_show.py <gate-module> <kind>     # where that kind concentrates

⚑⚑ THE TWO MODES ANSWER THE TWO HALVES OF ONE QUESTION, and either alone is a reflex. The kind
partition says a population is `as x135, using x51` — and picking the biggest is not a
measurement. The concentration says whether those 135 keys are three PROVIDERS (three decisions,
one sweep) or 135 (a hand-edit each). **A count of keys is not a count of decisions.**

⚑ AN UNMEASURABLE GATE PRINTS ITS REASON AND EXITS NON-ZERO. Reporting "0 kinds" for a gate
nobody could read is a false green about a population never measured.
"""

from __future__ import annotations

import sys

from substrate import kind_partition

# `<gate>` alone, or `<gate> <kind>`.
_MIN_ARGS = 1


def main(argv: list[str]) -> int:
    """Partition one gate, or one of its kinds."""
    args = [a for a in argv[1:] if not a.startswith("-")]
    if len(args) < _MIN_ARGS:
        sys.stderr.write("usage: kind_partition_show.py <gate-module> [<kind>]\n")
        return 2

    name = args[0]
    kind = args[1] if len(args) > 1 else None

    if kind is None:
        buckets, why = kind_partition.kinds(name)
        heading = f"{name} — added keys by KIND"
    else:
        buckets, why = kind_partition.concentration(name, kind)
        heading = f"{name} — `{kind}` keys by IDENTITY (where the decisions are)"

    sys.stdout.write(f"  {heading}\n")
    if buckets is None:
        sys.stdout.write(f"  UNMEASURABLE: {why}\n")
        return 1

    for bucket in buckets:
        sys.stdout.write(f"    {bucket.n:>5}  {bucket.label}\n")
    sys.stdout.write(f"  {kind_partition.render(buckets, limit=len(buckets))}\n")

    if kind is None and buckets:
        # ⚑ THE SECOND HALF IS NAMED, because a reader stopping here has only the reflex.
        sys.stdout.write(
            f"    ⚑ a count is not a count of DECISIONS — ask where the biggest\n"
            f"      bucket concentrates: {argv[0]} {name} {buckets[0].label}\n"
        )
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS MODULE, and it DELEGATES rather than
# exiting 0 — a no-op guard reports nothing, which the outcome classifier calls `silent`.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import kind_partition_selftest

        sys.exit(kind_partition_selftest.selftest())
    sys.exit(main(sys.argv))
