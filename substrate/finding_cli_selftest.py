#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the router, driving the WHOLE dispatch over a fixture roster.

⚑⚑⚑ THE CASES DRIVE `run`, NOT THE MODULES UNDER IT, AND THAT IS THE POINT. Each collaborator
has its own suite; what this one owns is the WIRING, and a defect in wiring is invisible to a
case that calls a collaborator directly. The origin's measured instance of that class was a
declared field its parser never populated — every unit passed and the composed behaviour was
wrong.

⚑⚑ A REFUSAL IS ASSERTED AS A RETURN VALUE. `run` yields `(lines, code)` rather than printing
and exiting, so a case can read a refusal's TEXT. The origin raised from inside a branch and
its own suite aborted at the first refusal, leaving later cases as dead text under a score
that read as full coverage.

⚑ AND AN UNKNOWN FLAG IS CASED IN BOTH DIRECTIONS. A router that fell through to the key
resolver would report *"no witness registered for '--nonsense'"* — technically true, useless,
and indistinguishable from a real missing key.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from substrate import finding_cli, finding_kinds

if TYPE_CHECKING:
    from collections.abc import Callable

Case = tuple[str, bool]
Roster = dict[str, "Callable[[], tuple[int, str]]"]


def _roster() -> Roster:
    """Build a three-key fixture roster covering two kinds."""
    return {
        "aa-F1-a-passing-thing": lambda: finding_kinds.standing("a measured fact"),
        "aa-F2-an-honest-gap": lambda: finding_kinds.unwitnessed("nothing can check this"),
        "bb-F1-another": lambda: finding_kinds.standing("a second fact"),
    }


def _classify(key: str) -> str:
    """Classify a fixture key by kind, standing in for the origin's bytecode probe."""
    return "unwitnessed" if key.endswith("gap") else "standing"


def _resolve_cases() -> list[Case]:
    """Return the cases pinning that a bare operand routes to the key resolver."""
    roster = _roster()
    exact, exact_code = finding_cli.run(["aa-F1-a-passing-thing"], roster, _classify)
    prefix, prefix_code = finding_cli.run(["aa-F2"], roster, _classify)
    ambiguous, amb_code = finding_cli.run(["aa-"], roster, _classify)
    unknown, unknown_code = finding_cli.run(["zz-nothing"], roster, _classify)
    return [
        ("an exact key runs its witness", exact_code == finding_kinds.CLOSED),
        ("...and the line carries the note", "a measured fact" in exact[0]),
        # ⚑ A UNIQUE PREFIX RESOLVES, and the kind's own code comes back — so the router is
        #   returning the WITNESS's verdict rather than a verdict of its own.
        ("a unique prefix resolves and carries its kind's code",
         prefix_code == finding_kinds.UNRUNNABLE),
        ("...naming the full key it resolved to", "aa-F2-an-honest-gap" in prefix[0]),
        ("an ambiguous prefix is refused", amb_code == finding_cli.REFUSED),
        ("...and the refusal lists the candidates", "AMBIGUOUS" in ambiguous[0]),
        ("an unknown key is refused", unknown_code == finding_cli.REFUSED),
        ("...as a roster/record disagreement", "roster/record" in unknown[0]),
    ]


def _mode_cases() -> list[Case]:
    """Return the cases pinning the flag routes and the unknown-flag refusal."""
    roster = _roster()
    kinds, kinds_code = finding_cli.run(["--kinds"], roster, _classify)
    bare, bare_code = finding_cli.run([], roster, _classify)
    nonsense, nonsense_code = finding_cli.run(["--nonsense"], roster, _classify)
    blob = "\n".join(kinds)
    return [
        ("--kinds answers", kinds_code == 0),
        # ⚑ THE ZERO ROW SURVIVES THE ROUTER, which is what makes the census reachable at all.
        ("...with a row for a kind no fixture witness uses", "refuses" in blob),
        ("...and the behavioural total is reported", "BEHAVIOURAL" in blob),
        ("...naming what standing cannot do", "flip" in blob),
        ("a bare invocation prints usage rather than guessing",
         bare_code == finding_cli.REFUSED),
        ("...and the usage names the modes", "--pairing" in bare[0]),
        # ⚑⚑ BOTH DIRECTIONS. Falling through to the resolver would report an unknown flag as
        #   a missing KEY — true, useless, and indistinguishable from a real one.
        ("an unknown flag is refused AS a flag", nonsense_code == finding_cli.REFUSED),
        ("...naming the flag rather than a missing key",
         "unknown mode" in nonsense[0] and "--nonsense" in nonsense[0]),
        ("...and NOT as a roster/record disagreement",
         all("roster/record" not in line for line in nonsense)),
    ]


def _roster_cases() -> list[Case]:
    """Return the cases pinning that the declared mode roster matches what routes."""
    roster = _roster()
    declared = set(finding_cli.MODES)
    # ⚑ EVERY DECLARED MODE MUST BE REACHABLE — a flag in the roster that falls through to the
    #   unknown-mode refusal is a promise the router does not keep.
    unreachable = [
        mode for mode in declared
        if mode != "--kinds"
        and "unknown mode" in "\n".join(finding_cli.run([mode], roster, _classify)[0])
    ]
    return [
        ("the mode roster is non-empty", len(declared) > 0),
        ("no declared mode reaches the unknown-mode refusal", unreachable == []),
        ("--kinds is declared", "--kinds" in declared),
        ("--pairing is declared", "--pairing" in declared),
    ]


def _no_decision_cases() -> list[Case]:
    """Return the cases pinning that the router returns the WITNESS's verdict, unaltered.

    ⚑ THE ROUTER MUST NOT NORMALISE A CODE. A wiring layer that mapped every non-zero to 1
    would erase the UNRUNNABLE/OPEN distinction the whole kind system exists to carry — and it
    would do so invisibly, since both still read as failure.
    """
    roster = _roster()
    _, closed = finding_cli.run(["aa-F1-a-passing-thing"], roster, _classify)
    _, unrunnable = finding_cli.run(["aa-F2-an-honest-gap"], roster, _classify)
    return [
        ("a standing witness returns CLOSED", closed == finding_kinds.CLOSED),
        # ⚑ NOT OPEN. Collapsing UNRUNNABLE into OPEN loses the honest-gap third outcome.
        ("an unwitnessed witness returns UNRUNNABLE, not OPEN",
         unrunnable == finding_kinds.UNRUNNABLE),
        ("...which is a distinct outcome from OPEN",
         finding_kinds.UNRUNNABLE != finding_kinds.OPEN),
        # ⚑⚑ AND THE ROUTER'S OWN REFUSAL SHARES THE INTEGER WITH UNRUNNABLE, unavoidably at
        #   the shell — naming them separately is what keeps the two facts distinguishable in
        #   code, where one is an honest gap and the other a malformed invocation.
        ("the router's refusal is spelled separately from the kind's verdict",
         finding_cli.REFUSED == finding_kinds.UNRUNNABLE),
    ]


def main() -> int:
    """Run every case and report n/m."""
    cases = _resolve_cases() + _mode_cases() + _roster_cases() + _no_decision_cases()
    bad = [label for label, holds in cases if not holds]
    print(f"finding_cli: {len(cases) - len(bad)}/{len(cases)}")  # noqa: T201
    for label in bad:
        print(f"  FAIL {label}")  # noqa: T201
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
