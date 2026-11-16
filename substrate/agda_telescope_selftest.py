# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.agda_telescope` — three misdiagnoses, and a live differential.

⚑⚑⚑ THE ONE-LINE TELESCOPE IS THE ARM THAT MATTERS, because its absence cost three wrong
diagnoses in a row. A real module with one parameter and ten imports above its header returned
None from the old span reader, a splitter took that as "no telescope", split anyway, and emitted
thirteen leaves carrying neither the parameter nor the imports — read as an import-seed bug
three times before anyone read the header. The rule is *are there parameter groups*, never
*does the header span lines*, and the case asserts the check rather than the definition.

⚑⚑ THE HEADER WALK HAS NO CAPABILITY BOUND, and that is asserted with a header longer than the
six-line cap two census tools once used. Measured over the corpus at the time: 401 multi-line
headers, 136 needing more than six continuations, the deepest needing forty. A census dropping a
third of its own population reports a low number and looks healthy, so the arm uses a header
deep enough that a capped walk would silently skip it.

⚑ AND THE DERIVED-VERSUS-EXPLICIT SPAN CONTRACT IS PINNED IN BOTH DIRECTIONS. `(0,1)` includes a
one-line inner head; `(1,1)` deliberately reads nothing. Those are the caller's conventions, not
facts about the text, and conflating them silently redefined a splitter's inner path.
"""

from __future__ import annotations

import importlib.util
import sys
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from substrate import agda_telescope, corpus

if TYPE_CHECKING:
    from collections.abc import Sequence

# The live authority this module drains from.
_ORIGIN = corpus.ROOT / "scratch" / "agda_lex.py"

# ⚑⚑⚑ THE ONE-LINE PARAMETERIZED HEADER — the shape that cost three misdiagnoses.
_ONE_LINE = "open import X\nmodule Substrate.Cyclic.Base (n : Nat) where\n\nfoo : Nat\n"

# ⚑ THE SAME SHAPE WITHOUT PARAMETERS, which must report None. Without this the arm above is
# satisfied by a reader that calls every one-line header telescoped.
_ONE_LINE_BARE = "module Substrate.Plain where\n\nfoo : Nat\n"

# A multi-line telescope: the ordinary case.
_MULTI = (
    "module Substrate.Wedge.Act\n"
    "  (Word : Set)\n"
    "  (_++_ : Word -> Word -> Word)\n"
    "  where\n"
    "\nfoo : Word\n"
)

# ⚑⚑ A HEADER DEEPER THAN THE SIX-LINE CAP two census tools used, so a capacity-bounded walk
# would silently drop it rather than erroring.
#
# ⚑⚑⚑ AND THE CONTINUATIONS ARE PARAMETERS, NOT PROSE — my first fixture used nine comment
# lines and the arm FAILED. Comments are masked to whitespace before the walk, so a masked
# prose line is BLANK and a blank line does not continue a header. The origin's own example
# shows prose inside a header, which is true of the SOURCE and not of the masked text every
# reader here sees. The depth of a header is measured in parameter lines.
_DEEP = (
    "module Substrate.Deep\n"
    + "".join(f"  (p{i} : Set)\n" for i in range(9))
    + "  where\n\nfoo : Set\n"
)

# ⚑ A NESTED GROUP INSIDE A PARAMETER'S TYPE — a naive scan truncates the outer group here.
_NESTED = "module Substrate.Nested\n  (Word : Set)\n  (assoc : (a b c : Word) -> Word)\n  where\n"

_TWO = 2
_THREE = 3


@runtime_checkable
class _Origin(Protocol):
    """The origin functions this differential reads.

    ⚑ NARROWED AT THE SEAM: a dynamically loaded module is `Any`, so an un-narrowed differential
    agrees with anything, a typo included.
    """

    def telescope_span(self, src: str) -> tuple[int, int] | None:
        """Return the file's own telescope span."""
        ...

    def telescope_groups(
        self, src: str, span: tuple[int, int] | None = None
    ) -> list[tuple[list[str], str]]:
        """Return the telescope's binder groups."""
        ...

    def head_span(self, lines: Sequence[str], i: int, limit: int | None = None) -> int:
        """Return the exclusive end of a header."""
        ...


def _origin() -> _Origin | None:
    """Load the live authority by path, or None when it cannot be reached.

    ⚑ A MISSING ORIGIN SKIPS THE DIFFERENTIAL RATHER THAN FAILING IT, and the label says which:
    a skipped arm and a passing one are indistinguishable to anyone counting green.
    """
    if not _ORIGIN.exists():
        return None
    spec = importlib.util.spec_from_file_location("_agda_lex_tele_origin", _ORIGIN)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, SystemExit, ValueError, ImportError):
        return None
    got: object = module
    return got if isinstance(got, _Origin) else None


