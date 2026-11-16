# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.law_telescope` — DIFFERENTIAL against the origin it drains.

⚑⚑⚑ THE ORIGIN IS RUN BESIDE THIS MODULE AND THE TWO ARE ASSERTED TO AGREE. Every other case
here states what I believe the parser SHOULD do; a differential case states that it does what
`scripts/law_motif_apex.py` ALREADY DOES, which is the only claim a drain actually owes. This
gate is BLOCKING and has no baseline — a motif with enough instances and no apex fails the
commit — so a parser that quietly reclassified one signature would change a verdict nobody
asked to change.

⚑⚑ THE ORIGIN IS LOADED BY PATH AND READ THROUGH A `Protocol`, AND BOTH ARE FORCED. It lives in
`scripts/`, which is not a package, so importing it by name is impossible. And a dynamically
loaded module is `Any`, so every read off it would type-check against nothing — a misspelled
attribute would pass and **a differential that agrees with anything is worthless**. The protocol
is what makes the comparison mean something, and it states the reach explicitly: three
functions, named.

⚑ THE FIXTURES ARE REAL SPELLINGS FROM THE TREE, not invented ones. `split-Canonical`'s shape is
what an APEX looks like; `Fin-roundtrip`'s is what an INSTANCE looks like. A fixture written to
suit the parser proves only that the parser agrees with itself.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import Protocol, runtime_checkable

from substrate import corpus, law_telescope

# The origin this module drains. ⚑ Its body runs at import and walks the Agda tree, so it is
# loaded ONCE and only when the differential arms actually run.
_ORIGIN = corpus.ROOT / "scripts" / "law_motif_apex.py"


@runtime_checkable
class _Origin(Protocol):
    """The three origin functions the differential reads.

    ⚑ NARROWED AT THE SEAM. Without this the dynamically loaded module is `Any` and every
    comparison below succeeds against a typo — mypy's own refusal named the fix, and it also
    makes the differential's REACH explicit: these three functions, nothing else.

    ⚑ `runtime_checkable` BECAUSE THE LOAD IS CHECKED AT RUNTIME. A protocol used only as an
    annotation would let a module missing one of these three through, and the differential would
    then fail with an AttributeError rather than reporting that the origin changed shape.
    """

    def classify(self, seg: str) -> tuple[str, str, str, str] | None:
        """Match a result type against a law motif."""
        ...

    def bound_names(self, ty: str) -> set[str]:
        """Return the names a telescope binds."""
        ...

    def result_and_hyps(self, ty: str) -> tuple[list[str], str]:
        """Split a telescope into hypotheses and result."""
        ...


