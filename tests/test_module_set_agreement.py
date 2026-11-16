# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Every route to "the set of Agda modules" must return the same set, over the LIVE tree.

⚑⚑ EXTRACTED FROM `test_rederive_agreement.py` UNDER Ⓝ71g″ ⟡drain-test-rederive, AND MOVED RATHER
THAN DELETED. The near-twin is real and it is a DIFFERENT claim: `tests/test_agda_lex_paths.py`
pins `agda_files()`'s behaviour — the `_build` exclusion, the root parameter, the sort — against
SYNTHETIC tempdirs it constructs itself. That asks *does the authority behave correctly*. This asks
*do the routes actually in use agree on the corpus that actually exists*, and a synthetic fixture
cannot answer it, because the divergence this class names appears only when a real tree grows a
file the fixture's author did not imagine. Both are needed; neither substitutes.

⚑⚑⚑ THE INCIDENT THAT STARTED THE WHOLE CLASS. The gates enumerated FILES (os.walk / glob) and saw
one count; the analysis tools enumerated by HEADER-PARSING and discarding unparseable files, and
saw a smaller one. 149 modules — 5.4% — were invisible to every analysis, and `audit_import_reach`
printed its module count with no way for a reader to know it was incomplete. **Gates report a BIT;
reports report a NUMBER, so the human-facing layer was quietly the less trustworthy one.**

⚑⚑ AND THE AGREEMENT IS CURRENTLY LUCK, WHICH IS THE POINT OF ASSERTING IT. Dozens of files
enumerate the corpus three ways — `glob **`, `os.walk` + `endswith`, `pathlib.rglob` — and most of
them carry no `_build` filter. That is harmless only because `agda/_build/` holds `.agdai` files
and no `.agda` TODAY. The first `.agda` to land under `_build` — a fixture, a vendored copy, a
generated module — splits the guarded routes from the unguarded ones; three pre-commit gates sit on
the unguarded side, so their census would inflate while the build generator's stayed put. A
gate-versus-gate divergence, armed and waiting. This test is the tripwire.

⚑⚑ THE INSTRUMENT IS RUNNING BOTH ROUTES AND DIFFING THE SETS, and no cheaper thing substitutes. A
structural-similarity instrument is blind to this class BY CONSTRUCTION: `os.walk` plus
`endswith('.agda')` and `Path.rglob('*.agda')` share no tokens, so an empty similarity result is
not evidence of agreement. `scripts/check_rederive_ratchet` COUNTS how many sites spell each route
and censuses them as debt — counting three routes is not reconciling three routes, and it is
exactly the blindness described above.

⚑ THE THREE ROUTES ARE SPELLED OUT HERE RATHER THAN DELEGATED, and that is deliberate in a file
whose other instinct is always to import the authority. The claim IS that three independent
spellings agree; routing them all through one helper would assert that a function equals itself.
The authority is still present as the fourth party — `agda_files` is what the guarded callers use,
and it is compared against the hand-spelled routes.

⚑ THE SECOND CASE IS A DIFFERENT KIND OF AGREEMENT: a file's DECLARED header against its
PATH-DERIVED name. Path-derivation is what the build generator trusts to key its targets, so a file
whose header disagreed with its location would make the build key on a name Agda does not use.
Nothing else in the tree pairs these two functions over the corpus — the lexer's own selftest spot-
checks a single hardcoded file.

⚑ THE HELPERS ARE IMPORTED AS BARE MODULE NAMES, typed through `stubs/agda_lex.pyi` (written for
this drain). `tests/__init__.py` puts `scratch/` on `sys.path` anchored on its own file, so the name
resolves regardless of cwd, and a stub is keyed on the module name it declares.

⚑ THE `Scenario:` LINES SIT BELOW EACH SUMMARY LINE. `D400`/`D415` require a first docstring line
ending in a period, while `gherkin_scan` captures to the closing quotes — so a period on the
`Scenario:` line becomes part of the scenario NAME and breaks the match against `features/`.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from agda_lex import agda_files, module_name_of, module_path

REPO = Path(__file__).resolve().parent.parent
AGDA = REPO / "agda"
SRC = AGDA / "Substrate"

# The generated tree the guarded routes exclude and the unguarded ones do not.
_BUILD = "_build"

_SUFFIX = "*.agda"


def _by_glob() -> set[Path]:
    """Enumerate by recursive glob — the spelling most gates use."""
    return {p.absolute() for p in SRC.glob(f"**/{_SUFFIX}") if _BUILD not in p.parts}


def _by_walk() -> set[Path]:
    """Enumerate by `os.walk` plus a suffix test — the spelling the generator uses."""
    found: set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(SRC):
        dirnames[:] = [d for d in dirnames if d != _BUILD]
        found |= {(Path(dirpath) / f).absolute() for f in filenames if f.endswith(".agda")}
    return found


def _by_rglob() -> set[Path]:
    """Enumerate by `pathlib.rglob` — the third spelling in circulation."""
    return {p.absolute() for p in SRC.rglob(_SUFFIX) if _BUILD not in p.parts}


def _by_authority() -> set[Path]:
    """Enumerate through THE authority — what a compliant caller gets."""
    return {Path(p).absolute() for p in agda_files(str(SRC))}


class ModuleSetAgreementTest(unittest.TestCase):
    """The enumeration routes agree, and every header matches its own path."""

    def test_walk_and_glob_and_rglob_agree(self) -> None:
        """All three hand-spelled routes and the authority return one set.

        Scenario: every enumeration route returns the same module set

        ⚑ THE AUTHORITY IS COMPARED TOO, NOT ASSUMED CORRECT. If it ever diverged from the routes
        its callers were converted FROM, the conversion would have silently changed what those
        callers see — which is the failure the authority exists to prevent, occurring in it.
        """
        by_glob = _by_glob()
        if not by_glob:
            self.skipTest("no Agda corpus present")

        assert by_glob == _by_walk(), "glob and os.walk disagree about the corpus"
        assert by_glob == _by_rglob(), "glob and rglob disagree about the corpus"
        assert by_glob == _by_authority(), (
            "the enumeration authority disagrees with the routes its callers were converted from"
        )

    def test_header_and_path_derivation_agree(self) -> None:
        """Every file's declared module header equals its path-derived name.

        Scenario: a module's declared header equals its path-derived name

        ⚑ A FILE WITH NO PARSEABLE HEADER IS SKIPPED, NOT FAILED. Absence of a declaration is a
        different fact from a declaration that disagrees, and conflating them would make this case
        fail for a reason it does not name.
        """
        files = agda_files(str(SRC))
        if not files:
            self.skipTest("no Agda corpus present")

        disagreeing: list[tuple[str, str, str]] = []
        for path in files:
            declared = module_name_of(Path(path).read_text(encoding="utf-8", errors="replace"))
            derived = module_path(path, str(AGDA))
            if declared and declared != derived:
                disagreeing.append((str(Path(path).relative_to(REPO)), declared, derived))

        assert disagreeing == [], (
            f"these files declare a module name their location does not derive, so the build "
            f"would key targets on a name Agda does not use: {disagreeing}"
        )


if __name__ == "__main__":
    unittest.main()
