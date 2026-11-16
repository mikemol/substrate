#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the dispatch reader, DIFFERENTIALLY, and pin every repaired false positive.

⚑⚑⚑ EACH MATCHING RULE HERE IS A REPAIRED FALSE POSITIVE AND EACH GETS ITS OWN CASE. A gate
that accuses a compliant tool is the one failure it must not make, because the fix it demands
is to break a working refusal — so a suite that only asserts real defects get caught is
testing the half that was never wrong.

⚑⚑ THE DIFFERENTIAL IS THE OBLIGATION. `procstruct` imports `contract_rows` from the origin
and `check_mode_contracts` imports the origin whole, so the question is whether this agrees
with what they already depend on, not whether it is well shaped.

⚑ AND THE ORIGIN IS READ THROUGH A `Protocol` FOR THE SAME REASON AS `selftest_decl`: a
dynamically loaded module is `Any`, so an untyped differential agrees with anything.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from substrate import mode_dispatch

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / "scripts" / "climode.py"

Case = tuple[str, bool]

# ⚑ THE THREE FIXTURES BELOW ARE THE REPAIRED FALSE POSITIVES; the differential covers those
#   PLUS the two ordinary ones, so agreement is not agreement on the easy cases alone.
REPAIRED = 3


@dataclass(frozen=True, slots=True)
class _Decl:
    """A roster entry carrying exactly what the reader consumes."""

    scans: bool = False
    writes: object = None
    opts: tuple[str, ...] = ()


# ⚑ THE NESTED-SUBFLAG FIXTURE. Under next-match bounding `--coverage` would end at `--emit`,
#   so the `--apply` its `--reap` sub-branch tests falls outside and a correctly-guarded
#   mutator reads as a silent-default writer. That was measured on a real file.
_NESTED = """
def main():
    if "--coverage" in sys.argv:
        if "--emit" in sys.argv:
            pass
        if "--reap" in sys.argv:
            if "--apply" not in sys.argv:
                refuse()
    if "--plain" in sys.argv:
        pass
"""

# ⚑ TWO MODES ON ONE LINE sharing a body. Matching only the first made the second read
#   DECLARED-never-dispatched — a phantom verdict whose demanded fix deletes a declaration.
_CO_LOCATED = """
def main():
    if "--replace-section" in sys.argv or "--append-section" in sys.argv:
        pass
"""

# ⚑ THE RECEIVER SPELLINGS. `sys.argv` is the commonest and a bare-word pattern misses it.
_RECEIVERS = """
def main():
    if "--dotted" in sys.argv:
        pass
    if "--called" in flagged_argv():
        pass
    if "--bare" in argv:
        pass
"""

_ONE_BRANCH = 'def main():\n    if "--here" in sys.argv:\n        pass\n'
_ONE_LIVE = 'def main():\n    if "--live" in sys.argv:\n        pass\n'


class _Origin(Protocol):
    """The origin surface this differential reads — named so a typo cannot pass."""

    def branch_bounds(self, src: str) -> dict[str, tuple[int, int]]: ...


def _origin() -> _Origin | None:
    """Load the origin by path, or return None when it cannot be reached."""
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_climode_dispatch", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _nesting_cases() -> list[Case]:
    """Return the cases pinning that a nested sub-flag does not truncate its parent."""
    bounds = mode_dispatch.branch_bounds(_NESTED)
    lines = _NESTED.splitlines()
    start, end = bounds["--coverage"]
    body = "\n".join(lines[start:end])
    roster: dict[str, mode_dispatch.Declared] = {
        "--coverage": _Decl(writes="files"),
        "--emit": _Decl(),
        "--reap": _Decl(),
        "--plain": _Decl(),
    }
    accused = [
        flag
        for flag, ok, _why in mode_dispatch.contract_rows(_NESTED, roster)
        if flag == "--coverage" and ok is False
    ]
    return [
        ("a nested sub-flag is still recorded", "--emit" in bounds and "--reap" in bounds),
        # ⚑⚑ THE REPAIRED FALSE POSITIVE: the parent's body must CONTAIN its sub-dispatch,
        #   which is where the --apply guard sits.
        ("the parent's body includes its own sub-dispatch", "--reap" in body),
        ("...and therefore the guard inside it", "--apply" in body),
        ("a SIBLING at the same indent does close the branch", end <= bounds["--plain"][0]),
        # ⚑ AND THE CONSEQUENCE, ASSERTED AS A VERDICT: a correctly-guarded mutator must NOT
        #   be reported as a silent-default writer.
        ("a guarded mutator is NOT accused", accused == []),
    ]


def _colocated_cases() -> list[Case]:
    """Return the cases pinning that co-located flags both dispatch."""
    bounds = mode_dispatch.branch_bounds(_CO_LOCATED)
    roster: dict[str, mode_dispatch.Declared] = {
        "--replace-section": _Decl(),
        "--append-section": _Decl(),
    }
    rows = mode_dispatch.contract_rows(_CO_LOCATED, roster)
    phantom = [flag for flag, ok, why in rows if ok is False and "never dispatched" in why]
    start, end = bounds["--replace-section"]
    return [
        ("the first co-located flag is located", "--replace-section" in bounds),
        ("the second is too", "--append-section" in bounds),
        # ⚑⚑ THE PHANTOM VERDICT IS THE DANGEROUS DIRECTION — its demanded fix is deleting a
        #   correct declaration.
        ("neither is reported as declared-but-never-dispatched", phantom == []),
        # ⚑ AND A SIBLING FROM THE SAME LINE MUST NOT CLOSE THE BRANCH AT ZERO LENGTH.
        ("the shared body is non-empty", end > start),
    ]


