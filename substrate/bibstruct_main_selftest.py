# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The cases for `substrate.bibstruct_main` — the assembled tool, checked against the ROSTER.

⚑⚑⚑ THE LOAD-BEARING CASE IS COMPLETENESS IN BOTH DIRECTIONS, and it is what makes the swap safe.
`bib_modes.unbound` names every declared mode with no handler AND every handler no mode declares —
so *"the replacement covers the origin's surface"* is a fact the roster states rather than a claim
anyone makes. Swapping on a hand-checked list is how a shim ships a roster naming modes it cannot
run.

⚑⚑ AND THE READS ARE DRIVEN AGAINST THE LIVE WORKLIST, because this module's whole job is choosing
CONCRETE collaborators. Every other suite in the drain runs on fixtures precisely so this one can
run on the real thing — a fixture here would test the assembly by not assembling it.

⚑ NO WRITE IS DRIVEN. `--apply` would arm the real snapshot guard, which reads the PROCESS argv and
refuses a suite's invocation — the defect that killed the origin's own suite at its first write
case. The write PATH is cased in `bib_write_handlers_selftest` against a faked bench; what is
asserted here is that the verbs are BOUND.
"""

from __future__ import annotations

from substrate import bib_modes, bibstruct_main, corpus


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    table = bibstruct_main.handlers()

    # ── COMPLETENESS, asked of the roster ────────────────────────────────────
    missing, extra = bib_modes.unbound(table)
    # ⚑ `--selftest` IS THE ONE DECLARED MODE WITH NO HANDLER, by design: the suite runner invokes
    # it, so binding it here would make the tool dispatch into its own test harness.
    check("every declared mode but --selftest is bound", passed=list(missing) == ["--selftest"])
    check("and no handler exists for a mode nothing declares", passed=extra == ())
    check("every write verb is bound", passed=all(flag in table for flag in bib_modes.WRITE_MODES))
    check(
        "and every read mode is bound", passed=all(flag in table for flag in bib_modes.READ_MODES)
    )

    # ── the reads run against the LIVE corpus ────────────────────────────────
    live = corpus.ROOT / "catalog" / "worklist" / "warrants.bib"
    if not live.exists():
        check("the live worklist is absent, so the read cases are skipped", passed=True)
        return out

    def run(*argv: str) -> int:
        return bibstruct_main.main([*argv, str(live)])

    check("--entries reads the live bib", passed=run("--entries") == 0)
    check("--edges reads the live bib", passed=run("--edges") == 0)
    # ⚑⚑ THE LIVE CORPUS HAS NO DANGLING EDGES AND NO ENGINE DROPS TODAY, so both exit 0. These
    # assert the ASSEMBLY runs, not that the corpus is healthy — the corpus's own gate answers that.
    check("--orphans reads the live bib", passed=run("--orphans") == 0)
    check("--dropped reads the live bib through the packaged engine", passed=run("--dropped") == 0)
    check("--roundtrip reads the live bib", passed=run("--roundtrip") == 0)
    check(
        "--field takes its operand",
        passed=bibstruct_main.main(["--field", "section", str(live)]) == 0,
    )

    # ── a refusal is a code, not a crash ─────────────────────────────────────
    # ⚑ THE ORIGIN RAISED `SystemExit` FROM INSIDE ITS DISPATCH, so a suite could not survive one.
    check(
        "a read given the write target refuses",
        passed=bibstruct_main.main(["--orphans", "--bib", str(live)]) != 0,
    )
    check("an unknown mode refuses", passed=bibstruct_main.main(["--nope"]) != 0)

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bibstruct-main selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
