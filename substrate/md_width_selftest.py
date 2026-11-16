# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.md_width` — the bracket refusal, the boundary, and the conjunction.

⚑⚑⚑ THE BRACKET ARM IS THE SUBJECT. A bisection over a predicate that never holds returns
whichever endpoint the loop lands on, and that reads as an answer — so the case that matters most
is the one where NO width satisfies both conditions and the search says so instead of returning a
number.

⚑⚑ AND THESE ARMS WERE UNREACHABLE IN THE ORIGIN. It opened every document, shelled to pandoc,
wrote to a temp directory and read the result back, so exercising the SEARCH required a corpus and
a converter — and a search bug and a pandoc bug produced the same symptom. Here the predicate is a
function whose boundary the case chooses, so the bisection is tested against a known answer.

⚑ THE CONJUNCTION IS TESTED IN BOTH HALVES SEPARATELY, because a search that ignored one half
would pass every arm driven by a predicate that fails both at once.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from substrate import md_width as mw

if TYPE_CHECKING:
    from collections.abc import Callable

#: The boundary a synthetic predicate is built around — arbitrary, and the point is that the
#: search must FIND it rather than be told it.
BOUNDARY = 137


def _at_least(boundary: int) -> Callable[[int], mw.Try]:
    """Return a predicate holding exactly at and above `boundary`, in both halves."""

    def holds(width: int) -> mw.Try:
        ok = width >= boundary
        return mw.Try(width, converges=ok, all_pipe=ok)

    return holds


def _never() -> Callable[[int], mw.Try]:
    """Return a predicate that never holds — the invalid-bracket case."""

    def holds(width: int) -> mw.Try:
        return mw.Try(width, converges=False, all_pipe=False)

    return holds


def _always() -> Callable[[int], mw.Try]:
    """Return a predicate holding everywhere — the lower bracket already satisfies it."""

    def holds(width: int) -> mw.Try:
        return mw.Try(width, converges=True, all_pipe=True)

    return holds


def _only_pipe(boundary: int) -> Callable[[int], mw.Try]:
    """Return a predicate where only the all-pipe half moves — convergence always holds."""

    def holds(width: int) -> mw.Try:
        return mw.Try(width, converges=True, all_pipe=width >= boundary)

    return holds


def _only_converge(boundary: int) -> Callable[[int], mw.Try]:
    """Return a predicate where only the convergence half moves — tables always stay pipe."""

    def holds(width: int) -> mw.Try:
        return mw.Try(width, converges=width >= boundary, all_pipe=True)

    return holds


def _boundary_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the search finds the boundary it was not told."""
    out: list[tuple[str, bool]] = []
    got = mw.narrowest(_at_least(BOUNDARY))

    out.append((f"the boundary is found: {got.why}", got.width == BOUNDARY))
    out.append(
        (
            f"and the width below it fails: {got.tried[-1].why()}",
            any(t.width == BOUNDARY - 1 and not t.holds for t in got.tried),
        )
    )
    # ⚑ A BISECTION MUST NOT BE A SCAN. Over this bracket a linear walk would try hundreds of
    # widths, so the trial count is what distinguishes the two.
    out.append(
        (
            f"and it bisected rather than scanned: {len(got.tried)} trial(s)",
            len(got.tried) < mw.HI - mw.LO,
        )
    )
    return out


def _bracket_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the two bracket outcomes that are not a search.

    ⚑⚑ THE REFUSAL IS THE LOAD-BEARING ONE. Without it a never-holding predicate yields a number,
    and a number is what a reader acts on.
    """
    out: list[tuple[str, bool]] = []

    none = mw.narrowest(_never())
    out.append((f"an invalid upper bracket REFUSES: {none.why}", none.width is None))
    out.append((f"and says the bracket is what failed: {none.why}", "upper bracket" in none.why))
    # ⚑ AND IT STOPS THERE — probing on after the supremum fails would be searching a range already
    # known to hold nothing.
    out.append((f"and it stops after one probe: {len(none.tried)}", len(none.tried) == 1))

    low = mw.narrowest(_always())
    out.append((f"a satisfied lower bracket returns it: {low.why}", low.width == mw.LO))
    return out


def _conjunction_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving BOTH halves gate the answer.

    ⚑⚑⚑ EVERY ARM ABOVE MOVES BOTH HALVES TOGETHER, so none of them shows the search consults
    each. These move one at a time: if either were ignored, one of these would find a narrower
    boundary than it should.
    """
    out: list[tuple[str, bool]] = []

    pipe = mw.narrowest(_only_pipe(BOUNDARY))
    out.append((f"the all-pipe half alone gates it: {pipe.width}", pipe.width == BOUNDARY))

    conv = mw.narrowest(_only_converge(BOUNDARY))
    out.append((f"the convergence half alone gates it: {conv.width}", conv.width == BOUNDARY))
    return out


def _account_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what a trial reports about itself."""
    out: list[tuple[str, bool]] = []

    good = mw.Try(120, converges=True, all_pipe=True)
    out.append((f"a holding trial says so: {good.why()}", good.holds and "all-pipe" in good.why()))

    off_pipe = mw.Try(120, converges=True, all_pipe=False)
    out.append(
        (
            f"a pipe failure names the pipe half: {off_pipe.why()}",
            not off_pipe.holds and "pipe" in off_pipe.why(),
        )
    )

    unstable = mw.Try(120, converges=False, all_pipe=True)
    out.append(
        (
            f"a convergence failure names that half: {unstable.why()}",
            not unstable.holds and "converge" in unstable.why(),
        )
    )

    both = mw.Try(120, converges=False, all_pipe=False)
    out.append((f"and a double failure names both: {both.why()}", " and " in both.why()))
    return out


def _options_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the writer options a width is measured under.

    ⚑ THE ANSWER IS ONLY MEANINGFUL FOR THE WRITER IT WAS MEASURED AGAINST, so the options string
    carries the width rather than the caller assembling it — the origin's own recorded defect was
    passing a whole options string as one pandoc argument, which made it read as an extension name.
    """
    out: list[tuple[str, bool]] = []
    opts = mw.options(120)

    out.append((f"the width reaches the writer: {opts}", "--columns=120" in opts))
    out.append((f"and the base survives: {opts}", opts.startswith(mw.BASE)))
    out.append(
        (f"and it is a flag sequence, not one token: {len(opts.split())}", len(opts.split()) > 1)
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _boundary_cases()
        + _bracket_cases()
        + _conjunction_cases()
        + _account_cases()
        + _options_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"md-width selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
