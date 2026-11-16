# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.module_paths` — dotted names resolved to repo files.

⚑⚑⚑ A WRONG GRAPH PRODUCES A CONFIDENT WRONG ORDERING, and nothing downstream can tell. The
decomposition order consumes this directly: a fabricated edge demotes a file that was ready,
and a missing edge promotes one that will hit a wall. Both look like a normal ranking.

⚑⚑ THE TRUNCATION TRAP IS THE ONE TO PIN. Top-level names make every file in a package look
like it imports the package, so a resolver built on them reports every intra-package pair as
mutually dependent and the cycle detector calls the whole package one knot. The case asserts
the resolution is over DOTTED names by checking that a sibling import resolves to the sibling
FILE rather than to the package.

⚑ AND A NON-REPO NAME MUST RESOLVE TO NOTHING. `os` is not a file anyone can decompose, so an
edge to it is not a blocker; admitting it would inflate every dependency set with work that
does not exist.
"""

from __future__ import annotations

from substrate import module_paths


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── resolution: a dotted name to the file that defines it ───────────────
    check(
        "a package module resolves to its file",
        passed=module_paths.path_of("substrate.corpus") == "substrate/corpus.py",
    )
    check(
        "a script resolves to its file",
        passed=module_paths.path_of("scripts.ratchet") == "scripts/ratchet.py",
    )
    # ⚑ A PACKAGE RESOLVES TO ITS `__init__`, so an import of the package is attributable.
    check(
        "a package resolves to its __init__",
        passed=module_paths.path_of("substrate") == "substrate/__init__.py",
    )

    # ⚑ AND A NAME OUTSIDE THE REPO RESOLVES TO NOTHING — not to a plausible-looking file.
    check("a stdlib name resolves to nothing", passed=module_paths.path_of("os") is None)
    check(
        "and an invented name does too",
        passed=module_paths.path_of("no.such.module.anywhere") is None,
    )

    # ── imports_of reads real edges ─────────────────────────────────────────
    # ⚑ THE TRUNCATION GUARD. `module_paths` imports `substrate.corpus` and
    # `substrate.import_edges`; a top-level-name resolver would report only `substrate`,
    # collapsing both to the package `__init__` and losing the actual dependency.
    mine = module_paths.imports_of("substrate/module_paths.py")
    check("a sibling import resolves to the sibling FILE", passed="substrate/corpus.py" in mine)
    check("and every named edge is a repo file", passed=all(p.endswith(".py") for p in mine))
    # ⚑ A FILE NEVER IMPORTS ITSELF in this reading, or the ordering would find a trivial
    # cycle in every file and place none of them.
    check("a file is never its own import", passed="substrate/module_paths.py" not in mine)

    # ── the graph is restricted to the population ──────────────────────────
    # ⚑ AN EDGE OUT OF THE POPULATION IS NOT A WAIT. Keeping it would make the ordering
    # depend on files outside the question, so the answer would move when an unrelated file
    # was added to the tree.
    pair = ["substrate/module_paths.py", "substrate/corpus.py"]
    got = module_paths.graph(pair)
    check("the graph covers exactly the population", passed=set(got) == set(pair))
    check(
        "and keeps an edge that lands inside it",
        passed="substrate/corpus.py" in got["substrate/module_paths.py"],
    )

    narrowed = module_paths.graph(["substrate/module_paths.py"])
    check(
        "an edge outside the population is dropped",
        passed=narrowed["substrate/module_paths.py"] == set(),
    )

    # ── a file that cannot be read yields no edges, rather than raising ────
    check(
        "an absent file yields no edges", passed=module_paths.imports_of("no/such/file.py") == set()
    )

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
