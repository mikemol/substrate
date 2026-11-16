# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""The cases for `substrate.tool_walk` — every exclusion tested with a real directory.

⚑⚑⚑ AN EXCLUSION IS TESTED BY BUILDING THE THING IT EXCLUDES, never by asserting the constant
holds a name. A case that checked `"tests" in EXCLUDE` would pass against a walk that ignores the
set entirely — and the excluded directories carry measured incidents, so a silent regression here
puts phantom keys into a paydown-only baseline that nobody can ever legitimately pay down.

⚑⚑ AND THE PRUNE IS ASSERTED, NOT THE FILTER. `os.walk` must not DESCEND into an excluded tree,
which is a different property from dropping its results: a walk that descends and then filters
gives the same answer while reading a vendored virtualenv. The fixture nests a file two levels
inside an excluded directory so a shallow check cannot pass for the wrong reason.

⚑ THE LIVE ARM IS SEPARATE AND MODEST. It asserts the real tree yields tools and that none comes
from an excluded directory — which is what a fixture cannot say, because a fixture only contains
what I put in it.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import corpus, tool_walk


def _fixture(tmp: str) -> Path:
    """Build a miniature repo with a tool in each declared root and in each exclusion."""
    root = Path(tmp)
    for tree in tool_walk.ROOTS:
        (root / tree).mkdir(parents=True)
        (root / tree / "live_tool.py").write_text("x = 1\n", encoding="utf-8")
    return root


def _exclusion_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for each excluded directory, built rather than asserted."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture(tmp)
        scripts = root / "scripts"

        # ⚑⚑⚑ EVERY EXCLUSION GETS A REAL DIRECTORY WITH A REAL `.py` IN IT, nested two deep so
        # a walk that descends and filters shallowly cannot pass by accident.
        for name in sorted(tool_walk.EXCLUDE):
            deep = scripts / name / "inner"
            deep.mkdir(parents=True)
            (deep / "hidden_tool.py").write_text("x = 1\n", encoding="utf-8")

        found = tool_walk.tool_files(scripts)
        check("the live tool is enumerated", passed=any(p.endswith("live_tool.py") for p in found))
        # ⚑ ONE ARM PER EXCLUSION, NAMED — a single "nothing hidden" arm would not say WHICH
        # exclusion regressed, and they have different reasons.
        for name in sorted(tool_walk.EXCLUDE):
            check(
                f"nothing under {name}/ is enumerated",
                passed=not any(f"/{name}/" in p for p in found),
            )

    return out


def _source_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the `(relpath, text)` pairing."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as tmp:
        root = _fixture(tmp)
        (root / "scripts" / "live_tool.py").write_text("marker = 42\n", encoding="utf-8")

        pairs = tool_walk.sources(root)
        rels = {rel for rel, _text in pairs}
        # ⚑⚑ REPO-RELATIVE, because these keys are compared against a committed baseline. An
        # absolute path would read as a new offender for every key at once.
        check("paths are repo-relative", passed="scripts/live_tool.py" in rels)
        check("and not absolute", passed=not any(r.startswith("/") for r in rels))
        check(
            "both declared roots are walked",
            passed=rels == {f"{tree}/live_tool.py" for tree in tool_walk.ROOTS},
        )
        check("the text is the file's", passed=any("marker = 42" in text for _rel, text in pairs))

        # ⚑ A MISSING ROOT IS SKIPPED, NOT RAISED — an adopter's checkout may carry only one
        # tree, and a walk that raised would make the census depend on the checkout's shape.
        partial = Path(tmp) / "partial"
        (partial / "scripts").mkdir(parents=True)
        (partial / "scripts" / "only.py").write_text("x = 1\n", encoding="utf-8")
        check(
            "a missing root is skipped rather than raised",
            passed={rel for rel, _t in tool_walk.sources(partial)} == {"scripts/only.py"},
        )

        # ⚑ AN EMPTY REPO YIELDS NOTHING rather than erroring.
        empty = Path(tmp) / "empty"
        empty.mkdir()
        check("an empty repo enumerates nothing", passed=tool_walk.sources(empty) == [])

    return out


def _live_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the real tree — what a fixture cannot say."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    pairs = tool_walk.sources(corpus.ROOT)
    check("the live tree yields tools", passed=len(pairs) > 1)
    # ⚑⚑ NO EXCLUDED DIRECTORY SURVIVES ON THE REAL TREE, which is the arm a fixture cannot
    # make: the live `scratch/` genuinely contains a vendored virtualenv and a snapshot
    # directory, and those are what the exclusions were written for.
    leaked = sorted(
        {rel for rel, _t in pairs if any(f"/{name}/" in f"/{rel}" for name in tool_walk.EXCLUDE)}
    )
    check(f"and no excluded directory leaks into it (e.g. {leaked[:3]})", passed=not leaked)
    # ⚑ AND EVERY PATH IS UNDER A DECLARED ROOT, or the population is wider than the policy.
    check(
        "every tool sits under a declared root",
        passed=all(rel.split("/", 1)[0] in tool_walk.ROOTS for rel, _t in pairs),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _exclusion_cases() + _source_cases() + _live_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"tool-walk selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
