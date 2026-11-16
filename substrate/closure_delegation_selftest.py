#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.closure_delegation` — the discarded half, and the search it replaces.

⚑⚑⚑ THE DISCARD CASE IS THE SUBJECT. `a, b = rests_closure(...)` keeps both halves;
`a = rests_closure(...)` keeps the pair and then indexes `[0]`, which is the blind spot — a walk
that agrees with the engine about what EXISTS while never seeing what is BROKEN. The two spellings
differ by one comma, and a substring search cannot tell them apart at all.

⚑⚑ AND THE MENTION CASE IS WHY THIS READS THE RELATION. The origin's predicate was
`"rests_closure" not in src`, so a docstring naming the function counted as a call and a call made
through an alias did not. Both fixtures are here: prose that must NOT count, and an attribute call
that MUST.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading the live corpus measures today's call sites —
MEASURED: exactly one, consuming both returns — so a case pinning that would report the corpus
rather than the reader, and would go red the moment someone adds a second caller.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import closure_delegation

# The correct shape: both halves bound.
_UNPACKED = '''def walk() -> None:
    """A walk that keeps the dangling edges."""
    reachable, dangling = rests_closure(seed, entries)
    report(reachable, dangling)
'''

# The defect: the pair is bound whole, and only the first half is ever used.
_DISCARDED = '''def walk() -> None:
    """A walk that throws the dangling edges away."""
    result = rests_closure(seed, entries)
    report(result[0])
'''

# The same call reached through the engine module — an alias a text search misses.
_ATTRIBUTE = '''def walk() -> None:
    """A walk calling through the module."""
    reachable, dangling = bib.rests_closure(seed, entries)
    report(reachable, dangling)
'''

# Prose naming the function without calling it — what a substring search miscounts.
_MENTION = '''def walk() -> None:
    """This walk deliberately does not use rests_closure; see the note on rests_closure.

    ⚑ A docstring naming rests_closure is not a call to rests_closure.
    """
    return None
'''

# A call whose result is discarded entirely.
_BARE = '''def walk() -> None:
    """A walk that invokes the engine and keeps nothing."""
    rests_closure(seed, entries)
'''


def _calls(where: str, text: str) -> tuple[closure_delegation.Call, ...]:
    """Write a fixture module and read its call sites back."""
    path = Path(where) / "walker.py"
    path.write_text(text, encoding="utf-8")
    return closure_delegation.calls(path, "walker.py")


def an_unpacked_call_consumes_both_returns(out: list[str]) -> int:
    """Check `a, b = f()` is read as keeping both halves."""
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, _UNPACKED)
    if len(got) != 1 or not got[0].consumes_both:
        out.append(f"selftest: an unpacked call read as {got!r}")
        return 1
    return 0


def a_whole_pair_assignment_discards_a_half(out: list[str]) -> int:
    """Check `a = f()` is reported as discarding — the POSITIVE CONTROL.

    ⚑⚑ THE TWO SPELLINGS DIFFER BY ONE COMMA, and that comma is the entire item. Without this
    arm, a reader calling everything consuming would pass the case above and report a corpus with
    no findings — the false green the origin's substring search produced.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, _DISCARDED)
    if len(got) != 1 or got[0].consumes_both:
        out.append(f"selftest: a discarding call read as {got!r}")
        return 1
    return 0


def a_discarding_call_carries_its_repair(out: list[str]) -> int:
    """Check the finding says what to do, not merely that something is wrong.

    ⚑ A FINDING WITH NO ROUTE IS ONE A READER MUST RE-DERIVE — and the repair here is one comma,
    which is precisely the kind a reader will not guess from a bare verdict.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, _DISCARDED)
    if not got or "unpack" not in got[0].route:
        out.append(f"selftest: a discarding call carries no route: {got!r}")
        return 1
    return 0


