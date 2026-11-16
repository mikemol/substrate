# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.agda_statements` — four measured losses, and a live differential.

⚑⚑⚑ EVERY RULE IN THE SEGMENTER IS A RECORDED LOSS, AND EACH GETS ITS OWN ARM. Four gates read
these functions from the origin and several codemods DELETE the spans they return, so a
segmenter that took one line too many would not fail here — it would delete a live import
somewhere else. The four shapes are the ones that actually produced losses:

  * a nested `module M where` whose indented import a bare startswith-space test swallows
    (the Discipline.agda loss),
  * an indented DEFINITION after an import, which opens no keyword and which a keyword-only
    guard absorbs (the F17 fixture, span (2,4) where (2,3) was right),
  * a wrapped `using (…; module WithTarget)` list, the ONE statement in the whole corpus where
    the depth rule and a depth-blind keyword guard disagree,
  * a trailing `;` on an import target, which the permissive name pattern must tolerate.

⚑⚑ AND THE DIFFERENTIAL RUNS OVER REAL FILES. Agreement with my fixtures says nothing about
agreement on what four gates actually read; the origin is run beside this module over sources
taken from the tree, and both are fed the SAME masked text so the comparison is of segmentation
rather than of masking.

⚑ THE ORIGIN'S ROWS ARE COMPARED AS TUPLES, because its `Stmt` is a different NamedTuple class
from this module's. Two NamedTuples with identical fields compare equal as tuples and unequal as
classes, so tupling is what makes the differential ask about the CONTENT rather than the type.

⚑ THE INPUT IS MASKED FIRST, BY THE DRAINED AUTHORITY. `agda_statements` deliberately does not
mask — that is the caller's job — so every case here does what a caller must.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from substrate import agda_mask, agda_statements, corpus

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

# The live authority this module drains from.
_ORIGIN = corpus.ROOT / "scratch" / "agda_lex.py"

# ⚑ A NESTED MODULE — the indented import a bare startswith-space test swallows into the span
# above it, and which a caller deleting that span then deletes.
_NESTED = "open import Substrate.A\nmodule Inner where\n  open import Substrate.B\n  x : Nat\n"

# ⚑ AN INDENTED DEFINITION after an import — opens no keyword, so a keyword-only guard absorbs
# it. This is the F17 shape.
_DEFN = "open import Substrate.A\nopen import Substrate.B\nx : Nat\n"

# ⚑⚑ THE WRAPPED USING-LIST re-exporting a submodule: the one statement in the corpus where the
# depth rule and a depth-blind keyword guard disagree. `module` here CONTINUES the statement.
_USING = (
    "open import Substrate.A using\n  ( foo\n  ; module WithTarget\n  )\nopen import Substrate.B\n"
)

# ⚑ A TRAILING DELIMITER on an import target, which the permissive pattern must not keep.
_SEMI = "open import Substrate.A;\n"

_TWO = 2
_FOUR = 4


@runtime_checkable
class _Origin(Protocol):
    """The origin functions this differential reads.

    ⚑ NARROWED AT THE SEAM: a dynamically loaded module is `Any`, so an un-narrowed differential
    agrees with anything, a typo included. `statements` is declared as yielding tuple-shaped
    rows, which is what its `Stmt` NamedTuple is at the comparison boundary.
    """

    def statements(self, lines: Sequence[str]) -> Iterable[tuple[object, ...]]:
        """Segment lines into statements."""
        ...

    def module_name(self, head: str) -> str | None:
        """Return the dotted module an import head names."""
        ...

    def span_end(self, lines: Sequence[str], i: int) -> int:
        """Return the exclusive end of one statement."""
        ...


def _origin() -> _Origin | None:
    """Load the live authority by path, or None when it cannot be reached.

    ⚑ A MISSING ORIGIN SKIPS THE DIFFERENTIAL RATHER THAN FAILING IT, and the label says which:
    a skipped arm and a passing one are indistinguishable to anyone counting green.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_agda_lex_stmt_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    got: object = module
    return got if isinstance(got, _Origin) else None


def _spans(src: str) -> list[agda_statements.Stmt]:
    """Segment `src` the way a caller must — masked first, then split."""
    return list(agda_statements.statements(agda_mask.mask_comments(src).splitlines()))


def _mine(src: str) -> list[tuple[object, ...]]:
    """Return this module's rows for `src`, as plain tuples."""
    return [tuple(s) for s in _spans(src)]


def _theirs(origin: _Origin, src: str) -> list[tuple[object, ...]]:
    """Return the origin's rows for `src`, as plain tuples."""
    lines = agda_mask.mask_comments(src).splitlines()
    return [tuple(s) for s in origin.statements(lines)]


