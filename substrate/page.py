#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Bound a listing DETERMINISTICALLY — `--top` with an offset, and a tail that says what is left.

⚑⚑⚑ TRUNCATION IS CURRENTLY THE HARNESS'S DECISION, WHICH MAKES IT NON-DETERMINISTIC. A tool that
prints 400 rows into a context-bounded reader gets cut at whatever byte the transport chooses, and
the reader cannot tell a short list from a clipped one — the same
`census-green-is-a-fact-about-the-census` shape, one layer out: **the boundary of the TRANSPORT
read as the boundary of the ANSWER.** MEASURED this session: a tool listing reached 400+ lines and
two separate mode dumps ran ~20KB each, all of them truncated by the harness rather than by the
tool.

⚑⚑ `--top` IS THE CONVERGENT SPELLING AND THE CENSUS SAYS SO. `toolmodes --conventions` reports
**`--top` accepted by 9 tools** (`autocorr_synth`, `prose_apex`, `pycodemod`, `toolmodes`,
`buildtime`, `proofcost`, …) against `--limit` on ONE, both sitting in *"accepted by ≥3 tools,
declared by NO convention"*. So the vocabulary already converged; what was missing was a
declaration and a shared implementation. Picking `--limit` here would have been a 10th spelling of
a question nine tools already answer.

⚑⚑ AND THE OFFSET IS THE HALF NOBODY HAS. Every existing `--top` is a BOUND — "show me the worst
N" — which is right for a ranked report and useless for a listing, because rows N+1 onward become
unreachable. A bound plus an offset makes the whole listing addressable in pages, so a reader that
cannot hold 432 rows can still SEE all 432 across four calls rather than guessing what the cut hid.

⚑ THE TAIL LINE IS NOT DECORATION — IT IS THE DIFFERENCE BETWEEN A SHORT LIST AND A CLIPPED ONE.
A page that ends silently is indistinguishable from a complete answer, which is precisely the
absence-reported-as-fact defect. So a bounded page always states the denominator and how to reach
the rest, and an UNBOUNDED page says nothing at all — a reader who asked for everything is not
told twice that they got it.
"""

from __future__ import annotations

from dataclasses import dataclass

# The declared flags. ⚑ NAMED HERE, ONCE: a tool spelling them at its own call site is the second
# spelling that drifts, and this module exists because there were already two.
TOP = "--top"
SKIP = "--skip"

# What `--top 0` means: no bound. ⚑ ZERO IS "ALL", NOT "NOTHING" — `toolmodes --top 0` already
# uses that reading ("`--top 0` prints every row"), so the convention is inherited rather than
# invented, and the opposite reading would make a reasonable-looking argument silently empty.
UNBOUNDED = 0


@dataclass(frozen=True, slots=True)
class Page[Row]:
    """One slice of a listing, and what it took from where."""

    rows: tuple[Row, ...]
    total: int
    skipped: int

    @property
    def shown(self) -> int:
        """Return how many rows this page carries."""
        return len(self.rows)

    @property
    def remaining(self) -> int:
        """Return how many rows sit past the end of this page."""
        return max(0, self.total - self.skipped - self.shown)

    @property
    def bounded(self) -> bool:
        """Report whether anything was withheld, in either direction."""
        return self.skipped > 0 or self.remaining > 0


def take[Row](rows: tuple[Row, ...], top: int = UNBOUNDED, skip: int = 0) -> Page[Row]:
    """Return the page `rows[skip : skip+top]`, carrying the denominator with it.

    ⚑ THE DENOMINATOR TRAVELS WITH THE PAGE. A caller that computed the total separately would
    have two derivations of one number — and the one that goes stale is the one printed in the
    tail, which is exactly the line a reader trusts to know whether they saw everything.

    ⚑ A NEGATIVE OR OVERSIZED `skip` IS CLAMPED RATHER THAN REFUSED. Paging is a reading
    convenience; refusing a walk that has run off the end would turn "you have seen it all" into
    an error.
    """
    total = len(rows)
    start = min(max(0, skip), total)
    end = total if top <= UNBOUNDED else min(total, start + top)
    return Page(rows=rows[start:end], total=total, skipped=start)


def tail[Row](page: Page[Row], flag_top: str = TOP, flag_skip: str = SKIP) -> str:
    """Return the one-line footer naming what was withheld and how to reach it, or "".

    ⚑⚑ AN UNBOUNDED PAGE SAYS NOTHING. A reader who asked for the whole listing does not need to
    be told they received it, and a footer on every call trains them to ignore the channel — which
    is what makes the one that matters invisible.

    ⚑ THE FOOTER NAMES THE NEXT INVOCATION, not merely a count. "showing 50 of 432" leaves the
    reader to work out the flags; naming `--skip 50` makes the next page one copy-paste, which is
    the difference between a bound a reader can walk and one they abandon.
    """
    if not page.bounded:
        return ""
    seen = page.skipped + page.shown
    if page.remaining <= 0:
        return f"  … {seen} of {page.total} (the last page; {flag_skip} 0 to start over)"
    more = (
        f"  … showing {page.skipped + 1}-{seen} of {page.total}; "
        f"{page.remaining} more — {flag_skip} {seen}"
    )
    return more + (f" {flag_top} {page.shown}" if page.shown else "")


def _value(argv: list[str], flag: str, fallback: int) -> int:
    """Return the integer following `flag` in `argv`, or `fallback`."""
    if flag not in argv:
        return fallback
    at = argv.index(flag) + 1
    if at >= len(argv):
        return fallback
    try:
        return int(argv[at])
    except ValueError:
        return fallback


def read_args(argv: list[str], flag_top: str = TOP, flag_skip: str = SKIP) -> tuple[int, int]:
    """Return `(top, skip)` from a command line, defaulting to unbounded from the start.

    ⚑ AN UNPARSEABLE VALUE FALLS BACK RATHER THAN RAISING. `--top banana` is a typo in a reading
    convenience, and a tool that died on it would refuse to answer a question it can answer — the
    bound is not the point of the invocation.

    ⚑ THE DEFAULT IS UNBOUNDED, WHICH KEEPS EVERY EXISTING CALLER'S BEHAVIOUR. Adding pagination
    must not silently start truncating output that something downstream parses; a reader opts IN
    to a page.
    """
    return (_value(argv, flag_top, UNBOUNDED), _value(argv, flag_skip, 0))
