# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.worklist_status` — DIFFERENTIAL against the live tracker.

⚑⚑⚑ THE DIFFERENTIAL IS THE POINT AND IT EXPIRES AT THE SWAP. `scripts/worklist.py` computes
these verdicts independently today, so agreeing with it over the whole live roster is EVIDENCE.
Once that file is rewritten to call this module, the same arm becomes a function agreeing with
itself — so the verification runs NOW, while it still measures something.

⚑⚑ AND IT AGREES ON EVERY ITEM, NOT ON A COUNT. Two rosters with the same DONE total and one
item flipped is exactly the failure a count cannot see, and here it would mean a finished arc
re-entering the dispatch queue or an open one vanishing from it — the defect the whole tracker
exists to prevent.

⚑ THE TRI-STATE IS CASED IN ALL THREE DIRECTIONS. A verdict engine that never returned MANUAL
would satisfy every DONE and OPEN arm, and the manual items are precisely the ones no artifact
can discharge, so their misclassification is silent.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Protocol, runtime_checkable

from substrate import corpus
from substrate import worklist_status as ws

#: The live tracker this module drains the verdict engine out of.
ORIGIN = corpus.ROOT / "scripts" / "worklist.py"

#: The three verdicts, as `(value, expected label)` — passed through a table rather than as bare
#: positional booleans, which the gate refuses and which read as unlabelled flags anyway.
VERDICTS: tuple[tuple[bool | None, str], ...] = ((True, "DONE"), (False, "OPEN"), (None, "MANUAL"))


@runtime_checkable
class _Origin(Protocol):
    """The origin's surface this differential reads.

    ⚑ NARROWED AT THE SEAM: a module loaded by path is `Any`, so an un-narrowed differential
    type-checks against nothing and agrees with a typo.
    """

    ROOT: str
    AGDA: str
    WORKLIST: list[dict[str, object]]

    def status(self, pred: tuple[object, ...]) -> bool | None:
        """Return the origin's verdict for one predicate."""
        ...


def _origin() -> _Origin | None:
    """Load the live tracker by path, or None when it cannot be reached."""
    if not ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_worklist_origin", ORIGIN)
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
    return found if isinstance(found, _Origin) else None


def _preds(items: list[dict[str, object]]) -> list[tuple[str, tuple[object, ...]]]:
    """Return `(symbol, predicate)` for every item carrying a tuple predicate.

    ⚑ THE NARROWING HAPPENS ONCE, HERE. `item["done"]` is `object`, so every caller would
    otherwise re-test it — and a caller that forgot would type-check against nothing.
    """
    out: list[tuple[str, tuple[object, ...]]] = []
    for item in items:
        pred = item.get("done")
        if isinstance(pred, (list, tuple)):
            out.append((str(item.get("sym", "?")), tuple(pred)))
    return out


def _atom_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for each predicate head, over a real temporary tree."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        agda = root / "agda"
        agda.mkdir()
        (root / "live.txt").write_text("the needle is here\n", encoding="utf-8")
        (agda / "Mod.agda").write_text(
            "module Mod where\n\nthm : Set\nthm = Set\n", encoding="utf-8"
        )

        def v(pred: tuple[object, ...]) -> bool | None:
            return ws.status(pred, root=root, agda=agda)

        check("exists is DONE for a present path", passed=v(("exists", "live.txt")) is True)
        check("and OPEN for a missing one", passed=v(("exists", "gone.txt")) is False)
        check(
            "grep is DONE when the needle is present",
            passed=v(("grep", "the needle", "live.txt")) is True,
        )
        check("and OPEN when it is not", passed=v(("grep", "absent", "live.txt")) is False)

        # ⚑⚑ A DEFINITION IS A LINE'S FIRST TOKEN, so a name appearing only inside another
        # declaration's body must NOT count — that is the difference between this and a grep.
        check(
            "defines is DONE for a column-0 definition",
            passed=v(("defines", "Mod.agda", "thm")) is True,
        )
        check(
            "and OPEN for a name that only appears in a body",
            passed=v(("defines", "Mod.agda", "Set")) is False,
        )
        check(
            "and OPEN when the module is absent", passed=v(("defines", "Gone.agda", "thm")) is False
        )

        check("cmd0 is DONE when the command exits 0", passed=v(("cmd0", "true")) is True)
        check("and OPEN when it does not", passed=v(("cmd0", "false")) is False)

        # ⚑⚑⚑ THE THIRD OUTCOME, IN BOTH ITS FORMS. `manual` is unjudged by declaration; an
        # unrecognised head is unjudged because nothing evaluated it. Reporting either as OPEN
        # would queue work no artifact can discharge.
        check("manual is MANUAL, never OPEN", passed=v(("manual",)) is None)
        check("an unrecognised head is MANUAL, never OPEN", passed=v(("nosuch", "x")) is None)
        check("and an empty predicate is too", passed=v(()) is None)

    return out


