#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.deadline_floor` — the improvement that read as a repair.

⚑⚑⚑ THE NAMED-DEFAULT CASE IS THE ITEM. The origin matched `default=` only when it held an
`_ast.Constant`, so the day the producer moved its default to `_probe.DEFAULT_DEADLINE` the walk
stopped seeing the declaration at all and the item went green. **A checker that goes quiet when
its subject improves cannot tell improvement from disappearance** — and green was the reading it
gave to a file it could no longer parse a value out of.

⚑⚑ THE FIXTURES ARE SOURCE STRINGS, NOT THE LIVE PRODUCER. A case pinning today's declaration
measures the producer rather than the reader, and would go red the moment someone adds a second
deadline — correct work reported as a defect.

⚑ AND THE EMPTY CASE MUST NOT READ AS CLEAN. Zero declarations is UNMEASURED: the same shape the
origin failed at, reached from the other side, so it is asserted rather than assumed.

⚑ ONE ARM WAS CUT RATHER THAN WRITTEN: an assertion that the producer roster is non-empty is
UNREACHABLE, because `PRODUCERS` is a literal tuple and the type system already proves it. mypy
said so. A case that cannot fail is a case that measures nothing.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import deadline_floor

# The seconds the fixture types at its call site — named so the assertion reads against a
# declaration rather than a magic number, which is the very property the module is about.
_FIXTURE_SECONDS = 30.0

# The shape the producer has today: the default names a shared authority.
_RESOLVED = '''def main() -> int:
    """Declare the verify deadline from the shared authority."""
    ap.add_argument("--deadline", type=float, default=_probe.DEFAULT_DEADLINE,
                    help="seconds to poll for OUR value to read back")
    return 0
'''

# The shape it used to have: a number typed at the call site.
_LITERAL = '''def main() -> int:
    """Declare the verify deadline as a literal."""
    ap.add_argument("--deadline", type=float, default=30.0,
                    help="seconds to poll")
    return 0
'''

# A bare name rather than a dotted one.
_BARE_NAME = '''def main() -> int:
    """Declare the verify deadline from a module-local name."""
    ap.add_argument("--deadline", type=float, default=DEADLINE)
    return 0
'''

# A different flag entirely — must not be counted.
_OTHER_FLAG = '''def main() -> int:
    """Declare an unrelated option."""
    ap.add_argument("--last-k", type=int, default=5)
    return 0
'''


def _read(where: str, text: str) -> tuple[deadline_floor.Deadline, ...]:
    """Write a fixture producer and read its declarations back."""
    path = Path(where) / "producer.py"
    path.write_text(text, encoding="utf-8")
    return deadline_floor.declarations(path, "producer.py")


def a_named_default_is_read_as_resolved(out: list[str]) -> int:
    """Check a dotted authority is seen and reported as resolved.

    ⚑⚑⚑ THE DECLARATION THE ORIGIN COULD NOT SEE AT ALL. It is the shape the producer has today,
    and the reason the item reported clean while measuring nothing.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _RESOLVED)
    if len(got) != 1 or not got[0].resolved:
        out.append(f"selftest: a named default read as {got!r}")
        return 1
    if got[0].authority != "_probe.DEFAULT_DEADLINE":
        out.append(f"selftest: the authority read as {got[0].authority!r}")
        return 1
    return 0


def a_literal_default_is_read_as_unresolved(out: list[str]) -> int:
    """Check a call-site number is reported as the finding — the POSITIVE CONTROL.

    ⚑⚑ WITHOUT THIS, A READER CALLING EVERYTHING RESOLVED would pass the case above and report a
    corpus with no findings forever. The pair says the two spellings are told apart.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _LITERAL)
    if len(got) != 1 or got[0].resolved:
        out.append(f"selftest: a literal default read as {got!r}")
        return 1
    if got[0].literal != _FIXTURE_SECONDS:
        out.append(f"selftest: the literal read as {got[0].literal!r}")
        return 1
    return 0


