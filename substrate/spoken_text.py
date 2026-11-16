#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The check a `speak()` banner must pass — one body, for every module that refuses instead.

⚑⚑⚑ IT IS ONE PROPERTY ACROSS FOUR MODULES AND COUNTING, SO IT IS ONE BODY. `--calls speak`
reports four definitions of the bare-invocation banner, each written after the same measured
defect: a module ran bare, printed nothing, exited 0, and the silence read as *your query matched
nothing*. The first repair (`store_calls`) checked its banner with arms written in its own suite;
copying those arms into each new module is how `rungs.Cases`' header describes fifty suites
reimplementing one contract — 55 defs, 0 delegating, 40 of them the identical statement.

⚑⚑ THE CHECK IS *DISCLAIMS*, NOT *IS NON-EMPTY*, AND THAT DISTINCTION IS THE WHOLE VALUE. A
banner reading only the module's name satisfies "it speaks" while leaving the reader with exactly
the wrong model of what the module can answer — which is the defect, not the silence as such. So
a spoken text owes three things: it says what the module IS, it names an entry point a caller can
reach, and it names the capability the module's NAME suggests but does not have.

⚑ THE THIRD IS THE ONE A COPY WOULD DROP. Saying what a module does is easy to write and easy to
check; saying what it does NOT do is the part that was missing when an operator read silence as a
zero, and it is the part a suite author omits when reproducing arms from memory.

⚑ AND THE MARKERS ARE PARAMETERS, NOT A FROZEN ROSTER. Each module's disclaimer is its own — the
capability `witness_row` lacks is not the one `warrant_bib` lacks — so this holds the SHAPE of the
check and takes the module's own words. A roster of needles here would be a second spelling of
four banners, drifting from all of them at once.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

# The exit status a refusing entry point owes. ⚑ NOT 0 AND NOT 1: 0 is the silence being
# retired, and 1 reads as "the thing you asked for failed" rather than "you asked nothing".
REFUSAL_STATUS = 2


@dataclass(frozen=True, slots=True)
class Missing:
    """What a banner failed to say — empty when it said everything owed."""

    empty: bool
    absent: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """Report whether the banner owes nothing further."""
        return not self.empty and not self.absent

    def why(self) -> str:
        """Return the reader-facing reason, naming what was absent."""
        if self.empty:
            return "the spoken text is empty"
        if self.absent:
            return f"the spoken text omits {list(self.absent)!r}"
        return "the spoken text says everything owed"


def audit(text: str, *needles: str) -> Missing:
    """Return what a spoken banner failed to say.

    ⚑ AN EMPTY TEXT IS ITS OWN FINDING, NOT AN ABSENT-EVERYTHING ONE. A caller told that a
    banner omitted four needles goes looking for four edits; a caller told the banner is empty
    knows there is no banner. Collapsing the two would report the second as the first.

    ⚑⚑ A CALL WITH NO NEEDLES IS THE VACUOUS CASE AND IT IS REPORTED, NOT PASSED. `audit(text)`
    with nothing to look for returns ok for any non-empty string, which is the check that always
    says yes — so `demands()` exists beside this for a suite to assert it asked for something.
    """
    if not text.strip():
        return Missing(empty=True, absent=())
    return Missing(empty=False, absent=tuple(n for n in needles if n not in text))


def demands(*needles: str) -> int:
    """Return how many things a check is actually asking a banner to say.

    ⚑ THE GUARD AGAINST A CHECK THAT CANNOT FAIL. An arm calling `audit(text)` with no needles
    passes on any banner, including one that says nothing useful — the always-says-yes predicate.
    A suite asserts this is positive so the vacuous call is a failure rather than a pass.
    """
    return len(needles)


def usage() -> str:
    """Return what this module is and how to ask it."""
    return (
        "spoken_text is a LIBRARY — it checks what a module's bare-invocation banner says.\n"
        "\n"
        "  audit(text, *needles) -> what the banner failed to say\n"
        "  demands(*needles)     -> how many things the check asks for (0 cannot fail)\n"
        f"  REFUSAL_STATUS       -> {REFUSAL_STATUS}, the exit a refusing entry point owes\n"
        "\n"
        "⚑ IT DOES NOT RUN A MODULE OR READ ITS BANNER. A caller passes the text; this has\n"
        "  no subprocess and no import machinery, so it cannot tell you whether some module\n"
        "  speaks — only whether a string it is handed says what a banner owes.\n"
        "\n"
        "usage: spoken_text.py --selftest\n"
    )


# ⚑ THIS MODULE REFUSES ON ITS OWN TERMS — the contract it checks, applied to itself. A checker
# for bare-invocation banners that exited 0 in silence would be the rule stated by a violator.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        from substrate import spoken_text_selftest

        sys.exit(spoken_text_selftest.selftest())
    sys.stderr.write(usage())
    sys.exit(REFUSAL_STATUS)
