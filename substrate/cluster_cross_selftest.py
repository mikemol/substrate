# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `cluster_cross` — which clusters span two trees.

⚑ THE CONTROLS CARRY AS MUCH WEIGHT AS THE CASES: a cluster wholly inside one tree must NOT be
reported, and a root that is merely a SUBSTRING of a path must not claim it — a census that
reported every cluster would pass every "spans both" assertion.
"""

from __future__ import annotations

import sys

from substrate import cluster_cross

_A = "/r/mtools/"
_B = "/r/substrate/"

# The fixture's clusters, by what each one is.
_SPANNING = 0
_ONE_TREE = 1
_SUBSTRING_ROOT = 2
_NO_UNITS = 3

_CLUSTERS: list[object] = [
    {"units": ["/r/mtools/x.py::f:1", "/r/substrate/y.py::g:2"]},
    {"units": ["/r/substrate/y.py::h:3", "/r/substrate/z.py::k:4"]},
    {"units": ["/q/r/mtools/w.py::m:5", "/r/substrate/y.py::n:6"]},
    {"nothing": True},
    "not a cluster",
]


def main(argv: list[str]) -> int:
    """Run every case; exit 1 if any failed. Refuses any argument but `--selftest`."""
    if argv[1:] not in ([], ["--selftest"]):
        sys.stderr.write("cluster_cross_selftest: takes no argument but --selftest\n")
        return cluster_cross.USAGE_EXIT
    found = cluster_cross.spans(_CLUSTERS, _A, _B)
    indices = [s.index for s in found]
    lines = cluster_cross.render(found, len(_CLUSTERS))
    cases = [
        ("a cluster with a member in each tree spans", indices == [_SPANNING]),
        ("each side carries its own members", found[0].a == ("/r/mtools/x.py::f:1",)),
        ("a one-tree cluster is not reported", _ONE_TREE not in indices),
        ("a root is a PREFIX, not a substring", _SUBSTRING_ROOT not in indices),
        ("a cluster without units is skipped, not a crash", _NO_UNITS not in indices),
        ("the denominator is printed", lines[-1] == "1 of 5 cluster(s) span both trees"),
        ("a wrong arity is refused", cluster_cross.main(["cc"]) == cluster_cross.USAGE_EXIT),
    ]
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"cluster-cross selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE: its predicate needs an entry point AND
# the `--selftest` literal, and a suite without it is written, green, and run by nothing.
if __name__ == "__main__":
    sys.exit(main(sys.argv))
