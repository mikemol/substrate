# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The ratchet write guard's ENVIRONMENT resolution, and refusal as its default.

⚑⚑ EXTRACTED FROM `test_rederive_agreement.py` UNDER Ⓝ88 ⟡split-and-annotate-are-one-drain.
The monolith carries findings the per-file gate refuses in bulk, and that gate has no
partial-credit path — so the one-keyword repair its guard case needed could not land in
place. The route is not to pay the monolith down to make a change: it is to extract the
concern into a module written clean in one pass. `baseline_io.may_write` is keyword-only
(`FBT001` refuses a boolean positional, because a bare `may_write(True)` says nothing at
the call site about what the True decides), and the monolith called it positionally, so
the suite raised `TypeError` and the tool-unit-tests gate read FAIL.

⚑⚑⚑ AND THE FAILING ARM WAS ALREADY OWNED ELSEWHERE, WHICH IS WHY THIS FILE IS NARROWER
THAN WHAT IT REPLACES. `substrate/baseline_io_selftest.py` pins explicit-intent-beats-the-
environment in BOTH directions, with `may_write(write=False)` spelled correctly. The
monolith's version was a DUPLICATE that had drifted out of the signature's reach while its
twin stayed green — the derived-view divergence class the monolith itself exists to name,
occurring in the monolith. Copying it here would mint that duplicate a third time.

⚑ SO WHAT IS KEPT IS THE ARM THE SIBLING DOES NOT HAVE: the ENVIRONMENT default. The
sibling never passes `write=None`, so nothing there pins that an unset flag reads as
REFUSE. That default is the whole safety property — a read-only auditor who forgets the
flag must not mutate a baseline — and it was measured failing twice before the guard
existed.

⚑ THE ENVIRONMENT IS PROCESS-GLOBAL, so every case here restores what it found. A suite
that leaks the flag hands every later test in the same process a write-enabled guard,
which is precisely the defect under test wearing a test's clothes.

⚑ THE FLAG'S NAME IS IMPORTED, NEVER RESPELLED. A test that types the string tests its own
copy: rename the variable in the resolver and this suite keeps passing against a flag
nothing reads. `baseline_io` owns the name; this asks it.

⚑⚑ THE `Scenario:` LINES SIT BELOW EACH SUMMARY LINE RATHER THAN ON IT, and that placement
is load-bearing rather than stylistic. `D400`/`D415` require a first docstring line ending
in a period, while `gherkin_scan`'s pattern captures to the closing quotes — so a period on
the `Scenario:` line becomes part of the scenario NAME and breaks the match against
`features/`. The scan is `re.MULTILINE` and `D400` governs only the FIRST line, so both are
satisfied by putting the summary first and the scenario after it.
"""

from __future__ import annotations

import os
import unittest

from substrate.baseline_io import may_write

# ⚑ THE RESOLVER COMPARES TO THIS EXACT VALUE, and the last case pins that it does.
_ENABLED = "1"
_FLAG = "SUBSTRATE_RATCHET_WRITE"


class RatchetWriteGuardTest(unittest.TestCase):
    """`may_write` resolves the environment, and refusal is the default.

    ⚑ THE GUARD MUST NOT BE RE-DERIVED PER GATE. It was added to the ratchet core after
    the read-mutates-state defect was measured twice — once by a read-only auditor who
    had been forbidden to write and could not avoid it. Six gates routed through it;
    one hand-rolled its own census compare, never received it, and kept banking debt on
    a plain read. The second-order damage was worse: "do not run the ratchet gates, they
    mutate" became true of one gate and false of six, with no way to tell which — training
    avoidance of a whole class for a reason that no longer applied to most of it.
    """

    def setUp(self) -> None:
        """Remember the ambient flag so each case can restore it."""
        self._saved = os.environ.pop(_FLAG, None)

    def tearDown(self) -> None:
        """Restore the ambient flag exactly as it was found, including absent."""
        os.environ.pop(_FLAG, None)
        if self._saved is not None:
            os.environ[_FLAG] = self._saved

    def test_the_guard_defaults_to_read_only(self) -> None:
        """An absent flag refuses, the enabling value permits, nothing else does.

        Scenario: the write guard defaults to read-only

        ⚑ ONE CASE, BECAUSE THE SPEC DECLARES ONE SCENARIO. The three arms below are the
        spec's own clauses — `may_write()` is False unless the flag is set — and splitting
        them across three methods would mint three scenario names the spec does not have,
        which `check_feature_coverage` correctly refuses. A test naming a scenario nobody
        declares has stopped meaning anything.

        ⚑ ABSENT IS REFUSE, NOT PERMIT. This is the arm that makes "the gates are safe to
        run read-only" a checkable fact rather than a convention.

        ⚑ AND A TRUTHY-STRING TEST WOULD ADMIT "0", the spelling an operator reaches for to
        turn the guard OFF — it would grant writes to a run that asked for none. The
        resolver compares to the literal, and that is asserted rather than believed.
        """
        assert may_write() is False

        os.environ[_FLAG] = _ENABLED
        assert may_write() is True

        for value in ("0", "", "true", "yes", "2"):
            os.environ[_FLAG] = value
            assert may_write() is False, value


if __name__ == "__main__":
    unittest.main()
