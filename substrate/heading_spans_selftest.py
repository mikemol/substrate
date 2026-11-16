# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.heading_spans` — including the drop the origin performed in silence.

⚑⚑⚑ THE LOAD-BEARING ARM IS THE ONE THAT ASSERTS A FAILURE IS REPORTED. The origin's scan fell
through on an unanchored heading and returned a shorter list, so a caller could not distinguish a
three-section document from a fourteen-section document eleven of whose headings failed to match.
Every other case here would pass against that origin; only the `unanchored` arms would not.

⚑⚑ AND THE SMART-PUNCTUATION CASES ARE THE REGRESSION, run against the real trigger classes rather
than invented ones. A heading carrying `---` is the shape that made a peer's whole document read as
empty, so it is cased directly instead of being represented by a stand-in.

⚑ THE FIXTURES ARE LINES, NOT FILES, because `anchor` takes headings and lines. That is the point
of the split: the origin fused the AST read, the file read and the anchoring, so it could only be
tested against a document on disk with pandoc installed.

⚑⚑ AND THE MUTATED DEPENDENCY IS IMPORTED DIRECTLY, WHICH THE TYPE CHECKER FORCED. A first cut
reached it as `heading_spans.heading_key` and was refused: a module's imports are not its declared
exports, so reaching a dependency THROUGH a consumer is an undeclared re-export that type-checks
against nothing. Importing `heading_key` here states the coupling the sensitivity arm actually has.
"""

from __future__ import annotations

import sys

from substrate import heading_key
from substrate import heading_spans as hs

#: What pandoc renders `---` as — the rendered side of the hardest real case.
EM = "\N{EM DASH}"


def _plain_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for headings whose rendered text equals their source."""
    out: list[tuple[str, bool]] = []
    lines = ["# Title", "", "body", "## First", "", "a", "## Second", "", "b"]
    got = hs.anchor([(1, "Title"), (2, "First"), (2, "Second")], lines)

    out.append((f"every heading anchors — {got.why()}", got.complete))
    out.append((f"and {len(got.spans)} span(s) come back", len(got.spans) == 3))  # noqa: PLR2004
    out.append((f"the H1 starts at line 1: {got.spans[0].start}", got.spans[0].start == 1))
    # ⚑ THE H1 CLOSES AT THE END, not at its first child: `## First` is DEEPER, so it does not
    # close the section above it. A reader that ended a span at the next heading of any level
    # would report a one-line H1 and look correct.
    out.append(
        (f"the H1 spans the whole document: {got.spans[0].end}", got.spans[0].end == len(lines) + 1)
    )
    out.append((f"the first H2 closes at the second: {got.spans[1].end}", got.spans[1].end == 7))  # noqa: PLR2004
    return out


def _smart_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the smart-punctuation class that broke the origin."""
    out: list[tuple[str, bool]] = []
    lines = ["# Root", "", "x", "## Overview --- two layers", "", "y", "## Plain child", "", "z"]
    # ⚑ THE HEADINGS ARRIVE AS PANDOC RENDERS THEM — an em dash, not three hyphens. That
    # difference IS the defect, so the fixture must carry the rendered form or it tests nothing.
    got = hs.anchor([(1, "Root"), (2, f"Overview {EM} two layers"), (2, "Plain child")], lines)

    out.append((f"an em-dash heading anchors to its raw source — {got.why()}", got.complete))
    out.append((f"and all three are placed: {len(got.spans)}", len(got.spans) == 3))  # noqa: PLR2004
    placed = [s.text for s in got.spans]
    out.append((f"the rendered text is preserved in the span: {placed[1]!r}", EM in placed[1]))
    return out


def _unanchored_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the reporting the origin could not do.

    ⚑⚑⚑ THIS IS THE DIFFERENTIAL AGAINST THE ORIGIN. Given a heading with no matching source line,
    the origin returned a short list and said nothing; this returns the same short list AND names
    what it could not place. An arm asserting only the span count would pass against both.
    """
    out: list[tuple[str, bool]] = []
    lines = ["# Root", "", "x", "## Present", "", "y"]
    got = hs.anchor([(1, "Root"), (2, "Present"), (2, "Absent from the source")], lines)

    out.append((f"the placeable headings still anchor: {len(got.spans)}", len(got.spans) == 2))  # noqa: PLR2004
    out.append((f"the unplaceable one is REPORTED: {got.unanchored}", len(got.unanchored) == 1))
    out.append((f"and it is named: {got.why()}", "Absent from the source" in got.why()))
    out.append((f"complete is False when anything is lost: {got.complete}", not got.complete))
    # ⚑ THE DENOMINATOR IS THE WHOLE POINT. 2 of 3 is a different claim from 2 of 2, and the
    # origin could only ever say the second.
    out.append((f"total counts placed AND unplaced: {got.total}", got.total == 3))  # noqa: PLR2004

    # ⚑⚑ THE WORST REAL CASE: every heading fails, which is what a peer's document did. The
    # result must be an EMPTY span list that still reports fourteen-style totals, never an
    # empty result indistinguishable from an empty document.
    none_placed = hs.anchor([(2, "Alpha"), (2, "Beta")], ["no headings here", "at all"])
    out.append(
        (
            f"a document where nothing anchors reports its total: {none_placed.why()}",
            none_placed.total == 2 and not none_placed.spans,
        )
    )  # noqa: PLR2004
    return out


