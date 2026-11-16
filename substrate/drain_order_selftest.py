# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.drain_order` — the cost ordering over drain candidates.

⚑ THE LOAD-BEARING CASE IS THE INVERSION. A candidate reaching many files must sort
BELOW one reaching few, even though the first retires more inserts and leads the value
ranking. If that case ever passes with the order reversed, this module has silently
become a second copy of the ranking it exists to complement.

⚑⚑ AND A BLOCKED CANDIDATE MUST NAME ITS BLOCKERS. "Blocked" alone is a wall; the list
of dirty consumers is a queue, and it is the difference between a plan and a complaint.
"""

from __future__ import annotations

from substrate import drain_order


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    clean: frozenset[str] = frozenset()

    # ── one name, one file ───────────────────────────────────────────────────
    cheap = drain_order.cost_of("reuse_tui", {"scripts/reuse_sweep.py": 1}, clean)
    check("a single consumer counts one file", passed=len(cheap.files) == 1)
    check("and one site", passed=cheap.sites == 1)
    check("with every consumer clean, it is startable", passed=cheap.startable)

    # ── sites and files are kept apart ───────────────────────────────────────
    # ⚑ One file importing a name five times is ONE edit and five sites. Collapsing
    # to either number alone loses a distinction a planner uses.
    repeat = drain_order.cost_of("agda_lex", {"scratch/a.py": 5}, clean)
    check("repeated sites in one file stay one file", passed=len(repeat.files) == 1)
    check("but the site count carries the repetition", passed=repeat.sites == 5)  # noqa: PLR2004

    # ── a dirty consumer blocks, and is named ────────────────────────────────
    blocked = drain_order.cost_of(
        "edit_snapshot",
        {"scratch/dirty.py": 2, "scratch/clean.py": 1},
        frozenset({"scratch/dirty.py"}),
    )
    check("a dirty consumer makes the drain unstartable", passed=not blocked.startable)
    check(
        "and the blocker is named, not merely counted",
        passed=blocked.dirty == ("scratch/dirty.py",),
    )
    check(
        "the clean consumer is not reported as a blocker",
        passed="scratch/clean.py" not in blocked.dirty,
    )

    # ── THE INVERSION: cost order is not value order ─────────────────────────
    wide = drain_order.cost_of("wide", {f"scratch/f{i}.py": 1 for i in range(20)}, clean)
    rows = drain_order.ordered([wide, cheap])
    check("the candidate reaching FEWER files sorts first", passed=rows[0].name == "reuse_tui")
    # ⚑ And that is the opposite of the retire-count ranking, where `wide` leads
    # precisely because it reaches more files.
    check("the wide candidate sorts last despite retiring more", passed=rows[-1].name == "wide")

    # ── startable beats cheap ────────────────────────────────────────────────
    # ⚑ A one-file drain behind a dirty consumer is NOT startable, so it sorts below
    # a three-file drain that is — because the first cannot begin at all today.
    tiny_blocked = drain_order.cost_of(
        "tiny", {"scratch/dirty.py": 1}, frozenset({"scratch/dirty.py"})
    )
    three_clean = drain_order.cost_of("three", {"a.py": 1, "b.py": 1, "c.py": 1}, clean)
    ranked = drain_order.ordered([tiny_blocked, three_clean])
    check("a startable drain outranks a smaller blocked one", passed=ranked[0].name == "three")

    # ── the render states its own scope ──────────────────────────────────────
    text = drain_order.render([cheap, blocked], limit=10)
    check("the render counts the startable subset", passed="1 startable" in text)
    check("and names the blocker inline", passed="blocked by: scratch/dirty.py" in text)
    check("and refuses to be read as a value ranking", passed="ORDERED BY COST, NOT VALUE" in text)

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
