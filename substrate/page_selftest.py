#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.page` — a silent page is indistinguishable from a complete one.

⚑⚑⚑ THE FOOTER ARMS ARE THE ITEM, NOT THE SLICING. Slicing a tuple is not where this goes wrong;
reporting is. A page that ends without saying what it withheld reads exactly like a short list,
which is the absence-reported-as-fact defect wearing a listing's clothes — and it is worse than
harness truncation, because the tool APPEARS to have answered.

⚑⚑ AND THE UNBOUNDED CASE MUST STAY SILENT. A footer on every call trains a reader to skip the
channel, which is what makes the one that matters invisible. So "you got everything" is said by
saying nothing, and only a withholding page speaks.

⚑ `--top 0` IS ALL, NOT NOTHING, and that reading is inherited rather than invented: `toolmodes
--top 0` already means "print every row". The opposite reading would make a reasonable-looking
argument silently empty, which is the failure mode a bound is supposed to prevent.
"""

from __future__ import annotations

import sys

from substrate import page

# A listing big enough to page, with distinguishable rows.
_ROWS = tuple(f"row{n}" for n in range(10))

# The size of that listing, named so the assertions and the fixture cannot drift.
_TOTAL = 10

# A page size that divides it unevenly, so an off-by-one shows.
_SIZE = 3


def an_unbounded_page_takes_everything(out: list[str]) -> int:
    """Check the default returns the whole listing."""
    got = page.take(_ROWS)
    if got.shown != _TOTAL or got.remaining != 0:
        out.append(f"selftest: an unbounded page took {got.shown} of {got.total}")
        return 1
    return 0


def an_unbounded_page_says_nothing(out: list[str]) -> int:
    """Check a complete answer carries no footer — THE SILENCE ARM.

    ⚑ A READER WHO ASKED FOR EVERYTHING IS NOT TOLD TWICE. A footer here would be noise on the
    common path, and noise on the common path is how the important line stops being read.
    """
    if page.tail(page.take(_ROWS)):
        out.append("selftest: an unbounded page emitted a footer")
        return 1
    return 0


def a_bounded_page_names_what_is_left(out: list[str]) -> int:
    """Check a withholding page states the denominator and the next call — THE ITEM.

    ⚑⚑⚑ THIS IS THE DIFFERENCE BETWEEN A SHORT LIST AND A CLIPPED ONE. Without it the reader
    cannot tell whether the tool answered or the transport cut it, and the two look identical.
    """
    got = page.tail(page.take(_ROWS, _SIZE))
    if not got:
        out.append("selftest: a bounded page emitted no footer")
        return 1
    if str(_TOTAL) not in got:
        out.append(f"selftest: the footer omits the denominator: {got!r}")
        return 1
    if page.SKIP not in got:
        out.append(f"selftest: the footer does not name the next invocation: {got!r}")
        return 1
    return 0


def the_offset_reaches_later_rows(out: list[str]) -> int:
    """Check `skip` addresses rows a bound alone cannot reach.

    ⚑⚑ THE OFFSET IS THE HALF THE NINE EXISTING `--top` TOOLS DO NOT HAVE. A bound alone makes
    rows N+1 onward unreachable — fine for a ranked report, useless for a listing, and the reason
    a 432-row census could only ever be read as its first page.
    """
    got = page.take(_ROWS, _SIZE, _SIZE)
    if got.rows != _ROWS[_SIZE : _SIZE * 2]:
        out.append(f"selftest: the second page read as {got.rows!r}")
        return 1
    return 0


def the_pages_cover_the_listing(out: list[str]) -> int:
    """Check walking the pages yields every row exactly once — the completeness arm.

    ⚑ A PAGINATION THAT DROPS OR REPEATS A ROW is worse than no pagination, because the reader
    now has a confident wrong denominator. Walking the whole listing is the only check that sees
    it.
    """
    seen: list[str] = []
    at = 0
    while True:
        got = page.take(_ROWS, _SIZE, at)
        if not got.rows:
            break
        seen.extend(got.rows)
        at += got.shown
    if tuple(seen) != _ROWS:
        out.append(f"selftest: walking the pages yielded {seen!r}")
        return 1
    return 0


def the_last_page_says_it_is_last(out: list[str]) -> int:
    """Check the final page is distinguishable from a middle one.

    ⚑ "428 more" AND "you have reached the end" ARE DIFFERENT FACTS, and a walker that could not
    tell them apart would either stop early or loop.
    """
    got = page.tail(page.take(_ROWS, _SIZE, _TOTAL - 1))
    if "more" in got:
        out.append(f"selftest: the last page offers more rows: {got!r}")
        return 1
    if not got:
        out.append("selftest: the last page of a bounded walk said nothing")
        return 1
    return 0


def an_overshooting_skip_is_clamped(out: list[str]) -> int:
    """Check a walk past the end degrades rather than raising.

    ⚑ PAGING IS A READING CONVENIENCE. Refusing a walk that ran off the end would turn "you have
    seen it all" into an error, which is the state a walker reaches on its last iteration by
    construction.
    """
    got = page.take(_ROWS, _SIZE, _TOTAL * 2)
    if got.rows:
        out.append(f"selftest: an overshooting skip returned rows: {got.rows!r}")
        return 1
    if got.total != _TOTAL:
        out.append(f"selftest: the denominator was lost past the end: {got.total}")
        return 1
    return 0


def a_negative_skip_is_clamped(out: list[str]) -> int:
    """Check a negative offset does not index from the end."""
    got = page.take(_ROWS, _SIZE, -5)
    if got.rows != _ROWS[:_SIZE]:
        out.append(f"selftest: a negative skip read as {got.rows!r}")
        return 1
    return 0


def zero_top_means_all(out: list[str]) -> int:
    """Check `--top 0` is unbounded, not empty.

    ⚑ INHERITED, NOT INVENTED — `toolmodes --top 0` already means "every row". The opposite
    reading would make a reasonable-looking argument silently return nothing, which is the exact
    failure a bound exists to prevent.
    """
    got = page.take(_ROWS, page.UNBOUNDED)
    if got.shown != _TOTAL:
        out.append(f"selftest: --top 0 returned {got.shown} row(s)")
        return 1
    return 0


def the_flags_are_read_from_argv(out: list[str]) -> int:
    """Check the shared flag reader takes both halves."""
    top, skip = page.read_args(["tool", page.TOP, "7", page.SKIP, "2"])
    if (top, skip) != (7, 2):
        out.append(f"selftest: the flags read as top={top} skip={skip}")
        return 1
    return 0


def a_malformed_bound_falls_back(out: list[str]) -> int:
    """Check a typo does not kill an answerable invocation.

    ⚑ THE BOUND IS NOT THE POINT OF THE CALL. A tool that died on `--top banana` would refuse a
    question it can answer, over a reading convenience.
    """
    top, skip = page.read_args(["tool", page.TOP, "banana"])
    if (top, skip) != (page.UNBOUNDED, 0):
        out.append(f"selftest: a malformed bound read as top={top} skip={skip}")
        return 1
    if page.read_args(["tool", page.TOP])[0] != page.UNBOUNDED:
        out.append("selftest: a trailing flag with no value did not fall back")
        return 1
    return 0


def the_default_is_unbounded(out: list[str]) -> int:
    """Check adding pagination changes no existing caller.

    ⚑⚑ A READER OPTS IN TO A PAGE. If the default bounded output, every downstream consumer that
    parses a tool's listing would start silently receiving a prefix — pagination introducing the
    exact defect it was added to remove.
    """
    if page.read_args(["tool"]) != (page.UNBOUNDED, 0):
        out.append("selftest: the default is not unbounded-from-the-start")
        return 1
    return 0


_ARMS = (
    an_unbounded_page_takes_everything,
    an_unbounded_page_says_nothing,
    a_bounded_page_names_what_is_left,
    the_offset_reaches_later_rows,
    the_pages_cover_the_listing,
    the_last_page_says_it_is_last,
    an_overshooting_skip_is_clamped,
    a_negative_skip_is_clamped,
    zero_top_means_all,
    the_flags_are_read_from_argv,
    a_malformed_bound_falls_back,
    the_default_is_unbounded,
)

_CASE_COUNT = 2 + 1 + 3 + 1 + 1 + 2 + 2 + 1 + 1 + 1 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"page selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"page selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