def _sensitivity_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the arms above would CATCH a broken key.

    ⚑⚑⚑ A PASSING ARM SAYS THE ANCHORER WORKS, NEVER THAT ITS PARTS ARE LOAD-BEARING. Every case
    above would also pass against an anchorer whose normalisation happened to be adequate for
    these fixtures, so this arm BREAKS the key in a restored-afterwards mutation and asserts the
    smart-punctuation heading stops anchoring — turning `heading_key` from a dependency this suite
    happens to exercise into one it would notice losing.

    ⚑⚑ AND THE AXIS IS CHOSEN TO BE THE ONE THE OTHER ARMS CANNOT VARY. The unanchored cases feed
    a heading that is genuinely absent, which exercises the anchorer behaving CORRECTLY; nothing
    above forces a heading that IS present to fail. That distinction was named by a peer working
    the same shape in a witness with no table to reverse: force the state where the check should
    refuse, and confirm it does.

    ⚑ THE EMPTY TABLE IS NOT AN ARBITRARY MUTATION — it is the ORIGIN's behaviour for this class,
    which normalised inline markup and no punctuation at all. So this arm reproduces the exact
    defect the drain exists to remove, and would fail the day someone narrowed the table back.
    """
    out: list[tuple[str, bool]] = []
    lines = ["# Root", "", "x", "## Overview --- two layers", "", "y"]
    headings = [(1, "Root"), (2, f"Overview {EM} two layers")]

    healthy = hs.anchor(headings, lines)
    original = heading_key.SMART
    try:
        heading_key.SMART = {}
        broken = hs.anchor(headings, lines)
    finally:
        heading_key.SMART = original

    out.append(
        (
            f"with the smart table emptied, the em-dash heading is LOST — {broken.why()}",
            not broken.complete,
        )
    )
    out.append(
        (
            f"and the loss is exactly one heading: {len(broken.unanchored)}",
            len(broken.unanchored) == 1,
        )
    )
    out.append((f"while the healthy table places it: {healthy.why()}", healthy.complete))
    out.append(("and the table is restored afterwards", hs.anchor(headings, lines).complete))
    return out


def _control_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the negative controls.

    ⚑ AN ANCHORER THAT MATCHED EVERYTHING WOULD PASS EVERY ARM ABOVE, so a heading that genuinely
    is not in the source must NOT be placed — and the forward cursor must not rebind a repeated
    heading to an earlier line.
    """
    out: list[tuple[str, bool]] = []
    empty = hs.anchor([], ["# Title", "body"])
    out.append(
        (
            f"no headings yields no spans and is complete: {empty.why()}",
            empty.complete and not empty.spans,
        )
    )

    # ⚑ THE FORWARD CURSOR, ASSERTED. Two identical headings must bind to line 1 and line 4, not
    # both to line 1 — a rebinding reader reports a zero-length section and looks plausible.
    dup = hs.anchor([(2, "Same"), (2, "Same")], ["## Same", "a", "b", "## Same", "c"])
    starts = [s.start for s in dup.spans]
    out.append((f"repeated headings bind in order: {starts}", starts == [1, 4]))

    # ⚑ A NON-HEADING LINE WHOSE TEXT MATCHES MUST NOT ANCHOR. The scan requires a leading `#`,
    # so prose repeating a heading's words cannot capture it.
    prose = hs.anchor([(2, "Overview")], ["Overview", "## Overview"])
    out.append(
        (
            f"prose matching a heading does not anchor it: {[s.start for s in prose.spans]}",
            [s.start for s in prose.spans] == [2],
        )
    )
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _plain_cases()
        + _smart_cases()
        + _unanchored_cases()
        + _sensitivity_cases()
        + _control_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"heading-spans selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
