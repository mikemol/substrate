#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.data_numbers` — a reader that flags every numeric literal is useless.

⚑⚑⚑ THE OUT-OF-SCOPE ARMS ARE THE DELIVERABLE, AND THE BRIEF NAMED THE ONE THAT MATTERS MOST: a
case that FAILS if a fixture's expected value is flagged. A string literal may be data the
program USES, and a reader reporting a format width, a SQL limit or a regex repetition would
fire hardest on the query builders and the suites — the most correct code in the tree. That is
strictly worse than reporting nothing, because it reads as authoritative while being noise.

⚑⚑ THE POSITION IS THE DISCRIMINATOR AND IT IS DRIVEN, NOT ASSUMED. Whether a string is prose
is a fact about its EDGE to a parent node, not a property of its text, so the arms below build
real sources and ask the reader — a text-only check would pass while the edge logic was wrong.

⚑ THE MEASUREMENT JUDGEMENT IS NOT RE-TESTED HERE. `prose_numbers` owns *is this number a
measurement*, with its own exemptions and its own cases; asserting it again would mint a second
authority for one predicate. What these arms cover is exactly what this module adds.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import data_numbers, suite_emit

#: This suite's key, as `suite_discovery` names it.
KEY = "substrate/data_numbers_selftest.py"

#: The motivating shape: a count claimed in a `why=` field, exactly `suite_declared`'s form.
_WHY_FIELD = 'Declared(why="a 56-case suite that grew")\n'

#: The same claim through an explanatory ASSIGNMENT target rather than a keyword.
_WHY_NAME = 'REASON = "the census read 42 modules"\n'

#: ⚑⚑⚑ A FIXTURE'S EXPECTED OUTPUT — the case the brief demanded must NOT be flagged. The
#: number is the value under test; the program consumes it, and nothing about the tree can make
#: it drift.
_FIXTURE = 'check("the suite ran", run(), "57 cases ran")\n'

#: A format string — the number is a width, an operand's companion.
_FORMAT = 'why = "processed {} of 130 rows"\n'

#: A SQL fragment — the number is a limit the query needs.
_SQL = 'why = "SELECT name FROM cores LIMIT 25 rows"\n'

#: A regex — the number is a repetition count.
_REGEX = 'why = "matches \\\\d{3} lines each"\n'


def _write(src: str) -> Path:
    """Write a python fixture and return its path.

    ⚑ A REAL FILE, BECAUSE THE READER PARSES A PATH AND WALKS PARENT EDGES. Handing it a string
    through a private seam would skip the very map that decides prose from data.
    """
    path = Path(tempfile.mkdtemp()) / "fixture.py"
    path.write_text(src, encoding="utf-8")
    return path


def _numbers(src: str) -> list[str]:
    """Return the numbers this reader flags in one source."""
    found, _refused = data_numbers.scan(_write(src))
    return [f.number for f in found]


def _positions(src: str) -> list[str]:
    """Return the positions this reader attributes each finding to."""
    found, _refused = data_numbers.scan(_write(src))
    return [f.position for f in found]


def _claims(src: str) -> list[bool]:
    """Return whether each finding is a CLAIM rather than a mention."""
    found, _refused = data_numbers.scan(_write(src))
    return [f.claim for f in found]


def cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case, in order."""
    out: list[tuple[str, bool]] = []

    def check(label: str, got: object, want: object) -> None:
        out.append((f"{label}: got {got!r}, want {want!r}", got == want))

    # ── IN SCOPE: prose sitting in a data position ─────────────────────────────────────
    # ⚑⚑⚑ THE MOTIVATING INSTANCE. `suite_declared.py`'s `why=` claimed a case count its own
    # suite contradicted, and `prose_numbers` could not see it because `code_lines` correctly
    # calls a data string CODE. This arm is the whole reason the module exists.
    check("a count in a why= field is found", _numbers(_WHY_FIELD), ["56"])
    check("and it is attributed to the keyword position", _positions(_WHY_FIELD), ["keyword"])
    # ⚑ THE SAME ACT ONE SYNTACTIC STEP OVER. Keying only on keywords would report the shape as
    # absent wherever an author used a variable — census-keyed-on-one-spelling, again.
    check("a count in an explanatory assignment is found", _numbers(_WHY_NAME), ["42"])
    check("and it is attributed to the name position", _positions(_WHY_NAME), ["name"])

    # ── ⚑⚑⚑ OUT OF SCOPE: the number is the PROGRAM'S business ─────────────────────────
    # THE CASE THE BRIEF REQUIRED. A fixture's expected output must never be flagged: the value
    # is under test, the program consumes it, and it cannot drift against any tool. This arm
    # goes red the moment the reader starts admitting positional string arguments.
    check("⚑ a FIXTURE's expected value is NOT flagged", _numbers(_FIXTURE), [])
    # ⚑ EACH OF THESE GOES RED IF ITS REFUSAL RULE IS DELETED, and each would fire on the most
    # correct code in the tree — the query builders, the renderers, the suites.
    check("a format string is NOT flagged", _numbers(_FORMAT), [])
    check("a SQL fragment is NOT flagged", _numbers(_SQL), [])
    check("a regex is NOT flagged", _numbers(_REGEX), [])

    # ── the REFUSAL RULES, each named so over-refusal is auditable ──────────────────────
    check(
        "a format string names the format rule",
        data_numbers.refusal_for("processed {} of 130 rows"),
        "a format string — the number is a width or a placeholder's operand",
    )
    check(
        "a SQL fragment names the SQL rule",
        data_numbers.refusal_for("SELECT x FROM t LIMIT 25"),
        "a SQL fragment — the number is a limit, an offset or a bound",
    )
    check(
        "a regex names the regex rule",
        data_numbers.refusal_for("matches \\d{3} lines"),
        "a regex — the number is a repetition count or a class bound",
    )
    check(
        "an ordinary explanation is refused by NO rule",
        data_numbers.refusal_for("a 56-case suite that grew"),
        None,
    )

    # ── ⚑⚑ MENTION vs USE: the one place data is CLEANER than prose ─────────────────────
    # `prose_numbers` reports an upper bound because a quoted specimen and a claim are both just
    # a number beside a noun. A `why=` field is different in KIND — it is addressed to a reader
    # and asserts — so this reader says CLAIM there rather than hedging uniformly. That
    # sharpening is asserted, or it would silently decay back into a uniform upper bound.
    check("a keyword field is a CLAIM, not a mention", _claims(_WHY_FIELD), [True])
    check("an explanatory name is reported as a mention", _claims(_WHY_NAME), [False])

    # ── a string in NO prose position is not this reader's business ─────────────────────
    # ⚑ A POSITIONAL ARGUMENT IS ADDRESSED TO THE MACHINE. Admitting it would make this reader
    # report every string in the tree, which is the failure mode the whole module guards.
    check("a plain positional string is not scanned", _numbers('run("57 cases ran")\n'), [])
    # ⚑ AND A DOCSTRING IS `prose_numbers`' POPULATION, NOT THIS ONE. Reporting it here would
    # double-count every figure across the two censuses.
    check("a docstring is left to prose_numbers", _numbers('"""There are 56 cases here."""\n'), [])

    # ── the BOUNDARIES are declared, not implied ────────────────────────────────────────
    # ⚑⚑ A ZERO FROM THIS READER IS A FACT ABOUT THE POSITIONS IT KNOWS. The boundaries are DATA
    # so the CLI can print them on every run; a suite letting them fall empty would let the tool
    # ship a confident zero with nothing saying what it could not match.
    check(
        "the reader declares what it cannot see",
        [b for b in data_numbers.BOUNDARIES if not b.strip()],
        [],
    )
    # ⚑ THE INHERITED BOUNDARY IS DECLARED. This reader delegates the measurement judgement, so
    # it inherits every limit of that judgement; a boundary set that omitted this would overstate
    # what a clean run here means.
    check(
        "the inherited prose_numbers boundaries are declared",
        [w for w in ["prose_numbers"] if not [b for b in data_numbers.BOUNDARIES if w in b]],
        [],
    )
    # ⚑ AND THE UPPER-BOUND HONESTY SURVIVES, scoped rather than uniform.
    check(
        "the upper-bound honesty is declared, scoped",
        [w for w in ["UPPER BOUND"] if not [b for b in data_numbers.BOUNDARIES if w in b]],
        [],
    )

    # ── an unparseable file is not a silent zero ────────────────────────────────────────
    check("an unparseable file yields nothing, does not raise", _numbers("def (:\n"), [])

    return out


def selftest() -> int:
    """Run every case and report through the typed record; return 0 when all pass."""
    rows = cases()
    bad = [label for label, ok in rows if not ok]
    for label in bad:
        sys.stderr.write(f"  FAIL {label}\n")
    return suite_emit.report(KEY, len(rows) - len(bad), len(rows))


if __name__ == "__main__":
    raise SystemExit(selftest())