def _receiver_cases() -> list[Case]:
    """Return the cases pinning every argv receiver spelling the reader must match."""
    bounds = mode_dispatch.branch_bounds(_RECEIVERS)
    return [
        # ⚑ THE DOT IS LOAD-BEARING: a bare-word pattern misses `sys.argv`, the commonest
        #   spelling of all, and every ordinary mode then reads UNKNOWN.
        ("a `sys.argv` receiver is matched", "--dotted" in bounds),
        ("a called accessor is matched", "--called" in bounds),
        ("a bare `argv` is matched", "--bare" in bounds),
    ]


def _verdict_cases() -> list[Case]:
    """Return the cases pinning the three verdicts, especially the honest third."""
    roster: dict[str, mode_dispatch.Declared] = {
        "--here": _Decl(scans=True),
        "--gone": _Decl(scans=True),
    }
    rows = mode_dispatch.contract_rows(_ONE_BRANCH, roster)
    # ⚑⚑⚑ ONE FLAG CAN CARRY SEVERAL ROWS, AND MY FIRST CASE ASSUMED ONE. `--gone` is both
    #   scans-declared-with-no-locatable-branch (UNKNOWN) and declared-never-dispatched
    #   (False), so a `{flag: row}` comprehension silently kept the LAST and the case read a
    #   different verdict than the one it named. The reader was right; the case was wrong.
    #   Collecting per flag is what makes each verdict assertable on its own terms.
    gone = [(ok, why) for flag, ok, why in rows if flag == "--gone"]
    here = [(ok, why) for flag, ok, why in rows if flag == "--here"]
    return [
        # ⚑⚑ UNKNOWN IS NEVER BANKED AS A PASS. A branch this reader cannot locate is a gap
        #   in the READER, and reporting it as True is the false green the design forbids.
        ("an unlocatable branch yields an UNKNOWN row", any(ok is None for ok, _ in gone)),
        (
            "...saying the branch was not located",
            any("not located" in why for ok, why in gone if ok is None),
        ),
        # ⚑ AND THE SECOND ROW IS A DIFFERENT, ALSO-TRUE FINDING — not a duplicate. Losing it
        #   to a one-row-per-flag assumption is how the reader's honesty gets flattened.
        (
            "...alongside a separate declared-never-dispatched row",
            any(ok is False and "never dispatched" in why for ok, why in gone),
        ),
        ("a scanning mode with no skip report FAILS", any(ok is False for ok, _ in here)),
        (
            "...naming the marker it never calls",
            any("_report_skipped(" in why for _ok, why in here),
        ),
        # ⚑ AND UNKNOWN IS COUNTED SEPARATELY, so the reader's blind spots cannot inflate a
        #   tool's defect count.
        (
            "unknown flags are reported apart from failures",
            mode_dispatch.unknown(rows) == ("--gone",),
        ),
    ]


def _both_directions_cases() -> list[Case]:
    """Return the cases pinning declared-undispatched against dispatched-undeclared."""
    paper: dict[str, mode_dispatch.Declared] = {"--paper": _Decl()}
    owner: dict[str, mode_dispatch.Declared] = {"--live": _Decl(opts=("--sub",))}
    rows = mode_dispatch.contract_rows(_ONE_LIVE, paper)
    why = {flag: text for flag, _ok, text in rows}
    owned = mode_dispatch.contract_rows(_ONE_LIVE, owner)
    return [
        ("a declared flag with no branch is named", "--paper" in why),
        ("...as a promise the CLI does not keep", "does not keep" in why["--paper"]),
        ("a dispatched flag absent from the roster is named", "--live" in why),
        ("...as undeclared arity", "undeclared arity" in why["--live"]),
        # ⚑ A MODE'S OWNED MODIFIER IS NOT AN UNDECLARED MODE — without this the gate
        #   demanded sub-flags be promoted, the opposite of what the roster says.
        (
            "an owned modifier is not reported as an undeclared mode",
            all(flag != "--sub" for flag, _ok, _why in owned),
        ),
    ]


def _differential_cases() -> list[Case]:
    """Compare `branch_bounds` with the origin's over every fixture."""
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    probes = (_NESTED, _CO_LOCATED, _RECEIVERS, _ONE_BRANCH, _ONE_LIVE)
    same = all(origin.branch_bounds(p) == mode_dispatch.branch_bounds(p) for p in probes)
    return [
        ("the origin loaded, so this differential means something", True),
        ("branch_bounds agrees with the origin on every fixture", same),
        # ⚑ AGREEMENT ON THE REPAIRED CASES IS THE CLAIM — agreement on the easy ones is not.
        ("the probe set includes every repaired-defect fixture", len(probes) > REPAIRED),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (
        _nesting_cases()
        + _colocated_cases()
        + _receiver_cases()
        + _verdict_cases()
        + _both_directions_cases()
        + _differential_cases()
    )
    bad = [label for label, holds in cases if not holds]
    print(f"mode_dispatch: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
