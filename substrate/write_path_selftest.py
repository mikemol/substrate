#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.write_path` — one guard does not protect three writes.

⚑⚑⚑ THE PER-WRITE UNIT IS THE ITEM. The origin asked three substring questions of the whole file,
so one armed write made every other write in it read as armed, and a comment EXPLAINING the
absence of a guard satisfied the check for having one. The arms below drive files holding both a
protected and an unprotected write and assert the two are told apart.

⚑⚑ AND THE ALIASED CALL IS WHY THE READ IS STRUCTURAL. MEASURED on the live tool: `--calls
edit_snapshot` reports 0 calls against 3 refs, because the guard is reached as `_es.guard(...)`
through an aliased import. A census keyed on the module name reports an armed tool as unarmed —
so the question is whether a guard CALL precedes the write, in either spelling.

⚑ THE FIXTURE-SCOPE ARMS ARE THE ONES THAT MOVED THE NUMBER. Live, the census read 26 of 29
unprotected; every flagged row was a temp-file write inside `_selftest`, and one survivor was a
helper DEFINED INSIDE that suite. Excluding by span rather than by name took it to 0 of 3 — a
population the reader had manufactured entirely from its own scope.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import write_path

# What the mixed fixture holds: two writes, one of them unprotected. ⚑ NAMED rather than typed at
# the assertion — a literal there is a number about the fixture wearing the clothes of one about
# the reader, and the gate has no suppression path for either.
_MIXED_WRITES = 2
_MIXED_BAD = 1

# Both protections, missing at once.
_BOTH = 2

# A write that is gated and armed, through an aliased guard.
_PROTECTED = '''"""A tool with a protected write."""


def add(target: str, text: str) -> int:
    """Write, gated and armed."""
    if "--apply" not in sys.argv:
        return 0
    import edit_snapshot as _es
    _es.guard("tool --add", [target])
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0
'''

# The same write with a bare guard call.
_BARE_GUARD = '''"""A tool guarding without an alias."""


def add(target: str, text: str) -> int:
    """Write, gated and armed."""
    if "--apply" not in sys.argv:
        return 0
    guard("tool --add", [target])
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0
'''

# ⚑ THE DEFECT: gated but not armed.
_UNARMED = '''"""A tool that writes without a snapshot."""


def add(target: str, text: str) -> int:
    """Write with no recovery."""
    if "--apply" not in sys.argv:
        return 0
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0
'''

# ⚑ THE OTHER DEFECT: armed but not gated.
_UNGATED = '''"""A tool that writes on a read."""


def add(target: str, text: str) -> int:
    """Write with no dry run."""
    import edit_snapshot as _es
    _es.guard("tool --add", [target])
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0
'''

# ⚑ THE FILE-SCOPE TRAP: one armed write and one unarmed one in the same file.
_MIXED = '''"""A tool with two writes and one guard."""


def add(target: str, text: str) -> int:
    """Write, gated and armed."""
    if "--apply" not in sys.argv:
        return 0
    import edit_snapshot as _es
    _es.guard("tool --add", [target])
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(text)
    return 0


def touch(target: str) -> int:
    """Write with nothing protecting it."""
    with open(target, "a", encoding="utf-8") as fh:
        fh.write("x")
    return 0
'''

# ⚑ THE SCOPE TRAP: fixture writes inside a suite, one through a nested helper.
_FIXTURES = '''"""A tool whose suite writes fixtures."""


def _selftest() -> int:
    """Write fixtures and check them."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "w.bib")
        with open(p, "w", encoding="utf-8") as fh:
            fh.write("@misc{A}\\n")

        def _via_disk(text, name):
            q = os.path.join(d, name)
            with open(q, "w", encoding="utf-8") as fh:
                fh.write(text)
            return q

        _via_disk("x", "y.bib")
    return 0
'''

# A guard called AFTER the write protects nothing.
_LATE_GUARD = '''"""A tool guarding after the fact."""


def add(target: str, text: str) -> int:
    """Write, then guard."""
    if "--apply" not in sys.argv:
        return 0
    with open(target, "w", encoding="utf-8") as fh:
        fh.write(text)
    guard("tool --add", [target])
    return 0
'''

# A read, which owes nothing.
_READ_ONLY = '''"""A tool that only reads."""


def load(target: str) -> str:
    """Read the file."""
    with open(target, encoding="utf-8") as fh:
        return fh.read()
'''


def _writes(where: str, text: str) -> tuple[write_path.Write, ...]:
    """Write a fixture tool and read its write paths back."""
    path = Path(where) / "tool.py"
    path.write_text(text, encoding="utf-8")
    return write_path.writes(path, "tool.py")


def a_protected_write_is_protected(out: list[str]) -> int:
    """Check a gated, armed write through an aliased guard passes."""
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, _PROTECTED)
    if len(got) != 1 or not got[0].protected:
        out.append(f"selftest: a protected write read as {got!r}")
        return 1
    return 0


