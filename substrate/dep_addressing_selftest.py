#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases pinning the addressing classification and — the load-bearing half — that it can FAIL.

⚑⚑⚑ A GATE THAT CANNOT FAIL IS THE DEFECT THIS REPO CATALOGUES MOST OFTEN, and it is exactly
what a form-based check invites: every requirement in the live manifest is currently addressed,
so a classifier that returned INDEXED unconditionally would pass every case an eyeball would
think to write. The DISCRIMINATOR cases below are therefore the point — each pairs a passing
spelling with the failing one it most resembles, so a predicate that stopped discriminating
fails a case rather than going quietly green.

⚑⚑ THE LIVE-TREE ARM IS ASKED IN BOTH DIRECTIONS. That the real manifest is clean is worth
pinning, and on its own it is a fact about today's manifest rather than about the reader — so it
sits beside a synthetic manifest carrying a bare `paperkit`, which MUST be caught. Only the pair
distinguishes "the tree is clean" from "the gate sees nothing".

⚑⚑⚑ AND EVERY ARM ABOVE PASSED WHILE `main` IGNORED ITS OPERAND (Ⓝ124a), WHICH IS THE FINDING
THIS SUITE OWES ITS NEWEST CASES TO. They all call `requirements(path)` — the parameterised
reader, which was never broken — so the suite proved the READING was correct about any manifest
and never once asked whether the COMMAND LINE reached it. The defect lived in the one seam no
case crossed, and a green suite is what let it ship.

⚑⚑ SO THE OPERAND CASES GO THROUGH `main(argv)` AND ASSERT AN EXIT CODE, NOT A CLASSIFICATION.
Anything calling the reader directly re-tests the half that worked. The discriminator is a
manifest whose verdict DIFFERS from the live tree's: `main` given a broken manifest must return
1, and if the operand is ever dropped again it reads the repo's own clean file and returns 0 — so
the case fails exactly on the regression it exists for, rather than on a shape near it.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import dep_addressing

# A synthetic manifest carrying the exact defect Ⓝ122b shipped: a bare unpublished name beside
# ordinary indexed ones, so the reader must discriminate rather than flag everything.
_BROKEN_MANIFEST = """[project]
name = "probe"
dependencies = [
    "libcst",
    "paperkit",
    "psycopg[binary]",
]
"""

# The same manifest with the defect repaired the way this gate's refusal instructs.
_FIXED_MANIFEST = """[project]
name = "probe"
dependencies = [
    "libcst",
    "paperkit @ git+https://github.com/mikemol/paperkit.git@main",
    "psycopg[binary]",
]
"""

# A manifest declaring the table but no dependencies — the empty POPULATION, which must be
# reported as such rather than passed silently.
_EMPTY_MANIFEST = """[project]
name = "probe"
dependencies = []
"""


def _forms(text: str) -> list[str]:
    """Classify every dependency of a manifest written to a temporary file."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "pyproject.toml"
        path.write_text(text, encoding="utf-8")
        return [item.form for item in dep_addressing.requirements(path)]


def _exit_for(text: str) -> int:
    """Return `main`'s exit code when handed a manifest AS AN OPERAND.

    ⚑⚑ THE WHOLE POINT IS THAT THIS GOES THROUGH `main`, not through `requirements`. The reader
    was always parameterised and always correct; the dropped operand lived between argv and the
    reader, which is the one edge `_forms` does not cross. A helper that took the shorter route
    would restate the passing half and pin nothing.

    ⚑ THE FILE IS NOT NAMED `pyproject.toml` — deliberately. A future `main` that recovered the
    path by GUESSING at a conventional filename rather than reading argv would pass a case built
    on the conventional name, so the fixture is named something the tool could not assume.
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "probe-manifest.toml"
        path.write_text(text, encoding="utf-8")
        return dep_addressing.main(["dep_addressing.py", "--quiet", str(path)])


