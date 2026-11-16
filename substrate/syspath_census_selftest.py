# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.syspath_census` — the sys.path drain's scope, by directory.

⚑⚑⚑ THE GROUPING IS THE CLAIM, so the cases assert it rather than a total. Several inserts
naming one directory are ONE decision; one file inserting several directories is several. A
census reporting only a count would make those indistinguishable, and the drain would be
planned against a number that answers neither question.

⚑⚑ AND `<unresolved>` MUST SURVIVE AS ITS OWN ROW. An insert whose argument is computed has
no statically knowable target; folding it under a plausible directory would invent a fact, and
dropping it would shrink the drain by exactly the sites that need a human to read them.

⚑ THE LIVE CASE ASSERTS SHAPE, NOT SIZE. A total over the repo is red the next time anyone
adds a file; that several directories are targeted, and that the reader names them, is the
property the tool exists to provide.
"""

from __future__ import annotations

from substrate import insert_census_fixture as fx
from substrate import syspath_census

_TWO = 2


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the population excludes copies ───────────────────────────────────────
    files = syspath_census.python_files()
    check("the population is non-empty", passed=bool(files))
    # ⚑ A MUTATION IN A COPY IS NOT A SITE ANYONE CAN FIX. Counting `build/` would inflate
    # the drain with work that does not exist.
    check(
        "vendored and generated trees are excluded",
        passed=not any(f.startswith(syspath_census.SKIP_PREFIXES) for f in files),
    )
    check("and hidden directories are too", passed=not any("/." in f"/{f}" for f in files))

    try:
        targets, _unparsed = syspath_census.census(fx.paths())
        by_dir = {t.directory: t for t in targets}

        # ── grouping: several sites in one directory are ONE decision ────────
        check(
            "two inserts naming one directory group into one target",
            passed="shared" in by_dir and by_dir["shared"].sites == _TWO,
        )
        check(
            "and that target names both owning files",
            passed="shared" in by_dir and len(by_dir["shared"].files) == _TWO,
        )

        # ⚑ ONE FILE INSERTING TWO DIRECTORIES IS TWO TARGETS — the dual case, and the
        # reason `owning_files` is a set rather than a sum.
        check(
            "one file inserting two directories yields two targets",
            passed="alpha" in by_dir and "beta" in by_dir,
        )
        check(
            "and it is counted once as an owning file",
            passed=len(syspath_census.owning_files(targets))
            == len({f for t in targets for f in t.files}),
        )

        # ── the unresolved bucket survives ──────────────────────────────────
        # ⚑ A COMPUTED ARGUMENT HAS NO STATIC TARGET. Naming one would invent a fact.
        unresolved = [t for t in targets if not t.is_resolved]
        check("a computed insert lands in the unresolved bucket", passed=len(unresolved) == 1)
        check(
            "and is reported rather than dropped",
            passed=bool(unresolved) and unresolved[0].sites >= 1,
        )

        # ── totals agree with the grouping ──────────────────────────────────
        check(
            "the site total is the sum over targets",
            passed=syspath_census.total_sites(targets) == sum(t.sites for t in targets),
        )

        # ── an unparseable file is counted, not silently skipped ────────────
        # ⚑ A SYNTAX ERROR MEANS THIS READER SAW NOTHING — a fact about the reader.
        # Folding it into a zero would report the file as clean.
        _t, unparsed = syspath_census.census([fx.BROKEN])
        check("an unparseable file is counted as unparsed", passed=unparsed == 1)

        # ── rendering names what it found ───────────────────────────────────
        text = syspath_census.render(targets, 0)
        check("the rendering names a target directory", passed="shared" in text)
        # ⚑ THE UNRESOLVED ROW CARRIES ITS OWN EXPLANATION, so a reader does not mistake
        # it for a directory literally named that.
        check("and marks the unresolved row as needing reading", passed="need reading" in text)
    finally:
        fx.remove()

    # ── the live tree: shape, never size ────────────────────────────────────
    live, _u = syspath_census.census()
    check("the live census finds several targeted directories", passed=len(live) > 1)
    check("and the largest target names its files", passed=bool(live) and bool(live[0].files))

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
