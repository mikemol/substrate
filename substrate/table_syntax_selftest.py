# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.table_syntax` — an estimate that says so, and a rule that is not one.

⚑⚑⚑ THE REMAINDER ARM IS THE REPAIR. The origin divided a dashed-rule count by three and returned
the quotient as a table count, so a headerless or truncated multiline table shifted the figure with
nothing saying so. Here the rule count travels beside the quotient, and the arms assert that a
document whose rules do NOT group cleanly says so in its own account.

⚑⚑ THE PIPE-VERSUS-MULTILINE DISCRIMINATION IS THE ONE A NAIVE SCAN GETS WRONG. Both are dashes;
only the absence of a pipe separates them. A rule counting every dashed line would inflate the
multiline estimate by exactly the documents that contain no multiline tables — every pipe table in
the corpus would register as a third of one.

⚑ AND THE SENSITIVITY ARM DROPS THE PIPE CONDITION, because every arm above feeds correct input and
none of them shows that the condition is doing work rather than being satisfied incidentally.
"""

from __future__ import annotations

import sys

from substrate import table_syntax as ts

#: A pipe table: delimiter row plus content.
PIPE_TABLE = [
    "| name | home |",
    "|------|------|",
    "| a    | b    |",
]

#: A complete multiline table: open rule, header, separator rule, body, close rule.
MULTILINE_TABLE = [
    "-------------------------",
    "name          home",
    "-------------------------",
    "alpha         one",
    "-------------------------",
]

#: A grid table's opening rule.
GRID_ROW = ["+------+------+"]

#: How many dashed rules a complete multiline table carries.
RULES = 3

#: How many rules a headerless or truncated multiline table leaves behind.
PARTIAL_RULES = 2


def _discrimination_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for telling the three syntaxes apart."""
    out: list[tuple[str, bool]] = []

    got = ts.forms(PIPE_TABLE)
    out.append((f"a pipe table counts as pipe — {got.why()}", got.pipe == 1))
    # ⚑⚑ THE DELIMITER ROW IS DASHES AND MUST NOT COUNT AS A MULTILINE RULE. This is the arm that
    # a scan counting every dashed line fails, and it fails on every pipe table in the corpus.
    out.append((f"and contributes no multiline rules: {got.rules}", got.rules == 0))

    multi = ts.forms(MULTILINE_TABLE)
    out.append(
        (f"a multiline table is estimated from its rules — {multi.why()}", multi.multiline == 1)
    )
    out.append((f"and its rule count is carried: {multi.rules}", multi.rules == RULES))
    out.append((f"and it registers no pipe rows: {multi.pipe}", multi.pipe == 0))

    grid = ts.forms(GRID_ROW)
    out.append((f"a grid rule counts as grid — {grid.why()}", grid.grid == 1))
    return out