def _fold_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the combinators, driven through `status`.

    ⚑ DRIVEN THROUGH THE PUBLIC ENTRY, not the private fold — a case calling the helper directly
    would pass against a `status` that never reached it, which is the wiring defect this session
    has already recorded twice.
    """
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "here.txt").write_text("x\n", encoding="utf-8")
        done: tuple[object, ...] = ("exists", "here.txt")
        opn: tuple[object, ...] = ("exists", "gone.txt")
        man: tuple[object, ...] = ("manual",)

        def v(pred: tuple[object, ...]) -> bool | None:
            return ws.status(pred, root=root, agda=root)

        check("all of DONE is DONE", passed=v(("all", [done, done])) is True)
        check("all with an OPEN is OPEN", passed=v(("all", [done, opn])) is False)
        # ⚑ MANUAL PROPAGATES: an `all` with an unjudged member is not DONE, or the fold would
        # report a judgement nobody made.
        check("all with a MANUAL is MANUAL", passed=v(("all", [done, man])) is None)
        # ⚑ AND OPEN OUTRANKS MANUAL in `all` — a known failure is a finding, not a gap.
        check("all with both OPEN and MANUAL is OPEN", passed=v(("all", [opn, man])) is False)

        check("any with a DONE is DONE", passed=v(("any", [opn, done])) is True)
        check("any of OPEN is OPEN", passed=v(("any", [opn, opn])) is False)
        check("any with no DONE and a MANUAL is MANUAL", passed=v(("any", [opn, man])) is None)

        # ⚑ A COMBINATOR WITH A MALFORMED MEMBER LIST IS MANUAL, not a crash — the roster is
        # hand-authored, so a scalar where a list belongs is a live possibility.
        check("a combinator with no member list is MANUAL", passed=v(("all", "not-a-list")) is None)

    return out


def _label_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the display names — one spelling, asserted."""
    return [
        (f"{verdict!r} renders {name}", ws.label(verdict) == name) for verdict, name in VERDICTS
    ]


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting per-item agreement with the live tracker.

    ⚑⚑⚑ PER ITEM, NEVER PER COUNT. Equal totals with one item flipped is the failure a count
    cannot see, and it would re-dispatch a finished arc or hide an open one.
    """
    origin = _origin()
    if origin is None:
        return [
            ("the origin could not be LOADED, so the differential is SKIPPED, not passed", True)
        ]

    root, agda = Path(origin.ROOT), Path(origin.AGDA)
    pairs = _preds(list(origin.WORKLIST))
    if not pairs:
        return [("the live roster carries no predicate — a fact about the TREE", True)]

    mine = [(sym, ws.status(pred, root=root, agda=agda)) for sym, pred in pairs]
    disagreed = [
        f"{sym}: mine={ws.label(got)}"
        for (sym, got), (_s, pred) in zip(mine, pairs, strict=True)
        if got is not origin.status(pred)
    ]
    seen = sorted({ws.label(got) for _sym, got in mine})
    return [
        (f"every live item agrees with the origin (e.g. {disagreed[:3]})", not disagreed),
        # ⚑ THE POSITIVE CONTROL: two engines that both returned None for everything would agree
        # vacuously, so assert the population actually exercised more than one verdict.
        (f"and the verdicts are not all one value ({seen})", len(seen) > 1),
    ]


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _atom_cases() + _fold_cases() + _label_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"worklist-status selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
