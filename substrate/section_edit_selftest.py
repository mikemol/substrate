# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.section_edit` — splice arithmetic, and the refusals that guard a write.

⚑⚑⚑ THE SPLICE ARITHMETIC IS WHERE AN OFF-BY-ONE HIDES, and an off-by-one here eats a heading or
duplicates a line in a document nobody diffs closely. So every arm asserts the RESULTING LINES, not
a length or a success flag — a case checking that the text changed would pass against a splice that
deleted the wrong row.

⚑⚑ THE REFUSALS ARE CASED AS HARD AS THE WRITES, because they are the whole safety argument. A
resolver that picked the first of two matches would satisfy every write arm below and would
silently edit the wrong section, which is not recoverable by re-running.

⚑ AND THE SENSITIVITY ARM FORCES THE STATE THE OTHER ARMS CANNOT REACH. Every case here uses a
correct span list, so nothing above proves the module reads `Span.start`/`Span.end` rather than
guessing — the mutation feeds a span whose bounds are off by one and asserts the output moves with
it. A passing arm says the splice works, never that the bounds are load-bearing.
"""

from __future__ import annotations

import sys

from substrate import section_edit as se
from substrate.heading_spans import Span

#: A four-section fixture whose bodies are distinguishable, so a wrong splice is visible.
LINES = [
    "# Root",  # 1
    "",  # 2
    "root body",  # 3
    "## Alpha",  # 4
    "",  # 5
    "alpha body",  # 6
    "",  # 7
    "## Beta",  # 8
    "",  # 9
    "beta body",  # 10
]

#: The spans that reader would produce for `LINES`, 1-indexed with `end` EXCLUSIVE.
SPANS = [
    Span(1, "Root", 1, 11),
    Span(2, "Alpha", 4, 8),
    Span(2, "Beta", 8, 11),
]


def _find_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for resolution and its two refusals."""
    out: list[tuple[str, bool]] = []

    got = se.find(SPANS, "alpha")
    out.append(
        (f"a needle resolves case-insensitively to one span: {got.text!r}", got.text == "Alpha")
    )

    try:
        se.find(SPANS, "nothing like this")
    except se.SectionError as exc:
        text = str(exc)
        out.append((f"an unmatched needle REFUSES: {text[:48]!r}…", True))
        # ⚑ THE SAMPLE IS THE REPAIR-DISCRIMINATING PART. A reader whose heading was LOST needs
        # to see what the reader DID have, or they will re-spell a correct needle forever.
        out.append((f"and samples the headings it did see: {'Alpha' in text}", "Alpha" in text))
        out.append(("and names the reader as a possible cause", "READER lost it" in text))
    else:
        out.append(("an unmatched needle REFUSES", False))

    try:
        # ⚑ `a` is a substring of BOTH `Alpha` and `Beta` — the ambiguity this must not resolve.
        se.find(SPANS, "a")
    except se.SectionError as exc:
        text = str(exc)
        out.append((f"an ambiguous needle REFUSES: {text[:48]!r}…", True))
        out.append(
            (
                f"and names every candidate: {'Alpha' in text and 'Beta' in text}",
                "Alpha" in text and "Beta" in text,
            )
        )
        out.append(("and says it is refusing rather than choosing", "REFUSING" in text))
    else:
        out.append(("an ambiguous needle REFUSES", False))

    return out


