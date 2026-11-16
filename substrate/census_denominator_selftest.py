#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.census_denominator` — a count with no population is blind.

⚑⚑⚑ THE FALSIFIED-ZERO CASE IS WHY THIS EXISTS. The origin's regex matched any message containing
`"of"` and returned ZERO on a day a live sweep was watched printing a count. A predicate reporting
its subject absent, on the day the subject was demonstrated, is an inert guard — and closing the
item against that number would have banked a false zero into a paydown-only baseline. So the arms
below drive both shapes and assert the reader separates them.

⚑⚑ UNDECIDABLE IS ITS OWN ANSWER. A message built from a variable or joined across statements
cannot be read structurally, and guessing either way is exactly what produced the false zero.
Those are not reported as compliant and not reported as bare — they are not reported.

⚑ THE FIXTURES ARE SOURCE STRINGS. A case reading a live tool measures today's messages: the two
tools this was validated against report 2 of 4 and 2 of 3 bare right now, and a case pinning that
would go red the moment someone adds a denominator — reporting a repair as a defect.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import census_denominator

# ⚑ A CENSUS: the count states what it is out of.
_CENSUS = '''"""A tool that reports a census."""


def main() -> int:
    """Report the population and the finding."""
    print(f"{n} of {m} editor(s) armed")
    return 0
'''

# ⚑ A SWEEP: a count with no denominator — the defect.
_SWEEP = '''"""A tool that reports a sweep."""


def main() -> int:
    """Report the finding alone."""
    print(f"{n} unused imports dropped")
    return 0
'''

# The `across` spelling of a denominator, which the origin's own falsifying example used.
_ACROSS = '''"""A tool reporting across a population."""


def main() -> int:
    """Report the finding and its scope."""
    print(f"{n} dead renaming clause(s) across {m} file(s)")
    return 0
'''

# Prose with no count at all — owes no denominator.
_PROSE = '''"""A tool that reports a header."""


def main() -> int:
    """Print a heading."""
    print("scanning the tree")
    return 0
'''

# A message assembled from a variable — not decidable here.
_INDIRECT = '''"""A tool whose message is built elsewhere."""


def main() -> int:
    """Print a prepared message."""
    print(summary)
    return 0
'''

# A stream write rather than a print.
_STREAM = '''"""A tool writing to a stream."""


def main() -> int:
    """Report the finding alone."""
    sys.stdout.write(f"{n} rows dropped\\n")
    return 0
'''


def _reports(where: str, text: str) -> tuple[census_denominator.Report, ...]:
    """Write a fixture tool and read its reports back."""
    path = Path(where) / "tool.py"
    path.write_text(text, encoding="utf-8")
    return census_denominator.reports(path, "tool.py")


def a_census_states_its_population(out: list[str]) -> int:
    """Check `n of m` is not reported as bare."""
    with tempfile.TemporaryDirectory() as where:
        got = _reports(where, _CENSUS)
    if not got or got[0].bare:
        out.append(f"selftest: a census read as {got!r}")
        return 1
    return 0


def a_sweep_is_reported_bare(out: list[str]) -> int:
    """Check a bare count is the finding — THE WHOLE ITEM.

    ⚑⚑⚑ BLINDNESS READS AS SUCCESS. Nothing separates *"found nothing"* from *"looked at
    nothing"* without a denominator, which is why the bare row is the one worth surfacing.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reports(where, _SWEEP)
    if not got or not got[0].bare:
        out.append(f"selftest: a sweep read as {got!r}")
        return 1
    return 0


def the_across_spelling_counts_as_a_denominator(out: list[str]) -> int:
    """Check `n across m` is a census — the ROW THAT FALSIFIED THE ORIGIN.

    ⚑⚑ THIS IS THE EXACT MESSAGE the origin's regex mishandled while its author watched it print.
    A denominator has more than one spelling, and a reader knowing only `"of"` reports a compliant
    tool as debt or, worse, reports the population as clean.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reports(where, _ACROSS)
    if not got or got[0].bare:
        out.append(f"selftest: the across spelling read as bare: {got!r}")
        return 1
    return 0


def prose_owes_no_denominator(out: list[str]) -> int:
    """Check a message with no count is not a finding.

    ⚑ A HEADER IS NOT A SWEEP. Flagging every non-counting message would bury the rows that
    matter under the ones that never claimed a number.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reports(where, _PROSE)
    if not got or got[0].bare:
        out.append(f"selftest: prose read as bare: {got!r}")
        return 1
    if got[0].counts:
        out.append(f"selftest: prose read as counting: {got!r}")
        return 1
    return 0


def an_indirect_message_is_undecidable(out: list[str]) -> int:
    """Check a message built elsewhere is not reported either way.

    ⚑⚑ GUESSING IS WHAT PRODUCED THE FALSE ZERO. A variable this reader cannot follow is neither
    compliant nor bare, and counting it as either makes the verdict a fact about the reader.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reports(where, _INDIRECT)
    if got != ():
        out.append(f"selftest: an indirect message was decided: {got!r}")
        return 1
    return 0


