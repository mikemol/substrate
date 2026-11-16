# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.drain_blockers` — the blocker ranking.

⚑ THE LOAD-BEARING CASE IS THE SOLE-BLOCKER RULE. A drain waiting on two dirty files is
released by cleaning NEITHER, so counting it toward both would promise each paydown a
payoff it cannot deliver. If that case ever passes with joint blockers counted, the
ranking has become a list of files that merely APPEAR near drains.

⚑⚑ AND THE JOINTLY-BLOCKED DRAINS MUST STAY VISIBLE. They appear under no blocker by
construction, so a reader seeing only the ranking would conclude their consumers gate
nothing. Reported separately, or the ranking's silence about them reads as absence.
"""

from __future__ import annotations

from substrate import drain_blockers, drain_order


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    clean: frozenset[str] = frozenset()
    dirty_a = frozenset({"a.py"})
    dirty_ab = frozenset({"a.py", "b.py"})

    one = drain_order.cost_of("one", {"a.py": 1}, dirty_a)
    two = drain_order.cost_of("two", {"a.py": 1}, dirty_a)
    other = drain_order.cost_of("other", {"b.py": 1}, frozenset({"b.py"}))
    joint = drain_order.cost_of("joint", {"a.py": 1, "b.py": 1}, dirty_ab)
    free = drain_order.cost_of("free", {"c.py": 1}, clean)

    # ── the ranking ──────────────────────────────────────────────────────────
    rows = drain_blockers.blockers([one, two, other])
    check("the file blocking two drains ranks first", passed=bool(rows) and rows[0].path == "a.py")
    check("and names both drains it gates", passed=bool(rows) and rows[0].gates == ("one", "two"))
    check(
        "the file blocking one drain ranks below", passed=len(rows) == 2 and rows[1].path == "b.py"
    )  # noqa: PLR2004

    # ── THE SOLE-BLOCKER RULE ────────────────────────────────────────────────
    # ⚑ `joint` waits on BOTH files, so cleaning either releases nothing and it must
    # contribute to neither blocker's count.
    with_joint = drain_blockers.blockers([one, joint])
    check(
        "a jointly-blocked drain contributes to no blocker",
        passed=bool(with_joint) and with_joint[0].gates == ("one",),
    )
    check("and does not invent a second blocker row", passed=len(with_joint) == 1)

    # ⚑ But it must remain REPORTABLE, or the ranking's silence reads as absence.
    check(
        "a jointly-blocked drain is reported separately",
        passed=[c.name for c in drain_blockers.multiply_blocked([one, joint])] == ["joint"],
    )

    # ── THE EDITABILITY COLUMN ───────────────────────────────────────────────
    # ⚑ UNMEASURED IS NOT CLEAN. A blocker absent from the counts map must not report as
    # actionable, or a monolith lands at the head of a plan — measured, twice.
    unmeasured = drain_blockers.blockers([one])
    check(
        "a blocker with no measurement is not actionable",
        passed=bool(unmeasured) and not unmeasured[0].actionable,
    )
    check(
        "and its own count reads as unknown", passed=bool(unmeasured) and unmeasured[0].own is None
    )

    dirty_blocker = drain_blockers.blockers([one], {"a.py": 307})
    check(
        "a blocker carrying its own findings is not actionable",
        passed=bool(dirty_blocker) and not dirty_blocker[0].actionable,
    )

    clean_blocker = drain_blockers.blockers([one], {"a.py": 0})
    check(
        "a blocker measured clean IS actionable",
        passed=bool(clean_blocker) and clean_blocker[0].actionable,
    )

    # ⚑ ACTIONABILITY LEADS THE ORDER: a clean blocker gating one drain outranks a
    # monolith gating two, because the second is not a plan however much it gates.
    mixed = drain_blockers.blockers([one, two, other], {"b.py": 0, "a.py": 307})
    check(
        "an editable blocker outranks a monolith that gates more",
        passed=bool(mixed) and mixed[0].path == "b.py",
    )

    # ── a startable drain blocks nothing ─────────────────────────────────────
    check(
        "a drain with no dirty consumer yields no blocker",
        passed=drain_blockers.blockers([free]) == [],
    )

    # ── the render states its own scope ──────────────────────────────────────
    text = drain_blockers.render([one, two, joint], limit=10)
    check("the render names the top blocker", passed="a.py" in text)
    check(
        "and warns that joint blockers release nothing alone",
        passed="cleaning any one releases none of them" in text,
    )
    check("and refuses to be read as a site count", passed="NOT BY SITES" in text)

    # ⚑ An empty population still reports its population rather than nothing.
    check(
        "an empty input still states its scope",
        passed="0 file(s)" in drain_blockers.render([], limit=10),
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


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
