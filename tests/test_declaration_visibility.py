# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The gates' declaration scan must see every declaration the definition index sees.

⚑⚑ EXTRACTED FROM `test_rederive_agreement.py` UNDER Ⓝ71g″ ⟡drain-test-rederive, AND MOVED RATHER
THAN DELETED. `check_carrier_locality.DECL` has no other coverage owner: the gate is imported by
nothing in the tree except this assertion, and while `check_rederive_ratchet` carries a `declscan`
motif, that motif COUNTS how many tools hand-roll a declaration scan. It does not run `DECL` over
the corpus, does not know about the indent anchor — which is the actual defect — and would be
perfectly green while a re-narrowed `DECL` silently lost the indented type names again.

⚑⚑⚑ PAID, AND KEPT AS THE REGRESSION GUARD. The gates scanned `data`/`record` with a COLUMN-0
anchor; the definition index was made indent-aware after a measured import-drop, and the gates
never learned. 142 type names — 20.6% — were invisible to carrier-locality, the sumtype ratchet,
the public ratchet, import-shape and decl-shape-tag. The consequences were not cosmetic: the
sumtype ratchet, whose entire purpose is refusing NEW duplicate declarations, saw 25 duplicated
names where the truth was 32, **so it could not refuse a new copy of the seven it could not see**;
and carrier-locality judged five carriers globally-unique that are not, then enforced "the operator
must live in the carrier's home" against a home that is not unique. Fixed by widening `DECL` to
match the index's own rule. It was held as an `expectedFailure` with the numbers in it first, so
the debt was A NUMBER IN THE SUITE rather than a note someone drops.

⚑⚑⚑ AND IT TESTS THE GATE'S OWN `DECL`, IMPORTED — NOT A LOCAL COPY OF THE REGEX. The first
version of this test compared two regexes it defined ITSELF, so it could pass while the gate stayed
broken, and would have kept reporting `expectedFailure` after the gate was FIXED — which is how the
mistake surfaced. **Import the thing under test, or the test is about the test.** That import is
what `stubs/check_carrier_locality.pyi` was written for; the monolith reached it with a
`sys.path.insert` and a bare import inside the test body, which is the prologue shape that makes a
tree unreadable and a second owner of `sys.path`.

⚑ THE OTHER SIDE OF THE COMPARISON IS THE DEFINITION INDEX'S RULE, and it is spelled here rather
than imported. That is not the same lapse as the paragraph above: the claim is that the GATE agrees
with the INDEX, so the index's rule is the reference arm and must be stated independently. What
would break the test is importing the gate's own pattern for both sides.

⚑ ONE-SIDED, AND THE DIRECTION IS THE CLAIM. The gate may match MORE than the index — an
over-match costs a spurious name in a census — but never FEWER, because a declaration the gate
cannot see is a duplicate it cannot refuse. Asserting equality would fail on a harmless widening
and teach the next reader to relax the test.

⚑ COMMENTS ARE MASKED FIRST. A commented-out `data` line is not a declaration, and none of the
gates' historical regex copies masked before scanning — so an unmasked comparison here would
manufacture disagreement out of dead text and report it as a gate defect.

⚑ THE `Scenario:` LINE SITS BELOW THE SUMMARY LINE. `D400`/`D415` require a first docstring line
ending in a period, while `gherkin_scan` captures to the closing quotes — so a period on the
`Scenario:` line becomes part of the scenario NAME and breaks the match against `features/`.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from agda_lex import agda_files, mask_comments
from check_carrier_locality import DECL

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "agda" / "Substrate"

# ⚑ THE DEFINITION INDEX'S RULE — the reference arm. Indent-aware (`^\s*`, not a column-0 anchor),
# and the name capture drops `(` and `{` so a parameterized head yields the bare name.
_INDEX_RULE = re.compile(r"^\s*(?:data|record)\s+([^\s({]+)")


def _declared_names(pattern: re.Pattern[str], text: str) -> set[str]:
    """Return the declaration names one per-line pattern finds in masked source."""
    found: set[str] = set()
    for line in text.split("\n"):
        m = pattern.match(line)
        if m:
            found.add(m.group(1))
    return found


class DeclarationVisibilityTest(unittest.TestCase):
    """No declaration the definition index sees may be invisible to the gate."""

    def test_gate_decl_scan_sees_what_agda_defs_sees(self) -> None:
        """The gate's own DECL matches every declaration the index rule matches.

        Scenario: the gates' declaration scan agrees with the definition index
        """
        # ⚑ NARROWED AT THE USE. `DECL` is declared `object` in the stub because the claim under
        # test is about what it MATCHES; promising a pattern type there would assert a property
        # nothing verified. This is the check that earns the narrowing.
        assert isinstance(DECL, re.Pattern), "check_carrier_locality.DECL is not a compiled pattern"

        files = agda_files(str(SRC))
        if not files:
            self.skipTest("no Agda corpus present")

        gate: set[str] = set()
        index: set[str] = set()
        for path in files:
            masked = mask_comments(Path(path).read_text(encoding="utf-8", errors="replace"))
            gate |= _declared_names(DECL, masked)
            index |= _declared_names(_INDEX_RULE, masked)

        if not index:
            self.skipTest("no declarations found in the corpus")

        assert index - gate == set(), (
            f"the gate's DECL misses declarations the definition index sees; a duplicate it "
            f"cannot see is a duplicate it cannot refuse: {sorted(index - gate)}"
        )


if __name__ == "__main__":
    unittest.main()
