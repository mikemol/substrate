# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.drain_ranking` — which dirty file to clean first.

⚑⚑⚑ THE ORDERING IS THE CLAIM, and it is deliberately NOT a score. A ranking that folded
sites-released and findings-carried into one number would need a weighting nobody can justify,
and would hide which half moved when the order changed. The cases assert that RELEASE leads and
cost only breaks ties — so a monolith carrying one site can never outrank a cheap file carrying
several, however many findings separate them.

⚑⚑ AND AN UNMEASURED FILE IS OMITTED, NOT DEFAULTED. Assuming it clean puts an unmeasured file
at the head of a work queue; assuming it dirty invents a finding count. Both directions are
pinned, because the omission is the one behaviour a caller could mistake for a bug.

⚑ THE FIXTURES ARE CONSTRUCTED VERDICTS. Ranking the live tree would make these cases a
measurement — slow, and reordering whenever anyone edits an unrelated file.
"""

from __future__ import annotations

from substrate import drain_ranking, editable


def _dirty(path: str, findings: int) -> editable.Verdict:
    """Build a verdict for a file the gate would refuse."""
    return editable.Verdict(path, editable.DIRTY, findings)


def _clean(path: str) -> editable.Verdict:
    """Build a verdict for a file the gate would accept."""
    return editable.Verdict(path, editable.CLEAN, 0)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── release leads the ordering ───────────────────────────────────────────
    # ⚑ THE MONOLITH LOSES. `big.py` carries three hundred findings and one site; `small.py`
    # carries ten and four. Ranking by cost would invert this and send the operator at the
    # work least likely to finish.
    sites = {"big.py": 1, "small.py": 4}
    verdicts = {"big.py": _dirty("big.py", 300), "small.py": _dirty("small.py", 10)}
    ranked = drain_ranking.rank(sites, verdicts)
    check(
        "the file releasing more sites ranks first",
        passed=[b.path for b in ranked] == ["small.py", "big.py"],
    )

    # ── cost breaks a tie, and only a tie ───────────────────────────────────
    tie_sites = {"cheap.py": 2, "dear.py": 2}
    tie_verdicts = {"cheap.py": _dirty("cheap.py", 3), "dear.py": _dirty("dear.py", 90)}
    tied = drain_ranking.rank(tie_sites, tie_verdicts)
    check(
        "equal release breaks toward fewer findings",
        passed=[b.path for b in tied] == ["cheap.py", "dear.py"],
    )

    # ⚑ AND PATH BREAKS THE REMAINING TIE, so two runs over an unchanged tree produce the
    # same report and a diff shows real movement rather than dict ordering.
    same = {"b.py": 1, "a.py": 1}
    same_v = {"b.py": _dirty("b.py", 5), "a.py": _dirty("a.py", 5)}
    check(
        "a full tie breaks on path, so the ranking is stable",
        passed=[b.path for b in drain_ranking.rank(same, same_v)] == ["a.py", "b.py"],
    )

    # ── only blocked files are ranked ───────────────────────────────────────
    # ⚑ A CLEAN FILE IS NOT A BLOCKER. Including it would pad the queue with work already
    # available, which is the opposite of what the ranking is for.
    mixed = {"dirty.py": 2, "clean.py": 9}
    mixed_v = {"dirty.py": _dirty("dirty.py", 4), "clean.py": _clean("clean.py")}
    check(
        "a clean file is not ranked as a blocker",
        passed=[b.path for b in drain_ranking.rank(mixed, mixed_v)] == ["dirty.py"],
    )

    # ⚑ AND AN UNKNOWN FILE IS ALSO NOT EDITABLE, so it IS a blocker — the verdict type
    # decides, not a second rule here.
    unknown_v = {"u.py": editable.Verdict("u.py", editable.UNKNOWN, 0, "no mypy")}
    check(
        "an unmeasurable file counts as blocked",
        passed=len(drain_ranking.rank({"u.py": 1}, unknown_v)) == 1,
    )

    # ── a file with no verdict is omitted, not defaulted ───────────────────
    check(
        "a file with no verdict is omitted",
        passed=drain_ranking.rank({"never_measured.py": 7}, {}) == [],
    )

    # ── released_by sums a prefix ───────────────────────────────────────────
    check(
        "released_by sums the top of the ranking", passed=drain_ranking.released_by(ranked, 1) == 4
    )  # noqa: PLR2004
    check(
        "and the whole ranking sums to every blocked site",
        passed=drain_ranking.released_by(ranked, len(ranked)) == 5,
    )  # noqa: PLR2004

    # ── the ratio is carried but not used to order ─────────────────────────
    # ⚑ IF THE RATIO ORDERED, `dear.py` (2/90) and `cheap.py` (2/3) would separate on it —
    # they tie on release and break on cost instead. Asserting the ratio EXISTS without
    # asserting the order uses it is the point.
    check(
        "the trade ratio is reported",
        passed=tied[0].release_per_finding > tied[1].release_per_finding,
    )
    # ⚑ AND A ZERO-FINDING ROW DOES NOT DIVIDE BY ZERO — it cannot arise from `rank`, but
    # the property is on the dataclass and a caller may build one.
    check(
        "a zero-finding row yields its site count rather than raising",
        passed=drain_ranking.Blocked("x.py", 3, 0).release_per_finding == 3,
    )  # noqa: PLR2004

    # ── rendering states the concentration ──────────────────────────────────
    text = drain_ranking.render(ranked)
    check("the rendering names a file", passed="small.py" in text)
    # ⚑ THE HEAD'S SHARE IS THE PLANNING NUMBER — a long tail means the ranking cannot
    # concentrate the work, and an operator should learn that before starting.
    check("and reports what the top of the ranking would release", passed="top" in text)

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
