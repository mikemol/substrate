# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_modes` — the roster is one authority, and both drift directions.

⚑⚑⚑ THE LOAD-BEARING CASES ARE THE TWO UNBINDING DIRECTIONS, because they are different defects
and the origin had one of them invisibly. A DECLARED mode with no handler is *"a promise the CLI
does not keep that still feeds arity resolution"*; a HANDLED flag with no declaration is a branch
a user can reach and no reader can see. The origin had eight of the second kind, and nothing could
report either.

⚑⚑ AND THE ROSTER-IS-ONE-AUTHORITY CASE IS THE ORIGIN'S MEASURED DEFECT. Write verbs were named
twice — a `WRITE_MODES` tuple and an inline `known` set — so `--addfield` reached the `--bib` guard
and never the recogniser, and its refusal listed only the other two verbs. Here both rosters are
DERIVED from one table, so the case asserts they partition it rather than agreeing by luck.

⚑ THE `mutates`-IS-DERIVED CASE GUARDS A PROPERTY OF `climode.Mode` THIS MODULE RELIES ON. If
`mutates` were ever a stored peer field it could disagree with `writes`, and every derivation here
would silently split. Asserting it tracks `writes` is asserting the invariant this table is built
on, not testing someone else's class.
"""

from __future__ import annotations

from substrate import bib_modes


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the roster is ONE authority ──────────────────────────────────────────
    # ⚑ THE ORIGIN'S DEFECT: two rosters of one fact, disagreeing. Both are derived here, so the
    # assertion is that they PARTITION the table — no verb in both, none in neither.
    both = set(bib_modes.WRITE_MODES) & set(bib_modes.READ_MODES)
    covered = set(bib_modes.WRITE_MODES) | set(bib_modes.READ_MODES) | {"--selftest"}
    check("no verb is both a read and a write", passed=not both)
    check("and every declared mode is one or the other", passed=covered == set(bib_modes.MODES))

    # ⚑ EVERY WRITE VERB, NAMED. `--addfield` is the one the origin's second roster missed;
    # `--delete` is the fourth, added for the duplicated sql-F34/F35 entries; `--rename` the fifth,
    # the findings roster's re-key successor — each landing turned this case red, the pin working.
    check(
        "every write verb is derived, --addfield, --delete and --rename included",
        passed=set(bib_modes.WRITE_MODES)
        == {"--add", "--set", "--addfield", "--delete", "--rename"},
    )

    # ── `mutates` tracks `writes`, which is what the derivation rests on ─────
    check(
        "a mode declaring an artifact kind mutates",
        passed=all(bib_modes.MODES[f].mutates for f in bib_modes.WRITE_MODES),
    )
    check(
        "and a mode declaring none does not",
        passed=not any(bib_modes.MODES[f].mutates for f in bib_modes.READ_MODES),
    )
    check(
        "the write verbs declare WHICH kind, not merely that they write",
        passed=all(bib_modes.MODES[f].writes == (".bib",) for f in bib_modes.WRITE_MODES),
    )

    # ── arity is declared, never guessed ─────────────────────────────────────
    # ⚑⚑ THE MEASURED COST OF GUESSING: `--key --archive f.py` crashed because an undeclared
    # mode's operand bound the next token, which was another flag's path.
    check("a mode taking a name declares it", passed=bib_modes.operand_of("--field") == "name")
    check("and a nullary mode declares none", passed=bib_modes.operand_of("--orphans") is None)
    check(
        "an unknown flag has no operand rather than a guessed one",
        passed=bib_modes.operand_of("--nope") is None,
    )
    check(
        "both name-taking reads declare the operand",
        passed=bib_modes.operand_of("--mentions") == "name",
    )

    # ── a modifier is owned by a mode, not globally true ─────────────────────
    # ⚑ `--bib` IS THE WRITE TARGET. Accepting it on a read DROPPED the named file from the read
    # set and produced false dangling edges against a peer's clean corpus.
    check("a write mode accepts the target flag", passed=bib_modes.accepts("--add", "--bib"))
    check("and a read mode does NOT", passed=not bib_modes.accepts("--orphans", "--bib"))
    check(
        "a read mode accepts no corpus flag either",
        passed=not bib_modes.accepts("--edges", "--corpus"),
    )
    check(
        "every write mode accepts --apply",
        passed=all(bib_modes.accepts(f, "--apply") for f in bib_modes.WRITE_MODES),
    )

    # ── membership ───────────────────────────────────────────────────────────
    check("a declared flag is known", passed=bib_modes.known("--entries"))
    check("an undeclared flag is not", passed=not bib_modes.known("--defs"))

    # ── dispatch is a lookup, and BOTH drift directions are reported ─────────
    full: dict[str, object] = dict.fromkeys(bib_modes.MODES, 0)
    handlers = {flag: (lambda: 0) for flag in full}
    missing, extra = bib_modes.unbound(handlers)
    check("a complete table has no unbound declaration", passed=missing == ())
    check("and no undeclared handler", passed=extra == ())

    # ⚑ A DECLARED MODE WITH NO HANDLER — the promise the CLI does not keep.
    short = {f: h for f, h in handlers.items() if f != "--edges"}
    check(
        "a declared mode with no handler is reported",
        passed=bib_modes.unbound(short)[0] == ("--edges",),
    )

    # ⚑⚑ A HANDLED FLAG WITH NO DECLARATION — the origin's invisible defect, eight times over.
    wide = dict(handlers)
    wide["--undeclared"] = lambda: 0
    check(
        "a handler with no declaration is reported",
        passed=bib_modes.unbound(wide)[1] == ("--undeclared",),
    )
    check(
        "and the two directions do not confuse each other", passed=bib_modes.unbound(wide)[0] == ()
    )

    # ── dispatch resolves only what the roster names ─────────────────────────
    check(
        "dispatch returns the declared handler",
        passed=bib_modes.dispatch("--edges", handlers) is not None,
    )
    check(
        "and refuses a flag the roster does not name",
        passed=bib_modes.dispatch("--undeclared", wide) is None,
    )

    # ── every mode says WHY, which is what a reader reads ────────────────────
    check(
        "every declared mode carries a reason",
        passed=all(mode.why for mode in bib_modes.MODES.values()),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-modes selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
