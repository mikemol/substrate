#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Arms for `substrate.bare_speech` — the census of CLIs that exit 0 in silence.

⚑⚑⚑ THIS SUITE EXISTS BECAUSE THE CENSUS GOT IT WRONG FIRST. Its opening run reported 32 silent
CLIs; running three of the accused showed `file_mode.py`, `module_outline.py` and `attr_reads.py`
each printing a usage line and exiting 2. The reader had stopped at `sys.exit(main(sys.argv[1:]))`
— the idiom nearly every CLI in this package uses — so it reported its own blind spot as a
corpus-wide defect. The delegation arm below is the case that would have caught it.

⚑⚑ THE CLASSES ARE ASSERTED AGAINST FIXTURES, NOT AGAINST LIVE MODULES. A case naming
`store_calls.py` as SPEAKS goes red the day that file is reorganised, and a case naming a live
SILENT module goes red the day someone fixes it — a witness-victim in both directions. The
property is what is pinned: this shape reads SPEAKS, that shape reads SILENT.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import bare_speech

# What `_kind` returns for a file the reader could not parse. ⚑ NAMED so an arm asserts against
# the same spelling the helper produces, rather than a literal repeated at each site.
UNREADABLE = "UNREADABLE"

# How many distinct classes the fixtures below must produce. ⚑ THE DISCRIMINATOR'S THRESHOLD,
# named because it is the arity of the classification being asserted, not a tuning knob.
_DISTINCT_CLASSES = 3

# The exit code a refused invocation returns.
_BAD_ARGV = 2

# A guard that delegates to a `main` which writes — the idiom the first cut misread.
_DELEGATING = (
    "import sys\n"
    "def main(argv: list[str]) -> int:\n"
    '    sys.stderr.write("usage: thing\\n")\n'
    "    return 2\n"
    'if __name__ == "__main__":\n'
    "    sys.exit(main(sys.argv[1:]))\n"
)

# A guard that speaks only under a flag and is mute bare — the measured `store_calls` shape.
_CONDITIONAL = (
    "import sys\n"
    'if __name__ == "__main__":\n'
    '    if "--selftest" in sys.argv:\n'
    "        sys.exit(0)\n"
)

# A guard that writes directly on the bare path.
_DIRECT = 'import sys\nif __name__ == "__main__":\n    sys.stdout.write("here is the reading\\n")\n'

# A guard that refuses with a non-zero exit and no text — speech without words.
_REFUSES = 'import sys\nif __name__ == "__main__":\n    sys.exit(2)\n'

# A module with no guard at all — a library, out of scope for the defect.
_LIBRARY = "def helper() -> int:\n    return 1\n"


def _kind(body: str, name: str = "probe.py") -> str:
    """Return the class `bare_speech` assigns to a fixture written to a fresh file."""
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / name
        path.write_text(body, encoding="utf-8")
        row = bare_speech.read_one(path, name)
    return UNREADABLE if row is None else row.kind


def a_delegating_entry_point_reads_as_speaking(out: list[str]) -> int:
    """Check `sys.exit(main(...))` into a writing `main` reads as speech.

    ⚑⚑⚑ THE FALSE POSITIVE THAT WAS SHIPPED AND CAUGHT BY RUNNING THE ACCUSED. This is the
    dominant entry-point idiom here, and reading it as silence turned a 3-module finding into a
    32-module one. A census that cannot follow one hop reports its own method as the substrate's
    defect.
    """
    got = _kind(_DELEGATING)
    if got != bare_speech.SPEAKS:
        out.append(f"a guard delegating to a writing main read as {got}, not SPEAKS")
        return 1
    return 0


def a_conditional_only_guard_reads_as_silent(out: list[str]) -> int:
    """Check a guard that speaks only under a flag reads as silent on the bare path.

    ⚑⚑ THE MEASURED DEFECT'S OWN SHAPE. `store_calls` spoke under `--selftest` and said nothing
    on the bare path, which is the path an operator actually ran. Counting the flag's speech
    would have reported it as already fixed.
    """
    got = _kind(_CONDITIONAL)
    if got != bare_speech.SILENT:
        out.append(f"a guard speaking only under a flag read as {got}, not SILENT")
        return 1
    return 0


def a_direct_write_reads_as_speaking(out: list[str]) -> int:
    """Check the plain positive — a write on the bare path is speech."""
    got = _kind(_DIRECT)
    if got != bare_speech.SPEAKS:
        out.append(f"a guard writing directly read as {got}, not SPEAKS")
        return 1
    return 0


