#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the polarity guard, and pin that the `mode:` arm is a DIVERGENCE from the origin.

⚑⚑⚑ THIS SUITE IS DIFFERENTIAL IN TWO DIRECTIONS AT ONCE, which is unusual and deliberate.
For `refuses` and `selftest` it asserts AGREEMENT with the origin — a drain that quietly
changed a guard would be a rewrite wearing a refactor's clothes. For `mode` it asserts
DISAGREEMENT, because the origin returns three lines early for that kind and registers it
unprobed. An intended divergence that is not cased reads exactly like an accidental one.

⚑⚑ THE MEASURED INSTANCE IS `gate-F55`: a `mode:` witness was registered reporting DOCUMENTED
under a finding that the flag IS documented — as a redirect — and NOT dispatched. Opposite
polarity, caught by a manual run because nothing probed the kind.

⚑ AND THE ACCEPT DIRECTION IS CASED AS HEAVILY AS THE REFUSE DIRECTION. A guard that refused
everything would satisfy every refusal case here and make the ledger unwritable; the cases
that assert a CORRECT registration passes are what stop the probe becoming a wall.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Protocol, cast

from substrate import finding_polarity

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = ROOT / ".claude" / "agents" / "findings.py"

Case = tuple[str, bool]

_PASSES = ["python3", "-c", "pass"]
_FAILS = ["python3", "-c", "raise SystemExit(3)"]
_ABSENT = ["/nonexistent/binary/entirely"]


class _Origin(Protocol):
    """The origin surface this differential reads — named so a typo cannot pass."""

    def _probe_polarity(self, cmd: list[str], kind: str) -> str | None: ...


def _origin() -> _Origin | None:
    """Load the origin by path, or return None when it cannot be reached."""
    if not ORIGIN.is_file():
        return None
    spec = importlib.util.spec_from_file_location("_origin_findings_polarity", ORIGIN)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 — a broken origin is a FINDING here, not a crash
        return None
    return cast("_Origin", mod)


def _refuse_cases() -> list[Case]:
    """Return the cases pinning that a wrong-polarity registration is refused."""
    gone = finding_polarity.probe(_PASSES, "refuses")
    open_now = finding_polarity.probe(_FAILS, "selftest")
    return [
        ("a `refuses:` command exiting 0 is REFUSED", gone is not None),
        ("...and the refusal says the refusal would read as GONE",
         gone is not None and "GONE" in gone),
        # ⚑ TWO CAUSES ARE NAMED RATHER THAN ONE ASSERTED — picking would be the over-reach the
        #   kind system exists to prevent, one layer up.
        ("...and names BOTH causes, without choosing",
         gone is not None and "(a)" in gone and "(b)" in gone),
        ("...and names the honest kind for the census case",
         gone is not None and "unwitnessed" in gone),
        ("a `selftest:` command exiting non-zero is REFUSED", open_now is not None),
        ("...and says the witness would be born OPEN",
         open_now is not None and "born" in open_now and "OPEN" in open_now),
    ]


def _accept_cases() -> list[Case]:
    """Return the cases pinning that a CORRECT registration passes.

    ⚑ WITHOUT THESE THE GUARD COULD REFUSE EVERYTHING and satisfy every case above, which
    would make the ledger unwritable — a probe becoming a wall rather than a gate.
    """
    return [
        ("a `refuses:` command that DOES refuse is accepted",
         finding_polarity.probe(_FAILS, "refuses") is None),
        ("a `selftest:` command that DOES pass is accepted",
         finding_polarity.probe(_PASSES, "selftest") is None),
        # ⚑ THE TWO UNPROBED KINDS RUN NO COMMAND, so they have no polarity to be born wrong
        #   about and must never be refused — absent by construction, not by omission.
        ("`standing` is not probed", finding_polarity.probe(_FAILS, "standing") is None),
        ("`unwitnessed` is not probed", finding_polarity.probe(_PASSES, "unwitnessed") is None),
        ("...and the probed roster says which kinds carry a polarity",
         set(finding_polarity.PROBED) == {"refuses", "selftest", "mode"}),
    ]