def a_bare_guard_call_arms(out: list[str]) -> int:
    """Check an unaliased guard call counts.

    ⚑ TWO SPELLINGS OF ONE ACT. Reading only the attribute form would report a bare-guard tool as
    unarmed; reading only the bare form misses every aliased import, which is the live shape.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, _BARE_GUARD)
    if len(got) != 1 or not got[0].armed:
        out.append(f"selftest: a bare guard read as {got!r}")
        return 1
    return 0


def an_unarmed_write_is_reported(out: list[str]) -> int:
    """Check a write with no snapshot is the finding — the POSITIVE CONTROL."""
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, _UNARMED)
    if len(got) != 1 or got[0].armed:
        out.append(f"selftest: an unarmed write read as {got!r}")
        return 1
    if not got[0].gated:
        out.append(f"selftest: a gated write read as ungated: {got!r}")
        return 1
    return 0


def an_ungated_write_is_reported(out: list[str]) -> int:
    """Check a write with no dry-run gate is reported separately.

    ⚑ TWO DIFFERENT REPAIRS. An unarmed write needs a snapshot; an ungated one needs a flag check
    — and one verdict covering both would tell a reader to do the wrong thing half the time.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, _UNGATED)
    if len(got) != 1 or got[0].gated:
        out.append(f"selftest: an ungated write read as {got!r}")
        return 1
    if not got[0].armed:
        out.append(f"selftest: an armed write read as unarmed: {got!r}")
        return 1
    return 0


def one_guard_does_not_cover_two_writes(out: list[str]) -> int:
    """Check a second, unprotected write in the same file is still reported — THE ITEM.

    ⚑⚑⚑ THE FILE-WIDE SUBSTRING TEST PASSES THIS FILE. One armed write makes the whole file read
    as armed, so a tool with three write paths and one guard reports clean.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, _MIXED)
    missing = write_path.unprotected(got)
    if len(got) != _MIXED_WRITES or len(missing) != _MIXED_BAD:
        out.append(f"selftest: the mixed file read as {got!r}")
        return 1
    return 0


def a_late_guard_does_not_arm(out: list[str]) -> int:
    """Check a guard called after the write protects nothing.

    ⚑ ORDER IS THE WHOLE POINT OF A SNAPSHOT. Recording the state after overwriting it captures
    the damage, not the recovery.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, _LATE_GUARD)
    if not got or got[0].armed:
        out.append(f"selftest: a late guard read as arming: {got!r}")
        return 1
    return 0


def a_read_is_not_a_write(out: list[str]) -> int:
    """Check an ordinary read is not a row."""
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, _READ_ONLY)
    if got != ():
        out.append(f"selftest: a read yielded write rows: {got!r}")
        return 1
    return 0


def fixture_writes_are_excluded(out: list[str]) -> int:
    """Check a suite's own fixtures are not reported — INCLUDING NESTED HELPERS.

    ⚑⚑⚑ THE POPULATION THE READER MANUFACTURED. Live, this read 26 of 29 unprotected; every row
    was a temp-file write inside `_selftest`, and after exempting that name one survivor remained
    — a helper DEFINED INSIDE the suite. Excluding by SPAN rather than by name took it to zero.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, _FIXTURES)
    if got != ():
        out.append(f"selftest: fixture write(s) reported: {got!r}")
        return 1
    return 0


def a_write_is_counted_once(out: list[str]) -> int:
    """Check a nested scope does not double-report its write.

    ⚑ `ast.walk` YIELDS AN INNER SCOPE AND REACHES IT AGAIN from the outer one, so a write in a
    closure was reported twice — with two different verdicts about the same line.
    """
    nested = (
        "def add(target: str) -> int:\n"
        '    """Write through a helper."""\n'
        '    if "--apply" not in sys.argv:\n'
        "        return 0\n"
        "    def _write(where: str) -> None:\n"
        '        with open(where, "w", encoding="utf-8") as fh:\n'
        '            fh.write("x")\n'
        "    _write(target)\n"
        "    return 0\n"
    )
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, nested)
    lines = [row.line for row in got]
    if len(lines) != len(set(lines)):
        out.append(f"selftest: a write was counted twice: {lines!r}")
        return 1
    return 0


def an_unparseable_tool_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = _writes(where, "def add(:\n")
    if got != ():
        out.append(f"selftest: an unparseable tool yielded {got!r}")
        return 1
    return 0


def an_absent_tool_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = write_path.writes(Path(where) / "gone.py", "gone.py")
    if got != ():
        out.append(f"selftest: an absent tool yielded {got!r}")
        return 1
    return 0


def a_finding_names_what_is_missing(out: list[str]) -> int:
    """Check an unprotected row says which protection it lacks."""
    row = write_path.Write(tool="a.py", line=1, armed=False, gated=False)
    if len(row.missing) != _BOTH:
        out.append(f"selftest: the missing set reads as {row.missing!r}")
        return 1
    return 0


def an_empty_population_is_unmeasured(out: list[str]) -> int:
    """Check no writes found renders as unmeasured, not as clean."""
    text = write_path.render(())
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty population renders as {text!r}")
        return 1
    return 0


def the_render_states_its_denominator(out: list[str]) -> int:
    """Check the finding says how many writes were examined."""
    rows = (
        write_path.Write(tool="a.py", line=1, armed=True, gated=True),
        write_path.Write(tool="a.py", line=9, armed=False, gated=True),
    )
    if " of " not in write_path.render(rows):
        out.append("selftest: the render states no denominator")
        return 1
    return 0


_ARMS = (
    a_protected_write_is_protected,
    a_bare_guard_call_arms,
    an_unarmed_write_is_reported,
    an_ungated_write_is_reported,
    one_guard_does_not_cover_two_writes,
    a_late_guard_does_not_arm,
    a_read_is_not_a_write,
    fixture_writes_are_excluded,
    a_write_is_counted_once,
    an_unparseable_tool_yields_nothing,
    an_absent_tool_yields_nothing,
    a_finding_names_what_is_missing,
    an_empty_population_is_unmeasured,
    the_render_states_its_denominator,
)

_CASE_COUNT = 1 + 1 + 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"write-path selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"write-path selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
