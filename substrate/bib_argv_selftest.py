# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.bib_argv` — one per defect the origin's comments record.

⚑⚑⚑ A DRAIN IS ONLY FAITHFUL IF IT REPRODUCES WHAT THE ORIGIN LEARNED. `scratch/bibstruct.py`'s
argv handling carries four recorded defects in its comments, each measured rather than imagined,
and each is a case here: a trailing bib path swallowed into a field's VALUE, a write-target flag
accepted by a read mode and silently dropped from the read set, a corpus flag consuming greedily
past the next flag, and a write verb reaching the guard but not the recogniser.

⚑⚑ THE COMMON SHAPE IS SILENT MISDIRECTION, so every case asserts a REFUSAL rather than a repair.
A tool that ran, produced a plausible answer, and answered about the wrong thing is worse than one
that stopped: the peer who hit the read-mode case reasonably read a clean corpus as broken.
"""

from __future__ import annotations

from substrate import bib_argv


def _cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case."""
    out: list[tuple[str, bool]] = []

    def check(label: str, *, passed: bool) -> None:
        out.append((label, passed))

    # ── the mode is recognised, and the rosters agree ────────────────────────
    # ⚑ TWO ROSTERS OF ONE FACT, DISAGREEING, is the origin's recorded defect: a third write verb
    # reached the `--bib` guard but not the recogniser, so the refusal named only its siblings.
    check(
        "every write mode is a known mode",
        passed=all(m in bib_argv.known_modes() for m in bib_argv.WRITE_MODES),
    )
    check(
        "and every read mode is too",
        passed=all(m in bib_argv.known_modes() for m in bib_argv.READ_MODES),
    )
    check(
        "the two rosters do not overlap",
        passed=not set(bib_argv.WRITE_MODES) & set(bib_argv.READ_MODES),
    )

    # ── the write target ─────────────────────────────────────────────────────
    got = bib_argv.parse(["--add", "K", "f=v", "--bib", "t.bib"])
    check(
        "a write mode takes its target as a flag",
        passed=isinstance(got, bib_argv.Parsed) and got.target == "t.bib",
    )
    check(
        "and the target is not also an operand",
        passed=isinstance(got, bib_argv.Parsed) and "t.bib" not in got.paths,
    )

    # ⚑⚑ THE READ-MODE CASE, AND IT IS THE ONE A PEER MEASURED. Accepting the write-target flag
    # on a read silently DROPPED the named file from the read set and reported false dangling
    # edges for every premise defined there — over-reporting, the dangerous direction.
    refused = bib_argv.parse(["--orphans", "--bib", "a.bib", "b.bib"])
    check("a read mode REFUSES the write-target flag", passed=isinstance(refused, bib_argv.Refusal))
    check(
        "and the refusal says the read takes its corpus positionally",
        passed=isinstance(refused, bib_argv.Refusal) and "POSITIONALLY" in refused.message,
    )

    check(
        "a target flag with no path refuses",
        passed=isinstance(bib_argv.parse(["--add", "--bib"]), bib_argv.Refusal),
    )

    # ⚑⚑⚑ AND A WRITE NAMING NO TARGET AT ALL REFUSES, which is the case a peer hit three times
    # in one day and routed around with a text editor. The reader answered `24 of 24` over their
    # floor while the writer refused the same key with `have 0` — a fact about the corpus the
    # writer DEFAULTED to, wearing the grammar of a fact about their file. Asserted for EVERY
    # write verb rather than for `--add`, because the origin's measured defect was one verb
    # receiving a repair its siblings did not.
    for verb in bib_argv.WRITE_MODES:
        check(
            f"{verb} refuses when it names no target",
            passed=isinstance(bib_argv.parse([verb, "K", "f=v"]), bib_argv.Refusal),
        )

    # ⚑ THE OTHER DIRECTION, or the assertion above passes against a parser that refuses every
    # write. A refusal nothing can satisfy is not a guard.
    targeted = bib_argv.parse(["--set", "K", "note", "v", "--bib", "t.bib"])
    check(
        "and a write that names one still parses",
        passed=isinstance(targeted, bib_argv.Parsed) and targeted.target == "t.bib",
    )

    # ⚑ READ MODES ARE UNTOUCHED — they take their corpus POSITIONALLY, so a read with no `--bib`
    # is correct rather than under-specified. Pinned because the refusal keys on WRITE_MODES, and
    # a future merge of the two rosters would silently break every read.
    check(
        "a read mode with no target is not refused",
        passed=isinstance(bib_argv.parse(["--edges", "a.bib"]), bib_argv.Parsed),
    )

    # ── the corpus flag stops at the next flag ───────────────────────────────
    # ⚑⚑⚑ GREEDY CONSUMPTION ATE THE WRITE TARGET. `--corpus a.bib --bib t.bib` swallowed
    # `t.bib`, leaving the write to fall through to the DEFAULT bib — so a write aimed at a
    # peer's file diffed cleanly against one the author never named.
    ordered = bib_argv.parse(["--add", "K", "--corpus", "a.bib", "--bib", "t.bib"])
    check(
        "the corpus flag stops at the next flag",
        passed=isinstance(ordered, bib_argv.Parsed) and ordered.corpus == ("a.bib",),
    )
    check(
        "so the write target survives corpus-first ordering",
        passed=isinstance(ordered, bib_argv.Parsed) and ordered.target == "t.bib",
    )

    check(
        "a read mode REFUSES the corpus flag",
        passed=isinstance(bib_argv.parse(["--edges", "--corpus", "a.bib"]), bib_argv.Refusal),
    )
    check(
        "an empty corpus refuses rather than passing silently",
        passed=isinstance(bib_argv.parse(["--add", "K", "--corpus", "--apply"]), bib_argv.Refusal),
    )

    # ── the stray positional is named, not eaten ─────────────────────────────
    # ⚑ THE ORIGIN APPENDED IT TO THE PREVIOUS FIELD'S VALUE, so a `check` field silently grew a
    # filesystem path. Refusing names the operand instead of writing it into the entry.
    stray = bib_argv.parse(["--add", "K", "claim=c", "other.bib"])
    check("a trailing bib on a write mode refuses", passed=isinstance(stray, bib_argv.Refusal))
    check(
        "and the refusal names the flag that owns it",
        passed=isinstance(stray, bib_argv.Refusal) and bib_argv.TARGET_FLAG in stray.message,
    )

    # ⚑ AND A READ MODE'S TRAILING BIB IS FINE — that is how a read names its corpus, so the
    # refusal must not fire there.
    read = bib_argv.parse(["--entries", "some.bib"])
    check(
        "a read mode keeps its positional bib",
        passed=isinstance(read, bib_argv.Parsed) and read.paths == ("some.bib",),
    )

    # ── the writes property ──────────────────────────────────────────────────
    check(
        "a write mode reports that it writes",
        passed=isinstance(got, bib_argv.Parsed) and got.writes,
    )
    check("and a read mode does not", passed=isinstance(read, bib_argv.Parsed) and not read.writes)

    # ── `rest` carries the modifiers, and it was EMPTY FOREVER ───────────────
    # ⚑⚑⚑ DECLARED BUT NEVER POPULATED UNTIL A CONSUMER NEEDED IT. `Parsed.rest` was a field from
    # the start and `parse` never filled it, so `--apply` was INVISIBLE and every write silently
    # took the dry-run branch. Nothing found it until a suite asserted a write actually landed —
    # a field nothing fills is the built-then-orphaned shape inside a dataclass, and it fails in
    # the safe-looking direction, which is why it survived.
    applied = bib_argv.parse(["--add", "K", "f=v", "--apply", "--bib", "t.bib"])
    check(
        "a modifier flag reaches `rest`",
        passed=isinstance(applied, bib_argv.Parsed) and "--apply" in applied.rest,
    )
    check(
        "and the mode itself is not a modifier",
        passed=isinstance(applied, bib_argv.Parsed) and "--add" not in applied.rest,
    )
    check(
        "an invocation with no modifiers has an empty rest",
        passed=isinstance(read, bib_argv.Parsed) and read.rest == (),
    )

    # ── an unknown mode parses to None rather than raising ───────────────────
    # ⚑ THE CALLER DECIDES WHAT AN ABSENT MODE MEANS — bare argv prints usage, which is not this
    # module's judgement to make.
    check(
        "an unrecognised mode is None, not an error",
        passed=isinstance(bib_argv.parse(["--nope"]), bib_argv.Parsed),
    )

    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = _cases()
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"bib-argv selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    import sys

    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
