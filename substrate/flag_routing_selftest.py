#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.flag_routing` — naming the authority is not calling it.

⚑⚑⚑ THE MENTIONS-ONLY CASE IS THE ITEM. The origin asked `"check_argv" not in _read(path)`, so a
docstring explaining why a gate does NOT route its flags satisfied the predicate, and so did an
import that merely re-exports the name. `scripts/ratchet.py` is exactly that shape. The two
readings agree on every other row, which is why only a constructed fixture separates them.

⚑⚑ AND THE CALL'S OWN NAME NODE MUST NOT COUNT AS A MENTION. A call site contains a `Name` node
spelling the authority; counting it would mark every routing gate as also mentioning it, and the
mentions-only row — the one that matters — would never fire.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading the live gates measures today's tree: 6 of 23
do not route right now, and a case pinning that goes red the moment a gate is added or repaired,
reporting correct work as a defect.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import flag_routing

# A gate that calls the authority the ordinary way.
_CALLS = '''"""A gate that routes its flags."""
from substrate.ratchet_flags import check_argv


def main() -> int:
    """Refuse an unknown flag."""
    check_argv(sys.argv)
    return 0
'''

# A gate calling it through a module attribute.
_ATTRIBUTE = '''"""A gate routing through the module."""
import ratchet_flags


def main() -> int:
    """Refuse an unknown flag."""
    ratchet_flags.check_argv(sys.argv)
    return 0
'''

# ⚑ THE DEFECT: the name is bound and forwarded, never called.
_REEXPORT = '''"""A module that re-exports the authority."""
from substrate.ratchet_flags import check_argv, mutating_argv

__all__ = ["check_argv", "mutating_argv"]
'''

# ⚑ THE OTHER DEFECT: prose naming the authority while explaining its absence.
_PROSE = '''"""A gate that deliberately does not use check_argv.

⚑ See the note on check_argv: this gate takes no flags.
"""


def main() -> int:
    """Do the work."""
    return 0
'''

# A gate with no relationship to the authority at all.
_SILENT = '''"""A gate with no flags."""


def main() -> int:
    """Do the work."""
    return 0
'''


def _routing(where: str, text: str) -> flag_routing.Routing | None:
    """Write a fixture gate and read its routing back."""
    path = Path(where) / "check_fixture.py"
    path.write_text(text, encoding="utf-8")
    return flag_routing.routing(path, "check_fixture.py")


def a_bare_call_routes(out: list[str]) -> int:
    """Check a plain call is read as routing."""
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, _CALLS)
    if got is None or not got.routes:
        out.append(f"selftest: a bare call read as {got!r}")
        return 1
    return 0


def an_attribute_call_routes(out: list[str]) -> int:
    """Check a call through a module attribute is read as routing.

    ⚑ TWO SPELLINGS, ONE CALL. A name-only reader reports a false zero for the other — the
    census-keyed-on-one-spelling defect.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, _ATTRIBUTE)
    if got is None or not got.routes:
        out.append(f"selftest: an attribute call read as {got!r}")
        return 1
    return 0


def a_reexport_does_not_route(out: list[str]) -> int:
    """Check an import that forwards the name is NOT routing — THE WHOLE ITEM.

    ⚑⚑⚑ THE FALSE COMPLIANT. `scripts/ratchet.py` holds the authority on an import line and never
    calls it; a substring test reads that as adoption, which is a fact about the text reported as
    a fact about the behaviour.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, _REEXPORT)
    if got is None or got.routes:
        out.append(f"selftest: a re-export read as routing: {got!r}")
        return 1
    if not got.mentions_only:
        out.append(f"selftest: a re-export was not marked mentions-only: {got!r}")
        return 1
    return 0


def prose_does_not_route(out: list[str]) -> int:
    """Check a docstring naming the authority is not counted.

    ⚑⚑ THE FILE THAT MOST CLEARLY STATES THE PROBLEM would read as the file that solved it — the
    same shape the closure-delegation reader was rewritten to remove.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, _PROSE)
    if got is None or got.routes:
        out.append(f"selftest: prose read as routing: {got!r}")
        return 1
    return 0


def a_routing_gate_is_not_marked_mentions_only(out: list[str]) -> int:
    """Check a call site's own name node is not counted as a mention.

    ⚑⚑ WITHOUT THIS, EVERY ROUTING GATE reads as also mentioning the authority, and the
    mentions-only row stops discriminating — the flag that matters, silently always on.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, _CALLS)
    if got is None or got.mentions_only:
        out.append(f"selftest: a routing gate was marked mentions-only: {got!r}")
        return 1
    return 0


def a_silent_gate_mentions_nothing(out: list[str]) -> int:
    """Check a gate with no relationship to the authority reports neither."""
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, _SILENT)
    if got is None or got.routes or got.mentions:
        out.append(f"selftest: a silent gate read as {got!r}")
        return 1
    return 0


