#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.store_calls` — the CALL lens, and the blind spots it trades for.

⚑⚑⚑ THE ARM THAT MATTERS IS THE ONE THE IMPORT WALK CANNOT DO: a connect inside a FUNCTION BODY
must be found. That is the whole reason this lens exists beside `import_edges`, which correctly
excludes it. A suite asserting only module-level calls would pass over an implementation that
never descended, and the two instruments would then agree — which is a report about one blind
spot, not none.

⚑⚑ AND THE OVER-REPORTING IS PINNED AS A PROPERTY, NOT APOLOGISED FOR IN PROSE. `connect` is a
common verb, so a socket's `connect` is a hit here BY DESIGN; the output is candidates for a
reader to adjudicate. A case asserting that an unrelated `connect` is filtered out would assert
a capability the module explicitly disclaims — and would go red the day someone tried to build
it, teaching the wrong lesson.

⚑⚑ THE NEGATIVE ARM IS THE DISCRIMINATOR AND IT IS DELIBERATE. Without a file that mentions no
roster name, a `connect_sites` returning its whole roster unconditionally passes every positive
case here. That is the constant-predicate failure a positive-only census cannot see.

⚑⚑ AN `isinstance(found, frozenset)` ARM WAS WRITTEN AND WITHDRAWN. The function's declared
return type makes the failure branch statically unreachable, so mypy refuses the file — the type
gate saying, correctly, that the assertion is about the annotation rather than the behaviour. The
memo-agreement arm below is what actually protects the shared cache. **A case that cannot fail is
worse than an absent one**, so this is recorded rather than written.

⚑ A FILE THAT DOES NOT PARSE READS EMPTY, AND THAT IS AN ARM RATHER THAN A HAPPY ACCIDENT. The
swallow is deliberate — a census must not abort on one bad file — but it means a syntax error
reports as CLEAN, which is a false negative in the flattering direction. Pinned so the trade
stays visible to the next reader rather than being rediscovered from a zero.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import store_calls


def _at(directory: Path, body: str) -> str:
    """Write `body` to a fresh file and return its path.

    ⚑ A UNIQUE NAME PER CALL, because `connect_sites` MEMOISES on the path. Reusing one name
    inside a case would return the first body's answer for the second body — the cache
    masquerading as a result.
    """
    path = directory / f"probe_{len(list(directory.iterdir()))}.py"
    path.write_text(body, encoding="utf-8")
    return str(path)


def a_module_level_connect_is_found(out: list[str]) -> int:
    """Check the plain case — a bare call at import scope."""
    with tempfile.TemporaryDirectory() as raw:
        path = _at(Path(raw), "connect()\n")
        if "connect" not in store_calls.connect_sites(path):
            out.append("selftest: a module-level connect() was not found")
            return 1
    return 0


def a_connect_inside_a_function_is_found(out: list[str]) -> int:
    """Check the call the IMPORT walk cannot see — THE REASON THIS LENS EXISTS.

    ⚑⚑ `scratch/scope_store.py` CALLS `store.sandbox_connect` FROM A FUNCTION BODY. The import
    walk correctly excludes it — a deferred import is a different edge — while the suite
    genuinely opens a store. If this census stopped at module scope the two instruments would
    agree and the gap would be invisible.
    """
    with tempfile.TemporaryDirectory() as raw:
        body = "def run() -> None:\n    store.sandbox_connect('x')\n"
        if "sandbox_connect" not in store_calls.connect_sites(_at(Path(raw), body)):
            out.append("selftest: a connect inside a function body was not found")
            return 1
    return 0


def a_connect_nested_several_levels_deep_is_found(out: list[str]) -> int:
    """Check `at any depth` means depth, not one level of descent."""
    with tempfile.TemporaryDirectory() as raw:
        body = (
            "class A:\n"
            "    def m(self) -> None:\n"
            "        if self.flag:\n"
            "            with open('f') as _f:\n"
            "                for _ in range(1):\n"
            "                    try:\n"
            "                        store.tenant()\n"
            "                    except OSError:\n"
            "                        pass\n"
        )
        if "tenant" not in store_calls.connect_sites(_at(Path(raw), body)):
            out.append("selftest: a deeply nested call was not found")
            return 1
    return 0


