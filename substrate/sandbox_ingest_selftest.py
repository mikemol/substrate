# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.sandbox_ingest` — order, the monotone guard, and every refusal.

⚑ NO CASE CONNECTS OR INGESTS. What the driver DECIDES — which cores, in what order, and whether
a reading has fallen — is checkable on fixture paths and plain dicts; the write itself was
measured against the sandbox (t86-t93) and is the command this module shells out to unchanged.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import sandbox_ingest as si


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    with tempfile.TemporaryDirectory() as where:
        root = Path(where)
        (root / "A").mkdir()
        (root / "A" / "B.agdai").write_text("", encoding="utf-8")
        (root / "C.agdai").write_text("", encoding="utf-8")
        got = si.plan(("C", "Missing", "A.B"), root)
        check("plan keeps the DAG's order", passed=[p.name for p in got] == ["C.agdai", "B.agdai"])
        check("an unbuilt module is omitted, not an error", passed=all(p.is_file() for p in got))
        check(
            "a dotted module name maps to a nested path", passed=got[-1] == root / "A" / "B.agdai"
        )

        refused = False
        try:
            si.build_root(root)
        except si.NoBuildRootError:
            refused = True
        check("no build root refuses", passed=refused)
        (root / "_build" / "2.8.0" / "agda").mkdir(parents=True)
        check(
            "exactly one build root is returned",
            passed=si.build_root(root) == root / "_build" / "2.8.0" / "agda",
        )
        (root / "_build" / "2.9.0" / "agda").mkdir(parents=True)
        refused = False
        try:
            si.build_root(root)
        except si.NoBuildRootError:
            refused = True
        check("two build roots refuse rather than pick one", passed=refused)

    with tempfile.TemporaryDirectory() as where:
        root = Path(where)
        eq = root / "Substrate" / "Foundation" / "Eq.agdai"
        nat = root / "Substrate" / "Foundation" / "Nat.agdai"
        check(
            "the key is the path below <root>/Substrate, as the store printed it",
            passed=si.key(eq, root) == "Foundation/Eq.agdai",
        )
        kept = si.unseen([eq, nat], root, {"Foundation/Eq.agdai"})
        check("a present core is skipped and an absent one kept", passed=kept == [nat])
        check(
            "nothing present keeps every core, in order",
            passed=si.unseen([eq, nat], root, set()) == [eq, nat],
        )

    before = {"edge": 10, "obs": 10, "schema_version": 1}
    check(
        "growth is not a drop",
        passed=si.drops(before, {"edge": 12, "obs": 10, "schema_version": 1}) == [],
    )
    check(
        "a falling count is named",
        passed=si.drops(before, {"edge": 9, "obs": 10, "schema_version": 1}) == ["edge"],
    )
    check(
        "a vanished table is a drop",
        passed=si.drops(before, {"obs": 10, "schema_version": 1}) == ["edge"],
    )
    check(
        "schema_version is exempt, as luthen's witness exempts it",
        passed=si.drops(before, {"edge": 10, "obs": 10, "schema_version": 0}) == [],
    )

    check("no --limit is the default bound", passed=si.parse_limit(["--apply"]) == si.DEFAULT_LIMIT)
    three = 3
    check("--limit N is read", passed=si.parse_limit(["--limit", "3"]) == three)
    check("--limit with no number is malformed", passed=si.parse_limit(["--limit"]) is None)
    check("--limit with a non-number is malformed", passed=si.parse_limit(["--limit", "x"]) is None)
    usage = 2
    check("an unknown flag is refused", passed=si.main(["--live"]) == usage)
    check("a malformed limit is refused", passed=si.main(["--limit", "x"]) == usage)
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"sandbox-ingest selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(0 if ("--selftest" in sys.argv or len(sys.argv) == 1) and selftest() else 1)