def _unrunnable_cases() -> list[Case]:
    """Return the cases pinning that an absent instrument is refused, not waved through."""
    refused = [finding_polarity.probe(_ABSENT, kind) for kind in finding_polarity.PROBED]
    return [
        ("an unstartable command is refused for EVERY probed kind",
         all(r is not None for r in refused)),
        ("...and the refusal says it did not run",
         all(r is not None and "DID NOT RUN" in r for r in refused)),
        # ⚑ THE REASON IS STATED, because a filer who reads only "refused" retries rather than
        #   fixing the command.
        ("...and says why that matters — it would report 2 forever",
         all(r is not None and "absent instrument" in r for r in refused)),
    ]


def _mode_arm_cases() -> list[Case]:
    """Pin the NEW `mode:` arm, and pin that the origin does NOT have it (Ⓝ162⁗).

    ⚑⚑⚑ AN INTENDED DIVERGENCE MUST BE CASED AS ONE. If this ever starts agreeing with the
    origin, either the origin grew the arm — in which case the drain should adopt it rather
    than keep a second spelling — or this module lost it. Both want a human, and a suite that
    only asserted agreement would report neither.
    """
    mine = finding_polarity.probe(_PASSES, "mode")
    origin = _origin()
    return [
        ("a `mode:` witness reporting DOCUMENTED is REFUSED", mine is not None),
        ("...and says it would assert the opposite of the finding",
         mine is not None and "opposite" in mine),
        # ⚑ THE ARM IS DECIDABLE ONLY BECAUSE THE READER HAS ONE ZERO-PATH, and the refusal
        #   says so — otherwise a reader cannot tell this from a heuristic.
        ("...and names why the arm is unambiguous, not a heuristic",
         mine is not None and "one zero-path" in mine.lower()),
        ("...and names `unwitnessed` for the documented-as-a-redirect case",
         mine is not None and "unwitnessed" in mine),
        # ⚑ A CORRECT `mode:` FILING STILL PASSES — the arm is a gate, not a wall.
        ("a `mode:` witness reporting UNDOCUMENTED is accepted",
         finding_polarity.probe(_FAILS, "mode") is None),
        # ⚑⚑ THE DIVERGENCE ITSELF, asserted against the live origin.
        ("the ORIGIN does not probe `mode:` — the gap Ⓝ162⁗ names",
         origin is not None and origin._probe_polarity(_PASSES, "mode") is None),  # noqa: SLF001
    ]


def _differential_cases() -> list[Case]:
    """Assert AGREEMENT with the origin on the two arms it has.

    ⚑ AGREEMENT IS ASSERTED ON THE VERDICT, NOT THE WORDING. The refusal texts are rewritten
    prose; what a drain owes is that the same registrations are refused and accepted, which is
    the behaviour a caller depends on.
    """
    origin = _origin()
    if origin is None:
        return [("⚑ the origin is readable, so the differential can run", False)]
    probes = ((_PASSES, "refuses"), (_FAILS, "refuses"),
              (_PASSES, "selftest"), (_FAILS, "selftest"),
              (_ABSENT, "refuses"), (_ABSENT, "selftest"))
    agree = all(
        (finding_polarity.probe(cmd, kind) is None)
        == (origin._probe_polarity(cmd, kind) is None)  # noqa: SLF001
        for cmd, kind in probes)
    return [
        ("the origin loaded, so this differential means something", True),
        ("both guards agree on refuses/selftest, accept and refuse alike", agree),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = (_refuse_cases() + _accept_cases() + _unrunnable_cases()
             + _mode_arm_cases() + _differential_cases())
    bad = [label for label, holds in cases if not holds]
    print(f"finding_polarity: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