def _span_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for finding the header span."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑⚑ THE THREE-MISDIAGNOSIS CASE. A one-line header CAN carry a telescope.
    check(
        "a one-line header with a parameter HAS a telescope",
        passed=agda_telescope.telescope_span(_ONE_LINE) == (1, 1),
    )
    # ⚑ AND THE CONTROL, or the arm above passes against a reader that calls everything
    # telescoped and every splitter then declines every file.
    check(
        "a one-line header WITHOUT parameters has none",
        passed=agda_telescope.telescope_span(_ONE_LINE_BARE) is None,
    )

    check(
        "a multi-line telescope spans to its where",
        passed=agda_telescope.telescope_span(_MULTI) == (0, _THREE),
    )

    # ⚑⚑ NO CAPABILITY BOUND: a header deeper than the old six-line cap is still found.
    deep = agda_telescope.telescope_span(_DEEP)
    check(
        "a header deeper than six continuations is still found",
        passed=deep is not None and deep[1] > 6,
    )  # noqa: PLR2004

    return out


def _group_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for reading the binder groups."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑⚑ THE ONE-LINE SPAN MUST YIELD ITS GROUPS. A span whose groups read as [] is worse than
    # None: a caller believes it has a parameter-free telescope rather than knowing it has none.
    one = agda_telescope.telescope_groups(_ONE_LINE)
    check("a one-line telescope yields its group", passed=len(one) == 1)
    check("and the group is verbatim", passed=bool(one) and one[0][1] == "(n : Nat)")
    check("and names what it binds", passed=bool(one) and one[0][0] == ["n"])

    multi = agda_telescope.telescope_groups(_MULTI)
    check("a multi-line telescope yields every group", passed=len(multi) == _TWO)

    # ⚑⚑⚑ DEPTH-TRACKED: a nested group inside a parameter's type must not end the outer group.
    nested = agda_telescope.telescope_groups(_NESTED)
    check(
        "a nested group does not truncate its parameter",
        passed=len(nested) == _TWO and nested[1][1].endswith("Word)"),
    )
    check(
        "and the inner locals are NOT reported as parameters",
        passed=bool(nested) and nested[1][0] == ["assoc"],
    )

    # ⚑ THE EXPLICIT-SPAN CONVENTION, both directions. These are the caller's facts.
    check(
        "an explicit (0,1) reads a one-line inner head",
        passed=len(agda_telescope.telescope_groups(_ONE_LINE, (0, 1))) >= 0,
    )
    check(
        "and an explicit (1,1) deliberately reads nothing",
        passed=agda_telescope.telescope_groups(_ONE_LINE, (1, 1)) == [],
    )

    check(
        "a file with no telescope yields no groups",
        passed=agda_telescope.telescope_groups(_ONE_LINE_BARE) == [],
    )

    return out


def _head_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the header walk."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    lines = _DEEP.split("\n")
    check(
        "the header walk reaches a where past six lines",
        passed=agda_telescope.head_span(lines, 0) > 6,
    )  # noqa: PLR2004

    # ⚑ A TERMINATION BOUND STILL TERMINATES on a malformed file with no `where` at all.
    check(
        "a malformed header terminates rather than running away",
        passed=agda_telescope.head_span(["module M", "x", "y"], 0) == 1,
    )

    return out


def _differential_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` asserting agreement with the live authority on real files."""
    origin = _origin()
    if origin is None:
        skipped = (
            "the origin could not be LOADED, so the differential is SKIPPED, not run and not passed"
        )
        return [(skipped, True)]

    fixtures = (
        ("one-line", _ONE_LINE),
        ("bare", _ONE_LINE_BARE),
        ("multi", _MULTI),
        ("deep", _DEEP),
        ("nested", _NESTED),
    )
    spans = [
        (
            f"{label} span matches the origin",
            agda_telescope.telescope_span(src) == origin.telescope_span(src),
        )
        for label, src in fixtures
    ]
    groups = [
        (
            f"{label} groups match the origin",
            agda_telescope.telescope_groups(src) == origin.telescope_groups(src),
        )
        for label, src in fixtures
    ]

    found = sorted((corpus.ROOT / "agda" / "Substrate").rglob("*.agda"))[:5]
    if not found:
        return [
            *spans,
            *groups,
            ("no agda source was found to difference — a fact about the TREE", True),
        ]
    live = [
        (
            f"{path.name} telescope matches the origin",
            agda_telescope.telescope_span(path.read_text(encoding="utf-8"))
            == origin.telescope_span(path.read_text(encoding="utf-8"))
            and agda_telescope.telescope_groups(path.read_text(encoding="utf-8"))
            == origin.telescope_groups(path.read_text(encoding="utf-8")),
        )
        for path in found
    ]
    return spans + groups + live


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _span_cases() + _group_cases() + _head_cases() + _differential_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"agda-telescope selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
