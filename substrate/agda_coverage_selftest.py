# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.agda_coverage` — what the shared enumeration root omits.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT THE ROOT IS NOT BORROWED. This reader audits the directory
three instruments walk, and if it took that directory FROM one of them it would return nothing
by construction and read as a passing check — the false green this whole family refuses. The
root is declared here as the thing under test, and a case asserts the partition is real.

⚑⚑ AND `outside_root` MUST NOT BE EMPTY TODAY. A coverage reader whose answer is always the
empty list is indistinguishable from one that works; the live case names the file it finds, so
the reader fails loudly if the population or the root ever shifts under it.

⚑ TRACKED, NOT PRESENT. The population is `git ls-files`, so a scratch module in the working
tree is not reported as an uncovered one — this reader must stay quiet while someone is
mid-edit, or it becomes noise exactly when the tree is being changed.
"""

from __future__ import annotations

from substrate import agda_coverage


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    tracked = agda_coverage.tracked_agda()
    inside = agda_coverage.covered()
    missed = agda_coverage.outside_root()

    # ── the population is real ───────────────────────────────────────────────
    check("the tracked population is non-empty", passed=bool(tracked))
    check(
        "every tracked path is an agda source file",
        passed=all(p.endswith(".agda") for p in tracked),
    )
    # ⚑ THE BUILD'S OUTPUT IS NOT SOURCE. Counting `_build` would report a coverage gap on
    # every machine, which is the noise that gets a reader disabled.
    check("build artifacts are excluded", passed=not any("_build" in p.split("/") for p in tracked))

    # ── the partition is exact ───────────────────────────────────────────────
    check(
        "inside and outside partition the population",
        passed=len(inside) + len(missed) == len(tracked),
    )
    check("and they do not overlap", passed=not (set(inside) & set(missed)))

    # ── THE READING ITSELF — non-empty, and naming what it finds ─────────────
    # ⚑ A COVERAGE READER THAT ALWAYS RETURNS EMPTY LOOKS EXACTLY LIKE ONE THAT WORKS. This is
    # the case that distinguishes them, so it asserts the KEY rather than a count.
    check(
        "the reader finds the tree's top-level module outside the root",
        passed="agda/Substrate.agda" in missed,
    )
    check(
        "and the modules under the root are covered",
        passed=all(p.startswith("agda/Substrate/") for p in inside),
    )

    # ── the root is DECLARED here, not borrowed from an instrument ───────────
    # ⚑ Borrowing it from the tool under test would make the answer trivially empty.
    check(
        "the enumeration root under test is the subdirectory, not agda/",
        passed=agda_coverage.ENUMERATION_ROOT == "agda/Substrate",
    )

    # ⚑ AND A WIDER ROOT COVERS EVERYTHING — which is what makes the finding a SCOPE fact
    # rather than a claim about the file. The same population, read from `agda`, has no gap.
    check(
        "read from the wider root, nothing is outside",
        passed=agda_coverage.outside_root("agda") == [],
    )

    # ── the rendering says what an absence MEANS ─────────────────────────────
    text = agda_coverage.render()
    check("the rendering names the file it found", passed="Substrate.agda" in text)
    # ⚑ THE DISTINCTION AN OPERATOR NEEDS: outside a domain is not exempt from a gate, and no
    # count taken inside the root can tell the two apart.
    check("and distinguishes being outside a DOMAIN from being exempt", passed="DOMAIN" in text)

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
