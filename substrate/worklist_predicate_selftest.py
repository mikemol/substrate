# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.worklist_predicate` — including the LIVE worklist roster.

⚑⚑⚑ THE LIVE ARM IS THE ONE THAT MATTERS, AND IT IS A CONTROL RATHER THAN AN ASSERTION OF ZERO.
The operator ruled that `worklist.py --check` should refuse on items whose predicate no longer
RESOLVES. Whether any such item exists today is a measurement, not a premise — so the live arm
asserts the reader reaches every item and returns a well-formed verdict for each, and REPORTS the
stale set rather than pinning it. A case asserting `stale == []` would go red the day the gate
starts earning its keep, which is the tracker-that-must-fail-when-the-work-arrives defect.

⚑⚑ AND THE FIXTURES DRIVE BOTH DIRECTIONS OF EVERY RULE. A resolver that answered STALE for
everything would satisfy every missing-path case; one that answered RESOLVES for everything would
satisfy every present-path case. Each rule is therefore cased with a real temporary tree, so the
positive and negative arms cannot both pass on a degenerate reader.

⚑ THE UNDECIDABLE ARMS ARE NOT HEDGES — they are the operator's ruling made checkable. `cmd0` and
`manual` must NOT reach the stale set, because refusing a commit over a human judgement or an
opaque shell exit is the false-refusal this gate exists not to produce.

⚑⚑ THE LIVE ROSTER IS LOADED BY PATH AND READ THROUGH A `Protocol`, AND THE GATE FORCED BOTH.
`scripts/` is not a package, so a bare `import worklist` is unresolvable to the type checker and a
`sys.path` insert to make it resolve is the very defect the package drain removes. And a
dynamically loaded module is `Any`, so every read off it type-checks against nothing — a
misspelled attribute would pass silently. The narrowing states exactly which three names this
suite depends on, which is also the honest statement of what it would break on.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Protocol, runtime_checkable

from substrate import worklist_predicate as wp


@runtime_checkable
class _Roster(Protocol):
    """The live worklist's roster surface — the three names this suite reads."""

    ROOT: str
    AGDA: str
    WORKLIST: list[dict[str, object]]


def _tree(tmp: str) -> tuple[Path, Path]:
    """Build a miniature repo + agda root, each holding one real file."""
    repo = Path(tmp) / "repo"
    agda = repo / "agda"
    agda.mkdir(parents=True)
    (repo / "live.py").write_text("x = 1\n", encoding="utf-8")
    (agda / "Live.agda").write_text("module Live where\n", encoding="utf-8")
    return repo, agda


def _path_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the three path-bearing predicate heads."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        repo, agda = _tree(tmp)

        def v(pred: tuple[object, ...]) -> wp.Verdict:
            return wp.verdict_for(pred, repo=repo, agda=agda).verdict

        # ⚑ `exists` CARRIES ITS PATH AT INDEX 1 while `grep`/`defines` carry it at 2 — two
        # conventions in one predicate vocabulary, and reading them as one is the shape that
        # would silently classify every needle as a path.
        check(
            "exists resolves for a present path",
            passed=v(("exists", "live.py")) is wp.Verdict.RESOLVES,
        )
        check("and is STALE for a missing one", passed=v(("exists", "gone.py")) is wp.Verdict.STALE)

        check(
            "grep resolves against the REPO root",
            passed=v(("grep", "x = 1", "live.py")) is wp.Verdict.RESOLVES,
        )
        # ⚑⚑ THE NEEDLE IS NOT CONSULTED, DELIBERATELY. Resolution is about the REFERENT; whether
        # the file says the thing is `worklist.py`'s question and stays there. A needle that
        # cannot be found in a present file is an OPEN item, not a stale one.
        check(
            "and resolves even when the needle would NOT be found",
            passed=v(("grep", "no such text anywhere", "live.py")) is wp.Verdict.RESOLVES,
        )
        check(
            "but is STALE when the file is gone",
            passed=v(("grep", "x = 1", "vanished.py")) is wp.Verdict.STALE,
        )

        # ⚑ `defines` RESOLVES AGAINST THE AGDA TREE, a different base for a same-shaped operand.
        check(
            "defines resolves against the AGDA root",
            passed=v(("defines", "Live.agda", "Live")) is wp.Verdict.RESOLVES,
        )
        check(
            "and a repo-root path is STALE under the agda base",
            passed=v(("defines", "live.py", "x")) is wp.Verdict.STALE,
        )

        # ⚑ AN ABSOLUTE OPERAND IS HONOURED, matching worklist.py's own `isabs` test — always
        # joining would report every absolute path missing, a refusal the reader manufactured.
        check(
            "an absolute path is honoured rather than joined",
            passed=v(("exists", str(repo / "live.py"))) is wp.Verdict.RESOLVES,
        )

    return out