def selftest() -> int:
    """Run every case, reporting which failed."""
    cases: list[tuple[str, object, object]] = []

    def check(name: str, got: object, want: object) -> None:
        cases.append((name, got, want))

    # ⚑ THE NAME IS READ AND NORMALISED. PEP 503 makes `Paper_Kit` and `paperkit` one name, so a
    # rename by punctuation must not walk past the roster.
    check("a bare name reads as itself", dep_addressing.distribution_name("libcst"), "libcst")
    check(
        "extras and specifiers are not part of the name",
        dep_addressing.distribution_name("psycopg[binary]>=3.1"),
        "psycopg",
    )
    check(
        "a direct reference's name stops at the marker",
        dep_addressing.distribution_name("paperkit @ git+https://x/y.git@main"),
        "paperkit",
    )
    check(
        "the name is normalised for comparison",
        dep_addressing.distribution_name("Paper_Kit"),
        "paper-kit",
    )

    # ⚑⚑ THE CENTRAL DISCRIMINATOR. These two strings differ only in whether an address is
    # present, and they must classify oppositely — the whole content of the gate.
    check(
        "a bare unpublished name is UNADDRESSED",
        dep_addressing.classify("paperkit").form,
        dep_addressing.UNADDRESSED,
    )
    check(
        "the same name WITH a git address is DIRECT",
        dep_addressing.classify("paperkit @ git+https://github.com/mikemol/paperkit.git@main").form,
        dep_addressing.DIRECT,
    )

    # ⚑ AND A BARE NAME THAT IS PUBLISHED MUST PASS, or the gate is flagging the common case and
    # would be disabled within a week.
    check(
        "a bare published name is INDEXED",
        dep_addressing.classify("libcst").form,
        dep_addressing.INDEXED,
    )
    check(
        "extras and specifiers do not change the form",
        dep_addressing.classify("salt>=3008.2").form,
        dep_addressing.INDEXED,
    )

    # ⚑⚑ THE `git+file:` TRAP, which is why `classify` checks local BEFORE git. It carries the
    # `git+` prefix a naive reader would accept and addresses one machine.
    check(
        "a git+file: reference is LOCAL, not DIRECT",
        dep_addressing.classify("paperkit @ git+file:///home/me/paperkit").form,
        dep_addressing.LOCAL,
    )
    check(
        "a plain file:// reference is LOCAL",
        dep_addressing.classify("paperkit @ file:///home/me/paperkit").form,
        dep_addressing.LOCAL,
    )
    check(
        "a git+ssh reference is DIRECT",
        dep_addressing.classify("paperkit @ git+ssh://git@github.com/mikemol/paperkit").form,
        dep_addressing.DIRECT,
    )
    # ⚑ FAIL-CLOSED: a scheme this reader cannot place is not evidence of a good address.
    check(
        "an unrecognised scheme fails rather than passing",
        dep_addressing.classify("paperkit @ wat://elsewhere").form,
        dep_addressing.LOCAL,
    )

    # ⚑ WHICH STATES ABORT, asked as a set so a newly-added state cannot be silently admitted.
    check(
        "exactly UNADDRESSED and LOCAL fail the gate",
        sorted(
            s
            for s in (
                dep_addressing.INDEXED,
                dep_addressing.DIRECT,
                dep_addressing.UNADDRESSED,
                dep_addressing.LOCAL,
            )
            if dep_addressing.Requirement("r", "n", s, "").failed
        ),
        [dep_addressing.LOCAL, dep_addressing.UNADDRESSED],
    )

    # ⚑⚑⚑ THE FAILURE PROBE, END TO END. A whole manifest carrying the shipped defect must be
    # caught, and the repaired one must go clean — the before/after pair that proves the gate
    # discriminates rather than always-passing or always-failing.
    check(
        "a manifest with a bare unpublished name is caught",
        _forms(_BROKEN_MANIFEST),
        [dep_addressing.INDEXED, dep_addressing.UNADDRESSED, dep_addressing.INDEXED],
    )
    check(
        "the repaired manifest goes clean",
        _forms(_FIXED_MANIFEST),
        [dep_addressing.INDEXED, dep_addressing.DIRECT, dep_addressing.INDEXED],
    )
    check("an empty dependency table yields an empty population", _forms(_EMPTY_MANIFEST), [])

    # ⚑ AND THE LIVE TREE IS CLEAN — a fact about today's manifest, meaningful only beside the
    # synthetic arm above which proves the reader can still say otherwise.
    check(
        "the live manifest declares no unaddressed dependency",
        [item.raw for item in dep_addressing.failures(dep_addressing.requirements())],
        [],
    )

    # ⚑⚑⚑ THE OPERAND CASES — the regression pin for Ⓝ124a. These are the ONLY arms that reach
    # `main`, and the broken one is the discriminator: a `main` that drops its operand reads the
    # repo's own clean manifest and returns 0, so this case fails on exactly the defect and not
    # on a neighbour of it. The clean arm sits beside it because a `main` that always returned 1
    # would satisfy the broken case alone.
    check("main given a broken manifest exits 1", _exit_for(_BROKEN_MANIFEST), 1)
    check("main given a repaired manifest exits 0", _exit_for(_FIXED_MANIFEST), 0)

    # ⚑ AND THE OPERAND IS READ OUT OF ARGV RATHER THAN INFERRED. Asked directly so a failure
    # names the parse rather than the verdict two layers down.
    check(
        "the first non-flag word is the operand",
        dep_addressing.operand(["prog", "--quiet", "m.toml"]),
        Path("m.toml"),
    )
    check(
        "a flag is never mistaken for the operand", dep_addressing.operand(["prog", "--list"]), None
    )
    # ⚑ THE PRE-SLICED SPELLING MUST AGREE — the `ratchet_flags._rest` incident, where a blind
    # `argv[1:]` made a guard examine nothing for the one caller that had already sliced.
    check(
        "an already-sliced argv reads the same operand",
        dep_addressing.operand(["--quiet", "m.toml"]),
        Path("m.toml"),
    )

    # ⚑ AN EMPTY POPULATION IS REPORTED, NOT PASSED. The rendered wording must not read as a
    # verdict, so the phrase that says so is asserted rather than a bare boolean.
    check(
        "an empty population renders as a population fact, never a pass",
        dep_addressing.render([]).split(" — ")[-1],
        "a fact about the POPULATION, not a pass",
    )

    ok = sum(1 for _n, got, want in cases if got == want)
    for name, got, want in cases:
        if got != want:
            sys.stdout.write(f"  FAIL {name}\n       got {got!r} want {want!r}\n")
    sys.stdout.write(f"dep-addressing selftest: {ok}/{len(cases)}\n")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    sys.exit(selftest())