def an_attribute_call_and_a_bare_call_both_resolve(out: list[str]) -> int:
    """Check both spellings reach the same name — the two shapes `_called_name` handles."""
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        bare = store_calls.connect_sites(_at(base, "tenant()\n"))
        attribute = store_calls.connect_sites(_at(base, "store.tenant()\n"))
        if bare != attribute:
            out.append(f"selftest: the two spellings differ: {bare!r} vs {attribute!r}")
            return 1
        if "tenant" not in bare:
            out.append("selftest: neither spelling resolved to `tenant`")
            return 1
    return 0


def a_file_calling_nothing_in_the_roster_is_empty(out: list[str]) -> int:
    """Check an unrelated file reports NOTHING — THE DISCRIMINATOR.

    ⚑⚑ WITHOUT THIS ARM A `connect_sites` RETURNING ITS WHOLE ROSTER passes every positive case
    above. A census that says yes to everything is indistinguishable from a working one until
    something asks it to say no.
    """
    with tempfile.TemporaryDirectory() as raw:
        body = "def run() -> None:\n    parse()\n    render()\n    walk()\n"
        found = store_calls.connect_sites(_at(Path(raw), body))
        if found:
            out.append(f"selftest: an unrelated file reported {sorted(found)!r}")
            return 1
    return 0


def a_roster_name_that_is_not_called_is_not_a_hit(out: list[str]) -> int:
    """Check a mere MENTION is not a call — the census keys on call sites.

    ⚑ AN IMPORT, AN ASSIGNMENT AND A STRING all name `connect` without invoking it. Counting
    those would make the lens a text search wearing an AST's clothes.
    """
    with tempfile.TemporaryDirectory() as raw:
        body = "from store import connect\nalias = connect\nnote = 'call connect here'\n"
        found = store_calls.connect_sites(_at(Path(raw), body))
        if found:
            out.append(f"selftest: a non-call mention was counted: {sorted(found)!r}")
            return 1
    return 0


def every_roster_name_is_findable(out: list[str]) -> int:
    """Check each declared name is reachable — a shape over the roster, not a named member.

    ⚑ THE ROSTER IS THE AUTHORITY AND MAY GROW. Iterating it rather than naming its members
    means a name added tomorrow is covered without editing this case — and a name added to the
    constant but unreachable by the walk fails here rather than silently reporting zero.
    """
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        for name in sorted(store_calls.CONNECT_CALLS):
            body = f"def run() -> None:\n    store.{name}()\n"
            if name not in store_calls.connect_sites(_at(base, body)):
                out.append(f"selftest: roster name {name!r} is not found by the walk")
                return 1
    return 0


def several_calls_in_one_file_are_all_reported(out: list[str]) -> int:
    """Check the result is the SET of names, not the first one found."""
    with tempfile.TemporaryDirectory() as raw:
        body = "def a() -> None:\n    store.connect()\ndef b() -> None:\n    store.tenant()\n"
        found = store_calls.connect_sites(_at(Path(raw), body))
        if found != frozenset({"connect", "tenant"}):
            out.append(f"selftest: two distinct calls reported as {sorted(found)!r}")
            return 1
    return 0


def an_unparseable_file_reads_empty_rather_than_raising(out: list[str]) -> int:
    """Check a syntax error is swallowed — and RECORD that this is a false negative.

    ⚑⚑ THE SWALLOW IS DELIBERATE AND ALSO A BLIND SPOT. A census must not abort on one bad
    file, but an unparseable store-reacher reports as CLEAN — the flattering direction. Pinned
    here so the trade is visible rather than rediscovered by someone reading a zero.
    """
    with tempfile.TemporaryDirectory() as raw:
        found = store_calls.connect_sites(_at(Path(raw), "def (:\n"))
        if found:
            out.append(f"selftest: an unparseable file reported {sorted(found)!r}")
            return 1
    return 0


def an_absent_file_reads_empty_rather_than_raising(out: list[str]) -> int:
    """Check a missing path is a fact about the read, not an exception through the census."""
    if store_calls.connect_sites("/nonexistent/probe.py"):
        out.append("selftest: a nonexistent path reported call sites")
        return 1
    return 0


