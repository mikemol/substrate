# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Pin the intake reader's arithmetic: sole is not total, and a count is not a naming.

⚑⚑⚑ THIS READER IS THE ONE EVERY OTHER FIGURE IS MEASURED AGAINST, AND IT HAD NO CASES. Two
modes were added to it across two ticks — `--sole` and `--names` — and the only protection
against a regression was byte-comparing its default output against a run from earlier in the
same session. That works once and cannot be repeated by anyone else.

⚑⚑ THE ARITHMETIC IT OWNS IS EXACTLY THE PART THAT WAS WRONG IN PRACTICE. Reading the
overlapping `by_blocker` count as a paydown order cost six batches of misdirected work, and the
`tests` tree reached zero header-lacking files while staying at zero READY. Both are properties
of the sole-versus-total distinction, so both are cased here rather than left to a reader's
recollection of which column means what.

⚑ THE FIXTURES CARRY EVERY BLOCKER COMBINATION, not a representative sample. With three
independent booleans there are eight modules, and enumerating them is cheaper than arguing
about which are interesting — the one that matters is the module blocked by two things, which
appears in two TOTALs and no SOLE and is the case an overlapping count cannot express.

⚑ AND THE EXPECTED COUNTS ARE DERIVED FROM THE FIXTURE, never typed. A case asserting `== 4`
states a fact about a population the case itself builds, so the two can drift apart and the
literal is the half that stops being true. Counting the fixture keeps the assertion about the
RELATION rather than about an arithmetic that happens to hold today.
"""

from __future__ import annotations

from substrate import intake_manifest


def _every_combination() -> tuple[intake_manifest.Module, ...]:
    """Return one module per (promotable, header, adoptable) triple — all eight.

    ⚑ THE LABELS NAME THE STATE so a failing case reads as a claim rather than an index. A
    fixture called `m3` tells a reader nothing about why it was expected to be sole-blocked.
    """
    return tuple(
        intake_manifest.Module(
            label=f"t/{'p' if p else '-'}{'h' if h else '-'}{'a' if a else '-'}.py",
            promotable=p,
            header=h,
            adoptable=a,
        )
        for p in (True, False)
        for h in (True, False)
        for a in (True, False)
    )


def _blocker_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what a module reports as standing in its way."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    clean = intake_manifest.Module(label="a.py", promotable=True, header=True, adoptable=True)
    check("a module with nothing missing is ready", passed=clean.ready)
    check("and names no blockers", passed=clean.blockers() == ())

    # ⚑ THE SOLE-BLOCKER PREDICATE IS A TUPLE COMPARISON, so a module missing ONE thing must
    # report a one-element tuple. A list, a set, or a different order would all break
    # `sole_blocked` silently, since it tests equality against a literal.
    one = intake_manifest.Module(label="b.py", promotable=True, header=False, adoptable=True)
    check(
        "a module missing only the header names exactly that",
        passed=one.blockers() == ("no-header",),
    )
    check("and is not ready", passed=not one.ready)

    two = intake_manifest.Module(label="c.py", promotable=False, header=False, adoptable=True)
    check(
        "a module missing two names both, in declaration order",
        passed=two.blockers() == ("not-promotable", "no-header"),
    )

    nothing = intake_manifest.Module(label="d.py", promotable=False, header=False, adoptable=False)
    check(
        "a module missing everything names all three",
        passed=nothing.blockers() == ("not-promotable", "no-header", "reaches-unpackaged"),
    )
    return out


def _sole_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the sole-versus-total distinction."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    found = _every_combination()
    totals = intake_manifest.by_blocker(found)
    sole = intake_manifest.sole_blocked(found, "no-header")
    carrying = sum(1 for m in found if not m.header)

    # ⚑⚑ THE LOAD-BEARING CASE, AND IT IS A STRICT INEQUALITY RATHER THAN TWO NUMBERS. Several
    # modules lack a header and only ONE lacks nothing else, so paying the header releases far
    # fewer than carry it. The gap is the property — it held at fourfold on this fixture and
    # roughly ninefold on the real corpus, and a case pinning either figure would expire.
    check(
        "every header-lacking module is counted in the total",
        passed=totals["no-header"] == carrying,
    )
    check("but the sole set is strictly smaller", passed=len(sole) < carrying)
    check(
        "and the sole one is the module missing nothing else",
        passed=tuple(m.label for m in sole) == ("t/p-a.py",),
    )

    check(
        "a blocker nothing carries alone reports an empty sole set",
        passed=intake_manifest.sole_blocked(
            tuple(m for m in found if not m.promotable), "no-header"
        )
        == (),
    )

    # ⚑ THE OTHER DIRECTION, or every assertion above passes against a reader that returns
    # nothing. A reader that never finds a sole-blocked module would satisfy the empty case.
    check(
        "and a population of one clean-but-for-X module reports it",
        passed=len(
            intake_manifest.sole_blocked(
                (
                    intake_manifest.Module(
                        label="e.py", promotable=True, header=True, adoptable=False
                    ),
                ),
                "reaches-unpackaged",
            )
        )
        == 1,
    )

    check(
        "ready() keeps only the module with no blockers",
        passed=tuple(m.label for m in intake_manifest.ready(found)) == ("t/pha.py",),
    )
    return out


def _render_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what each renderer puts on the page."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    found = _every_combination()
    sole_text = intake_manifest.render_sole(found)
    names_text = intake_manifest.render_names(found, "no-header")
    carrying = sum(1 for m in found if not m.header)

    # ⚑ BOTH COLUMNS OR THE TABLE LIES. A reader shown only SOLE cannot see how much work sits
    # behind a shared blocker, and one shown only TOTAL takes the largest class for the
    # frontier — which is the measured defect this module's `--sole` mode exists to prevent.
    check("the sole table names both columns", passed="SOLE" in sole_text and "TOTAL" in sole_text)
    check("and states that the columns are different populations", passed="do not sum" in sole_text)

    # ⚑⚑ A COUNT IS NOT A NAMING, which is the distinction that cost a tick. `render_names`
    # must emit the PATH, and its denominator must be the blocker's total rather than the sole
    # count, or a reader cannot see what fraction paying it releases.
    check("the names renderer emits the path, not a count", passed="t/p-a.py" in names_text)
    check(
        "and carries the blocker's TOTAL as its denominator",
        passed=f"of {carrying} module(s)" in names_text,
    )

    check(
        "a blocker with no sole-blocked modules renders zero of its total",
        passed=intake_manifest.render_names(
            tuple(m for m in found if not m.promotable), "no-header"
        ).startswith("sole-"),
    )
    return out


def _tree_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the per-tree split."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ⚑ THE TREE KEY IS THE FIRST PATH SEGMENT, so two modules under one directory must fold
    # into one row. A per-file row would make the tree table a restatement of the module list.
    found = (
        intake_manifest.Module(label="x/a.py", promotable=True, header=True, adoptable=True),
        intake_manifest.Module(label="x/b.py", promotable=True, header=False, adoptable=True),
        intake_manifest.Module(label="y/c.py", promotable=True, header=True, adoptable=True),
    )
    trees = intake_manifest.by_tree(found)
    check("modules fold into their top-level directory", passed=set(trees) == {"x", "y"})
    check("and a mixed tree reports ready under total", passed=trees["x"] == (1, 2))
    check("while a fully-ready tree reports both equal", passed=trees["y"] == (1, 1))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _blocker_cases() + _sole_cases() + _render_cases() + _tree_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"intake-manifest selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


if __name__ == "__main__":
    raise SystemExit(0 if selftest() else 1)