def a_bare_name_default_is_resolved(out: list[str]) -> int:
    """Check a module-local name counts as an authority.

    ⚑ A NAME IS A NAME WHETHER OR NOT IT IS DOTTED. Reading only `Attribute` would call a
    module-local constant a literal, which is the opposite verdict about a correct declaration.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _BARE_NAME)
    if len(got) != 1 or not got[0].resolved or got[0].authority != "DEADLINE":
        out.append(f"selftest: a bare-name default read as {got!r}")
        return 1
    return 0


def a_literal_carries_no_authority(out: list[str]) -> int:
    """Check the two fields are exclusive on a literal row."""
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _LITERAL)
    if not got or got[0].authority is not None:
        out.append(f"selftest: a literal row carries an authority: {got!r}")
        return 1
    return 0


def a_resolved_row_carries_no_literal(out: list[str]) -> int:
    """Check a resolved row reports no seconds.

    ⚑ A NUMBER ON A RESOLVED ROW WOULD BE INVENTED. The value lives behind the name, in a file
    this reader is not reading, and printing one would state a figure with no source.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _RESOLVED)
    if not got or got[0].literal is not None:
        out.append(f"selftest: a resolved row carries a literal: {got!r}")
        return 1
    return 0


def another_flag_is_not_counted(out: list[str]) -> int:
    """Check an unrelated argparse default is skipped."""
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, _OTHER_FLAG)
    if got != ():
        out.append(f"selftest: an unrelated flag was counted: {got!r}")
        return 1
    return 0


def an_unparseable_producer_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = _read(where, "def main(:\n")
    if got != ():
        out.append(f"selftest: an unparseable producer yielded {got!r}")
        return 1
    return 0


def an_absent_producer_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = deadline_floor.declarations(Path(where) / "gone.py", "gone.py")
    if got != ():
        out.append(f"selftest: an absent producer yielded {got!r}")
        return 1
    return 0


def unresolved_selects_only_the_literals(out: list[str]) -> int:
    """Check the finding set holds exactly the call-site numbers."""
    rows = (
        deadline_floor.Deadline(path="a.py", line=1, authority="M.D", literal=None),
        deadline_floor.Deadline(path="b.py", line=2, authority=None, literal=_FIXTURE_SECONDS),
    )
    got = deadline_floor.unresolved(rows)
    if len(got) != 1 or got[0].path != "b.py":
        out.append(f"selftest: unresolved selected {got!r}")
        return 1
    return 0


def an_empty_census_says_unmeasured(out: list[str]) -> int:
    """Check no declarations renders as unmeasured, not as clean.

    ⚑⚑ THE ORIGIN'S FAILURE FROM THE OTHER SIDE. Its walk found nothing and reported the item
    satisfied; an empty population here has to say the measurement did not happen.
    """
    text = deadline_floor.render(())
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty census does not say unmeasured: {text!r}")
        return 1
    return 0


def the_render_marks_only_the_unresolved_rows(out: list[str]) -> int:
    """Check a resolved row and a literal row are visibly different."""
    rows = (
        deadline_floor.Deadline(path="a.py", line=1, authority="M.D", literal=None),
        deadline_floor.Deadline(path="b.py", line=2, authority=None, literal=_FIXTURE_SECONDS),
    )
    text = deadline_floor.render(rows)
    if "resolved" not in text or "⚑" not in text:
        out.append(f"selftest: the render does not distinguish the rows:\n{text}")
        return 1
    return 0


def the_population_stays_inside_its_roster(out: list[str]) -> int:
    """Check every row comes from a declared producer.

    ⚑ A PATH REACHED OUTSIDE THE ROSTER is how a census starts reporting on a file its own
    constant does not name — the reader measures one thing and labels it another.
    """
    unknown = [
        row.path for row in deadline_floor.population() if row.path not in deadline_floor.PRODUCERS
    ]
    if unknown:
        out.append(f"selftest: rows from files outside the roster: {unknown!r}")
        return 1
    return 0


_ARMS = (
    a_named_default_is_read_as_resolved,
    a_literal_default_is_read_as_unresolved,
    a_bare_name_default_is_resolved,
    a_literal_carries_no_authority,
    a_resolved_row_carries_no_literal,
    another_flag_is_not_counted,
    an_unparseable_producer_yields_nothing,
    an_absent_producer_yields_nothing,
    unresolved_selects_only_the_literals,
    an_empty_census_says_unmeasured,
    the_render_marks_only_the_unresolved_rows,
    the_population_stays_inside_its_roster,
)

_CASE_COUNT = 2 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"deadline-floor selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"deadline-floor selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
