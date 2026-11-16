# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The private-block ratchet as a gate: every hidden definition is debt, paid down only.

⚑ POLICY. `private` narrows an over-wide module surface, and under one-definition-per-file
there is no surface to narrow — so a `private` helper is a SECOND definition in a file that
should hold one. The repair is to extract it and bind it at its owner. Deleting the keyword
and leaving the definition in place is not a paydown; it moves the debt to a different gate.

⚑⚑⚑ THIS REPLACES AN ENTRY POINT RATHER THAN EDITING ONE, AND THAT IS THE WHOLE MOVE.
`scripts/check_private_ratchet.py` does three jobs in about a hundred lines — census, gate
entry, selftest — behind two `sys.path.insert` calls, and carries enough findings that the
per-file gate refuses every edit to it, including the one-argument edit that would fix it.
So the argument was never reachable in place. Splitting the census out (`private_census`) and
writing the entry fresh makes the origin DELETABLE instead of editable, and its findings go
with it. ⚑ A file too dirty to edit is not a file that must stay: it is a file whose parts
have to move somewhere they can be clean.

⚑⚑ AND SUPPLYING `key_move` IS THE POINT, NOT A DETAIL. A set ratchet has no vocabulary for
a relocation, so a decomposition — which retires a key at the old path and mints one at the
new — reads as growth and REFUSES. Because the ratchet returns on `added` before its paydown
branch, that churn also blocks every genuine paydown in the same run from recording.
MEASURED on this gate before the change (`churn_report.py private`): two additions, both
churn from one decomposition, holding back the entire recorded paydown. The `key_move` comes
from the declared key schema rather than a hand-written lambda, because the one hand-written
instance in the tree is correct only for a path-first grammar and this repo has two reversed
ones.

⚑ THE BASELINE DOES NOT MOVE. The ledger IS the debt; relocating it beside the new code
would orphan the recorded census and read as a gate that had been paid down.

⚑ AND AN UNLOADABLE SCANNER REFUSES RATHER THAN REPORTING CLEAN. The census depends on two
tools loaded from `scratch/`; if either is missing the honest census is EMPTY, which is
indistinguishable from a clean tree and would bank an absolution of every existing violation
into a paydown-only baseline. `Unmeasurable` is the branch that separates the two.
"""

from __future__ import annotations

import sys

from mikemol.ratchet.render import Report

from substrate import corpus, private_census, ratchet_move
from substrate.gate_main import Gate, Unmeasurable, run_gate

# ⚑ WHERE THE GATES KEEP THEIR LEDGERS. Named from the schema's declared filename so the
# gate and every reader of its churn resolve the same file.
BASELINE = str(corpus.ROOT / "scripts" / "private_ratchet_baseline.txt")

_GATE = "private"


class ScannerUnavailable(Unmeasurable):
    """The declaration scanners could not be loaded, so no census exists to rule on."""

    remedy = "check that scratch/agda_lex.py and scratch/split_lemmas.py are present"


def census() -> set[str]:
    """Return the private-block census, or refuse if it could not be taken.

    ⚑ THE REFUSAL CARRIES THE TOOL'S OWN REASON, never a summary of it. "could not load"
    covers a missing file, a syntax error and a tool that exits at import, and each wants a
    different fix — so the message that comes back is the one the loader produced.
    """
    keys, why = private_census.census_or_why()
    if why is not None:
        raise ScannerUnavailable(why)
    return keys


GATE = Gate(
    label="private-ratchet",
    census=census,
    baseline_path=BASELINE,
    key_move=ratchet_move.key_move(_GATE),
)

REPORT = Report(
    noun="definition(s) hidden in a `private` block",
    refuse_hint=(
        "A `private` helper is a SECOND definition in a file that should hold one.\n"
        "  EXTRACT it to its own file and bind it at the owner. Do not delete the\n"
        "  keyword and leave the definition in place, and do not add an exemption.\n"
        "  (`private variable` is a binding form, not a helper, and is not censused.)\n"
        "  Enumerate the census with:  private_gate.py --list"
    ),
)


def main(argv: list[str]) -> int:
    """Run the gate. 0 = clean, 1 = the census grew, 2 = it could not be taken."""
    return run_gate(GATE, REPORT, argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