def a_second_read_agrees_with_the_first(out: list[str]) -> int:
    """Check the memo returns the same answer rather than a degraded second read.

    ⚑ THIS IS THE CACHE ARM THAT SURVIVED. Asserting the return TYPE is unfalsifiable under the
    annotation; asserting that a repeated read still carries the same non-empty answer is not,
    and it is what a caller relying on the memo actually needs.
    """
    with tempfile.TemporaryDirectory() as raw:
        path = _at(Path(raw), "def run() -> None:\n    store.connect()\n")
        first = store_calls.connect_sites(path)
        if not first:
            out.append("selftest: the fixture found nothing, so the memo arm asserts nothing")
            return 1
        if store_calls.connect_sites(path) != first:
            out.append("selftest: two reads of one file disagree")
            return 1
    return 0


def the_bare_invocation_speaks_rather_than_exiting_silently(out: list[str]) -> int:
    """Check the module SAYS what it is — THE MEASURED DEFECT WAS SILENCE AND EXIT 0.

    ⚑⚑⚑ AN OPERATOR RAN THIS BARE AND WITH A NAME WHILE LOOKING FOR CALL SITES, and read the
    silence as *no matches*. Silence-and-exit-0 is indistinguishable from a query that matched
    nothing — the false-zero class in the CLI surface rather than in a census.

    ⚑ THE TEXT IS ASSERTED TO CARRY THE DISCLAIMER, not merely to be non-empty. A banner that
    said only the module's name would satisfy "it speaks" while leaving the reader with the same
    wrong model of what this tool can answer.
    """
    bad = 0
    text = store_calls.speak()
    if not text.strip():
        out.append("selftest: the bare-invocation text is empty")
        return 1
    for needle in ("LIBRARY", "connect_sites", "NOT A GENERAL CALL CENSUS"):
        if needle not in text:
            out.append(f"selftest: the bare-invocation text omits {needle!r}")
            bad += 1
    return bad


def the_spoken_roster_is_read_from_the_constant(out: list[str]) -> int:
    """Check the help text names every roster member — DERIVED, never restated in prose.

    ⚑ A USAGE LINE LISTING THE THREE NAMES BY HAND is a second spelling that drifts the day a
    fourth is added, which is `census-keyed-on-one-spelling` inside the help text of the tool
    that warns about it. Iterating the constant means a new name is covered without editing this
    case, and a name the text fails to mention fails here.
    """
    text = store_calls.speak()
    missing = [name for name in sorted(store_calls.CONNECT_CALLS) if name not in text]
    if missing:
        out.append(f"selftest: the spoken text omits roster name(s) {missing!r}")
        return 1
    return 0


def the_library_still_answers_its_real_question(out: list[str]) -> int:
    """Check the refusal did NOT swallow the capability — THE PAIR for the arms above.

    ⚑⚑ A MODULE THAT REFUSED EVERYTHING, entry point and function alike, would satisfy every
    refusal arm and read as fixed. What the refusal must remove is the SILENT ZERO, not the
    reading; so the one function this library exists for is asserted to still work beside it.
    """
    with tempfile.TemporaryDirectory() as raw:
        body = "def run() -> None:\n    store.sandbox_connect('x')\n"
        if "sandbox_connect" not in store_calls.connect_sites(_at(Path(raw), body)):
            out.append("selftest: the library stopped answering its own question")
            return 1
    return 0


_ARMS = (
    a_module_level_connect_is_found,
    a_connect_inside_a_function_is_found,
    a_connect_nested_several_levels_deep_is_found,
    an_attribute_call_and_a_bare_call_both_resolve,
    a_file_calling_nothing_in_the_roster_is_empty,
    a_roster_name_that_is_not_called_is_not_a_hit,
    every_roster_name_is_findable,
    several_calls_in_one_file_are_all_reported,
    an_unparseable_file_reads_empty_rather_than_raising,
    an_absent_file_reads_empty_rather_than_raising,
    a_second_read_agrees_with_the_first,
    the_bare_invocation_speaks_rather_than_exiting_silently,
    the_spoken_roster_is_read_from_the_constant,
    the_library_still_answers_its_real_question,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 1 + 1 + 3 + 1 + 1 + 1 + 2 + 3 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"store-calls selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"store-calls selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
