#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.typehole` — the origin's positional behaviour, and the keyed repair.

⚑⚑ THE POSITIONAL ARMS PIN THE ORIGIN, READ FROM ITS SOURCE (`jea_pysim.py:555-605`): the
shared leaf, the same-head recursion, the variadic hole on an arity mismatch, the diverged
skeleton when children still share, and the terminal hole when nothing does. `jea_pysim` is a
bare-import module the package cannot import cleanly, so these are transcriptions of its
branches rather than a live differential — stated as such, and the reason every branch has
its own arm.

⚑⚑⚑ THE KEYED ARM IS amr-skills' MEASURED FAILURE IN MINIATURE: two candidates with the same
head, children keyed by role, one carrying an extra role. Positionally that is an arity
mismatch and the whole subtree vanishes into one variadic hole — 0 votes of support in 64 of
64 sentences. Keyed, the common roles recurse and the shared filler surfaces as `shared`,
which is what a support vote is made of; the extra role is still reported as a hole.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from substrate import typehole as th


@dataclass(frozen=True, slots=True)
class _Node:
    kind: str
    role: str = ""
    op: str = ""
    lit: str = ""
    children: tuple[int, ...] = ()
    payload: tuple[object, ...] = ()


@dataclass
class _Table:
    nodes: list[_Node] = field(default_factory=list)

    def add(
        self,
        kind: str,
        *children: int,
        role: str = "",
        op: str = "",
        lit: str = "",
        payload: tuple[object, ...] = (),
    ) -> int:
        self.nodes.append(_Node(kind, role, op, lit, tuple(children), payload))
        return len(self.nodes) - 1


def _kids(report: th.Report) -> list[th.Report]:
    """Return a report's children as reports, narrowing at the seam."""
    kids = report.get("children")
    if not isinstance(kids, list):
        return []
    return [k for k in kids if isinstance(k, dict)]


def _kinds(report: th.Report) -> list[object]:
    """Return the `kind` of each child report."""
    return [k.get("kind") for k in _kids(report)]


def identical_ids_are_one_shared_leaf(out: list[str]) -> int:
    """Check the base case: the same id K times is `shared`, with the four-tuple head."""
    t = _Table()
    a = t.add("Name", role="local0", payload=("x",))
    r = th.typehole(t, [a, a, a])
    shared = r.get("kind") == "shared" and r.get("head") == ("Name", "local0", "", "")
    if not shared or r.get("node") != a:
        out.append(f"selftest: the shared leaf read {r!r}")
        return 1
    return 0


def positional_children_recurse_and_the_variadic_hole_stops(out: list[str]) -> int:
    """Check the origin's two same-head branches: equal arity recurses; unequal is one hole."""
    t = _Table()
    x = t.add("Name", payload=("x",))
    y = t.add("Name", payload=("y",))
    # ⚑ A LEAF DIFFERING ONLY IN PAYLOAD IS NOT A HOLE — payload is residue, outside the head,
    # so two `Name`s with different names are an agreeing (empty) skeleton in the origin. The
    # hole below needs a head that differs: a Constant against a Name.
    z = t.add("Constant", lit="int", payload=(3,))
    c2a, c2b = t.add("Call", x, y), t.add("Call", x, z)
    c3 = t.add("Call", x, y, z)
    bad = 0
    same = th.typehole(t, [c2a, c2b])
    if same.get("kind") != "skeleton" or _kinds(same) != ["shared", "hole"]:
        out.append(f"selftest: equal-arity positional recursion read {same!r}")
        bad += 1
    var = th.typehole(t, [c2a, c3])
    kids = _kids(var)
    if (
        var.get("kind") != "skeleton"
        or len(kids) != 1
        or kids[0].get("type") != "Call:variadic"
        or "keyed" in var
    ):
        out.append(f"selftest: the positional variadic hole read {var!r}")
        bad += 1
    return bad


def diverging_heads_keep_a_shared_child_and_drop_a_hole_otherwise(out: list[str]) -> int:
    """Check the diverged branch: shared children make a skeleton; none makes a terminal hole."""
    t = _Table()
    x = t.add("Name", payload=("x",))
    add, mul = t.add("BinOp", x, x, op="Add"), t.add("BinOp", x, x, op="Mult")
    bad = 0
    d = th.typehole(t, [add, mul])
    if (
        d.get("kind") != "skeleton"
        or d.get("diverged") is not True
        or d.get("head") != ("BinOp", "", "")
    ):
        out.append(f"selftest: diverging heads with shared children read {d!r}")
        bad += 1
    n, s = t.add("Name", payload=("n",)), t.add("Constant", lit="str", payload=("s",))
    h = th.typehole(t, [n, s])
    terminal = h.get("kind") == "hole" and h.get("type") == "?"
    if not terminal or h.get("head_kinds") != ["Constant", "Name"]:
        out.append(f"selftest: the terminal hole read {h!r}")
        bad += 1
    return bad


def keyed_children_align_by_role_and_still_report_the_extra_one(out: list[str]) -> int:
    """Check amr-skills' case: same head, role-keyed children, one candidate with an extra role."""
    t = _Table()
    boy = t.add("concept", role=":ARG0", payload=("boy",))
    girl = t.add("concept", role=":ARG1", payload=("girl",))
    now = t.add("concept", role=":time", payload=("now",))
    want_a = t.add("frame", boy, girl, payload=("want-01",))
    want_b = t.add("frame", boy, girl, now, payload=("want-01",))
    r = th.typehole(t, [want_a, want_b])
    bad = 0
    if r.get("kind") != "skeleton" or r.get("keyed") is not True:
        out.append(f"selftest: keyed alignment did not engage: {r!r}")
        return 1
    kinds = _kinds(r)
    if kinds != ["shared", "shared", "hole"]:
        out.append(f"selftest: keyed children read {kinds}, want the two shared roles then a hole")
        bad += 1
    kids = _kids(r)
    if kids and kids[-1].get("keys") != [":time"]:
        out.append(f"selftest: the extra role was not named: {kids[-1]!r}")
        bad += 1
    return bad


def a_partially_keyed_node_is_positional(out: list[str]) -> int:
    """Check the rule's edge: one unkeyed child, or a duplicate key, means positional alignment."""
    t = _Table()
    a = t.add("concept", role=":ARG0")
    b = t.add("concept")
    dup = t.add("concept", role=":ARG0")
    bad = 0
    p = th.typehole(t, [t.add("frame", a, b), t.add("frame", a, b, dup)])
    if p.get("keyed") is not None or _kinds(p) != ["hole"]:
        out.append(f"selftest: a partially keyed node did not fall back to positional: {p!r}")
        bad += 1
    d = th.typehole(t, [t.add("frame", a, dup), t.add("frame", a, dup, b)])
    if d.get("keyed") is not None:
        out.append(f"selftest: duplicate keys did not fall back to positional: {d!r}")
        bad += 1
    return bad


_ARMS = (
    identical_ids_are_one_shared_leaf,
    positional_children_recurse_and_the_variadic_hole_stops,
    diverging_heads_keep_a_shared_child_and_drop_a_hole_otherwise,
    keyed_children_align_by_role_and_still_report_the_extra_one,
    a_partially_keyed_node_is_positional,
)

_CASE_COUNT = 1 + 2 + 2 + 3 + 2


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"typehole selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"typehole selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
