# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_handlers` — driven END TO END through the entry point.

⚑⚑⚑ THESE CASES CALL `bib_cli.run`, NOT THE HANDLERS DIRECTLY, AND THAT IS THE ORIGIN'S OWN
LESSON. Its composed-corpus defect lived entirely in the CLI: the reader was always correct and
`main` passed it only the first path. **A case calling the reader twice by hand would have passed
against the broken code**, because it never touches the layer that dropped the files. So the
invocation is the unit under test.

⚑⚑ EVERY READ IS ASSERTED TO CARRY ITS DENOMINATOR. A zero with no population beside it cannot
distinguish a total read from one that examined nothing, and the origin shipped `--roundtrip`
without the second number until a reader could not tell them apart.

⚑ THE PARSER IS A FIXTURE, WHICH IS WHY NO FILE IS WRITTEN. `bind()` takes the bib reader, so the
whole CLI runs over in-memory bibs — where the origin's suite had to write real files to say
anything about its readers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import bib_cli, bib_handlers, bib_modes, bib_parse, corpus

if TYPE_CHECKING:
    from pathlib import Path


def _engine_cases() -> list[tuple[str, bool]]:
    """Return the `--dropped` cases, run against the LIVE worklist and the real parser.

    ⚑⚑⚑ THE FIXTURE PARSER CANNOT ANSWER THIS QUESTION. `--dropped` asks what the ENGINE keeps,
    which is a second authority — so the only meaningful case reads a real project with a real
    `paper.toml`.

    ⚑⚑ AND THE LOAD-BEARING ASSERTION IS THAT A DECLARED FIELD IS *NOT* REPORTED. The worklist
    declares `enables` as a consumer field; the origin passed the engine's BARE defaults, so every
    declared field read as dropped forever — fourteen warnings per read against a correctly
    declared field, which the author read as the engine's verdict rather than their own call.
    """
    live = corpus.ROOT / "catalog" / "worklist" / "warrants.bib"
    if not live.exists():
        # ⚑ SKIPPED, NOT FAILED. A suite going red because a file moved reports on the file.
        return [("the live worklist is absent, so the engine cases are skipped", True)]

    handlers = bib_handlers.bind(bib_handlers.Context(parse=bib_parse.read))
    lines, code = bib_cli.run(["--dropped", str(live)], handlers)
    return [
        ("dropped reads the live worklist", code == 0),
        ("and carries its denominator", any(" of " in line for line in lines)),
        # ⚑ THE DECLARED CONSUMER FIELD IS NOT REPORTED — the silently-narrowing-default fix.
        (
            "a DECLARED consumer field is not reported as dropped",
            not any(".enables" in line for line in lines),
        ),
    ]


# ⚑ `B` DECLARES an edge to `A` and carries a DELIBERATE dangler; `M` NAMES `A` in prose. The two
# are separable on purpose: a mention reader that reported `B`'s declared edge would be offering
# the author's own declaration back as evidence for making it.
_W = {
    "A": {"section": "s", "claim": "alpha", "check": "item:A"},
    "B": {"section": "s", "from": "A", "enables": "A, NOSUCH", "claim": "beta", "check": "item:B"},
    "M": {"section": "s", "claim": "this rests on the A case", "check": "item:M"},
}
_W2 = {"C": {"section": "s", "rests-on": "A", "claim": "gamma", "check": "item:C"}}

_BIBS: dict[str, dict[str, dict[str, str]]] = {"w.bib": _W, "w2.bib": _W2}