def a_consuming_call_carries_no_route(out: list[str]) -> int:
    """Check a correct call is not given a repair.

    ⚑ A ROUTE ON A CLEAN ROW READS AS A FINDING. Offering one for a call that already does the
    right thing trains a reader to ignore the column.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, _UNPACKED)
    if not got or got[0].route:
        out.append(f"selftest: a consuming call carries a route: {got!r}")
        return 1
    return 0


def an_attribute_call_is_seen(out: list[str]) -> int:
    """Check `bib.rests_closure(...)` counts as a call.

    ⚑⚑ THE SPELLING A NAME-ONLY READER MISSES. Both forms are the same call, and a reader seeing
    one reports a false zero for the other — the census-keyed-on-one-spelling defect.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, _ATTRIBUTE)
    if len(got) != 1 or not got[0].consumes_both:
        out.append(f"selftest: an attribute call read as {got!r}")
        return 1
    return 0


def a_mention_is_not_a_call(out: list[str]) -> int:
    """Check prose naming the function is NOT counted.

    ⚑⚑⚑ THE DEFECT THIS MODULE REPLACES. The origin asked `"rests_closure" not in src`, so a
    docstring explaining why the walk does not delegate would have satisfied the predicate — the
    file that most clearly states the problem reading as the file that solved it.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, _MENTION)
    if got != ():
        out.append(f"selftest: a mention was counted as a call: {got!r}")
        return 1
    return 0


def a_bare_call_consumes_neither_half(out: list[str]) -> int:
    """Check an unassigned call is reported as discarding.

    ⚑ IT KEEPS NOTHING, so reporting it as consuming both would excuse the strongest form of the
    very shape the item is about.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, _BARE)
    if len(got) != 1 or got[0].consumes_both:
        out.append(f"selftest: a bare call read as {got!r}")
        return 1
    return 0


def a_call_is_counted_once(out: list[str]) -> int:
    """Check an assigned call is not also reported as a bare one.

    ⚑ THE TWO PASSES MUST BE DISJOINT. An earlier shape walked every `ast.Call` and asked whether
    an assignment shared its line, which read one site twice under two verdicts — a census whose
    total exceeds its population, and whose extra row always says "discarding".
    """
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, _UNPACKED)
    if len(got) != 1:
        out.append(f"selftest: one call site was counted {len(got)} time(s)")
        return 1
    return 0


def a_file_with_no_call_yields_nothing(out: list[str]) -> int:
    """Check a module that never delegates reports no call sites."""
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, "def walk() -> None:\n    return None\n")
    if got != ():
        out.append(f"selftest: a non-delegating file yielded {got!r}")
        return 1
    return 0


def an_unparseable_file_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising.

    ⚑ ONE BAD FILE MUST NOT TAKE A CORPUS-WIDE CENSUS DOWN.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _calls(where, "def broken(:\n")
    if got != ():
        out.append(f"selftest: an unparseable file yielded {got!r}")
        return 1
    return 0


def an_empty_census_says_the_walk_is_re_rolled(out: list[str]) -> int:
    """Check no-calls-anywhere renders as a finding, not as silence.

    ⚑ ZERO CALL SITES IS THE ORIGIN'S OWN VERDICT — *"the walk is re-rolled"* — and it is the one
    reading that must never come back as an empty line.
    """
    if "re-rolled" not in closure_delegation.render(()):
        out.append("selftest: an empty census does not name what zero means")
        return 1
    return 0


def the_render_marks_only_the_discarding_rows(out: list[str]) -> int:
    """Check a clean row and a discarding row are visibly different."""
    rows = (
        closure_delegation.Call(path="a.py", line=1, consumes_both=True),
        closure_delegation.Call(path="b.py", line=2, consumes_both=False),
    )
    text = closure_delegation.render(rows)
    if "consumes both returns" not in text or "⚑" not in text:
        out.append(f"selftest: the render does not distinguish the two rows:\n{text}")
        return 1
    return 0


_ARMS = (
    an_unpacked_call_consumes_both_returns,
    a_whole_pair_assignment_discards_a_half,
    a_discarding_call_carries_its_repair,
    a_consuming_call_carries_no_route,
    an_attribute_call_is_seen,
    a_mention_is_not_a_call,
    a_bare_call_consumes_neither_half,
    a_call_is_counted_once,
    a_file_with_no_call_yields_nothing,
    an_unparseable_file_yields_nothing,
    an_empty_census_says_the_walk_is_re_rolled,
    the_render_marks_only_the_discarding_rows,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"closure-delegation selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"closure-delegation selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
