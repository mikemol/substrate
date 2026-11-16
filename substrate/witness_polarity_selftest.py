#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Pin the polarity guard, including the arm the origin does not have.

⚑⚑⚑ THE DIFFERENTIAL CASES ARE THE ONES THAT MATTER, AND THEY RUN AGAINST THE LIVE ORIGIN.
A replacement verified only against my own fixtures proves the module agrees with itself.
Three cases drive `.claude/agents/findings.py --register` on a throwaway key and assert the
ORIGIN refuses for the same reason this module does — so fidelity is checked by a program
rather than by my reading of its comments.

⚑⚑ AND ONE CASE ASSERTS A DELIBERATE DIVERGENCE. The `mode:` arm is the whole reason this
module exists: the origin registers a wrong-polarity `mode:` witness CLEAN, and this module
refuses it. That case would fail if someone "fixed" the drift by making this module match
the origin, which is exactly the regression a differential suite otherwise invites.

⚑ THE NEGATIVE CONTROLS CARRY AS MUCH WEIGHT AS THE CASES. A probe that refused everything
would pass every refusal assertion, so a right-polarity command in each probed kind is
asserted to return None — and an UNPROBED kind is asserted to return None *while*
`probes()` reports False, because those two Nones mean different things.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from substrate import witness_polarity as wp

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / ".claude" / "agents" / "findings.py"

_TRUE = ["true"]
_FALSE = ["false"]
_ABSENT = ["substrate-no-such-command-at-all"]

Case = tuple[str, bool]


def _polarity_cases(root: str) -> list[Case]:
    """Return the cases asserting each probed kind's required exit polarity."""
    return [
        # ── refuses: the polarity is NON-ZERO ────────────────────────────────────────
        (
            "a refuses: command that exits 0 is REFUSED",
            wp.probe(_TRUE, "refuses", root) is not None,
        ),
        (
            "the refuses: refusal names the census alternative",
            "CENSUS" in (wp.probe(_TRUE, "refuses", root) or ""),
        ),
        (
            "a refuses: command that exits non-zero PASSES",
            wp.probe(_FALSE, "refuses", root) is None,
        ),
        # ── selftest: the polarity is ZERO ───────────────────────────────────────────
        (
            "a selftest: command that exits non-zero is REFUSED",
            wp.probe(_FALSE, "selftest", root) is not None,
        ),
        ("a selftest: command that exits 0 PASSES", wp.probe(_TRUE, "selftest", root) is None),
        # ── mode: THE ARM THE ORIGIN LACKS ───────────────────────────────────────────
        # ⚑ `_mode_undocumented` returns 0 on exactly one path — DOCUMENTED — so rc 0 at
        #   filing time contradicts a finding claiming the flag is undocumented.
        (
            "a mode: witness reporting DOCUMENTED is REFUSED",
            wp.probe(_TRUE, "mode", root) is not None,
        ),
        (
            "the mode: refusal names the redirect case",
            "REDIRECT" in (wp.probe(_TRUE, "mode", root) or ""),
        ),
        ("a mode: witness reporting UNDOCUMENTED PASSES", wp.probe(_FALSE, "mode", root) is None),
    ]


def _coverage_cases(root: str) -> list[Case]:
    """Return the cases asserting WHICH kinds carry a polarity claim at all.

    ⚑ BOTH HALVES ARE ASSERTED FOR AN UNPROBED KIND. `probe` returning None for `standing`
    is correct AND uninformative; only `probes()` distinguishes it from a real pass, so a
    suite checking one without the other would let the two Nones silently merge.
    """
    absent = [
        (
            f"an absent command is REFUSED under {kind}:",
            "DID NOT RUN" in (wp.probe(_ABSENT, kind, root) or ""),
        )
        for kind in wp.PROBED
    ]
    unprobed = [
        (
            f"{kind} is not probed at all",
            wp.probe(_FALSE, kind, root) is None and not wp.probes(kind),
        )
        for kind in ("standing", "unwitnessed")
    ]
    declared = [(f"probes() reports {kind}: as probed", wp.probes(kind)) for kind in wp.PROBED]
    return absent + unprobed + declared


def _evidence_cases() -> list[Case]:
    """Return the cases pinning which line gets QUOTED beside a verdict."""
    return [
        (
            "evidence prefers a refusal line over the last line",
            wp.evidence("error: the guard fired\nsee --help for usage") == "error: the guard fired",
        ),
        (
            "evidence flags a fallback rather than passing it off as the guard",
            wp.evidence("just some output").startswith("(no refusal line found"),
        ),
        (
            "evidence says so when there is no output at all",
            "exit code is the whole evidence" in wp.evidence(""),
        ),
        ("an absent command yields rc=None", wp.run(_ABSENT, str(ROOT)).rc is None),
        ("a failing command yields rc!=0, not None", wp.run(_FALSE, str(ROOT)).rc == 1),
    ]


def _origin_register(key: str, kind: str) -> tuple[int, str]:
    """Drive the ORIGIN's --register (no --apply) and return (rc, output)."""
    p = subprocess.run(  # noqa: S603
        [sys.executable, str(LEDGER), "--register", key, kind, "a differential probe"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def _differential() -> list[Case]:
    """Return cases asserting agreement — and one deliberate divergence — with the origin.

    ⚑ THESE SHELL OUT TO THE LIVE LEDGER. A fixture would only prove this module agrees
    with a copy of the origin's comments rather than with the origin itself.
    """
    if not LEDGER.exists():
        return [("the origin ledger is present to difference against", False)]

    key = "wp-differential-probe-never-registered"
    root = str(ROOT)

    rc_refuses, msg_refuses = _origin_register(key, "refuses:true")
    rc_selftest, _ = _origin_register(key, "selftest:false")
    rc_mode, msg_mode = _origin_register(key, "mode:true:--flag")

    return [
        # AGREEMENT: both refuse a `refuses:` witness whose command exits 0.
        ("origin REFUSES a refuses: that exits 0", rc_refuses != 0),
        ("this module refuses it too", wp.probe(_TRUE, "refuses", root) is not None),
        ("origin's refusal names the same polarity fact", "EXITS 0" in msg_refuses),
        # AGREEMENT: both refuse a `selftest:` witness whose command exits non-zero.
        ("origin REFUSES a selftest: that exits non-zero", rc_selftest != 0),
        ("this module refuses it too", wp.probe(_FALSE, "selftest", root) is not None),
        # ⚑⚑⚑ DIVERGENCE, DELIBERATE AND THE REASON THIS MODULE EXISTS. The origin does not
        # probe `mode:` at all, so it accepts a witness whose polarity is already wrong.
        # This case FAILS if anyone "reconciles" the two by removing the new arm.
        (
            "origin does NOT refuse a mode: witness on polarity",
            rc_mode == 0 or "already registered" in msg_mode,
        ),
        (
            "this module DOES refuse the wrong-polarity mode: witness",
            wp.probe(_TRUE, "mode", root) is not None,
        ),
    ]


def main() -> int:
    """Run every case and report n/m."""
    root = str(ROOT)
    cases = _polarity_cases(root) + _coverage_cases(root) + _evidence_cases() + _differential()
    bad = [label for label, holds in cases if not holds]
    print(f"witness_polarity: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
