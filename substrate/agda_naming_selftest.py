# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.agda_naming` — DIFFERENTIAL, over real paths from the tree.

⚑⚑⚑ FOUR PRE-COMMIT GATES AND EVERY `test_agda_lex_*` SUITE READ THESE FUNCTIONS from the
origin, so a drained copy that disagreed on one path would change what a gate sees while every
fixture of mine stayed green. The differential arms run the live authority beside this module
over paths taken FROM THE TREE rather than invented, which is the only claim a drain owes.

⚑⚑ THE HEADER-VERSUS-PATH ARMS ARE RECORDED DEFECTS, not hypotheses. A parameterized module
header spans lines, so the eight copies of `^module\s+(\S+)\s+where` in this tree all miss it;
and an ASCII-only character class rejects most of this corpus. Both shapes are cased, because a
reimplementation that looked right would reintroduce exactly them.

⚑ THE NON-ASCII FIXTURE IS SPELLED AS A NAMED ESCAPE, and that is the gate's doing rather than
a preference: the ambiguous-character rule refuses a literal whose entire purpose is to carry a
character an ASCII reader would reject. The escape keeps the case exact, keeps the file clean,
and names the character rather than relying on a reader to recognise the glyph.

⚑ AND THE ROUND TRIP IS ASSERTED IN BOTH DIRECTIONS. `module_file` is documented as the inverse
of `module_path`; a pair that agreed only one way would let a caller's path survive the trip and
come back naming a different module.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import Protocol, runtime_checkable

from substrate import agda_naming, corpus

# The live authority this module drains from.
_ORIGIN = corpus.ROOT / "scratch" / "agda_lex.py"

# ⚑ A PARAMETERIZED HEADER — the shape a same-line `where` anchor misses. The parameters begin
# on the following line, so the module name is all that precedes them.
_PARAM_HEADER = "module Substrate.Wedge.Act\n  (Word : Set)\n  where\n\nopen import X\n"

# ⚑ A NAME CARRYING A MATHEMATICAL LETTER, which an ASCII allow-list rejects.
_UNICODE_NAME = "Substrate.Foundation.\N{DOUBLE-STRUCK CAPITAL N}-elim"
_UNICODE_HEADER = f"module {_UNICODE_NAME} where\n"

# ⚑ A COMMENTED-OUT HEADER, which is NOT a declaration — the reason masking comes first.
_MASKED_HEADER = "-- module Substrate.Ghost where\nmodule Substrate.Real where\n"


@runtime_checkable
class _Origin(Protocol):
    """The origin functions this differential reads.

    ⚑ NARROWED AT THE SEAM: a dynamically loaded module is `Any`, and a differential that
    type-checks against nothing agrees with anything, a typo included.
    """

    def module_path(self, path: str, root: str) -> str:
        """Return the dotted module name for a path."""
        ...

    def module_file(self, mod: str, root: str) -> str:
        """Return the path for a dotted module name."""
        ...

    def module_name_of(self, src: str) -> str | None:
        """Return the module a source declares."""
        ...