def _replace_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for body replacement, asserted on the resulting lines."""
    out: list[tuple[str, bool]] = []
    edit = se.replace(LINES, SPANS[1], "NEW")
    got = edit.text.split("\n")

    out.append((f"the edit reports its target — {edit.why()}", edit.section.text == "Alpha"))
    # ⚑⚑ THE HEADING SURVIVES. Replacing it would move the anchor every other reader resolves
    # against, so this is the load-bearing assertion rather than a formatting preference.
    out.append((f"the heading line is untouched: {got[3]!r}", got[3] == "## Alpha"))
    out.append((f"the body is replaced: {got[4]!r}", got[4] == "NEW"))
    out.append((f"the NEXT heading survives at its new index: {got[5]!r}", got[5] == "## Beta"))
    # ⚑ AND NOTHING ABOVE THE SECTION MOVED — a splice that shifted the preamble would still
    # produce a plausible document.
    out.append((f"the preamble is intact: {got[:3]!r}", got[:3] == LINES[:3]))
    out.append((f"the tail is intact: {got[-1]!r}", got[-1] == "beta body"))
    return out


def _append_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for in-section append and blank-line preservation."""
    out: list[tuple[str, bool]] = []
    edit = se.append(LINES, SPANS[1], "ADDED")
    got = edit.text.split("\n")

    out.append(
        (
            f"the appended line lands INSIDE the section: {got.index('ADDED')}",
            got.index("ADDED") < got.index("## Beta"),
        )
    )
    out.append((f"the original body survives above it: {got[5]!r}", got[5] == "alpha body"))
    # ⚑⚑⚑ THE BLANK BEFORE THE NEXT HEADING IS THE CASE THE ORIGIN'S COMMENT ARGUES FOR. Markdown
    # block separation is load-bearing, and appending AFTER the blank places the text where it
    # reads as belonging to the following section.
    out.append(
        (
            f"a blank line still separates the next heading: {got[got.index('## Beta') - 1]!r}",
            got[got.index("## Beta") - 1] == "",
        )
    )
    out.append((f"the heading is untouched: {got[3]!r}", got[3] == "## Alpha"))

    # ⚑ A SECTION WITH NO TRAILING BLANK must still append cleanly — the `tail` loop's zero case.
    tight = ["## Only", "body"]
    tight_edit = se.append(tight, Span(2, "Only", 1, 3), "X")
    out.append(
        (
            f"a section with no trailing blank appends: {tight_edit.text.split(chr(10))!r}",
            tight_edit.text.split("\n") == ["## Only", "body", "", "X"],
        )
    )
    return out


def _sensitivity_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving the splice READS the span rather than guessing.

    ⚑⚑⚑ EVERY ARM ABOVE FEEDS A CORRECT SPAN, so none of them can tell a splice that uses
    `start`/`end` from one that happens to land right on this fixture. This feeds a DELIBERATELY
    WRONG span and asserts the output moves with it — if the result were unchanged, the bounds
    would be decoration and the module would be splicing by some other rule.
    """
    out: list[tuple[str, bool]] = []
    correct = se.replace(LINES, SPANS[1], "NEW").text.split("\n")
    shifted = se.replace(LINES, Span(2, "Alpha", 5, 8), "NEW").text.split("\n")

    out.append(
        (
            f"a shifted span produces DIFFERENT output: {shifted[4]!r} vs {correct[4]!r}",
            shifted != correct,
        )
    )
    # ⚑ AND THE SHIFT IS VISIBLE IN THE EXPECTED DIRECTION: start=5 keeps one more line above.
    out.append((f"the extra line above is kept: {shifted[4]!r}", shifted[4] == ""))
    return out


def _control_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the negative controls.

    ⚑ A SPLICE THAT RETURNED ITS INPUT would pass any arm asserting the heading survives, so the
    output must be asserted DIFFERENT from the input — and an empty body must still remove the
    old text rather than silently doing nothing.
    """
    out: list[tuple[str, bool]] = []
    edit = se.replace(LINES, SPANS[1], "NEW")
    out.append(
        (
            f"the output differs from the input: {edit.text != chr(10).join(LINES)}",
            edit.text != "\n".join(LINES),
        )
    )

    # ⚑⚑ AN EMPTY BODY LEAVES ONE BLANK LINE, NOT NOTHING, AND I ASSERTED THE WRONG THING FIRST.
    # `"".split("\n")` is `[""]`, so the section empties to a single blank row. That is CORRECT
    # markdown — a heading immediately followed by another heading loses its block separation —
    # and the case now pins the real behaviour rather than the one I expected.
    empty = se.replace(LINES, SPANS[1], "").text.split("\n")
    out.append(
        (
            f"an empty body clears to one blank line: {empty[3:6]!r}",
            empty[3] == "## Alpha" and empty[4] == "" and empty[5] == "## Beta",
        )
    )

    # ⚑ AN EMPTY SPAN LIST REFUSES WITH A READABLE SAMPLE rather than crashing on the slice.
    try:
        se.find([], "anything")
    except se.SectionError as exc:
        out.append(
            (f"an empty span list refuses readably: {'none' in str(exc)}", "none" in str(exc))
        )
    else:
        out.append(("an empty span list refuses", False))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _find_cases() + _replace_cases() + _append_cases() + _sensitivity_cases() + _control_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"section-edit selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