def _parse(path: Path) -> dict[str, dict[str, str]]:
    """Return the fixture bib at `path`, standing in for the real parser."""
    return _BIBS[path.name]


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    handlers = bib_handlers.bind(bib_handlers.Context(parse=_parse))

    def run(*argv: str) -> tuple[tuple[str, ...], int]:
        return bib_cli.run(list(argv), handlers)

    # ── every declared read is wired ─────────────────────────────────────────
    # ⚑⚑ THE BINDING IS ASSERTED AGAINST THE ROSTER, not counted. A handler for an undeclared flag
    # is a branch no reader can see; a declared mode with no handler is a promise the CLI does not
    # keep. Only the second is expected here, and it is named.
    missing, extra = bib_modes.unbound(handlers)
    check("no handler is bound to an undeclared mode", passed=extra == ())
    check(
        "every bound handler is a declared read",
        passed=all(flag in bib_modes.READ_MODES for flag in handlers),
    )

    # ⚑⚑⚑ COMPLETENESS IS ASKED OF THE ROSTER, NOT TRACKED BY HAND. `unbound` names every declared
    # mode with no handler — the promise-the-CLI-does-not-keep arm — so the read side's coverage is
    # a fact the roster states rather than a note anyone maintains.
    # ⚑⚑ THIS CASE PREVIOUSLY ASSERTED `--dropped` WAS THE ONE GAP, AND IT WENT RED THE MOMENT THE
    # GAP CLOSED. That is the case doing its job: a tracker of remaining work must fail when the
    # work lands, or it is a comment with a test's costs.
    check(
        "every declared READ mode is bound",
        passed=[f for f in missing if f in bib_modes.READ_MODES] == [],
    )
    check(
        "and the write verbs are absent from a READ table by design",
        passed=all(f in missing for f in bib_modes.WRITE_MODES),
    )

    # ── --entries ────────────────────────────────────────────────────────────
    lines, code = run("--entries", "w.bib")
    check("entries succeeds", passed=code == 0)
    check(
        "and lists every key", passed=all(any(k in line for line in lines) for k in ("A", "B", "M"))
    )
    check("and carries its denominator", passed="3 of 3" in lines[-1])

    # ── --field ──────────────────────────────────────────────────────────────
    lines, code = run("--field", "check", "w.bib")
    check("field reports only entries carrying it", passed="3 of 3" in lines[-1])
    lines, _code = run("--field", "from", "w.bib")
    check("...and a sparse field reports the smaller numerator", passed="1 of 3" in lines[-1])
    # ⚑⚑ THE REFUSAL FIRES ON ZERO OPERANDS, AND MY FIRST CASE ASSERTED THE WRONG ONE. I wrote
    # `--field w.bib` expecting a refusal; the roster declares `--field <name> [bib …]`, so a LONE
    # positional is the NAME and the corpus falls back to the default — which crashed the fixture
    # parser rather than refusing. The tool is right and the case was wrong: a single operand is
    # unambiguous BY DECLARATION, and reading it as a path would be the arity guess the roster
    # exists to prevent.
    _lines, code = run("--field")
    check("a field mode with no name refuses", passed=code == bib_cli.REFUSED)

    # ── --mentions: evidence, not declarations ───────────────────────────────
    lines, code = run("--mentions", "A", "w.bib")
    check("mentions succeeds", passed=code == 0)
    check(
        "prose naming the key is reported",
        passed=any("M" in line and "rests on the A case" in line for line in lines),
    )
    # ⚑ `B` DECLARES `from = A`. Reporting it would offer the author's own edge back as evidence.
    check(
        "but a declared edge is NOT reported as a mention",
        passed=not any("from" in line for line in lines[:-1]),
    )
    check("and the denominator excludes the entry itself", passed="of 2" in lines[-1])

    # ── --edges ──────────────────────────────────────────────────────────────
    lines, code = run("--edges", "w.bib")
    check("edges succeeds", passed=code == 0)
    check("and shows the direction", passed=any("->" in line for line in lines))

    # ── --orphans, and the COMPOSED-CORPUS case ──────────────────────────────
    # ⚑⚑⚑ THE ORIGIN'S DEFECT LIVED HERE, IN THE CLI RATHER THAN THE READER. `C rests-on A` with A
    # in the other bib: read alone it dangles, read together it resolves. Same edge, opposite
    # verdicts, decided by what the INVOCATION passed.
    lines, code = run("--orphans", "w2.bib")
    check(
        "a premise in another bib DANGLES when that bib is not passed",
        passed=any("C" in line and "A" in line for line in lines[:-1]),
    )
    check("and the mode exits non-zero on a finding", passed=code == 1)

    lines, code = run("--orphans", "w2.bib", "w.bib")
    # ⚑⚑ THE PREDICATE NAMES THE EDGE, NOT A SUBSTRING, AND MY FIRST CUT MATCHED THE WRONG ROW.
    # It tested `"C" in line and "no such entry" in line`, which the `B -> NOSUCH` row satisfies:
    # "NOSUCH" contains a C. A case that can be satisfied by an unrelated row is not testing the
    # claim it states — the same substring-vs-structure defect `mentions` carries a longest-first
    # guard for, arriving in the assertion instead of the reader.
    resolved = [line for line in lines if "-> A" in line and "no such entry" in line]
    check("...and RESOLVES when both bibs are passed", passed=not resolved)
    check("every bib passed is counted", passed="of 4" in lines[-1])
    # ⚑ THE FIXTURE'S OWN DELIBERATE DANGLER SURVIVES, so "no orphans" is never the assertion.
    check(
        "the deliberate dangler is still reported", passed=any("NOSUCH" in line for line in lines)
    )

    # ── --roundtrip: the one read whose rows are FAILURES ────────────────────
    # ⚑⚑ IT EXITS NON-ZERO ON A FINDING while every other read exits 0 with results. A totality
    # probe that reported its losses and exited 0 would be a gate that cannot go red.
    # ⚑ THE FIXTURE PARSER IS TOTAL BY CONSTRUCTION — it returns a dict, so there is no file for
    # the probe to disagree with. What the case asserts is the CONTRACT: green, a denominator,
    # and the bound printed beside the verdict.
    lines, code = run("--roundtrip", "w.bib")
    check("roundtrip over an accounted-for read exits 0", passed=code == 0)
    check("and carries its denominator", passed=any(" of " in line for line in lines))
    # ⚑⚑⚑ THE BOUND SHIPS WITH THE VERDICT, IN BAND. A green here is an ALGEBRA result about this
    # input; a caveat kept in prose gets summarised away, and this is the read whose green is most
    # likely to be over-read as "the parser has no kernel".
    check(
        "and the total verdict states its own bound",
        passed=any("ALGEBRA" in line for line in lines),
    )
    check("...naming what it does NOT say", passed=any("does NOT say" in line for line in lines))

    # ── a read with no path falls back to the default, not to nothing ────────
    # ⚑ THE DEFAULT IS NAMED ONCE. The origin resolved it inside each branch, so a mode added
    # later got whatever its author remembered.
    check("the default bib is named in one place", passed=bib_handlers.DEFAULT_BIB.endswith(".bib"))

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases() + _engine_cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-handlers selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
