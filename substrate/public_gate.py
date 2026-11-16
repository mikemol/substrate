# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The public re-export ratchet as a gate: every wholesale `open … public` is debt, paid down only.

⚑ POLICY. `open import M public` re-materialises M's entire API into every consumer of this
module, so the import ban and the memory cap are the same constraint seen twice: a consumer that
needs one name elaborates the whole surface. The repair is to import what is used, at the file
that uses it — never to narrow the re-export with a `using` list, which leaves the module applied
and elaborated while only hiding names from view.

⚑⚑⚑ THIS REPLACES AN ENTRY POINT RATHER THAN EDITING ONE, the same move as `private_gate` and for
the same reason: the origin does census, gate entry and selftest in one file behind `sys.path`
mutation, and carries enough findings that the per-file gate refuses every edit to it. Splitting
the census out (`public_census`) and writing the entry fresh makes the origin DELETABLE rather
than editable.

⚑⚑ AND THE REPLACEMENT SEES ONE VIOLATION THE ORIGIN CANNOT — which is why the baseline RISES by
a key rather than matching. MEASURED: `public_census` holds 491 where the origin holds 490, and
the extra is `agda/Substrate.agda::Substrate.Cocycle`. That file is the tree's TOP-LEVEL module,
outside the enumeration root the origin scans, and its line 15 is `open import Substrate.Cocycle
public` — a wholesale re-export of exactly the kind this gate refuses, in the one file the gate
could never look at. **A census that cannot reach a file reports a clean tree there**, and the
gap was invisible for as long as the origin was the only reader.

⚑ SO THE +1 IS A FIX, NOT A DIVERGENCE, and recording it is a baseline RAISE that must be
reviewed rather than absorbed. The honest sequence is: retire toward the wider census, see the
gate refuse on a key that was always a violation, and pay it down or record it deliberately.
Matching the origin's number would have meant preserving its blind spot to keep a gate green.

⚑ THE BASELINE DOES NOT MOVE. The ledger IS the debt; relocating it beside the new code would
orphan the recorded census and read as a gate that had been paid down.
"""

from __future__ import annotations

import sys

from mikemol.ratchet.render import Report

from substrate import corpus, public_census, ratchet_move
from substrate.gate_main import Gate, run_gate

# ⚑ WHERE THE GATES KEEP THEIR LEDGERS. Named from the schema's declared filename so the gate and
# every reader of its churn resolve the same file.
BASELINE = str(corpus.ROOT / "scripts" / "public_ratchet_baseline.txt")

_GATE = "public"


def census() -> set[str]:
    """Return the re-export census.

    ⚑ NO `Unmeasurable` BRANCH HERE, UNLIKE `private_gate` — and the difference is real rather
    than an omission. That gate loads two scanners out of `scratch/` and must distinguish "no
    violations" from "the scanner is missing"; this census walks the tree itself, so an empty
    result is an empty tree and there is no third state to report.
    """
    return public_census.census()


GATE = Gate(
    label="public-ratchet",
    census=census,
    baseline_path=BASELINE,
    key_move=ratchet_move.key_move(_GATE),
)

REPORT = Report(
    noun="wholesale `open … public` re-export(s)",
    refuse_hint=(
        "A wholesale re-export re-materialises the upstream API into every\n"
        "  consumer. IMPORT WHAT IS USED, at the file that uses it. Narrowing the\n"
        "  re-export with `using` is not a paydown: the module is still applied and\n"
        "  elaborated, and the names are merely hidden.\n"
        "  Enumerate the census with:  public_gate.py --list"
    ),
)


def main(argv: list[str]) -> int:
    """Run the gate. 0 = clean, 1 = the census grew, 2 = it could not be taken."""
    return run_gate(GATE, REPORT, argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
