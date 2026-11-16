#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the promoted declaration, DIFFERENTIALLY against the origin it promotes from.

⚑⚑⚑ A PROMOTION THAT CHANGES BEHAVIOUR IS A REWRITE WEARING A MOVE'S CLOTHES, and two live
consumers depend on this one — `procstruct` imports `Selftest` and `check_mode_contracts`
imports the module whole. So the cases run BOTH implementations over the same declarations and
assert they agree on every verdict, rather than asserting what I believe the verdict should be.

⚑⚑ THE ORIGIN IS LOADED BY PATH AND READ THROUGH TWO `Protocol`s — one for the module and one
for the RECORD it constructs. `scripts/` is not a package, so an ordinary import cannot reach
it; and a dynamically loaded module is `Any`, so a Protocol returning `object` still leaves
every read off the record untyped. Naming the record's shape too is what gives the comparison
teeth: a misspelled attribute is a type error rather than a silent pass.

⚑ AND THE ONE INTENDED DIVERGENCE IS CASED AS ONE. `self_including` returns a `Cycle` carrying
its denominator where the origin returns a bare list: an empty list over an empty declaration
set and an empty list over the whole fleet are different facts, and the origin cannot tell them
apart. An intended divergence that is not cased reads exactly like an accidental one.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import selftest_decl

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / "scripts" / "climode.py"

Case = tuple[str, bool]

# ⚑ THE DECLARATIONS THE DIFFERENTIAL RUNS OVER: one of each state, plus every contradiction
#   `contract` is meant to catch. A fixture carrying only valid records tests one branch.
_PROBES: tuple[tuple[str, dict[str, object]], ...] = (
    ("a plain suite", {}),
    ("a fixture", {"state": "fixture"}),
    ("a declared absence with a reason", {"state": "none", "why": "a pure data module"}),
    ("⚑ an absence with NO reason", {"state": "none"}),
    ("⚑ a key on a fixture", {"state": "fixture", "key": "somewhere"}),
    ("⚑ requires on an absence", {"state": "none", "why": "r", "requires": ("numpy",)}),
    ("⚑ a tenant on a fixture", {"state": "fixture", "tenant": "sandbox"}),
    ("⚑ runs_roster on an absence", {"state": "none", "why": "r", "runs_roster": True}),
    ("a suite that runs the roster", {"runs_roster": True}),
    ("a suite with a record key", {"key": "parent.py"}),
)


class _Record(Protocol):
    """The origin's Selftest RECORD — named so a read off it is typed, not `Any`."""

    runnable: bool

    def contract(self) -> tuple[bool, str]: ...


class _Origin(Protocol):
    """The origin MODULE surface this differential reads."""

    SELFTEST_STATES: tuple[str, ...]

    def Selftest(self, **kwargs: object) -> _Record: ...  # noqa: N802 — origin's spelling


def _origin() -> _Origin | None:
    """Load the origin by path, or return None when it cannot be reached."""
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_climode", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _mine(kwargs: dict[str, object]) -> selftest_decl.Selftest:
    """Build the promoted record from a probe's keyword set, narrowed at the seam."""
    state = kwargs.get("state", "suite")
    why = kwargs.get("why", "")
    key = kwargs.get("key")
    requires = kwargs.get("requires", ())
    tenant = kwargs.get("tenant")
    runs = kwargs.get("runs_roster", False)
    return selftest_decl.Selftest(
        state=state if isinstance(state, str) else "suite",
        why=why if isinstance(why, str) else "",
        key=key if isinstance(key, str) else None,
        requires=requires if isinstance(requires, tuple) else (),
        tenant=tenant if isinstance(tenant, str) else None,
        runs_roster=bool(runs),
    )


def _state_cases() -> list[Case]:
    """Return the cases pinning that the state is a closed set, refused at construction."""
    try:
        selftest_decl.Selftest(state="sweet")
    except ValueError:
        refused = True
    else:
        refused = False
    return [
        # ⚑ REFUSED, NOT DEFAULTED. A typo'd state becoming `suite` puts a tool with no suite
        #   in the roster, and the runner then reports it SILENT.
        ("an unrecognised state REFUSES at construction", refused),
        (
            "the declared states are the closed set",
            set(selftest_decl.STATES) == {"suite", "fixture", "none"},
        ),
        ("a suite is runnable", selftest_decl.Selftest().runnable),
        ("a fixture is NOT runnable", not selftest_decl.Selftest(state="fixture").runnable),
        # ⚑ AND A DECLARED ABSENCE IS NOT RUNNABLE EITHER — the state the record exists for.
        (
            "a declared absence is NOT runnable",
            not selftest_decl.Selftest(state="none", why="r").runnable,
        ),
    ]