def a_stream_write_is_read(out: list[str]) -> int:
    """Check `sys.stdout.write` counts as reporting.

    ⚑ TWO SPELLINGS OF ONE ACT. A reader seeing only `print` reports a false zero for every tool
    that writes to a stream — and this package's own modules all do.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _reports(where, _STREAM)
    if not got or not got[0].bare:
        out.append(f"selftest: a stream write read as {got!r}")
        return 1
    return 0


def the_finding_carries_its_line(out: list[str]) -> int:
    """Check a bare report says where it is."""
    with tempfile.TemporaryDirectory() as where:
        got = _reports(where, _SWEEP)
    if not got or got[0].line < 1:
        out.append(f"selftest: the report line read as {got!r}")
        return 1
    return 0


def an_unparseable_file_yields_nothing(out: list[str]) -> int:
    """Check a syntax error is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = _reports(where, "def main(:\n")
    if got != ():
        out.append(f"selftest: an unparseable file yielded {got!r}")
        return 1
    return 0


def an_absent_file_yields_nothing(out: list[str]) -> int:
    """Check a missing file is skipped rather than raising."""
    with tempfile.TemporaryDirectory() as where:
        got = census_denominator.reports(Path(where) / "gone.py", "gone.py")
    if got != ():
        out.append(f"selftest: an absent file yielded {got!r}")
        return 1
    return 0


def bare_selects_only_the_unbounded_counts(out: list[str]) -> int:
    """Check the finding set excludes both censuses and non-counting prose."""
    rows = (
        census_denominator.Report(path="a.py", line=1, message="{} of {} armed"),
        census_denominator.Report(path="b.py", line=2, message="{} dropped"),
        census_denominator.Report(path="c.py", line=3, message="scanning"),
    )
    got = census_denominator.bare(rows)
    if len(got) != 1 or got[0].path != "b.py":
        out.append(f"selftest: bare selected {got!r}")
        return 1
    return 0


def an_empty_population_is_unmeasured(out: list[str]) -> int:
    """Check no decidable report renders as unmeasured, not as clean.

    ⚑ THE READER MUST HOLD ITSELF TO THE PROPERTY IT MEASURES. Reporting a file with no readable
    message as compliant would be a sweep inside the sweep detector.
    """
    text = census_denominator.render((), "tool.py")
    if "UNMEASURED" not in text:
        out.append(f"selftest: an empty population renders as {text!r}")
        return 1
    return 0


def the_render_states_its_own_denominator(out: list[str]) -> int:
    """Check this census reports `n of m` about itself.

    ⚑⚑ A SWEEP DETECTOR THAT SWEEPS would be the defect it exists to find, in the file that
    defines it — so its own output carries the population it examined.
    """
    rows = (
        census_denominator.Report(path="a.py", line=1, message="{} of {} armed"),
        census_denominator.Report(path="b.py", line=2, message="{} dropped"),
    )
    text = census_denominator.render(rows, "tool.py")
    if " of " not in text:
        out.append(f"selftest: the render states no denominator: {text!r}")
        return 1
    return 0


def a_clean_file_reports_its_population_too(out: list[str]) -> int:
    """Check the compliant reading also carries the denominator."""
    rows = (census_denominator.Report(path="a.py", line=1, message="{} of {} armed"),)
    text = census_denominator.render(rows, "tool.py")
    if " of " not in text:
        out.append(f"selftest: the clean render states no denominator: {text!r}")
        return 1
    return 0


_ARMS = (
    a_census_states_its_population,
    a_sweep_is_reported_bare,
    the_across_spelling_counts_as_a_denominator,
    prose_owes_no_denominator,
    an_indirect_message_is_undecidable,
    a_stream_write_is_read,
    the_finding_carries_its_line,
    an_unparseable_file_yields_nothing,
    an_absent_file_yields_nothing,
    bare_selects_only_the_unbounded_counts,
    an_empty_population_is_unmeasured,
    the_render_states_its_own_denominator,
    a_clean_file_reports_its_population_too,
)

_CASE_COUNT = 1 + 1 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"census-denominator selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"census-denominator selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
