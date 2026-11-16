# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_cli` — refusals are RESULTS, and the roster binds both ways.

⚑⚑⚑ THE LOAD-BEARING CASE IS THAT A REFUSAL RETURNS RATHER THAN RAISES, AND THE ORIGIN'S SUITE IS
WHY. `main` raised `SystemExit` from inside a branch, so the suite ABORTED at the first refusal and
twenty-four cases below it were dead text — while still printing an N/N that read as full coverage.
`census-green-is-a-fact-about-the-census` in its strongest form: the suite's own count was reporting
a population it had stopped iterating. **A tool whose main job is refusing must be able to assert on
a refusal.**

⚑⚑ AND THE UNWIRED CASE IS NOT HYPOTHETICAL. A declared mode with no handler is reachable the
moment someone adds a `Mode` and forgets the table — which is exactly how the origin shipped a mode
with zero callers for its whole life. It is named distinctly from usage, because a reader who
invoked a DOCUMENTED mode needs to know the wiring is missing, not that they mistyped.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import bib_argv, bib_cli, bib_modes, bib_report
from substrate.climode import Mode

if TYPE_CHECKING:
    from collections.abc import Callable

# The handler shape the entry point dispatches to.
_Table = dict[str, "Callable[[bib_argv.Parsed], bib_cli.Result]"]


def _ok(_parsed: bib_argv.Parsed) -> bib_cli.Result:
    """Succeed, standing in for any mode's body."""
    return ("ran",), 0


def _full() -> _Table:
    """Bind every declared mode to a succeeding handler."""
    return dict.fromkeys(bib_modes.MODES, _ok)


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    handlers = _full()

    # ── a refusal is a RESULT ────────────────────────────────────────────────
    # ⚑⚑⚑ THE ORIGIN RAISED HERE, AND ITS OWN SUITE DIED AT THIS LINE. Every case below the first
    # refusal was dead text while the count still read as full coverage.
    lines, code = bib_cli.run(["--orphans", "--bib", "a.bib"], handlers)
    check(
        "a read mode given the write target REFUSES rather than raising",
        passed=code == bib_cli.REFUSED,
    )
    check(
        "and the refusal's own words are returned",
        passed=any("POSITIONALLY" in line for line in lines),
    )

    # ── an unknown mode prints usage and refuses ─────────────────────────────
    # ⚑ NOT A DEFAULT. A tool that guesses which mode was meant is the operand-ownership defect
    # one level up.
    lines, code = bib_cli.run(["--nope"], handlers)
    check("an unrecognised mode refuses", passed=code == bib_cli.REFUSED)

    # ── an unreadable operand exits on its OWN code ──────────────────────────
    # ⚑⚑⚑ THE CONTRACT gate-G244 SPLIT, PINNED. An absent path and an unknown verb are two
    # different repairs — correct the path versus spell the mode differently — and they shared a
    # code until this arm existed. The assertion that matters is that the codes DIFFER: checking
    # each against its own constant would pass even if both constants held the same number.
    def _raises(_parsed: object) -> tuple[tuple[str, ...], int]:
        message = "no such bib: /nonexistent — ABSENT, not empty."
        raise FileNotFoundError(message)

    # ⚑ ONE MODE REPLACED, NOT THE WHOLE TABLE. A first cut swapped every handler for the raiser
    # and broke a LATER case that dispatches a different mode — a fixture wider than the case it
    # serves reaches past its own arm, which is the shared-mutable-fixture defect in miniature.
    failing: _Table = {**handlers, "--entries": _raises}
    lines, code = bib_cli.run(["--entries"], failing)
    check(
        f"an unreadable operand exits UNREADABLE, not REFUSED: {code}",
        passed=code == bib_cli.UNREADABLE,
    )
    check(
        f"and that code is DISTINCT from a refusal: {bib_cli.UNREADABLE} vs {bib_cli.REFUSED}",
        passed=bib_cli.UNREADABLE != bib_cli.REFUSED,
    )
    # ⚑ AND IT IS NOT 1 EITHER — an ordinary failure is a third state, so folding an absent
    # operand into it is the same collapse one step over. This is where substrate diverges from
    # paperkit's fork deliberately rather than accidentally.
    check(
        f"and distinct from an ordinary failure: {bib_cli.UNREADABLE}",
        passed=bib_cli.UNREADABLE != 1,
    )
    check(
        "and the refusal's own words reach the caller",
        passed=any("ABSENT" in line for line in lines),
    )
    # ⚑ AND IT DOES *NOT* PRINT USAGE, which I asserted wrongly at first. Usage answers *which
    # verbs exist* and is the right response to an unknown mode; a caller whose PATH is wrong
    # already used a real verb, so listing the verbs buries the one line that names their file.
    check(
        f"and does NOT print usage — that answers a different question: {lines[:1]}",
        passed=not any("bibstruct.py —" in line for line in lines),
    )

    # ── the usage IS the roster, so it cannot drift ──────────────────────────
    # ⚑⚑ THE ORIGIN PRINTED ITS DOCSTRING, which is a second roster a reader maintains by hand.
    rendered = "\n".join(bib_cli.usage())
    check(
        "every declared mode appears in the usage",
        passed=all(flag in rendered for flag in bib_modes.MODES),
    )
    check("a write mode is marked as writing", passed="⚑ writes" in rendered)
    check("and a mode's operand is shown", passed="<name>" in rendered)

    # ⚑ THE USAGE FOLLOWS A SUBSTITUTED ROSTER, which is what proves it is rendered rather than
    # recited — a hardcoded block would ignore the argument entirely.
    small = "\n".join(bib_cli.usage({"--only": Mode(why="the only mode")}))
    check(
        "the usage renders whatever roster it is given",
        passed="--only" in small and "--entries" not in small,
    )

    # ── dispatch reaches the declared handler ────────────────────────────────
    lines, code = bib_cli.run(["--entries", "some.bib"], handlers)
    check("a declared, wired mode runs its handler", passed=code == 0 and lines == ("ran",))

    # ── a declared mode with NO handler is named, not silently usage'd ───────
    # ⚑⚑ REACHABLE THE MOMENT SOMEONE ADDS A `Mode` AND FORGETS THE TABLE.
    partial = {f: h for f, h in handlers.items() if f != "--edges"}
    lines, code = bib_cli.run(["--edges", "a.bib"], partial)
    check("a declared mode with no handler refuses", passed=code == bib_cli.REFUSED)
    check(
        "and says the roster names it",
        passed=any("declared but not wired" in line for line in lines),
    )
    check("and names the mode", passed=any("--edges" in line for line in lines))

    # ── the roster binds the table in both directions ────────────────────────
    missing, extra = bib_modes.unbound(handlers)
    check("a complete table leaves nothing unbound", passed=missing == () and extra == ())
    check(
        "and a partial table names what is missing",
        passed=bib_modes.unbound(partial)[0] == ("--edges",),
    )

    # ── the render helper appends the denominator ────────────────────────────
    # ⚑ EVERY READ ENDS WITH `n of m`, which is why it is a function rather than a convention each
    # branch remembers to honour.
    shown = bib_cli.render(("row",), bib_report.Census("orphans", found=0, population=84))
    check("render keeps the rows", passed=shown[0] == "row")
    check("and appends the census line", passed="0 of 84" in shown[-1])

    # ── the refusal code is the parser's, not a second constant ──────────────
    check(
        "the refusal code is read from the parser",
        passed=bib_argv.Refusal("").code == bib_cli.REFUSED,
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-cli selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