def _contract_cases() -> list[Case]:
    """Return the cases pinning each internal contradiction `contract` refuses."""
    ok_suite, _ = selftest_decl.Selftest().contract()
    bare_none, bare_why = selftest_decl.Selftest(state="none").contract()
    keyed, keyed_why = selftest_decl.Selftest(state="fixture", key="x").contract()
    edged, edged_why = selftest_decl.Selftest(state="none", why="r", runs_roster=True).contract()
    return [
        # ⚑ THE ACCEPT DIRECTION FIRST — a contract that refused everything would satisfy
        #   every case below and make the record unusable.
        ("a plain suite passes its contract", ok_suite),
        ("an absence with no reason is refused", not bare_none),
        ("...naming the shrug it replaces", "constructor around it" in bare_why),
        ("a key on a non-suite is refused", not keyed),
        ("...because it names a report nobody writes", "nobody writes" in keyed_why),
        # ⚑⚑ THE ONE THAT MATTERS MOST: a tool never invoked cannot close a cycle, so the
        #   edge has no referent and the static reader would emit a FALSE finding.
        ("runs_roster on a non-suite is refused", not edged),
        ("...because the edge has no referent", "no referent" in edged_why),
    ]


def _cycle_cases() -> list[Case]:
    """Return the cases pinning the static roster-cycle read and its in-band bound."""
    declared = {
        "a.py": selftest_decl.Selftest(runs_roster=True),
        "b.py": selftest_decl.Selftest(),
        "roster.py": selftest_decl.Selftest(runs_roster=True),
    }
    found = selftest_decl.self_including(declared, "roster.py")
    empty = selftest_decl.self_including({}, "roster.py")
    return [
        ("a self-including tool is named", found.closing == ("a.py",)),
        # ⚑ THE ROSTER TOOL IS EXEMPT BY NAME, since running the roster is what it IS.
        ("the roster tool itself is not named", "roster.py" not in found.closing),
        ("a plain suite is not named", "b.py" not in found.closing),
        ("the denominator travels with the result", found.declared == len(declared)),
        # ⚑⚑ AN EMPTY RESULT OVER NOTHING AND OVER THE FLEET ARE DIFFERENT FACTS, which the
        #   origin's bare list cannot express — the intended divergence.
        ("an empty read reports its own emptiness", empty.declared == 0),
        ("...distinguishably from a clean fleet", found.declared != empty.declared),
        ("the bound names the runtime walk as the uncovered half", "ppid" in found.bound),
    ]


def _failing_cases() -> list[Case]:
    """Return the cases pinning the roster-level contract sweep."""
    declared = {
        "good.py": selftest_decl.Selftest(),
        "bad.py": selftest_decl.Selftest(state="none"),
    }
    bad = selftest_decl.failing(declared)
    clean = selftest_decl.failing({"g": selftest_decl.Selftest()})
    return [
        ("a contradicting declaration is named", len(bad) == 1),
        ("...by tool", bad[0][0] == "bad.py"),
        ("...with its reason", "no `why`" in bad[0][1]),
        ("a clean roster reports none", clean == ()),
    ]


def _differential_cases() -> list[Case]:
    """Run the ORIGIN's `Selftest` beside the promoted one over every probe.

    ⚑⚑⚑ THIS IS WHAT A PROMOTION OWES. Two live consumers import the origin's name, so the
    question is not whether the new record is well-designed but whether it agrees with the one
    they already depend on.
    """
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    same_contract = True
    same_runnable = True
    for _label, kwargs in _PROBES:
        mine = _mine(kwargs)
        theirs = origin.Selftest(**kwargs)
        if mine.contract()[0] != theirs.contract()[0]:
            same_contract = False
        if mine.runnable != theirs.runnable:
            same_runnable = False
    return [
        ("the origin loaded, so this differential means something", True),
        ("the declared state sets agree", set(origin.SELFTEST_STATES) == set(selftest_decl.STATES)),
        ("every probe's contract VERDICT agrees with the origin", same_contract),
        ("every probe's runnable agrees with the origin", same_runnable),
        # ⚑ THE PROBE SET COVERS EVERY REFUSAL BRANCH, or the agreement above is agreement on
        #   the happy path alone.
        (
            "the probe set exercises more than the happy path",
            len(_PROBES) > len(selftest_decl.STATES),
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (
        _state_cases()
        + _contract_cases()
        + _cycle_cases()
        + _failing_cases()
        + _differential_cases()
    )
    bad = [label for label, holds in cases if not holds]
    print(f"selftest_decl: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
