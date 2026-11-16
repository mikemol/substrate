# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.drain_queue` — the candidate/consumer/checker join.

⚑ THE LOAD-BEARING CASES ARE THE TWO REFUSALS. mypy can be absent, can fail to run, or can
report a census, and only the third is knowledge. If either failure returned an empty
dirty set, every candidate would report as startable and the queue would read its own
blindness as a green board — the false zero this whole family of readers refuses.

⚑⚑ AND A CANDIDATE NOTHING IMPORTS IS OMITTED, NOT FREE. Zero consumers means the reader
could not find its importers — the unresolvable dynamic-import shapes it names itself —
so reporting it as a costless drain would put an unmeasured candidate at the head of the
queue.
"""

from __future__ import annotations

from pathlib import Path

from substrate import drain_queue, mypy_census

_ROOT = Path(__file__).resolve().parent.parent


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    def refuses(census: dict[str, list[str]] | None) -> bool:
        try:
            drain_queue.dirty_files(census)
        except drain_queue.CensusUnavailableError:
            return True
        return False

    # ── THE THREE OUTCOMES ───────────────────────────────────────────────────
    check("an absent checker refuses rather than reporting a clean tree", passed=refuses(None))
    check(
        "an unrunnable census refuses rather than reporting a clean tree",
        passed=refuses({mypy_census.UNRUNNABLE: ["mypy exited 2"]}),
    )
    check(
        "a real census yields its dirty files",
        passed=drain_queue.dirty_files({"misc::scratch/a.py": ["x"]})
        == frozenset({"scratch/a.py"}),
    )
    # ⚑ An empty census is CLEAN, and that is the one case that may be empty.
    check(
        "an empty census is a clean tree, not an unknown one",
        passed=drain_queue.dirty_files({}) == frozenset(),
    )

    # ⚑ A key without the separator is not a file verdict and must not become one.
    check(
        "a key carrying no relpath contributes no file",
        passed=drain_queue.dirty_files({"summary": ["x"]}) == frozenset(),
    )

    # ── consumers ────────────────────────────────────────────────────────────
    files = drain_queue.population(_ROOT)
    # ⚑ THE NAME MUST BE THE ONE THE IMPORTS SPELL. `sites` resolves what it is given; a
    # bare leaf cannot tell it which package holds the module, and this corpus imports
    # substrate modules dottedly. Passing the leaf found nothing and read as "no
    # consumers" — a fact about the query, not the tree.
    found = drain_queue.consumers_of("substrate.drain_order", files)
    check("a real candidate's consumers are found", passed=bool(found))
    check(
        "and the selftest that imports it is among them",
        passed=any(p.endswith("drain_order_selftest.py") for p in found),
    )

    # ⚑ THE BARE SPELLING MUST RESOLVE — the defect that rendered the whole queue
    # EMPTY. A bare name is queried as a top-level module, so the `from <pkg> import
    # <mod>` branch cannot fire and the answer is a confident zero.
    check(
        "a BARE candidate name finds the same consumers as the dotted one",
        passed=drain_queue.consumers_of("drain_order", files) == found,
    )

    # ── the cost join ────────────────────────────────────────────────────────
    dirty = frozenset({"substrate/drain_order_selftest.py"})
    rows = drain_queue.costs(["substrate.drain_order"], files, dirty)
    check("the candidate yields one cost row", passed=len(rows) == 1)
    check(
        "and its dirty consumer is named as a blocker",
        passed=bool(rows) and "substrate/drain_order_selftest.py" in rows[0].dirty,
    )
    check("so it is not startable", passed=bool(rows) and not rows[0].startable)

    # ⚑ A candidate nothing imports is OMITTED rather than reported as costless.
    check(
        "a name with no consumers is omitted",
        passed=drain_queue.costs(["no_such_module_xyzzy"], files, frozenset()) == [],
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
