# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Every gate that writes a ratchet baseline must route through the shared write guard.

⚑⚑ EXTRACTED FROM `test_rederive_agreement.py` UNDER Ⓝ88 ⟡split-and-annotate-are-one-drain,
alongside `test_ratchet_write_guard.py`. The two were one class in the monolith, and they
are two modules here because they are two kinds of claim: that one asks what the resolver
DOES (a behavioural property of a function), this asks who CALLS it (a census over the
gate population). They fail for unrelated reasons and are read by different people.

⚑ THE CENSUS IS THE POINT, AND IT IS NOT A DUPLICATE OF THE RESOLVER'S OWN SUITE. A guard
that is correct and unused is worth nothing: `set1_ratchet_cores.py` hand-rolled its own
census compare, never received the guard, and kept banking debt on a plain read while six
sibling gates were safe. The fix applied to the abstraction but not to the one member that
opted out of it — invisible precisely BECAUSE the surrounding convention is well-articulated.
"All of them are guarded" is exactly the kind of fact that silently becomes "all but one",
so it is asserted here rather than believed.

⚑ THIS IS A TEXTUAL SCAN, AND ITS BOUND IS PART OF ITS RESULT. It recognises a baseline
writer by source shape, so a gate that writes one by a spelling this does not match is
INVISIBLE to it — an empty offender list is a fact about the recognisers below, not a proof
that the population is clean. Recorded rather than papered over: the alternative is to
report a census green as a property of the tree, which is the failure this repo names.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GATES = REPO / "scripts"

# ⚑ THE RECOGNISERS, EACH NAMING WHAT IT CANNOT SEE. `_OPENS` catches an explicit write to a
# path whose name carries "baseline"; `_WRITES` catches the helper spelling. A writer using
# neither is outside this census's reach, which is the bound the docstring reports.
_OPENS = re.compile(r'open\(\s*\w*baseline\w*\s*,\s*["\']w["\']')
_WRITES = "_write("

# ⚑ THE GUARD'S OWN SPELLINGS. A file mentioning either is routed; the resolver is
# `substrate.baseline_io.may_write`, reached through the `ratchet` facade by most callers.
_ROUTED = ("set_ratchet", "may_write")

# ⚑ THE MODULE THAT DEFINES THE GUARD IS NOT ONE OF ITS CALLERS, so it cannot be an offender.
_DEFINER = "ratchet.py"


def _writes_a_baseline(src: str) -> bool:
    """Report whether this source looks like it writes a ratchet baseline."""
    return bool(_OPENS.search(src) or _WRITES in src) and "baseline" in src.lower()


class BaselineWritersGuardedTest(unittest.TestCase):
    """No baseline writer may reach the filesystem without consulting the guard."""

    def test_every_baseline_writer_is_guarded(self) -> None:
        """Each recognised baseline writer mentions the guard.

        Scenario: every baseline-writing gate routes through the write guard
        """
        offenders = [
            p.name
            for p in sorted(GATES.glob("*.py"))
            if p.name != _DEFINER
            and _writes_a_baseline(src := p.read_text(encoding="utf-8", errors="replace"))
            and not any(marker in src for marker in _ROUTED)
        ]
        assert offenders == [], (
            f"these write a baseline without routing through the write guard, so a plain "
            f"read will bank debt: {offenders}"
        )


if __name__ == "__main__":
    unittest.main()
