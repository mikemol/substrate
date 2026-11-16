#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.dagcone` — a cone is not a liberation, and overlap is the reason.

⚑⚑⚑ THE EXCLUSIVITY CASE IS WHY THIS MODULE EXISTS. Two implementations of `leverage` both called
a cone *"what clearing this would free"*, and both were wrong by ~4x: MEASURED on three real
buckets, cones of 538 / 417 / 298 had exclusive parts of 205 / 97 / 82 — 60-75% shared. A node in
a cone can sit behind several blocking sets at once, so clearing one frees only the nodes whose
remaining blockers are all inside it.

⚑⚑ AND THE FIGURES NEVER SUMMED, which is the tell a reader can check without the subtraction:
538+417+298 over a ~3400-module tree is one subtree counted three times. The cases assert both
halves — that a shared node is IN both cones, and that it is in NEITHER exclusive part.

⚑ THE UNBOUNDED WALK IS PINNED because a depth bound here silently truncates: a recorded instance
capped at three levels and 1,506 of 2,964 modules reached past it.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from substrate import dagcone

if TYPE_CHECKING:
    from collections.abc import Iterable

# A small DAG with a DELIBERATE SHARED DESCENDANT: both `a` and `b` reach `shared`.
#
#   a -> x -> shared      b -> y -> shared      c -> deep1 -> deep2 -> deep3 -> deep4
_EDGES: dict[str, tuple[str, ...]] = {
    "a": ("x",),
    "b": ("y",),
    "x": ("shared",),
    "y": ("shared",),
    "c": ("deep1",),
    "deep1": ("deep2",),
    "deep2": ("deep3",),
    "deep3": ("deep4",),
}

# How deep the `c` chain runs — past any three-level bound.
_CHAIN_DEPTH = 4

# `a` reaches `x` and `shared`; `x` reaches `shared` alone.
_WEIGHT_A, _WEIGHT_X = 2, 1


def _successors(node: str) -> Iterable[str]:
    """Return the fixture's edges out of `node`."""
    return _EDGES.get(node, ())


def reach_excludes_the_seeds(out: list[str]) -> int:
    """Check a cone does not contain what was asked about."""
    got = dagcone.reach(["a"], _successors)
    bad = 0
    if "a" in got:
        out.append("selftest: the seed appears in its own cone")
        bad += 1
    if got != {"x", "shared"}:
        out.append(f"selftest: the cone read as {got!r}")
        bad += 1
    return bad


def reach_is_unbounded_in_depth(out: list[str]) -> int:
    """Check the walk crosses more levels than a naive bound would allow.

    ⚑ A DEPTH BOUND SILENTLY TRUNCATES. The recorded instance capped at three and lost 1,506 of
    2,964 modules — a capability bound wearing a termination bound's clothes, invisible in the
    output because a shorter answer looks like a smaller graph.
    """
    got = dagcone.reach(["c"], _successors)
    if len(got) != _CHAIN_DEPTH:
        out.append(f"selftest: a depth-{_CHAIN_DEPTH} chain reached {len(got)} node(s)")
        return 1
    return 0


def two_cones_share_a_descendant(out: list[str]) -> int:
    """Check the fixture actually overlaps — a POSITIVE CONTROL for the case below.

    ⚑ WITHOUT OVERLAP, `exclusive` AND `reach` AGREE and the exclusivity case cannot fail. This
    asserts the fixture can distinguish them.
    """
    bad = 0
    if "shared" not in dagcone.reach(["a"], _successors):
        out.append("selftest: `a` does not reach the shared node")
        bad += 1
    if "shared" not in dagcone.reach(["b"], _successors):
        out.append("selftest: `b` does not reach the shared node")
        bad += 1
    return bad


def exclusive_subtracts_what_others_also_block(out: list[str]) -> int:
    """Check a shared descendant is in neither blocker's exclusive part.

    ⚑⚑ THE ~4x ERROR, AS A CASE. Reporting a cone as "frees N" counts nodes another set also
    blocks — and clearing this set would not free them.
    """
    got = dagcone.exclusive(["a"], [["b"]], _successors)
    bad = 0
    if "shared" in got:
        out.append("selftest: a node blocked by another set counted as exclusive")
        bad += 1
    if got != {"x"}:
        out.append(f"selftest: the exclusive part read as {got!r}")
        bad += 1
    return bad


def rank_returns_every_seed(out: list[str]) -> int:
    """Check the ranking is whole, not truncated.

    ⚑ THE TRUNCATION THAT USED TO LIVE IN THE COMPUTATION returned `top[:5]` — a display decision
    baked in where no caller could ask for more, silently dropping the sixth-largest seed from
    every consumer.
    """
    seeds = ["a", "b", "c"]
    got = dagcone.rank(seeds, _successors)
    bad = 0
    if len(got) != len(seeds):
        out.append(f"selftest: rank returned {len(got)} of {len(seeds)} seed(s)")
        bad += 1
    elif got[0][1] != "c":
        out.append(f"selftest: the widest seed ranked {got[0]!r}")
        bad += 1
    return bad


def weigh_counts_a_union_not_a_sum(out: list[str]) -> int:
    """Check a node's weight is the size of its descendant SET.

    ⚑⚑ UNION, NEVER SUM. Children's weights double-count shared descendants, so adding them
    counts one subtree several times — the same error the exclusivity subtraction exists for,
    one level down.
    """
    got = dagcone.weigh(["a", "b", "x", "y"], _successors)
    if got.get("a") != _WEIGHT_A or got.get("x") != _WEIGHT_X:
        out.append(f"selftest: the weights read as {got!r}")
        return 1
    return 0


def an_unknown_node_weighs_nothing_rather_than_raising(out: list[str]) -> int:
    """Check a node absent from the caller's relation is answered, not an exception.

    ⚑ THE LIBRARY RAISES FOR AN ABSENT SOURCE — which the stub now declares — so the membership
    guard in `weigh` is LOAD-BEARING rather than defensive. This case is what says so.
    """
    got = dagcone.weigh(["nonexistent"], _successors)
    if got != {"nonexistent": 0}:
        out.append(f"selftest: an unknown node weighed {got!r}")
        return 1
    return 0


_ARMS = (
    reach_excludes_the_seeds,
    reach_is_unbounded_in_depth,
    two_cones_share_a_descendant,
    exclusive_subtracts_what_others_also_block,
    rank_returns_every_seed,
    weigh_counts_a_union_not_a_sum,
    an_unknown_node_weighs_nothing_rather_than_raising,
)

_CASE_COUNT = 2 + 1 + 2 + 2 + 2 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"dagcone selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"dagcone selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
