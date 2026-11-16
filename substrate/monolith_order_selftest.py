# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.monolith_order` — biggest first, unless something blocks it.

⚑⚑⚑ THE BLOCKING CLAUSE IS WHERE THIS GOES SILENTLY WRONG, so it is pinned in both
directions. A monolith emitted ahead of its blocker is a plan that cannot begin — the operator
starts the largest file and hits a wall the ordering already knew about. A blocker emitted
that ISN'T one stalls work that was available. Neither failure announces itself in the output.

⚑⚑ AND THE ORDER MUST NOT DEPEND ON THE INPUT'S ORDER. A size sort with the blocked rows
patched downward gives different answers for different starting dicts, which makes two runs
over an unchanged tree disagree and a diff meaningless. The case feeds the same graph twice in
different insertion orders and requires the same result.

⚑ A DEFERRED IMPORT IS NOT A BLOCKER, and that distinction belongs to the CALLER — this module
takes whatever edge set it is given. The case documents the contract by passing module-level
edges only, so a future caller that hands it deferred edges too can see what it broke.
"""

from __future__ import annotations

from substrate import monolith_order


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── biggest first when nothing blocks ────────────────────────────────────
    plain = monolith_order.order({"big.py": 300, "mid.py": 100, "small.py": 10}, {})
    check(
        "with no edges, the largest file leads",
        passed=[m.path for m in plain] == ["big.py", "mid.py", "small.py"],
    )
    check("and every row is startable", passed=all(m.startable for m in plain))

    # ── THE CLAUSE: a blocker precedes what it blocks, even when smaller ─────
    # ⚑ THE WHOLE POINT. `big` imports `small`, so `small` must come first despite being a
    # thirtieth of the size — otherwise the operator starts `big` and discovers the wall.
    blocked = monolith_order.order({"big.py": 300, "small.py": 10}, {"big.py": {"small.py"}})
    check(
        "a smaller blocker is emitted before the monolith it blocks",
        passed=[m.path for m in blocked] == ["small.py", "big.py"],
    )
    check(
        "and the monolith records what it waited on", passed=blocked[1].blocked_by == ("small.py",)
    )
    check("while the blocker itself is startable", passed=blocked[0].startable)

    # ⚑ A CLEAN DEPENDENCY DOES NOT BLOCK. Only DIRTY files are in the population, so an
    # edge into a file nobody must clean is not a wait.
    unblocked = monolith_order.order({"big.py": 300}, {"big.py": {"already_clean.py"}})
    check("an edge to a file outside the dirty set does not block", passed=unblocked[0].startable)

    # ⚑ AND A SELF-EDGE DOES NOT BLOCK — counting it would make every file unstartable and
    # the ordering empty, which reads as "nothing can be done".
    selfish = monolith_order.order({"a.py": 5}, {"a.py": {"a.py"}})
    check("a self-edge is not a blocker", passed=len(selfish) == 1 and selfish[0].startable)

    # ── the order does not depend on the input's order ──────────────────────
    # ⚑ TWO RUNS OVER AN UNCHANGED TREE MUST AGREE, or a diff of two reports shows churn
    # rather than movement.
    edges = {"a.py": {"c.py"}, "b.py": {"c.py"}}
    one = monolith_order.order({"a.py": 90, "b.py": 80, "c.py": 5}, edges)
    two = monolith_order.order({"c.py": 5, "b.py": 80, "a.py": 90}, edges)
    check(
        "the ordering is independent of input order",
        passed=[m.path for m in one] == [m.path for m in two],
    )
    check("and the shared blocker leads both", passed=one[0].path == "c.py")

    # ── a chain orders end to end ───────────────────────────────────────────
    chain = monolith_order.order(
        {"a.py": 300, "b.py": 200, "c.py": 100}, {"a.py": {"b.py"}, "b.py": {"c.py"}}
    )
    check(
        "a dependency chain orders from its far end",
        passed=[m.path for m in chain] == ["c.py", "b.py", "a.py"],
    )

    # ── a cycle is REPORTED, not broken arbitrarily ─────────────────────────
    # ⚑ AN ARBITRARY LINEARISATION WOULD HIDE THE ONE FACT THAT MATTERS: one of these must
    # be cut before either can move.
    cyc = monolith_order.order({"x.py": 50, "y.py": 40}, {"x.py": {"y.py"}, "y.py": {"x.py"}})
    check("a cycle still emits every file", passed=len(cyc) == 2)  # noqa: PLR2004
    check(
        "and the cycle is detectable rather than silent", passed=len(monolith_order.cycles(cyc)) > 0
    )
    # ⚑ THE ACYCLIC CASE MUST REPORT NO CYCLE, or the detector is stuck-on and useless.
    check("an acyclic order reports no cycle", passed=monolith_order.cycles(chain) == [])

    # ── UNPLACED IS NOT THE SAME SET AS THE KNOT ────────────────────────────
    # ⚑⚑⚑ A FILE STRANDED BEHIND A CYCLE CANNOT BE PLACED EITHER, so it appears in `cycles`
    # while being on nobody's cut list. MEASURED LIVE: twelve unplaced rows, of which two
    # carried no edge to another member — an order of magnitude cheaper than the rest and
    # merely stranded. A reader taking that list as "the cycle" weighs a cut against files
    # that are not in it, which is how a cut lands on the wrong file.
    stranded = monolith_order.order(
        {"x.py": 50, "y.py": 40, "behind.py": 30},
        {"x.py": {"y.py"}, "y.py": {"x.py"}, "behind.py": {"x.py"}},
    )
    unplaced = {m.path for m in monolith_order.cycles(stranded)}
    tied = {m.path for m in monolith_order.knot(stranded)}
    check("the stranded file is unplaced", passed="behind.py" in unplaced)
    # ⚑ AND IS NOT IN THE KNOT — cutting it would free nothing, because the knot stays tied.
    check("but is NOT in the knot", passed="behind.py" not in tied)
    check("while both true members are", passed={"x.py", "y.py"} <= tied)

    # ── the hub is the cheapest cut ─────────────────────────────────────────
    # ⚑ THE MOST-DEPENDED-ON MEMBER FREES THE MOST ROWS AT ONCE. Here two members wait on
    # `h.py` and nothing waits on the others.
    hubbed = monolith_order.order(
        {"h.py": 10, "a.py": 20, "b.py": 30},
        {"h.py": {"a.py"}, "a.py": {"h.py"}, "b.py": {"h.py", "a.py"}},
    )
    check(
        "the hub is the member most others wait on",
        passed=monolith_order.hub(hubbed) in {"h.py", "a.py"},
    )
    # ⚑ AND AN ACYCLIC ORDER HAS NO HUB — an empty string, not an arbitrary pick.
    check("an acyclic order names no hub", passed=monolith_order.hub(chain) == "")

    # ── rendering surfaces the wait and the cycle ───────────────────────────
    text = monolith_order.render(blocked)
    check("the rendering names what a blocked file waits on", passed="waits on: small.py" in text)
    check(
        "and a cycle is called out in the rendering", passed="CYCLE" in monolith_order.render(cyc)
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