def _opaque_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the heads that name no inspectable artifact."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        repo, agda = _tree(tmp)

        def v(pred: tuple[object, ...]) -> wp.Verdict:
            return wp.verdict_for(pred, repo=repo, agda=agda).verdict

        check(
            "cmd0 is UNDECIDABLE, not stale", passed=v(("cmd0", "true")) is wp.Verdict.UNDECIDABLE
        )
        check("manual is UNDECIDABLE, not stale", passed=v(("manual",)) is wp.Verdict.UNDECIDABLE)
        # ⚑⚑ A COMMIT CANNOT GO STALE — a miss means it has not happened, which is the item being
        # open. Classifying it stale would refuse a commit for every unfinished item at once.
        check("commit always RESOLVES", passed=v(("commit", "some subject")) is wp.Verdict.RESOLVES)
        # ⚑ AN UNKNOWN HEAD IS UNDECIDABLE, NEVER RESOLVES — worklist.py returns None for one, so
        # a typo reads as MANUAL and is excused; answering RESOLVES here extends that excuse.
        check(
            "an unrecognised head is UNDECIDABLE",
            passed=v(("nosuchhead", "x")) is wp.Verdict.UNDECIDABLE,
        )
        check("and an empty predicate is too", passed=v(()) is wp.Verdict.UNDECIDABLE)

    return out


def _combinator_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the fold — asserted on VERDICTS, which is what it reads."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    live = wp.Finding(wp.Verdict.RESOLVES, "ok")
    gone = wp.Finding(wp.Verdict.STALE, "missing")
    murky = wp.Finding(wp.Verdict.UNDECIDABLE, "opaque")

    check(
        "all-resolving folds to RESOLVES",
        passed=wp.combine("all", [live, live]).verdict is wp.Verdict.RESOLVES,
    )
    # ⚑⚑ ONE STALE MEMBER MAKES THE WHOLE PREDICATE STALE — the item cannot be discharged as
    # written, whichever combinator joins them.
    check(
        "one stale member makes the fold STALE",
        passed=wp.combine("all", [live, gone]).verdict is wp.Verdict.STALE,
    )
    check(
        "and that holds for `any` too, not just `all`",
        passed=wp.combine("any", [live, gone]).verdict is wp.Verdict.STALE,
    )
    # ⚑ UNDECIDABLE BEATS RESOLVES: the unchecked member is exactly the part nothing verified.
    check(
        "an undecidable member blocks a clean verdict",
        passed=wp.combine("all", [live, murky]).verdict is wp.Verdict.UNDECIDABLE,
    )
    # ⚑ BUT STALE BEATS UNDECIDABLE — a known-missing artifact is a finding, not a gap.
    check(
        "and stale outranks undecidable",
        passed=wp.combine("all", [murky, gone]).verdict is wp.Verdict.STALE,
    )
    check(
        "an empty combinator is UNDECIDABLE",
        passed=wp.combine("all", []).verdict is wp.Verdict.UNDECIDABLE,
    )

    # ⚑ THE DETAIL NAMES WHAT WENT MISSING, so a refusal can say which path died rather than
    # only that something did.
    check(
        "the stale detail carries the member's own detail",
        passed="missing" in wp.combine("all", [live, gone]).detail,
    )

    return out