def _estimate_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the estimate declaring itself an estimate.

    ⚑⚑⚑ THE ORIGIN RETURNED A ROUNDED QUOTIENT AND CALLED IT A COUNT. A multiline table missing its
    header separator carries two rules, not three, so the quotient reads zero while a table is
    plainly there. The remainder is the signal that the grouping assumption broke, and these arms
    assert it reaches the caller rather than being rounded away.
    """
    out: list[tuple[str, bool]] = []

    clean = ts.forms(MULTILINE_TABLE)
    out.append((f"a complete table leaves no remainder: {clean.remainder}", clean.remainder == 0))
    out.append(
        (
            f"and its account says so: {'none left over' in clean.why()}",
            "none left over" in clean.why(),
        )
    )

    # ⚑ A TWO-RULE TABLE — headerless, or truncated. The quotient rounds to zero while the rules
    # are visibly there, which is exactly the case the origin reported as "no tables".
    partial = ts.forms([*MULTILINE_TABLE[:2], *MULTILINE_TABLE[3:]])
    out.append(
        (f"a two-rule table estimates 0 tables: {partial.multiline}", partial.multiline == 0)
    )
    out.append(
        (f"but the rules are still reported: {partial.rules}", partial.rules == PARTIAL_RULES)
    )
    out.append(
        (f"and the remainder is non-zero: {partial.remainder}", partial.remainder == PARTIAL_RULES)
    )
    # ⚑⚑ AND THE ACCOUNT NAMES IT AS AN ESTIMATE, so a reader of the line does not have to know
    # the derivation to distrust the figure.
    out.append(
        (
            f"the account flags the estimate: {'ESTIMATE' in partial.why()}",
            "ESTIMATE" in partial.why(),
        )
    )
    return out


def _style_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the pipe-spacing population."""
    out: list[tuple[str, bool]] = []

    canonical = ts.style(PIPE_TABLE)
    out.append((f"a canonical table has no hits: {canonical}", canonical == []))

    # ⚑⚑⚑ THE DELIMITER ROW IS THE FALSE-POSITIVE CLASS (gate-G241). `|---|---|` has no space
    # beside its interior pipes and is CANONICAL — the rule governs content rows. Measured on the
    # live plan, every one of the origin's four hits was a delimiter row, so its whole reported
    # population was spurious. This arm is what stops that returning.
    delimiter_only = ts.style(["|------|------|"])
    out.append((f"a delimiter row is NOT a violation: {delimiter_only}", delimiter_only == []))
    out.append(
        (
            f"and a compact one is not either: {ts.style(['|---|---|'])}",
            ts.style(["|---|---|"]) == [],
        )
    )

    # ⚑⚑ THE SIDE NAMED IS THE SIDE OF THE *PIPE*, NOT OF THE CELL, AND I HAD IT BACKWARDS.
    # In `| a| b |` the offending pipe is the one CLOSING cell `a`, and what it lacks is a space
    # to its LEFT. I wrote the case expecting RIGHT because I was thinking about the cell's
    # trailing space. The scan checks left before right per pipe, so left wins when both are
    # cramped — pinned here so the convention is stated rather than rediscovered.
    cramped = ts.style(["| a| b |"])
    out.append((f"a cramped closing pipe is caught: {cramped}", len(cramped) == 1))
    out.append((f"and named for the PIPE's side: {cramped[0].kind!r}", "LEFT" in cramped[0].kind))
    out.append((f"and located: line {cramped[0].line}", cramped[0].line == 1))

    right = ts.style(["| a |b |"])
    out.append(
        (f"a cramped opening pipe reports RIGHT: {right[0].kind!r}", "RIGHT" in right[0].kind)
    )

    # ⚑ ONE HIT PER LINE, NOT PER PIPE. A row with several cramped pipes is ONE repair, and
    # reporting it repeatedly would make the population read as more work than it is.
    many = ts.style(["|a|b|c|"])
    out.append((f"a row with several cramped pipes reports once: {len(many)}", len(many) == 1))

    # ⚑ AND THE LINE NUMBER IS 1-INDEXED against the input, so a hit can be opened.
    later = ts.style(["", "", "| a| b |"])
    out.append((f"line numbers are 1-indexed: {later[0].line}", later[0].line == RULES))
    return out


def _sensitivity_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the no-pipe condition is load-bearing.

    ⚑⚑ EVERY DISCRIMINATION ARM ABOVE FEEDS WELL-FORMED INPUT, so none of them shows that
    `is_multiline_rule`'s pipe exclusion does work rather than being satisfied by accident. This
    computes what the predicate WOULD answer without that condition and asserts it differs — a
    pipe table's delimiter row would register as a multiline rule.
    """
    out: list[tuple[str, bool]] = []
    delimiter = "|------|------|"

    real = ts.is_multiline_rule(delimiter)
    stripped = delimiter.strip()
    naive = bool(stripped) and stripped.count("-") > ts.MIN_RULE

    out.append(
        (f"without the no-pipe test a delimiter WOULD count: {naive} vs {real}", naive and not real)
    )
    return out


def _control_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the negative controls.

    ⚑ A CLASSIFIER THAT COUNTED EVERYTHING would pass every positive arm, so prose must register
    nothing — and an empty document must report zeroes rather than raising.
    """
    out: list[tuple[str, bool]] = []

    prose = ts.forms(["ordinary prose", "with no tables at all", "-- a short dash --"])
    out.append(
        (
            f"prose registers nothing: {prose.why()}",
            (prose.pipe, prose.multiline, prose.grid, prose.rules) == (0, 0, 0, 0),
        )
    )

    empty = ts.forms([])
    out.append((f"an empty document reports zeroes: {empty.why()}", empty.rules == 0))
    out.append((f"and an empty style scan is empty: {ts.style([])}", ts.style([]) == []))

    # ⚑ A LINE MENTIONING ONE PIPE IS NOT A TABLE ROW — the minimum-pipes guard, which stops
    # prose about the shell registering as malformed table style.
    mention = ts.style(["| this is prose about a pipe"])
    out.append((f"a single-pipe line is not a row: {mention}", mention == []))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _discrimination_cases()
        + _estimate_cases()
        + _style_cases()
        + _sensitivity_cases()
        + _control_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"table-syntax selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
