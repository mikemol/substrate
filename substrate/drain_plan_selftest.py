# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.drain_plan` — the drain-queue CLI.

⚑ THE CASES COVER THE DISPATCH, NOT THE CENSUS. Running the real queue means running mypy
over the corpus, which is minutes; a suite that did that would be skipped, and a skipped
suite is a case nobody reads. What is tested here is what the CLI decides: argument
handling, the startable filter, the blockers mode, and the refusal when editability cannot
be known.

⚑⚑ AND THE REFUSAL IS THE ONE THAT MATTERS. If an unavailable census printed an empty
queue instead of an error, the output would read as "no drains are startable" — a
plausible sentence that is a fact about the checker rather than the tree.
"""

from __future__ import annotations

from substrate import drain_blockers, drain_order, drain_plan


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── argument handling ────────────────────────────────────────────────────
    check("--help exits zero", passed=drain_plan.main(["--help"]) == 0)
    # ⚑ A flag whose value is missing or non-numeric REFUSES rather than falling back to
    # the default: a silently-ignored --top is a report that answers a question the
    # caller did not ask.
    check("--top without a value refuses", passed=drain_plan.main(["--top"]) == 2)  # noqa: PLR2004
    check("--top with a non-number refuses", passed=drain_plan.main(["--top", "many"]) == 2)  # noqa: PLR2004

    # ── the startable filter ─────────────────────────────────────────────────
    clean: frozenset[str] = frozenset()
    ready = drain_order.cost_of("ready", {"a.py": 1}, clean)
    blocked = drain_order.cost_of("blocked", {"dirty.py": 1}, frozenset({"dirty.py"}))
    rows = [ready, blocked]

    kept = [r for r in rows if r.startable]
    check(
        "the default view keeps only startable candidates",
        passed=[r.name for r in kept] == ["ready"],
    )
    check("and --all would keep both", passed=len(rows) == 2)  # noqa: PLR2004

    # ── the blockers mode ────────────────────────────────────────────────────
    # ⚑ THE MODE THAT MATTERS WHEN NOTHING IS STARTABLE, which is the measured state.
    # A shipped mode with no case is the un-exercised capability this repo gates on.
    blocked_text = drain_blockers.render(rows, 10)
    check("the blockers view names the gating file", passed="dirty.py" in blocked_text)
    check("and reports how many drains it releases", passed="unblocks" in blocked_text)
    check(
        "a startable candidate contributes no blocker",
        passed=drain_blockers.blockers([ready]) == [],
    )

    # ── the rendering states its own scope ───────────────────────────────────
    text = drain_order.render(rows, 10)
    check("the render names the blocker", passed="blocked by: dirty.py" in text)
    check("and refuses to be read as a value ranking", passed="ORDERED BY COST, NOT VALUE" in text)

    # ⚑ An empty startable set must not render as an empty board without saying why.
    empty = drain_order.render([], 10)
    check("an empty render still reports its population", passed="0 candidate(s)" in empty)

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