def a_silent_gate_is_not_mentions_only(out: list[str]) -> int:
    """Check the mentions-only flag needs an actual mention.

    ⚑ THE TWO UNROUTED KINDS ARE DIFFERENT FINDINGS. A gate that never heard of the authority
    needs adding to; one that names it without calling it may already believe it complies.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, _SILENT)
    if got is not None and got.mentions_only:
        out.append("selftest: a silent gate was marked mentions-only")
        return 1
    return 0


def the_call_line_is_reported(out: list[str]) -> int:
    """Check a routing gate carries where it routes."""
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, _CALLS)
    if got is None or not got.calls or got.calls[0] < 1:
        out.append(f"selftest: the call line read as {got!r}")
        return 1
    return 0


def an_unparseable_gate_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising.

    ⚑ ONE BAD FILE MUST NOT TAKE THE CENSUS DOWN.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _routing(where, "def main(:\n")
    if got is not None:
        out.append(f"selftest: an unparseable gate yielded {got!r}")
        return 1
    return 0


def an_absent_gate_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = flag_routing.routing(Path(where) / "gone.py", "gone.py")
    if got is not None:
        out.append(f"selftest: an absent gate yielded {got!r}")
        return 1
    return 0


def unrouted_selects_only_the_non_callers(out: list[str]) -> int:
    """Check the finding set holds exactly the gates that do not call."""
    rows = (
        flag_routing.Routing(gate="a.py", calls=(7,), mentions=()),
        flag_routing.Routing(gate="b.py", calls=(), mentions=(3,)),
    )
    got = flag_routing.unrouted(rows)
    if len(got) != 1 or got[0].gate != "b.py":
        out.append(f"selftest: unrouted selected {got!r}")
        return 1
    return 0


def an_empty_population_is_unmeasured(out: list[str]) -> int:
    """Check no gates read renders as unmeasured, not as clean.

    ⚑ ZERO GATES IS A FACT ABOUT THE GLOB, and reading it as a clean census banks a false green
    over a population nobody enumerated.
    """
    text = flag_routing.render(())
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty population renders as {text!r}")
        return 1
    return 0


def every_unrouted_row_is_marked(out: list[str]) -> int:
    """Check each finding row carries the marker — ⟡marker-convention.

    ⚑⚑⚑ THE UNMARKED HALF UNDER-REPORTED, MEASURED. The mentions-only rows carried the flag and
    the plain ones did not, so a consumer reading marked lines as the population saw ZERO findings
    over a census holding six — while `universal_flags`, built from the same gates, marked every
    row and reported all six. **The under-report is the direction that reads as clean.**

    ⚑ THE MARKER SAYS *THIS ROW IS A FINDING*; the prose after it says which kind. Expressing the
    distinction by withholding the marker overloads it onto two jobs, and the consumer only reads
    one of them.
    """
    rows = (
        flag_routing.Routing(gate="plain.py", calls=(), mentions=()),
        flag_routing.Routing(gate="named.py", calls=(), mentions=(4,)),
    )
    marked = [
        line for line in flag_routing.render(rows).splitlines() if line.strip().startswith("⚑")
    ]
    if len(marked) != len(rows):
        out.append(f"selftest: {len(rows)} unrouted row(s) produced {len(marked)} marked line(s)")
        return 1
    return 0


def the_render_marks_the_false_compliant(out: list[str]) -> int:
    """Check a mentions-only row is visibly different from a silent one.

    ⚑ THE READER MUST SEE WHICH ROWS A TEXT SEARCH WOULD HAVE MISSED, because those are the ones
    a previous census reported as fine.
    """
    rows = (
        flag_routing.Routing(gate="a.py", calls=(), mentions=(4,)),
        flag_routing.Routing(gate="b.py", calls=(), mentions=()),
    )
    text = flag_routing.render(rows)
    if "⚑" not in text or "without calling" not in text:
        out.append(f"selftest: the render does not mark the false compliant:\n{text}")
        return 1
    return 0


def a_fully_routed_population_reports_clean(out: list[str]) -> int:
    """Check every gate routing renders as the closed reading."""
    rows = (flag_routing.Routing(gate="a.py", calls=(7,), mentions=()),)
    text = flag_routing.render(rows)
    if "every one of" not in text:
        out.append(f"selftest: a clean population renders as {text!r}")
        return 1
    return 0


_ARMS = (
    a_bare_call_routes,
    an_attribute_call_routes,
    a_reexport_does_not_route,
    prose_does_not_route,
    a_routing_gate_is_not_marked_mentions_only,
    a_silent_gate_mentions_nothing,
    a_silent_gate_is_not_mentions_only,
    the_call_line_is_reported,
    an_unparseable_gate_yields_nothing,
    an_absent_gate_yields_nothing,
    unrouted_selects_only_the_non_callers,
    an_empty_population_is_unmeasured,
    every_unrouted_row_is_marked,
    the_render_marks_the_false_compliant,
    a_fully_routed_population_reports_clean,
)

_CASE_COUNT = 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"flag-routing selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"flag-routing selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
