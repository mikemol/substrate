# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_roundtrip` — two drift measures that must be allowed to disagree.

⚑⚑⚑ THE DISAGREEMENT ARM IS THE SUBJECT. `aligned` and `positional` count the same edit
differently — an inserted line is ONE aligned row and every following positional row — and reusing
one for the other would report a single insertion as hundreds of changes. A suite exercising only
rewrites would pass with the two measures conflated, because on a pure rewrite they agree.

⚑⚑ AND THE IDENTICAL ARM IS THE CONTROL. Pandoc normalizes by design, so a report that never
returns `identical` cannot be told from one whose comparison is broken — the arm asserts the
unusual case is reachable.

⚑ THE FIXTURES ARE TEXTS, so each case states the edit it is about. The origin opened a file and
shelled to pandoc, which is why the measure difference above was never observed: it needed a real
document whose normalization happens to insert a line.
"""

from __future__ import annotations

import sys

from substrate import md_roundtrip as mr

#: Three lines, unchanged — the control.
SAME = "alpha\nbeta\ngamma"

#: ⚑ ONE LINE REWRITTEN IN PLACE. Both measures agree here, which is why this arm alone proves
#: nothing about the distinction.
REWRITTEN = "alpha\nBETA\ngamma"

#: ⚑⚑ ONE LINE INSERTED AT THE TOP. Aligned counts one row; positional counts every line after it.
#: This is the arm that separates the two measures.
INSERTED = "new\nalpha\nbeta\ngamma"

#: A rewritten line costs TWO aligned rows — the removal and the addition — because a unified diff
#: names both sides of a change and that is what a reviewer reads.
ROWS_PER_REWRITE = 2

#: How many lines the sample fixture holds, comfortably past the bound.
WIDE = 50

#: How far past the default bound the sensitivity arm raises the sample.
WIDER = 5


def _identical_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the unusual case that must stay reachable."""
    out: list[tuple[str, bool]] = []
    got = mr.compare(SAME, SAME)

    out.append((f"identical text reports identical: {got.why()}", got.identical))
    out.append(
        (
            f"and both measures are zero: {got.aligned}/{got.positional}",
            got.aligned == 0 and got.positional == 0,
        )
    )
    out.append((f"and the sample is empty: {got.sample}", got.sample == ()))
    out.append((f"and it does not read as an insertion: {got.inserted}", not got.inserted))
    return out


def _rewrite_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for an in-place rewrite, where the measures agree."""
    out: list[tuple[str, bool]] = []
    got = mr.compare(SAME, REWRITTEN)

    out.append((f"a rewrite is not identical: {got.why()}", not got.identical))
    out.append((f"and the positional count is one: {got.positional}", got.positional == 1))
    # ⚑ ON A PURE REWRITE THE TWO AGREE ON THE LINE COUNT — aligned reports the removal AND the
    # addition, so it is two ROWS for one changed line, which is what a reviewer reads.
    out.append((f"and aligned reports both rows: {got.aligned}", got.aligned == ROWS_PER_REWRITE))
    out.append((f"and the sample carries them: {got.sample}", len(got.sample) == got.aligned))
    return out


def _insertion_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the case that separates the two measures.

    ⚑⚑⚑ THIS IS WHY BOTH ARE CARRIED. One inserted line is a single aligned row and shifts every
    following line positionally — so a report giving only the positional number would send a
    reviewer looking for four edits when one was made.
    """
    out: list[tuple[str, bool]] = []
    got = mr.compare(SAME, INSERTED)

    out.append((f"an insertion is one aligned row: {got.aligned}", got.aligned == 1))
    out.append(
        (f"and the positional count runs ahead: {got.positional}", got.positional > got.aligned)
    )
    out.append((f"and the report says lines moved: {got.why()}", got.inserted))
    out.append((f"and names it in the account: {got.why()}", "moved" in got.why()))
    return out


def _sample_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the bounded sample."""
    out: list[tuple[str, bool]] = []
    wide_before = "\n".join(f"line {i}" for i in range(WIDE))
    wide_after = "\n".join(f"LINE {i}" for i in range(WIDE))

    got = mr.compare(wide_before, wide_after)
    out.append((f"the sample is bounded: {len(got.sample)}", len(got.sample) == mr.SAMPLE))
    out.append((f"while the count is not: {got.aligned}", got.aligned > mr.SAMPLE))

    # ⚑ THE SENSITIVITY ARM. Raising ONLY the bound must lengthen the sample, or the parameter is
    # not consulted and the cap is incidental.
    wider = mr.compare(wide_before, wide_after, sample=mr.SAMPLE + WIDER)
    out.append(
        (
            f"raising ONLY the bound lengthens it: {len(wider.sample)}",
            len(wider.sample) == mr.SAMPLE + WIDER,
        )
    )

    # ⚑ AND THE SAMPLE HOLDS CHANGED ROWS, NEVER HEADERS — a diff header would read as a change to
    # a line the document does not have.
    out.append(
        (
            f"no header row reaches the sample: {got.sample[0]}",
            not any(row.startswith(("+++", "---")) for row in got.sample),
        )
    )
    return out


def _summary_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the denominator a summary must carry.

    ⚑ `0 drifted` AND `0 drifted of 40` ARE DIFFERENT CLAIMS. Only the second separates a clean
    corpus from a run that examined nothing.
    """
    out: list[tuple[str, bool]] = []
    clean = [mr.compare(SAME, SAME), mr.compare(SAME, SAME)]
    mixed = [mr.compare(SAME, SAME), mr.compare(SAME, INSERTED)]

    out.append(
        (
            f"a clean run states its denominator: {mr.summarise(clean)}",
            "0 of 2" in mr.summarise(clean),
        )
    )
    out.append(
        (
            f"and a drifting one counts only the movers: {mr.summarise(mixed)}",
            "1 of 2" in mr.summarise(mixed),
        )
    )
    out.append((f"an empty run says so: {mr.summarise([])}", "0 of 0" in mr.summarise([])))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _identical_cases()
        + _rewrite_cases()
        + _insertion_cases()
        + _sample_cases()
        + _summary_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-roundtrip selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