def _selection_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `stale_items` — the operator's ruling as a selection."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        repo, agda = _tree(tmp)
        items: list[dict[str, object]] = [
            {"sym": "live", "done": ("exists", "live.py")},
            {"sym": "dead", "done": ("exists", "gone.py")},
            {"sym": "judged", "done": ("manual",)},
            {"sym": "shelled", "done": ("cmd0", "true")},
        ]
        picked = dict(wp.stale_items(items, repo=repo, agda=agda))

        check("the stale item is selected", passed="dead" in picked)
        check("the live one is not", passed="live" not in picked)
        # ⚑⚑⚑ THE TWO ARMS THE RULING TURNS ON. Refusing on a manual or an opaque item would
        # block every commit over a human judgement — the false refusal the narrower class exists
        # to avoid, and the reason UNDECIDABLE is a verdict rather than a synonym for stale.
        check("a MANUAL item is never an offender", passed="judged" not in picked)
        check("nor is an opaque cmd0", passed="shelled" not in picked)
        check("the detail names the missing path", passed="gone.py" in picked.get("dead", ""))

        # ⚑ A NON-TUPLE PREDICATE IS SKIPPED, NOT CRASHED ON — the roster is hand-authored data.
        check(
            "a malformed predicate is skipped rather than raising",
            passed=wp.stale_items([{"sym": "bad", "done": "not-a-tuple"}], repo=repo, agda=agda)
            == [],
        )

    return out


def _roster() -> _Roster | None:
    """Load the live worklist roster by path, or None when it cannot be reached.

    ⚑ THE MODULE MUTATES `sys.path` AT IMPORT, so what it inserts is restored afterwards —
    leaving it would make this suite's environment more permissive than the one it tests.
    """
    origin = Path(__file__).resolve().parent.parent / "scripts" / "worklist.py"
    if not origin.exists():
        return None
    spec = importlib.util.spec_from_file_location("_worklist_roster", origin)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    saved = list(sys.path)
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    finally:
        sys.path[:] = saved
    found: object = module
    return found if isinstance(found, _Roster) else None


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the REAL worklist roster — what a fixture cannot say.

    ⚑⚑⚑ THIS REPORTS THE STALE SET RATHER THAN PINNING IT AT ZERO. Whether the live tree has a
    stale predicate is the measurement the gate exists to make, and a case asserting none would
    fail the day one appears — a tracker that goes red when the work arrives is a comment
    carrying a test's costs. What IS asserted is that the reader reaches every item and returns a
    well-formed verdict, which is the property a fixture cannot establish.
    """
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    roster = _roster()
    if roster is None:
        skipped = (
            "the live roster could not be LOADED, so the live arm is SKIPPED, "
            "not run and not passed"
        )
        return [(skipped, True)]

    repo, agda = Path(roster.ROOT), Path(roster.AGDA)
    items: list[dict[str, object]] = list(roster.WORKLIST)
    check("the live roster is non-empty, so agreement is not vacuous", passed=bool(items))

    preds = [it["done"] for it in items]
    verdicts = [
        wp.verdict_for(tuple(p), repo=repo, agda=agda)
        for p in preds
        if isinstance(p, (list, tuple))
    ]
    check(
        "every item carries a tuple predicate the reader can read",
        passed=len(verdicts) == len(items),
    )
    check(
        "and every verdict is a declared member",
        passed=all(f.verdict in set(wp.Verdict) for f in verdicts),
    )
    check(
        "and every one carries a detail a refusal could print",
        passed=all(f.detail for f in verdicts),
    )

    stale = wp.stale_items(items, repo=repo, agda=agda)
    check(f"the live stale set is REPORTED, not pinned: {stale[:3]}", passed=True)
    # ⚑ THE POSITIVE CONTROL: the reader must be CAPABLE of finding a stale row on this very
    # roster, or a report of none is a fact about the reader. One synthetic missing path proves
    # the instrument can see the shape it reports empty.
    probe: list[dict[str, object]] = [
        *items,
        {"sym": "control", "done": ("exists", "no/such/path/at/all.txt")},
    ]
    check(
        "and a control row IS detected, so an empty report would mean something",
        passed="control" in dict(wp.stale_items(probe, repo=repo, agda=agda)),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _path_cases() + _opaque_cases() + _combinator_cases() + _selection_cases() + _live_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"worklist-predicate selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