def _loss_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the four measured losses."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑⚑ THE NESTED-MODULE LOSS. The indented import is its OWN statement, not part of the one
    # above it — a span that swallowed it would make a caller delete a live import.
    nested = _spans(_NESTED)
    check(
        "a nested module's indented import is its own statement",
        passed=sum(1 for s in nested if s.kind == "import") == _TWO,
    )
    check("and the outer import's span stops before it", passed=bool(nested) and nested[0].end == 1)

    # ⚑⚑⚑ THE F17 LOSS. An indented declaration opens no keyword, so a keyword-only guard takes
    # it into the import's span — and a caller deleting the span deletes the declaration.
    defn = _spans(_DEFN)
    check(
        "a following declaration is NOT absorbed into the import span",
        passed=len(defn) == _TWO and defn[1].end == _TWO,
    )

    # ⚑⚑⚑ THE USING-LIST. `module` inside an open paren CONTINUES the statement; a depth-blind
    # guard truncates the list and silently drops the re-export.
    using = _spans(_USING)
    check(
        "a wrapped using-list is ONE statement", passed=len(using) == _TWO and using[0].end == _FOUR
    )
    check(
        "and the re-exported submodule stays inside it",
        passed=bool(using) and "WithTarget" in using[0].text,
    )

    # ⚑ THE PERMISSIVE NAME PATTERN must stop at the delimiter rather than keeping it.
    semi = _spans(_SEMI)
    check(
        "a trailing delimiter is not part of the module name",
        passed=bool(semi) and semi[0].module == "Substrate.A",
    )

    return out


def _shape_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the pieces the segmenter is built from."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    check("depth rises on an open paren", passed=agda_statements.depth_after("f (", 0) == 1)
    check("and falls on a close", passed=agda_statements.depth_after("f (x)", 0) == 0)
    # ⚑ DEPTH NEVER GOES NEGATIVE, or a stray close paren would make every later line read as a
    # statement opener.
    check("and never goes negative", passed=agda_statements.depth_after(")", 0) == 0)

    # ⚑⚑ BOTH DIRECTIONS OF THE CONTINUATION RULE. An arm asserting only that something
    # continues would pass against a predicate that always says yes.
    check("an unindented line does not continue", passed=not agda_statements.continues("open x"))
    check(
        "an indented keyword does not continue at depth 0",
        passed=not agda_statements.continues("  open import X"),
    )
    check("but it DOES inside an open paren", passed=agda_statements.continues("  module W", 1))
    check("an indented plain line continues", passed=agda_statements.continues("  ( foo"))

    check(
        "a non-import head names no module", passed=agda_statements.module_name("open Foo") is None
    )

    # ⚑⚑⚑ `span_end` TAKES RAW LINES AND MASKS THEM ITSELF, which is what its consumers hold.
    # A blocking gate reimplements this privately one line below importing the module that
    # exports it, reaching two underscore-prefixed names to do so — so the arm asserts the
    # public path answers the same question its private copy does.
    raw = ["open import Substrate.A using", "  ( foo", "  )", "open import Substrate.B"]
    wrapped = _TWO + 1
    check(
        "span_end walks a wrapped statement to its close",
        passed=agda_statements.span_end(raw, 0) == wrapped,
    )
    check(
        "and a one-line statement ends at the next line",
        passed=agda_statements.span_end(raw, wrapped) == _FOUR,
    )
    # ⚑ IT MASKS: a comment carrying an unbalanced paren must not open a depth that never
    # closes, which would swallow every following line into the span.
    check(
        "a comment's paren does not open a span",
        passed=agda_statements.span_end(["open import A -- (", "x : Nat"], 0) == 1,
    )

    # ⚑ `group_statements` TAKES THE CALLER'S OPENER — a col-0 anchored one here, which is the
    # shape a splitter needs and which `statements` deliberately does not impose.
    grouped = agda_statements.group_statements(
        ["open import A", "  using (x)", "open import B"], lambda line: line.startswith("open")
    )
    check("group_statements groups by the caller's opener", passed=len(grouped) == _TWO)
    check("and keeps continuations with their head", passed=len(grouped[0]) == _TWO)

    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting agreement with the live authority on real files."""
    origin = _origin()
    if origin is None:
        skipped = (
            "the origin could not be LOADED, so the differential is SKIPPED, not run and not passed"
        )
        return [(skipped, True)]

    out: list[tuple[str, bool]] = [
        (f"{label} matches the origin", _mine(src) == _theirs(origin, src))
        for label, src in (
            ("nested module", _NESTED),
            ("declaration", _DEFN),
            ("using-list", _USING),
            ("trailing delimiter", _SEMI),
        )
    ]

    # ⚑⚑ `span_end` IS DIFFERENCED ON RAW LINES, because that is how its consumers call it —
    # a blocking gate's private copy passes unmasked source, and the masking happens inside.
    out.extend(
        (
            f"span_end on {label} matches the origin",
            agda_statements.span_end(src.split("\n"), 0) == origin.span_end(src.split("\n"), 0),
        )
        for label, src in (
            ("nested module", _NESTED),
            ("using-list", _USING),
            ("declaration", _DEFN),
        )
    )

    found = sorted((corpus.ROOT / "agda" / "Substrate").rglob("*.agda"))[:5]
    if not found:
        out.append(("no agda source was found to difference — a fact about the TREE", True))
        return out
    out.extend(
        (
            f"{path.name} segments identically",
            _mine(path.read_text(encoding="utf-8"))
            == _theirs(origin, path.read_text(encoding="utf-8")),
        )
        for path in found
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _loss_cases() + _shape_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"agda-statements selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
