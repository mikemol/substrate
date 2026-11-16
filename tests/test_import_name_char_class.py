# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""No tool may capture an Agda import's module name with an ASCII-only character class.

⚑⚑ EXTRACTED FROM `test_rederive_agreement.py` UNDER Ⓝ71g″ ⟡drain-test-rederive, AND MOVED RATHER
THAN DELETED. `scripts/check_rederive_ratchet.py` holds a byte-identical `importname` motif over
the same two directories, which is the closest thing to a twin in the tree — and it is deliberately
a DIFFERENT claim. That gate is a paydown RATCHET against a baseline: it tolerates every existing
offender, admits a `⚑rederive:` opt-out, and excludes `tests/` by construction, so it stays green
while live offenders stand. It asserts *no NEW key*; this asserts *zero*. The gate's own docstring
names this suite as the complete instrument it is the cheap always-on layer beneath, so draining
the suite would remove the strict half and leave the tolerant half reading as coverage.

⚑⚑⚑ THE CLASS, NOT AN INSTANCE. `[A-Za-z0-9_.'-]+` and its relatives stop at the first non-ASCII
letter, so the capture returns a TRUNCATED name — which is worse than failing, because a truncated
name is plausible and flows onward as data. The severities differ by which characters the class
omits: omitting non-ASCII misses two modules (`PriorAñelé`, `IsAñeléTerminal`); omitting `-` as
well misses 160, every hyphenated name. The same defect in the build generator dropped eight real
edges from the committed `agda/Flat.mk`. Python's `\w` is Unicode-aware, so `[\w.'-]+` is both
correct and shorter than every broken form it replaces.

⚑⚑⚑ AND THIS GUARD WAS ONCE A SPELLING GUARD, NOT A CLASS GUARD, AND IT PASSED WHILE FOUR
INSTANCES STOOD. It matched `import\s+([A-Za-z0-9` — the exact literal shape of the sites its
author had just converted. The four survivors write `(?:open\s+import|import)\s+([A-Za-z0-9`, with
an ALTERNATION between the keyword and the capture, so the fixed prefix never matched and the test
would have passed forever. Same failure as an `expectedFailure` that compared two regexes it
defined itself: **a test written from the INSTANCE passes on everything except the instance.** The
rule this encodes is to match the thing that is WRONG — the character class — and never the context
that happened to surround it in the examples you fixed. The pattern below therefore makes no
assumption about what precedes the capture.

⚑ THE TWO CASES ARE TWO KINDS OF CLAIM AND SO TWO METHODS. One is a CENSUS over tool sources asking
who spells the defect; the other RUNS the corrected class over the live corpus and diffs against
the lexer. They fail for unrelated reasons — the first when someone writes a new broken tool, the
second when the corrected class turns out to be incomplete — and the spec declares them as two
scenarios.

⚑ THE SCAN'S BOUND IS PART OF ITS RESULT. It recognises the defect by source shape over `scripts/`
and `scratch/`, so a tool spelling it differently, or living elsewhere, is INVISIBLE to it. An
empty offender list is a fact about the recogniser, not a proof that the population is clean —
recorded rather than papered over, because reporting a census green as a property of the tree is
the failure this suite exists to name.

⚑ THE LEXER IS IMPORTED AS A BARE MODULE NAME, typed through `stubs/agda_lex.pyi` (written for this
drain). `tests/__init__.py` puts `scratch/` on `sys.path` anchored on its own file, so the name
resolves regardless of cwd, and a stub is keyed on the module name it declares — a package-path
spelling would bypass it and drag mypy into the untyped source.

⚑⚑ `re.findall` IS ANNOTATED `list[Any]`, AND A COMPREHENSION OVER IT DOES NOT NARROW IT — the
iteration happens over an `Any`-typed sequence, so the checker refuses the expression before
`str()` ever runs. `_findall` below binds to a declared `object` and tests with a real
`isinstance`, which is a CHECK rather than an assertion. This is the same shape `gherkin_scan`
records at its own `findall`, and it recurs at every untyped-boundary seam in this tree.

⚑ THE `Scenario:` LINES SIT BELOW EACH SUMMARY LINE. `D400`/`D415` require a first docstring line
ending in a period, while `gherkin_scan` captures to the closing quotes — so a period on the
`Scenario:` line becomes part of the scenario NAME and breaks the match against `features/`.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from agda_lex import agda_files, mask_comments, statements

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "agda" / "Substrate"

# The directories the census covers. Named here so the bound above is readable as data.
_SCANNED = ("scripts", "scratch")

# ⚑ THE CLASS, ANCHORED ON THE DEFECT RATHER THAN ON ITS NEIGHBOURS: an ASCII-only character class
# capturing a name, anywhere within a short reach of an `import` on the same line. The window is
# what lets an alternation sit between the keyword and the capture — the exact gap that let four
# offenders through a prefix-anchored version of this guard.
_ASCII_ONLY = re.compile(r"import[^\n]{0,40}\[A-Za-z0-9[^\]]*\]\+")

# ⚑ THE CORRECTED CLASS. `\w` is Unicode-aware in Python, so this admits `Añelé` and the `-` and
# `'` that Agda names legitimately carry.
_CANONICAL = re.compile(r"^\s*(?:open\s+import|import)\s+([\w.'-]+)", re.MULTILINE)

_IN_TREE = "Substrate"


def _findall(pattern: re.Pattern[str], text: str) -> set[str]:
    """Return a pattern's captures as strings, narrowed at the untyped boundary."""
    found: object = pattern.findall(text)
    if not isinstance(found, list):
        return set()
    return {str(m) for m in found}


def _lexer_modules(text: str) -> set[str]:
    """Return the in-tree modules THE LEXER sees imported in one source."""
    return {
        s.module
        for s in statements(mask_comments(text).split("\n"))
        if s.kind == "import" and s.module and s.module.startswith(_IN_TREE)
    }


class ImportNameCharClassTest(unittest.TestCase):
    """The broken class appears nowhere, and the corrected one loses nothing."""

    def test_no_ascii_only_import_capture_survives(self) -> None:
        """No tool source spells an ASCII-only import-name capture.

        Scenario: no tool captures an import name with an ASCII-only class
        """
        offenders = [
            f"{d}/{p.name}"
            for d in _SCANNED
            if (REPO / d).is_dir()
            for p in sorted((REPO / d).glob("*.py"))
            if _ASCII_ONLY.search(p.read_text(encoding="utf-8", errors="replace"))
        ]
        assert offenders == [], (
            f"an ASCII-only import-name class truncates unicode and hyphenated module names; "
            f"use a unicode-aware class instead: {offenders}"
        )

    def test_the_canonical_class_misses_nothing(self) -> None:
        """The corrected class captures every in-tree module the lexer sees.

        Scenario: the corrected import class captures every module the lexer sees

        ⚑ RUN OVER THE LIVE CORPUS, NOT A FIXTURE. The defect this replaces was invisible to every
        synthetic case its authors wrote, because the names that break an ASCII class are exactly
        the ones nobody thinks to invent.
        """
        files = agda_files(str(SRC))
        if not files:
            self.skipTest("no Agda corpus present")

        lost: set[str] = set()
        for path in files:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
            lost |= _lexer_modules(text) - _findall(_CANONICAL, text)

        assert lost == set(), (
            f"the corrected import class misses modules the lexer sees: {sorted(lost)}"
        )


if __name__ == "__main__":
    unittest.main()
