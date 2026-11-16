# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The build DAG's import edges must never be fewer than the lexer's.

⚑⚑ EXTRACTED FROM `test_rederive_agreement.py` UNDER Ⓝ71g″ ⟡drain-test-rederive, AND IT IS A MOVE
RATHER THAN A DELETION BECAUSE THE TWIN SEARCH CAME BACK EMPTY. The two classes drained before this
one were duplicates of arms already owned by `substrate/baseline_io_selftest.py`, and a prior note
suggested the remaining classes might share that shape. They do not. `gen_build_makefiles.IMPRE` is
bound at exactly two sites tree-wide and neither is a test; the generator has no `--selftest`; and
nothing else in the tree runs its edge set against the lexer's. **A drain that treated the classes
alike would have deleted the only cross-authority check in order to remove a duplicate.**

⚑⚑⚑ THE INCIDENT THIS CARRIES, AND THE REASON THE ASSERTION IS ONE-SIDED. `IMPRE` was
`[A-Za-z0-9_.'-]+` — ASCII-only — so an import of a module whose name holds a non-ASCII letter
contributed NO EDGE. `PhaseTransition.agda` imports `IsAñeléTerminal` and `PriorAñelé`, and neither
was a prerequisite: eight edges were missing from the committed `agda/Flat.mk`. make could not see
those modules go stale, so `make -j` could schedule an importer concurrently with the import it
depends on. **`--check` certified it, because the gate compared Flat.mk against the same broken
regex — a gate re-using the buggy parser certifies its own blind spot.** This is the assertion that
would have caught it on the day it was written, instead of it shipping into a committed artifact.

⚑ SO THE GENERATOR MAY HOLD MORE, NEVER FEWER, AND THE DIRECTION IS THE WHOLE CLAIM. A spurious
edge only over-builds; a missing one corrupts staleness, which is the property make's mtime model
rests on. Asserting equality would fail on the generator's legitimate over-approximation and teach
the next reader to relax the test rather than read it.

⚑⚑ THE INSTRUMENT IS RUNNING BOTH ROUTES AND DIFFING THE SETS, and nothing cheaper substitutes. A
structural-similarity instrument is blind to this class BY CONSTRUCTION — the two routes share no
tokens, so an empty similarity result is not evidence of agreement. `scripts/check_rederive_ratchet`
greps for the broken SPELLING and is the cheap always-on layer; its own docstring names this suite
as the complete instrument it approximates. It is a paydown ratchet that tolerates declared debt,
so it would stay green with live offenders standing. This asserts zero.

⚑ THE GENERATOR AND THE LEXER ARE IMPORTED, NEVER RESPELLED. A test that types the regex tests its
own copy: repair `IMPRE` and this suite would keep passing against a pattern nothing uses.

⚑⚑ THE IMPORTS ARE BARE MODULE NAMES ON PURPOSE, AND THE PACKAGE SPELLING DOES NOT WORK HERE.
`tests/__init__.py` puts `scratch/` and `scripts/` on `sys.path` anchored on ITS OWN file, so a
bare name resolves regardless of cwd. Typing comes from `stubs/agda_lex.pyi` and
`stubs/gen_build_makefiles.pyi`, written for this drain — and a stub is keyed on the module name it
declares, so `from scripts.gen_build_makefiles import …` bypasses it and mypy follows the untyped
source instead. **This replaces the monolith's `sys.path.insert` plus bare import INSIDE the test
body** — the prologue shape that makes a tree unreadable, and a second owner of `sys.path`.

⚑ THE `Scenario:` LINE SITS BELOW THE SUMMARY LINE, and that placement is load-bearing rather than
stylistic. `D400`/`D415` require a first docstring line ending in a period, while `gherkin_scan`'s
pattern captures to the closing quotes — so a period on the `Scenario:` line becomes part of the
scenario NAME and breaks the match against `features/`. The scan is `re.MULTILINE` and `D400`
governs only the FIRST line, so both are satisfied by putting the summary first.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from agda_lex import agda_files, mask_comments, statements
from gen_build_makefiles import IMPRE

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "agda" / "Substrate"

# ⚑ ONLY IN-TREE MODULES ARE COMPARED. A `Substrate`-prefixed name is one the build generator is
# responsible for; anything else is an out-of-tree import that carries no build edge, so a
# difference there is not a defect this claim is about.
_IN_TREE = "Substrate"


def _generator_edges(text: str) -> set[str]:
    """Return the import edges the BUILD GENERATOR's own pattern finds in one source."""
    # ⚑ NARROWED AT THE USE, NOT ASSUMED AT THE IMPORT. `IMPRE` is declared `object` in the stub
    # because the claim under test is about what it MATCHES; promising a pattern type there would
    # assert a property nothing verified. This is the check that earns the narrowing.
    assert isinstance(IMPRE, re.Pattern), "gen_build_makefiles.IMPRE is not a compiled pattern"
    return {m.group(1) for m in IMPRE.finditer(text)}


def _lexer_edges(text: str) -> set[str]:
    """Return the import edges THE LEXER finds in one source."""
    return {
        s.module
        for s in statements(mask_comments(text).split("\n"))
        if s.kind == "import" and s.module
    }


class ImportEdgeAgreementTest(unittest.TestCase):
    """The generator's edge set must cover the lexer's over the live corpus."""

    def test_build_generator_agrees_with_the_lexer(self) -> None:
        """No in-tree edge the lexer sees is missing from the generator's.

        Scenario: the build DAG's import edges equal the lexer's import edges

        ⚑ THE FAILURE MESSAGE NAMES FILES AND MODULES, because the repair is per-edge. A bare
        count would say the generator is broken without saying where, and the last time this went
        wrong the eight missing edges were found by reading a build failure rather than a report.
        """
        files = agda_files(str(SRC))
        if not files:
            self.skipTest("no Agda corpus present")

        missing: list[tuple[str, list[str]]] = []
        for path in files:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
            lost = sorted(
                m for m in _lexer_edges(text) - _generator_edges(text) if m.startswith(_IN_TREE)
            )
            if lost:
                missing.append((str(Path(path).relative_to(REPO)), lost))

        assert missing == [], (
            f"the build generator is missing import edges the lexer sees, so make cannot mark "
            f"these modules stale: {missing}"
        )


if __name__ == "__main__":
    unittest.main()