def a_wordless_refusal_is_still_speech(out: list[str]) -> int:
    """Check a non-zero exit counts as speech even with no text.

    ⚑ A NON-ZERO STATUS IS A SIGNAL A CALLER CAN ACT ON, which is exactly what exit 0 in silence
    denies them. Requiring TEXT would report a tool that refuses correctly as defective.
    """
    got = _kind(_REFUSES)
    if got != bare_speech.SPEAKS:
        out.append(f"a wordless non-zero exit read as {got}, not SPEAKS")
        return 1
    return 0


def a_library_is_not_counted_as_a_silent_cli(out: list[str]) -> int:
    """Check a module with no guard is scoped out rather than counted.

    ⚑⚑ THE SCOPING ARM. A library's silence is a fact about running it as a script; counting the
    guard-less modules here would inflate the census with files never asked to speak — the same
    instrument-answers-where-it-should-scope defect one level up.
    """
    got = _kind(_LIBRARY)
    if got != bare_speech.LIBRARY:
        out.append(f"a module with no __main__ guard read as {got}, not LIBRARY")
        return 1
    return 0


def a_suite_is_classified_by_its_convention(out: list[str]) -> int:
    """Check a `*_selftest.py` is its own class — its bare run IS its verdict."""
    got = _kind(_CONDITIONAL, name=f"probe{bare_speech.SUITE_SUFFIX}")
    if got != bare_speech.SUITE:
        out.append(f"a *_selftest.py read as {got}, not SUITE")
        return 1
    return 0


def the_classes_are_not_all_one_value(out: list[str]) -> int:
    """Check the classifier separates its fixtures — THE DISCRIMINATOR OVER THE WHOLE READING.

    ⚑⚑⚑ A `read_one` RETURNING A CONSTANT satisfies whichever arms happen to expect that
    constant. Separating four distinct fixtures into three or more classes is the property no
    degenerate implementation has.
    """
    seen = {_kind(body) for body in (_DELEGATING, _CONDITIONAL, _DIRECT, _LIBRARY)}
    if len(seen) < _DISTINCT_CLASSES:
        out.append(f"four distinct fixtures produced only {sorted(seen)!r}")
        return 1
    return 0


def an_unparseable_module_is_unmeasured_not_silent(out: list[str]) -> int:
    """Check a file that will not parse is unmeasured rather than classified.

    ⚑ CALLING IT SILENT WOULD BANK A FACT ABOUT THE READER as a fact about the module — the
    class this whole census is about.
    """
    got = _kind("def f(:\n")
    if got != UNREADABLE:
        out.append(f"an unparseable module read as {got}, not None")
        return 1
    return 0


def the_census_reads_the_real_package(out: list[str]) -> int:
    """Check the package census reads something — a positive control against a zero scan."""
    rows = bare_speech.census()
    if not rows:
        out.append("the package census produced no rows")
        return 1
    if not any(r.in_scope for r in rows):
        out.append("the census found no runnable module at all in substrate/")
        return 1
    return 0


def the_render_names_its_denominators_and_its_bound(out: list[str]) -> int:
    """Check the output states its denominator AND its residual false positive.

    ⚑⚑ SPEECH TWO CALLS DEEP STILL READS SILENT, and a reader who does not know that treats a
    row as established rather than confirming it by running the module — which is exactly how the
    first cut's 32 rows would have been believed.
    """
    bad = 0
    text = bare_speech.render(())
    if "runnable" not in text:
        out.append("the render does not state its runnable denominator")
        bad += 1
    if "RUNNING it" not in text:
        out.append("the render does not tell the reader to confirm a row by running it")
        bad += 1
    return bad


def an_operand_is_refused_rather_than_discarded(out: list[str]) -> int:
    """Check a path operand is refused — this census is package-wide and cannot be scoped.

    ⚑ ACCEPTING AND DROPPING IT would return a whole-package answer that reads as scoped, which
    is `module_size`'s measured defect rebuilt in the tool written beside its repair.
    """
    if bare_speech.main(["substrate/store_calls.py"]) != _BAD_ARGV:
        out.append("an operand did not exit 2")
        return 1
    return 0


_ARMS = (
    a_delegating_entry_point_reads_as_speaking,
    a_conditional_only_guard_reads_as_silent,
    a_direct_write_reads_as_speaking,
    a_wordless_refusal_is_still_speech,
    a_library_is_not_counted_as_a_silent_cli,
    a_suite_is_classified_by_its_convention,
    the_classes_are_not_all_one_value,
    an_unparseable_module_is_unmeasured_not_silent,
    the_census_reads_the_real_package,
    the_render_names_its_denominators_and_its_bound,
    an_operand_is_refused_rather_than_discarded,
)

_CASE_COUNT = 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 2 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"bare-speech selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"bare-speech selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