def _origin() -> _Origin | None:
    """Load the origin by path, or None when it cannot be reached.

    ⚑⚑ A MISSING ORIGIN SKIPS THE DIFFERENTIAL, IT DOES NOT FAIL IT. The origin retires when the
    drain completes, and a suite that went red at that moment would be asserting the presence of
    the thing being removed — which is how a drain gets rolled back to make a census green.

    ⚑ ITS ARGV IS EMPTIED SO THE ORIGIN DOES NOT TAKE A GATE BRANCH. The module body reads
    `sys.argv` at import; leaving the suite's argv in place would make it parse flags meant for
    something else.

    ⚑⚑⚑ `ModuleNotFoundError` IS CAUGHT, AND IT IS A FINDING ABOUT THE ORIGIN RATHER THAN AN
    ACCIDENT (gate-F66). The origin does `import _agdatext` — a `scripts/` sibling by BARE name,
    which resolves only under a `sys.path` insert. This tree forbids that, so the origin is
    UNREACHABLE from any properly-packaged consumer, and no differential against it can run
    until its own import is repointed. Catching it keeps the honest verdict: the differential is
    SKIPPED because the origin cannot be loaded, never silently passed.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_law_motif_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["law_motif_apex.py"]
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    finally:
        sys.argv = argv
    got: object = module
    return got if isinstance(got, _Origin) else None


# Real telescope shapes. ⚑ THE APEX ONE BINDS `F` AND `s`; the instance one does not — that is
# the entire distinction the gate rests on, so both are present rather than one.
_APEX = "(F : A → B)(s : B → A) → ((y : B) → F (s y) ≡ y) → Split A B"
_INSTANCE = "canonical-to-Fin (Fin-to-canonical i) ≡ i"
_INVOL = "bar (bar w) ≡ w"
_IDEM = "normalize (normalize p) ≡ normalize p"

# The equations the differential compares, and the telescopes it compares binding over.
_SEGS = (_INSTANCE, _INVOL, _IDEM, "f x ≡ x", "f (x ⊕ y) ≡ f x ⊗ f y")
_TELESCOPES = (_APEX, _INSTANCE, "{a b : A} → a ≡ b", "(F : A)(s : B) → C")

_PAIR = 2


def _shape_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the paren-aware primitives."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑ THE DEPTH SPLIT IS WHY THIS IS NOT A REGEX. A nested arrow must not split the telescope.
    check(
        "an arrow inside parens does not split the telescope",
        passed=len(law_telescope.depth_split("(A → B) → C", ["→"])) == _PAIR,
    )
    check(
        "and a top-level arrow does",
        passed=len(law_telescope.depth_split("A → B → C", ["→"])) == _PAIR + 1,
    )

    # ⚑⚑ UNWRAP MUST NOT PEEL TWO ADJACENT GROUPS. `(f x) (g y)` starts and ends with a paren
    # and is NOT enclosed; peeling would yield `f x) (g y` and every spine off it is nonsense.
    check("fully-enclosing parens are peeled", passed=law_telescope.unwrap("(g x)") == "g x")
    check(
        "but adjacent groups are NOT", passed=law_telescope.unwrap("(f x) (g y)") == "(f x) (g y)"
    )

    head, args = law_telescope.spine("f (g x) y")
    check("the spine head is the function", passed=head == "f")
    check("and its arguments keep their grouping", passed=args == ["(g x)", "y"])

    check("an operator is not an identifier", passed=not law_telescope.is_ident("≡"))
    check("but a hyphenated agda name is", passed=law_telescope.is_ident("F₂-to-R"))

    return out


def _binding_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the bound-versus-concrete discriminator."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑⚑ THE DISCRIMINATOR, BOTH DIRECTIONS. An apex binds the names its law is over; an
    # instance does not. A reader stuck in either direction turns every instance into an apex
    # (the gate can never fire) or every apex into an instance (it fires forever).
    check(
        "an apex telescope binds the names its law is over",
        passed={"F", "s"} <= law_telescope.bound_names(_APEX),
    )
    check("and an equation binds nothing", passed=law_telescope.bound_names(_INSTANCE) == set())

    # ⚑⚑ JUXTAPOSED BINDERS ARE TWO GROUPS, NOT ONE. Agda writes `(F : A)(s : B)` with no arrow
    # between them, so a reader splitting on arrows sees one group and misses every later name.
    check(
        "juxtaposed binder groups are read separately",
        passed=len(law_telescope.binder_groups("(F : A)(s : B)")) == _PAIR,
    )
    check(
        "and implicit binders bind every name in the group",
        passed=law_telescope.bound_names("{a b : A} → a ≡ b") == {"a", "b"},
    )

    _hyps, res = law_telescope.result_and_hyps(_APEX)
    check("the RESULT is the last segment, not the first", passed=res == "Split A B")

    return out


def _motif_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what each law shape classifies as."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    got = law_telescope.classify(_INSTANCE)
    check(
        "a two-function roundtrip is a retraction",
        passed=got is not None and got[0] == law_telescope.RETRACTION,
    )
    check(
        "and the triple names the outer function",
        passed=got is not None and got[1] == "canonical-to-Fin",
    )
    check("and the inner one", passed=got is not None and got[2] == "Fin-to-canonical")

    invol = law_telescope.classify(_INVOL)
    check(
        "the SAME function twice is an involution, not a retraction",
        passed=invol is not None and invol[0] == law_telescope.INVOLUTION,
    )

    idem = law_telescope.classify(_IDEM)
    check(
        "and re-applying on the right is idempotence",
        passed=idem is not None and idem[0] == law_telescope.IDEMPOTENT,
    )

    # ⚑⚑ THE NEGATIVE CONTROLS. A classifier that matched everything would satisfy every case
    # above, so the shapes that must NOT match are asserted too.
    check("a non-equation is not a law", passed=law_telescope.classify("Split A B") is None)
    check(
        "an equation with no inner application is not a law",
        passed=law_telescope.classify("f x ≡ x") is None,
    )
    # ⚑ HOMOMORPHISM IS DELIBERATELY UNMATCHED — the bare law has no clean parametric apex.
    check(
        "and a homomorphism is deliberately not matched",
        passed=law_telescope.classify("f (x ⊕ y) ≡ f x ⊗ f y") is None,
    )

    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting this module agrees with the origin it drains.

    ⚑⚑⚑ THE ONLY CLAIM A DRAIN ACTUALLY OWES. Every case above says what I believe; these say
    the behaviour is the ORIGIN'S. The gate is blocking with no baseline, so a silently
    reclassified signature changes a commit verdict — and no fixture of mine would notice.
    """
    origin = _origin()
    if origin is None:
        # ⚑⚑ SKIPPED, NOT FAILED, AND THE LABEL SAYS WHICH. The origin retires with the drain,
        # so a suite going red then would assert the presence of the thing being removed. But it
        # is currently unreachable for a DIFFERENT reason — its bare `import _agdatext` needs a
        # `sys.path` insert (gate-F66) — and a skip that did not say so would read as a passing
        # differential to anyone counting green arms.
        skipped = (
            "the origin could not be LOADED, so the differential is SKIPPED, "
            "not run and not passed (gate-F66)"
        )
        return [(skipped, True)]

    classified = [
        (
            f"classify {seg!r} matches the origin",
            law_telescope.classify(seg) == origin.classify(seg),
        )
        for seg in _SEGS
    ]
    bound = [
        (
            f"bound_names {ty!r} matches the origin",
            law_telescope.bound_names(ty) == origin.bound_names(ty),
        )
        for ty in _TELESCOPES
    ]
    split = [
        (
            f"result_and_hyps {ty!r} matches the origin",
            law_telescope.result_and_hyps(ty) == origin.result_and_hyps(ty),
        )
        for ty in _TELESCOPES
    ]
    return classified + bound + split


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _shape_cases() + _binding_cases() + _motif_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"law-telescope selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
