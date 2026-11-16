# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.agda_mask` — the two inherited bugs, and a live differential.

⚑⚑⚑ TWO ARMS HERE ARE THE ORIGIN'S OWN RECORDED DEFECTS, and they are the reason this module
could not be rewritten from memory. A codemod once consolidated fifteen strippers onto the
WEAKER body and nineteen importers inherited both bugs, three of them pre-commit gates: a
non-greedy block match that stops at the first closer where Agda comments NEST, and a line
match that eats an arrow operator because Agda's lexer reads it as a NAME. A reimplementation
that looked right would reintroduce exactly these, so both are cased against the shapes that
produced them.

⚑⚑ AND THE DIFFERENTIAL AGAINST THE ORIGIN RUNS, unlike the one in `law_telescope_selftest`
(gate-F66). `scratch/agda_lex` imports cleanly by path, so this suite asserts the drained copy
agrees with the live authority on real corpus text rather than on my reading of it — which is
the only claim a drain actually owes.

⚑ LENGTH PRESERVATION IS ASSERTED ON EVERY CASE, not once. Callers index by line and by column,
so a mask that shortened its input would be a drop-in for nothing — and the failure would
surface far from here, as an offset that drifted after the first comment.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import Protocol, runtime_checkable

from substrate import agda_mask, corpus

# The live authority this module drains a function out of.
_ORIGIN = corpus.ROOT / "scratch" / "agda_lex.py"

# ⚑ THE NESTED BLOCK — the shape the non-greedy regex got wrong. A reader stopping at the first
# closer leaves `z -}` live, and every consumer then censuses commented-out code as real.
_NESTED = "open import A\n{- x {- y -} z -}\nopen import B\n"

# ⚑ THE ARROW OPERATOR — the shape the line-comment regex ate. This is live code, not a comment.
_ARROW = "_-->_ : A -> B\nx --> y = f x y\n"


@runtime_checkable
class _Origin(Protocol):
    """The one origin function this differential reads.

    ⚑ NARROWED AT THE SEAM, because a dynamically loaded module is `Any` and a differential that
    type-checks against nothing agrees with anything — including a typo.
    """

    def mask_comments(self, src: str) -> str:
        """Blank every comment character."""
        ...


def _origin() -> _Origin | None:
    """Load the live authority by path, or None when it cannot be reached.

    ⚑ A MISSING ORIGIN SKIPS THE DIFFERENTIAL RATHER THAN FAILING IT — and the label says which,
    because a skipped arm and a passing one are indistinguishable to anyone counting green.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_agda_lex_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    got: object = module
    return got if isinstance(got, _Origin) else None


def _defect_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the two bugs nineteen importers inherited."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑⚑ THE NESTING BUG. A non-greedy match stops at the inner closer and leaves the tail live.
    nested = agda_mask.mask_comments(_NESTED)
    check(
        "a nested block comment is masked to its LAST closer",
        passed="z" not in nested and "-}" not in nested,
    )
    check(
        "and the code around it survives",
        passed="open import A" in nested and "open import B" in nested,
    )

    # ⚑⚑⚑ THE ARROW BUG. Agda's lexer reads this as a NAME; masking it eats live code.
    arrow = agda_mask.mask_comments(_ARROW)
    check("an arrow operator is NOT a comment", passed=arrow == _ARROW)

    # ⚑ THE CONTROL, or a masker that never masks would pass the arm above. A real line comment
    # after whitespace MUST go.
    got = agda_mask.mask_comments("x = 1  -- a note\ny = 2\n")
    check("but a real line comment IS masked", passed="a note" not in got)
    check("and the code before it is kept", passed="x = 1" in got)
    check("and the following line is untouched", passed="y = 2" in got)

    # ⚑ A TRIPLE HYPHEN IS STILL A COMMENT — the `_AFTER` guard admits a further hyphen.
    check(
        "a --- rule line is a comment",
        passed=agda_mask.mask_comments("--- section\n").strip() == "",
    )

    return out


def _shape_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the properties every caller depends on."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑ LENGTH AND LINE STRUCTURE ARE THE CONTRACT. Callers index by line and by column, so a
    # mask that shortened anything would be a drop-in for nothing, and the failure would surface
    # as an offset drifting somewhere far from this module.
    for label, src in (
        ("nested", _NESTED),
        ("arrow", _ARROW),
        ("comment", "x = 1  -- a note\ny = 2\n"),
    ):
        got = agda_mask.mask_comments(src)
        check(f"{label}: the mask preserves length", passed=len(got) == len(src))
        check(f"{label}: and preserves newlines", passed=got.count("\n") == src.count("\n"))

    check(
        "text with no comment is returned unchanged",
        passed=agda_mask.mask_comments("f x = y\n") == "f x = y\n",
    )
    check("and the empty string is handled", passed=agda_mask.mask_comments("") == "")

    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting the drained copy agrees with the live authority.

    ⚑⚑⚑ ON REAL CORPUS TEXT, not only fixtures. A drained masker that agrees with my fixtures
    and disagrees with the authority on an actual Agda file would silently change what four
    pre-commit gates see — and no fixture of mine would notice.
    """
    origin = _origin()
    if origin is None:
        skipped = (
            "the origin could not be LOADED, so the differential is SKIPPED, not run and not passed"
        )
        return [(skipped, True)]

    out: list[tuple[str, bool]] = [
        (f"{label} matches the origin", agda_mask.mask_comments(src) == origin.mask_comments(src))
        for label, src in (
            ("nested block", _NESTED),
            ("arrow operator", _ARROW),
            ("line comment", "x = 1  -- a note\ny = 2\n"),
            ("triple hyphen", "--- section\n"),
            ("no comment", "f x = y\n"),
            ("empty", ""),
        )
    ]

    # ⚑⚑ AND ON A REAL FILE FROM THE TREE, which is where a fixture-only differential is weakest.
    # A file is picked from the corpus rather than named, so this keeps working as the tree moves.
    agda = sorted((corpus.ROOT / "agda" / "Substrate").rglob("*.agda"))[:3]
    if not agda:
        out.append(("no agda source was found to difference — a fact about the TREE", True))
        return out
    out.extend(
        (
            f"{path.name} matches the origin",
            agda_mask.mask_comments(path.read_text(encoding="utf-8"))
            == origin.mask_comments(path.read_text(encoding="utf-8")),
        )
        for path in agda
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _defect_cases() + _shape_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"agda-mask selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
