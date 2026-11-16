# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.extraction` — whether a migration out of a monolith finished.

⚑⚑⚑ THE FAILURE THIS GUARDS IS A DUPLICATE, and it is the one that looks like success. Code
copied into a clean new home reads as progress in every summary — a new module exists, its cases
pass — while the origin still defines the same thing and two implementations drift apart. This
session produced exactly that with a private sibling finder, so the case asserting a defining
origin is INCOMPLETE is the load-bearing one.

⚑⚑ AND A MENTION IS NOT A DEFINITION. A finished extraction leaves the origin MENTIONING the
name — in a comment recording where it went, or in an import of the new home — so a reader that
counted mentions would report every correct extraction as incomplete and the check would be
useless in the direction that matters.

⚑ THE LIVE CASE RUNS AGAINST A REAL EXTRACTION FROM THIS SESSION, because a checker validated
only on fixtures is validated against its author's idea of the shape.
"""

from __future__ import annotations

from substrate import extraction

_ORIGIN_DEFINES = "class SiblingFinder:\n    pass\n"
_ORIGIN_MENTIONS = (
    "# the finder that sat here moved to substrate.sibling_finder\n"
    "from substrate import sibling_finder\n"
)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── definition vs mention ───────────────────────────────────────────────
    check(
        "a class definition is a definition",
        passed=extraction.defines(_ORIGIN_DEFINES, "SiblingFinder"),
    )
    # ⚑ THE ASYMMETRY THAT MAKES THE CHECK USABLE. A finished extraction leaves mentions
    # behind by design; counting them would fail every correct migration.
    check(
        "a comment and an import are NOT a definition",
        passed=not extraction.defines(_ORIGIN_MENTIONS, "SiblingFinder"),
    )
    check(
        "a def is a definition", passed=extraction.defines("def helper(x):\n    pass\n", "helper")
    )
    # ⚑ AN INDENTED DEF IS A METHOD, NOT A TOP-LEVEL DEFINITION — the origin may legitimately
    # keep a method of that name on some class it still owns.
    check(
        "an indented def is not a top-level definition",
        passed=not extraction.defines("class C:\n    def helper(self):\n        pass\n", "helper"),
    )

    # ── the verdict needs all three conditions ─────────────────────────────
    duplicate = extraction.Extraction(
        name="X", origin="o.py", home="h.py", home_clean=True, origin_still_defines=True
    )
    # ⚑ THE FAILURE THAT LOOKS LIKE SUCCESS. Clean home, passing cases, and a live duplicate.
    check("a clean home with a defining origin is INCOMPLETE", passed=not duplicate.complete)
    check("and the failure names it as a COPY", passed="COPY" in duplicate.failure)

    dirty_home = extraction.Extraction(
        name="X", origin="o.py", home="h.py", home_clean=False, origin_still_defines=False
    )
    check("a dirty new home is INCOMPLETE", passed=not dirty_home.complete)
    # ⚑ MOVING DEBT IS NOT DRAINING IT, and the message must say which.
    check(
        "and the failure says debt moved rather than drained",
        passed="not drained" in dirty_home.failure,
    )

    stale = extraction.Extraction(
        name="X",
        origin="o.py",
        home="h.py",
        home_clean=True,
        origin_still_defines=False,
        consumers_stale=("c.py",),
    )
    check("a stale consumer is INCOMPLETE", passed=not stale.complete)
    check("and the failure says the old path is live", passed="live" in stale.failure)

    done = extraction.Extraction(
        name="X",
        origin="o.py",
        home="h.py",
        home_clean=True,
        origin_still_defines=False,
        consumers_repointed=("c.py",),
    )
    check("all three conditions met is COMPLETE", passed=done.complete)
    check("and a complete extraction names no failure", passed=done.failure == "")

    # ── the live case: a real extraction from this session ─────────────────
    # ⚑ A CHECKER VALIDATED ONLY ON FIXTURES is validated against its author's idea of the
    # shape. `SiblingFinder` moved out of `scratch_module` into `sibling_finder`, and the
    # origin now only mentions it.
    live = extraction.check(
        "SiblingFinder", "substrate/scratch_module.py", "substrate/sibling_finder.py", consumers={}
    )
    check("the live extraction reads as complete", passed=live.complete)
    check("its new home is clean", passed=live.home_clean)
    check("and the origin no longer defines it", passed=not live.origin_still_defines)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