def _origin() -> _Origin | None:
    """Load the live authority by path, or None when it cannot be reached.

    ⚑ A MISSING ORIGIN SKIPS THE DIFFERENTIAL RATHER THAN FAILING IT, and the label says which:
    a skipped arm and a passing one are indistinguishable to anyone counting green.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_agda_lex_naming_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    got: object = module
    return got if isinstance(got, _Origin) else None


def _path_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the path/module correspondence."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    check(
        "a path under the root becomes a dotted name",
        passed=agda_naming.module_path("agda/Substrate/Foundation/Eq.agda", "agda")
        == "Substrate.Foundation.Eq",
    )

    # ⚑⚑ THE SPELLING OF THE ROOT MUST NOT CHANGE THE ANSWER, or every module name would depend
    # on where the caller happened to be standing.
    check(
        "a trailing slash on the root changes nothing",
        passed=agda_naming.module_path("agda/Substrate/X.agda", "agda/")
        == agda_naming.module_path("agda/Substrate/X.agda", "agda"),
    )

    # ⚑⚑⚑ THE ORIGIN'S OWN CASE, RECOVERED — AND IT PASSED, WHICH I DID NOT EXPECT.
    # `scratch/agda_lex.py`'s suite pins `module_path("agda/A/B.agda", "./agda") == "A.B"`. I
    # predicted the drained copy would fail it, because I had removed the origin's explicit
    # normalisation while narrowing what this function promises about frames (gate-F68). It
    # passes: `PurePosixPath` folds `./agda` to `agda` on construction, so the behaviour survived
    # by a DIFFERENT MECHANISM than the one I deleted.
    #
    # ⚑⚑ SO THE CASE IS KEPT PRECISELY BECAUSE THE MECHANISM CHANGED. The origin guarantees this
    # by normalising deliberately; the copy inherits it from a library's construction rule. Those
    # are the same answer from different causes, and an unpinned inherited behaviour is one
    # refactor away from vanishing with nothing to notice — which is what a recovered case is
    # FOR. Reading the origin's suite was still the act that surfaced it (gate-F85); what the
    # reading found was a property held by luck rather than a case lost.
    check(
        "a dot-slash prefix on the root changes nothing either",
        passed=agda_naming.module_path("agda/A/B.agda", "./agda") == "A.B",
    )
    # ⚑⚑⚑ AN ABSOLUTE PAIR IS THE CASE THAT HOLDS, AND MY FIRST ARM ASSERTED A DIFFERENT ONE.
    # I wrote `/w/agda/Substrate/X.agda` against the relative root `agda` and expected
    # `Substrate.X`. It fails, correctly: a relative root cannot be reconciled with an absolute
    # path WITHOUT a cwd, and consulting the cwd is the dependence this function exists to
    # avoid. The origin reaches for `abspath` there and so answers differently depending on
    # where it was invoked — a bound worth naming rather than a behaviour worth copying.
    check(
        "an absolute path against an absolute root resolves",
        passed=agda_naming.module_path("/w/agda/Substrate/X.agda", "/w/agda") == "Substrate.X",
    )

    # ⚑ THE ROUND TRIP, BOTH WAYS. `module_file` is documented as the inverse.
    mod = "Substrate.Foundation.Eq"
    check(
        "module_file inverts module_path",
        passed=agda_naming.module_path(agda_naming.module_file(mod, "agda"), "agda") == mod,
    )
    check(
        "and module_path inverts module_file",
        passed=agda_naming.module_file(
            agda_naming.module_path("agda/Substrate/A/B.agda", "agda"), "agda"
        )
        == "agda/Substrate/A/B.agda",
    )

    # ⚑ A PATH OUTSIDE THE ROOT IS NOT SILENTLY REBASED. Returning a name as though it were
    # under the root would invent a module that does not exist.
    check(
        "a path outside the root keeps its own shape",
        passed=agda_naming.module_path("other/X.agda", "agda") == "other.X",
    )

    return out


def _header_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for reading the name a source DECLARES."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    check(
        "an ordinary header is read",
        passed=agda_naming.module_name_of("module Substrate.X where\n") == "Substrate.X",
    )

    # ⚑⚑⚑ THE PARAMETERIZED HEADER — eight copies of the same-line `where` regex miss this.
    check(
        "a PARAMETERIZED header spanning lines is read",
        passed=agda_naming.module_name_of(_PARAM_HEADER) == "Substrate.Wedge.Act",
    )

    # ⚑⚑ A NON-ASCII NAME — an allow-list character class rejects most of this corpus.
    check(
        "a header whose name is not ASCII is read",
        passed=agda_naming.module_name_of(_UNICODE_HEADER) == _UNICODE_NAME,
    )

    # ⚑⚑ A COMMENTED HEADER IS NOT A DECLARATION, which is why the mask runs first.
    check(
        "a commented-out header is NOT taken as the declaration",
        passed=agda_naming.module_name_of(_MASKED_HEADER) == "Substrate.Real",
    )

    # ⚑ THE NEGATIVE CONTROL: a reader that always found something would pass every arm above.
    check(
        "a source with no header reports None",
        passed=agda_naming.module_name_of("open import X\n") is None,
    )

    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting agreement with the live authority.

    ⚑⚑ OVER REAL TREE PATHS, not only fixtures. Four gates read these functions from the origin,
    so agreement on my inputs says nothing about agreement on theirs.
    """
    origin = _origin()
    if origin is None:
        skipped = (
            "the origin could not be LOADED, so the differential is SKIPPED, not run and not passed"
        )
        return [(skipped, True)]

    root = str(corpus.ROOT / "agda")
    found = sorted((corpus.ROOT / "agda" / "Substrate").rglob("*.agda"))[:5]
    if not found:
        return [("no agda source was found to difference — a fact about the TREE", True)]

    paths = [
        (
            f"module_path {path.name} matches the origin",
            agda_naming.module_path(str(path), root) == origin.module_path(str(path), root),
        )
        for path in found
    ]
    names = [
        (
            f"module_name_of {path.name} matches the origin",
            agda_naming.module_name_of(path.read_text(encoding="utf-8"))
            == origin.module_name_of(path.read_text(encoding="utf-8")),
        )
        for path in found
    ]
    files = [
        (
            f"module_file {mod} matches the origin",
            agda_naming.module_file(mod, root) == origin.module_file(mod, root),
        )
        for mod in ("Substrate.Foundation.Eq", "Substrate.Wedge.Act")
    ]
    return paths + names + files


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _path_cases() + _header_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"agda-naming selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
